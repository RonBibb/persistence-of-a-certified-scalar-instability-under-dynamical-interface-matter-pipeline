"""Independent exact reconstruction of uniform-tension saved proof arithmetic."""
import copy
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
DELTA = (Q(-1, 1000000), Q(1, 1000000))
BASELINE = Q(-851862101055633, 140737488355328)

def bounds(record):
    result = tuple(map(Q, record['exact_bounds']))
    if len(result) != 2 or result[0] > result[1]:
        raise ValueError('malformed interval')
    return result

def add(a, b): return a[0] + b[0], a[1] + b[1]
def neg(a): return -a[1], -a[0]
def subtract(a, b): return add(a, neg(b))
def multiply(a, b):
    points = [x * y for x in a for y in b]
    return min(points), max(points)
def divide(a, b):
    if b[0] <= 0 <= b[1]:
        raise ValueError('zero denominator')
    return multiply(a, (1 / b[1], 1 / b[0]))
def distance(a): return Q(0) if a[0] <= 0 <= a[1] else min(abs(x) for x in a)
def texts(a): return list(map(str, a))

def evaluate(data):
    failed, checks = [], []
    def check(name, passed):
        checks.append({'check': name, 'pass': bool(passed)})
        if not passed:
            failed.append(name)
    try:
        result, root_saved, center_saved, transport, parent, bindings = (data[k] for k in ('result', 'root', 'center', 'transport', 'parent', 'bindings'))
        root, center = root_saved['event'], center_saved['event']
        rq, cq = root['event_quantities'], center['event_quantities']
        model = bindings['exact_model']
        baseline = Q(result['parameter']['baseline_exact'])
        delta = tuple(map(Q, result['parameter']['delta_exact']))
        check('frozen_parameter', baseline == BASELINE == Q(model['LAMBDA_B_Q']) and delta == DELTA and tuple(map(Q, bindings['contract']['delta_exact'])) == DELTA)
        intended = add((baseline, baseline), delta)
        check('intended_tension', tuple(map(Q, result['parameter']['tension_exact'])) == intended == tuple(map(Q, bindings['intended_tension_exact'])))
        enclosure = bounds(result['parameter']['outward_tension_enclosure'])
        check('tension_enclosure', enclosure[0] <= intended[0] <= intended[1] <= enclosure[1])
        for saved in (root_saved, center_saved):
            check('flow_tension_enclosure', bounds(saved['tension_enclosure']) == enclosure)
            check('flow_guard', saved['guard'] == result['guard'] == data['freeze_sha256'])
            check('flow_source', saved['source_sha256'] == data['producer_sha256'])
        box = (Q(model['ROOT_LO_Q']), Q(model['ROOT_HI_Q']))
        cp = Q(model['ROOT_CENTER_Q'])
        check('frozen_root_launch', tuple(map(Q, root_saved['launch_exact'])) == box and tuple(map(Q, center_saved['launch_exact'])) == (cp, cp))
        der = bounds(rq['q_a'])
        check('derivative_excludes_zero', not der[0] <= 0 <= der[1])
        newton = subtract((cp, cp), divide(bounds(cq['h']), der))
        neighborhood = result['neighborhood']
        check('newton_exact_reconstruction', newton == bounds(neighborhood['newton_image']))
        check('newton_strict_inclusion', box[0] < newton[0] <= newton[1] < box[1])
        check('saved_newton_strict_inclusion', box[0] < bounds(neighborhood['newton_image'])[0] <= bounds(neighborhood['newton_image'])[1] < box[1])
        gd, ga, hd, ha = (bounds(rq[k]) for k in ('G_s', 'G_a', 'h_s', 'h_a'))
        chain = neg(multiply(gd, der))
        direct = subtract(multiply(ga, hd), multiply(gd, ha))
        check('chain_exact_reconstruction', chain == bounds(neighborhood['determinant_chain']))
        check('direct_exact_reconstruction', direct == bounds(neighborhood['determinant_direct']))
        check('determinants_positive', chain[0] > 0 and direct[0] > 0)
        determinant = max(chain[0], direct[0]), min(chain[1], direct[1])
        check('determinant_intersection', determinant[0] <= determinant[1])
        da = divide(hd, multiply((Q(6), Q(6)), determinant))
        dd = neg(divide(ha, multiply((Q(6), Q(6)), determinant)))
        check('launch_response_exact', da == bounds(neighborhood['response']['da_dlambda_b']))
        check('separation_response_exact', dd == bounds(neighborhood['response']['dD_dlambda_b']))
        check('launch_response_positive', da[0] > 0)
        check('separation_response_negative', dd[1] < 0)
        check('transversality_negative', gd[1] < 0)
        check('root_curvature_positive', bounds(rq['curvature'])[0] > 0)
        check('transport_delta', tuple(map(Q, transport['delta_exact'])) == DELTA)
        shift = divide(delta, (Q(6), Q(6)))
        rows, minimum, negative, endpoint = [], None, 0, Q(0)
        parent_boxes = parent['terminal_boxes']
        check('parent_box_count', len(parent_boxes) == 693)
        for index, box_record in enumerate(parent_boxes):
            lo, hi = map(Q, box_record['a_exact_bounds'])
            check('parent_adjacency', lo == endpoint and lo < hi)
            endpoint = hi
            r = box_record['record']
            curvature = tuple(map(Q, r['curvature_exact_bounds']))
            if curvature[1] < 0:
                negative += 1
                rows.append({'index': index, 'a_exact': texts((lo, hi)), 'kind': 'NEGATIVE_CURVATURE', 'k_exact': texts(curvature)})
            else:
                g = subtract(tuple(map(Q, r['G_exact_bounds'])), shift)
                h = tuple(map(Q, r['scalar_residual_exact_bounds']))
                margin = max(distance(g), distance(h))
                check('transport_residual_positive', margin > 0)
                minimum = margin if minimum is None else min(minimum, margin)
                rows.append({'index': index, 'a_exact': texts((lo, hi)), 'kind': 'RESIDUAL_EXCLUSION' if margin > 0 else 'UNRESOLVED', 'G_exact': texts(g), 'h_exact': texts(h), 'lower_bound_exact': str(margin)})
        check('transport_rows_exact', rows == transport['boxes'])
        last = Q(0)
        for row in transport['boxes']:
            lo, hi = map(Q, row['a_exact'])
            check('transport_adjacency', lo == last and hi > lo)
            last = hi
        check('cover_endpoint', last == endpoint == Q(model['V0_Q']) == Q(float('0.1')))
        check('transport_counts', negative == 20 and len(rows) - negative == 673 and transport['negative_curvature_boxes'] == 20 and transport['residual_boxes'] == 673 and transport['box_count'] == 693)
        check('transport_minimum', minimum == Q(transport['minimum_lower_bound_exact']) == Q(result['fixed_separation']['minimum_lower_bound_exact']))
        check('transport_margin', minimum > Q(77, 10000))
        check('transport_no_unresolved', transport['unresolved'] == [] and result['fixed_separation']['unresolved'] == [])
        return {'pass': not failed, 'failed_predicates': failed, 'predicate_count': len(checks), 'checks': checks, 'newton_exact': texts(newton), 'response': {'da_dlambda_b_exact': texts(da), 'dD_dlambda_b_exact': texts(dd), 'da_display': list(map(float, da)), 'dD_display': list(map(float, dd))}, 'minimum_residual_margin_exact': str(minimum), 'minimum_residual_margin_display': float(minimum), 'reconstructed_rows': len(rows)}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError) as error:
        return {'pass': False, 'failed_predicates': failed + ['schema_or_arithmetic_error'], 'error': str(error), 'predicate_count': len(checks), 'checks': checks}

def load_data():
    manifest = json.loads((HERE / 'TENSION_SOURCE_BINDINGS.json').read_text())
    blobs = {}
    for record in manifest['files']:
        path = HERE / record['path']
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('input symlink')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('input hash mismatch')
        blobs[record['path'].removeprefix('tension_inputs/')] = raw
    names = {'result': 'RESULT.json', 'root': 'flows/uniform_root/RESULT.json', 'center': 'flows/uniform_center/RESULT.json', 'transport': 'D2A_TRANSPORT.json', 'parent': 'd2a_parent.json', 'bindings': 'BINDINGS.json'}
    result = {k: json.loads(blobs[v]) for k, v in names.items()}
    result['freeze_sha256'] = hashlib.sha256(blobs['FREEZE.json']).hexdigest()
    result['producer_sha256'] = hashlib.sha256(blobs['run.py']).hexdigest()
    return result

def main():
    data = load_data()
    baseline = evaluate(data)
    controls = []
    for name in ('newton_boundary', 'chain_mismatch', 'response_sign', 'omit_tension_shift', 'transport_gap', 'delta_widened', 'zero_derivative'):
        mutated = copy.deepcopy(data)
        n = mutated['result']['neighborhood']
        if name == 'newton_boundary':
            n['newton_image']['exact_bounds'][0] = mutated['bindings']['exact_model']['ROOT_LO_Q']; expected = 'saved_newton_strict_inclusion'
        elif name == 'chain_mismatch':
            n['determinant_chain']['exact_bounds'][0] = '0'; expected = 'chain_exact_reconstruction'
        elif name == 'response_sign':
            n['response']['dD_dlambda_b']['exact_bounds'] = texts(neg(bounds(n['response']['dD_dlambda_b']))); expected = 'separation_response_exact'
        elif name == 'omit_tension_shift':
            row = next(x for x in mutated['transport']['boxes'] if x['kind'] == 'RESIDUAL_EXCLUSION')
            row['G_exact'] = mutated['parent']['terminal_boxes'][row['index']]['record']['G_exact_bounds']; expected = 'transport_rows_exact'
        elif name == 'transport_gap':
            mutated['transport']['boxes'][1]['a_exact'][0] = '0'; expected = 'transport_adjacency'
        elif name == 'delta_widened':
            mutated['result']['parameter']['delta_exact'] = ['-1/100000', '1/100000']; expected = 'frozen_parameter'
        else:
            mutated['root']['event']['event_quantities']['q_a']['exact_bounds'][0] = '-1'; expected = 'derivative_excludes_zero'
        result = evaluate(mutated)
        controls.append({'name': name, 'expected_failed_predicate': expected, 'rejected_for_targeted_reason': not result['pass'] and expected in result['failed_predicates'], 'failed_predicates': result['failed_predicates']})
    passed = baseline['pass'] and all(x['rejected_for_targeted_reason'] for x in controls)
    print(json.dumps({'schema': 'paper-a-tension-saved-proof-test/v1', 'status': 'PASS' if passed else 'FAIL', 'baseline': baseline, 'semantic_negative_controls': controls, 'controls_bypass_hash_gate': True, 'claim_boundary': 'Uniform saved-interval arithmetic only; no fresh flow validation, no independent neighborhood producer, no extension of full-launch first-event uniqueness.'}, indent=2))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':
    main()
