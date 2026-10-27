"""Linux-only documentary closure builder/verifier. Read-only; JSON stdout."""
import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import sys

ROOT = Path(__file__).resolve().parent
MANIFEST = 'CLOSURE_MANIFEST.json'
RECEIPT = 'CLOSURE_VERIFICATION.json'
CUTOFF = dt.datetime(2026, 10, 26, 0, 57, 50, tzinfo=dt.timezone.utc)
# Per-process only: manifest and verification invocations start fresh caches.
# Expected immutable paths must retain their stat identity throughout a pass.
HASH_CACHE = {}

def excluded(path):
    rel = path.relative_to(ROOT).as_posix()
    return rel in (MANIFEST, RECEIPT) or path.name.endswith('.lock')

def sha(path):
    path = path.resolve()
    st = path.stat()
    identity = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    if path in HASH_CACHE:
        prior_identity, digest = HASH_CACHE[path]
        assert identity == prior_identity, 'FILE_CHANGED_DURING_CLOSURE'
        return digest
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    after = path.stat()
    assert identity == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns), 'FILE_CHANGED_DURING_HASH'
    digest = h.hexdigest()
    HASH_CACHE[path] = (identity, digest)
    return digest

def read(path):
    return json.loads(path.read_text())

def main():
    assert sys.platform == 'linux', 'LINUX_ONLY'
    p = argparse.ArgumentParser()
    p.add_argument('--mode', choices=['manifest', 'verify'], required=True)
    p.add_argument('--audit-file', required=True)
    p.add_argument('--expected-file', required=True)
    args = p.parse_args()
    assert dt.datetime.now(dt.timezone.utc) >= CUTOFF, 'NOT_FINAL_BEFORE_CUTOFF'
    signal.alarm(180)
    locks = Path('/tmp/research-20261012-astra-medium')
    admission = (locks/'admission.lock').open('r+')
    fcntl.flock(admission, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not any('hold' in x.name.lower() for x in locks.iterdir()), 'HOLD'
    free, occupied = [], []
    for cpu in sorted(os.sched_getaffinity(0)):
        path = locks/f'cpu-{cpu}.lock'
        if not path.exists():
            continue
        handle = path.open('r+')
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            free.append((cpu, handle))
        except BlockingIOError:
            occupied.append(cpu)
            handle.close()
    assert free and len(occupied) < 2, 'NO_AGGREGATE_CPU_HEADROOM'
    cpu, lease = free[0]
    for _, handle in free[1:]:
        handle.close()
    os.sched_setaffinity(0, {cpu})
    admission.close()

    audit_path = ROOT/args.audit_file
    assert audit_path.parent == ROOT and audit_path.is_file(), 'ROOT_AUDIT_FILE'
    audit = read(audit_path)
    assert audit['phase'] == 'final', 'FINAL_AUDIT_REQUIRED'
    assert dt.datetime.fromisoformat(audit['utc']) >= CUTOFF, 'FINAL_AUDIT_TOO_EARLY'
    assert not audit['matching_live_workers'], 'LIVE_CAMPAIGN_WORKER'
    assert not any(x['campaign_identified'] for x in audit['other_scientific_process_snapshot']), 'LIVE_CAMPAIGN_AUDIT'
    assert audit['lock_availability_after_own_cpu_release']['line-L001.lock'] == 'available', 'LINE_LOCK'
    assert audit['predecessor_closure']['checked'] == 131 and not audit['predecessor_closure']['issues'], 'PARENT_CLOSURE'
    expected_path = ROOT/args.expected_file
    assert expected_path.parent == ROOT and expected_path.is_file(), 'ROOT_EXPECTED_FILE'
    expected = read(expected_path)['packets']
    assert set(expected) == {row['packet'] for row in audit['packets']}, 'EXPLICIT_PACKET_INVENTORY'
    assert set(expected) == {x.name for x in ROOT.glob('T*') if x.is_dir()}, 'CURRENT_PACKET_INVENTORY'
    for row in audit['packets']:
        spec = expected[row['packet']]
        disposition = spec['disposition']
        assert disposition in ('result', 'failure', 'resource_hold', 'unrun'), 'EXPECTED_DISPOSITION'
        if disposition != 'unrun':
            assert row['admitted'], row['packet']
        if row['sources'] is not None:
            assert not row['sources']['issues'], row['packet']
        if row['runtime_files'] is not None:
            assert not row['runtime_files']['issues'], row['packet']
        packet = ROOT/row['packet']
        terminals = [x for x in [packet/'RESULT.json', packet/'FAILURE.json', packet/'output/RESULT.json', packet/'output/FAILURE.json'] if x.is_file()]
        if disposition in ('result', 'failure'):
            assert (packet/'PROSPECTIVE_REVIEW.md').is_file() and (packet/'TERMINAL_REVIEW.md').is_file()
            execution = read(packet/'EXECUTION.json')
            assert execution['child_reaped'] is True
            assert dt.datetime.fromisoformat(execution['start_utc']) < CUTOFF, 'LATE_START'
            assert len(terminals) == 1, 'AMBIGUOUS_TERMINAL'
            assert terminals[0].name == ('RESULT.json' if disposition == 'result' else 'FAILURE.json')
            assert (execution['exit_code'] == 0) == (disposition == 'result')
            assert read(terminals[0])['classification'] == spec['classification']
        else:
            assert not terminals and not (packet/'EXECUTION.json').exists(), 'UNEXPECTED_EXECUTION'
            assert not (packet/'STARTED.json').exists() and not (packet/'output/STARTED.json').exists()
            if disposition == 'resource_hold':
                assert read(packet/'RESOURCE_HOLD.json')['classification'] == 'RESOURCE_HOLD'
                assert (packet/'TERMINAL_REVIEW.md').is_file()
            else:
                assert not (packet/'RESOURCE_HOLD.json').exists(), 'UNRECORDED_HOLD'
        # Fresh inherited/source/runtime verification, not just old snapshot trust.
        if (packet/'ADMISSION.json').exists():
            for rel, digest in read(packet/'ADMISSION.json')['sources'].items():
                assert sha(packet/rel) == digest, rel
        runtime = packet/'RUNTIME_BINDINGS.json'
        if runtime.exists():
            for path, digest in read(runtime)['files'].items():
                assert sha(Path(path)) == digest, path
    predecessor = ROOT.parent/'20261025T212050Z_UNIFORM_SIXTH_ORDER_READMISSION/CLOSURE_MANIFEST.json'
    assert sha(predecessor) == audit['predecessor_closure']['manifest_sha256']
    for rel, digest in read(predecessor)['files'].items():
        assert sha(predecessor.parent/rel) == digest, rel

    files, exclusions = {}, []
    for path in sorted(ROOT.rglob('*')):
        assert not path.is_symlink(), 'UNEXPECTED_SYMLINK:'+str(path)
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if excluded(path):
            exclusions.append(rel)
        else:
            files[rel] = sha(path)
    common = {'utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'verification_platform': 'academic-linux',
              'audit_cpu': cpu, 'final_audit_file': args.audit_file, 'final_audit_sha256': sha(audit_path),
              'expected_dispositions_file': args.expected_file, 'expected_dispositions_sha256': sha(expected_path),
              'packet_count': len(expected), 'packet_dispositions': expected, 'source_parent_runtime_checks': 'PASS',
              'exclusion_rules': [MANIFEST, RECEIPT, 'any file whose basename ends in .lock'],
              'resource_scope': 'Final audit snapshot plus leased documentary hash check; not full historical CPU telemetry.'}
    live = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            comm = (proc/'comm').read_text().strip()
            cmd = (proc/'cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            cwd = str((proc/'cwd').resolve(strict=True))
            if any(x in comm.lower() for x in ('python', 'julia', 'wolfram', 'solver', 'mpirun')) and (ROOT.name in cmd or ROOT.name in cwd):
                live.append({'pid': int(proc.name), 'command': cmd, 'affinity': sorted(os.sched_getaffinity(int(proc.name)))})
        except (OSError, ProcessLookupError):
            pass
    assert not live, 'LIVE_CAMPAIGN_PROCESS_AT_MANIFEST_CHECK'
    line = (locks/'line-L001.lock').open('r+')
    fcntl.flock(line, fcntl.LOCK_EX | fcntl.LOCK_NB)
    line.close()
    common['current_campaign_processes'] = live
    common['current_line_lock'] = 'available; checked and released'
    if args.mode == 'manifest':
        assert not (ROOT/MANIFEST).exists() and not (ROOT/RECEIPT).exists(), 'NO_OVERWRITE'
        result = dict(common, classification='DOCUMENTARY_CLOSURE_MANIFEST', files=files,
                      present_excluded_files=exclusions, file_count=len(files))
    else:
        assert not (ROOT/RECEIPT).exists(), 'NO_OVERWRITE_RECEIPT'
        saved = read(ROOT/MANIFEST)
        assert saved['files'] == files, 'MANIFEST_HASH_OR_INVENTORY_MISMATCH'
        assert saved['final_audit_file'] == args.audit_file
        assert saved['expected_dispositions_file'] == args.expected_file
        assert saved['exclusion_rules'] == common['exclusion_rules']
        result = dict(common, classification='DOCUMENTARY_CLOSURE_VERIFIED',
                      manifest_sha256=sha(ROOT/MANIFEST), checked_files=len(files),
                      exact_file_inventory_match=True)
    lease.close()
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
