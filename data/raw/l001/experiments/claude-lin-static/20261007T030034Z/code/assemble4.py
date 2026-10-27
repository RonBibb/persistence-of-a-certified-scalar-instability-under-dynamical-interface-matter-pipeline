"""Producer assembly for run 20261007T030034Z: gates in the frozen order and the provisional classification.

assemble() is the single decision path; the preflight runs it on every synthetic fixture. When any job
recorded CONTROL_FAILED, no outcome record is opened: only the control records are read.
    python -B <run>/code/assemble4.py run
"""
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common4 import OUT, RUN3, CONFIG, now, sha, read, atomic, freeze_guard  # noqa: E402

ORDER = ('R', 'P', 'T', 'K', 'B')
LABELS = {'R': 'TECHNICAL_REPLAY_MISMATCH', 'P': 'PREPARATION_PIPELINE_MISMATCH', 'T': 'TECHNICAL_INCOMPLETE',
          'K': 'ROOT_ITERATION_INCONSISTENT', 'B': 'BUDGET_NOT_CLOSED'}
CLASSES = ('CENTER_DISCREPANCY', 'STATE_RADIUS', 'COMPARISON_STEP', 'EVENT_WIDTH')


def classify(gates, science):
    failed = {r['group'] for r in gates if not r['pass']}
    for group in ORDER:
        if group in failed:
            return LABELS[group]
    return science


def gate(rows, gid, group, ok, value=None):
    rows.append({'id': gid, 'group': group, 'pass': bool(ok), 'value': value})


def control_gates(rows, job, controls):
    gate(rows, f'R0.{job}.source_last_block_bitwise', 'R', controls['R0_source_last_block_bitwise'], controls['R0_differing_keys'])
    for w, m in controls['R0m_accepted_phase_maps_reproduced'].items():
        gate(rows, f"R0m.{job}.{w}.accepted_phase_maps_reproduced", 'R', m['center'] and m['box'], m)
    gate(rows, f'R0j.{job}.jets_K_reproduced', 'P', controls['R0j_upper_and_lower_jets_K_reproduced'])
    for which, ok in controls['R0p_preparation_K_reproduced'].items():
        gate(rows, f'R0p.{job}.{which}.preparation_K_reproduced', 'P', ok)
    gate(rows, f'D0.{job}.D_prime_recorded_inside_K_and_last_cell', 'P', controls['D0_D_prime_recorded_inside_K_and_last_cell'])


def science_label(summaries):
    def common(field):
        doms = [summaries[w]['fieldsummary'][field]['dominant_width'] for w in sorted(summaries)]
        return doms[0] if len(set(doms)) == 1 else 'MIXED'
    return f"REPREPARED__A_DOMINATED_BY_{common('A')}__PHI_DOMINATED_BY_{common('Phi')}"


ATT = CONFIG['attribution']
PRE = CONFIG['prediction']
ATT_FLOOR = Fraction(1, 2 ** (-ATT['floor_log2']))
PRE_FLOOR = Fraction(1, 2 ** (-PRE['denominator_floor_log2']))
QUANTITIES = ('Q_c7', 'Q_W0', 'Q_W1')


def attribution_outcome(Qv):
    """One quantity: NOT_APPLICABLE below the gross floor, FLOOR_LIMITED if the all-points variant keeps > 1/10,
    DECISIVE_<g> if g alone at a point keeps <= 1/10 and every other group keeps >= 9/10, otherwise MIXED."""
    full = Qv['FULL']
    if full < ATT_FLOOR:
        return {'outcome': 'NOT_APPLICABLE', 'rho': None}
    rho = {v: Qv[v] / full for v in ATT['variants'] if v != 'FULL'}
    low, high = Fraction(ATT['decisive_max']), Fraction(ATT['other_min'])
    shown = {k: str(v) for k, v in rho.items()}
    if rho['ALL'] > low:
        return {'outcome': 'FLOOR_LIMITED', 'rho': shown}
    dec = [g for g in ATT['groups'] if rho[g] <= low and all(rho[h] >= high for h in ATT['groups'] if h != g)]
    return {'outcome': 'DECISIVE_' + dec[0] if dec else 'MIXED', 'rho': shown}


def attribution_record(summaries, cases):
    per, K_per, mu_ok, carriers = {}, {}, True, {}
    for w in cases:
        A = summaries[w]['attribution_inputs']
        Q = {prep: {v: {k: Fraction(x) for k, x in row.items()} for v, row in A['quantities'][prep].items()} for prep in ('D_prime', 'K')}
        for q in QUANTITIES:
            per[f'{w}.{q}'] = attribution_outcome({v: Q['D_prime'][v][q] for v in ATT['variants']})
            K_per[f'{w}.{q}'] = attribution_outcome({v: Q['K'][v][q] for v in ATT['variants']})
            full = Q['D_prime']['FULL'][q]
            mu = Fraction(A['quantities']['MU_point'][q])
            mu_ok = mu_ok and full >= ATT_FLOOR and mu / full <= Fraction(ATT['mu_bracket_max'])
            per[f'{w}.{q}']['rho_mu'] = None if full < ATT_FLOOR else str(mu / full)
        split = {k: Fraction(v) for k, v in A['A_split_rad_w_upper_wall'].items()}
        parts = {'POINT_PART': split['rad_w_point'], 'A_BOX': split['a_box'], 'B0_BOX': split['b0_box'], 'B1_BOX': split['b1_box']}
        carriers[w] = max(parts, key=lambda k: parts[k])
    outs = [r['outcome'] for r in per.values()]
    if all(o.startswith('DECISIVE_') for o in outs) and len({ATT['classes'][o[len('DECISIVE_'):]] for o in outs}) == 1:
        label = 'NEXT_WIDTH__' + ATT['classes'][outs[0][len('DECISIVE_'):]]
        if label == 'NEXT_WIDTH__MODE_JET_RADIUS' and mu_ok:
            label += '__MU_BRACKET'
    elif all(o == 'NOT_APPLICABLE' for o in outs):
        label = 'ATTRIBUTION_NOT_APPLICABLE'
    elif any(o == 'FLOOR_LIMITED' for o in outs):
        label = 'ATTRIBUTION_FLOOR_LIMITED'
    else:
        label = 'ATTRIBUTION_MIXED'
    carrier = carriers[cases[0]] if len(set(carriers.values())) == 1 else 'MIXED'
    label += f'__A_CARRIED_BY_{carrier}' + ('__A_NEXT_WIDTH_UNDECIDED' if carrier == 'A_BOX' else '')
    return {'assigned': True, 'label': label, 'per_quantity_D_prime': per, 'per_quantity_K': K_per, 'A_carriers': carriers,
            'mu_bracket_named': label.startswith('NEXT_WIDTH__MODE_JET_RADIUS__MU_BRACKET')}


def score_row(rows, pid, case, name, num, den, lo, hi, extra=True, note=None):
    row = {'id': pid, 'case': case, 'quantity': name, 'interval': [str(lo), str(hi)]}
    if num is None or den is None or den < PRE_FLOOR:
        row.update(value=None, value_exact=None, outcome='REFUTED', note='missing value or denominator below 2^-500')
    else:
        r = num / den
        row.update(value=float(r), value_exact=str(r), outcome='CONFIRMED' if lo <= r <= hi and extra else 'REFUTED', note=note)
    rows.append(row)


def prediction_record(summaries, cases, label, previous):
    rows = []
    iv = {k: (Fraction(v['interval'][0]), Fraction(v['interval'][1])) for k, v in PRE.items() if isinstance(v, dict) and 'interval' in v}
    F = lambda x: None if x is None else Fraction(x)
    for w in cases:
        s = summaries[w]
        Q = s['attribution_inputs']['quantities']
        pi = s['prediction_inputs']
        score_row(rows, 'P1', w, 'Q_c7', F(Q['D_prime']['FULL']['Q_c7']), F(Q['K']['FULL']['Q_c7']), *iv['P1'])
        for q in ('Q_W0', 'Q_W1'):
            score_row(rows, 'P2', w, q, F(Q['D_prime']['FULL'][q]), F(Q['K']['FULL'][q]), *iv['P2'])
        for i, x in enumerate(('a', 'b0', 'b1')):
            score_row(rows, 'P3', w, 'rad G ' + x, F(pi['G_radius_new'][i]), F(pi['G_radius_accepted'][i]), *iv['P3'])
        for i, x in enumerate(('a', 'b0', 'b1')):
            score_row(rows, 'P4', w, 'width ' + x, F(pi['Xn_widths'][i]), None if pi['XK_widths'] is None else F(pi['XK_widths'][i]), *iv['P4'])
        score_row(rows, 'P5', w, 'width a', F(pi['Xn_widths'][0]), F(pi['X_widths'][0]), *iv['P5'])
        for pid, f in (('P6', 'A'), ('P7', 'Phi')):
            dom = s['fieldsummary'][f]['dominant_width']
            prev = None if previous is None else F(previous[w][f]['bound_exact'])
            score_row(rows, pid, w, f + ' bound', F(s['fieldsummary'][f]['bound_exact']), prev, *iv[pid], extra=dom == 'STATE_RADIUS',
                      note='dominant ' + dom)
        for prep in ('D_prime', 'K'):
            for q in QUANTITIES:
                full = F(Q[prep]['FULL'][q])
                ok = full >= PRE_FLOOR
                rf = F(Q[prep]['F'][q]) / full if ok else None
                rd = F(Q[prep]['D'][q]) / full if ok else None
                good = ok and rf <= Fraction(PRE['P8']['rho_F_max']) and rd >= Fraction(PRE['P8']['rho_D_min'])
                rows.append({'id': 'P8', 'case': w, 'quantity': f'{prep}.{q}', 'rho_F': None if rf is None else str(rf),
                             'rho_D': None if rd is None else str(rd), 'outcome': 'CONFIRMED' if good else 'REFUTED'})
    rows.append({'id': 'P9', 'case': None, 'quantity': 'label', 'value': label, 'expected': PRE['P9']['label'],
                 'outcome': 'CONFIRMED' if label == PRE['P9']['label'] else 'REFUTED'})
    refuted = [f"{r['id']}.{r['case']}.{r['quantity']}" for r in rows if r['outcome'] != 'CONFIRMED']
    return {'scored': True, 'outcome': 'NEAR_NULL_CONFIRMED' if not refuted else 'NEAR_NULL_REFUTED', 'rows': rows, 'refuted': refuted,
            'rows_total': len(rows), 'rows_confirmed': len(rows) - len(refuted)}


def assemble(out, cases, phases, D_prime, guard, previous=None):
    out = Path(out)
    jobs = [(f'phase-{w}-{n}', 'PHASE.json') for w in cases for n in phases] + [(f'material-{w}', 'SUMMARY.json') for w in cases]
    g = []
    controls_failed = {j: read(out / j / 'CONTROL_FAILED.json') for j, _ in jobs if (out / j / 'CONTROL_FAILED.json').exists()}
    result = {'guard': guard, 'utc': now(), 'D_prime': [str(v) for v in D_prime], 'outcomes_opened': not controls_failed,
              'deferred': ['gauge completion q*', 'conformal lapse', 'coordinate length X*', 'inverse map and node positions',
                           'node-level field bounds'], 'note': 'Provisional until the independent verifier accepts it.'}
    if controls_failed:
        for job, rec in controls_failed.items():
            if rec['guard'] != guard:
                raise RuntimeError('Stale control record ' + job)
            control_gates(g, job, rec['controls'])
        gate(g, 'T0.no_control_failure', 'T', False, sorted(controls_failed))
        cls = classify(g, 'TECHNICAL_INCOMPLETE')
        result.update({'classification_provisional': cls, 'gates': g, 'gates_passed': sum(r['pass'] for r in g), 'gates_total': len(g),
                       'control_failures': sorted(controls_failed), 'control_records': {j: sha(out / j / 'CONTROL_FAILED.json') for j in controls_failed},
                       'note': 'A control failed: outcome records were not opened; the coordinator decides.'})
        atomic(out / 'PRODUCER_RESULT.json', result, True)
        write_side_records(out, result, {}, cases, previous)
        return result
    recs, inconsistent, summaries = {}, {}, {}
    for job, name in jobs:
        d = out / job
        failed = (d / 'FAILURE.json').exists()
        present = (d / name).exists()
        if job.startswith('material-') and (d / 'ROOT_INCONSISTENT.json').exists():
            rec = read(d / 'ROOT_INCONSISTENT.json')
            if rec['guard'] != guard:
                raise RuntimeError('Stale root record ' + job)
            inconsistent[job[len('material-'):]] = rec
            gate(g, f'T1.{job}.terminal_record', 'T', not failed)
            continue
        gate(g, f'T1.{job}.terminal_record', 'T', present and not failed)
        if not present:
            continue
        rec = read(d / name)
        if rec['guard'] != guard:
            raise RuntimeError('Stale record ' + job)
        if name == 'SUMMARY.json':
            if rec['arrays']['sha256'] != sha(d / 'CELLS.f64'):
                raise RuntimeError('Altered cell array ' + job)
            summaries[job[len('material-'):]] = rec
        recs[job] = rec
    for job, rec in recs.items():
        control_gates(g, job, rec['stage_a_controls'])
    prints = [rec['fingerprints'] for rec in recs.values()]
    ctl = [json.dumps(rec['stage_a_controls'], sort_keys=True) for rec in recs.values()]
    gate(g, 'R1.fingerprints_and_control_records_identical_across_jobs', 'R',
         all(f == prints[0] for f in prints) and len(set(ctl)) <= 1, len(prints))
    D1, D2 = (str(v) for v in D_prime)
    for w in cases:
        for n in phases:
            rec = recs.get(f'phase-{w}-{n}')
            if rec is not None:
                gate(g, f'B1.{w}.{n}.cover_equals_D_prime', 'P', rec['cover_equals_D_prime'] and rec['cover'] == [[D1, D2]])
    for w in cases:
        gate(g, f'K1.{w}.krawczyk_image_meets_box', 'K', w not in inconsistent)
        s = summaries.get(w)
        if s is None:
            continue
        X = [(Fraction(a), Fraction(b)) for a, b in s['krawczyk']['X']]
        Xn = [(Fraction(a), Fraction(b)) for a, b in s['krawczyk']['new_box']]
        gate(g, f'K2.{w}.new_box_inside_old', 'K', all(a <= na <= nb <= b for (a, b), (na, nb) in zip(X, Xn)))
        gate(g, f'B2.{w}.closure', 'B', s['closure_violations'] == 0, s['closure_violations'])
        gate(g, f'B3.{w}.coverage_0_to_D2', 'B', s['coverage_gaps'] == 0 and bool(s['coverage_end_equals_D2']))
    complete = sorted(summaries) == sorted(cases)
    science = science_label(summaries) if complete else 'TECHNICAL_INCOMPLETE'
    cls = classify(g, science)
    result.update({'classification_provisional': cls, 'science_label_if_gates_pass': science, 'gates': g,
                   'gates_passed': sum(r['pass'] for r in g), 'gates_total': len(g), 'root_inconsistent_cases': sorted(inconsistent),
                   'records': {job: sha(out / job / name) for job, name in jobs if (out / job / name).exists()}})
    if inconsistent:
        result['root_inconsistent_records'] = {w: sha(out / f'material-{w}' / 'ROOT_INCONSISTENT.json') for w in inconsistent}
    if complete:
        result['bounds'] = {w: {f: {k: fs[k] for k in ('bound', 'bound_exact', 'dominant_width', 'shares', 'argmax_cell',
                                                       'argmax_components', 'argmax_state_split')}
                                for f, fs in s['fieldsummary'].items()} for w, s in summaries.items()}
        result['krawczyk'] = {w: {k: s['krawczyk'][k] for k in ('old_widths', 'new_widths', 'width_ratios', 'strict_inclusion_in_X',
                                                                'weighted_row_norms', 'G_center_radius', 'new_box')}
                              for w, s in summaries.items()}
        result['diagnostics'] = {w: s['diagnostics'] for w, s in summaries.items()}
        result['walls'] = {w: s['walls'] for w, s in summaries.items()}
        result['proper_separation'] = {w: s['proper_separation'] for w, s in summaries.items()}
        if previous is not None:
            result['previous_run_bounds'] = {w: {f: previous[w][f]['bound'] for f in ('A', 'ell', 'Phi')} for w in cases}
            result['bound_ratio_new_over_previous'] = {
                w: {f: float(Fraction(summaries[w]['fieldsummary'][f]['bound_exact']) / Fraction(previous[w][f]['bound_exact']))
                    for f in ('A', 'ell', 'Phi')} for w in cases}
    atomic(out / 'PRODUCER_RESULT.json', result, True)
    write_side_records(out, result, summaries, cases, previous)
    return result


def write_side_records(out, result, summaries, cases, previous):
    """Prediction and attribution: separate records, outside the validity order, assigned only when every R, P, T,
    K and B gate passes."""
    errors = {w: s.get('side_error') for w, s in summaries.items() if s.get('side_error') is not None}
    if not result['classification_provisional'].startswith('REPREPARED__'):
        reason = 'a validity gate failed: ' + result['classification_provisional']
        attribution = {'assigned': False, 'label': None, 'reason': reason}
        prediction = {'scored': False, 'outcome': None, 'reason': reason}
    elif errors:
        attribution = {'assigned': False, 'label': None, 'reason': 'side computation error', 'errors': errors}
        prediction = {'scored': False, 'outcome': None, 'reason': 'side computation error', 'errors': errors}
    else:
        try:
            attribution = attribution_record(summaries, cases)
        except Exception as error:
            attribution = {'assigned': False, 'label': None, 'reason': 'side computation error',
                           'errors': {'assembly': {'type': type(error).__name__, 'message': str(error)}}}
        try:
            prediction = prediction_record(summaries, cases, result['classification_provisional'], previous)
        except Exception as error:
            prediction = {'scored': False, 'outcome': None, 'reason': 'side computation error',
                          'errors': {'assembly': {'type': type(error).__name__, 'message': str(error)}}}
    for name, rec in (('ATTRIBUTION.json', attribution), ('PREDICTION.json', prediction)):
        try:
            atomic(out / name, rec | {'guard': result['guard'], 'utc': now(), 'producer_result_sha256': sha(out / 'PRODUCER_RESULT.json')}, True)
        except Exception as error:
            print(json.dumps({'side_record_write_error': name, 'type': type(error).__name__, 'message': str(error)}), flush=True)


def previous_bounds():
    run3 = read(RUN3 / 'outputs' / 'PRODUCER_RESULT.json')
    out = {}
    for w in CONFIG['cases']:
        s = read(RUN3 / 'outputs' / w / 'SUMMARY.json')
        out[w] = {f: {'bound': run3['bounds'][w][f]['bound'], 'bound_exact': s['fieldsummary'][f]['bound_exact']} for f in ('A', 'ell', 'Phi')}
    return out


def main():
    guard, _ = freeze_guard()
    D_prime = tuple(Fraction(v) for v in CONFIG['D_prime'])
    result = assemble(OUT, CONFIG['cases'], CONFIG['phases'], D_prime, guard, previous_bounds())
    side = {n: (read(OUT / f'{n}.json') if (OUT / f'{n}.json').exists() else {}) for n in ('ATTRIBUTION', 'PREDICTION')}
    print(json.dumps({'classification_provisional': result['classification_provisional'],
                      'gates': [result['gates_passed'], result['gates_total']], 'outcomes_opened': result['outcomes_opened'],
                      'attribution': side['ATTRIBUTION'].get('label'), 'prediction': side['PREDICTION'].get('outcome')}), flush=True)


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'run':
        raise SystemExit('usage: assemble4.py run')
    main()
