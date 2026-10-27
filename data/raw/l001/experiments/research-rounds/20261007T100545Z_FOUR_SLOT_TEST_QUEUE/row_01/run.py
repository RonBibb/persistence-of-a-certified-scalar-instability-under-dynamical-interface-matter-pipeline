"""R01-P1 only: one certified mu contraction and bounded preparation diagnostics.

Reuses frozen interval engines read-only. All output stays in this row. No
root-box iteration, new material bounds, time evolution, or automatic successor.
"""
import argparse
import copy
import fcntl
import json
import math
import os
import platform
import signal
import subprocess
import sys
import time
import traceback
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ROUND = ROOT.parents[1]
RESEARCH = Path('/media/psf/Home/Research')
BASE = RESEARCH / 'ClaudeCode/lines/02_lin_static/runs/20261007T030034Z'
CODE = BASE / 'code'
sys.path[:0] = [str(CODE), str(CODE / 'inherited')]
import reprep as rp
import common4 as c4
import records as rec
import preparation
import source_flow
import nonlinear
import validated
from series import bounds, interval
from flint import arb, ctx

CONTRACT = rec.read(ROOT / 'CONTRACT.json')
OUT = ROOT / 'output'
PRE = ROOT / 'preflight'
STATUS = ROUND / 'status/row_01.json'
FINITE = c4.PACKET['finite']
IDENTITY = c4.PACKET['identity']
CENTRAL = FINITE.parent / 'lin-central-validated-mode-r1-20261005T172800Z'
START_CP = FINITE / 'output/source/checkpoints/00-016128-0d2f437026fed619b8e7ebdcd5c56b5920081e053fd545cec65de3a90478e307.json'
END_CP = FINITE / 'output/source/checkpoints/00-016365-5c47139435f52919162b6ec5976736f16ca80c9db797cf9fc8935a9976898667.json'
D1, D2 = map(rp.f2q, CONTRACT['D_prime'])
K1, K2 = map(rp.f2q, c4.CONFIG['D_K'])
H = rp.f2q(CONTRACT['step'])
TOTAL = CONTRACT['maximum_cells_per_flow']
EPS = {w: rp.f2q(e) for w, e in CONTRACT['epsilon'].items()}
GUARD = None
COMPUTE_START = None
PRIOR_SECONDS = 0.0
CURRENT = None


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def qends(ball):
    return [str(x) for x in bounds(ball)]


def fraction_radius(endpoints):
    lo, hi = map(Q, endpoints)
    require(lo <= hi, 'Reversed saved enclosure')
    return (hi - lo) / 2


def metrics(prep):
    return {'Q_C7': sum((rp.rad(v) * Q(str(D2))**n for n, v in enumerate(prep['c7'])), Q(0)),
            'rad_W0': rp.rad(prep['W'][0]), 'rad_W1': rp.rad(prep['W'][1])}


def endpoint_metrics(e):
    return {'Q_C7': sum((fraction_radius(v) * Q(str(D2))**n for n, v in enumerate(e['c7'])), Q(0)),
            'rad_W0': fraction_radius(e['W'][0]), 'rad_W1': fraction_radius(e['W'][1])}


def prep_endpoints(p):
    return {k: [qends(v) for v in p[k]] for k in ('c7', 'W')}


def fractions(values):
    return {k: str(v) for k, v in values.items()}


def identity():
    return {'pid': os.getpid(), 'hostname': platform.node(),
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'proc_start_ticks': Path('/proc/self/stat').read_text().split()[21],
            'executable': str(Path(sys.executable).resolve()), 'source_sha256': rec.sha(__file__)}


def status(phase, running=False, outcome=None, **extra):
    data = {'round_id': CONTRACT['round_id'], 'row': 1, 'proposal_id': 'R01-P1',
            'phase': phase, 'created_utc': '2026-10-07T10:17:00Z', 'updated_utc': rec.now(),
            'run_path': str(ROOT), 'owned_pid': os.getpid(), 'runtime_identity': identity(),
            'experiment_running': running, 'terminal_outcome': outcome, 'guard': GUARD}
    data.update(extra)
    rec.atomic(STATUS, data)


def parent_entry(parent, relative):
    manifest = rec.read(parent / 'MANIFEST.json')
    rows = manifest.get('entries')
    if rows is None:
        rows = [v | {'path': k} for k, v in manifest['files'].items()]
    matches = [r for r in rows if r['path'] == relative]
    require(len(matches) == 1, 'Missing manifest entry: ' + str(parent / relative))
    require(rec.sha(parent / relative) == matches[0]['sha256'], 'Parent digest mismatch: ' + relative)


def bindings():
    authorization = rec.read(ROUND / 'AUTHORIZATION.json')
    selected = next(r for r in authorization['selected'] if r['row'] == 1)
    require(selected['gate_authorization'] == 'USER_APPROVED_FOR_THIS_SINGLE_TEST', 'Authorization missing')
    require(selected['proposal_id'] == 'R01-P1', 'Wrong authorized proposal')
    require(rec.sha(ROUND / 'approved/row_01.json') == selected['source_sha256'], 'Proposal changed')
    require(selected['approved_gate_ids'] == CONTRACT['approved_gates'], 'Gate mismatch')
    old = rec.read(BASE / 'FREEZE.json')
    paths = [ROUND / 'AUTHORIZATION.json', ROUND / 'approved/row_01.json',
             RESEARCH / 'ClaudeCode/config/linux.json', BASE / 'FREEZE.json', BASE / 'MANIFEST.json',
             BASE / 'verification/VERIFICATION.json', BASE / 'outputs/PRODUCER_RESULT.json',
             FINITE / 'BINDINGS.json', FINITE / 'MANIFEST.json', FINITE / 'output/source/RESULT.json',
             START_CP, END_CP, IDENTITY / 'BINDINGS.json', IDENTITY / 'MANIFEST.json',
             IDENTITY / 'output/mode/RESULT.json', CENTRAL / 'BINDINGS.json', CENTRAL / 'MANIFEST.json',
             CENTRAL / 'RESULT.json', CENTRAL / 'output/RESULT.json',
             c4.RUN3 / 'outputs/PRODUCER_RESULT.json', c4.RUN3 / 'verification/VERIFICATION.json']
    for p in sorted(CODE.rglob('*.py')):
        require(rec.sha(p) == old['sources'][str(p.relative_to(BASE))], 'Frozen engine changed: ' + str(p))
        paths.append(p)
    for w in EPS:
        p = BASE / f'outputs/phase-{w}-center/PHASE.json'
        parent_entry(BASE, str(p.relative_to(BASE)))
        paths.append(p)
    for parent, rels in ((FINITE, ['BINDINGS.json', 'output/source/RESULT.json', str(START_CP.relative_to(FINITE)), str(END_CP.relative_to(FINITE))]),
                         (IDENTITY, ['BINDINGS.json', 'output/mode/RESULT.json']),
                         (CENTRAL, ['BINDINGS.json', 'RESULT.json', 'output/RESULT.json']),
                         (BASE, ['verification/VERIFICATION.json', 'outputs/PRODUCER_RESULT.json'])):
        for rel in rels:
            parent_entry(parent, rel)
    finite = rec.read(FINITE / 'BINDINGS.json')
    central = rec.read(CENTRAL / 'BINDINGS.json')
    derivative = rec.read(IDENTITY / 'BINDINGS.json')
    require(finite['model_exact'] == central['model_exact'] == derivative['model_exact'], 'Action mismatch')
    require(finite['config']['root'] == central['config']['A'], 'Background bracket mismatch')
    require(finite['config']['mu'] == central['config']['mu'] == CONTRACT['mu_interval'], 'Mu bracket mismatch')
    require(finite['config']['D'] == central['config']['D'] == c4.CONFIG['D_K'], 'Old event bracket mismatch')
    require(rec.read(CENTRAL / 'RESULT.json')['independently_accepted'], 'Inherited existence not accepted')
    require(rec.read(CENTRAL / 'output/RESULT.json')['endpoint_certificate'], 'No inherited endpoint signs')
    mode = rec.read(IDENTITY / 'output/mode/RESULT.json')
    require(mode['passed'] and Q(mode['F_mu']['exact'][1]) < 0, 'Uniform derivative does not exclude zero')
    require(rec.read(BASE / 'verification/VERIFICATION.json')['resolved'], 'Unresolved baseline')
    require(rec.read(c4.RUN3 / 'outputs/PRODUCER_RESULT.json')['narrowed_interval'] == CONTRACT['D_prime'], 'Unbound D prime')
    require(rec.read(c4.RUN3 / 'verification/VERIFICATION.json')['resolved'], 'Unresolved D prime certificate')
    require(K1 <= D1 < D2 <= K2 and (TOTAL - 1)*H <= D1 < D2 <= TOTAL*H, 'D prime containment')
    data = {'utc': rec.now(), 'contract': CONTRACT,
            'sources': {str(ROOT / n): rec.sha(ROOT / n) for n in ('run.py', 'CONTRACT.json')},
            'inputs': {str(p): rec.sha(p) for p in paths}, 'runtime': c4.runtime_fingerprint(),
            'capacity': c4.capacity(), 'inherited_unique_root': True,
            'non_mu_inputs_unchanged': True}
    require(data['capacity']['available_bytes'] >= 4*1024**3, 'Insufficient memory')
    rec.atomic(ROOT / 'BINDINGS.json', data, True)
    return rec.sha(ROOT / 'BINDINGS.json')


def guard_check():
    b = rec.read(ROOT / 'BINDINGS.json')
    require(b['contract'] == CONTRACT, 'Changed contract')
    for path, digest in (b['sources'] | b['inputs']).items():
        require(rec.sha(path) == digest, 'Changed binding: ' + path)
    require(b['runtime'] == c4.runtime_fingerprint(), 'Changed runtime')
    f = rec.read(ROOT / 'FREEZE.json')
    require(f['bindings_sha256'] == rec.sha(ROOT / 'BINDINGS.json'), 'Changed binding file')
    require(f['preflight_sha256'] == rec.sha(PRE / 'RESULT.json'), 'Changed preflight')
    require(rec.read(PRE / 'RESULT.json')['passed'], 'Preflight failed')
    return rec.sha(ROOT / 'FREEZE.json')


def restart_child(guard):
    st = rec.load(PRE / 'restart', guard)
    rp.finite_cell(st, source_flow, K1, K2, H)
    rec.atomic(PRE / 'restart_child.json', st, True)


def preflight(guard):
    status('PREFLIGHT')
    initial = rec.read(START_CP)
    final = rec.read(END_CP)
    for path, body in ((START_CP, initial), (END_CP, final)):
        require(rec.fingerprint(body) == path.stem.split('-')[-1], 'Checkpoint fingerprint')
        require(body['guard'] == c4.CONFIG['finite_guard'], 'Wrong inherited checkpoint binding')
    st = rec.unpack(initial['state'])
    model = {}
    while st['cell_index'] < TOTAL:
        rp.finite_cell(st, source_flow, K1, K2, H, keep=lambda j, s, cell: model.update(last=(s, cell)))
    packed = rec.pack({k: st[k] for k in rp.SOURCE_KEYS})
    controls = {'source_block_bitwise': all(packed[k] == final['state'][k] for k in rp.SOURCE_KEYS)}
    require(controls['source_block_bitwise'], 'Accepted source block replay differs')
    # One fresh-process restart control, using the same real source checkpoint.
    trial = rec.unpack(initial['state'])
    trial['elapsed_seconds'] = 0.0
    rec.save(PRE / 'restart', trial, guard)
    ptr = rec.read(PRE / 'restart/LATEST.json')
    rec.atomic(PRE / 'restart/checkpoints/partial.uncommitted.json', {'partial': True}, True)
    require(rec.read(PRE / 'restart/LATEST.json') == ptr, 'Partial write changed recovery pointer')
    rejected = False
    try:
        rec.load(PRE / 'restart', guard + '-changed')
    except AssertionError:
        rejected = True
    require(rejected, 'Changed guard accepted')
    subprocess.run([sys.executable, '-B', str(ROOT / 'run.py'), 'restart-control', '--guard', guard], check=True, timeout=60)
    direct = rec.load(PRE / 'restart', guard)
    rp.finite_cell(direct, source_flow, K1, K2, H)
    controls['fresh_process_exact_restart'] = rec.pack(direct) == rec.read(PRE / 'restart_child.json')
    controls['changed_guard_rejected'] = rejected
    controls['partial_does_not_replace_pointer'] = rec.read(PRE / 'restart/LATEST.json') == ptr
    common = rec.unpack(rec.read(FINITE / 'output/source/RESULT.json'))
    y0 = rp.finite_initial(rec.read(FINITE / 'BINDINGS.json'))
    controls['fresh_lower_state_matches'] = rec.pack(y0) == rec.pack(common['y0'])
    s, cell = model['last']
    end = rp.canonical(validated.range_on_cell(cell, D1 - s, D2 - s))
    jets = [common['jets'][0], preparation.wall_jets(end, common['p'], 1)]
    p = dict(common['p']); p['D'] = interval(D1, D2)
    preps = {w: preparation.prepare(e, jets, p) for w, e in EPS.items()}
    for w in EPS:
        old = rec.read(BASE / f'outputs/phase-{w}-center/PHASE.json')
        controls[w + '_jets_reproduced'] = rec.fingerprint(jets) == old['fingerprints']['jets']
        controls[w + '_preparation_reproduced'] = rec.fingerprint(preps[w]) == old['fingerprints']['preparation'][w]
    rec.atomic(PRE / 'BASELINE_PREPARATION.json', {'jets': jets, 'preps': preps,
               'endpoints': {w: prep_endpoints(p) for w, p in preps.items()},
               'metrics': {w: fractions(metrics(p)) for w, p in preps.items()}}, True)
    result = {'utc': rec.now(), 'guard': guard, 'controls': controls, 'passed': all(controls.values()),
              'source_block': [16128, 16365], 'production_outcomes_computed': False}
    rec.atomic(PRE / 'RESULT.json', result, True)
    require(result['passed'], 'Preflight control failed')
    rec.atomic(ROOT / 'FREEZE.json', {'utc': rec.now(), 'bindings_sha256': guard,
               'preflight_sha256': rec.sha(PRE / 'RESULT.json'), 'baseline_sha256': rec.sha(PRE / 'BASELINE_PREPARATION.json')}, True)


def spent():
    return PRIOR_SECONDS + (0.0 if COMPUTE_START is None else time.monotonic() - COMPUTE_START)


def budget():
    if spent() >= CONTRACT['compute_cap_seconds']:
        raise TimeoutError('Approved 45-minute compute cap reached')


def flow(name, state, engine):
    global CURRENT
    CURRENT = name
    out = OUT / name
    if (out / 'RESULT.json').exists():
        saved = rec.unpack(rec.read(out / 'RESULT.json'))
        require(saved['guard'] == GUARD and saved['cells'] == TOTAL, 'Incompatible cached flow')
        return saved
    if (out / 'LATEST.json').exists():
        state = rec.load(out, GUARD)
        require(state['which'] == name, 'Wrong resume flow')
    started = time.monotonic()
    previous = state.get('elapsed_seconds', 0.0)
    status('RUNNING', True, current_flow=name, completed_cells=state['cell_index'], total_cells=TOTAL)
    while state['cell_index'] < TOTAL:
        budget()
        endpoint = None if engine is source_flow else lambda z: rp.map_at(z, state['p'], state['jets'])
        rp.finite_cell(state, engine, D1, D2, H, endpoint=endpoint)
        if state['cell_index'] % CONTRACT['checkpoint_cells'] == 0 or state['cell_index'] == TOTAL:
            state['elapsed_seconds'] = previous + time.monotonic() - started
            state['campaign_compute_seconds'] = spent()
            rec.save(out, state, GUARD)
            status('RUNNING', True, current_flow=name, completed_cells=state['cell_index'], total_cells=TOTAL,
                   compute_elapsed_seconds=spent(), last_checkpoint=rec.read(out / 'LATEST.json'))
            if state['cell_index'] % 4096 == 0 or state['cell_index'] == TOTAL:
                print(json.dumps({'flow': name, 'cell': state['cell_index'], 'flow_seconds': state['elapsed_seconds'],
                                  'compute_seconds': spent(), 'utc': rec.now()}), flush=True)
    require(state['cover'] == [[str(D1), str(D2)]], 'Incomplete event coverage')
    result = {'guard': GUARD, 'flow': name, 'cells': state['cell_index'], 'max_picard': state['max_picard'],
              'cover': state['cover'], 'end': state['end'], 'map': state.get('map'), 'p': state['p'],
              'elapsed_seconds': state['elapsed_seconds'], 'compute_seconds': spent(),
              'checkpoint': rec.read(out / 'LATEST.json'), 'utc': rec.now()}
    rec.atomic(out / 'RESULT.json', result, True)
    return rec.unpack(rec.read(out / 'RESULT.json'))


def source_initial(mu, name):
    binding = copy.deepcopy(rec.read(FINITE / 'BINDINGS.json'))
    binding['config']['mu'] = list(map(str, mu))
    old = rec.unpack(rec.read(FINITE / 'output/source/RESULT.json'))
    p = dict(old['p'])
    p['mu'] = interval(*map(rp.f2q, mu))
    p['D'] = interval(D1, D2)
    y0 = rp.finite_initial(binding)
    require(all(rec.pack(p[k]) == rec.pack(old['p'][k]) for k in old['p'] if k not in ('mu', 'D')), 'Non-mu source input changed')
    require(bounds(y0[5]) == (rp.f2q(1), rp.f2q(1)), 'Normalization changed')
    st = {'task_index': CONTRACT['production_order'].index(name), 'cell_index': 0, 'elapsed_seconds': 0.0,
          'which': name, 'p': p, 'y': y0, 'max_picard': 0, 'cover': [], 'end': None}
    return st, y0


def interval_newton(F, derivative):
    lo, hi = map(Q, CONTRACT['mu_interval'])
    m = (lo + hi)/2
    fa, fb = map(Q, F)
    da, db = map(Q, derivative)
    require(da <= db < 0 or 0 < da <= db, 'Derivative contains zero')
    quotients = [a/b for a in (fa, fb) for b in (da, db)]
    n = [m - max(quotients), m - min(quotients)]
    meet = [max(lo, n[0]), min(hi, n[1])]
    return {'old_interval': [str(lo), str(hi)], 'midpoint': str(m), 'F_midpoint': list(F),
            'F_mu': list(derivative), 'newton_image': list(map(str, n)), 'intersection': list(map(str, meet)),
            'nonempty': meet[0] <= meet[1], 'subset': lo <= meet[0] <= meet[1] <= hi,
            'width_ratio': str((meet[1] - meet[0])/(hi - lo)),
            'tenfold_contraction': meet[0] <= meet[1] and (meet[1] - meet[0])*10 <= hi - lo}


def experiment():
    lo, hi = map(Q, CONTRACT['mu_interval'])
    m = (lo + hi)/2
    st, _ = source_initial((m, m), 'midpoint_determinant')
    mid = flow('midpoint_determinant', st, source_flow)
    # Evaluate the actual Robin determinant before ANY wall-identity replacement.
    y, p = mid['end'], mid['p']
    F = y[7] + 2*y[3]*y[5] + p['gamma']*y[6]/2
    derivative = rec.read(IDENTITY / 'output/mode/RESULT.json')['F_mu']['exact']
    newton = interval_newton(qends(F), derivative)
    if not (OUT / 'NEWTON.json').exists():
        rec.atomic(OUT / 'NEWTON.json', newton, True)
    else:
        require(rec.read(OUT / 'NEWTON.json') == newton, 'Newton resume mismatch')
    result = {'proposal_id': 'R01-P1', 'guard': GUARD, 'newton': newton,
              'gates': {'R01-G1': 'PASS' if newton['subset'] else 'FAIL_INCONSISTENCY',
                        'R01-G2': 'NOT_EVALUATED', 'R01-G3': 'NOT_RUN'},
              'new_time_evolution_steps': 0, 'new_full_domain_material_bound': False,
              'old_failure_preserved': True}
    print(json.dumps({'newton_nonempty': newton['nonempty'], 'mu_width_ratio': float(Q(newton['width_ratio']))}), flush=True)
    if not newton['subset']:
        result['classification'] = 'INCONSISTENT_EMPTY_NEWTON_INTERSECTION'
        return result
    if not newton['tenfold_contraction']:
        result['gates']['R01-G2'] = 'UNDECIDED_INSUFFICIENT_CONTRACTION'
        result['classification'] = 'UNDECIDED__ONE_CONTRACTION_INSUFFICIENT'
        return result
    st, y0 = source_initial(newton['intersection'], 'contracted_source')
    lower = preparation.wall_jets(y0, st['p'], 0)
    src = flow('contracted_source', st, source_flow)
    p = src['p']
    jets = [lower, preparation.wall_jets(src['end'], p, 1)]
    preps = {w: preparation.prepare(e, jets, p) for w, e in EPS.items()}
    old = rec.read(PRE / 'BASELINE_PREPARATION.json')
    pairs = {}
    for w in EPS:
        baseline, new = endpoint_metrics(old['endpoints'][w]), metrics(preps[w])
        ratios = {k: new[k]/baseline[k] for k in baseline}
        pairs[w] = {'baseline_endpoints': old['endpoints'][w], 'new_endpoints': prep_endpoints(preps[w]),
                    'baseline': fractions(baseline), 'new': fractions(new), 'ratios': fractions(ratios),
                    'all_halved': all(v <= Q(1, 2) for v in ratios.values())}
    prep_record = {'guard': GUARD, 'mu': newton['intersection'], 'jets': jets, 'preps': preps, 'comparisons': pairs}
    if not (OUT / 'PREPARATION.json').exists():
        rec.atomic(OUT / 'PREPARATION.json', prep_record, True)
    else:
        require(rec.read(OUT / 'PREPARATION.json') == rec.pack(prep_record), 'Preparation resume mismatch')
    result['preparation'] = pairs
    ok = all(v['all_halved'] for v in pairs.values())
    result['gates']['R01-G2'] = 'PASS' if ok else 'NEGATIVE_FOR_STRATEGY'
    result['classification'] = 'MU_CONTRACTION_AND_PREPARATION_REDUCTION_CONFIRMED' if ok else 'MU_CONTRACTED__PREPARATION_NOT_HALVED'
    print(json.dumps({'preparation_ratios': {w: {k: float(Q(v)) for k, v in r['ratios'].items()} for w, r in pairs.items()}}), flush=True)
    if not ok:
        return result
    A = {'common': {'p': p, 'y0': rp.canonical(y0)}, 'D_ball': p['D'], 'jets': jets, 'preps': preps}
    result['center_diagnostics'] = {}
    for w in EPS:
        base = rec.unpack(rec.read(BASE / f'outputs/phase-{w}-center/PHASE.json'))
        centers = [Q(x) for x in base['center']]
        initial = rp.phase_initial(A, w, 'center', None, centers)
        name = w + '_center'
        initial['which'] = name
        initial['task_index'] = CONTRACT['production_order'].index(name)
        try:
            phase = flow(name, initial, nonlinear)
            G = phase['map']['G'][0]
            ratio = rp.rad(G)/rp.rad(base['map']['G'][0])
            require(rec.pack(initial['p']['x']) == rec.pack([arb(rp.f2q(x)) for x in centers]), 'Center moved')
            result['center_diagnostics'][w] = {'status': 'AVAILABLE', 'center': base['center'],
                'baseline_G_a': qends(base['map']['G'][0]), 'new_G_a': qends(G),
                'baseline_radius': str(rp.rad(base['map']['G'][0])), 'new_radius': str(rp.rad(G)),
                'radius_ratio': str(ratio)}
        except (ArithmeticError, ValueError, TimeoutError) as error:
            result['center_diagnostics'][w] = {'status': 'UNAVAILABLE', 'reason': str(error)}
            rec.atomic(OUT / name / 'DIAGNOSTIC_FAILURE.json', {'guard': GUARD, 'error': str(error)}, True)
            break
    for w in EPS:
        result['center_diagnostics'].setdefault(w, {'status': 'NOT_RUN_AFTER_DIAGNOSTIC_STOP'})
    result['gates']['R01-G3'] = 'REPORTED' if all(v['status'] == 'AVAILABLE' for v in result['center_diagnostics'].values()) else 'DIAGNOSTIC_UNAVAILABLE'
    return result


def integrity(result):
    status('RESULT_INTEGRITY_CHECK', False)
    checks = {'guard_unchanged': guard_check() == GUARD,
              'preflight_baseline_unchanged': rec.sha(PRE / 'BASELINE_PREPARATION.json') == rec.read(ROOT / 'FREEZE.json')['baseline_sha256'],
              'flow_count_at_most_four': len(list(OUT.glob('*/RESULT.json'))) <= 4}
    n = result.get('newton')
    if n is not None:
        checks['interval_newton_exact_reconstruction'] = interval_newton(n['F_midpoint'], n['F_mu']) == n
        st = rec.unpack(rec.read(OUT / 'midpoint_determinant/RESULT.json'))
        y = st['end']
        checks['determinant_from_saved_enclosure'] = qends(y[7]+2*y[3]*y[5]+st['p']['gamma']*y[6]/2) == n['F_midpoint']
    for w, pair in result.get('preparation', {}).items():
        before, after = endpoint_metrics(pair['baseline_endpoints']), endpoint_metrics(pair['new_endpoints'])
        ratios = {k: after[k]/before[k] for k in before}
        checks[w + '_radii_reconstructed'] = (fractions(before) == pair['baseline'] and fractions(after) == pair['new']
            and fractions(ratios) == pair['ratios'] and all(v <= Q(1,2) for v in ratios.values()) == pair['all_halved'])
    for w, diag in result.get('center_diagnostics', {}).items():
        if diag['status'] == 'AVAILABLE':
            r = fraction_radius(diag['new_G_a'])/fraction_radius(diag['baseline_G_a'])
            base = rec.read(BASE / f'outputs/phase-{w}-center/PHASE.json')
            checks[w + '_G_a_radius_and_center'] = str(r) == diag['radius_ratio'] and diag['center'] == base['center']
    for p in OUT.glob('*/RESULT.json'):
        flow_result = rec.read(p)
        checks[p.parent.name + '_guard_and_coverage'] = flow_result['guard'] == GUARD and flow_result['cover'] == [[str(D1), str(D2)]]
        cp = flow_result['checkpoint']
        checks[p.parent.name + '_checkpoint_digest'] = rec.fingerprint(rec.read(p.parent/cp['path'])) == cp['digest']
    record = {'utc': rec.now(), 'guard': GUARD, 'checks': checks, 'passed': all(checks.values()),
              'result_sha256': rec.sha(ROOT / 'RESULT.json'),
              'output_sha256': {str(p.relative_to(ROOT)): rec.sha(p) for p in OUT.rglob('*.json') if p.name != 'STATUS.json'}}
    rec.atomic(ROOT / 'RESULT_INTEGRITY.json', record, True)
    return record


def main():
    global GUARD, COMPUTE_START, PRIOR_SECONDS
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['run', 'resume', 'restart-control'])
    parser.add_argument('--guard')
    args = parser.parse_args()
    require(sys.platform == 'linux', 'Numerical work is Linux-only')
    c4.check_environment()
    c4.limit_address_space()
    ctx.prec = CONTRACT['bits']; ctx.threads = 1
    if args.command == 'restart-control':
        restart_child(args.guard)
        return
    lock = open(ROOT / 'RUN.lock', 'a+')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    require(not (ROOT / 'TERMINAL.json').exists(), 'Terminal result must never restart')
    require(not (ROOT / 'FAILURE.json').exists(), 'Failed-closed run must never automatically restart')
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt('SIGTERM')))
    try:
        if args.command == 'run':
            require(not (ROOT / 'BINDINGS.json').exists(), 'Use exact resume, not rerun')
            GUARD = bindings()
            preflight(GUARD)
        GUARD = guard_check()
        for p in OUT.glob('*/LATEST.json'):
            st = rec.load(p.parent, GUARD)
            PRIOR_SECONDS = max(PRIOR_SECONDS, st.get('campaign_compute_seconds', 0.0))
        COMPUTE_START = time.monotonic()
        result = experiment()
        result.update(compute_seconds=spent(), completed_utc=rec.now(), runtime_identity=identity(),
                      full_production_flows_completed=len(list(OUT.glob('*/RESULT.json'))))
        rec.atomic(ROOT / 'RESULT.json', result, True)
        check = integrity(result)
        outcome = result['classification'] if check['passed'] else 'TECHNICAL_INCOMPLETE__RESULT_INTEGRITY_FAILED'
        terminal = {'utc': rec.now(), 'guard': GUARD, 'classification': outcome,
                    'integrity_passed': check['passed'], 'result_sha256': rec.sha(ROOT / 'RESULT.json'),
                    'integrity_sha256': rec.sha(ROOT / 'RESULT_INTEGRITY.json'), 'successor_launched': False}
        rec.atomic(ROOT / 'TERMINAL.json', terminal, True)
        status('TERMINAL', False, outcome, gates=result['gates'], compute_seconds=spent())
        print(json.dumps(terminal), flush=True)
    except KeyboardInterrupt as error:
        status('STOPPED_RECOVERABLE', False, note=str(error), current_flow=CURRENT)
        raise
    except Exception as error:
        failure = {'utc': rec.now(), 'guard': GUARD, 'error_type': type(error).__name__,
                   'error': str(error), 'traceback': traceback.format_exc(), 'current_flow': CURRENT,
                   'classification': 'TECHNICAL_INCOMPLETE', 'scientific_exclusion': False}
        if not (ROOT / 'FAILURE.json').exists():
            rec.atomic(ROOT / 'FAILURE.json', failure, True)
        status('FAILED_CLOSED', False, 'TECHNICAL_INCOMPLETE', error=str(error), current_flow=CURRENT)
        print(json.dumps(failure), flush=True)
        raise


if __name__ == '__main__':
    main()
