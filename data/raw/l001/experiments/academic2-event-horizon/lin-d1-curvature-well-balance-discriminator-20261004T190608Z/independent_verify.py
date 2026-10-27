#!/usr/bin/env python3
"""Independent post-run integrity, continuum, and decision audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


EXPECTED_A_GRIDS = [[65, 121], [97, 181], [129, 241]]
EXPECTED_B_NX = [257, 513, 1025, 1537, 2049]
EXPECTED_B_NR = 241
EXPECTED_GATES = {
    "hamiltonian_full": 2e-6,
    "hamiltonian_interior": 5e-7,
    "wall": 2e-6,
    "wall_any": 2e-5,
    "axis": 5e-12,
    "gauge": 5e-5,
    "source": 1e-12,
    "outer": 1e-12,
    "adm_acceleration": 5e-5,
    "gh_acceleration": 1e-4,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            default=lambda item: item.item() if isinstance(item, np.generic) else str(item),
        )
        + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def observed_order(coarse: float, fine: float, coarse_n: int, fine_n: int) -> float | None:
    if coarse <= 0.0 or fine <= 0.0 or coarse == fine:
        return None
    return float(math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1)))


def close(left: float, right: float, atol: float = 1e-13, rtol: float = 5e-12) -> bool:
    return bool(abs(float(left) - float(right)) <= atol + rtol * max(abs(float(left)), abs(float(right))))


def recompute_hamiltonian_decisions(result: dict[str, Any]) -> dict[str, Any]:
    a = result["producer_A"]
    a_levels = a["levels"]
    a_control = a["perturbation_control"]
    a_expected = {
        "full": a_levels[-1]["hamiltonian_full"] <= EXPECTED_GATES["hamiltonian_full"],
        "interior": a_levels[-1]["hamiltonian_interior"] <= EXPECTED_GATES["hamiltonian_interior"],
        "nonincreasing": (
            a_levels[-1]["hamiltonian_full"] <= a_levels[-2]["hamiltonian_full"]
            and a_levels[-1]["hamiltonian_interior"] <= a_levels[-2]["hamiltonian_interior"]
        ),
        "perturbation_active": bool(a_control["finite"] and a_control["nonzero"]),
    }

    b = result["producer_B"]
    b_levels = b["levels"]
    passing_indices = [
        index
        for index, item in enumerate(b_levels)
        if item["hamiltonian_full"] <= EXPECTED_GATES["hamiltonian_full"]
        and item["hamiltonian_interior"] <= EXPECTED_GATES["hamiltonian_interior"]
    ]
    full_order = observed_order(
        b_levels[-2]["hamiltonian_full"],
        b_levels[-1]["hamiltonian_full"],
        b_levels[-2]["grid"][0],
        b_levels[-1]["grid"][0],
    )
    interior_order = observed_order(
        b_levels[-2]["hamiltonian_interior"],
        b_levels[-1]["hamiltonian_interior"],
        b_levels[-2]["grid"][0],
        b_levels[-1]["grid"][0],
    )
    b_expected = {
        "full": b_levels[-1]["hamiltonian_full"] <= EXPECTED_GATES["hamiltonian_full"],
        "interior": b_levels[-1]["hamiltonian_interior"] <= EXPECTED_GATES["hamiltonian_interior"],
        "monotone_full": all(
            right["hamiltonian_full"] < left["hamiltonian_full"]
            for left, right in zip(b_levels[:-1], b_levels[1:])
        ),
        "monotone_interior": all(
            right["hamiltonian_interior"] < left["hamiltonian_interior"]
            for left, right in zip(b_levels[:-1], b_levels[1:])
        ),
        "last_full_order": full_order is not None and 2.0 <= full_order <= 6.0,
        "last_interior_order": interior_order is not None and 2.0 <= interior_order <= 6.0,
        "two_consecutive_absolute_passes": (
            len(passing_indices) >= 2
            and passing_indices[-2:] == [len(b_levels) - 2, len(b_levels) - 1]
        ),
    }
    return {
        "producer_A_expected": a_expected,
        "producer_A_recorded": a["hamiltonian_gates"],
        "producer_B_expected": b_expected,
        "producer_B_recorded": b["hamiltonian_gates"],
        "producer_B_passing_indices_expected": passing_indices,
        "producer_B_passing_indices_recorded": b["passing_indices"],
        "producer_A_match": a_expected == a["hamiltonian_gates"]
        and bool(all(a_expected.values())) == bool(a["hamiltonian_passed"]),
        "producer_B_match": b_expected == b["hamiltonian_gates"]
        and passing_indices == b["passing_indices"]
        and bool(all(b_expected.values())) == bool(b["hamiltonian_passed"]),
    }


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
    freeze = json.loads((namespace / "FREEZE_RECORD.json").read_text(encoding="utf-8"))
    bindings = json.loads((namespace / "BINDINGS.json").read_text(encoding="utf-8"))

    checks: dict[str, Any] = {}
    checks["terminal_result_hash"] = terminal["result_sha256"] == sha256(result_path)
    checks["terminal_evidence_hash"] = terminal["evidence_sha256"] == sha256(evidence_path)
    checks["terminal_status"] = terminal["status"] == result["status"] == "COMPLETE"
    checks["terminal_classification"] = terminal["classification"] == result["classification"]
    checks["contract_hash"] = result["contract_sha256"] == sha256(namespace / "CONTRACT.md")
    checks["bindings_hash"] = result["bindings_sha256"] == sha256(namespace / "BINDINGS.json")
    checks["gate_contract"] = result["gates"] == EXPECTED_GATES

    frozen_hashes = {item["path"]: item["sha256"] for item in freeze["files"]}
    freeze_matches = {}
    for relative, expected in frozen_hashes.items():
        freeze_matches[relative] = sha256(namespace / relative) == expected
    checks["frozen_source_hashes"] = all(freeze_matches.values())

    parent_matches = {}
    for item in bindings["parents"] + bindings["production_sources"]:
        parent_matches[item["path"]] = sha256(root / item["path"]) == item["sha256"]
    checks["parent_bindings"] = all(parent_matches.values())

    decisions = recompute_hamiltonian_decisions(result)
    checks["producer_A_decision"] = decisions["producer_A_match"]
    checks["producer_B_decision"] = decisions["producer_B_match"]
    checks["A_grids"] = [item["grid"] for item in result["producer_A"]["levels"]] == EXPECTED_A_GRIDS
    checks["B_grids"] = [item["grid"] for item in result["producer_B"]["levels"]] == [
        [nx, EXPECTED_B_NR] for nx in EXPECTED_B_NX
    ]

    with np.load(evidence_path, allow_pickle=False) as evidence:
        x = np.asarray(evidence["x"], dtype=float)
        r = np.asarray(evidence["r"], dtype=float)
        a = np.asarray(evidence["A"], dtype=float)
        h = np.asarray(evidence["H"], dtype=float)
        phi = np.asarray(evidence["phi"], dtype=float)
        u = np.asarray(evidence["U"], dtype=float)
        q = np.asarray(evidence["q"], dtype=float)
        source = np.asarray(evidence["source"], dtype=float)
        k = float(evidence["k"])
        cscale = float(evidence["cscale"])
        archived_analytic = np.asarray(evidence["analytic_hamiltonian"], dtype=float)
    w = np.exp(a)
    f = 1.0 - k * r[None, :] ** 2
    reconstructed_analytic = -12.0 * (
        h * h - 1.0 - u * u / 12.0 + 0.41 * phi * phi / 12.0 - k * np.exp(-2.0 * a)
    )
    checks["analytic_hamiltonian_array"] = bool(
        np.allclose(archived_analytic, reconstructed_analytic, rtol=0.0, atol=5e-15)
    )
    analytic_max = float(np.max(np.abs(reconstructed_analytic)))
    checks["analytic_hamiltonian_result"] = close(
        analytic_max, result["independent_analytic_hamiltonian_maximum"], atol=5e-15, rtol=1e-12
    )
    checks["analytic_hamiltonian_small"] = analytic_max <= 2e-12
    checks["q_zz"] = bool(np.allclose(q[:, :, 6], (w * cscale)[:, None] ** 2, rtol=0.0, atol=5e-14))
    checks["q_tt"] = bool(np.allclose(q[:, :, 2], -(w[:, None] ** 2) * f, rtol=0.0, atol=5e-14))
    checks["q_transverse"] = bool(np.allclose(q[:, :, 3], w[:, None] ** 2, rtol=0.0, atol=5e-14))
    checks["source_compact"] = bool(
        np.allclose(source[:, :, 1], (-3.0 * cscale * w * h)[:, None], rtol=0.0, atol=5e-14)
    )
    checks["source_radial"] = bool(np.allclose(source[:, :, 2], 4.0 * k / f, rtol=0.0, atol=5e-14))
    checks["finite_evidence"] = bool(
        all(np.all(np.isfinite(item)) for item in (x, r, a, h, phi, u, q, source))
    )

    # On the exact D1 background, the subtract/add definition makes all
    # componentwise corrected-Ricci errors algebraically zero.  This verifies
    # the recorded outcome without importing the producer implementation.
    a_component_zero = all(
        max(abs(float(value)) for value in level["componentwise_ricci_errors"].values()) <= 5e-14
        for level in result["producer_A"]["levels"]
    )
    checks["A_componentwise_exact_background"] = a_component_zero
    checks["A_generic_response_nonzero"] = bool(
        result["producer_A"]["perturbation_control"]["finite"]
        and result["producer_A"]["perturbation_control"]["nonzero"]
        and result["producer_A"]["perturbation_control"]["maximum_absolute_response"] > 1e-12
    )

    verified = all(bool(value) for value in checks.values())
    audit = {
        "schema": "lin-d1-curvature-discriminator-independent-audit-v1",
        "classification": "VERIFIED" if verified else "NOT_VERIFIED",
        "producer_classification": result["classification"],
        "checks": checks,
        "freeze_matches": freeze_matches,
        "parent_matches": parent_matches,
        "decision_reconstruction": decisions,
        "independent_analytic_hamiltonian_maximum": analytic_max,
        "claim_boundary": [
            "This audit verifies integrity, the D1 analytic Hamiltonian, represented fields, and frozen decision logic.",
            "It does not turn a finite-resolution producer outcome into a continuum, stability, collapse, or causal claim.",
        ],
    }
    atomic_json(output / "INDEPENDENT_AUDIT.json", audit)
    print(json.dumps({"classification": audit["classification"], "checks": checks}, indent=2, sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
