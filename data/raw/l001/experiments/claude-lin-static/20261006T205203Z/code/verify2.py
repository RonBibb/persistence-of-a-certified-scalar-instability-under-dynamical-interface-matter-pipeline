"""Independent verifier for the enclosure-width budget (run 20261006T205203Z).

Does not import budget.py. Uses the byte-identical inherited validated engine (disclosed as
shared) with its own block driver. For sampled blocks and for the block of every field's
argmax cell it recomputes every per-cell component exactly and requires the producer's
binary64 column to equal the upward rounding of that exact value; it reproduces the
checkpoints, the inherited accepted bounds and the dominant-width decisions.
    python -B <run>/code/verify2.py run
"""
import json
import math
import os
import subprocess
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
from common2 import (RUN, OUT, VER, PACKET, CONFIG, now, sha, read, atomic, fq, up_float, show,  # noqa: E402
                     check_environment, limit_address_space)

COLS = ('E1', 'center', 'state', 'source_step', 'event', 'native_step', 'E16')
KEYS = ('max_errors', 'domain_maxima', 'event_cover', 'event_derivative', 'max_picard', 'cell_index', 'task_index', 'name', 'p', 'y')


def mr(x):
    lo, hi = bounds(x)
    return (lo + hi) / 2, (hi - lo) / 2


def field_names(flow):
    return ['W', 'H', 'Phi', 'T', 'exp(-W)', 'psi', 'f', 'g'] if flow == 'mode' else ['A', 'ell', 'Phi']


def cell_components(flow, cell, t, h, p, prof, Dlo, Dhi, m):
    """Exact components of every compared field for one validated cell (own implementation)."""
    D = prof.D
    full = ir.physical_values(validated.range_on_cell(cell, fmpq(0), h), p, flow)
    nat = prof.enclose(t * D / Dhi, min(D, (t + h) * D / Dlo))
    start = ir.physical_values(validated.range_on_cell(cell, fmpq(0), fmpq(0)), p, flow)
    natD = prof.enclose(t * D / Dhi, min(D, t * D / Dlo))
    subs = []
    for k in range(m):
        a0, a1 = h * k / m, h * (k + 1) / m
        subs.append((ir.physical_values(validated.range_on_cell(cell, a0, a1), p, flow),
                     prof.enclose((t + a0) * D / Dhi, min(D, (t + a1) * D / Dlo))))
    out = []
    for j in range(len(full)):
        E = ir.maximum_abs(full[j] - nat[j])
        (ma, ra), (mb, rb) = mr(full[j]), mr(nat[j])
        r0, rd = mr(start[j])[1], mr(natD[j])[1]
        E16 = max(ir.maximum_abs(a[j] - b[j]) for a, b in subs)
        out.append({'E1': E, 'center': abs(ma - mb), 'state': r0, 'source_step': ra - r0, 'event': rd,
                    'native_step': rb - rd, 'E16': E16})
    return out


def own_block(flow, state, prof, Dlo, Dhi, step, m, want):
    """Inherited cell update (identity_run.integrate body), independently driven; returns end state and components."""
    engine = mode_flow if flow == 'mode' else prepared_flow
    comps = {}
    while state['cell_index'] * step < Dhi:
        i = state['cell_index']
        t = i * step
        h = min(step, Dhi - t)
        y, cell = validated.step(state['y'], h, state['p'], engine)
        ranged = validated.range_on_cell(cell, fmpq(0), h)
        before = prof.enclose(t * prof.D / Dhi, min(prof.D, (t + h) * prof.D / Dlo))
        after = ir.physical_values(ranged, state['p'], flow)
        state['max_errors'] = [max(a, ir.maximum_abs(b - c)) for a, b, c in zip(state['max_errors'], after, before)]
        state['domain_maxima'] = [max(a, ir.maximum_abs(b)) for a, b in zip(state['domain_maxima'], ranged)]
        if flow == 'mode' and t + h >= Dlo:
            lo, hi = max(fmpq(0), Dlo - t), min(h, Dhi - t)
            v = mode_flow.determinant_mu(validated.range_on_cell(cell, lo, hi), state['p'])
            state['event_derivative'] = v if state['event_derivative'] is None else hull(state['event_derivative'], v)
            state['event_cover'].append({'cell': i, 'left': t + lo, 'right': t + hi, 'F_mu': v})
        if want(i):
            comps[i] = cell_components(flow, cell, t, h, state['p'], prof, Dlo, Dhi, m)
        state['y'] = y
        state['cell_index'] += 1
        state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
        if state['cell_index'] % 256 == 0 or t + h == Dhi:
            break
    return state, comps


def gate(rows, gid, ok, value=None):
    rows.append({'id': gid, 'pass': bool(ok), 'value': value})


def dominant(c):
    shares = {'CENTER_DISCREPANCY': c['center'], 'STATE_RADIUS': c['state'],
              'COMPARISON_STEP': c['source_step'] + c['native_step'], 'EVENT_WIDTH': c['event']}
    return max(shares, key=lambda k: shares[k])


def verify_flow(C, flow, g):
    out = Path(C['out']) / flow
    summ = read(out / 'SUMMARY.json')
    if summ['arrays']['sha256'] != sha(out / 'CELLS.f64'):
        raise RuntimeError('Cell array changed after publication')
    data = array('d')
    data.frombytes((out / 'CELLS.f64').read_bytes())
    n = summ['cells']
    cols = {name: data[k * n:(k + 1) * n] for k, name in enumerate(summ['arrays']['columns'])}
    fields = field_names(flow)
    gate(g, f'R1.{flow}.all_blocks_bitwise_equal', summ['all_blocks_bitwise_equal'], summ['blocks'])
    inherited = read(Path(C['identity']) / 'output' / flow / 'RESULT.json')['max_error_bounds_exact'] if C['identity'] else C['inherited'][flow]
    gate(g, f'R2.{flow}.accepted_bounds_equal_inherited', summ['accepted_max_errors_exact'] == inherited)
    gate(g, f'B1.{flow}.closure', summ['closure_violations'] == 0, summ['closure_worst_absolute'])
    prof = C['profile'](flow)
    Dlo, Dhi, step, m = C['Dlo'], C['Dhi'], C['step'], C['subcells']
    cks = sorted(Path(C['checkpoints'](flow)).glob(f"{C['task'][flow]:02d}-*.json"))
    ends = [int(p.name.split('-')[1]) for p in cks]
    argmax = {f: summ['fieldsummary'][f]['argmax_cell'] for f in fields}
    blocks = sorted(set(C['sample_blocks']) | {next(b for b, e in enumerate(ends) if c < e) for c in argmax.values()})
    checked_cells = 0
    float_mismatch = 0
    exact_argmax = {}
    for b in blocks:
        if b == 0:
            state = C['fresh'](flow)
        else:
            body = read(cks[b - 1])
            if records.fingerprint(body) != cks[b - 1].name.split('-')[-1][:-5]:
                raise RuntimeError('Checkpoint digest mismatch')
            state = records.unpack(body['state'])
        first = state['cell_index']
        state, comps = own_block(flow, state, prof, Dlo, Dhi, step, m, lambda i: True)
        end = read(cks[b])
        packed = records.pack({k: state[k] for k in KEYS})
        gate(g, f'VR.{flow}.block{b}.bitwise', all(packed[k] == end['state'][k] for k in KEYS))
        for i, rows in comps.items():
            for j, f in enumerate(fields):
                for c in COLS:
                    checked_cells += 1
                    if cols[f + ':' + c][i] != up_float(fq(rows[j][c])):
                        float_mismatch += 1
                if argmax[f] == i:
                    exact_argmax[f] = rows[j]
    gate(g, f'VF.{flow}.producer_columns_equal_upward_rounding_of_exact', float_mismatch == 0,
         {'values_checked': checked_cells, 'mismatches': float_mismatch, 'blocks': blocks})
    for j, f in enumerate(fields):
        fs = summ['fieldsummary'][f]
        e = exact_argmax.get(f)
        ok = e is not None and str(e['E1']) == fs['accepted_bound_exact'] and str(e['E1']) == inherited[j] \
            and all(str(e[k]) == fs['argmax_components_exact'][k] for k in fs['argmax_components_exact'])
        gate(g, f'VA.{flow}.{f}.argmax_cell_exact', ok, fs['argmax_cell'])
        colmax = max(cols[f + ':E1'])
        gate(g, f'VM.{flow}.{f}.column_max_is_accepted', colmax == up_float(Fraction(inherited[j])), colmax)
        dom = dominant(e) if e is not None else None
        gate(g, f'VD.{flow}.{f}.dominant_width', dom == fs['dominant_width'], dom)
    return summ


def classify(summaries):
    signed = [summaries[x]['fieldsummary']['A']['dominant_width'] for x in ('positive', 'negative')]
    label = signed[0] if signed[0] == signed[1] else 'MIXED'
    return 'ENCLOSURE_BUDGET_RESOLVED__A_DOMINATED_BY_' + label


def verify(C):
    t0 = time.monotonic()
    ctx.prec = 768
    ctx.threads = 1
    g = []
    summaries = {}
    for flow in C['flows']:
        summaries[flow] = verify_flow(C, flow, g)
    ok = all(r['pass'] for r in g)
    cls = classify(summaries) if ok else 'UNRESOLVED_VERIFICATION'
    produced = read(Path(C['out']) / 'PRODUCER_RESULT.json')
    gate(g, 'VC.classification_agrees', produced['classification_provisional'] == cls, produced['classification_provisional'])
    if not C['fixture']:
        ps = subprocess.run(['ps', '-eo', 'pid,args'], capture_output=True, text=True, check=True).stdout.splitlines()
        live = [line.strip() for line in ps if 'code/budget.py' in line and RUN.name in line]
        gate(g, 'VP.no_live_producer', not live, live)
    resolved = all(r['pass'] for r in g)
    return {'classification': cls if resolved else 'UNRESOLVED_VERIFICATION', 'resolved': resolved,
            'checks_passed': sum(r['pass'] for r in g), 'checks_total': len(g), 'checks': g,
            'failed': [r['id'] for r in g if not r['pass']], 'utc': now(), 'seconds': time.monotonic() - t0,
            'shared_inherited_engine_disclosed': True, 'imports_budget_py': False}


def real_context():
    conn = read(PACKET['connected'] / 'BINDINGS.json')['config']
    Dlo, Dhi = map(ir.exact, conn['D'])
    ir.capacity = lambda: {'replaced_for_replay': True}
    profiles = {}

    def profile(flow):
        if flow not in profiles:
            profiles[flow] = ir.SavedProfile(None if flow == 'mode' else CONFIG['case_of_flow'][flow])
        return profiles[flow]
    return {'flows': CONFIG['flows'], 'out': OUT, 'identity': PACKET['identity'], 'Dlo': Dlo, 'Dhi': Dhi,
            'step': ir.exact(CONFIG['step']), 'subcells': CONFIG['subcells'], 'profile': profile,
            'checkpoints': lambda flow: PACKET['identity'] / 'output' / flow / 'checkpoints', 'task': CONFIG['task_index'],
            'fresh': lambda flow: ir.fresh_state(flow, CONFIG['task_index'][flow]),
            'sample_blocks': CONFIG['verifier_sample_blocks'], 'fixture': False}


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'run':
        raise SystemExit('usage: verify2.py run')
    check_environment()
    limits = limit_address_space()
    if (VER / 'VERIFICATION.json').exists():
        raise RuntimeError('Verification already terminal')
    try:
        frozen = read(RUN / 'FREEZE.json')
        for name, digest in frozen['inputs'].items():
            if sha(name) != digest:
                raise RuntimeError('Changed input ' + name)
        for name, digest in frozen['sources'].items():
            if sha(RUN / name) != digest:
                raise RuntimeError('Changed source ' + name)
        result = verify(real_context())
        result.update({'guard': sha(RUN / 'FREEZE.json'), 'address_space': limits, 'pid': os.getpid(),
                       'compute_slot': os.environ.get('COMPUTE_SLOT'), 'verifier_source_sha256': sha(Path(__file__).resolve())})
        atomic(VER / 'VERIFICATION.json', result, True)
        print(json.dumps({'classification': result['classification'], 'checks': [result['checks_passed'], result['checks_total']],
                          'failed': result['failed']}), flush=True)
    except Exception as error:
        atomic(VER / f'FAILURE_{int(time.time())}.json', {'type': type(error).__name__, 'error': str(error),
                                                          'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise
