#!/usr/bin/env python3
"""R1 wrapper around the frozen neighborhood runner with a corrected root tube."""

from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from pathlib import Path
from typing import Any


BRANCH = Path(__file__).resolve().parent
BASE_DIR = (BRANCH / "../lin-static-parameter-neighborhood-20261005T070024Z").resolve()
sys.path.insert(0, str(BASE_DIR))
base = importlib.import_module("parameter_neighborhood")

BASE_CONFIG: dict[str, Any] = copy.deepcopy(base.CONFIG)
CONFIG: dict[str, Any] = copy.deepcopy(BASE_CONFIG)
CONFIG.update(
    {
        "schema": "lin-static-parameter-neighborhood-r1-config-v1",
        "root_box": [
            "696726888586725316547/7036874417766400000000",
            "696727170061702027203/7036874417766400000000",
        ],
        "root_tube_half_width_exact": "1/50000000",
        "root_tube_design_basis": "CERTIFIED_CENTRAL_LOCAL_SENSITIVITY_DIAGNOSTIC",
    }
)
base.CONFIG = CONFIG


def verify_bindings(path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    bindings = json.loads(path.read_text())
    declared = {
        "runner_source_sha256": Path(__file__).resolve(),
        "contract_sha256": BRANCH / "CONTRACT.md",
        "test_source_sha256": BRANCH / "test_r1.py",
        "postrun_audit_source_sha256": BRANCH / "postrun_audit_r1.py",
        "base_runner_source_sha256": BASE_DIR / "parameter_neighborhood.py",
    }
    for key, candidate in declared.items():
        if base.sha256_file(candidate) != bindings[key]:
            raise RuntimeError(f"binding mismatch: {key}")
    if base.sha256_bytes(base.canonical_bytes(CONFIG)) != bindings["config_sha256"]:
        raise RuntimeError("R1 config digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        candidate = (BRANCH / item["relative_path"]).resolve()
        if not candidate.is_file() or base.sha256_file(candidate) != item["sha256"]:
            raise RuntimeError(f"predecessor mismatch: {name}")
        resolved[name] = candidate
    guard = {
        "runner_source_sha256": bindings["runner_source_sha256"],
        "base_runner_source_sha256": bindings["base_runner_source_sha256"],
        "contract_sha256": bindings["contract_sha256"],
        "config_sha256": bindings["config_sha256"],
        "bindings_sha256": base.sha256_file(path),
    }
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return guard, resolved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preflight", "production"))
    parser.add_argument("--workers", type=int, default=CONFIG["default_workers"])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    guard, resolved = verify_bindings(args.bindings.resolve())
    if not 1 <= args.workers <= 10:
        raise ValueError("workers must be between 1 and 10")
    try:
        result = (
            base.run_preflight(args.output.resolve(), guard, resolved)
            if args.mode == "preflight"
            else base.run_production(args.output.resolve(), guard, resolved, args.workers)
        )
        print(json.dumps({"mode": args.mode, "status": result["status"], "classification": result.get("classification")}, sort_keys=True))
    except Exception as exc:
        base.atomic_write_json(
            args.output.resolve() / "FAILURE.json",
            {
                "schema": "lin-static-parameter-neighborhood-r1-failure-v1",
                "status": "INCOMPLETE",
                "mode": args.mode,
                "error_type": type(exc).__name__,
                "error": str(exc),
                "guard": guard,
                "checkpoint_present": (args.output.resolve() / "CHECKPOINT.json").exists(),
            },
        )
        raise


if __name__ == "__main__":
    main()
