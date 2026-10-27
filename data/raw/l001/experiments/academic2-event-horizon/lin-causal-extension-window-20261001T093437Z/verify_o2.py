#!/usr/bin/env python3
"""Independent archive and reduction verifier for the O2 null pilot."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from pathlib import Path

import numpy as np


TERMINALS = (1744, 1760, 1776, 1792)
COMMON_STEPS = tuple(range(512, 1537, 64))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, raw = tempfile.mkstemp(prefix=f".{path.name}.tmp-", dir=path.parent)
    temporary = Path(raw)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        path.chmod(0o444)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary.exists():
            temporary.unlink()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads(args.contract.read_text())
    result_path = args.output / "O2_RESULT.json"
    archive_path = args.output / "O2_RESULT.npz"
    result = json.loads(result_path.read_text())
    checks: dict[str, bool] = {}

    def check(name: str, value: bool) -> None:
        checks[name] = bool(value)

    check("contract_schema", contract.get("schema") == "stable-band-multiterminal-null-pilot-contract-v1")
    check("result_schema", result.get("schema") == "stable-band-multiterminal-null-pilot-result-v1")
    check("result_complete", result.get("status") == "COMPLETE")
    check("contract_binding", result.get("contract_sha256") == sha256(args.contract))
    check("result_archive_binding", result.get("archive_sha256") == sha256(archive_path))
    check("conditional_spacetime_disclosed", result.get("conditional_on_inherited_spacetime") is True)
    check("boundary_unresolved_disclosed", result.get("boundary_acceleration_compatibility_resolved") is False)
    firewall = result.get("claim_firewall", {})
    check("event_horizon_firewall", firewall.get("event_horizon_claim_authorized") is False)
    check("future_infinity_firewall", firewall.get("future_null_infinity_claim_authorized") is False)
    check("wall_not_infinity", firewall.get("physical_wall_is_infinity") is False)

    root = args.contract.resolve().parent
    for relative, expected in contract["local_files"].items():
        candidate = root / relative
        check(f"local_unchanged:{relative}", candidate.is_file() and sha256(candidate) == expected)
    for raw, expected in contract["external_files"].items():
        candidate = Path(raw)
        check(f"external_unchanged:{raw}", candidate.is_file() and sha256(candidate) == expected)

    trace_pass = True
    unit_records = {}
    for spec in contract["trace_specs"]:
        tag = spec["tag"]
        record_path = args.output / "trace-units" / f"{tag}.json"
        unit_path = args.output / "trace-units" / f"{tag}.npz"
        record = json.loads(record_path.read_text())
        unit_records[tag] = record
        check(f"{tag}:schema", record.get("schema") == "stable-band-null-trace-unit-v1")
        check(f"{tag}:contract", record.get("contract_sha256") == sha256(args.contract))
        check(f"{tag}:spec", record.get("spec") == spec)
        check(f"{tag}:archive", record.get("archive_sha256") == sha256(unit_path))
        check(f"{tag}:result_record", result["trace_units"][tag]["record_sha256"] == sha256(record_path))
        check(f"{tag}:result_archive", result["trace_units"][tag]["archive_sha256"] == sha256(unit_path))
        with np.load(unit_path, allow_pickle=False) as arrays:
            positions = arrays["positions"]
            velocities = arrays["velocities"]
            residual = arrays["normalized_null_residual"]
            in_domain = arrays["in_domain"]
            check(f"{tag}:finite_positions", bool(np.all(np.isfinite(positions))))
            check(f"{tag}:finite_velocities", bool(np.all(np.isfinite(velocities))))
            check(f"{tag}:finite_residual", bool(np.all(np.isfinite(residual))))
            check(f"{tag}:labels", positions.shape[1] == int(spec["labels"]))
            check(f"{tag}:in_domain", bool(np.all(in_domain == 1)))
            check(
                f"{tag}:residual_scalar",
                float(np.max(residual)) == record["trace"]["maximum_normalized_null_defect"],
            )
            check(
                f"{tag}:residual_gate",
                float(np.max(residual)) <= contract["gates"]["maximum_normalized_null_defect"],
            )
        local_pass = record["trace"].get("all_checks_pass") is True
        trace_pass = trace_pass and local_pass
        check(f"{tag}:trace_gate", local_pass)

    pairs = list(itertools.combinations(TERMINALS, 2))
    pair_tensor = np.empty((len(pairs), len(COMMON_STEPS)), dtype=float)
    primary_projection = True
    for pair_index, (left, right) in enumerate(pairs):
        key = f"T{left}-T{right}"
        rows = result["pairwise_primary"][key]
        check(f"{key}:row_count", len(rows) == len(COMMON_STEPS))
        for step_index, step in enumerate(COMMON_STEPS):
            row = rows[step_index]
            check(f"{key}:step:{step}", row["step"] == step)
            pair_tensor[pair_index, step_index] = row["native_cell_fraction"]
            primary_projection = primary_projection and row["projection_and_coverage_pass"]

    control_maxima = {}
    control_projection = True
    for spec in contract["trace_specs"]:
        if spec["role"] != "control":
            continue
        rows = result["control_comparisons"][spec["tag"]]
        control_maxima[spec["tag"]] = max(row["native_cell_fraction"] for row in rows)
        control_projection = control_projection and all(row["projection_and_coverage_pass"] for row in rows)
    check("control_maxima_rederived", control_maxima == result["control_maximum_native_cell_fraction"])
    envelope = max(control_maxima.values())
    check("numerical_envelope_rederived", envelope == result["numerical_envelope_native_cell_fraction"])

    d_all = np.max(pair_tensor, axis=0)
    tail_indices = [index for index, pair in enumerate(pairs) if pair[0] != TERMINALS[0]]
    d_tail = np.max(pair_tensor[tail_indices], axis=0)
    target = float(contract["gates"]["localization_target_native_cell_fraction"])
    budget = target * float(contract["gates"]["numerical_budget_fraction_of_target"])
    localized = np.asarray([
        bool(primary_projection and control_projection and envelope <= budget and value + 2.0 * envelope <= target)
        for value in d_all
    ], dtype=np.uint8)
    technical = bool(trace_pass and primary_projection and control_projection)
    pass_count = int(np.sum(localized))
    required = int(contract["gates"]["required_localized_steps"])
    if not technical:
        classification = "TECHNICALLY-INCONCLUSIVE"
    elif pass_count >= required:
        classification = "FINITE-ARCHIVE-TERMINAL-SHEET-LOCALIZATION-SUPPORTED"
    else:
        classification = "VALID-NO-EPOCH1-TERMINAL-LOCALIZATION-FUTURE-EXTENSION-REQUIRED"

    with np.load(archive_path, allow_pickle=False) as arrays:
        check("archive_steps", np.array_equal(arrays["primary_steps"], np.asarray(COMMON_STEPS, dtype=np.int64)))
        check("archive_pairs", np.array_equal(arrays["primary_terminal_pairs"], np.asarray(pairs, dtype=np.int64)))
        check("archive_pairwise", np.array_equal(arrays["pairwise_native_cell_fraction"], pair_tensor))
        check("archive_all_diameter", np.array_equal(arrays["all_terminal_diameter_native_cell_fraction"], d_all))
        check("archive_tail_diameter", np.array_equal(arrays["tail_terminal_diameter_native_cell_fraction"], d_tail))
        check("archive_localized", np.array_equal(arrays["localized_mask"], localized))
        archived_envelope = float(
            np.asarray(arrays["numerical_envelope_native_cell_fraction"]).reshape(-1)[0]
        )
        check("archive_envelope", archived_envelope == envelope)
    check("technical_rederived", result.get("technically_complete") is technical)
    check("localized_count_rederived", result.get("localized_step_count") == pass_count)
    check("classification_rederived", result.get("classification") == classification)

    failed = sorted(name for name, passed in checks.items() if not passed)
    report = {
        "schema": "stable-band-multiterminal-null-pilot-independent-verification-v1",
        "classification": "VERIFIED" if not failed else "NOT_VERIFIED",
        "contract_sha256": sha256(args.contract),
        "producer_result_sha256": sha256(result_path),
        "producer_archive_sha256": sha256(archive_path),
        "verifier_sha256": sha256(Path(__file__)),
        "check_count": len(checks),
        "failed_checks": failed,
        "checks": checks,
        "rederived_scientific_classification": classification,
        "rederived_localized_step_count": pass_count,
        "rederived_numerical_envelope_native_cell_fraction": envelope,
        "claim_boundary": {
            "finite_archive_only": True,
            "event_horizon_established": False,
            "boundary_acceleration_compatibility_resolved": False
        }
    }
    if args.report.exists():
        raise SystemExit("refusing to overwrite verification report")
    atomic_json(args.report, report)
    print(json.dumps({
        "classification": report["classification"],
        "check_count": report["check_count"],
        "failed_checks": failed,
        "rederived_scientific_classification": classification,
        "rederived_localized_step_count": pass_count,
    }, indent=2, sort_keys=True))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
