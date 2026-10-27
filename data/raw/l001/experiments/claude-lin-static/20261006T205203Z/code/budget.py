"""Producer: enclosure-width budget of one accepted identity flow by checkpoint-anchored replay.

Replays each 256-cell block of an accepted flow from its own checkpoint (block 0 from the
reconstructed fresh state) with the byte-identical inherited engine, reproduces every
checkpoint bitwise, and splits every per-cell comparison bound E into exact components:
center discrepancy, state radius, source step, event (D) stretch and native step. Also
evaluates the same validated cell on 16 subcells (refined bound). No new flow, no changed
interval, no time evolution.
    python -B <run>/code/budget.py run <mode|positive|negative>
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
import mode_flow  # noqa: E402
import prepared_flow  # noqa: E402
from series import bounds, hull  # noqa: E402
import identity_run as ir  # noqa: E402
from common2 import (RUN, OUT, PACKET, CONFIG, now, sha, read, atomic, atomic_bytes, fq, up_float,  # noqa: E402
                     show, check_environment, limit_address_space, capacity, freeze_guard)

COMPARED = ('max_errors', 'domain_maxima', 'event_cover', 'event_derivative', 'max_picard', 'cell_index',
            'task_index', 'name', 'p', 'y')
COLUMNS = ('E1', 'center', 'state', 'source_step', 'event', 'native_step', 'E16')


def parts(x):
    lo, hi = bounds(x)
    return (lo + hi) / 2, (hi - lo) / 2


def ratio(v, E):
    """Share v/E as a display float, clamped; None when E is zero."""
    if E == 0:
        return None
    r = fq(v) / fq(E)
    return float(r) if abs(r) < 10 ** 300 else (1e300 if r > 0 else -1e300)


def fields_of(name):
    return ['W', 'H', 'Phi', 'T', 'exp(-W)', 'psi', 'f', 'g'] if name == 'mode' else ['A', 'ell', 'Phi']


def attribution(name, y, p):
    """Radii of the state components that enter each compared field (cell start)."""
    if name == 'mode':
        mu_half = parts(p['mu'])[1]
        return {'rad_' + k: parts(y[j])[1] for j, k in enumerate(fields_of('mode'))} | {
            'mu_first_order_psi': abs(parts(y[9])[0]) * mu_half,
            'mu_first_order_f': abs(parts(y[10])[0]) * mu_half,
            'mu_first_order_g': abs(parts(y[11])[0]) * mu_half}
    eps = abs(p['eps'])
    return {'rad_W': parts(y[0])[1], 'eps_rad_psi': eps * parts(y[5])[1], 'rad_w': parts(y[9])[1],
            'rad_P': parts(y[2])[1], 'eps_rad_f': eps * parts(y[6])[1]}


ATTR = {'mode': ['rad_W', 'rad_H', 'rad_Phi', 'rad_T', 'rad_exp(-W)', 'rad_psi', 'rad_f', 'rad_g',
                 'mu_first_order_psi', 'mu_first_order_f', 'mu_first_order_g'],
        'signed': ['rad_W', 'eps_rad_psi', 'rad_w', 'rad_P', 'eps_rad_f']}


class Budget:
    def __init__(self, P):
        self.P = P
        self.name = P['name']
        self.fields = fields_of(self.name)
        self.engine = mode_flow if self.name == 'mode' else prepared_flow
        self.cols = {(f, c): array('d') for f in self.fields for c in COLUMNS}
        self.attr_names = ATTR['mode' if self.name == 'mode' else 'signed']
        self.attr = {k: array('d') for k in self.attr_names}
        self.best = {f: None for f in self.fields}
        self.best16 = {f: None for f in self.fields}
        self.closure_violations = 0
        self.closure_worst = Fraction(0)
        self.refined_above_accepted = 0
        self.tol = Fraction(1, 2 ** (-CONFIG['closure_relative_tolerance_log2']))

    def decompose(self, i, t, h, state, cell, after, before):
        P, p, name = self.P, state['p'], self.name
        prof, Dlo, Dhi, m = P['profile'], P['Dlo'], P['Dhi'], P['subcells']
        point = ir.physical_values(validated.range_on_cell(cell, fmpq(0), fmpq(0)), p, name)
        pointD = prof.enclose(t * prof.D / Dhi, min(prof.D, t * prof.D / Dlo))
        att = attribution(name, state['y'], p)
        for k in self.attr_names:
            self.attr[k].append(up_float(fq(att[k])))
        sub = [None] * m
        for j, f in enumerate(self.fields):
            E = ir.maximum_abs(after[j] - before[j])
            ma, ra = parts(after[j])
            mb, rb = parts(before[j])
            r0 = parts(point[j])[1]
            rd = parts(pointD[j])[1]
            dm = abs(ma - mb)
            # Arb radii are 30-bit upward-rounded magnitudes: the identity E = |dm| + ra + rb holds up to a
            # relative 2^-28 on the radius part plus midpoint rounding at the working precision.
            total = fq(dm + ra + rb)
            slack = Fraction(1, 2 ** 28) * fq(ra + rb) + self.tol * (1 + fq(abs(ma)) + fq(abs(mb)))
            if not (total - slack <= fq(E) <= total + slack):
                self.closure_violations += 1
            self.closure_worst = max(self.closure_worst, abs(fq(E) - total))
            comp = {'E1': E, 'center': dm, 'state': r0, 'source_step': ra - r0, 'event': rd, 'native_step': rb - rd}
            E16 = None
            for k in range(m):
                if sub[k] is None:
                    lo, hi = h * k / m, h * (k + 1) / m
                    a = ir.physical_values(validated.range_on_cell(cell, lo, hi), p, name)
                    b = prof.enclose((t + lo) * prof.D / Dhi, min(prof.D, (t + hi) * prof.D / Dlo))
                    sub[k] = (a, b, lo)
                a, b, _ = sub[k]
                Ek = ir.maximum_abs(a[j] - b[j])
                if E16 is None or Ek > E16[0]:
                    E16 = (Ek, k)
            comp['E16'] = E16[0]
            if E16[0] > E:
                self.refined_above_accepted += 1
            for c in COLUMNS:
                self.cols[(f, c)].append(up_float(fq(comp[c])))
            if self.best[f] is None or E > self.best[f]['E1']:
                self.best[f] = {'cell': i, 'E1': E, 'components': {c: comp[c] for c in COLUMNS if c != 'E1'},
                                'attribution': {kk: att[kk] for kk in self.attr_names}}
            if self.best16[f] is None or E16[0] > self.best16[f]['E16']:
                k = E16[1]
                a, b, lo = sub[k]
                s0 = t + lo
                pa = ir.physical_values(validated.range_on_cell(cell, lo, lo), p, name)
                pd = prof.enclose(s0 * prof.D / Dhi, min(prof.D, s0 * prof.D / Dlo))
                sa, sra = parts(a[j])
                sb, srb = parts(b[j])
                r0s, rds = parts(pa[j])[1], parts(pd[j])[1]
                self.best16[f] = {'cell': i, 'subcell': k, 'E16': E16[0],
                                  'components': {'center': abs(sa - sb), 'state': r0s, 'source_step': sra - r0s,
                                                 'event': rds, 'native_step': srb - rds}}

    def run_block(self, state, record_cells=True):
        """Inherited cell update for one 256-cell block (identity_run.integrate body) plus the budget."""
        P = self.P
        prof, Dlo, Dhi, step = P['profile'], P['Dlo'], P['Dhi'], P['step']
        while state['cell_index'] * step < Dhi:
            i = state['cell_index']
            t = i * step
            h = min(step, Dhi - t)
            y, cell = validated.step(state['y'], h, state['p'], self.engine)
            ranged = validated.range_on_cell(cell, fmpq(0), h)
            before = prof.enclose(t * prof.D / Dhi, min(prof.D, (t + h) * prof.D / Dlo))
            after = ir.physical_values(ranged, state['p'], self.name)
            state['max_errors'] = [max(a, ir.maximum_abs(b - c)) for a, b, c in zip(state['max_errors'], after, before)]
            state['domain_maxima'] = [max(a, ir.maximum_abs(b)) for a, b in zip(state['domain_maxima'], ranged)]
            if self.name == 'mode' and t + h >= Dlo:
                lo = max(fmpq(0), Dlo - t)
                hi = min(h, Dhi - t)
                ey = validated.range_on_cell(cell, lo, hi)
                v = mode_flow.determinant_mu(ey, state['p'])
                state['event_derivative'] = v if state['event_derivative'] is None else hull(state['event_derivative'], v)
                state['event_cover'].append({'cell': i, 'left': t + lo, 'right': t + hi, 'F_mu': v})
            if record_cells:
                self.decompose(i, t, h, state, cell, after, before)
            state['y'] = y
            state['cell_index'] += 1
            state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
            if state['cell_index'] % CONFIG['checkpoint_cells'] == 0 or t + h == Dhi:
                return state
        return state


def same_as_checkpoint(state, body):
    packed = records.pack({k: state[k] for k in COMPARED})
    return all(packed[k] == body['state'][k] for k in COMPARED), [k for k in COMPARED if packed[k] != body['state'][k]]


def checkpoints(folder, task):
    rows = []
    for path in sorted(Path(folder).glob(f'{task:02d}-*.json')):
        body = read(path)
        digest = path.name.split('-')[-1][:-5]
        if records.fingerprint(body) != digest:
            raise RuntimeError('Checkpoint digest mismatch ' + path.name)
        rows.append((int(path.name.split('-')[1]), path, body))
    return rows


def execute(P):
    """Replay all blocks; returns the summary. P supplies data sources (real or fixture)."""
    started, cpu0 = time.monotonic(), time.process_time()
    b = Budget(P)
    cks = checkpoints(P['checkpoint_dir'], P['task_index'])
    if [c[0] for c in cks] != P['expected_checkpoint_cells']:
        raise RuntimeError('Unexpected checkpoint cell indices')
    block_checks = []
    start = P['fresh_state']()
    for n, (cell_index, path, body) in enumerate(cks):
        if body['guard'] != P['guard']:
            raise RuntimeError('Checkpoint guard mismatch')
        state = start
        if state['cell_index'] != (0 if n == 0 else cks[n - 1][0]):
            raise RuntimeError('Block start mismatch')
        state = b.run_block(state)
        ok, bad = same_as_checkpoint(state, body)
        block_checks.append({'block': n, 'end_cell': cell_index, 'checkpoint': path.name, 'bitwise_equal': ok, 'differs': bad})
        start = records.unpack(body['state'])
        P['progress'](n + 1, len(cks))
    final = records.unpack(cks[-1][2]['state'])
    summary = {'flow': P['name'], 'fields': b.fields, 'cells': len(b.cols[(b.fields[0], 'E1')]),
               'blocks': len(block_checks), 'all_blocks_bitwise_equal': all(c['bitwise_equal'] for c in block_checks),
               'block_checks': block_checks, 'closure_violations': b.closure_violations,
               'closure_worst_absolute': show(b.closure_worst), 'refined_above_accepted_cells': b.refined_above_accepted,
               'accepted_max_errors_exact': [str(v) for v in final['max_errors']], 'fieldsummary': {}}
    for j, f in enumerate(b.fields):
        best, best16 = b.best[f], b.best16[f]
        E = best['E1']
        comp = best['components']
        shares = {'CENTER_DISCREPANCY': comp['center'], 'STATE_RADIUS': comp['state'],
                  'COMPARISON_STEP': comp['source_step'] + comp['native_step'], 'EVENT_WIDTH': comp['event']}
        dominant = max(shares, key=lambda k: shares[k])
        comp16 = best16['components']
        shares16 = {'CENTER_DISCREPANCY': comp16['center'], 'STATE_RADIUS': comp16['state'],
                    'COMPARISON_STEP': comp16['source_step'] + comp16['native_step'], 'EVENT_WIDTH': comp16['event']}
        sup = {c: max(b.cols[(f, c)]) for c in COLUMNS}
        summary['fieldsummary'][f] = {
            'accepted_bound_exact': str(E), 'accepted_bound': show(fq(E)),
            'accepted_equals_inherited_running_max': E == final['max_errors'][j],
            'argmax_cell': best['cell'], 'argmax_s': str(Fraction(best['cell'], 8192)),
            'argmax_components_exact': {k: str(v) for k, v in comp.items()},
            'argmax_shares': {k: ratio(v, E) for k, v in shares.items()},
            'dominant_width': dominant,
            'argmax_attribution': {k: show(fq(v)) for k, v in best['attribution'].items()},
            'refined_bound_exact': str(best16['E16']), 'refined_bound': show(fq(best16['E16'])),
            'refined_argmax_cell': best16['cell'], 'refined_argmax_subcell': best16['subcell'],
            'refined_components': {k: show(fq(v)) for k, v in comp16.items()},
            'refined_shares': {k: ratio(v, best16['E16']) for k, v in shares16.items()},
            'refined_dominant_width': max(shares16, key=lambda k: shares16[k]),
            'refined_over_accepted': ratio(best16['E16'], E),
            'component_sup_over_cells_upper': sup}
    summary['attribution_sup_over_cells_upper'] = {k: max(b.attr[k]) for k in b.attr_names}
    payload = array('d')
    names = []
    for f in b.fields:
        for c in COLUMNS:
            payload.extend(b.cols[(f, c)])
            names.append(f + ':' + c)
    for k in b.attr_names:
        payload.extend(b.attr[k])
        names.append('attr:' + k)
    summary['arrays'] = {'columns': names, 'rows_per_column': summary['cells'], 'dtype': 'float64 little-endian, upward-rounded'}
    summary['elapsed_seconds'] = time.monotonic() - started
    summary['cpu_seconds'] = time.process_time() - cpu0
    return summary, payload


def real_context(name, out):
    task = CONFIG['task_index'][name]
    ident = PACKET['identity']
    conn = read(PACKET['connected'] / 'BINDINGS.json')['config']
    Dlo, Dhi = map(ir.exact, conn['D'])
    if [str(Dlo), str(Dhi)] != CONFIG['D_interval']:
        raise RuntimeError('D interval differs from the frozen value')
    ir.capacity = lambda: {'replaced_for_replay': True}
    profile = ir.SavedProfile(None if name == 'mode' else CONFIG['case_of_flow'][name])
    cells = CONFIG['cells']
    expected = [256 * k for k in range(1, cells // 256 + 1)] + ([cells] if cells % 256 else [])

    def progress(done, total):
        atomic(out / 'status.json', {'flow': name, 'state': 'RUNNING', 'blocks_done': done, 'blocks_total': total,
                                     'utc': now(), 'pid': os.getpid(), 'compute_slot': os.environ.get('COMPUTE_SLOT')})
    return {'name': name, 'task_index': task, 'profile': profile, 'Dlo': Dlo, 'Dhi': Dhi, 'step': ir.exact(CONFIG['step']),
            'subcells': CONFIG['subcells'], 'checkpoint_dir': ident / 'output' / name / 'checkpoints',
            'expected_checkpoint_cells': expected, 'guard': CONFIG['identity_guard'],
            'fresh_state': lambda: ir.fresh_state(name, task), 'progress': progress}


def run(name):
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    out = OUT / name
    if (out / 'SUMMARY.json').exists() or (out / 'FAILURE.json').exists():
        raise RuntimeError('Flow output already terminal or failed closed; no restart')
    guard_sha, _ = freeze_guard()
    cap = capacity()
    if cap['available_bytes'] < CONFIG['minimum_available_bytes']:
        raise RuntimeError('Insufficient available memory')
    P = real_context(name, out)

    def alarm(*args):
        raise TimeoutError('Frozen job wall budget')
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(CONFIG['job_wall_seconds'])
    try:
        summary, payload = execute(P)
        signal.alarm(0)
        result = read(PACKET['identity'] / 'output' / name / 'RESULT.json')
        spatial = read(PACKET['identity'] / 'SPATIAL_ENCLOSURES.json')
        task = next(x for x in spatial['tasks'] if x['task'] == name)
        summary['inherited_result_max_error_bounds_exact'] = result['max_error_bounds_exact']
        summary['replayed_bounds_equal_inherited_result'] = summary['accepted_max_errors_exact'] == result['max_error_bounds_exact']
        summary['replayed_bounds_equal_spatial_enclosures'] = summary['accepted_max_errors_exact'] == task['max_error_bounds_exact']
        summary.update({'guard': guard_sha, 'utc': now(), 'address_space': limits, 'capacity': cap,
                        'compute_slot': os.environ.get('COMPUTE_SLOT'), 'pid': os.getpid(),
                        'new_flows': 0, 'intervals_changed': False, 'time_evolution': False})
        atomic_bytes(out / 'CELLS.f64', payload.tobytes())
        summary['arrays']['sha256'] = sha(out / 'CELLS.f64')
        atomic(out / 'SUMMARY.json', summary, True)
        atomic(out / 'status.json', {'flow': name, 'state': 'COMPLETE', 'utc': now(), 'pid': os.getpid(),
                                     'compute_slot': os.environ.get('COMPUTE_SLOT')})
        print(json.dumps({'flow': name, 'bitwise': summary['all_blocks_bitwise_equal'],
                          'equal_inherited': summary['replayed_bounds_equal_inherited_result'],
                          'seconds': round(summary['elapsed_seconds'], 1)}), flush=True)
    except Exception as error:
        atomic(out / 'FAILURE.json', {'status': 'FAILED_CLOSED', 'type': type(error).__name__, 'error': str(error),
                                      'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[1] != 'run' or sys.argv[2] not in CONFIG['flows']:
        raise SystemExit('usage: budget.py run <mode|positive|negative>')
    run(sys.argv[2])
