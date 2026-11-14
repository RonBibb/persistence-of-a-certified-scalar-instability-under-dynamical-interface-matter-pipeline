"""DESIGN ONLY (binary64 float exploration). Writes the frozen sub-box table.

For each sub-box P_j of a one-parameter segment (parameter v1 or lambda_b,
other five parameters at the archived exact values) this computes, in
binary64 RK4 (not a certificate):
  A0_j   float shooting root at the sub-box midpoint,
  spread largest |A(edge) - A0_j| over the two edges,
  Nest   predicted half-width of the parametric interval-Newton image,
         (h_s*dDc/2 + |dh/dp|*rho)/|q'|, dDc = 2*rho*|dD/dp|_A + 2 cells,
  r_j    = 2.5*max(spread, Nest) + 5e-9   (the frozen rule),
and the A-box [A0_j - r_j, A0_j + r_j] rounded outward to binary64.
Predicted enclosure margins are reported for the design record only.
"""
import json
import math
import sys
from fractions import Fraction as Q

import explore_float as ef

CELL_INDEPENDENT = 2 / 8192


def q_at(A, p):
    r = ef.shoot(A, p)
    return None if r is None else r["q"]


def wall_data(A, p):
    H, T, k, Tp = ef.launch(A, p)
    r = ef.shoot(A, p)
    return r, k


def design(param, lo, hi, width, rows_out):
    base = {key: float(v) for key, v in ef.ANCHOR.items()}
    n = round((hi - lo) / width)
    assert lo + n * width == hi
    seed = ef.A_ANCHOR
    anchor_value = ef.ANCHOR[param]
    order = sorted(range(n), key=lambda j: abs(float(lo + j * width + width / 2) - float(anchor_value)))
    seeds = {}
    results = {}
    for j in order:
        a, b = lo + j * width, lo + (j + 1) * width
        mid = (a + b) / 2
        near = min(seeds, key=lambda i: abs(i - j)) if seeds else None
        s0 = seeds[near] if near is not None else ef.A_ANCHOR
        vals = {}
        for tag, v in (("lo", a), ("mid", mid), ("hi", b)):
            p = dict(base)
            p[param] = float(v)
            r = ef.root(p, s0)
            if r is None:
                vals = None
                break
            vals[tag] = (p, r)
        if vals is None:
            results[j] = {"j": j, "param": param, "lo": str(a), "hi": str(b), "error": "NO_FLOAT_ROOT"}
            continue
        p, r = vals["mid"]
        A0 = r["A"]
        seeds[j] = A0
        spread = max(abs(vals["lo"][1]["A"] - A0), abs(vals["hi"][1]["A"] - A0))
        dA = 1e-10
        qp, qm = q_at(A0 + dA, p), q_at(A0 - dA, p)
        qprime = (qp - qm) / (2 * dA)
        H, T, k, Tp = ef.launch(A0, p)
        Tb, Phib, warp = r["T_b"], r["Phi_b"], r["warp_b"]
        Hb = (p["lambda_b"] + p["gamma"] * (Phib - p["v1"]) ** 2 / 2) / 6
        Tpb = p["m2"] * Phib - 4 * Hb * Tb
        Hpb = -Tb * Tb / 3 - k / warp ** 2
        Gs = Hpb - p["gamma"] * (Phib - p["v1"]) * Tb / 6
        hs = Tpb + p["gamma"] * Tb / 2
        if param == "v1":
            dF1dp = p["gamma"] * (Phib - p["v1"]) / 6
            dhdp = -p["gamma"] / 2
        else:
            dF1dp = -1.0 / 6
            dhdp = 0.0
        rho = float(width) / 2
        dDdp_A = abs(dF1dp / Gs)
        dDc = 2 * rho * dDdp_A + 2 * CELL_INDEPENDENT
        nest = (abs(hs) * dDc / 2 + abs(dhdp) * rho) / abs(qprime)
        radius = 2.5 * max(spread, nest) + 5e-9
        a_lo = A0 - radius
        a_hi = A0 + radius
        a_lo = math.nextafter(a_lo, -math.inf)
        a_hi = math.nextafter(a_hi, math.inf)
        results[j] = {
            "j": j, "param": param, "lo": str(a), "hi": str(b),
            "A0": repr(A0), "A_lo": repr(a_lo), "A_hi": repr(a_hi),
            "float_design": {
                "spread": spread, "newton_halfwidth_estimate": nest, "radius": radius,
                "qprime": qprime, "Gs": Gs, "hs": hs, "dDdp_at_fixed_A": dDdp_A,
                "T_b_mid": Tb, "T_b_lo": vals["lo"][1]["T_b"], "T_b_hi": vals["hi"][1]["T_b"],
                "D_mid": r["D"], "D_lo": vals["lo"][1]["D"], "D_hi": vals["hi"][1]["D"],
                "k_mid": k, "theta_over_pi_mid": r["theta_over_pi"],
                "predicted_T_b_lower_bound": min(vals["lo"][1]["T_b"], vals["hi"][1]["T_b"]) - 3.7e4 * radius,
            },
        }
    for j in range(n):
        rows_out.append(results[j])


def main():
    rows = []
    which = sys.argv[1]
    if which == "V":
        design("v1", Q(43, 500), Q(3, 20), Q(1, 1000), rows)
    else:
        design("lambda_b", Q(-60529, 10000), Q(-60229, 10000), Q(1, 1000), rows)
    print(json.dumps({"label": "FLOAT_DESIGN_NOT_A_CERTIFICATE", "family": which, "rows": rows}, indent=1))


if __name__ == "__main__":
    main()
