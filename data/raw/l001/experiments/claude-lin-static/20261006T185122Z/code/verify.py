"""Independent verifier for the deterministic knot-selection replay.

Imports no producer, representation or reference module. It rebuilds the exact-input
coordinate maps in outward Arb arithmetic (768 bits) from the bound native pieces, derives
the floating-point knot rules by exact emulation of round-to-nearest-even binary arithmetic,
evaluates every saved grid independently and re-decides every gate it can recompute.

Three kinds of record:
  shared gates          same IDs as the producer, recomputed here; flags must agree;
  verifier-only gates   extra scientific gates (prefix X), grouped by hypothesis;
  integrity checks      group V: record consistency, bindings, agreement, process state.
Only an integrity failure (including a shared-gate disagreement) makes the result
UNRESOLVED_VERIFICATION. Otherwise the classification computed here is final.

Usage (Linux, Research root, through slot_run.sh):  python -B <run>/code/verify.py run
Synthetic dry run (preflight only):                  python -B <run>/code/verify.py fixture <context.json>
"""
import hashlib
import json
import math
import os
import platform
import signal
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

from flint import arb, fmpq, ctx

RUN = Path(__file__).resolve().parents[1]
BRANCH = Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches')
REAL = {
    'native': BRANCH / '01-horizon-core/d1-native-cauchy-20261005T201829Z',
    'grid_dir': BRANCH / '01-horizon-core/d1-spatial-evolution-20261005T232000Z/inputs',
    'spatial_root': BRANCH / '01-horizon-core/d1-spatial-evolution-20261005T232000Z',
    'admission_verification': BRANCH / '01-horizon-core/d1-evolution-admission-20261005T214600Z/VERIFICATION.json',
    'finite': BRANCH / '02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z',
    'connected_audit': BRANCH / '02-event-horizon/lin-c4-connected-branch-20261006T004500Z/INDEPENDENT_AUDIT.json',
    'identity': BRANCH / '02-event-horizon/lin-c4-evolution-identity-r1-20261006T051000Z',
    'out': RUN / 'outputs', 'verification': RUN / 'verification',
    'level': 'fine_c4', 'cases': [0, 3, 4], 'degrees': [160, 192], 'dps': [80, 100], 'old_rule_dps': 80,
    'fixture': False}
GATE = Fraction(1, 10 ** 50)
MARGIN = Fraction(1, 10 ** 40)
ROW_GATE_02 = Fraction(1, 10 ** 10)
ROW_GATE_4 = Fraction(1, 10 ** 12)
TARGETS = {0: Fraction(0), 3: Fraction(1, 200000), 4: Fraction(-1, 200000)}
RULES = ('canonical', 'old80', 'floor_at_p')
FAMILIES = ('Hamiltonian', 'momentum', 'strong wall order 0', 'strong wall order 2', 'strong wall order 4',
            'weak wall order 0', 'weak wall order 2', 'weak wall order 4', 'inverse map derivative')


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def write_once(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError('Refuse to overwrite ' + str(path))
    text = json.dumps(data, indent=1, sort_keys=True, allow_nan=False) + '\n'
    fd, name = tempfile.mkstemp(prefix=path.name + '.uncommitted-', dir=path.parent)
    with os.fdopen(fd, 'w') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(name, path)
    path.chmod(0o444)


def Q(text):
    return Fraction(str(text))


def pow2(e):
    return Fraction(2) ** e if e >= 0 else Fraction(1, 2 ** (-e))


def pow10(e):
    return Fraction(10) ** e if e >= 0 else Fraction(1, 10 ** (-e))


def pair(p):
    return int(p[0]) * pow2(int(p[1]))


def A(x):
    """Exact rational to an Arb ball; Arb balls pass through."""
    if isinstance(x, arb):
        return x
    x = Fraction(x)
    return arb(fmpq(int(x.numerator), int(x.denominator)))


def up(x):
    """Rigorous upper bound of |x| as an exact Fraction."""
    q = abs(x).upper().fmpq()
    return Fraction(int(q.p), int(q.q))


def lo(x):
    q = x.lower().fmpq()
    return Fraction(int(q.p), int(q.q))


def hi(x):
    q = x.upper().fmpq()
    return Fraction(int(q.p), int(q.q))


def show(x, digits=7):
    """Exact decimal display, truncated to the requested significant digits."""
    if x is None:
        return None
    x = Fraction(x)
    if x == 0:
        return '0'
    sign = '-' if x < 0 else ''
    x = abs(x)
    e = len(str(x.numerator)) - len(str(x.denominator))
    while pow10(e) > x:
        e -= 1
    while pow10(e + 1) <= x:
        e += 1
    m = str(math.floor(x * pow10(digits - 1 - e)))
    return f'{sign}{m[0]}.{m[1:]}e{e:+d}'


def horner(row, z):
    v = arb(0)
    for c in reversed(row):
        v = v * z + c
    return v


def cell_interval(w):
    half = fmpq(int(w.numerator), 2 * int(w.denominator))
    return arb(half, half)


def arb_powers(w, n):
    out = [arb(1)]
    for _ in range(n):
        out.append(out[-1] * w)
    return out


def same_shape(a, b):
    if len(a) != len(b) or any(len(x) != len(y) for x, y in zip(a, b)):
        raise RuntimeError('Representation shape mismatch')


# ---------- exact emulation of mpmath round-to-nearest-even binary arithmetic ----------

def mp_prec(dps):
    """mpmath's decimal-to-binary precision rule."""
    return max(1, int(round((int(dps) + 1) * 3.3219280948873626)))


def rne(r, prec):
    """Round a rational to the nearest binary float with prec significant bits, ties to even."""
    r = Fraction(r)
    if r == 0:
        return r
    sign = -1 if r < 0 else 1
    r = abs(r)
    e = r.numerator.bit_length() - r.denominator.bit_length()
    while pow2(e) > r:
        e -= 1
    while pow2(e + 1) <= r:
        e += 1
    scale = pow2(e - prec + 1)
    scaled = r / scale
    m = scaled.numerator // scaled.denominator
    rem = scaled - m
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and m % 2 == 1):
        m += 1
    return sign * m * scale


def floor_table(h_text, prec, cells):
    """clamp(floor(fl(fl(i*h)/h))) with h parsed by correct rounding at prec bits."""
    hp = rne(Q(h_text), prec)
    table = []
    for i in range(cells):
        s = rne(i * hp, prec)
        quotient = rne(s / hp, prec)
        table.append(max(0, min(cells - 1, math.floor(quotient))))
    return table


# ---------- independent exact-input coordinate map in Arb ----------

def taylor_shift(row, z, n):
    """Coefficients in t of p(z+t), orders 0..n, for an Arb coefficient list."""
    zp = arb_powers(z, len(row))
    out = []
    for i in range(n + 1):
        v = arb(0)
        for j in range(i, len(row)):
            v += row[j] * math.comb(j, i) * zp[j - i]
        out.append(v)
    return out


def exp_series(u):
    e = [u[0].exp()]
    for n in range(1, len(u)):
        v = arb(0)
        for j in range(1, n + 1):
            v += j * u[j] * e[n - j]
        e.append(v / n)
    return e


class Native:
    def __init__(self, C):
        seed = read(Path(C['native']) / 'results' / C['level'] / 'SEED.json')
        self.seed_raw = seed
        self.h = Q(seed['h'])
        self.D = Q(seed['D'])
        self.cells = seed['cells']
        self.degree = seed['degree']
        self.widths = [self.h] * (self.cells - 1) + [self.D - (self.cells - 1) * self.h]
        self.seed = [[[A(Q(c)) for c in row] for row in block] for block in seed['segments']]
        self.dense = {}

    def case(self, C, case):
        if case not in self.dense:
            raw = read(Path(C['native']) / 'results' / C['level'] / f'case_{case}.dense.json')
            self.dense[case] = {'raw': raw, 'eps': Q(raw['epsilon']),
                                'A': [[A(Q(c)) for c in block[0]] for block in raw['segments']],
                                'corr': [A(Q(c)) for c in raw['correction']]}
        return self.dense[case]

    def piece(self, s):
        """Exact floor(s/h) clamped; nearest shared knot j and its distance; contract piece choice."""
        k = max(0, min(self.cells - 1, math.floor(s / self.h)))
        j = max(1, min(self.cells - 1, math.floor(s / self.h + Fraction(1, 2))))
        margin = abs(s - j * self.h)
        return (j if margin < MARGIN else k), j, margin

    def fields_on(self, case, s, q, k):
        dd = self.dense[case]
        z = A(s - k * self.h)
        sa = A(s)
        base = [horner(row, z) for row in self.seed[k]]
        a = horner(dd['A'][k], z)
        eps = A(dd['eps'])
        return [a, a + horner(q, sa), base[2] + eps * base[6] + horner(dd['corr'], sa), -2 * eps * base[5]], base

    def fields(self, case, s, q, piece=None):
        """(A, B, Phi, ell) and the eight seed rows at exact s on the contract's piece."""
        k = self.piece(s)[0] if piece is None else piece
        return self.fields_on(case, s, q, k)

    def dual(self, case, s, q):
        """Largest difference between the two pieces adjacent to the nearest shared knot."""
        _, j, _ = self.piece(s)
        a, ba = self.fields_on(case, s, q, j)
        b, bb = self.fields_on(case, s, q, j - 1)
        return max(up(x - y) for x, y in zip(a + ba, b + bb))

    def reference_map(self, case, q, table):
        """Exact-input Taylor-integral map: cell i built at knot i*h from piece table[i] at offset (i-table[i])*h."""
        dd = self.dense[case]
        n = self.degree
        eps = A(dd['eps'])
        hA = A(self.h)
        rows, knots = [], [arb(0)]
        for i in range(self.cells):
            p = table[i]
            if p == i:
                a_j = (list(dd['A'][p]) + [arb(0)] * (n + 1))[:n + 1]
                psi_j = (list(self.seed[p][5]) + [arb(0)] * (n + 1))[:n + 1]
            else:
                z = A((i - p) * self.h)
                a_j = taylor_shift(dd['A'][p], z, n)
                psi_j = taylor_shift(self.seed[p][5], z, n)
            q_j = taylor_shift(q, A(i * self.h), n)
            u = [-2 * eps * ps - aa - qq for ps, aa, qq in zip(psi_j, a_j, q_j)]
            e = exp_series(u)
            c = [arb(0)] + [v / (j + 1) for j, v in enumerate(e)]
            rows.append(c)
            knots.append(knots[-1] + horner(c, hA))
        return rows, knots


def load_producer_map(C, case, dps, rule):
    m = read(Path(C['out']) / 'maps' / f'case{case}_p{dps}_{rule}.json')
    return {'rows': [[pair(v) for v in row] for row in m['coefficients']], 'knots': [pair(v) for v in m['knots']],
            'X': pair(m['X']), 'q': [pair(v) for v in m['q']], 'table': m['table'], 'guard': m['guard']}


def exact_compare(rows_a, knots_a, X_a, rows_b, knots_b, X_b):
    same_shape(rows_a, rows_b)
    if len(knots_a) != len(knots_b):
        raise RuntimeError('Knot count mismatch')
    raw, at, cells = Fraction(0), None, []
    for i, (ra, rb) in enumerate(zip(rows_a, rows_b)):
        top = max(abs(x - y) for x, y in zip(ra, rb))
        if top > raw:
            raw, at = top, i
        if top > GATE:
            cells.append(i)
    return {'raw': raw, 'raw_cell': at, 'raw_cells_above_gate': cells,
            'knots': max(abs(x - y) for x, y in zip(knots_a, knots_b)), 'X': abs(X_a - X_b)}


def arb_compare(rows_a, knots_a, rows_b, knots_b, widths):
    """Raw maximum, whole-cell triangle bounds and Horner sup enclosures (value and Jacobian)."""
    same_shape(rows_a, rows_b)
    if len(knots_a) != len(knots_b) or len(rows_a) != len(widths):
        raise RuntimeError('Knot or width count mismatch')
    raw = V = J = SV = SJ = Fraction(0)
    cache = {}
    for i, (ra, rb) in enumerate(zip(rows_a, rows_b)):
        d = [A(x) - A(y) for x, y in zip(ra, rb)]
        dk = A(knots_a[i]) - A(knots_b[i])
        w = widths[i]
        if w not in cache:
            cache[w] = arb_powers(A(w), len(d))
        pw = cache[w]
        raw = max(raw, max(up(x) for x in d))
        tri = abs(dk)
        tj = arb(0)
        for j, x in enumerate(d):
            tri += abs(x) * pw[j]
            if j:
                tj += j * abs(x) * pw[j - 1]
        V = max(V, up(tri))
        J = max(J, up(tj))
        z = cell_interval(w)
        SV = max(SV, up(dk + horner(d, z)))
        SJ = max(SJ, up(horner([j * x for j, x in enumerate(d) if j], z)))
    return {'raw': raw, 'V_triangle': V, 'J_triangle': J, 'V_sup_enclosure': SV, 'J_sup_enclosure': SJ}


def jac_lower(rows, widths):
    lower = None
    for i, row in enumerate(rows):
        dv = horner([j * A(c) for j, c in enumerate(row) if j], cell_interval(widths[i]))
        if not dv.is_finite():
            raise ArithmeticError('Nonfinite Jacobian enclosure')
        b = lo(dv)
        lower = b if lower is None else min(lower, b)
    return lower


def gate(rows, gid, group, ok, value=None):
    rows.append({'id': gid, 'group': group, 'pass': bool(ok), 'value': value})


def classify(gates):
    failing = [r for r in gates if not r['pass']]
    groups = {r['group'] for r in failing}
    if not failing:
        return 'DETERMINISTIC_KNOT_REPRESENTATION_ADMITTED__HISTORICAL_RAW_GATE_RETAINED_FAILED'
    if groups & {'I', 'H'}:
        return 'IMPLEMENTATION_OR_HISTORICAL_CONTROL_FAILED'
    if groups <= {'R', 'S', 'C', 'U', 'M', 'W', 'E', 'A'} and all(('.c3.' in r['id'] or '.c4.' in r['id']) for r in failing):
        return 'SIGNED_REPLAY_FAILED'
    if groups & {'R', 'S'}:
        return 'SAVED_MAP_NOT_REPRODUCED'
    if 'C' in groups:
        return 'CANONICAL_REPRESENTATION_PRECISION_DEPENDENT'
    if 'U' in groups:
        return 'REPRESENTATION_CHOICE_MATERIAL'
    if 'G' in groups:
        return 'SIGNED_ROOT_BOUND_FAILED'
    return 'REPRESENTATION_ADMISSION_FAILED_' + ''.join(sorted(groups))


def grid_files(C, case, N):
    name = f"{C['level']}_case{case}_N{N}_p80"
    base = Path(C['grid_dir'])
    return base / (name + '.grid.json'), base / (name + '.audit.json'), base / (name + '.json')


def saved_map(grid):
    return {'rows': [[Q(x) for x in row] for row in grid['coordinate_integral_polynomials']],
            'knots': [Q(x) for x in grid['coordinate_knots']], 'X': Q(grid['X']),
            'q': [Q(x) for x in grid['gauge_coefficients']]}


def check_grid(C, nat, case, N, grid, saved, ref_can, pm, q_arb, case_recs, g, x, v):
    """Every per-grid decision recomputed from saved decimals and the producer's exact outputs."""
    cells = nat.cells
    gp, ap, _ = grid_files(C, case, N)
    audit = read(ap)
    struct = (audit['grid_sha256'] == sha(gp) and bool(audit['all_velocities_exactly_zero'])
              and all(Q(z) == 0 for row in grid['velocities'] for z in row)
              and all(Q(z) == 0 for z in grid['Cauchy_constants'].values()) and grid['N'] == N and grid['dps'] == 80
              and all(len(grid[k]) == N + 1 for k in ('A', 'B', 'Phi', 'ell', 's', 'x', 'seed_fields'))
              and len(grid['gauge_coefficients']) == 12 and len(grid['coordinate_knots']) == cells + 1
              and len(grid['coordinate_integral_polynomials']) == cells
              and all(len(r) == nat.degree + 2 for r in grid['coordinate_integral_polynomials'])
              and all(len(r) == 8 for r in grid['seed_fields']))
    gate(g, f'S3.c{case}.N{N}.structure', 'S', struct)
    lower_saved = jac_lower(saved['rows'], nat.widths)
    gate(g, f'M1.c{case}.N{N}.saved.monotone', 'M',
         lower_saved > 0 and all(b > a for a, b in zip(saved['knots'], saved['knots'][1:])), show(lower_saved))
    gq = [A(z) for z in saved['q']]
    S = [Q(z) for z in grid['s']]
    Xn = [Q(z) for z in grid['x']]
    fields_saved = seed_saved = fwd_saved = fwd_ref = Fraction(0)
    flagged_saved, duals = set(), []
    ref_rows, ref_knots = ref_can
    saved_rows_arb = [[A(c) for c in row] for row in saved['rows']]
    for k, s in enumerate(S):
        kk, _, margin = nat.piece(s)
        if margin < MARGIN:
            flagged_saved.add(k)
            duals.append(nat.dual(case, s, gq))
        fl, base = nat.fields(case, s, gq)
        for val, key in zip(fl, ('A', 'B', 'Phi', 'ell')):
            fields_saved = max(fields_saved, up(val - A(Q(grid[key][k]))))
        for val, stored in zip(base, grid['seed_fields'][k]):
            seed_saved = max(seed_saved, up(val - A(Q(stored))))
        z = A(s - kk * nat.h)
        fwd_saved = max(fwd_saved, up(A(saved['knots'][kk]) + horner(saved_rows_arb[kk], z) - A(Xn[k])))
        fwd_ref = max(fwd_ref, up(ref_knots[kk] + horner(ref_rows[kk], z) - A(Xn[k])))
    gate(x, f'XR3.c{case}.N{N}.saved_map_forward_reproduces_saved_x', 'R', fwd_saved <= GATE, show(fwd_saved))
    gate(x, f'XU2.c{case}.N{N}.exact_canonical_forward_matches_saved_x', 'U', fwd_ref <= GATE, show(fwd_ref))
    rec = {'fields_at_saved_s': show(fields_saved), 'seed_fields_at_saved_s': show(seed_saved),
           'forward_saved_map_minus_saved_x': show(fwd_saved), 'forward_exact_canonical_minus_saved_x': show(fwd_ref),
           'saved_positions_within_margin_of_shared_knot': sorted(flagged_saved), 'saved_map_jacobian_lower': show(lower_saved)}
    Dq = nat.D
    qd1 = [j * c for j, c in enumerate(gq) if j]
    qd2 = [j * c for j, c in enumerate(qd1) if j]
    qwall = max(up(horner(p, A(z))) for p in (gq, qd1, qd2) for z in (Fraction(0), Dq))
    bmina = [Q(grid['B'][i]) - Q(grid['A'][i]) for i in (0, N)]
    last = A(saved['knots'][cells - 1]) + horner(saved_rows_arb[cells - 1], A(nat.widths[-1]))
    end_saved = up(last - A(saved['X']))
    wall_ok = (qwall <= GATE and all(abs(z) <= GATE for z in bmina) and abs(S[N] - Dq) <= GATE and S[0] == 0
               and Xn[0] == 0 and Xn[N] == saved['X'])
    gate(g, f'W1.c{case}.N{N}.wall_gauge_and_positions', 'W', wall_ok, [show(qwall), show(abs(S[N] - Dq))])
    gate(x, f'XW1.c{case}.N{N}.saved_map_end_trace', 'W', end_saved <= GATE, show(end_saved))
    rec['walls'] = {'q_and_two_derivatives_at_walls': show(qwall), 'B_minus_A_wall_nodes': [str(z) for z in bmina],
                    'sN_minus_D': show(abs(S[N] - Dq)), 'saved_X_minus_last_cell_at_D': show(end_saved)}
    clocks = [(A(Q(grid['B'][i])) - A(Q(grid['seed_fields'][i][0]))).exp() for i in (0, N)]
    rec['clock_rate_enclosures'] = [[show(lo(c), 40), show(hi(c), 40)] for c in clocks]
    for d in C['dps']:
        cr = case_recs[d]['grids'][str(N)]
        gate(g, f'S1.c{case}.p{d}.N{N}.fields_at_saved_s', 'S', fields_saved <= GATE and seed_saved <= GATE,
             [show(fields_saved), show(seed_saved)])
        qd = max(abs(a - b) for a, b in zip(pm[(d, 'canonical')]['q'], saved['q']))
        gate(g, f'S2.c{case}.p{d}.N{N}.gauge_coefficients', 'S', qd <= GATE, show(qd))
        reported = [pair(cn['normalized_proper_clock_rate']) for cn in cr['clock_and_normals']]
        clock_ok = all(up(A(r) - c) <= GATE for r, c in zip(reported, clocks))
        orient = [cn['normal_orientation_sigma'] for cn in cr['clock_and_normals']] == [1, -1]
        gate(v, f'VCLK.c{case}.p{d}.N{N}.producer_clock_rates_inside_enclosures', 'V', clock_ok and orient)
        reported_saved = {f['node'] for f in cr['saved_position_ambiguous_points']}
        gate(v, f'VAMB.c{case}.p{d}.N{N}.saved_position_flags_agree', 'V', reported_saved == flagged_saved,
             [sorted(flagged_saved), sorted(reported_saved)])
        grid_duals = list(duals)
        for rule in RULES:
            m = pm[(d, rule)]
            rows_m = [[A(c) for c in row] for row in m['rows']]
            knots_m = [A(c) for c in m['knots']]
            qv = q_arb[d]
            srec = [pair(p) for p in cr['nodes'][rule]['s_reconstructed']]
            if len(srec) != N + 1:
                raise RuntimeError('Reconstructed position count mismatch')
            inv = max(abs(a - b) for a, b in zip(srec, S))
            frec = fwd = jac = Fraction(0)
            flagged = set(flagged_saved)
            for k, s in enumerate(srec):
                fl, _ = nat.fields(case, s, qv)
                for val, key in zip(fl, ('A', 'B', 'Phi', 'ell')):
                    frec = max(frec, up(val - A(Q(grid[key][k]))))
                kk, j, margin = nat.piece(s)
                if margin < MARGIN:
                    flagged.add(k)
                    grid_duals.append(nat.dual(case, s, qv))
                fwd = max(fwd, up(knots_m[kk] + horner(rows_m[kk], A(s - kk * nat.h)) - A(Xn[k])))
            for k, s in enumerate(S):
                kk = nat.piece(s)[0]
                fl, _ = nat.fields(case, s, qv)
                slope = horner([j * c for j, c in enumerate(rows_m[kk]) if j], A(s - kk * nat.h))
                jac = max(jac, up(slope - (fl[3] - fl[1]).exp()))
            for k, xv in enumerate(Xn):
                near = [jj for jj in range(1, cells) if abs(xv - m['knots'][jj]) < MARGIN]
                if near:
                    flagged.add(k)
                    jj = near[0]
                    s = srec[k]
                    left = knots_m[jj - 1] + horner(rows_m[jj - 1], A(s - (jj - 1) * nat.h))
                    right = knots_m[jj] + horner(rows_m[jj], A(s - jj * nat.h))
                    grid_duals.append(up(left - right))
            reported = {f['node'] for f in cr['nodes'][rule]['ambiguous_points']}
            gate(v, f'VAMB.c{case}.p{d}.N{N}.{rule}.flag_sets_agree', 'V', flagged == reported, [sorted(flagged), sorted(reported)])
            if rule == 'old80':
                gate(g, f'R3.c{case}.p{d}.N{N}.inverse_s', 'R', inv <= GATE, show(inv))
                gate(g, f'R4.c{case}.p{d}.N{N}.fields_at_reconstructed_s', 'R', frec <= GATE, show(frec))
            elif rule == 'canonical':
                gate(g, f'U3.c{case}.p{d}.N{N}.canonical_nodes', 'U', inv <= GATE and frec <= GATE, [show(inv), show(frec)])
            if rule != 'floor_at_p':
                gate(g, f'E2.c{case}.p{d}.N{N}.{rule}.jacobian_identity', 'E', jac <= GATE, show(jac))
                gate(v, f'VINV.c{case}.p{d}.N{N}.{rule}.producer_positions_forward_consistent', 'V', fwd <= GATE, show(fwd))
            rec[f'{rule}_p{d}'] = {'inverse_s': show(inv), 'fields_at_reconstructed_s': show(frec), 'jacobian_identity': show(jac),
                                   'forward_consistency': show(fwd), 'flagged_nodes': sorted(flagged)}
            if N == C['degrees'][0] and rule != 'floor_at_p':
                end = up(knots_m[cells - 1] + horner(rows_m[cells - 1], A(nat.widths[-1])) - A(m['X']))
                top = max(abs(pair(case_recs[d]['grids'][str(NN)]['nodes'][rule]['s_reconstructed'][NN]) - Dq) for NN in C['degrees'])
                gate(g, f'W3.c{case}.p{d}.{rule}.map_wall_trace', 'W', m['knots'][0] == 0 and end <= GATE and top <= GATE,
                     [show(end), show(top)])
                flo, _ = nat.fields(case, Fraction(0), qv)
                fhi, _ = nat.fields(case, Dq, qv, piece=cells - 1)
                s_lo = rows_m[0][1]
                s_hi = horner([j * c for j, c in enumerate(rows_m[cells - 1]) if j], A(nat.widths[-1]))
                wj = max(up(s_lo - (flo[3] - flo[1]).exp()), up(s_hi - (fhi[3] - fhi[1]).exp()))
                gate(g, f'W4.c{case}.p{d}.{rule}.wall_jacobian', 'W', wj <= GATE, show(wj))
        flags_all = cr['saved_position_ambiguous_points'] + [f for r in RULES for f in cr['nodes'][r]['ambiguous_points']]
        gate(g, f'A1.c{case}.p{d}.N{N}.ambiguous_points', 'A',
             all(f['dual_within_gate'] for f in flags_all) and all(z <= GATE for z in grid_duals),
             [len(flags_all), len(grid_duals), show(max(grid_duals)) if grid_duals else None])
    return rec


def verify(C, guard):
    t0 = time.monotonic()
    ctx.prec = 768
    ctx.threads = 1
    out = Path(C['out'])
    if (out / 'FAILURE.json').exists():
        raise RuntimeError('Producer failed closed; nothing to verify')
    producer = read(out / 'PRODUCER_RESULT.json')
    if producer['guard'] != guard:
        raise RuntimeError('Producer result bound to another guard')
    for name, digest in producer['case_records'].items():
        if sha(out / name) != digest:
            raise RuntimeError('Case record changed after publication: ' + name)
    for name, digest in producer['maps'].items():
        if sha(out / 'maps' / name) != digest:
            raise RuntimeError('Map file changed after publication: ' + name)
    lo_dps, hi_dps = C['dps']
    nat = Native(C)
    cells = nat.cells
    g, x, v = [], [], []
    record = {'cases': {}}
    emulated = {d: floor_table(nat.seed_raw['h'], mp_prec(d), cells) for d in sorted(set(C['dps']) | {C['old_rule_dps']})}
    diagnostic_tables = {bits: floor_table(nat.seed_raw['h'], bits, cells) for bits in (53, 113)}
    old80 = emulated[C['old_rule_dps']]
    tables_ok = True
    for case in C['cases']:
        for d in C['dps']:
            maps = {r: load_producer_map(C, case, d, r) for r in RULES}
            tables_ok = (tables_ok and maps['old80']['table'] == old80 and maps['floor_at_p']['table'] == emulated[d]
                         and maps['canonical']['table'] == list(range(cells)) and all(m['guard'] == guard for m in maps.values()))
    gate(v, 'VTAB.emulated_knot_rules_equal_producer_tables', 'V', tables_ok,
         {'old80_non_canonical': [i for i, p in enumerate(old80) if p != i],
          'floor_at_hi_non_canonical': [i for i, p in enumerate(emulated[hi_dps]) if p != i]})
    gate(g, 'A2.selection_tables', 'A', len(old80) == cells and all(p in (i - 1, i) for i, p in enumerate(old80)) and tables_ok,
         {'old80_prec_bits': mp_prec(C['old_rule_dps'])})
    record['selection'] = {'prec_bits': {str(d): mp_prec(d) for d in emulated},
                           'non_canonical_cells': {str(d): [i for i, p in enumerate(t) if p != i] for d, t in emulated.items()},
                           'diagnostic_non_canonical_cells_by_bits': {str(b): [i for i, p in enumerate(t) if p != i]
                                                                     for b, t in diagnostic_tables.items()},
                           'cells_where_hi_differs_from_old80': [i for i in range(cells) if emulated[hi_dps][i] != old80[i]]}
    for case in C['cases']:
        dd = nat.case(C, case)
        crec = {}
        grids = {N: read(grid_files(C, case, N)[0]) for N in C['degrees']}
        saved = {N: saved_map(grids[N]) for N in C['degrees']}
        key0 = json.dumps([grids[C['degrees'][0]][k] for k in ('coordinate_integral_polynomials', 'coordinate_knots', 'X', 'gauge_coefficients')])
        same = all(json.dumps([gr[k] for k in ('coordinate_integral_polynomials', 'coordinate_knots', 'X', 'gauge_coefficients')]) == key0
                   for gr in grids.values())
        gate(g, f'S4.c{case}.saved_map_identical_across_degrees', 'S', same)
        pm = {(d, r): load_producer_map(C, case, d, r) for d in C['dps'] for r in RULES}
        q_arb = {d: [A(z) for z in pm[(d, 'canonical')]['q']] for d in C['dps']}
        refs = {}

        def ref(rule, qkey, qvalues):
            if (rule, qkey) not in refs:
                refs[(rule, qkey)] = nat.reference_map(case, qvalues, list(range(cells)) if rule == 'canonical' else old80)
            return refs[(rule, qkey)]
        like = {}
        for d in C['dps']:
            for rule, gid, group in (('canonical', 'XC1', 'C'), ('old80', 'XR1', 'R')):
                rows, knots = ref(rule, d, q_arb[d])
                c = arb_compare(pm[(d, rule)]['rows'], pm[(d, rule)]['knots'], rows, knots, nat.widths)
                like[f'{rule}_p{d}_vs_exact_reference'] = c
                gate(x, f'{gid}.c{case}.p{d}.{rule}.producer_vs_exact_reference', group, c['raw'] <= GATE and c['V_triangle'] <= GATE,
                     [show(c['raw']), show(c['V_triangle'])])
        for N in C['degrees']:
            sv = saved[N]
            qkey = 'saved' + json.dumps(grids[N]['gauge_coefficients'])
            qs = [A(z) for z in sv['q']]
            rows, knots = ref('old80', qkey, qs)
            c = arb_compare(sv['rows'], sv['knots'], rows, knots, nat.widths)
            like[f'saved_N{N}_vs_exact_old80_reference'] = c
            gate(x, f'XR2.c{case}.N{N}.saved_map_equals_exact_old80_reference', 'R', c['raw'] <= GATE and c['V_triangle'] <= GATE,
                 [show(c['raw']), show(c['V_triangle'])])
            rows, knots = ref('canonical', qkey, qs)
            c = arb_compare(sv['rows'], sv['knots'], rows, knots, nat.widths)
            like[f'saved_N{N}_vs_exact_canonical_reference'] = c
            gate(x, f'XU1.c{case}.N{N}.saved_vs_exact_canonical_whole_cell', 'U',
                 c['V_sup_enclosure'] <= GATE and c['J_sup_enclosure'] <= GATE and c['V_triangle'] <= GATE and c['J_triangle'] <= GATE,
                 [show(c['V_sup_enclosure']), show(c['J_sup_enclosure']), show(c['raw'])])
            ref_lower = jac_lower(rows, nat.widths)
            gate(x, f'XM1.c{case}.N{N}.exact_canonical_reference_monotone', 'M', ref_lower > 0, show(ref_lower))
        crec['map_comparisons_arb'] = {k: {kk: show(vv) for kk, vv in val.items()} for k, val in like.items()}
        hz = A(nat.h)
        eps = A(dd['eps'])
        jump_value = jump_slope = Fraction(0)
        for k in range(1, cells):
            psiL, psiR = nat.seed[k - 1][5], nat.seed[k][5]
            aL, aR = dd['A'][k - 1], dd['A'][k]
            valL = -2 * eps * horner(psiL, hz) - horner(aL, hz)
            dL = -2 * eps * horner([j * c for j, c in enumerate(psiL) if j], hz) - horner([j * c for j, c in enumerate(aL) if j], hz)
            jump_value = max(jump_value, up(valL - (-2 * eps * psiR[0] - aR[0])))
            jump_slope = max(jump_slope, up(dL - (-2 * eps * psiR[1] - aR[1])))
        crec['native_knot_jumps_of_ell_minus_A'] = {'value': show(jump_value), 'first_derivative': show(jump_slope)}
        for d in C['dps']:
            for N in C['degrees']:
                sv = saved[N]
                for rule in RULES:
                    m = pm[(d, rule)]
                    e = exact_compare(m['rows'], m['knots'], m['X'], sv['rows'], sv['knots'], sv['X'])
                    if rule == 'old80':
                        gate(g, f'R1.c{case}.p{d}.N{N}.raw_coefficients', 'R', e['raw'] <= GATE, show(e['raw']))
                        gate(g, f'R2.c{case}.p{d}.N{N}.knots_and_length', 'R', e['knots'] <= GATE and e['X'] <= GATE,
                             [show(e['knots']), show(e['X'])])
                    if rule == 'canonical':
                        c = arb_compare(m['rows'], m['knots'], sv['rows'], sv['knots'], nat.widths)
                        gate(g, f'U1.c{case}.p{d}.N{N}.cell_value_bound', 'U', c['V_triangle'] <= GATE, show(c['V_triangle']))
                        gate(g, f'U2.c{case}.p{d}.N{N}.cell_jacobian_bound', 'U', c['J_triangle'] <= GATE, show(c['J_triangle']))
                        crec[f'canonical_p{d}_vs_saved_N{N}'] = {kk: show(vv) for kk, vv in c.items()} | {
                            'raw_cells_above_gate': e['raw_cells_above_gate'], 'raw_exact_display': show(e['raw'])}
                    if rule == 'floor_at_p' and d == hi_dps:
                        crec[f'floor_hi_vs_saved_N{N}'] = {'raw': show(e['raw']), 'raw_cell': e['raw_cell'],
                                                           'raw_cells_above_gate': e['raw_cells_above_gate'], 'raw_exact': str(e['raw'])}
                        if case == C['cases'][0] and N == C['degrees'][0]:
                            switched = set(record['selection']['cells_where_hi_differs_from_old80'])
                            gate(g, f"H1.c{case}.p{d}.N{N}.historical_failure_reproduced", 'H',
                                 e['raw'] > GATE and set(e['raw_cells_above_gate']) <= switched, [show(e['raw']), e['raw_cell']])
            for rule in ('canonical', 'old80'):
                lower = jac_lower(pm[(d, rule)]['rows'], nat.widths)
                kn = pm[(d, rule)]['knots']
                gate(g, f'M1.c{case}.p{d}.{rule}.monotone', 'M', lower > 0 and all(b > a for a, b in zip(kn, kn[1:])), show(lower))
            rows_c, rows_o = pm[(d, 'canonical')]['rows'], pm[(d, 'old80')]['rows']
            differing = [i for i in range(cells) if rows_c[i] != rows_o[i]]
            gate(g, f'C3.c{case}.p{d}.selection_isolated', 'C', set(differing) <= {i for i in range(cells) if old80[i] != i}, differing)
        for label, rule in (('C1', 'canonical'), ('C2', 'old80')):
            a, b = pm[(lo_dps, rule)], pm[(hi_dps, rule)]
            e = exact_compare(a['rows'], a['knots'], a['X'], b['rows'], b['knots'], b['X'])
            gate(g, f'{label}.c{case}.{rule}_cross_precision', 'C', e['raw'] <= GATE and e['knots'] <= GATE and e['X'] <= GATE,
                 [show(e['raw']), show(e['knots']), show(e['X'])])
            crec[f'{rule}_cross_precision_exact'] = {k: (show(val) if isinstance(val, Fraction) else val) for k, val in e.items()}
        q_cross = max(abs(a - b) for a, b in zip(pm[(lo_dps, 'canonical')]['q'], pm[(hi_dps, 'canonical')]['q']))
        case_recs = {d: read(out / f'case{case}_p{d}.json') for d in C['dps']}
        rows_by_dps = {}
        for d in C['dps']:
            fr = [[[pair(z) for z in row] for row in wall] for wall in case_recs[d]['gauge']['final_rows']]
            rows_by_dps[d] = fr
            m02 = max(abs(z) for wall in fr for row in wall[:2] for z in row)
            m4 = max(abs(z) for wall in fr for z in wall[2])
            gate(g, f'E1.c{case}.p{d}.wall_rows_inherited_thresholds', 'E', m02 < ROW_GATE_02 and m4 < ROW_GATE_4, [show(m02), show(m4)])
            gate(v, f'VQ.c{case}.p{d}.gauge_record_matches_map_files', 'V',
                 all(pm[(d, r)]['q'] == [pair(z) for z in case_recs[d]['gauge']['q']] for r in RULES))
        rows_cross = max(abs(a - b) for wa, wb in zip(rows_by_dps[lo_dps], rows_by_dps[hi_dps])
                         for ra, rb in zip(wa, wb) for a, b in zip(ra, rb))
        gate(g, f'E1x.c{case}.wall_rows_cross_precision', 'E', rows_cross <= GATE and q_cross <= GATE, [show(rows_cross), show(q_cross)])
        crec['gauge'] = {'q_cross_precision': show(q_cross), 'wall_rows_cross_precision': show(rows_cross)}
        crec['grids'] = {}
        for N in C['degrees']:
            qkey = 'saved' + json.dumps(grids[N]['gauge_coefficients'])
            ref_can = ref('canonical', qkey, [A(z) for z in saved[N]['q']])
            crec['grids'][str(N)] = check_grid(C, nat, case, N, grids[N], saved[N], ref_can, pm, q_arb, case_recs, g, x, v)
        for rule in ('canonical', 'old80'):
            worst = Fraction(0)
            for N in C['degrees']:
                ra = [pair(p) for p in case_recs[lo_dps]['grids'][str(N)]['nodes'][rule]['s_reconstructed']]
                rb = [pair(p) for p in case_recs[hi_dps]['grids'][str(N)]['nodes'][rule]['s_reconstructed']]
                if len(ra) != len(rb):
                    raise RuntimeError('Reconstructed position count mismatch')
                worst = max(worst, max(abs(a - b) for a, b in zip(ra, rb)))
            gate(g, f'Cx.c{case}.{rule}.reconstructed_s_cross_precision', 'C', worst <= GATE, show(worst))
            crec[f'{rule}_reconstructed_s_cross_precision'] = show(worst)
        for N in C['degrees']:
            ca = [pair(z['normalized_proper_clock_rate']) for z in case_recs[lo_dps]['grids'][str(N)]['clock_and_normals']]
            cb = [pair(z['normalized_proper_clock_rate']) for z in case_recs[hi_dps]['grids'][str(N)]['clock_and_normals']]
            delta = max(abs(a - b) for a, b in zip(ca, cb))
            orient = all([z['normal_orientation_sigma'] for z in case_recs[d]['grids'][str(N)]['clock_and_normals']] == [1, -1]
                         for d in C['dps'])
            gate(g, f'W2.c{case}.N{N}.clocks_cross_precision', 'W', delta <= GATE and orient, show(delta))
        eps_saved = dd['eps']
        crec['epsilon'] = {'target': str(TARGETS[case]), 'saved_exact_decimal': str(eps_saved),
                           'offset': str(eps_saved - TARGETS[case]), 'offset_display': show(eps_saved - TARGETS[case]),
                           'in_certified_interval': -Fraction(1, 200000) <= eps_saved <= Fraction(1, 200000)}
        gate(x, f'XS1.c{case}.saved_amplitude_in_certified_interval', 'S', crec['epsilon']['in_certified_interval'])
        record['cases'][str(case)] = crec
    audit = read(C['connected_audit'])
    roots_prod = {r['name']: r for r in producer['root_bounds']}
    box = [Fraction(1, 100000), Fraction(1, 10), Fraction(1, 10)]
    record['roots'] = {}
    for name, case in (('positive', 3), ('negative', 4)):
        src = Path(C['finite']) / 'output' / name / 'RESULT.json'
        old = read(src)
        ind = audit['endpoint_identity'][name]
        dense = nat.case(C, case)['raw']
        eps = Fraction(old['epsilon'])
        centers = [Q(dense['A0']) - eps] + [Q(z) for z in dense['fifth_jet_coefficients']]
        images = [[Q(z) for z in row['exact']] for row in ind['translated_root_image']]
        inside = all(-r < a <= b < r for (a, b), r in zip(images, box))
        dist = [max(abs(a - c), abs(b - c)) for (a, b), c in zip(images, centers)]
        ok = (bool(old['pass']) and bool(ind['pass']) and ind['old_result_sha256'] == sha(src) and inside
              and centers == [Q(z) for z in old['center']] and eps == TARGETS[case])
        rp = roots_prod.get(name)
        agree = (rp is not None and [str(z) for z in dist] == rp['distance_from_saved_center_upper_exact']
                 and [str(z) for z in centers] == rp['center_exact'])
        gate(g, f'G1.{name}.root_bounds', 'G', ok)
        gate(v, f'VROOT.{name}.producer_root_bound_record_agrees', 'V', agree)
        record['roots'][name] = {'distance_from_saved_center_upper': [show(z) for z in dist], 'inside_box': inside,
                                 'root_enclosure_widths': [show(b - a) for a, b in images],
                                 'centers': [show(c, 12) for c in centers]}
    root = Path(C['spatial_root'])
    adm = read(root / 'GRID_ADMISSION.json')
    required = {f"inputs/{C['level']}_case{c}_N{N}_p80{s}" for c in C['cases'] for N in C['degrees'] for s in ('.json', '.grid.json', '.audit.json')}
    sel = {r['path']: r['sha256'] for r in adm['inputs'] if r['path'] in required}
    spatial_ver = read(root / 'VERIFICATION.json')
    rec_ok = (set(sel) == required and all(sha(root / p) == h for p, h in sel.items()) and bool(adm['all_passed'])
              and bool(read(C['admission_verification'])['all_passed']) and bool(spatial_ver['record_integrity_valid'])
              and bool(spatial_ver['complete_signed_cohort_qualified']))
    for c in C['cases']:
        for N in C['degrees']:
            tag = f"{C['level']}_case{c}_N{N}_p80 "
            rows = [r for r in adm['checks'] if r['check'].startswith(tag)]
            names = {r['check'][len(tag):] for r in rows}
            rec_ok = rec_ok and set(FAMILIES) <= names and all(r['pass'] for r in rows)
    gate(g, 'E3.inherited_original_equation_receipts', 'E', rec_ok)
    if not C['fixture']:
        ident = Path(C['identity'])
        spatial = read(ident / 'SPATIAL_ENCLOSURES.json')
        flows = all(read(ident / 'output' / f / 'RESULT.json')['passed']
                    and read(ident / 'output' / f / 'TERMINAL_CHECKPOINT.json')['status'] == 'COMPLETE'
                    for f in ('mode', 'positive', 'negative'))
        gate(v, 'VSPATIAL.accepted_spatial_flows_reused_unchanged', 'V', bool(spatial['passed']) and flows)
        failure = read(ident / 'NUMERICAL_READBACK_FAILURE.json')
        diag = read(ident / 'audit' / 'FAILED_REPLAY_DIAGNOSTIC.json')
        gate(v, 'VHIST0.historical_failure_record_preserved', 'V',
             failure['status'] == 'FAILED_CLOSED' and failure['error'] == 'Frozen representation replay gate'
             and not (ident / 'NUMERICAL_READBACK.json').exists())
        fh = record['cases'][str(C['cases'][0])][f"floor_hi_vs_saved_N{C['degrees'][0]}"]
        diag_cells = sorted(r['cell'] for r in diag['cells_exceeding_raw_coefficient_gate'])
        diag_max = Q(diag['maximum_map_coefficient']['absolute_difference'])
        prod_max = Q(fh['raw_exact'])
        sel_ok = all(old80[r['nominal_cell']] == r['selected_at_80_digits'] and emulated[100][r['nominal_cell']] == r['selected_at_100_digits']
                     for r in diag['knot_selection_diagnostics'])
        gate(x, 'XH1.historical_failure_numbers_reproduced', 'H',
             sorted(fh['raw_cells_above_gate']) == diag_cells and abs(prod_max - diag_max) <= Fraction(1, 10 ** 60)
             and fh['raw_cell'] == diag['maximum_map_coefficient']['cell'] and sel_ok,
             {'producer_max': fh['raw'], 'diagnostic_max': show(diag_max), 'cells': diag_cells})
    pg = {r['id']: r for r in producer['gates']}
    mine = {r['id']: r for r in g}
    disagreements = sorted(k for k in mine if k in pg and pg[k]['pass'] != mine[k]['pass'])
    missing = sorted(k for k in mine if k not in pg)
    producer_only = sorted(k for k in pg if k not in mine)
    gate(v, 'VAGREE.shared_gate_flags_agree', 'V', not disagreements and not missing,
         {'disagreements': disagreements, 'missing_in_producer': missing})
    if not C['fixture']:
        ps = subprocess.run(['ps', '-eo', 'pid,args'], capture_output=True, text=True, check=True).stdout.splitlines()
        live = [line.strip() for line in ps if 'code/replay.py' in line and RUN.name in line and 'verify.py' not in line]
        gate(v, 'VPROC.no_live_producer', 'V', not live, live)
    resolved = all(r['pass'] for r in v)
    combined = g + x + [pg[k] for k in producer_only]
    classification = classify(combined) if resolved else 'UNRESOLVED_VERIFICATION'
    failed = [r['id'] for r in combined if not r['pass']]
    return {'guard': guard, 'utc': now(), 'verifier_source_sha256': sha(Path(__file__).resolve()),
            'classification': classification, 'resolved': resolved,
            'producer_classification_provisional': producer['classification_provisional'],
            'producer_confirmed': classification == producer['classification_provisional'],
            'shared_gates_passed': sum(r['pass'] for r in g), 'shared_gates_total': len(g),
            'verifier_only_gates_passed': sum(r['pass'] for r in x), 'verifier_only_gates_total': len(x),
            'producer_only_gates': producer_only, 'producer_only_gates_failed': [k for k in producer_only if not pg[k]['pass']],
            'integrity_checks_passed': sum(r['pass'] for r in v), 'integrity_checks_total': len(v),
            'decision_gates_passed': sum(r['pass'] for r in combined), 'decision_gates_total': len(combined),
            'failed_decision_gates': failed, 'failed_integrity_checks': [r['id'] for r in v if not r['pass']],
            'shared_gates': g, 'verifier_only_gates': x, 'integrity_checks': v,
            'record': record, 'seconds': time.monotonic() - t0,
            'arithmetic': 'Arb 768-bit outward balls for evaluations; exact Fractions for stored values and knot-rule emulation',
            'imports_no_producer_or_reference_code': True}


def prepare_real():
    for key, value in {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0', 'PYTHONNOUSERSITE': '1',
                       'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}.items():
        if os.environ.get(key) != value:
            raise RuntimeError('Runtime environment ' + key)
    folder = RUN / 'verification'
    if (folder / 'VERIFICATION.json').exists():
        raise RuntimeError('Verification already terminal')
    if folder.exists() and any(folder.glob('FAILURE_*.json')):
        raise RuntimeError('Verification failed closed; no restart')
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    target = 3 * 1024 ** 3
    for inherited in (soft, hard):
        if inherited != resource.RLIM_INFINITY and inherited < target:
            target = inherited
    resource.setrlimit(resource.RLIMIT_AS, (target, target))
    freeze = RUN / 'FREEZE.json'
    frozen = read(freeze)
    guard = sha(freeze)
    for name, digest in frozen['inputs'].items():
        if sha(name) != digest:
            raise RuntimeError('Changed input ' + name)
    for name, digest in frozen['sources'].items():
        if sha(RUN / name) != digest:
            raise RuntimeError('Changed source ' + name)
    for name, digest in frozen['runtime']['libraries'].items():
        if sha(name) != digest:
            raise RuntimeError('Changed runtime library ' + name)
    if frozen['runtime']['python'] != platform.python_version():
        raise RuntimeError('Changed interpreter')
    cfg = frozen['config']
    C = dict(REAL)
    if cfg['cases'] != C['cases'] or cfg['degrees'] != C['degrees'] or cfg['dps'] != C['dps'] or cfg['old_rule_dps'] != C['old_rule_dps']:
        raise RuntimeError('Verifier case matrix differs from the frozen contract')
    if cfg['gate_absolute'] != '1e-50' or cfg['ambiguity_margin'] != '1e-40':
        raise RuntimeError('Verifier norms differ from the frozen contract')
    return C, guard, cfg, list(resource.getrlimit(resource.RLIMIT_AS))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        try:
            C0, guard0, cfg0, limits0 = prepare_real()
        except Exception as error:
            write_once(RUN / 'verification' / 'refusals' / f'VERIFY_LAUNCH_REFUSED_{int(time.time())}_{os.getpid()}.json',
                       {'type': type(error).__name__, 'error': str(error), 'utc': now(), 'outcomes_started': False})
            raise

        def alarm(*args):
            raise TimeoutError('Frozen verifier wall budget')
        try:
            signal.signal(signal.SIGALRM, alarm)
            signal.alarm(cfg0['verifier_wall_seconds'])
            result = verify(C0, guard0)
            signal.alarm(0)
            result.update({'address_space': limits0, 'compute_slot': os.environ.get('COMPUTE_SLOT'), 'pid': os.getpid()})
            write_once(Path(C0['verification']) / 'VERIFICATION.json', result)
            print(json.dumps({'classification': result['classification'], 'resolved': result['resolved'],
                              'producer_confirmed': result['producer_confirmed'],
                              'decision_gates': [result['decision_gates_passed'], result['decision_gates_total']],
                              'integrity': [result['integrity_checks_passed'], result['integrity_checks_total']],
                              'failed': result['failed_decision_gates'][:40] + result['failed_integrity_checks'][:20]}), flush=True)
        except Exception as error:
            write_once(RUN / 'verification' / f'FAILURE_{int(time.time())}.json',
                       {'type': type(error).__name__, 'error': str(error), 'traceback': traceback.format_exc(), 'utc': now()})
            raise
    elif len(sys.argv) == 3 and sys.argv[1] == 'fixture':
        C = read(sys.argv[2])
        result = verify(C, C['guard'])
        write_once(Path(C['verification']) / 'VERIFICATION.json', result)
        print(json.dumps({'classification': result['classification'], 'resolved': result['resolved'],
                          'producer_confirmed': result['producer_confirmed'],
                          'failed': result['failed_decision_gates'][:60] + result['failed_integrity_checks']}), flush=True)
    else:
        raise SystemExit('usage: verify.py run | verify.py fixture <context.json>')
