#!/usr/bin/env python3
"""Independent record audit for the fixed-D continuation dimension test."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from fractions import Fraction
from pathlib import Path
from typing import Any


ISOLATED_CLASSIFICATION = "CERTIFIED_ISOLATED_D1_ROOT_NO_NONTRIVIAL_FIXED_D_CONTINUATION"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def atomic_text(path: Path, value: str) -> None:
    tmp = path.with_name(path.name + f".tmp-{os.getpid()}")
    tmp.write_text(value, encoding="utf-8")
    os.replace(tmp, path)


def q(text: str) -> Fraction:
    return Fraction(text)


def audit(branch: Path) -> dict[str, Any]:
    output = branch / "output"
    result_path = output / "RESULT.json"
    terminal_path = output / "TERMINAL.json"
    binding_path = branch / "BINDINGS.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    preflight = json.loads((output / "PREFLIGHT.json").read_text(encoding="utf-8"))
    bindings = json.loads(binding_path.read_text(encoding="utf-8"))

    checks: dict[str, bool] = {
        "result_hash_matches_terminal": sha256_file(result_path) == terminal.get("result_sha256"),
        "result_terminal_classification_agree": result.get("classification") == terminal.get("classification"),
        "guard_agreement": result.get("guard") == terminal.get("guard") == preflight.get("guard"),
        "preflight_pass": preflight.get("status") == "PASS",
        "producer_source_bound": sha256_file(branch / "continuation_dimension_audit.py")
        == bindings.get("producer_source_sha256"),
        "audit_source_bound": sha256_file(Path(__file__).resolve())
        == bindings.get("postrun_audit_source_sha256"),
        "contract_bound": sha256_file(branch / "CONTRACT.md") == bindings.get("contract_sha256"),
        "bindings_hash_guarded": sha256_file(binding_path) == result["guard"].get("bindings_sha256"),
    }
    bound_inputs: dict[str, bool] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        bound_inputs[name] = path.is_file() and sha256_file(path) == item["sha256"]
    checks["all_bound_inputs_unchanged"] = all(bound_inputs.values())
    checks["all_authority_checks_pass"] = bool(result["authority_checks"]["pass"])

    producer_checks: dict[str, dict[str, bool]] = {}
    for producer in ("primary", "independent"):
        record = result[producer]
        event = record["event_cells"]
        chain = tuple(q(x) for x in record["jacobian_determinant_from_chain_rule"]["exact_bounds"])
        direct = tuple(q(x) for x in record["jacobian_determinant_direct"]["exact_bounds"])
        G_D = tuple(q(x) for x in record["G_D"]["exact_bounds"])
        curvature = tuple(q(x) for x in record["curvature"]["exact_bounds"])
        q_a = tuple(q(x) for x in record["q_a_along_first_event"]["exact_bounds"])
        producer_checks[producer] = {
            "record_validated": bool(record["validated"]),
            "event_cluster_closed_immediately": record["negative_after_cell"] == event[1] + 1,
            "curvature_positive": curvature[0] > 0,
            "G_D_negative": G_D[1] < 0,
            "q_a_positive": q_a[0] > 0,
            "chain_determinant_positive": chain[0] > 0,
            "direct_determinant_positive": direct[0] > 0,
            "determinant_forms_overlap": max(chain[0], direct[0]) <= min(chain[1], direct[1]),
        }
    checks["both_producer_records_replay"] = all(
        all(values.values()) for values in producer_checks.values()
    )

    pD = tuple(q(x) for x in result["primary"]["event_bracket_exact"])
    iD = tuple(q(x) for x in result["independent"]["event_bracket_exact"])
    intersection = (max(pD[0], iD[0]), min(pD[1], iD[1]))
    reported_intersection = tuple(
        q(x) for x in result["cross_producer"]["event_bracket_intersection_exact"]
    )
    checks["event_bracket_intersection_recomputed"] = intersection == reported_intersection and intersection[0] <= intersection[1]
    singleton = result["maximal_connected_D_solution_set"]
    checks["singleton_semantics_explicit"] = bool(
        singleton.get("type") == "SINGLETON"
        and singleton.get("cardinality") == 1
        and not singleton.get("positive_width_continuation_interval_certified")
        and singleton.get("enclosure_is_not_an_interval_of_solutions")
    )
    isolated = bool(
        all(checks.values())
        and result.get("classification") == ISOLATED_CLASSIFICATION
        and result.get("status") == "COMPLETE"
    )
    checks["isolated_classification_recomputed"] = isolated
    verified = all(checks.values())
    return {
        "schema": "lin-d1-fixed-d-continuation-dimension-postrun-audit-v1",
        "status": "VERIFIED" if verified else "FAILED",
        "completed_utc": utc_now(),
        "checks": checks,
        "bound_input_checks": bound_inputs,
        "producer_evidence_checks": producer_checks,
        "recomputed": {
            "classification": ISOLATED_CLASSIFICATION if isolated else "FIXED_D_CONTINUATION_DIMENSION_UNRESOLVED",
            "event_bracket_intersection_exact": [str(intersection[0]), str(intersection[1])],
            "zero_set_dimension": 0 if isolated else None,
            "maximal_connected_D_solution_set": "{D*}" if isolated else None,
        },
        "claim_boundary": result.get("claim_boundary"),
    }


def report(result: dict[str, Any], audit_record: dict[str, Any]) -> str:
    pdet = result["primary"]["jacobian_determinant_from_chain_rule"]["decimal_bounds"]
    idet = result["independent"]["jacobian_determinant_from_chain_rule"]["decimal_bounds"]
    D = result["maximal_connected_D_solution_set"]["D_star_certified_enclosure_decimal"]
    gap = result["toward_D0"]["D_star_minus_D0_enclosure_decimal"]
    return f"""# D1 fixed-D continuation dimension result

## Result

The fixed-model simultaneous-wall solution does **not** form a nontrivial
continuation branch in prescribed proper separation. It is an isolated root
of the two-equation map `F(a,D)=(G,h)`.

- Classification: `{result['classification']}`
- Independent audit: `{audit_record['status']}`
- Primary determinant enclosure: `{pdet}`
- Independent determinant enclosure: `{idet}`
- Certified enclosure of the singleton `D*`: `{D}`
- Enclosed `D* - D0`: `{gap}`
- Positive-width continuation interval certified: `False`

## Interpretation

Both independent interval producers enclose the full Jacobian determinant
strictly above zero. The simultaneous zero set is therefore locally
zero-dimensional. Combined with the gap-free global first-event uniqueness
cover, there is exactly one solution pair `(a*,D*)` in the declared problem.
The finite width of the reported D enclosure is numerical uncertainty around
one number; it is not a family of solutions.

This means the requested continuation toward `D0` stops at the seed: the
certified continuation distance is zero. D2A separately excludes a solution
at `D0`. A nontrivial continuation study would require prospectively varying
one additional physical model parameter rather than treating `D` as a free
degree of freedom in the unchanged model.

## Boundary

This is a static reduced-model result. It establishes no dynamical selection,
stability, collapse matching, MOTS, event horizon, radion transition, or baby
universe. No manuscript or predecessor package was changed.
"""


def manifest(branch: Path) -> dict[str, Any]:
    rows = []
    for path in sorted(branch.rglob("*")):
        if not path.is_file() or path.name in {"MANIFEST.json", "STATUS.json"} or path.suffix == ".log":
            continue
        rows.append(
            {
                "relative_path": str(path.relative_to(branch)),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return {
        "schema": "lin-d1-fixed-d-continuation-dimension-manifest-v1",
        "created_utc": utc_now(),
        "excluded": ["MANIFEST.json", "STATUS.json", "*.log"],
        "all_listed_files_hashed": True,
        "file_count": len(rows),
        "files": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True, type=Path)
    args = parser.parse_args()
    branch = args.branch.resolve()
    record = audit(branch)
    atomic_json(branch / "output" / "POSTRUN_AUDIT.json", record)
    if record["status"] != "VERIFIED":
        raise RuntimeError("post-run audit failed")
    result = json.loads((branch / "output" / "RESULT.json").read_text(encoding="utf-8"))
    atomic_text(branch / "FINAL_REPORT.md", report(result, record))
    m = manifest(branch)
    atomic_json(branch / "MANIFEST.json", m)
    written = json.loads((branch / "MANIFEST.json").read_text(encoding="utf-8"))
    for row in written["files"]:
        if sha256_file(branch / row["relative_path"]) != row["sha256"]:
            raise RuntimeError(f"manifest mismatch: {row['relative_path']}")
    print(json.dumps({"status": record["status"], "classification": result["classification"], "manifest_files": m["file_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
