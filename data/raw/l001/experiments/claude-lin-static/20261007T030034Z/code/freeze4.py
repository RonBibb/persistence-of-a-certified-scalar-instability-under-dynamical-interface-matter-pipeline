"""Freeze sources, contract, inputs (each listed in its predecessor manifest), runtime and the pre-freeze records.

    python -B <run>/code/freeze4.py <preflight/STAMP/PREFLIGHT.json> <preflight/REAL_CONTROLS_CHECK_n.json> <preflight/VERIFIER_CONTROLS_CHECK_n.json>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common4 import (RUN, OUT, VER, PACKET, RUN3, CONFIG, RESEARCH, now, sha, read, atomic, source_hashes,  # noqa: E402
                     runtime_fingerprint, capacity, check_environment)


def input_files():
    f, c, n, s, i = PACKET['finite'], PACKET['connected'], PACKET['native'], PACKET['spatial'], PACKET['identity']
    files = [f / 'MANIFEST.json', f / 'BINDINGS.json', f / 'runner.py', f / 'preparation.py', f / 'output/source/RESULT.json']
    files += sorted((f / 'output/source/checkpoints').glob('*.json'))
    for w in CONFIG['cases']:
        files += [f / 'output' / w / 'RESULT.json'] + sorted((f / 'output' / w / 'checkpoints').glob('*.json'))
    files += [c / 'MANIFEST.json', c / 'BINDINGS.json', c / 'INDEPENDENT_AUDIT.json']
    files += [n / 'MANIFEST.json', n / 'BINDINGS.json'] + [n / 'results/fine_c4' / x for x in ('SEED.json', 'case_3.dense.json', 'case_4.dense.json')]
    files += [s / 'MANIFEST.json'] + [s / 'inputs' / f'fine_c4_case{k}_N{N}_p80{x}' for k in (3, 4) for N in CONFIG['degrees'] for x in ('.json', '.grid.json')]
    files += [i / 'MANIFEST.json', i / 'BINDINGS.json']
    files += [RUN3 / 'MANIFEST.json', RUN3 / 'outputs/PRODUCER_RESULT.json', RUN3 / 'verification/VERIFICATION.json']
    files += [RUN3 / 'outputs' / w / 'SUMMARY.json' for w in CONFIG['cases']]
    return files


def rows(data):
    if isinstance(data.get('entries'), list):
        return data['entries']
    return [dict(v, path=k) for k, v in data['files'].items()]


def crosscheck(files):
    roots = {k: PACKET[k] for k in ('finite', 'connected', 'native', 'spatial', 'identity')} | {'run3': RUN3}
    index = {k: {r['path']: r['sha256'] for r in rows(read(root / 'MANIFEST.json'))} for k, root in roots.items()}
    problems, matched = [], 0
    for path in files:
        key = next(k for k, root in roots.items() if str(path).startswith(str(root) + '/'))
        rel = str(path.relative_to(roots[key]))
        if rel == 'MANIFEST.json':
            continue
        if index[key].get(rel) != sha(path):
            problems.append(str(path))
        else:
            matched += 1
    return matched, problems


def main(preflight, real_check, verifier_check):
    check_environment()
    if (RUN / 'FREEZE.json').exists():
        raise RuntimeError('Already frozen')
    for folder in (OUT, VER):
        if folder.exists() and any(folder.iterdir()):
            raise RuntimeError('Outputs exist before freeze')
    if not (RUN / 'GATE_REVIEW_FINDINGS.md').exists():
        raise RuntimeError('Gate review findings must be recorded before the freeze')
    pre = read(preflight)
    if not pre['passed'] or pre['sources'] != source_hashes() or pre['runtime'] != runtime_fingerprint() or pre['config'] != CONFIG:
        raise RuntimeError('Stale or failed preflight')
    if pre['real_data_outcomes_computed'] is not False:
        raise RuntimeError('Preflight computed real outcomes')
    for path in (real_check, verifier_check):
        real = read(path)
        if (not real['all_controls_pass'] or real['outcomes_computed'] is not False or real.get('sources') != source_hashes()
                or real.get('runtime') != runtime_fingerprint() or not real.get('control_records_identical_across_amplitudes')):
            raise RuntimeError('Real-data control check failed, computed outcomes, or is stale: ' + str(path))
    files = input_files()
    counts = {w: len(list((PACKET['finite'] / 'output' / w / 'checkpoints').glob('*.json'))) for w in CONFIG['cases']}
    counts['source'] = len(list((PACKET['finite'] / 'output/source/checkpoints').glob('*.json')))
    matched, problems = crosscheck(files)
    if problems:
        raise RuntimeError('Inputs absent from or different in predecessor manifests: ' + ', '.join(problems[:5]))
    inherited = {p.name: sha(p) for p in sorted((RUN / 'code' / 'inherited').glob('*.py'))}
    ident = read(PACKET['identity'] / 'BINDINGS.json')['sources']
    finite = read(PACKET['finite'] / 'BINDINGS.json')['sources']
    origin = {name: ('finite' if name == 'preparation.py' else 'identity') for name in inherited}
    shared = ('preparation.py', 'series.py', 'records.py', 'validated.py', 'algebra.py', 'source_flow.py', 'nonlinear.py')
    same = (all((sha(PACKET['finite'] / name) if origin[name] == 'finite' else ident.get(name)) == digest for name, digest in inherited.items())
            and all(finite.get(name) == inherited.get(name) for name in shared))
    if not same:
        raise RuntimeError('Inherited copies differ from their source packets')
    policy = RESEARCH / 'ClaudeCode' / 'runtime'
    frozen = {'utc': now(), 'line': '02_lin_static', 'run': RUN.name, 'config': CONFIG, 'sources': source_hashes(),
              'inputs': {str(p): sha(p) for p in files}, 'manifest_matched_inputs': matched, 'checkpoint_counts': counts,
              'inherited_copies': {name: {'sha256': d, 'origin_packet': origin[name]} for name, d in inherited.items()},
              'inherited_copies_equal_source_packets': same, 'runtime': runtime_fingerprint(),
              'preflight': {'path': str(Path(preflight).resolve()), 'sha256': sha(preflight)},
              'real_control_check': {'path': str(Path(real_check).resolve()), 'sha256': sha(real_check)},
              'verifier_control_check': {'path': str(Path(verifier_check).resolve()), 'sha256': sha(verifier_check)},
              'inherited_shared_with_finite_bindings': list(shared),
              'compute_policy': {k: sha(policy / k) for k in ('SLOTS.md', 'slot_run.sh', 'PRIORITY', 'LAUNCH_CUTOFF') if (policy / k).exists()},
              'gate_review_findings_sha256': sha(RUN / 'GATE_REVIEW_FINDINGS.md'),
              'capacity': capacity(), 'real_data_outcomes_before_freeze': False}
    atomic(RUN / 'FREEZE.json', frozen, True)
    atomic(RUN / 'FREEZE_RECORD.json', {'utc': now(), 'guard': sha(RUN / 'FREEZE.json')}, True)
    print('FROZEN', sha(RUN / 'FREEZE.json'), len(files), 'inputs', matched, 'manifest-matched', counts)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        raise SystemExit('usage: freeze4.py <PREFLIGHT.json> <REAL_CONTROLS_CHECK.json> <VERIFIER_CONTROLS_CHECK.json>')
    main(sys.argv[1], sys.argv[2], sys.argv[3])
