"""Exact interval reconstruction of two saved isolation determinant forms."""
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent

def interval(record):
    a, b = map(Q, record['exact_bounds'])
    if a > b:
        raise ValueError('reversed interval')
    return a, b

def mul(a, b):
    corners = [x * y for x in a for y in b]
    return min(corners), max(corners)

def sub(a, b):
    return a[0] - b[1], a[1] - b[0]

def contains(outer, inner):
    return outer[0] <= inner[0] <= inner[1] <= outer[1]

def overlap(a, b):
    return max(a[0], b[0]) <= min(a[1], b[1])

def evaluate(data):
    failures, checks, reconstructions = [], [], {}
    def check(name, passed, producer=None):
        checks.append({'check': name, 'producer': producer, 'pass': bool(passed)})
        if not passed:
            failures.append({'check': name, 'producer': producer})
    try:
        brackets = []
        for producer, steps in (('primary', 32768), ('independent', 16384)):
            record = data[producer]
            gd, ga, hd, ha, qa = (interval(record[k]) for k in ('G_D', 'G_a', 'h_D', 'h_a', 'q_a_along_first_event'))
            chain = mul((-gd[1], -gd[0]), qa)
            direct = sub(mul(ga, hd), mul(gd, ha))
            saved_chain = interval(record['jacobian_determinant_from_chain_rule'])
            saved_direct = interval(record['jacobian_determinant_direct'])
            check('chain_enclosure', contains(saved_chain, chain), producer)
            check('direct_enclosure', contains(saved_direct, direct), producer)
            check('chain_positive', chain[0] > 0, producer)
            check('direct_positive', direct[0] > 0, producer)
            check('saved_determinants_positive', saved_chain[0] > 0 and saved_direct[0] > 0, producer)
            check('determinant_forms_overlap', overlap(chain, direct), producer)
            check('transversality', gd[1] < 0, producer)
            check('event_derivative_positive', qa[0] > 0, producer)
            check('curvature_positive', interval(record['curvature'])[0] > 0, producer)
            for key in ('G', 'h'):
                bounds = interval(record[key])
                check('root_residual_' + key, bounds[0] <= 0 <= bounds[1], producer)
            first, last = record['event_cells']
            check('event_indices', 0 <= first <= last < steps and record['negative_after_cell'] == last + 1 and last + 1 < steps, producer)
            bracket = tuple(map(Q, record['event_bracket_exact']))
            brackets.append(bracket)
            check('event_bracket', record['steps'] == steps and bracket == (Q(2 * first, steps), Q(2 * (last + 1), steps)), producer)
            check('no_obstruction', record['obstruction'] is None, producer)
            reconstructions[producer] = {'chain_exact': list(map(str, chain)), 'direct_exact': list(map(str, direct)), 'chain_decimal_display': list(map(float, chain)), 'direct_decimal_display': list(map(float, direct)), 'saved_chain_exact': list(map(str, saved_chain)), 'saved_direct_exact': list(map(str, saved_direct))}
        intersection = (max(x[0] for x in brackets), min(x[1] for x in brackets))
        check('event_overlap', intersection[0] <= intersection[1])
        check('intersection_record', intersection == tuple(map(Q, data['cross_producer']['event_bracket_intersection_exact'])))
        return {'pass': not failures, 'failures': failures, 'checks': checks, 'reconstructions': reconstructions, 'event_intersection_exact': list(map(str, intersection))}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError) as error:
        return {'pass': False, 'failures': failures + [{'check': 'schema_or_interval_error', 'error': str(error)}], 'checks': checks}

def main():
    binding = next(x for x in json.loads((HERE / 'SOURCE_BINDINGS.json').read_text())['files'] if x['path'] == 'inputs/isolation.json')
    path = HERE / binding['path']
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise ValueError('input symlink')
    blob = path.read_bytes()
    if hashlib.sha256(blob).hexdigest() != binding['sha256']:
        raise ValueError('input hash mismatch')
    data = json.loads(blob)
    baseline = evaluate(data)
    controls = []
    for name in ('chain_clipped', 'direct_clipped', 'q_contains_zero', 'gd_contains_zero', 'event_bracket_corrupt', 'intersection_corrupt'):
        mutated = copy.deepcopy(data)
        p = mutated['primary']
        if name == 'chain_clipped':
            p['jacobian_determinant_from_chain_rule']['exact_bounds'] = ['0', '1']; expected = 'chain_enclosure'
        elif name == 'direct_clipped':
            p['jacobian_determinant_direct']['exact_bounds'] = ['0', '1']; expected = 'direct_enclosure'
        elif name == 'q_contains_zero':
            p['q_a_along_first_event']['exact_bounds'][0] = '-1'; expected = 'event_derivative_positive'
        elif name == 'gd_contains_zero':
            p['G_D']['exact_bounds'][1] = '0'; expected = 'transversality'
        elif name == 'event_bracket_corrupt':
            p['event_bracket_exact'][0] = '0'; expected = 'event_bracket'
        else:
            mutated['cross_producer']['event_bracket_intersection_exact'][0] = '0'; expected = 'intersection_record'
        result = evaluate(mutated)
        controls.append({'name': name, 'expected_failed_predicate': expected, 'rejected_for_targeted_reason': not result['pass'] and expected in {x['check'] for x in result['failures']}, 'failures': result['failures']})
    passed = baseline['pass'] and all(x['rejected_for_targeted_reason'] for x in controls)
    print(json.dumps({'schema': 'paper-a-isolation-saved-proof-test/v1', 'status': 'PASS' if passed else 'FAIL', 'baseline': baseline, 'semantic_negative_controls': controls, 'controls_bypass_hash_gate': True, 'claim_boundary': 'Exact determinant arithmetic from saved derivative intervals only; no ODE or sensitivity enclosure regeneration.'}, indent=2))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':
    main()
