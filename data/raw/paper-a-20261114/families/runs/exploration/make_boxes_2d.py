"""DESIGN ONLY (binary64 float exploration). Frozen sub-box table for the 2-D box.

Box: v1 in [43/500, 1/10] x lambda_b in [-60529/10000, -60429/10000], cells of
1/1000 x 1/1000, other four parameters at the archived exact values.  For each
cell: float roots at the centre and the four corners; spread = largest corner
deviation from the centre root; predicted parametric-Newton half-width
Nest = (h_s*dDc/2 + 10*rho_v1)/|q'| with dDc = 2*rho*(|dD/dv1|_A + |dD/dlambda_b|_A)
+ 2 independent cells; r = 2.5*max(spread, Nest) + 5e-9 (same rule as V and L).
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


def main():
    part, parts = int(sys.argv[1]), int(sys.argv[2])
    base = {key: float(v) for key, v in ef.ANCHOR.items()}
    v_lo, v_hi, l_lo, l_hi, w = Q(43, 500), Q(1, 10), Q(-60529, 10000), Q(-60429, 10000), Q(1, 1000)
    nv, nl = int((v_hi - v_lo) / w), int((l_hi - l_lo) / w)
    cells = [(i, k) for k in range(nl) for i in range(nv)]
    cells = [c for n, c in enumerate(cells) if n % parts == part]
    rows = []
    seed = ef.A_ANCHOR
    for i, k in cells:
        va, vb = v_lo + i * w, v_lo + (i + 1) * w
        la, lb = l_lo + k * w, l_lo + (k + 1) * w
        pts = {"c": ((va + vb) / 2, (la + lb) / 2)}
        for tag, v, l in (("aa", va, la), ("ab", va, lb), ("ba", vb, la), ("bb", vb, lb)):
            pts[tag] = (v, l)
        roots = {}
        for tag, (v, l) in pts.items():
            p = dict(base)
            p["v1"], p["lambda_b"] = float(v), float(l)
            r = ef.root(p, seed)
            if r is None:
                roots = None
                break
            roots[tag] = (p, r)
            if tag == "c":
                seed = r["A"]
        if roots is None:
            rows.append({"i": i, "k": k, "error": "NO_FLOAT_ROOT"})
            continue
        p, r = roots["c"]
        A0 = r["A"]
        spread = max(abs(roots[t][1]["A"] - A0) for t in ("aa", "ab", "ba", "bb"))
        dA = 1e-10
        qprime = (q_at(A0 + dA, p) - q_at(A0 - dA, p)) / (2 * dA)
        H, T, k_, Tp = ef.launch(A0, p)
        Tb, Phib, warp = r["T_b"], r["Phi_b"], r["warp_b"]
        Hb = (p["lambda_b"] + p["gamma"] * (Phib - p["v1"]) ** 2 / 2) / 6
        Tpb = p["m2"] * Phib - 4 * Hb * Tb
        Gs = -Tb * Tb / 3 - k_ / warp ** 2 - p["gamma"] * (Phib - p["v1"]) * Tb / 6
        hs = Tpb + p["gamma"] * Tb / 2
        rho = float(w) / 2
        dDv = abs(p["gamma"] * (Phib - p["v1"]) / 6 / Gs)
        dDl = abs((1.0 / 6) / Gs)
        dDc = 2 * rho * (dDv + dDl) + 2 * CELL_INDEPENDENT
        nest = (abs(hs) * dDc / 2 + 10 * rho) / abs(qprime)
        radius = 2.5 * max(spread, nest) + 5e-9
        a_lo = math.nextafter(A0 - radius, -math.inf)
        a_hi = math.nextafter(A0 + radius, math.inf)
        tbs = [roots[t][1]["T_b"] for t in ("aa", "ab", "ba", "bb")]
        ds = [roots[t][1]["D"] for t in ("aa", "ab", "ba", "bb")]
        rows.append({"i": i, "k": k, "v1": [str(va), str(vb)], "lambda_b": [str(la), str(lb)],
                     "A0": repr(A0), "A_lo": repr(a_lo), "A_hi": repr(a_hi),
                     "float_design": {"spread": spread, "nest": nest, "radius": radius, "qprime": qprime,
                                      "T_b_min_corner": min(tbs), "D_max_corner": max(ds), "D_min_corner": min(ds),
                                      "theta_over_pi_centre": r["theta_over_pi"],
                                      "predicted_T_b_lower_bound": min(tbs) - 3.7e4 * radius}})
    print(json.dumps({"label": "FLOAT_DESIGN_NOT_A_CERTIFICATE", "rows": rows}))


if __name__ == "__main__":
    main()
