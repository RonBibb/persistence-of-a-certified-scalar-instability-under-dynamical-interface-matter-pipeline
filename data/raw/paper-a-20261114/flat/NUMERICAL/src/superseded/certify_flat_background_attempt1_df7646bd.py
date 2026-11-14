"""Certified k = 0 background for a one-turn flat-slice example (stretch goal).

Derived from a copy of the archived producer
papers/paper-A/github-release/producer/certify_family.py
(SHA-256 2a6aa0b8...e810; unmodified copy kept as certify_family_COPY_UNMODIFIED.py).
The interval arithmetic helpers, the Dual class, the Picard whole-cell box `step`
and the degree-4 Taylor polynomial with fifth-order remainder `coefficients` /
`evaluate` are carried over verbatim; `initial`, the potential parameters and the
fixed-endpoint flow are new.

Model: V = 2 Phi^2 (m2 = 4, q = 0), k = 0, lower launch W = 0, Phi = 1,
T = -1/2, H = -sqrt(11)/4 (Hamiltonian constraint at k = 0: H^2 = 11/16), E = 1/a = 1.
Integrate to D = 3/4 with h = 1/8192 (6144 cells).  Wall data are then defined
from the exact solution (ANALYTIC_AUDIT A12): tau_a(1) = -6 H_a, tau_a'(1) = 2 T_a,
tau_b(Phi_b) = 6 H_b, tau_b'(Phi_b) = -2 T_b; perturbative Hessians free.
Predicates: positive E on every cell, background-constraint containment on every
cell (consistency gate), T(D) > 0 and T'(D) > 0 on the endpoint enclosure.
With T_a = -1/2 < 0 exact and V'' = 4 >= 0, Lemma 1 (k = 0 form, audit A4) gives
exactly one simple turn and T' > 0, i.e. (RT1) with n = 1.
"""
import hashlib, json, math, os, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT = Path(__file__).resolve().parent
from flint import arb, fmpq, ctx
ctx.prec = 768; ctx.threads = 1
OUT = ROOT / 'flat_certificate'; OUT.mkdir(exist_ok=True)


# ---- verbatim helpers from the archived producer ----
def exact(x): return x if isinstance(x, arb) else arb(fmpq(str(Q(x))))
def bounds(x): return x.lower().fmpq(), x.upper().fmpq()
def interval(a, b): a, b = fmpq(str(a)), fmpq(str(b)); return arb((a + b) / 2, (b - a) / 2)
def hull(a, b): al, ah = bounds(a); bl, bh = bounds(b); return interval(min(al, bl), max(ah, bh))
def pad(x): lo, hi = bounds(x); e = (hi - lo) / 8 + fmpq(1, 2**640); return interval(lo - e, hi + e)
def inside(a, b): al, ah = bounds(a); bl, bh = bounds(b); return bl < al and ah < bh
def pack(x): lo, hi = bounds(x); return {'bounds': [str(lo), str(hi)], 'approx': [float(lo), float(hi)]}
def save(p, x):
    t = p.with_suffix('.tmp')
    with t.open('w') as f: json.dump(x, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(t, p)
def need(ok, label):
    if not ok: raise RuntimeError(label)
class Dual:
    def __init__(self, v, d=0): self.v = exact(v); self.d = exact(d)
    def __add__(self, b):
        b = asdual(b); return Dual(self.v + b.v, self.d + b.d)
    __radd__ = __add__
    def __neg__(self): return Dual(-self.v, -self.d)
    def __sub__(self, b): return self + -asdual(b)
    def __rsub__(self, b): return asdual(b) + -self
    def __mul__(self, b):
        b = asdual(b); return Dual(self.v * b.v, self.d * b.v + self.v * b.d)
    __rmul__ = __mul__
    def __truediv__(self, b):
        b = asdual(b); return Dual(self.v / b.v, (self.d * b.v - self.v * b.d) / (b.v * b.v))
def asdual(x): return x if isinstance(x, Dual) else Dual(x)
def flatten(y): return [x.v for x in y] + [x.d for x in y]
def dualize(y): return [Dual(v, d) for v, d in zip(y[:5], y[5:])]
def potential(P, p): return p['m2'] * P * P / 2 + p['q'] * P * P * P * P / 4
def slope(P, p): return p['m2'] * P + p['q'] * P * P * P
def rhs(y, p, k):
    W, H, P, T, E = dualize(y)
    return flatten([H, -T * T / 3 - k * E * E, T, slope(P, p) - 4 * H * T, -H * E])
def conv(a, b, n): return sum((a[j] * b[n - j] for j in range(n + 1)), Dual(0))
def coefficients(y, nmax, p, k):
    rows = [[v] for v in dualize(y)]; W, H, P, T, E = rows; pp = []
    for n in range(nmax):
        pp.append(conv(P, P, n))
        vals = [H[n], -conv(T, T, n) / 3 - k * conv(E, E, n), T[n], p['m2'] * P[n] + p['q'] * conv(pp, P, n) - 4 * conv(H, T, n), -conv(H, E, n)]
        for row, v in zip(rows, vals): row.append(v / (n + 1))
    return [[z.v for z in row] for row in rows] + [[z.d for z in row] for row in rows]
def step(y, h, p, k):
    dt = interval(0, h); box = [pad(hull(a, a + dt * v)) for a, v in zip(y, rhs(y, p, k))]
    for it in range(32):
        image = [hull(a, a + dt * v) for a, v in zip(y, rhs(box, p, k))]
        if all(inside(a, b) for a, b in zip(image, box)): break
        box = [pad(hull(a, b)) for a, b in zip(image, box)]
    else: raise RuntimeError('PICARD_FAIL')
    point = coefficients(y, 4, p, k); rem = [r[5] for r in coefficients(box, 5, p, k)]
    return evaluate(point, rem, h), {'point': point, 'rem': rem, 'box': box, 'h': h}
def evaluate(point, rem, t):
    yy = []
    for row, r in zip(point, rem):
        v = r
        for c in reversed(row): v = v * t + c
        yy.append(v)
    return yy
# ---- end verbatim helpers ----


def initial_flat(p):
    """k = 0 launch: W = 0, Phi = 1, T = -1/2, H = -sqrt(11)/4, E = 1 (no sensitivity)."""
    Ha = -arb(11).sqrt() / 4
    y = flatten([Dual(0), Dual(Ha), Dual(1), Dual(exact('-1/2')), Dual(1)])
    return y, Dual(0)


def main():
    need(not (OUT / 'RESULT.json').exists() and not (OUT / 'FAILURE.json').exists(), 'NO_RETRY')
    p = {'m2': exact(4), 'q': exact(0)}
    y, k = initial_flat(p)
    W, H, P, T, E = y[:5]
    # exact launch checks: constraint at k=0 and endpoint signs at the lower wall
    c0 = H * H - 1 - T * T / 12 + potential(P, p) / 6
    need(c0.contains(0), 'LAUNCH_CONSTRAINT')
    Tpa = slope(P, p) - 4 * H * T
    need(T.upper() < 0 and Tpa.lower() > 0, 'LOWER_SIGNS')
    h = fmpq(1, 8192); n = 6144  # D = 3/4
    start = time.monotonic(); profile = {}
    source = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for j in range(n):
        y, cell = step(y, h, p, k)
        Wb, Hb, Pb, Tb, Eb = cell['box'][:5]
        Tpb = slope(Pb, p) - 4 * Hb * Tb
        need(all(v.is_finite() for v in y), 'NONFINITE'); need(Eb.lower() > 0, 'POSITIVE_E')
        inv = Hb * Hb - 1 - Tb * Tb / 12 + potential(Pb, p) / 6
        need(inv.contains(0), 'BACKGROUND_CONSTRAINT_ESCAPE')
        for key, v in [('W', Wb), ('H', Hb), ('P', Pb), ('T', Tb), ('Tp', Tpb), ('E', Eb)]:
            profile[key] = v if key not in profile else hull(profile[key], v)
        if j % 512 == 0:
            save(OUT / 'progress.json', {'state': 'RUNNING', 'completed_cells': j + 1, 'total_cells': n,
                                         'elapsed_seconds': time.monotonic() - start})
        need(time.monotonic() - start < 1800, 'TIMEOUT')
    W, H, P, T, E = y[:5]
    Tp = slope(P, p) - 4 * H * T
    preds = {'T_a_negative_exact': True, 'Tprime_a_positive_exact': True,
             'positive_E_all_cells': True, 'constraint_contained_all_cells': True,
             'T_D_positive': bool(T.lower() > 0), 'Tprime_D_positive': bool(Tp.lower() > 0),
             'convex_potential': True}
    result = {'status': 'COMPLETE' if all(preds.values()) else 'PREDICATE_FAILED',
              'model': {'V': '2*Phi^2', 'k': 0, 'Phi_a': '1', 'T_a': '-1/2', 'H_a': '-sqrt(11)/4', 'D': '3/4',
                        'h': '1/8192', 'cells': n},
              'endpoint': {'W': pack(W), 'H': pack(H), 'Phi': pack(P), 'T': pack(T), 'Tprime': pack(Tp),
                           'E': pack(E)},
              'wall_data_from_solution': {'tau_a': pack(-6 * (-arb(11).sqrt() / 4)), 'tau_a_slope': '-1',
                                          'tau_b': pack(6 * H), 'tau_b_slope': pack(-2 * T)},
              'profile_hulls': {key: pack(v) for key, v in profile.items()},
              'predicates': preds, 'elapsed_seconds': time.monotonic() - start, 'source_sha256': source,
              'scope': ('Certified existence and (RT1) for one exact k = 0 background with one fine-tuned '
                        'upper wall (wall data defined from the solution). The count n = 1 then follows '
                        'from Lemma 1 (k = 0) and the audited k = 0 Theorem 1; no spectral certificate.')}
    save(OUT / 'RESULT.json', result); print(json.dumps(result['predicates']))


if __name__ == '__main__':
    try: main()
    except BaseException as e:
        save(OUT / 'FAILURE.json', {'status': 'TECHNICAL_INCOMPLETE', 'error': repr(e), 'traceback': traceback.format_exc()})
        raise
