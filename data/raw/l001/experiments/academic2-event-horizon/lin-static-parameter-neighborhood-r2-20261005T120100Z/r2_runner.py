#!/usr/bin/env python3
"""R2 recovery wrapper: conservatively subdivide non-finite event unions."""

from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import importlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any


BRANCH = Path(__file__).resolve().parent
R1_DIR = (BRANCH / "../lin-static-parameter-neighborhood-r1-20261005T114000Z").resolve()
sys.path.insert(0, str(R1_DIR))
r1 = importlib.import_module("r1_runner")
base = r1.base

CONFIG: dict[str, Any] = copy.deepcopy(r1.CONFIG)
CONFIG.update(
    {
        "schema": "lin-static-parameter-neighborhood-r2-config-v1",
        "nonfinite_event_union_policy": "CONSERVATIVE_SUBDIVISION_THEN_UNRESOLVED_AT_FROZEN_DEPTH",
    }
)
base.CONFIG = CONFIG

_ORIGINAL_EVENT_RECORD = base.event_record


def guarded_event_record(
    module: Any,
    a_lo: Any,
    a_hi: Any,
    steps: int,
    producer: str,
) -> dict[str, Any]:
    """Turn only the known non-finite public-conversion error into nonqualification."""
    started = time.monotonic()
    try:
        return _ORIGINAL_EVENT_RECORD(module, a_lo, a_hi, steps, producer)
    except ValueError as exc:
        if "fmpq requires an exact, finite value" not in str(exc):
            raise
        return {
            "producer": producer,
            "validated": False,
            "obstruction": "NONFINITE_EVENT_UNION_REQUIRES_SUBDIVISION",
            "event_cells": None,
            "wall_seconds": time.monotonic() - started,
            "maximum_picard_iterations": None,
        }


# The spawn workers import this module before unpickling base.global_box_task, so the
# frozen task sees the same conservative routing in the parent and every worker.
base.event_record = guarded_event_record


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_bindings(path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    bindings = json.loads(path.read_text())
    declared = {
        "runner_source_sha256": Path(__file__).resolve(),
        "contract_sha256": BRANCH / "CONTRACT.md",
        "test_source_sha256": BRANCH / "test_r2.py",
        "postrun_audit_source_sha256": BRANCH / "postrun_audit_r2.py",
        "r1_runner_source_sha256": R1_DIR / "r1_runner.py",
        "base_runner_source_sha256": r1.BASE_DIR / "parameter_neighborhood.py",
    }
    for key, candidate in declared.items():
        if sha256_file(candidate) != bindings[key]:
            raise RuntimeError(f"binding mismatch: {key}")
    if sha256_bytes(canonical_bytes(CONFIG)) != bindings["config_sha256"]:
        raise RuntimeError("R2 config digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        candidate = (BRANCH / item["relative_path"]).resolve()
        if not candidate.is_file() or sha256_file(candidate) != item["sha256"]:
            raise RuntimeError(f"predecessor mismatch: {name}")
        resolved[name] = candidate
    guard = {
        "runner_source_sha256": bindings["runner_source_sha256"],
        "r1_runner_source_sha256": bindings["r1_runner_source_sha256"],
        "base_runner_source_sha256": bindings["base_runner_source_sha256"],
        "contract_sha256": bindings["contract_sha256"],
        "config_sha256": bindings["config_sha256"],
        "bindings_sha256": sha256_file(path),
    }
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return guard, resolved


def bootstrap_r1_checkpoint(output: Path, guard: dict[str, str], resolved: dict[str, Path], workers: int) -> None:
    if (output / "CHECKPOINT.json").exists():
        return
    latest = json.loads(resolved["r1_latest_checkpoint"].read_text())
    payload = latest["payload"]
    if sha256_bytes(canonical_bytes(payload)) != latest["checkpoint_sha256"]:
        raise RuntimeError("R1 latest checkpoint payload digest mismatch")
    expected_name = f"checkpoint-{latest['checkpoint_sha256']}.json"
    if resolved["r1_immutable_checkpoint"].name != expected_name:
        raise RuntimeError("R1 immutable checkpoint name does not bind the payload digest")
    if json.loads(resolved["r1_immutable_checkpoint"].read_text()) != payload:
        raise RuntimeError("R1 checkpoint pointer and immutable payload disagree")
    state = payload["state"]
    state["r2_recovery"] = {
        "recovered_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "r1_checkpoint_sha256": latest["checkpoint_sha256"],
        "policy": CONFIG["nonfinite_event_union_policy"],
    }
    base.save_state(output, guard, state, workers)


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
        if args.mode == "preflight":
            result = base.run_preflight(args.output.resolve(), guard, resolved)
        else:
            bootstrap_r1_checkpoint(args.output.resolve(), guard, resolved, args.workers)
            result = base.run_production(args.output.resolve(), guard, resolved, args.workers)
        print(json.dumps({"mode": args.mode, "status": result["status"], "classification": result.get("classification")}, sort_keys=True))
    except Exception as exc:
        base.atomic_write_json(
            args.output.resolve() / "FAILURE.json",
            {
                "schema": "lin-static-parameter-neighborhood-r2-failure-v1",
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
