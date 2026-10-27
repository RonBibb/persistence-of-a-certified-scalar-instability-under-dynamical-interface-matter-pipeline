"""Corrected validated D2A cover with exact-resumption checkpoints.

This successor imports the frozen D2A/validated-flow numerical operators after
digest verification.  Its sole scientific correction is to use either upper
wall residual as a direct exclusion certificate on every integrated box; the
analytic no-turn certificate remains an additional route below its threshold.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

from flint import arb, ctx, fmpq


CONFIG: dict[str, Any] = {
    "schema": "d2a-fixed-separation-cover-r1-config-v1",
    "D0_decimal_promoted_as_binary64_dyadic": "0.9996389747145851",
    "a_min": "0",
    "a_max_parent_constant": "V0_Q",
    "no_turn_threshold": "989750001/10000000000",
    "steps": 1024,
    "target_width": "1/65536",
    "maximum_depth": 24,
    "arb_precision_bits": 512,
    "checkpoint_every_integrated_boxes": 8,
    "checkpoint_max_seconds": 180,
    "classification_order": [
        "negative_curvature",
        "target_width_split",
        "either_direct_wall_residual",
        "analytic_no_turn",
        "maximum_depth_unresolved",
        "refine",
    ],
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def parse_q(text: str) -> fmpq:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return fmpq(int(numerator), int(denominator))
    return fmpq(int(text))


def exact_bounds(flow: Any, value: arb) -> tuple[fmpq, fmpq]:
    return flow.bounds(value)


def display_bounds(bounds: tuple[fmpq, fmpq]) -> list[float]:
    return [float(bounds[0]), float(bounds[1])]


def exact_bound_strings(bounds: tuple[fmpq, fmpq]) -> list[str]:
    return [str(bounds[0]), str(bounds[1])]


def verify_and_import(bindings_path: Path) -> tuple[Any, dict[str, str], dict[str, Any]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    expected_config = bindings["config_sha256"]
    actual_config = sha256_bytes(canonical_bytes(CONFIG))
    if actual_config != expected_config:
        raise RuntimeError(f"config digest mismatch: {actual_config} != {expected_config}")

    source_actual = sha256_file(Path(__file__).resolve())
    if source_actual != bindings["source_sha256"]:
        raise RuntimeError("producer source digest mismatch")

    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        if sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"import digest mismatch: {name}")
        resolved[name] = path

    sys.path.insert(0, str(resolved["validated_flow_source"].parent))
    sys.path.insert(0, str(resolved["frozen_d2a_source"].parent))
    parent = importlib.import_module("d2a_validated_cover")

    guard = {
        "source_sha256": source_actual,
        "config_sha256": actual_config,
        "bindings_sha256": sha256_file(bindings_path),
        "frozen_d2a_source_sha256": bindings["imports"]["frozen_d2a_source"]["sha256"],
        "validated_flow_source_sha256": bindings["imports"]["validated_flow_source"]["sha256"],
        "validated_flow_terminal_sha256": bindings["imports"]["validated_flow_terminal"]["sha256"],
    }
    return parent, guard, bindings


def integrate_box(parent: Any, lo: fmpq, hi: fmpq) -> dict[str, Any]:
    flow = parent.flow
    hstep = parent.D0 / parent.STEPS
    y = flow.launch(flow.ball(lo, hi))
    phi_path_lo, phi_path_hi = exact_bounds(flow, y[2])
    max_picard = 0
    for _ in range(parent.STEPS):
        enclosure, iterations = flow.picard_box(y, hstep)
        max_picard = max(max_picard, iterations)
        local_lo, local_hi = exact_bounds(flow, enclosure[2])
        phi_path_lo = min(phi_path_lo, local_lo)
        phi_path_hi = max(phi_path_hi, local_hi)
        f0 = flow.rhs(y)
        f2 = flow.second_derivative(enclosure, flow.rhs(enclosure))
        y = [
            value + arb(hstep) * first + arb(hstep * hstep / 2) * second
            for value, first, second in zip(y, f0, f2, strict=True)
        ]

    G, scalar = flow.residuals(y)
    G_bounds = exact_bounds(flow, G)
    scalar_bounds = exact_bounds(flow, scalar)
    phi_endpoint = exact_bounds(flow, y[2])
    G_excludes = G_bounds[0] > 0 or G_bounds[1] < 0
    scalar_excludes = scalar_bounds[0] > 0 or scalar_bounds[1] < 0
    return {
        "G_exact_bounds": exact_bound_strings(G_bounds),
        "G_decimal_bounds": display_bounds(G_bounds),
        "scalar_residual_exact_bounds": exact_bound_strings(scalar_bounds),
        "scalar_residual_decimal_bounds": display_bounds(scalar_bounds),
        "phi_endpoint_exact_bounds": exact_bound_strings(phi_endpoint),
        "phi_endpoint_decimal_bounds": display_bounds(phi_endpoint),
        "phi_path_exact_bounds": exact_bound_strings((phi_path_lo, phi_path_hi)),
        "phi_path_decimal_bounds": display_bounds((phi_path_lo, phi_path_hi)),
        "G_excludes_zero": G_excludes,
        "scalar_residual_excludes_zero": scalar_excludes,
        "path_scalar_admissible": phi_path_lo > 0 and phi_path_hi <= flow.V0_Q,
        "phi_endpoint_below_v1": phi_endpoint[1] < flow.V1_Q,
        "max_picard_iterations": max_picard,
    }


def classify_evidence(
    record: dict[str, Any],
    *,
    below_threshold: bool,
    no_turn_lower: fmpq | None,
    depth: int,
    maximum_depth: int,
) -> str:
    G_excludes = bool(record["G_excludes_zero"])
    scalar_excludes = bool(record["scalar_residual_excludes_zero"])
    if G_excludes and scalar_excludes:
        return "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO"
    if G_excludes:
        return "UPPER_ISRAEL_EXCLUDED"
    if scalar_excludes:
        return "UPPER_SCALAR_EXCLUDED"
    if (
        below_threshold
        and no_turn_lower is not None
        and record["path_scalar_admissible"]
        and record["phi_endpoint_below_v1"]
        and no_turn_lower >= 0
    ):
        return "NO_TURN_EXCLUDED"
    if depth >= maximum_depth:
        return "UNRESOLVED"
    return "SPLIT"


def classify_box(parent: Any, lo: fmpq, hi: fmpq, depth: int) -> tuple[str, dict[str, Any] | None]:
    flow = parent.flow
    initial = flow.launch(flow.ball(lo, hi))
    curvature_bounds = exact_bounds(flow, initial[5])
    if curvature_bounds[1] < 0:
        return "NEGATIVE_CURVATURE_EXCLUDED", {
            "curvature_exact_bounds": exact_bound_strings(curvature_bounds),
            "curvature_decimal_bounds": display_bounds(curvature_bounds),
        }
    if hi - lo > parent.TARGET_WIDTH:
        return "SPLIT", None

    record = integrate_box(parent, lo, hi)
    record["curvature_exact_bounds"] = exact_bound_strings(curvature_bounds)
    record["curvature_decimal_bounds"] = display_bounds(curvature_bounds)
    below = hi <= parent.THRESHOLD
    no_turn_lower: fmpq | None = None
    if below:
        polynomial = parent.no_turn_polynomial(flow.ball(lo, hi))
        no_turn_lower, no_turn_upper = exact_bounds(flow, polynomial)
        record["no_turn_polynomial_exact_bounds"] = exact_bound_strings((no_turn_lower, no_turn_upper))
        record["no_turn_polynomial_decimal_bounds"] = display_bounds((no_turn_lower, no_turn_upper))

    classification = classify_evidence(
        record,
        below_threshold=below,
        no_turn_lower=no_turn_lower,
        depth=depth,
        maximum_depth=parent.MAX_DEPTH,
    )
    return classification, record


def nominal_cover_count(parent: Any) -> dict[str, int]:
    flow = parent.flow
    stack = [(parent.A_MIN, parent.THRESHOLD), (parent.THRESHOLD, parent.A_MAX)]
    negative = 0
    integrated = 0
    while stack:
        lo, hi = stack.pop()
        curvature = exact_bounds(flow, flow.launch(flow.ball(lo, hi))[5])
        if curvature[1] < 0:
            negative += 1
        elif hi - lo > parent.TARGET_WIDTH:
            middle = (lo + hi) / 2
            stack.append((middle, hi))
            stack.append((lo, middle))
        else:
            integrated += 1
    return {"negative_curvature_terminal_boxes": negative, "boxes_requiring_integration_before_any_deeper_refinement": integrated}


def synthetic_record(**changes: Any) -> dict[str, Any]:
    value = {
        "G_excludes_zero": False,
        "scalar_residual_excludes_zero": False,
        "path_scalar_admissible": False,
        "phi_endpoint_below_v1": False,
    }
    value.update(changes)
    return value


def run_preflight(parent: Any, guard: dict[str, str], output: Path) -> dict[str, Any]:
    flow = parent.flow
    ctx.prec = parent.PRECISION_BITS
    route_cases = {
        "both": (synthetic_record(G_excludes_zero=True, scalar_residual_excludes_zero=True), False, None, 0, "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO"),
        "israel": (synthetic_record(G_excludes_zero=True), True, fmpq(1), 0, "UPPER_ISRAEL_EXCLUDED"),
        "scalar_fallback": (synthetic_record(scalar_residual_excludes_zero=True), True, fmpq(-1), 0, "UPPER_SCALAR_EXCLUDED"),
        "no_turn": (synthetic_record(path_scalar_admissible=True, phi_endpoint_below_v1=True), True, fmpq(1), 0, "NO_TURN_EXCLUDED"),
        "split": (synthetic_record(), False, None, 0, "SPLIT"),
        "unresolved": (synthetic_record(), False, None, parent.MAX_DEPTH, "UNRESOLVED"),
    }
    route_results: dict[str, str] = {}
    for name, (record, below, lower, depth, expected) in route_cases.items():
        actual = classify_evidence(
            record,
            below_threshold=below,
            no_turn_lower=lower,
            depth=depth,
            maximum_depth=parent.MAX_DEPTH,
        )
        if actual != expected:
            raise RuntimeError(f"classification route {name}: {actual} != {expected}")
        route_results[name] = actual

    exact_ball = flow.ball(fmpq(1, 3), fmpq(1, 2))
    containment = {
        "contains_2_over_5": bool(exact_ball.contains(arb(fmpq(2, 5)))),
        "excludes_3_over_5": not bool(exact_ball.contains(arb(fmpq(3, 5)))),
        "strict_nested_ball": bool(
            flow.strictly_contains(flow.ball(fmpq(0), fmpq(1)), flow.ball(fmpq(1, 4), fmpq(3, 4)))
        ),
    }
    if not all(containment.values()):
        raise RuntimeError("exact containment preflight failed")

    negative_curvature_bounds = exact_bounds(flow, flow.launch(flow.ball(fmpq(0), fmpq(1, 100)))[5])
    if not negative_curvature_bounds[1] < 0:
        raise RuntimeError("negative-curvature route preflight failed")
    if not parent.THRESHOLD - parent.A_MIN > parent.TARGET_WIDTH:
        raise RuntimeError("target-width split route preflight failed")

    # A real below-threshold box verifies that the repaired direct fallback is
    # connected to the validated numerical operator, not only to synthetic data.
    representative_lo = fmpq(93, 1000)
    representative_hi = representative_lo + parent.TARGET_WIDTH / 2
    representative = integrate_box(parent, representative_lo, representative_hi)
    representative_class = classify_evidence(
        representative,
        below_threshold=True,
        no_turn_lower=exact_bounds(flow, parent.no_turn_polynomial(flow.ball(representative_lo, representative_hi)))[0],
        depth=parent.MAX_DEPTH,
        maximum_depth=parent.MAX_DEPTH,
    )
    if representative_class not in {
        "BOTH_WALL_RESIDUALS_EXCLUDE_ZERO",
        "UPPER_ISRAEL_EXCLUDED",
        "UPPER_SCALAR_EXCLUDED",
        "NO_TURN_EXCLUDED",
    }:
        raise RuntimeError("real representative box was not certified")

    roundtrip_stack = [[str(fmpq(1, 7)), str(fmpq(2, 7)), 9]]
    if [[str(parse_q(a)), str(parse_q(b)), depth] for a, b, depth in roundtrip_stack] != roundtrip_stack:
        raise RuntimeError("checkpoint rational roundtrip failed")

    result = {
        "schema": "d2a-r1-preflight-v1",
        "status": "PASS",
        "guard": guard,
        "classification_routes": route_results,
        "exact_containment_controls": containment,
        "negative_curvature_route_exact_bounds": exact_bound_strings(negative_curvature_bounds),
        "target_width_split_route": True,
        "nominal_cover_estimate": nominal_cover_count(parent),
        "real_below_threshold_representative": {
            "a_exact_bounds": [str(representative_lo), str(representative_hi)],
            "classification": representative_class,
            "G_exact_bounds": representative["G_exact_bounds"],
            "scalar_residual_exact_bounds": representative["scalar_residual_exact_bounds"],
            "path_scalar_admissible": representative["path_scalar_admissible"],
        },
        "checkpoint_exact_rational_roundtrip": True,
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
        },
    }
    atomic_write_json(output / "PREFLIGHT.json", result)
    return result


def state_payload(guard: dict[str, str], stack: list[tuple[fmpq, fmpq, int]], terminal: list[dict[str, Any]], unresolved: list[dict[str, Any]], integrated: int, processed: int) -> dict[str, Any]:
    return {
        "schema": "d2a-r1-exact-resumption-checkpoint-v1",
        "guard": guard,
        "stack": [[str(lo), str(hi), depth] for lo, hi, depth in stack],
        "terminal": terminal,
        "unresolved": unresolved,
        "integrated_box_count": integrated,
        "processed_stack_item_count": processed,
    }


def publish_checkpoint(output: Path, payload: dict[str, Any]) -> str:
    digest = sha256_bytes(canonical_bytes(payload))
    immutable = output / "checkpoints" / f"checkpoint-{digest}.json"
    if immutable.exists():
        existing = json.loads(immutable.read_text(encoding="utf-8"))
        if canonical_bytes(existing) != canonical_bytes(payload):
            raise RuntimeError("immutable checkpoint digest collision")
    else:
        atomic_write_json(immutable, payload)
        immutable.chmod(0o444)
    latest = {"checkpoint_sha256": digest, "checkpoint_relative_path": str(immutable.relative_to(output)), "payload": payload}
    atomic_write_json(output / "CHECKPOINT.json", latest)
    return digest


def load_checkpoint(output: Path, guard: dict[str, str]) -> tuple[list[tuple[fmpq, fmpq, int]], list[dict[str, Any]], list[dict[str, Any]], int, int] | None:
    latest_path = output / "CHECKPOINT.json"
    if not latest_path.exists():
        return None
    latest = json.loads(latest_path.read_text(encoding="utf-8"))
    payload = latest["payload"]
    if sha256_bytes(canonical_bytes(payload)) != latest["checkpoint_sha256"]:
        raise RuntimeError("latest checkpoint payload digest mismatch")
    immutable = output / latest["checkpoint_relative_path"]
    if sha256_file(immutable) != sha256_bytes(json.dumps(payload, indent=2, sort_keys=True).encode() + b"\n"):
        raise RuntimeError("immutable checkpoint file digest mismatch")
    if payload["guard"] != guard:
        raise RuntimeError("checkpoint compatibility guard mismatch")
    stack = [(parse_q(lo), parse_q(hi), int(depth)) for lo, hi, depth in payload["stack"]]
    return stack, list(payload["terminal"]), list(payload["unresolved"]), int(payload["integrated_box_count"]), int(payload["processed_stack_item_count"])


def coverage_audit(parent: Any, terminal: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(terminal, key=lambda row: parse_q(row["a_exact_bounds"][0]))
    contiguous = bool(ordered) and parse_q(ordered[0]["a_exact_bounds"][0]) == parent.A_MIN
    previous = parent.A_MIN
    for row in ordered:
        lo, hi = map(parse_q, row["a_exact_bounds"])
        contiguous = contiguous and lo == previous and hi >= lo
        previous = hi
    contiguous = contiguous and previous == parent.A_MAX
    return {
        "exact_contiguous_cover": contiguous,
        "first_exact_endpoint": ordered[0]["a_exact_bounds"][0] if ordered else None,
        "last_exact_endpoint": ordered[-1]["a_exact_bounds"][1] if ordered else None,
    }


def run_production(parent: Any, guard: dict[str, str], output: Path) -> dict[str, Any]:
    preflight_path = output / "PREFLIGHT.json"
    if not preflight_path.exists():
        raise RuntimeError("production requires a completed preflight")
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    if preflight.get("status") != "PASS" or preflight.get("guard") != guard:
        raise RuntimeError("preflight guard mismatch")

    ctx.prec = parent.PRECISION_BITS
    resumed = load_checkpoint(output, guard)
    if resumed is None:
        stack = [(parent.A_MIN, parent.THRESHOLD, 0), (parent.THRESHOLD, parent.A_MAX, 0)]
        terminal: list[dict[str, Any]] = []
        unresolved: list[dict[str, Any]] = []
        integrated = 0
        processed = 0
        publish_checkpoint(output, state_payload(guard, stack, terminal, unresolved, integrated, processed))
    else:
        stack, terminal, unresolved, integrated, processed = resumed

    started = time.monotonic()
    last_checkpoint_time = started
    last_checkpoint_integrated = integrated
    while stack:
        lo, hi, depth = stack.pop()
        classification, record = classify_box(parent, lo, hi, depth)
        processed += 1
        if record is not None and classification != "NEGATIVE_CURVATURE_EXCLUDED":
            integrated += 1
        if classification == "SPLIT":
            middle = (lo + hi) / 2
            stack.append((middle, hi, depth + 1))
            stack.append((lo, middle, depth + 1))
        else:
            row = {
                "a_exact_bounds": [str(lo), str(hi)],
                "a_decimal_bounds": [float(lo), float(hi)],
                "depth": depth,
                "classification": classification,
                "record": record,
            }
            terminal.append(row)
            if classification == "UNRESOLVED":
                unresolved.append(row)

        now = time.monotonic()
        if (
            integrated - last_checkpoint_integrated >= CONFIG["checkpoint_every_integrated_boxes"]
            or now - last_checkpoint_time >= CONFIG["checkpoint_max_seconds"]
            or not stack
        ):
            publish_checkpoint(output, state_payload(guard, stack, terminal, unresolved, integrated, processed))
            last_checkpoint_integrated = integrated
            last_checkpoint_time = now

    audit = coverage_audit(parent, terminal)
    counts: dict[str, int] = {}
    for row in terminal:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    passed = not unresolved and audit["exact_contiguous_cover"]
    ordered = sorted(terminal, key=lambda row: parse_q(row["a_exact_bounds"][0]))
    result = {
        "schema": "d2a-validated-fixed-separation-cover-r1-result-v1",
        "status": "COMPLETE" if passed else "INCOMPLETE",
        "classification": "FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE" if passed else "FIXED_SEPARATION_COVER_UNRESOLVED",
        "authority": "VALIDATED_COVER_OF_0_LE_A_LE_V0_FOR_THE_DECLARED_REDUCED_STATIC_IVP",
        "guard": guard,
        "resumed_from_checkpoint": resumed is not None,
        "runtime": {
            "current_invocation_wall_seconds": time.monotonic() - started,
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": parent.PRECISION_BITS,
        },
        "frozen_design": CONFIG,
        "terminal_box_count": len(ordered),
        "integrated_box_count_including_pre_split_attempts": integrated,
        "processed_stack_item_count": processed,
        "classification_counts": counts,
        "coverage_audit": audit,
        "unresolved": unresolved,
        "terminal_boxes": ordered,
        "claim_boundary": [
            "The exclusion is for the declared reduced static IVP, positive curvature, and 0<=a<=v0.",
            "It does not exclude a dynamical radion bridge, altered wall/action parameters, or a branch outside the declared admissible launch range.",
            "It is not an event-horizon or collapse-development result.",
        ],
    }
    atomic_write_json(output / "RESULT.json", result)
    result_sha = sha256_file(output / "RESULT.json")
    terminal_record = {
        "schema": "d2a-r1-production-terminal-v1",
        "status": result["status"],
        "classification": result["classification"],
        "result_sha256": result_sha,
        "guard": guard,
        "predecessors_mutated": False,
    }
    atomic_write_json(output / "TERMINAL_CHECKPOINT.json", terminal_record)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--mode", required=True, choices=("preflight", "production"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    parent, guard, _bindings = verify_and_import(args.bindings.resolve())
    try:
        if args.mode == "preflight":
            result = run_preflight(parent, guard, args.output.resolve())
        else:
            result = run_production(parent, guard, args.output.resolve())
        print(json.dumps({"status": result["status"], "mode": args.mode}, sort_keys=True))
    except Exception as exc:
        failure = {
            "schema": "d2a-r1-runtime-failure-v1",
            "status": "INCOMPLETE",
            "mode": args.mode,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "guard": guard,
            "checkpoint_present": (args.output / "CHECKPOINT.json").exists(),
        }
        atomic_write_json(args.output / "FAILURE.json", failure)
        raise


if __name__ == "__main__":
    main()
