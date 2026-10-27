"""Check saved mode samples with local-polynomial derivatives, not ODE RHS.

This verifier does not import stability.py, solve an eigenproblem, integrate
the mode, or use the saved p/constraint arrays to supply equation derivatives.
Its input and own source hashes are recorded separately from CONTRACT.json.
"""
from pathlib import Path
import hashlib
import json
import math
import platform
import time

import numpy as np

BASE = Path(__file__).resolve().parents[1]
BACKGROUND = (BASE.parent / "capture-to-model-2026-09-12" /
              "static-background-successor/proper-shooting/narrow-gap" /
              "fine-collocation/results/arrays.npz")
PROFILE = BASE / "results/shoot_tight.npz"
METADATA = BASE / "results/shoot_tight.json"
OUTPUT = BASE / "results/INDEPENDENT_MODE_CHECK.json"
REAL = np.longdouble
M2 = REAL("0.41")
GAMMA = REAL("20")
GATE = 1e-6


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def authenticate():
    contract = json.loads((BASE / "CONTRACT.json").read_text())
    for filename, expected in contract["bound_files"].items():
        path = Path(filename)
        if not path.is_absolute():
            path = BASE / path
        if sha(path) != expected:
            raise RuntimeError(f"Frozen input hash mismatch: {filename}")
    if contract["model"]["m2"] != .41 or contract["model"]["gamma"] != 20:
        raise RuntimeError("Model differs from independent verifier specification")


def weights(nodes, order=2):
    """Fornberg recursion at zero; all arithmetic uses Linux longdouble."""
    n = len(nodes)
    c = np.zeros((n, order + 1), dtype=REAL)
    c[0, 0] = 1
    c1 = REAL(1)
    c4 = nodes[0]
    for i in range(1, n):
        maximum = min(i, order)
        c2 = REAL(1)
        c5 = c4
        c4 = nodes[i]
        for j in range(i):
            c3 = nodes[i] - nodes[j]
            c2 *= c3
            if j == i - 1:
                for k in range(maximum, 0, -1):
                    c[i, k] = c1 * (k * c[i - 1, k - 1] - c5 * c[i - 1, k]) / c2
                c[i, 0] = -c1 * c5 * c[i - 1, 0] / c2
            for k in range(maximum, 0, -1):
                c[j, k] = (c4 * c[j, k] - k * c[j, k - 1]) / c3
            c[j, 0] = c4 * c[j, 0] / c3
        c1 = c2
    return c


def differentiate(z, values, stencil):
    """Derivatives of degree stencil-1 interpolants, one-sided at endpoints."""
    n = len(z)
    first = np.empty_like(values)
    second = np.empty_like(values)
    half = stencil // 2
    for i in range(n):
        start = max(0, min(i - half, n - stencil))
        section = slice(start, start + stencil)
        x = z[section] - z[i]
        scale = (z[start + stencil - 1] - z[start]) / (stencil - 1)
        nodes = x / scale
        w = weights(nodes)
        y = values[section] - values[i]
        first[i] = np.dot(w[:, 1], y) / scale
        # Removing an exact linear function improves cancellation; its second
        # derivative is zero. The slope is measured from the saved samples.
        slope = (y[-1] - y[0]) / (nodes[-1] - nodes[0])
        second[i] = np.dot(w[:, 2], y - slope * nodes) / scale**2
    return first, second


def background(z, raw):
    """Evaluate inherited piecewise polynomials by independent Horner code."""
    length = REAL(float(np.exp(raw["parameters"][0])))
    u = z / length
    mesh = np.asarray(raw["mesh"], dtype=REAL)
    coeff = np.asarray(raw["poly_coefficients"], dtype=REAL)
    index = np.clip(np.searchsorted(mesh, u, side="right") - 1, 0, len(mesh) - 2)
    dx = u - mesh[index]
    result = coeff[0, index, :].copy()
    for row in coeff[1:]:
        result = result * dx[:, None] + row[index, :]
    W, A, phi, S = result.T
    a = np.exp(W)
    return a, A, phi, S


def residual(terms, z):
    value = sum(terms)
    scale = 1 + sum(abs(t) for t in terms)
    normalized = abs(value) / scale
    index = int(np.argmax(normalized))
    return {"normalized_max": float(normalized[index]),
            "absolute_max": float(np.max(abs(value))),
            "worst_z": float(z[index]), "all_points_including_endpoints": True}


def simpson(y, z):
    if len(z) % 2 != 1:
        raise ValueError("Composite Simpson requires an odd sample count")
    h = (z[-1] - z[0]) / (len(z) - 1)
    if np.max(abs(np.diff(z) - h)) > REAL("1e-12") * h:
        raise ValueError("Saved nodes are not adequately uniform")
    return h / 3 * (y[0] + y[-1] + 4 * sum(y[1:-1:2]) + 2 * sum(y[2:-1:2]))


def check_case(profile, raw, mu, k, stride, stencil):
    z = np.asarray(profile["z"][::stride], dtype=REAL)
    psi = np.asarray(profile["psi"][::stride], dtype=REAL)
    f = np.asarray(profile["f"][::stride], dtype=REAL)
    stored_p = np.asarray(profile["p"][::stride], dtype=REAL)
    psip, _ = differentiate(z, psi, stencil)
    fp, fpp = differentiate(z, f, stencil)
    a, A, phi, S = background(z, raw)
    Vp = a*a*M2*phi
    B = Vp - 4*A*S
    mom = residual([psip, 2*A*psi, S*f/3], z)
    constraint = residual([S*fp, -B*f, (2*S*S - 3*mu - 12*k)*psi], z)
    kg = residual([fpp, 3*A*fp, (mu - a*a*M2)*f, 6*S*psip, 4*Vp*psi], z)
    walls = []
    for index, sign in [(0, 1), (-1, -1)]:
        terms = [fp[index], 2*S[index]*psi[index], -sign*a[index]*GAMMA*f[index]/2]
        walls.append({"signed_absolute": float(sum(terms)),
                      "normalized": float(abs(sum(terms)) / (1 + sum(abs(t) for t in terms)))})
    norm = 2*simpson(a**3*(f*f + 6*psi*psi), z)
    delta = -2*simpson(a*psi, z)
    # This is a secondary comparison; stored_p is never used for a derivative
    # in any Einstein, KG, or Robin residual above.
    derivative_agreement = residual([fp, -stored_p], z)
    maxima = [mom["normalized_max"], constraint["normalized_max"], kg["normalized_max"]]
    maxima.extend(w["normalized"] for w in walls)
    return {"stride": stride, "samples": len(z), "stencil_points": stencil,
            "polynomial_degree": stencil - 1, "momentum": mom,
            "einstein_constraint": constraint, "scalar_kg": kg, "walls": walls,
            "derived_fprime_vs_saved_p": derivative_agreement,
            "kinetic_Z": float(norm), "delta_D": float(delta),
            "delta_D_over_sqrt_Z": float(delta / np.sqrt(norm)),
            "maximum_equation_residual": max(maxima),
            "residual_gate_pass": max(maxima) <= GATE}


def polynomial_control():
    # Check first and second derivative formulas, including one-sided stencils,
    # against exact polynomials before differentiating any physical samples.
    z = np.linspace(0, 1, 33, dtype=REAL)
    y = z**7 - 2*z**3 + 3*z + 1
    yp = 7*z**6 - 6*z**2 + 3
    ypp = 42*z**5 - 12*z
    first, second = differentiate(z, y, 9)
    e1 = float(np.max(abs(first - yp)))
    e2 = float(np.max(abs(second - ypp)))
    return {"polynomial_degree": 7, "first_derivative_max_error": e1,
            "second_derivative_max_error": e2, "pass": max(e1, e2) < 1e-12}


def main():
    start = time.monotonic()
    authenticate()
    bound = [Path(__file__), BASE / "CONTRACT.json", PROFILE, METADATA, BACKGROUND]
    hashes = {str(p): sha(p) for p in bound}
    control = polynomial_control()
    if not control["pass"]:
        raise RuntimeError("Independent derivative control failed")
    metadata = json.loads(METADATA.read_text())
    mu = REAL(str(metadata["mu"]))
    raw = np.load(BACKGROUND, allow_pickle=False)
    k = REAL(raw["parameters"][1])
    profile = np.load(PROFILE, allow_pickle=False)
    cases = [check_case(profile, raw, mu, k, stride, 9) for stride in (4, 2, 1)]
    cases.append(check_case(profile, raw, mu, k, 1, 7))
    if hashes != {str(p): sha(p) for p in bound}:
        raise RuntimeError("An input changed during verification")
    finest = cases[2]
    output = {
        "method": "independent actual-sample Fornberg local polynomial derivatives",
        "source_and_input_sha256": hashes,
        "python": platform.python_version(), "numpy": np.__version__,
        "longdouble_nmant": int(np.finfo(REAL).nmant),
        "arithmetic_qualification": "extended evaluation of saved binary64 inputs; not new precision in input data",
        "primary_code_imported": False, "ode_rhs_used_as_derivative": False,
        "saved_p_used_in_equation_residuals": False,
        "normalization": "max abs(sum terms)/(1+sum abs(terms)); endpoint Robin has same normalization",
        "frozen_residual_gate": GATE, "mu": float(mu), "k": float(k),
        "derivative_control": control, "cases": cases,
        "finest_independent_residuals_pass": finest["residual_gate_pass"],
        "all_reported_discretizations_pass": all(case["residual_gate_pass"] for case in cases),
        "positive_kinetic_norm": finest["kinetic_Z"] > 0,
        "nonzero_separation_response": abs(finest["delta_D_over_sqrt_Z"]) > 1e-6,
        "relative_norm_difference_from_saved_receipt": abs(finest["kinetic_Z"] / metadata["kinetic_Z"] - 1),
        "relative_separation_difference_from_saved_receipt": abs(finest["delta_D"] / metadata["delta_D"] - 1),
        "scope": "Residual and physical-overlap verification of this saved mode only; no completeness claim, no independent eigenvalue solve",
        "elapsed_seconds": time.monotonic() - start,
    }
    temp = OUTPUT.with_suffix(".json.tmp")
    temp.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    temp.replace(OUTPUT)
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
