"""Diagnostic fixed-separation shooting probe.

This is not interval arithmetic and cannot prove root completeness or
existence. It maps the frozen proper-distance ODE at the source-bound selector
separation to size the validated D2A calculation.
"""

from __future__ import annotations

import json
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq


M2 = 0.41
GAMMA = 20.0
V0 = 0.1
V1 = 0.09048374180359596
LAMBDA_A = 5.999990376773895
LAMBDA_B = -6.052844277744164
D0 = 0.9996389747145851
A_MIN = 0.0924
A_MAX = 0.09999
NO_TURN_LO = 0.0989750001
NO_TURN_HI = 0.0989750002


def launch(a: float) -> tuple[np.ndarray, float]:
    h0 = -(LAMBDA_A + GAMMA * (a - V0) ** 2 / 2) / 6
    s0 = GAMMA * (a - V0) / 2
    curvature = h0 * h0 - 1 - s0 * s0 / 12 + M2 * a * a / 12
    return np.array([0.0, h0, a, s0, 0.0]), curvature


def rhs(_s: float, y: np.ndarray, curvature: float) -> np.ndarray:
    A, H, phi, S, Z = y
    return np.array(
        [
            H,
            -S * S / 3 - curvature * np.exp(-2 * A),
            S,
            M2 * phi - 4 * H * S,
            np.exp(-A),
        ]
    )


def evaluate(a: float, level: dict[str, float]) -> dict[str, float | bool]:
    y0, curvature = launch(a)
    solution = solve_ivp(
        lambda s, y: rhs(s, y, curvature),
        (0.0, D0),
        y0,
        method="DOP853",
        rtol=level["rtol"],
        atol=level["atol"],
        max_step=level["max_step"],
    )
    A, H, phi, S, Z = solution.y[:, -1]
    tau_b = LAMBDA_B + GAMMA * (phi - V1) ** 2 / 2
    G = H - tau_b / 6
    h = S + GAMMA * (phi - V1) / 2
    valid = bool(
        solution.success
        and curvature >= 0
        and np.all(np.isfinite(solution.y))
        and np.all(solution.y[2] > 0)
        and np.all(solution.y[2] <= V0 + 1e-12)
    )
    return {
        "a": a,
        "curvature": float(curvature),
        "A_upper": float(A),
        "H_upper": float(H),
        "phi_upper": float(phi),
        "S_upper": float(S),
        "Z_upper": float(Z),
        "upper_israel_residual": float(G),
        "upper_scalar_residual": float(h),
        "valid_sampled_path": valid,
    }


def run_level(level: dict[str, float], samples: int = 601) -> dict[str, object]:
    grid = np.linspace(A_MIN, A_MAX, samples)
    rows = [evaluate(float(a), level) for a in grid]
    valid = [row for row in rows if row["valid_sampled_path"]]
    brackets: list[tuple[float, float]] = []
    for left, right in zip(rows[:-1], rows[1:], strict=True):
        if not left["valid_sampled_path"] or not right["valid_sampled_path"]:
            continue
        gl = float(left["upper_israel_residual"])
        gr = float(right["upper_israel_residual"])
        if gl == 0 or gl * gr < 0:
            brackets.append((float(left["a"]), float(right["a"])))

    roots: list[dict[str, float | bool]] = []
    for lo, hi in brackets:
        root = brentq(
            lambda a: float(evaluate(a, level)["upper_israel_residual"]),
            lo,
            hi,
            xtol=5e-15,
            rtol=1e-14,
            maxiter=100,
        )
        roots.append(evaluate(root, level))

    min_abs = min(valid, key=lambda row: abs(float(row["upper_israel_residual"])))
    return {
        "level": level,
        "samples": samples,
        "valid_sample_count": len(valid),
        "sign_change_brackets": brackets,
        "roots": roots,
        "minimum_sampled_absolute_G": min_abs,
    }


def main() -> None:
    levels = [
        {"rtol": 1e-10, "atol": 1e-12, "max_step": 0.005},
        {"rtol": 1e-12, "atol": 1e-14, "max_step": 0.0025},
    ]
    result = {
        "schema": "fixed-separation-diagnostic-probe-v1",
        "authority": "FLOATING_DIAGNOSTIC_NOT_ROOT_COMPLETENESS_OR_EXISTENCE_PROOF",
        "parameters": {
            "proper_separation_D0": D0,
            "a_scan": [A_MIN, A_MAX],
            "samples": 601,
            "no_turn_threshold_bracket": [NO_TURN_LO, NO_TURN_HI],
        },
        "levels": [run_level(level) for level in levels],
        "limitations": [
            "Finite sampling cannot exclude tangential or unresolved roots.",
            "solve_ivp is not validated interval integration.",
            "Sampled scalar guards are not continuum enclosures.",
            "The target separation is a source-bound binary64 diagnostic value.",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
