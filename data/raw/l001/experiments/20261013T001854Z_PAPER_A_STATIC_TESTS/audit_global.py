"""Reviewer implementation of exact saved-cover reconstruction; no owner imports."""
from pathlib import Path
from fractions import Fraction
import collections
import hashlib
import json

P = Path(__file__).resolve().parent

def read(name):
    return json.loads((P / 'inputs' / name).read_text())

def pair(value):
    a, b = [Fraction(x) for x in value]
    assert a <= b
    return a, b

def bounds(record):
    return pair(record['exact_bounds'])

def main():
    inputs = json.loads((P / 'SOURCE_BINDINGS.json').read_text())
    for row in inputs['files']:
        data = (P / row['path']).read_bytes()
        source = P.parent / 'academic2-event-horizon' / row['source_relative_to_academic2_event_horizon']
        assert hashlib.sha256(data).hexdigest() == row['sha256'] and data == source.read_bytes()
    result = read('global.json')
    primary = read('primary_root.json')
    independent = read('independent_root.json')
    rows = result['terminal_boxes']
    intervals = [pair(r['a_exact_bounds']) for r in rows]
    assert len(rows) == 726 and not result['unresolved']
    assert all(a < b for a, b in intervals)
    assert intervals[0][0] == 0 and intervals[-1][1] == Fraction(3602879701896397, 36028797018963968)
    assert all(intervals[k][1] == intervals[k+1][0] for k in range(len(rows)-1))
    kinds = collections.Counter(r['classification'] for r in rows)
    assert kinds == {'NEGATIVE_CURVATURE_EXCLUDED': 19, 'FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED': 706, 'CERTIFIED_D1_UNIQUE_ROOT': 1}
    for row in rows:
        record = row['record']
        if row['classification'] == 'NEGATIVE_CURVATURE_EXCLUDED':
            assert all(bounds(record['curvature'][producer])[1] < 0 for producer in ['primary', 'independent'])
        elif row['classification'] == 'FIRST_EVENT_SCALAR_RESIDUAL_EXCLUDED':
            assert pair(record['a_exact_bounds']) == pair(row['a_exact_bounds'])
            signed = []
            for producer in ['primary', 'independent']:
                r = record[producer]
                lower, upper = bounds(r['h'])
                assert upper < 0 or lower > 0
                signed.append(upper < 0)
                assert bounds(r['G_s'])[1] < 0
                lowg, highg = bounds(r['G'])
                assert lowg <= 0 <= highg
                left, right = r['event_cells']
                assert r['steps'] == 8192 and 0 <= left <= right < 8191
                assert r['negative_after_cell'] == right+1 and r['obstruction'] is None
                assert pair(r['event_bracket_exact']) == (Fraction(left,4096), Fraction(right+1,4096))
            assert signed[0] == signed[1]
    root = next(row for row in rows if row['classification'] == 'CERTIFIED_D1_UNIQUE_ROOT')
    expected_root = (Fraction(3567242354111177,36028797018963968), Fraction(3567242426168771,36028797018963968))
    assert pair(root['a_exact_bounds']) == pair(root['record']['root_exact_bounds']) == expected_root
    assert root['record'] == result['root_authority']
    images = [pair(primary['narrow']['newton_exact_bounds'])]
    assert images[0] == pair(root['record']['primary_newton_exact_bounds'])
    assert tuple(Fraction(float(x)) for x in independent['frozen_inputs']['root_box']) == expected_root
    assert [r['steps'] for r in independent['levels']] == [8192,16384]
    for level in independent['levels']:
        images.append(bounds(level['interval_newton_image']))
        a,b = bounds(level['root_box']['event_quantities']['q_a'])
        assert a > 0 or b < 0
    assert all(expected_root[0] < a <= b < expected_root[1] for a,b in images)
    print(json.dumps({'status':'PASS','reviewer_implementation_independent_of_owner':True,'input_bytes_unchanged':True,'cover_boxes':len(rows),'classification_counts':dict(kinds),'newton_images_checked':len(images),'claim_boundary':'Saved interval arithmetic and event-index consistency; no earlier-cell flow or enclosure regeneration.'},indent=2))

if __name__ == '__main__':
    main()
