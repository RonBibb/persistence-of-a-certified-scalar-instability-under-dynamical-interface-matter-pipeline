"""Read-only independent review of a frozen MP-background stability packet.

No primary integrator, primary verifier, or primary equation helper is imported.
Actual-coordinate barycentric rows differentiate the saved fields. Conformal
mode shooting uses separate equations. A central-fine background is independently
integrated with MP RK4 in conformal distance, at two predeclared step counts.
All result data are printed to stdout; this program writes no files.
"""

import argparse
import hashlib
import json
import os
import platform
from fractions import Fraction
from pathlib import Path

import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicSpline, PPoly
from scipy.optimize import brentq


R = np.longdouble
BACKGROUND_GATE = 1e-8
MODE_GATE = 1e-6
MASS_GATE = 1e-7
MASS_BRACKET = (-0.0015, -0.0011)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def exact_fraction(value):
    if isinstance(value, str):
        return Fraction(value)
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction.from_float(value)
    raise TypeError("Unsupported exact scalar: " + type(value).__name__)


def real(value):
    if isinstance(value, str) and "/" in value:
        q = Fraction(value)
        return R(str(q.numerator)) / R(str(q.denominator))
    return R(value)


def mp_real(value):
    q = exact_fraction(value)
    return mp.mpf(q.numerator) / q.denominator


def norm(*terms):
    result = np.abs(sum(terms)) / (1 + sum(np.abs(v) for v in terms))
    if not np.all(np.isfinite(result)):
        raise RuntimeError("Nonfinite independent residual")
    return float(np.max(result))


class LocalDerivative:
    """Direct barycentric differentiation; independent of Fornberg recursion."""

    def __init__(self, grid, width=9):
        grid = np.asarray(grid, dtype=R)
        n = len(grid)
        if width != 9 or n < width or np.any(np.diff(grid) <= 0):
            raise RuntimeError("Invalid frozen differentiation grid")
        self.scale = (grid[-1] - grid[0]) / (n - 1)
        starts = np.clip(np.arange(n) - width // 2, 0, n - width)
        self.indices = starts[:, None] + np.arange(width)[None, :]
        self.x = (grid[self.indices] - grid[:, None]) / self.scale
        delta = self.x[:, :, None] - self.x[:, None, :]
        delta[:, np.arange(width), np.arange(width)] = 1
        bary = 1 / np.prod(delta, axis=2)
        target = np.arange(n) - starts
        denominator = -self.x.copy()
        denominator[np.arange(n), target] = 1
        self.d1 = bary / (bary[np.arange(n), target, None] * denominator)
        self.d1[np.arange(n), target] = 0
        diagonal = -np.sum(self.d1, axis=1)
        self.d2 = 2 * self.d1 * (diagonal[:, None] - 1 / denominator)
        self.d1[np.arange(n), target] = diagonal
        self.d2[np.arange(n), target] = -np.sum(self.d2, axis=1)

    def apply(self, values):
        values = np.asarray(values, dtype=R)
        local = values[self.indices] - values[:, None]
        first = np.sum(self.d1 * local, axis=1) / self.scale
        slope = (local[:, -1] - local[:, 0]) / (self.x[:, -1] - self.x[:, 0])
        second = np.sum(self.d2 * (local - slope[:, None] * self.x), axis=1) / self.scale**2
        return first, second


def polynomial_control():
    x = np.linspace(R(0), R(1), 33, dtype=R)
    y = x**7 - 2 * x**3 + 3 * x + 1
    first, second = LocalDerivative(x).apply(y)
    e1 = float(np.max(abs(first - (7 * x**6 - 6 * x**2 + 3))))
    e2 = float(np.max(abs(second - (42 * x**5 - 12 * x))))
    return {"first": e1, "second": e2, "pass": max(e1, e2) <= 1e-20}


def integrate(values, grid):
    values, grid = np.asarray(values, dtype=R), np.asarray(grid, dtype=R)
    h = (grid[-1] - grid[0]) / (len(grid) - 1)
    if len(grid) % 2 != 1 or np.max(abs(np.diff(grid) / h - 1)) > R("1e-25"):
        raise RuntimeError("MP saved Simpson grid is not odd and uniform")
    return h / 3 * (values[0] + values[-1] + 4 * np.sum(values[1:-1:2]) + 2 * np.sum(values[2:-1:2]))


def storage_check(background, mode_arrays):
    rows = [background["s"], *background["fields"]]
    if len(rows) != 6 or any(len(row) != 2001 for row in rows):
        raise RuntimeError("MP storage must have 2001 proper samples and five field rows")
    if not all(isinstance(v, str) for row in rows for v in row):
        raise RuntimeError("MP fields or proper nodes were not stored as strings")
    for key in ("a", "k", "D", "L"):
        if not isinstance(background[key], str):
            raise RuntimeError("MP metadata was not stored as strings: " + key)
    data = np.asarray(rows, dtype=R)
    if not np.all(np.isfinite(data)) or np.any(np.diff(data[0]) <= 0):
        raise RuntimeError("Nonfinite or nonmonotone MP saved fields")
    if len(background["E"]) != 2001 or not all(isinstance(v, str) for v in background["E"]):
        raise RuntimeError("Auxiliary exponential lacks MP string storage")
    E = np.asarray(background["E"], dtype=R)
    exponential_identity_error = float(np.max(abs(E * np.exp(data[1]) - 1)))
    if mode_arrays["mode"].shape != (3, 2001) or mode_arrays["s"].shape != (2001,):
        raise RuntimeError("Mode storage shape mismatch")
    expected_mode_nodes = np.asarray(background["s"], dtype=np.float64)
    if not np.array_equal(mode_arrays["s"], expected_mode_nodes):
        raise RuntimeError("Mode samples are not at the rounded saved MP proper nodes")
    source_dps = int(background.get("mp_dps", background.get("dps", background["control"]["dps"])))
    with mp.workdps(max(90, source_dps + 15)):
        D = mp_real(background["D"])
        relative_uniform_error = max(abs(mp_real(v) - D * j / 2000) / (1 + abs(D))
                                     for j, v in enumerate(background["s"]))
        metadata_error = max(abs(mp_real(background["fields"][4][-1]) - mp_real(background["L"])),
                             abs(mp_real(background["s"][-1]) - D))
        extra_information = sum(mp_real(v) != mp.mpf(float(v)) for row in rows for v in row)
        uniform_gate = mp.mpf(10) ** (-source_dps + 5)
        storage_pass = (relative_uniform_error <= uniform_gate and metadata_error <= uniform_gate
                        and exponential_identity_error <= 1e-20
                        and extra_information > 10000)
        return {"source_dps": source_dps, "all_fields_decimal_strings": True,
                "longdouble_nmant": int(np.finfo(R).nmant),
                "nonbinary64_value_count": extra_information,
                "total_value_count": 12006,
                "relative_uniform_node_error": str(relative_uniform_error),
                "metadata_endpoint_error": str(metadata_error),
                "uniform_storage_gate": str(uniform_gate),
                "independent_E_exp_W_identity_error": exponential_identity_error,
                "mode_nodes_match_rounded_MP_nodes": True, "pass": bool(storage_pass)}


def saved_check(background, arrays, receipt, stride):
    s = np.asarray(background["s"], dtype=R)[::stride]
    W, H, phi, T, z = np.asarray(background["fields"], dtype=R)[:, ::stride]
    psi, f, g = np.asarray(arrays["mode"], dtype=R)[:, ::stride]
    d = LocalDerivative(s)
    Ws, Wss = d.apply(W)
    ps, pss = d.apply(phi)
    Hs, _ = d.apply(H)
    Ts, _ = d.apply(T)
    zs, _ = d.apply(z)
    hs, _ = d.apply(psi)
    fs, fss = d.apply(f)
    m = {key: real(value) for key, value in background["model_exact"].items()}
    mu, k = real(receipt["mu"]), real(background["k"])
    e = np.exp(-2 * W)
    bg = {
        "direct_metric": norm(Wss, ps**2 / 3, k * e),
        "direct_scalar": norm(pss, 4 * Ws * ps, -m["m2"] * phi),
        "first_integral": norm(Ws**2, -np.ones_like(W), -ps**2 / 12, m["m2"] * phi**2 / 12, -k * e),
        "W_aux": norm(Ws, -H), "Phi_aux": norm(ps, -T),
        "H_aux": norm(Hs, T * T / 3, k * e),
        "T_aux": norm(Ts, 4 * H * T, -m["m2"] * phi),
        "coordinate": norm(zs, -np.exp(-W)),
    }
    mode = {
        "momentum": norm(hs, 2 * Ws * psi, ps * f / 3),
        "Einstein": norm(ps * fs, -(m["m2"] * phi - 4 * Ws * ps) * f,
                         (2 * ps**2 - 3 * (mu + 4 * k) * e) * psi),
        "KG": norm(fss, 4 * Ws * fs, (mu * e - m["m2"]) * f,
                   6 * ps * hs, 4 * m["m2"] * phi * psi),
    }
    for i, sign, v, lam in ((0, 1, m["v0"], m["lambda_a"]), (-1, -1, m["v1"], m["lambda_b"])):
        tau = lam + m["gamma"] * (phi[i] - v)**2 / 2
        bg["Israel_" + str(i)] = norm(sign * Ws[i], tau / 6)
        bg["scalar_wall_" + str(i)] = norm(sign * ps[i], -m["gamma"] * (phi[i] - v) / 2)
        mode["Robin_" + str(i)] = norm(fs[i], 2 * ps[i] * psi[i], -sign * m["gamma"] * f[i] / 2)
    Z = 2 * integrate(np.exp(2 * W) * (f * f + 6 * psi * psi), s)
    delta = -2 * integrate(psi, s)
    metric_terms = (Wss, ps**2 / 3, k * e)
    metric_residual = sum(metric_terms)
    metric_scaled = abs(metric_residual) / (1 + sum(abs(v) for v in metric_terms))
    worst = int(np.argmax(metric_scaled))
    norm_error = abs(Z / real(receipt["Z"]) - 1)
    delta_error = abs(delta / real(receipt["deltaD"]) - 1)
    passed = (max(bg.values()) <= BACKGROUND_GATE and max(mode.values()) <= MODE_GATE
              and Z > 0 and abs(delta / np.sqrt(Z)) > 1e-6
              and max(norm_error, delta_error) <= 1e-7)
    return {"stride": stride, "samples": len(s), "stencil": 9,
            "all_nodes_including_endpoints": True, "primary_rhs_used_as_derivative": False,
            "background": bg, "mode": mode, "max_background": max(bg.values()),
            "max_mode": max(mode.values()), "Z": float(Z), "deltaD": float(delta),
            "overlap": float(delta / np.sqrt(Z)), "relative_norm_receipt_error": float(norm_error),
            "relative_delta_receipt_error": float(delta_error),
            "derived_f_s_vs_stored_g": norm(fs, -g),
            "metric_worst": {"sample_index": worst, "normalized_s": float(s[worst] / s[-1]),
                             "signed_absolute_residual": float(metric_residual[worst]),
                             "terms": [float(v[worst]) for v in metric_terms],
                             "stencil_indices": list(map(int, d.indices[worst]))},
            "pass": bool(passed)}


class ConformalBackground:
    def __init__(self, background, stride):
        W, H, phi, T, z = np.asarray(background["fields"], dtype=np.float64)[:, ::stride]
        if np.any(np.diff(z) <= 0):
            raise RuntimeError("Nonmonotone independent conformal grid")
        self.L = float(z[-1])
        self.k = float(background["k"])
        self.m2 = float(real(background["model_exact"]["m2"]))
        self.gamma = float(real(background["model_exact"]["gamma"]))
        self.spline = CubicSpline(z, np.array([W, np.exp(W) * H, phi, np.exp(W) * T]).T, axis=0)

    def __call__(self, z):
        W, A, phi, S = np.moveaxis(self.spline(z), -1, 0)
        a = np.exp(W)
        potential_gradient = a * a * self.m2 * phi
        return a, A, phi, S, potential_gradient


def conformal_shoot(bg, mu, dense=False):
    a, A, phi, S, Vp = bg(0.0)
    denominator = a * bg.gamma * S / 2 - (Vp - 4 * A * S)
    if abs(denominator) <= 1e-12:
        raise RuntimeError("Independent conformal lower-wall degeneracy")
    f = 3 * (mu + 4 * bg.k) / denominator
    initial = [1.0, f, a * bg.gamma * f / 2 - 2 * S]

    def rhs(z, y):
        a, A, phi, S, Vp = bg(z)
        psi, field, p = y
        return [-2 * A * psi - S * field / 3, p,
                -3 * A * p + (a * a * bg.m2 - mu + 2 * S * S) * field
                + (12 * A * S - 4 * Vp) * psi]

    sol = solve_ivp(rhs, (0.0, bg.L), initial, method="DOP853", rtol=2e-13,
                    atol=2e-16, max_step=bg.L / 128, dense_output=dense)
    if not sol.success:
        raise RuntimeError("Independent conformal mode integration failed: " + sol.message)
    a, A, phi, S, Vp = bg(bg.L)
    psi, f, p = sol.y[:, -1]
    return float(p + 2 * S * psi + a * bg.gamma * f / 2), sol


def replay_mode(background, arrays, receipt, stride):
    bg = ConformalBackground(background, stride)
    mismatch = lambda mass: conformal_shoot(bg, mass)[0]
    lo, hi = MASS_BRACKET
    left, right = mismatch(lo), mismatch(hi)
    if left * right >= 0:
        raise RuntimeError("Independent conformal fixed mass bracket failed")
    mu = brentq(mismatch, lo, hi, xtol=5e-16, rtol=2e-14, maxiter=80)
    wall, sol = conformal_shoot(bg, mu, True)
    W, H, phi, T, z = np.asarray(background["fields"], dtype=np.float64)
    target = arrays["mode"].copy()
    target[2] *= np.exp(W)
    profile = np.max(abs(sol.sol(z) - target) / (1 + abs(target)), axis=1)
    mass_difference = abs(mu - float(receipt["mu"]))
    return {"stride": stride, "samples": len(z[::stride]), "mu": float(mu),
            "difference_from_proper": float(mu - float(receipt["mu"])),
            "bracket": list(MASS_BRACKET), "bracket_mismatches": [left, right],
            "upper_wall_absolute": wall, "profile_scaled_differences": list(map(float, profile)),
            "pass": bool(mass_difference <= MASS_GATE and max(profile) <= MODE_GATE)}


def scalar_turn_check(background, arrays, receipt):
    s = np.asarray(background["s"], dtype=np.float64)
    W, H, phi, T, z = np.asarray(background["fields"], dtype=np.float64)
    crossings = np.flatnonzero(T[:-1] * T[1:] < 0)
    if len(crossings) != 1:
        return {"turn_count": len(crossings), "pass": False}
    i = int(crossings[0])
    interpolation = CubicSpline(s, np.array([W, phi, T, arrays["mode"][0], arrays["mode"][1]]).T, axis=0)
    turn = brentq(lambda x: interpolation(x)[2], s[i], s[i + 1], xtol=5e-15, rtol=2e-14)
    warp, scalar, gradient, psi, f = np.asarray(interpolation(turn), dtype=R)
    m2, mu, k = real(background["model_exact"]["m2"]), real(receipt["mu"]), real(background["k"])
    residual = norm(m2 * scalar * f, 3 * (mu + 4 * k) * np.exp(-2 * warp) * psi)
    return {"turn_count": 1, "s": float(turn), "normalized_relation": residual,
            "sample_interpolation": "independent cubic on saved fields", "pass": residual <= MODE_GATE}


def central_branch_check(packet, bindings, background, receipt):
    inp = lambda name: packet / bindings["inputs"][name]["path"]
    high = read(inp("d1_high_result"))
    independent = read(inp("d1_independent_result"))
    fine = max(independent["levels"], key=lambda row: row["steps"])
    root_interval = list(map(Fraction, high["narrow"]["newton_exact_bounds"]))
    curvature_interval = list(map(Fraction, fine["geometry"]["curvature"]["exact_bounds"]))
    event_interval = list(map(exact_fraction, high["narrow"]["event_bracket"]))
    with np.load(inp("old_background_arrays"), allow_pickle=False) as old:
        polynomial = PPoly(old["poly_coefficients"], old["mesh"])
        old_L = float(np.exp(old["parameters"][0]))
    old_meta = read(inp("old_background_receipt"))["report"]
    old_mode = read(inp("old_summary"))
    W, H, phi, T, z = np.asarray(background["fields"], dtype=np.float64)
    current = np.asarray([W, np.exp(W) * H, phi, np.exp(W) * T])
    reference = polynomial(z / old_L).T
    differences = np.max(abs(current - reference) / (1 + abs(reference)), axis=1)
    D_difference = abs(float(background["D"]) / old_meta["proper_separation_D"] - 1)
    L_difference = abs(float(background["L"]) / old_L - 1)
    mass_difference = abs(float(receipt["mu"]) - old_mode["mu"])
    tests = {
        "a_in_D1": root_interval[0] <= Fraction(background["a"]) <= root_interval[1],
        "D_in_D1": event_interval[0] <= Fraction(background["D"]) <= event_interval[1],
        "k_in_D1": curvature_interval[0] <= Fraction(background["k"]) <= curvature_interval[1],
        "mass_agreement": mass_difference <= MASS_GATE,
        "D_agreement": D_difference <= 1e-7, "L_agreement": L_difference <= 1e-7,
        "whole_profile_agreement": max(differences) <= 1e-7,
    }
    return {"checks": {key: bool(value) for key, value in tests.items()},
            "profile_scaled_maxima": dict(zip(["W", "A", "Phi", "S"], map(float, differences))),
            "mass_difference": mass_difference, "D_relative_difference": D_difference,
            "L_relative_difference": L_difference, "pass": bool(all(tests.values()))}


def pair_check(records):
    if len(records) != 2:
        return {"pair_complete": False, "pass": False}
    first, second = records
    mu0, mu1 = real(first[0]["mu"]), real(second[0]["mu"])
    lambda0 = mu0 + 4 * real(first[1]["k"])
    lambda1 = mu1 + 4 * real(second[1]["k"])
    dm, dl = abs(mu1 - mu0), abs(lambda1 - lambda0)
    tests = {"both_producer_admitted": all(row[0]["accepted"] for row in records),
             "mass_refinement": dm <= MASS_GATE,
             "mass_sign_resolved": mu1 < -1e-8 and abs(mu1) > 100 * dm,
             "exceptional_sector_separated": abs(lambda1) > 100 * dl}
    return {"checks": {key: bool(value) for key, value in tests.items()},
            "mass_difference": float(dm), "lambda_difference": float(dl),
            "mu": float(mu1), "lambda": float(lambda1), "pass": bool(all(tests.values()))}


def conformal_background_control(background):
    """Independent MP RK4; no primary Taylor recurrence or dense coefficients."""
    with mp.workdps(50):
        m = {key: mp_real(value) for key, value in background["model_exact"].items()}
        a0, k = mp_real(background["a"]), mp_real(background["k"])
        H0 = -(m["lambda_a"] + m["gamma"] * (a0 - m["v0"])**2 / 2) / 6
        T0 = m["gamma"] * (a0 - m["v0"]) / 2
        k0 = H0**2 - 1 - T0**2 / 12 + m["m2"] * a0**2 / 12
        z = [mp_real(v) for v in background["fields"][4]]
        saved_s = [mp_real(v) for v in background["s"]]
        W, H, phi, T = [[mp_real(v) for v in row] for row in background["fields"][:4]]
        expected = [[W[i], mp.exp(W[i]) * H[i], phi[i], mp.exp(W[i]) * T[i], saved_s[i]]
                    for i in range(len(z))]

        def rhs(y):
            warp, A, scalar, S, proper = y
            aw = mp.exp(warp)
            return [A, A * A - S * S / 3 - k, S,
                    m["m2"] * aw * aw * scalar - 3 * A * S, aw]

        def rk4(y, h):
            q1 = rhs(y)
            q2 = rhs([v + h * q / 2 for v, q in zip(y, q1)])
            q3 = rhs([v + h * q / 2 for v, q in zip(y, q2)])
            q4 = rhs([v + h * q for v, q in zip(y, q3)])
            return [v + h * (r1 + 2 * r2 + 2 * r3 + r4) / 6
                    for v, r1, r2, r3, r4 in zip(y, q1, q2, q3, q4)]

        runs = []
        profiles = []
        for subdivisions in (4, 8):
            y = [mp.mpf(0), H0, a0, T0, mp.mpf(0)]
            trace = [y[:]]
            errors = [mp.mpf(0)] * 5
            for i in range(1, len(z)):
                step = (z[i] - z[i - 1]) / subdivisions
                for _ in range(subdivisions):
                    y = rk4(y, step)
                trace.append(y[:])
                for j in range(5):
                    errors[j] = max(errors[j], abs(y[j] - expected[i][j]) / (1 + abs(expected[i][j])))
            walls = {}
            for index, sign, v, lam in ((0, 1, m["v0"], m["lambda_a"]), (-1, -1, m["v1"], m["lambda_b"])):
                warp, A, scalar, S, proper = trace[index]
                warp_factor = mp.exp(warp)
                physical_H, physical_T = A / warp_factor, S / warp_factor
                tau = lam + m["gamma"] * (scalar - v)**2 / 2
                terms = [sign * physical_H, tau / 6]
                walls["Israel_" + str(index)] = abs(sum(terms)) / (1 + sum(abs(v) for v in terms))
                terms = [sign * physical_T, -m["gamma"] * (scalar - v) / 2]
                walls["scalar_" + str(index)] = abs(sum(terms)) / (1 + sum(abs(v) for v in terms))
            passed = max([*errors, *walls.values()]) <= mp.mpf("1e-8")
            runs.append({"substeps_per_saved_z_interval": subdivisions, "steps": 2000 * subdivisions,
                         "mp_dps": 50, "field_scaled_maxima": dict(zip(["W", "A", "Phi", "S", "s"], map(float, errors))),
                         "wall_normalized_residuals": {key: float(value) for key, value in walls.items()},
                         "pass": bool(passed)})
            profiles.append(trace)
        paired = max(abs(fine[j] - coarse[j]) / (1 + abs(fine[j]))
                     for coarse, fine in zip(*profiles) for j in range(5))
        curvature_error = abs(k0 - k) / (1 + abs(k))
        passed = all(row["pass"] for row in runs) and paired <= mp.mpf("1e-8") and curvature_error <= mp.mpf("1e-35")
        return {"formulation": "W_z=A; A_z=A^2-S^2/3-k; Phi_z=S; S_z=m2 exp(2W)Phi-3AS; s_z=exp(W)",
                "method": "independent 50-digit fixed-step classical RK4", "root_reshooting": False,
                "same_exact_initial_launch": True, "launch_curvature_scaled_error": str(curvature_error),
                "refinement_scaled_maximum": float(paired), "runs": runs, "pass": bool(passed)}


def metadata_checks(background, receipt, bindings, r2):
    expected = {key: exact_fraction(value) for key, value in bindings["model_exact"].items()}
    expected.update({key: Fraction(value) for key, value in receipt["point"]["exact_parameters"].items()})
    model_match = {key: Fraction(value) == expected[key] for key, value in background["model_exact"].items()}
    if set(model_match) != {"gamma", "m2", "lambda_a", "lambda_b", "v0", "v1"}:
        raise RuntimeError("Exact six-parameter model schema mismatch")
    root_box = [Fraction(v) for v in r2["frozen_design"]["root_box"]]
    root_inside = root_box[0] <= Fraction(background["a"]) <= root_box[1]
    parameter_inside = {key: Fraction(bounds[0]) <= Fraction(background["model_exact"][key]) <= Fraction(bounds[1])
                        for key, bounds in r2["frozen_design"]["parameter_box"].items()}
    point_named = [p for p in bindings["points"] if p["name"] == receipt["point"]["name"]]
    point_match = len(point_named) == 1 and point_named[0]["exact_parameters"] == receipt["point"]["exact_parameters"]
    positive_curvature = Fraction(background["k"]) > 0
    return {"exact_six_parameter_match": model_match, "root_in_frozen_R2_tube": root_inside,
            "parameter_membership": parameter_inside, "declared_point_identity": point_match,
            "positive_curvature": positive_curvature,
            "pass": bool(all(model_match.values()) and root_inside and all(parameter_inside.values()) and point_match and positive_curvature)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--output", default="output")
    parser.add_argument("--allow-nonterminal", action="store_true")
    args = parser.parse_args()
    packet = args.packet.resolve()
    output = packet / args.output
    if platform.system() != "Linux" or np.finfo(R).nmant < 100:
        raise RuntimeError("Linux with genuine extended-precision numpy.longdouble required")
    if any(os.environ.get(k) != "1" for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")):
        raise RuntimeError("Exactly one numerical thread required")
    bindings_path = packet / "BINDINGS.json"
    bindings = read(bindings_path)
    guard = digest(bindings_path)
    tracked = {Path(__file__).resolve(), bindings_path, output / "CHECKPOINT.json"}
    for name, expected in bindings["source"].items():
        path = packet / name
        if digest(path) != expected:
            raise RuntimeError("Frozen source mismatch: " + name)
        tracked.add(path)
    for name, entry in bindings["inputs"].items():
        path = (packet / entry["path"]).resolve()
        if digest(path) != entry["sha256"]:
            raise RuntimeError("Frozen input mismatch: " + name)
        tracked.add(path)
    runtime = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
               "mpmath": mp.__version__, "mpmath_backend": mp.libmp.BACKEND,
               "longdouble_nmant": int(np.finfo(R).nmant)}
    if runtime != bindings["runtime"]:
        raise RuntimeError("Frozen runtime mismatch")
    preflight_path = packet / bindings["inputs"]["preflight_controls"]["path"]
    if digest(preflight_path) != bindings["preflight_sha256"] or not read(preflight_path)["pass"]:
        raise RuntimeError("Frozen preflight evidence mismatch or failure")
    for name, expected in read(preflight_path)["source_sha256"].items():
        if digest(packet / name) != expected:
            raise RuntimeError("Preflight source identity mismatch: " + name)
    tracked.add(preflight_path)
    cp = read(output / "CHECKPOINT.json")
    if cp["guard"] != guard or cp["runtime"] != runtime:
        raise RuntimeError("Checkpoint guard/runtime mismatch")
    expected_order = [p["name"] + "_" + c["name"] for p in bindings["points"] for c in bindings["controls"]]
    if set(cp["completed"]) != set(expected_order[:len(cp["completed"])]) or cp["pending"] != expected_order[len(cp["completed"]):]:
        raise RuntimeError("Checkpoint case queue is not the frozen prefix")
    if "central_independent_sha256" in cp:
        central_path = output / "CENTRAL_INDEPENDENT.json"
        if digest(central_path) != cp["central_independent_sha256"] or read(central_path)["guard"] != guard:
            raise RuntimeError("Central independent receipt identity mismatch")
        tracked.add(central_path)
    if (output / "TERMINAL.json").exists():
        terminal, result = read(output / "TERMINAL.json"), read(output / "RESULT.json")
        if terminal["result_sha256"] != digest(output / "RESULT.json") or any(v["guard"] != guard for v in (terminal, result)):
            raise RuntimeError("Terminal/result identity mismatch")
        tracked.update([output / "TERMINAL.json", output / "RESULT.json"])
    elif not args.allow_nonterminal:
        raise RuntimeError("Independent final review requires a terminal or explicit --allow-nonterminal")
    if (output / "CONTROLS.json").exists():
        path = output / "CONTROLS.json"
        controls = read(path)
        if cp.get("controls_sha256") != digest(path) or not controls["pass"] or controls["guard"] != guard:
            raise RuntimeError("Producer controls receipt does not authenticate or pass")
        tracked.add(path)
    for name, record in cp["completed"].items():
        for kind in ("receipt", "arrays", "background"):
            path = output / record[kind]
            if digest(path) != record[kind + "_sha256"]:
                raise RuntimeError("Completed case artifact mismatch: " + name + "/" + kind)
            tracked.add(path)
    before = {str(p): digest(p) for p in sorted(tracked)}
    polynomial = polynomial_control()
    if not polynomial["pass"]:
        raise RuntimeError("Independent derivative polynomial control failed")
    r2 = read(packet / bindings["inputs"]["r2_result"]["path"])
    cases = []
    pairs = []
    central_control = None
    central_qualified = False
    for point in bindings["points"]:
        point_records = []
        for label in ("coarse", "fine"):
            name = point["name"] + "_" + label
            if name not in cp["completed"]:
                continue
            record = cp["completed"][name]
            receipt = read(output / record["receipt"])
            if receipt.get("guard") != guard:
                raise RuntimeError("Case receipt guard mismatch: " + name)
            if "mu" not in receipt:
                cases.append({"case": name, "producer_solve_incomplete": True, "pass": False,
                              "error": receipt.get("error"), "producer_accepted": receipt.get("accepted", False)})
                continue
            background = read(output / record["background"])
            with np.load(output / record["arrays"], allow_pickle=False) as loaded:
                arrays = {key: loaded[key] for key in ("s", "mode")}
            storage = storage_check(background, arrays)
            metadata = metadata_checks(background, receipt, bindings, r2)
            checks = [saved_check(background, arrays, receipt, stride) for stride in (2, 1)]
            replays = [replay_mode(background, arrays, receipt, stride) for stride in (2, 1)]
            turn = scalar_turn_check(background, arrays, receipt)
            branch = central_branch_check(packet, bindings, background, receipt) if point["name"] == "center" else None
            replay_difference = abs(replays[0]["mu"] - replays[1]["mu"])
            if name == "center_fine":
                central_control = conformal_background_control(background)
            passed = (storage["pass"] and metadata["pass"] and turn["pass"]
                      and (branch is None or branch["pass"]) and all(v["pass"] for v in checks)
                      and all(v["pass"] for v in replays) and replay_difference <= MASS_GATE)
            point_records.append((receipt, background))
            cases.append({"case": name, "storage": storage, "metadata": metadata, "checks": checks,
                          "conformal_mode_replays": replays, "conformal_interpolation_mass_sensitivity": replay_difference,
                          "scalar_turn": turn, "central_branch_comparison": branch,
                          "producer_accepted": bool(receipt["accepted"]), "pass": bool(passed),
                          "agrees_with_producer": bool(passed) == bool(receipt["accepted"])})
        pair = pair_check(point_records)
        if point_records:
            pairs.append({"point": point["name"], **pair})
        if point["name"] == "center":
            center_rows = [r for r in cases if r["case"].startswith("center_")]
            central_qualified = (len(center_rows) == 2 and all(r["pass"] for r in center_rows)
                                 and pair["pass"] and central_control is not None and central_control["pass"])
    after = {str(p): digest(p) for p in sorted(tracked)}
    if before != after:
        raise RuntimeError("Frozen inputs or completed artifacts changed during independent review")
    all_pass = bool(cases and central_qualified and all(row["pass"] for row in cases) and all(row["pass"] for row in pairs))
    report = {"classification": "INDEPENDENT_MP_STABILITY_CHECKS_PASS" if all_pass else "INDEPENDENT_MP_STABILITY_UNRESOLVED",
              "guard": guard,
              "runtime": runtime, "processes": 1, "threads": 1, "polynomial_control": polynomial,
              "cases": cases, "pairs": pairs, "conformal_background_control": central_control,
              "central_qualified": bool(central_qualified), "all_completed_cases_pass": all_pass,
              "completed_case_count": len(cases), "inputs_unchanged": True, "source_and_input_sha256": before,
              "scope": "Finite saved-field numerical qualification at the frozen completed parameter points; no continuous spectral theorem, full stability, nonlinear evolution, event horizon, or new initial-data inference."}
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
