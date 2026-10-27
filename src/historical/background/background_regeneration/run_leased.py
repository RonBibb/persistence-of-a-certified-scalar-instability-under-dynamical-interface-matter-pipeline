"""One admitted background-chain reproduction; no retry, cache or installation."""
import datetime
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / 'output'
CUTOFF = datetime.datetime.fromisoformat('2026-10-18T18:06:44+00:00')
LIMIT = 900
LOCKS = Path('/tmp/research-20261012-astra-medium')


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    assert sys.platform == 'linux'
    OUT.mkdir(exist_ok=False)
    started = time.monotonic()
    record = {'status': 'PREPARING', 'started_utc': now().isoformat(),
              'cutoff_utc': CUTOFF.isoformat(), 'hard_limit_seconds': LIMIT,
              'cases': [], 'retries': 0}
    lease = None
    admission = None
    child = None
    try:
        if (CUTOFF-now()).total_seconds() < LIMIT+10:
            raise RuntimeError('ADMISSION_HOLD_INSUFFICIENT_TIME')
        manifest = json.loads((BASE/'SOURCE_BINDINGS.json').read_text())
        for rel, item in manifest.items():
            if sha(BASE/'source'/rel) != item['sha256']:
                raise RuntimeError('SOURCE_BINDING_FAILURE:'+rel)
        record['source_bindings_sha256'] = sha(BASE/'SOURCE_BINDINGS.json')
        record['harness_sha256'] = {p.name: sha(p) for p in
                                  [BASE/'run_leased.py', BASE/'bootstrap.py']}
        admission = (LOCKS/'admission.lock').open('r+')
        fcntl.flock(admission, fcntl.LOCK_EX | fcntl.LOCK_NB)
        excluded = set()
        active = []
        rows = subprocess.check_output(['ps', '-eo', 'pid,comm'], text=True)
        for row in rows.splitlines()[1:]:
            pid_text, comm = row.split(None, 1)
            pid = int(pid_text)
            if pid == os.getpid():
                continue
            if any(s in comm.lower() for s in ['python', 'julia', 'solver', 'wolfram', 'mpirun']):
                try:
                    affinity = os.sched_getaffinity(pid)
                except ProcessLookupError:
                    continue
                excluded.update(affinity)
                active.append({'pid': pid, 'comm': comm, 'affinity': sorted(affinity)})
        allowed = os.sched_getaffinity(0)
        record['active_science_at_admission'] = active
        for cpu in sorted(allowed):
            lock = LOCKS/f'cpu-{cpu}.lock'
            if cpu in excluded or not lock.is_file():
                continue
            candidate = lock.open('r+')
            try:
                fcntl.flock(candidate, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                candidate.close()
                continue
            lease = candidate
            record['cpu'] = cpu
            os.sched_setaffinity(0, {cpu})
            break
        if lease is None:
            raise RuntimeError('RESOURCE_HOLD_NO_CPU')
        admission.close()
        admission = None
        env = dict(os.environ)
        for key in ['OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS']:
            env[key] = '1'
        env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0', PYTHONNOUSERSITE='1')
        for name, entry in [('primary', 'confirm_32768.py'),
                            ('independent', 'independent_d1_replay_r1.py')]:
            remaining = min(LIMIT-(time.monotonic()-started), (CUTOFF-now()).total_seconds())
            if remaining <= 0:
                raise RuntimeError('CUTOFF_OR_LIMIT_NO_NEW_CASE')
            case = {'name': name, 'entry': entry, 'started_utc': now().isoformat()}
            record['cases'].append(case)
            case_started = time.monotonic()
            with (OUT/f'{name}_RESULT.json').open('x') as stdout, (OUT/f'{name}.stderr').open('x') as stderr:
                child = subprocess.Popen([sys.executable, '-I', '-B', str(BASE/'bootstrap.py'), name, entry],
                                         stdout=stdout, stderr=stderr, env=env, start_new_session=True)
                case['pid'] = child.pid
                try:
                    code = child.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGTERM)
                    try:
                        code = child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        code = child.wait()
                    case['timed_out'] = True
                case.update(exit_code=code, elapsed_seconds=time.monotonic()-case_started,
                            completed_utc=now().isoformat())
            if code != 0:
                raise RuntimeError('PRODUCER_NONZERO_EXIT:'+name)
            result = json.loads((OUT/f'{name}_RESULT.json').read_text())
            case['producer_status'] = result.get('status')
            case['producer_classification'] = result.get('classification')
            if result.get('status') != 'COMPLETE':
                raise RuntimeError('PRODUCER_INCOMPLETE:'+name)
            expected = ('RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS' if name == 'primary'
                        else 'INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS')
            if result.get('classification') != expected:
                raise RuntimeError('FROZEN_PRODUCER_GATE_NOT_PASSED:'+name)
        record['status'] = 'FRESH_BACKGROUND_PRODUCERS_COMPLETE_PENDING_INDEPENDENT_AUDIT'
    except Exception as exc:
        record['status'] = 'INCOMPLETE_OR_HOLD'
        record['error'] = repr(exc)
    finally:
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid, signal.SIGKILL)
                child.wait()
        if admission is not None:
            admission.close()
        if lease is not None:
            lease.close()
        record.update(completed_utc=now().isoformat(), elapsed_seconds=time.monotonic()-started,
                      lease_released=True)
        (OUT/'EXECUTION.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps(record, indent=2))
    return 0 if record['status'].startswith('FRESH_BACKGROUND_PRODUCERS_COMPLETE') else 1


if __name__ == '__main__':
    raise SystemExit(main())
