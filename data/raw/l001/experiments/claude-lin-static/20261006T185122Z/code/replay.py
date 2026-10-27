"""Producer: deterministic knot-selection replay of the six saved D1 conformal grids.

No time evolution, no physical IVP and no new evolution grid. Reads bound inputs only and
writes inside outputs/. Usage on Linux, from the Research root, through slot_run.sh:
    python -B <run>/code/replay.py run
The same execute() is dry-run on a synthetic fixture by preflight.py before the freeze.
"""
import json
import os
import signal
import sys
import time
import traceback
from fractions import Fraction
from pathlib import Path

import mpmath as mp

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (CONFIG, GATE, now, sha, read, atomic, exact_mpf, encode_mpf, decode_pair,  # noqa: E402
                    exact_decimal, check_environment, limit_address_space, capacity, freeze_guard,
                    real_paths)
import representation as rep  # noqa: E402

RULES = CONFIG['rules']
GATED_RULES = ('canonical', 'old80')
FAMILIES = ('Hamiltonian', 'momentum', 'strong wall order 0', 'strong wall order 2', 'strong wall order 4',
            'weak wall order 0', 'weak wall order 2', 'weak wall order 4', 'inverse map derivative')


def fmt(value, digits=25):
    """Decimal display of an exact rational or mpf; decisions never use this string."""
    if value is None:
        return None
    if not isinstance(value, Fraction):
        value = exact_mpf(value)
    if value == 0:
        return '0'
    with mp.workdps(digits + 30):
        return mp.nstr(mp.mpf(value.numerator) / value.denominator, digits)


def within(value):
    """Exact comparison with the absolute gate for an mpf or Fraction."""
    return (value if isinstance(value, Fraction) else exact_mpf(value)) <= GATE


def bitwise(a, b):
    return a._mpf_ == b._mpf_


def rows_bitwise(a, b):
    return len(a) == len(b) and all(bitwise(x, y) for x, y in zip(a, b))


def snapshot(d):
    return {'xpoly': [list(row) for row in d.xpoly], 'xknots': list(d.xknots), 'X': d.X,
            'offsets': list(d.offsets), 'table': list(d.table)}


def load_snapshot(d, snap):
    d.xpoly = [list(row) for row in snap['xpoly']]
    d.xknots = list(snap['xknots'])
    d.X = snap['X']
    d.offsets = list(snap['offsets'])
    d.table = list(snap['table'])


def map_bitwise(snap, ref):
    return (len(snap['xpoly']) == len(ref.xpoly)
            and all(rows_bitwise(a, b) for a, b in zip(snap['xpoly'], ref.xpoly))
            and rows_bitwise(snap['xknots'], ref.xknots) and bitwise(snap['X'], ref.X))


def widths_exact(seed):
    """Closed native cells: width h, except the last, which ends at the wall D."""
    h, D, cells = exact_decimal(seed['h']), exact_decimal(seed['D']), seed['cells']
    return [h] * (cells - 1) + [D - (cells - 1) * h]


def powers(w, n):
    out = [Fraction(1)]
    for _ in range(n):
        out.append(out[-1] * w)
    return out


def compare_maps(a, b, widths):
    """Exact rational raw and whole-cell comparison of two piecewise map representations.

    V_i = |dK_i| + sum_j |dc_ij| w_i^j bounds the represented map difference on the whole
    closed cell 0<=z<=w_i; J_i = sum_j j |dc_ij| w_i^(j-1) bounds the Jacobian difference.
    """
    rows_a, knots_a, X_a = a
    rows_b, knots_b, X_b = b
    if len(rows_a) != len(rows_b) or len(knots_a) != len(knots_b):
        raise RuntimeError('Map cell count mismatch')
    cache = {}
    raw, raw_at, raw_cells, V, J = Fraction(0), [None, None], [], [], []
    for i, (ra, rb) in enumerate(zip(rows_a, rows_b)):
        if len(ra) != len(rb):
            raise RuntimeError('Map polynomial dimension mismatch')
        diffs = [abs(x - y) for x, y in zip(ra, rb)]
        top = max(diffs)
        if top > raw:
            raw, raw_at = top, [i, diffs.index(top)]
        if top > GATE:
            raw_cells.append(i)
        w = widths[i]
        if w not in cache:
            cache[w] = powers(w, len(ra))
        pw = cache[w]
        V.append(abs(knots_a[i] - knots_b[i]) + sum((diffs[j] * pw[j] for j in range(len(diffs)) if diffs[j]), Fraction(0)))
        J.append(sum((j * diffs[j] * pw[j - 1] for j in range(1, len(diffs)) if diffs[j]), Fraction(0)))
    knot_max = max(abs(x - y) for x, y in zip(knots_a, knots_b))
    vmax, jmax = max(V), max(J)
    order = sorted(range(len(V)), key=lambda i: V[i], reverse=True)[:12]
    return {'raw_coefficient_max': fmt(raw), 'raw_coefficient_max_exact': str(raw),
            'raw_argmax_cell_power': raw_at, 'raw_cells_above_gate': raw_cells,
            'raw_within_gate': raw <= GATE,
            'knots_max': fmt(knot_max), 'knots_within_gate': knot_max <= GATE,
            'X_difference': fmt(abs(X_a - X_b)), 'X_within_gate': abs(X_a - X_b) <= GATE,
            'V_max': fmt(vmax), 'V_argmax': V.index(vmax), 'V_within_gate': vmax <= GATE,
            'J_max': fmt(jmax), 'J_argmax': J.index(jmax), 'J_within_gate': jmax <= GATE,
            'largest_V_cells': [[i, fmt(V[i]), fmt(J[i])] for i in order]}


def exact_map(snap):
    return ([[exact_mpf(v) for v in row] for row in snap['xpoly']],
            [exact_mpf(v) for v in snap['xknots']], exact_mpf(snap['X']))


def jacobian_lower(rows, widths):
    """Outward Arb lower bound of the represented map derivative over every closed cell."""
    from flint import arb, fmpq
    lower = None
    for i, row in enumerate(rows):
        derivative = [arb(fmpq((j * c).numerator, (j * c).denominator)) for j, c in enumerate(row) if j]
        half = fmpq(widths[i].numerator, 2 * widths[i].denominator)
        z = arb(half, half)
        value = arb(0)
        for coefficient in reversed(derivative):
            value = value * z + coefficient
        if not value.is_finite():
            raise ArithmeticError('Nonfinite Jacobian enclosure')
        q = value.lower().fmpq()
        bound = Fraction(int(q.p), int(q.q))
        lower = bound if lower is None else min(lower, bound)
    return lower


def old80_table(P):
    """Piece choice of the predecessor producer at 80 digits, recomputed with its own rule."""
    with mp.workdps(P['old_rule_dps']):
        d = rep.reference.Dense(P['level'], P['cases'][0])
        prec = mp.mp.prec
        table = rep.floor_table(d)
    return table, prec


def grid_paths(P, case, N):
    name = f"{P['level']}_case{case}_N{N}_p80"
    base = Path(P['grid_dir'])
    return base / (name + '.grid.json'), base / (name + '.audit.json'), base / (name + '.json')


def structure_checks(grid, audit, gp, N, cells, degree):
    ok = {'audit_bound_to_grid': audit['grid_sha256'] == sha(gp),
          'audit_velocities_zero': bool(audit['all_velocities_exactly_zero']),
          'velocities_exactly_zero': all(exact_decimal(v) == 0 for row in grid['velocities'] for v in row),
          'cauchy_constants_zero': all(exact_decimal(v) == 0 for v in grid['Cauchy_constants'].values()),
          'dimensions': grid['N'] == N and all(len(grid[k]) == N + 1 for k in ('A', 'B', 'Phi', 'ell', 's', 'x', 'seed_fields'))
          and len(grid['gauge_coefficients']) == 12 and len(grid['coordinate_knots']) == cells + 1
          and len(grid['coordinate_integral_polynomials']) == cells
          and all(len(r) == degree + 2 for r in grid['coordinate_integral_polynomials']),
          'saved_dps_80': grid['dps'] == 80}
    ok['all'] = all(ok.values())
    return ok


def flag(node, kind, info, delta):
    return {'node': node, 'kind': kind, 'margin': fmt(info['margin']), 'dual_difference': fmt(delta),
            'dual_within_gate': within(delta)}


def node_replay(d, grid):
    """Inverse map, reconstructed fields and Jacobian identity at every saved node."""
    keys = ('A', 'B', 'Phi', 'ell')
    inverse = fields_rec = jac_identity = mp.mpf(0)
    flags, s_rec = [], []
    for k in range(grid['N'] + 1):
        s = mp.mpf(grid['s'][k])
        x = mp.mpf(grid['x'][k])
        si, inv = d.invert_explicit(x)
        s_rec.append(encode_mpf(si))
        inverse = max(inverse, abs(si - s))
        fields, _, finfo = d.fields_explicit(si, d.q)
        for value, key in zip(fields, keys):
            fields_rec = max(fields_rec, abs(value - mp.mpf(grid[key][k])))
        fs, _, sinfo = d.fields_explicit(s, d.q)
        value, slope, minfo = d.map_at(s)
        jac_identity = max(jac_identity, abs(slope - mp.exp(fs[3] - fs[1])))
        if inv['ambiguous']:
            flags.append(flag(k, 'inverse_cell', inv, abs(inv['alternate']['s'] - si)))
        if finfo['ambiguous']:
            flags.append(flag(k, 'reconstructed_piece', finfo, max(abs(a - b) for a, b in zip(finfo['alternate']['fields'], fields))))
        if sinfo['ambiguous']:
            flags.append(flag(k, 'saved_piece_identity', sinfo, max(abs(a - b) for a, b in zip(sinfo['alternate']['fields'], fs))))
        if minfo['ambiguous']:
            alt = minfo['alternate']
            flags.append(flag(k, 'map_cell', minfo, max(abs(alt['value'] - value), abs(alt['slope'] - slope))))
    return {'inverse_s': fmt(inverse), 'inverse_s_within_gate': within(inverse),
            'fields_at_reconstructed_s': fmt(fields_rec), 'fields_at_reconstructed_s_within_gate': within(fields_rec),
            'jacobian_identity': fmt(jac_identity), 'jacobian_identity_within_gate': within(jac_identity),
            'ambiguous_points': flags, 's_reconstructed': s_rec}


def wall_traces(d, grids):
    """Map, Jacobian and inverse traces at both walls for the map currently loaded in d."""
    D = mp.mpf(d.seed['D'])
    last = d.cells - 1
    z_end = D - last * d.h
    x_end = d.xknots[last] + rep.horner(d.xpoly[last], z_end)
    lower_fields, _, _ = d.fields_explicit(mp.mpf(0), d.q)
    upper_fields, _, upper_info = d.fields_explicit(D, d.q)
    slope_lower = rep.horner(d.derivative_row(0), mp.mpf(0))
    slope_upper = rep.horner(d.derivative_row(last), z_end)
    inverse_upper = {str(N): abs(d.invert_explicit(mp.mpf(g['x'][N]))[0] - D) for N, g in grids.items()}
    j_lower = abs(slope_lower - mp.exp(lower_fields[3] - lower_fields[1]))
    j_upper = abs(slope_upper - mp.exp(upper_fields[3] - upper_fields[1]))
    end = abs(d.X - x_end)
    return {'x_at_lower_wall_exactly_zero': bool(d.xknots[0] == 0),
            'X_minus_last_cell_at_D': fmt(end), 'X_minus_last_cell_at_D_within_gate': within(end),
            'inverse_of_saved_upper_x_minus_D': {k: fmt(v) for k, v in inverse_upper.items()},
            'inverse_of_saved_upper_x_within_gate': all(within(v) for v in inverse_upper.values()),
            'jacobian_lower_wall_minus_exp_ell_minus_B': fmt(j_lower),
            'jacobian_upper_wall_minus_exp_ell_minus_B': fmt(j_upper),
            'jacobian_walls_within_gate': within(max(j_lower, j_upper)),
            'upper_wall_native_piece': upper_info['piece'],
            'jacobian_lower_wall': fmt(slope_lower), 'jacobian_upper_wall': fmt(slope_upper)}


def poly_derivative(c):
    return [(j + 1) * c[j + 1] for j in range(len(c) - 1)]


def one_case(P, case, dps, old80, guard_sha):
    mp.mp.dps = dps
    started, cpu0, prec = time.monotonic(), time.process_time(), mp.mp.prec
    out = Path(P['out'])
    level = P['level']
    seed = read(Path(P['native']) / 'results' / level / 'SEED.json')
    dense_raw = read(Path(P['native']) / 'results' / level / f'case_{case}.dense.json')
    cells, degree = seed['cells'], seed['degree']
    widths = widths_exact(seed)
    ref = rep.reference.Dense(level, case)
    ref.qualify_gauge()
    ref.make_map()
    d = rep.ExplicitDense(level, case)
    gauge = d.qualify_gauge()
    floor_p = rep.floor_table(d)
    tables = {'canonical': rep.canonical_table(cells), 'old80': list(old80), 'floor_at_p': floor_p}
    snaps = {}
    for rule in RULES:
        d.make_map_explicit(tables[rule])
        snaps[rule] = snapshot(d)
        atomic(out / 'maps' / f'case{case}_p{dps}_{rule}.json', {
            'guard': guard_sha, 'case': case, 'dps': dps, 'prec': prec, 'rule': rule, 'table': tables[rule],
            'offsets': [encode_mpf(v) for v in snaps[rule]['offsets']],
            'knots': [encode_mpf(v) for v in snaps[rule]['xknots']],
            'coefficients': [[encode_mpf(v) for v in row] for row in snaps[rule]['xpoly']],
            'X': encode_mpf(snaps[rule]['X']), 'q': [encode_mpf(v) for v in d.q],
            'encoding': 'each value is [signed integer mantissa, binary exponent], exact'}, True)
    controls = {'floor_rule_map_bitwise_equals_reference_make_map': map_bitwise(snaps['floor_at_p'], ref),
                'explicit_gauge_bitwise_equals_reference': rows_bitwise(d.q, ref.q)}
    if dps == P['old_rule_dps']:
        controls['old80_map_bitwise_equals_reference_make_map_at_80'] = floor_p == list(old80) and map_bitwise(snaps['old80'], ref)
    switched = [i for i in range(cells) if old80[i] != i]
    differing = [i for i in range(cells) if not rows_bitwise(snaps['canonical']['xpoly'][i], snaps['old80']['xpoly'][i])]
    exact_maps = {rule: exact_map(snaps[rule]) for rule in RULES}
    loaded = {N: tuple(read(p) for p in grid_paths(P, case, N)) for N in P['degrees']}
    grids = {N: loaded[N][0] for N in P['degrees']}
    saved_cache = {}
    per_grid = {}
    Dm = mp.mpf(seed['D'])
    for N in P['degrees']:
        grid, audit, _ = loaded[N]
        gp, ap, rp = grid_paths(P, case, N)
        key = json.dumps([grid['coordinate_integral_polynomials'], grid['coordinate_knots'], grid['X']])
        if key not in saved_cache:
            saved = ([[exact_decimal(v) for v in row] for row in grid['coordinate_integral_polynomials']],
                     [exact_decimal(v) for v in grid['coordinate_knots']], exact_decimal(grid['X']))
            saved_cache[key] = ({rule: compare_maps(exact_maps[rule], saved, widths) for rule in RULES},
                                jacobian_lower(saved[0], widths), all(b > a for a, b in zip(saved[1], saved[1][1:])))
        comparisons, saved_lower, increasing = saved_cache[key]
        q_saved = [mp.mpf(v) for v in grid['gauge_coefficients']]
        gauge_coeff = max(abs(a - b) for a, b in zip(d.q, q_saved))
        fields_saved = seed_saved = mp.mpf(0)
        saved_flags = []
        for k in range(N + 1):
            s = mp.mpf(grid['s'][k])
            fields, base, info = d.fields_explicit(s, q_saved)
            for value, field in zip(fields, ('A', 'B', 'Phi', 'ell')):
                fields_saved = max(fields_saved, abs(value - mp.mpf(grid[field][k])))
            for value, stored in zip(base, grid['seed_fields'][k]):
                seed_saved = max(seed_saved, abs(value - mp.mpf(stored)))
            if info['ambiguous']:
                saved_flags.append(flag(k, 'saved_piece', info, max(abs(a - b) for a, b in zip(info['alternate']['fields'], fields))))
        nodes = {}
        invert_port = True
        for rule in RULES:
            load_snapshot(d, snaps[rule])
            nodes[rule] = node_replay(d, grid)
            if rule == 'floor_at_p':
                for k in range(N + 1):
                    x = mp.mpf(grid['x'][k])
                    si, info = d.invert_explicit(x)
                    if not info['ambiguous'] and not bitwise(si, ref.invert(x)):
                        invert_port = False
        clocks = []
        for i in (0, N):
            B, A, W = mp.mpf(grid['B'][i]), mp.mpf(grid['A'][i]), mp.mpf(grid['seed_fields'][i][0])
            clocks.append({'wall': 0 if i == 0 else 1, 'normal_orientation_sigma': 1 if i == 0 else -1,
                           'q_at_wall_exact': str(exact_decimal(grid['B'][i]) - exact_decimal(grid['A'][i])),
                           'initial_log_lapse': mp.nstr(B, 40), 'initial_log_angular_warp': mp.nstr(A, 40),
                           'normalized_proper_clock_rate': encode_mpf(mp.exp(B - W)),
                           'normalized_proper_clock_rate_decimal': mp.nstr(mp.exp(B - W), 40)})
        q_wall = []
        for poly in (q_saved, poly_derivative(q_saved), poly_derivative(poly_derivative(q_saved))):
            q_wall += [abs(rep.horner(poly, mp.mpf(0))), abs(rep.horner(poly, Dm))]
        top = abs(mp.mpf(grid['s'][N]) - Dm)
        per_grid[str(N)] = {
            'grid_sha256': sha(gp), 'audit_sha256': sha(ap), 'record_sha256': sha(rp),
            'structure': structure_checks(grid, audit, gp, N, cells, degree),
            'map_vs_saved': comparisons,
            'saved_map_jacobian_lower': str(saved_lower), 'saved_map_jacobian_lower_decimal': fmt(saved_lower),
            'saved_knots_strictly_increasing': increasing,
            'gauge_coefficients_vs_saved': fmt(gauge_coeff), 'gauge_coefficients_within_gate': within(gauge_coeff),
            'fields_at_saved_s': fmt(fields_saved), 'seed_fields_at_saved_s': fmt(seed_saved),
            'fields_at_saved_s_within_gate': within(max(fields_saved, seed_saved)),
            'saved_position_ambiguous_points': saved_flags,
            'nodes': nodes, 'invert_port_bitwise_on_unambiguous_nodes': invert_port,
            'clock_and_normals': clocks,
            'saved_q_wall_jets_max': fmt(max(q_wall)), 'saved_q_wall_jets_within_gate': within(max(q_wall)),
            'saved_wall_nodes': {'sN_minus_D': fmt(top), 'sN_minus_D_within_gate': within(top),
                                 's0_exactly_zero': exact_decimal(grid['s'][0]) == 0,
                                 'x0_exactly_zero': exact_decimal(grid['x'][0]) == 0,
                                 'xN_equals_saved_X': exact_decimal(grid['x'][N]) == exact_decimal(grid['X'])}}
    rules_out = {}
    for rule in RULES:
        load_snapshot(d, snaps[rule])
        rows, knots, _ = exact_maps[rule]
        lower = jacobian_lower(rows, widths)
        rules_out[rule] = {'table_differs_from_canonical_at': [i for i, p in enumerate(tables[rule]) if p != i],
                           'jacobian_lower': str(lower), 'jacobian_lower_decimal': fmt(lower),
                           'knots_strictly_increasing': all(b > a for a, b in zip(knots, knots[1:])),
                           'wall_traces': wall_traces(d, grids)}
    final = gauge['final']
    order02 = max(abs(v) for wall in final for row in wall[:2] for v in row)
    order4 = max(abs(v) for wall in final for v in wall[2])
    finite = all(mp.isfinite(v) for wall in final for row in wall for v in row)
    eps_saved = exact_decimal(dense_raw['epsilon'])
    target = Fraction(CONFIG['epsilon_targets'][str(case)])
    return {
        'guard': guard_sha, 'case': case, 'dps': dps, 'prec': prec, 'utc': now(),
        'epsilon_target': str(target), 'epsilon_saved_exact_decimal': str(eps_saved),
        'epsilon_rounding_offset': str(eps_saved - target), 'epsilon_rounding_offset_decimal': fmt(eps_saved - target),
        'saved_epsilon_in_certified_interval': -Fraction(1, 200000) <= eps_saved <= Fraction(1, 200000),
        'tables': {'old80_differs_from_canonical_at': switched,
                   'floor_at_p_differs_from_canonical_at': [i for i, p in enumerate(floor_p) if p != i],
                   'floor_at_p_differs_from_old80_at': [i for i in range(cells) if floor_p[i] != old80[i]]},
        'implementation_controls': controls,
        'selection_isolated': {'cells_where_canonical_and_old80_rows_differ': differing,
                               'differ_only_where_tables_differ': set(differing) <= set(switched)},
        'gauge': {'q': [encode_mpf(v) for v in d.q],
                  'final_rows': [[[encode_mpf(v) for v in row] for row in wall] for wall in final],
                  'final_rows_decimal': [[[mp.nstr(v, 20) for v in row] for row in wall] for wall in final],
                  'max_orders_0_2': fmt(order02), 'max_order_4': fmt(order4), 'finite': finite,
                  'within_inherited_thresholds': bool(finite and order02 < mp.mpf(CONFIG['inherited_wall_row_gate_orders_0_2'])
                                                      and order4 < mp.mpf(CONFIG['inherited_wall_row_gate_order_4']))},
        'rules': rules_out, 'grids': per_grid,
        'seconds': time.monotonic() - started, 'cpu_seconds': time.process_time() - cpu0,
        'new_evolution_steps': 0, 'physical_ivp_run': False}


def load_map(P, case, dps, rule):
    m = read(Path(P['out']) / 'maps' / f'case{case}_p{dps}_{rule}.json')
    return ([[decode_pair(v) for v in row] for row in m['coefficients']],
            [decode_pair(v) for v in m['knots']], decode_pair(m['X'])), [decode_pair(v) for v in m['q']]


def cross_precision(P, case, widths, records):
    lo, hi = P['dps']
    out = {}
    for rule in GATED_RULES:
        a, _ = load_map(P, case, lo, rule)
        b, _ = load_map(P, case, hi, rule)
        cmp = compare_maps(a, b, widths)
        nodes = {}
        for N in P['degrees']:
            ra = records[(case, lo)]['grids'][str(N)]['nodes'][rule]['s_reconstructed']
            rb = records[(case, hi)]['grids'][str(N)]['nodes'][rule]['s_reconstructed']
            nodes[str(N)] = max(abs(decode_pair(x) - decode_pair(y)) for x, y in zip(ra, rb))
        out[rule] = {'map': cmp, 'map_within_gate': cmp['raw_within_gate'] and cmp['knots_within_gate'] and cmp['X_within_gate'],
                     'reconstructed_s_max': {k: fmt(v) for k, v in nodes.items()},
                     'nodes_within_gate': all(v <= GATE for v in nodes.values())}
    qa = load_map(P, case, lo, 'canonical')[1]
    qb = load_map(P, case, hi, 'canonical')[1]
    rows_a = records[(case, lo)]['gauge']['final_rows']
    rows_b = records[(case, hi)]['gauge']['final_rows']
    rows_delta = max(abs(decode_pair(x) - decode_pair(y)) for wa, wb in zip(rows_a, rows_b)
                     for ra, rb in zip(wa, wb) for x, y in zip(ra, rb))
    q_delta = max(abs(x - y) for x, y in zip(qa, qb))
    clocks = {}
    for N in P['degrees']:
        ca = records[(case, lo)]['grids'][str(N)]['clock_and_normals']
        cb = records[(case, hi)]['grids'][str(N)]['clock_and_normals']
        delta = max(abs(decode_pair(x['normalized_proper_clock_rate']) - decode_pair(y['normalized_proper_clock_rate']))
                    for x, y in zip(ca, cb))
        clocks[str(N)] = {'max_rate_difference': fmt(delta), 'within_gate': delta <= GATE,
                          'orientations_correct': [x['normal_orientation_sigma'] for x in ca] == [1, -1]
                          and [y['normal_orientation_sigma'] for y in cb] == [1, -1]}
    out['gauge'] = {'q_max': fmt(q_delta), 'q_within_gate': q_delta <= GATE,
                    'final_rows_max': fmt(rows_delta), 'final_rows_within_gate': rows_delta <= GATE}
    out['clocks'] = clocks
    return out


def correction_bounds(P):
    """Port of the predecessor readback's unexecuted signed root-bound comparison (exact)."""
    out = []
    box = [Fraction(1, 100000), Fraction(1, 10), Fraction(1, 10)]
    independent_path = Path(P['connected_audit'])
    audit = read(independent_path)
    for name, case in (('positive', 3), ('negative', 4)):
        source = Path(P['finite']) / f'output/{name}/RESULT.json'
        old = read(source)
        dense = read(Path(P['native']) / 'results' / P['level'] / f'case_{case}.dense.json')
        independent = audit['endpoint_identity'][name]
        fresh = bool(independent['pass']) and independent['old_result_sha256'] == sha(source)
        eps = Fraction(old['epsilon'])
        centers = [Fraction(dense['A0']) - eps] + [Fraction(v) for v in dense['fifth_jet_coefficients']]
        absolute, errors, inside = [], [], True
        for center, row, r in zip(centers, independent['translated_root_image'], box):
            lo, hi = map(Fraction, row['exact'])
            inside = inside and (-r < lo <= hi < r)
            absolute.append([str(lo), str(hi)])
            errors.append(max(abs(lo - center), abs(hi - center)))
        out.append({'case': case, 'name': name, 'target_epsilon': str(eps), 'source_sha256': sha(source),
                    'old_result_pass': bool(old['pass']), 'independent_reconstruction_fresh': fresh,
                    'coordinates': ['A0-epsilon', 'b0', 'b1'], 'center_exact': [str(v) for v in centers],
                    'centers_equal_certified_sample_center': centers == [Fraction(v) for v in old['center']],
                    'root_enclosure_exact': absolute, 'within_common_uniqueness_box': inside,
                    'distance_from_saved_center_upper_exact': [str(v) for v in errors],
                    'distance_from_saved_center_upper_decimal': [fmt(v) for v in errors],
                    'independent_reconstruction_sha256': sha(independent_path),
                    'interpretation': 'Certified root at the exact target versus the numerical coefficient center; not literal equality.'})
    return out


def inherited_receipts(P):
    """Original-equation admission records of the six saved grids, authenticated by hash."""
    root = Path(P['spatial_root'])
    verification = read(P['admission_verification'])
    spatial = read(root / 'VERIFICATION.json')
    admission = read(root / 'GRID_ADMISSION.json')
    level = P['level']
    required = {f'inputs/{level}_case{c}_N{N}_p80{suffix}' for c in P['cases'] for N in P['degrees']
                for suffix in ('.json', '.grid.json', '.audit.json')}
    selected = {r['path']: r['sha256'] for r in admission['inputs'] if r['path'] in required}
    hashes_ok = set(selected) == required and all(sha(root / p) == h for p, h in selected.items())
    per_grid = {}
    for c in P['cases']:
        for N in P['degrees']:
            tag = f'{level}_case{c}_N{N}_p80 '
            rows = [r for r in admission['checks'] if r['check'].startswith(tag)]
            names = {r['check'][len(tag):] for r in rows}
            per_grid[f'case{c}_N{N}'] = {'checks': len(rows), 'required_families_present': set(FAMILIES) <= names,
                                         'all_pass': set(FAMILIES) <= names and all(r['pass'] for r in rows),
                                         'names': sorted(names)}
    ok = (bool(verification['all_passed']) and bool(spatial['record_integrity_valid'])
          and bool(spatial['complete_signed_cohort_qualified']) and bool(admission['all_passed']) and hashes_ok
          and all(v['all_pass'] for v in per_grid.values()))
    return {'admission_verification_all_passed': bool(verification['all_passed']),
            'spatial_record_integrity_valid': bool(spatial['record_integrity_valid']),
            'spatial_complete_signed_cohort_qualified': bool(spatial['complete_signed_cohort_qualified']),
            'grid_admission_all_passed': bool(admission['all_passed']), 'selected_input_hashes_unchanged': hashes_ok,
            'per_grid': per_grid, 'all_authenticated_and_passing': ok}


def saved_map_identity(P, case):
    keys = set()
    for N in P['degrees']:
        grid = read(grid_paths(P, case, N)[0])
        keys.add(json.dumps([grid['coordinate_integral_polynomials'], grid['coordinate_knots'], grid['X'],
                             grid['gauge_coefficients']]))
    return len(keys) == 1


def gate(rows, gid, group, ok, value=None, limit=None):
    rows.append({'id': gid, 'group': group, 'pass': bool(ok), 'value': value, 'limit': limit})


def evaluate(P, records, cross, roots, receipts, old80, old_prec, cells):
    g = []
    lim = CONFIG['gate_absolute']
    lo_dps, hi_dps = P['dps']
    for (case, dps), r in sorted(records.items()):
        tag = f'c{case}.p{dps}'
        ic = r['implementation_controls']
        gate(g, f'I1.{tag}.floor_rule_port_bitwise', 'I', ic['floor_rule_map_bitwise_equals_reference_make_map'])
        gate(g, f'I3.{tag}.gauge_port_bitwise', 'I', ic['explicit_gauge_bitwise_equals_reference'])
        if dps == P['old_rule_dps']:
            gate(g, f'I2.{tag}.old80_port_bitwise', 'I', ic['old80_map_bitwise_equals_reference_make_map_at_80'])
        gate(g, f'E1.{tag}.wall_rows_inherited_thresholds', 'E', r['gauge']['within_inherited_thresholds'],
             [r['gauge']['max_orders_0_2'], r['gauge']['max_order_4']], ['1e-10', '1e-12'])
        gate(g, f'C3.{tag}.selection_isolated', 'C', r['selection_isolated']['differ_only_where_tables_differ'],
             r['selection_isolated']['cells_where_canonical_and_old80_rows_differ'])
        for rule in GATED_RULES:
            ro = r['rules'][rule]
            w = ro['wall_traces']
            gate(g, f'M1.{tag}.{rule}.monotone', 'M', Fraction(ro['jacobian_lower']) > 0 and ro['knots_strictly_increasing'],
                 ro['jacobian_lower_decimal'], '>0')
            gate(g, f'W3.{tag}.{rule}.map_wall_trace', 'W', w['x_at_lower_wall_exactly_zero'] and w['X_minus_last_cell_at_D_within_gate']
                 and w['inverse_of_saved_upper_x_within_gate'], [w['X_minus_last_cell_at_D'], w['inverse_of_saved_upper_x_minus_D']], lim)
            gate(g, f'W4.{tag}.{rule}.wall_jacobian', 'W', w['jacobian_walls_within_gate'],
                 [w['jacobian_lower_wall_minus_exp_ell_minus_B'], w['jacobian_upper_wall_minus_exp_ell_minus_B']], lim)
        for N, gr in r['grids'].items():
            t = f'{tag}.N{N}'
            old = gr['map_vs_saved']['old80']
            can = gr['map_vs_saved']['canonical']
            gate(g, f'R1.{t}.raw_coefficients', 'R', old['raw_within_gate'], old['raw_coefficient_max'], lim)
            gate(g, f'R2.{t}.knots_and_length', 'R', old['knots_within_gate'] and old['X_within_gate'],
                 [old['knots_max'], old['X_difference']], lim)
            gate(g, f'R3.{t}.inverse_s', 'R', gr['nodes']['old80']['inverse_s_within_gate'], gr['nodes']['old80']['inverse_s'], lim)
            gate(g, f'R4.{t}.fields_at_reconstructed_s', 'R', gr['nodes']['old80']['fields_at_reconstructed_s_within_gate'],
                 gr['nodes']['old80']['fields_at_reconstructed_s'], lim)
            gate(g, f'S1.{t}.fields_at_saved_s', 'S', gr['fields_at_saved_s_within_gate'],
                 [gr['fields_at_saved_s'], gr['seed_fields_at_saved_s']], lim)
            gate(g, f'S2.{t}.gauge_coefficients', 'S', gr['gauge_coefficients_within_gate'], gr['gauge_coefficients_vs_saved'], lim)
            gate(g, f'U1.{t}.cell_value_bound', 'U', can['V_within_gate'], can['V_max'], lim)
            gate(g, f'U2.{t}.cell_jacobian_bound', 'U', can['J_within_gate'], can['J_max'], lim)
            cn = gr['nodes']['canonical']
            gate(g, f'U3.{t}.canonical_nodes', 'U', cn['inverse_s_within_gate'] and cn['fields_at_reconstructed_s_within_gate'],
                 [cn['inverse_s'], cn['fields_at_reconstructed_s']], lim)
            for rule in GATED_RULES:
                nd = gr['nodes'][rule]
                gate(g, f'E2.{t}.{rule}.jacobian_identity', 'E', nd['jacobian_identity_within_gate'], nd['jacobian_identity'], lim)
            flags = gr['saved_position_ambiguous_points'] + [f for rule in RULES for f in gr['nodes'][rule]['ambiguous_points']]
            gate(g, f'A1.{t}.ambiguous_points', 'A', all(f['dual_within_gate'] for f in flags), len(flags), lim)
            gate(g, f'I4.{t}.invert_port_bitwise', 'I', gr['invert_port_bitwise_on_unambiguous_nodes'])
            if dps == lo_dps:
                gate(g, f'S3.c{case}.N{N}.structure', 'S', gr['structure']['all'])
                gate(g, f'M1.c{case}.N{N}.saved.monotone', 'M',
                     Fraction(gr['saved_map_jacobian_lower']) > 0 and gr['saved_knots_strictly_increasing'],
                     gr['saved_map_jacobian_lower_decimal'], '>0')
                wn = gr['saved_wall_nodes']
                gate(g, f'W1.c{case}.N{N}.wall_gauge_and_positions', 'W',
                     gr['saved_q_wall_jets_within_gate'] and all(abs(Fraction(c['q_at_wall_exact'])) <= GATE for c in gr['clock_and_normals'])
                     and wn['sN_minus_D_within_gate'] and wn['s0_exactly_zero'] and wn['x0_exactly_zero'] and wn['xN_equals_saved_X'],
                     [gr['saved_q_wall_jets_max'], wn['sN_minus_D']], lim)
    for case in P['cases']:
        cx = cross[case]
        for label, rule in (('C1', 'canonical'), ('C2', 'old80')):
            gate(g, f'{label}.c{case}.{rule}_cross_precision', 'C', cx[rule]['map_within_gate'],
                 [cx[rule]['map']['raw_coefficient_max'], cx[rule]['map']['knots_max'], cx[rule]['map']['X_difference']], lim)
            gate(g, f'Cx.c{case}.{rule}.reconstructed_s_cross_precision', 'C', cx[rule]['nodes_within_gate'],
                 cx[rule]['reconstructed_s_max'], lim)
        gate(g, f'E1x.c{case}.wall_rows_cross_precision', 'E', cx['gauge']['final_rows_within_gate'] and cx['gauge']['q_within_gate'],
             [cx['gauge']['final_rows_max'], cx['gauge']['q_max']], lim)
        for N, c in cx['clocks'].items():
            gate(g, f'W2.c{case}.N{N}.clocks_cross_precision', 'W', c['within_gate'] and c['orientations_correct'],
                 c['max_rate_difference'], lim)
        gate(g, f'S4.c{case}.saved_map_identical_across_degrees', 'S', saved_map_identity(P, case))
    gate(g, 'E3.inherited_original_equation_receipts', 'E', receipts['all_authenticated_and_passing'])
    first = str(P['degrees'][0])
    h1 = records[(P['cases'][0], hi_dps)]['grids'][first]['map_vs_saved']['floor_at_p']
    switched_hi = set(records[(P['cases'][0], hi_dps)]['tables']['floor_at_p_differs_from_old80_at'])
    gate(g, f"H1.c{P['cases'][0]}.p{hi_dps}.N{first}.historical_failure_reproduced", 'H',
         (not h1['raw_within_gate']) and set(h1['raw_cells_above_gate']) <= switched_hi,
         [h1['raw_coefficient_max'], h1['raw_argmax_cell_power']], '>1e-50, only at precision-switched cells')
    gate(g, 'A2.selection_tables', 'A', len(old80) == cells and all(p in (i - 1, i) for i, p in enumerate(old80))
         and all(records[(c, P['old_rule_dps'])]['tables']['floor_at_p_differs_from_old80_at'] == [] for c in P['cases']),
         {'old80_prec_bits': old_prec, 'old80_non_canonical_cells': [i for i, p in enumerate(old80) if p != i]})
    for row in roots:
        gate(g, f"G1.{row['name']}.root_bounds", 'G', row['old_result_pass'] and row['independent_reconstruction_fresh']
             and row['centers_equal_certified_sample_center'] and row['within_common_uniqueness_box'],
             row['distance_from_saved_center_upper_decimal'])
    return g


def classify(gates):
    failing = [row for row in gates if not row['pass']]
    groups = {row['group'] for row in failing}
    if not failing:
        return 'DETERMINISTIC_KNOT_REPRESENTATION_ADMITTED__HISTORICAL_RAW_GATE_RETAINED_FAILED'
    if groups & {'I', 'H'}:
        return 'IMPLEMENTATION_OR_HISTORICAL_CONTROL_FAILED'
    if groups <= {'R', 'S', 'C', 'U', 'M', 'W', 'E', 'A'} and all(('.c3.' in r['id'] or '.c4.' in r['id']) for r in failing):
        return 'SIGNED_REPLAY_FAILED'
    if groups & {'R', 'S'}:
        return 'SAVED_MAP_NOT_REPRODUCED'
    if 'C' in groups:
        return 'CANONICAL_REPRESENTATION_PRECISION_DEPENDENT'
    if 'U' in groups:
        return 'REPRESENTATION_CHOICE_MATERIAL'
    if 'G' in groups:
        return 'SIGNED_ROOT_BOUND_FAILED'
    return 'REPRESENTATION_ADMISSION_FAILED_' + ''.join(sorted(groups))


def status(P, state, **extra):
    atomic(P['status'], {'line': '02_lin_static', 'state': state, 'utc': now(), 'pid': os.getpid(),
                         'compute_slot': os.environ.get('COMPUTE_SLOT'), 'line_token': os.environ.get('LINE_TOKEN'),
                         'stage': 'producer', 'fixture': P['fixture']} | extra)


def execute(P, guard_sha):
    out = Path(P['out'])
    if (out / 'PRODUCER_RESULT.json').exists() or (out / 'FAILURE.json').exists():
        raise RuntimeError('Producer already terminal or failed closed; no restart')
    rep.bind_parent(P['native'])
    started, cpu0 = time.monotonic(), time.process_time()
    old80, old_prec = old80_table(P)
    records = {}
    fresh = 0
    for case in P['cases']:
        for dps in P['dps']:
            path = out / f'case{case}_p{dps}.json'
            if path.exists():
                record = read(path)
                if record['guard'] != guard_sha or record['case'] != case or record['dps'] != dps:
                    raise RuntimeError('Stale case record')
            else:
                if (out / 'maps').exists() and any((out / 'maps').glob(f'case{case}_p{dps}_*.json')):
                    raise RuntimeError('Partial maps for an unrecorded case; inspect before any rerun')
                if P['fixture'] and P.get('stop_after_records') is not None and fresh >= P['stop_after_records']:
                    raise SystemExit(17)
                atomic(path, one_case(P, case, dps, old80, guard_sha), True)
                record = read(path)
                fresh += 1
            records[(case, dps)] = record
            print(json.dumps({'case': case, 'dps': dps, 'seconds': round(record['seconds'], 2)}), flush=True)
            status(P, 'RUNNING', completed=[list(k) for k in records])
    seed = read(Path(P['native']) / 'results' / P['level'] / 'SEED.json')
    widths = widths_exact(seed)
    mp.mp.dps = max(P['dps'])
    cross = {case: cross_precision(P, case, widths, records) for case in P['cases']}
    roots = correction_bounds(P)
    receipts = inherited_receipts(P)
    gates = evaluate(P, records, cross, roots, receipts, old80, old_prec, seed['cells'])
    classification = classify(gates)
    result = {'guard': guard_sha, 'utc': now(), 'classification_provisional': classification,
              'gates_passed': sum(1 for r in gates if r['pass']), 'gates_total': len(gates), 'gates': gates,
              'failed_gates': [r['id'] for r in gates if not r['pass']],
              'selection_tables': {'old80': old80, 'old80_prec_bits': old_prec,
                                   'old80_non_canonical_cells': [i for i, p in enumerate(old80) if p != i],
                                   'floor_at_hi_non_canonical_cells': records[(P['cases'][0], max(P['dps']))]['tables']['floor_at_p_differs_from_canonical_at']},
              'cross_precision': {str(k): v for k, v in cross.items()}, 'root_bounds': roots,
              'inherited_original_equation_receipts': receipts,
              'case_records': {f'case{c}_p{p}.json': sha(out / f'case{c}_p{p}.json') for c, p in records},
              'maps': {p.name: sha(p) for p in sorted((out / 'maps').glob('*.json'))},
              'elapsed_seconds': time.monotonic() - started, 'cpu_seconds': time.process_time() - cpu0,
              'new_evolution_steps': 0, 'physical_ivp_run': False,
              'historical_raw_coefficient_gate': 'RETAINED_FAILED: predecessor case 0, 100 digits; not rescored',
              'note': 'Producer decision is provisional until the independent verifier accepts it.'}
    atomic(out / 'PRODUCER_RESULT.json', result, True)
    status(P, 'PRODUCER_COMPLETE', classification_provisional=classification,
           gates_passed=result['gates_passed'], gates_total=result['gates_total'])
    print(json.dumps({'classification_provisional': classification, 'gates_passed': result['gates_passed'],
                      'gates_total': result['gates_total']}), flush=True)
    return result


def prepare():
    """Launch checks that precede any outcome; a refusal here leaves no failed outcome."""
    check_environment()
    limits = limit_address_space()
    from flint import ctx
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    guard_sha, _ = freeze_guard()
    cap = capacity()
    if cap['available_bytes'] < CONFIG['minimum_available_bytes']:
        raise RuntimeError('Insufficient available memory')
    return guard_sha, cap, limits


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'run':
        raise SystemExit('usage: replay.py run')
    P0 = real_paths()
    try:
        guard0, cap0, limits0 = prepare()
    except Exception as error:
        stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
        atomic(Path(P0['out']) / 'refusals' / f'LAUNCH_REFUSED_{stamp}_{os.getpid()}.json',
               {'type': type(error).__name__, 'error': str(error), 'utc': now(), 'outcomes_started': False}, True)
        raise

    def alarm(*args):
        raise TimeoutError('Frozen producer wall budget')
    try:
        signal.signal(signal.SIGALRM, alarm)
        signal.alarm(CONFIG['producer_wall_seconds'])
        status(P0, 'RUNNING', capacity=cap0, address_space=limits0)
        execute(P0, guard0)
        signal.alarm(0)
    except Exception as error:
        atomic(Path(P0['out']) / 'FAILURE.json', {'status': 'FAILED_CLOSED', 'type': type(error).__name__, 'error': str(error),
                                                 'traceback': traceback.format_exc(), 'utc': now(),
                                                 'automatic_restart_allowed': False}, True)
        try:
            status(P0, 'FAILED_CLOSED', error=str(error))
        except Exception:
            pass
        raise
