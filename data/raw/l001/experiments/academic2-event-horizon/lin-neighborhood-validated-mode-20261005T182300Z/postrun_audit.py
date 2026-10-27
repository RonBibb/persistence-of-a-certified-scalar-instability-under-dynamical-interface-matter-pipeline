"""Full-neighborhood read-only audit adapted from the reviewed central R1 checker.

No physical IVP and no producer import. Parameter scope is independently checked.
"""
import argparse
import ast
from datetime import datetime, timezone
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import sys


EXPECTED_GUARD = "2c83c19c3db530b475b59cbffcde1d22db86e90a72cbeb4070b76fdc3aaf07cf"
EXPECTED_CONFIG = {
    "bits": 768, "primary_steps": 8192, "independent_steps": 16384,
    "order": 5, "checkpoint_cells": 256,
    "mu": ["-33/25000", "-131/100000"],
    "A": ["696726888586725316547/7036874417766400000000", "696727170061702027203/7036874417766400000000"],
    "D": ["8177/4096", "8187/4096"],
    "scope": "EVERY_PARAMETER_PAIR_IN_COMPLETE_CERTIFIED_STATIC_BOX",
    "parameter_box": {
        "v1": ["3256417487256207/36028797018963968", "101988226458125/1125899906842624"],
        "lambda_b": ["-1703752349608937/281474976710656", "-1703696054613595/281474976710656"],
    },
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
    demand(str(Path(flint.__file__).resolve().parent) == runtime["flint_file"], "Loaded Arb binding path changed")
    demand(str(Path(sys.executable).resolve()) == runtime["executable"], "Python executable changed")
    check_file(runtime["executable"], runtime["executable_sha256"])
    for name, expected in runtime["libraries"].items():
        check_file(name, expected)

    preflight = read(packet / binding["inputs"]["preflight"]["path"])
    demand(preflight["pass"] and all_true(preflight["checks"]), "Preflight failed")
    demand(preflight["source"] == binding["source"] and preflight["runtime"] == runtime,
           "Stale preflight source/runtime")
    demand(preflight["physical_model_evaluated"] is False, "Preflight was physical")
    static_path = packet / binding["inputs"]["static_neighborhood_result"]["path"]
    static = read(static_path)
    static_audit = read(packet / binding["inputs"]["static_neighborhood_audit"]["path"])
    demand(static_audit["status"] == "PASS" and static_audit["result_sha256"] == sha(static_path),
           "Independent static audit authority differs")
    demand(static["status"] == "COMPLETE" and static["admitted_fraction"] == 1
           and not static["unresolved_parameter_cells"], "Full static neighborhood not admitted")
    demand(static["frozen_design"]["parameter_box"] == EXPECTED_CONFIG["parameter_box"],
           "Continuous parameter box differs")
    demand(static["frozen_design"]["root_box"] == EXPECTED_CONFIG["A"], "Full root tube differs")
    volume = Q(1)
    for pair in EXPECTED_CONFIG["parameter_box"].values():
        volume *= Q(pair[1]) - Q(pair[0])
    demand(Q(static["total_parameter_volume_exact"]) == Q(static["admitted_parameter_volume_exact"]) == volume,
           "Exact admitted parameter volume differs")
    demand(len(static["terminal_parameter_cells"]) == 1, "Unexpected static subdivision")
    cell = static["terminal_parameter_cells"][0]
    demand(cell["pass"] and cell["parameter_cell"]["depth"] == 0 and cell["root"]["pass"],
           "Whole depth-zero root cell not admitted")
    for name, pair in EXPECTED_CONFIG["parameter_box"].items():
        demand(cell["parameter_cell"][name] == pair, "Static terminal cell is not the full box")
    root = cell["root"]
    demand(root["root_box_exact_bounds"] == EXPECTED_CONFIG["A"], "Root certificate uses a different tube")
    for engine in ("primary", "independent"):
        certificate = root[engine]
        event = certificate["root_box_event"]
        demand(certificate["qualified_parametric_interval_newton"]
               and Q(certificate["strict_inclusion_margin_exact"]) > 0, "Static parametric Newton failed")
        demand(event["validated"] and event["G_s_strictly_negative"] and event["q_a_excludes_zero"]
               and event["event_bracket_exact"] == EXPECTED_CONFIG["D"], "Uniform static event certificate differs")
    static_binding_path = packet / binding["inputs"]["static_neighborhood_binding"]["path"]
    static_binding = read(static_binding_path)
    for entry in static_binding["imports"].values():
        check_file(static_binding_path.parent / entry["relative_path"], entry["sha256"])
    fixed_symbols = {"m2": "M2", "gamma": "GAMMA", "v0": "V0", "lambda_a": "LAMBDA_A"}
    for engine in ("primary", "independent"):
        source_path = static_binding_path.parent / static_binding["imports"][engine + "_source"]["relative_path"]
        tree = ast.parse(source_path.read_text())
        constants = {node.targets[0].id: node.value.value for node in tree.body
                     if isinstance(node, ast.Assign) and len(node.targets) == 1
                     and isinstance(node.targets[0], ast.Name) and isinstance(node.value, ast.Constant)}
        for name, symbol in fixed_symbols.items():
            demand(Q(float(constants[symbol])) == Q(binding["model_exact"][name]),
                   "Nonvaried action parameter differs from the static producer")
    for name, pair in EXPECTED_CONFIG["parameter_box"].items():
        demand(Q(pair[0]) <= Q(binding["model_exact"][name]) <= Q(pair[1]),
               "Inherited central anchor lies outside the varied parameter box")
    prior_binding = read(packet / binding["inputs"]["previous_binding"]["path"])
    demand(binding["model_exact"] == prior_binding["model_exact"], "Exact action parameters changed")
    for name in ("primary_interval.py", "independent_interval.py"):
        demand(binding["source"][name] == prior_binding["source"][name], "Validated interval kernel changed")
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
    classification = ("NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_ON_STATIC_PARAMETER_NEIGHBORHOOD" if strip_certificate else
                      "NEGATIVE_SCALAR_EIGENVALUE_CERTIFIED_ON_STATIC_PARAMETER_NEIGHBORHOOD_RADION_OVERLAP_UNRESOLVED" if endpoint_certificate else
                      "NEIGHBORHOOD_VALIDATED_MODE_UNRESOLVED")
    demand(result["classification"] == terminal["classification"] == classification,
           "Producer classification not supported by independent audit")
    demand(result["endpoint_certificate"] == endpoint_certificate and
           result["uniform_separation_certificate"] == strip_certificate, "Producer certificate flags differ")

    def check_parameter_scope(params, task_index):
        for name, pair in EXPECTED_CONFIG["parameter_box"].items():
            m, r = params[name]["_arb_native"]
            center, radius = Q(m[0]) * Q(2)**m[1], Q(r[0]) * Q(2)**r[1]
            demand(center - radius <= Q(pair[0]) <= Q(pair[1]) <= center + radius,
                   "Checkpoint upper-wall parameter does not enclose the complete domain")
        for name in ("m2", "gamma", "v0", "lambda_a"):
            m, r = params[name]["_arb_native"]
            center, radius = Q(m[0]) * Q(2)**m[1], Q(r[0]) * Q(2)**r[1]
            demand(center - radius <= Q(binding["model_exact"][name]) <= center + radius,
                   "Checkpoint fixed action parameter excludes its exact value")
        m, r = params["mu"]["_arb_native"]
        center, radius = Q(m[0]) * Q(2)**m[1], Q(r[0]) * Q(2)**r[1]
        kind = EXPECTED_CONFIG["task_order"][task_index].split("_")[1]
        pair = EXPECTED_CONFIG["mu"] if kind == "strip" else [EXPECTED_CONFIG["mu"][kind == "high"]] * 2
        demand(center - radius <= Q(pair[0]) <= Q(pair[1]) <= center + radius,
               "Checkpoint mass does not cover its declared endpoint or strip")

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
        check_parameter_scope(state["params"], i if j else i - 1)
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
               "complete_parameter_box_exact": EXPECTED_CONFIG["parameter_box"],
               "root_tube_exact": EXPECTED_CONFIG["A"], "event_interval_exact": EXPECTED_CONFIG["D"],
               "admitted_static_volume_exact": str(volume),
               "parameter_scope_checkpoints_verified": len(checkpoint_files),
               "quantifier": "For every p in the exact closed box, there exists a negative scalar mass for that fixed exact certified background",
               "all_nonvaried_action_parameters_match_static_producers": True,
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
