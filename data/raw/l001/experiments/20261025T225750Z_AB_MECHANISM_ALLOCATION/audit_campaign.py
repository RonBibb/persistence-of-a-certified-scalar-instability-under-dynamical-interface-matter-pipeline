"""Read-only Linux integrity snapshot; stdout only, no science/restart actions."""
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

def main():
    assert sys.platform == 'linux', 'LINUX_ONLY'
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=['interim', 'final'], required=True)
    args = parser.parse_args()
    signal.alarm(180)
    lock = Path('/tmp/research-20261012-astra-medium')
    admission = (lock/'admission.lock').open('r+')
    fcntl.flock(admission, fcntl.LOCK_EX | fcntl.LOCK_NB)
    assert not any('hold' in p.name.lower() for p in lock.iterdir()), 'HOLD'
    available = []
    occupied = []
    for cpu in sorted(os.sched_getaffinity(0)):
        p = lock/f'cpu-{cpu}.lock'
        if not p.exists():
            continue
        f = p.open('r+')
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            f.close()
            occupied.append(cpu)
            continue
        available.append((cpu, f))
    assert available and len(occupied) < 2, 'NO_AGGREGATE_CPU_HEADROOM'
    cpu, lease = available[0]
    for _, unused in available[1:]:
        unused.close()
    os.sched_setaffinity(0, {cpu})
    admission.close()
    cache = {}
    def sha(path):
        path = path.resolve()
        if path not in cache:
            h = hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda: stream.read(1024*1024), b''):
                    h.update(block)
            cache[path] = h.hexdigest()
        return cache[path]
    read = lambda p: json.loads(p.read_text())
    def verify(folder, mapping):
        issues = []
        for rel, expected in mapping.items():
            try:
                if sha(folder/rel) != expected:
                    issues.append({'path': rel, 'issue': 'HASH_MISMATCH'})
            except OSError as exc:
                issues.append({'path': rel, 'issue': repr(exc)})
        return {'checked': len(mapping), 'issues': issues}
    packets = []
    spans = []
    for folder in sorted(ROOT.glob('T*')):
        if not folder.is_dir():
            continue
        row = {'packet': folder.name}
        gate = folder/'ADMISSION.json'
        row['admitted'] = gate.exists() and read(gate).get('admitted') is True
        row['sources'] = verify(folder, read(gate)['sources']) if gate.exists() else None
        runtime = folder/'RUNTIME_BINDINGS.json'
        row['runtime_files'] = verify(folder, read(runtime)['files']) if runtime.exists() else None
        artifacts = {}
        for name in ['RESULT.json', 'FAILURE.json', 'RESOURCE_HOLD.json', 'EXECUTION.json',
                     'RESOURCE_START.json', 'STARTED.json', 'PROSPECTIVE_REVIEW.md', 'TERMINAL_REVIEW.md']:
            for path in [folder/name, folder/'output'/name]:
                if path.exists():
                    rel = str(path.relative_to(ROOT))
                    item = {'path': rel, 'sha256': sha(path)}
                    if path.suffix == '.json':
                        data = read(path)
                        for key in ['classification', 'exit_code', 'child_reaped', 'child_pid', 'start_utc', 'wall_seconds']:
                            if key in data:
                                item[key] = data[key]
                    artifacts[rel] = item
        row['artifacts'] = artifacts
        ex = folder/'EXECUTION.json'
        if ex.exists():
            data = read(ex)
            pid = data.get('child_pid')
            proc = Path('/proc')/str(pid)
            row['recorded_child_pid_exists_now'] = proc.exists()
            row['recorded_child_current_cmdline'] = proc.joinpath('cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace') if proc.exists() else None
            if data.get('start_utc') and 'wall_seconds' in data:
                start = dt.datetime.fromisoformat(data['start_utc']).timestamp()
                spans += [(start, 1), (start + data['wall_seconds'], -1)]
        packets.append(row)
    closure = ROOT.parent/'20261025T212050Z_UNIFORM_SIXTH_ORDER_READMISSION/CLOSURE_MANIFEST.json'
    predecessor = {'manifest_sha256': sha(closure), **verify(closure.parent, read(closure)['files'])}
    live = []
    scientific_processes = []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            cmd = proc.joinpath('cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
            comm = proc.joinpath('comm').read_text().strip()
            if any(word in comm.lower() for word in ['python', 'julia', 'wolfram', 'solver', 'mpirun']):
                try:
                    cwd = str(proc.joinpath('cwd').resolve(strict=True))
                except OSError:
                    cwd = None
                scientific_processes.append({'pid': int(proc.name), 'comm': comm, 'cmdline': cmd,
                    'cwd': cwd, 'affinity': sorted(os.sched_getaffinity(int(proc.name))),
                    'campaign_identified': ROOT.name in cmd or (cwd is not None and ROOT.name in cwd)})
            if ROOT.name in cmd and ('producer.py' in cmd or 'lease_run.py' in cmd):
                live.append({'pid': int(proc.name), 'cmdline': cmd, 'affinity': sorted(os.sched_getaffinity(int(proc.name)))})
        except (OSError, ProcessLookupError):
            pass
    running = peak = 0
    for _, change in sorted(spans):
        running += change
        peak = max(peak, running)
    # All expensive verification is complete. Release our CPU before the
    # final lock-availability observation; never retain or alter other leases.
    lease.close()
    lock_snapshot = {}
    try:
        final_gate = (lock/'admission.lock').open('r+')
        fcntl.flock(final_gate, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for path in [lock/'line-L001.lock', *sorted(lock.glob('cpu-*.lock'))]:
            try:
                handle = path.open('r+')
                try:
                    fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    lock_snapshot[path.name] = 'available'
                except BlockingIOError:
                    lock_snapshot[path.name] = 'held'
                finally:
                    handle.close()
            except OSError as exc:
                lock_snapshot[path.name] = repr(exc)
        final_gate.close()
    except OSError as exc:
        lock_snapshot['admission_snapshot'] = repr(exc)
    result = {'phase': args.phase, 'utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'audit_source_sha256': sha(Path(__file__)), 'audit_cpu': cpu, 'audit_pid': os.getpid(),
              'packets': packets, 'predecessor_closure': predecessor, 'matching_live_workers': live,
              'other_scientific_process_snapshot': scientific_processes,
              'lock_availability_after_own_cpu_release': lock_snapshot,
              'recorded_wrapper_span_peak_overlap': peak,
              'resource_evidence_limits': ['Recorded wrapper spans do not inventory all historical independent audit processes.',
                  'Review records state Linux pinning/lease use; no complete historical aggregate CPU telemetry exists.',
                  'PID existence alone can reflect reuse; command lines are reported.',
                  'Unlabelled stdin Python processes may not be attributable to this campaign; all scientific-process command lines and affinities are exposed.',
                  'Snapshot checks file integrity and review presence, not scientific contents anew.'],
              'unique_hashed_files': len(cache)}
    print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()
