import copy
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent

def interval(values):
    lo, hi = map(Q, values)
    if lo > hi:
        raise ValueError('reversed interval')
    return lo, hi

def evaluate(flow, trace, trace_digest, source_digest, guard):
    errors, counts = [], Counter()
    def check(name, good):
        counts[name] += 1
        if not good and name not in errors:
            errors.append(name)
    try:
        check('trace_hash_link', flow['trace_sha256'] == trace_digest)
        check('source_guard_links', flow['source_sha256'] == source_digest and flow['guard'] == trace['guard'] == guard)
        event = flow['event']
        first, last = event['event_cells']
        check('event_indices', 0 < first <= last < 16383)
        check('cell_count', len(trace['trace']) == trace['steps'] == event['steps'] == 16384)
        zero_cells, cluster_g, cluster_gs = [], [], []
        for index, cell in enumerate(trace['trace']):
            check('cell_order', cell['cell'] == index)
            g, gs = interval(cell['G']), interval(cell['G_s'])
            sign = 1 if g[0] > 0 else -1 if g[1] < 0 else 0
            if sign == 0:
                zero_cells.append(index)
            expected = 1 if index < first else -1 if index > last else 0
            check('first_event_history', sign == expected)
            check('cell_consistency_flags', cell['finite'] is True and cell['first_integral_contains_zero'] is True and 1 <= cell['picard'] <= 32)
            check('positive_warp', Q(cell['warp_lower']) > 0)
            if first <= index <= last:
                check('event_transversality', gs[1] < 0)
                cluster_g.append(g); cluster_gs.append(gs)
        check('contiguous_zero_cluster', zero_cells == list(range(first, last + 1)))
        check('exact_event_bracket', tuple(map(Q, event['event_bracket_exact'])) == (Q(first, 8192), Q(last + 1, 8192)))
        for label, values in [('G', cluster_g), ('G_s', cluster_gs)]:
            hull = min(x[0] for x in values), max(x[1] for x in values)
            outer = interval(event['event_quantities'][label]['exact_bounds'])
            check('aggregate_' + label + '_contains_trace', outer[0] <= hull[0] <= hull[1] <= outer[1])
        return {'pass': not errors, 'failed_predicates': errors, 'predicate_counts': dict(counts), 'total_predicates': sum(counts.values()), 'zero_cells': zero_cells, 'event_bracket_exact': event['event_bracket_exact']}
    except (KeyError, TypeError, ValueError, IndexError) as error:
        return {'pass': False, 'failed_predicates': errors + ['schema_or_interval_error'], 'error': str(error), 'predicate_counts': dict(counts)}

def main():
    blobs = {}
    for r in json.loads((HERE / 'SOURCE_BINDINGS.json').read_text())['files']:
        p = HERE / r['path']
        if any(x.is_symlink() for x in [p, *p.parents]):
            raise ValueError('symlink')
        raw = p.read_bytes()
        if hashlib.sha256(raw).hexdigest() != r['sha256']:
            raise ValueError('snapshot hash mismatch')
        blobs[r['path'].removeprefix('inputs/')] = raw
    sha = lambda name: hashlib.sha256(blobs[name]).hexdigest()
    binding, freeze, terminal = (json.loads(blobs[x]) for x in ('BINDINGS.json', 'FREEZE.json', 'TERMINAL.json'))
    anchors = {
        'producer_source': sha('run.py') == next(v for k, v in binding['sources'].items() if k.endswith('/run.py')),
        'binding_freeze': sha('BINDINGS.json') == freeze['bindings_sha256'],
        'freeze_terminal': sha('FREEZE.json') == terminal['artifacts']['freeze_sha256'] == '55bda8fcf4b6b7dbc0dc19f3534dd74612e1e943355162d35eff6977821b7057',
        'integrity_terminal': sha('RESULT_INTEGRITY.json') == terminal['artifacts']['integrity_sha256'] == '25b7daeea7d2474465577a6e399e9532db091feac9de71cf8a799aa779bf39b4',
    }
    results, controls = {}, []
    for name in ('uniform_root', 'uniform_center'):
        flow = json.loads(blobs['flows/' + name + '/RESULT.json'])
        trace = json.loads(blobs['flows/' + name + '/CELLS.json'])
        args = (sha('flows/' + name + '/CELLS.json'), sha('run.py'), sha('FREEZE.json'))
        results[name] = evaluate(flow, trace, *args)
        if name == 'uniform_root':
            for mutation in ('early_negative_G', 'event_zero_Gs', 'broken_trace_hash'):
                f, t = copy.deepcopy((flow, trace))
                if mutation == 'early_negative_G':
                    t['trace'][0]['G'] = ['-2', '-1']; expected = 'first_event_history'
                elif mutation == 'event_zero_Gs':
                    t['trace'][f['event']['event_cells'][0]]['G_s'][1] = '0'; expected = 'event_transversality'
                else:
                    f['trace_sha256'] = '0' * 64; expected = 'trace_hash_link'
                report = evaluate(f, t, *args)
                controls.append({'name': mutation, 'expected_failed_predicate': expected, 'rejected_for_targeted_reason': not report['pass'] and expected in report['failed_predicates'], 'failed_predicates': report['failed_predicates']})
    passed = all(anchors.values()) and all(r['pass'] for r in results.values()) and all(c['rejected_for_targeted_reason'] for c in controls)
    print(json.dumps({'schema': 'uniform-tension-trace-history-test/v1', 'status': 'PASS' if passed else 'FAIL', 'historical_anchor_links': anchors, 'flows': results, 'negative_controls': controls, 'historical_whole_flow_authentication': 'UNRESOLVED; no separate original top-level metadata flow-result digest found; internal trace/source/guard links establish consistency only', 'claim_boundary': 'Saved observational history reconstruction for two uniform flows, no IVP regeneration or independent whole-flow historical authentication.'}, indent=2))
    raise SystemExit(0 if passed else 1)

if __name__ == '__main__':
    main()
