"""Rigorous Arb box-flow feasibility pilot for the D1 proper-distance ODE.

This validates a second-order Taylor enclosure on fixed proper-distance steps.
It does not validate event order, sensitivities, or an interval-Newton root.
"""

from __future__ import annotations

import json
import platform
import sys
import time

from flint import arb, ctx, fmpq


M2 = "0.41"
GAMMA = "20.0"
V0 = "0.1"
V1 = "0.09048374180359596"
LAMBDA_A = "5.999990376773895"
LAMBDA_B = "-6.052844277744164"
A_LO = "0.09901076956670637"
A_HI = "0.09901087894170638"
S_END = fmpq(2)
STEP_COUNTS = (512, 1024)
SUBDIVISIONS = (1, 8, 32)
PRECISION_BITS = 384


def dyadic(text: str) -> fmpq:
    n, d = float(text).as_integer_ratio()
    return fmpq(n, d)


def ball(lo: fmpq, hi: fmpq) -> arb:
    if lo > hi:
        raise ValueError("empty interval")
    return arb((lo + hi) / 2, (hi - lo) / 2)


def bounds(x: arb) -> tuple[fmpq, fmpq]:
    return x.lower().fmpq(), x.upper().fmpq()


def hull(x: arb, y: arb) -> arb:
    xl, xh = bounds(x)
    yl, yh = bounds(y)
    return ball(min(xl, yl), max(xh, yh))


def inflate(x: arb) -> arb:
    lo, hi = bounds(x)
    pad = (hi - lo) / 10 + fmpq(1, 2**300)
    return ball(lo - pad, hi + pad)


def strictly_contains(outer: arb, inner: arb) -> bool:
    ol, oh = bounds(outer)
    il, ih = bounds(inner)
    return ol < il and ih < oh


def width(x: arb) -> float:
    lo, hi = bounds(x)
    return float(hi - lo)


M2_Q = dyadic(M2)
GAMMA_Q = dyadic(GAMMA)
V0_Q = dyadic(V0)
V1_Q = dyadic(V1)
LAMBDA_A_Q = dyadic(LAMBDA_A)
LAMBDA_B_Q = dyadic(LAMBDA_B)
A_LO_Q = dyadic(A_LO)
A_HI_Q = dyadic(A_HI)


def launch(a: arb) -> list[arb]:
    h0 = -(arb(LAMBDA_A_Q) + arb(GAMMA_Q) * (a - arb(V0_Q)) ** 2 / 2) / 6
    s0 = arb(GAMMA_Q) * (a - arb(V0_Q)) / 2
    curvature = h0**2 - 1 - s0**2 / 12 + arb(M2_Q) * a**2 / 12
    return [arb(0), h0, a, s0, arb(0), curvature]


def rhs(y: list[arb]) -> list[arb]:
    A, H, phi, S, _Z, curvature = y
    em2a = (-2 * A).exp()
    return [
        H,
        -S**2 / 3 - curvature * em2a,
        S,
        arb(M2_Q) * phi - 4 * H * S,
        (-A).exp(),
        arb(0),
    ]


def second_derivative(y: list[arb], fy: list[arb]) -> list[arb]:
    A, H, phi, S, _Z, curvature = y
    return [
        fy[1],
        2 * curvature * (-2 * A).exp() * H - 2 * S * fy[3] / 3,
        fy[3],
        -4 * S * fy[1] + arb(M2_Q) * S - 4 * H * fy[3],
        -(-A).exp() * H,
        arb(0),
    ]


def picard_box(y0: list[arb], h: fmpq) -> tuple[list[arb], int]:
    time_interval = ball(fmpq(0), h)
    f0 = rhs(y0)
    z = [inflate(hull(y, y + time_interval * f)) for y, f in zip(y0, f0, strict=True)]
    for iteration in range(1, 25):
        fz = rhs(z)
        candidate = [hull(y, y + time_interval * f) for y, f in zip(y0, fz, strict=True)]
        if all(strictly_contains(zo, ci) for zo, ci in zip(z, candidate, strict=True)):
            return z, iteration
        z = [inflate(hull(zo, ci)) for zo, ci in zip(z, candidate, strict=True)]
    raise RuntimeError("Picard enclosure did not self-contain in 24 iterations")


def step(y0: list[arb], h: fmpq) -> tuple[list[arb], int]:
    z, iterations = picard_box(y0, h)
    f0 = rhs(y0)
    f2 = second_derivative(z, rhs(z))
    return [y + arb(h) * f + arb(h * h / 2) * a2 for y, f, a2 in zip(y0, f0, f2, strict=True)], iterations


def residuals(y: list[arb]) -> tuple[arb, arb]:
    _A, H, phi, S, _Z, _curvature = y
    tau_b = arb(LAMBDA_B_Q) + arb(GAMMA_Q) * (phi - arb(V1_Q)) ** 2 / 2
    upper_israel = H - tau_b / 6
    upper_scalar = S + arb(GAMMA_Q) * (phi - arb(V1_Q)) / 2
    return upper_israel, upper_scalar


def run_box(a_lo: fmpq, a_hi: fmpq, steps: int) -> dict[str, object]:
    h = S_END / steps
    y = launch(ball(a_lo, a_hi))
    max_picard_iterations = 0
    for _ in range(steps):
        y, iterations = step(y, h)
        max_picard_iterations = max(max_picard_iterations, iterations)
    G, scalar = residuals(y)
    return {
        "state_widths_at_s_2": [width(v) for v in y],
        "upper_israel_residual_bounds": [str(q) for q in bounds(G)],
        "upper_israel_residual_width": width(G),
        "upper_scalar_residual_bounds": [str(q) for q in bounds(scalar)],
        "upper_scalar_residual_width": width(scalar),
        "max_picard_iterations": max_picard_iterations,
    }


def run_level(steps: int, subdivisions: int) -> dict[str, object]:
    started = time.monotonic()
    delta = (A_HI_Q - A_LO_Q) / subdivisions
    rows = []
    for i in range(subdivisions):
        lo = A_LO_Q + i * delta
        hi = A_LO_Q + (i + 1) * delta
        rows.append(run_box(lo, hi, steps))
    return {
        "steps": steps,
        "subdivisions": subdivisions,
        "boxes_completed": len(rows),
        "wall_seconds": time.monotonic() - started,
        "maximum_state_widths_at_s_2": [max(row["state_widths_at_s_2"][j] for row in rows) for j in range(6)],
        "maximum_upper_israel_residual_width": max(row["upper_israel_residual_width"] for row in rows),
        "maximum_upper_scalar_residual_width": max(row["upper_scalar_residual_width"] for row in rows),
        "maximum_picard_iterations": max(row["max_picard_iterations"] for row in rows),
        "first_box_residual_bounds": {
            "upper_israel": rows[0]["upper_israel_residual_bounds"],
            "upper_scalar": rows[0]["upper_scalar_residual_bounds"],
        },
        "last_box_residual_bounds": {
            "upper_israel": rows[-1]["upper_israel_residual_bounds"],
            "upper_scalar": rows[-1]["upper_scalar_residual_bounds"],
        },
    }


def main() -> None:
    ctx.prec = PRECISION_BITS
    levels = []
    status = "COMPLETE"
    error = None
    try:
        for steps in STEP_COUNTS:
            for subdivisions in SUBDIVISIONS:
                levels.append(run_level(steps, subdivisions))
    except Exception as exc:  # retained as technical incompleteness
        status = "INCOMPLETE"
        error = repr(exc)
    finest = levels[-1] if levels else None
    readiness = bool(
        status == "COMPLETE"
        and finest is not None
        and finest["steps"] == 1024
        and finest["subdivisions"] == 32
        and finest["maximum_upper_israel_residual_width"] <= 1e-3
        and finest["maximum_upper_scalar_residual_width"] <= 1e-3
    )
    result = {
        "schema": "d1-validated-box-flow-prerequisite-v1",
        "status": status,
        "authority": "RIGOROUS_FIXED_STEP_FLOW_ENCLOSURE_FEASIBILITY_ONLY",
        "runtime": {
            "python": sys.version,
            "platform": platform.platform(),
            "python_flint": __import__("flint").__version__,
            "arb_precision_bits": PRECISION_BITS,
        },
        "frozen_design": {
            "shooting_interval_decimal_labels": [A_LO, A_HI],
            "binary64_values_promoted_to_exact_dyadics": True,
            "proper_distance_endpoint": 2,
            "step_counts": list(STEP_COUNTS),
            "subdivisions": list(SUBDIVISIONS),
            "readiness_width_gate_each_residual": 1e-3,
        },
        "levels": levels,
        "readiness_for_sensitivity_and_interval_newton": readiness,
        "error": error,
        "not_established": [
            "No upper-Israel event order or transversality is enclosed.",
            "No variational equation or interval-Newton map is evaluated.",
            "No curved-background existence result follows.",
            "A fixed-s endpoint is not the moving upper-wall event.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
