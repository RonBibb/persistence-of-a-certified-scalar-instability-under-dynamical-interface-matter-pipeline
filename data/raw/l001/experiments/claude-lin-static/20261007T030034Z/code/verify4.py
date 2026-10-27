"""Independent verifier for run 20261007T030034Z (narrowed-D' re-preparation, root iteration, material bounds).

Does not import reprep.py or assemble4.py. Uses the byte-identical inherited validated engine, wall jets,
preparation and profiles (shared, disclosed) with its own drivers, its own map assembly and an exact
rational Krawczyk step. Also shared and disclosed: the common4 helpers (paths, CONFIG, read/atomic/plain,
fq, up_float, show, check_environment, limit_address_space). Every check is an agreement check between its own recomputation and the producer's
record. The final label is the producer's label (technical labels included) if and only if all agreement
checks pass and that label follows from the producer's gates in the frozen order; otherwise
UNRESOLVED_VERIFICATION.
    python -B <run>/code/verify4.py case <positive|negative>
    python -B <run>/code/verify4.py final
    python -B <run>/code/verify4.py check <record.json>      (own controls only, before any D' quantity)
"""
import json
import math
import os
import signal
import sys
import time
import traceback
from array import array
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inherited'))
sys.path.insert(1, str(HERE))
from flint import arb, fmpq, ctx  # noqa: E402
import records  # noqa: E402
import validated  # noqa: E402
import source_flow  # noqa: E402
import nonlinear  # noqa: E402
import prepared_flow  # noqa: E402
import preparation  # noqa: E402
from algebra import e1, exp  # noqa: E402
from series import bounds, hull, interval, power  # noqa: E402
import identity_run as ir  # noqa: E402
from common4 import (RUN, OUT, VER, PACKET, RUN3, CONFIG, now, sha, read, atomic, fq, up_float, show,  # noqa: E402
                     check_environment, limit_address_space)

SRC_KEYS = ('y', 'p', 'cover', 'end', 'max_picard', 'cell_index', 'task_index', 'which')
PHASE_KEYS = ('y', 'p', 'jets', 'cover', 'end', 'map', 'max_picard', 'cell_index', 'task_index', 'which', 'phase')
MAT_KEYS = ('y', 'p', 'max_picard', 'cell_index', 'task_index', 'name')
COLS = ('E', 'center', 'state', 'source_step', 'event', 'native_step')
FIELDS = ('A', 'ell', 'Phi')
RADIUS = Fraction(1, 2 ** (-CONFIG['closure_radius_relative_log2']))
FLOOR = Fraction(1, 2 ** (-CONFIG['closure_absolute_log2']))
ORDER = (('R', 'TECHNICAL_REPLAY_MISMATCH'), ('P', 'PREPARATION_PIPELINE_MISMATCH'), ('T', 'TECHNICAL_INCOMPLETE'),
         ('K', 'ROOT_ITERATION_INCONSISTENT'), ('B', 'BUDGET_NOT_CLOSED'))


def mr(x):
    lo, hi = bounds(x)
    return (lo + hi) / 2, (hi - lo) / 2


def q(x):
    x = Fraction(x)
    return fmpq(x.numerator, x.denominator)


def gate(rows, gid, ok, value=None):
    rows.append({'id': gid, 'pass': bool(ok), 'value': value})


def listing(folder):
    out = []
    for p in sorted(Path(folder).glob('*.json')):
        body = read(p)
        if records.fingerprint(body) != p.name.split('-')[-1][:-5]:
            raise RuntimeError('Checkpoint digest mismatch ' + p.name)
        out.append((int(p.name.split('-')[1]), body))
    return out


def same(state, body, keys):
    packed = records.pack({k: state[k] for k in keys})
    return all(packed[k] == body['state'].get(k) for k in keys)


def one_cell(state, engine, lo, hi, h, endpoint=None, keep=None):
    """Own driver of the inherited finite-packet cell update."""
    s = state['cell_index'] * h
    ynext, cell = validated.step(state['y'], h, state['p'], engine)
    if not all(v.is_finite() for v in ynext) or bounds(cell['box'][4])[0] <= 0:
        raise ArithmeticError('Own replay lost finiteness or positivity')
    state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
    if s + h >= lo and s <= hi:
        a, b = max(fmpq(0), lo - s), min(h, hi - s)
        z = validated.range_on_cell(cell, a, b)
        state['cover'].append([str(s + a), str(s + b)])
        state['end'] = z if state.get('end') is None else [hull(u, v) for u, v in zip(state['end'], z)]
        if endpoint is not None:
            r = endpoint(z)
            state['map'] = r if state.get('map') is None else {k: [hull(u, v) for u, v in zip(state['map'][k], r[k])] for k in r}
    if keep is not None:
        keep(state['cell_index'], s, cell)
    state['y'] = ynext
    state['cell_index'] += 1


def own_map(y, p, jets):
    """Own assembly of the inherited upper-wall map (Israel mismatch, two fifth-jet rows) and its Jacobian."""
    eps = p['eps']
    G = [y[10] - preparation.wall_increment(y, jets[1], p, eps)['target']]
    J = [y[12], y[14], y[16]]
    diag = []
    for side in (0, 1):
        j = jets[side]
        e = preparation.wall_increment(y, j, p, eps)
        w = p['x'][0] if side == 0 else y[9]
        qn = j['qbg'] * exp(-2 * (eps * e['psi'] + w))
        dl = j['qbg'] * e1(-2 * (eps * e['psi'] + w)) - e['dr']
        corr = power(e['L'], 5) * (-12 * e['c'] * e['S'] * dl - 24 * e['t'] * dl * dl)
        G.append(p['x'][side + 1] + p['W'][side] + corr)
        col = [arb(1), arb(0), arb(0)] if side == 0 else [y[11], y[13], y[15]]
        mult = power(e['L'], 5) * (-12 * e['c'] * e['S'] - 48 * e['t'] * dl) * (-2 * qn)
        J += [int(n == side + 1) + mult * col[n] for n in range(3)]
        diag += [qn, dl, e['S'], e['L'], corr]
    if not all(v.is_finite() for v in G + J + diag) or not all(bounds(diag[i])[0] > 0 for i in (0, 3, 5, 8)):
        raise ArithmeticError('Own map lost finiteness or positivity')
    return {'G': G, 'J': J, 'wall_diagnostics': diag}


def own_phase_maps(C, w, common):
    """Own replay of the accepted finite certificate's last phase blocks and own map against the accepted record."""
    rows = [(e, b) for e, b in listing(Path(C['case_dirs'][w]) / 'checkpoints')]
    names = sorted(p.name for p in (Path(C['case_dirs'][w]) / 'checkpoints').glob('*.json'))
    tagged = [(int(n.split('-')[0]), e, b) for n, (e, b) in zip(names, rows)]
    acc = records.unpack(read(C['case_results'][w]))
    K1, K2 = C['K']
    out = {}
    for task, name in ((0, 'center'), (1, 'box')):
        st0 = [b for t, e, b in tagged if t == task and e == C['restart'] and b['guard'] == C['finite_guard']]
        st1 = [b for t, e, b in tagged if t == task and e == C['total'] and b['guard'] == C['finite_guard']]
        if len(st0) != 1 or len(st1) != 1:
            out[name] = False
            continue
        st = records.unpack(st0[0]['state'])
        while st['cell_index'] < C['total']:
            one_cell(st, nonlinear, K1, K2, C['step'], endpoint=lambda z: own_map(z, st['p'], common['jets']))
        keys = ('y', 'p', 'cover', 'end', 'map', 'max_picard', 'cell_index', 'task_index')
        ref = acc['G_center'] if name == 'center' else acc['J_box']
        mine = st['map']['G'] if name == 'center' else [st['map']['J'][3 * i:3 * i + 3] for i in range(3)]
        out[name] = bool(same(st, st1[0], keys) and records.pack(mine) == records.pack(ref))
    return out


def own_initial(binding, mu_point=None):
    """Own port of the finite runner's initial state at s = 0 (before outward canonicalization)."""
    m = {k: arb(ir.exact(v)) for k, v in binding['model_exact'].items()}
    a = interval(*[ir.exact(v) for v in binding['config']['root']])
    mu = interval(*[ir.exact(v) for v in binding['config']['mu']]) if mu_point is None else arb(mu_point)
    gap = a - m['v0']
    H = -(m['lambda_a'] + m['gamma'] * gap * gap / 2) / 6
    T = m['gamma'] * gap / 2
    k = H * H - 1 - T * T / 12 + m['m2'] * a * a / 12
    f = 3 * (mu + 4 * k) / (m['gamma'] * T / 2 - m['m2'] * a + 4 * H * T)
    return [arb(0), H, a, T, arb(1), arb(1), f, m['gamma'] * f / 2 - 2 * T, arb(0)]


def own_stage_a(C, w, controls_only=False):
    src = Path(C['source_dir'])
    common = records.unpack(read(src / 'RESULT.json'))
    rows = listing(src / 'checkpoints')
    start = [b for c, b in rows if c == C['restart']]
    ok_shape = len(start) == 1 and rows[-1][0] == C['total'] and all(b['guard'] == C['finite_guard'] for b in (start[0], rows[-1][1]))
    K1, K2 = C['K']
    h = C['step']
    cells = {}
    flag = False
    st = None
    if ok_shape:
        st = records.unpack(start[0]['state'])
        while st['cell_index'] < C['total']:
            one_cell(st, source_flow, K1, K2, h, keep=lambda i, s, cell: cells.__setitem__(i, (s, cell)))
        flag = same(st, rows[-1][1], SRC_KEYS)
    y0 = C['fresh_y0']()
    jets_K = None
    if flag:
        jets_K = [preparation.wall_jets(y0, common['p'], 0),
                  preparation.wall_jets(records.unpack(records.pack(st['end'])), common['p'], 1)]
    jflag = flag and records.pack(y0) == records.pack(common['y0']) and records.pack(jets_K) == records.pack(common['jets'])
    pflags, prepK = {}, {}
    for v in C['cases']:
        prepK[v] = preparation.prepare(C['eps'][v], common['jets'], common['p'])
        pflags[v] = records.pack(prepK[v]) == records.pack(records.unpack(read(C['case_results'][v]))['preparation'])
    mflags = {v: (own_phase_maps(C, v, common) if flag else {'center': False, 'box': False}) for v in C['cases']}
    D1, D2 = C['D_prime']
    last = C['total'] - 1
    dflag = bool(C['D_prime_recorded']) and K1 <= D1 < D2 <= K2 and last in cells and cells[last][0] <= D1 and D2 <= cells[last][0] + h
    own = {'R0': bool(flag), 'R0j': bool(jflag), 'R0p': pflags, 'R0m': mflags, 'D0': bool(dflag)}
    if not (flag and jflag and all(pflags.values()) and all(all(m.values()) for m in mflags.values()) and dflag):
        return own, None
    if controls_only:
        return own, {}
    s, cell = cells[last]
    up = records.unpack(records.pack(validated.range_on_cell(cell, D1 - s, D2 - s)))
    jets = [common['jets'][0], preparation.wall_jets(up, common['p'], 1)]
    pD = dict(common['p'])
    pD['D'] = interval(D1, D2)
    preps = {v: preparation.prepare(C['eps'][v], jets, pD) for v in C['cases']}
    return own, {'common': common, 'jets': jets, 'D': pD['D'], 'pD': pD, 'preps': preps, 'prepK': prepK,
                 'cells': {i: cells[i] for i in (last - 1, last) if i in cells}}


def controls_as_producer(rec):
    return {'R0': rec['R0_source_last_block_bitwise'], 'R0j': rec['R0j_upper_and_lower_jets_K_reproduced'],
            'R0p': rec['R0p_preparation_K_reproduced'], 'R0m': rec['R0m_accepted_phase_maps_reproduced'],
            'D0': rec['D0_D_prime_recorded_inside_K_and_last_cell']}


def own_mid(x):
    lo, hi = bounds(x)
    return arb((lo + hi) / 2)


def own_points(jets, keys):
    out = []
    for j in jets:
        k = dict(j)
        for key in keys:
            k[key] = [own_mid(v) for v in j[key]] if isinstance(j[key], list) else own_mid(j[key])
        out.append(k)
    return out


def own_meet(x, ident):
    lo, hi = bounds(x)
    u, v = bounds(ident)
    return interval(max(lo, u), min(hi, v)) if max(lo, u) <= min(hi, v) else ident


def own_imposed_jets(y, p, side):
    """Own port of the attribution wall jets: H at its Israel identity value, T and g met with their identities."""
    z = list(y[:9])
    sg = 1 if side == 0 else -1
    vi, lam = (p['v0'], p['lambda_a']) if side == 0 else (p['v1'], p['lambda_b'])
    gap = z[2] - vi
    c = sg * p['gamma'] / 2
    z[1] = -sg * (lam + p['gamma'] * gap * gap / 2) / 6
    z[3] = own_meet(z[3], c * gap)
    z[7] = own_meet(z[7], c * z[6] - 2 * z[3] * z[5])
    cc = source_flow.coeff(z, 5, p)
    out = {name: [cc[j][n] * math.factorial(n) for n in range(6)] for name, j in (('Phi', 2), ('psi', 5), ('f', 6))}
    out.update({'H': z[1], 'T': z[3], 'qbg': p['k'] * z[4] * z[4], 'sigma': sg, 'vi': vi, 'lam': lam})
    return out


def own_point_state(cells, s, h):
    j = max(i for i, (t, cell) in cells.items() if t <= s <= t + h)
    t, cell = cells[j]
    return validated.range_on_cell(cell, s - t, s - t)


def own_Q(prep, D2):
    q2 = fq(D2)
    return {'Q_c7': sum((fq(mr(v)[1]) * q2 ** n for n, v in enumerate(prep['c7'])), Fraction(0)),
            'Q_W0': fq(mr(prep['W'][0])[1]), 'Q_W1': fq(mr(prep['W'][1])[1])}


OWN_KEYS = {'F': ('f',), 'S': ('psi',), 'B': ('Phi',), 'Z': ('H', 'T', 'qbg')}
OWN_VARIANTS = {'FULL': (), 'F': ('F',), 'S': ('S',), 'B': ('B',), 'Z': ('Z',), 'D': ('D',), 'ALL': ('F', 'S', 'B', 'Z', 'D')}


def own_attribution_quantities(C, S, w):
    D1, D2 = C['D_prime']
    K1, K2 = C['K']
    common = S['common']
    out = {}
    for name, jets, p, Dball, Dmid in (('D_prime', S['jets'], S['pD'], S['D'], (D1 + D2) / 2),
                                      ('K', common['jets'], common['p'], common['p']['D'], (K1 + K2) / 2)):
        pt = own_imposed_jets(records.unpack(records.pack(own_point_state(S['cells'], Dmid, C['step']))), common['p'], 1)
        row = {}
        for v, groups in OWN_VARIANTS.items():
            js = [dict(jets[0]), dict(pt if 'D' in groups else jets[1])]
            js = own_points(js, [k for g in groups if g != 'D' for k in OWN_KEYS[g]])
            pp = dict(p)
            pp['D'] = arb(Dmid) if 'D' in groups else Dball
            row[v] = {k: str(x) for k, x in own_Q(preparation.prepare(C['eps'][w], js, pp), D2).items()}
        out[name] = row
    lo, hi = bounds(common['p']['mu'])
    pm = dict(common['p'])
    pm['mu'] = arb((lo + hi) / 2)
    y = C['fresh_y0_mu']((lo + hi) / 2)
    lower = preparation.wall_jets(y, pm, 0)
    cell = None
    for _ in range(C['total']):
        y, cell = validated.step(y, C['step'], pm, source_flow)
    s0 = (C['total'] - 1) * C['step']
    upper = own_imposed_jets(records.unpack(records.pack(validated.range_on_cell(cell, D1 - s0, D2 - s0))), pm, 1)
    pmD = dict(pm)
    pmD['D'] = S['D']
    out['MU_point'] = {k: str(x) for k, x in own_Q(preparation.prepare(C['eps'][w], [lower, upper], pmD), D2).items()}
    return out


def own_image_at(C, G, J, X, c0):
    Gi = [(fq(bounds(v)[0]), fq(bounds(v)[1])) for v in G]
    new = []
    for i in range(3):
        Ci = Fraction(C[i])
        lo = c0[i] - max(Ci * Gi[i][0], Ci * Gi[i][1])
        hi = c0[i] - min(Ci * Gi[i][0], Ci * Gi[i][1])
        for j in range(3):
            a, b = fq(bounds(J[i][j])[0]), fq(bounds(J[i][j])[1])
            m = (int(i == j) - max(Ci * a, Ci * b), int(i == j) - min(Ci * a, Ci * b))
            d = (X[j][0] - c0[j], X[j][1] - c0[j])
            pr = [m[0] * d[0], m[0] * d[1], m[1] * d[0], m[1] * d[1]]
            lo, hi = lo + min(pr), hi + max(pr)
        if max(X[i][0], lo) > min(X[i][1], hi):
            return None
        new.append((max(X[i][0], lo), min(X[i][1], hi)))
    return new


def params(S, w, x):
    p = dict(S['common']['p'])
    p.update(S['preps'][w])
    p['D'] = S['D']
    p['x'] = x
    return p


def exact_krawczyk(C, G, J, X, c):
    """Exact rational interval arithmetic on the recorded G(c) and J(X) bounds."""
    def iv(x):
        lo, hi = bounds(x)
        return fq(lo), fq(hi)

    def mul(a, b):
        v = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
        return min(v), max(v)
    Gi = [iv(v) for v in G]
    Ji = [iv(v) for v in J]
    Cq = [Fraction(v) for v in C]
    new, empty = [], False
    for i in range(3):
        lo = c[i] - max(Cq[i] * Gi[i][0], Cq[i] * Gi[i][1])
        hi = c[i] - min(Cq[i] * Gi[i][0], Cq[i] * Gi[i][1])
        for j in range(3):
            cj = (Cq[i] * Ji[3 * i + j][0], Cq[i] * Ji[3 * i + j][1])
            m = (int(i == j) - max(cj), int(i == j) - min(cj))
            t = mul(m, (X[j][0] - c[j], X[j][1] - c[j]))
            lo, hi = lo + t[0], hi + t[1]
        nlo, nhi = max(X[i][0], lo), min(X[i][1], hi)
        empty = empty or nlo > nhi
        new.append((nlo, nhi))
    return None if empty else new


def components(prof, m, cell, t, h, p, D1, D2):
    """Own recomputation of one cell's comparison (worst subcell per field), components and closure."""
    Dn = prof.D
    worst = [None] * 3
    for k in range(m):
        lo, hi = h * k / m, h * (k + 1) / m
        a = ir.physical_values(validated.range_on_cell(cell, lo, hi), p, 'positive')
        b = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + hi) * Dn / D1))
        for j in range(3):
            E = ir.maximum_abs(a[j] - b[j])
            if worst[j] is None or E > worst[j][0]:
                worst[j] = (E, lo, a[j], b[j])
    out = []
    for j, (E, lo, a, b) in enumerate(worst):
        pa = ir.physical_values(validated.range_on_cell(cell, lo, lo), p, 'positive')[j]
        pd = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + lo) * Dn / D1))[j]
        (ma, ra), (mb, rb) = mr(a), mr(b)
        total = fq(abs(ma - mb) + ra + rb)
        slack = RADIUS * fq(ra + rb) + FLOOR * (1 + fq(abs(ma)) + fq(abs(mb)))
        out.append({'E': E, 'center': abs(ma - mb), 'state': mr(pa)[1], 'source_step': ra - mr(pa)[1],
                    'event': mr(pd)[1], 'native_step': rb - mr(pd)[1], 'closed': total - slack <= fq(E) <= total + slack})
    return out


def verify_phases(C, S, w, X, c, g):
    D1, D2 = C['D_prime']
    h = C['step']
    total = math.ceil(fq(D2) / fq(h))
    recs = {}
    for name in C['phases']:
        d = Path(C['out']) / f'phase-{w}-{name}'
        rec = records.unpack(read(d / 'PHASE.json'))
        recs[name] = rec
        rows = listing(d / 'checkpoints')
        ends = [e for e, _ in rows]
        expect = list(range(C['ck'], total, C['ck'])) + [total]
        gate(g, f'VB0.{w}.{name}.checkpoint_cells', ends == expect, len(ends))
        x = [arb(q(v)) for v in c] if name == 'center' else [interval(q(a), q(b)) for a, b in X]
        p = params(S, w, x)
        low = preparation.wall_increment(S['common']['y0'], S['jets'][0], p, p['eps'])['target']
        fresh = {'task_index': 0, 'cell_index': 0, 'elapsed_seconds': 0.0, 'which': w, 'phase': name, 'p': p,
                 'y': list(S['common']['y0']) + [x[0], low, arb(1)] + [arb(0)] * 5, 'jets': S['jets'], 'max_picard': 0,
                 'cover': [], 'end': None, 'map': None}
        flags = []
        for b in range(len(rows)):
            st = fresh if b == 0 else records.unpack(rows[b - 1][1]['state'])
            while st['cell_index'] < rows[b][0]:
                one_cell(st, nonlinear, D1, D2, h, endpoint=lambda z, st=st: own_map(z, st['p'], st['jets']))
            flags.append(same(st, rows[b][1], PHASE_KEYS))
            if b == len(rows) - 1:
                gate(g, f'VB2.{w}.{name}.own_map_equals_record', records.pack(st['map']) == records.pack(rec['map']))
                gate(g, f'VB3.{w}.{name}.own_cover_is_D_prime', (st['cover'] == [[str(D1), str(D2)]]) == bool(rec['cover_equals_D_prime']))
                gate(g, f'VB4.{w}.{name}.own_end_equals_record', records.pack(st['end']) == records.pack(rec['end']))
                # the producer reads these from its PHASE.json, i.e. after outward canonicalization; VB2/VB4 above
                # establish that the packed forms are equal, so the canonical copies are the same balls
                recs[name] = rec | {'own_map': records.unpack(records.pack(st['map'])), 'own_end': records.unpack(records.pack(st['end']))}
        gate(g, f'VB1.{w}.{name}.all_blocks_bitwise', all(flags), sum(flags))
    return recs


def side_checks(C, S, w, s, recs, X, Xp):
    """VS1-VS6, outside the validity verification: an error here, or a producer side error, is reported as an
    ERROR of the side records and never changes the validity checks."""
    if s.get('side_error') is not None or s.get('prediction_inputs') is None or s.get('attribution_inputs') is None:
        return [], {'producer_side_error': s.get('side_error')}
    try:
        side = []
        fin = records.unpack(read(C['case_results'][w]))
        pi = s['prediction_inputs']
        gate(side, f'VS1.{w}.G_radius_new', pi['G_radius_new'] == [str(fq(mr(v)[1])) for v in recs['center']['own_map']['G']])
        gate(side, f'VS2.{w}.G_radius_accepted', pi['G_radius_accepted'] == [str(fq(mr(v)[1])) for v in fin['G_center']])
        gate(side, f'VS3.{w}.widths', pi['X_widths'] == [str(b - a) for a, b in X] and pi['Xn_widths'] == [str(b - a) for a, b in Xp])
        c0 = [Fraction(v) for v in fin['center']]
        XK = own_image_at(C['C'], fin['G_center'], fin['J_box'], X, c0)
        gate(side, f'VS4.{w}.X_prime_K_exact', pi['XK_box'] == (None if XK is None else [[str(a), str(b)] for a, b in XK]))
        ce, be = recs['center']['own_end'], recs['box']['own_end']
        own_split = {'rad_w_point': str(fq(mr(ce[9])[1])), 'a_box': str(fq(ir.maximum_abs(be[11])) * (Xp[0][1] - Xp[0][0]) / 2),
                     'b0_box': str(fq(ir.maximum_abs(be[13])) * (Xp[1][1] - Xp[1][0]) / 2),
                     'b1_box': str(fq(ir.maximum_abs(be[15])) * (Xp[2][1] - Xp[2][0]) / 2)}
        gate(side, f'VS5.{w}.A_split', s['attribution_inputs']['A_split_rad_w_upper_wall'] == own_split)
        gate(side, f'VS6.{w}.attribution_quantities_bitwise', s['attribution_inputs']['quantities'] == own_attribution_quantities(C, S, w))
        return side, None
    except Exception as error:
        return [], {'verifier_side_error': {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}}


def verify_case(C, w):
    t0 = time.monotonic()
    g = []
    out = Path(C['out'])
    own, S = own_stage_a(C, w)
    jobs = [f'phase-{w}-{n}' for n in C['phases']] + [f'material-{w}']
    every = [f'phase-{v}-{n}' for v in C['cases'] for n in C['phases']] + [f'material-{v}' for v in C['cases']]
    failed = {j: read(out / j / 'CONTROL_FAILED.json') for j in every if (out / j / 'CONTROL_FAILED.json').exists()}
    if failed:
        mine = {j: r for j, r in failed.items() if j in jobs}
        if mine:
            gate(g, f'V0.{w}.own_controls_fail_as_recorded', S is None and all(controls_as_producer(r['controls']) == own for r in mine.values()), own)
        else:
            gate(g, f'V0.{w}.own_controls_pass_and_outcomes_left_unopened', S is not None, own)
        return {'case': w, 'checks': g, 'own_controls': own, 'outcomes_opened': False, 'seconds': time.monotonic() - t0}
    if S is None:
        gate(g, f'V0.{w}.own_controls_pass', False, own)
        return {'case': w, 'checks': g, 'own_controls': own, 'outcomes_opened': False, 'seconds': time.monotonic() - t0}
    X, c = C['old_box'](w)
    terminal = {j: [n for n in ('PHASE.json', 'SUMMARY.json', 'ROOT_INCONSISTENT.json') if (out / j / n).exists()] for j in jobs}
    missing = [j for j, names in terminal.items() if not names or (out / j / 'FAILURE.json').exists()]
    if missing:
        produced = read(out / 'PRODUCER_RESULT.json')
        reported = {r['id'] for r in produced['gates'] if r['group'] == 'T' and not r['pass']}
        gate(g, f'V0.{w}.incomplete_jobs_reported', all(f'T1.{j}.terminal_record' in reported for j in missing), missing)
        return {'case': w, 'checks': g, 'own_controls': own, 'incomplete': missing, 'seconds': time.monotonic() - t0}
    own_fp = {'jets': records.fingerprint(S['jets']), 'preparation': {v: records.fingerprint(S['preps'][v]) for v in C['cases']}}
    mismatch = []
    for j in jobs:
        for name in ('PHASE.json', 'SUMMARY.json'):
            if (out / j / name).exists():
                rec = read(out / j / name)
                gate(g, f'V0.{j}.controls_agree', controls_as_producer(rec['stage_a_controls']) == own)
                if rec['fingerprints'] != own_fp:
                    mismatch.append(j)
    if mismatch:
        r1 = [r for r in read(out / 'PRODUCER_RESULT.json')['gates'] if r['id'].startswith('R1.')]
        gate(g, f'V1.{w}.fingerprint_mismatch_flagged_by_R1', bool(r1) and not r1[0]['pass'], mismatch)
    else:
        gate(g, f'V1.{w}.fingerprints_agree', True)
    recs = verify_phases(C, S, w, X, c, g)
    Xn = exact_krawczyk(C['C'], recs['center']['map']['G'], recs['box']['map']['J'], X, c)
    mat = out / f'material-{w}'
    if (mat / 'ROOT_INCONSISTENT.json').exists():
        gate(g, f'VK1.{w}.own_exact_krawczyk_empty_agrees', Xn is None)
        return {'case': w, 'checks': g, 'own_controls': own, 'own_new_box': None, 'seconds': time.monotonic() - t0}
    s = read(mat / 'SUMMARY.json')
    if s['arrays']['sha256'] != sha(mat / 'CELLS.f64'):
        raise RuntimeError('Cell array changed after publication')
    Xp = [(Fraction(a), Fraction(b)) for a, b in s['krawczyk']['new_box']]
    gate(g, f'VK1.{w}.own_exact_krawczyk_nonempty', Xn is not None)
    gate(g, f'VK2.{w}.own_box_inside_producer_box_inside_X', Xn is not None and all(
        a <= pa <= na <= nb <= pb <= b for (a, b), (pa, pb), (na, nb) in zip(X, Xp, Xn)),
         None if Xn is None else [show(nb - na) for na, nb in Xn])
    gate(g, f'VK3.{w}.recorded_X_and_center', s['krawczyk']['X'] == [[str(a), str(b)] for a, b in X] and s['krawczyk']['c'] == [str(v) for v in c])
    D1, D2 = C['D_prime']
    step, m = C['step'], C['m']
    prof = C['profile'](w)
    p = params(S, w, [interval(q(a), q(b)) for a, b in Xp])
    eps = p['eps']
    y0 = list(S['common']['y0']) + [p['x'][0], preparation.wall_increment(S['common']['y0'], S['jets'][0], p, eps)['target']]
    state = {'task_index': 0, 'cell_index': 0, 'elapsed_seconds': 0.0, 'name': w, 'y': list(y0), 'p': p, 'max_picard': 0}
    rows = listing(mat / 'checkpoints')
    ends = [e for e, _ in rows]
    total = math.ceil(fq(D2) / fq(step))
    gate(g, f'VM0.{w}.checkpoint_cells', ends == list(range(C['ck'], total, C['ck'])) + [total], len(ends))
    data = array('d')
    data.frombytes((mat / 'CELLS.f64').read_bytes())
    n = s['arrays']['rows_per_column']
    cols = {name: data[k * n:(k + 1) * n] for k, name in enumerate(s['arrays']['columns'])}
    argmax = {f: s['fieldsummary'][f]['argmax_cell'] for f in FIELDS}
    sample = set(C['sample_blocks']) | {next(b for b, e in enumerate(ends) if cc < e) for cc in argmax.values()}
    interior, event_part, covered, gaps = arb(0), arb(0), fmpq(0), 0
    flags, exact, mism, checked, unclosed, Y = [], {}, 0, 0, 0, None
    for b, (end, body) in enumerate(rows):
        while state['cell_index'] < end:
            i = state['cell_index']
            t = i * step
            h = min(step, D2 - t)
            pc = state['p']
            ynext, cell = validated.step(state['y'], h, pc, prepared_flow)
            for k in range(m):
                a0, a1 = h * k / m, h * (k + 1) / m
                if t + a0 != covered:
                    gaps += 1
                covered = t + a1
                cuts = [a0, a1] if not (t + a0 < D1 < t + a1) else [a0, D1 - t, a1]
                for u0, u1 in zip(cuts, cuts[1:]):
                    ell = (-2 * eps) * validated.range_on_cell(cell, u0, u1)[5]
                    piece = (u1 - u0) * ell.exp()
                    if t + u1 <= D1:
                        interior += piece
                    else:
                        event_part += piece
            if b in sample:
                comp = components(prof, m, cell, t, h, pc, D1, D2)
                for j, f in enumerate(FIELDS):
                    unclosed += 0 if comp[j]['closed'] else 1
                    for cname in COLS:
                        checked += 1
                        if cols[f + ':' + cname][i] != up_float(fq(comp[j][cname])):
                            mism += 1
                    if argmax[f] == i:
                        exact[f] = comp[j]
            if t + h == D2:
                Y = validated.range_on_cell(cell, D1 - t, h)
            state['y'] = ynext
            state['cell_index'] += 1
            state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
        flags.append(same(state, body, MAT_KEYS))
        state = records.unpack(body['state'])
    gate(g, f'VM1.{w}.all_material_blocks_bitwise', all(flags), sum(flags))
    gate(g, f'VM2.{w}.closure_agrees_on_sampled_cells', (unclosed == 0) == (s['closure_violations'] == 0), unclosed)
    gate(g, f'VM3.{w}.coverage_agrees', (gaps == 0 and covered == D2) == (s['coverage_gaps'] == 0 and s['coverage_end_equals_D2']))
    gate(g, f'VM4.{w}.columns_equal_upward_rounding_of_exact', mism == 0, {'checked': checked, 'mismatches': mism, 'blocks': sorted(sample)})
    for f in FIELDS:
        fs = s['fieldsummary'][f]
        e = exact.get(f)
        ok = e is not None and str(e['E']) == fs['bound_exact'] and all(str(e[k]) == fs['argmax_components_exact'][k] for k in fs['argmax_components_exact'])
        gate(g, f'VA.{w}.{f}.argmax_exact', ok, fs['argmax_cell'])
        gate(g, f'VC.{w}.{f}.column_max_is_bound', max(cols[f + ':E']) == up_float(Fraction(fs['bound_exact'])))
        shares = {'CENTER_DISCREPANCY': e['center'], 'STATE_RADIUS': e['state'],
                  'COMPARISON_STEP': e['source_step'] + e['native_step'], 'EVENT_WIDTH': e['event']} if e else {}
        gate(g, f'VD.{w}.{f}.dominant_width', bool(shares) and max(shares, key=lambda k: shares[k]) == fs['dominant_width'])
    Llo, Lhi = bounds(interior)[0], bounds(interior)[1] + bounds(event_part)[1]
    gate(g, f'VL.{w}.own_separation_enclosure_equals_producer', [str(Llo), str(Lhi)] == s['proper_separation']['enclosure'],
         [show(fq(Llo)), show(fq(Lhi))])
    for N in C['degrees']:
        L = ir.exact(read(C['record'](w, N))['proper_separation'])
        gate(g, f'VL.{w}.N{N}.separation_bound', str(max(abs(Llo - L), abs(Lhi - L))) == s['proper_separation'][str(N)]['bound_exact'])
    kseed = arb(ir.exact(read(C['seed_path'])['k']))
    pl = state['p']
    for N in C['degrees']:
        grid = read(C['grid'](w, N))
        for wall, y, node in (('lower', y0, 0), ('upper', Y, N)):
            A, ell, Phi = ir.physical_values(y, pl, 'positive')
            rho = eps * y[5] + y[9]
            WN = arb(ir.exact(grid['seed_fields'][node][0]))
            AN, BN = arb(ir.exact(grid['A'][node])), arb(ir.exact(grid['B'][node]))
            mine = {'A': ir.maximum_abs(A - AN), 'ell': ir.maximum_abs(ell - arb(ir.exact(grid['ell'][node]))),
                    'Phi': ir.maximum_abs(Phi - arb(ir.exact(grid['Phi'][node]))), 'rho_A_minus_W': ir.maximum_abs(rho - (AN - WN)),
                    'clock_rate': ir.maximum_abs(rho.exp() - (BN - WN).exp()),
                    'log_angular_radius': ir.maximum_abs((A - pl['k'].log() / 2) - (AN - kseed.log() / 2))}
            rec = s['walls'][str(N)][wall]
            gate(g, f'VW.{w}.N{N}.{wall}', all(str(v) == rec[k]['bound_exact'] for k, v in mine.items()))
    side, side_error = side_checks(C, S, w, s, recs, X, Xp)
    return {'case': w, 'checks': g, 'side_checks': side, 'side_error': side_error, 'own_controls': own,
            'own_new_box': [[str(a), str(b)] for a, b in Xn] if Xn else None,
            'own_separation': [str(Llo), str(Lhi)], 'seconds': time.monotonic() - t0}


def expected_label(produced, summaries):
    failed = {r['group'] for r in produced['gates'] if not r['pass']}
    for group, label in ORDER:
        if group in failed:
            return label
    if sorted(summaries) != sorted(CONFIG['cases']):
        return 'TECHNICAL_INCOMPLETE'

    def dom(f):
        d = {summaries[w]['fieldsummary'][f]['dominant_width'] for w in summaries}
        return d.pop() if len(d) == 1 else 'MIXED'
    return f"REPREPARED__A_DOMINATED_BY_{dom('A')}__PHI_DOMINATED_BY_{dom('Phi')}"


def recorded_pids(out):
    pids = []
    for p in sorted(Path(out).glob('*/*.json')):
        if p.name in ('PHASE.json', 'SUMMARY.json', 'ROOT_INCONSISTENT.json', 'CONTROL_FAILED.json', 'progress.json'):
            body = read(p)
            if isinstance(body.get('pid'), int):
                pids.append(body['pid'])
    return sorted(set(pids))


def live_producers(pids):
    live = []
    for pid in pids:
        try:
            cmd = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        except OSError:
            continue
        if 'reprep.py' in cmd:
            live.append([pid, cmd])
    return live


ATT = CONFIG['attribution']
PRE = CONFIG['prediction']


def own_outcome(Qv):
    full = Qv['FULL']
    if full < Fraction(1, 2 ** (-ATT['floor_log2'])):
        return 'NOT_APPLICABLE', None
    rho = {v: Qv[v] / full for v in ('F', 'S', 'B', 'Z', 'D', 'ALL')}
    if rho['ALL'] > Fraction(ATT['decisive_max']):
        return 'FLOOR_LIMITED', rho
    for gname in ('F', 'S', 'B', 'Z', 'D'):
        if rho[gname] <= Fraction(ATT['decisive_max']) and all(rho[o] >= Fraction(ATT['other_min']) for o in ('F', 'S', 'B', 'Z', 'D') if o != gname):
            return 'DECISIVE_' + gname, rho
    return 'MIXED', rho


def own_attribution_label(summaries):
    outs, mu_named, carriers = [], True, {}
    floor = Fraction(1, 2 ** (-ATT['floor_log2']))
    for w in CONFIG['cases']:
        A = summaries[w]['attribution_inputs']
        Q = A['quantities']
        for qn in ('Q_c7', 'Q_W0', 'Q_W1'):
            o, _ = own_outcome({v: Fraction(Q['D_prime'][v][qn]) for v in Q['D_prime']})
            outs.append(o)
            full = Fraction(Q['D_prime']['FULL'][qn])
            mu_named = mu_named and full >= floor and Fraction(Q['MU_point'][qn]) / full <= Fraction(ATT['mu_bracket_max'])
        sp = {k: Fraction(v) for k, v in A['A_split_rad_w_upper_wall'].items()}
        parts = [('POINT_PART', sp['rad_w_point']), ('A_BOX', sp['a_box']), ('B0_BOX', sp['b0_box']), ('B1_BOX', sp['b1_box'])]
        best = max(v for _, v in parts)
        carriers[w] = next(k for k, v in parts if v == best)
    classes = {ATT['classes'][o.split('_', 1)[1]] for o in outs if o.startswith('DECISIVE_')}
    if all(o.startswith('DECISIVE_') for o in outs) and len(classes) == 1:
        label = 'NEXT_WIDTH__' + classes.pop()
        if label == 'NEXT_WIDTH__MODE_JET_RADIUS' and mu_named:
            label += '__MU_BRACKET'
    elif all(o == 'NOT_APPLICABLE' for o in outs):
        label = 'ATTRIBUTION_NOT_APPLICABLE'
    elif 'FLOOR_LIMITED' in outs:
        label = 'ATTRIBUTION_FLOOR_LIMITED'
    else:
        label = 'ATTRIBUTION_MIXED'
    car = set(carriers.values())
    carrier = car.pop() if len(car) == 1 else 'MIXED'
    return label + '__A_CARRIED_BY_' + carrier + ('__A_NEXT_WIDTH_UNDECIDED' if carrier == 'A_BOX' else '')


def own_confirm(num, den, lo, hi, extra=True):
    floor = Fraction(1, 2 ** (-PRE['denominator_floor_log2']))
    return num is not None and den is not None and den >= floor and lo <= num / den <= hi and bool(extra)


def own_scores(summaries, label, previous):
    """Own scoring of the frozen prediction table; returns {row key: outcome}."""
    floor = Fraction(1, 2 ** (-PRE['denominator_floor_log2']))
    res = {}

    def put(key, num, den, iv, extra=True):
        lo, hi = Fraction(PRE[iv]['interval'][0]), Fraction(PRE[iv]['interval'][1])
        res[key] = 'CONFIRMED' if own_confirm(num, den, lo, hi, extra) else 'REFUTED'
    for w in CONFIG['cases']:
        sm = summaries[w]
        Q = sm['attribution_inputs']['quantities']
        pi = sm['prediction_inputs']
        put(f'P1.{w}.Q_c7', Fraction(Q['D_prime']['FULL']['Q_c7']), Fraction(Q['K']['FULL']['Q_c7']), 'P1')
        for qn in ('Q_W0', 'Q_W1'):
            put(f'P2.{w}.{qn}', Fraction(Q['D_prime']['FULL'][qn]), Fraction(Q['K']['FULL'][qn]), 'P2')
        for i, x in enumerate(('a', 'b0', 'b1')):
            put(f'P3.{w}.rad G {x}', Fraction(pi['G_radius_new'][i]), Fraction(pi['G_radius_accepted'][i]), 'P3')
            put(f'P4.{w}.width {x}', Fraction(pi['Xn_widths'][i]), None if pi['XK_widths'] is None else Fraction(pi['XK_widths'][i]), 'P4')
        put(f'P5.{w}.width a', Fraction(pi['Xn_widths'][0]), Fraction(pi['X_widths'][0]), 'P5')
        for pid, f in (('P6', 'A'), ('P7', 'Phi')):
            prev = None if previous is None else Fraction(previous[w][f]['bound_exact'])
            put(f'{pid}.{w}.{f} bound', Fraction(sm['fieldsummary'][f]['bound_exact']), prev, pid,
                sm['fieldsummary'][f]['dominant_width'] == 'STATE_RADIUS')
        for prep in ('D_prime', 'K'):
            for qn in ('Q_c7', 'Q_W0', 'Q_W1'):
                full = Fraction(Q[prep]['FULL'][qn])
                ok = (full >= floor and Fraction(Q[prep]['F'][qn]) / full <= Fraction(PRE['P8']['rho_F_max'])
                      and Fraction(Q[prep]['D'][qn]) / full >= Fraction(PRE['P8']['rho_D_min']))
                res[f'P8.{w}.{prep}.{qn}'] = 'CONFIRMED' if ok else 'REFUTED'
    res['P9.None.label'] = 'CONFIRMED' if label == PRE['P9']['label'] else 'REFUTED'
    return res


def verify_side_records(C, produced, summaries, cases_records):
    out = Path(C['out'])
    att = read(out / 'ATTRIBUTION.json') if (out / 'ATTRIBUTION.json').exists() else None
    pre = read(out / 'PREDICTION.json') if (out / 'PREDICTION.json').exists() else None
    if att is None or pre is None:
        return {'attribution_verification': 'ERROR', 'prediction_verification': 'ERROR', 'reason': 'side record missing'}
    errors = {w: rec.get('side_error') for w, rec in cases_records.items() if rec.get('side_error') is not None}
    if errors and produced['classification_provisional'].startswith('REPREPARED__'):
        consistent = att.get('assigned') is False and pre.get('scored') is False
        return {'attribution_verification': 'ERROR', 'prediction_verification': 'ERROR', 'reason': 'side computation error',
                'side_errors': errors, 'records_unassigned': consistent}
    side_ok = all(r['pass'] for rec in cases_records.values() for r in rec.get('side_checks', []))
    if not produced['classification_provisional'].startswith('REPREPARED__'):
        a_ok = att['assigned'] is False
        p_ok = pre['scored'] is False
        return {'attribution_verification': 'AGREES' if a_ok else 'DISAGREES', 'prediction_verification': 'AGREES' if p_ok else 'DISAGREES',
                'own_attribution_label': None, 'own_prediction_outcome': None}
    own_label = own_attribution_label(summaries)
    scores = own_scores(summaries, produced['classification_provisional'], C.get('previous'))
    theirs = {f"{r['id']}.{r['case']}.{r['quantity']}": r['outcome'] for r in pre['rows']}
    own_outcome_all = 'NEAR_NULL_CONFIRMED' if all(v == 'CONFIRMED' for v in scores.values()) else 'NEAR_NULL_REFUTED'
    return {'attribution_verification': 'AGREES' if side_ok and att.get('label') == own_label else 'DISAGREES',
            'prediction_verification': 'AGREES' if side_ok and theirs == scores and pre.get('outcome') == own_outcome_all else 'DISAGREES',
            'own_attribution_label': own_label, 'own_prediction_outcome': own_outcome_all,
            'side_checks_passed': side_ok}


def verify_final(C, cases_records):
    g = []
    out = Path(C['out'])
    produced = read(out / 'PRODUCER_RESULT.json')
    summaries = {}
    if produced['outcomes_opened']:
        for w in C['cases']:
            if (out / f'material-{w}' / 'SUMMARY.json').exists():
                summaries[w] = read(out / f'material-{w}' / 'SUMMARY.json')
    for w, rec in cases_records.items():
        for r in rec['checks']:
            g.append(r)
    expected = expected_label(produced, summaries)
    gate(g, 'VC.producer_label_follows_frozen_order', produced['classification_provisional'] == expected, expected)
    if not C['fixture']:
        live = live_producers(recorded_pids(out))
        gate(g, 'VP.no_live_recorded_producer_pid', not live, live)
    agreed = all(r['pass'] for r in g)
    try:
        side = verify_side_records(C, produced, summaries, cases_records)
    except Exception as error:
        side = {'attribution_verification': 'ERROR', 'prediction_verification': 'ERROR',
                'reason': 'verifier side error', 'error': {'type': type(error).__name__, 'message': str(error)}}
    return {'classification': produced['classification_provisional'] if agreed else 'UNRESOLVED_VERIFICATION', 'resolved': agreed,
            'side_records': side,
            'producer_classification_provisional': produced['classification_provisional'],
            'checks_passed': sum(r['pass'] for r in g), 'checks_total': len(g), 'checks': g,
            'failed': [r['id'] for r in g if not r['pass']], 'utc': now(), 'shared_inherited_engine_disclosed': True,
            'imports_reprep_or_assemble': False,
            'label_rule': 'producer label kept (technical labels included) iff every agreement check passes'}


def real_context():
    ir.capacity = lambda: {'replaced_for_replay': True}
    profiles = {}

    def profile(w):
        if w not in profiles:
            profiles[w] = ir.SavedProfile(CONFIG['case_of'][w])
        return profiles[w]

    def old_box(w):
        audit = read(PACKET['connected'] / 'INDEPENDENT_AUDIT.json')['endpoint_identity'][w]
        if not (audit['pass'] and audit['old_gates_recomputed_pass']
                and audit['old_result_sha256'] == sha(PACKET['finite'] / 'output' / w / 'RESULT.json')):
            raise RuntimeError('Old root image not accepted')
        X = [(Fraction(r['exact'][0]), Fraction(r['exact'][1])) for r in audit['translated_root_image']]
        return X, [(a + b) / 2 for a, b in X]
    spatial = PACKET['spatial'] / 'inputs'
    run3 = read(RUN3 / 'outputs' / 'PRODUCER_RESULT.json')
    run3v = read(RUN3 / 'verification' / 'VERIFICATION.json')
    fin = PACKET['finite'] / 'output'
    return {'out': OUT, 'source_dir': fin / 'source', 'case_results': {w: fin / w / 'RESULT.json' for w in CONFIG['cases']},
            'case_dirs': {w: fin / w for w in CONFIG['cases']},
            'fresh_y0': lambda: own_initial(read(PACKET['finite'] / 'BINDINGS.json')),
            'fresh_y0_mu': lambda mu: own_initial(read(PACKET['finite'] / 'BINDINGS.json'), mu),
            'previous': {w: {f: {'bound_exact': read(RUN3 / 'outputs' / w / 'SUMMARY.json')['fieldsummary'][f]['bound_exact']} for f in FIELDS}
                         for w in CONFIG['cases']},
            'cases': CONFIG['cases'], 'phases': CONFIG['phases'], 'eps': {w: ir.exact(CONFIG['epsilon'][w]) for w in CONFIG['cases']},
            'K': tuple(ir.exact(v) for v in CONFIG['D_K']), 'D_prime': tuple(ir.exact(v) for v in CONFIG['D_prime']),
            'D_prime_recorded': run3['narrowed_interval'] == CONFIG['D_prime'] and run3v['resolved']
            and run3v['classification'] == run3['classification_provisional'],
            'step': ir.exact(CONFIG['step']), 'total': CONFIG['source_total_cells'], 'restart': CONFIG['source_restart_cell'],
            'finite_guard': CONFIG['finite_guard'], 'm': CONFIG['subcells'], 'ck': CONFIG['checkpoint_cells'],
            'C': CONFIG['preconditioner_diagonal'], 'old_box': old_box, 'profile': profile, 'degrees': CONFIG['degrees'],
            'seed_path': PACKET['native'] / 'results/fine_c4/SEED.json',
            'grid': lambda w, N: spatial / f"fine_c4_case{CONFIG['case_of'][w]}_N{N}_p80.grid.json",
            'record': lambda w, N: spatial / f"fine_c4_case{CONFIG['case_of'][w]}_N{N}_p80.json",
            'sample_blocks': CONFIG['verifier_sample_blocks'], 'fixture': False}


def frozen_check():
    frozen = read(RUN / 'FREEZE.json')
    for name, digest in frozen['inputs'].items():
        if sha(name) != digest:
            raise RuntimeError('Changed input ' + name)
    for name, digest in frozen['sources'].items():
        if sha(RUN / name) != digest:
            raise RuntimeError('Changed source ' + name)
    return sha(RUN / 'FREEZE.json')


def own_check(path):
    """Own stage-A controls on the real inputs, returning before any D' jet, preparation or flow (no outcome)."""
    from common4 import source_hashes, runtime_fingerprint
    C = real_context()
    own = {w: own_stage_a(C, w, controls_only=True)[0] for w in C['cases']}
    ok = all(o['R0'] and o['R0j'] and all(o['R0p'].values()) and all(all(m.values()) for m in o['R0m'].values()) and o['D0']
             for o in own.values())
    rec = {'utc': now(), 'own_controls': own, 'all_controls_pass': ok, 'outcomes_computed': False,
           'control_records_identical_across_amplitudes': len({json.dumps(o, sort_keys=True) for o in own.values()}) == 1,
           'sources': source_hashes(), 'runtime': runtime_fingerprint()}
    atomic(path, rec, True)
    print(json.dumps({k: rec[k] for k in ('all_controls_pass', 'outcomes_computed', 'control_records_identical_across_amplitudes')}), flush=True)


def main(argv):
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    mode = argv[1]
    if mode == 'check':
        own_check(argv[2])
        return
    target = VER / (f'VERIFICATION_{argv[2]}.json' if mode == 'case' else 'VERIFICATION.json')
    if target.exists() or any(VER.glob(f'FAILURE_{mode}*.json')):
        raise RuntimeError('Verification step already terminal or failed closed')
    try:
        guard = frozen_check()

        def alarm(*args):
            raise TimeoutError('Frozen verifier wall budget')
        signal.signal(signal.SIGALRM, alarm)
        signal.alarm(CONFIG['verifier_wall_seconds'])
        C = real_context()
        if mode == 'case':
            result = verify_case(C, argv[2])
        else:
            result = verify_final(C, {w: read(VER / f'VERIFICATION_{w}.json') for w in CONFIG['cases']})
        signal.alarm(0)
        result.update({'guard': guard, 'address_space': limits, 'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT'),
                       'verifier_source_sha256': sha(Path(__file__).resolve())})
        atomic(target, result, True)
        print(json.dumps({k: result.get(k) for k in ('case', 'classification', 'checks_passed', 'checks_total', 'failed')} |
                         {'own_checks': len(result.get('checks', []))}), flush=True)
    except Exception as error:
        atomic(VER / f'FAILURE_{mode}_{int(time.time())}.json', {'type': type(error).__name__, 'error': str(error),
                                                               'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise


if __name__ == '__main__':
    if not ((len(sys.argv) == 3 and sys.argv[1] == 'case' and sys.argv[2] in CONFIG['cases']) or (len(sys.argv) == 2 and sys.argv[1] == 'final')
            or (len(sys.argv) == 3 and sys.argv[1] == 'check')):
        raise SystemExit('usage: verify4.py case <positive|negative> | verify4.py final | verify4.py check <record.json>')
    main(sys.argv)
