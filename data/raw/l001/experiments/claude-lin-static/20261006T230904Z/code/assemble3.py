"""Producer assembly for run 20261006T230904Z: gates, case-0 background separation, provisional classification.

assemble() is the single decision path; the preflight runs it on every synthetic fixture.
    python -B <run>/code/assemble3.py run
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common3 import RUN, OUT, PACKET, CONFIG, now, sha, read, atomic, show, freeze_guard  # noqa: E402

ORDER = ('R', 'E', 'B')


def classify(gates, science):
    failed = {r['group'] for r in gates if not r['pass']}
    if 'R' in failed:
        return 'ACCEPTED_FLOW_REPLAY_MISMATCH'
    if 'E' in failed:
        return 'EVENT_EXCLUSION_INCONSISTENT'
    if 'B' in failed:
        return 'BUDGET_NOT_CLOSED'
    return science


def assemble(out, flows, inherited, K, guard, case0_records):
    out = Path(out)
    g, summaries, inconsistent = [], {}, {}
    for flow in flows:
        d = out / flow
        if (d / 'EVENT_INCONSISTENT.json').exists():
            inconsistent[flow] = read(d / 'EVENT_INCONSISTENT.json')
            continue
        s = read(d / 'SUMMARY.json')
        if s['guard'] != guard or s['arrays']['sha256'] != sha(d / 'CELLS.f64'):
            raise RuntimeError('Stale or altered flow summary ' + flow)
        summaries[flow] = s
    for flow, rec in inconsistent.items():
        det = rec['details']
        g.append({'id': f'R1e.{flow}.event_stage_bitwise_equal', 'group': 'R', 'pass': bool(det['event_stage_bitwise_equal'])})
        for f2, r in det['per_flow'].items():
            g.append({'id': f'E2.{flow}.{f2}.nonempty_inside_K', 'group': 'E', 'pass': 'interval' in r and r['kept'] > 0})
        g.append({'id': f'E3.{flow}.common_interval_nonempty', 'group': 'E', 'pass': False})
    first = None
    for flow, s in summaries.items():
        first = first or s['event']['common_narrowed_interval']
        g.append({'id': f'R1.{flow}.all_blocks_bitwise_equal', 'group': 'R', 'pass': bool(s['all_blocks_bitwise_equal'])})
        g.append({'id': f'R1e.{flow}.event_stage_bitwise_equal', 'group': 'R', 'pass': bool(s['event_stage_bitwise_equal'])})
        g.append({'id': f'R2.{flow}.replayed_running_max_equals_inherited', 'group': 'R',
                  'pass': s['accepted_max_errors_exact'] == inherited[flow]})
        g.append({'id': f'E1.{flow}.common_interval_identical_across_jobs', 'group': 'E',
                  'pass': s['event']['common_narrowed_interval'] == first})
        for f2, rec in s['event']['per_flow'].items():
            g.append({'id': f'E2.{flow}.{f2}.nonempty_inside_K', 'group': 'E', 'pass': 'interval' in rec and rec['kept'] > 0})
        g.append({'id': f'B1.{flow}.closure', 'group': 'B', 'pass': s['closure_violations'] == 0})
        g.append({'id': f'C1.{flow}.coverage_0_to_D2', 'group': 'B', 'pass': s['coverage_gaps'] == 0 and bool(s['coverage_end_equals_D2'])})
    science, narrowed, interval = None, None, None
    if summaries and not inconsistent:
        lo, hi = Fraction(first[0]), Fraction(first[1])
        Dlo, Dhi = K
        g.append({'id': 'E3.common_interval_nonempty_inside_K', 'group': 'E', 'pass': Dlo <= lo < hi <= Dhi})
        narrowed = (lo, hi) != (Dlo, Dhi)
        doms = [summaries[x]['fieldsummary']['A']['dominant_width'] for x in ('positive', 'negative') if x in summaries]
        dom = doms[0] if len(set(doms)) == 1 else 'MIXED'
        science = ('DSTAR_NARROWED__A_DOMINATED_BY_' if narrowed else 'DSTAR_NOT_NARROWED__A_DOMINATED_BY_') + dom
        interval = first
    cls = classify(g, science or 'EVENT_EXCLUSION_INCONSISTENT')
    result = {'guard': guard, 'utc': now(), 'classification_provisional': cls, 'gates': g,
              'gates_passed': sum(r['pass'] for r in g), 'gates_total': len(g), 'narrowed_interval': interval,
              'narrowed': narrowed, 'inconsistent_flows': sorted(inconsistent),
              'deferred': ['gauge completion q*', 'conformal lapse', 'coordinate length X*', 'inverse map and node positions', 'node-level field bounds'],
              'note': 'Provisional until the independent verifier accepts it.'}
    if interval is not None:
        s0 = summaries.get('positive') or next(iter(summaries.values()))
        result['event'] = s0['event']
        result['width_ratio'] = s0['event']['width_ratio']
        result['bounds'] = {flow: {f: {k: fs[k] for k in ('bound', 'dominant_width', 'shares', 'argmax_cell', 'argmax_components')}
                                   for f, fs in s['fieldsummary'].items()} for flow, s in summaries.items()}
        result['walls'] = {flow: summaries[flow]['walls'] for flow in summaries if 'walls' in summaries[flow]}
        result['proper_separation'] = {flow: summaries[flow]['proper_separation'] for flow in summaries if 'proper_separation' in summaries[flow]}
        lo, hi = (Fraction(v) for v in interval)
        bg = {}
        for N, path in case0_records.items():
            L = Fraction(str(read(path)['proper_separation']))
            b = max(abs(lo - L), abs(hi - L))
            bg[str(N)] = {'bound_exact': str(b), 'bound': show(b)}
        result['background_proper_separation_case0_D_star'] = bg
        result['summaries'] = {flow: sha(out / flow / 'SUMMARY.json') for flow in summaries}
    if inconsistent:
        result['inconsistency_records'] = {flow: sha(out / flow / 'EVENT_INCONSISTENT.json') for flow in inconsistent}
    atomic(out / 'PRODUCER_RESULT.json', result, True)
    return result


def main():
    guard, _ = freeze_guard()
    inherited = {flow: read(PACKET['identity'] / 'output' / flow / 'RESULT.json')['max_error_bounds_exact'] for flow in CONFIG['flows']}
    K = tuple(Fraction(v) for v in CONFIG['D_interval'])
    case0 = {N: PACKET['spatial'] / 'inputs' / f'fine_c4_case0_N{N}_p80.json' for N in CONFIG['degrees']}
    result = assemble(OUT, CONFIG['flows'], inherited, K, guard, case0)
    print(json.dumps({'classification_provisional': result['classification_provisional'],
                      'gates': [result['gates_passed'], result['gates_total']], 'interval': result['narrowed_interval']}), flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'run':
        raise SystemExit('usage: assemble3.py run')
    main()
