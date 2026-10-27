#!/usr/bin/env python3
"""Independent record-level audit and finalization for the D1 global cover."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from fractions import Fraction


SUCCESS_CLASSIFICATION = (
    "GLOBAL_FIRST_EVENT_SIMULTANEOUS_WALL_ROOT_UNIQUE_ON_DECLARED_"
    "POSITIVE_CURVATURE_LAUNCH_INTERVAL"
)
UNRESOLVED_CLASSIFICATION = "GLOBAL_FIRST_EVENT_UNIQUENESS_UNRESOLVED"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_json(path: Path, value: Any) -> None:
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def atomic_write_text(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def q(text: str) -> Fraction:
    return Fraction(text)


def audit(branch: Path) -> dict[str, Any]:
    output = branch / "output"
    bindings_path = branch / "BINDINGS.json"
    result_path = output / "RESULT.json"
    terminal_path = output / "TERMINAL_CHECKPOINT.json"
    preflight_path = output / "PREFLIGHT.json"
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))

    checks: dict[str, bool] = {}
    checks["result_hash_matches_terminal"] = sha256_file(result_path) == terminal.get("result_sha256")
    checks["terminal_classification_matches_result"] = terminal.get("classification") == result.get("classification")
    checks["terminal_status_matches_result"] = terminal.get("status") == result.get("status")
    checks["preflight_pass"] = preflight.get("status") == "PASS"
    checks["guard_agreement"] = result.get("guard") == terminal.get("guard") == preflight.get("guard")
    checks["bindings_hash_in_guard"] = sha256_file(bindings_path) == result["guard"].get("bindings_sha256")
    checks["producer_hash_in_bindings"] = (
        sha256_file(branch / "global_uniqueness_cover.py") == bindings.get("producer_source_sha256")
    )
    checks["contract_hash_in_bindings"] = sha256_file(branch / "CONTRACT.md") == bindings.get("contract_sha256")
    checks["audit_hash_in_bindings"] = sha256_file(Path(__file__).resolve()) == bindings.get("postrun_audit_source_sha256")

    import_checks: dict[str, bool] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        import_checks[name] = path.is_file() and sha256_file(path) == item["sha256"]
    checks["all_bound_inputs_unchanged"] = all(import_checks.values())

    rows = sorted(result["terminal_boxes"], key=lambda row: q(row["a_exact_bounds"][0]))
    contiguous = bool(rows)
    previous = Fraction(0)
    root_count = 0
    unresolved_count = 0
    evidence_failures: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        lo, hi = map(q, row["a_exact_bounds"])
        if lo != previous or hi <= lo:
            contiguous = False
        previous = hi
        classification = row["classification"]
        if classification == "CERTIFIED_D1_UNIQUE_ROOT":
            root_count += 1
            if not row["record"].get("pass"):
                evidence_failures.append({"index": index, "reason": "root authority false"})
        elif classification == "NEGATIVE_CURVATURE_EXCLUDED":
            curvature = row["record"]["curvature"]
            for producer in ("primary", "independent"):
                if q(curvature[producer]["exact_bounds"][1]) >= 0:
                    evidence_failures.append({"index": index, "reason": f"{producer} curvature not negative"})
        elif classification == "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED":
            record = row["record"]
            if not record.get("qualified_dual_exclusion") or not record.get("same_h_sign"):
                evidence_failures.append({"index": index, "reason": "dual exclusion flag false"})
            for producer in ("primary", "independent"):
                evidence = record[producer]
                if not (
                    evidence.get("validated")
                    and evidence.get("G_s_strictly_negative")
                    and evidence.get("h_excludes_zero")
                    and evidence.get("negative_after_cell") == evidence.get("event_cells", [None, None])[1] + 1
                ):
                    evidence_failures.append({"index": index, "reason": f"{producer} event evidence failed"})
            if record["primary"].get("h_sign") != record["independent"].get("h_sign"):
                evidence_failures.append({"index": index, "reason": "producer h signs disagree"})
        elif classification == "UNRESOLVED":
            unresolved_count += 1
        else:
            evidence_failures.append({"index": index, "reason": f"unknown classification {classification}"})

    v0 = Fraction(float("0.1").as_integer_ratio()[0], float("0.1").as_integer_ratio()[1])
    contiguous = contiguous and previous == v0
    checks["exact_gap_free_cover"] = contiguous
    checks["exactly_one_certified_root_box"] = root_count == 1
    checks["all_terminal_evidence_replays"] = not evidence_failures
    checks["recorded_unresolved_count_agrees"] = unresolved_count == len(result.get("unresolved", []))
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    checks["classification_counts_recomputed"] = counts == result.get("classification_counts")

    recomputed_pass = contiguous and root_count == 1 and unresolved_count == 0 and not evidence_failures
    expected_classification = SUCCESS_CLASSIFICATION if recomputed_pass else UNRESOLVED_CLASSIFICATION
    expected_status = "COMPLETE" if recomputed_pass else "INCOMPLETE"
    checks["terminal_classification_recomputed"] = result.get("classification") == expected_classification
    checks["terminal_status_recomputed"] = result.get("status") == expected_status
    verified = all(checks.values())
    return {
        "schema": "lin-d1-global-first-event-uniqueness-postrun-audit-v1",
        "status": "VERIFIED" if verified else "FAILED",
        "completed_utc": utc_now(),
        "checks": checks,
        "bound_input_checks": import_checks,
        "recomputed": {
            "terminal_box_count": len(rows),
            "classification_counts": counts,
            "root_box_count": root_count,
            "unresolved_box_count": unresolved_count,
            "exact_gap_free_cover": contiguous,
            "classification": expected_classification,
            "status": expected_status,
        },
        "evidence_failures": evidence_failures,
        "claim_boundary": result.get("claim_boundary"),
    }


def report_text(result: dict[str, Any], audit_record: dict[str, Any]) -> str:
    counts = result["classification_counts"]
    unresolved = len(result.get("unresolved", []))
    if result["classification"] == SUCCESS_CLASSIFICATION and audit_record["status"] == "VERIFIED":
        conclusion = (
            "The certified D1 root is the only positive-curvature simultaneous-wall solution "
            "on the complete declared launch interval for first-event placement."
        )
    else:
        conclusion = (
            "Global uniqueness was not certified. The exact unresolved boxes in RESULT.json "
            "are the complete obstruction record."
        )
    return f"""# D1 global first-event uniqueness result

## Result

{conclusion}

- Classification: `{result['classification']}`
- Post-run audit: `{audit_record['status']}`
- Exact gap-free cover: `{result['coverage_audit']['exact_contiguous_cover']}`
- Terminal boxes: {result['terminal_box_count']}
- Certified root boxes: {counts.get('CERTIFIED_D1_UNIQUE_ROOT', 0)}
- Negative-curvature exclusions: {counts.get('NEGATIVE_CURVATURE_EXCLUDED', 0)}
- Dual-producer first-event scalar exclusions: {counts.get('FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED', 0)}
- Unresolved boxes: {unresolved}
- Dual-evaluated boxes including refined attempts: {result['dual_evaluated_box_count_including_pre_split_attempts']}
- Accumulated wall time: {result['runtime']['accumulated_wall_seconds']:.1f} s
- Worker processes: {result['runtime']['workers']}

## What was established

The existing interval-Newton certificate supplies exactly one root in the
inherited narrow D1 box. The new exact cover accounts for every launch value
outside that box. Every admitted positive-curvature exclusion was reproduced
by both the validated second-order Taylor/Picard flow and the independent
fifth-order Taylor/Picard flow: both locate the first transverse upper-Israel
event and enclose the scalar residual strictly on the same side of zero.

## Boundary of inference

This is a global uniqueness result only for the declared reduced static
first-event shooting problem. It does not establish dynamical selection,
stability, collapse matching, a MOTS, an event horizon, a radion transition,
or a baby universe. D2A and the manuscripts were not changed.
"""


def build_manifest(branch: Path) -> dict[str, Any]:
    excluded_names = {"MANIFEST.json", "STATUS.json"}
    records = []
    for path in sorted(branch.rglob("*")):
        if not path.is_file() or path.name in excluded_names or path.suffix == ".log":
            continue
        records.append(
            {
                "relative_path": str(path.relative_to(branch)),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return {
        "schema": "lin-d1-global-first-event-uniqueness-manifest-v1",
        "created_utc": utc_now(),
        "root": str(branch),
        "excluded_mutable_or_runtime_files": ["MANIFEST.json", "output/STATUS.json", "*.log"],
        "all_listed_files_hashed": True,
        "file_count": len(records),
        "files": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", required=True, type=Path)
    args = parser.parse_args()
    branch = args.branch.resolve()
    record = audit(branch)
    atomic_write_json(branch / "output" / "POSTRUN_AUDIT.json", record)
    if record["status"] != "VERIFIED":
        raise RuntimeError("post-run audit failed")
    result = json.loads((branch / "output" / "RESULT.json").read_text(encoding="utf-8"))
    atomic_write_text(branch / "FINAL_REPORT.md", report_text(result, record))
    manifest = build_manifest(branch)
    atomic_write_json(branch / "MANIFEST.json", manifest)
    # Verify the written manifest immediately from the filesystem.
    written = json.loads((branch / "MANIFEST.json").read_text(encoding="utf-8"))
    for item in written["files"]:
        if sha256_file(branch / item["relative_path"]) != item["sha256"]:
            raise RuntimeError(f"manifest verification failed: {item['relative_path']}")
    print(json.dumps({"status": record["status"], "classification": result["classification"], "manifest_files": manifest["file_count"]}, sort_keys=True))


if __name__ == "__main__":
    main()
