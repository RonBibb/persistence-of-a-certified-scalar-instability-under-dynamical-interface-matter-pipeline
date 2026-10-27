#!/usr/bin/env python3
"""Validated two-parameter neighborhood theorem for the Lin static D1 root.

The numerical ODE and junction operators are imported from sealed predecessor
sources after digest verification.  This successor adds exact parameter-ball
propagation, a frozen parametric interval-Newton gate, gap-free launch covers,
fixed-D0 replay, and exact-resumption orchestration.
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
from typing import Any, Callable

from flint import arb, ctx, fmpq


CONFIG: dict[str, Any] = {
    "schema": "lin-static-parameter-neighborhood-config-v1",
    "parameter_box": {
        "v1": [
            "3256417487256207/36028797018963968",
            "101988226458125/1125899906842624",
        ],
        "lambda_b": [
            "-1703752349608937/281474976710656",
            "-1703696054613595/281474976710656",
        ],
    },
    "central_parameters_decimal_labels": {
        "v1": "0.09048374180359596",
        "lambda_b": "-6.052844277744164",
    },
    "root_center": "1783621195069987/18014398509481984",
    "root_box": [
        "222948145784121/2251799813685248",
        "891828611933503/9007199254740992",
    ],
    "launch_domain": ["0", "V0_Q"],
    "proper_distance_endpoint": "2",
    "arb_precision_bits": 768,
    "primary_steps": 8192,
    "independent_steps": 8192,
    "d0_steps": 1024,
    "target_launch_width": "1/65536",
    "maximum_launch_bisection_depth": 48,
    "maximum_parameter_subdivision_depth": 2,
    "parameter_split_axes": ["v1", "lambda_b"],
    "default_workers": 10,
    "checkpoint_max_seconds": 180,
    "batch_size_multiplier": 1,
    "event_rule": (
        "all earlier cells G>0; contiguous zero-containing cells; union G_s<0; "
        "immediately following cell G<0"
    ),
}

SUCCESS = "STATIC_D1_ROOT_UNIQUE_AND_D0_EXCLUDED_ON_FROZEN_V1_LAMBDA_B_NEIGHBORHOOD"
INCOMPLETE = "STATIC_PARAMETER_NEIGHBORHOOD_THEOREM_UNRESOLVED"


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


def qpair(values: list[str]) -> tuple[fmpq, fmpq]:
    return parse_q(values[0]), parse_q(values[1])


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_bindings(bindings_path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    declared = {
        "runner_source_sha256": Path(__file__).resolve(),
        "contract_sha256": branch / "CONTRACT.md",
        "test_source_sha256": branch / "test_parameter_neighborhood.py",
        "postrun_audit_source_sha256": branch / "postrun_audit.py",
    }
    for key, path in declared.items():
        if sha256_file(path) != bindings[key]:
            raise RuntimeError(f"binding mismatch: {key}")
    if sha256_bytes(canonical_bytes(CONFIG)) != bindings["config_sha256"]:
        raise RuntimeError("configuration digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"bound predecessor mismatch: {name}")
        resolved[name] = path
    guard = {
        "runner_source_sha256": bindings["runner_source_sha256"],
        "contract_sha256": bindings["contract_sha256"],
        "config_sha256": bindings["config_sha256"],
        "bindings_sha256": sha256_file(bindings_path),
    }
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return guard, resolved


def make_ball(module: Any, lo: fmpq, hi: fmpq) -> arb:
    return module.ball(lo, hi)


def set_parameter_cell(module: Any, cell: dict[str, Any]) -> None:
    v1_lo, v1_hi = qpair(cell["v1"])
    lb_lo, lb_hi = qpair(cell["lambda_b"])
    module.V1_Q = make_ball(module, v1_lo, v1_hi)
    module.LAMBDA_B_Q = make_ball(module, lb_lo, lb_hi)


def bounds(module: Any, value: arb) -> tuple[fmpq, fmpq]:
    return module.bounds(value)


def interval_public(module: Any, value: arb) -> dict[str, Any]:
    lo, hi = bounds(module, value)
    return {
        "exact_bounds": [str(lo), str(hi)],
        "decimal_bounds": [float(lo), float(hi)],
        "contains_zero": lo <= 0 <= hi,
        "width": float(hi - lo),
    }


def sign(module: Any, value: arb) -> str:
    lo, hi = bounds(module, value)
    if lo > 0:
        return "positive"
    if hi < 0:
        return "negative"
    return "zero-containing"


def distance_from_zero(pair: tuple[fmpq, fmpq]) -> fmpq:
    lo, hi = pair
    if lo > 0:
        return lo
    if hi < 0:
        return -hi
    return fmpq(0)


def event_record(module: Any, lo: fmpq, hi: fmpq, steps: int, producer: str) -> dict[str, Any]:
    started = time.monotonic()
    step = module.S_END / steps
    state = module.launch(module.ball(lo, hi))
    zero_cells: list[int] = []
    records: list[dict[str, arb]] = []
    maximum_picard = 0
    negative_after: int | None = None
    obstruction: str | None = None
    q_key = "hprime" if producer == "primary" else "q_a"
    gs_key = "Gs" if producer == "primary" else "G_s"
    try:
        for index in range(steps):
            enclosure, iterations = module.picard_box(state, step)
            maximum_picard = max(maximum_picard, iterations)
            quantities = (
                module.event_quantities(enclosure)
                if producer == "primary"
                else module.upper_quantities(enclosure)
            )
            current = sign(module, quantities["G"])
            if not zero_cells:
                if current == "positive":
                    pass
                elif current == "zero-containing":
                    zero_cells.append(index)
                    records.append(quantities)
                else:
                    obstruction = "STRICTLY_NEGATIVE_CELL_BEFORE_ZERO_CLUSTER"
                    break
            else:
                if current == "zero-containing":
                    if index != zero_cells[-1] + 1:
                        obstruction = "NONCONTIGUOUS_ZERO_CLUSTER"
                        break
                    zero_cells.append(index)
                    records.append(quantities)
                elif current == "negative":
                    negative_after = index
                    break
                else:
                    obstruction = "POSITIVE_CELL_AFTER_ZERO_CLUSTER"
                    break
            state = module.advance(state, enclosure, step)
    except Exception as exc:
        obstruction = f"{type(exc).__name__}: {exc}"
    if not zero_cells and obstruction is None:
        obstruction = "NO_ZERO_CLUSTER_BEFORE_S_END"
    if zero_cells and negative_after is None and obstruction is None:
        obstruction = "ZERO_CLUSTER_NOT_CLOSED_BEFORE_S_END"
    if not records:
        return {
            "producer": producer,
            "validated": False,
            "obstruction": obstruction,
            "event_cells": None,
            "wall_seconds": time.monotonic() - started,
            "maximum_picard_iterations": maximum_picard,
        }
    G = module.union_all([row["G"] for row in records])
    Gs = module.union_all([row[gs_key] for row in records])
    h = module.union_all([row["h"] for row in records])
    qa = module.union_all([row[q_key] for row in records])
    Gs_bounds = bounds(module, Gs)
    qa_bounds = bounds(module, qa)
    validated = bool(
        obstruction is None
        and zero_cells == list(range(zero_cells[0], zero_cells[-1] + 1))
        and negative_after == zero_cells[-1] + 1
        and Gs_bounds[1] < 0
    )
    return {
        "producer": producer,
        "steps": steps,
        "validated": validated,
        "obstruction": obstruction,
        "event_cells": [zero_cells[0], zero_cells[-1]],
        "negative_after_cell": negative_after,
        "event_bracket_exact": [str(zero_cells[0] * step), str((zero_cells[-1] + 1) * step)],
        "G": interval_public(module, G),
        "G_s": interval_public(module, Gs),
        "G_s_strictly_negative": Gs_bounds[1] < 0,
        "h": interval_public(module, h),
        "h_sign": sign(module, h),
        "q_a": interval_public(module, qa),
        "q_a_excludes_zero": qa_bounds[0] > 0 or qa_bounds[1] < 0,
        "maximum_picard_iterations": maximum_picard,
        "wall_seconds": time.monotonic() - started,
        "_h": h,
        "_q_a": qa,
    }


def public_event(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def producer_newton(module: Any, producer: str) -> dict[str, Any]:
    root_lo, root_hi = qpair(CONFIG["root_box"])
    center = parse_q(CONFIG["root_center"])
    steps = CONFIG["primary_steps"] if producer == "primary" else CONFIG["independent_steps"]
    box_event = event_record(module, root_lo, root_hi, steps, producer)
    center_event = event_record(module, center, center, steps, producer)
    qualified = False
    newton_public: dict[str, Any] | None = None
    strict_margin = fmpq(0)
    if (
        box_event.get("validated")
        and center_event.get("validated")
        and box_event.get("q_a_excludes_zero")
    ):
        newton = arb(center) - center_event["_h"] / box_event["_q_a"]
        newton_lo, newton_hi = bounds(module, newton)
        strict_margin = min(newton_lo - root_lo, root_hi - newton_hi)
        qualified = strict_margin > 0
        newton_public = interval_public(module, newton)
    return {
        "producer": producer,
        "qualified_parametric_interval_newton": qualified,
        "root_box_event": public_event(box_event),
        "center_event": public_event(center_event),
        "newton_image": newton_public,
        "strict_inclusion_margin_exact": str(strict_margin),
        "strict_inclusion_margin_decimal": float(strict_margin),
    }


def root_certificate(primary: Any, independent: Any, cell: dict[str, Any]) -> dict[str, Any]:
    set_parameter_cell(primary, cell)
    set_parameter_cell(independent, cell)
    primary_record = producer_newton(primary, "primary")
    independent_record = producer_newton(independent, "independent")
    passed = bool(
        primary_record["qualified_parametric_interval_newton"]
        and independent_record["qualified_parametric_interval_newton"]
    )
    return {
        "pass": passed,
        "parameter_cell": cell,
        "root_box_exact_bounds": CONFIG["root_box"],
        "root_center_exact": CONFIG["root_center"],
        "primary": primary_record,
        "independent": independent_record,
    }


_GLOBAL_WORKER: dict[str, Any] = {}


def global_worker_initialize(primary_path: str, independent_path: str, cell: dict[str, Any]) -> None:
    sys.dont_write_bytecode = True
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    ctx.prec = CONFIG["arb_precision_bits"]
    primary = load_module(f"pn_primary_{os.getpid()}", Path(primary_path))
    independent = load_module(f"pn_independent_{os.getpid()}", Path(independent_path))
    set_parameter_cell(primary, cell)
    set_parameter_cell(independent, cell)
    _GLOBAL_WORKER["primary"] = primary
    _GLOBAL_WORKER["independent"] = independent


def global_box_task(task: tuple[str, str, int]) -> dict[str, Any]:
    lo_text, hi_text, depth = task
    lo, hi = parse_q(lo_text), parse_q(hi_text)
    primary = event_record(_GLOBAL_WORKER["primary"], lo, hi, CONFIG["primary_steps"], "primary")
    independent = event_record(
        _GLOBAL_WORKER["independent"], lo, hi, CONFIG["independent_steps"], "independent"
    )
    same_sign = (
        primary.get("h_sign") in {"positive", "negative"}
        and primary.get("h_sign") == independent.get("h_sign")
    )
    qualified = bool(
        primary.get("validated")
        and independent.get("validated")
        and primary.get("h", {}).get("contains_zero") is False
        and independent.get("h", {}).get("contains_zero") is False
        and same_sign
    )
    return {
        "a_exact_bounds": [lo_text, hi_text],
        "depth": depth,
        "qualified_dual_exclusion": qualified,
        "same_h_sign": same_sign,
        "h_sign": primary.get("h_sign") if same_sign else None,
        "primary": public_event(primary),
        "independent": public_event(independent),
    }


def dual_curvature(primary: Any, independent: Any, lo: fmpq, hi: fmpq) -> dict[str, Any]:
    p = bounds(primary, primary.launch(primary.ball(lo, hi))[5])
    q = bounds(independent, independent.launch(independent.ball(lo, hi))[5])
    return {
        "both_strictly_negative": p[1] < 0 and q[1] < 0,
        "primary_exact_bounds": [str(p[0]), str(p[1])],
        "independent_exact_bounds": [str(q[0]), str(q[1])],
    }


def launch_coverage(terminal: list[dict[str, Any]], domain_hi: fmpq) -> dict[str, Any]:
    ordered = sorted(terminal, key=lambda row: parse_q(row["a_exact_bounds"][0]))
    previous = fmpq(0)
    contiguous = bool(ordered)
    positive = True
    roots = 0
    for row in ordered:
        lo, hi = qpair(row["a_exact_bounds"])
        contiguous &= lo == previous
        positive &= hi > lo
        previous = hi
        roots += row["classification"] == "CERTIFIED_PARAMETRIC_ROOT_CONTAINER"
    return {
        "exact_contiguous_cover": contiguous and previous == domain_hi,
        "all_boxes_positive_width": positive,
        "certified_root_box_count": roots,
        "first_exact_endpoint": ordered[0]["a_exact_bounds"][0] if ordered else None,
        "last_exact_endpoint": ordered[-1]["a_exact_bounds"][1] if ordered else None,
    }


_D0_WORKER: dict[str, Any] = {}


def d0_worker_initialize(flow_path: str, cell: dict[str, Any]) -> None:
    sys.dont_write_bytecode = True
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    ctx.prec = CONFIG["arb_precision_bits"]
    flow = load_module(f"pn_d0_flow_{os.getpid()}", Path(flow_path))
    set_parameter_cell(flow, cell)
    _D0_WORKER["flow"] = flow


def d0_box_task(task: tuple[int, str, str, int]) -> dict[str, Any]:
    index, lo_text, hi_text, depth = task
    flow = _D0_WORKER["flow"]
    lo, hi = parse_q(lo_text), parse_q(hi_text)
    D0 = dyadic("0.9996389747145851")
    step = D0 / CONFIG["d0_steps"]
    state = flow.launch(flow.ball(lo, hi))
    maximum_picard = 0
    for _ in range(CONFIG["d0_steps"]):
        enclosure, iterations = flow.picard_box(state, step)
        maximum_picard = max(maximum_picard, iterations)
        first = flow.rhs(state)
        second = flow.second_derivative(enclosure, flow.rhs(enclosure))
        state = [
            value + arb(step) * f1 + arb(step * step / 2) * f2
            for value, f1, f2 in zip(state, first, second, strict=True)
        ]
    G, scalar = flow.residuals(state)
    G_bounds = bounds(flow, G)
    scalar_bounds = bounds(flow, scalar)
    G_distance = distance_from_zero(G_bounds)
    scalar_distance = distance_from_zero(scalar_bounds)
    floor = max(G_distance, scalar_distance)
    return {
        "parent_index": index,
        "a_exact_bounds": [lo_text, hi_text],
        "depth": depth,
        "G": interval_public(flow, G),
        "scalar_residual": interval_public(flow, scalar),
        "residual_vector_lower_bound_exact": str(floor),
        "residual_vector_lower_bound_decimal": float(floor),
        "excluded": floor > 0,
        "maximum_picard_iterations": maximum_picard,
    }


def parameter_cell(depth: int, v1: tuple[fmpq, fmpq], lb: tuple[fmpq, fmpq]) -> dict[str, Any]:
    return {"depth": depth, "v1": [str(v1[0]), str(v1[1])], "lambda_b": [str(lb[0]), str(lb[1])]}


def split_parameter_cell(cell: dict[str, Any]) -> list[dict[str, Any]]:
    depth = int(cell["depth"])
    axis = CONFIG["parameter_split_axes"][depth % len(CONFIG["parameter_split_axes"])]
    v1 = qpair(cell["v1"])
    lb = qpair(cell["lambda_b"])
    target = v1 if axis == "v1" else lb
    middle = (target[0] + target[1]) / 2
    if axis == "v1":
        return [parameter_cell(depth + 1, (v1[0], middle), lb), parameter_cell(depth + 1, (middle, v1[1]), lb)]
    return [parameter_cell(depth + 1, v1, (lb[0], middle)), parameter_cell(depth + 1, v1, (middle, lb[1]))]


def parameter_volume(cell: dict[str, Any]) -> fmpq:
    v1 = qpair(cell["v1"])
    lb = qpair(cell["lambda_b"])
    return (v1[1] - v1[0]) * (lb[1] - lb[0])


def cell_faces(cell: dict[str, Any]) -> list[str]:
    faces: list[str] = []
    aggregate_v1 = qpair(CONFIG["parameter_box"]["v1"])
    aggregate_lb = qpair(CONFIG["parameter_box"]["lambda_b"])
    v1 = qpair(cell["v1"])
    lb = qpair(cell["lambda_b"])
    if v1[0] == aggregate_v1[0]:
        faces.append("v1_lower")
    if v1[1] == aggregate_v1[1]:
        faces.append("v1_upper")
    if lb[0] == aggregate_lb[0]:
        faces.append("lambda_b_lower")
    if lb[1] == aggregate_lb[1]:
        faces.append("lambda_b_upper")
    return faces


def checkpoint_payload(guard: dict[str, str], state: dict[str, Any]) -> dict[str, Any]:
    return {"schema": "lin-static-parameter-neighborhood-checkpoint-v1", "guard": guard, "state": state}


def publish_checkpoint(output: Path, guard: dict[str, str], state: dict[str, Any]) -> str:
    payload = checkpoint_payload(guard, state)
    digest = sha256_bytes(canonical_bytes(payload))
    immutable = output / "checkpoints" / f"checkpoint-{digest}.json"
    if immutable.exists():
        if canonical_bytes(json.loads(immutable.read_text())) != canonical_bytes(payload):
            raise RuntimeError("content-addressed checkpoint collision")
    else:
        atomic_write_json(immutable, payload)
        immutable.chmod(0o444)
    atomic_write_json(
        output / "CHECKPOINT.json",
        {"checkpoint_sha256": digest, "checkpoint_relative_path": str(immutable.relative_to(output)), "payload": payload},
    )
    return digest


def load_checkpoint(output: Path, guard: dict[str, str]) -> dict[str, Any] | None:
    latest_path = output / "CHECKPOINT.json"
    if not latest_path.exists():
        return None
    latest = json.loads(latest_path.read_text())
    payload = latest["payload"]
    if sha256_bytes(canonical_bytes(payload)) != latest["checkpoint_sha256"]:
        raise RuntimeError("checkpoint payload digest mismatch")
    immutable = output / latest["checkpoint_relative_path"]
    if sha256_file(immutable) != sha256_bytes(json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"):
        raise RuntimeError("immutable checkpoint file digest mismatch")
    if payload["guard"] != guard:
        raise RuntimeError("checkpoint guard mismatch")
    return payload["state"]


def write_status(output: Path, state: dict[str, Any], checkpoint: str | None, workers: int) -> None:
    current = state.get("current") or {}
    global_state = current.get("global") or {}
    d0_state = current.get("d0") or {}
    atomic_write_json(
        output / "STATUS.json",
        {
            "schema": "lin-static-parameter-neighborhood-status-v1",
            "informational_only": True,
            "updated_utc": utc_now(),
            "pid": os.getpid(),
            "phase": current.get("phase", "PARAMETER_QUEUE"),
            "workers": workers,
            "pending_parameter_cells": len(state.get("pending_cells", [])),
            "completed_parameter_cells": len(state.get("terminal_cells", [])),
            "attempted_parameter_cells": len(state.get("attempted_cells", [])),
            "current_parameter_cell": current.get("cell"),
            "global_pending_launch_boxes": len(global_state.get("stack", [])),
            "global_terminal_launch_boxes": len(global_state.get("terminal", [])),
            "d0_pending_boxes": len(d0_state.get("pending", [])),
            "d0_completed_boxes": len(d0_state.get("records", [])),
            "latest_checkpoint_sha256": checkpoint,
        },
    )


def save_state(output: Path, guard: dict[str, str], state: dict[str, Any], workers: int) -> None:
    digest = publish_checkpoint(output, guard, state)
    write_status(output, state, digest, workers)


def run_preflight(output: Path, guard: dict[str, str], resolved: dict[str, Path]) -> dict[str, Any]:
    ctx.prec = CONFIG["arb_precision_bits"]
    primary = load_module("pn_preflight_primary", resolved["primary_source"])
    independent = load_module("pn_preflight_independent", resolved["independent_source"])
    flow = load_module("pn_preflight_flow", resolved["flow_source"])
    central = parameter_cell(
        0,
        (dyadic(CONFIG["central_parameters_decimal_labels"]["v1"]),) * 2,
        (dyadic(CONFIG["central_parameters_decimal_labels"]["lambda_b"]),) * 2,
    )
    set_parameter_cell(primary, central)
    set_parameter_cell(independent, central)
    set_parameter_cell(flow, central)
    producer_agreement = bool(primary.V0_Q == independent.V0_Q and primary.S_END == independent.S_END)
    if not producer_agreement:
        raise RuntimeError("producer constants disagree")
    controls = independent.algebra_controls()
    if not all(controls.values()):
        raise RuntimeError("independent algebra controls failed")
    interval = primary.ball(fmpq(1, 3), fmpq(1, 2))
    interval_controls = {
        "contains_2_over_5": bool(interval.contains(arb(fmpq(2, 5)))),
        "excludes_3_over_5": not bool(interval.contains(arb(fmpq(3, 5)))),
    }
    if not all(interval_controls.values()):
        raise RuntimeError("interval controls failed")
    parent = json.loads(resolved["d2a_result"].read_text())
    rows = parent["terminal_boxes"]
    previous = fmpq(0)
    parent_cover = True
    for row in rows:
        lo, hi = qpair(row["a_exact_bounds"])
        parent_cover &= lo == previous and hi > lo
        previous = hi
    parent_cover &= previous == primary.V0_Q and len(rows) == 693
    if not parent_cover:
        raise RuntimeError("sealed D2A cover is not the expected exact 693-box cover")
    root_lo, root_hi = qpair(CONFIG["root_box"])
    center = parse_q(CONFIG["root_center"])
    if not root_lo < center < root_hi:
        raise RuntimeError("root center is outside frozen container")
    result = {
        "schema": "lin-static-parameter-neighborhood-preflight-v1",
        "status": "PASS",
        "completed_utc": utc_now(),
        "guard": guard,
        "producer_constant_agreement": producer_agreement,
        "independent_algebra_controls": controls,
        "interval_controls": interval_controls,
        "sealed_d2a_exact_cover": parent_cover,
        "sealed_d2a_terminal_box_count": len(rows),
        "root_container_ordered": True,
        "parameter_subdivision_axes": CONFIG["parameter_split_axes"],
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": CONFIG["arb_precision_bits"],
        },
    }
    atomic_write_json(output / "PREFLIGHT.json", result)
    return result


def initialize_global_state(root: dict[str, Any], V0: fmpq) -> dict[str, Any]:
    root_lo, root_hi = qpair(CONFIG["root_box"])
    root_terminal = {
        "a_exact_bounds": CONFIG["root_box"],
        "depth": None,
        "classification": "CERTIFIED_PARAMETRIC_ROOT_CONTAINER",
        "record": root,
    }
    return {
        "stack": [[str(root_hi), str(V0), 0], ["0", str(root_lo), 0]],
        "terminal": [root_terminal],
        "unresolved": [],
        "processed": 0,
        "evaluated": 0,
        "batches": 0,
    }


def run_global_cover(
    current: dict[str, Any],
    primary: Any,
    independent: Any,
    resolved: dict[str, Path],
    state: dict[str, Any],
    output: Path,
    guard: dict[str, str],
    workers: int,
) -> dict[str, Any]:
    cell = current["cell"]
    set_parameter_cell(primary, cell)
    set_parameter_cell(independent, cell)
    global_state = current["global"]
    target_width = parse_q(CONFIG["target_launch_width"])
    context = multiprocessing.get_context("spawn")
    batch_limit = max(1, workers * CONFIG["batch_size_multiplier"])
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers,
        mp_context=context,
        initializer=global_worker_initialize,
        initargs=(str(resolved["primary_source"]), str(resolved["independent_source"]), cell),
    ) as executor:
        while global_state["stack"]:
            tasks: list[tuple[str, str, int]] = []
            while global_state["stack"] and len(tasks) < batch_limit:
                lo_text, hi_text, depth = global_state["stack"].pop()
                lo, hi = parse_q(lo_text), parse_q(hi_text)
                global_state["processed"] += 1
                curvature = dual_curvature(primary, independent, lo, hi)
                if curvature["both_strictly_negative"]:
                    global_state["terminal"].append(
                        {
                            "a_exact_bounds": [lo_text, hi_text],
                            "depth": depth,
                            "classification": "NEGATIVE_CURVATURE_EXCLUDED",
                            "record": {"curvature": curvature},
                        }
                    )
                elif hi - lo > target_width:
                    middle = (lo + hi) / 2
                    global_state["stack"].append([str(middle), hi_text, depth + 1])
                    global_state["stack"].append([lo_text, str(middle), depth + 1])
                else:
                    tasks.append((lo_text, hi_text, depth))
            if tasks:
                records = [future.result() for future in [executor.submit(global_box_task, task) for task in tasks]]
                global_state["evaluated"] += len(records)
                global_state["batches"] += 1
                for record in records:
                    lo, hi = qpair(record["a_exact_bounds"])
                    depth = int(record["depth"])
                    if record["qualified_dual_exclusion"]:
                        global_state["terminal"].append(
                            {
                                "a_exact_bounds": record["a_exact_bounds"],
                                "depth": depth,
                                "classification": "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED",
                                "record": record,
                            }
                        )
                    elif depth >= CONFIG["maximum_launch_bisection_depth"]:
                        row = {
                            "a_exact_bounds": record["a_exact_bounds"],
                            "depth": depth,
                            "classification": "UNRESOLVED",
                            "record": record,
                        }
                        global_state["terminal"].append(row)
                        global_state["unresolved"].append(row)
                    else:
                        middle = (lo + hi) / 2
                        global_state["stack"].append([str(middle), str(hi), depth + 1])
                        global_state["stack"].append([str(lo), str(middle), depth + 1])
            save_state(output, guard, state, workers)
    audit = launch_coverage(global_state["terminal"], primary.V0_Q)
    passed = bool(
        not global_state["unresolved"]
        and audit["exact_contiguous_cover"]
        and audit["all_boxes_positive_width"]
        and audit["certified_root_box_count"] == 1
    )
    margins: list[tuple[fmpq, dict[str, Any]]] = []
    for row in global_state["terminal"]:
        if row["classification"] == "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED":
            record = row["record"]
            p = qpair(record["primary"]["h"]["exact_bounds"])
            q = qpair(record["independent"]["h"]["exact_bounds"])
            margins.append((min(distance_from_zero(p), distance_from_zero(q)), row))
    limiting = min(margins, key=lambda item: item[0]) if margins else None
    return {
        "pass": passed,
        "coverage_audit": audit,
        "terminal_box_count": len(global_state["terminal"]),
        "processed_box_count": global_state["processed"],
        "dual_evaluated_box_count": global_state["evaluated"],
        "unresolved": global_state["unresolved"],
        "limiting_h_exclusion_margin_exact": str(limiting[0]) if limiting else None,
        "limiting_h_exclusion_margin_decimal": float(limiting[0]) if limiting else None,
        "limiting_h_launch_box": limiting[1]["a_exact_bounds"] if limiting else None,
        "terminal_boxes": sorted(global_state["terminal"], key=lambda row: parse_q(row["a_exact_bounds"][0])),
    }


def initialize_d0_state(parent_rows: list[dict[str, Any]]) -> dict[str, Any]:
    negative: list[dict[str, Any]] = []
    pending: list[list[Any]] = []
    for index, row in enumerate(parent_rows):
        if row["classification"] == "NEGATIVE_CURVATURE_EXCLUDED":
            negative.append(
                {
                    "parent_index": index,
                    "a_exact_bounds": row["a_exact_bounds"],
                    "depth": row["depth"],
                    "classification": "NEGATIVE_CURVATURE_EXCLUDED",
                    "excluded": True,
                }
            )
        else:
            pending.append([index, row["a_exact_bounds"][0], row["a_exact_bounds"][1], row["depth"]])
    return {"pending": pending, "records": negative, "batches": 0}


def run_d0_cover(
    current: dict[str, Any],
    resolved: dict[str, Path],
    state: dict[str, Any],
    output: Path,
    guard: dict[str, str],
    workers: int,
) -> dict[str, Any]:
    d0_state = current["d0"]
    batch_limit = max(1, workers * CONFIG["batch_size_multiplier"])
    context = multiprocessing.get_context("spawn")
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=workers,
        mp_context=context,
        initializer=d0_worker_initialize,
        initargs=(str(resolved["flow_source"]), current["cell"]),
    ) as executor:
        while d0_state["pending"]:
            batch = [tuple(d0_state["pending"].pop()) for _ in range(min(batch_limit, len(d0_state["pending"])))]
            rows = [future.result() for future in [executor.submit(d0_box_task, task) for task in batch]]
            for row in rows:
                row["classification"] = "FIXED_D0_WALL_RESIDUAL_EXCLUDED" if row["excluded"] else "UNRESOLVED"
                d0_state["records"].append(row)
            d0_state["batches"] += 1
            save_state(output, guard, state, workers)
    ordered = sorted(d0_state["records"], key=lambda row: parse_q(row["a_exact_bounds"][0]))
    previous = fmpq(0)
    contiguous = bool(ordered)
    for row in ordered:
        lo, hi = qpair(row["a_exact_bounds"])
        contiguous &= lo == previous and hi > lo
        previous = hi
    flow = load_module(f"pn_d0_audit_{os.getpid()}_{time.time_ns()}", resolved["flow_source"])
    contiguous &= previous == flow.V0_Q
    unresolved = [row for row in ordered if not row["excluded"]]
    numeric = [row for row in ordered if row["classification"] != "NEGATIVE_CURVATURE_EXCLUDED"]
    limiting = min(numeric, key=lambda row: parse_q(row["residual_vector_lower_bound_exact"])) if numeric else None
    return {
        "pass": contiguous and not unresolved and len(ordered) == 693,
        "exact_contiguous_cover": contiguous,
        "terminal_box_count": len(ordered),
        "negative_curvature_box_count": sum(row["classification"] == "NEGATIVE_CURVATURE_EXCLUDED" for row in ordered),
        "integrated_box_count": len(numeric),
        "unresolved": unresolved,
        "limiting_residual_vector_lower_bound_exact": limiting["residual_vector_lower_bound_exact"] if limiting else None,
        "limiting_residual_vector_lower_bound_decimal": limiting["residual_vector_lower_bound_decimal"] if limiting else None,
        "limiting_launch_box": limiting["a_exact_bounds"] if limiting else None,
        "terminal_boxes": ordered,
    }


def run_production(
    output: Path,
    guard: dict[str, str],
    resolved: dict[str, Path],
    workers: int,
) -> dict[str, Any]:
    preflight = json.loads((output / "PREFLIGHT.json").read_text())
    if preflight.get("status") != "PASS" or preflight.get("guard") != guard:
        raise RuntimeError("production requires matching preflight")
    ctx.prec = CONFIG["arb_precision_bits"]
    primary = load_module("pn_main_primary", resolved["primary_source"])
    independent = load_module("pn_main_independent", resolved["independent_source"])
    parent_rows = json.loads(resolved["d2a_result"].read_text())["terminal_boxes"]
    resumed = load_checkpoint(output, guard)
    if resumed is None:
        aggregate = parameter_cell(0, qpair(CONFIG["parameter_box"]["v1"]), qpair(CONFIG["parameter_box"]["lambda_b"]))
        state = {
            "pending_cells": [aggregate],
            "attempted_cells": [],
            "terminal_cells": [],
            "current": None,
            "started_utc": utc_now(),
        }
        save_state(output, guard, state, workers)
    else:
        state = resumed
    while state["current"] is not None or state["pending_cells"]:
        if state["current"] is None:
            cell = state["pending_cells"].pop(0)
            state["current"] = {"cell": cell, "phase": "ROOT"}
            save_state(output, guard, state, workers)
        current = state["current"]
        cell = current["cell"]
        if current["phase"] == "ROOT":
            root = root_certificate(primary, independent, cell)
            current["root"] = root
            if root["pass"]:
                current["global"] = initialize_global_state(root, primary.V0_Q)
                current["phase"] = "GLOBAL"
            else:
                current["failure_gate"] = "PARAMETRIC_ROOT"
                current["phase"] = "FINISH_CELL"
            save_state(output, guard, state, workers)
        if current["phase"] == "GLOBAL":
            global_result = run_global_cover(current, primary, independent, resolved, state, output, guard, workers)
            current["global_result"] = global_result
            if global_result["pass"]:
                current["d0"] = initialize_d0_state(parent_rows)
                current["phase"] = "D0"
            else:
                current["failure_gate"] = "GLOBAL_FIRST_EVENT_COVER"
                current["phase"] = "FINISH_CELL"
            save_state(output, guard, state, workers)
        if current["phase"] == "D0":
            d0_result = run_d0_cover(current, resolved, state, output, guard, workers)
            current["d0_result"] = d0_result
            if not d0_result["pass"]:
                current["failure_gate"] = "FIXED_D0_EXCLUSION"
            current["phase"] = "FINISH_CELL"
            save_state(output, guard, state, workers)
        if current["phase"] == "FINISH_CELL":
            passed = bool(
                current.get("root", {}).get("pass")
                and current.get("global_result", {}).get("pass")
                and current.get("d0_result", {}).get("pass")
            )
            attempt = {
                "parameter_cell": cell,
                "pass": passed,
                "failure_gate": current.get("failure_gate"),
                "parameter_faces": cell_faces(cell),
                "root": current.get("root"),
                "global_result": current.get("global_result"),
                "d0_result": current.get("d0_result"),
            }
            state["attempted_cells"].append(attempt)
            if passed:
                state["terminal_cells"].append(attempt)
            elif int(cell["depth"]) < CONFIG["maximum_parameter_subdivision_depth"]:
                state["pending_cells"] = split_parameter_cell(cell) + state["pending_cells"]
            else:
                state["terminal_cells"].append(attempt)
            state["current"] = None
            save_state(output, guard, state, workers)

    total_volume = parameter_volume(parameter_cell(0, qpair(CONFIG["parameter_box"]["v1"]), qpair(CONFIG["parameter_box"]["lambda_b"])))
    admitted = sum((parameter_volume(row["parameter_cell"]) for row in state["terminal_cells"] if row["pass"]), fmpq(0))
    unresolved = [row for row in state["terminal_cells"] if not row["pass"]]
    passed = not unresolved and admitted == total_volume
    root_margins: list[tuple[fmpq, dict[str, Any], str]] = []
    d0_margins: list[tuple[fmpq, dict[str, Any]]] = []
    global_margins: list[tuple[fmpq, dict[str, Any]]] = []
    for row in state["terminal_cells"]:
        if not row["pass"]:
            continue
        for producer in ("primary", "independent"):
            root_margins.append((parse_q(row["root"][producer]["strict_inclusion_margin_exact"]), row, producer))
        d0_margins.append((parse_q(row["d0_result"]["limiting_residual_vector_lower_bound_exact"]), row))
        global_margins.append((parse_q(row["global_result"]["limiting_h_exclusion_margin_exact"]), row))
    limiting_root = min(root_margins, key=lambda item: item[0]) if root_margins else None
    limiting_d0 = min(d0_margins, key=lambda item: item[0]) if d0_margins else None
    limiting_global = min(global_margins, key=lambda item: item[0]) if global_margins else None
    result = {
        "schema": "lin-static-parameter-neighborhood-result-v1",
        "status": "COMPLETE" if passed else "INCOMPLETE",
        "classification": SUCCESS if passed else INCOMPLETE,
        "authority": "DUAL_PRODUCER_PARAMETRIC_INTERVAL_NEWTON_PLUS_GAP_FREE_LAUNCH_AND_FIXED_D0_COVERS",
        "completed_utc": utc_now(),
        "guard": guard,
        "resumed_from_checkpoint": resumed is not None,
        "frozen_design": CONFIG,
        "total_parameter_volume_exact": str(total_volume),
        "admitted_parameter_volume_exact": str(admitted),
        "admitted_fraction": float(admitted / total_volume),
        "terminal_parameter_cell_count": len(state["terminal_cells"]),
        "attempted_parameter_cell_count": len(state["attempted_cells"]),
        "unresolved_parameter_cells": unresolved,
        "limiting_root": {
            "margin_exact": str(limiting_root[0]),
            "margin_decimal": float(limiting_root[0]),
            "producer": limiting_root[2],
            "parameter_cell": limiting_root[1]["parameter_cell"],
            "parameter_faces": limiting_root[1]["parameter_faces"],
        } if limiting_root else None,
        "limiting_global_exclusion": {
            "margin_exact": str(limiting_global[0]),
            "margin_decimal": float(limiting_global[0]),
            "parameter_cell": limiting_global[1]["parameter_cell"],
            "parameter_faces": limiting_global[1]["parameter_faces"],
            "launch_box": limiting_global[1]["global_result"]["limiting_h_launch_box"],
        } if limiting_global else None,
        "limiting_d0_exclusion": {
            "margin_exact": str(limiting_d0[0]),
            "margin_decimal": float(limiting_d0[0]),
            "parameter_cell": limiting_d0[1]["parameter_cell"],
            "parameter_faces": limiting_d0[1]["parameter_faces"],
            "launch_box": limiting_d0[1]["d0_result"]["limiting_launch_box"],
        } if limiting_d0 else None,
        "terminal_parameter_cells": state["terminal_cells"],
        "attempted_parameter_cells": state["attempted_cells"],
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": CONFIG["arb_precision_bits"],
            "workers": workers,
        },
        "claim_boundary": [
            "This is a theorem only for the declared reduced static first-event boundary-value problem and frozen parameter box.",
            "It establishes persistence, uniqueness, isolation in the shooting coordinate, and fixed-D0 exclusion; it does not establish dynamical or spectral stability.",
            "No collapse, MOTS, event-horizon, radion-transition, cosmology, or baby-universe inference follows.",
        ],
    }
    atomic_write_json(output / "RESULT.json", result)
    terminal = {
        "schema": "lin-static-parameter-neighborhood-terminal-v1",
        "status": result["status"],
        "classification": result["classification"],
        "completed_utc": result["completed_utc"],
        "result_sha256": sha256_file(output / "RESULT.json"),
        "guard": guard,
        "predecessors_mutated": False,
    }
    atomic_write_json(output / "TERMINAL_CHECKPOINT.json", terminal)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preflight", "production"))
    parser.add_argument("--workers", type=int, default=CONFIG["default_workers"])
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    guard, resolved = verify_bindings(args.bindings.resolve())
    if args.workers < 1 or args.workers > 10:
        raise ValueError("workers must be between 1 and 10")
    try:
        result = (
            run_preflight(args.output.resolve(), guard, resolved)
            if args.mode == "preflight"
            else run_production(args.output.resolve(), guard, resolved, args.workers)
        )
        print(json.dumps({"mode": args.mode, "status": result["status"], "classification": result.get("classification")}, sort_keys=True))
    except Exception as exc:
        failure = {
            "schema": "lin-static-parameter-neighborhood-failure-v1",
            "status": "INCOMPLETE",
            "mode": args.mode,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "guard": guard,
            "checkpoint_present": (args.output / "CHECKPOINT.json").exists(),
            "completed_utc": utc_now(),
        }
        atomic_write_json(args.output / "FAILURE.json", failure)
        raise


if __name__ == "__main__":
    main()
