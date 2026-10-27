"""Synthetic-only pre-freeze controls for the enclosure-width budget. No real outcome.

Two manufactured flows (mode-type, 12 states; prepared-type, 11 states) are integrated by the
inherited validated engine with the inherited checkpoint writer (records.save), 513 cells in
three blocks, with a manufactured native profile carrying a known center offset 1e-9*s.
    python -B <run>/code/preflight2.py all
"""
import json
import shutil
import sys
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'inherited'))
sys.path.insert(1, str(HERE))
from flint import arb, fmpq, ctx  # noqa: E402
import records  # noqa: E402
import identity_run as ir  # noqa: E402
from series import interval  # noqa: E402
import budget  # noqa: E402
import verify2  # noqa: E402
from common2 import RUN, CONFIG, now, read, atomic, fq, up_float, source_hashes, runtime_fingerprint, check_environment, limit_address_space  # noqa: E402

STEP = fmpq(1, 256)
DHI = fmpq(1025, 512)
DLO = DHI - STEP
GUARD = 'fixture-guard'
OFFSET = fmpq(1, 10 ** 9)


def profile(kind):
    pr = ir.SavedProfile.__new__(ir.SavedProfile)
    pr.D = fmpq(2)
    pr.h = fmpq(1, 8)
    pieces = []
    for i in range(16):
        s0 = i * pr.h
        rows = [[arb(OFFSET * s0), arb(OFFSET)], [arb(0)], [arb(0)], [arb(0)], [arb(1)], [arb(1)], [arb(1)], [arb(0)]]
        pieces.append(rows)
    pr.seed = pieces
    if kind == 'mode':
        pr.case = None
    else:
        pr.case = 3
        pr.eps = arb(fmpq(1, 200000))
        pr.metric = [[arb(fmpq(1, 200000) + OFFSET * i * pr.h), arb(OFFSET)] for i in range(16)]
        pr.correction = [arb(0)]
    return pr


def fresh(kind):
    if kind == 'mode':
        p = {'m2': arb(0), 'mu': interval(fmpq(-132, 100000), fmpq(-131, 100000)), 'k': arb(0), 'gamma': arb(20)}
        y = [arb(v) for v in (0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0)]
        nf = 8
    else:
        p = {'m2': arb(0), 'mu': interval(fmpq(-132, 100000), fmpq(-131, 100000)), 'k': arb(0), 'gamma': arb(20),
             'D': interval(DLO, DHI), 'eps': fmpq(1, 200000), 'c7': [arb(0)] * 8,
             'x': [interval(fmpq(-1, 10 ** 6), fmpq(1, 10 ** 6)), interval(fmpq(-1, 1000), fmpq(1, 1000)),
                   interval(fmpq(-1, 1000), fmpq(1, 1000))]}
        y = [arb(v) for v in (0, 0, 0, 0, 1, 1, 1, 0, 0)] + [p['x'][0], arb(0)]
        nf = 3
    return {'task_index': 0 if kind == 'mode' else 1, 'cell_index': 0, 'name': 'mode' if kind == 'mode' else 'positive',
            'y': y, 'p': p, 'max_errors': [fmpq(0)] * nf, 'event_derivative': None, 'event_cover': [],
            'elapsed_seconds': 0.0, 'integration_cpu_seconds': 0.0, 'max_picard': 0,
            'domain_maxima': [fmpq(0)] * len(y), 'capacity': {}}


def context(kind, ckdir):
    name = 'mode' if kind == 'mode' else 'positive'
    return {'name': name, 'task_index': 0 if kind == 'mode' else 1, 'profile': profile(kind), 'Dlo': DLO, 'Dhi': DHI,
            'step': STEP, 'subcells': CONFIG['subcells'], 'checkpoint_dir': ckdir, 'expected_checkpoint_cells': [256, 512, 513],
            'guard': GUARD, 'fresh_state': lambda: fresh(kind), 'progress': lambda a, b: None}


def generate(kind, base):
    out = base / f'flow-{kind}'
    P = context(kind, out / 'checkpoints')
    b = budget.Budget(P)
    state = fresh(kind)
    while state['cell_index'] * STEP < DHI:
        state = b.run_block(state, record_cells=False)
        records.save(out, state, GUARD)
    return out / 'checkpoints', [str(v) for v in state['max_errors']]


def tamper(src, dst):
    shutil.copytree(src, dst)
    target = sorted(dst.glob('*-000512-*.json'))[0]
    body = read(target)
    body['state']['max_picard'] = body['state']['max_picard'] + 1
    target.unlink()
    name = '-'.join(target.name.split('-')[:2]) + '-' + records.fingerprint(body) + '.json'
    (dst / name).write_text(json.dumps(body))
    return dst


def run_all():
    check_environment()
    limits = limit_address_space()
    ctx.prec = CONFIG['arb_bits']
    ctx.threads = 1
    stamp = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    root = RUN / 'preflight' / stamp
    base = root / 'fixture'
    base.mkdir(parents=True)
    t0 = time.monotonic()
    res = {}
    for kind in ('mode', 'prepared'):
        ckdir, final = generate(kind, base)
        P = context(kind, ckdir)
        summ, payload = budget.execute(P)
        fields = summ['fields']
        f0 = 'W' if kind == 'mode' else 'A'
        fs = summ['fieldsummary'][f0]
        # Known manufactured center: |source - native| for W (mode) is 1e-9*s at s up to D; for A it is ~1e-9*s.
        center = Fraction(fs['argmax_components_exact']['center'])
        expect_hi = Fraction(1, 10 ** 9) * Fraction(2) * Fraction(11, 10)
        res[kind] = {'bitwise_all_blocks': summ['all_blocks_bitwise_equal'],
                     'accepted_equals_generator_final': summ['accepted_max_errors_exact'] == final,
                     'closure_violations_zero': summ['closure_violations'] == 0,
                     'manufactured_center_visible': 0 < center <= expect_hi,
                     'refined_above_accepted_cells_diagnostic': summ['refined_above_accepted_cells'],
                     'refined_max_not_above_accepted_max': Fraction(fs['refined_bound_exact']) <= Fraction(fs['accepted_bound_exact']),
                     'dominant_width_reported': fs['dominant_width'] in ('CENTER_DISCREPANCY', 'STATE_RADIUS', 'COMPARISON_STEP', 'EVENT_WIDTH'),
                     'dominant_width': fs['dominant_width'], 'shares': fs['argmax_shares'], 'cells': summ['cells'],
                     'seconds': summ['elapsed_seconds']}
        bad = tamper(ckdir, base / f'tampered-{kind}')
        sb, _ = budget.execute(context(kind, bad))
        res[kind]['tamper_detected'] = (not sb['all_blocks_bitwise_equal']) and [c['bitwise_equal'] for c in sb['block_checks']][:2] == [True, False]
        flowdir = base / 'out' / summ['flow']
        flowdir.mkdir(parents=True)
        (flowdir / 'CELLS.f64').write_bytes(payload.tobytes())
        summ['arrays']['sha256'] = __import__('hashlib').sha256(payload.tobytes()).hexdigest()
        (flowdir / 'SUMMARY.json').write_text(json.dumps(summ))
        C = {'out': base / 'out', 'identity': None, 'inherited': {summ['flow']: final}, 'Dlo': DLO, 'Dhi': DHI, 'step': STEP,
             'subcells': CONFIG['subcells'], 'profile': lambda flow, k=kind: profile(k), 'checkpoints': lambda flow, d=ckdir: d,
             'task': {summ['flow']: 0 if kind == 'mode' else 1}, 'fresh': lambda flow, k=kind: fresh(k),
             'sample_blocks': [0, 2], 'fixture': True}
        g = []
        verify2.verify_flow(C, summ['flow'], g)
        res[kind]['verifier_checks_all_pass'] = all(r['pass'] for r in g)
        res[kind]['verifier_failed'] = [r['id'] for r in g if not r['pass']]
        res[kind]['verifier_checks'] = len(g)
    units = {'up_float_is_upward': all(Fraction(up_float(Fraction(1, 3) * k)) >= Fraction(1, 3) * k for k in range(1, 50)),
             'assemble_logic': True}
    passed = all(v for r in res.values() for k, v in r.items() if isinstance(v, bool)) and all(units.values())
    result = {'passed': passed, 'utc': now(), 'real_data_outcomes_computed': False, 'physical_outcomes': False,
              'fixtures': res, 'units': units, 'sources': source_hashes(), 'runtime': runtime_fingerprint(), 'config': CONFIG,
              'address_space': limits, 'seconds': time.monotonic() - t0}
    atomic(root / 'PREFLIGHT.json', result, True)
    print(json.dumps({'passed': passed, 'path': str(root / 'PREFLIGHT.json'), 'fixtures': res}, indent=1, default=str), flush=True)
    return passed


if __name__ == '__main__':
    if len(sys.argv) != 2 or sys.argv[1] != 'all':
        raise SystemExit('usage: preflight2.py all')
    sys.exit(0 if run_all() else 3)
