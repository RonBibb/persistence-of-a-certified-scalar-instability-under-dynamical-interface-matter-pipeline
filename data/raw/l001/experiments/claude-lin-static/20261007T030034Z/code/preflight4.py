"""Synthetic-only pre-freeze controls for run 20261007T030034Z. No real outcome is computed.

Manufactured background (gamma = 0, m2 = 0, T = 0, P = v0 = v1, lambda_a = 0): H(s) = -sqrt(k) tan(sqrt(k) s),
E = 1/cos(sqrt(k) s), W = log cos(sqrt(k) s), psi = 1/cos^2(sqrt(k) s), f = 1 and g = 0 for mu = 0 (mu is a
bracket around 0); lambda_b = 6 H(s_target) puts the upper wall at a known s*. The fixture builds its own
accepted artifacts with the inherited engine at 768 bits in the finite-packet formats (source flow and its
checkpoints, K preparations, two-phase certificate with checkpoints, certified root image), then runs the
production record path at production precision with 64 subcells: reprep.produce_phase x4 ->
reprep.produce_material x2 -> assemble4.assemble -> verify4.verify_case x2 -> verify4.verify_final.
Step 1/64, K = [2 - 1/128, 2 + 1/128] (the last two cells, as in production), checkpoints every 32 cells.
    python -B <run>/code/preflight4.py all
"""
import json
import shutil
import sys
import time
from fractions import Fraction
from pathlib import Path

import mpmath as mp

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inherited'))
sys.path.insert(1, str(HERE))
from flint import arb, fmpq, ctx  # noqa: E402
import records  # noqa: E402
import nonlinear  # noqa: E402
import source_flow  # noqa: E402
import preparation  # noqa: E402
import identity_run as ir  # noqa: E402
from series import interval, bounds  # noqa: E402
import reprep  # noqa: E402
import assemble4  # noqa: E402
import verify4  # noqa: E402
from common4 import RUN, CONFIG, now, read, atomic, fq, source_hashes, runtime_fingerprint, check_environment, limit_address_space  # noqa: E402

STEP = fmpq(1, 64)
K = (fmpq(2) - fmpq(1, 128), fmpq(2) + fmpq(1, 128))
TOTAL, RESTART, CK = 129, 128, 32
GUARD, FGUARD = 'fixture-guard', 'fixture-finite-guard'
V = fmpq(9, 100)
EPS = {'positive': fmpq(1, 200000), 'negative': fmpq(-1, 200000)}
CASES, PHASES = ['positive', 'negative'], ['center', 'box']
RADII = [Fraction(1, 100000), Fraction(1, 10), Fraction(1, 10)]
S_TARGET = Fraction(2) + Fraction(1, 256)
DEGREES = (8, 12)


def closed(s):
    c = mp.cos(mp.mpf('0.1') * s)
    return {'W': mp.log(c), 'H': -mp.mpf('0.1') * mp.tan(mp.mpf('0.1') * s), 'E': 1 / c, 'psi': 1 / (c * c)}


def q60(x):
    return Fraction(mp.nstr(x, 60))


def background():
    with mp.workdps(120):
        lam = Fraction(mp.nstr(6 * closed(mp.mpf(S_TARGET.numerator) / S_TARGET.denominator)['H'], 110))
        s_true = mp.mpf(10) * mp.atan(-mp.mpf(lam.numerator) / lam.denominator * 10 / 6)
        st = q60(s_true)
    w = Fraction(64, 2 ** 24)
    D1 = Fraction(int(st * 2 ** 24) - 64, 2 ** 24)
    D2 = D1 + 2 * w
    return lam, st, (D1, D2)


def common_parameters(lam, mu_point=False):
    return {'m2': arb(0), 'gamma': arb(0), 'lambda_a': arb(0), 'lambda_b': arb(fmpq(lam.numerator, lam.denominator)),
            'v0': arb(V), 'v1': arb(V), 'k': interval(fmpq(1, 100) - fmpq(1, 10 ** 12), fmpq(1, 100) + fmpq(1, 10 ** 12)),
            'mu': arb(0) if mu_point else interval(fmpq(-1, 10 ** 6), fmpq(1, 10 ** 6)), 'D': interval(*K)}


def fresh_y0():
    return [arb(0), arb(0), interval(V - fmpq(1, 10 ** 10), V + fmpq(1, 10 ** 10)), arb(0), arb(1), arb(1), arb(1), arb(0), arb(0)]


def make_finite(base, lam, mu_point=False):
    """Fixture analogue of the accepted finite packet: source flow, K preparations, two-phase certificate."""
    p = common_parameters(lam, mu_point)
    src = base / 'finite' / 'source'
    st = {'task_index': 0, 'cell_index': 0, 'elapsed_seconds': 0.0, 'which': 'source', 'phase_results': [], 'y': fresh_y0(), 'p': p,
          'max_picard': 0, 'cover': [], 'end': None}
    while st['cell_index'] < TOTAL:
        reprep.finite_cell(st, source_flow, K[0], K[1], STEP)
        if st['cell_index'] % CK == 0 or st['cell_index'] == TOTAL:
            records.save(src, st, FGUARD)
    y0 = fresh_y0()
    jets = [preparation.wall_jets(y0, st['p'], 0), preparation.wall_jets(st['end'], st['p'], 1)]
    common = {'status': 'COMPLETE', 'which': 'source', 'guard': FGUARD, 'p': st['p'], 'y0': y0, 'jets': jets, 'event_cover': st['cover'], 'cells': TOTAL}
    atomic(src / 'RESULT.json', records.pack(common), True)
    common = records.unpack(read(src / 'RESULT.json'))
    boxes, C = {}, None
    for w in CASES:
        prep = preparation.prepare(EPS[w], common['jets'], common['p'])
        out = base / 'finite' / w
        center = [Fraction(0), -fq((bounds(prep['W'][0])[0] + bounds(prep['W'][0])[1]) / 2),
                  -fq((bounds(prep['W'][1])[0] + bounds(prep['W'][1])[1]) / 2)]
        maps = {}
        for task, name in ((0, 'center'), (1, 'box')):
            x = [arb(reprep.f2q(c)) for c in center] if name == 'center' else [interval(reprep.f2q(c - r), reprep.f2q(c + r)) for c, r in zip(center, RADII)]
            pp = dict(common['p'])
            pp.update(prep)
            pp['x'] = x
            lower = preparation.wall_increment(common['y0'], common['jets'][0], pp, EPS[w])['target']
            ph = {'task_index': task, 'cell_index': 0, 'elapsed_seconds': 0.0, 'which': w, 'phase_results': [], 'preparation': prep, 'p': pp,
                  'y': list(common['y0']) + [x[0], lower, arb(1)] + [arb(0)] * 5, 'max_picard': 0, 'cover': [], 'end': None, 'map': None}
            while ph['cell_index'] < TOTAL:
                reprep.finite_cell(ph, nonlinear, K[0], K[1], STEP, endpoint=lambda z, ph=ph: reprep.map_at(z, ph['p'], common['jets']))
                if ph['cell_index'] % CK == 0 or ph['cell_index'] == TOTAL:
                    records.save(out, ph, FGUARD)
            maps[name] = ph['map']
        if C is None:
            j00 = maps['box']['J'][0]
            ratio = (Fraction(1) / fq((bounds(j00)[0] + bounds(j00)[1]) / 2)).limit_denominator(10 ** 6)
            C = [fmpq(ratio.numerator, ratio.denominator), fmpq(1), fmpq(1)]
        X0 = [(c - r, c + r) for c, r in zip(center, RADII)]
        kr = reprep.krawczyk(C, maps['center']['G'], maps['box']['J'], X0, center)
        if kr['empty'] or not kr['strict_inclusion_in_X']:
            raise RuntimeError('Fixture certificate did not include its image: ' + json.dumps(kr['image']))
        X = [(Fraction(a), Fraction(b)) for a, b in kr['new_box']]
        boxes[w] = (X, [(a + b) / 2 for a, b in X])
        res = {'pass': True, 'preparation': prep, 'G_center': maps['center']['G'],
               'J_box': [maps['box']['J'][3 * i:3 * i + 3] for i in range(3)], 'center': [str(c) for c in center], 'radii': [str(r) for r in RADII]}
        atomic(out / 'RESULT.json', records.pack(res), True)
    return boxes, C


_PROFILES = {}


def profile(name, Dn):
    key = (name, str(Dn))
    if key not in _PROFILES:
        pr = ir.SavedProfile.__new__(ir.SavedProfile)
        pr.D = fmpq(Dn.numerator, Dn.denominator)
        pr.h = fmpq(1, 8)
        pieces, metric = [], []
        eps = mp.mpf(int(EPS[name].p)) / int(EPS[name].q)
        with mp.workdps(60):
            for i in range(16):
                s0 = mp.mpf(i) / 8
                rows = []
                for key2 in ('W', 'H', 'P', 'T', 'E', 'psi', 'f', 'g'):
                    if key2 in ('W', 'H', 'E', 'psi'):
                        co = mp.taylor(lambda s, key2=key2: closed(s)[key2], s0, 14)
                        rows.append([arb(fmpq(*Fraction(mp.nstr(c, 55)).as_integer_ratio())) for c in co])
                    else:
                        rows.append([arb(V)] if key2 == 'P' else [arb(1)] if key2 == 'f' else [arb(0)])
                pieces.append(rows)
                co = mp.taylor(lambda s: closed(s)['W'] + eps * closed(s)['psi'], s0, 14)
                metric.append([arb(fmpq(*Fraction(mp.nstr(c, 55)).as_integer_ratio())) for c in co])
        pr.seed = pieces
        pr.case, pr.eps, pr.metric, pr.correction = 3, arb(EPS[name]), metric, [arb(0)]
        _PROFILES[key] = pr
    return _PROFILES[key]


def write_saved(base, Dn):
    files = {}
    with mp.workdps(60):
        top = mp.mpf(Dn.numerator) / Dn.denominator
        lo, hi = closed(mp.mpf(0)), closed(top)
        for name in CASES:
            eps = mp.mpf(int(EPS[name].p)) / int(EPS[name].q)
            Lref = mp.quad(lambda s: mp.exp(-2 * eps * closed(s)['psi']), [0, top])
            for N in DEGREES:
                def col(v0, vN):
                    return [mp.nstr(v0, 50)] + ['0.0'] * (N - 1) + [mp.nstr(vN, 50)]
                A0, AN = lo['W'] + eps * lo['psi'], hi['W'] + eps * hi['psi']
                grid = {'A': col(A0, AN), 'B': col(A0, AN), 'Phi': col(mp.mpf(9) / 100, mp.mpf(9) / 100),
                        'ell': col(-2 * eps * lo['psi'], -2 * eps * hi['psi']),
                        'seed_fields': [[mp.nstr(lo['W'], 50)] + ['0.0'] * 7] + [['0.0'] * 8] * (N - 1) + [[mp.nstr(hi['W'], 50)] + ['0.0'] * 7]}
                (base / f'{name}_N{N}.grid.json').write_text(json.dumps(grid))
                (base / f'{name}_N{N}.json').write_text(json.dumps({'proper_separation': mp.nstr(Lref, 50)}))
                files[(name, N)] = (base / f'{name}_N{N}.grid.json', base / f'{name}_N{N}.json', Lref)
    (base / 'SEED.json').write_text(json.dumps({'k': '0.01'}))
    return files


def contexts(base, finite, boxes, C, Dp, Dn, files, recorded=True):
    out = base / 'out'
    P = {'source_dir': finite / 'source', 'case_results': {w: finite / w / 'RESULT.json' for w in CASES},
         'case_dirs': {w: finite / w for w in CASES}, 'fresh_y0': fresh_y0, 'fresh_y0_mu': lambda mu: fresh_y0(),
         'cases': CASES, 'phases': PHASES, 'epsilon': EPS,
         'K': K, 'D_prime': tuple(fmpq(v.numerator, v.denominator) for v in Dp), 'D_prime_matches_record': recorded, 'step': STEP,
         'source_total_cells': TOTAL, 'source_restart_cell': RESTART, 'finite_guard': FGUARD, 'subcells': CONFIG['subcells'],
         'checkpoint_cells': CK, 'C': C, 'old_box': lambda w: boxes[w], 'profile': lambda w: profile(w, Dn), 'degrees': list(DEGREES),
         'seed_path': base / 'SEED.json', 'grid': lambda w, N: files[(w, N)][0], 'record': lambda w, N: files[(w, N)][1],
         'phase_dir': lambda w, n: out / f'phase-{w}-{n}'}
    V4 = {'out': out, 'source_dir': finite / 'source', 'case_results': P['case_results'], 'case_dirs': P['case_dirs'], 'fresh_y0': fresh_y0,
          'fresh_y0_mu': lambda mu: fresh_y0(), 'previous': None,
          'cases': CASES, 'phases': PHASES, 'eps': EPS, 'K': K, 'D_prime': P['D_prime'], 'D_prime_recorded': recorded, 'step': STEP,
          'total': TOTAL, 'restart': RESTART, 'finite_guard': FGUARD, 'm': CONFIG['subcells'], 'ck': CK, 'C': [str(v) for v in C],
          'old_box': lambda w: boxes[w], 'profile': lambda w: profile(w, Dn), 'degrees': list(DEGREES), 'seed_path': base / 'SEED.json',
          'grid': lambda w, N: files[(w, N)][0], 'record': lambda w, N: files[(w, N)][1], 'sample_blocks': [0, 2], 'fixture': True}
    return P, V4


def campaign(base, P, V4, Dp, after_phases=None, previous=None):
    """The production record path, in the production order, with the production stop rule: materials only after all
    four phases complete. A raising job is caught here as the process boundary would."""
    out = base / 'out'
    status = {}
    for w in CASES:
        for n in PHASES:
            try:
                status[f'phase-{w}-{n}'] = reprep.produce_phase(P, w, n, out / f'phase-{w}-{n}', GUARD)
            except Exception as error:
                status[f'phase-{w}-{n}'] = 'FAILED: ' + type(error).__name__
    if after_phases is not None:
        after_phases(out)
    if all(v == 'COMPLETE' for v in status.values()):
        for w in CASES:
            status[f'material-{w}'] = reprep.produce_material(P, w, out / f'material-{w}', GUARD)
    prod = assemble4.assemble(out, CASES, PHASES, Dp, GUARD, previous)
    V4 = V4 | {'previous': previous}
    cases = {w: verify4.verify_case(V4, w) for w in CASES}
    for w, rec in cases.items():
        atomic(base / 'verification' / f'VERIFICATION_{w}.json', rec, True)
    ver = verify4.verify_final(V4, cases)
    atomic(base / 'verification' / 'VERIFICATION.json', ver, True)
    return status, prod, ver


def tamper_checkpoint(folder, pattern, edit):
    target = sorted(Path(folder).glob(pattern))[0]
    body = read(target)
    edit(body)
    target.chmod(0o644)
    target.unlink()
    (Path(folder) / ('-'.join(target.name.split('-')[:2]) + '-' + records.fingerprint(body) + '.json')).write_text(json.dumps(body))


def outcome_files(base):
    return sorted(str(p.relative_to(base)) for p in (base / 'out').glob('*/*') if p.name in ('PHASE.json', 'SUMMARY.json', 'ROOT_INCONSISTENT.json'))


def copy_finite(src, base):
    shutil.copytree(src, base / 'finite')
    for p in (base / 'finite').rglob('*.json'):
        p.chmod(0o644)
    return base / 'finite'


def main_fixture(root):
    base = root / 'main'
    base.mkdir(parents=True)
    lam, st, Dp = background()
    boxes, C = make_finite(base, lam)
    files = write_saved(base, st)
    P, V4 = contexts(base, base / 'finite', boxes, C, Dp, st, files)
    previous = {w: {f: {'bound': 'self', 'bound_exact': '1'} for f in ('A', 'ell', 'Phi')} for w in CASES}
    status, prod, ver = campaign(base, P, V4, Dp, previous=previous)
    A = reprep.stage_a(P, 'positive')
    s = {w: read(base / 'out' / f'material-{w}' / 'SUMMARY.json') for w in CASES}
    with mp.workdps(60):
        cf, c0 = closed(mp.mpf(st.numerator) / st.denominator), closed(mp.mpf(0))
    inside = (lambda e, v: Fraction(e[0]) <= Fraction(mp.nstr(v, 55)) <= Fraction(e[1]))
    walls_ok = all(inside(s[w]['walls']['8']['upper']['state_enclosures'][k], cf[k]) and inside(s[w]['walls']['8']['lower']['state_enclosures'][k], c0[k])
                   for w in CASES for k in ('W', 'H', 'E', 'psi'))
    sep_ok = all(Fraction(s[w]['proper_separation']['enclosure'][0]) <= Fraction(mp.nstr(files[(w, 8)][2], 55)) <= Fraction(s[w]['proper_separation']['enclosure'][1])
                 for w in CASES)
    up = A['jets'][1]
    lam_q = fmpq(lam.numerator, lam.denominator)
    jets_ok = (inside([str(v) for v in bounds(up['psi'][0])], cf['psi']) and inside([str(v) for v in bounds(up['Phi'][0])], mp.mpf(9) / 100)
               and bounds(up['H'])[0] <= lam_q / 6 <= bounds(up['H'])[1] and fq(bounds(up['H'])[1] - bounds(up['H'])[0]) < Fraction(1, 10 ** 200)
               and abs(Fraction(mp.nstr(cf['H'], 55)) - lam / 6) < Fraction(1, 10 ** 50))
    res = {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'], 'verifier_failed': ver['failed'],
           'verifier_checks': ver['checks_total'], 'status': status, 'walls_contain_closed_forms': walls_ok, 'separation_contains_reference': sep_ok,
           'upper_jets_contain_closed_forms': jets_ok, 'D_prime_contains_s_star': Dp[0] <= st <= Dp[1],
           'new_widths': {w: s[w]['krawczyk']['new_widths'] for w in CASES}, 'old_widths': {w: s[w]['krawczyk']['old_widths'] for w in CASES},
           'A_bound': {w: s[w]['fieldsummary']['A']['bound'] for w in CASES}, 'C': [str(v) for v in C],
           'attribution': read(base / 'out' / 'ATTRIBUTION.json').get('label'), 'prediction': read(base / 'out' / 'PREDICTION.json').get('outcome'),
           'prediction_rows': read(base / 'out' / 'PREDICTION.json').get('rows_total'), 'side_records': ver['side_records']}
    return res, base, lam, st, Dp, boxes, C, files


def control_fixture(root, label, main_base, lam, st, Dp, boxes, C, edit=None, recorded=True):
    base = root / label
    base.mkdir(parents=True)
    finite = copy_finite(main_base / 'finite', base)
    if edit is not None:
        edit(finite)
    files = write_saved(base, st)
    P, V4 = contexts(base, finite, boxes, C, Dp, st, files, recorded)
    status, prod, ver = campaign(base, P, V4, Dp)
    return {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'],
            'verifier_failed': ver['failed'], 'outcomes_opened': prod['outcomes_opened'], 'status': status, 'outcome_files': outcome_files(base)}


def root_fixture(root, main_base, lam, st, Dp, boxes, C):
    """A box that misses the root in b1: the Krawczyk image must not meet it."""
    shifted = {}
    for w, (X, c) in boxes.items():
        width = X[2][1] - X[2][0]
        X2 = [X[0], X[1], (X[2][1] + 2 * width, X[2][1] + 3 * width)]
        shifted[w] = (X2, [(a + b) / 2 for a, b in X2])
    base = root / 'root-inconsistent'
    base.mkdir(parents=True)
    finite = copy_finite(main_base / 'finite', base)
    files = write_saved(base, st)
    P, V4 = contexts(base, finite, shifted, C, Dp, st, files)
    status, prod, ver = campaign(base, P, V4, Dp)
    return {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'],
            'verifier_failed': ver['failed'], 'status': status}


def verifier_tamper(root, main_base, st, Dp, boxes, C, files):
    """Producer outputs altered after publication: the verifier must not keep the producer label."""
    base = root / 'verifier-tamper'
    shutil.copytree(main_base, base, ignore=shutil.ignore_patterns('verification'))
    for p in base.rglob('*.json'):
        p.chmod(0o644)
    tamper_checkpoint(base / 'out' / 'material-positive' / 'checkpoints', '*-000064-*.json', lambda b: b['state'].update(max_picard=b['state']['max_picard'] + 1))
    files2 = {k: (base / v[0].name, base / v[1].name, v[2]) for k, v in files.items()}
    P, V4 = contexts(base, base / 'finite', boxes, C, Dp, st, files2)
    cases = {w: verify4.verify_case(V4, w) for w in CASES}
    ver = verify4.verify_final(V4, cases)
    atomic(base / 'verification' / 'VERIFICATION.json', ver, True)
    return {'final': ver['classification'], 'resolved': ver['resolved'], 'verifier_failed': ver['failed']}


def mu_point_fixture(root):
    """Fixture (b): mu at the point 0 makes the C7 background exact (delta = 0, Q_FULL below 2^-500): the attribution
    must be NOT_APPLICABLE without dividing by zero (item 11's exact-background case)."""
    base = root / 'mu-point'
    base.mkdir(parents=True)
    lam, st, Dp = background()
    boxes, C = make_finite(base, lam, mu_point=True)
    files = write_saved(base, st)
    P, V4 = contexts(base, base / 'finite', boxes, C, Dp, st, files)
    status, prod, ver = campaign(base, P, V4, Dp)
    return {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'],
            'verifier_failed': ver['failed'], 'attribution': read(base / 'out' / 'ATTRIBUTION.json').get('label'),
            'prediction': read(base / 'out' / 'PREDICTION.json').get('outcome'), 'side_records': ver['side_records'], 'status': status}


def unit_wall_position():
    """Fixture (c): point jets with a nonzero mismatch and a D ball of K size: the D channel alone carries c7 and W."""
    mk = (lambda xs: [arb(fmpq(*Fraction(x).as_integer_ratio())) for x in xs])
    lower = {'Phi': mk(['99/1000', '-1/100', '1/10', '1/2', '2', '9']), 'psi': mk(['1', '2', '3', '4', '5', '6']),
             'f': mk(['1', '10', '-3', '2', '-1', '5']), 'H': arb(-1), 'T': arb(fmpq(-1, 100)), 'qbg': arb(fmpq(1, 3000)),
             'sigma': 1, 'vi': arb(fmpq(1, 10)), 'lam': arb(6)}
    upper = {'Phi': mk(['88/1000', '2/100', '12/100', '1/2', '2', '9']), 'psi': mk(['55', '110', '225', '466', '1006', '2400']),
             'f': mk(['1', '-2', '-30', '-250', '-1800', '-12000']), 'H': arb(-1), 'T': arb(fmpq(2, 100)), 'qbg': arb(fmpq(2, 1000)),
             'sigma': -1, 'vi': arb(fmpq(9, 100)), 'lam': arb(-6)}
    p = {'m2': arb(fmpq(41, 100)), 'gamma': arb(20), 'D': interval(fmpq(32727, 16384), fmpq(32729, 16384))}
    Dmid, D2, eps = fmpq(4091, 2048), fmpq(32729, 16384), fmpq(1, 200000)
    Q = {v: reprep.attribution_quantities(reprep.variant_preparation(eps, [lower, upper], upper, p, p['D'], Dmid, groups), D2)
         for v, groups in reprep.ATTR_VARIANTS.items()}
    names = ('Q_c7', 'Q_W0', 'Q_W1')
    return {'producer': {q: assemble4.attribution_outcome({v: Q[v][q] for v in Q})['outcome'] for q in names},
            'verifier': {q: verify4.own_outcome({v: Q[v][q] for v in Q})[0] for q in names},
            'Q_full': {q: str(float(Q['FULL'][q])) for q in names}}


def unit_edges():
    """Scoring and attribution decisions at every tolerance edge, in the producer and the verifier."""
    lo, hi = Fraction(99, 100), Fraction(1001, 1000)
    floor, tiny = Fraction(1, 2 ** 500), Fraction(1, 2 ** 60)
    res = []
    for r, want in ((lo, True), (hi, True), (lo - tiny, False), (hi + tiny, False)):
        rows = []
        assemble4.score_row(rows, 'X', 'w', 'q', r, Fraction(1), lo, hi)
        res.append(('score', str(r), (rows[0]['outcome'] == 'CONFIRMED') == want and verify4.own_confirm(r, Fraction(1), lo, hi) == want))
    rows = []
    assemble4.score_row(rows, 'X', 'w', 'q', Fraction(1), floor / 2, lo, hi)
    res.append(('score-floor', None, rows[0]['outcome'] == 'REFUTED' and verify4.own_confirm(Fraction(1), floor / 2, lo, hi) is False))
    rows = []
    assemble4.score_row(rows, 'X', 'w', 'q', Fraction(1), Fraction(1), lo, hi, extra=False)
    res.append(('score-extra', None, rows[0]['outcome'] == 'REFUTED' and verify4.own_confirm(Fraction(1), Fraction(1), lo, hi, False) is False))
    t, n9, one, z = Fraction(1, 10), Fraction(9, 10), Fraction(1), Fraction(0)

    def Qs(full, F, S, B, Z, D, ALL):
        return {'FULL': full, 'F': F, 'S': S, 'B': B, 'Z': Z, 'D': D, 'ALL': ALL}
    for Q, want in ((Qs(one, t, n9, n9, n9, n9, t), 'DECISIVE_F'), (Qs(one, t + tiny, n9, n9, n9, n9, t), 'MIXED'),
                    (Qs(one, t, n9 - tiny, n9, n9, n9, t), 'MIXED'), (Qs(one, t, n9, n9, n9, n9, t + tiny), 'FLOOR_LIMITED'),
                    (Qs(floor, t * floor, n9 * floor, n9 * floor, n9 * floor, n9 * floor, t * floor), 'DECISIVE_F'),
                    (Qs(floor - floor * tiny, z, z, z, z, z, z), 'NOT_APPLICABLE'), (Qs(z, z, z, z, z, z, z), 'NOT_APPLICABLE'),
                    (Qs(one, n9, n9, n9, n9, t, t), 'DECISIVE_D')):
        res.append(('attribution', want, assemble4.attribution_outcome(Q)['outcome'] == want and verify4.own_outcome(Q)[0] == want))
    return {'cases': res, 'all_pass': all(r[2] for r in res)}


def special_fixture(root, label, main_base, st, Dp, boxes, C, files_needed=True, P_edit=None, after_phases=None, V_edit=None):
    base = root / label
    base.mkdir(parents=True)
    finite = copy_finite(main_base / 'finite', base)
    files = write_saved(base, st)
    P, V4 = contexts(base, finite, boxes, C, Dp, st, files)
    if P_edit is not None:
        P = P_edit(P)
    if V_edit is not None:
        V4 = V_edit(V4)
    status, prod, ver = campaign(base, P, V4, Dp, after_phases=after_phases)
    side = {n: (read(base / 'out' / f'{n}.json') if (base / 'out' / f'{n}.json').exists() else None) for n in ('ATTRIBUTION', 'PREDICTION')}
    return {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'],
            'verifier_failed': ver['failed'], 'status': status, 'side_records': ver['side_records'],
            'attribution_record': None if side['ATTRIBUTION'] is None else {k: side['ATTRIBUTION'].get(k) for k in ('assigned', 'reason')},
            'prediction_record': None if side['PREDICTION'] is None else {k: side['PREDICTION'].get(k) for k in ('scored', 'reason')}}


def unit_krawczyk():
    """Linear map G(x) = A (x - x*) with a known root: K(X) must contain x*; a box missing x* must give an empty meet."""
    xs = [Fraction(3, 10 ** 7), Fraction(-2, 10 ** 4), Fraction(5, 10 ** 4)]
    A = [[Fraction(-23, 24), Fraction(1, 10 ** 6), 0], [0, 1, 0], [Fraction(1, 10 ** 3), 0, 1]]
    out = {}
    for label, X in (('contains', [(Fraction(-1, 10 ** 5), Fraction(1, 10 ** 5)), (Fraction(-1, 10 ** 3), Fraction(1, 10 ** 3)), (Fraction(-1, 10 ** 3), Fraction(1, 10 ** 3))]),
                     ('misses', [(Fraction(-1, 10 ** 5), Fraction(1, 10 ** 5)), (Fraction(-1, 10 ** 3), Fraction(1, 10 ** 3)), (Fraction(1, 10 ** 3), Fraction(2, 10 ** 3))])):
        c = [(a + b) / 2 for a, b in X]
        G = [sum(A[i][j] * (c[j] - xs[j]) for j in range(3)) for i in range(3)]
        Gb = [interval(reprep.f2q(g) - fmpq(1, 10 ** 12), reprep.f2q(g) + fmpq(1, 10 ** 12)) for g in G]
        Jb = [interval(reprep.f2q(A[i][j]) - fmpq(1, 10 ** 9), reprep.f2q(A[i][j]) + fmpq(1, 10 ** 9)) for i in range(3) for j in range(3)]
        Cq = [fmpq(-24, 23), fmpq(1), fmpq(1)]
        kr = reprep.krawczyk(Cq, Gb, Jb, X, c)
        own = verify4.exact_krawczyk(['-24/23', '1', '1'], Gb, Jb, X, c)
        rec = {'empty': kr['empty'], 'own_empty': own is None}
        if not kr['empty']:
            Xn = [(Fraction(a), Fraction(b)) for a, b in kr['new_box']]
            rec['contains_root'] = all(a <= x <= b for (a, b), x in zip(Xn, xs))
            rec['own_inside_producer'] = own is not None and all(pa <= oa <= ob <= pb for (pa, pb), (oa, ob) in zip(Xn, own))
            rec['own_contains_root'] = own is not None and all(a <= x <= b for (a, b), x in zip(own, xs))
        out[label] = rec
    return out


def run_all():
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    root = RUN / 'preflight' / stamp
    root.mkdir(parents=True)
    t0 = time.monotonic()
    units = unit_krawczyk()
    main, mbase, lam, st, Dp, boxes, C, files = main_fixture(root)

    def bump_source(fin):
        tamper_checkpoint(fin / 'source' / 'checkpoints', f'00-{TOTAL:06d}-*.json', lambda b: b['state'].update(max_picard=b['state']['max_picard'] + 1))

    def bump_phase(fin):
        tamper_checkpoint(fin / 'positive' / 'checkpoints', f'01-{TOTAL:06d}-*.json', lambda b: b['state'].update(max_picard=b['state']['max_picard'] + 1))

    def bump_prep(fin):
        p = fin / 'positive' / 'RESULT.json'
        body = records.unpack(read(p))
        body['preparation']['c7'][4] = body['preparation']['c7'][4] + arb(fmpq(1, 2 ** 700))
        p.unlink()
        atomic(p, records.pack(body))
    r0 = control_fixture(root, 'source-tamper', mbase, lam, st, Dp, boxes, C, bump_source)
    r0m = control_fixture(root, 'phase-map-tamper', mbase, lam, st, Dp, boxes, C, bump_phase)
    r0p = control_fixture(root, 'preparation-tamper', mbase, lam, st, Dp, boxes, C, bump_prep)
    d0 = control_fixture(root, 'D-prime-unrecorded', mbase, lam, st, Dp, boxes, C, None, recorded=False)
    rk = root_fixture(root, mbase, lam, st, Dp, boxes, C)
    vt = verifier_tamper(root, mbase, st, Dp, boxes, C, files)
    mu = mu_point_fixture(root)
    wp = unit_wall_position()
    edges = unit_edges()

    def broken(P):
        def box(w):
            if w == 'negative':
                raise RuntimeError('fixture: injected phase failure')
            return boxes[w]
        return P | {'old_box': box}
    rf = special_fixture(root, 'raising-phase', mbase, st, Dp, boxes, C, P_edit=broken)
    saved = (reprep.CLOSURE_RADIUS, reprep.CLOSURE_FLOOR, verify4.RADIUS, verify4.FLOOR)
    reprep.CLOSURE_RADIUS = reprep.CLOSURE_FLOOR = verify4.RADIUS = verify4.FLOOR = Fraction(0)
    try:
        zs = special_fixture(root, 'zero-slack-closure', mbase, st, Dp, boxes, C)
    finally:
        reprep.CLOSURE_RADIUS, reprep.CLOSURE_FLOOR, verify4.RADIUS, verify4.FLOOR = saved

    def tamper_fp(out):
        p = out / 'phase-positive-center' / 'PHASE.json'
        body = read(p)
        body['fingerprints']['jets'] = '0' * 64
        p.chmod(0o644)
        p.unlink()
        atomic(p, body, True)
    fp = special_fixture(root, 'fingerprint-tamper', mbase, st, Dp, boxes, C, after_phases=tamper_fp)

    def raising_mu(ctx_):
        def bad(mu):
            raise RuntimeError('fixture: injected point-mu start-state failure')
        return ctx_ | {'fresh_y0_mu': bad}
    se = special_fixture(root, 'side-computation-error', mbase, st, Dp, boxes, C, P_edit=raising_mu, V_edit=raising_mu)
    prev = assemble4.previous_bounds()
    expect = {
        'main_label': main['label'].startswith('REPREPARED__A_DOMINATED_BY_') and main['final'] == main['label'] and main['resolved'],
        'main_walls': main['walls_contain_closed_forms'], 'main_separation': main['separation_contains_reference'],
        'main_upper_jets': main['upper_jets_contain_closed_forms'], 'main_D_prime': main['D_prime_contains_s_star'],
        'source_tamper_label': r0['label'] == 'TECHNICAL_REPLAY_MISMATCH' and r0['final'] == r0['label'] and r0['resolved']
        and not r0['outcomes_opened'] and not r0['outcome_files'],
        'phase_map_tamper_label': r0m['label'] == 'TECHNICAL_REPLAY_MISMATCH' and r0m['final'] == r0m['label'] and r0m['resolved']
        and not r0m['outcomes_opened'] and not r0m['outcome_files'],
        'preparation_tamper_label': r0p['label'] == 'PREPARATION_PIPELINE_MISMATCH' and r0p['final'] == r0p['label'] and r0p['resolved']
        and not r0p['outcomes_opened'] and not r0p['outcome_files'],
        'D_prime_unrecorded_label': d0['label'] == 'PREPARATION_PIPELINE_MISMATCH' and d0['final'] == d0['label'] and d0['resolved']
        and not d0['outcome_files'],
        'root_inconsistent_label': rk['label'] == 'ROOT_ITERATION_INCONSISTENT' and rk['final'] == rk['label'] and rk['resolved'],
        'verifier_tamper_unresolved': vt['final'] == 'UNRESOLVED_VERIFICATION' and 'VM1.positive.all_material_blocks_bitwise' in vt['verifier_failed'],
        'unit_contains_root': units['contains']['contains_root'] and units['contains']['own_contains_root'] and units['contains']['own_inside_producer'],
        'unit_misses_empty': units['misses']['empty'] and units['misses']['own_empty'],
        'main_attribution_assigned_and_verified': str(main['attribution']).startswith('NEXT_WIDTH__MODE_JET_RADIUS')
        and main['side_records']['attribution_verification'] == 'AGREES',
        'main_prediction_scored_and_verified': main['prediction'] in ('NEAR_NULL_CONFIRMED', 'NEAR_NULL_REFUTED') and main['prediction_rows'] == 37
        and main['side_records']['prediction_verification'] == 'AGREES',
        'mu_point_not_applicable': str(mu['attribution']).startswith('ATTRIBUTION_NOT_APPLICABLE') and mu['resolved']
        and mu['final'] == mu['label'] and mu['side_records']['attribution_verification'] == 'AGREES'
        and mu['side_records']['prediction_verification'] == 'AGREES',
        'unit_wall_position': all(v == 'DECISIVE_D' for v in wp['producer'].values()) and all(v == 'DECISIVE_D' for v in wp['verifier'].values()),
        'unit_edges': edges['all_pass'],
        'raising_phase_label': rf['label'] == 'TECHNICAL_INCOMPLETE' and rf['final'] == rf['label'] and rf['resolved'],
        'zero_slack_label': zs['label'] == 'BUDGET_NOT_CLOSED' and zs['final'] == zs['label'] and zs['resolved']
        and zs['side_records']['attribution_verification'] == 'AGREES',
        'fingerprint_tamper_label': fp['label'] == 'TECHNICAL_REPLAY_MISMATCH' and fp['final'] == fp['label'] and fp['resolved'],
        'previous_bounds_readable': all(f in prev[w] for w in CASES for f in ('A', 'ell', 'Phi')),
        'side_error_isolated': se['label'].startswith('REPREPARED__') and se['final'] == se['label'] and se['resolved']
        and se['attribution_record'] == {'assigned': False, 'reason': 'side computation error'}
        and se['prediction_record'] == {'scored': False, 'reason': 'side computation error'}
        and se['side_records']['attribution_verification'] == 'ERROR' and se['side_records']['prediction_verification'] == 'ERROR'}
    passed = all(expect.values())
    result = {'passed': passed, 'utc': now(), 'real_data_outcomes_computed': False, 'physical_outcomes': False, 'expectations': expect,
              'fixtures': {'main': main, 'source_tamper': r0, 'phase_map_tamper': r0m, 'preparation_tamper': r0p, 'D_prime_unrecorded': d0,
                           'root_inconsistent': rk, 'verifier_tamper': vt, 'unit_krawczyk': units, 'mu_point': mu,
                           'unit_wall_position': wp, 'unit_edges': edges, 'raising_phase': rf, 'zero_slack_closure': zs,
                           'fingerprint_tamper': fp, 'previous_bounds': prev, 'side_computation_error': se},
              'sources': source_hashes(), 'runtime': runtime_fingerprint(), 'config': CONFIG, 'address_space': limits,
              'seconds': time.monotonic() - t0,
              'production_size_elements': {'arb_bits': CONFIG['arb_bits'], 'subcells': CONFIG['subcells'], 'cells': TOTAL,
                                           'checkpoint_cells': CK, 'preconditioner': [str(v) for v in C]}}
    atomic(root / 'PREFLIGHT.json', result, True)
    print(json.dumps({'passed': passed, 'path': str(root / 'PREFLIGHT.json'), 'expectations': expect,
                      'labels': {'main': main['label'], 'source_tamper': r0['label'], 'phase_map_tamper': r0m['label'],
                                 'preparation_tamper': r0p['label'], 'D_prime_unrecorded': d0['label'], 'root': rk['label'], 'vtamper': vt['final'],
                                 'mu_point': mu['label'], 'raising': rf['label'], 'zero_slack': zs['label'], 'fingerprint': fp['label'],
                                 'side_error': se['label']},
                      'attribution': {'main': main['attribution'], 'mu_point': mu['attribution'], 'unit_wall_position': wp['producer']},
                      'prediction': {'main': main['prediction'], 'mu_point': mu['prediction']},
                      'failed': {'main': main['verifier_failed'], 'r0': r0['verifier_failed'], 'r0m': r0m['verifier_failed'],
                                 'r0p': r0p['verifier_failed'], 'd0': d0['verifier_failed'], 'root': rk['verifier_failed'], 'vt': vt['verifier_failed'],
                                 'mu': mu['verifier_failed'], 'raising': rf['verifier_failed'], 'zero_slack': zs['verifier_failed'],
                                 'fingerprint': fp['verifier_failed']},
                      'widths': {'old': main['old_widths'], 'new': main['new_widths']}, 'A': main['A_bound'],
                      'seconds': round(time.monotonic() - t0)}, indent=1, default=str), flush=True)
    return passed


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'all':
        raise SystemExit('usage: preflight4.py all')
    sys.exit(0 if run_all() else 3)
