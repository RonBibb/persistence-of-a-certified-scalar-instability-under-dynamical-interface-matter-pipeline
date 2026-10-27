#!/usr/bin/env python3
"""Independent integrity and decision audit for the D1 gauge discriminator."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


EXPECTED_A = [[65, 121], [97, 181], [129, 241]]
EXPECTED_B = [[129, 241], [193, 241], [257, 241]]
GATE = 5e-5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def order(c: float, f: float, cn: int, fn: int) -> float | None:
    if c <= 0 or f <= 0 or c == f:
        return None
    return math.log(c / f) / math.log((fn - 1) / (cn - 1))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--namespace", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(); ns = args.namespace.resolve(); out = ns / "output"
    result_path = out / "RESULT.json"; terminal_path = out / "TERMINAL.json"; evidence_path = out / "EVIDENCE.npz"
    result = json.loads(result_path.read_text()); terminal = json.loads(terminal_path.read_text())
    freeze = json.loads((ns / "FREEZE_RECORD.json").read_text()); bindings = json.loads((ns / "BINDINGS.json").read_text())
    checks = {
        "terminal_status": result["status"] == terminal["status"] == "COMPLETE",
        "terminal_classification": result["classification"] == terminal["classification"],
        "result_hash": sha256(result_path) == terminal["result_sha256"],
        "evidence_hash": sha256(evidence_path) == terminal["evidence_sha256"],
        "contract_hash": result["contract_sha256"] == sha256(ns / "CONTRACT.md"),
        "bindings_hash": result["bindings_sha256"] == sha256(ns / "BINDINGS.json"),
    }
    freeze_matches = {item["path"]: sha256(ns / item["path"]) == item["sha256"] for item in freeze["files"]}
    parent_matches = {item["path"]: sha256(root / item["path"]) == item["sha256"] for item in bindings["parents"] + bindings["production_sources"]}
    checks["frozen_sources"] = all(freeze_matches.values()); checks["parent_bindings"] = all(parent_matches.values())
    a = result["producer_A"]; b = result["producer_B"]
    checks["A_grids"] = [item["grid"] for item in a["levels"]] == EXPECTED_A
    checks["A_background_zero"] = all(item["corrected"]["maximum_absolute"] == 0.0 for item in a["levels"])
    checks["A_generic_response"] = bool(a["perturbation_control"]["finite"] and a["perturbation_control"]["maximum_absolute"] > 1e-12)
    checks["A_decision"] = bool(all(a["gates"].values())) == bool(a["passed"])
    levels = b["levels"]
    checks["B_grids"] = [item["grid"] for item in levels] == EXPECTED_B
    passing = [i for i, item in enumerate(levels) if item["maximum_absolute"] <= GATE and item["maximum_local_relative"] <= GATE]
    last = order(levels[-2]["maximum_absolute"], levels[-1]["maximum_absolute"], levels[-2]["grid"][0], levels[-1]["grid"][0])
    expected = {
        "absolute": levels[-1]["maximum_absolute"] <= GATE,
        "relative": levels[-1]["maximum_local_relative"] <= GATE,
        "monotone_absolute": all(y["maximum_absolute"] < x["maximum_absolute"] for x, y in zip(levels[:-1], levels[1:])),
        "monotone_relative": all(y["maximum_local_relative"] < x["maximum_local_relative"] for x, y in zip(levels[:-1], levels[1:])),
        "last_absolute_order": last is not None and 2.0 <= last <= 6.0,
        "two_consecutive_passes": len(passing) >= 2 and passing[-2:] == [len(levels)-2, len(levels)-1],
    }
    checks["B_decision"] = expected == b["gates"] and passing == b["passing_indices"] and bool(all(expected.values())) == bool(b["passed"])
    with np.load(evidence_path, allow_pickle=False) as evidence:
        arrays = [np.asarray(evidence[name]) for name in evidence.files]
    checks["finite_evidence"] = all(np.all(np.isfinite(value)) for value in arrays)
    verified = all(checks.values())
    audit = {"schema": "lin-d1-gauge-independent-audit-v1", "classification": "VERIFIED" if verified else "NOT_VERIFIED",
             "producer_classification": result["classification"], "checks": checks, "freeze_matches": freeze_matches,
             "parent_matches": parent_matches, "B_expected_gates": expected,
             "claim_boundary": "finite-resolution formulation audit only"}
    atomic_json(out / "INDEPENDENT_AUDIT.json", audit)
    print(json.dumps(audit, indent=2, sort_keys=True))
    if not verified:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
