#!/usr/bin/env python3
"""Independent integrity and decision audit for the D1 qualification packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np


RAW_GATE = 1e-4
PERTURB_GATES = {
    "acceleration_minimum": 1e-12,
    "acceleration_maximum": 1e-2,
    "wall": 2e-5,
    "gauge_absolute": 2e-4,
    "departure": 1e-4,
    "final_scalar_velocity_minimum": 1e-12,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def order(coarse: float, fine: float, coarse_n: int, fine_n: int):
    if coarse <= 0.0 or fine <= 0.0 or coarse == fine:
        return None
    return math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1))


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
    evidence_path = output / "EVIDENCE.npz"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    bindings = json.loads((namespace / "BINDINGS.json").read_text(encoding="utf-8"))
    freeze = json.loads((namespace / "FREEZE_RECORD.json").read_text(encoding="utf-8"))

    checks = {
        "terminal_complete": result["status"] == terminal["status"] == "COMPLETE",
        "terminal_classification": result["classification"] == terminal["classification"],
        "result_hash": sha256(result_path) == terminal["result_sha256"],
        "evidence_hash": sha256(evidence_path) == terminal["evidence_sha256"],
        "contract_hash": result["contract_sha256"] == sha256(namespace / "CONTRACT.md"),
        "bindings_hash": result["bindings_sha256"] == sha256(namespace / "BINDINGS.json"),
        "source_hash": result["source_sha256"]
        == sha256(namespace / "d1_raw_gh_qualification.py"),
    }

    freeze_matches = {
        entry["path"]: sha256(namespace / entry["path"]) == entry["sha256"]
        for entry in freeze["files"]
    }
    parent_matches = {
        entry["path"]: sha256(root / entry["path"]) == entry["sha256"]
        for entry in bindings["parents"] + bindings["production_sources"]
    }
    checks["frozen_sources"] = all(freeze_matches.values())
    checks["parent_sources"] = all(parent_matches.values())

    raw = result["raw_gh_extension"]
    levels = raw["levels"]
    expected_grids = [[nx, 241] for nx in (65, 97, 129, 193, 257, 385, 513)]
    passing = [
        index
        for index, level in enumerate(levels)
        if level["finite"] and level["maximum_normalized"] <= RAW_GATE
    ]
    orders = [
        order(
            left["maximum_normalized"],
            right["maximum_normalized"],
            left["grid"][0],
            right["grid"][0],
        )
        for left, right in zip(levels[:-1], levels[1:])
    ]
    parent_result_path = root / "branches/02-event-horizon/lin-d1-gh-well-balance-discriminator-20261004T203750Z/output/RESULT.json"
    parent_result = json.loads(parent_result_path.read_text(encoding="utf-8"))
    parent_anchor = next(
        level
        for level in parent_result["producer_B"]["levels"]
        if level["grid"] == [257, 241]
    )
    anchor = next(level for level in levels if level["grid"] == [257, 241])
    expected_raw_gates = {
        "anchor_exact": anchor == parent_anchor,
        "finite": all(level["finite"] for level in levels),
        "monotone": all(
            right["maximum_normalized"] < left["maximum_normalized"]
            for left, right in zip(levels[:-1], levels[1:])
        ),
        "last_order": orders[-1] is not None and 2.0 <= orders[-1] <= 6.0,
        "finest": levels[-1]["maximum_normalized"] <= RAW_GATE,
        "two_consecutive": len(passing) >= 2
        and passing[-2:] == [len(levels) - 2, len(levels) - 1],
    }
    raw_passed = all(expected_raw_gates.values())
    checks.update(
        {
            "raw_grids": [level["grid"] for level in levels] == expected_grids,
            "raw_gates": raw["gates"] == expected_raw_gates,
            "raw_passing_indices": raw["passing_indices"] == passing,
            "raw_orders": all(
                math.isclose(record["order"], expected, rel_tol=0.0, abs_tol=1e-14)
                for record, expected in zip(raw["orders"], orders)
            ),
            "raw_decision": raw["passed"] == raw_passed,
        }
    )

    perturbation_checks = {}
    checkpoint_checks = {}
    if raw_passed:
        perturbation = result["perturbation"]
        records = perturbation["records"]
        expected_step_passes = []
        last_q = None
        last_v = None
        for step in range(1, 9):
            checkpoint_path = output / f"PERTURB_STEP_{step}.npz"
            record_path = output / f"PERTURB_STEP_{step}.json"
            exists = checkpoint_path.exists() and record_path.exists()
            expected_exists = step <= len(records)
            compatible = False
            finite = False
            if exists:
                with np.load(checkpoint_path, allow_pickle=False) as checkpoint:
                    compatible = (
                        int(checkpoint["step"]) == step
                        and float(checkpoint["dt"]) == 0.000125
                        and str(checkpoint["contract_sha256"])
                        == result["contract_sha256"]
                        and str(checkpoint["bindings_sha256"])
                        == result["bindings_sha256"]
                        and str(checkpoint["source_sha256"]) == result["source_sha256"]
                        and str(checkpoint["parent_result_sha256"])
                        == result["parent_result_sha256"]
                    )
                    finite = bool(
                        np.all(np.isfinite(checkpoint["q"]))
                        and np.all(np.isfinite(checkpoint["v"]))
                    )
                    if step == len(records):
                        last_q = checkpoint["q"].copy()
                        last_v = checkpoint["v"].copy()
            checkpoint_checks[str(step)] = {
                "presence": exists == expected_exists,
                "compatible": compatible if expected_exists else True,
                "finite": finite if expected_exists else True,
            }
            if not expected_exists:
                continue
            record = records[step - 1]
            expected_gates = {
                "finite": bool(record["gates"]["finite"]),
                "positivity": bool(record["positivity"]["passed"]),
                "wall": record["wall"] <= PERTURB_GATES["wall"],
                "gauge": bool(
                    record["gauge"]["finite"]
                    and record["gauge"]["maximum_absolute"]
                    <= PERTURB_GATES["gauge_absolute"]
                ),
                "hamiltonian": record["hamiltonian_change"]
                <= record["hamiltonian_limit"],
                "departure": record["departure_from_equilibrium"]
                <= PERTURB_GATES["departure"],
            }
            expected_step_passes.append(
                record["gates"] == expected_gates
                and record["passed"] == all(expected_gates.values())
            )

        response = perturbation["initial_acceleration"]
        expected_response_gates = {
            "initial_amplitude": 0.5e-6
            <= perturbation["initial_scalar_amplitude"]
            <= 1e-6,
            "initial_acceleration_finite": bool(response["finite"]),
            "initial_acceleration_nonzero": response["maximum_normalized"]
            > PERTURB_GATES["acceleration_minimum"],
            "initial_acceleration_bounded": response["maximum_normalized"]
            <= PERTURB_GATES["acceleration_maximum"],
            "all_steps": len(records) == 8
            and all(record["passed"] for record in records),
            "dynamic_response_nonzero": len(records) == 8
            and records[-1]["scalar_velocity"]
            > PERTURB_GATES["final_scalar_velocity_minimum"],
        }
        perturbation_passed = all(expected_response_gates.values())
        perturbation_checks = {
            "step_decisions": all(expected_step_passes),
            "response_gates": perturbation["gates"] == expected_response_gates,
            "decision": perturbation["passed"] == perturbation_passed,
            "all_checkpoints": all(
                all(values.values()) for values in checkpoint_checks.values()
            ),
        }
        with np.load(evidence_path, allow_pickle=False) as evidence:
            shape = evidence["shape"]
            perturbation_checks["shape_boundaries"] = bool(
                np.count_nonzero(shape[0]) == 0
                and np.count_nonzero(shape[-1]) == 0
                and np.all(np.isfinite(shape))
            )
            perturbation_checks["final_state_matches"] = bool(
                len(records) == 0
                or (
                    np.array_equal(evidence["q_final"], last_q)
                    and np.array_equal(evidence["v_final"], last_v)
                )
            )
        checks["perturbation"] = all(perturbation_checks.values())
        expected_classification = (
            "D1_RAW_GH_TWO_LEVEL_GATE_PASS__BOUNDED_SHORT_SCALAR_RESPONSE"
            if perturbation_passed
            else "D1_RAW_GH_TWO_LEVEL_GATE_PASS__PERTURBED_RESPONSE_BLOCKED"
        )
    else:
        checks["perturbation_not_run"] = result["perturbation"]["status"] == "NOT_RUN_RAW_GATE_FAILED"
        expected_classification = (
            "D1_RAW_GH_TWO_LEVEL_GATE_NOT_MET__PERTURBATION_NOT_RUN"
        )

    checks["classification"] = result["classification"] == expected_classification
    passed = all(checks.values())
    audit = {
        "schema": "lin-d1-raw-gh-dynamical-independent-audit-v1",
        "classification": "VERIFIED" if passed else "NOT_VERIFIED",
        "producer_classification": result["classification"],
        "checks": checks,
        "raw_expected_gates": expected_raw_gates,
        "freeze_matches": freeze_matches,
        "parent_matches": parent_matches,
        "checkpoint_checks": checkpoint_checks,
        "perturbation_checks": perturbation_checks,
        "claim_boundary": "finite-resolution raw-GH gate and bounded short scalar response only",
    }
    atomic_json(output / "INDEPENDENT_AUDIT.json", audit)
    print(json.dumps(audit, indent=2, sort_keys=True))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
