#!/usr/bin/env python3
"""R1 runner: finite theorem-quantity unions near the D1 root."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from flint import ctx


def _load_base() -> Any:
    path = (
        Path(__file__).resolve().parent.parent
        / "lin-d1-global-first-event-uniqueness-20261004T133213Z"
        / "global_uniqueness_cover.py"
    )
    spec = importlib.util.spec_from_file_location("d1_global_cover_base_r1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen base cover")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


base = _load_base()
CONFIG = dict(base.CONFIG)
CONFIG.update(
    {
        "schema": "lin-d1-global-first-event-uniqueness-config-r1-v1",
        "event_union_fields": ["G", "G_s", "h"],
        "technical_correction": "omit non-theorem derived quotients from event union",
    }
)
base.CONFIG = CONFIG


def corrected_early_first_event(
    module: Any, lo: Any, hi: Any, steps: int, producer: str
) -> dict[str, Any]:
    """Enclose only G, G_s and h at the first event."""

    started = time.monotonic()
    step = module.S_END / steps
    state = module.launch(module.ball(lo, hi))
    zero_cells: list[int] = []
    event_records: list[dict[str, Any]] = []
    maximum_picard = 0
    negative_after_cell: int | None = None
    obstruction: str | None = None

    try:
        for cell in range(steps):
            enclosure, iterations = module.picard_box(state, step)
            maximum_picard = max(maximum_picard, iterations)
            quantities = (
                module.event_quantities(enclosure)
                if producer == "primary"
                else module.upper_quantities(enclosure)
            )
            sign = base.interval_sign(module, quantities["G"])
            if not zero_cells:
                if sign == "positive":
                    pass
                elif sign == "zero-containing":
                    zero_cells.append(cell)
                    event_records.append(quantities)
                else:
                    obstruction = "STRICTLY_NEGATIVE_CELL_BEFORE_ZERO_CLUSTER"
                    break
            else:
                if sign == "zero-containing":
                    if cell != zero_cells[-1] + 1:
                        obstruction = "NONCONTIGUOUS_ZERO_CLUSTER"
                        break
                    zero_cells.append(cell)
                    event_records.append(quantities)
                elif sign == "negative":
                    negative_after_cell = cell
                    break
                else:
                    obstruction = "POSITIVE_CELL_AFTER_ZERO_CLUSTER"
                    break
            state = module.advance(state, enclosure, step)

        if not zero_cells and obstruction is None:
            obstruction = "NO_ZERO_CLUSTER_BEFORE_S_END"
        if zero_cells and negative_after_cell is None and obstruction is None:
            obstruction = "ZERO_CLUSTER_NOT_CLOSED_BEFORE_S_END"

        if not event_records:
            return {
                "producer": producer,
                "steps": steps,
                "validated": False,
                "obstruction": obstruction,
                "event_cells": None,
                "wall_seconds": time.monotonic() - started,
                "maximum_picard_iterations": maximum_picard,
            }

        Gs_key = "Gs" if producer == "primary" else "G_s"
        required = {
            "G": module.union_all([record["G"] for record in event_records]),
            "G_s": module.union_all([record[Gs_key] for record in event_records]),
            "h": module.union_all([record["h"] for record in event_records]),
        }
        Gs_bounds = module.bounds(required["G_s"])
        h_bounds = module.bounds(required["h"])
    except Exception as exc:
        return {
            "producer": producer,
            "steps": steps,
            "validated": False,
            "obstruction": f"{type(exc).__name__}: {exc}",
            "event_cells": [zero_cells[0], zero_cells[-1]] if zero_cells else None,
            "wall_seconds": time.monotonic() - started,
            "maximum_picard_iterations": maximum_picard,
        }

    Gs_negative = Gs_bounds[1] < 0
    h_sign = (
        "positive"
        if h_bounds[0] > 0
        else "negative"
        if h_bounds[1] < 0
        else "zero-containing"
    )
    validated = bool(
        obstruction is None
        and zero_cells == list(range(zero_cells[0], zero_cells[-1] + 1))
        and negative_after_cell == zero_cells[-1] + 1
        and Gs_negative
    )
    return {
        "producer": producer,
        "steps": steps,
        "validated": validated,
        "obstruction": obstruction,
        "event_cells": [zero_cells[0], zero_cells[-1]],
        "negative_after_cell": negative_after_cell,
        "event_bracket_exact": [
            str(zero_cells[0] * step),
            str((zero_cells[-1] + 1) * step),
        ],
        "event_bracket_decimal": [
            float(zero_cells[0] * step),
            float((zero_cells[-1] + 1) * step),
        ],
        "G": base.public_interval(module, required["G"]),
        "G_s": base.public_interval(module, required["G_s"]),
        "G_s_strictly_negative": Gs_negative,
        "h": base.public_interval(module, required["h"]),
        "h_sign": h_sign,
        "h_excludes_zero": h_sign in {"positive", "negative"},
        "maximum_picard_iterations": maximum_picard,
        "wall_seconds": time.monotonic() - started,
    }


_original_worker_initialize = base.worker_initialize


def corrected_worker_initialize(primary_path: str, independent_path: str) -> None:
    _original_worker_initialize(primary_path, independent_path)


def corrected_evaluate_box_task(task: tuple[str, str, int]) -> dict[str, Any]:
    lo_text, hi_text, depth = task
    lo, hi = base.parse_q(lo_text), base.parse_q(hi_text)
    started = time.monotonic()
    primary_record = corrected_early_first_event(
        base._WORKER["primary"], lo, hi, CONFIG["primary_steps"], "primary"
    )
    independent_record = corrected_early_first_event(
        base._WORKER["independent"], lo, hi, CONFIG["independent_steps"], "independent"
    )
    same_sign = (
        primary_record.get("h_sign") in {"positive", "negative"}
        and primary_record.get("h_sign") == independent_record.get("h_sign")
    )
    qualified = bool(
        primary_record.get("validated")
        and independent_record.get("validated")
        and primary_record.get("h_excludes_zero")
        and independent_record.get("h_excludes_zero")
        and same_sign
    )
    return {
        "a_exact_bounds": [lo_text, hi_text],
        "a_decimal_bounds": [float(lo), float(hi)],
        "depth": depth,
        "qualified_dual_exclusion": qualified,
        "same_h_sign": same_sign,
        "h_sign": primary_record.get("h_sign") if same_sign else None,
        "primary": primary_record,
        "independent": independent_record,
        "wall_seconds": time.monotonic() - started,
    }


base.early_first_event = corrected_early_first_event
base.worker_initialize = corrected_worker_initialize
base.evaluate_box_task = corrected_evaluate_box_task


def verify_bindings(bindings_path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    source_sha = base.sha256_file(Path(__file__).resolve())
    if source_sha != bindings["producer_source_sha256"]:
        raise RuntimeError("R1 producer source digest mismatch")
    config_sha = base.sha256_bytes(base.canonical_bytes(CONFIG))
    if config_sha != bindings["config_sha256"]:
        raise RuntimeError("R1 configuration digest mismatch")
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
    parser.add_argument("--workers", type=int, default=CONFIG["default_workers"])
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    args.output.mkdir(parents=True, exist_ok=True)
    guard, resolved = verify_bindings(args.bindings.resolve())
    primary, independent = base.import_producers(resolved, f"r1_main_{os.getpid()}")
    ctx.prec = CONFIG["arb_precision_bits"]
    try:
        if args.mode == "preflight":
            result = base.run_preflight(
                args.bindings.resolve(),
                args.output.resolve(),
                guard,
                resolved,
                primary,
                independent,
            )
        else:
            result = base.run_production(
                args.output.resolve(),
                guard,
                resolved,
                primary,
                independent,
                args.workers,
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
            "schema": "lin-d1-global-first-event-uniqueness-r1-failure-v1",
            "status": "INCOMPLETE",
            "mode": args.mode,
            "failed_utc": base.utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "guard": guard,
            "checkpoint_present": (args.output / "CHECKPOINT.json").exists(),
        }
        base.atomic_write_json(args.output / "FAILURE.json", failure)
        raise


if __name__ == "__main__":
    main()
