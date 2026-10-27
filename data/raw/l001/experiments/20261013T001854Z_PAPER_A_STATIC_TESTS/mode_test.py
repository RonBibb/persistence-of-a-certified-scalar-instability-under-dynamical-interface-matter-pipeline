"""Fresh rational endpoint, event-cover, norm and displacement checker."""
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
MU = (Q(-33, 25000), Q(-131, 100000))
D = (Q(32727, 16384), Q(32729, 16384))
A = (Q(456607025194779413, 4611686018427387904), Q(114151756532473697, 1152921504606846976))
ORDER = ['primary_low', 'primary_high', 'independent_low', 'independent_high', 'primary_strip', 'independent_strip']

def bounds(record):
    a, b = Q(record['lo_exact']), Q(record['hi_exact'])
    if a > b:
        raise ValueError('reversed interval')
    return a, b

def sign(pair): return 1 if pair[0] > 0 else -1 if pair[1] < 0 else 0
def overlap(a, b): return max(a[0], b[0]) <= min(a[1], b[1])
def ceil(x): return -((-x.numerator) // x.denominator)
def floor_decimal(x):
    scale = 10**10
    return Q((x * scale).numerator // (x * scale).denominator, scale)

def alternating_exp(x):
    if not Q(-8) < x <= 0:
        raise ValueError('alternating-series range premise failed')
    term = total = Q(1)
    for n in range(1, 65):
        term = term * x / n
        total += term
    upper = total
    lower = total + term * x / 65
    if not lower <= upper or not abs(x) / 66 < 1:
        raise ValueError('alternating-tail premise failed')
    return lower, upper

def evaluate(data):
    failed, checks, strips = [], [], []
    def check(name, passed, task=None):
        checks.append({'check': name, 'task': task, 'pass': bool(passed)})
        if not passed:
            failed.append({'check': name, 'task': task})
    try:
        result, acceptance, audit = data['result'], data['acceptance'], data['audit']
        config = result['config']
        check('frozen_intervals', tuple(map(Q, config['mu'])) == MU and tuple(map(Q, config['D'])) == D and tuple(map(Q, config['A'])) == A)
        tasks = result['tasks']
        check('six_tasks', len(tasks) == 6 and [t['task'] for t in tasks] == ORDER == config['task_order'])
        check('separate_final_acceptance', acceptance['independently_accepted'] is True and audit['audit_pass'] is True)
        check('provisional_preserved', result['producer_provisional_pending_audit'] is True)
        check('acceptance_binding', acceptance['artifacts']['output/RESULT.json'] == data['producer_result_sha256'] == audit['result_sha256'] and acceptance['artifacts']['INDEPENDENT_AUDIT.json'] == data['audit_sha256'])
        check('accepted_mu_interval', tuple(map(Q, acceptance['mu_open_interval'])) == MU)
        signs = []
        for task in tasks:
            name = task['task']
            steps = 8192 if name.startswith('primary') else 16384
            step = Q(2, steps)
            cells = ceil(D[1] / step)
            cover = []
            for j in range(max(0, ceil(D[0] / step) - 1), cells):
                s = j * step
                if s + step >= D[0] and s <= D[1]:
                    cover.append({'index': j, 's_exact': str(s), 'lo_exact': str(max(D[0], s)), 'hi_exact': str(min(D[1], s + step))})
            check('event_cover', task['event_cover'] == cover and task['cells'] == cells, name)
            k, b0, sector = (bounds(task[key]) for key in ('K', 'B0', 'sector'))
            check('curvature_positive', k[0] > 0, name)
            check('normalization_nonzero', sign(b0) != 0, name)
            exact_sector = MU[0] + 4 * k[0], MU[1] + 4 * k[1]
            check('sector_outward', sector[0] <= exact_sector[0] <= exact_sector[1] <= sector[1], name)
            check('sector_negative', sector[1] < 0, name)
            if not name.endswith('strip'):
                signs.append(sign(bounds(task['determinant'])))
                check('endpoint_nonzero', signs[-1] != 0, name)
            else:
                psi, w = bounds(task['extrema']['psi']), bounds(task['extrema']['W'])
                check('strip_psi_positive', psi[0] > 0, name)
                exponential = alternating_exp(2 * w[0])
                check('rational_exp_positive', exponential[0] > 0, name)
                norm = tuple(12 * D[0] * psi[0]**2 * x for x in exponential)
                check('norm_common_floor', norm[0] > Q(437, 1000), name)
                check('norm_formula_overlap', overlap(norm, bounds(task['Z_lower_bound'])), name)
                displacement = -2 * D[1] * psi[1], -2 * D[0] * psi[0]
                archived = bounds(task['deltaD_bound'])
                check('displacement_outward', archived[0] <= displacement[0] <= displacement[1] <= archived[1], name)
                check('displacement_common_bound', Q(-219) < displacement[0] <= displacement[1] < Q(-1997, 500), name)
                check('archived_displacement_nonzero', archived[1] < 0, name)
                strips.append({'task': name, 'rigorous_norm_lower_floor': str(floor_decimal(norm[0])), 'displacement_exact': list(map(str, displacement)), 'displacement_display': list(map(float, displacement)), 'alternating_series_degrees': [65, 64], 'tail_ratio_upper': str(abs(2 * w[0]) / 66)})
        check('opposite_endpoint_signs', len(signs) == 4 and signs[0] * signs[1] == signs[2] * signs[3] == -1)
        for i in (0, 1):
            check('independent_endpoint_overlap', overlap(bounds(tasks[i]['determinant']), bounds(tasks[i + 2]['determinant'])))
        return {'pass': not failed, 'failures': failed, 'predicate_count': len(checks), 'checks': checks, 'endpoint_signs': signs, 'strip_bounds': strips}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError) as error:
        return {'pass': False, 'failures': failed + [{'check': 'schema_or_arithmetic_error', 'error': str(error)}], 'predicate_count': len(checks), 'checks': checks}

def load_data():
    manifest = json.loads((HERE / 'MODE_SOURCE_BINDINGS.json').read_text())
    blobs = {}
    for record in manifest['files']:
        path = HERE / record['path']
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('input symlink')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('input hash mismatch')
        blobs[record['path'].removeprefix('mode_inputs/')] = raw
    return {'result': json.loads(blobs['output/RESULT.json']), 'acceptance': json.loads(blobs['RESULT.json']), 'audit': json.loads(blobs['INDEPENDENT_AUDIT.json']), 'producer_result_sha256': hashlib.sha256(blobs['output/RESULT.json']).hexdigest(), 'audit_sha256': hashlib.sha256(blobs['INDEPENDENT_AUDIT.json']).hexdigest()}

def main():
    data = load_data()
    baseline = evaluate(data)
    controls = []
    for name in ('endpoint_zero', 'psi_zero', 'displacement_corrupt', 'event_cover_missing', 'sector_zero', 'acceptance_removed'):
        mutated = copy.deepcopy(data)
        tasks = mutated['result']['tasks']
        if name == 'endpoint_zero':
            tasks[0]['determinant']['lo_exact'] = '0'; expected = 'endpoint_nonzero'
        elif name == 'psi_zero':
            tasks[4]['extrema']['psi']['lo_exact'] = '0'; expected = 'strip_psi_positive'
        elif name == 'displacement_corrupt':
            tasks[4]['deltaD_bound']['lo_exact'] = '0'; tasks[4]['deltaD_bound']['hi_exact'] = '1'; expected = 'displacement_outward'
        elif name == 'event_cover_missing':
            tasks[0]['event_cover'].pop(); expected = 'event_cover'
        elif name == 'sector_zero':
            tasks[0]['sector']['hi_exact'] = '0'; expected = 'sector_negative'
        else:
            mutated['acceptance']['independently_accepted'] = False; expected = 'separate_final_acceptance'
        result = evaluate(mutated)
        controls.append({'name': name, 'expected_failed_predicate': expected, 'rejected_for_targeted_reason': not result['pass'] and expected in {x['check'] for x in result['failures']}, 'failures': result['failures']})
    passed = baseline['pass'] and all(c['rejected_for_targeted_reason'] for c in controls)
    print(json.dumps({'schema': 'paper-a-central-mode-saved-proof-test/v1', 'status': 'PASS' if passed else 'FAIL', 'baseline': baseline, 'semantic_negative_controls': controls, 'controls_bypass_hash_gate': True, 'claim_boundary': 'Saved endpoint sign and strip-inequality reconstruction; no spectral ODE, determinant enclosure, full spectrum or nonlinear fate rederivation.'}, indent=2))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':
    main()
