"""Freeze sources, contract, inputs (each listed in its predecessor manifest) and runtime.

    python -B <run>/code/freeze3.py <preflight/STAMP/PREFLIGHT.json>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common3 import (RUN, OUT, VER, PACKET, CONFIG, RESEARCH, now, sha, read, atomic, source_hashes,  # noqa: E402
                     runtime_fingerprint, capacity, check_environment)


def input_files():
    i, n, f, c = PACKET['identity'], PACKET['native'], PACKET['finite'], PACKET['connected']
    files = [i / 'MANIFEST.json', i / 'SPATIAL_ENCLOSURES.json', i / 'BINDINGS.json', i / 'RESULT.json']
    for flow in CONFIG['flows']:
        files += [i / 'output' / flow / 'RESULT.json', i / 'output' / flow / 'TERMINAL_CHECKPOINT.json']
        files += sorted((i / 'output' / flow / 'checkpoints').glob('*.json'))
    files += [n / 'MANIFEST.json', n / 'BINDINGS.json'] + [n / 'results/fine_c4' / x for x in ('SEED.json', 'case_3.dense.json', 'case_4.dense.json')]
    sp = PACKET['spatial']
    files += [sp / 'MANIFEST.json'] + [sp / 'inputs' / f'fine_c4_case{c}_N{N}_p80{x}' for c in (0, 3, 4) for N in CONFIG['degrees'] for x in ('.json', '.grid.json')]
    files += [f / 'MANIFEST.json', f / 'output/source/RESULT.json', f / 'output/positive/RESULT.json', f / 'output/negative/RESULT.json']
    files += [c / 'MANIFEST.json', c / 'BINDINGS.json', c / 'INDEPENDENT_AUDIT.json']
    return files


def rows(data):
    if isinstance(data.get('entries'), list):
        return data['entries']
    return [dict(v, path=k) for k, v in data['files'].items()]


def crosscheck(files):
    problems, matched = [], 0
    index = {k: {r['path']: r['sha256'] for r in rows(read(PACKET[k] / 'MANIFEST.json'))} for k in ('identity', 'native', 'finite', 'connected', 'spatial')}
    for path in files:
        key = next(k for k in index if str(path).startswith(str(PACKET[k]) + '/'))
        rel = str(path.relative_to(PACKET[key]))
        if rel == 'MANIFEST.json':
            continue
        if index[key].get(rel) != sha(path):
            problems.append(str(path))
        else:
            matched += 1
    return matched, problems


def main(preflight):
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
    files = input_files()
    counts = {flow: len(list((PACKET['identity'] / 'output' / flow / 'checkpoints').glob('*.json'))) for flow in CONFIG['flows']}
    if counts != {flow: 64 for flow in CONFIG['flows']}:
        raise RuntimeError('Unexpected checkpoint counts')
    matched, problems = crosscheck(files)
    if problems:
        raise RuntimeError('Inputs absent from or different in predecessor manifests: ' + ', '.join(problems[:5]))
    inherited = {p.name: sha(p) for p in sorted((RUN / 'code' / 'inherited').glob('*.py'))}
    ident_sources = read(PACKET['identity'] / 'BINDINGS.json')['sources']
    same = all(ident_sources.get(k) == v for k, v in inherited.items())
    if not same:
        raise RuntimeError('Inherited copies differ from the identity packet sources')
    policy = RESEARCH / 'ClaudeCode' / 'runtime'
    frozen = {'utc': now(), 'line': '02_lin_static', 'run': RUN.name, 'config': CONFIG, 'sources': source_hashes(),
              'inputs': {str(p): sha(p) for p in files}, 'manifest_matched_inputs': matched,
              'inherited_copies_equal_identity_sources': same, 'runtime': runtime_fingerprint(),
              'preflight': {'path': str(Path(preflight).resolve()), 'sha256': sha(preflight)},
              'compute_policy': {k: sha(policy / k) for k in ('SLOTS.md', 'slot_run.sh', 'PRIORITY', 'LAUNCH_CUTOFF') if (policy / k).exists()},
              'gate_review_findings_sha256': sha(RUN / 'GATE_REVIEW_FINDINGS.md'),
              'capacity': capacity(), 'real_data_outcomes_before_freeze': False}
    atomic(RUN / 'FREEZE.json', frozen, True)
    atomic(RUN / 'FREEZE_RECORD.json', {'utc': now(), 'guard': sha(RUN / 'FREEZE.json')}, True)
    print('FROZEN', sha(RUN / 'FREEZE.json'), len(files), 'inputs', matched, 'manifest-matched')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: freeze3.py <PREFLIGHT.json>')
    main(sys.argv[1])
