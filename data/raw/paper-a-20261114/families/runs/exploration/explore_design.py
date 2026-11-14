"""FLOAT EXPLORATION ONLY (binary64 RK4). Not a certificate.

Design numbers for a v1-segment family: float roots A(v1) at sub-box
endpoints and midpoints, the minimum of the upper Israel residual before the
event, finite-difference flow sensitivities dT/dA and dPhi/dA at the wall,
and the zero-mass lifted phase. Output is used only to fix the frozen boxes.
"""
import json
import math
import sys
from fractions import Fraction as Q

import explore_float as ef


def g_profile(A, p):
    H, T, k, Tp = ef.launch(A, p)
    y = [0.0, H, A, T, 1.0, 0.0, -2 * T]
    h = ef.S_END / ef.STEPS
    gmin_before = None
    s = 0.0
    for _ in range(ef.STEPS):
        y2 = ef.rk4(y, h, p, k, False)
        g2 = ef.F1(y2, p)
        if g2 <= 0:
            return gmin_before, s
        gmin_before = g2 if gmin_before is None else min(gmin_before, g2)
        y = y2
        s += h
    return gmin_before, None


def state_at(A, p, s_target):
    H, T, k, Tp = ef.launch(A, p)
    y = [0.0, H, A, T, 1.0, 0.0, -2 * T]
    n = 8192
    h = s_target / n
    for _ in range(n):
        y = ef.rk4(y, h, p, k, False)
    return y


def main():
    lo, hi, width = Q(sys.argv[1]), Q(sys.argv[2]), Q(sys.argv[3])
    part, parts = int(sys.argv[4]), int(sys.argv[5])
    base = {key: float(v) for key, v in ef.ANCHOR.items()}
    n = int((hi - lo) / width)
    pts = []
    for j in range(n + 1):
        pts.append(("edge", j, lo + j * width))
        if j < n:
            pts.append(("mid", j, lo + j * width + width / 2))
    pts = [x for i, x in enumerate(pts) if i % parts == part]
    rows = []
    seed = ef.A_ANCHOR
    for kind, j, v in pts:
        p = dict(base)
        p["v1"] = float(v)
        r = ef.root(p, seed)
        if r is None:
            rows.append({"kind": kind, "j": j, "v1": str(v), "result": None})
            continue
        seed = r["A"]
        gmin, _ = g_profile(r["A"], p)
        dA = 1e-9
        yp = state_at(r["A"] + dA, p, r["D"])
        ym = state_at(r["A"] - dA, p, r["D"])
        r["dT_dA_at_wall"] = (yp[3] - ym[3]) / (2 * dA)
        r["dPhi_dA_at_wall"] = (yp[2] - ym[2]) / (2 * dA)
        r["G_min_before_event"] = gmin
        rows.append({"kind": kind, "j": j, "v1": str(v), "result": r})
    print(json.dumps({"label": "FLOAT_EXPLORATION_NOT_A_CERTIFICATE", "rows": rows}))


if __name__ == "__main__":
    main()
