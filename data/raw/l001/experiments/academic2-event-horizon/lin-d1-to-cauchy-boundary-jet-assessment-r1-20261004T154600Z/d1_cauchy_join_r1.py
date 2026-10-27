#!/usr/bin/env python3
"""Exact-decimal parser correction for the frozen D1/Cauchy evaluator."""

from __future__ import annotations

import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


BASE_PATH = (
    Path(__file__).resolve().parent.parent
    / "lin-d1-to-cauchy-boundary-jet-assessment-20261004T154046Z"
    / "d1_cauchy_join.py"
)
spec = importlib.util.spec_from_file_location("d1_cauchy_join_frozen_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot import frozen base evaluator")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def decimal_fmpq(text: str) -> Any:
    value = Fraction(str(text))
    return base.fmpq(value.numerator, value.denominator)


def point_record(text: str) -> dict[str, Any]:
    value = decimal_fmpq(text)
    return {"exact": str(value), "decimal": float(value)}


def difference_record(interval: Any, point_text: str) -> dict[str, Any]:
    point = decimal_fmpq(point_text)
    difference = interval - base.arb(point)
    lo, hi = base.bounds(interval)
    return {
        "D1_minus_P16": base.interval_record(difference),
        "P16_point": point_record(point_text),
        "passes_absolute_1e_minus_8": bool(
            lo - base.ABSOLUTE_GATE <= point <= hi + base.ABSOLUTE_GATE
        ),
    }


base.point_record = point_record
base.difference_record = difference_record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base.ctx.prec = 768
    result = base.run(args.root.resolve(), args.output.resolve())
    print(json.dumps({
        "status": result["status"],
        "classification": result["classification"],
        "technical_gates": result["technical_gates"],
        "mismatch_categories": result["mismatch_categories"],
    }, indent=2))


if __name__ == "__main__":
    main()
