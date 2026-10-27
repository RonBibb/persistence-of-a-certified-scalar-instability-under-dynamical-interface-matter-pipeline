"""Synthetic-only pre-freeze controls for run 20261006T230904Z. No real outcome is computed.

Manufactured background (m2 = 0, T = 0): H(s) = -sqrt(k) tan(sqrt(k) s), E = 1/cos(sqrt(k) s),
W = log cos(sqrt(k) s), psi = 1/cos^2(sqrt(k) s); lambda_b = 6 H(s_star) puts the Israel crossing at a
known point. Three flows (mode, positive, negative) are integrated by the inherited engine at 768 bits with
the inherited checkpoint writer: 513 cells at step 1/256, K = [2 - 1/512, 2 + 1/512], seam 2, 2048 event
subintervals per half and 64 subcells as in production. Every fixture runs the production record path:
narrow.produce -> assemble3.assemble -> verify3.verify, all written through common3.atomic.
    python -B <run>/code/preflight3.py all
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
import identity_run as ir  # noqa: E402
from series import interval  # noqa: E402
import narrow  # noqa: E402
import assemble3  # noqa: E402
import verify3  # noqa: E402
from common3 import RUN, CONFIG, now, read, atomic, fq, source_hashes, runtime_fingerprint, check_environment, limit_address_space  # noqa: E402

STEP = fmpq(1, 256)
DHI = fmpq(1025, 512)
DLO = fmpq(1023, 512)
SEAM = fmpq(2)
GUARD = 'fixture-guard'
V1 = fmpq(9, 100)
EPS = {'positive': fmpq(1, 200000), 'negative': fmpq(-1, 200000)}
TASK = {'mode': 0, 'positive': 1, 'negative': 2}
FLOWS = ['mode', 'positive', 'negative']
PIECE = (Fraction(1025, 512) - Fraction(1023, 512)) / 2 / CONFIG['event_subintervals_per_half']


def lam_for(s_star):
    with mp.workdps(120):
        H = -mp.mpf('0.1') * mp.tan(mp.mpf('0.1') * mp.mpf(s_star.numerator) / s_star.denominator)
        return Fraction(mp.nstr(6 * H, 110))


def true_crossing(lam):
    with mp.workdps(120):
        return mp.mpf(10) * mp.atan(-mp.mpf(lam.numerator) / lam.denominator * 10 / 6)


def fresh(name, lam, h0):
    p = {'m2': arb(0), 'mu': interval(fmpq(-132, 100000), fmpq(-131, 100000)),
         'k': interval(fmpq(1, 100) - fmpq(1, 10 ** 12), fmpq(1, 100) + fmpq(1, 10 ** 12)),
         'gamma': arb(20), 'v0': arb(fmpq(1, 10)), 'v1': arb(V1), 'lambda_a': arb(6), 'lambda_b': arb(fmpq(lam.numerator, lam.denominator))}
    P0 = interval(V1 - fmpq(1, 10 ** 10), V1 + fmpq(1, 10 ** 10))
    base = [arb(0), interval(-h0, h0), P0, arb(0), arb(1), arb(1), arb(1), arb(0), arb(0)]
    if name == 'mode':
        y, nf = base + [arb(0), arb(0), arb(0)], 8
    else:
        p |= {'D': interval(DLO, DHI), 'eps': EPS[name], 'c7': [arb(0)] * 8,
              'x': [interval(-fmpq(1, 10 ** 6), fmpq(1, 10 ** 6)), interval(-fmpq(1, 1000), fmpq(1, 1000)), interval(-fmpq(1, 1000), fmpq(1, 1000))]}
        y, nf = base + [p['x'][0], arb(0)], 3
    return {'task_index': TASK[name], 'cell_index': 0, 'name': name, 'y': y, 'p': p, 'max_errors': [fmpq(0)] * nf,
            'event_derivative': None, 'event_cover': [], 'elapsed_seconds': 0.0, 'integration_cpu_seconds': 0.0,
            'max_picard': 0, 'domain_maxima': [fmpq(0)] * len(y), 'capacity': {}}


def closed(s):
    c = mp.cos(mp.mpf('0.1') * s)
    return {'W': mp.log(c), 'H': -mp.mpf('0.1') * mp.tan(mp.mpf('0.1') * s), 'E': 1 / c, 'psi': 1 / (c * c)}


_PROFILES = {}


def profile(name, Dn):
    key = (name, str(Dn))
    if key not in _PROFILES:
        pr = ir.SavedProfile.__new__(ir.SavedProfile)
        pr.D = fmpq(Dn.numerator, Dn.denominator)
        pr.h = fmpq(1, 8)
        pieces, metric = [], []
        with mp.workdps(60):
            for i in range(16):
                s0 = mp.mpf(i) / 8
                rows = []
                for key2 in ('W', 'H', 'P', 'T', 'E', 'psi', 'f', 'g'):
                    if key2 in ('W', 'H', 'E', 'psi'):
                        co = mp.taylor(lambda s, key2=key2: closed(s)[key2], s0, 14)
                        rows.append([arb(fmpq(*Fraction(mp.nstr(c, 55)).as_integer_ratio())) for c in co])
                    else:
                        rows.append([arb(V1)] if key2 == 'P' else [arb(1)] if key2 == 'f' else [arb(0)])
                pieces.append(rows)
                if name != 'mode':
                    eps = mp.mpf(int(EPS[name].p)) / int(EPS[name].q)
                    co = mp.taylor(lambda s: closed(s)['W'] + eps * closed(s)['psi'], s0, 14)
                    metric.append([arb(fmpq(*Fraction(mp.nstr(c, 55)).as_integer_ratio())) for c in co])
        pr.seed = pieces
        if name == 'mode':
            pr.case = None
        else:
            pr.case, pr.eps, pr.metric, pr.correction = 3, arb(EPS[name]), metric, [arb(0)]
        _PROFILES[key] = pr
    return _PROFILES[key]


def write_saved(base, Dn, degrees):
    files = {}
    with mp.workdps(60):
        top = mp.mpf(Dn.numerator) / Dn.denominator
        lo, hi = closed(mp.mpf(0)), closed(top)
        for name in ('positive', 'negative'):
            eps = mp.mpf(int(EPS[name].p)) / int(EPS[name].q)
            Lref = mp.quad(lambda s: mp.exp(-2 * eps * closed(s)['psi']), [0, top])
            for N in degrees:
                def col(v0, vN):
                    return [mp.nstr(v0, 50)] + ['0.0'] * (N - 1) + [mp.nstr(vN, 50)]
                A0, AN = lo['W'] + eps * lo['psi'], hi['W'] + eps * hi['psi']
                grid = {'A': col(A0, AN), 'B': col(A0, AN), 'Phi': col(mp.mpf(9) / 100, mp.mpf(9) / 100),
                        'ell': col(-2 * eps * lo['psi'], -2 * eps * hi['psi']),
                        'seed_fields': [[mp.nstr(lo['W'], 50)] + ['0.0'] * 7] + [['0.0'] * 8] * (N - 1) + [[mp.nstr(hi['W'], 50)] + ['0.0'] * 7]}
                (base / f'{name}_N{N}.grid.json').write_text(json.dumps(grid))
                (base / f'{name}_N{N}.json').write_text(json.dumps({'proper_separation': mp.nstr(Lref, 50)}))
                files[(name, N)] = (base / f'{name}_N{N}.grid.json', base / f'{name}_N{N}.json', Lref)
        L0 = mp.nstr(top, 50)
        for N in degrees:
            (base / f'case0_N{N}.json').write_text(json.dumps({'proper_separation': L0}))
    (base / 'SEED.json').write_text(json.dumps({'k': '0.01'}))
    return files


def context(base, name, lam, h0, Dn, ckdirs, degrees, files, flows=FLOWS):
    return {'name': name, 'flows': flows, 'task_of': TASK, 'profile': profile(name, Dn),
            'profiles': {f: profile(f, Dn) for f in flows}, 'Dlo': DLO, 'Dhi': DHI, 'seam': SEAM,
            'event_M': CONFIG['event_subintervals_per_half'], 'event_cells': [511, 512], 'step': STEP, 'subcells': CONFIG['subcells'],
            'checkpoint_dirs': ckdirs, 'expected_checkpoint_cells': [256, 512, 513], 'guard': GUARD,
            'fresh_states': {f: (lambda f=f: fresh(f, lam, h0)) for f in flows}, 'degrees': degrees, 'seed_path': base / 'SEED.json',
            'grid': (lambda N: files[(name, N)][0]), 'record': (lambda N: files[(name, N)][1]), 'progress': lambda a, b: None}


def generate(base, name, lam, h0, Dn):
    out = base / f'flow-{name}'
    P = {'Dlo': DLO, 'Dhi': DHI, 'step': STEP}
    state = fresh(name, lam, h0)
    while state['cell_index'] * STEP < DHI:
        state = narrow.replay_block(name, state, P, profile(name, Dn))
        records.save(out, state, GUARD)
    return out / 'checkpoints', [str(v) for v in state['max_errors']]


def pipeline(base, lam, h0, Dn, ckdirs, finals, degrees=(8, 12)):
    """Production record path on a fixture: produce x3 -> assemble -> verify; all records through common3.atomic."""
    files = write_saved(base, Dn, degrees)
    out = base / 'out'
    status = {}
    for f in FLOWS:
        P = context(base, f, lam, h0, Dn, ckdirs, list(degrees), files)
        status[f] = narrow.produce(P, out / f, GUARD, finals[f])
    case0 = {N: base / f'case0_N{N}.json' for N in degrees}
    prod = assemble3.assemble(out, FLOWS, finals, (Fraction(1023, 512), Fraction(1025, 512)), GUARD, case0)
    C = {'flows': FLOWS, 'out': out, 'Dlo': DLO, 'Dhi': DHI, 'seam': SEAM, 'M': CONFIG['event_subintervals_per_half'],
         'event_cells': [511, 512], 'step': STEP, 'm': CONFIG['subcells'], 'profile': lambda flow: profile(flow, Dn), 'task': TASK,
         'ckdir': ckdirs, 'fresh': lambda flow: fresh(flow, lam, h0), 'grid': lambda flow, N: files[(flow, N)][0],
         'seed_path': base / 'SEED.json', 'case0': case0, 'degrees': list(degrees), 'sample_blocks': [0, 2], 'fixture': True}
    ver = verify3.verify(C)
    atomic(base / 'verification' / 'VERIFICATION.json', ver, True)
    return status, prod, ver, files


def crossing_fixture(root, label, s_star, h0):
    base = root / label
    base.mkdir(parents=True)
    lam = lam_for(s_star)
    s_true = true_crossing(lam)
    Dn = Fraction(mp.nstr(s_true, 60))
    ckdirs, finals = {}, {}
    for f in FLOWS:
        ckdirs[f], finals[f] = generate(base, f, lam, h0, Dn)
    status, prod, ver, files = pipeline(base, lam, h0, Dn, ckdirs, finals)
    iv = [Fraction(v) for v in prod['narrowed_interval']]
    st = Fraction(mp.nstr(s_true, 60))
    pos = read(base / 'out' / 'positive' / 'SUMMARY.json')
    up = pos['walls']['8']['upper']['state_enclosures']
    with mp.workdps(60):
        cf = closed(mp.mpf(st.numerator) / st.denominator)
        c0 = closed(mp.mpf(0))
    contains = lambda e, v: Fraction(e[0]) <= Fraction(mp.nstr(v, 55)) <= Fraction(e[1])
    lw = pos['walls']['8']['lower']['state_enclosures']
    res = {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'],
           'verifier_failed': ver['failed'], 'verifier_checks': ver['checks_total'],
           'narrowed_contains_true_crossing': iv[0] <= st <= iv[1], 'width_pieces': float((iv[1] - iv[0]) / PIECE),
           'upper_wall_state_contains_closed_forms': all(contains(up[k], cf[k]) for k in ('W', 'H', 'E', 'psi')),
           'lower_wall_state_contains_closed_forms': all(contains(lw[k], c0[k]) for k in ('W', 'H', 'E', 'psi')),
           'separation_contains_reference': all(Fraction(read(base / 'out' / f / 'SUMMARY.json')['proper_separation']['enclosure'][0])
                                                <= Fraction(mp.nstr(files[(f, 8)][2], 55)) <=
                                                Fraction(read(base / 'out' / f / 'SUMMARY.json')['proper_separation']['enclosure'][1])
                                                for f in ('positive', 'negative')),
           'A_bound': pos['fieldsummary']['A']['bound'], 'excluded_by_e_I': pos['event']['per_flow']['mode']['excluded_by_e_I']}
    return res, base, lam, h0, Dn, ckdirs, finals


def tamper_fixture(root, seam_base, lam, h0, Dn, finals):
    base = root / 'tamper'
    base.mkdir(parents=True)
    ckdirs = {}
    for f in FLOWS:
        ckdirs[f] = base / f'flow-{f}' / 'checkpoints'
        shutil.copytree(seam_base / f'flow-{f}' / 'checkpoints', ckdirs[f])
    target = sorted(ckdirs['mode'].glob('*-000512-*.json'))[0]
    body = read(target)
    body['state']['max_picard'] = body['state']['max_picard'] + 1
    target.unlink()
    (ckdirs['mode'] / ('-'.join(target.name.split('-')[:2]) + '-' + records.fingerprint(body) + '.json')).write_text(json.dumps(body))
    status, prod, ver, _ = pipeline(base, lam, h0, Dn, ckdirs, finals)
    return {'label': prod['classification_provisional'], 'final': ver['classification'], 'resolved': ver['resolved'],
            'verifier_failed': ver['failed']}


def inconsistent_fixture(root):
    base = root / 'inconsistent'
    base.mkdir(parents=True)
    lam = lam_for(Fraction(199, 100))
    Dn = Fraction(2)
    h0 = fmpq(1, 10 ** 15)
    ckdirs, finals = {}, {}
    for f in FLOWS:
        ckdirs[f], finals[f] = generate(base, f, lam, h0, Dn)
    status, prod, ver, _ = pipeline(base, lam, h0, Dn, ckdirs, finals)
    return {'producer_status': status, 'label': prod['classification_provisional'], 'final': ver['classification'],
            'resolved': ver['resolved'], 'verifier_failed': ver['failed']}


def not_narrowed_label(root, seam_base):
    """Label path for D' = K: copy a fixture output, set the common interval to K, re-assemble."""
    out = root / 'not-narrowed'
    shutil.copytree(seam_base / 'out', out, ignore=shutil.ignore_patterns('PRODUCER_RESULT.json'))
    for f in FLOWS:
        p = out / f / 'SUMMARY.json'
        p.chmod(0o644)
        s = read(p)
        s['event']['common_narrowed_interval'] = [str(DLO), str(DHI)]
        p.write_text(json.dumps(s))
    finals = {f: read(out / f / 'SUMMARY.json')['accepted_max_errors_exact'] for f in FLOWS}
    prod = assemble3.assemble(out, FLOWS, finals, (Fraction(1023, 512), Fraction(1025, 512)), GUARD,
                              {N: seam_base / f'case0_N{N}.json' for N in (8, 12)})
    return prod['classification_provisional']


def unit_models():
    """Synthetic cell models: e_I = 0.05 (s - s*), e_R = (t1 + 10 p1)(s - s*) with s* inside cell 511's half of K."""
    s_star = fmpq(2) - fmpq(1, 2048)
    lam, v1, gamma, h1, p1, t1 = fmpq(-6, 100), V1, 20, fmpq(5, 100), fmpq(2, 1000), fmpq(3, 1000)
    p = {'lambda_b': arb(lam), 'v1': arb(v1), 'gamma': arb(gamma), 'k': arb(fmpq(1, 100))}

    def model(t0, h, robin_offset=fmpq(0)):
        d0 = t0 - s_star
        Pc = [v1 + p1 * d0, p1]
        Hc = [lam / 6 + h1 * d0 + gamma * p1 * p1 * d0 * d0 / 12, h1 + gamma * p1 * p1 * d0 / 6, gamma * p1 * p1 / 12]
        Tc = [t1 * d0 + robin_offset, t1]
        rows = [[arb(0)], [arb(c) for c in Hc], [arb(c) for c in Pc], [arb(c) for c in Tc], [arb(1)]]
        rows = [[(r[j] if j < len(r) else arb(0)) + (interval(-fmpq(1, 10 ** 9), fmpq(1, 10 ** 9)) if j == 0 else 0) for j in range(5)] for r in rows]
        return {'h': h, 'coeff': rows, 'remainder': [arb(0)] * 5}
    P = {'Dlo': DLO, 'Dhi': DHI, 'seam': SEAM, 'event_M': CONFIG['event_subintervals_per_half'], 'event_cells': [511, 512]}
    good = {511: (fmpq(511, 256), fmpq(1, 256), model(fmpq(511, 256), fmpq(1, 256)), p),
            512: (fmpq(2), fmpq(1, 512), model(fmpq(2), fmpq(1, 512)), p)}
    iv, rec = narrow.narrow_flow(good, P)
    flipped = {511: (fmpq(511, 256), fmpq(1, 256), model(fmpq(511, 256), fmpq(1, 256), fmpq(1, 10)), p),
               512: (fmpq(2), fmpq(1, 512), model(fmpq(2), fmpq(1, 512), fmpq(1, 10)), p)}
    iv2, rec2 = narrow.narrow_flow(flipped, P)
    return {'contains_s_star': iv is not None and iv[0] <= s_star <= iv[1], 'excluded_by_e_I': rec['excluded_by_e_I'],
            'excluded_by_e_R': rec['excluded_by_e_R'], 'both_functions_exclude': rec['excluded_by_e_I'] > 0 and rec['excluded_by_e_R'] > 0,
            'sign_flipped_robin_gives_empty': iv2 is None, 'kept': rec['kept']}


def run_all():
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    root = RUN / 'preflight' / stamp
    root.mkdir(parents=True)
    t0 = time.monotonic()
    units = unit_models()
    seam, seam_base, lam, h0, Dn, ckdirs, finals = crossing_fixture(root, 'seam', Fraction(2), fmpq(1, 10 ** 15))
    inflated, *_ = crossing_fixture(root, 'inflated-interior', Fraction(2) - Fraction(37, 102400), fmpq(1, 10 ** 7))
    tam = tamper_fixture(root, seam_base, lam, h0, Dn, finals)
    inc = inconsistent_fixture(root)
    nn = not_narrowed_label(root, seam_base)
    expect = {
        'seam_label': seam['label'].startswith('DSTAR_NARROWED__') and seam['final'] == seam['label'] and seam['resolved'],
        'seam_contains': seam['narrowed_contains_true_crossing'], 'seam_walls': seam['upper_wall_state_contains_closed_forms'] and seam['lower_wall_state_contains_closed_forms'],
        'seam_separation': seam['separation_contains_reference'],
        'inflated_label': inflated['label'].startswith('DSTAR_NARROWED__') and inflated['final'] == inflated['label'] and inflated['resolved'],
        'inflated_contains': inflated['narrowed_contains_true_crossing'], 'inflated_radius_limited': inflated['width_pieces'] >= 3,
        'inflated_walls': inflated['upper_wall_state_contains_closed_forms'] and inflated['lower_wall_state_contains_closed_forms'],
        'inflated_separation': inflated['separation_contains_reference'],
        'tamper_label': tam['label'] == 'ACCEPTED_FLOW_REPLAY_MISMATCH' and tam['final'] == tam['label'] and tam['resolved'],
        'inconsistent_label': inc['label'] == 'EVENT_EXCLUSION_INCONSISTENT' and inc['final'] == inc['label'] and inc['resolved'],
        'not_narrowed_label': nn.startswith('DSTAR_NOT_NARROWED__'),
        'unit_contains': units['contains_s_star'], 'unit_both_exclude': units['both_functions_exclude'],
        'unit_flipped_empty': units['sign_flipped_robin_gives_empty']}
    passed = all(expect.values())
    result = {'passed': passed, 'utc': now(), 'real_data_outcomes_computed': False, 'physical_outcomes': False,
              'expectations': expect, 'fixtures': {'seam': seam, 'inflated_interior': inflated, 'tamper': tam, 'inconsistent': inc,
                                                   'not_narrowed_label': nn, 'unit_models': units},
              'sources': source_hashes(), 'runtime': runtime_fingerprint(), 'config': CONFIG, 'address_space': limits,
              'seconds': time.monotonic() - t0,
              'production_size_elements': {'arb_bits': CONFIG['arb_bits'], 'event_subintervals_per_half': CONFIG['event_subintervals_per_half'],
                                           'subcells': CONFIG['subcells'], 'cells': 513}}
    atomic(root / 'PREFLIGHT.json', result, True)
    print(json.dumps({'passed': passed, 'path': str(root / 'PREFLIGHT.json'), 'expectations': expect,
                      'labels': {'seam': seam['label'], 'inflated': inflated['label'], 'tamper': tam['label'], 'inconsistent': inc['label'], 'not_narrowed': nn},
                      'widths': {'seam': seam['width_pieces'], 'inflated': inflated['width_pieces']}, 'units': units,
                      'failed': {'seam': seam['verifier_failed'], 'inflated': inflated['verifier_failed'], 'tamper': tam['verifier_failed'],
                                 'inconsistent': inc['verifier_failed']}, 'seconds': round(time.monotonic() - t0)}, indent=1, default=str), flush=True)
    return passed


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'all':
        raise SystemExit('usage: preflight3.py all')
    sys.exit(0 if run_all() else 3)
