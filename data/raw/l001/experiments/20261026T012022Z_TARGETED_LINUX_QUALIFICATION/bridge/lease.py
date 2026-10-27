"""Linux one-core administrative-freeze/scientific-run lease supervisor."""
import sys
sys.dont_write_bytecode = True
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

HERE = Path(__file__).resolve().parent
LOCK = Path('/tmp/research-20261012-astra-medium')
handles = []
child = None
mode = sys.argv[1]
assert mode in ('freeze', 'run') and sys.platform == 'linux'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(name, record):
    with (HERE / name).open('x') as f:
        json.dump(record, f, indent=2); f.flush(); os.fsync(f.fileno())

def take(path, create=False):
    f = path.open('a+' if create else 'r+')
    try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BaseException: f.close(); raise
    handles.append(f)
    return f

def check_manifest():
    admission = json.loads((HERE / 'ADMISSION.json').read_text())
    assert admission['admitted'] is True
    assert sha(HERE / 'FROZEN.json') == admission['frozen_sha256']
    frozen = json.loads((HERE / 'FROZEN.json').read_text())
    assert str(Path(sys.executable).resolve()) == frozen['executable_realpath'], 'actual interpreter differs'
    for path, expected in frozen['files'].items():
        assert sha(path) == expected, path
    return len(frozen['files'])

def main():
    global child
    assert (HERE / 'SOURCE_REVIEW.md').is_file()
    assert not (HERE / (mode + '_EXECUTION.json')).exists()
    packet = take(HERE / 'packet.lock', True)
    if mode == 'run':
        assert not any((HERE / n).exists() for n in ('RESULT.json','FAILURE.json','RUNTIME_BEFORE.json','output'))
    admission = take(LOCK / 'admission.lock')
    assert not any('hold' in p.name.lower() for p in LOCK.iterdir()), 'HOLD present'
    line = take(LOCK / 'line-L001.lock', True)
    snapshot = subprocess.check_output(['ps','-eo','pid,pcpu,comm,args'], text=True)
    occupied = set()
    for row in snapshot.splitlines()[1:]:
        fields = row.split(None, 3)
        if len(fields) != 4: continue
        pid, pct, comm, args = fields
        if int(pid) == os.getpid(): continue
        science = any(s in comm.lower() for s in ('python','julia','wolfram','math','solver','mpirun'))
        system = any(s in args for s in ('unattended-upgrade','update-manager','check-new-release'))
        if (science and not system) or (float(pct)>20 and not args.startswith('[')):
            try: occupied.update(os.sched_getaffinity(int(pid)))
            except ProcessLookupError: pass
    available = []
    for cpu in sorted(os.sched_getaffinity(0)):
        path = LOCK / ('cpu-' + str(cpu) + '.lock')
        if not path.exists(): continue
        try: f = take(path)
        except (BlockingIOError, PermissionError): occupied.add(cpu); continue
        if cpu in occupied: f.close(); handles.remove(f)
        else: available.append((cpu, f))
    mem = int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))
    assert available and len(occupied | {available[0][0]}) <= 2 and mem >= 4*1024**2, 'RESOURCE_HOLD'
    cpu, lease = available[0]
    for _, f in available[1:]: f.close(); handles.remove(f)
    admission.close(); handles.remove(admission)
    os.sched_setaffinity(0, {cpu})
    if mode == 'run': check_manifest()
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key] = '1'
    os.environ.update(PYTHONDONTWRITEBYTECODE='1', PYTHONHASHSEED='0', PYTHONNOUSERSITE='1')
    resource.setrlimit(resource.RLIMIT_AS, (1024**3,1024**3))
    start = time.monotonic()
    record = {'start_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'cpu': cpu, 'cores': 1, 'occupied_cpus': sorted(occupied), 'mode': mode,
              'timeout_seconds': 130 if mode == 'run' else 120,
              'executable': sys.executable, 'executable_sha256': sha(sys.executable),
              'locks_inherited_by_child': True}
    save(mode + '_START.json', record)
    with (HERE / (mode + '.log')).open('x') as log:
        child = subprocess.Popen([sys.executable, '-I','-B', str(HERE / ('check_bridge.py' if mode=='run' else 'freeze.py'))],
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True,
                    pass_fds=(line.fileno(),lease.fileno(),packet.fileno()))
        try: code = child.wait(timeout=record['timeout_seconds'])
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGTERM)
            try: code = child.wait(timeout=3)
            except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); code=child.wait()
    record.update(exit_code=code, child_pid=child.pid, child_reaped=True, wall_seconds=time.monotonic()-start)
    if mode == 'run':
        try: record['post_frozen_files_verified'] = check_manifest()
        except BaseException as exc: record['integrity_error']=repr(exc); code=1
    save(mode + '_EXECUTION.json', record)
    return code

try:
    code = main()
except BaseException as exc:
    save(mode + '_SUPERVISOR_FAILURE.json', {'type':type(exc).__name__, 'error':str(exc)})
    raise
finally:
    if child is not None and child.poll() is None:
        os.killpg(child.pid,signal.SIGTERM)
        try: child.wait(timeout=3)
        except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL); child.wait()
    for f in handles: f.close()
raise SystemExit(code)
