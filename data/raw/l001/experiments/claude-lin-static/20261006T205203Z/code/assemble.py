"""Producer assembly: gates and provisional classification from the three flow summaries.

    python -B <run>/code/assemble.py run
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common2 import RUN, OUT, CONFIG, now, sha, read, atomic, freeze_guard  # noqa: E402


def gates_and_class(summaries):
    g = []
    for flow, s in summaries.items():
        g.append({'id': f'R1.{flow}.all_blocks_bitwise_equal', 'pass': bool(s['all_blocks_bitwise_equal'])})
        g.append({'id': f'R2.{flow}.accepted_bounds_equal_inherited', 'pass': bool(s['replayed_bounds_equal_inherited_result'])
                  and bool(s.get('replayed_bounds_equal_spatial_enclosures', True))})
        g.append({'id': f'B1.{flow}.closure', 'pass': s['closure_violations'] == 0})
        for f, fs in s['fieldsummary'].items():
            g.append({'id': f'R3.{flow}.{f}.argmax_equals_running_max', 'pass': bool(fs['accepted_equals_inherited_running_max'])})
    ok = all(r['pass'] for r in g)
    if not ok:
        failed = {r['id'].split('.')[0] for r in g if not r['pass']}
        cls = 'ACCEPTED_FLOW_REPLAY_MISMATCH' if failed & {'R1', 'R2', 'R3'} else 'BUDGET_NOT_CLOSED'
    else:
        doms = [summaries[x]['fieldsummary']['A']['dominant_width'] for x in ('positive', 'negative')]
        cls = 'ENCLOSURE_BUDGET_RESOLVED__A_DOMINATED_BY_' + (doms[0] if doms[0] == doms[1] else 'MIXED')
    return g, cls


def main():
    guard, _ = freeze_guard()
    summaries = {}
    for flow in CONFIG['flows']:
        s = read(OUT / flow / 'SUMMARY.json')
        if s['guard'] != guard or s['arrays']['sha256'] != sha(OUT / flow / 'CELLS.f64'):
            raise RuntimeError('Stale or altered flow summary ' + flow)
        summaries[flow] = s
    g, cls = gates_and_class(summaries)
    table = {flow: {f: {k: fs[k] for k in ('accepted_bound', 'dominant_width', 'argmax_cell', 'argmax_shares',
                                           'refined_bound', 'refined_dominant_width', 'refined_shares', 'argmax_attribution')}
                    for f, fs in s['fieldsummary'].items()} for flow, s in summaries.items()}
    result = {'guard': guard, 'utc': now(), 'classification_provisional': cls, 'gates': g,
              'gates_passed': sum(r['pass'] for r in g), 'gates_total': len(g), 'budget_table': table,
              'summaries': {flow: sha(OUT / flow / 'SUMMARY.json') for flow in summaries},
              'propagation_to_lapse_map_observables': 'NOT_PERFORMED: frozen scope of this window is the width budget only',
              'note': 'Provisional until the independent verifier accepts it.'}
    atomic(OUT / 'PRODUCER_RESULT.json', result, True)
    print(json.dumps({'classification_provisional': cls, 'gates': [result['gates_passed'], result['gates_total']]}), flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'run':
        raise SystemExit('usage: assemble.py run')
    main()
