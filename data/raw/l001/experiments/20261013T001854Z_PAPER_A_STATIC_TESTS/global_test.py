"""Independent saved-cover arithmetic; standard library only."""
import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXPECTED_COUNTS = {'NEGATIVE_CURVATURE_EXCLUDED': 19, 'FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED': 706, 'CERTIFIED_D1_UNIQUE_ROOT': 1}
ROOT = tuple(Q(float(x)) for x in ('0.09901086489880687', '0.09901086689880687'))

def interval(record):
    a, b = map(Q, record['exact_bounds'])
    if a > b:
        raise ValueError('reversed interval')
    return a, b

def sign(pair):
    return 1 if pair[0] > 0 else -1 if pair[1] < 0 else 0

def evaluate(data, primary, independent):
    failures = []
    checked = Counter()
    def check(name, condition, index=None):
        checked[name] += 1
        if not condition:
            failures.append({'check': name, 'box': index})
    try:
        boxes = data['terminal_boxes']
        check('box_count', len(boxes) == 726)
        check('classification_counts', dict(Counter(b['classification'] for b in boxes)) == EXPECTED_COUNTS)
        check('no_unresolved', data['unresolved'] == [])
        previous = Q(0)
        roots = []
        for index, box in enumerate(boxes):
            lo, hi = map(Q, box['a_exact_bounds'])
            check('positive_width', lo < hi, index)
            check('adjacency', lo == previous, index)
            previous = hi
            kind, record = box['classification'], box['record']
            if kind == 'NEGATIVE_CURVATURE_EXCLUDED':
                for producer in ('primary', 'independent'):
                    check('negative_curvature', interval(record['curvature'][producer])[1] < 0, index)
            elif kind == 'FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED':
                check('record_launch_bounds', tuple(map(Q, record['a_exact_bounds'])) == (lo, hi), index)
                signs = []
                for producer in ('primary', 'independent'):
                    event = record[producer]
                    s = sign(interval(event['h']))
                    signs.append(s)
                    check('scalar_exclusion', s != 0, index)
                    check('transversality', interval(event['G_s'])[1] < 0, index)
                    g = interval(event['G'])
                    check('event_zero_enclosure', g[0] <= 0 <= g[1], index)
                    first, last = event['event_cells']
                    check('event_indices', 0 <= first <= last < 8192 and event['negative_after_cell'] == last + 1 and last + 1 < 8192, index)
                    check('event_bracket', event['steps'] == 8192 and tuple(map(Q, event['event_bracket_exact'])) == (Q(first, 4096), Q(last + 1, 4096)), index)
                    check('no_event_obstruction', event['obstruction'] is None, index)
                check('dual_same_scalar_sign', signs[0] == signs[1] != 0, index)
            elif kind == 'CERTIFIED_D1_UNIQUE_ROOT':
                roots.append((lo, hi))
                check('root_box', (lo, hi) == ROOT == tuple(map(Q, record['root_exact_bounds'])), index)
                check('root_record_binding', record == data['root_authority'], index)
            else:
                check('known_classification', False, index)
        check('last_endpoint', previous == Q(float('0.1')))
        check('one_root', roots == [ROOT])
        image = tuple(map(Q, primary['narrow']['newton_exact_bounds']))
        check('primary_newton_inclusion', ROOT[0] < image[0] <= image[1] < ROOT[1])
        check('primary_image_binding', image == tuple(map(Q, data['root_authority']['primary_newton_exact_bounds'])))
        check('independent_root_box', tuple(Q(float(x)) for x in independent['frozen_inputs']['root_box']) == ROOT)
        check('independent_levels', [x['steps'] for x in independent['levels']] == [8192, 16384])
        for level in independent['levels']:
            image = interval(level['interval_newton_image'])
            check('independent_newton_inclusion', ROOT[0] < image[0] <= image[1] < ROOT[1])
            check('independent_root_derivative', sign(interval(level['root_box']['event_quantities']['q_a'])) != 0)
        return {'pass': not failures, 'failures': failures, 'predicate_counts': dict(checked), 'total_predicates': sum(checked.values())}
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError) as error:
        return {'pass': False, 'failures': failures + [{'check': 'schema_or_interval_error', 'error': str(error)}], 'predicate_counts': dict(checked)}

def load_inputs():
    bindings = json.loads((HERE / 'SOURCE_BINDINGS.json').read_text())
    result = {}
    for name in ('global.json', 'primary_root.json', 'independent_root.json'):
        record = next(x for x in bindings['files'] if x['path'] == 'inputs/' + name)
        path = HERE / record['path']
        if any(p.is_symlink() for p in [path, *path.parents]):
            raise ValueError('input symlink')
        blob = path.read_bytes()
        if hashlib.sha256(blob).hexdigest() != record['sha256']:
            raise ValueError('source hash mismatch')
        result[name] = json.loads(blob)
    return result

def main():
    loaded = load_inputs()
    data, primary, independent = (loaded[n] for n in ('global.json', 'primary_root.json', 'independent_root.json'))
    baseline = evaluate(data, primary, independent)
    controls = []
    for name in ('gap', 'duplicate_root', 'curvature_touch_zero', 'scalar_contains_zero', 'transversality_zero', 'invalid_event_bracket', 'newton_touches_boundary'):
        d, p, i = copy.deepcopy((data, primary, independent))
        scalar = next(b for b in d['terminal_boxes'] if b['classification'] == 'FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED')
        if name == 'gap':
            d['terminal_boxes'][1]['a_exact_bounds'][0] = str(Q(d['terminal_boxes'][1]['a_exact_bounds'][0]) + Q(1, 10**20)); expected = 'adjacency'
        elif name == 'duplicate_root':
            d['terminal_boxes'].append(copy.deepcopy(next(b for b in d['terminal_boxes'] if b['classification'] == 'CERTIFIED_D1_UNIQUE_ROOT'))); expected = 'one_root'
        elif name == 'curvature_touch_zero':
            d['terminal_boxes'][0]['record']['curvature']['primary']['exact_bounds'][1] = '0'; expected = 'negative_curvature'
        elif name == 'scalar_contains_zero':
            scalar['record']['primary']['h']['exact_bounds'] = ['-1', '1']; expected = 'scalar_exclusion'
        elif name == 'transversality_zero':
            scalar['record']['primary']['G_s']['exact_bounds'][1] = '0'; expected = 'transversality'
        elif name == 'invalid_event_bracket':
            scalar['record']['primary']['event_bracket_exact'][0] = '0'; expected = 'event_bracket'
        else:
            p['narrow']['newton_exact_bounds'][0] = str(ROOT[0]); expected = 'primary_newton_inclusion'
        result = evaluate(d, p, i)
        controls.append({'name': name, 'expected_failed_predicate': expected, 'rejected_for_targeted_reason': not result['pass'] and expected in {x['check'] for x in result['failures']}, 'result': result})
    passed = baseline['pass'] and all(x['rejected_for_targeted_reason'] for x in controls)
    print(json.dumps({'schema': 'paper-a-global-saved-proof-test/v1', 'status': 'PASS' if passed else 'FAIL', 'baseline': baseline, 'semantic_negative_controls': controls, 'controls_bypass_hash_gate': True, 'claim_boundary': 'Exact saved-cover predicates and root-image inclusion only; interval-flow validity and full first-event cell history remain inherited.'}, indent=2))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':
    main()
