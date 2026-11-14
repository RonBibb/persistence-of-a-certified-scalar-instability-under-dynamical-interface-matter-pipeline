#!/usr/bin/env python3
"""Exact radial-identity checks for DERIVATION.md (F04).  Standard library only.

s-derivatives are computed exactly by forward-mode dual numbers over Fractions:
each base quantity carries (value, d/ds value) with d/ds given by the background
system (9) and, where stated, by the rows of (10).  Partial derivatives of the
quadratic radial functional l are exact central differences with unit step.

Checks (random rational points; k drawn from positive, zero and negative values):
  R1  d/ds of the Hamiltonian constraint vanishes identically along (9)
  R2  (H1) on the sector (A=-2psi, row 1) equals -C, C = Tg - T'f + (2T^2 - 3 lam/a^2) psi
  R3  (S) on the sector with g' from row 3 vanishes identically
  R4  C' = -4 H C identically in (psi, f, g) along (9)-(10)
  R5  Green identity (M1) on the constraint surface for two modes
  R6  EL_A(l) = -a^4 (H1),  EL_f(l) = a^4 (S),  identically off the sector
  R7  EL_psi(l) = -a^4 * [trace formula of C6]  identically; EL_psi = 0 on the sector
  R8  conjunct F_j.dl/dF'(F_i) - F_i.dl/dF'(F_j) = a^4 (f_i L_j - L_i f_j) on the sector
  R9  boundary terms: B_i = -a^4(8 sigma T psi f + kappa f^2/2) and natural BCs
      give 2 sigma L = kappa f and row 1 at the wall
  R10 raw no-derivative omega^2 and alpha*omega coefficients reduce to -12 k a^2
  R11 FW2 wall algebra: W at a wall = sigma (mu_i - mu_j) a^2 z_i^T K z_j / 2;
      Gamma'(mu) = -a^-2 v^T K v (exact dual numbers); B > 0 for mu < 0
  R12 norm response: alpha-shift identity (mu_i-mu_j)/(kappa_i-kappa_j) = a^4 f_i f_j / Z_ij
      reproduced from the wall values of W (algebraic form)
"""
import random
import sys
from fractions import Fraction as Fr


class D:
    """Dual number (value, s-derivative) over Fractions."""
    __slots__ = ("v", "d")

    def __init__(self, v, d=0):
        self.v = Fr(v)
        self.d = Fr(d)

    @staticmethod
    def c(x):
        return x if isinstance(x, D) else D(x, 0)

    def __add__(self, o):
        o = D.c(o)
        return D(self.v + o.v, self.d + o.d)

    __radd__ = __add__

    def __sub__(self, o):
        o = D.c(o)
        return D(self.v - o.v, self.d - o.d)

    def __rsub__(self, o):
        return D.c(o) - self

    def __neg__(self):
        return D(-self.v, -self.d)

    def __mul__(self, o):
        o = D.c(o)
        return D(self.v * o.v, self.v * o.d + self.d * o.v)

    __rmul__ = __mul__

    def __truediv__(self, o):
        o = D.c(o)
        return D(self.v / o.v, (self.d * o.v - self.v * o.d) / (o.v * o.v))

    def __rtruediv__(self, o):
        return D.c(o) / self

    def __pow__(self, n):
        out = D(1)
        for _ in range(n):
            out = out * self
        return out


def rnd(rng, nonzero=False, pos=False):
    while True:
        v = Fr(rng.randint(-60, 60), rng.randint(1, 7))
        if pos:
            v = abs(v)
        if (not nonzero and not pos) or v != 0:
            return v


def background(rng, k):
    a = rnd(rng, pos=True)
    H, T, V1, V2, V3 = (rnd(rng) for _ in range(5))
    T = T if T != 0 else Fr(1, 3)
    Hp = -T * T / 3 - k / (a * a)
    Tp = V1 - 4 * H * T
    bg = dict(a=D(a, H * a), H=D(H, Hp), T=D(T, Tp), V1=D(V1, V2 * T), V2=D(V2, V3 * T),
              V3=V3, k=Fr(k), Hp=Hp, Tp=Tp)
    return bg


def row1(bg, psi, f):
    return -2 * bg['H'] * psi - bg['T'] * f / 3


def row3(bg, mu, psi, f, g):
    a, H, T, V1, V2 = bg['a'], bg['H'], bg['T'], bg['V1'], bg['V2']
    return -4 * H * g + (V2 - mu / (a * a) + 2 * T * T) * f + (12 * H * T - 4 * V1) * psi


def mode_duals(bg, mu, psi, f, g):
    """psi, f, g as duals along (10)."""
    P = D(psi)
    Fv = D(f)
    G = D(g)
    dpsi = row1(bg, P, Fv).v
    dg = row3(bg, mu, P, Fv, G).v
    return D(psi, dpsi), D(f, g), D(g, dg)


def constraint(bg, mu, psi, f, g):
    a, T = bg['a'], bg['T']
    lam = mu + 4 * bg['k']
    Tp = bg['V1'] - 4 * bg['H'] * T
    return T * g - Tp * f + (2 * T * T - 3 * lam / (a * a)) * psi


def H1(bg, mu, A, psi, psi1, f, f1):
    a, H, T, V1 = bg['a'], bg['H'], bg['T'], bg['V1']
    lam = mu + 4 * bg['k']
    return 3 * lam * psi / (a * a) + 12 * H * (psi1 - H * A) - T * f1 + T * T * A + V1 * f


def S_onshell(bg, mu, A, A1, psi, psi1, f, f1, f2):
    a, H, T, V1, V2 = bg['a'], bg['H'], bg['T'], bg['V1'], bg['V2']
    return f2 + 4 * H * f1 + 4 * T * psi1 - T * A1 - 2 * A * V1 - V2 * f + mu * f / (a * a)


def ell(bg, mu, psi, psi1, A, f, f1):
    a, H, T, V1, V2, k = bg['a'], bg['H'], bg['T'], bg['V1'], bg['V2'], bg['k']
    a2 = a * a
    a4 = a2 * a2
    return (6 * a4 * psi1 * psi1 - Fr(1, 2) * a4 * f1 * f1 - 12 * k * a2 * psi * psi
            - 12 * k * a2 * A * psi - 12 * a4 * H * A * psi1 + a4 * T * A * f1 - a4 * V1 * A * f
            + a4 * (6 * H * H - T * T / 2) * A * A - 4 * a4 * T * psi * f1 - 4 * a4 * V1 * psi * f
            - Fr(1, 2) * a4 * V2 * f * f + Fr(1, 2) * mu * a2 * (f * f - 6 * psi * psi - 6 * A * psi))


def partial(fun, args, name):
    up = dict(args)
    dn = dict(args)
    up[name] = args[name] + 1
    dn[name] = args[name] - 1
    return (fun(**up) - fun(**dn)) / 2


def run(seed, npts):
    rng = random.Random(seed)
    res = {}

    def mark(key, ok):
        res[key] = res.get(key, True) and bool(ok)

    for k in (Fr(1), Fr(2, 7), Fr(0), Fr(-1), Fr(-9, 4)):
        for _ in range(npts):
            bg = background(rng, k)
            a, H, T, V1 = bg['a'], bg['H'], bg['T'], bg['V1']
            mu = rnd(rng)
            # R1
            Vd = None
            # V(s) along the background: V' = V1 * T ; constraint derivative
            Vval = rnd(rng)
            Vdual = D(Vval, V1.v * T.v)
            Kc = H * H - 1 - T * T / 12 + Vdual / 6 - bg['k'] / (a * a)
            mark('R1_constraint_preserved_by_(9)', Kc.d == 0)
            # sector data
            psi, f, g = rnd(rng), rnd(rng), rnd(rng)
            P, Fv, G = mode_duals(bg, mu, psi, f, g)
            A = -2 * P
            C = constraint(bg, mu, P, Fv, G)
            mark('R2_H1_on_sector_equals_-C', H1(bg, mu, A.v, P.v, P.d, Fv.v, Fv.d).v == -C.v)
            mark('R3_S_on_sector_equals_row3', S_onshell(bg, mu, A.v, A.d, P.v, P.d, Fv.v, Fv.d, G.d).v == 0)
            mark('R4_Cprime_equals_-4HC', C.d == -4 * H.v * C.v)
            # R5 Green identity on the constraint surface
            mu2 = rnd(rng)
            psi2_, f2_ = rnd(rng), rnd(rng)

            def g_on_surface(m, ps, ff):
                lam = m + 4 * bg['k']
                return (bg['Tp'] * ff - (2 * T.v * T.v - 3 * lam / (a.v * a.v)) * ps) / T.v
            gi = g_on_surface(mu, psi, f)
            gj = g_on_surface(mu2, psi2_, f2_)
            Pi, Fi, Gi = mode_duals(bg, mu, psi, f, gi)
            Pj, Fj, Gj = mode_duals(bg, mu2, psi2_, f2_, gj)
            Li = Gi + 2 * T * Pi
            Lj = Gj + 2 * T * Pj
            W = a ** 4 * (Fi * Lj - Li * Fj)
            mark('R5_constraint_zero_check', constraint(bg, mu, Pi, Fi, Gi).v == 0 and constraint(bg, mu2, Pj, Fj, Gj).v == 0)
            mark('R5_Green_identity_M1', W.d == (mu - mu2) * a.v ** 2 * (Fi.v * Fj.v + 6 * Pi.v * Pj.v))
            # R6, R7: EL equations of l with free jets
            fr = dict(psi=D(rnd(rng), rnd(rng)), psi1=None, A=D(rnd(rng), rnd(rng)),
                      f=D(rnd(rng), rnd(rng)), f1=None)
            psi1v, psi2v = fr['psi'].d, rnd(rng)
            f1v, f2v = fr['f'].d, rnd(rng)
            fr['psi1'] = D(psi1v, psi2v)
            fr['f1'] = D(f1v, f2v)
            A1v = fr['A'].d

            def L_(psi, psi1, A, f, f1):
                return ell(bg, mu, psi, psi1, A, f, f1)
            EL_A = partial(L_, fr, 'A')
            EL_f = partial(L_, fr, 'f') - partial(L_, fr, 'f1').d
            EL_psi = partial(L_, fr, 'psi') - partial(L_, fr, 'psi1').d
            h1 = H1(bg, mu, fr['A'].v, fr['psi'].v, psi1v, fr['f'].v, f1v)
            s1 = S_onshell(bg, mu, fr['A'].v, A1v, fr['psi'].v, psi1v, fr['f'].v, f1v, f2v)
            a4 = a.v ** 4
            mark('R6_EL_A_equals_-a4_H1', EL_A.v == -a4 * h1.v)
            mark('R6_EL_f_equals_a4_S', EL_f.v == a4 * s1.v)
            Av, psv, fv = fr['A'].v, fr['psi'].v, fr['f'].v
            trace = (12 * (psi2v - bg['Hp'] * Av - H.v * A1v + 4 * H.v * (psi1v - H.v * Av))
                     + (24 * bg['k'] * psv + 12 * bg['k'] * Av) / a.v ** 2 + 4 * T.v * f1v + 4 * V1.v * fv) \
                + 3 * (Av + 2 * psv) * mu / a.v ** 2
            mark('R7_EL_psi_equals_-a4_trace', EL_psi.v == -a4 * trace)
            # EL_psi on the sector: psi1 = row1, A = -2 psi, psi2 = (row1)'
            secP, secF, secG = mode_duals(bg, mu, psi, f, g)
            r1 = row1(bg, secP, secF)
            fr2 = dict(psi=D(secP.v, secP.d), psi1=D(r1.v, r1.d), A=D(-2 * secP.v, -2 * secP.d),
                       f=D(secF.v, secF.d), f1=D(secG.v, secG.d))
            EL_psi_sec = partial(L_, fr2, 'psi') - partial(L_, fr2, 'psi1').d
            EL_f_sec = partial(L_, fr2, 'f') - partial(L_, fr2, 'f1').d
            EL_A_sec = partial(L_, fr2, 'A')
            Csec = constraint(bg, mu, secP, secF, secG)
            mark('R7_EL_psi_zero_on_sector', EL_psi_sec.v == 0)
            mark('R6_EL_f_zero_on_sector', EL_f_sec.v == 0)
            mark('R6_EL_A_equals_a4_C_on_sector', EL_A_sec.v == a4 * Csec.v)
            # R8 conjunct identity for two sector modes (on the constraint surface)
            def Pis(Pm, Fm, Gm):
                r = row1(bg, Pm, Fm)
                args = dict(psi=Pm.v, psi1=r.v, A=-2 * Pm.v, f=Fm.v, f1=Gm.v)

                def Lv(psi, psi1, A, f, f1):
                    return ell({kk: (vv.v if isinstance(vv, D) else vv) for kk, vv in bg.items()}, mu, psi, psi1, A, f, f1)
                return partial(Lv, args, 'f1'), partial(Lv, args, 'psi1')
            Pfi, Ppi = Pis(Pi, Fi, Gi)
            Pfj, Ppj = Pis(Pj, Fj, Gj)
            conj = Fj.v * Pfi + Pj.v * Ppi - (Fi.v * Pfj + Pi.v * Ppj)
            mark('R8_conjunct_equals_W', conj == W.v)
            # R9 boundary terms and natural BCs at either wall
            kap = abs(rnd(rng))
            for sig in (1, -1):
                tau, taup = -6 * sig * H.v, 2 * sig * T.v
                Bsum = -2 * sig * 24 * a4 * H.v * psi ** 2 - a4 * (8 * tau * psi ** 2 + 4 * taup * psi * f + kap * f * f / 2)
                mark('R9_boundary_term_form', Bsum == -a4 * (8 * sig * T.v * psi * f + kap * f * f / 2))
                # choose g so that the wall law 2 sigma L = kappa f holds, then test natural BCs
                gw = sig * kap * f / 2 - 2 * T.v * psi
                Pw, Fw, Gw = mode_duals(bg, mu, psi, f, gw)
                r = row1(bg, Pw, Fw)
                Pf = -a4 * (Fw.d - T.v * (-2 * Pw.v) + 4 * T.v * Pw.v)
                Pp = 12 * a4 * (r.v - H.v * (-2 * Pw.v))
                cf = -2 * sig * Pf - a4 * (8 * sig * T.v * Pw.v + kap * Fw.v)
                cp = -2 * sig * Pp - 8 * sig * a4 * T.v * Fw.v
                mark('R9_natural_BC_f_gives_wall_law', cf == 0)
                mark('R9_natural_BC_psi_is_row1', cp == 0)
            # R10 raw coefficient algebra
            V0 = 6 + T.v ** 2 / 2 + 6 * bg['k'] / a.v ** 2 - 6 * H.v ** 2
            a2v = a.v ** 2
            raw_w2 = 12 * bg['k'] * a2v + 48 * a4 * H.v ** 2 + 48 * a4 - 4 * a4 * T.v ** 2 - 8 * a4 * V0
            a4H_prime = a4 * (4 * H.v ** 2 + bg['Hp'])
            mark('R10_omega2_coefficient', raw_w2 - 24 * a4H_prime == -12 * bg['k'] * a2v)
            raw_aw = 12 * bg['k'] * a2v - 24 * a4 * H.v ** 2 + 24 * a4 + 2 * a4 * T.v ** 2 - 4 * a4 * V0
            mark('R10_alpha_omega_coefficient', raw_aw == -12 * bg['k'] * a2v)
            # R12 norm response from wall values (algebraic): with L = sigma kappa f/2 at one wall
            ki, kj = abs(rnd(rng)), abs(rnd(rng))
            fi, fj = rnd(rng, nonzero=True), rnd(rng, nonzero=True)
            for sig in (1, -1):
                Wwall = a4 * (fi * (sig * kj * fj / 2) - (sig * ki * fi / 2) * fj)
                # integral identity: W(D) - W(0) = (mu_i - mu_j) Z_ij / 2 ; wall a enters with -, wall b with +
                lhs = -Wwall if sig == 1 else Wwall
                # => (mu_i - mu_j) Z_ij / 2 = lhs  ;  lhs = a^4 f_i f_j (k_i - k_j)/2 in both cases
                mark('R12_wall_value_gives_response', lhs == a4 * fi * fj * (ki - kj) / 2)
    # R11 FW2 algebra
    for _ in range(npts * 5):
        n = rng.randint(1, 3)          # number of chi fields
        dim = n + 1

        def rmat(r, c):
            return [[rnd(rng) for _ in range(c)] for _ in range(r)]

        def mt(Mx):
            return [list(r) for r in zip(*Mx)]

        def mm(X, Y):
            return [[sum(X[i][t] * Y[t][j] for t in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
        Mh = rmat(dim, dim)
        Hm = mm(mt(Mh), Mh)
        Mk = rmat(dim, dim)
        Km = mm(mt(Mk), Mk)
        for i in range(1, dim):
            Km[i][i] += 1     # chi block of K positive definite
        aw = rnd(rng, pos=True)
        sig = rng.choice((1, -1))

        def Qm(m):
            x = -m / aw ** 2
            return [[Hm[i][j] + x * Km[i][j] for j in range(dim)] for i in range(dim)]

        def solve(Mx, b):
            n_ = len(Mx)
            Aug = [list(Mx[i]) + [b[i]] for i in range(n_)]
            for c in range(n_):
                p = next(r for r in range(c, n_) if Aug[r][c] != 0)
                Aug[c], Aug[p] = Aug[p], Aug[c]
                for r in range(n_):
                    if r != c and Aug[r][c] != 0:
                        fac = Aug[r][c] / Aug[c][c]
                        Aug[r] = [Aug[r][t] - fac * Aug[c][t] for t in range(n_ + 1)]
            return [Aug[i][n_] / Aug[i][i] for i in range(n_)]

        def zvec(m, f0):
            Q = Qm(m)
            B = [[Q[i][j] for j in range(1, dim)] for i in range(1, dim)]
            c = [Q[i][0] for i in range(1, dim)]
            u = solve(B, [-f0 * ci for ci in c])
            return [f0] + u, Q, B, c
        mi, mj = -abs(rnd(rng, nonzero=True)), -abs(rnd(rng, nonzero=True))
        fi0, fj0 = rnd(rng, nonzero=True), rnd(rng, nonzero=True)
        zi, Qi, Bi, ci = zvec(mi, fi0)
        zj, Qj, Bj, cj = zvec(mj, fj0)
        chi_ok = all(sum(Qi[r][t] * zi[t] for t in range(dim)) == 0 for r in range(1, dim))
        Li = sig * sum(Qi[0][t] * zi[t] for t in range(dim)) / 2
        Lj = sig * sum(Qj[0][t] * zj[t] for t in range(dim)) / 2
        a4w = aw ** 4
        Wwall = a4w * (zi[0] * Lj - Li * zj[0])
        zKz = sum(zi[r] * Km[r][t] * zj[t] for r in range(dim) for t in range(dim))
        mark('R11_chi_rows_solved', chi_ok)
        mark('R11_wall_W_value', Wwall == sig * (mi - mj) * aw ** 2 * zKz / 2)
        # Gamma'(mu) by dual numbers
        md = D(mi, 1)
        xd = -md / (aw * aw)
        Qd = [[Hm[i][j] + xd * Km[i][j] for j in range(dim)] for i in range(dim)]
        # Schur complement Gamma = Q00 - c^T B^{-1} c via dual Gaussian elimination
        Bd = [[Qd[i][j] for j in range(1, dim)] for i in range(1, dim)]
        cd = [Qd[i][0] for i in range(1, dim)]
        nB = len(Bd)
        Aug = [list(Bd[i]) + [cd[i]] for i in range(nB)]
        for c_ in range(nB):
            p = next(r for r in range(c_, nB) if Aug[r][c_].v != 0)
            Aug[c_], Aug[p] = Aug[p], Aug[c_]
            for r in range(nB):
                if r != c_ and (Aug[r][c_].v != 0 or Aug[r][c_].d != 0):
                    fac = Aug[r][c_] / Aug[c_][c_]
                    Aug[r] = [Aug[r][t] - fac * Aug[c_][t] for t in range(nB + 1)]
        sol = [Aug[i][nB] / Aug[i][i] for i in range(nB)]
        Gam = Qd[0][0] - sum((cd[i] * sol[i] for i in range(nB)), D(0))
        v = [Fr(1)] + [-s.v for s in sol]
        vKv = sum(v[r] * Km[r][t] * v[t] for r in range(dim) for t in range(dim))
        mark('R11_Gamma_prime_envelope', Gam.d == -vKv / aw ** 2)
        # B positive definite for mu < 0: check all leading principal minors > 0
        def det(Mx):
            Mx = [list(r) for r in Mx]
            n_ = len(Mx)
            dt = Fr(1)
            for c_ in range(n_):
                p = next((r for r in range(c_, n_) if Mx[r][c_] != 0), None)
                if p is None:
                    return Fr(0)
                if p != c_:
                    Mx[c_], Mx[p] = Mx[p], Mx[c_]
                    dt = -dt
                dt *= Mx[c_][c_]
                for r in range(c_ + 1, n_):
                    fac = Mx[r][c_] / Mx[c_][c_]
                    Mx[r] = [Mx[r][t] - fac * Mx[c_][t] for t in range(n_)]
            return dt
        mark('R11_B_positive_for_mu_negative', all(det([row[:m] for row in Bi[:m]]) > 0 for m in range(1, len(Bi) + 1)))
        mark('R11_Gamma_nonnegative', Gam.v >= 0)
    return res


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20261114
    npts = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    res = run(seed, npts)
    for kk in sorted(res):
        print(f"{kk}: {'PASS' if res[kk] else 'FAIL'}")
    ok = all(res.values())
    print("ALL_PASS" if ok else "SOME_FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
