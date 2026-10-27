"""Producer: narrow the certified upper-wall interval D* inside the accepted last two cells, then
re-evaluate the accepted material comparisons on [0, D2] with 64 subcells, and bound the wall and
proper-separation observables. No new flow, no changed flow parameter, no time evolution.

Event exclusion: K = [Dlo, Dhi] contains D* (inherited certificate). The exact static background
satisfies both upper-wall junction conditions at D*:
    e_I = H - (lambda_b + gamma (P - v1)^2 / 2) / 6 = 0,      e_R = T + gamma (P - v1) / 2 = 0
(the identities of the inherited preparation.wall_jets with sigma = -1). A subinterval of K on which the
validated enclosure of e_I or of e_R excludes 0 cannot contain D*.
    python -B <run>/code/narrow.py run <mode|positive|negative>
"""
import json
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
import mode_flow  # noqa: E402
import prepared_flow  # noqa: E402
from series import bounds, hull, interval  # noqa: E402
import identity_run as ir  # noqa: E402
from common3 import (RUN, OUT, PACKET, CONFIG, now, sha, read, atomic, atomic_bytes, fq, up_float, show,  # noqa: E402
                     check_environment, limit_address_space, capacity, freeze_guard)

COMPARED = ('max_errors', 'domain_maxima', 'event_cover', 'event_derivative', 'max_picard', 'cell_index',
            'task_index', 'name', 'p', 'y')
COLUMNS = ('E', 'center', 'state', 'source_step', 'event', 'native_step')
CLASSES = ('CENTER_DISCREPANCY', 'STATE_RADIUS', 'COMPARISON_STEP', 'EVENT_WIDTH')
CLOSURE_RADIUS = Fraction(1, 2 ** (-CONFIG['closure_radius_relative_log2']))
CLOSURE_FLOOR = Fraction(1, 2 ** (-CONFIG['closure_absolute_log2']))


class EventInconsistent(Exception):
    def __init__(self, message, details):
        super().__init__(message)
        self.details = details


def parts(x):
    lo, hi = bounds(x)
    return (lo + hi) / 2, (hi - lo) / 2


def ratio(v, E):
    if E == 0:
        return None
    r = fq(v) / fq(E)
    return float(r) if abs(r) < 10 ** 300 else (1e300 if r > 0 else -1e300)


def fields_of(name):
    return ['W', 'H', 'Phi', 'T', 'exp(-W)', 'psi', 'f', 'g'] if name == 'mode' else ['A', 'ell', 'Phi']


def contains_zero(x):
    lo, hi = bounds(x)
    return lo <= 0 <= hi


def checkpoints(folder, task):
    rows = []
    for path in sorted(Path(folder).glob(f'{task:02d}-*.json')):
        body = read(path)
        if records.fingerprint(body) != path.name.split('-')[-1][:-5]:
            raise RuntimeError('Checkpoint digest mismatch ' + path.name)
        rows.append((int(path.name.split('-')[1]), path, body))
    return rows


def same_as_checkpoint(state, body):
    packed = records.pack({k: state[k] for k in COMPARED})
    bad = [k for k in COMPARED if packed[k] != body['state'][k]]
    return not bad, bad


def replay_block(name, state, P, prof, on_cell=None):
    """Inherited cell update (identity_run.integrate body) for one checkpoint block; on_cell sees each cell."""
    engine = mode_flow if name == 'mode' else prepared_flow
    Dlo, Dhi, step = P['Dlo'], P['Dhi'], P['step']
    while state['cell_index'] * step < Dhi:
        i = state['cell_index']
        t = i * step
        h = min(step, Dhi - t)
        y, cell = validated.step(state['y'], h, state['p'], engine)
        ranged = validated.range_on_cell(cell, fmpq(0), h)
        before = prof.enclose(t * prof.D / Dhi, min(prof.D, (t + h) * prof.D / Dlo))
        after = ir.physical_values(ranged, state['p'], name)
        state['max_errors'] = [max(a, ir.maximum_abs(b - c)) for a, b, c in zip(state['max_errors'], after, before)]
        state['domain_maxima'] = [max(a, ir.maximum_abs(b)) for a, b in zip(state['domain_maxima'], ranged)]
        if name == 'mode' and t + h >= Dlo:
            lo, hi = max(fmpq(0), Dlo - t), min(h, Dhi - t)
            v = mode_flow.determinant_mu(validated.range_on_cell(cell, lo, hi), state['p'])
            state['event_derivative'] = v if state['event_derivative'] is None else hull(state['event_derivative'], v)
            state['event_cover'].append({'cell': i, 'left': t + lo, 'right': t + hi, 'F_mu': v})
        if on_cell is not None:
            on_cell(i, t, h, cell, state)
        state['y'] = y
        state['cell_index'] += 1
        state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
        if state['cell_index'] % CONFIG['checkpoint_cells'] == 0 or t + h == Dhi:
            return state
    return state


def event_models(name, P):
    """Replay from the last checkpoint at or before the first event cell to the end; keep the event cells' models."""
    cks = checkpoints(P['checkpoint_dirs'][name], P['task_of'][name])
    first = min(P['event_cells'])
    starts = [c for c in cks if c[0] <= first]
    state = records.unpack(starts[-1][2]['state']) if starts else P['fresh_states'][name]()
    models, checks = {}, []

    def keep(i, t, h, cell, st):
        if i in P['event_cells']:
            models[i] = (t, h, cell, st['p'])
    for cell_index, path, body in cks:
        if cell_index <= state['cell_index']:
            continue
        state = replay_block(name, state, P, P['profiles'][name], keep)
        ok, bad = same_as_checkpoint(state, body)
        checks.append({'end_cell': cell_index, 'bitwise_equal': ok, 'differs': bad})
        state = records.unpack(body['state'])
    if sorted(models) != sorted(P['event_cells']):
        raise RuntimeError('Event cells not reached')
    return models, checks


def event_pieces(P):
    """Common grid of K: each half of K split into equal subintervals; seam at the cell boundary."""
    Dlo, Dhi, seam, M = P['Dlo'], P['Dhi'], P['seam'], P['event_M']
    out = []
    for left, right, idx in ((Dlo, seam, P['event_cells'][0]), (seam, Dhi, P['event_cells'][1])):
        w = (right - left) / M
        for k in range(M):
            out.append((left + k * w, left + (k + 1) * w if k < M - 1 else right, idx))
    return out


def event_functions(y, p):
    H, Pv, T = y[1], y[2], y[3]
    d = Pv - p['v1']
    return H - (p['lambda_b'] + p['gamma'] * d * d / 2) / 6, T + p['gamma'] * d / 2


def narrow_flow(models, P):
    pieces = event_pieces(P)
    keep, exI, exR = [], 0, 0
    for a, b, idx in pieces:
        t, h, cell, p = models[idx]
        y = validated.range_on_cell(cell, a - t, b - t)
        eI, eR = event_functions(y, p)
        zI, zR = contains_zero(eI), contains_zero(eR)
        exI += 0 if zI else 1
        exR += 0 if zR else 1
        if zI and zR:
            keep.append((a, b))
    deriv = None
    for idx, (left, right) in ((P['event_cells'][0], (P['Dlo'], P['seam'])), (P['event_cells'][1], (P['seam'], P['Dhi']))):
        t, h, cell, p = models[idx]
        y = validated.range_on_cell(cell, left - t, right - t)
        H, Pv, T, E = y[1], y[2], y[3], y[4]
        dI = -T * T / 3 - p['k'] * E * E - p['gamma'] * (Pv - p['v1']) * T / 6
        deriv = dI if deriv is None else hull(deriv, dI)
    rec = {'pieces': len(pieces), 'kept': len(keep), 'excluded_by_e_I': exI, 'excluded_by_e_R': exR,
           'contiguous': all(keep[i][1] == keep[i + 1][0] for i in range(len(keep) - 1)),
           'e_I_derivative_on_K': [str(v) for v in bounds(deriv)], 'e_I_monotone_on_K': not contains_zero(deriv)}
    if not keep:
        return None, rec
    rec['interval'] = [str(keep[0][0]), str(keep[-1][1])]
    return (keep[0][0], keep[-1][1]), rec


def common_event(P):
    """Every job recomputes the narrowed interval from all three accepted flows; the intersection is used."""
    per, models_all, checks = {}, {}, {}
    lo, hi = P['Dlo'], P['Dhi']
    empty = []
    for name in P['flows']:
        models, ck = event_models(name, P)
        models_all[name] = models
        checks[name] = ck
        iv, rec = narrow_flow(models, P)
        per[name] = rec
        if iv is None:
            empty.append(name)
        else:
            lo, hi = max(lo, iv[0]), min(hi, iv[1])
    details = {'per_flow': per, 'block_checks': checks,
               'event_stage_bitwise_equal': all(c['bitwise_equal'] for v in checks.values() for c in v)}
    if empty:
        raise EventInconsistent('No subinterval of K survives for flows ' + ', '.join(empty), details | {'empty_flows': empty})
    if lo >= hi:
        raise EventInconsistent('Per-flow narrowed intervals do not intersect', details | {'empty_flows': []})
    return (lo, hi), per, models_all, checks


class Recompare:
    """New comparison on [0, D2] with the narrowed D' and 64 subcells, plus the separation integral."""

    def __init__(self, P, name, D1, D2):
        self.P, self.name, self.D1, self.D2 = P, name, D1, D2
        self.fields = fields_of(name)
        self.cols = {(f, c): array('d') for f in self.fields for c in COLUMNS}
        self.best = {f: None for f in self.fields}
        self.closure_violations = 0
        self.covered_to = fmpq(0)
        self.gaps = 0
        self.interior = arb(0)
        self.event_part = arb(0)
        self.cells_used = 0

    def p_new(self, p):
        return p if self.name == 'mode' else (p | {'D': interval(self.D1, self.D2)})

    def cell(self, i, t, h, cell, state):
        D1, D2, m, name = self.D1, self.D2, self.P['subcells'], self.name
        if t >= D2:
            return
        prof = self.P['profile']
        Dn = prof.D
        p = self.p_new(state['p'])
        self.cells_used += 1
        worst = [None] * len(self.fields)
        for k in range(m):
            lo, hi = h * k / m, h * (k + 1) / m
            if t + lo >= D2:
                break
            if t + hi > D2:
                hi = D2 - t
            if t + lo != self.covered_to:
                self.gaps += 1
            self.covered_to = t + hi
            a = ir.physical_values(validated.range_on_cell(cell, lo, hi), p, name)
            b = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + hi) * Dn / D1))
            for j in range(len(self.fields)):
                E = ir.maximum_abs(a[j] - b[j])
                if worst[j] is None or E > worst[j][0]:
                    worst[j] = (E, lo, a[j], b[j])
            if name != 'mode':
                self.integrate(cell, t, lo, hi, a[1], p)
        for j, f in enumerate(self.fields):
            E, lo, a, b = worst[j]
            pa = ir.physical_values(validated.range_on_cell(cell, lo, lo), p, name)[j]
            pd = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + lo) * Dn / D1))[j]
            (ma, ra), (mb, rb) = parts(a), parts(b)
            r0, rd = parts(pa)[1], parts(pd)[1]
            total = fq(abs(ma - mb) + ra + rb)
            slack = CLOSURE_RADIUS * fq(ra + rb) + CLOSURE_FLOOR * (1 + fq(abs(ma)) + fq(abs(mb)))
            if not (total - slack <= fq(E) <= total + slack):
                self.closure_violations += 1
            comp = {'E': E, 'center': abs(ma - mb), 'state': r0, 'source_step': ra - r0, 'event': rd, 'native_step': rb - rd}
            for c in COLUMNS:
                self.cols[(f, c)].append(up_float(fq(comp[c])))
            if self.best[f] is None or E > self.best[f]['E']:
                self.best[f] = {'cell': i, 'subcell_left_offset': str(lo), 'E': E,
                                'components': {c: comp[c] for c in COLUMNS if c != 'E'}}

    def integrate(self, cell, t, lo, hi, ell_range, p):
        D1 = self.D1
        s0, s1 = t + lo, t + hi
        if s1 <= D1:
            self.interior += (s1 - s0) * ell_range.exp()
        elif s0 >= D1:
            self.event_part += (s1 - s0) * ell_range.exp()
        else:
            left = ir.physical_values(validated.range_on_cell(cell, lo, D1 - t), p, self.name)[1]
            right = ir.physical_values(validated.range_on_cell(cell, D1 - t, hi), p, self.name)[1]
            self.interior += (D1 - s0) * left.exp()
            self.event_part += (s1 - D1) * right.exp()

    def summary(self):
        out = {}
        for f in self.fields:
            best = self.best[f]
            E, comp = best['E'], best['components']
            shares = {'CENTER_DISCREPANCY': comp['center'], 'STATE_RADIUS': comp['state'],
                      'COMPARISON_STEP': comp['source_step'] + comp['native_step'], 'EVENT_WIDTH': comp['event']}
            out[f] = {'bound_exact': str(E), 'bound': show(fq(E)), 'argmax_cell': best['cell'],
                      'argmax_subcell_left_offset': best['subcell_left_offset'],
                      'argmax_components_exact': {k: str(v) for k, v in comp.items()},
                      'argmax_components': {k: show(fq(v)) for k, v in comp.items()},
                      'shares': {k: ratio(v, E) for k, v in shares.items()},
                      'dominant_width': max(shares, key=lambda k: shares[k]),
                      'component_sup_over_cells_upper': {c: max(self.cols[(f, c)]) for c in COLUMNS}}
        return out


def wall_observables(P, name, D1, D2, models, y0, p0):
    """Exact-family enclosures at both walls versus the saved grid wall nodes (signed flows)."""
    pnew = p0 | {'D': interval(D1, D2)}
    eps = p0['eps']
    Y = None
    for a, b, idx in event_pieces(P):
        if a >= D1 and b <= D2:
            t, h, cell, p = models[idx]
            y = validated.range_on_cell(cell, a - t, b - t)
            Y = y if Y is None else [hull(u, v) for u, v in zip(Y, y)]
    walls = {'lower': y0, 'upper': Y}
    out = {}
    k = p0['k']
    for N in P['degrees']:
        grid = read(P['grid'](N))
        k_seed = arb(ir.exact(read(P['seed_path'])['k']))
        rows = {}
        for wall, node in (('lower', 0), ('upper', N)):
            y = walls[wall]
            A, ell, Phi = ir.physical_values(y, pnew, name)
            rho = eps * y[5] + y[9]
            exact = {'A': A, 'ell': ell, 'Phi': Phi, 'rho_A_minus_W': rho, 'clock_rate': rho.exp(),
                     'log_angular_radius': A - k.log() / 2}
            WN = arb(ir.exact(grid['seed_fields'][node][0]))
            AN, BN = arb(ir.exact(grid['A'][node])), arb(ir.exact(grid['B'][node]))
            saved = {'A': AN, 'ell': arb(ir.exact(grid['ell'][node])), 'Phi': arb(ir.exact(grid['Phi'][node])),
                     'rho_A_minus_W': AN - WN, 'clock_rate': (BN - WN).exp(), 'log_angular_radius': AN - k_seed.log() / 2}
            rows[wall] = {q: {'bound_exact': str(ir.maximum_abs(exact[q] - saved[q])),
                              'bound': show(fq(ir.maximum_abs(exact[q] - saved[q]))),
                              'enclosure_radius': show(fq(parts(exact[q])[1])),
                              'center_offset': show(fq(abs(parts(exact[q])[0] - parts(saved[q])[0])))} for q in exact}
            rows[wall]['state_enclosures'] = {key: [str(v) for v in bounds(y[j])] for j, key in ((0, 'W'), (1, 'H'), (4, 'E'), (5, 'psi'))}
            rows[wall]['radius_split_at_wall'] = {'rad_W': show(fq(parts(y[0])[1])), 'eps_rad_psi': show(fq(abs(eps) * parts(y[5])[1])),
                                                  'rad_w': show(fq(parts(y[9])[1])), 'rad_P': show(fq(parts(y[2])[1])),
                                                  'eps_rad_f': show(fq(abs(eps) * parts(y[6])[1]))}
        out[str(N)] = rows
    return out


def separation(P, R, name):
    out = {}
    lo = bounds(R.interior)[0]
    hi = bounds(R.interior)[1] + bounds(R.event_part)[1]
    for N in P['degrees']:
        L = ir.exact(read(P['record'](N))['proper_separation'])
        bound = max(abs(lo - L), abs(hi - L))
        out[str(N)] = {'bound_exact': str(bound), 'bound': show(fq(bound)), 'saved_proper_separation': str(L)}
    out['enclosure'] = [str(lo), str(hi)]
    out['interior_radius'] = show(fq(parts(R.interior)[1]))
    out['event_part_upper'] = show(fq(bounds(R.event_part)[1]))
    return out


def execute(P):
    started, cpu0 = time.monotonic(), time.process_time()
    name = P['name']
    (D1, D2), per, models_all, ev_checks = common_event(P)
    R = Recompare(P, name, D1, D2)
    cks = checkpoints(P['checkpoint_dirs'][name], P['task_of'][name])
    if [c[0] for c in cks] != P['expected_checkpoint_cells']:
        raise RuntimeError('Unexpected checkpoint cell indices')
    blocks = []
    start = P['fresh_states'][name]()
    y0, p0 = list(start['y']), start['p']
    for n, (cell_index, path, body) in enumerate(cks):
        if body['guard'] != P['guard']:
            raise RuntimeError('Checkpoint guard mismatch')
        state = replay_block(name, start, P, P['profiles'][name], R.cell)
        ok, bad = same_as_checkpoint(state, body)
        blocks.append({'block': n, 'end_cell': cell_index, 'bitwise_equal': ok, 'differs': bad})
        replayed_max = [str(v) for v in state['max_errors']]
        start = records.unpack(body['state'])
        P['progress'](n + 1, len(cks))
    Dlo, Dhi = P['Dlo'], P['Dhi']
    summary = {'flow': name, 'fields': R.fields,
               'event': {'K': [str(Dlo), str(Dhi)], 'common_narrowed_interval': [str(D1), str(D2)],
                         'narrowed_width': show(fq(D2 - D1)), 'K_width': show(fq(Dhi - Dlo)),
                         'width_ratio': float(fq(D2 - D1) / fq(Dhi - Dlo)), 'per_flow': per,
                         'block_checks': {k: v for k, v in ev_checks.items()},
                         'native_D_in_narrowed': D1 <= P['profile'].D <= D2,
                         'native_D_distance_bound': str(max(abs(P['profile'].D - D1), abs(D2 - P['profile'].D)))},
               'blocks': len(blocks), 'all_blocks_bitwise_equal': all(b['bitwise_equal'] for b in blocks),
               'event_stage_bitwise_equal': all(c['bitwise_equal'] for v in ev_checks.values() for c in v),
               'block_checks': blocks, 'accepted_max_errors_exact': replayed_max,
               'accepted_max_errors_source': 'running maxima of the replayed final state (before checkpoint reload)',
               'closure_violations': R.closure_violations, 'coverage_gaps': R.gaps,
               'coverage_end_equals_D2': R.covered_to == D2, 'cells_used': R.cells_used,
               'fieldsummary': R.summary()}
    if name != 'mode':
        summary['walls'] = wall_observables(P, name, D1, D2, models_all[name], y0, p0)
        summary['proper_separation'] = separation(P, R, name)
    payload = array('d')
    names = []
    for f in R.fields:
        for c in COLUMNS:
            payload.extend(R.cols[(f, c)])
            names.append(f + ':' + c)
    summary['arrays'] = {'columns': names, 'rows_per_column': R.cells_used, 'dtype': 'float64 little-endian, upward-rounded'}
    summary['elapsed_seconds'] = time.monotonic() - started
    summary['cpu_seconds'] = time.process_time() - cpu0
    return summary, payload


def real_context(name, out):
    ident = PACKET['identity']
    conn = read(PACKET['connected'] / 'BINDINGS.json')['config']
    Dlo, Dhi = map(ir.exact, conn['D'])
    if [str(Dlo), str(Dhi)] != CONFIG['D_interval']:
        raise RuntimeError('D interval differs from the frozen value')
    ir.capacity = lambda: {'replaced_for_replay': True}
    profiles = {f: ir.SavedProfile(None if f == 'mode' else CONFIG['case_of_flow'][f]) for f in CONFIG['flows']}
    profile = profiles[name]
    cells = CONFIG['cells']
    expected = [256 * k for k in range(1, cells // 256 + 1)] + ([cells] if cells % 256 else [])
    case = CONFIG['case_of_flow'].get(name)
    spatial = PACKET['spatial'] / 'inputs'

    def progress(done, total):
        atomic(out / 'status.json', {'flow': name, 'state': 'RUNNING', 'blocks_done': done, 'blocks_total': total,
                                     'utc': now(), 'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT')})
    return {'name': name, 'flows': CONFIG['flows'], 'task_of': CONFIG['task_index'], 'profile': profile, 'profiles': profiles,
            'Dlo': Dlo, 'Dhi': Dhi, 'seam': ir.exact(CONFIG['event_seam']), 'event_M': CONFIG['event_subintervals_per_half'],
            'event_cells': CONFIG['event_cells'], 'step': ir.exact(CONFIG['step']), 'subcells': CONFIG['subcells'],
            'checkpoint_dirs': {f: ident / 'output' / f / 'checkpoints' for f in CONFIG['flows']},
            'expected_checkpoint_cells': expected, 'guard': CONFIG['identity_guard'],
            'fresh_states': {f: (lambda f=f: ir.fresh_state(f, CONFIG['task_index'][f])) for f in CONFIG['flows']},
            'degrees': CONFIG['degrees'], 'seed_path': PACKET['native'] / 'results/fine_c4/SEED.json',
            'grid': (lambda N: spatial / f'fine_c4_case{case}_N{N}_p80.grid.json'),
            'record': (lambda N: spatial / f'fine_c4_case{case}_N{N}_p80.json'), 'progress': progress}


def produce(P, out, guard_sha, inherited_result, extra=None):
    """Execute one flow job and write its records exactly as production does (also used by the fixtures)."""
    out = Path(out)
    if (out / 'SUMMARY.json').exists() or (out / 'FAILURE.json').exists() or (out / 'EVENT_INCONSISTENT.json').exists():
        raise RuntimeError('Flow output already terminal or failed closed; no restart')
    try:
        summary, payload = execute(P)
    except EventInconsistent as error:
        atomic(out / 'EVENT_INCONSISTENT.json', {'status': 'EVENT_EXCLUSION_INCONSISTENT', 'flow': P['name'], 'guard': guard_sha,
                                                 'error': str(error), 'details': error.details, 'utc': now()}, True)
        atomic(out / 'status.json', {'flow': P['name'], 'state': 'EVENT_EXCLUSION_INCONSISTENT', 'utc': now(), 'pid': os.getpid()})
        return 'EVENT_EXCLUSION_INCONSISTENT'
    except Exception as error:
        atomic(out / 'FAILURE.json', {'status': 'FAILED_CLOSED', 'type': type(error).__name__, 'error': str(error),
                                      'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise
    summary['replayed_bounds_equal_inherited_result'] = summary['accepted_max_errors_exact'] == inherited_result
    summary.update({'guard': guard_sha, 'utc': now(), 'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT'),
                    'new_flows': 0, 'flow_parameters_changed': False, 'time_evolution': False} | (extra or {}))
    atomic_bytes(out / 'CELLS.f64', payload.tobytes())
    summary['arrays']['sha256'] = sha(out / 'CELLS.f64')
    atomic(out / 'SUMMARY.json', summary, True)
    atomic(out / 'status.json', {'flow': P['name'], 'state': 'COMPLETE', 'utc': now(), 'pid': os.getpid(),
                                 'compute_slot': os.environ.get('COMPUTE_SLOT')})
    return 'COMPLETE'


def check_real_entry(name, record_path):
    """Real-input structure check without any outcome: profiles, checkpoints, p['D'] and record writes."""
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    P = real_context(name, Path(record_path).parent)
    rows = {f: [c[0] for c in checkpoints(P['checkpoint_dirs'][f], P['task_of'][f])] for f in P['flows']}
    p_check = records.unpack(read(sorted(Path(P['checkpoint_dirs'][name]).glob('*.json'))[0])['state'])['p']
    rec = {'flow': name, 'utc': now(), 'address_space': limits, 'profiles_built': sorted(P['profiles']),
           'checkpoint_cells_as_expected': all(v == P['expected_checkpoint_cells'] for v in rows.values()),
           'flow_D_contains_K': bool(p_check['D'].contains(P['Dlo']) and p_check['D'].contains(P['Dhi'])),
           'event_cells_in_last_block': all(P['expected_checkpoint_cells'][-2] <= c < P['expected_checkpoint_cells'][-1] for c in P['event_cells']),
           'outcomes_computed': False}
    atomic(record_path, rec, True)
    print(json.dumps(rec), flush=True)
    return rec


def run(name):
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    out = OUT / name
    guard_sha, _ = freeze_guard()
    cap = capacity()
    if cap['available_bytes'] < CONFIG['minimum_available_bytes']:
        raise RuntimeError('Insufficient available memory')
    P = real_context(name, out)
    p_check = records.unpack(checkpoints(P['checkpoint_dirs'][name], P['task_of'][name])[0][2]['state'])['p']
    if not (p_check['D'].contains(P['Dlo']) and p_check['D'].contains(P['Dhi'])):
        raise RuntimeError('Flow D parameter does not cover K')

    def alarm(*args):
        raise TimeoutError('Frozen job wall budget')
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(CONFIG['job_wall_seconds'])
    inherited = read(PACKET['identity'] / 'output' / name / 'RESULT.json')['max_error_bounds_exact']
    status = produce(P, out, guard_sha, inherited, {'address_space': limits, 'capacity': cap})
    signal.alarm(0)
    print(json.dumps({'flow': name, 'status': status}), flush=True)


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'run' and sys.argv[2] in CONFIG['flows']:
        run(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == 'check' and sys.argv[2] in CONFIG['flows']:
        check_real_entry(sys.argv[2], sys.argv[3])
    else:
        raise SystemExit('usage: narrow.py run <flow> | narrow.py check <flow> <record.json>')
