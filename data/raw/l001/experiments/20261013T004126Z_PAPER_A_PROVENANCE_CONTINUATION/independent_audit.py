import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

root = Path(__file__).resolve().parent
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
gate = read(root / 'INDEPENDENT_GATE.json')
assert all(digest(root / p) == h for p, h in gate['files_sha256'].items())
binding = read(root / 'SOURCE_BINDINGS.json')
for row in binding['files']:
    assert digest(root / row['path']) == row['sha256']
meta = read(root / 'RUN_METADATA.json')
assert meta['returncode'] == 0 and (root / 'STDERR.txt').read_bytes() == b''
assert meta['stdout_sha256'] == digest(root / 'RESULT.json')
result = read(root / 'RESULT.json')
assert result['status'] == 'PASS'
reports = {}
for name in ['uniform_root', 'uniform_center']:
    directory = root / 'inputs' / 'flows' / name
    flow = read(directory / 'RESULT.json')
    trace = read(directory / 'CELLS.json')
    assert flow['trace_sha256'] == digest(directory / 'CELLS.json')
    assert flow['source_sha256'] == digest(root / 'inputs' / 'run.py')
    assert flow['guard'] == trace['guard'] == digest(root / 'inputs' / 'FREEZE.json')
    cells = trace['trace']
    a, b = flow['event']['event_cells']
    assert len(cells) == trace['steps'] == flow['event']['steps'] == 16384
    assert 0 < a <= b < 16383
    positives, negatives, zeros = [], [], []
    gs_intervals, g_intervals = [], []
    for i, cell in enumerate(cells):
        low, high = [F(v) for v in cell['G']]
        slo, shi = [F(v) for v in cell['G_s']]
        assert low <= high and slo <= shi
        if high < 0: negatives.append(i)
        elif low > 0: positives.append(i)
        else: zeros.append(i)
        assert cell['cell'] == i and cell['finite'] is True
        assert cell['first_integral_contains_zero'] is True
        assert 1 <= cell['picard'] <= 32 and F(cell['warp_lower']) > 0
        if a <= i <= b:
            assert shi < 0
            gs_intervals.append((slo, shi)); g_intervals.append((low, high))
    assert positives == list(range(a))
    assert zeros == list(range(a, b + 1))
    assert negatives == list(range(b + 1, 16384))
    event = flow['event']
    assert list(map(F, event['event_bracket_exact'])) == [F(a, 8192), F(b + 1, 8192)]
    for key, intervals in [('G', g_intervals), ('G_s', gs_intervals)]:
        lo, hi = map(F, event['event_quantities'][key]['exact_bounds'])
        assert all(lo <= x <= y <= hi for x, y in intervals)
    reports[name] = {'cells': len(cells), 'positive_cells': len(positives), 'zero_cells': zeros, 'negative_cells': len(negatives), 'all_checks_pass': True}
assert all(x['rejected_for_targeted_reason'] for x in result['negative_controls'])
assert len(result['negative_controls']) == 3
assert result['historical_whole_flow_authentication'].startswith('UNRESOLVED')
print(json.dumps({'status': 'PASS_WITH_HISTORICAL_AUTHENTICATION_UNRESOLVED', 'method': 'Separate stdlib evaluator partitions all exact rational G intervals into sign-index sets; no owner or producer import.', 'flows': reports, 'controls_reviewed': 3, 'result_sha256': digest(root / 'RESULT.json'), 'metadata_sha256': digest(root / 'RUN_METADATA.json'), 'limitations': 'Reconstructs saved interval history and links only. Finite and invariant fields are recorded flags; no IVP regeneration or independently authenticated historical whole-flow bytes.'}, indent=2))
