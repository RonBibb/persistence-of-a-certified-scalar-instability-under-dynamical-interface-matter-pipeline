"""Pre-freeze controls on manufactured inputs only. No real outcome is computed here.

Builds a synthetic native packet with the real file schema (128 cells, degree 28, pieces that
disagree at high order like Taylor-integrator pieces), synthetic saved grids made by the
byte-identical reference producer, and synthetic receipts. Runs the producer twice (direct,
and interrupted then resumed in a fresh process), runs the independent verifier, and checks
unit controls of every decision primitive.
    python -B <run>/code/preflight.py all
"""
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (RUN, CONFIG, GATE, now, sha, read, atomic, plain, exact_mpf, encode_mpf, decode_pair,  # noqa: E402
                    exact_decimal, check_environment, limit_address_space, source_hashes, runtime_fingerprint,
                    freeze_guard)
import representation as rep  # noqa: E402
import replay  # noqa: E402
import verify as ver  # noqa: E402

LEVEL = 'fix'
CELLS = 128
DEG = 28
DEGREES = [8, 12]
ETA = Fraction(1, 10 ** 30)


def dec(x, digits=90):
    x = Fraction(x)
    if x == 0:
        return '0.0'
    with mp.workdps(digits + 25):
        return mp.nstr(mp.mpf(x.numerator) / x.denominator, digits)


def shift_exact(coeffs, a, n):
    return [sum((coeffs[j] * math.comb(j, i) * a ** (j - i) for j in range(i, len(coeffs))), Fraction(0)) for i in range(n + 1)]


def choose_h():
    """A 90-digit cell width whose floating knot rule switches pieces, differently at 80 and 100 digits."""
    for trial in range(400):
        digits = str(pow(7, 301 + trial))[:88]
        D = '1.99' + digits
        h = dec(Fraction(D) / CELLS)
        t80 = ver.floor_table(h, ver.mp_prec(80), CELLS)
        t100 = ver.floor_table(h, ver.mp_prec(100), CELLS)
        canon = list(range(CELLS))
        if t80 != canon and t100 != canon and t80 != t100:
            return D, h, t80, t100, trial
    raise RuntimeError('No fixture width with precision-dependent knots')


def polynomials(eps):
    F = Fraction
    W = [F(0), F(-1), F(1, 50)]
    H = [F(-1), F(1, 25)]
    Phi = [F(1, 10), F(1, 20), F(-1, 100)]
    T = [F(0), F(1, 50)]
    E = [F(1), F(1), F(1, 2)]
    psi = [F(1), F(0), F(-1, 5)]
    f = [F(0), F(3, 10)]
    g = [F(3, 10)]
    A = [W[0] + eps * psi[0], W[1] + eps * psi[1], W[2] + eps * psi[2], F(1, 1000)]
    return [W, H, Phi, T, E, psi, f, g], A


def piece_rows(poly, s_i, perturb, i):
    rows = shift_exact(poly, s_i, DEG)
    if perturb:
        rows[DEG] += ETA * (-1) ** i * (1 + Fraction(i, 100))
        rows[DEG - 1] += ETA * (-1) ** (i + 1) / 2
    return rows


def build_fixture(base):
    if base.exists():
        shutil.rmtree(base)
    native = base / 'native'
    (native / 'results' / LEVEL).mkdir(parents=True)
    D, h, t80, t100, trial = choose_h()
    hq = Fraction(h)
    model = {'gamma': '20', 'lambda_a': '6', 'lambda_b': '-6', 'm2': '2/5', 'v0': '1/10', 'v1': '9/100'}
    (native / 'BINDINGS.json').write_text(json.dumps({'model_exact': model}) + '\n')
    seed_polys, _ = polynomials(Fraction(0))
    segments = []
    for i in range(CELLS):
        s_i = i * hq
        segments.append([[dec(c) for c in piece_rows(p, s_i, r == 5, i)] for r, p in enumerate(seed_polys)])
    seed = {'a': '0.099', 'D': D, 'k': '0.0003', 'mu': '-0.0013', 'degree': DEG, 'cells': CELLS, 'h': h,
            'segments': segments, 'end': ['0.0'] * 8}
    (native / 'results' / LEVEL / 'SEED.json').write_text(json.dumps(seed) + '\n')
    eps_text = {0: '0.0', 3: '0.000005', 4: '-0.000005'}
    centers = {}
    for case, et in eps_text.items():
        eps = Fraction(et)
        _, Apoly = polynomials(eps)
        segs = []
        for i in range(CELLS):
            row0 = [dec(c) for c in piece_rows(Apoly, i * hq, True, i + case)]
            segs.append([row0] + [['0.0'] * (DEG + 1) for _ in range(4)])
        A0 = eps + Fraction(3, 10 ** 9)
        fifth = ['0.0001', '-0.0002']
        dense = {'epsilon': et, 'A0': dec(A0), 'correction': [dec(Fraction(j, 10 ** 7)) for j in range(12)],
                 'endpoints': [0, 0], 'segments': segs, 'end': ['0.0'] * 5, 'history': [], 'passed_shooting': True,
                 'fifth_jet_coefficients': fifth}
        (native / 'results' / LEVEL / f'case_{case}.dense.json').write_text(json.dumps(dense) + '\n')
        centers[case] = [Fraction(dense['A0']) - eps] + [Fraction(x) for x in fifth]
    spatial = base / 'spatial'
    inputs = spatial / 'inputs'
    inputs.mkdir(parents=True)
    rep.bind_parent(native)
    rows = []
    for case in eps_text:
        for N in DEGREES:
            mp.mp.dps = 80
            d = rep.reference.Dense(LEVEL, case)
            d.qualify_gauge()
            d.make_map()
            xi, w, _, _ = rep.reference.lgl(N, d.X)
            s = [d.invert((z + 1) * d.X / 2) for z in xi]
            fields = [d.jets(z, 0) for z in s]
            U = [mp.matrix([r[j][0] for r in fields]) for j in range(3)]
            seeds = [d.seed_values(z) for z in s]
            data = {'N': N, 'dps': 80, 'X': d.X, 'xi': xi, 'x': [(z + 1) * d.X / 2 for z in xi], 's': s, 'weights': w,
                    'A': list(U[0]), 'B': list(U[1]), 'Phi': list(U[2]), 'velocities': [[mp.mpf(0)] * (N + 1) for _ in range(3)],
                    'seed_fields': seeds, 'ell': [r[3][0] for r in fields], 'gauge_coefficients': d.q, 'k': d.k,
                    'action': d.par, 'coordinate_knots': d.xknots, 'coordinate_integral_polynomials': d.xpoly,
                    'Cauchy_constants': {'K_ij': 0, 'Pi': 0, 'collapse_scalar': 0, 'collapse_momentum': 0, 'shift': 0},
                    'fields': ['A', 'B', 'Phi']}
            name = f'{LEVEL}_case{case}_N{N}_p80'
            rep.reference.save(inputs / (name + '.grid.json'), data)
            gp = inputs / (name + '.grid.json')
            (inputs / (name + '.audit.json')).write_text(json.dumps({'grid_sha256': sha(gp), 'all_velocities_exactly_zero': True}) + '\n')
            (inputs / (name + '.json')).write_text(json.dumps({'N': N, 'case': case, 'synthetic': True}) + '\n')
            for suffix in ('.json', '.grid.json', '.audit.json'):
                rows.append({'path': f'inputs/{name}{suffix}', 'sha256': sha(inputs / (name + suffix))})
    checks = [{'check': f'{LEVEL}_case{c}_N{N}_p80 {family}', 'pass': True} for c in eps_text for N in DEGREES
              for family in replay.FAMILIES + ('synthetic',)]
    (spatial / 'GRID_ADMISSION.json').write_text(json.dumps({'all_passed': True, 'inputs': rows, 'checks': checks}) + '\n')
    (spatial / 'VERIFICATION.json').write_text(json.dumps({'record_integrity_valid': True, 'complete_signed_cohort_qualified': True}) + '\n')
    (base / 'admission').mkdir()
    (base / 'admission' / 'VERIFICATION.json').write_text(json.dumps({'all_passed': True}) + '\n')
    identity = {}
    for name, case, target in (('positive', 3, '1/200000'), ('negative', 4, '-1/200000')):
        folder = base / 'finite' / 'output' / name
        folder.mkdir(parents=True)
        (folder / 'RESULT.json').write_text(json.dumps({'pass': True, 'epsilon': target,
                                                        'center': [str(c) for c in centers[case]]}) + '\n')
        identity[name] = {'pass': True, 'old_result_sha256': sha(folder / 'RESULT.json'),
                          'translated_root_image': [{'exact': [str(c - Fraction(1, 10 ** 7)), str(c + Fraction(1, 10 ** 7))]}
                                                    for c in centers[case]]}
    (base / 'connected').mkdir()
    (base / 'connected' / 'INDEPENDENT_AUDIT.json').write_text(json.dumps({'endpoint_identity': identity}) + '\n')
    return {'D': D, 'h': h, 'width_trial': trial, 't80_non_canonical': [i for i, p in enumerate(t80) if p != i],
            't100_non_canonical': [i for i, p in enumerate(t100) if p != i]}


def context(base, out_name):
    return {'native': str(base / 'native'), 'grid_dir': str(base / 'spatial' / 'inputs'), 'spatial_root': str(base / 'spatial'),
            'admission_verification': str(base / 'admission' / 'VERIFICATION.json'), 'finite': str(base / 'finite'),
            'connected_audit': str(base / 'connected' / 'INDEPENDENT_AUDIT.json'), 'identity': None,
            'out': str(base / out_name), 'verification': str(base / (out_name + '-verification')),
            'status': str(base / (out_name + '-status.json')), 'level': LEVEL, 'cases': [0, 3, 4], 'degrees': DEGREES,
            'dps': [80, 100], 'old_rule_dps': 80, 'freeze': None, 'fixture': True, 'guard': 'fixture-guard'}


def run_child(args, expect=0):
    started = time.monotonic()
    proc = subprocess.run([sys.executable, '-B'] + args, capture_output=True, text=True)
    if proc.returncode != expect:
        raise RuntimeError(f'Child {args} exited {proc.returncode}: {proc.stderr[-3000:]}')
    return {'seconds': time.monotonic() - started, 'stdout_tail': proc.stdout[-1500:], 'returncode': proc.returncode}


def strip_volatile(record):
    if isinstance(record, dict):
        return {k: strip_volatile(v) for k, v in record.items() if k not in ('utc', 'seconds', 'cpu_seconds')}
    if isinstance(record, list):
        return [strip_volatile(v) for v in record]
    return record


def unit_controls(base):
    checks = {}
    rng = random.Random(20261006)
    # Exact encodings round-trip.
    mp.mp.dps = 100
    values = [mp.mpf(0), mp.mpf('-3.25e-77'), mp.mpf(2) ** 300, -mp.mpf(1) / 3, mp.pi]
    checks['exact_encoding_roundtrip'] = all(decode_pair(encode_mpf(v)) == exact_mpf(v) for v in values)
    # Knot-rule emulation agrees with mpmath for products and quotients at both precisions.
    agree = True
    for dps in (80, 100):
        with mp.workdps(dps):
            for _ in range(300):
                text = '0.' + ''.join(rng.choice('0123456789') for _ in range(rng.randint(5, 95))) + '1'
                h = mp.mpf(text)
                hq = ver.rne(Fraction(text), ver.mp_prec(dps))
                if exact_mpf(h) != hq:
                    agree = False
                i = rng.randint(1, 255)
                s = i * h
                if exact_mpf(s) != ver.rne(i * hq, ver.mp_prec(dps)):
                    agree = False
                q = s / h
                if exact_mpf(q) != ver.rne(ver.rne(i * hq, ver.mp_prec(dps)) / hq, ver.mp_prec(dps)):
                    agree = False
                if int(mp.floor(q)) != math.floor(ver.rne(ver.rne(i * hq, ver.mp_prec(dps)) / hq, ver.mp_prec(dps))):
                    agree = False
            prec = mp.mp.prec
            tie = Fraction(2 ** prec + 1, 2 ** prec)
            if exact_mpf(mp.mpf(tie.numerator) / tie.denominator) != ver.rne(tie, prec):
                agree = False
            tie2 = Fraction(2 ** (prec + 1) + 3, 2)
            if exact_mpf(mp.mpf(tie2.numerator) / 2) != ver.rne(tie2, prec):
                agree = False
            if ver.mp_prec(dps) != mp.mp.prec:
                agree = False
    checks['knot_rule_emulation_matches_mpmath'] = agree
    # Whole-cell bounds dominate sampled differences; Jacobian lower bound is below sampled minima.
    w = Fraction(rng.randint(10 ** 9, 2 * 10 ** 9), 10 ** 11)
    rows_a = [[Fraction(rng.randint(-10 ** 6, 10 ** 6), 10 ** 6) for _ in range(30)] for _ in range(3)]
    rows_a = [[Fraction(0), Fraction(1)] + r[2:] for r in rows_a]
    rows_b = [[c + Fraction(rng.randint(-10 ** 6, 10 ** 6), 10 ** 6) * Fraction(1, 10 ** (3 * j + 5)) for j, c in enumerate(r)] for r in rows_a]
    knots_a = [Fraction(k) for k in range(4)]
    knots_b = [k + Fraction(1, 10 ** 70) for k in knots_a]
    widths = [w] * 3
    cmp = replay.compare_maps((rows_a, knots_a, Fraction(3)), (rows_b, knots_b, Fraction(3)), widths)
    sampled = Fraction(0)
    sampled_j = Fraction(0)
    for i in range(3):
        for t in range(41):
            z = w * t / 40
            da = sum(c * z ** j for j, c in enumerate(rows_a[i])) - sum(c * z ** j for j, c in enumerate(rows_b[i])) + knots_a[i] - knots_b[i]
            dj = sum(j * c * z ** (j - 1) for j, c in enumerate(rows_a[i]) if j) - sum(j * c * z ** (j - 1) for j, c in enumerate(rows_b[i]) if j)
            sampled = max(sampled, abs(da))
            sampled_j = max(sampled_j, abs(dj))
    checks['triangle_bounds_dominate_samples'] = (float(cmp['V_max']) >= float(sampled) * (1 - 1e-12)
                                                  and float(cmp['J_max']) >= float(sampled_j) * (1 - 1e-12) and sampled > 0)
    ac = ver.arb_compare(rows_a, knots_a, rows_b, knots_b, widths)
    checks['arb_sup_enclosure_dominates_samples'] = (ac['V_sup_enclosure'] >= sampled and ac['J_sup_enclosure'] >= sampled_j
                                                     and abs(float(ac['V_triangle']) - float(cmp['V_max'])) <= 1e-6 * float(cmp['V_max'])
                                                     and abs(float(ac['J_triangle']) - float(cmp['J_max'])) <= 1e-6 * float(cmp['J_max']))
    lower = replay.jacobian_lower(rows_a, widths)
    sampled_min = min(sum(j * c * (w * t / 40) ** (j - 1) for j, c in enumerate(r) if j) for r in rows_a for t in range(41))
    checks['jacobian_lower_bounds_samples'] = lower <= sampled_min and ver.jac_lower(rows_a, widths) <= sampled_min
    # Negative controls for gates: a perturbed coefficient fails raw; a large perturbation fails V.
    bad = [list(r) for r in rows_a]
    bad[1][3] += Fraction(1, 10 ** 45)
    c1 = replay.compare_maps((rows_a, knots_a, Fraction(3)), (bad, knots_a, Fraction(3)), widths)
    bad2 = [list(r) for r in rows_a]
    bad2[2][1] += Fraction(1, 10 ** 30)
    c2 = replay.compare_maps((rows_a, knots_a, Fraction(3)), (bad2, knots_a, Fraction(3)), widths)
    checks['raw_gate_rejects_1e-45_coefficient_change'] = (not c1['raw_within_gate']) and c1['V_within_gate']
    checks['cell_gate_rejects_1e-30_value_change'] = (not c2['V_within_gate']) and (not c2['J_within_gate'])
    # Immutable writes refuse overwrite and ignore uncommitted fixtures.
    target = base / 'immutable-test.json'
    atomic(target, {'a': 1}, True)
    refused = False
    try:
        atomic(target, {'a': 2}, True)
    except RuntimeError:
        refused = True
    (base / 'immutable-test.json.uncommitted-orphan').write_text('{"a": 99}')
    checks['immutable_write_refuses_overwrite_and_orphans_ignored'] = refused and read(target) == {'a': 1}
    # numpy scalars are cast or rejected explicitly.
    import numpy as np
    checks['plain_casts_numpy_bool'] = plain({'x': np.bool_(True)}) == {'x': True}
    checks['plain_numpy_float_serializes_as_float'] = json.dumps(plain({'x': np.float64(1.5)})) == '{"x": 1.5}'
    try:
        plain({'x': float('nan')})
        checks['plain_rejects_nan'] = False
    except ArithmeticError:
        checks['plain_rejects_nan'] = True
    # Ambiguity detection at a shared knot with dual evaluation.
    rep.bind_parent(base / 'native')
    mp.mp.dps = 100
    d = rep.ExplicitDense(LEVEL, 3)
    d.qualify_gauge()
    d.make_map_explicit(rep.canonical_table(d.cells))
    k = 7
    near = k * d.h - mp.mpf(10) ** -60
    piece, ambiguous, margin, j = d.piece_of(near)
    fields, base_rows, info = d.fields_explicit(near, d.q)
    far = k * d.h + d.h / 3
    piece_far, amb_far, _, _ = d.piece_of(far)
    x_near = d.xknots[k] + mp.mpf(10) ** -60
    s_inv, inv_info = d.invert_explicit(x_near)
    checks['ambiguity_flags_and_dual_evaluation'] = (ambiguous and piece == k and info['alternate']['piece'] == k - 1
                                                     and not amb_far and piece_far == k and inv_info['ambiguous']
                                                     and inv_info['cell'] == k and inv_info['alternate']['cell'] == k - 1
                                                     and abs(inv_info['alternate']['s'] - s_inv) < mp.mpf('1e-50'))
    # Freeze guard rejects changed configuration and changed input on a fixture binding.
    good = {'config': CONFIG, 'sources': {'x': '1'}, 'inputs': {str(target): sha(target)}, 'runtime': {'r': 1}}
    gpath = base / 'FREEZE-fixture.json'
    gpath.write_text(json.dumps(good))
    accepted = freeze_guard(gpath, sources={'x': '1'}, runtime={'r': 1})[0] == sha(gpath)
    rejections = []
    for mutate in ('config', 'input', 'source', 'runtime'):
        bad_bind = json.loads(json.dumps(good))
        if mutate == 'config':
            bad_bind['config'] = dict(CONFIG, gate_absolute='1e-40')
        elif mutate == 'input':
            bad_bind['inputs'] = {str(target): '0' * 64}
        elif mutate == 'source':
            bad_bind['sources'] = {'x': '2'}
        else:
            bad_bind['runtime'] = {'r': 2}
        bpath = base / f'FREEZE-bad-{mutate}.json'
        bpath.write_text(json.dumps(bad_bind))
        try:
            freeze_guard(bpath, sources={'x': '1'}, runtime={'r': 1})
            rejections.append(False)
        except RuntimeError:
            rejections.append(True)
    checks['freeze_guard_accepts_valid_and_rejects_four_mutations'] = accepted and all(rejections)
    return checks


def fixture_expectations(base, info):
    out = base / 'outA'
    prod = read(out / 'PRODUCER_RESULT.json')
    verification = read(base / 'outA-verification' / 'VERIFICATION.json')
    failed = set(prod['failed_gates'])
    expected_failed = {f'E1.c{c}.p{d}.wall_rows_inherited_thresholds' for c in (0, 3, 4) for d in (80, 100)}
    gates = {r['id']: r for r in prod['gates']}
    return {
        'fixture_has_precision_dependent_knots': bool(info['t80_non_canonical']) and bool(info['t100_non_canonical']),
        'producer_tables_match_fixture_emulation': prod['selection_tables']['old80_non_canonical_cells'] == info['t80_non_canonical'],
        'only_synthetic_original_equation_rows_fail': failed <= expected_failed,
        'synthetic_rows_detected_as_non_solutions': any(not gates[k]['pass'] for k in expected_failed if k in gates),
        'old_map_reproduced_at_both_precisions': all(r['pass'] for k, r in gates.items() if k.startswith(('R1.', 'R2.', 'R3.', 'R4.'))),
        'canonical_like_representation_passes': all(r['pass'] for k, r in gates.items() if k.startswith(('C1.', 'C2.', 'C3.', 'Cx.'))),
        'unlike_whole_cell_gates_pass': all(r['pass'] for k, r in gates.items() if k.startswith(('U1.', 'U2.', 'U3.'))),
        'historical_type_failure_reproduced': gates['H1.c0.p100.N8.historical_failure_reproduced']['pass'],
        'port_controls_pass': all(r['pass'] for k, r in gates.items() if k.startswith(('I1.', 'I2.', 'I3.', 'I4.'))),
        'root_bounds_pass': all(r['pass'] for k, r in gates.items() if k.startswith('G1.')),
        'inherited_receipts_pass_with_required_families': gates['E3.inherited_original_equation_receipts']['pass'],
        'classification_is_E_failure': prod['classification_provisional'] == 'REPRESENTATION_ADMISSION_FAILED_E',
        'verifier_resolved_and_confirms': verification['resolved'] and verification['producer_confirmed']
        and verification['classification'] == prod['classification_provisional'],
        'verifier_integrity_checks_all_pass': all(r['pass'] for r in verification['integrity_checks']),
        'verifier_only_gates_all_pass': all(r['pass'] for r in verification['verifier_only_gates']),
        'shared_plus_producer_only_equals_producer_total': verification['shared_gates_total'] + len(verification['producer_only_gates']) == prod['gates_total'],
        'verifier_shared_gate_count': verification['shared_gates_total'], 'producer_gate_count': prod['gates_total']}


def tampered_fixture(base, me):
    """Negative path: one saved coefficient moved by 1e-45 at power 5 (raw failure, whole-cell pass)."""
    tamper = base / 'spatial_tamper'
    shutil.copytree(base / 'spatial', tamper)
    name = f'{LEVEL}_case3_N8_p80'
    gp = tamper / 'inputs' / (name + '.grid.json')
    os.chmod(gp, 0o644)
    grid = read(gp)
    old = Fraction(grid['coordinate_integral_polynomials'][5][5])
    grid['coordinate_integral_polynomials'][5][5] = dec(old + Fraction(1, 10 ** 45), 80)
    gp.write_text(json.dumps(grid, indent=2) + '\n')
    ap = tamper / 'inputs' / (name + '.audit.json')
    os.chmod(ap, 0o644)
    ap.write_text(json.dumps({'grid_sha256': sha(gp), 'all_velocities_exactly_zero': True}) + '\n')
    adm = read(tamper / 'GRID_ADMISSION.json')
    for row in adm['inputs']:
        row['sha256'] = sha(tamper / row['path'])
    os.chmod(tamper / 'GRID_ADMISSION.json', 0o644)
    (tamper / 'GRID_ADMISSION.json').write_text(json.dumps(adm) + '\n')
    cT = dict(context(base, 'outT'), grid_dir=str(tamper / 'inputs'), spatial_root=str(tamper))
    (base / 'ctxT.json').write_text(json.dumps(cT))
    run_child([me, 'producer', str(base / 'ctxT.json')])
    run_child([str(Path(me).parent / 'verify.py'), 'fixture', str(base / 'ctxT.json')])
    prod = read(base / 'outT' / 'PRODUCER_RESULT.json')
    ver_t = read(base / 'outT-verification' / 'VERIFICATION.json')
    allowed = {f'E1.c{c}.p{d}.wall_rows_inherited_thresholds' for c in (0, 3, 4) for d in (80, 100)} | {
        'R1.c3.p80.N8.raw_coefficients', 'R1.c3.p100.N8.raw_coefficients', 'S4.c3.saved_map_identical_across_degrees'}
    gates = {r['id']: r for r in prod['gates']}
    return {'tampered_classification': prod['classification_provisional'],
            'tamper_classified_as_saved_map_not_reproduced': prod['classification_provisional'] == 'SAVED_MAP_NOT_REPRODUCED',
            'tamper_failures_are_exactly_expected': set(prod['failed_gates']) == allowed,
            'tamper_whole_cell_gates_still_pass': all(gates[k]['pass'] for k in gates if k.startswith(('U1.c3', 'U2.c3'))),
            'tamper_verifier_resolved_and_confirms': ver_t['resolved'] and ver_t['producer_confirmed'],
            'tamper_verifier_only_raw_reference_fails': [r['id'] for r in ver_t['verifier_only_gates'] if not r['pass']] == ['XR2.c3.N8.saved_map_equals_exact_old80_reference']}


def disagreement_fixture(base, me):
    """Negative path: a producer gate flag flipped after publication must leave the result unresolved."""
    outD = base / 'outD'
    shutil.copytree(base / 'outA', outD)
    path = outD / 'PRODUCER_RESULT.json'
    os.chmod(path, 0o644)
    result = read(path)
    for row in result['gates']:
        if row['id'] == 'R1.c0.p80.N8.raw_coefficients':
            row['pass'] = False
    path.write_text(json.dumps(result) + '\n')
    cD = context(base, 'outD')
    (base / 'ctxD.json').write_text(json.dumps(cD))
    run_child([str(Path(me).parent / 'verify.py'), 'fixture', str(base / 'ctxD.json')])
    ver_d = read(base / 'outD-verification' / 'VERIFICATION.json')
    return {'disagreement_unresolved': ver_d['classification'] == 'UNRESOLVED_VERIFICATION' and not ver_d['resolved'],
            'disagreement_names_the_gate': 'VAGREE.shared_gate_flags_agree' in ver_d['failed_integrity_checks']}


def all_controls():
    check_environment()
    limits = limit_address_space()
    from flint import ctx
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    root = RUN / 'preflight' / stamp
    base = root / 'fixture'
    started = time.monotonic()
    info = build_fixture(base)
    build_seconds = time.monotonic() - started
    units = unit_controls(base)
    cA = context(base, 'outA')
    cB = context(base, 'outB')
    (base / 'ctxA.json').write_text(json.dumps(cA))
    cB_stop = dict(cB, stop_after_records=2)
    (base / 'ctxB-stop.json').write_text(json.dumps(cB_stop))
    (base / 'ctxB.json').write_text(json.dumps(cB))
    me = str(Path(__file__).resolve())
    runs = {'direct': run_child([me, 'producer', str(base / 'ctxA.json')]),
            'interrupted': run_child([me, 'producer', str(base / 'ctxB-stop.json')], expect=17),
            'resumed': run_child([me, 'producer', str(base / 'ctxB.json')])}
    maps_equal = all(sha(p) == sha(base / 'outB' / 'maps' / p.name) for p in sorted((base / 'outA' / 'maps').glob('*.json')))
    records_equal = all(strip_volatile(read(p)) == strip_volatile(read(base / 'outB' / p.name))
                        for p in sorted((base / 'outA').glob('case*_p*.json')))
    gates_equal = read(base / 'outA' / 'PRODUCER_RESULT.json')['gates'] == read(base / 'outB' / 'PRODUCER_RESULT.json')['gates']
    refused = run_child([me, 'producer', str(base / 'ctxA.json')], expect=1)
    runs['refuse_terminal_rerun'] = refused
    partial = base / 'outC'
    (partial / 'maps').mkdir(parents=True)
    (partial / 'maps' / 'case0_p80_canonical.json').write_text('{}')
    cC = context(base, 'outC')
    (base / 'ctxC.json').write_text(json.dumps(cC))
    runs['refuse_partial_maps'] = run_child([me, 'producer', str(base / 'ctxC.json')], expect=1)
    runs['verifier'] = run_child([str(Path(__file__).resolve().parent / 'verify.py'), 'fixture', str(base / 'ctxA.json')])
    expectations = fixture_expectations(base, info)
    negative = tampered_fixture(base, me) | disagreement_fixture(base, me)
    resume = {'interrupted_exit_17': runs['interrupted']['returncode'] == 17, 'map_files_bitwise_equal': maps_equal,
              'case_records_equal_except_timing': records_equal, 'gate_lists_equal': gates_equal,
              'terminal_rerun_refused': runs['refuse_terminal_rerun']['returncode'] == 1,
              'partial_maps_refused': runs['refuse_partial_maps']['returncode'] == 1}
    passed = (all(v for v in units.values()) and all(v for k, v in expectations.items() if isinstance(v, bool))
              and all(resume.values()) and all(v for k, v in negative.items() if isinstance(v, bool)))
    result = {'passed': passed, 'utc': now(), 'physical_outcomes': False, 'real_data_outcomes_computed': False,
              'fixture': info, 'fixture_build_seconds': build_seconds, 'unit_controls': units,
              'fixture_expectations': expectations, 'negative_paths': negative, 'fresh_process_resume': resume,
              'child_runs': {k: {kk: vv for kk, vv in v.items()} for k, v in runs.items()},
              'sources': source_hashes(), 'runtime': runtime_fingerprint(), 'config': CONFIG, 'address_space': limits,
              'seconds': time.monotonic() - started}
    atomic(root / 'PREFLIGHT.json', result, True)
    print(json.dumps({'preflight_passed': passed, 'path': str(root / 'PREFLIGHT.json'), 'units': units,
                      'expectations': expectations, 'negative_paths': negative, 'resume': resume,
                      'timing': {k: round(v['seconds'], 1) for k, v in runs.items()}}, indent=1), flush=True)
    return passed


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == 'producer':
        C = read(sys.argv[2])
        P = dict(C)
        from flint import ctx
        ctx.prec = CONFIG['arb_bits']
        ctx.threads = 1
        replay.execute(P, C['guard'])
    elif len(sys.argv) == 2 and sys.argv[1] == 'all':
        sys.exit(0 if all_controls() else 3)
    else:
        raise SystemExit('usage: preflight.py all')
