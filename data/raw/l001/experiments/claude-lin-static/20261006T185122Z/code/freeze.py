"""Freeze sources, contract, inputs (cross-checked against predecessor manifests) and runtime.

Refuses if any real outcome exists. Usage: python -B <run>/code/freeze.py <preflight/STAMP/PREFLIGHT.json>
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (RUN, OUT, VER, PACKET, CONFIG, RESEARCH, now, sha, read, atomic, source_hashes,  # noqa: E402
                    runtime_fingerprint, capacity, check_environment)


def input_files():
    n, s, a, i = PACKET['native'], PACKET['spatial'], PACKET['admission'], PACKET['identity']
    c, f = PACKET['connected'], PACKET['finite']
    files = [n / 'BINDINGS.json', n / 'MANIFEST.json']
    files += [n / 'results' / 'fine_c4' / x for x in ('SEED.json', 'case_0.dense.json', 'case_3.dense.json', 'case_4.dense.json')]
    files += [s / 'GRID_ADMISSION.json', s / 'VERIFICATION.json', s / 'MANIFEST.json']
    files += [s / 'inputs' / f'fine_c4_case{case}_N{N}_p80{suffix}' for case in CONFIG['cases'] for N in CONFIG['degrees']
              for suffix in ('.grid.json', '.audit.json', '.json')]
    files += [a / 'VERIFICATION.json', a / 'MANIFEST.json', a / 'code' / 'producer.py', a / 'code' / 'jet.py']
    files += [i / x for x in ('MANIFEST.json', 'RESULT.json', 'BINDINGS.json', 'FREEZE_RECORD.json', 'TERMINAL_CHECKPOINT.json',
                              'NUMERICAL_READBACK_FAILURE.json', 'SPATIAL_ENCLOSURES.json', 'INDEPENDENT_AUDIT.json',
                              'numerical_readback.py', 'readback/case0-p80.json', 'audit/FAILED_REPLAY_DIAGNOSTIC.json',
                              'audit/diagnose_failed_replay.py')]
    files += [i / 'output' / flow / x for flow in ('mode', 'positive', 'negative') for x in ('RESULT.json', 'TERMINAL_CHECKPOINT.json')]
    files += [c / 'INDEPENDENT_AUDIT.json', c / 'MANIFEST.json']
    files += [f / 'output' / 'positive' / 'RESULT.json', f / 'output' / 'negative' / 'RESULT.json', f / 'MANIFEST.json']
    return files


def manifest_rows(data):
    if isinstance(data.get('entries'), list):
        return data['entries']
    if isinstance(data.get('files'), dict):
        return [dict(v, path=k) for k, v in data['files'].items()]
    raise RuntimeError('Unsupported manifest schema')


def crosscheck(files):
    table, problems = {}, []
    for key, root in PACKET.items():
        index = {r['path']: r['sha256'] for r in manifest_rows(read(root / 'MANIFEST.json'))}
        for path in files:
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                continue
            if rel == 'MANIFEST.json':
                continue
            digest = sha(path)
            listed = index.get(rel)
            table[str(path)] = {'packet': key, 'manifest_sha256': listed, 'matches_manifest': None if listed is None else listed == digest}
            if listed is None or listed != digest:
                problems.append(str(path))
    return table, problems


def main(preflight_path):
    check_environment()
    if (RUN / 'FREEZE.json').exists():
        raise RuntimeError('Already frozen')
    for folder in (OUT, VER):
        if folder.exists() and any(folder.iterdir()):
            raise RuntimeError('Outputs exist before freeze: ' + str(folder))
    pre = read(preflight_path)
    if not pre['passed'] or pre['sources'] != source_hashes() or pre['runtime'] != runtime_fingerprint() or pre['config'] != CONFIG:
        raise RuntimeError('Stale or failed preflight')
    if pre.get('real_data_outcomes_computed') is not False:
        raise RuntimeError('Preflight must not compute real outcomes')
    files = input_files()
    inputs = {str(p): sha(p) for p in files}
    table, problems = crosscheck(files)
    if problems:
        raise RuntimeError('Inputs absent from or different in predecessor manifests: ' + ', '.join(problems))
    reference = {'producer.py': sha(RUN / 'code/reference/producer.py') == inputs[str(PACKET['admission'] / 'code' / 'producer.py')],
                 'jet.py': sha(RUN / 'code/reference/jet.py') == inputs[str(PACKET['admission'] / 'code' / 'jet.py')]}
    if not all(reference.values()):
        raise RuntimeError('Reference copies are not byte-identical')
    policy = RESEARCH / 'ClaudeCode' / 'runtime'
    frozen = {'utc': now(), 'line': '02_lin_static', 'run': RUN.name, 'config': CONFIG, 'sources': source_hashes(),
              'inputs': inputs, 'manifest_crosscheck': table,
              'manifest_listed_inputs': sum(1 for v in table.values() if v['matches_manifest']),
              'inputs_not_listed_in_a_manifest': sorted(k for k, v in table.items() if v['manifest_sha256'] is None),
              'reference_copies_byte_identical': reference, 'runtime': runtime_fingerprint(),
              'preflight': {'path': str(Path(preflight_path).resolve()), 'sha256': sha(preflight_path)},
              'compute_policy': {'SLOTS.md': sha(policy / 'SLOTS.md'), 'slot_run.sh': sha(policy / 'slot_run.sh')},
              'capacity': capacity(), 'real_data_outcomes_before_freeze': False, 'physical_outcomes_before_freeze': False,
              'note': 'Pre-freeze work used manufactured fixtures only; no real replay, root bound or receipt outcome was computed.'}
    atomic(RUN / 'FREEZE.json', frozen, True)
    atomic(RUN / 'FREEZE_RECORD.json', {'utc': now(), 'guard': sha(RUN / 'FREEZE.json')}, True)
    print('FROZEN', sha(RUN / 'FREEZE.json'), len(inputs), 'inputs', frozen['manifest_listed_inputs'], 'manifest-matched')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: freeze.py <PREFLIGHT.json>')
    main(sys.argv[1])
