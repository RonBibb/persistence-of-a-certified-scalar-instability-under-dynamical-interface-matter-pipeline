"""Validated first upper-Israel-event bracket over the D1 shooting interval."""

from __future__ import annotations

import json
import platform
import sys
import time

from flint import arb, ctx, fmpq

import validated_flow_pilot as flow


STEPS = 2048
SUBDIVISIONS = 32
S_END = fmpq(2)
PRECISION_BITS = 384
MAX_EVENT_BRACKET_WIDTH = fmpq(1, 100)


def upper_israel(y: list[arb]) -> arb:
    _A, H, phi, _S, _Z, _k = y
    tau_b = arb(flow.LAMBDA_B_Q) + arb(flow.GAMMA_Q) * (phi - arb(flow.V1_Q)) ** 2 / 2
    return H - tau_b / 6


def upper_israel_s(y: list[arb]) -> arb:
    _A, _H, phi, S, _Z, _k = y
    fy = flow.rhs(y)
    return fy[1] - arb(flow.GAMMA_Q) * (phi - arb(flow.V1_Q)) * S / 6


def advance(y: list[arb], z: list[arb], h: fmpq) -> list[arb]:
    f0 = flow.rhs(y)
    f2 = flow.second_derivative(z, flow.rhs(z))
    return [v + arb(h) * f + arb(h * h / 2) * a2 for v, f, a2 in zip(y, f0, f2, strict=True)]


def analyze_box(a_lo: fmpq, a_hi: fmpq) -> dict[str, object]:
    h = S_END / STEPS
    y = flow.launch(flow.ball(a_lo, a_hi))
    zero_cells: list[int] = []
    gs_upper = None
    max_picard = 0
    sign_sequence: list[str] = []
    for index in range(STEPS):
        z, iterations = flow.picard_box(y, h)
        max_picard = max(max_picard, iterations)
        G = upper_israel(z)
        lo, hi = flow.bounds(G)
        if lo > 0:
            sign_sequence.append("positive")
        elif hi < 0:
            sign_sequence.append("negative")
        else:
            sign_sequence.append("zero-containing")
            zero_cells.append(index)
            _gsl, gsh = flow.bounds(upper_israel_s(z))
            gs_upper = gsh if gs_upper is None else max(gs_upper, gsh)
        y = advance(y, z, h)

    contiguous = bool(zero_cells) and zero_cells == list(range(zero_cells[0], zero_cells[-1] + 1))
    positive_before = bool(zero_cells) and all(s == "positive" for s in sign_sequence[: zero_cells[0]])
    negative_after = bool(zero_cells) and all(s == "negative" for s in sign_sequence[zero_cells[-1] + 1 :])
    transverse_negative = gs_upper is not None and gs_upper < 0
    bracket_lo = zero_cells[0] * h if zero_cells else None
    bracket_hi = (zero_cells[-1] + 1) * h if zero_cells else None
    bracket_width = bracket_hi - bracket_lo if zero_cells else None
    passed = bool(
        contiguous
        and positive_before
        and negative_after
        and transverse_negative
        and bracket_width <= MAX_EVENT_BRACKET_WIDTH
    )
    return {
        "passed": passed,
        "zero_cell_count": len(zero_cells),
        "first_zero_cell": zero_cells[0] if zero_cells else None,
        "last_zero_cell": zero_cells[-1] if zero_cells else None,
        "event_bracket": [str(bracket_lo), str(bracket_hi)] if zero_cells else None,
        "event_bracket_width": float(bracket_width) if zero_cells else None,
        "upper_bound_on_G_s_over_zero_cells": float(gs_upper) if gs_upper is not None else None,
        "positive_on_all_preceding_cells": positive_before,
        "negative_on_all_following_cells": negative_after,
        "zero_cells_contiguous": contiguous,
        "max_picard_iterations": max_picard,
    }


def main() -> None:
    ctx.prec = PRECISION_BITS
    started = time.monotonic()
    delta = (flow.A_HI_Q - flow.A_LO_Q) / SUBDIVISIONS
    rows = []
    status = "COMPLETE"
    error = None
    try:
        for i in range(SUBDIVISIONS):
            rows.append(analyze_box(flow.A_LO_Q + i * delta, flow.A_LO_Q + (i + 1) * delta))
    except Exception as exc:
        status = "INCOMPLETE"
        error = repr(exc)
    passed = status == "COMPLETE" and len(rows) == SUBDIVISIONS and all(row["passed"] for row in rows)
    result = {
        "schema": "d1-validated-first-event-prerequisite-v1",
        "status": status,
        "classification": "VALIDATED_FIRST_EVENT_BRACKET_READY" if passed else (
            "VALIDATED_FIRST_EVENT_BRACKET_NOT_ESTABLISHED" if status == "COMPLETE" else "VALIDATED_EVENT_PILOT_INCOMPLETE"
        ),
        "authority": "RIGOROUS_BOX_ENCLOSURE_OF_FIRST_UPPER_ISRAEL_EVENT_ONLY",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": PRECISION_BITS,
            "wall_seconds": time.monotonic() - started,
        },
        "frozen_design": {
            "steps_to_s_2": STEPS,
            "shooting_subdivisions": SUBDIVISIONS,
            "maximum_event_bracket_width": float(MAX_EVENT_BRACKET_WIDTH),
            "flow_source_sha256": "53bcaab6420d050bc4f7e3ca825f74390e0b59b20fe96feae10e72c32288dd3c"
        },
        "all_boxes_pass": passed,
        "maximum_event_bracket_width": max((row["event_bracket_width"] or 0.0) for row in rows) if rows else None,
        "maximum_upper_bound_on_G_s": max(row["upper_bound_on_G_s_over_zero_cells"] for row in rows if row["upper_bound_on_G_s_over_zero_cells"] is not None) if rows else None,
        "minimum_bracket_lower_endpoint": min(row["event_bracket"][0] for row in rows if row["event_bracket"] is not None) if rows else None,
        "maximum_bracket_upper_endpoint": max(row["event_bracket"][1] for row in rows if row["event_bracket"] is not None) if rows else None,
        "box_results": rows,
        "error": error,
        "not_established": [
            "No scalar upper-wall residual root is enclosed.",
            "No event-time sensitivity or interval-Newton map is evaluated.",
            "No curved-background existence theorem follows.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
