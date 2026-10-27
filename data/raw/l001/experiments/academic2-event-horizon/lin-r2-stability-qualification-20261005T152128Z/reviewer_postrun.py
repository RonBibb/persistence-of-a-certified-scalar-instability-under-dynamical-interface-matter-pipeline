"""Read-only independent saved-field audit and two conformal mode replays.

Run with one numerical thread on Linux after the spectrum-r1 terminal exists.
The script writes no files. It imports the archived conformal solver, but none
of the new proper-coordinate producer/checker source. Derivatives use direct
barycentric differentiation matrices on actual local sample coordinates,
independent of the producer's Fornberg recursion.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import platform
from fractions import Fraction as F
from pathlib import Path

import numpy as np
import scipy
from scipy.interpolate import CubicSpline
from scipy.optimize import brentq

R = np.longdouble


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def norm(*terms):
    value = np.abs(sum(terms)) / (1 + sum(np.abs(t) for t in terms))
    if not np.all(np.isfinite(value)):
        raise RuntimeError("Nonfinite residual")
    return float(np.max(value))


class LocalDerivative:
    def __init__(self, grid, width=9):
        self.grid = np.asarray(grid, dtype=R)
        n = len(grid)
        self.scale = (self.grid[-1] - self.grid[0]) / (n - 1)
        starts = np.clip(np.arange(n) - width//2, 0, n - width)
        self.indices = starts[:, None] + np.arange(width)[None, :]
        self.x = (self.grid[self.indices] - self.grid[:, None]) / self.scale
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
    y = x**7 - 2*x**3 + 3*x + 1
    d1, d2 = LocalDerivative(x).apply(y)
    error1 = float(np.max(abs(d1 - (7*x**6 - 6*x**2 + 3))))
    error2 = float(np.max(abs(d2 - (42*x**5 - 12*x))))
    return {"first": error1, "second": error2, "pass": max(error1, error2) <= 1e-20}


def integrate(values, grid):
    values = np.asarray(values, dtype=R)
    grid = np.asarray(grid, dtype=R)
    h = (grid[-1] - grid[0]) / (len(grid) - 1)
    if len(grid) % 2 != 1 or np.max(abs(np.diff(grid)/h - 1)) > R("1e-10"):
        raise RuntimeError("Simpson grid is not odd and uniform")
    return h/3 * (values[0] + values[-1] + 4*np.sum(values[1:-1:2]) + 2*np.sum(values[2:-1:2]))


def saved_check(arr, receipt, stride, width):
    s = np.asarray(arr["s"][::stride], dtype=R)
    W, H, phi, T, z = np.asarray(arr["background"][:, ::stride], dtype=R)
    psi, f, g = np.asarray(arr["mode"][:, ::stride], dtype=R)
    if not all(np.all(np.isfinite(x)) for x in (s, W, H, phi, T, z, psi, f, g)):
        raise RuntimeError("Nonfinite saved fields")
    d = LocalDerivative(s, width)
    Ws, Wss = d.apply(W)
    ps, pss = d.apply(phi)
    Hs, _ = d.apply(H)
    Ts, _ = d.apply(T)
    zs, _ = d.apply(z)
    hs, _ = d.apply(psi)
    fs, fss = d.apply(f)
    m = {k: R(float(v)) for k, v in receipt["model"].items()}
    mu = R(float(receipt["mu"]))
    k = R(float(receipt["background"]["k"]))
    e = np.exp(-2*W)
    background = {
        "metric": norm(Wss, ps**2/3, k*e),
        "scalar": norm(pss, 4*Ws*ps, -m["m2"]*phi),
        "constraint": norm(Ws**2, -np.ones_like(W), -ps**2/12, m["m2"]*phi**2/12, -k*e),
        "W_aux": norm(Ws, -H), "Phi_aux": norm(ps, -T),
        "H_aux": norm(Hs, T*T/3, k*e),
        "T_aux": norm(Ts, 4*H*T, -m["m2"]*phi),
        "coordinate": norm(zs, -np.exp(-W)),
    }
    mode = {
        "momentum": norm(hs, 2*Ws*psi, ps*f/3),
        "Einstein": norm(ps*fs, -(m["m2"]*phi-4*Ws*ps)*f, (2*ps**2-3*(mu+4*k)*e)*psi),
        "KG": norm(fss, 4*Ws*fs, (mu*e-m["m2"])*f, 6*ps*hs, 4*m["m2"]*phi*psi),
    }
    for i, sign, v, lam in ((0, 1, m["v0"], m["lambda_a"]), (-1, -1, m["v1"], m["lambda_b"])):
        tau = lam + m["gamma"]*(phi[i]-v)**2/2
        background[f"Israel_{i}"] = norm(sign*Ws[i], tau/6)
        background[f"scalar_wall_{i}"] = norm(sign*ps[i], -m["gamma"]*(phi[i]-v)/2)
        mode[f"Robin_{i}"] = norm(fs[i], 2*ps[i]*psi[i], -sign*m["gamma"]*f[i]/2)
    Z = 2*integrate(np.exp(2*W)*(f*f + 6*psi*psi), s)
    delta = -2*integrate(psi, s)
    metric_terms = (Wss, ps**2/3, k*e)
    metric_residual = sum(metric_terms)
    metric_scale = 1 + sum(abs(t) for t in metric_terms)
    worst = int(np.argmax(abs(metric_residual)/metric_scale))
    raw_W = np.asarray(arr["background"][0, ::stride], dtype=np.float64)
    ulp = np.asarray(abs(np.nextafter(raw_W, np.inf) - raw_W), dtype=R)
    storage_bound = np.sum(abs(d.d2)*ulp[d.indices]/2, axis=1)/d.scale**2
    diagnostics = {
        "stride": stride, "samples": len(s), "stencil": width, "background": background, "mode": mode,
        "max_background": max(background.values()), "max_mode": max(mode.values()),
        "Z": float(Z), "deltaD": float(delta), "overlap": float(delta/np.sqrt(Z)),
        "relative_norm_receipt_error": float(abs(Z/R(float(receipt["Z"]))-1)),
        "relative_delta_receipt_error": float(abs(delta/R(float(receipt["deltaD"]))-1)),
        "derived_f_s_vs_stored_g": norm(fs, -g),
        "metric_worst": {"sample_index": worst, "proper_s": float(s[worst]),
            "normalized_s": float(s[worst]/s[-1]), "signed_absolute_residual": float(metric_residual[worst]),
            "terms": list(map(float, [v[worst] for v in metric_terms])),
            "stencil_indices": list(map(int, d.indices[worst])),
            "W_half_ulp_second_derivative_amplification": float(storage_bound[worst]),
            "W_half_ulp_normalized_amplification": float(storage_bound[worst]/metric_scale[worst]),
            "qualification": "Conditioning diagnostic for hypothetical final-storage rounding only; not an error bound on the numerical trajectory."},
    }
    diagnostics["pass"] = bool(diagnostics["max_background"] <= 1e-8 and diagnostics["max_mode"] <= 1e-6
        and Z > 0 and abs(delta/np.sqrt(Z)) > 1e-6
        and diagnostics["relative_norm_receipt_error"] <= 1e-7 and diagnostics["relative_delta_receipt_error"] <= 1e-7)
    return diagnostics


class ConformalBackground:
    def __init__(self, arr, receipt, stride):
        W, H, phi, T, z = arr["background"][:, ::stride]
        if np.any(np.diff(z) <= 0):
            raise RuntimeError("Nonmonotone conformal coordinate")
        self.L = float(z[-1])
        self.k = float(receipt["background"]["k"])
        self.m2 = float(receipt["model"]["m2"])
        self.spline = CubicSpline(z, np.array([W, np.exp(W)*H, phi, np.exp(W)*T]).T, axis=0)

    def __call__(self, z):
        W, A, phi, S = np.moveaxis(self.spline(z), -1, 0)
        a = np.exp(W)
        Vp = a*a*self.m2*phi
        return a, A, phi, S, Vp, Vp-4*A*S


def replay(module, arr, receipt, stride):
    bg = ConformalBackground(arr, receipt, stride)
    mismatch = lambda mass: module.shoot_at(bg, mass, 2e-13)[0]
    lo, hi = -0.0015, -0.0011
    left, right = mismatch(lo), mismatch(hi)
    if left*right >= 0:
        raise RuntimeError("Fixed conformal mass bracket failed")
    mu = brentq(mismatch, lo, hi, xtol=5e-16, rtol=2e-14, maxiter=80)
    wall, sol = module.shoot_at(bg, mu, 2e-13, True)
    z = arr["background"][4]
    mapped = sol.sol(z)
    original = arr["mode"].copy()
    original[2] *= np.exp(arr["background"][0])
    profile = np.max(abs(mapped-original)/(1+abs(original)), axis=1)
    return {"stride": stride, "mu": float(mu), "difference_from_proper": float(mu-receipt["mu"]),
        "bracket_mismatches": [left, right], "upper_wall": float(wall),
        "psi_f_p_scaled_profile_differences": list(map(float, profile)),
        "mass_gate_pass": bool(abs(mu-receipt["mu"]) <= 1e-7)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    args = parser.parse_args()
    packet = args.packet.resolve()
    output = packet/"spectrum-r1"
    if platform.system() != "Linux" or any(os.environ.get(k) != "1" for k in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")):
        raise RuntimeError("Linux and one thread required")
    bindings_path = packet/"SPECTRUM_R1_BINDINGS.json"
    bindings = read(bindings_path)
    guard = digest(bindings_path)
    tracked = {Path(__file__).resolve(), bindings_path, output/"CHECKPOINT.json", output/"CONTROLS.json", output/"RESULT.json", output/"TERMINAL.json"}
    for name, expected in bindings["source"].items():
        path = packet/name
        if digest(path) != expected:
            raise RuntimeError("Source binding mismatch: " + name)
        tracked.add(path)
    for name, entry in bindings["inputs"].items():
        path = (packet/entry["path"]).resolve()
        if digest(path) != entry["sha256"]:
            raise RuntimeError("Input binding mismatch: " + name)
        tracked.add(path)
    result, terminal, cp = (read(output/name) for name in ("RESULT.json", "TERMINAL.json", "CHECKPOINT.json"))
    if terminal["result_sha256"] != digest(output/"RESULT.json") or any(x["guard"] != guard for x in (terminal, result, cp)):
        raise RuntimeError("Terminal/checkpoint guard mismatch")
    if cp["controls_sha256"] != digest(output/"CONTROLS.json"):
        raise RuntimeError("Control receipt digest mismatch")
    old_source = packet.parent/"lin-curved-stability-2026-09-29/code/stability.py"
    old_contract = read(packet.parent/"lin-curved-stability-2026-09-29/CONTRACT.json")
    if digest(old_source) != old_contract["bound_files"]["code/stability.py"]:
        raise RuntimeError("Archived conformal source binding mismatch")
    tracked.add(old_source)
    for rec in cp["completed"].values():
        for key in ("receipt", "arrays"):
            path = output/rec[key]
            if digest(path) != rec[key+"_sha256"]:
                raise RuntimeError("Case digest mismatch")
            tracked.add(path)
    before = {str(p): digest(p) for p in sorted(tracked)}
    control = polynomial_control()
    if not control["pass"]:
        raise RuntimeError("Independent barycentric derivative control failed")
    r2 = read(packet/bindings["inputs"]["r2_result"]["path"])
    root_box = list(map(F, r2["frozen_design"]["root_box"]))
    cases = []
    for label in ("coarse", "fine"):
        name = "center_"+label
        rec = read(output/(name+".json"))
        point = rec["point"]
        arr = np.load(output/(name+".npz"), allow_pickle=False)
        checks = [saved_check(arr, rec, stride, width) for width in (7, 9, 11) for stride in (4, 2, 1)]
        membership = root_box[0] <= F.from_float(rec["background"]["a"]) <= root_box[1]
        parameter_membership = all(F.from_float(point["parameters"][key]) == F(point["exact_parameters"][key])
            and F(r2["frozen_design"]["parameter_box"][key][0]) <= F(point["exact_parameters"][key]) <= F(r2["frozen_design"]["parameter_box"][key][1]) for key in ("v1", "lambda_b"))
        frozen = [row for row in checks if row["stencil"] == 9 and row["stride"] in (2, 1)]
        frozen_pass = bool(membership and parameter_membership and all(row["pass"] for row in frozen))
        cases.append({"case": name, "root_in_exact_R2_tube": membership, "exact_parameter_membership": parameter_membership,
            "checks": checks, "frozen_gate_pass": frozen_pass,
            "agrees_with_producer_acceptance": frozen_pass == rec["accepted"]})
    spec = importlib.util.spec_from_file_location("archived_conformal", old_source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    replays = []
    for name in ("center_coarse", "center_fine"):
        receipt = read(output/(name+".json"))
        arr = np.load(output/(name+".npz"), allow_pickle=False)
        rows = [replay(module, arr, receipt, stride) for stride in (2, 1)]
        replays.append({"point": name, "cases": rows, "interpolation_mass_sensitivity": abs(rows[0]["mu"]-rows[1]["mu"]),
            "pass": all(row["mass_gate_pass"] for row in rows) and abs(rows[0]["mu"]-rows[1]["mu"]) <= 1e-7})
    if before != {str(p): digest(p) for p in sorted(tracked)}:
        raise RuntimeError("Inputs changed during audit")
    summary = {"classification": "INDEPENDENT_DIAGNOSIS_CONFIRMS_FROZEN_GATE_FAILURE" if all(c["agrees_with_producer_acceptance"] for c in cases) and not cases[1]["frozen_gate_pass"] else "INDEPENDENT_DIAGNOSIS_DISCREPANCY",
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "longdouble_nmant": int(np.finfo(R).nmant)},
        "derivative_algorithm": "actual-node barycentric first and second derivative rows; declared contrasts 7/9/11 points and 501/1001/2001 nodes; no Fornberg/source-equation import",
        "polynomial_control": control, "cases": cases, "conformal_replays": replays,
        "source_and_input_sha256": before, "inputs_unchanged": True,
        "scope": "Preserve the frozen central fine direct-metric gate failure. Alternate stencil/stride contrasts are diagnostic only. Conformal central mode replays do not qualify the uncomputed eight parameter points or supply a rigorous eigenvalue enclosure."}
    print(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
