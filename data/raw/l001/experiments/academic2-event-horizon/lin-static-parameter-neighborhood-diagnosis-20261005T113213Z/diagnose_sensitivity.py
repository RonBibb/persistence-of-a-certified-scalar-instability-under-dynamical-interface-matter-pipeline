#!/usr/bin/env python3
"""Audit the incomplete neighborhood run and derive local root sensitivities."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from flint import arb, ctx, fmpq


CONFIG: dict[str, Any] = {
    "schema": "lin-static-parameter-neighborhood-diagnosis-config-v1",
    "root_box_decimal_labels": ["0.09901086489880687", "0.09901086689880687"],
    "central_parameters_decimal_labels": {"v1": "0.09048374180359596", "lambda_b": "-6.052844277744164"},
    "finite_box_exact": {
        "v1": ["3256417487256207/36028797018963968", "101988226458125/1125899906842624"],
        "lambda_b": ["-1703752349608937/281474976710656", "-1703696054613595/281474976710656"],
    },
    "steps": 8192,
    "arb_precision_bits": 768,
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
    temporary = path.with_name(path.name + f".tmp-{os.getpid()}")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def parse_q(text: str) -> fmpq:
    if "/" in text:
        a, b = text.split("/", 1)
        return fmpq(int(a), int(b))
    return fmpq(int(text))


def dyadic(text: str) -> fmpq:
    a, b = float(text).as_integer_ratio()
    return fmpq(a, b)


def qpair(values: list[str]) -> tuple[fmpq, fmpq]:
    return parse_q(values[0]), parse_q(values[1])


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_bindings(path: Path) -> tuple[dict[str, str], dict[str, Path]]:
    branch = Path(__file__).resolve().parent
    bindings = json.loads(path.read_text())
    if sha256_file(Path(__file__).resolve()) != bindings["source_sha256"]:
        raise RuntimeError("source digest mismatch")
    if sha256_file(branch / "CONTRACT.md") != bindings["contract_sha256"]:
        raise RuntimeError("contract digest mismatch")
    if sha256_bytes(canonical_bytes(CONFIG)) != bindings["config_sha256"]:
        raise RuntimeError("config digest mismatch")
    resolved: dict[str, Path] = {}
    for name, item in bindings["imports"].items():
        candidate = (branch / item["relative_path"]).resolve()
        if not candidate.is_file() or sha256_file(candidate) != item["sha256"]:
            raise RuntimeError(f"input digest mismatch: {name}")
        resolved[name] = candidate
    guard = {"source_sha256": bindings["source_sha256"], "contract_sha256": bindings["contract_sha256"], "config_sha256": bindings["config_sha256"], "bindings_sha256": sha256_file(path)}
    for name, item in sorted(bindings["imports"].items()):
        guard[f"input_{name}_sha256"] = item["sha256"]
    return guard, resolved


def interval(module: Any, value: arb) -> dict[str, Any]:
    lo, hi = module.bounds(value)
    return {"exact_bounds": [str(lo), str(hi)], "decimal_bounds": [float(lo), float(hi)], "contains_zero": lo <= 0 <= hi}


def intersect(left: tuple[fmpq, fmpq], right: tuple[fmpq, fmpq]) -> bool:
    return max(left[0], right[0]) <= min(left[1], right[1])


def interval_sign(pair: tuple[fmpq, fmpq]) -> str:
    if pair[0] > 0:
        return "positive"
    if pair[1] < 0:
        return "negative"
    return "zero-containing"


def max_abs(pair: tuple[fmpq, fmpq]) -> fmpq:
    return max(abs(pair[0]), abs(pair[1]))


def event_union(module: Any, producer: str) -> dict[str, Any]:
    lo, hi = (dyadic(x) for x in CONFIG["root_box_decimal_labels"])
    step = module.S_END / CONFIG["steps"]
    state = module.launch(module.ball(lo, hi))
    records: list[dict[str, arb]] = []
    cells: list[int] = []
    signs: list[str] = []
    max_picard = 0
    for index in range(CONFIG["steps"]):
        enclosure, iterations = module.picard_box(state, step)
        max_picard = max(max_picard, iterations)
        q = dict(module.event_quantities(enclosure) if producer == "primary" else module.upper_quantities(enclosure))
        q["_phi"] = enclosure[2]
        Glo, Ghi = module.bounds(q["G"])
        current = "positive" if Glo > 0 else "negative" if Ghi < 0 else "zero-containing"
        signs.append(current)
        if current == "zero-containing":
            cells.append(index)
            records.append(q)
        state = module.advance(state, enclosure, step)
    if not records:
        raise RuntimeError(f"{producer}: no event cells")
    valid = cells == list(range(cells[0], cells[-1] + 1)) and all(s == "positive" for s in signs[: cells[0]]) and all(s == "negative" for s in signs[cells[-1] + 1 :])
    union = {key: module.union_all([row[key] for row in records]) for key in records[0]}
    Gs_key = "Gs" if producer == "primary" else "G_s"
    hs_key = "hs" if producer == "primary" else "h_s"
    qa_key = "hprime" if producer == "primary" else "q_a"
    Da_key = "Dprime" if producer == "primary" else "D_a"
    Gs = union[Gs_key]
    phi = union["_phi"]
    hs = union[hs_key]
    qa = union[qa_key]
    Da = union[Da_key]
    gamma = arb(module.GAMMA_Q)
    v1 = arb(module.V1_Q)
    G_v1 = gamma * (phi - v1) / 6
    G_lambda = -arb(1) / 6
    D_v1 = -G_v1 / Gs
    D_lambda = -G_lambda / Gs
    q_v1 = -gamma / 2 + hs * D_v1
    q_lambda = hs * D_lambda
    a_v1 = -q_v1 / qa
    a_lambda = -q_lambda / qa
    total_D_v1 = D_v1 + Da * a_v1
    total_D_lambda = D_lambda + Da * a_lambda
    Gs_bounds = module.bounds(Gs)
    qa_bounds = module.bounds(qa)
    qualified = valid and Gs_bounds[1] < 0 and not (qa_bounds[0] <= 0 <= qa_bounds[1])
    return {
        "producer": producer,
        "qualified": qualified,
        "event_cells": [cells[0], cells[-1]],
        "event_bracket_exact": [str(cells[0] * step), str((cells[-1] + 1) * step)],
        "maximum_picard_iterations": max_picard,
        "G_s": interval(module, Gs),
        "q_a": interval(module, qa),
        "a_v1": interval(module, a_v1),
        "a_lambda_b": interval(module, a_lambda),
        "D_v1_at_root": interval(module, total_D_v1),
        "D_lambda_b_at_root": interval(module, total_D_lambda),
    }


def structural_audit(result: dict[str, Any], terminal: dict[str, Any], result_path: Path) -> dict[str, Any]:
    cells = result["terminal_parameter_cells"]
    aggregate_v = qpair(result["frozen_design"]["parameter_box"]["v1"])
    aggregate_l = qpair(result["frozen_design"]["parameter_box"]["lambda_b"])
    total = (aggregate_v[1] - aggregate_v[0]) * (aggregate_l[1] - aggregate_l[0])
    volume = fmpq(0)
    inside = True
    pairwise_disjoint = True
    for index, row in enumerate(cells):
        v = qpair(row["parameter_cell"]["v1"])
        l = qpair(row["parameter_cell"]["lambda_b"])
        inside &= aggregate_v[0] <= v[0] < v[1] <= aggregate_v[1] and aggregate_l[0] <= l[0] < l[1] <= aggregate_l[1]
        volume += (v[1] - v[0]) * (l[1] - l[0])
        for other in cells[index + 1 :]:
            ov = qpair(other["parameter_cell"]["v1"])
            ol = qpair(other["parameter_cell"]["lambda_b"])
            pairwise_disjoint &= not (max(v[0], ov[0]) < min(v[1], ov[1]) and max(l[0], ol[0]) < min(l[1], ol[1]))
    common_failure = all(
        not row["pass"]
        and row["failure_gate"] == "PARAMETRIC_ROOT"
        and row["global_result"] is None
        and row["d0_result"] is None
        and row["root"]["primary"]["root_box_event"]["obstruction"] == "ZERO_CLUSTER_NOT_CLOSED_BEFORE_S_END"
        and row["root"]["independent"]["root_box_event"]["obstruction"] == "ZERO_CLUSTER_NOT_CLOSED_BEFORE_S_END"
        and row["root"]["primary"]["center_event"]["validated"]
        and row["root"]["independent"]["center_event"]["validated"]
        for row in cells
    )
    checks = {
        "terminal_result_digest": terminal["result_sha256"] == sha256_file(result_path),
        "expected_incomplete_classification": result["status"] == "INCOMPLETE" and result["classification"] == "STATIC_PARAMETER_NEIGHBORHOOD_THEOREM_UNRESOLVED",
        "seven_attempts": result["attempted_parameter_cell_count"] == 7,
        "four_depth2_terminal_cells": len(cells) == 4 and all(row["parameter_cell"]["depth"] == 2 for row in cells),
        "terminal_cells_inside_aggregate": inside,
        "terminal_cells_pairwise_disjoint": pairwise_disjoint,
        "terminal_cells_exact_total_volume": volume == total,
        "common_root_enclosure_failure": common_failure,
        "no_downstream_cover_executed": all(row["global_result"] is None and row["d0_result"] is None for row in cells),
        "zero_admitted_volume": parse_q(result["admitted_parameter_volume_exact"]) == 0,
    }
    return {"pass": all(checks.values()), "checks": checks, "mechanism": "OVERSIZED_ROOT_CONTAINER_CAUSES_FIRST_EVENT_INTERVAL_CLUSTER_TO_REACH_S_END_AND_Q_A_TO_CONTAIN_ZERO", "scientific_consequence": "NO_FINITE_PARAMETER_PERSISTENCE_OR_NONEXISTENCE_INFERENCE"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    guard, resolved = verify_bindings(args.bindings.resolve())
    started = time.monotonic()
    result_path = resolved["neighborhood_result"]
    result = json.loads(result_path.read_text())
    terminal = json.loads(resolved["neighborhood_terminal"].read_text())
    audit = structural_audit(result, terminal, result_path)
    ctx.prec = CONFIG["arb_precision_bits"]
    primary = load_module("sensitivity_primary", resolved["primary_source"])
    independent = load_module("sensitivity_independent", resolved["independent_source"])
    primary_record = event_union(primary, "primary")
    independent_record = event_union(independent, "independent")
    names = ("a_v1", "a_lambda_b", "D_v1_at_root", "D_lambda_b_at_root")
    agreement: dict[str, Any] = {}
    for name in names:
        p = qpair(primary_record[name]["exact_bounds"])
        i = qpair(independent_record[name]["exact_bounds"])
        agreement[name] = {"intervals_overlap": intersect(p, i), "same_nonzero_sign": interval_sign(p) == interval_sign(i) and interval_sign(p) != "zero-containing", "primary_sign": interval_sign(p), "independent_sign": interval_sign(i)}
    sensitivity_pass = primary_record["qualified"] and independent_record["qualified"] and all(item["intervals_overlap"] and item["same_nonzero_sign"] for item in agreement.values())
    v0 = dyadic(CONFIG["central_parameters_decimal_labels"]["v1"])
    l0 = dyadic(CONFIG["central_parameters_decimal_labels"]["lambda_b"])
    vb = qpair(CONFIG["finite_box_exact"]["v1"])
    lb = qpair(CONFIG["finite_box_exact"]["lambda_b"])
    dv = max(abs(vb[0] - v0), abs(vb[1] - v0))
    dl = max(abs(lb[0] - l0), abs(lb[1] - l0))
    root_shift_bounds = []
    event_shift_bounds = []
    for record in (primary_record, independent_record):
        av = qpair(record["a_v1"]["exact_bounds"])
        al = qpair(record["a_lambda_b"]["exact_bounds"])
        Dv = qpair(record["D_v1_at_root"]["exact_bounds"])
        Dl = qpair(record["D_lambda_b_at_root"]["exact_bounds"])
        root_shift_bounds.append(max_abs(av) * dv + max_abs(al) * dl)
        event_shift_bounds.append(max_abs(Dv) * dv + max_abs(Dl) * dl)
    linearized = {
        "not_a_rigorous_finite_box_bound": True,
        "v1_max_offset_exact": str(dv),
        "lambda_b_max_offset_exact": str(dl),
        "maximum_root_displacement_from_central_local_sensitivities_exact": str(max(root_shift_bounds)),
        "maximum_root_displacement_decimal": float(max(root_shift_bounds)),
        "maximum_event_position_displacement_from_central_local_sensitivities_exact": str(max(event_shift_bounds)),
        "maximum_event_position_displacement_decimal": float(max(event_shift_bounds)),
    }
    passed = audit["pass"] and sensitivity_pass
    output = {
        "schema": "lin-static-parameter-neighborhood-diagnosis-result-v1",
        "status": "COMPLETE" if passed else "INCOMPLETE",
        "classification": "ROOT_CONTAINER_DEPENDENCY_IDENTIFIED_AND_LOCAL_PARAMETER_SENSITIVITY_CERTIFIED" if passed else "PARAMETER_NEIGHBORHOOD_DIAGNOSIS_INCOMPLETE",
        "guard": guard,
        "structural_failure_audit": audit,
        "primary_sensitivity": primary_record,
        "independent_sensitivity": independent_record,
        "producer_agreement": agreement,
        "local_sensitivity_pass": sensitivity_pass,
        "linearized_design_diagnostic": linearized,
        "runtime_seconds": time.monotonic() - started,
        "claim_boundary": ["The incomplete finite-box theorem remains incomplete.", "The sensitivities are rigorous local interval quantities at the central narrow root box, but their finite-box extrapolation is only a design diagnostic.", "No spectral or dynamical stability claim follows."],
    }
    result_out = args.output.resolve() / "RESULT.json"
    atomic_write_json(result_out, output)
    atomic_write_json(args.output.resolve() / "TERMINAL.json", {"schema": "lin-static-parameter-neighborhood-diagnosis-terminal-v1", "status": output["status"], "classification": output["classification"], "result_sha256": sha256_file(result_out), "guard": guard, "predecessors_mutated": False})
    print(json.dumps({"status": output["status"], "classification": output["classification"]}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
