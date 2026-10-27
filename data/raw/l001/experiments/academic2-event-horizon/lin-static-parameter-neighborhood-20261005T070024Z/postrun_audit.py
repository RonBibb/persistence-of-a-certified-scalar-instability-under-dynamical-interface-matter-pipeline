#!/usr/bin/env python3
"""Independent structural reconstruction of the parameter-neighborhood result."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
from typing import Any

from flint import fmpq


def load_runner(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("parameter_neighborhood_audit_bound", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import bound runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def q(text: str) -> fmpq:
    if "/" in text:
        a, b = text.split("/", 1)
        return fmpq(int(a), int(b))
    return fmpq(int(text))


def pair(values: list[str]) -> tuple[fmpq, fmpq]:
    return q(values[0]), q(values[1])


def exact_cover(rows: list[dict[str, Any]], lo: fmpq, hi: fmpq) -> bool:
    ordered = sorted(rows, key=lambda row: q(row["a_exact_bounds"][0]))
    previous = lo
    valid = bool(ordered)
    for row in ordered:
        left, right = pair(row["a_exact_bounds"])
        valid &= left == previous and right > left
        previous = right
    return bool(valid and previous == hi)


def rectangles_disjoint(rows: list[dict[str, Any]]) -> bool:
    for index, left in enumerate(rows):
        lv = pair(left["parameter_cell"]["v1"])
        ll = pair(left["parameter_cell"]["lambda_b"])
        for right in rows[index + 1 :]:
            rv = pair(right["parameter_cell"]["v1"])
            rl = pair(right["parameter_cell"]["lambda_b"])
            overlap_v = max(lv[0], rv[0]) < min(lv[1], rv[1])
            overlap_l = max(ll[0], rl[0]) < min(ll[1], rl[1])
            if overlap_v and overlap_l:
                return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    branch = Path(__file__).resolve().parent
    bindings = json.loads(args.bindings.resolve().read_text())
    runner_path = branch / "parameter_neighborhood.py"
    runner = load_runner(runner_path)
    guard, resolved = runner.verify_bindings(args.bindings.resolve())
    result_path = args.output.resolve() / "RESULT.json"
    terminal_path = args.output.resolve() / "TERMINAL_CHECKPOINT.json"
    result = json.loads(result_path.read_text())
    terminal = json.loads(terminal_path.read_text())
    checks: dict[str, bool] = {}
    checks["terminal_result_digest"] = terminal["result_sha256"] == runner.sha256_file(result_path)
    checks["guard_exact"] = result["guard"] == guard == terminal["guard"]
    checks["frozen_design_exact"] = result["frozen_design"] == runner.CONFIG
    checks["classification_consistent"] = (
        result["classification"] == runner.SUCCESS
        and result["status"] == "COMPLETE"
        and terminal["classification"] == runner.SUCCESS
        and terminal["status"] == "COMPLETE"
    )
    cells = result["terminal_parameter_cells"]
    aggregate_v = pair(runner.CONFIG["parameter_box"]["v1"])
    aggregate_l = pair(runner.CONFIG["parameter_box"]["lambda_b"])
    total = (aggregate_v[1] - aggregate_v[0]) * (aggregate_l[1] - aggregate_l[0])
    area = fmpq(0)
    inside = True
    cell_checks: list[dict[str, Any]] = []
    for row in cells:
        cell = row["parameter_cell"]
        v = pair(cell["v1"])
        l = pair(cell["lambda_b"])
        inside &= aggregate_v[0] <= v[0] < v[1] <= aggregate_v[1]
        inside &= aggregate_l[0] <= l[0] < l[1] <= aggregate_l[1]
        area += (v[1] - v[0]) * (l[1] - l[0])
        root = row["root"]
        root_ok = bool(root["pass"])
        root_lo, root_hi = pair(runner.CONFIG["root_box"])
        for producer in ("primary", "independent"):
            record = root[producer]
            image = pair(record["newton_image"]["exact_bounds"])
            root_ok &= bool(record["qualified_parametric_interval_newton"])
            root_ok &= root_lo < image[0] <= image[1] < root_hi
            root_ok &= q(record["strict_inclusion_margin_exact"]) > 0
        global_result = row["global_result"]
        global_rows = global_result["terminal_boxes"]
        global_ok = bool(
            global_result["pass"]
            and not global_result["unresolved"]
            and exact_cover(global_rows, fmpq(0), runner.dyadic("0.1"))
            and sum(item["classification"] == "CERTIFIED_PARAMETRIC_ROOT_CONTAINER" for item in global_rows) == 1
            and all(
                item["classification"]
                in {
                    "CERTIFIED_PARAMETRIC_ROOT_CONTAINER",
                    "NEGATIVE_CURVATURE_EXCLUDED",
                    "FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED",
                }
                for item in global_rows
            )
        )
        d0 = row["d0_result"]
        d0_rows = d0["terminal_boxes"]
        d0_ok = bool(
            d0["pass"]
            and not d0["unresolved"]
            and len(d0_rows) == 693
            and exact_cover(d0_rows, fmpq(0), runner.dyadic("0.1"))
            and all(item["excluded"] for item in d0_rows)
        )
        cell_checks.append(
            {
                "parameter_cell": cell,
                "root_reconstructed": root_ok,
                "global_cover_reconstructed": global_ok,
                "d0_cover_reconstructed": d0_ok,
                "pass": root_ok and global_ok and d0_ok,
            }
        )
    checks["parameter_cells_inside_aggregate"] = inside
    checks["parameter_cells_pairwise_interior_disjoint"] = rectangles_disjoint(cells)
    checks["parameter_volume_exact"] = area == total == q(result["total_parameter_volume_exact"])
    checks["admitted_volume_exact"] = q(result["admitted_parameter_volume_exact"]) == total
    checks["all_cell_gates_reconstructed"] = bool(cell_checks) and all(row["pass"] for row in cell_checks)
    checks["no_unresolved_parameter_cells"] = not result["unresolved_parameter_cells"]
    checks["predecessor_hashes_still_match"] = all(
        runner.sha256_file(path) == bindings["imports"][name]["sha256"] for name, path in resolved.items()
    )
    passed = all(checks.values())
    audit = {
        "schema": "lin-static-parameter-neighborhood-postrun-audit-v1",
        "status": "PASS" if passed else "FAIL",
        "classification": "INDEPENDENT_STRUCTURAL_RECONSTRUCTION_PASS" if passed else "INDEPENDENT_RECONSTRUCTION_FAILED",
        "checks": checks,
        "cell_reconstruction": cell_checks,
        "result_sha256": runner.sha256_file(result_path),
        "bindings_sha256": runner.sha256_file(args.bindings.resolve()),
        "predecessors_mutated": False,
    }
    audit_path = args.output.resolve() / "POSTRUN_AUDIT.json"
    runner.atomic_write_json(audit_path, audit)
    runner.atomic_write_json(
        args.output.resolve() / "POSTRUN_TERMINAL.json",
        {
            "schema": "lin-static-parameter-neighborhood-postrun-terminal-v1",
            "status": audit["status"],
            "classification": audit["classification"],
            "audit_sha256": runner.sha256_file(audit_path),
            "result_sha256": audit["result_sha256"],
        },
    )
    print(json.dumps({"status": audit["status"], "classification": audit["classification"]}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
