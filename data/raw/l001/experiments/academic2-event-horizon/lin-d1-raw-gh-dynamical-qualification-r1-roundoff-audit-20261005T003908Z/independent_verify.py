#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

import numpy as np


EPSILON = 1e-6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--namespace", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    namespace = args.namespace.resolve()
    output = namespace / "output"
    result_path = output / "RESULT.json"
    terminal_path = output / "TERMINAL.json"
    result = json.loads(result_path.read_text())
    terminal = json.loads(terminal_path.read_text())
    freeze = json.loads((namespace / "FREEZE_RECORD.json").read_text())
    bindings = json.loads((namespace / "BINDINGS.json").read_text())
    parent = root / "branches/02-event-horizon/lin-d1-raw-gh-dynamical-qualification-20261005T000023Z"
    parent_result = json.loads((parent / "output/RESULT.json").read_text())
    parent_audit = json.loads((parent / "output/INDEPENDENT_AUDIT.json").read_text())

    parent_matches = {
        entry["path"]: sha256(root / entry["path"]) == entry["sha256"]
        for entry in bindings["parents"]
    }
    freeze_matches = {
        entry["path"]: sha256(namespace / entry["path"]) == entry["sha256"]
        for entry in freeze["files"]
    }
    with np.load(parent / "output/EVIDENCE.npz", allow_pickle=False) as evidence:
        shape = evidence["shape"]
        phi_background = evidence["q_background"][:, :, 7]
        declared = EPSILON * shape
        stored = phi_background + declared
        measured = float(np.max(np.abs(stored - phi_background)))
        exact_maximum = float(np.max(np.abs(declared)))
        allowance = 8.0 * np.finfo(np.float64).eps * max(
            1.0, float(np.max(np.abs(phi_background)))
        )
        excess = max(0.0, measured - EPSILON)

    other = {
        key: value
        for key, value in parent_result["perturbation"]["gates"].items()
        if key != "initial_amplitude"
    }
    expected_gates = {
        "shape_finite": bool(np.all(np.isfinite(shape))),
        "shape_nonnegative": bool(np.min(shape) >= 0.0),
        "shape_unit_bounded": bool(np.max(shape) <= 1.0),
        "shape_compact_walls_zero": bool(
            np.count_nonzero(shape[0]) == 0 and np.count_nonzero(shape[-1]) == 0
        ),
        "declared_increment_bounded": exact_maximum <= EPSILON,
        "stored_increment_within_roundoff": measured <= EPSILON + allowance,
        "excess_within_roundoff": excess <= allowance,
        "producer_measurement_reproduced": measured
        == parent_result["perturbation"]["initial_scalar_amplitude"],
        "producer_independently_verified": parent_audit["classification"] == "VERIFIED",
        "all_other_response_gates": all(other.values()),
        "all_step_gates": len(parent_result["perturbation"]["records"]) == 8
        and all(record["passed"] for record in parent_result["perturbation"]["records"]),
    }
    passed = all(expected_gates.values())
    expected_classification = (
        "D1_SCALAR_RESPONSE_PASS__FROZEN_AMPLITUDE_GATE_FALSE_FAILURE"
        if passed
        else "D1_SCALAR_RESPONSE_REMAINS_BLOCKED__ROUNDOFF_AUDIT_FAIL"
    )
    calculation = result["calculation"]
    checks = {
        "terminal": result["status"] == terminal["status"] == "COMPLETE",
        "terminal_classification": result["classification"] == terminal["classification"],
        "result_hash": sha256(result_path) == terminal["result_sha256"],
        "contract_hash": result["contract_sha256"] == sha256(namespace / "CONTRACT.md"),
        "bindings_hash": result["bindings_sha256"] == sha256(namespace / "BINDINGS.json"),
        "source_hash": result["source_sha256"] == sha256(namespace / "roundoff_audit.py"),
        "parents": all(parent_matches.values()),
        "freeze": all(freeze_matches.values()),
        "gates": calculation["gates"] == expected_gates,
        "numbers": calculation["declared_amplitude"] == EPSILON
        and calculation["exact_increment_maximum"] == exact_maximum
        and calculation["measured_stored_increment"] == measured
        and calculation["measured_excess"] == excess
        and calculation["representation_allowance"] == allowance,
        "decision": calculation["passed"] == passed
        and result["classification"] == expected_classification,
        "parent_unchanged": result["parent_producer_classification"]
        == parent_result["classification"]
        and result["parent_producer_classification_unchanged"] is True,
    }
    verified = all(checks.values())
    audit = {
        "schema": "lin-d1-raw-gh-roundoff-independent-audit-v1",
        "classification": "VERIFIED" if verified else "NOT_VERIFIED",
        "corrected_classification": result["classification"],
        "checks": checks,
        "expected_gates": expected_gates,
        "parent_matches": parent_matches,
        "freeze_matches": freeze_matches,
        "measured_excess": excess,
        "representation_allowance": allowance,
        "scope": "independent roundoff audit; no evolution rerun",
    }
    atomic_json(output / "INDEPENDENT_AUDIT.json", audit)
    print(json.dumps(audit, indent=2, sort_keys=True))
    raise SystemExit(0 if verified else 1)


if __name__ == "__main__":
    main()

