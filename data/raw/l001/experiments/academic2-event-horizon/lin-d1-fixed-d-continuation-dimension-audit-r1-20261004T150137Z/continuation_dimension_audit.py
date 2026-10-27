#!/usr/bin/env python3
"""R1 wrapper for the fixed-D dimension audit's sealed-status correction."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any


def load_base() -> Any:
    path = (
        Path(__file__).resolve().parent.parent
        / "lin-d1-fixed-d-continuation-dimension-audit-20261004T145827Z"
        / "continuation_dimension_audit.py"
    )
    spec = importlib.util.spec_from_file_location("fixed_d_dimension_base_r1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen base producer")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = load_base()
CONFIG = dict(base.CONFIG)
CONFIG.update(
    {
        "schema": "lin-d1-fixed-d-continuation-dimension-config-r1-v1",
        "technical_correction": "accept digest-bound D2A audit status PASS with all substantive audit gates",
    }
)
base.CONFIG = CONFIG


def corrected_authority_checks(resolved: dict[str, Path]) -> dict[str, Any]:
    primary = json.loads(resolved["primary_result"].read_text(encoding="utf-8"))
    primary_terminal = json.loads(resolved["primary_terminal"].read_text(encoding="utf-8"))
    independent = json.loads(resolved["independent_result"].read_text(encoding="utf-8"))
    independent_terminal = json.loads(resolved["independent_terminal"].read_text(encoding="utf-8"))
    global_result = json.loads(resolved["global_result"].read_text(encoding="utf-8"))
    global_audit = json.loads(resolved["global_audit"].read_text(encoding="utf-8"))
    global_terminal = json.loads(resolved["global_terminal"].read_text(encoding="utf-8"))
    d2a = json.loads(resolved["d2a_result"].read_text(encoding="utf-8"))
    d2a_audit = json.loads(resolved["d2a_audit"].read_text(encoding="utf-8"))
    d2a_terminal = json.loads(resolved["d2a_terminal"].read_text(encoding="utf-8"))
    d2a_audit_pass = bool(
        d2a_audit.get("status") == "PASS"
        and d2a_audit.get("exact_contiguous_cover_reproduced")
        and d2a_audit.get("unresolved_boxes") == 0
        and d2a_audit.get("all_checkpoint_content_addresses_verified")
        and d2a_audit.get("source_and_input_guards_verified")
        and d2a_audit.get("final_checkpoint_stack_empty")
    )
    checks = {
        "primary_D1_root": primary.get("classification")
        == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS"
        and primary_terminal.get("classification")
        == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS",
        "independent_D1_root": independent.get("classification")
        == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS"
        and independent_terminal.get("classification")
        == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS",
        "global_first_event_uniqueness": global_result.get("classification")
        == base.GLOBAL_UNIQUENESS_CLASSIFICATION
        and global_terminal.get("classification") == base.GLOBAL_UNIQUENESS_CLASSIFICATION
        and global_audit.get("status") == "VERIFIED"
        and not global_result.get("unresolved"),
        "D2A_exclusion": d2a.get("classification") == base.D2A_CLASSIFICATION
        and d2a_terminal.get("classification") == base.D2A_CLASSIFICATION
        and d2a_audit_pass,
    }
    return {
        "pass": all(checks.values()),
        "checks": checks,
        "D2A_audit_subchecks": {
            "status_is_PASS": d2a_audit.get("status") == "PASS",
            "exact_contiguous_cover_reproduced": bool(
                d2a_audit.get("exact_contiguous_cover_reproduced")
            ),
            "zero_unresolved_boxes": d2a_audit.get("unresolved_boxes") == 0,
            "checkpoint_addresses_verified": bool(
                d2a_audit.get("all_checkpoint_content_addresses_verified")
            ),
            "source_and_input_guards_verified": bool(
                d2a_audit.get("source_and_input_guards_verified")
            ),
            "final_checkpoint_stack_empty": bool(d2a_audit.get("final_checkpoint_stack_empty")),
        },
    }


base.authority_checks = corrected_authority_checks


def verify_bindings(bindings_path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    source_sha = base.sha256_file(Path(__file__).resolve())
    config_sha = base.sha256_bytes(base.canonical_bytes(CONFIG))
    if source_sha != bindings["producer_source_sha256"]:
        raise RuntimeError("R1 producer source digest mismatch")
    if config_sha != bindings["config_sha256"]:
        raise RuntimeError("R1 config digest mismatch")
    if base.sha256_file(branch / "CONTRACT.md") != bindings["contract_sha256"]:
        raise RuntimeError("R1 contract digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        if not path.is_file() or base.sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"R1 bound input mismatch: {name}")
        resolved[name] = path
    guard = {
        "producer_source_sha256": source_sha,
        "config_sha256": config_sha,
        "contract_sha256": bindings["contract_sha256"],
        "bindings_sha256": base.sha256_file(bindings_path),
    }
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return guard, resolved


def main() -> None:
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preflight", "production"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    guard, resolved = verify_bindings(args.bindings.resolve())
    try:
        result = (
            base.run_preflight(args.output.resolve(), guard, resolved)
            if args.mode == "preflight"
            else base.run_production(args.output.resolve(), guard, resolved)
        )
        print(
            json.dumps(
                {
                    "mode": args.mode,
                    "status": result["status"],
                    "classification": result.get("classification"),
                },
                sort_keys=True,
            )
        )
    except Exception as exc:
        failure = {
            "schema": "lin-d1-fixed-d-continuation-dimension-r1-failure-v1",
            "status": "INCOMPLETE",
            "mode": args.mode,
            "failed_utc": base.utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "guard": guard,
        }
        base.atomic_write_json(args.output / "FAILURE.json", failure)
        raise


if __name__ == "__main__":
    main()
