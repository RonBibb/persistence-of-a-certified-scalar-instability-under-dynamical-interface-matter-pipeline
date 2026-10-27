#!/usr/bin/env python3
"""Structural post-run audit for the R2 recovered neighborhood theorem."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import r2_runner as r2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    guard, _ = r2.verify_bindings(args.bindings.resolve())
    result_path = args.output.resolve() / "RESULT.json"
    result = json.loads(result_path.read_text())
    checks = {
        "result_guard_matches": result.get("guard") == guard,
        "recovered_from_checkpoint": result.get("resumed_from_checkpoint") is True,
        "r2_policy_frozen": result.get("frozen_design", {}).get("nonfinite_event_union_policy") == r2.CONFIG["nonfinite_event_union_policy"],
        "all_parameter_volume_admitted": result.get("admitted_fraction") == 1.0,
        "no_unresolved_parameter_cells": result.get("unresolved_parameter_cells") == [],
        "terminal_checkpoint_present": (args.output.resolve() / "TERMINAL_CHECKPOINT.json").is_file(),
    }
    audit = {
        "schema": "lin-static-parameter-neighborhood-r2-postrun-audit-v1",
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "result_sha256": r2.sha256_file(result_path),
    }
    r2.base.atomic_write_json(args.output.resolve() / "POSTRUN_AUDIT.json", audit)
    print(json.dumps(audit, sort_keys=True))
    if audit["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
