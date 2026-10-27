#!/usr/bin/env python3
"""Producer-independent validated replay of the D1 shooting root.

This source imports no predecessor implementation and reads no predecessor
enclosure. It uses Arb balls, an independent Taylor-series algebra, and a
Picard box to bound the fifth-order Taylor remainder on every cell.
"""

from __future__ import annotations

import json
import platform
import sys
import time
from dataclasses import dataclass
from typing import Any

from flint import arb, ctx, fmpq


M2 = "0.41"
GAMMA = "20.0"
V0 = "0.1"
V1 = "0.09048374180359596"
LAMBDA_A = "5.999990376773895"
LAMBDA_B = "-6.052844277744164"
ROOT_CENTER = "0.09901086589880687"
ROOT_LO = "0.09901086489880687"
ROOT_HI = "0.09901086689880687"

STEP_COUNTS = (4096, 8192)
S_END = fmpq(2)
PRECISION_BITS = 768
TAYLOR_ORDER = 5
MAX_PICARD_ITERATIONS = 32


def dyadic(text: str) -> fmpq:
    numerator, denominator = float(text).as_integer_ratio()
    return fmpq(numerator, denominator)


def ball(lo: fmpq, hi: fmpq) -> arb:
    if lo > hi:
        raise ValueError("empty interval")
    return arb((lo + hi) / 2, (hi - lo) / 2)


def bounds(value: arb) -> tuple[fmpq, fmpq]:
    return value.lower().fmpq(), value.upper().fmpq()


def hull(left: arb, right: arb) -> arb:
    ll, lh = bounds(left)
    rl, rh = bounds(right)
    return ball(min(ll, rl), max(lh, rh))


def union_all(values: list[arb]) -> arb:
    if not values:
        raise ValueError("empty union")
    result = values[0]
    for value in values[1:]:
        result = hull(result, value)
    return result


def inflate(value: arb) -> arb:
    lo, hi = bounds(value)
    pad = (hi - lo) / 8 + fmpq(1, 2**640)
    return ball(lo - pad, hi + pad)


def strictly_contains(outer: arb, inner: arb) -> bool:
    outer_lo, outer_hi = bounds(outer)
    inner_lo, inner_hi = bounds(inner)
    return outer_lo < inner_lo and inner_hi < outer_hi


def contains_zero(value: arb) -> bool:
    lo, hi = bounds(value)
    return lo <= 0 <= hi


def interval_record(value: arb) -> dict[str, Any]:
    lo, hi = bounds(value)
    return {
        "exact_bounds": [str(lo), str(hi)],
        "decimal_bounds": [float(lo), float(hi)],
        "contains_zero": lo <= 0 <= hi,
        "width": float(hi - lo),
    }


M2_Q = dyadic(M2)
GAMMA_Q = dyadic(GAMMA)
V0_Q = dyadic(V0)
V1_Q = dyadic(V1)
LAMBDA_A_Q = dyadic(LAMBDA_A)
LAMBDA_B_Q = dyadic(LAMBDA_B)
ROOT_CENTER_Q = dyadic(ROOT_CENTER)
ROOT_LO_Q = dyadic(ROOT_LO)
ROOT_HI_Q = dyadic(ROOT_HI)


@dataclass
class Series:
    """Truncated ordinary power series with Arb coefficients."""

    coefficients: list[arb]

    @property
    def order(self) -> int:
        return len(self.coefficients) - 1

    def coerce(self, other: object) -> "Series":
        if isinstance(other, Series):
            if other.order != self.order:
                raise ValueError("series orders differ")
            return other
        return Series([arb(other)] + [arb(0) for _ in range(self.order)])

    def __add__(self, other: object) -> "Series":
        other_series = self.coerce(other)
        return Series([a + b for a, b in zip(self.coefficients, other_series.coefficients, strict=True)])

    __radd__ = __add__

    def __neg__(self) -> "Series":
        return Series([-value for value in self.coefficients])

    def __sub__(self, other: object) -> "Series":
        return self + (-self.coerce(other))

    def __rsub__(self, other: object) -> "Series":
        return self.coerce(other) - self

    def __mul__(self, other: object) -> "Series":
        other_series = self.coerce(other)
        out = [arb(0) for _ in range(self.order + 1)]
        for degree in range(self.order + 1):
            total = arb(0)
            for left_degree in range(degree + 1):
                total += self.coefficients[left_degree] * other_series.coefficients[degree - left_degree]
            out[degree] = total
        return Series(out)

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> "Series":
        if isinstance(other, Series):
            raise TypeError("series division is intentionally not implemented")
        return self * (arb(1) / arb(other))

    def __pow__(self, exponent: int) -> "Series":
        if exponent != 2:
            raise ValueError("only squaring is required")
        return self * self

    def exp(self) -> "Series":
        out = [arb(0) for _ in range(self.order + 1)]
        out[0] = self.coefficients[0].exp()
        for degree in range(1, self.order + 1):
            total = arb(0)
            for index in range(1, degree + 1):
                total += arb(index) * self.coefficients[index] * out[degree - index]
            out[degree] = total / degree
        return Series(out)


def launch(a: arb) -> list[arb]:
    H = -(arb(LAMBDA_A_Q) + arb(GAMMA_Q) * (a - arb(V0_Q)) ** 2 / 2) / 6
    S = arb(GAMMA_Q) * (a - arb(V0_Q)) / 2
    curvature = H**2 - 1 - S**2 / 12 + arb(M2_Q) * a**2 / 12
    H_a = -arb(GAMMA_Q) * (a - arb(V0_Q)) / 6
    S_a = arb(GAMMA_Q) / 2
    curvature_a = 2 * H * H_a - S * S_a / 6 + arb(M2_Q) * a / 6
    return [
        arb(0),
        H,
        a,
        S,
        arb(0),
        curvature,
        arb(0),
        H_a,
        arb(1),
        S_a,
        arb(0),
        curvature_a,
    ]


def rhs(state: list[Any]) -> list[Any]:
    A, H, phi, S, _Z, curvature, A_a, H_a, phi_a, S_a, _Z_a, curvature_a = state
    exp_minus_2A = (-2 * A).exp()
    exp_minus_A = (-A).exp()
    zero = A * 0
    return [
        H,
        -S**2 / 3 - curvature * exp_minus_2A,
        S,
        arb(M2_Q) * phi - 4 * H * S,
        exp_minus_A,
        zero,
        H_a,
        2 * curvature * exp_minus_2A * A_a - 2 * S * S_a / 3 - exp_minus_2A * curvature_a,
        S_a,
        arb(M2_Q) * phi_a - 4 * (H_a * S + H * S_a),
        -exp_minus_A * A_a,
        zero,
    ]


def taylor_coefficients(initial: list[arb], order: int) -> list[list[arb]]:
    series = [Series([value] + [arb(0) for _ in range(order)]) for value in initial]
    for degree in range(order):
        derivative_series = rhs(series)
        for component, derivative in zip(series, derivative_series, strict=True):
            component.coefficients[degree + 1] = derivative.coefficients[degree] / (degree + 1)
    return [component.coefficients for component in series]


def picard_box(initial: list[arb], step: fmpq) -> tuple[list[arb], int]:
    time_interval = ball(fmpq(0), step)
    initial_rhs = rhs(initial)
    enclosure = [
        inflate(hull(value, value + time_interval * derivative))
        for value, derivative in zip(initial, initial_rhs, strict=True)
    ]
    for iteration in range(1, MAX_PICARD_ITERATIONS + 1):
        enclosure_rhs = rhs(enclosure)
        candidate = [
            hull(value, value + time_interval * derivative)
            for value, derivative in zip(initial, enclosure_rhs, strict=True)
        ]
        if all(strictly_contains(outer, inner) for outer, inner in zip(enclosure, candidate, strict=True)):
            return enclosure, iteration
        enclosure = [inflate(hull(outer, inner)) for outer, inner in zip(enclosure, candidate, strict=True)]
    raise RuntimeError(f"Picard enclosure failed after {MAX_PICARD_ITERATIONS} iterations")


def advance(initial: list[arb], enclosure: list[arb], step: fmpq) -> list[arb]:
    point_coefficients = taylor_coefficients(initial, TAYLOR_ORDER - 1)
    remainder_coefficients = taylor_coefficients(enclosure, TAYLOR_ORDER)
    out: list[arb] = []
    step_ball = arb(step)
    for point, remainder in zip(point_coefficients, remainder_coefficients, strict=True):
        value = arb(0)
        power = arb(1)
        for degree in range(TAYLOR_ORDER):
            value += point[degree] * power
            power *= step_ball
        value += remainder[TAYLOR_ORDER] * power
        out.append(value)
    return out


def upper_quantities(state: list[arb]) -> dict[str, arb]:
    A, H, phi, S, Z, curvature, _A_a, H_a, phi_a, S_a, _Z_a, _curvature_a = state
    flow = rhs(state)
    tau_b = arb(LAMBDA_B_Q) + arb(GAMMA_Q) * (phi - arb(V1_Q)) ** 2 / 2
    G = H - tau_b / 6
    G_s = flow[1] - arb(GAMMA_Q) * (phi - arb(V1_Q)) * S / 6
    G_a = H_a - arb(GAMMA_Q) * (phi - arb(V1_Q)) * phi_a / 6
    D_a = -G_a / G_s
    h = S + arb(GAMMA_Q) * (phi - arb(V1_Q)) / 2
    h_a = S_a + arb(GAMMA_Q) * phi_a / 2
    h_s = flow[3] + arb(GAMMA_Q) * S / 2
    q_a = h_a + h_s * D_a
    wall_rhs = tau_b**2 / 36 - 1 - arb(GAMMA_Q) ** 2 * (phi - arb(V1_Q)) ** 2 / 48 + arb(M2_Q) * phi**2 / 12
    wall_identity = curvature * (-2 * A).exp() - wall_rhs
    return {
        "A": A,
        "H": H,
        "phi": phi,
        "S": S,
        "Z": Z,
        "curvature": curvature,
        "warp": A.exp(),
        "G": G,
        "G_s": G_s,
        "G_a": G_a,
        "D_a": D_a,
        "h": h,
        "h_a": h_a,
        "h_s": h_s,
        "q_a": q_a,
        "upper_wall_identity": wall_identity,
    }


def first_integral(state: list[arb]) -> arb:
    A, H, phi, S, _Z, curvature = state[:6]
    return H**2 - 1 - S**2 / 12 + arb(M2_Q) * phi**2 / 12 - curvature * (-2 * A).exp()


def lower_wall_identity(a: arb) -> arb:
    initial = launch(a)
    _A, _H, phi, _S, _Z, curvature = initial[:6]
    tau_a = arb(LAMBDA_A_Q) + arb(GAMMA_Q) * (phi - arb(V0_Q)) ** 2 / 2
    rhs_value = tau_a**2 / 36 - 1 - arb(GAMMA_Q) ** 2 * (phi - arb(V0_Q)) ** 2 / 48 + arb(M2_Q) * phi**2 / 12
    return curvature - rhs_value


def run_event(a_lo: fmpq, a_hi: fmpq, steps: int) -> dict[str, Any]:
    step = S_END / steps
    state = launch(ball(a_lo, a_hi))
    zero_cells: list[int] = []
    signs: list[str] = []
    event_records: list[dict[str, arb]] = []
    maximum_picard_iterations = 0
    first_integral_every_contains_zero = True
    first_integral_lower: fmpq | None = None
    first_integral_upper: fmpq | None = None
    all_H_strictly_negative = True
    global_warp_lower: fmpq | None = None
    global_warp_upper: fmpq | None = None

    for cell in range(steps):
        enclosure, iterations = picard_box(state, step)
        maximum_picard_iterations = max(maximum_picard_iterations, iterations)

        invariant = first_integral(enclosure)
        invariant_lo, invariant_hi = bounds(invariant)
        first_integral_every_contains_zero &= invariant_lo <= 0 <= invariant_hi
        first_integral_lower = invariant_lo if first_integral_lower is None else min(first_integral_lower, invariant_lo)
        first_integral_upper = invariant_hi if first_integral_upper is None else max(first_integral_upper, invariant_hi)

        H_lo, H_hi = bounds(enclosure[1])
        all_H_strictly_negative &= H_hi < 0
        warp = enclosure[0].exp()
        warp_lo, warp_hi = bounds(warp)
        global_warp_lower = warp_lo if global_warp_lower is None else min(global_warp_lower, warp_lo)
        global_warp_upper = warp_hi if global_warp_upper is None else max(global_warp_upper, warp_hi)

        quantities = upper_quantities(enclosure)
        G_lo, G_hi = bounds(quantities["G"])
        if G_lo > 0:
            signs.append("positive")
        elif G_hi < 0:
            signs.append("negative")
        else:
            signs.append("zero-containing")
            zero_cells.append(cell)
            event_records.append(quantities)
        state = advance(state, enclosure, step)

    if not zero_cells:
        raise RuntimeError("no upper-Israel zero-containing cell")

    contiguous = zero_cells == list(range(zero_cells[0], zero_cells[-1] + 1))
    positive_before = all(sign == "positive" for sign in signs[: zero_cells[0]])
    negative_after = all(sign == "negative" for sign in signs[zero_cells[-1] + 1 :])
    event_union = {
        key: union_all([record[key] for record in event_records])
        for key in event_records[0]
    }
    G_s_lo, G_s_hi = bounds(event_union["G_s"])
    q_a_lo, q_a_hi = bounds(event_union["q_a"])
    event_validated = contiguous and positive_before and negative_after and G_s_hi < 0
    first_integral_union = ball(first_integral_lower, first_integral_upper)
    warp_union = ball(global_warp_lower, global_warp_upper)
    return {
        "steps": steps,
        "event_cells": [zero_cells[0], zero_cells[-1]],
        "event_bracket_exact": [str(zero_cells[0] * step), str((zero_cells[-1] + 1) * step)],
        "event_bracket_decimal": [float(zero_cells[0] * step), float((zero_cells[-1] + 1) * step)],
        "zero_cells_contiguous": contiguous,
        "positive_before": positive_before,
        "negative_after": negative_after,
        "event_validated": event_validated,
        "G_s_strictly_negative": G_s_hi < 0,
        "q_a_excludes_zero": q_a_lo > 0 or q_a_hi < 0,
        "maximum_picard_iterations": maximum_picard_iterations,
        "all_H_strictly_negative": all_H_strictly_negative,
        "first_integral_every_cell_contains_zero": first_integral_every_contains_zero,
        "first_integral_union": interval_record(first_integral_union),
        "global_warp_enclosure": interval_record(warp_union),
        "event_quantities": {key: interval_record(value) for key, value in event_union.items()},
        "_event_balls": event_union,
    }


def public_event(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if not key.startswith("_")}


def run_level(steps: int) -> dict[str, Any]:
    started = time.monotonic()
    root_box = run_event(ROOT_LO_Q, ROOT_HI_Q, steps)
    center = run_event(ROOT_CENTER_Q, ROOT_CENTER_Q, steps)
    derivative = root_box["_event_balls"]["q_a"]
    derivative_lo, derivative_hi = bounds(derivative)
    if derivative_lo <= 0 <= derivative_hi:
        newton = None
        strict_self_map = False
        newton_ball = None
    else:
        newton_ball = arb(ROOT_CENTER_Q) - center["_event_balls"]["h"] / derivative
        newton_lo, newton_hi = bounds(newton_ball)
        newton = interval_record(newton_ball)
        strict_self_map = ROOT_LO_Q < newton_lo and newton_hi < ROOT_HI_Q

    root_pass = bool(
        root_box["event_validated"]
        and center["event_validated"]
        and root_box["q_a_excludes_zero"]
        and strict_self_map
    )

    root_event = root_box["_event_balls"]
    lower_identity = lower_wall_identity(ball(ROOT_LO_Q, ROOT_HI_Q))
    curvature_lo, _curvature_hi = bounds(root_event["curvature"])
    D_lo = fmpq(root_box["event_bracket_exact"][0])
    _D_hi = fmpq(root_box["event_bracket_exact"][1])
    L_lo, _L_hi = bounds(root_event["Z"])
    warp_lo, _warp_hi = bounds(root_event["warp"])
    geometry_checks = {
        "curvature_strictly_positive": curvature_lo > 0,
        "proper_separation_strictly_positive": D_lo > 0,
        "conformal_separation_strictly_positive": L_lo > 0,
        "warp_strictly_positive": warp_lo > 0,
        "warp_monotone_decreasing": root_box["all_H_strictly_negative"],
        "first_integral_every_cell_contains_zero": root_box["first_integral_every_cell_contains_zero"],
        "lower_wall_identity_contains_zero": contains_zero(lower_identity),
        "upper_wall_identity_contains_zero": contains_zero(root_event["upper_wall_identity"]),
        "upper_Israel_residual_contains_zero": contains_zero(root_event["G"]),
        "upper_scalar_residual_contains_zero": contains_zero(root_event["h"]),
    }
    geometry_pass = all(geometry_checks.values())
    return {
        "steps": steps,
        "wall_seconds": time.monotonic() - started,
        "root_box": public_event(root_box),
        "center": public_event(center),
        "interval_newton_image": newton,
        "strict_self_map": strict_self_map,
        "root_replay_pass": root_pass,
        "geometry": {
            "curvature": root_box["event_quantities"]["curvature"],
            "proper_separation": {
                "exact_bounds": root_box["event_bracket_exact"],
                "decimal_bounds": root_box["event_bracket_decimal"],
            },
            "conformal_separation": root_box["event_quantities"]["Z"],
            "warp_at_event": root_box["event_quantities"]["warp"],
            "global_warp_enclosure": root_box["global_warp_enclosure"],
            "first_integral_union": root_box["first_integral_union"],
            "lower_wall_identity": interval_record(lower_identity),
            "upper_wall_identity": root_box["event_quantities"]["upper_wall_identity"],
            "upper_Israel_residual": root_box["event_quantities"]["G"],
            "upper_scalar_residual": root_box["event_quantities"]["h"],
            "checks": geometry_checks,
            "pass": geometry_pass,
        },
        "_newton_ball": newton_ball,
    }


def algebra_controls() -> dict[str, bool]:
    order = 5
    x = Series([arb(1), arb(2), arb(3)] + [arb(0) for _ in range(order - 2)])
    y = Series([arb(4), arb(5), arb(0)] + [arb(0) for _ in range(order - 2)])
    product = x * y
    exponential = Series([arb(0), arb(1)] + [arb(0) for _ in range(order - 1)]).exp()
    return {
        "product_degree_0": product.coefficients[0] == 4,
        "product_degree_1": product.coefficients[1] == 13,
        "product_degree_2": product.coefficients[2] == 22,
        "exp_degree_0": exponential.coefficients[0] == 1,
        "exp_degree_1": exponential.coefficients[1] == 1,
        "exp_degree_2_overlaps_half": exponential.coefficients[2].overlaps(arb(1) / 2),
        "exp_degree_5_overlaps_factorial_inverse": exponential.coefficients[5].overlaps(arb(1) / 120),
        "launch_first_integral_contains_zero": contains_zero(first_integral(launch(ball(ROOT_LO_Q, ROOT_HI_Q)))),
    }


def main() -> None:
    ctx.prec = PRECISION_BITS
    started = time.monotonic()
    controls = algebra_controls()
    levels: list[dict[str, Any]] = []
    status = "COMPLETE"
    error = None
    try:
        if not all(controls.values()):
            raise RuntimeError("independent Taylor algebra control failed")
        for steps in STEP_COUNTS:
            levels.append(run_level(steps))
    except Exception as exc:
        status = "INCOMPLETE"
        error = repr(exc)

    root_pass = status == "COMPLETE" and len(levels) == len(STEP_COUNTS) and all(level["root_replay_pass"] for level in levels)
    geometry_pass = root_pass and all(level["geometry"]["pass"] for level in levels)
    nesting = False
    if len(levels) == 2 and levels[0]["_newton_ball"] is not None and levels[1]["_newton_ball"] is not None:
        coarse_lo, coarse_hi = bounds(levels[0]["_newton_ball"])
        fine_lo, fine_hi = bounds(levels[1]["_newton_ball"])
        nesting = coarse_lo < fine_lo < fine_hi < coarse_hi

    if status != "COMPLETE":
        classification = "INDEPENDENT_D1_REPLAY_INCOMPLETE"
    elif root_pass and geometry_pass:
        classification = "INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS"
    elif root_pass:
        classification = "INDEPENDENT_D1_ROOT_REPLAY_PASS_GEOMETRY_INCOMPLETE"
    else:
        classification = "INDEPENDENT_D1_REPLAY_NOT_ESTABLISHED"

    result = {
        "schema": "lin-d1-independent-ode-replay-result-v1",
        "status": status,
        "classification": classification,
        "authority": "PRODUCER_INDEPENDENT_INTERVAL_FLOW_SENSITIVITY_NEWTON_AND_DERIVED_GEOMETRY_REPLAY",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": PRECISION_BITS,
            "wall_seconds": time.monotonic() - started,
        },
        "method": {
            "imports_predecessor_source": False,
            "reads_predecessor_enclosures": False,
            "taylor_order": TAYLOR_ORDER,
            "remainder": "Picard self-containing cell box evaluated by independent Taylor-series recurrence",
            "step_counts": list(STEP_COUNTS),
        },
        "frozen_inputs": {
            "m_squared": M2,
            "gamma": GAMMA,
            "v0": V0,
            "v1": V1,
            "lambda_a": LAMBDA_A,
            "lambda_b": LAMBDA_B,
            "root_center": ROOT_CENTER,
            "root_box": [ROOT_LO, ROOT_HI],
            "proper_distance_endpoint": 2,
        },
        "algebra_controls": controls,
        "all_levels_root_replay_pass": root_pass,
        "all_levels_geometry_pass": geometry_pass,
        "fine_newton_image_strictly_inside_coarse_image": nesting,
        "levels": [
            {key: value for key, value in level.items() if not key.startswith("_")}
            for level in levels
        ],
        "error": error,
        "claim_boundary": [
            "The result concerns only the declared reduced static shooting problem.",
            "No stability or dynamical selection is established.",
            "No bridge to the separate constraint-compatible initial-data line is established.",
            "No collapse, event-horizon, radion-transition, or baby-universe claim follows."
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
