#!/usr/bin/env python3
"""Exact jet-arithmetic checks of the geometric steps in DERIVATION.md (F04).

Python standard library only (fractions). No sympy, no floating point.

Functions are represented by truncated multivariate Taylor polynomials ("jets")
about a point p, in the variables u0 = s - s0, u1..u4 (slice coordinates) and
the bookkeeping parameter e (epsilon).  Metric jets are kept to coordinate
degree 2, so curvature is exact at p (coordinate degree 0).  Every comparison
below is an exact equality of rationals at p.

Slices: k > 0 uses dS4 in conformal time, gamma = (-dw^2+dx^2)/(k w^2);
k < 0 uses AdS4 Poincare, gamma = (-dt^2+dx^2)/(|k| z^2); k = 0 Minkowski.
In each case Ric(gamma) = 3 k gamma, which is checked.

Checks (each at several random rational points, for k > 0, k = 0, k < 0):
  C1  Ric(gamma) = 3 k gamma (sanity of the slice construction)
  C2  background E_AB = 0 and scalar eq when (9) is imposed at p
  C3  first-order E_nn  equals (H1)                      [off-shell]
  C4  first-order E_s mu equals (M1')                    [off-shell]
  C5  first-order traceless E_mu nu = -(A+2psi) TfHess Q  [off-shell]
  C6  first-order trace of E_mu nu equals -EL_psi/a^4 from the reduced action
      (on-shell background at p)
  C7  first-order scalar equation equals (S)             [off-shell]
  C8  ADM/Gibbons-Hawking identity
        sqrt(-g) R = N sqrt(-q)[R4 + K^2 - K.K] - 2 d_A[sqrt(-g)(n^A K - a^A)]
      through second order in e                          [off-shell]
  C9  conformal slice formula through second order in e:
        sqrt(-q) R4[a^2 e^{2w} gamma] = a^2 sqrt(-gamma) e^{2w}(12k - 6 Box w - 6|dw|^2)
  C10 extrinsic curvature of the displaced wall s = s0 + e xi Q(x) in the
      perturbed metric, inward normal sigma: matches P2.1   [off-shell]
  C11 first-order normal derivative n.dPhi on the displaced wall: matches
      sigma[T + (f' - A T + T' xi) Q]                     [off-shell]
"""
import random
import sys
from fractions import Fraction as Fr

NV = 6          # u0, u1, u2, u3, u4, e
EIDX = 5
DC = 2          # max coordinate degree kept
DE = 1          # max epsilon degree kept (set per check)

ZERO_KEY = (0,) * NV


def cdeg(k):
    return k[0] + k[1] + k[2] + k[3] + k[4]


def jconst(c):
    c = Fr(c)
    return {ZERO_KEY: c} if c != 0 else {}


def jvar(i, c=1):
    k = [0] * NV
    k[i] = 1
    return {tuple(k): Fr(c)}


def jadd(*js):
    out = {}
    for j in js:
        for k, v in j.items():
            nv = out.get(k, 0) + v
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
    return out


def jscale(j, s):
    s = Fr(s)
    if s == 0:
        return {}
    return {k: v * s for k, v in j.items()}


def jsub(a, b):
    return jadd(a, jscale(b, -1))


def jmul(a, b, maxdc=None):
    if not a or not b:
        return {}
    mdc = DC if maxdc is None else maxdc
    out = {}
    for k1, v1 in a.items():
        d1 = cdeg(k1)
        e1 = k1[EIDX]
        if d1 > mdc or e1 > DE:
            continue
        for k2, v2 in b.items():
            if d1 + cdeg(k2) > mdc or e1 + k2[EIDX] > DE:
                continue
            k = (k1[0] + k2[0], k1[1] + k2[1], k1[2] + k2[2], k1[3] + k2[3],
                 k1[4] + k2[4], e1 + k2[EIDX])
            nv = out.get(k, 0) + v1 * v2
            if nv == 0:
                out.pop(k, None)
            else:
                out[k] = nv
    return out


def jmuln(*js, maxdc=None):
    out = jconst(1)
    for j in js:
        out = jmul(out, j, maxdc)
    return out


def jinv(a):
    a0 = a.get(ZERO_KEY, 0)
    if a0 == 0:
        raise ZeroDivisionError("jet with zero constant term")
    r = {k: v for k, v in a.items() if k != ZERO_KEY}
    t = jscale(r, -1 / a0)
    out = jconst(1)
    term = jconst(1)
    for _ in range(DC + DE + 1):
        term = jmul(term, t)
        if not term:
            break
        out = jadd(out, term)
    return jscale(out, 1 / a0)


def jderiv(a, i):
    out = {}
    for k, v in a.items():
        if k[i] > 0:
            nk = list(k)
            nk[i] -= 1
            out[tuple(nk)] = out.get(tuple(nk), 0) + v * k[i]
    return {k: v for k, v in out.items() if v != 0}


def at_p(a, epow):
    """Coefficient of e^epow at coordinate degree 0."""
    k = [0] * NV
    k[EIDX] = epow
    return a.get(tuple(k), Fr(0))


def upoly(i, coeffs):
    """sum_n coeffs[n] * u_i^n / n!  (coeffs = value, 1st, 2nd derivative ...)."""
    out = {}
    fact = 1
    for n, c in enumerate(coeffs):
        if n > 0:
            fact *= n
        if c == 0:
            continue
        k = [0] * NV
        k[i] = n
        out[tuple(k)] = Fr(c) / fact
    return out


def subst_s_shift(a, shift):
    """Compose a(u0, ...) with u0 -> u0 + shift (shift a jet without constant term)."""
    # a = sum_n a_n(u1..,e) u0^n ; expand (u0+shift)^n
    out = {}
    u0 = jvar(0)
    base = jadd(u0, shift)
    for k, v in a.items():
        n = k[0]
        rest = dict()
        rk = (0,) + k[1:]
        rest[rk] = v
        term = rest
        for _ in range(n):
            term = jmul(term, base)
        out = jadd(out, term)
    return out


def rnd(lo=-9, hi=9, nonzero=False, rng=random):
    while True:
        num = rng.randint(lo * 6, hi * 6)
        den = rng.randint(1, 6)
        v = Fr(num, den)
        if not nonzero or v != 0:
            return v


# ---------------------------------------------------------------- geometry
def christoffel_diag(g, idx):
    """Gamma^a_{bc} for a diagonal metric g[a] over coordinate indices idx."""
    ginv = {a: jinv(g[a]) for a in idx}
    dg = {(c, a): jderiv(g[a], c) for a in idx for c in idx}
    G = {}
    for a in idx:
        for b in idx:
            for c in idx:
                t = {}
                if a == c:
                    t = jadd(t, dg[(b, c)])
                if a == b:
                    t = jadd(t, dg[(c, b)])
                if b == c:
                    t = jadd(t, jscale(dg[(a, b)], -1))
                if t:
                    G[(a, b, c)] = jscale(jmul(ginv[a], t), Fr(1, 2))
    return G, ginv


def ricci(G, idx):
    """R_bd = d_a G^a_bd - d_d G^a_ab + G^a_ae G^e_bd - G^a_de G^e_ab, at coordinate degree 0."""
    R = {}
    for b in idx:
        for d in idx:
            t = {}
            for a in idx:
                x = G.get((a, b, d))
                if x:
                    t = jadd(t, jderiv(x, a))
                y = G.get((a, a, b))
                if y:
                    t = jadd(t, jscale(jderiv(y, d), -1))
                for e in idx:
                    p1 = G.get((a, a, e))
                    p2 = G.get((e, b, d))
                    if p1 and p2:
                        t = jadd(t, jmul(p1, p2, maxdc=0))
                    p3 = G.get((a, d, e))
                    p4 = G.get((e, a, b))
                    if p3 and p4:
                        t = jadd(t, jscale(jmul(p3, p4, maxdc=0), -1))
            R[(b, d)] = {k: v for k, v in t.items() if cdeg(k) == 0}
    return R


def ricci_scalar(R, ginv, idx):
    out = {}
    for b in idx:
        out = jadd(out, jmul(ginv[b], R[(b, b)], maxdc=0))
    return out


# ------------------------------------------------------------- the setup
class Setup:
    pass


def slice_conformal_factor(k, w0):
    """Omega(x) with gamma = Omega * eta, and the coordinate it depends on."""
    if k > 0:
        c = jadd(jconst(w0), jvar(1))
        return jinv(jscale(jmul(c, c), k)), 1
    if k < 0:
        c = jadd(jconst(w0), jvar(4))
        return jinv(jscale(jmul(c, c), -k)), 4
    return jconst(1), None


ETA = {1: -1, 2: 1, 3: 1, 4: 1}


def make_setup(rng, k, onshell):
    S = Setup()
    S.k = Fr(k)
    S.w0 = rnd(1, 4, nonzero=True, rng=rng)
    if S.w0 < 0:
        S.w0 = -S.w0
    S.a0 = abs(rnd(1, 3, nonzero=True, rng=rng))
    S.H = rnd(rng=rng)
    S.T = rnd(rng=rng)
    S.V1 = rnd(rng=rng)
    S.V2 = rnd(rng=rng)
    S.V3 = rnd(rng=rng)
    if onshell:
        S.Hp = -S.T ** 2 / 3 - S.k / S.a0 ** 2
        S.T1 = S.V1 - 4 * S.H * S.T
        S.V0 = 6 + S.T ** 2 / 2 + 6 * S.k / S.a0 ** 2 - 6 * S.H ** 2
    else:
        S.Hp = rnd(rng=rng)
        S.T1 = rnd(rng=rng)
        S.V0 = rnd(rng=rng)
    S.a1 = S.H * S.a0
    S.a2 = (S.Hp + S.H ** 2) * S.a0
    S.phi0 = rnd(rng=rng)
    # perturbation profiles: value, first, second derivative at s0
    S.A = [rnd(rng=rng) for _ in range(3)]
    S.psi = [rnd(rng=rng) for _ in range(3)]
    S.f = [rnd(rng=rng) for _ in range(3)]
    S.xi = rnd(rng=rng)
    # harmonic jet Q (arbitrary; formulas are pointwise in Q, dQ, ddQ)
    S.q0 = rnd(nonzero=True, rng=rng)
    S.q1 = {i: rnd(rng=rng) for i in range(1, 5)}
    S.q2 = {}
    for i in range(1, 5):
        for j in range(i, 5):
            S.q2[(i, j)] = S.q2[(j, i)] = rnd(rng=rng)
    return S


def Qjet(S):
    out = jconst(S.q0)
    for i in range(1, 5):
        out = jadd(out, jvar(i, S.q1[i]))
    for i in range(1, 5):
        for j in range(1, 5):
            out = jadd(out, jmul(jvar(i, S.q2[(i, j)] / 2), jvar(j)))
    return out


def gamma_data(S):
    """gamma diagonal jets, its Christoffels, covariant Hessian of Q and Box Q at p."""
    Om, _ = slice_conformal_factor(S.k, S.w0)
    gam = {m: jscale(Om, ETA[m]) for m in range(1, 5)}
    idx = [1, 2, 3, 4]
    G, ginv = christoffel_diag(gam, idx)
    R = ricci(G, idx)
    Om0 = at_p(Om, 0)
    gam0 = {m: ETA[m] * Om0 for m in idx}
    # covariant Hessian at p
    hess = {}
    for m in idx:
        for n in idx:
            v = S.q2[(m, n)]
            for r in idx:
                x = G.get((r, m, n))
                if x:
                    v -= at_p(x, 0) * S.q1[r]
            hess[(m, n)] = v
    boxQ = sum(hess[(m, m)] / gam0[m] for m in idx)
    ric_ok = all(at_p(R[(m, n)], 0) == (3 * S.k * gam0[m] if m == n else 0)
                 for m in idx for n in idx)
    return Om, gam, gam0, hess, boxQ, ric_ok


def build_metric(S, Om, Q, eps_order):
    e = jvar(EIDX)
    a = upoly(0, [S.a0, S.a1, S.a2])
    A = upoly(0, S.A)
    psi = upoly(0, S.psi)
    N = jadd(jconst(1), jmuln(e, A, Q))
    conf = jadd(jconst(1), jscale(jmuln(e, psi, Q), 2))
    a2 = jmul(a, a)
    g = {0: jmul(N, N)}
    for m in range(1, 5):
        g[m] = jscale(jmuln(a2, conf, Om), ETA[m])
    return g, N, conf, a2


def phi_jet(S, Q):
    e = jvar(EIDX)
    phi0 = upoly(0, [S.phi0, S.T, S.T1])
    f = upoly(0, S.f)
    return jadd(phi0, jmuln(e, f, Q)), phi0


def V_of(S, Phi, deriv=0):
    """V(Phi) or V'(Phi) as a jet, using the cubic Taylor model about phi0."""
    d = jsub(Phi, jconst(S.phi0))
    if deriv == 0:
        c = [S.V0, S.V1, S.V2, S.V3]
    else:
        c = [S.V1, S.V2, S.V3]
    out = {}
    term = jconst(1)
    fact = 1
    for n, cn in enumerate(c):
        if n > 0:
            term = jmul(term, d)
            fact *= n
        out = jadd(out, jscale(term, Fr(cn) / fact))
    return out


def field_equation_checks(S):
    global DE
    DE = 1
    Om, gam, gam0, hess, boxQ, ric_ok = gamma_data(S)
    Q = Qjet(S)
    g, N, conf, a2 = build_metric(S, Om, Q, 1)
    idx = [0, 1, 2, 3, 4]
    G, ginv = christoffel_diag(g, idx)
    R = ricci(G, idx)
    Rs = ricci_scalar(R, ginv, idx)
    Phi, _ = phi_jet(S, Q)
    dPhi = {A_: jderiv(Phi, A_) for A_ in idx}
    kin = {}
    for A_ in idx:
        kin = jadd(kin, jmuln(ginv[A_], dPhi[A_], dPhi[A_], maxdc=0))
    Vp = V_of(S, Phi, 0)
    E = {}
    for A_ in idx:
        for B_ in idx:
            gAB = g[A_] if A_ == B_ else {}
            Gab = jsub(R[(A_, B_)], jscale(jmul(Rs, gAB, maxdc=0), Fr(1, 2)))
            Tab = jsub(jmul(dPhi[A_], dPhi[B_], maxdc=0),
                       jmul(gAB, jadd(jscale(kin, Fr(1, 2)), Vp), maxdc=0))
            E[(A_, B_)] = {k: v for k, v in jsub(jsub(Gab, jscale(gAB, 6)), Tab).items() if cdeg(k) == 0}
    # scalar: Box Phi - V'(Phi)
    box = {}
    for A_ in idx:
        t = jderiv(dPhi[A_], A_)
        for C_ in idx:
            x = G.get((C_, A_, A_))
            if x:
                t = jsub(t, jmul(x, dPhi[C_]))
        box = jadd(box, jmul(ginv[A_], t, maxdc=0))
    scal = jsub(box, V_of(S, Phi, 1))
    return dict(E=E, scal=scal, g=g, ginv=ginv, gam0=gam0, hess=hess, boxQ=boxQ, ric_ok=ric_ok)


def expected_first_order(S, gam0, hess, boxQ):
    a, H, T, T1 = S.a0, S.H, S.T, S.T1
    k = S.k
    A, A1, _ = S.A
    psi, psi1, psi2 = S.psi
    f, f1, f2 = S.f
    q = S.q0
    lam_part = 3 * psi * (boxQ + 4 * k * q) / a ** 2
    Enn = lam_part + 12 * H * (psi1 - H * A) * q - (T * f1 - T ** 2 * A - S.V1 * f) * q
    Esm = {m: -3 * (psi1 - H * A + T * f / 3) * S.q1[m] for m in range(1, 5)}
    tf = {}
    for m in range(1, 5):
        for n in range(1, 5):
            tr = boxQ * gam0[m] / 4 if m == n else 0
            tf[(m, n)] = -(A + 2 * psi) * (hess[(m, n)] - tr)
    scal = (f2 + 4 * H * f1 - (A + 4 * psi) * (T1 + 4 * H * T)
            + (4 * psi1 - A1) * T + (4 * psi - A) * T1 + 4 * H * (4 * psi - A) * T
            - S.V2 * f) * q + f * boxQ / a ** 2
    # trace (needs on-shell background at p): -EL_psi / a^4
    Hp = S.Hp
    trace = (12 * (psi2 - Hp * A - H * A1 + 4 * H * (psi1 - H * A))
             + (24 * k * psi + 12 * k * A) / a ** 2 + 4 * T * f1 + 4 * S.V1 * f) * q \
        + 3 * (A + 2 * psi) * boxQ / a ** 2
    return dict(Enn=Enn, Esm=Esm, tf=tf, scal=scal, trace=trace)


def run_field_checks(S, onshell):
    res = field_equation_checks(S)
    E, g = res['E'], res['g']
    gam0, hess, boxQ = res['gam0'], res['hess'], res['boxQ']
    out = {'C1_ric_gamma': res['ric_ok']}
    if onshell:
        bg = all(at_p(E[(A_, B_)], 0) == 0 for A_ in range(5) for B_ in range(5))
        out['C2_background'] = bg and at_p(res['scal'], 0) == 0
    exp = expected_first_order(S, gam0, hess, boxQ)
    # E_nn = E_ss / g_ss
    Enn = jmul(E[(0, 0)], jinv(g[0]), maxdc=0)
    out['C3_Enn_H1'] = at_p(Enn, 1) == exp['Enn']
    out['C4_Esmu_M1'] = all(at_p(E[(0, m)], 1) == exp['Esm'][m] for m in range(1, 5))
    # traceless part w.r.t. gamma at p: X_mn - (1/4) gamma_mn gamma^rs X_rs
    a2 = S.a0 ** 2
    X = {(m, n): at_p(E[(m, n)], 1) for m in range(1, 5) for n in range(1, 5)}
    trg = sum(X[(m, m)] / gam0[m] for m in range(1, 5))
    tf_ok = all(X[(m, n)] - (trg * gam0[m] / 4 if m == n else 0) == exp['tf'][(m, n)]
                for m in range(1, 5) for n in range(1, 5))
    out['C5_traceless'] = tf_ok
    if onshell:
        trace_bar = trg / a2   # gbar^{mu nu} E_mu nu with gbar = a^2 gamma
        out['C6_trace_vs_ELpsi'] = trace_bar == exp['trace']
    out['C7_scalar_S'] = at_p(res['scal'], 1) == exp['scal']
    return out


def adm_and_conformal_checks(S):
    global DE
    DE = 2
    Om, gam, gam0, hess, boxQ, ric_ok = gamma_data(S)
    Q = Qjet(S)
    g, N, conf, a2 = build_metric(S, Om, Q, 2)
    idx = [0, 1, 2, 3, 4]
    G, ginv = christoffel_diag(g, idx)
    R = ricci(G, idx)
    Rs = ricci_scalar(R, ginv, idx)
    sl = [1, 2, 3, 4]
    qmet = {m: g[m] for m in sl}
    Gq, qinv = christoffel_diag(qmet, sl)
    Rq = ricci(Gq, sl)
    R4 = ricci_scalar(Rq, qinv, sl)
    # sqrt(-q) = (a^2 conf Om)^2 ; sqrt(-g) = N sqrt(-q)
    s1 = jmuln(a2, conf, Om)
    sq = jmul(s1, s1)
    sg = jmul(N, sq)
    Ninv = jinv(N)
    Kmix = {m: jscale(jmuln(Ninv, qinv[m], jderiv(g[m], 0)), Fr(1, 2)) for m in sl}
    K = jadd(*Kmix.values())
    KK = jadd(*[jmul(Kmix[m], Kmix[m]) for m in sl])
    lhs = {kk: v for kk, v in jmul(sg, Rs, maxdc=0).items() if cdeg(kk) == 0}
    bulk = jmuln(N, sq, jadd(R4, jmul(K, K), jscale(KK, -1)), maxdc=0)
    div_n = jderiv(jmuln(sg, K, Ninv), 0)
    div_a = {}
    for m in sl:
        div_a = jadd(div_a, jderiv(jmuln(sg, qinv[m], jderiv(N, m), Ninv), m))
    rhs = jsub(bulk, jscale(jsub(div_n, div_a), 2))
    adm_ok = all(at_p(lhs, ep) == at_p(rhs, ep) for ep in range(3))
    # conformal formula: sqrt(-q) R4 vs a^2 sqrt(-gamma) e^{2w}(12k - 6 Box w - 6 |dw|^2)
    x = jscale(jmuln(jvar(EIDX), upoly(0, S.psi), Q), 2)
    w = jscale(jsub(x, jscale(jmul(x, x), Fr(1, 2))), Fr(1, 2))     # (1/2) ln(1+x) to e^2
    sgam = jmul(Om, Om)
    boxw = {}
    for m in sl:
        boxw = jadd(boxw, jscale(jderiv(jmul(Om, jderiv(w, m)), m), ETA[m]))
    boxw = jmul(jinv(sgam), boxw)
    dw2 = {}
    for m in sl:
        dw2 = jadd(dw2, jscale(jmuln(jinv(Om), jderiv(w, m), jderiv(w, m)), ETA[m]))
    brk = jsub(jsub(jconst(12 * S.k), jscale(boxw, 6)), jscale(dw2, 6))
    conf_rhs = jmuln(a2, sgam, conf, brk, maxdc=0)
    conf_lhs = jmul(sq, R4, maxdc=0)
    conf_ok = all(at_p(conf_lhs, ep) == at_p(conf_rhs, ep) for ep in range(3))
    return {'C8_ADM_GH_identity_e0_e1_e2': adm_ok, 'C9_conformal_slice_formula_e0_e1_e2': conf_ok}


def wall_checks(S, sigma):
    """Displaced wall s = s0 + e xi Q(x), inward normal sigma * (ds - e xi dQ) normalized."""
    global DE
    DE = 1
    Om, gam, gam0, hess, boxQ, ric_ok = gamma_data(S)
    Q = Qjet(S)
    g, N, conf, a2 = build_metric(S, Om, Q, 1)
    idx = [0, 1, 2, 3, 4]
    G, ginv = christoffel_diag(g, idx)
    e = jvar(EIDX)
    zeta = jscale(jmul(e, Q), S.xi)                    # displacement u0 = e xi Q(x)
    # embedding X^A(x) = (zeta(x), x^mu); dX^A_mu
    dX = {}
    for m in range(1, 5):
        dX[(0, m)] = jderiv(zeta, m)
        for A_ in range(1, 5):
            dX[(A_, m)] = jconst(1) if A_ == m else {}
    ddX0 = {(m, n): jderiv(jderiv(zeta, m), n) for m in range(1, 5) for n in range(1, 5)}
    # fields evaluated on the wall: substitute u0 -> u0 + zeta then set u0 = 0 (degree-0 use only)
    def on_wall(j):
        return subst_s_shift(j, zeta)
    gw = {A_: on_wall(g[A_]) for A_ in idx}
    giw = {A_: jinv(gw[A_]) for A_ in idx}
    Gw = {key: on_wall(v) for key, v in G.items()}
    # normal covector dF = (1, -d zeta), normalized with g^{-1} on the wall
    dF = {0: jconst(1)}
    for m in range(1, 5):
        dF[m] = jscale(dX[(0, m)], -1)
    nrm2 = {}
    for A_ in idx:
        nrm2 = jadd(nrm2, jmuln(giw[A_], dF[A_], dF[A_]))
    # 1/sqrt(nrm2): nrm2 = c0 (1 + r); use series (1+r)^(-1/2) with exact c0 = 1/N^2-type square
    c0 = nrm2.get(ZERO_KEY)
    # c0 = g^{ss}(p) at e^0 = 1 (background g_ss = 1); require it
    assert c0 == 1
    r = jsub(nrm2, jconst(1))
    inv_sqrt = jadd(jconst(1), jscale(r, Fr(-1, 2)), jscale(jmul(r, r), Fr(3, 8)))
    n = {A_: jscale(jmul(dF[A_], inv_sqrt), sigma) for A_ in idx}
    # K_mn = -n_C (d_m d_n X^C + Gamma^C_AB dX^A_m dX^B_n)
    Kmn = {}
    for m in range(1, 5):
        for nn in range(1, 5):
            t = jmul(n[0], ddX0[(m, nn)])
            for C_ in idx:
                acc = {}
                for A_ in idx:
                    for B_ in idx:
                        x = Gw.get((C_, A_, B_))
                        if x and dX[(A_, m)] and dX[(B_, nn)]:
                            acc = jadd(acc, jmuln(x, dX[(A_, m)], dX[(B_, nn)], maxdc=1))
                if acc:
                    t = jadd(t, jmul(n[C_], acc, maxdc=0))
            Kmn[(m, nn)] = jscale(t, -1)
    # induced metric h_mn = g_AB dX^A_m dX^B_n (diagonal g)
    h = {}
    for m in range(1, 5):
        for nn in range(1, 5):
            t = {}
            for A_ in idx:
                if dX[(A_, m)] and dX[(A_, nn)]:
                    t = jadd(t, jmuln(gw[A_], dX[(A_, m)], dX[(A_, nn)], maxdc=0))
            h[(m, nn)] = t
    # invert h at p to first order in e: h = h0 + e h1 with h0 diagonal
    h0 = {m: at_p(h[(m, m)], 0) for m in range(1, 5)}
    Kmix_ok = True
    H, Hp = S.H, S.Hp
    A, psi, psi1 = S.A[0], S.psi[0], S.psi[1]
    a = S.a0
    for m in range(1, 5):
        for nn in range(1, 5):
            # (h^{-1} K)^m_n first order: h0^{-1}K1 - h0^{-1} h1 h0^{-1} K0
            K0 = {(i, j): at_p(Kmn[(i, j)], 0) for i in range(1, 5) for j in range(1, 5)}
            K1 = {(i, j): at_p(Kmn[(i, j)], 1) for i in range(1, 5) for j in range(1, 5)}
            h1 = {(i, j): at_p(h[(i, j)], 1) for i in range(1, 5) for j in range(1, 5)}
            v = K1[(m, nn)] / h0[m]
            for r_ in range(1, 5):
                v -= h1[(m, r_)] / h0[m] * K0[(r_, nn)] / h0[r_]
            ddQup = hess[(m, nn)] / gam0[m]
            expect = sigma * ((psi1 - H * A + Hp * S.xi) * S.q0 * (1 if m == nn else 0)
                              - S.xi * ddQup / a ** 2)
            if v != expect:
                Kmix_ok = False
            if m == nn:
                if K0[(m, m)] / h0[m] != sigma * H:
                    Kmix_ok = False
    # normal derivative of Phi on the wall at first order
    Phi, _ = phi_jet(S, Q)
    dPhi_w = {A_: on_wall(jderiv(Phi, A_)) for A_ in idx}
    nup = {A_: jmul(giw[A_], n[A_]) for A_ in idx}
    ndphi = {}
    for A_ in idx:
        ndphi = jadd(ndphi, jmul(nup[A_], dPhi_w[A_], maxdc=0))
    T, T1 = S.T, S.T1
    f, f1 = S.f[0], S.f[1]
    nd_ok = (at_p(ndphi, 0) == sigma * T and
             at_p(ndphi, 1) == sigma * (f1 - A * T + T1 * S.xi) * S.q0)
    return {'C10_wall_extrinsic_curvature': Kmix_ok, 'C11_wall_normal_derivative': nd_ok}


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261114
    npts = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    rng = random.Random(seed)
    print("seed", seed, "points per case", npts)
    allok = True
    for k in (Fr(1), Fr(1, 3), Fr(0), Fr(-1), Fr(-5, 2)):
        for trial in range(npts):
            for onshell in (False, True):
                S = make_setup(rng, k, onshell)
                res = run_field_checks(S, onshell)
                res.update(adm_and_conformal_checks(S))
                for sigma in (1, -1):
                    w = wall_checks(S, sigma)
                    res.update({kk + ('_sigma+1' if sigma == 1 else '_sigma-1'): vv for kk, vv in w.items()})
                ok = all(res.values())
                allok &= ok
                print(f"k={k} trial={trial} onshell_bg={onshell} ok={ok} {res}")
                sys.stdout.flush()
    print("ALL_PASS" if allok else "SOME_FAIL")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
