"""FLOAT EXPLORATION ONLY (binary64 RK4). Not a certificate.

Maps the quadratic-model shooting root A(p), wall distance D(p), slice
curvature k(p), endpoint scalar derivatives and the zero-mass lifted phase
theta_b/pi along one-parameter segments through the archived anchor.
Used only to choose a family design before pre-registration.
"""
import json
import math
import sys
from fractions import Fraction as Q

ANCHOR = {
    "m2": Q(7385903388887613, 18014398509481984),
    "gamma": Q(20),
    "v0": Q(3602879701896397, 36028797018963968),
    "v1": Q(6520040733916207, 72057594037927936),
    "lambda_a": Q(6755388606266369, 1125899906842624),
    "lambda_b": Q(-851862101055633, 140737488355328),
}
A_ANCHOR = 0.09901086589880687
STEPS = 8192
S_END = 2.0


def launch(A, p):
    g, v0, la, m2 = p["gamma"], p["v0"], p["lambda_a"], p["m2"]
    H = -(la + g * (A - v0) ** 2 / 2) / 6
    T = g * (A - v0) / 2
    k = H * H - 1 - T * T / 12 + m2 * A * A / 12
    Tp = m2 * A - 4 * H * T
    return H, T, k, Tp


def rhs(y, p, k, mode):
    W, H, P, T, psi, f, g = y
    m2 = p["m2"]
    e2 = math.exp(-2 * W)
    out = [H, -T * T / 3 - k * e2, T, m2 * P - 4 * H * T]
    if mode:
        out += [-2 * H * psi - T * f / 3, g,
                -4 * H * g + (m2 + 2 * T * T) * f + (12 * H * T - 4 * m2 * P) * psi]
    else:
        out += [0.0, 0.0, 0.0]
    return out


def rk4(y, h, p, k, mode):
    k1 = rhs(y, p, k, mode)
    k2 = rhs([a + h / 2 * b for a, b in zip(y, k1)], p, k, mode)
    k3 = rhs([a + h / 2 * b for a, b in zip(y, k2)], p, k, mode)
    k4 = rhs([a + h * b for a, b in zip(y, k3)], p, k, mode)
    return [a + h / 6 * (b + 2 * c + 2 * d + e) for a, b, c, d, e in zip(y, k1, k2, k3, k4)]


def F1(y, p):
    tau_b = p["lambda_b"] + p["gamma"] * (y[2] - p["v1"]) ** 2 / 2
    return y[1] - tau_b / 6


def F2(y, p):
    return y[3] + p["gamma"] * (y[2] - p["v1"]) / 2


def angle(y):
    psi, f, g, T = y[4], y[5], y[6], y[3]
    L = g + 2 * T * psi
    return math.atan2(f, L)


def shoot(A, p, mode=False):
    H, T, k, Tp = launch(A, p)
    y = [0.0, H, A, T, 1.0, -12 * k / Tp if mode else 0.0, -2 * T]
    h = S_END / STEPS
    s = 0.0
    theta = 1.5 * math.pi
    prev = angle(y) if mode else 0.0
    if F1(y, p) <= 0:
        return None
    for _ in range(STEPS):
        y2 = rk4(y, h, p, k, mode)
        if F1(y2, p) <= 0:
            lo, hi = 0.0, h
            for _ in range(60):
                mid = (lo + hi) / 2
                if F1(rk4(y, mid, p, k, mode), p) > 0:
                    lo = mid
                else:
                    hi = mid
            t = (lo + hi) / 2
            ye = rk4(y, t, p, k, mode)
            if mode:
                a = angle(ye)
                d = (a - prev + math.pi) % (2 * math.pi) - math.pi
                theta += d
            return {"D": s + t, "q": F2(ye, p), "T_b": ye[3], "Phi_b": ye[2], "warp_b": math.exp(ye[0]),
                    "k": k, "T_a": T, "Tp_a": Tp, "theta_over_pi": theta / math.pi if mode else None}
        if mode:
            a = angle(y2)
            d = (a - prev + math.pi) % (2 * math.pi) - math.pi
            theta += d
            prev = a
        y = y2
        s += h
    return None


def root(p, A0):
    A1 = A0 * (1 + 1e-9)
    r0, r1 = shoot(A0, p), shoot(A1, p)
    if r0 is None or r1 is None:
        return None
    q0, q1 = r0["q"], r1["q"]
    for _ in range(40):
        if q1 == q0:
            break
        A2 = A1 - q1 * (A1 - A0) / (q1 - q0)
        A0, q0 = A1, q1
        A1 = A2
        r = shoot(A1, p)
        if r is None:
            return None
        q1 = r["q"]
        if abs(A1 - A0) < 1e-17:
            break
    out = shoot(A1, p, mode=True)
    if out is None:
        return None
    out["A"] = A1
    out["dqdA"] = (q1 - q0) / (A1 - A0) if A1 != A0 else None
    return out


def main():
    name = sys.argv[1]
    lo, hi, n = float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    base = {key: float(v) for key, v in ANCHOR.items()}
    rows = []
    A = A_ANCHOR
    values = [lo + (hi - lo) * i / (n - 1) for i in range(n)]
    anchor_value = base[name]
    order = sorted(range(n), key=lambda i: abs(values[i] - anchor_value))
    seeds = {}
    for i in order:
        p = dict(base)
        p[name] = values[i]
        nearest = min(seeds, key=lambda j: abs(values[j] - values[i])) if seeds else None
        A0 = seeds[nearest] if nearest is not None else A_ANCHOR
        r = root(p, A0)
        if r is not None:
            seeds[i] = r["A"]
        rows.append((i, values[i], r))
    rows.sort()
    out = []
    for i, v, r in rows:
        out.append({"param": name, "value": v, "result": r})
        if r is None:
            print(f"{name}={v:.10g}: NO ROOT")
        else:
            print(f"{name}={v:.10g}: A={r['A']:.15g} D={r['D']:.10g} k={r['k']:.6g} "
                  f"Ta={r['T_a']:.4g} Tb={r['T_b']:.4g} Tpa={r['Tp_a']:.4g} th/pi={r['theta_over_pi']:.6f} "
                  f"q={r['q']:.2e} dqdA={r['dqdA']}")
    print(json.dumps({"label": "FLOAT_EXPLORATION_NOT_A_CERTIFICATE", "rows": out}))


if __name__ == "__main__":
    main()
