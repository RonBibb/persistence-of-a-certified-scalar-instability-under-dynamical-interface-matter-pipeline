"""Independent verifier for run 20261006T230904Z (D* narrowing, re-evaluated bounds, wall and separation observables).

Does not import narrow.py or assemble3.py. Uses the byte-identical inherited validated engine (shared,
disclosed) with its own drivers. Every check is an agreement check between its own recomputation and the
producer's record. The final label is the producer's label (technical labels included) if and only if all
agreement checks pass and that label follows from the producer's gates in the frozen order; otherwise
UNRESOLVED_VERIFICATION.
    python -B <run>/code/verify3.py run
"""
import json
import os
import signal
import subprocess
import sys
import time
import traceback
from array import array
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inherited'))
sys.path.insert(1, str(HERE))
from flint import arb, fmpq, ctx  # noqa: E402
import records  # noqa: E402
import validated  # noqa: E402
import mode_flow  # noqa: E402
import prepared_flow  # noqa: E402
from series import bounds, hull, interval  # noqa: E402
import identity_run as ir  # noqa: E402
from common3 import (RUN, OUT, VER, PACKET, CONFIG, now, sha, read, atomic, fq, up_float, show,  # noqa: E402
                     check_environment, limit_address_space)

KEYS = ('max_errors', 'domain_maxima', 'event_cover', 'event_derivative', 'max_picard', 'cell_index', 'task_index', 'name', 'p', 'y')
COLS = ('E', 'center', 'state', 'source_step', 'event', 'native_step')
RADIUS = Fraction(1, 2 ** (-CONFIG['closure_radius_relative_log2']))
FLOOR = Fraction(1, 2 ** (-CONFIG['closure_absolute_log2']))


def mr(x):
    lo, hi = bounds(x)
    return (lo + hi) / 2, (hi - lo) / 2


def zero_in(x):
    lo, hi = bounds(x)
    return lo <= 0 <= hi


def gate(rows, gid, ok, value=None):
    rows.append({'id': gid, 'pass': bool(ok), 'value': value})


def ck_list(C, flow):
    out = []
    for p in sorted(Path(C['ckdir'][flow]).glob(f"{C['task'][flow]:02d}-*.json")):
        body = read(p)
        if records.fingerprint(body) != p.name.split('-')[-1][:-5]:
            raise RuntimeError('Checkpoint digest mismatch')
        out.append((int(p.name.split('-')[1]), body))
    return out


def advance(C, flow, state, hook):
    """Own driver of the inherited cell update until the next checkpoint boundary."""
    engine = mode_flow if flow == 'mode' else prepared_flow
    prof, Dlo, Dhi, step = C['profile'](flow), C['Dlo'], C['Dhi'], C['step']
    while state['cell_index'] * step < Dhi:
        i = state['cell_index']
        t = i * step
        h = min(step, Dhi - t)
        y, cell = validated.step(state['y'], h, state['p'], engine)
        ranged = validated.range_on_cell(cell, fmpq(0), h)
        before = prof.enclose(t * prof.D / Dhi, min(prof.D, (t + h) * prof.D / Dlo))
        after = ir.physical_values(ranged, state['p'], flow)
        state['max_errors'] = [max(a, ir.maximum_abs(b - c)) for a, b, c in zip(state['max_errors'], after, before)]
        state['domain_maxima'] = [max(a, ir.maximum_abs(b)) for a, b in zip(state['domain_maxima'], ranged)]
        if flow == 'mode' and t + h >= Dlo:
            lo, hi = max(fmpq(0), Dlo - t), min(h, Dhi - t)
            v = mode_flow.determinant_mu(validated.range_on_cell(cell, lo, hi), state['p'])
            state['event_derivative'] = v if state['event_derivative'] is None else hull(state['event_derivative'], v)
            state['event_cover'].append({'cell': i, 'left': t + lo, 'right': t + hi, 'F_mu': v})
        hook(i, t, h, cell, state)
        state['y'] = y
        state['cell_index'] += 1
        state['max_picard'] = max(state['max_picard'], cell['picard_iterations'])
        if state['cell_index'] % 256 == 0 or t + h == Dhi:
            break
    return state


def bitwise(state, body):
    packed = records.pack({k: state[k] for k in KEYS})
    return all(packed[k] == body['state'][k] for k in KEYS)


def own_event(C, flow):
    """Own replay of the event cells and own exclusion; returns models and a record in the producer's schema."""
    cks = ck_list(C, flow)
    first = min(C['event_cells'])
    prior = [c for c in cks if c[0] <= first]
    state = records.unpack(prior[-1][1]['state']) if prior else C['fresh'](flow)
    models, checks = {}, []

    def keep(i, t, h, cell, st):
        if i in C['event_cells']:
            models[i] = (t, cell, st['p'])
    for end, body in cks:
        if end <= state['cell_index']:
            continue
        state = advance(C, flow, state, keep)
        checks.append([end, bitwise(state, body)])
        state = records.unpack(body['state'])
    Dlo, Dhi, seam, M = C['Dlo'], C['Dhi'], C['seam'], C['M']
    survivors, exI, exR, deriv = [], 0, 0, None
    for left, right, idx in ((Dlo, seam, C['event_cells'][0]), (seam, Dhi, C['event_cells'][1])):
        t, cell, p = models[idx]
        width = (right - left) / M
        for k in range(M):
            a = left + width * k
            b = right if k == M - 1 else left + width * (k + 1)
            y = validated.range_on_cell(cell, a - t, b - t)
            gap = y[2] - p['v1']
            israel = y[1] - (p['lambda_b'] + p['gamma'] * gap * gap / 2) / 6
            robin = y[3] + p['gamma'] * gap / 2
            zi, zr = zero_in(israel), zero_in(robin)
            exI += 0 if zi else 1
            exR += 0 if zr else 1
            if zi and zr:
                survivors.append((a, b))
        y = validated.range_on_cell(cell, left - t, right - t)
        slope = -y[3] * y[3] / 3 - p['k'] * y[4] * y[4] - p['gamma'] * (y[2] - p['v1']) * y[3] / 6
        deriv = slope if deriv is None else hull(deriv, slope)
    rec = {'pieces': 2 * M, 'kept': len(survivors), 'excluded_by_e_I': exI, 'excluded_by_e_R': exR,
           'contiguous': all(survivors[i][1] == survivors[i + 1][0] for i in range(len(survivors) - 1)),
           'e_I_derivative_on_K': [str(v) for v in bounds(deriv)], 'e_I_monotone_on_K': not zero_in(deriv)}
    if survivors:
        rec['interval'] = [str(survivors[0][0]), str(survivors[-1][1])]
    return models, rec, checks


def components(C, flow, cell, t, h, p, D1, D2):
    """Own recomputation of one cell's new comparison (worst subcell per field), components and closure."""
    prof = C['profile'](flow)
    Dn, m = prof.D, C['m']
    if flow != 'mode':
        p = p | {'D': interval(D1, D2)}
    worst = None
    for k in range(m):
        lo, hi = h * k / m, h * (k + 1) / m
        if t + lo >= D2:
            break
        hi = min(hi, D2 - t)
        a = ir.physical_values(validated.range_on_cell(cell, lo, hi), p, flow)
        b = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + hi) * Dn / D1))
        if worst is None:
            worst = [None] * len(a)
        for j in range(len(a)):
            E = ir.maximum_abs(a[j] - b[j])
            if worst[j] is None or E > worst[j][0]:
                worst[j] = (E, lo, a[j], b[j])
    out = []
    for j, (E, lo, a, b) in enumerate(worst):
        pa = ir.physical_values(validated.range_on_cell(cell, lo, lo), p, flow)[j]
        pd = prof.enclose((t + lo) * Dn / D2, min(Dn, (t + lo) * Dn / D1))[j]
        (ma, ra), (mb, rb) = mr(a), mr(b)
        total = fq(abs(ma - mb) + ra + rb)
        slack = RADIUS * fq(ra + rb) + FLOOR * (1 + fq(abs(ma)) + fq(abs(mb)))
        out.append({'E': E, 'center': abs(ma - mb), 'state': mr(pa)[1], 'source_step': ra - mr(pa)[1],
                    'event': mr(pd)[1], 'native_step': rb - mr(pd)[1], 'closed': total - slack <= fq(E) <= total + slack})
    return out


def frozen_order(gates, summaries, narrowed):
    failed = {r['group'] for r in gates if not r['pass']}
    if 'R' in failed:
        return 'ACCEPTED_FLOW_REPLAY_MISMATCH'
    if 'E' in failed:
        return 'EVENT_EXCLUSION_INCONSISTENT'
    if 'B' in failed:
        return 'BUDGET_NOT_CLOSED'
    doms = [summaries[x]['fieldsummary']['A']['dominant_width'] for x in ('positive', 'negative')]
    dom = doms[0] if doms[0] == doms[1] else 'MIXED'
    return ('DSTAR_NARROWED__A_DOMINATED_BY_' if narrowed else 'DSTAR_NOT_NARROWED__A_DOMINATED_BY_') + dom


def verify(C):
    t0 = time.monotonic()
    ctx.prec = 768
    ctx.threads = 1
    g = []
    out = Path(C['out'])
    produced = read(out / 'PRODUCER_RESULT.json')
    summaries, inconsistent = {}, {}
    for f in C['flows']:
        if (out / f / 'EVENT_INCONSISTENT.json').exists():
            inconsistent[f] = read(out / f / 'EVENT_INCONSISTENT.json')
        else:
            summaries[f] = read(out / f / 'SUMMARY.json')
            if summaries[f]['arrays']['sha256'] != sha(out / f / 'CELLS.f64'):
                raise RuntimeError('Cell array changed after publication')
    any_rec = next(iter(summaries.values()))['event'] if summaries else next(iter(inconsistent.values()))['details']
    lo, hi, empty = fq(C['Dlo']), fq(C['Dhi']), False
    models_all = {}
    for flow in C['flows']:
        models, rec, checks = own_event(C, flow)
        models_all[flow] = models
        ref_checks = [[c['end_cell'], c['bitwise_equal']] for c in any_rec['block_checks'][flow]]
        gate(g, f'VE0.{flow}.event_stage_bitwise_flags_agree', checks == ref_checks, checks)
        gate(g, f'VE1.{flow}.own_exclusion_record_equals_producer', rec == any_rec['per_flow'][flow], rec.get('interval'))
        if 'interval' not in rec:
            empty = True
        else:
            lo, hi = max(lo, Fraction(rec['interval'][0])), min(hi, Fraction(rec['interval'][1]))
    own_common = None if (empty or lo >= hi) else [str(lo), str(hi)]
    gate(g, 'VE2.common_interval_agrees', own_common == produced.get('narrowed_interval'), own_common)
    if summaries and not inconsistent and own_common is not None:
        D1, D2 = fmpq(*Fraction(own_common[0]).as_integer_ratio()), fmpq(*Fraction(own_common[1]).as_integer_ratio())
        for flow in C['flows']:
            s = summaries[flow]
            data = array('d')
            data.frombytes((out / flow / 'CELLS.f64').read_bytes())
            n = s['arrays']['rows_per_column']
            cols = {name: data[k * n:(k + 1) * n] for k, name in enumerate(s['arrays']['columns'])}
            cks = ck_list(C, flow)
            ends = [c[0] for c in cks]
            argmax = {f: s['fieldsummary'][f]['argmax_cell'] for f in s['fields']}
            sample = set(C['sample_blocks']) | {next(b for b, e in enumerate(ends) if c < e) for c in argmax.values()}
            mism, checked, unclosed, exact = 0, 0, 0, {}
            interior, event_part = arb(0), arb(0)
            covered, gaps = fmpq(0), 0
            state = C['fresh'](flow)
            y0, p0 = list(state['y']), state['p']
            pnew = p0 if flow == 'mode' else (p0 | {'D': interval(D1, D2)})
            own_flags = []
            for b, (end, body) in enumerate(cks):
                rows = {}

                def hook(i, t, h, cell, st, b=b):
                    nonlocal interior, event_part, covered, gaps
                    if t >= D2:
                        return
                    if b in sample:
                        rows[i] = components(C, flow, cell, t, h, st['p'], D1, D2)
                    m = C['m']
                    for k in range(m):
                        a0, a1 = h * k / m, h * (k + 1) / m
                        if t + a0 >= D2:
                            break
                        a1 = min(a1, D2 - t)
                        if t + a0 != covered:
                            gaps += 1
                        covered = t + a1
                        if flow == 'mode':
                            continue
                        cuts = [a0, a1] if not (t + a0 < D1 < t + a1) else [a0, D1 - t, a1]
                        for u0, u1 in zip(cuts, cuts[1:]):
                            ell = ir.physical_values(validated.range_on_cell(cell, u0, u1), pnew, flow)[1]
                            piece = (u1 - u0) * ell.exp()
                            if t + u1 <= D1:
                                interior += piece
                            else:
                                event_part += piece
                state = advance(C, flow, state, hook)
                own_flags.append([end, bitwise(state, body)])
                replayed_max = [str(v) for v in state['max_errors']]
                for i, comp in rows.items():
                    for j, f in enumerate(s['fields']):
                        unclosed += 0 if comp[j]['closed'] else 1
                        for c in COLS:
                            checked += 1
                            if cols[f + ':' + c][i] != up_float(fq(comp[j][c])):
                                mism += 1
                        if argmax[f] == i:
                            exact[f] = comp[j]
                state = records.unpack(body['state'])
            gate(g, f'VR1.{flow}.all_block_bitwise_flags_agree', own_flags == [[c['end_cell'], c['bitwise_equal']] for c in s['block_checks']])
            gate(g, f'VR2.{flow}.replayed_running_max_agrees', replayed_max == s['accepted_max_errors_exact'])
            gate(g, f'VB1.{flow}.closure_agrees_on_sampled_cells', (unclosed == 0) == (s['closure_violations'] == 0), unclosed)
            gate(g, f'VC1.{flow}.coverage_agrees', (gaps == 0 and covered == D2) == (s['coverage_gaps'] == 0 and s['coverage_end_equals_D2']))
            gate(g, f'VF.{flow}.columns_equal_upward_rounding_of_exact', mism == 0, {'checked': checked, 'mismatches': mism, 'blocks': sorted(sample)})
            for f in s['fields']:
                fs = s['fieldsummary'][f]
                e = exact.get(f)
                ok = e is not None and str(e['E']) == fs['bound_exact'] and all(str(e[k]) == fs['argmax_components_exact'][k] for k in fs['argmax_components_exact'])
                gate(g, f'VA.{flow}.{f}.argmax_exact', ok, fs['argmax_cell'])
                gate(g, f'VM.{flow}.{f}.column_max_is_bound', max(cols[f + ':E']) == up_float(Fraction(fs['bound_exact'])))
                shares = {'CENTER_DISCREPANCY': e['center'], 'STATE_RADIUS': e['state'],
                          'COMPARISON_STEP': e['source_step'] + e['native_step'], 'EVENT_WIDTH': e['event']} if e else {}
                gate(g, f'VD.{flow}.{f}.dominant_width', bool(shares) and max(shares, key=lambda k: shares[k]) == fs['dominant_width'])
            if flow == 'mode':
                continue
            Llo, Lhi = bounds(interior)[0], bounds(interior)[1] + bounds(event_part)[1]
            gate(g, f'VL.{flow}.own_separation_enclosure_equals_producer', [str(Llo), str(Lhi)] == s['proper_separation']['enclosure'],
                 [show(fq(Llo)), show(fq(Lhi))])
            Y = None
            for left, right, idx in ((C['Dlo'], C['seam'], C['event_cells'][0]), (C['seam'], C['Dhi'], C['event_cells'][1])):
                t, cell, p = models_all[flow][idx]
                width = (right - left) / C['M']
                for k in range(C['M']):
                    a = left + width * k
                    b2 = right if k == C['M'] - 1 else left + width * (k + 1)
                    if a >= D1 and b2 <= D2:
                        y = validated.range_on_cell(cell, a - t, b2 - t)
                        Y = y if Y is None else [hull(u, v) for u, v in zip(Y, y)]
            eps, kball = p0['eps'], p0['k']
            kseed = arb(ir.exact(read(C['seed_path'])['k']))
            for N in C['degrees']:
                grid = read(C['grid'](flow, N))
                for wall, y, node in (('lower', y0, 0), ('upper', Y, N)):
                    A, ell, Phi = ir.physical_values(y, pnew, flow)
                    rho = eps * y[5] + y[9]
                    WN = arb(ir.exact(grid['seed_fields'][node][0]))
                    AN, BN = arb(ir.exact(grid['A'][node])), arb(ir.exact(grid['B'][node]))
                    own = {'A': ir.maximum_abs(A - AN), 'ell': ir.maximum_abs(ell - arb(ir.exact(grid['ell'][node]))),
                           'Phi': ir.maximum_abs(Phi - arb(ir.exact(grid['Phi'][node]))), 'rho_A_minus_W': ir.maximum_abs(rho - (AN - WN)),
                           'clock_rate': ir.maximum_abs(rho.exp() - (BN - WN).exp()),
                           'log_angular_radius': ir.maximum_abs((A - kball.log() / 2) - (AN - kseed.log() / 2))}
                    rec = s['walls'][str(N)][wall]
                    gate(g, f'VW.{flow}.N{N}.{wall}', all(str(v) == rec[q]['bound_exact'] for q, v in own.items()))
        lo_f, hi_f = Fraction(own_common[0]), Fraction(own_common[1])
        own_bg = {}
        for N, path in C['case0'].items():
            L = Fraction(str(read(path)['proper_separation']))
            own_bg[str(N)] = str(max(abs(lo_f - L), abs(hi_f - L)))
        gate(g, 'VS0.case0_background_separation_agrees',
             own_bg == {k: v['bound_exact'] for k, v in produced['background_proper_separation_case0_D_star'].items()})
        narrowed = (Fraction(own_common[0]), Fraction(own_common[1])) != (fq(C['Dlo']), fq(C['Dhi']))
        expected = frozen_order(produced['gates'], summaries, narrowed)
    elif summaries and not inconsistent:
        expected = 'UNRESOLVED_VERIFICATION'
    else:
        expected = 'ACCEPTED_FLOW_REPLAY_MISMATCH' if any(not r['pass'] for r in produced['gates'] if r['group'] == 'R') else 'EVENT_EXCLUSION_INCONSISTENT'
    gate(g, 'VC.producer_label_follows_frozen_order', produced['classification_provisional'] == expected, expected)
    if not C['fixture']:
        ps = subprocess.run(['ps', '-eo', 'pid,args'], capture_output=True, text=True, check=True).stdout.splitlines()
        live = [line.strip() for line in ps if 'code/narrow.py' in line and RUN.name in line]
        gate(g, 'VP.no_live_producer', not live, live)
    agreed = all(r['pass'] for r in g)
    return {'classification': produced['classification_provisional'] if agreed else 'UNRESOLVED_VERIFICATION', 'resolved': agreed,
            'producer_classification_provisional': produced['classification_provisional'],
            'checks_passed': sum(r['pass'] for r in g), 'checks_total': len(g), 'checks': g,
            'failed': [r['id'] for r in g if not r['pass']], 'own_common_interval': own_common, 'utc': now(),
            'seconds': time.monotonic() - t0, 'shared_inherited_engine_disclosed': True, 'imports_narrow_or_assemble': False,
            'label_rule': 'producer label kept (technical labels included) iff every agreement check passes'}


def real_context():
    conn = read(PACKET['connected'] / 'BINDINGS.json')['config']
    Dlo, Dhi = map(ir.exact, conn['D'])
    ir.capacity = lambda: {'replaced_for_replay': True}
    profiles = {}

    def profile(flow):
        if flow not in profiles:
            profiles[flow] = ir.SavedProfile(None if flow == 'mode' else CONFIG['case_of_flow'][flow])
        return profiles[flow]
    spatial = PACKET['spatial'] / 'inputs'
    return {'flows': CONFIG['flows'], 'out': OUT, 'Dlo': Dlo, 'Dhi': Dhi, 'seam': ir.exact(CONFIG['event_seam']),
            'M': CONFIG['event_subintervals_per_half'], 'event_cells': CONFIG['event_cells'], 'step': ir.exact(CONFIG['step']),
            'm': CONFIG['subcells'], 'profile': profile, 'task': CONFIG['task_index'],
            'ckdir': {f: PACKET['identity'] / 'output' / f / 'checkpoints' for f in CONFIG['flows']},
            'fresh': lambda flow: ir.fresh_state(flow, CONFIG['task_index'][flow]),
            'grid': lambda flow, N: spatial / f"fine_c4_case{CONFIG['case_of_flow'][flow]}_N{N}_p80.grid.json",
            'seed_path': PACKET['native'] / 'results/fine_c4/SEED.json',
            'case0': {N: spatial / f'fine_c4_case0_N{N}_p80.json' for N in CONFIG['degrees']},
            'degrees': CONFIG['degrees'], 'sample_blocks': CONFIG['verifier_sample_blocks'], 'fixture': False}


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'run':
        raise SystemExit('usage: verify3.py run')
    check_environment()
    limits = limit_address_space()
    if (VER / 'VERIFICATION.json').exists() or any(VER.glob('FAILURE_*.json')):
        raise RuntimeError('Verification already terminal or failed closed')
    try:
        frozen = read(RUN / 'FREEZE.json')
        for name, digest in frozen['inputs'].items():
            if sha(name) != digest:
                raise RuntimeError('Changed input ' + name)
        for name, digest in frozen['sources'].items():
            if sha(RUN / name) != digest:
                raise RuntimeError('Changed source ' + name)

        def alarm(*args):
            raise TimeoutError('Frozen verifier wall budget')
        signal.signal(signal.SIGALRM, alarm)
        signal.alarm(CONFIG['verifier_wall_seconds'])
        result = verify(real_context())
        signal.alarm(0)
        result.update({'guard': sha(RUN / 'FREEZE.json'), 'address_space': limits, 'pid': os.getpid(),
                       'compute_slot': os.environ.get('COMPUTE_SLOT'), 'verifier_source_sha256': sha(Path(__file__).resolve())})
        atomic(VER / 'VERIFICATION.json', result, True)
        print(json.dumps({'classification': result['classification'], 'checks': [result['checks_passed'], result['checks_total']],
                          'failed': result['failed']}), flush=True)
    except Exception as error:
        atomic(VER / f'FAILURE_{int(time.time())}.json', {'type': type(error).__name__, 'error': str(error),
                                                          'traceback': traceback.format_exc(), 'utc': now()}, True)
        raise
