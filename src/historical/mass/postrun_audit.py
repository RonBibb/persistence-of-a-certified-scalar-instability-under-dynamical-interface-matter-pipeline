"""Read-only exact-bound/integrity audit; no physical IVP and no producer import."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import sys


EXPECTED_GUARD = "fca1b49a652afc1832e61e31e5e8c47dc86d63144de791211c89372f55a82e00"
EXPECTED_CONFIG = {
    "bits": 768, "primary_steps": 8192, "independent_steps": 16384,
    "order": 5, "checkpoint_cells": 256,
    "mu": ["-33/25000", "-131/100000"],
    "A": ["456607025194779413/4611686018427387904", "114151756532473697/1152921504606846976"],
    "D": ["32727/16384", "32729/16384"],
    "task_order": ["primary_low", "primary_high", "independent_low", "independent_high",
                   "primary_strip", "independent_strip"],
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                      allow_nan=False).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def demand(condition, message):
    if not condition:
        raise AssertionError(message)


def exact_bounds(record):
    lo, hi = Q(record["lo_exact"]), Q(record["hi_exact"])
    demand(lo <= hi, "Reversed exact enclosure")
    return lo, hi


def approximate(record):
    return [float(v) for v in exact_bounds(record)]


def exp_positive_bounds(x, degree=64):
    """Exact rational series and geometric-tail bound, independent of Arb."""
    demand(x >= 0 and x < degree + 2, "Exponential tail ratio invalid")
    term = Q(1)
    partial = term
    for n in range(1, degree + 1):
        term *= x / n
        partial += term
    next_term = term * x / (degree + 1)
    return partial, partial + next_term / (1 - x / (degree + 2))


def exp_bounds(x):
    if x >= 0:
        return exp_positive_bounds(x)
    lo, hi = exp_positive_bounds(-x)
    return 1 / hi, 1 / lo


def decimal_floor(value, places=10):
    scale = 10**places
    return str(Q((value * scale).numerator // (value * scale).denominator, scale))


def all_true(tree):
    return all(all_true(v) for v in tree.values()) if isinstance(tree, dict) else tree is True


def main(packet):
    from flint import arb, ctx
    import flint

    ctx.prec = 768
    ctx.threads = 1
    tracked = {}
    hash_links = 0
    native_count = 0

    def check_file(path, expected):
        nonlocal hash_links
        path = Path(path).resolve()
        observed = sha(path)
        demand(observed == expected, "Hash mismatch: " + str(path))
        tracked[str(path)] = observed
        hash_links += 1

    def validate_native(value):
        nonlocal native_count
        if isinstance(value, dict):
            if "_arb_native" in value:
                demand(set(value) == {"_arb_native"}, "Unexpected native fields")
                midpoint, radius = value["_arb_native"]
                demand(all(type(v) is int for pair in (midpoint, radius) for v in pair),
                       "Native tuple not integral")
                demand(len(midpoint) == len(radius) == 2 and radius[0] >= 0, "Invalid native pair")
                restored = arb(tuple(midpoint), tuple(radius))
                demand(restored.is_finite(), "Nonfinite native interval")
                observed = [[int(v) for v in restored.mid().man_exp()],
                            [int(v) for v in restored.rad().man_exp()]]
                demand(observed == value["_arb_native"], "Canonical native roundtrip differs")
                native_count += 1
            elif "_rational" in value:
                demand(set(value) == {"_rational"}, "Unexpected rational fields")
                Q(value["_rational"])
            else:
                for child in value.values():
                    validate_native(child)
        elif isinstance(value, list):
            for child in value:
                validate_native(child)
        elif isinstance(value, float):
            demand(math.isfinite(value), "Nonfinite JSON number")

    binding = read(packet / "BINDINGS.json")
    freeze = read(packet / "FREEZE_RECORD.json")
    check_file(packet / "BINDINGS.json", EXPECTED_GUARD)
    demand(freeze["binding_sha256"] == EXPECTED_GUARD, "Freeze guard mismatch")
    demand(binding["config"] == EXPECTED_CONFIG, "Prospective configuration changed")
    for name, expected in binding["source"].items():
        check_file(packet / name, expected)
    for name, expected in binding["review_sources"].items():
        check_file(packet / name, expected)
    for entry in binding["inputs"].values():
        check_file(packet / entry["path"], entry["sha256"])

    runtime = binding["runtime"]
    demand(flint.__version__ == runtime["flint"], "Arb binding version changed")
    demand(str(Path(sys.executable).resolve()) == runtime["executable"], "Python executable changed")
    check_file(runtime["executable"], runtime["executable_sha256"])
    for name, expected in runtime["libraries"].items():
        check_file(name, expected)

    preflight = read(packet / binding["inputs"]["preflight"]["path"])
    demand(preflight["pass"] and all_true(preflight["checks"]), "Preflight failed")
    demand(preflight["source"] == binding["source"] and preflight["runtime"] == runtime,
           "Stale preflight source/runtime")
    demand(preflight["physical_model_evaluated"] is False, "Preflight was physical")
    high = read(packet / binding["inputs"]["d1_high_result"]["path"])
    demand(high["narrow"]["newton_exact_bounds"] == EXPECTED_CONFIG["A"], "Static root mismatch")
    demand([Q(x) for x in high["narrow"]["event_bracket"]] == [Q(x) for x in EXPECTED_CONFIG["D"]],
           "Static event interval mismatch")
    prior_binding = read(packet / binding["inputs"]["previous_binding"]["path"])
    demand(binding["model_exact"] == prior_binding["model_exact"], "Exact action parameters changed")
    manifest_path = packet / binding["inputs"]["previous_manifest"]["path"]
    manifest = read(manifest_path)
    entries = manifest["files"]
    if isinstance(entries, dict):
        entries = [{"path": k, "sha256": v if isinstance(v, str) else v["sha256"]}
                   for k, v in entries.items()]
    for entry in entries:
        check_file(manifest_path.parent / entry["path"], entry["sha256"])

    out = packet / "output"
    demand(not (out / "FAILURE.json").exists(), "R1 has a failure record")
    result = read(out / "RESULT.json")
    terminal = read(out / "TERMINAL.json")
    demand(result["status"] == terminal["status"] == "COMPLETE", "Not terminal complete")
    demand(result["guard"] == terminal["guard"] == EXPECTED_GUARD, "Terminal guard mismatch")
    check_file(out / "RESULT.json", terminal["result_sha256"])
    demand(result["config"] == EXPECTED_CONFIG, "Result configuration differs")
    tasks = result["tasks"]
    demand(len(tasks) == 6, "Expected all six fixed tasks")
    Dlo, Dhi = map(Q, EXPECTED_CONFIG["D"])
    summary = []
    for index, name in enumerate(EXPECTED_CONFIG["task_order"]):
        task = read(out / (name + ".json"))
        demand(task == tasks[index] and task["task"] == name, "Task/result disagreement")
        demand(task["status"] == "COMPLETE" and task["guard"] == EXPECTED_GUARD,
               "Task incomplete or wrong guard")
        body = {k: v for k, v in task.items() if k != "task_record_digest"}
        demand(canonical_digest(body) == task["task_record_digest"], "Task content digest differs")
        check_file(out / (name + ".json"), sha(out / (name + ".json")))
        validate_native(task)
        engine = name.split("_")[0]
        h = Q(2, EXPECTED_CONFIG[engine + "_steps"])
        cells = math.ceil(Dhi / h)
        demand(task["cells"] == cells, "Wrong accepted cell count")
        expected_cover = []
        for j in range(max(0, math.ceil(Dlo / h) - 1), cells):
            s = j * h
            if s + h >= Dlo and s <= Dhi:
                expected_cover.append({"index": j, "s_exact": str(s),
                                       "lo_exact": str(max(Dlo, s)), "hi_exact": str(min(Dhi, s + h))})
        demand(task["event_cover"] == expected_cover, "Event cover is not the full exact cell intersections")
        demand(Q(expected_cover[0]["lo_exact"]) == Dlo and Q(expected_cover[-1]["hi_exact"]) == Dhi,
               "Event cover misses an endpoint")
        for left, right in zip(expected_cover, expected_cover[1:]):
            demand(left["hi_exact"] == right["lo_exact"], "Event cover gap")
        klo, khi = exact_bounds(task["K"])
        blo, bhi = exact_bounds(task["B0"])
        slo, shi = exact_bounds(task["sector"])
        demand(klo > 0 and (bhi < 0 or blo > 0) and shi < 0, "Physical sector gate failed")
        mlo, mhi = map(Q, EXPECTED_CONFIG["mu"])
        demand(slo <= mlo + 4 * klo and shi >= mhi + 4 * khi, "Sector interval not outward")
        item = {"task": name, "cells": cells, "determinant": approximate(task["determinant"]),
                "event_cover_verified": expected_cover, "K": approximate(task["K"]),
                "B0": approximate(task["B0"]), "sector": approximate(task["sector"]),
                "extrema": {k: approximate(v) for k, v in task["extrema"].items()},
                "picard_iterations_max": task["max_picard_iterations"]}
        if name.endswith("strip"):
            psilo, psihi = exact_bounds(task["extrema"]["psi"])
            Wlo, Whi = exact_bounds(task["extrema"]["W"])
            flo, fhi = exact_bounds(task["extrema"]["f"])
            zlo, zhi = exact_bounds(task["Z_lower_bound"])
            dlo, dhi = exact_bounds(task["deltaD_bound"])
            demand(psilo > 0 and zlo > 0 and dhi < 0, "Strip positivity gate failed")
            demand(dlo <= -2 * Dhi * psihi and dhi >= -2 * Dlo * psilo, "Displacement bound is not outward")
            exp_lo, exp_hi = exp_bounds(2 * Wlo)
            exact_z_lower = 12 * Dlo * psilo * psilo * exp_lo
            formula_hi = 12 * Dlo * psilo * psilo * exp_hi
            demand(exact_z_lower <= zhi and zlo <= formula_hi, "Norm formula disagrees with independent rational exp bounds")
            exact_z_upper = 2 * Dhi * exp_bounds(2 * Whi)[1] * (max(abs(flo), abs(fhi))**2 + 6 * psihi**2)
            item.update({"uniform_psi_positive": True,
                         "independent_Z_lower_rational_floor": decimal_floor(exact_z_lower),
                         "independent_Z_upper_integer_ceiling": math.ceil(exact_z_upper),
                         "reported_Z_formula": [float(zlo), float(zhi)],
                         "deltaD": [float(dlo), float(dhi)]})
        summary.append(item)

    signs = []
    for task in tasks[:4]:
        lo, hi = exact_bounds(task["determinant"])
        signs.append(1 if lo > 0 else -1 if hi < 0 else 0)
    endpoint_certificate = signs[0] * signs[1] == signs[2] * signs[3] == -1
    for j in (0, 1):
        a, b = exact_bounds(tasks[j]["determinant"]), exact_bounds(tasks[j + 2]["determinant"])
        demand(max(a[0], b[0]) <= min(a[1], b[1]), "Independent endpoint enclosures disagree")
    strip_certificate = endpoint_certificate and all(x.get("uniform_psi_positive") for x in summary[4:])
    classification = ("NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1" if strip_certificate else
                      "NEGATIVE_SCALAR_EIGENVALUE_CERTIFIED_RADION_OVERLAP_UNRESOLVED" if endpoint_certificate else
                      "VALIDATED_MODE_UNRESOLVED")
    demand(result["classification"] == terminal["classification"] == classification,
           "Producer classification not supported by independent audit")
    demand(result["endpoint_certificate"] == endpoint_certificate and
           result["uniform_separation_certificate"] == strip_certificate, "Producer certificate flags differ")

    checkpoint_positions = set()
    checkpoint_files = sorted((out / "checkpoints").glob("*.json"))
    for path in checkpoint_files:
        data = read(path)
        state = data["state"]
        digest = canonical_digest(data)
        demand(data["guard"] == EXPECTED_GUARD and path.stem.endswith("-" + digest), "Checkpoint guard/digest changed")
        i, j = state["task_index"], state["cell_index"]
        demand(path.name == f"{i:02d}-{j:06d}-{digest}.json", "Checkpoint coordinate/name differs")
        demand((i, j) not in checkpoint_positions, "Duplicate checkpoint position")
        checkpoint_positions.add((i, j))
        demand(state["results"] == tasks[:i], "Checkpoint prior committed tasks differ")
        if j:
            engine = EXPECTED_CONFIG["task_order"][i].split("_")[0]
            demand(state["total_cells"] == math.ceil(Dhi / Q(2, EXPECTED_CONFIG[engine + "_steps"])),
                   "Checkpoint total_cells differs")
        elif i:
            demand(state["state"] == tasks[i - 1]["native_final_state"], "Completion checkpoint final state differs")
        validate_native(data)
        check_file(path, sha(path))
    expected_positions = {(i + 1, 0) for i in range(6)}
    for i, name in enumerate(EXPECTED_CONFIG["task_order"]):
        engine = name.split("_")[0]
        cells = math.ceil(Dhi / Q(2, EXPECTED_CONFIG[engine + "_steps"]))
        expected_positions.update((i, j) for j in range(256, cells + 1, 256))
    demand(checkpoint_positions == expected_positions, "Missing or unexpected checkpoint positions")
    latest = read(out / "LATEST.json")
    demand(latest["guard"] == EXPECTED_GUARD, "Latest pointer guard differs")
    last_path = (out / latest["path"]).resolve()
    demand(last_path.parent == (out / "checkpoints").resolve(), "Latest pointer escapes checkpoint directory")
    last = read(last_path)
    demand(canonical_digest(last) == latest["digest"] and last["state"]["task_index"] == 6,
           "Latest pointer is not the complete state")

    for name in ("FREEZE_RECORD.json", "output/TERMINAL.json", "output/LATEST.json", "output/PROGRESS.json"):
        check_file(packet / name, sha(packet / name))
    demand(all(sha(path) == expected for path, expected in tracked.items()), "Inputs changed during audit")
    receipt = {"audit_pass": True, "classification_independently_derived": classification,
               "endpoint_certificate": endpoint_certificate, "uniform_separation_certificate": strip_certificate,
               "guard": EXPECTED_GUARD, "exact_signs": signs, "tasks": summary,
               "checkpoint_count": len(checkpoint_files), "native_roundtrips_checked": native_count,
               "file_hash_links_verified": hash_links, "unique_files_unchanged": len(tracked),
               "previous_manifest_files_verified": len(entries), "runtime_libraries_verified": len(runtime["libraries"]),
               "result_sha256": sha(out / "RESULT.json"), "terminal_sha256": sha(out / "TERMINAL.json"),
               "audit_source_sha256": sha(__file__), "new_physical_integration_performed": False,
               "independent_norm_check": "exact rational exponential series with geometric remainder, degree 64",
               "utc": datetime.now(timezone.utc).isoformat()}
    print(json.dumps(receipt, sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    main(parser.parse_args().packet.resolve())
