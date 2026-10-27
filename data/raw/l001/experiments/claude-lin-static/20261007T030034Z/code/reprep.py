"""Producer for run 20261007T030034Z: narrowed-D' re-preparation, one Krawczyk root iteration, material re-evaluation.

Stage A (every job, deterministic, before any outcome):
  replay the accepted finite-packet source flow's last block from its own checkpoint with the inherited
  cell update and require bitwise agreement with the accepted final checkpoint (control R0); recompute the
  accepted upper-wall jets over K (control R0j) and the accepted K preparations (control R0p); check that D'
  equals the run-3 record and lies in K and in the last source cell (control D0). Any failed control stops the
  job before an outcome exists (CONTROL_FAILED.json). Then: upper-wall jets over D' (range of the replayed
  last source cell over D') and the C7/W preparation with the D ball replaced by D'.
Stage B (phase jobs): the inherited 17-state nonlinear flow with that preparation, at the exact center c of the
  certified old root enclosure X and over X, with the inherited upper-wall map over D'.
Stage C (material jobs): one Krawczyk step K(X) = c - C G(c) + (I - C J(X))(X - c); X' = X intersect K(X)
  (the root in X lies in K(X)); then the inherited 11-state prepared flow with X' and the D' preparation on
  [0, D2], compared with the native polynomials on 64 subcells per cell, walls and proper separation.
    python -B reprep.py phase <positive|negative> <center|box>
    python -B reprep.py material <positive|negative>
    python -B reprep.py check <record.json>
"""
import json
import math
import os
import signal
import sys
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
from common4 import (OUT, PACKET, RUN3, CONFIG, now, sha, read, atomic, atomic_bytes, fq, up_float, show,  # noqa: E402
                     check_environment, limit_address_space, capacity, freeze_guard, source_hashes, runtime_fingerprint)

SOURCE_KEYS = ('y', 'p', 'cover', 'end', 'max_picard', 'cell_index', 'task_index', 'which')
COLUMNS = ('E', 'center', 'state', 'source_step', 'event', 'native_step')
FIELDS = ('A', 'ell', 'Phi')
CLOSURE_RADIUS = Fraction(1, 2 ** (-CONFIG['closure_radius_relative_log2']))
CLOSURE_FLOOR = Fraction(1, 2 ** (-CONFIG['closure_absolute_log2']))


class ControlFailed(Exception):
    def __init__(self, controls):
        super().__init__('A stage-A control failed; no outcome was computed')
        self.controls = controls


class RootInconsistent(Exception):
    def __init__(self, record):
        super().__init__('The Krawczyk image does not meet the certified box')
        self.record = record


def parts(x):
    lo, hi = bounds(x)
    return (lo + hi) / 2, (hi - lo) / 2


def rad(x):
    return fq(parts(x)[1])


def ratio(v, E):
    if E == 0:
        return None
    r = fq(v) / fq(E)
    return float(r) if abs(r) < 10 ** 300 else 1e300


def f2q(x):
    if isinstance(x, fmpq):
        return x
    x = Fraction(x)
    return fmpq(x.numerator, x.denominator)


def mid_ball(x):
    lo, hi = bounds(x)
    return arb((lo + hi) / 2)


def checkpoint_rows(folder):
    rows = []
    for path in sorted(Path(folder).glob('*.json')):
        body = read(path)
        if records.fingerprint(body) != path.name.split('-')[-1][:-5]:
            raise RuntimeError('Checkpoint digest mismatch ' + path.name)
        rows.append((int(path.name.split('-')[1]), path, body))
    return rows


def finite_cell(state, engine, lo, hi, h, endpoint=None, keep=None):
    """One cell of the inherited finite-packet integrate loop (runner.integrate body), without timing fields."""
    j = state['cell_index']
    s = j * h
    ynext, cell = validated.step(state['y'], h, state['p'], engine)
    if not all(v.is_finite() for v in ynext):
        raise ArithmeticError('Nonfinite interval')
    if bounds(cell['box'][4])[0] <= 0:
        raise ArithmeticError('exp(-W) positivity lost')
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
        keep(j, s, cell)
    state['y'] = ynext
    state['cell_index'] += 1


FINITE_PHASE_KEYS = ('y', 'p', 'cover', 'end', 'map', 'max_picard', 'cell_index', 'task_index')


def finite_initial(binding, mu_point=None):
    """Port of the finite runner's initial(model): the fresh background state at s = 0 from which the accepted
    lower-wall jets were formed (its stored copy is outward-canonicalized, so the jets need the fresh one).
    mu_point replaces the mu bracket by one point (attribution input only)."""
    model, cfg = binding['model_exact'], binding['config']
    p = {k: arb(ir.exact(v)) for k, v in model.items()}
    a = interval(*map(ir.exact, cfg['root']))
    mu = interval(*map(ir.exact, cfg['mu'])) if mu_point is None else arb(f2q(mu_point))
    H = -(p['lambda_a'] + p['gamma'] * (a - p['v0']) * (a - p['v0']) / 2) / 6
    T = p['gamma'] * (a - p['v0']) / 2
    k = H * H - 1 - T * T / 12 + p['m2'] * a * a / 12
    B = p['gamma'] * T / 2 - p['m2'] * a + 4 * H * T
    f = 3 * (mu + 4 * k) / B
    return [arb(0), H, a, T, arb(1), arb(1), f, p['gamma'] * f / 2 - 2 * T, arb(0)]


def canonical(x):
    """The outward-canonicalized copy that the inherited checkpoint writer stores and reloads."""
    return records.unpack(records.pack(x))


def accepted_phase_maps(P, which, common):
    """Replay the last block of the accepted finite certificate's two phase flows with this run's driver and map."""
    rows = checkpoint_rows(Path(P['case_dirs'][which]) / 'checkpoints')
    accepted = records.unpack(read(P['case_results'][which]))
    K1, K2 = P['K']
    out = {}
    for task, name in ((0, 'center'), (1, 'box')):
        mine = [r for r in rows if r[1].name.startswith(f'{task:02d}-')]
        start = [r for r in mine if r[0] == P['source_restart_cell']]
        end = [r for r in mine if r[0] == P['source_total_cells']]
        if len(start) != 1 or len(end) != 1 or start[0][2]['guard'] != P['finite_guard'] or end[0][2]['guard'] != P['finite_guard']:
            out[name] = False
            continue
        st = records.unpack(start[0][2]['state'])
        while st['cell_index'] < P['source_total_cells']:
            finite_cell(st, nonlinear, K1, K2, P['step'], endpoint=lambda z: map_at(z, st['p'], common['jets']))
        packed = records.pack({k: st[k] for k in FINITE_PHASE_KEYS})
        bitwise = all(packed[k] == end[0][2]['state'].get(k) for k in FINITE_PHASE_KEYS)
        if name == 'center':
            result = records.pack(st['map']['G']) == records.pack(accepted['G_center'])
        else:
            result = records.pack([st['map']['J'][i * 3:i * 3 + 3] for i in range(3)]) == records.pack(accepted['J_box'])
        out[name] = bool(bitwise and result)
    return out


def stage_a(P, which, controls_only=False):
    """Controls first (no outcome before they pass), then the D' jets and preparations."""
    src = Path(P['source_dir'])
    common = records.unpack(read(src / 'RESULT.json'))
    rows = checkpoint_rows(src / 'checkpoints')
    starts = [r for r in rows if r[0] == P['source_restart_cell']]
    final = rows[-1] if rows else None
    shape = (len(starts) == 1 and final is not None and final[0] == P['source_total_cells']
             and starts[0][2]['guard'] == P['finite_guard'] and final[2]['guard'] == P['finite_guard'])
    K1, K2 = P['K']
    h = P['step']
    D1, D2 = P['D_prime']
    models = {}
    differs = list(SOURCE_KEYS)
    state = None
    if shape:
        state = records.unpack(starts[0][2]['state'])
        while state['cell_index'] < P['source_total_cells']:
            finite_cell(state, source_flow, K1, K2, h, keep=lambda j, s, cell: models.__setitem__(j, (s, cell)))
        packed = records.pack({k: state[k] for k in SOURCE_KEYS})
        differs = [k for k in SOURCE_KEYS if packed[k] != final[2]['state'].get(k)]
    r0 = shape and not differs
    jets_K = None
    y0 = P['fresh_y0']()
    y0_ok = records.pack(y0) == records.pack(common['y0'])
    if r0:
        jets_K = [preparation.wall_jets(y0, common['p'], 0), preparation.wall_jets(canonical(state['end']), common['p'], 1)]
    r0j = r0 and y0_ok and records.pack(jets_K) == records.pack(common['jets'])
    preps_K, r0p = {}, {}
    for w in P['cases']:
        accepted = records.unpack(read(P['case_results'][w]))['preparation']
        mine = preparation.prepare(P['epsilon'][w], common['jets'], common['p'])
        preps_K[w] = mine
        r0p[w] = records.pack(mine) == records.pack(accepted)
    r0m = {w: (accepted_phase_maps(P, w, common) if r0 else {'center': False, 'box': False}) for w in P['cases']}
    last = P['source_total_cells'] - 1
    d0 = (bool(P['D_prime_matches_record']) and K1 <= D1 < D2 <= K2 and last in models
          and models[last][0] <= D1 and D2 <= models[last][0] + h)
    controls = {'R0_source_last_block_bitwise': bool(r0), 'R0_checkpoint_shape': bool(shape), 'R0_differing_keys': differs,
                'R0j_fresh_initial_state_equals_stored': bool(y0_ok),
                'R0j_upper_and_lower_jets_K_reproduced': bool(r0j), 'R0p_preparation_K_reproduced': r0p,
                'R0m_accepted_phase_maps_reproduced': r0m,
                'D0_D_prime_recorded_inside_K_and_last_cell': bool(d0)}
    if not (r0 and r0j and all(r0p.values()) and all(all(v.values()) for v in r0m.values()) and d0):
        raise ControlFailed(controls)
    if controls_only:
        return {'controls': controls}
    s_last, cell_last = models[last]
    end_new = canonical(validated.range_on_cell(cell_last, D1 - s_last, D2 - s_last))
    jets = [common['jets'][0], preparation.wall_jets(end_new, common['p'], 1)]
    Dball = interval(D1, D2)
    p_new = dict(common['p'])
    p_new['D'] = Dball
    preps = {w: preparation.prepare(P['epsilon'][w], jets, p_new) for w in P['cases']}
    return {'common': common, 'jets': jets, 'D_ball': Dball, 'p_new': p_new, 'preps': preps, 'preps_K': preps_K,
            'controls': controls, 'end_new': end_new, 'end_K': state['end'], 'cells': {j: models[j] for j in (last - 1, last) if j in models},
            'fingerprints': {'jets': records.fingerprint(jets), 'preparation': {w: records.fingerprint(preps[w]) for w in P['cases']}}}


def map_at(y, p, jets):
    """Inherited upper-wall map of the finite certificate (runner.map_at), with W read from the flow parameters."""
    eps = p['eps']
    diag, J, G = [], [y[12], y[14], y[16]], [y[10] - preparation.wall_increment(y, jets[1], p, eps)['target']]
    for side, j in enumerate(jets):
        e = preparation.wall_increment(y, j, p, eps)
        w = p['x'][0] if side == 0 else y[9]
        qnew = j['qbg'] * exp(-2 * (eps * e['psi'] + w))
        Delta = j['qbg'] * e1(-2 * (eps * e['psi'] + w)) - e['dr']
        correction = power(e['L'], 5) * (-12 * e['c'] * e['S'] * Delta - 24 * e['t'] * Delta * Delta)
        G.append(p['x'][side + 1] + p['W'][side] + correction)
        cols = [arb(1), arb(0), arb(0)] if side == 0 else [y[11], y[13], y[15]]
        multiplier = power(e['L'], 5) * (-12 * e['c'] * e['S'] - 48 * e['t'] * Delta) * (-2 * qnew)
        J.extend([int(n == side + 1) + multiplier * cols[n] for n in range(3)])
        diag.extend([qnew, Delta, e['S'], e['L'], correction])
    if not all(v.is_finite() for v in G + J + diag):
        raise ArithmeticError('Nonfinite map')
    if not all(bounds(diag[i])[0] > 0 for i in (0, 3, 5, 8)):
        raise ArithmeticError('Wall positivity diagnostic failed')
    return {'G': G, 'J': J, 'wall_diagnostics': diag}


def flow_parameters(A, which, x):
    p = dict(A['common']['p'])
    p.update(A['preps'][which])
    p['D'] = A['D_ball']
    p['x'] = x
    return p


def phase_initial(A, which, name, X, c):
    x = [arb(f2q(v)) for v in c] if name == 'center' else [interval(f2q(a), f2q(b)) for a, b in X]
    p = flow_parameters(A, which, x)
    lower = preparation.wall_increment(A['common']['y0'], A['jets'][0], p, p['eps'])['target']
    y = list(A['common']['y0']) + [x[0], lower, arb(1)] + [arb(0)] * 5
    return {'task_index': 0, 'cell_index': 0, 'elapsed_seconds': 0.0, 'which': which, 'phase': name, 'p': p, 'y': y,
            'jets': A['jets'], 'max_picard': 0, 'cover': [], 'end': None, 'map': None}


def phase_total(P):
    return math.ceil(fq(P['D_prime'][1]) / fq(P['step']))


def run_phase(P, A, which, name, out, guard, progress):
    X, c = P['old_box'](which)
    state = phase_initial(A, which, name, X, c)
    D1, D2 = P['D_prime']
    h = P['step']
    total = phase_total(P)
    extra = {}

    def keep(j, s, cell):
        if s <= D1 < s + h:
            extra['map_at_D1'] = map_at(validated.range_on_cell(cell, D1 - s, D1 - s), state['p'], state['jets'])
            extra['map_at_D2'] = map_at(validated.range_on_cell(cell, D2 - s, D2 - s), state['p'], state['jets'])
    while state['cell_index'] < total:
        finite_cell(state, nonlinear, D1, D2, h, endpoint=lambda z: map_at(z, state['p'], state['jets']), keep=keep)
        if state['cell_index'] % P['checkpoint_cells'] == 0 or state['cell_index'] == total:
            records.save(out, state, guard)
            progress(state['cell_index'], total)
    return {'which': which, 'phase': name, 'map': state['map'], 'cover': state['cover'],
            'cover_equals_D_prime': state['cover'] == [[str(D1), str(D2)]], 'cells': state['cell_index'], 'max_picard': state['max_picard'],
            'end': state['end'],
            'stage_a_controls': A['controls'], 'fingerprints': A['fingerprints'],
            'x': [[str(v) for v in bounds(u)] for u in state['p']['x']], 'center': [str(v) for v in c], 'box': [[str(a), str(b)] for a, b in X],
            'map_at_D1': extra.get('map_at_D1'), 'map_at_D2': extra.get('map_at_D2')}


def krawczyk(C, G, J, X, c):
    """One Krawczyk step: any root in X lies in K(X) = c - C G(c) + (I - C J(X))(X - c)."""
    Jm = [J[i * 3:i * 3 + 3] for i in range(3)]
    M = [[int(i == j) - C[i] * Jm[i][j] for j in range(3)] for i in range(3)]
    d = [interval(f2q(a - cc), f2q(b - cc)) for (a, b), cc in zip(X, c)]
    image = [f2q(c[i]) - C[i] * G[i] + sum((M[i][j] * d[j] for j in range(3)), arb(0)) for i in range(3)]
    box, empty = [], False
    for (a, b), im in zip(X, image):
        lo, hi = (fq(v) for v in bounds(im))
        nlo, nhi = max(a, lo), min(b, hi)
        empty = empty or nlo > nhi
        box.append((nlo, nhi))
    strict = all(a < fq(bounds(im)[0]) and fq(bounds(im)[1]) < b for (a, b), im in zip(X, image))
    rownorm = [None if X[i][1] == X[i][0] else sum(fq(ir.maximum_abs(M[i][j])) * (X[j][1] - X[j][0]) for j in range(3)) / (X[i][1] - X[i][0])
               for i in range(3)]
    return {'image': [[str(v) for v in bounds(im)] for im in image], 'new_box': None if empty else [[str(a), str(b)] for a, b in box],
            'empty': empty, 'strict_inclusion_in_X': strict, 'weighted_row_norms': [None if r is None else show(r) for r in rownorm],
            'old_widths': [show(b - a) for a, b in X], 'new_widths': None if empty else [show(b - a) for a, b in box],
            'width_ratios': None if empty else [None if b == a else float((nb - na) / (b - a)) for (a, b), (na, nb) in zip(X, box)],
            'G_center_radius': [show(rad(g)) for g in G], 'G_center_mid_magnitude': [show(abs(fq(parts(g)[0]))) for g in G],
            'C': [str(v) for v in C], 'X': [[str(a), str(b)] for a, b in X], 'c': [str(v) for v in c]}


def state_split(y, p):
    """Radius split of A = W + eps psi + w and Phi = P + eps f + d at one state enclosure."""
    eps, D, s = p['eps'], p['D'], y[8]
    H0 = power(s, 5) * power(D - s, 6) / (120 * power(D, 6))
    H1 = power(s, 6) * power(s - D, 5) / (120 * power(D, 6))
    c7 = ir.poly(p['c7'], s)
    hb = p['x'][1] * H0 + p['x'][2] * H1
    return {'rad_W': show(rad(y[0])), 'eps_rad_psi': show(abs(fq(eps)) * rad(y[5])), 'rad_w': show(rad(y[9])),
            'rad_P': show(rad(y[2])), 'eps_rad_f': show(abs(fq(eps)) * rad(y[6])), 'rad_d': show(rad(c7 + hb)),
            'rad_d_c7_part': show(rad(c7)), 'rad_d_root_box_part': show(rad(hb))}


ATTR_GROUPS = ('F', 'S', 'B', 'Z', 'D')
ATTR_KEYS = {'F': ('f',), 'S': ('psi',), 'B': ('Phi',), 'Z': ('H', 'T', 'qbg')}
ATTR_VARIANTS = {'FULL': (), 'F': ('F',), 'S': ('S',), 'B': ('B',), 'Z': ('Z',), 'D': ('D',), 'ALL': ATTR_GROUPS}


def midpoint_jets(jets, keys):
    out = []
    for j in jets:
        k = dict(j)
        for key in keys:
            k[key] = [mid_ball(v) for v in j[key]] if isinstance(j[key], list) else mid_ball(j[key])
        out.append(k)
    return out


def meet_or(state_value, identity):
    """Intersection of a state enclosure with its identity value when they meet; otherwise the identity value."""
    lo, hi = bounds(state_value)
    u, v = bounds(identity)
    return interval(max(lo, u), min(hi, v)) if max(lo, u) <= min(hi, v) else identity


def imposed_wall_jets(y, p, side):
    """Attribution input only, not an enclosure claim: the inherited wall_jets with H set to its Israel identity
    value and T and g met with their identities when they meet (away from D* the state need not meet them)."""
    z = list(y[:9])
    sigma = 1 if side == 0 else -1
    vi = p['v0'] if side == 0 else p['v1']
    lam = p['lambda_a'] if side == 0 else p['lambda_b']
    P = z[2]
    c = sigma * p['gamma'] / 2
    z[1] = -sigma * (lam + p['gamma'] * (P - vi) * (P - vi) / 2) / 6
    z[3] = meet_or(z[3], c * (P - vi))
    z[7] = meet_or(z[7], c * z[6] - 2 * z[3] * z[5])
    cc = source_flow.coeff(z, 5, p)
    return {name: [cc[j][n] * math.factorial(n) for n in range(6)] for name, j in [('Phi', 2), ('psi', 5), ('f', 6)]} | {
        'H': z[1], 'T': z[3], 'qbg': p['k'] * z[4] * z[4], 'sigma': sigma, 'vi': vi, 'lam': lam}


def point_state(cells, s, h):
    j = max(i for i, (t, cell) in cells.items() if t <= s <= t + h)
    t, cell = cells[j]
    return validated.range_on_cell(cell, s - t, s - t)


def attribution_quantities(prep, D2):
    """Gross radii: Q_c7 = sum_n rad(c7_n) D2^n (the c7 part of rad d at the upper wall), Q_W0, Q_W1."""
    q = fq(D2)
    return {'Q_c7': sum((rad(v) * q ** n for n, v in enumerate(prep['c7'])), Fraction(0)), 'Q_W0': rad(prep['W'][0]), 'Q_W1': rad(prep['W'][1])}


def variant_preparation(eps, jets, point_upper, p, Dball, Dmid, groups):
    js = [dict(jets[0]), dict(point_upper if 'D' in groups else jets[1])]
    js = midpoint_jets(js, [k for g in groups if g != 'D' for k in ATTR_KEYS[g]])
    pp = dict(p)
    pp['D'] = arb(f2q(Dmid)) if 'D' in groups else Dball
    return preparation.prepare(eps, js, pp)


def point_mu_preparation(P, A, which):
    """The source flow from s = 0 with mu at its bracket midpoint, its last-cell upper jets over D', then prepare."""
    common = A['common']
    lo, hi = bounds(common['p']['mu'])
    mid = (lo + hi) / 2
    pm = dict(common['p'])
    pm['mu'] = arb(mid)
    y = P['fresh_y0_mu'](mid)
    lower = preparation.wall_jets(y, pm, 0)
    h, cell = P['step'], None
    for _ in range(P['source_total_cells']):
        y, cell = validated.step(y, h, pm, source_flow)
    s_last = (P['source_total_cells'] - 1) * h
    D1, D2 = P['D_prime']
    upper = imposed_wall_jets(canonical(validated.range_on_cell(cell, D1 - s_last, D2 - s_last)), pm, 1)
    pD = dict(pm)
    pD['D'] = A['D_ball']
    return preparation.prepare(P['epsilon'][which], [lower, upper], pD)


def attribution_inputs(P, A, which):
    """Q for the D' and the K preparation under each frozen variant, and for the point-mu source variant (D' only)."""
    D1, D2 = P['D_prime']
    K1, K2 = P['K']
    common = A['common']
    eps = P['epsilon'][which]
    out = {}
    for name, jets, p, Dball, Dmid in (('D_prime', A['jets'], A['p_new'], A['D_ball'], (D1 + D2) / 2),
                                      ('K', common['jets'], common['p'], common['p']['D'], (K1 + K2) / 2)):
        point = imposed_wall_jets(canonical(point_state(A['cells'], Dmid, P['step'])), common['p'], 1)
        out[name] = {v: {k: str(x) for k, x in attribution_quantities(variant_preparation(eps, jets, point, p, Dball, Dmid, groups), D2).items()}
                     for v, groups in ATTR_VARIANTS.items()}
    out['MU_point'] = {k: str(x) for k, x in attribution_quantities(point_mu_preparation(P, A, which), D2).items()}
    return out


def exact_image_at(C, G, J, X, c0):
    """X meet [c0 - C G(c0) + (I - C J(B))(X - c0)] in exact rational interval arithmetic; None if empty."""
    out = []
    for i in range(3):
        Ci = fq(f2q(C[i]))
        g = sorted([Ci * fq(bounds(G[i])[0]), Ci * fq(bounds(G[i])[1])])
        lo, hi = c0[i] - g[1], c0[i] - g[0]
        for j in range(3):
            cj = sorted([Ci * fq(bounds(J[i][j])[0]), Ci * fq(bounds(J[i][j])[1])])
            m = (int(i == j) - cj[1], int(i == j) - cj[0])
            d = (X[j][0] - c0[j], X[j][1] - c0[j])
            prods = [m[0] * d[0], m[0] * d[1], m[1] * d[0], m[1] * d[1]]
            lo, hi = lo + min(prods), hi + max(prods)
        nlo, nhi = max(X[i][0], lo), min(X[i][1], hi)
        if nlo > nhi:
            return None
        out.append((nlo, nhi))
    return out


def side_inputs(P, A, which, old, ph, X, Xn):
    """Prediction and attribution inputs. These are outside the validity path: any error here is recorded and
    leaves both side records unassigned; it never fails the material job."""
    try:
        c0 = [Fraction(v) for v in old['center']]
        XK = exact_image_at(P['C'], old['G_center'], old['J_box'], X, c0)
        ce, be = ph['center']['end'], ph['box']['end']
        split = {'rad_w_point': str(rad(ce[9])), 'a_box': str(fq(ir.maximum_abs(be[11])) * (Xn[0][1] - Xn[0][0]) / 2),
                 'b0_box': str(fq(ir.maximum_abs(be[13])) * (Xn[1][1] - Xn[1][0]) / 2),
                 'b1_box': str(fq(ir.maximum_abs(be[15])) * (Xn[2][1] - Xn[2][0]) / 2)}
        prediction = {'G_radius_new': [str(rad(v)) for v in ph['center']['map']['G']],
                      'G_radius_accepted': [str(rad(v)) for v in old['G_center']],
                      'X_widths': [str(b - a) for a, b in X], 'Xn_widths': [str(b - a) for a, b in Xn],
                      'XK_box': None if XK is None else [[str(a), str(b)] for a, b in XK],
                      'XK_widths': None if XK is None else [str(b - a) for a, b in XK], 'old_center': [str(v) for v in c0],
                      'upper_state_radius_at_point_D_mid': [show(rad(v)) for v in
                                                            point_state(A['cells'], (P['D_prime'][0] + P['D_prime'][1]) / 2, P['step'])[:9]]}
        attribution = {'quantities': attribution_inputs(P, A, which), 'A_split_rad_w_upper_wall': split}
        return prediction, attribution, None
    except Exception as error:
        return None, None, {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}


def run_material(P, A, which, out, guard, progress):
    X, c = P['old_box'](which)
    ph = {}
    for name in P['phases']:
        rec = read(Path(P['phase_dir'](which, name)) / 'PHASE.json')
        if rec['guard'] != guard:
            raise RuntimeError('Stale phase record ' + name)
        ph[name] = records.unpack(rec)
        if ph[name]['box'] != [[str(a), str(b)] for a, b in X] or ph[name]['center'] != [str(v) for v in c]:
            raise RuntimeError('Phase record box or center differs ' + name)
    kr = krawczyk(P['C'], ph['center']['map']['G'], ph['box']['map']['J'], X, c)
    if kr['empty']:
        raise RootInconsistent(kr)
    Xn = [(Fraction(a), Fraction(b)) for a, b in kr['new_box']]
    p = flow_parameters(A, which, [interval(f2q(a), f2q(b)) for a, b in Xn])
    eps = p['eps']
    y0 = list(A['common']['y0']) + [p['x'][0], preparation.wall_increment(A['common']['y0'], A['jets'][0], p, eps)['target']]
    state = {'task_index': 0, 'cell_index': 0, 'elapsed_seconds': 0.0, 'name': which, 'y': list(y0), 'p': p, 'max_picard': 0}
    D1, D2 = P['D_prime']
    prof = P['profile'](which)
    Dn, step, m = prof.D, P['step'], P['subcells']
    cols = {(f, cc): array('d') for f in FIELDS for cc in COLUMNS}
    best = {f: None for f in FIELDS}
    closure_bad, gaps, covered = 0, 0, fmpq(0)
    interior, event_part = arb(0), arb(0)
    Y, last = None, None
    while state['cell_index'] * step < D2:
        i = state['cell_index']
        t = i * step
        h = min(step, D2 - t)
        p = state['p']
        ynext, cell = validated.step(state['y'], h, p, prepared_flow)
        if not all(v.is_finite() for v in ynext):
            raise ArithmeticError('Nonfinite material state')
        worst = [None] * 3
        for k in range(m):
            lo, hi = h * k / m, h * (k + 1) / m
            if t + lo != covered:
                gaps += 1
            covered = t + hi
            a = ir.physical_values(validated.range_on_cell(cell, lo, hi), p, 'positive')
            b = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + hi) * Dn / D1))
            for j in range(3):
                E = ir.maximum_abs(a[j] - b[j])
                if worst[j] is None or E > worst[j][0]:
                    worst[j] = (E, lo, a[j], b[j])
            s0, s1 = t + lo, t + hi
            if s1 <= D1:
                interior += (s1 - s0) * a[1].exp()
            elif s0 >= D1:
                event_part += (s1 - s0) * a[1].exp()
            else:
                left = ir.physical_values(validated.range_on_cell(cell, lo, D1 - t), p, 'positive')[1]
                right = ir.physical_values(validated.range_on_cell(cell, D1 - t, hi), p, 'positive')[1]
                interior += (D1 - s0) * left.exp()
                event_part += (s1 - D1) * right.exp()
        for j, f in enumerate(FIELDS):
            E, lo, a, b = worst[j]
            pa = ir.physical_values(validated.range_on_cell(cell, lo, lo), p, 'positive')[j]
            pd = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + lo) * Dn / D1))[j]
            (ma, ra), (mb, rb) = parts(a), parts(b)
            r0, rd = parts(pa)[1], parts(pd)[1]
            total = fq(abs(ma - mb) + ra + rb)
            slack = CLOSURE_RADIUS * fq(ra + rb) + CLOSURE_FLOOR * (1 + fq(abs(ma)) + fq(abs(mb)))
            if not (total - slack <= fq(E) <= total + slack):
                closure_bad += 1
            comp = {'E': E, 'center': abs(ma - mb), 'state': r0, 'source_step': ra - r0, 'event': rd, 'native_step': rb - rd}
            for cc in COLUMNS:
                cols[(f, cc)].append(up_float(fq(comp[cc])))
            if best[f] is None or E > best[f]['E']:
                best[f] = {'cell': i, 'lo': lo, 'E': E, 'components': {cc: comp[cc] for cc in COLUMNS if cc != 'E'}, 'model': cell, 'p': p}
        if t + h == D2:
            Y = validated.range_on_cell(cell, D1 - t, h)
            last = i
        state['y'] = ynext
        state['cell_index'] += 1
        state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
        if state['cell_index'] % P['checkpoint_cells'] == 0 or t + h == D2:
            records.save(out, state, guard)
            progress(state['cell_index'], None)
    fs = {}
    for f in FIELDS:
        bf = best[f]
        E, comp = bf['E'], bf['components']
        shares = {'CENTER_DISCREPANCY': comp['center'], 'STATE_RADIUS': comp['state'],
                  'COMPARISON_STEP': comp['source_step'] + comp['native_step'], 'EVENT_WIDTH': comp['event']}
        fs[f] = {'bound_exact': str(E), 'bound': show(fq(E)), 'argmax_cell': bf['cell'], 'argmax_subcell_left_offset': str(bf['lo']),
                 'argmax_components_exact': {k: str(v) for k, v in comp.items()},
                 'argmax_components': {k: show(fq(v)) for k, v in comp.items()},
                 'shares': {k: ratio(v, E) for k, v in shares.items()}, 'dominant_width': max(shares, key=lambda k: shares[k]),
                 'argmax_state_split': state_split(validated.range_on_cell(bf['model'], bf['lo'], bf['lo']), bf['p']),
                 'component_sup_over_cells_upper': {cc: max(cols[(f, cc)]) for cc in COLUMNS}}
    walls = {}
    kseed = arb(ir.exact(read(P['seed_path'])['k']))
    for N in P['degrees']:
        grid = read(P['grid'](which, N))
        rows = {}
        for wall, y, node in (('lower', y0, 0), ('upper', Y, N)):
            Av, ell, Phi = ir.physical_values(y, p, 'positive')
            rho = eps * y[5] + y[9]
            WN = arb(ir.exact(grid['seed_fields'][node][0]))
            AN, BN = arb(ir.exact(grid['A'][node])), arb(ir.exact(grid['B'][node]))
            exact = {'A': Av, 'ell': ell, 'Phi': Phi, 'rho_A_minus_W': rho, 'clock_rate': rho.exp(),
                     'log_angular_radius': Av - p['k'].log() / 2}
            saved = {'A': AN, 'ell': arb(ir.exact(grid['ell'][node])), 'Phi': arb(ir.exact(grid['Phi'][node])),
                     'rho_A_minus_W': AN - WN, 'clock_rate': (BN - WN).exp(), 'log_angular_radius': AN - kseed.log() / 2}
            rows[wall] = {q: {'bound_exact': str(ir.maximum_abs(exact[q] - saved[q])), 'bound': show(fq(ir.maximum_abs(exact[q] - saved[q]))),
                              'enclosure_radius': show(rad(exact[q])),
                              'center_offset': show(abs(fq(parts(exact[q])[0]) - fq(parts(saved[q])[0])))} for q in exact}
            rows[wall]['state_enclosures'] = {key: [str(v) for v in bounds(y[j])] for j, key in ((0, 'W'), (1, 'H'), (4, 'E'), (5, 'psi'))}
            rows[wall]['radius_split_at_wall'] = state_split(y, p)
        walls[str(N)] = rows
    Llo, Lhi = bounds(interior)[0], bounds(interior)[1] + bounds(event_part)[1]
    sep = {'enclosure': [str(Llo), str(Lhi)], 'interior_radius': show(rad(interior)), 'event_part_upper': show(fq(bounds(event_part)[1]))}
    for N in P['degrees']:
        L = ir.exact(read(P['record'](which, N))['proper_separation'])
        b = max(abs(Llo - L), abs(Lhi - L))
        sep[str(N)] = {'bound_exact': str(b), 'bound': show(fq(b)), 'saved_proper_separation': str(L)}
    old = records.unpack(read(P['case_results'][which]))
    prep, prepK = A['preps'][which], A['preps_K'][which]
    diagnostics = {
        'c7_coefficient_radius': {'old_K': [show(rad(v)) for v in prepK['c7']], 'new_D_prime': [show(rad(v)) for v in prep['c7']]},
        'c7_max_coefficient_radius': {'old_K': show(max(rad(v) for v in prepK['c7'])), 'new_D_prime': show(max(rad(v) for v in prep['c7']))},
        'W_radius': {'old_K': [show(rad(v)) for v in prepK['W']], 'new_D_prime': [show(rad(v)) for v in prep['W']]},
        'G_center_radius': {'old_K': [show(rad(v)) for v in old['G_center']], 'new_D_prime': kr['G_center_radius']},
        'G_center_radius_at_point_D1': [show(rad(v)) for v in ph['center']['map_at_D1']['G']],
        'root_box_widths': {'old': kr['old_widths'], 'new': kr['new_widths'], 'ratio': kr['width_ratios']},
        'upper_state_radius_over_D_prime_vs_K': {'K': [show(rad(v)) for v in A['end_K'][:9]], 'D_prime': [show(rad(v)) for v in A['end_new'][:9]]}}
    prediction_inputs, attribution_record, side_error = side_inputs(P, A, which, old, ph, X, Xn)
    summary = {'which': which, 'stage_a_controls': A['controls'], 'fingerprints': A['fingerprints'], 'krawczyk': kr,
               'phase_records': {n: sha(Path(P['phase_dir'](which, n)) / 'PHASE.json') for n in P['phases']},
               'fieldsummary': fs, 'walls': walls, 'proper_separation': sep, 'closure_violations': closure_bad,
               'coverage_gaps': gaps, 'coverage_end_equals_D2': covered == D2, 'cells': state['cell_index'], 'last_cell': last,
               'max_picard': state['max_picard'], 'diagnostics': diagnostics, 'prediction_inputs': prediction_inputs,
               'attribution_inputs': attribution_record, 'side_error': side_error,
               'arrays': {'columns': [f + ':' + cc for f in FIELDS for cc in COLUMNS], 'rows_per_column': len(cols[('A', 'E')]),
                          'dtype': 'float64 little-endian, upward-rounded'}}
    payload = array('d')
    for f in FIELDS:
        for cc in COLUMNS:
            payload.extend(cols[(f, cc)])
    return summary, payload


def status_writer(out, kind, which):
    def progress(done, total):
        atomic(Path(out) / 'progress.json', {'job': kind, 'which': which, 'cells': done, 'total': total, 'utc': now(),
                                           'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT')})
    return progress


def control_stop(out, error, guard):
    atomic(Path(out) / 'CONTROL_FAILED.json', {'status': 'CONTROL_FAILED', 'controls': error.controls, 'guard': guard,
                                               'outcomes_computed': False, 'utc': now(), 'pid': os.getpid()}, True)


def produce_phase(P, which, name, out, guard):
    out = Path(out)
    if any((out / n).exists() for n in ('PHASE.json', 'FAILURE.json', 'CONTROL_FAILED.json')):
        raise RuntimeError('Phase output already terminal or failed closed; no restart')
    try:
        A = stage_a(P, which)
        rec = run_phase(P, A, which, name, out, guard, status_writer(out, 'phase-' + name, which))
    except ControlFailed as error:
        control_stop(out, error, guard)
        return 'CONTROL_FAILED'
    except Exception as error:
        atomic(out / 'FAILURE.json', {'status': 'FAILED_CLOSED', 'type': type(error).__name__, 'error': str(error),
                                      'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise
    rec.update({'guard': guard, 'utc': now(), 'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT')})
    atomic(out / 'PHASE.json', records.pack(rec), True)
    return 'COMPLETE'


def produce_material(P, which, out, guard):
    out = Path(out)
    if any((out / n).exists() for n in ('SUMMARY.json', 'FAILURE.json', 'ROOT_INCONSISTENT.json', 'CONTROL_FAILED.json')):
        raise RuntimeError('Material output already terminal or failed closed; no restart')
    try:
        A = stage_a(P, which)
        summary, payload = run_material(P, A, which, out, guard, status_writer(out, 'material', which))
    except ControlFailed as error:
        control_stop(out, error, guard)
        return 'CONTROL_FAILED'
    except RootInconsistent as error:
        atomic(out / 'ROOT_INCONSISTENT.json', {'status': 'ROOT_ITERATION_INCONSISTENT', 'krawczyk': error.record, 'guard': guard,
                                                'utc': now(), 'pid': os.getpid()}, True)
        return 'ROOT_ITERATION_INCONSISTENT'
    except Exception as error:
        atomic(out / 'FAILURE.json', {'status': 'FAILED_CLOSED', 'type': type(error).__name__, 'error': str(error),
                                      'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise
    summary.update({'guard': guard, 'utc': now(), 'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT')})
    atomic_bytes(out / 'CELLS.f64', payload.tobytes())
    summary['arrays']['sha256'] = sha(out / 'CELLS.f64')
    atomic(out / 'SUMMARY.json', summary, True)
    return 'COMPLETE'


def old_root_image(which):
    audit = read(PACKET['connected'] / 'INDEPENDENT_AUDIT.json')['endpoint_identity'][which]
    if not audit['pass'] or not audit['old_gates_recomputed_pass']:
        raise RuntimeError('Old root image not accepted')
    if audit['old_result_sha256'] != sha(PACKET['finite'] / 'output' / which / 'RESULT.json'):
        raise RuntimeError('Old root image is stale')
    X = [(Fraction(r['exact'][0]), Fraction(r['exact'][1])) for r in audit['translated_root_image']]
    return X, [(a + b) / 2 for a, b in X]


def real_context():
    ir.capacity = lambda: {'replaced_for_replay': True}
    profiles = {}

    def profile(which):
        if which not in profiles:
            profiles[which] = ir.SavedProfile(CONFIG['case_of'][which])
        return profiles[which]
    spatial = PACKET['spatial'] / 'inputs'
    run3 = read(RUN3 / 'outputs' / 'PRODUCER_RESULT.json')
    run3v = read(RUN3 / 'verification' / 'VERIFICATION.json')
    recorded = (run3['narrowed_interval'] == CONFIG['D_prime'] and run3v['resolved']
                and run3v['classification'] == run3['classification_provisional'])
    fin = PACKET['finite'] / 'output'
    return {'source_dir': fin / 'source', 'case_results': {w: fin / w / 'RESULT.json' for w in CONFIG['cases']},
            'case_dirs': {w: fin / w for w in CONFIG['cases']},
            'fresh_y0': lambda: finite_initial(read(PACKET['finite'] / 'BINDINGS.json')),
            'fresh_y0_mu': lambda mu: finite_initial(read(PACKET['finite'] / 'BINDINGS.json'), mu),
            'cases': CONFIG['cases'], 'phases': CONFIG['phases'], 'epsilon': {w: ir.exact(CONFIG['epsilon'][w]) for w in CONFIG['cases']},
            'K': tuple(ir.exact(v) for v in CONFIG['D_K']), 'D_prime': tuple(ir.exact(v) for v in CONFIG['D_prime']),
            'D_prime_matches_record': recorded, 'step': ir.exact(CONFIG['step']),
            'source_total_cells': CONFIG['source_total_cells'], 'source_restart_cell': CONFIG['source_restart_cell'],
            'finite_guard': CONFIG['finite_guard'], 'subcells': CONFIG['subcells'], 'checkpoint_cells': CONFIG['checkpoint_cells'],
            'C': [ir.exact(v) for v in CONFIG['preconditioner_diagonal']], 'old_box': old_root_image, 'profile': profile,
            'degrees': CONFIG['degrees'], 'seed_path': PACKET['native'] / 'results/fine_c4/SEED.json',
            'grid': lambda which, N: spatial / f"fine_c4_case{CONFIG['case_of'][which]}_N{N}_p80.grid.json",
            'record': lambda which, N: spatial / f"fine_c4_case{CONFIG['case_of'][which]}_N{N}_p80.json",
            'phase_dir': lambda which, name: OUT / f'phase-{which}-{name}'}


def prepare_process():
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    guard, _ = freeze_guard()
    cap = capacity()
    if cap['available_bytes'] < CONFIG['minimum_available_bytes']:
        raise RuntimeError('Insufficient available memory')

    def alarm(*args):
        raise TimeoutError('Frozen job wall budget')
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(CONFIG['job_wall_seconds'])
    return guard, limits


def check_real_entry(path):
    """Real-input structure check without any outcome: paths, checkpoint shape, D' record, old box shape."""
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    P = real_context()
    rows = checkpoint_rows(P['source_dir'] / 'checkpoints')
    boxes = {w: P['old_box'](w)[0] for w in P['cases']}
    controls = {}
    for w in P['cases']:
        try:
            controls[w] = stage_a(P, w, controls_only=True)['controls']
        except ControlFailed as error:
            controls[w] = error.controls
    rec = {'utc': now(), 'address_space': limits, 'D_prime_matches_run3_record': P['D_prime_matches_record'],
           'stage_a_controls_only': controls,
           'all_controls_pass': all(c['R0_source_last_block_bitwise'] and c['R0j_upper_and_lower_jets_K_reproduced']
                                    and all(c['R0p_preparation_K_reproduced'].values())
                                    and all(all(v.values()) for v in c['R0m_accepted_phase_maps_reproduced'].values())
                                    and c['D0_D_prime_recorded_inside_K_and_last_cell'] for c in controls.values()),
           'control_records_identical_across_amplitudes': len({json.dumps(c, sort_keys=True) for c in controls.values()}) == 1,
           'source_checkpoint_cells': [r[0] for r in rows][-3:], 'source_checkpoint_count': len(rows),
           'restart_checkpoint_present': any(r[0] == P['source_restart_cell'] for r in rows),
           'old_boxes_nondegenerate': all(len(b) == 3 and all(lo < hi for lo, hi in b) for b in boxes.values()),
           'D_prime_in_K': P['K'][0] <= P['D_prime'][0] < P['D_prime'][1] <= P['K'][1],
           'phase_cells': phase_total(P), 'outcomes_computed': False, 'sources': source_hashes(), 'runtime': runtime_fingerprint()}
    atomic(path, rec, True)
    print(json.dumps(rec), flush=True)


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'phase' and sys.argv[2] in CONFIG['cases'] and sys.argv[3] in CONFIG['phases']:
        g, _ = prepare_process()
        st = produce_phase(real_context(), sys.argv[2], sys.argv[3], OUT / f'phase-{sys.argv[2]}-{sys.argv[3]}', g)
        signal.alarm(0)
        print(json.dumps({'phase': sys.argv[2:], 'status': st}), flush=True)
        sys.exit(0 if st == 'COMPLETE' else 4)
    elif len(sys.argv) == 3 and sys.argv[1] == 'material' and sys.argv[2] in CONFIG['cases']:
        g, _ = prepare_process()
        st = produce_material(real_context(), sys.argv[2], OUT / f'material-{sys.argv[2]}', g)
        signal.alarm(0)
        print(json.dumps({'material': sys.argv[2], 'status': st}), flush=True)
        sys.exit(0 if st == 'COMPLETE' else 4 if st == 'CONTROL_FAILED' else 5)
    elif len(sys.argv) == 3 and sys.argv[1] == 'check':
        check_real_entry(sys.argv[2])
    else:
        raise SystemExit('usage: reprep.py phase <case> <center|box> | reprep.py material <case> | reprep.py check <record.json>')
