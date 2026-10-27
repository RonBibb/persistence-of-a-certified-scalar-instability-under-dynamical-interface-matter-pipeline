#!/usr/bin/env python3
"""Gap-free dual-producer cover for global D1 first-event uniqueness.

The script imports two sealed interval ODE implementations only after all
declared digests verify.  It never writes to a predecessor directory.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import importlib.util
import json
import multiprocessing
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

from flint import arb, ctx, fmpq


CONFIG: dict[str, Any] = {
    "schema": "lin-d1-global-first-event-uniqueness-config-v1",
    "launch_interval": ["0", "V0_Q"],
    "root_box_decimal_labels": ["0.09901086489880687", "0.09901086689880687"],
    "proper_distance_endpoint": "2",
    "target_launch_width": "1/65536",
    "maximum_bisection_depth": 48,
    "arb_precision_bits": 768,
    "primary_steps": 8192,
    "independent_steps": 8192,
    "default_workers": 10,
    "batch_size_multiplier": 1,
    "checkpoint_max_seconds": 180,
    "classification_order": [
        "certified_root",
        "dual_negative_curvature",
        "target_width_split",
        "dual_first_event_scalar_exclusion",
        "maximum_depth_unresolved",
        "refine",
    ],
    "event_rule": (
        "all earlier cells G>0; contiguous zero-containing cells; union G_s<0; "
        "immediately following cell G<0"
    ),
}

EXPECTED_PRIMARY_CLASSIFICATION = "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS"
EXPECTED_INDEPENDENT_CLASSIFICATION = "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS"
SUCCESS_CLASSIFICATION = (
    "GLOBAL_FIRST_EVENT_SIMULTANEOUS_WALL_ROOT_UNIQUE_ON_DECLARED_"
    "POSITIVE_CURVATURE_LAUNCH_INTERVAL"
)
UNRESOLVED_CLASSIFICATION = "GLOBAL_FIRST_EVENT_UNIQUENESS_UNRESOLVED"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def parse_q(text: str) -> fmpq:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return fmpq(int(numerator), int(denominator))
    return fmpq(int(text))


def dyadic(text: str) -> fmpq:
    numerator, denominator = float(text).as_integer_ratio()
    return fmpq(numerator, denominator)


def exact_bounds(module: Any, value: arb) -> tuple[fmpq, fmpq]:
    return module.bounds(value)


def exact_bound_strings(pair: tuple[fmpq, fmpq]) -> list[str]:
    return [str(pair[0]), str(pair[1])]


def decimal_bounds(pair: tuple[fmpq, fmpq]) -> list[float]:
    return [float(pair[0]), float(pair[1])]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_bindings(bindings_path: Path) -> tuple[dict[str, Any], dict[str, str], dict[str, Path]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    source_sha = sha256_file(Path(__file__).resolve())
    if source_sha != bindings["producer_source_sha256"]:
        raise RuntimeError("producer source digest mismatch")
    config_sha = sha256_bytes(canonical_bytes(CONFIG))
    if config_sha != bindings["config_sha256"]:
        raise RuntimeError("configuration digest mismatch")
    if sha256_file(branch / "CONTRACT.md") != bindings["contract_sha256"]:
        raise RuntimeError("contract digest mismatch")

    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        if not path.is_file():
            raise RuntimeError(f"bound input missing: {name}")
        actual = sha256_file(path)
        if actual != item["sha256"]:
            raise RuntimeError(f"bound input digest mismatch: {name}")
        resolved[name] = path

    guard = {
        "producer_source_sha256": source_sha,
        "config_sha256": config_sha,
        "contract_sha256": bindings["contract_sha256"],
        "bindings_sha256": sha256_file(bindings_path),
    }
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return bindings, guard, resolved


def import_producers(resolved: dict[str, Path], suffix: str) -> tuple[Any, Any]:
    primary = load_module(f"d1_primary_{suffix}", resolved["primary_base_source"])
    independent = load_module(f"d1_independent_{suffix}", resolved["independent_source"])
    ctx.prec = CONFIG["arb_precision_bits"]
    return primary, independent


def interval_sign(module: Any, value: arb) -> str:
    lo, hi = module.bounds(value)
    if lo > 0:
        return "positive"
    if hi < 0:
        return "negative"
    return "zero-containing"


def public_interval(module: Any, value: arb) -> dict[str, Any]:
    pair = module.bounds(value)
    return {
        "exact_bounds": exact_bound_strings(pair),
        "decimal_bounds": decimal_bounds(pair),
        "contains_zero": pair[0] <= 0 <= pair[1],
    }


def early_first_event(module: Any, lo: fmpq, hi: fmpq, steps: int, producer: str) -> dict[str, Any]:
    """Enclose the first transverse G=0 event and stop after its negative side."""

    started = time.monotonic()
    step = module.S_END / steps
    state = module.launch(module.ball(lo, hi))
    zero_cells: list[int] = []
    event_records: list[dict[str, arb]] = []
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
            sign = interval_sign(module, quantities["G"])
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
    except Exception as exc:
        obstruction = f"{type(exc).__name__}: {exc}"

    if not zero_cells and obstruction is None:
        obstruction = "NO_ZERO_CLUSTER_BEFORE_S_END"
    if zero_cells and negative_after_cell is None and obstruction is None:
        obstruction = "ZERO_CLUSTER_NOT_CLOSED_BEFORE_S_END"

    event_union: dict[str, arb] | None = None
    if event_records:
        event_union = {
            key: module.union_all([record[key] for record in event_records])
            for key in event_records[0]
        }
    if event_union is None:
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
    h_key = "h"
    Gs_bounds = module.bounds(event_union[Gs_key])
    h_bounds = module.bounds(event_union[h_key])
    Gs_negative = Gs_bounds[1] < 0
    h_sign = "positive" if h_bounds[0] > 0 else "negative" if h_bounds[1] < 0 else "zero-containing"
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
        "event_bracket_exact": [str(zero_cells[0] * step), str((zero_cells[-1] + 1) * step)],
        "event_bracket_decimal": [float(zero_cells[0] * step), float((zero_cells[-1] + 1) * step)],
        "G_s": public_interval(module, event_union[Gs_key]),
        "G_s_strictly_negative": Gs_negative,
        "h": public_interval(module, event_union[h_key]),
        "h_sign": h_sign,
        "h_excludes_zero": h_sign in {"positive", "negative"},
        "maximum_picard_iterations": maximum_picard,
        "wall_seconds": time.monotonic() - started,
    }


_WORKER: dict[str, Any] = {}


def worker_initialize(primary_path: str, independent_path: str) -> None:
    sys.dont_write_bytecode = True
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    resolved = {
        "primary_base_source": Path(primary_path),
        "independent_source": Path(independent_path),
    }
    primary, independent = import_producers(resolved, f"worker_{os.getpid()}")
    _WORKER["primary"] = primary
    _WORKER["independent"] = independent


def evaluate_box_task(task: tuple[str, str, int]) -> dict[str, Any]:
    lo_text, hi_text, depth = task
    lo, hi = parse_q(lo_text), parse_q(hi_text)
    started = time.monotonic()
    primary_record = early_first_event(
        _WORKER["primary"], lo, hi, CONFIG["primary_steps"], "primary"
    )
    independent_record = early_first_event(
        _WORKER["independent"], lo, hi, CONFIG["independent_steps"], "independent"
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


def dual_curvature(primary: Any, independent: Any, lo: fmpq, hi: fmpq) -> dict[str, Any]:
    primary_value = primary.launch(primary.ball(lo, hi))[5]
    independent_value = independent.launch(independent.ball(lo, hi))[5]
    primary_bounds = primary.bounds(primary_value)
    independent_bounds = independent.bounds(independent_value)
    return {
        "both_strictly_negative": primary_bounds[1] < 0 and independent_bounds[1] < 0,
        "primary": {
            "exact_bounds": exact_bound_strings(primary_bounds),
            "decimal_bounds": decimal_bounds(primary_bounds),
        },
        "independent": {
            "exact_bounds": exact_bound_strings(independent_bounds),
            "decimal_bounds": decimal_bounds(independent_bounds),
        },
    }


def root_authority(resolved: dict[str, Path], primary: Any, independent: Any) -> dict[str, Any]:
    root_lo, root_hi = map(dyadic, CONFIG["root_box_decimal_labels"])
    primary_result = json.loads(resolved["primary_result"].read_text(encoding="utf-8"))
    primary_terminal = json.loads(resolved["primary_terminal"].read_text(encoding="utf-8"))
    independent_result = json.loads(resolved["independent_result"].read_text(encoding="utf-8"))
    independent_terminal = json.loads(resolved["independent_terminal"].read_text(encoding="utf-8"))

    primary_newton = tuple(parse_q(value) for value in primary_result["narrow"]["newton_exact_bounds"])
    primary_pass = bool(
        primary_result.get("status") == "COMPLETE"
        and primary_result.get("classification") == EXPECTED_PRIMARY_CLASSIFICATION
        and primary_result.get("both_frozen_boxes_strict_self_maps")
        and primary_terminal.get("classification") == EXPECTED_PRIMARY_CLASSIFICATION
        and root_lo < primary_newton[0] <= primary_newton[1] < root_hi
        and tuple(primary.ROOT_BOXES["narrow"]) == tuple(CONFIG["root_box_decimal_labels"])
    )
    independent_pass = bool(
        independent_result.get("status") == "COMPLETE"
        and independent_result.get("classification") == EXPECTED_INDEPENDENT_CLASSIFICATION
        and independent_result.get("all_levels_root_replay_pass")
        and independent_terminal.get("classification") == EXPECTED_INDEPENDENT_CLASSIFICATION
        and independent_result.get("frozen_inputs", {}).get("root_box")
        == CONFIG["root_box_decimal_labels"]
        and independent.ROOT_LO_Q == root_lo
        and independent.ROOT_HI_Q == root_hi
    )
    return {
        "pass": primary_pass and independent_pass,
        "root_exact_bounds": [str(root_lo), str(root_hi)],
        "root_decimal_labels": CONFIG["root_box_decimal_labels"],
        "primary_pass": primary_pass,
        "independent_pass": independent_pass,
        "primary_classification": primary_result.get("classification"),
        "independent_classification": independent_result.get("classification"),
        "primary_newton_exact_bounds": [str(primary_newton[0]), str(primary_newton[1])],
    }


def run_preflight(
    bindings_path: Path,
    output: Path,
    guard: dict[str, str],
    resolved: dict[str, Path],
    primary: Any,
    independent: Any,
) -> dict[str, Any]:
    ctx.prec = CONFIG["arb_precision_bits"]
    root = root_authority(resolved, primary, independent)
    if not root["pass"]:
        raise RuntimeError("sealed root authority verification failed")
    if primary.V0_Q != independent.V0_Q:
        raise RuntimeError("producer launch endpoints disagree")
    if primary.S_END != independent.S_END:
        raise RuntimeError("producer proper-distance endpoints disagree")

    controls = independent.algebra_controls()
    if not all(controls.values()):
        raise RuntimeError("independent Taylor algebra control failed")
    exact_ball = primary.ball(fmpq(1, 3), fmpq(1, 2))
    interval_controls = {
        "contains_2_over_5": bool(exact_ball.contains(arb(fmpq(2, 5)))),
        "excludes_3_over_5": not bool(exact_ball.contains(arb(fmpq(3, 5)))),
        "strict_nesting": bool(
            primary.strictly_contains(
                primary.ball(fmpq(0), fmpq(1)),
                primary.ball(fmpq(1, 4), fmpq(3, 4)),
            )
        ),
    }
    if not all(interval_controls.values()):
        raise RuntimeError("interval containment controls failed")

    negative = dual_curvature(primary, independent, fmpq(0), fmpq(1, 100))
    if not negative["both_strictly_negative"]:
        raise RuntimeError("negative-curvature route control failed")

    representative_tasks = [
        (str(dyadic("0.095")), str(dyadic("0.095") + fmpq(1, 2**18)), 18),
        (str(dyadic("0.0991")), str(dyadic("0.0991") + fmpq(1, 2**20)), 20),
    ]
    worker_initialize(str(resolved["primary_base_source"]), str(resolved["independent_source"]))
    representatives = [evaluate_box_task(task) for task in representative_tasks]
    if not all(row["qualified_dual_exclusion"] for row in representatives):
        raise RuntimeError("real dual-producer first-event representative failed")
    if [row["h_sign"] for row in representatives] != ["negative", "positive"]:
        raise RuntimeError("representatives did not bracket root with expected signs")

    roundtrip = [["1/7", "2/7", 9]]
    if [[str(parse_q(a)), str(parse_q(b)), d] for a, b, d in roundtrip] != roundtrip:
        raise RuntimeError("exact checkpoint rational roundtrip failed")

    d2a_result = json.loads(resolved["d2a_result"].read_text(encoding="utf-8"))
    d2a_terminal = json.loads(resolved["d2a_terminal"].read_text(encoding="utf-8"))
    result = {
        "schema": "lin-d1-global-first-event-uniqueness-preflight-v1",
        "status": "PASS",
        "completed_utc": utc_now(),
        "guard": guard,
        "root_authority": root,
        "producer_parameter_agreement": True,
        "independent_algebra_controls": controls,
        "interval_controls": interval_controls,
        "negative_curvature_route": negative,
        "dual_event_representatives": representatives,
        "checkpoint_exact_rational_roundtrip": True,
        "d2a_bound_without_mutation": {
            "result_classification": d2a_result.get("classification"),
            "terminal_classification": d2a_terminal.get("classification"),
        },
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": CONFIG["arb_precision_bits"],
        },
    }
    atomic_write_json(output / "PREFLIGHT.json", result)
    return result


def state_payload(
    guard: dict[str, str],
    stack: list[tuple[fmpq, fmpq, int]],
    terminal: list[dict[str, Any]],
    unresolved: list[dict[str, Any]],
    processed: int,
    evaluated: int,
    batches: int,
    accumulated_wall_seconds: float,
) -> dict[str, Any]:
    return {
        "schema": "lin-d1-global-first-event-uniqueness-checkpoint-v1",
        "guard": guard,
        "stack": [[str(lo), str(hi), depth] for lo, hi, depth in stack],
        "terminal": terminal,
        "unresolved": unresolved,
        "processed_box_count": processed,
        "dual_evaluated_box_count": evaluated,
        "completed_batch_count": batches,
        "accumulated_wall_seconds": accumulated_wall_seconds,
    }


def publish_checkpoint(output: Path, payload: dict[str, Any]) -> str:
    digest = sha256_bytes(canonical_bytes(payload))
    immutable = output / "checkpoints" / f"checkpoint-{digest}.json"
    if immutable.exists():
        existing = json.loads(immutable.read_text(encoding="utf-8"))
        if canonical_bytes(existing) != canonical_bytes(payload):
            raise RuntimeError("content-addressed checkpoint collision")
    else:
        atomic_write_json(immutable, payload)
        immutable.chmod(0o444)
    latest = {
        "checkpoint_sha256": digest,
        "checkpoint_relative_path": str(immutable.relative_to(output)),
        "payload": payload,
    }
    atomic_write_json(output / "CHECKPOINT.json", latest)
    return digest


def load_checkpoint(
    output: Path, guard: dict[str, str]
) -> tuple[list[tuple[fmpq, fmpq, int]], list[dict[str, Any]], list[dict[str, Any]], int, int, int, float] | None:
    latest_path = output / "CHECKPOINT.json"
    if not latest_path.exists():
        return None
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    payload = latest["payload"]
    if sha256_bytes(canonical_bytes(payload)) != latest["checkpoint_sha256"]:
        raise RuntimeError("checkpoint payload digest mismatch")
    immutable = output / latest["checkpoint_relative_path"]
    if sha256_file(immutable) != sha256_bytes(json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"):
        raise RuntimeError("immutable checkpoint file digest mismatch")
    if payload["guard"] != guard:
        raise RuntimeError("checkpoint compatibility guard mismatch")
    stack = [(parse_q(lo), parse_q(hi), int(depth)) for lo, hi, depth in payload["stack"]]
    return (
        stack,
        list(payload["terminal"]),
        list(payload["unresolved"]),
        int(payload["processed_box_count"]),
        int(payload["dual_evaluated_box_count"]),
        int(payload["completed_batch_count"]),
        float(payload["accumulated_wall_seconds"]),
    )


def root_terminal(root: dict[str, Any]) -> dict[str, Any]:
    return {
        "a_exact_bounds": root["root_exact_bounds"],
        "a_decimal_bounds": [float(parse_q(x)) for x in root["root_exact_bounds"]],
        "depth": None,
        "classification": "CERTIFIED_D1_UNIQUE_ROOT",
        "record": root,
    }


def coverage_audit(
    terminal: list[dict[str, Any]], domain_lo: fmpq, domain_hi: fmpq
) -> dict[str, Any]:
    ordered = sorted(terminal, key=lambda row: parse_q(row["a_exact_bounds"][0]))
    contiguous = bool(ordered) and parse_q(ordered[0]["a_exact_bounds"][0]) == domain_lo
    previous = domain_lo
    positive_width = True
    for row in ordered:
        lo, hi = map(parse_q, row["a_exact_bounds"])
        contiguous = contiguous and lo == previous
        positive_width = positive_width and hi > lo
        previous = hi
    contiguous = contiguous and previous == domain_hi
    roots = [row for row in ordered if row["classification"] == "CERTIFIED_D1_UNIQUE_ROOT"]
    return {
        "exact_contiguous_cover": contiguous,
        "all_boxes_positive_width": positive_width,
        "first_exact_endpoint": ordered[0]["a_exact_bounds"][0] if ordered else None,
        "last_exact_endpoint": ordered[-1]["a_exact_bounds"][1] if ordered else None,
        "certified_root_box_count": len(roots),
    }


def write_status(
    output: Path,
    *,
    phase: str,
    workers: int,
    stack: int,
    terminal: int,
    unresolved: int,
    evaluated: int,
    batches: int,
    elapsed: float,
    checkpoint_sha256: str | None,
) -> None:
    atomic_write_json(
        output / "STATUS.json",
        {
            "schema": "lin-d1-global-first-event-uniqueness-status-v1",
            "informational_only": True,
            "updated_utc": utc_now(),
            "phase": phase,
            "pid": os.getpid(),
            "workers": workers,
            "pending_stack_count": stack,
            "terminal_box_count": terminal,
            "unresolved_box_count": unresolved,
            "dual_evaluated_box_count": evaluated,
            "completed_batch_count": batches,
            "accumulated_wall_seconds": elapsed,
            "latest_checkpoint_sha256": checkpoint_sha256,
        },
    )


def run_production(
    output: Path,
    guard: dict[str, str],
    resolved: dict[str, Path],
    primary: Any,
    independent: Any,
    workers: int,
) -> dict[str, Any]:
    preflight_path = output / "PREFLIGHT.json"
    if not preflight_path.exists():
        raise RuntimeError("production requires preflight")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("status") != "PASS" or preflight.get("guard") != guard:
        raise RuntimeError("preflight guard mismatch")
    root = preflight["root_authority"]
    if not root.get("pass"):
        raise RuntimeError("root authority is not admitted")

    domain_lo = fmpq(0)
    domain_hi = primary.V0_Q
    root_lo, root_hi = map(parse_q, root["root_exact_bounds"])
    target_width = parse_q(CONFIG["target_launch_width"])
    resumed = load_checkpoint(output, guard)
    if resumed is None:
        stack = [(root_hi, domain_hi, 0), (domain_lo, root_lo, 0)]
        terminal = [root_terminal(root)]
        unresolved: list[dict[str, Any]] = []
        processed = evaluated = batches = 0
        base_wall = 0.0
        checkpoint = publish_checkpoint(
            output,
            state_payload(guard, stack, terminal, unresolved, processed, evaluated, batches, base_wall),
        )
    else:
        stack, terminal, unresolved, processed, evaluated, batches, base_wall = resumed
        checkpoint = json.loads((output / "CHECKPOINT.json").read_text(encoding="utf-8"))["checkpoint_sha256"]

    started = time.monotonic()
    batch_limit = max(1, workers * CONFIG["batch_size_multiplier"])
    write_status(
        output,
        phase="PRODUCTION",
        workers=workers,
        stack=len(stack),
        terminal=len(terminal),
        unresolved=len(unresolved),
        evaluated=evaluated,
        batches=batches,
        elapsed=base_wall,
        checkpoint_sha256=checkpoint,
    )

    context = multiprocessing.get_context("spawn")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers,
        mp_context=context,
        initializer=worker_initialize,
        initargs=(str(resolved["primary_base_source"]), str(resolved["independent_source"])),
    ) as executor:
        while stack:
            tasks: list[tuple[str, str, int]] = []
            while stack and len(tasks) < batch_limit:
                lo, hi, depth = stack.pop()
                processed += 1
                curvature = dual_curvature(primary, independent, lo, hi)
                if curvature["both_strictly_negative"]:
                    terminal.append(
                        {
                            "a_exact_bounds": [str(lo), str(hi)],
                            "a_decimal_bounds": [float(lo), float(hi)],
                            "depth": depth,
                            "classification": "NEGATIVE_CURVATURE_EXCLUDED",
                            "record": {"curvature": curvature},
                        }
                    )
                elif hi - lo > target_width:
                    middle = (lo + hi) / 2
                    stack.append((middle, hi, depth + 1))
                    stack.append((lo, middle, depth + 1))
                else:
                    tasks.append((str(lo), str(hi), depth))

            if not tasks:
                elapsed = base_wall + (time.monotonic() - started)
                checkpoint = publish_checkpoint(
                    output,
                    state_payload(guard, stack, terminal, unresolved, processed, evaluated, batches, elapsed),
                )
                write_status(
                    output,
                    phase="PRODUCTION",
                    workers=workers,
                    stack=len(stack),
                    terminal=len(terminal),
                    unresolved=len(unresolved),
                    evaluated=evaluated,
                    batches=batches,
                    elapsed=elapsed,
                    checkpoint_sha256=checkpoint,
                )
                continue

            # The latest checkpoint predates removal of this batch. A crash or
            # worker abort therefore safely replays the whole batch.
            futures = [executor.submit(evaluate_box_task, task) for task in tasks]
            records = [future.result() for future in futures]
            evaluated += len(records)
            batches += 1
            for record in records:
                lo, hi = map(parse_q, record["a_exact_bounds"])
                depth = int(record["depth"])
                if record["qualified_dual_exclusion"]:
                    terminal.append(
                        {
                            "a_exact_bounds": record["a_exact_bounds"],
                            "a_decimal_bounds": record["a_decimal_bounds"],
                            "depth": depth,
                            "classification": "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED",
                            "record": record,
                        }
                    )
                elif depth >= CONFIG["maximum_bisection_depth"]:
                    row = {
                        "a_exact_bounds": record["a_exact_bounds"],
                        "a_decimal_bounds": record["a_decimal_bounds"],
                        "depth": depth,
                        "classification": "UNRESOLVED",
                        "record": record,
                    }
                    terminal.append(row)
                    unresolved.append(row)
                else:
                    middle = (lo + hi) / 2
                    stack.append((middle, hi, depth + 1))
                    stack.append((lo, middle, depth + 1))

            elapsed = base_wall + (time.monotonic() - started)
            checkpoint = publish_checkpoint(
                output,
                state_payload(guard, stack, terminal, unresolved, processed, evaluated, batches, elapsed),
            )
            write_status(
                output,
                phase="PRODUCTION",
                workers=workers,
                stack=len(stack),
                terminal=len(terminal),
                unresolved=len(unresolved),
                evaluated=evaluated,
                batches=batches,
                elapsed=elapsed,
                checkpoint_sha256=checkpoint,
            )

    ordered = sorted(terminal, key=lambda row: parse_q(row["a_exact_bounds"][0]))
    audit = coverage_audit(ordered, domain_lo, domain_hi)
    counts: dict[str, int] = {}
    for row in ordered:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    passed = bool(
        not unresolved
        and audit["exact_contiguous_cover"]
        and audit["all_boxes_positive_width"]
        and audit["certified_root_box_count"] == 1
        and all(
            row["classification"]
            in {
                "CERTIFIED_D1_UNIQUE_ROOT",
                "NEGATIVE_CURVATURE_EXCLUDED",
                "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED",
            }
            for row in ordered
        )
    )
    total_wall = base_wall + (time.monotonic() - started)
    result = {
        "schema": "lin-d1-global-first-event-uniqueness-result-v1",
        "status": "COMPLETE" if passed else "INCOMPLETE",
        "classification": SUCCESS_CLASSIFICATION if passed else UNRESOLVED_CLASSIFICATION,
        "authority": "GAP_FREE_DUAL_PRODUCER_INTERVAL_COVER_OF_DECLARED_STATIC_FIRST_EVENT_SHOOTING_PROBLEM",
        "completed_utc": utc_now(),
        "guard": guard,
        "resumed_from_checkpoint": resumed is not None,
        "runtime": {
            "accumulated_wall_seconds": total_wall,
            "current_invocation_wall_seconds": time.monotonic() - started,
            "workers": workers,
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": CONFIG["arb_precision_bits"],
        },
        "frozen_design": CONFIG,
        "root_authority": root,
        "terminal_box_count": len(ordered),
        "dual_evaluated_box_count_including_pre_split_attempts": evaluated,
        "processed_box_count": processed,
        "completed_batch_count": batches,
        "classification_counts": counts,
        "coverage_audit": audit,
        "unresolved": unresolved,
        "terminal_boxes": ordered,
        "claim_boundary": [
            "The result concerns only the declared reduced static first-event shooting problem.",
            "It establishes neither dynamical selection nor stability.",
            "It is not a collapse, MOTS, event-horizon, radion-transition, or baby-universe result.",
        ],
    }
    atomic_write_json(output / "RESULT.json", result)
    terminal_record = {
        "schema": "lin-d1-global-first-event-uniqueness-terminal-v1",
        "status": result["status"],
        "classification": result["classification"],
        "completed_utc": result["completed_utc"],
        "result_sha256": sha256_file(output / "RESULT.json"),
        "guard": guard,
        "predecessors_mutated": False,
    }
    atomic_write_json(output / "TERMINAL_CHECKPOINT.json", terminal_record)
    write_status(
        output,
        phase="TERMINAL",
        workers=workers,
        stack=0,
        terminal=len(ordered),
        unresolved=len(unresolved),
        evaluated=evaluated,
        batches=batches,
        elapsed=total_wall,
        checkpoint_sha256=checkpoint,
    )
    return result


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

    bindings, guard, resolved = verify_bindings(args.bindings.resolve())
    del bindings
    primary, independent = import_producers(resolved, f"main_{os.getpid()}")
    try:
        if args.mode == "preflight":
            result = run_preflight(
                args.bindings.resolve(), args.output.resolve(), guard, resolved, primary, independent
            )
        else:
            result = run_production(
                args.output.resolve(), guard, resolved, primary, independent, args.workers
            )
        print(json.dumps({"mode": args.mode, "status": result["status"], "classification": result.get("classification")}, sort_keys=True))
    except Exception as exc:
        failure = {
            "schema": "lin-d1-global-first-event-uniqueness-failure-v1",
            "status": "INCOMPLETE",
            "mode": args.mode,
            "failed_utc": utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "guard": guard,
            "checkpoint_present": (args.output / "CHECKPOINT.json").exists(),
        }
        atomic_write_json(args.output / "FAILURE.json", failure)
        raise


if __name__ == "__main__":
    main()
