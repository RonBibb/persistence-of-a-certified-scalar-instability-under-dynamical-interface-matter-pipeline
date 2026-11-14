#!/usr/bin/env python3
"""Float-exploratory radial scalar counts for Paper A's separated system (10).  v2.

Every number this program prints is FLOAT EXPLORATORY (IEEE double, fixed-step
RK4).  Nothing here is an interval certificate.

Usage:  python3 -I flatcount.py CASE_ID OUT_JSON [--dry]
CASE_ID in {DS, F1, F1b, F3, F0}.  --dry writes a REDACTED flag-only record
(no counts, eigenvalues, characteristic values or endpoint phases).
"""
import json
import math
import sys
import time
from fractions import Fraction as Fr

DELTA = 1e-6
BIG = 1e8

# ----------------------------------------------------------------- potentials


class Quadratic:
    """V = c0 + c2 * Phi^2."""

    def __init__(self, c0, c2):
        self.c0 = float(c0)
        self.c2 = float(c2)

    def V(self, p):
        return self.c0 + self.c2 * p * p

    def dV(self, p):
        return 2.0 * self.c2 * p

    def d2V(self, p):
        return 2.0 * self.c2


# ----------------------------------------------------------------- background


def bg_rhs(y, k, pot):
    W, H, P, T = y
    return (H, -T * T / 3.0 - k * math.exp(-2.0 * W), T, pot.dV(P) - 4.0 * H * T)


def rk4(rhs, y, h, *args):
    k1 = rhs(y, *args)
    y2 = tuple(a + 0.5 * h * b for a, b in zip(y, k1))
    k2 = rhs(y2, *args)
    y3 = tuple(a + 0.5 * h * b for a, b in zip(y, k2))
    k3 = rhs(y3, *args)
    y4 = tuple(a + h * b for a, b in zip(y, k3))
    k4 = rhs(y4, *args)
    return tuple(a + h / 6.0 * (b + 2.0 * c + 2.0 * d + e)
                 for a, b, c, d, e in zip(y, k1, k2, k3, k4))


def bad_state(y):
    return (not all(math.isfinite(v) for v in y)) or max(abs(v) for v in y) > BIG


def constraint_residual(y, k, pot):
    W, H, P, T = y
    e2 = math.exp(-2.0 * W)
    V = pot.V(P)
    r = H * H - 1.0 - T * T / 12.0 + V / 6.0 - k * e2
    scale = max(1.0, H * H, T * T / 12.0, abs(V) / 6.0, abs(k) * e2)
    return abs(r) / scale


def pre_scan(y0, k, pot, smax=6.0, nsteps=24000):
    """First s at which the RK4 pre-integration leaves the finite/bounded region."""
    h = smax / nsteps
    y = y0
    for i in range(nsteps):
        y = rk4(bg_rhs, y, h, k, pot)
        if bad_state(y):
            return (i + 1) * h
    return None


def find_event(y0, k, pot, smax, nsteps, func, after=0.0, which=1):
    """s of the `which`-th strict sign change of func(y) in steps starting at s >= after.

    Stops (returns None) at the first non-finite or |state| > 1e8 value.
    Refined by bisection on the step length to 1e-12.
    """
    h = smax / nsteps
    y = y0
    s = 0.0
    g_prev = func(y)
    count = 0
    for i in range(nsteps):
        y_new = rk4(bg_rhs, y, h, k, pot)
        if bad_state(y_new):
            return None, None
        s_new = (i + 1) * h
        g_new = func(y_new)
        if s >= after and g_prev * g_new < 0.0:
            count += 1
            if count == which:
                lo, hi = 0.0, h
                for _ in range(200):
                    mid = 0.5 * (lo + hi)
                    gm = func(rk4(bg_rhs, y, mid, k, pot))
                    if gm * g_prev < 0.0:
                        hi = mid
                    else:
                        lo = mid
                    if hi - lo <= 1e-12:
                        break
                tau = 0.5 * (lo + hi)
                return s + tau, rk4(bg_rhs, y, tau, k, pot)
        y, s, g_prev = y_new, s_new, g_new
    return None, None


class Background:
    """Background on a half-step grid for perturbation step h = D/N."""

    def __init__(self, y0, k, pot, D, N):
        self.k = k
        self.pot = pot
        self.D = D
        self.N = N
        M = 2 * N
        hh = D / M
        ys = [y0]
        y = y0
        for _ in range(M):
            y = rk4(bg_rhs, y, hh, k, pot)
            ys.append(y)
        self.finite = not any(bad_state(v) for v in ys)
        self.ys = ys
        self.h = D / N
        self.H = [v[1] for v in ys]
        self.T = [v[3] for v in ys]
        self.a2 = [math.exp(2.0 * v[0]) for v in ys]
        self.a = [math.exp(v[0]) for v in ys]
        self.Tp = [pot.dV(v[2]) - 4.0 * v[1] * v[3] for v in ys]
        self.Q = [pot.d2V(v[2]) + 4.0 * k * math.exp(-2.0 * v[0]) + 4.0 * v[3] * v[3] / 3.0 for v in ys]
        self.Qm0 = [pot.d2V(v[2]) + 4.0 * v[3] * v[3] / 3.0 for v in ys]
        self.max_constraint = max(constraint_residual(v, k, pot) for v in ys)
        self.maxabsQ = max(abs(q) for q in self.Q)
        self.mina2 = min(self.a2)

    def nu_h(self, mu):
        return math.sqrt(self.maxabsQ + abs(mu) / self.mina2) * self.h

    def coop_bound(self):
        """max_s x_s, x_s = a^2(-Q + sqrt(Q^2 + 8T'^2/3))/2 (audit A9 step 2)."""
        best = 0.0
        for a2, Q, Tp in zip(self.a2, self.Q, self.Tp):
            best = max(best, a2 * (-Q + math.sqrt(Q * Q + 8.0 * Tp * Tp / 3.0)) / 2.0)
        return best

    def zeros_of_T(self):
        return [i for i in range(len(self.T) - 1) if self.T[i] == 0.0 or self.T[i] * self.T[i + 1] < 0.0]

    def vartheta_D(self):
        """Continuous lift of arg(T' + iT) from atan2(T_a, T'_a) to s = D."""
        th = math.atan2(self.T[0], self.Tp[0])
        maxjump = 0.0
        for i in range(1, len(self.T)):
            new = math.atan2(self.T[i], self.Tp[i])
            d = new - math.atan2(math.sin(th), math.cos(th))
            while d > math.pi:
                d -= 2.0 * math.pi
            while d <= -math.pi:
                d += 2.0 * math.pi
            th += d
            maxjump = max(maxjump, abs(d))
        return th, maxjump


# --------------------------------------------------------------- perturbation


def launch(bg, mu, ta):
    """(K4) launch, psi_a = 1; theta_a from the launch direction (not signed zeros)."""
    lam = mu + 4.0 * bg.k
    Ta, Tpa, a2a = bg.T[0], bg.Tp[0], bg.a2[0]
    ja = -(1.0 - ta) / 2.0
    Ea = ta * Tpa + ja * Ta
    if Ea == 0.0:
        raise ZeroDivisionError("E_a = 0 (massless-radion wall value)")
    x = (1.0, -3.0 * lam * ta / (a2a * Ea), 3.0 * lam * ja / (a2a * Ea))
    base = math.atan2(ta, -ja)  # direction (t_a, -j_a), in [0, pi/2]
    theta_a = base if (lam / Ea) < 0.0 else base + math.pi
    return x, Ea, theta_a


def _rhs_factory(bg, mu):
    H, T, Tp, a2, Qm0 = bg.H, bg.T, bg.Tp, bg.a2, bg.Qm0

    def rhs(xx, i):
        psi, f, L = xx
        return (-2.0 * H[i] * psi - T[i] * f / 3.0,
                L - 2.0 * T[i] * psi,
                -4.0 * H[i] * L + (Qm0[i] - mu / a2[i]) * f - 2.0 * Tp[i] * psi)
    return rhs


def _wrap(d):
    while d > math.pi:
        d -= 2.0 * math.pi
    while d <= -math.pi:
        d += 2.0 * math.pi
    return d


class NonFinite(Exception):
    pass


FINE_LEVELS = 12  # finest phase sub-step h / 2**12 (post-freeze G6 fix; CHANGELOG)


def _fine_background(bg, n):
    """Background states on [s_n, s_n + h] at spacing h / 2**(FINE_LEVELS + 1), RK4 from the stored grid point."""
    M = 2 ** (FINE_LEVELS + 1)
    hh = bg.h / M
    y = bg.ys[2 * n]
    ys = [y]
    for _ in range(M):
        y = rk4(bg_rhs, y, hh, bg.k, bg.pot)
        ys.append(y)
    pot = bg.pot
    return [(v[1], v[3], pot.dV(v[2]) - 4.0 * v[1] * v[3], math.exp(2.0 * v[0]),
             pot.d2V(v[2]) + 4.0 * v[3] * v[3] / 3.0) for v in ys]


def _refine_phase(bg, mu, x0, n):
    """Phase increments across step n, by recursive halving until every increment is < pi/4
    (or the finest level is reached).  The state used for the characteristic is NOT changed.
    Returns (list_of_increments, depth_used)."""
    fb = _fine_background(bg, n)
    top = 2 ** (FINE_LEVELS + 1)

    def rhs(xx, idx):
        H, T, Tp, a2, Qm0 = fb[idx]
        psi, f, L = xx
        return (-2.0 * H * psi - T * f / 3.0, L - 2.0 * T * psi, -4.0 * H * L + (Qm0 - mu / a2) * f - 2.0 * Tp * psi)

    def step(x, i0, i2, hsub):
        i1 = (i0 + i2) // 2
        k1 = rhs(x, i0)
        xa = tuple(p + 0.5 * hsub * q for p, q in zip(x, k1))
        k2 = rhs(xa, i1)
        xb = tuple(p + 0.5 * hsub * q for p, q in zip(x, k2))
        k3 = rhs(xb, i1)
        xc = tuple(p + hsub * q for p, q in zip(x, k3))
        k4 = rhs(xc, i2)
        return tuple(p + hsub / 6.0 * (q + 2.0 * r + 2.0 * s + t) for p, q, r, s, t in zip(x, k1, k2, k3, k4))

    incs = []
    deepest = [0]

    def rec(x, i0, i2, depth):
        hsub = bg.h * (i2 - i0) / top
        x_end = step(x, i0, i2, hsub)
        d = _wrap(math.atan2(x_end[1], x_end[2]) - math.atan2(x[1], x[2]))
        if abs(d) < math.pi / 4.0 or (i2 - i0) <= 2:
            incs.append(d)
            deepest[0] = max(deepest[0], depth)
            return x_end
        mid = (i0 + i2) // 2
        xm = rec(x, i0, mid, depth + 1)
        return rec(xm, mid, i2, depth + 1)

    rec(x0, 0, top, 0)
    return incs, deepest[0]


def shoot(bg, mu, ta, tb, phase=False, quadrant_check=False):
    """Forward integration of the lower-admissible solution to s = D."""
    lam = mu + 4.0 * bg.k
    h = bg.h
    x, Ea, theta_a = launch(bg, mu, ta)
    rhs = _rhs_factory(bg, mu)
    theta = theta_a
    max_dtheta = 0.0
    first = {}
    quad_ok = True
    f_launch = x[1]
    L_launch = x[2]
    n_refined = 0
    max_discrepancy = 0.0
    max_depth = 0
    for n in range(bg.N):
        x_prev = x
        i0 = 2 * n
        k1 = rhs(x, i0)
        xa = (x[0] + 0.5 * h * k1[0], x[1] + 0.5 * h * k1[1], x[2] + 0.5 * h * k1[2])
        k2 = rhs(xa, i0 + 1)
        xb = (x[0] + 0.5 * h * k2[0], x[1] + 0.5 * h * k2[1], x[2] + 0.5 * h * k2[2])
        k3 = rhs(xb, i0 + 1)
        xc = (x[0] + h * k3[0], x[1] + h * k3[1], x[2] + h * k3[2])
        k4 = rhs(xc, i0 + 2)
        x = (x[0] + h / 6.0 * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
             x[1] + h / 6.0 * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]),
             x[2] + h / 6.0 * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]))
        m = max(abs(x[0]), abs(x[1]), abs(x[2]))
        if not math.isfinite(m):
            raise NonFinite(f"non-finite state at step {n}, mu={mu}")
        if m > 1e100:
            x = (x[0] / m, x[1] / m, x[2] / m)
        if phase:
            d = _wrap(math.atan2(x[1], x[2]) - math.atan2(math.sin(theta), math.cos(theta)))
            step_max = abs(d)
            if abs(d) >= math.pi / 4.0:
                incs, depth = _refine_phase(bg, mu, x_prev, n)
                d_ref = sum(incs)
                max_discrepancy = max(max_discrepancy, abs(d_ref - d))
                max_depth = max(max_depth, depth)
                n_refined += 1
                d = d_ref
                step_max = max(abs(v) for v in incs)
            theta += d
            if n == 0:
                first = {"first_dtheta": abs(d), "f_launch": f_launch, "L_launch": L_launch,
                         "f_h": x[1], "L_h": x[2], "theta_h_mod_2pi": theta % (2.0 * math.pi)}
            else:
                max_dtheta = max(max_dtheta, step_max)
        if quadrant_check and not (x[1] * x[2] > 0.0):
            quad_ok = False
    psi, f, L = x
    iN = 2 * bg.N
    char = tb * L + (1.0 - tb) / 2.0 * f
    C = bg.T[iN] * L - bg.Tp[iN] * f - 3.0 * lam * psi / bg.a2[iN]
    Cn = (abs(bg.T[iN]) + abs(bg.Tp[iN]) + 3.0 * abs(lam) / bg.a2[iN]) * (abs(psi) + abs(f) + abs(L))
    if not math.isfinite(char):
        raise NonFinite(f"non-finite characteristic, mu={mu}")
    out = {"char": char, "constraint_rel": abs(C) / Cn, "nu_h": bg.nu_h(mu)}
    if phase:
        out.update({"theta_a": theta_a, "theta_b": theta, "max_dtheta": max_dtheta,
                    "n_refined_steps": n_refined, "max_refine_discrepancy": max_discrepancy,
                    "max_refine_depth": max_depth})
        out.update(first)
    if quadrant_check:
        out["quadrant_ok"] = quad_ok
    return out


def shoot_back(bg, mu, ta, tb):
    """Backward integration of the upper-admissible solution; residual at the lower wall."""
    lam = mu + 4.0 * bg.k
    h = bg.h
    iN = 2 * bg.N
    jb = (1.0 - tb) / 2.0
    Eb = tb * bg.Tp[iN] + jb * bg.T[iN]
    if Eb == 0.0:
        raise ZeroDivisionError("E_b = 0 (massless-radion wall value)")
    a2b = bg.a2[iN]
    x = (1.0, -3.0 * lam * tb / (a2b * Eb), 3.0 * lam * jb / (a2b * Eb))
    rhs = _rhs_factory(bg, mu)
    for n in range(bg.N - 1, -1, -1):
        i2 = 2 * n + 2
        k1 = rhs(x, i2)
        xa = (x[0] - 0.5 * h * k1[0], x[1] - 0.5 * h * k1[1], x[2] - 0.5 * h * k1[2])
        k2 = rhs(xa, i2 - 1)
        xb = (x[0] - 0.5 * h * k2[0], x[1] - 0.5 * h * k2[1], x[2] - 0.5 * h * k2[2])
        k3 = rhs(xb, i2 - 1)
        xc = (x[0] - h * k3[0], x[1] - h * k3[1], x[2] - h * k3[2])
        k4 = rhs(xc, i2 - 2)
        x = (x[0] - h / 6.0 * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
             x[1] - h / 6.0 * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]),
             x[2] - h / 6.0 * (k1[2] + 2.0 * k2[2] + 2.0 * k3[2] + k4[2]))
        m = max(abs(x[0]), abs(x[1]), abs(x[2]))
        if not math.isfinite(m):
            raise NonFinite(f"non-finite backward state, mu={mu}")
        if m > 1e100:
            x = (x[0] / m, x[1] / m, x[2] / m)
    ja = -(1.0 - ta) / 2.0
    return ta * x[2] + ja * x[1]


def ls_shoot(bg, mu, ta, tb):
    """Lesgourgues-Sorbo / KOS flat system (proper distance), monotonic T only."""
    h = bg.h
    H, T, Tp, a = bg.H, bg.T, bg.Tp, bg.a
    ca = a[0] * ((1.0 - ta) / 2.0 - ta * Tp[0] / T[0])
    x = (1.0, -ta * mu / ca)

    def rhs(xx, i):
        Psi, Pi = xx
        return (Pi / a[i] - 2.0 * H[i] * Psi,
                (H[i] + 2.0 * Tp[i] / T[i]) * Pi + (-mu / a[i] + (2.0 / 3.0) * a[i] * T[i] * T[i]) * Psi)

    for n in range(bg.N):
        i0 = 2 * n
        k1 = rhs(x, i0)
        xa = (x[0] + 0.5 * h * k1[0], x[1] + 0.5 * h * k1[1])
        k2 = rhs(xa, i0 + 1)
        xb = (x[0] + 0.5 * h * k2[0], x[1] + 0.5 * h * k2[1])
        k3 = rhs(xb, i0 + 1)
        xc = (x[0] + h * k3[0], x[1] + h * k3[1])
        k4 = rhs(xc, i0 + 2)
        x = (x[0] + h / 6.0 * (k1[0] + 2.0 * k2[0] + 2.0 * k3[0] + k4[0]),
             x[1] + h / 6.0 * (k1[1] + 2.0 * k2[1] + 2.0 * k3[1] + k4[1]))
        m = max(abs(x[0]), abs(x[1]))
        if not math.isfinite(m):
            raise NonFinite("non-finite LS state")
        if m > 1e100:
            x = (x[0] / m, x[1] / m)
    iN = 2 * bg.N
    cb = a[iN] * (-tb * Tp[iN] / T[iN] - (1.0 - tb) / 2.0)
    return cb * x[1] + tb * mu * x[0]


# -------------------------------------------------------------------- counting


def linspace(a, b, m):
    """m points with the endpoints exactly a and b."""
    return [a] + [a + (b - a) * i / (m - 1) for i in range(1, m - 1)] + [b]


GRID_N = 300  # per sub-grid; reduced to 200 by the pre-registered timing rule (--grid200)


def merged_grid(bg, lam_abs_min):
    """Uniform in mu on [mu_min, mu_top] union uniform in log|lambda| on [DELTA, lam_abs_min];
    endpoints mu_min and mu_top are included exactly."""
    k4 = 4.0 * bg.k
    mu_min, mu_top = -k4 - lam_abs_min, -k4 - DELTA
    g = set(linspace(mu_min, mu_top, GRID_N))
    la, lb = math.log(lam_abs_min), math.log(DELTA)
    for i in range(1, GRID_N - 1):
        g.add(-k4 - math.exp(la + (lb - la) * i / (GRID_N - 1)))
    g = sorted(v for v in g if mu_min <= v <= mu_top)
    return g


def sign_changes(vals):
    idx = [i for i in range(len(vals) - 1) if vals[i] * vals[i + 1] < 0.0]
    zero = any(v == 0.0 for v in vals)
    return idx, zero


def bisect(func, lo, hi, flo):
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        fm = func(mid)
        if fm * flo < 0.0:
            hi = mid
        else:
            lo, flo = mid, fm
        if hi - lo <= 1e-11 * max(1.0, abs(mid)):
            break
    return 0.5 * (lo + hi)


def scan(func, grid, refine=True, nested=True):
    vals = [func(mu) for mu in grid]
    idx, zero = sign_changes(vals)
    roots = [bisect(func, grid[i], grid[i + 1], vals[i]) for i in idx] if refine else []
    res = {"count": len(idx), "roots": roots, "exact_zero": zero, "vals": vals}
    if nested:
        fine = []
        for i in range(len(grid) - 1):
            fine.append(vals[i])
            fine.append(func(0.5 * (grid[i] + grid[i + 1])))
        fine.append(vals[-1])
        idx2, zero2 = sign_changes(fine)
        res["count_nested"] = len(idx2)
        res["exact_zero"] = zero or zero2
    return res


def targets_between(th_lo, th_hi, theta_t):
    jmin = math.floor((th_lo - theta_t) / math.pi) + 1
    jmax = math.ceil((th_hi - theta_t) / math.pi) - 1
    cnt = max(0, jmax - jmin + 1)

    def dist(th):
        r = (th - theta_t) / math.pi
        return abs(r - round(r)) * math.pi

    return cnt, min(dist(th_lo), dist(th_hi))


def gap_index(theta, theta_t):
    return math.floor((theta - theta_t) / math.pi)


def theta_target(tb):
    return math.atan2(tb, -(1.0 - tb) / 2.0)  # in [pi/2, pi]


def sgn(v):
    return (v > 0.0) - (v < 0.0)


# ------------------------------------------------------------------- cases


def build_case(cid, N):
    """Return (background, meta).  Parameters pre-registered in PLAN.md v2."""
    smax, pre_steps = 6.0, 24000
    meta = {"case": cid}
    if cid == "DS":
        m2 = Fr(7385903388887613, 18014398509481984)
        gam = Fr(20)
        v0 = Fr(3602879701896397, 36028797018963968)
        v1 = Fr(6520040733916207, 72057594037927936)
        la = Fr(6755388606266369, 1125899906842624)
        lb = Fr(-851862101055633, 140737488355328)
        A = (Fr(456607025194779413, 4611686018427387904) + Fr(114151756532473697, 1152921504606846976)) / 2
        pot = Quadratic(0.0, float(m2 / 2))
        Af = float(A)
        Ta = float(gam) * (Af - float(v0)) / 2.0
        Ha = -(float(la) + float(gam) * (Af - float(v0)) ** 2 / 2.0) / 6.0
        k = Ha * Ha - 1.0 - Ta * Ta / 12.0 + pot.V(Af) / 6.0
        y0 = (0.0, Ha, Af, Ta)

        def F1(y):
            return y[1] - (float(lb) + float(gam) * (y[2] - float(v1)) ** 2 / 2.0) / 6.0

        D, yD = find_event(y0, k, pot, 2.0, 20000, F1)
        F2 = yD[3] + float(gam) * (yD[2] - float(v1)) / 2.0 if yD else None
        meta.update({"k": k, "D": D, "F2_at_D": F2, "Phi_a": Af, "T_a": Ta, "H_a": Ha,
                     "s_sing": pre_scan(y0, k, pot, 2.5, 25000)})
        return Background(y0, k, pot, D, N), meta
    if cid in ("F1", "F1b", "F0"):
        pot = Quadratic(0.0, 2.0)
        Pa = 1.0
        Ta = -0.5 if cid in ("F1", "F1b") else 0.5
        H2 = 1.0 + Ta * Ta / 12.0 - pot.V(Pa) / 6.0
        Ha = -math.sqrt(H2) if cid == "F1" else math.sqrt(H2)
    elif cid == "F3":
        pot = Quadratic(5.5, -10.0)
        Pa, Ta = -0.3, -0.5
        H2 = 1.0 + Ta * Ta / 12.0 - pot.V(Pa) / 6.0
        Ha = math.sqrt(H2)
    else:
        raise ValueError(cid)
    k = 0.0
    y0 = (0.0, Ha, Pa, Ta)
    meta["s_sing"] = pre_scan(y0, k, pot, smax, pre_steps)
    if cid in ("F1", "F1b"):
        s1, _ = find_event(y0, k, pot, smax, pre_steps, lambda y: y[3], which=1)
        D = s1 + (0.3 if cid == "F1" else 0.5)
        meta["s_zeros"] = [s1]
    elif cid == "F3":
        zs = [find_event(y0, k, pot, smax, pre_steps, lambda y: y[3], which=w)[0] for w in (1, 2, 3)]
        s3 = zs[2]
        p3, _ = find_event(y0, k, pot, smax, pre_steps,
                           lambda y: pot.dV(y[2]) - 4.0 * y[1] * y[3], after=s3, which=1)
        D = s3 + 0.5 * (p3 - s3)
        meta["s_zeros"] = zs
        meta["p3"] = p3
    else:
        D = 0.8
    meta.update({"k": k, "D": D, "Phi_a": Pa, "T_a": Ta, "H_a": Ha})
    return Background(y0, k, pot, D, N), meta


def background_gates(bg, meta, expected_n, monotonic=False):
    Ta, Tb, Tpa, Tpb = bg.T[0], bg.T[-1], bg.Tp[0], bg.Tp[-1]
    zi = bg.zeros_of_T()
    mtz = min([abs(bg.Tp[i]) for i in zi] + [abs(bg.Tp[i + 1]) for i in zi]) if zi else None
    s_sing = meta.get("s_sing")
    sing_ok = (s_sing is None) or (s_sing >= bg.D + 0.05)
    g1 = bg.finite and bg.max_constraint <= 1e-9
    if monotonic:
        g2 = (len(zi) == 0) and sing_ok
    else:
        g2 = (Ta <= -1e-6 and Tb >= 1e-6 and Tpa >= 1e-6 and Tpb >= 1e-6 and len(zi) == expected_n
              and (mtz is None or mtz >= 1e-6) and sing_ok)
    return {"G1_max_constraint": bg.max_constraint, "G1_pass": g1, "finite": bg.finite,
            "T_a": Ta, "T_b": Tb, "Tp_a": Tpa, "Tp_b": Tpb, "n_detected": len(zi),
            "min_abs_Tp_at_zero": mtz, "s_sing": s_sing, "sing_ok": sing_ok, "G2_pass": g2,
            "a_min": min(bg.a), "a_max": max(bg.a), "max_abs_Q": bg.maxabsQ}


def g6_check(rec_phase, lam, rt1_branch):
    """Unwrap safety.  Steps >= 2: |dtheta| < pi/2.  Step 1: |dtheta| < pi - 0.01 and, at
    |lambda| <= 1e-5 on the (RT1)/DS branch, the half-plane condition that makes the
    first-step rotation unambiguous (lambda < 0: f(launch) >= 0 and f(h) > 0;
    lambda > 0: L(launch) <= 0 and L(h) < 0)."""
    ok = rec_phase["max_dtheta"] < math.pi / 2.0 and rec_phase["first_dtheta"] < math.pi - 0.01
    if abs(lam) <= 1e-5 and rt1_branch:
        if lam < 0.0:
            ok = ok and rec_phase["f_launch"] >= 0.0 and rec_phase["f_h"] > 0.0
        else:
            ok = ok and rec_phase["L_launch"] <= 0.0 and rec_phase["L_h"] < 0.0
    return ok


def count_case(bg, ta, tb, lam_abs_min, rt1, theta_pred, lite=False):
    """M1 (forward), M1' (backward) and M2 (phase) counts in (mu_min, mu_top).

    lite=True (pre-registered timing reduction, 2N pass only): forward M1 on the
    merged grid with bisected roots, and M2; no nested grid, backward or far scan."""
    k4 = 4.0 * bg.k
    mu_min, mu_top = -k4 - lam_abs_min, -k4 - DELTA
    grid = merged_grid(bg, lam_abs_min)
    phases = {}

    def fwd(mu):
        r = shoot(bg, mu, ta, tb, phase=True)
        phases[mu] = r
        return r["char"]

    def fchar(mu):
        return shoot(bg, mu, ta, tb)["char"]

    m1 = scan(fwd, grid, refine=False, nested=False)
    idx, _ = sign_changes(m1["vals"])
    roots = [bisect(fchar, grid[i], grid[i + 1], m1["vals"][i]) for i in idx]
    lo = shoot(bg, mu_min, ta, tb, phase=True, quadrant_check=True)
    hi = shoot(bg, mu_top, ta, tb, phase=True)
    th_t = theta_target(tb)
    m2, margin = targets_between(lo["theta_b"], hi["theta_b"], th_t)
    if lite:
        return {"t_a": ta, "t_b": tb, "lite": True, "M1_count": m1["count"], "M2_count": m2,
                "M2_target_margin": margin, "eigenvalues": roots,
                "theta_b_mu_top_over_pi": hi["theta_b"] / math.pi}
    fine = []
    for i in range(len(grid) - 1):
        fine.append(m1["vals"][i])
        fine.append(fchar(0.5 * (grid[i] + grid[i + 1])))
    fine.append(m1["vals"][-1])
    idx2, zero2 = sign_changes(fine)
    m1b = scan(lambda mu: shoot_back(bg, mu, ta, tb), grid, refine=False, nested=False)
    far = scan(fchar, linspace(8.0 * mu_min, mu_min, 50), refine=False, nested=False)
    nu_far = bg.nu_h(8.0 * mu_min)
    thetas = [phases[mu]["theta_b"] for mu in grid]
    diffs = [b - a for a, b in zip(thetas, thetas[1:])]
    g6_all = (all(g6_check(phases[mu], mu + k4, rt1) for mu in grid) and g6_check(lo, mu_min + k4, rt1)
              and g6_check(hi, mu_top + k4, rt1))
    char0 = shoot(bg, -k4, ta, tb)["char"]
    root_constraints = [shoot(bg, r, ta, tb)["constraint_rel"] for r in roots]
    cons = [lo["constraint_rel"], hi["constraint_rel"]] + root_constraints
    rec = {
        "t_a": ta, "t_b": tb, "mu_min": mu_min, "mu_top": mu_top, "grid_points": len(grid),
        "M1_count": m1["count"], "M1_count_nested": len(idx2), "M1b_count": m1b["count"],
        "M1_exact_zero_hit": m1["exact_zero"] or zero2 or m1b["exact_zero"],
        "M2_count": m2, "M2_target_margin": margin, "theta_t": th_t,
        "theta_b_mu_min": lo["theta_b"], "theta_b_mu_top": hi["theta_b"],
        "theta_b_mu_top_over_pi": hi["theta_b"] / math.pi, "theta_pred_over_pi": theta_pred / math.pi,
        "theta_b_mu_min_mod_pi": lo["theta_b"] % math.pi,
        "max_dtheta_steps_ge2": max([phases[mu]["max_dtheta"] for mu in grid] + [lo["max_dtheta"], hi["max_dtheta"]]),
        "max_first_dtheta": max([phases[mu]["first_dtheta"] for mu in grid] + [lo["first_dtheta"], hi["first_dtheta"]]),
        "top_first_step": {key: hi[key] for key in ("first_dtheta", "f_launch", "f_h", "L_h", "theta_h_mod_2pi")},
        "phase_refinement": {
            "n_refined_steps_total": sum(phases[mu]["n_refined_steps"] for mu in grid) + lo["n_refined_steps"] + hi["n_refined_steps"],
            "max_refine_discrepancy": max([phases[mu]["max_refine_discrepancy"] for mu in grid] + [lo["max_refine_discrepancy"], hi["max_refine_discrepancy"]]),
            "max_refine_depth": max([phases[mu]["max_refine_depth"] for mu in grid] + [lo["max_refine_depth"], hi["max_refine_depth"]])},
        "quadrant_ok_mu_min": lo["quadrant_ok"], "far_sign_changes": far["count"],
        "constraint_rel_max": max(cons), "min_theta_increment": min(diffs) if diffs else None,
        "nu_h_mu_min": lo["nu_h"], "nu_h_far": nu_far,
        "eigenvalues": roots, "char_mu_top": hi["char"], "char_mu0_physical": char0,
    }
    rec["G3_pass"] = rec["constraint_rel_max"] <= 1e-7
    rec["G5_pass"] = (rec["M1_count"] == rec["M1_count_nested"])
    rec["G6_pass"] = g6_all
    rec["G7_pass"] = (rec["M1_count"] == rec["M2_count"] == rec["M1b_count"])
    rec["G8_pass"] = (lo["quadrant_ok"] and 0.0 < rec["theta_b_mu_min_mod_pi"] < math.pi / 2.0 and far["count"] == 0)
    rec["G9_pass"] = margin >= 1e-6
    rec["near_threshold_eigenvalue_flag"] = not rec["G9_pass"]
    g12 = (sgn(hi["char"]) == sgn(char0) and sgn(char0) != 0
           and gap_index(hi["theta_b"], th_t) == gap_index(theta_pred, th_t))
    if rt1:
        g12 = g12 and char0 < 0.0
    rec["G12_pass"] = g12
    rec["G13_pass"] = all(d > 0.0 for d in diffs)
    rec["G14_pass"] = (rec["nu_h_mu_min"] <= 0.02 and nu_far <= 0.3)
    rec["implementation_gates_pass"] = all(rec[g] for g in ("G3_pass", "G5_pass", "G6_pass", "G8_pass",
                                                            "G9_pass", "G12_pass", "G13_pass", "G14_pass"))
    return rec


def tgrid():
    return [1.0, 0.5, 0.1, 0.0]


def pairs_for(cid, bg, meta, f1b9=False):
    if cid == "F1b" and f1b9:
        return [(ta, tb) for ta in (1.0, 0.1, 0.0) for tb in (1.0, 0.1, 0.0)]
    if cid in ("F1", "F1b", "F3"):
        return [(ta, tb) for ta in tgrid() for tb in tgrid()]
    if cid == "F0":
        Ta, Tpa, Tb, Tpb = bg.T[0], bg.Tp[0], bg.T[-1], bg.Tp[-1]
        ka3 = 6.0 * Tpa / Ta
        kb3 = max(0.0, -6.0 * Tpb / Tb)
        meta["F0_case3_kappas"] = [ka3, kb3]
        return [(0.0, 0.0), (1.0, 0.0), (1.0 / (1.0 + ka3), 1.0 / (1.0 + kb3))]
    return [(1.0, 1.0), (0.0, 0.0)]


def choose_N(cid, base=2000):
    """Smallest N in {base, 2base, 4base} with nu*h <= 0.02 at mu_min (G14 rule)."""
    for j in range(3):
        N = base * (2 ** j)
        bg, meta = build_case(cid, N)
        lam_abs_min = 2.0 * max(1.0, bg.coop_bound())
        if bg.nu_h(-4.0 * bg.k - lam_abs_min) <= 0.02:
            return N
    return base * 4


def dry(cid, out_path):
    """REDACTED flag-only dry run: no counts, eigenvalues, characteristic values or phases."""
    t0 = time.time()
    rec = {"label": "FLOAT EXPLORATORY - REDACTED DRY RUN", "case": cid, "per_N": {}}
    for N in (1000, 2000):
        tb0 = time.time()
        bg, meta = build_case(cid, N)
        t_bg = time.time() - tb0
        expected = {"F1": 1, "F1b": 1, "F3": 3, "F0": 0, "DS": 1}[cid]
        bgate = background_gates(bg, meta, expected, monotonic=(cid == "F0"))
        lam_abs_min = 2.0 * max(1.0, bg.coop_bound())
        k4 = 4.0 * bg.k
        prs = pairs_for(cid, bg, meta)[:2] if cid != "F0" else pairs_for(cid, bg, meta)
        flags = []
        for ta, tb in prs:
            ts = time.time()
            lo = shoot(bg, -k4 - lam_abs_min, ta, tb, phase=True, quadrant_check=True)
            hi = shoot(bg, -k4 - DELTA, ta, tb, phase=True)
            t_shoot = (time.time() - ts) / 2.0
            tb_s = time.time()
            shoot_back(bg, -k4 - DELTA, ta, tb)
            t_back = time.time() - tb_s
            flags.append({"t_a": ta, "t_b": tb, "G3_lo": lo["constraint_rel"], "G3_hi": hi["constraint_rel"],
                          "max_dtheta_steps_ge2": max(lo["max_dtheta"], hi["max_dtheta"]),
                          "first_dtheta_top": hi["first_dtheta"],
                          "G6_top_branch_ok": g6_check(hi, -DELTA, cid != "F0"),
                          "quadrant_ok_mu_min": lo["quadrant_ok"],
                          "nu_h_mu_min": lo["nu_h"], "nu_h_far": bg.nu_h(8.0 * (-k4 - lam_abs_min)),
                          "sec_per_forward_shoot": t_shoot, "sec_per_backward_shoot": t_back})
        meta_red = {key: meta[key] for key in meta if key in ("D", "s_zeros", "p3", "s_sing", "k", "F2_at_D")}
        rec["per_N"][str(N)] = {"meta": meta_red, "background_gates": bgate, "lam_abs_min": lam_abs_min,
                                "sec_background": t_bg, "pair_flags": flags}
    rec["elapsed_s"] = time.time() - t0
    with open(out_path, "w") as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({"case": cid, "dry": True, "elapsed_s": rec["elapsed_s"]}))


def run(cid, out_path, opts):
    global GRID_N
    t0 = time.time()
    if "--grid200" in opts:
        GRID_N = 200
    g4lite = "--g4lite" in opts
    f1b9 = "--f1b9" in opts
    result = {"label": "FLOAT EXPLORATORY", "case": cid, "version": "v2", "options": sorted(opts),
              "GRID_N": GRID_N}
    expected = {"F1": 1, "F1b": 1, "F3": 3, "F0": 0, "DS": 1}[cid]
    Nb = choose_N(cid)
    result["N_base"] = Nb
    per_N = {}
    for N in (Nb, 2 * Nb):
        lite = g4lite and N == 2 * Nb
        bg, meta = build_case(cid, N)
        bgate = background_gates(bg, meta, expected, monotonic=(cid == "F0"))
        lam_abs_min = 2.0 * max(1.0, bg.coop_bound())
        vth, vjump = bg.vartheta_D()
        theta_pred = math.pi + vth
        k4 = 4.0 * bg.k
        recs = []
        for (ta, tb) in pairs_for(cid, bg, meta, f1b9):
            rec = count_case(bg, ta, tb, lam_abs_min, rt1=(cid != "F0"), theta_pred=theta_pred, lite=lite)
            if cid == "DS" and not lite:
                band_grid = linspace(-k4 + DELTA, 0.0, 400)
                bf = scan(lambda mu: shoot(bg, mu, ta, tb)["char"], band_grid, refine=True, nested=True)
                bb = scan(lambda mu: shoot_back(bg, mu, ta, tb), band_grid, refine=False, nested=False)
                lo = shoot(bg, -k4 + DELTA, ta, tb, phase=True)
                hi = shoot(bg, 0.0, ta, tb, phase=True)
                b2, bmargin = targets_between(lo["theta_b"], hi["theta_b"], theta_target(tb))
                c_m = shoot(bg, -k4 - DELTA, ta, tb)["char"]
                c_0 = shoot(bg, -k4, ta, tb)["char"]
                c_p = shoot(bg, -k4 + DELTA, ta, tb)["char"]
                rec["band"] = {"M1_count": bf["count"], "M1_count_nested": bf["count_nested"], "roots": bf["roots"],
                               "M1b_count": bb["count"], "exact_zero": bf["exact_zero"] or bb["exact_zero"],
                               "M2_count": b2, "margin": bmargin,
                               "theta_b_band_lo_over_pi": lo["theta_b"] / math.pi,
                               "theta_b_mu0_over_pi": hi["theta_b"] / math.pi,
                               "theta_a_band_over_pi": lo["theta_a"] / math.pi, "char_mu0": hi["char"],
                               "G6_band": g6_check(lo, DELTA, True) and g6_check(hi, 4.0 * bg.k, True),
                               "G12_threshold_signs": (sgn(c_m) == sgn(c_0) == sgn(c_p) and sgn(c_0) != 0),
                               "band_lo_gap_matches_pred": gap_index(lo["theta_b"], theta_target(tb)) ==
                               gap_index(theta_pred, theta_target(tb))}
            recs.append(rec)
        ls = None
        if cid == "F0" and not lite:
            ls = []
            win = linspace(-k4 - lam_abs_min, 300.0, 600)
            for (ta, tb) in pairs_for(cid, bg, meta):
                sa = scan(lambda mu, ta=ta, tb=tb: shoot(bg, mu, ta, tb)["char"], win, refine=True, nested=True)
                sb = scan(lambda mu, ta=ta, tb=tb: ls_shoot(bg, mu, ta, tb), win, refine=True, nested=True)
                diffs = [abs(x - y) / max(1.0, abs(x)) for x, y in zip(sa["roots"], sb["roots"])]
                ls.append({"t_a": ta, "t_b": tb, "paperA_roots": sa["roots"], "LS_roots": sb["roots"],
                           "n_paperA": sa["count"], "n_paperA_nested": sa["count_nested"],
                           "n_LS": sb["count"], "n_LS_nested": sb["count_nested"], "rel_diffs": diffs,
                           "G11_pass": (sa["count"] == sb["count"] == sa["count_nested"] == sb["count_nested"]
                                        and len(diffs) == sa["count"] and (max(diffs) if diffs else 0.0) <= 1e-6)})
        per_N[str(N)] = {"meta": meta, "background_gates": bgate, "lam_abs_min": lam_abs_min,
                         "vartheta_D": vth, "vartheta_max_jump": vjump, "records": recs, "LS": ls}
    result["per_N"] = per_N
    a, b = per_N[str(Nb)]["records"], per_N[str(2 * Nb)]["records"]
    g4 = []
    for ra, rb in zip(a, b):
        same = (ra["M1_count"] == rb["M1_count"] and ra["M2_count"] == rb["M2_count"])
        ev = [abs(x - y) / max(1.0, abs(x)) for x, y in zip(ra["eigenvalues"], rb["eigenvalues"])]
        g4.append({"t_a": ra["t_a"], "t_b": ra["t_b"], "counts_equal": same,
                   "max_rel_ev_diff": max(ev) if ev else 0.0,
                   "G4_pass": same and len(ra["eigenvalues"]) == len(rb["eigenvalues"]) and
                   (max(ev) if ev else 0.0) <= 1e-6})
    result["G4"] = g4
    result["elapsed_s"] = time.time() - t0
    with open(out_path, "w") as fh:
        json.dump(result, fh, indent=1)
    print(json.dumps({"case": cid, "elapsed_s": result["elapsed_s"]}))


if __name__ == "__main__":
    if "--dry" in sys.argv[3:]:
        dry(sys.argv[1], sys.argv[2])
    else:
        run(sys.argv[1], sys.argv[2], set(sys.argv[3:]))
