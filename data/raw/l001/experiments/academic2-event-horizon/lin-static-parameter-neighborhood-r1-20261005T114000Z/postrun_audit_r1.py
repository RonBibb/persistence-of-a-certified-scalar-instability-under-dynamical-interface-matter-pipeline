#!/usr/bin/env python3
"""Independent structural reconstruction for an admitted R1 result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from flint import fmpq

import r1_runner as r1


def q(text: str) -> fmpq:
    return r1.base.parse_q(text)


def pair(values: list[str]) -> tuple[fmpq, fmpq]:
    return q(values[0]), q(values[1])


def exact_cover(rows: list[dict[str, Any]], hi: fmpq) -> bool:
    previous = fmpq(0)
    valid = bool(rows)
    for row in sorted(rows, key=lambda item: q(item["a_exact_bounds"][0])):
        lo, right = pair(row["a_exact_bounds"])
        valid &= lo == previous and right > lo
        previous = right
    return bool(valid and previous == hi)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bindings", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    guard, resolved = r1.verify_bindings(args.bindings.resolve())
    result_path = args.output.resolve() / "RESULT.json"
    terminal_path = args.output.resolve() / "TERMINAL_CHECKPOINT.json"
    result = json.loads(result_path.read_text())
    terminal = json.loads(terminal_path.read_text())
    cells = result["terminal_parameter_cells"]
    aggregate_v = pair(r1.CONFIG["parameter_box"]["v1"])
    aggregate_l = pair(r1.CONFIG["parameter_box"]["lambda_b"])
    total = (aggregate_v[1] - aggregate_v[0]) * (aggregate_l[1] - aggregate_l[0])
    area = fmpq(0)
    inside = True
    disjoint = True
    cell_checks: list[dict[str, Any]] = []
    for index, row in enumerate(cells):
        cell = row["parameter_cell"]
        v, lb = pair(cell["v1"]), pair(cell["lambda_b"])
        inside &= aggregate_v[0] <= v[0] < v[1] <= aggregate_v[1] and aggregate_l[0] <= lb[0] < lb[1] <= aggregate_l[1]
        area += (v[1] - v[0]) * (lb[1] - lb[0])
        for other in cells[index + 1 :]:
            ov, ol = pair(other["parameter_cell"]["v1"]), pair(other["parameter_cell"]["lambda_b"])
            disjoint &= not (max(v[0], ov[0]) < min(v[1], ov[1]) and max(lb[0], ol[0]) < min(lb[1], ol[1]))
        root_lo, root_hi = pair(r1.CONFIG["root_box"])
        root_ok = bool(row["root"]["pass"])
        for producer in ("primary", "independent"):
            record = row["root"][producer]
            image = pair(record["newton_image"]["exact_bounds"])
            root_ok &= record["qualified_parametric_interval_newton"] and root_lo < image[0] <= image[1] < root_hi and q(record["strict_inclusion_margin_exact"]) > 0
        global_rows = row["global_result"]["terminal_boxes"]
        global_ok = row["global_result"]["pass"] and not row["global_result"]["unresolved"] and exact_cover(global_rows, r1.base.dyadic("0.1")) and sum(item["classification"] == "CERTIFIED_PARAMETRIC_ROOT_CONTAINER" for item in global_rows) == 1
        d0_rows = row["d0_result"]["terminal_boxes"]
        d0_ok = row["d0_result"]["pass"] and not row["d0_result"]["unresolved"] and len(d0_rows) == 693 and exact_cover(d0_rows, r1.base.dyadic("0.1")) and all(item["excluded"] for item in d0_rows)
        cell_checks.append({"parameter_cell": cell, "root": bool(root_ok), "global": bool(global_ok), "d0": bool(d0_ok), "pass": bool(root_ok and global_ok and d0_ok)})
    checks = {
        "result_digest": terminal["result_sha256"] == r1.base.sha256_file(result_path),
        "guard_exact": result["guard"] == guard == terminal["guard"],
        "frozen_design_exact": result["frozen_design"] == r1.CONFIG,
        "success_classification": result["status"] == "COMPLETE" and result["classification"] == r1.base.SUCCESS and terminal["status"] == "COMPLETE",
        "cells_inside": inside,
        "cells_disjoint": disjoint,
        "exact_total_volume": area == total == q(result["admitted_parameter_volume_exact"]),
        "all_cell_gates": bool(cell_checks) and all(item["pass"] for item in cell_checks),
        "no_unresolved": not result["unresolved_parameter_cells"],
        "predecessors_unchanged": all(r1.base.sha256_file(path) == json.loads(args.bindings.read_text())["imports"][name]["sha256"] for name, path in resolved.items()),
    }
    passed = all(checks.values())
    audit = {"schema": "lin-static-parameter-neighborhood-r1-postrun-audit-v1", "status": "PASS" if passed else "FAIL", "checks": checks, "cell_checks": cell_checks, "result_sha256": r1.base.sha256_file(result_path), "predecessors_mutated": False}
    audit_path = args.output.resolve() / "POSTRUN_AUDIT.json"
    r1.base.atomic_write_json(audit_path, audit)
    r1.base.atomic_write_json(args.output.resolve() / "POSTRUN_TERMINAL.json", {"schema": "lin-static-parameter-neighborhood-r1-postrun-terminal-v1", "status": audit["status"], "audit_sha256": r1.base.sha256_file(audit_path), "result_sha256": audit["result_sha256"]})
    print(json.dumps({"status": audit["status"]}, sort_keys=True))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
