#!/usr/bin/env python3
"""Independent integrity, D1 wall-identity, and decision audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


GAMMA = 20.0
V0 = 0.1
V1 = 0.09048374180359596
LAMBDA_A = 5.999990376773895
LAMBDA_B = -6.052844277744164
EXPECTED_A_GRIDS = [[65, 121], [97, 181], [129, 241]]
EXPECTED_B_NX = [129, 193, 257, 385, 513]
EXPECTED_B_NR = 241
WALL_GATE = 2e-6
WALL_ANY_GATE = 2e-5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def observed_order(coarse: float, fine: float, coarse_n: int, fine_n: int) -> float | None:
    if coarse <= 0.0 or fine <= 0.0 or coarse == fine:
        return None
    return float(math.log(coarse / fine) / math.log((fine_n - 1) / (coarse_n - 1)))


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
    checks: dict[str, bool] = {
        "terminal_status": result["status"] == terminal["status"] == "COMPLETE",
        "terminal_classification": result["classification"] == terminal["classification"],
        "terminal_result_hash": sha256(result_path) == terminal["result_sha256"],
        "terminal_evidence_hash": sha256(evidence_path) == terminal["evidence_sha256"],
        "contract_hash": result["contract_sha256"] == sha256(namespace / "CONTRACT.md"),
        "bindings_hash": result["bindings_sha256"] == sha256(namespace / "BINDINGS.json"),
    }
    freeze_matches = {
        item["path"]: sha256(namespace / item["path"]) == item["sha256"]
        for item in freeze["files"]
    }
    parent_matches = {
        item["path"]: sha256(root / item["path"]) == item["sha256"]
        for item in bindings["parents"] + bindings["production_sources"]
    }
    checks["frozen_sources"] = all(freeze_matches.values())
    checks["parent_bindings"] = all(parent_matches.values())

    a = result["producer_A"]
    checks["A_grids"] = [item["grid"] for item in a["levels"]] == EXPECTED_A_GRIDS
    checks["A_background_rows_zero"] = all(item["wall"]["maximum"] == 0.0 for item in a["levels"])
    checks["A_generic_response"] = bool(
        a["perturbation_control"]["finite"]
        and a["perturbation_control"]["nonzero"]
        and a["perturbation_control"]["maximum_absolute_normalized_response"] > 1e-12
    )
    checks["A_decision"] = bool(all(a["gates"].values())) == bool(a["passed"])

    b = result["producer_B"]
    levels = b["levels"]
    checks["B_grids"] = [item["grid"] for item in levels] == [[nx, EXPECTED_B_NR] for nx in EXPECTED_B_NX]
    passing = [index for index, item in enumerate(levels) if item["maximum"] <= WALL_GATE]
    last_order = observed_order(
        levels[-2]["maximum"], levels[-1]["maximum"], levels[-2]["grid"][0], levels[-1]["grid"][0]
    )
    b_expected = {
        "candidate": levels[-1]["maximum"] <= WALL_GATE,
        "all_levels": max(item["maximum"] for item in levels) <= WALL_ANY_GATE,
        "monotone": all(right["maximum"] < left["maximum"] for left, right in zip(levels[:-1], levels[1:])),
        "last_order": last_order is not None and 2.0 <= last_order <= 6.0,
        "two_consecutive_candidate_passes": len(passing) >= 2 and passing[-2:] == [len(levels)-2, len(levels)-1],
    }
    checks["B_decision"] = (
        b_expected == b["gates"] and passing == b["passing_indices"]
        and bool(all(b_expected.values())) == bool(b["passed"])
    )

    with np.load(evidence_path, allow_pickle=False) as evidence:
        q = np.asarray(evidence["q"], dtype=float)
        source = np.asarray(evidence["source"], dtype=float)
        h = np.asarray(evidence["H"], dtype=float)
        phi = np.asarray(evidence["phi"], dtype=float)
        u = np.asarray(evidence["U"], dtype=float)
        k = float(evidence["k"])
        r = np.asarray(evidence["r"], dtype=float)
    lower_beta = LAMBDA_A / 6.0 + 0.5 * GAMMA * (phi[0] - V0) ** 2 / 6.0
    upper_beta = -LAMBDA_B / 6.0 - 0.5 * GAMMA * (phi[-1] - V1) ** 2 / 6.0
    wall_identities = {
        "lower_metric": abs(float(h[0] + lower_beta)),
        "upper_metric": abs(float(h[-1] + upper_beta)),
        "lower_scalar": abs(float(u[0] - 0.5 * GAMMA * (phi[0] - V0))),
        "upper_scalar": abs(float(u[-1] + 0.5 * GAMMA * (phi[-1] - V1))),
    }
    checks["continuum_wall_identities"] = max(wall_identities.values()) <= 2e-10
    checks["finite_evidence"] = bool(np.all(np.isfinite(q)) and np.all(np.isfinite(source)))
    checks["radial_domain_positive"] = bool(np.min(1.0 - k * r ** 2) > 0.0)

    verified = all(checks.values())
    audit = {
        "schema": "lin-d1-wall-discriminator-independent-audit-v1",
        "classification": "VERIFIED" if verified else "NOT_VERIFIED",
        "producer_classification": result["classification"],
        "checks": checks,
        "freeze_matches": freeze_matches,
        "parent_matches": parent_matches,
        "continuum_wall_identity_residuals": wall_identities,
        "B_expected_gates": b_expected,
        "claim_boundary": [
            "This audit independently checks integrity, continuum wall identities, and frozen decisions.",
            "It does not establish continuum existence, stability, collapse, or causality.",
        ],
    }
    atomic_json(output / "INDEPENDENT_AUDIT.json", audit)
    print(json.dumps(audit, indent=2, sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
