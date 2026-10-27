#!/usr/bin/env python3
"""Roundoff-only audit of the frozen perturbation amplitude false failure."""

from __future__ import annotations

import argparse
import datetime as dt
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


def verify_bindings(root: Path, namespace: Path):
    bindings = json.loads((namespace / "BINDINGS.json").read_text())
    records = []
    for entry in bindings["parents"]:
        actual = sha256(root / entry["path"])
        if actual != entry["sha256"]:
            raise RuntimeError(f"binding changed: {entry['path']} {actual}")
        records.append({"path": entry["path"], "sha256": actual})
    return records


def evaluate(parent_result: dict, parent_audit: dict, evidence) -> dict:
    shape = evidence["shape"]
    phi_background = evidence["q_background"][:, :, 7]
    declared_increment = EPSILON * shape
    stored_phi = phi_background + declared_increment
    measured_increment = float(np.max(np.abs(stored_phi - phi_background)))
    exact_increment_maximum = float(np.max(np.abs(declared_increment)))
    background_scale = max(1.0, float(np.max(np.abs(phi_background))))
    allowance = 8.0 * np.finfo(np.float64).eps * background_scale
    excess = max(0.0, measured_increment - EPSILON)
    producer_perturbation = parent_result["perturbation"]
    other_response_gates = {
        key: value
        for key, value in producer_perturbation["gates"].items()
        if key != "initial_amplitude"
    }
    gates = {
        "shape_finite": bool(np.all(np.isfinite(shape))),
        "shape_nonnegative": bool(np.min(shape) >= 0.0),
        "shape_unit_bounded": bool(np.max(shape) <= 1.0),
        "shape_compact_walls_zero": bool(
            np.count_nonzero(shape[0]) == 0 and np.count_nonzero(shape[-1]) == 0
        ),
        "declared_increment_bounded": exact_increment_maximum <= EPSILON,
        "stored_increment_within_roundoff": measured_increment <= EPSILON + allowance,
        "excess_within_roundoff": excess <= allowance,
        "producer_measurement_reproduced": measured_increment
        == producer_perturbation["initial_scalar_amplitude"],
        "producer_independently_verified": parent_audit["classification"] == "VERIFIED",
        "all_other_response_gates": all(other_response_gates.values()),
        "all_step_gates": len(producer_perturbation["records"]) == 8
        and all(record["passed"] for record in producer_perturbation["records"]),
    }
    passed = all(gates.values())
    return {
        "declared_amplitude": EPSILON,
        "exact_increment_maximum": exact_increment_maximum,
        "measured_stored_increment": measured_increment,
        "measured_excess": excess,
        "representation_allowance": allowance,
        "excess_fraction_of_allowance": excess / allowance if allowance else None,
        "other_response_gates": other_response_gates,
        "gates": gates,
        "passed": passed,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    namespace = Path(__file__).resolve().parent
    parent = root / "branches/02-event-horizon/lin-d1-raw-gh-dynamical-qualification-20261005T000023Z"
    bindings_verified = verify_bindings(root, namespace)
    parent_result = json.loads((parent / "output/RESULT.json").read_text())
    parent_audit = json.loads((parent / "output/INDEPENDENT_AUDIT.json").read_text())
    with np.load(parent / "output/EVIDENCE.npz", allow_pickle=False) as evidence:
        calculation = evaluate(parent_result, parent_audit, evidence)
    classification = (
        "D1_SCALAR_RESPONSE_PASS__FROZEN_AMPLITUDE_GATE_FALSE_FAILURE"
        if calculation["passed"]
        else "D1_SCALAR_RESPONSE_REMAINS_BLOCKED__ROUNDOFF_AUDIT_FAIL"
    )
    result = {
        "schema": "lin-d1-raw-gh-roundoff-audit-result-v1",
        "status": "COMPLETE",
        "classification": classification,
        "completed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "contract_sha256": sha256(namespace / "CONTRACT.md"),
        "bindings_sha256": sha256(namespace / "BINDINGS.json"),
        "source_sha256": sha256(namespace / "roundoff_audit.py"),
        "bindings_verified": bindings_verified,
        "parent_producer_classification": parent_result["classification"],
        "parent_producer_classification_unchanged": True,
        "calculation": calculation,
        "claim_boundary": "roundoff audit only; no numerical evolution rerun",
    }
    atomic_json(output / "RESULT.json", result)
    terminal = {
        "schema": "lin-d1-raw-gh-roundoff-audit-terminal-v1",
        "status": "COMPLETE",
        "classification": classification,
        "result_sha256": sha256(output / "RESULT.json"),
        "completed_utc": result["completed_utc"],
    }
    atomic_json(output / "TERMINAL.json", terminal)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

