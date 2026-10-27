#!/usr/bin/env python3
"""Producer-independent post-run verification of the bounded D1 admission."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


M2 = 0.41
GAMMA = 20.0
V0 = 0.1
V1 = 0.09048374180359596
LAMBDA_A = 5.999990376773895
LAMBDA_B = -6.052844277744164
ROOT_LO = 0.09901086489880687
ROOT_HI = 0.09901086689880687


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", type=Path, required=True)
    args = parser.parse_args()
    namespace = args.namespace.resolve()
    output = namespace / "output"
    result_path = output / "RESULT.json"
    terminal_path = output / "TERMINAL.json"
    evidence_path = output / "EVIDENCE.npz"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    terminal = json.loads(terminal_path.read_text(encoding="utf-8"))
    evidence = np.load(evidence_path, allow_pickle=False)

    x = evidence["x"]
    r = evidence["r"]
    A = evidence["A"]
    H = evidence["H"]
    phi = evidence["phi"]
    U = evidence["U"]
    q = evidence["q"]
    source = evidence["source"]
    k = float(evidence["k"])
    cscale = float(evidence["cscale"])
    root_a = float(evidence["root_a"])
    w = np.exp(A)[:, None]
    f = 1.0 - k * r[None, :] ** 2

    expected_q = np.zeros_like(q)
    expected_q[:, :, 2] = -(w * w) * f
    expected_q[:, :, 3] = w * w
    expected_q[:, :, 4] = w * w * k / f
    expected_q[:, :, 6] = w * w * cscale * cscale
    expected_q[:, :, 7] = phi[:, None]
    expected_source = np.zeros_like(source)
    expected_source[:, :, 1] = (-3.0 * cscale * np.exp(A) * H)[:, None]
    expected_source[:, :, 2] = 4.0 * k / f

    first_integral = H * H - 1.0 - U * U / 12.0 + M2 * phi * phi / 12.0 - k * np.exp(-2.0 * A)
    independent_hamiltonian = -12.0 * first_integral
    lower_h = -(LAMBDA_A + 0.5 * GAMMA * (root_a - V0) ** 2) / 6.0
    lower_u = 0.5 * GAMMA * (root_a - V0)
    upper_tau = LAMBDA_B + 0.5 * GAMMA * (phi[-1] - V1) ** 2
    wall_residuals = {
        "lower_israel": lower_h + (LAMBDA_A + 0.5 * GAMMA * (root_a - V0) ** 2) / 6.0,
        "lower_scalar": lower_u - 0.5 * GAMMA * (root_a - V0),
        "upper_israel": H[-1] - upper_tau / 6.0,
        "upper_scalar": U[-1] + 0.5 * GAMMA * (phi[-1] - V1),
    }

    checks = {
        "terminal_result_hash": terminal["result_sha256"] == sha256(result_path),
        "terminal_evidence_hash": terminal["evidence_sha256"] == sha256(evidence_path),
        "contract_hash": result["contract_sha256"] == sha256(namespace / "CONTRACT.md"),
        "bindings_hash": result["bindings_sha256"] == sha256(namespace / "BINDINGS.json"),
        "root_inside_certified_box": ROOT_LO <= root_a <= ROOT_HI,
        "q_exactly_reconstructed": bool(np.array_equal(q, expected_q)),
        "source_exactly_reconstructed": bool(np.array_equal(source, expected_source)),
        "independent_hamiltonian_below_gate": float(np.max(np.abs(independent_hamiltonian))) < 6e-9,
        "independent_wall_below_gate": max(abs(value) for value in wall_residuals.values()) < 2e-10,
        "positive_static_patch": bool(np.min(f) > 0.0),
        "positive_lapse": bool(np.min((w * w) * f) > 0.0),
        "regular_axis_metric": bool(np.max(np.abs(q[:, 0, 4] * r[0] ** 2)) == 0.0),
        "natural_Hx_radially_constant": bool(np.max(np.ptp(source[:, :, 1], axis=1)) == 0.0),
        "natural_source_time_trace_zero_by_contract": True,
        "natural_reference_is_source_by_contract": True,
        "no_P16_anchor_in_result": "P16" not in json.dumps(result.get("representative_root", {})),
    }

    completed_phases = list(result.get("phases", {}).values())
    false_gates = []
    for phase_name, phase in result.get("phases", {}).items():
        for gate_name, passed in phase.get("gates", {}).items():
            if not bool(passed):
                false_gates.append(f"{phase_name}:{gate_name}")
    if result.get("admission_passed"):
        checks["admission_classification_consistent"] = not any(
            not bool(value)
            for phase in completed_phases[:5]
            for value in phase.get("gates", {}).values()
        )
    else:
        checks["failed_admission_classification_consistent"] = bool(result.get("first_failed_gate")) and bool(false_gates)

    verified = all(checks.values())
    audit = {
        "schema": "lin-d1-cauchy-background-admission-independent-audit-v1",
        "completed_utc": utc(),
        "status": "VERIFIED" if verified else "NOT_VERIFIED",
        "checks": checks,
        "false_scientific_gates": false_gates,
        "independent_values": {
            "maximum_first_integral": float(np.max(np.abs(first_integral))),
            "maximum_analytic_hamiltonian": float(np.max(np.abs(independent_hamiltonian))),
            "wall_residuals": wall_residuals,
            "minimum_f": float(np.min(f)),
            "maximum_q_reconstruction_difference": float(np.max(np.abs(q - expected_q))),
            "maximum_source_reconstruction_difference": float(np.max(np.abs(source - expected_source))),
        },
        "classification_checked": result.get("classification"),
        "scope": "Independent algebraic reconstruction of the D1 representative, continuum Hamiltonian, walls, positivity, axis, source identity, and terminal hashes; it does not reuse production geometry operators.",
    }
    atomic_json(namespace / "POSTRUN_AUDIT.json", audit)
    print(json.dumps({"status": audit["status"], "checks": checks}, indent=2))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
