#!/usr/bin/env python3
"""Validated dimension test for fixed-D continuation of the D1 root."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

from flint import arb, ctx, fmpq


CONFIG: dict[str, Any] = {
    "schema": "lin-d1-fixed-d-continuation-dimension-config-v1",
    "root_box_decimal_labels": ["0.09901086489880687", "0.09901086689880687"],
    "D_domain": ["0", "2"],
    "D0_decimal_promoted_as_binary64_dyadic": "0.9996389747145851",
    "arb_precision_bits": 768,
    "primary_steps": 32768,
    "independent_steps": 16384,
    "primary_method": "second-order Taylor endpoint plus Picard cell enclosure",
    "independent_method": "fifth-order Taylor series plus Picard remainder enclosure",
    "stopping_rule": (
        "stop with isolated-root classification when both independent Jacobian determinant "
        "enclosures exclude zero; otherwise report continuation dimension unresolved"
    ),
}

ISOLATED_CLASSIFICATION = "CERTIFIED_ISOLATED_D1_ROOT_NO_NONTRIVIAL_FIXED_D_CONTINUATION"
UNRESOLVED_CLASSIFICATION = "FIXED_D_CONTINUATION_DIMENSION_UNRESOLVED"
GLOBAL_UNIQUENESS_CLASSIFICATION = (
    "GLOBAL_FIRST_EVENT_SIMULTANEOUS_WALL_ROOT_UNIQUE_ON_DECLARED_"
    "POSITIVE_CURVATURE_LAUNCH_INTERVAL"
)
D2A_CLASSIFICATION = "FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE"


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


def dyadic(text: str) -> fmpq:
    numerator, denominator = float(text).as_integer_ratio()
    return fmpq(numerator, denominator)


def parse_q(text: str) -> fmpq:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return fmpq(int(numerator), int(denominator))
    return fmpq(int(text))


def interval_record(module: Any, value: arb) -> dict[str, Any]:
    lo, hi = module.bounds(value)
    return {
        "exact_bounds": [str(lo), str(hi)],
        "decimal_bounds": [float(lo), float(hi)],
        "contains_zero": lo <= 0 <= hi,
        "strictly_positive": lo > 0,
        "strictly_negative": hi < 0,
    }


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_bindings(bindings_path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(bindings_path.read_text(encoding="utf-8"))
    source_sha = sha256_file(Path(__file__).resolve())
    config_sha = sha256_bytes(canonical_bytes(CONFIG))
    if source_sha != bindings["producer_source_sha256"]:
        raise RuntimeError("producer source digest mismatch")
    if config_sha != bindings["config_sha256"]:
        raise RuntimeError("configuration digest mismatch")
    if sha256_file(branch / "CONTRACT.md") != bindings["contract_sha256"]:
        raise RuntimeError("contract digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        path = (branch / item["relative_path"]).resolve()
        if not path.is_file() or sha256_file(path) != item["sha256"]:
            raise RuntimeError(f"bound input mismatch: {name}")
        resolved[name] = path
    guard = {
        "producer_source_sha256": source_sha,
        "config_sha256": config_sha,
        "contract_sha256": bindings["contract_sha256"],
        "bindings_sha256": sha256_file(bindings_path),
    }
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return guard, resolved


def sign(module: Any, value: arb) -> str:
    lo, hi = module.bounds(value)
    return "positive" if lo > 0 else "negative" if hi < 0 else "zero-containing"


def root_event(module: Any, lo: fmpq, hi: fmpq, steps: int, producer: str) -> dict[str, Any]:
    started = time.monotonic()
    step = module.S_END / steps
    state = module.launch(module.ball(lo, hi))
    curvature = state[5]
    records: list[dict[str, arb]] = []
    zero_cells: list[int] = []
    negative_after: int | None = None
    max_picard = 0
    obstruction: str | None = None

    for cell in range(steps):
        enclosure, iterations = module.picard_box(state, step)
        max_picard = max(max_picard, iterations)
        quantities = (
            module.event_quantities(enclosure)
            if producer == "primary"
            else module.upper_quantities(enclosure)
        )
        G_sign = sign(module, quantities["G"])
        if not zero_cells:
            if G_sign == "positive":
                pass
            elif G_sign == "zero-containing":
                zero_cells.append(cell)
                records.append(quantities)
            else:
                obstruction = "NEGATIVE_BEFORE_EVENT_CLUSTER"
                break
        else:
            if G_sign == "zero-containing":
                zero_cells.append(cell)
                records.append(quantities)
            elif G_sign == "negative":
                negative_after = cell
                break
            else:
                obstruction = "POSITIVE_AFTER_EVENT_CLUSTER"
                break
        state = module.advance(state, enclosure, step)

    if not records:
        raise RuntimeError(f"{producer}: no first-event cluster: {obstruction}")
    if negative_after is None:
        obstruction = obstruction or "EVENT_CLUSTER_NOT_CLOSED"

    keys = (
        {"G": "G", "G_D": "Gs", "G_a": "Ga", "h": "h", "h_a": "ha", "h_D": "hs", "q_a": "hprime"}
        if producer == "primary"
        else {"G": "G", "G_D": "G_s", "G_a": "G_a", "h": "h", "h_a": "h_a", "h_D": "h_s", "q_a": "q_a"}
    )
    union = {
        public: module.union_all([record[source] for record in records])
        for public, source in keys.items()
    }
    determinant_chain = -union["G_D"] * union["q_a"]
    determinant_direct = union["G_a"] * union["h_D"] - union["G_D"] * union["h_a"]
    chain_lo, chain_hi = module.bounds(determinant_chain)
    direct_lo, direct_hi = module.bounds(determinant_direct)
    overlap = max(chain_lo, direct_lo) <= min(chain_hi, direct_hi)
    G_D_lo, G_D_hi = module.bounds(union["G_D"])
    q_lo, q_hi = module.bounds(union["q_a"])
    curvature_lo, curvature_hi = module.bounds(curvature)
    validated = bool(
        obstruction is None
        and zero_cells == list(range(zero_cells[0], zero_cells[-1] + 1))
        and negative_after == zero_cells[-1] + 1
        and G_D_hi < 0
        and q_lo > 0
        and curvature_lo > 0
        and chain_lo > 0
        and direct_lo > 0
        and overlap
    )
    return {
        "producer": producer,
        "steps": steps,
        "validated": validated,
        "obstruction": obstruction,
        "event_cells": [zero_cells[0], zero_cells[-1]],
        "negative_after_cell": negative_after,
        "event_bracket_exact": [str(zero_cells[0] * step), str((zero_cells[-1] + 1) * step)],
        "event_bracket_decimal": [float(zero_cells[0] * step), float((zero_cells[-1] + 1) * step)],
        "curvature": interval_record(module, curvature),
        "G": interval_record(module, union["G"]),
        "G_D": interval_record(module, union["G_D"]),
        "G_a": interval_record(module, union["G_a"]),
        "h": interval_record(module, union["h"]),
        "h_a": interval_record(module, union["h_a"]),
        "h_D": interval_record(module, union["h_D"]),
        "q_a_along_first_event": interval_record(module, union["q_a"]),
        "jacobian_determinant_from_chain_rule": interval_record(module, determinant_chain),
        "jacobian_determinant_direct": interval_record(module, determinant_direct),
        "determinant_forms_overlap": overlap,
        "maximum_picard_iterations": max_picard,
        "wall_seconds": time.monotonic() - started,
    }


def authority_checks(resolved: dict[str, Path]) -> dict[str, Any]:
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
    checks = {
        "primary_D1_root": primary.get("classification") == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS"
        and primary_terminal.get("classification") == "RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS",
        "independent_D1_root": independent.get("classification") == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS"
        and independent_terminal.get("classification") == "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS",
        "global_first_event_uniqueness": global_result.get("classification") == GLOBAL_UNIQUENESS_CLASSIFICATION
        and global_terminal.get("classification") == GLOBAL_UNIQUENESS_CLASSIFICATION
        and global_audit.get("status") == "VERIFIED"
        and not global_result.get("unresolved"),
        "D2A_exclusion": d2a.get("classification") == D2A_CLASSIFICATION
        and d2a_terminal.get("classification") == D2A_CLASSIFICATION
        and d2a_audit.get("status") == "VERIFIED",
    }
    return {"pass": all(checks.values()), "checks": checks}


def run_preflight(output: Path, guard: dict[str, str], resolved: dict[str, Path]) -> dict[str, Any]:
    authority = authority_checks(resolved)
    if not authority["pass"]:
        raise RuntimeError("sealed authority check failed")
    # Exact algebra control for det J = -G_D q_a.
    G_D, G_a, h_D, h_a = map(arb, (-2, 3, 5, 7))
    D_a = -G_a / G_D
    q_a = h_a + h_D * D_a
    direct = G_a * h_D - G_D * h_a
    chain = -G_D * q_a
    algebra = {
        "direct_equals_chain": direct == chain,
        "reference_value_29": direct == 29,
        "root_box_ordered": dyadic(CONFIG["root_box_decimal_labels"][0])
        < dyadic(CONFIG["root_box_decimal_labels"][1]),
        "D0_inside_declared_D_domain": fmpq(0) < dyadic(CONFIG["D0_decimal_promoted_as_binary64_dyadic"]) < fmpq(2),
    }
    if not all(algebra.values()):
        raise RuntimeError("continuation dimension algebra preflight failed")
    result = {
        "schema": "lin-d1-fixed-d-continuation-dimension-preflight-v1",
        "status": "PASS",
        "completed_utc": utc_now(),
        "guard": guard,
        "authority": authority,
        "algebra_controls": algebra,
        "registered_stopping_rule": CONFIG["stopping_rule"],
    }
    atomic_write_json(output / "PREFLIGHT.json", result)
    return result


def run_production(output: Path, guard: dict[str, str], resolved: dict[str, Path]) -> dict[str, Any]:
    preflight = json.loads((output / "PREFLIGHT.json").read_text(encoding="utf-8"))
    if preflight.get("status") != "PASS" or preflight.get("guard") != guard:
        raise RuntimeError("preflight guard mismatch")
    ctx.prec = CONFIG["arb_precision_bits"]
    primary = load_module("fixed_d_primary", resolved["primary_source"])
    independent = load_module("fixed_d_independent", resolved["independent_source"])
    root_lo, root_hi = map(dyadic, CONFIG["root_box_decimal_labels"])
    started = time.monotonic()
    primary_record = root_event(primary, root_lo, root_hi, CONFIG["primary_steps"], "primary")
    independent_record = root_event(
        independent, root_lo, root_hi, CONFIG["independent_steps"], "independent"
    )

    pD = tuple(parse_q(value) for value in primary_record["event_bracket_exact"])
    iD = tuple(parse_q(value) for value in independent_record["event_bracket_exact"])
    D_intersection = (max(pD[0], iD[0]), min(pD[1], iD[1]))
    brackets_overlap = D_intersection[0] <= D_intersection[1]
    D0 = dyadic(CONFIG["D0_decimal_promoted_as_binary64_dyadic"])
    determinant_same_sign = (
        primary_record["jacobian_determinant_from_chain_rule"]["strictly_positive"]
        and independent_record["jacobian_determinant_from_chain_rule"]["strictly_positive"]
    ) or (
        primary_record["jacobian_determinant_from_chain_rule"]["strictly_negative"]
        and independent_record["jacobian_determinant_from_chain_rule"]["strictly_negative"]
    )
    authorities = authority_checks(resolved)
    isolated = bool(
        authorities["pass"]
        and primary_record["validated"]
        and independent_record["validated"]
        and determinant_same_sign
        and brackets_overlap
    )
    classification = ISOLATED_CLASSIFICATION if isolated else UNRESOLVED_CLASSIFICATION
    status = "COMPLETE" if isolated else "INCOMPLETE"
    result = {
        "schema": "lin-d1-fixed-d-continuation-dimension-result-v1",
        "status": status,
        "classification": classification,
        "authority": "DUAL_PRODUCER_INTERVAL_JACOBIAN_DIMENSION_TEST_AT_GLOBALLY_UNIQUE_D1_ROOT",
        "completed_utc": utc_now(),
        "guard": guard,
        "frozen_design": CONFIG,
        "authority_checks": authorities,
        "primary": primary_record,
        "independent": independent_record,
        "cross_producer": {
            "event_brackets_overlap": brackets_overlap,
            "event_bracket_intersection_exact": [str(D_intersection[0]), str(D_intersection[1])]
            if brackets_overlap
            else None,
            "event_bracket_intersection_decimal": [float(D_intersection[0]), float(D_intersection[1])]
            if brackets_overlap
            else None,
            "jacobian_determinants_have_same_nonzero_sign": determinant_same_sign,
        },
        "maximal_connected_D_solution_set": {
            "type": "SINGLETON" if isolated else "UNRESOLVED",
            "symbolic_set": "{D*}" if isolated else None,
            "cardinality": 1 if isolated else None,
            "D_star_exact_value_resolved": False,
            "D_star_certified_enclosure_exact": [str(D_intersection[0]), str(D_intersection[1])]
            if isolated
            else None,
            "D_star_certified_enclosure_decimal": [float(D_intersection[0]), float(D_intersection[1])]
            if isolated
            else None,
            "positive_width_continuation_interval_certified": False,
            "enclosure_is_not_an_interval_of_solutions": True,
        },
        "toward_D0": {
            "D0_exact": str(D0),
            "D0_decimal": float(D0),
            "D_star_minus_D0_enclosure_exact": [
                str(D_intersection[0] - D0),
                str(D_intersection[1] - D0),
            ]
            if brackets_overlap
            else None,
            "D_star_minus_D0_enclosure_decimal": [
                float(D_intersection[0] - D0),
                float(D_intersection[1] - D0),
            ]
            if brackets_overlap
            else None,
            "D0_separately_excluded_by_D2A": authorities["checks"]["D2A_exclusion"],
            "certified_continuation_distance_toward_D0": 0,
        },
        "interpretation": {
            "zero_set_dimension_at_D1": 0 if isolated else None,
            "reason": (
                "Both independent interval Jacobian determinants exclude zero; the fixed-model simultaneous-wall root is isolated."
                if isolated
                else "At least one registered rank or authority gate did not close."
            ),
            "next_parameter_requirement": (
                "A nontrivial continuation study would require prospectively varying one additional physical model parameter."
                if isolated
                else None
            ),
        },
        "runtime": {
            "wall_seconds": time.monotonic() - started,
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": CONFIG["arb_precision_bits"],
        },
        "claim_boundary": [
            "The result concerns only the declared reduced static first-event boundary problem.",
            "The D-star enclosure contains one unknown solution value; it is not itself a solution interval.",
            "No dynamical selection, stability, collapse, MOTS, event horizon, radion transition, or baby-universe claim follows.",
        ],
    }
    atomic_write_json(output / "RESULT.json", result)
    terminal = {
        "schema": "lin-d1-fixed-d-continuation-dimension-terminal-v1",
        "status": status,
        "classification": classification,
        "completed_utc": result["completed_utc"],
        "result_sha256": sha256_file(output / "RESULT.json"),
        "guard": guard,
        "predecessors_mutated": False,
    }
    atomic_write_json(output / "TERMINAL.json", terminal)
    return result


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
            run_preflight(args.output.resolve(), guard, resolved)
            if args.mode == "preflight"
            else run_production(args.output.resolve(), guard, resolved)
        )
        print(json.dumps({"mode": args.mode, "status": result["status"], "classification": result.get("classification")}, sort_keys=True))
    except Exception as exc:
        failure = {
            "schema": "lin-d1-fixed-d-continuation-dimension-failure-v1",
            "status": "INCOMPLETE",
            "mode": args.mode,
            "failed_utc": utc_now(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "guard": guard,
        }
        atomic_write_json(args.output / "FAILURE.json", failure)
        raise


if __name__ == "__main__":
    main()
