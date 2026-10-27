"""One-shot existing-lock admission; one core, no queue or retry."""
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
LOCK = Path('/tmp/research-20261012-astra-medium')
handles = []
child = None
start = time.monotonic()

def save(name,data):
    with (HERE/name).open('x') as f:
        json.dump(data,f,indent=2)
        f.flush()
        os.fsync(f.fileno())

def take(path, create=False):
    f = path.open('a+' if create else 'r+')
    try:
        fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:
        f.close()
        raise
    handles.append(f)
    return f

def main():
    global child
    assert sys.platform=='linux'
    packet = take(HERE/'packet.lock',True)
    assert not any((HERE/p).exists() for p in ('RESULT.json','FAILURE.json','EXECUTION.json','RESOURCE_HOLD.json'))
    admitted = json.loads((HERE/'ADMISSION.json').read_text())
    assert admitted['admitted'] is True
    for name,digest in admitted['sources'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest, name
    try:
        admission = take(LOCK/'admission.lock')
        if any('hold' in p.name.lower() for p in LOCK.iterdir()):
            raise RuntimeError('HOLD marker present')
        line = take(LOCK/'line-L001.lock',True)
        snapshot = subprocess.check_output(['ps','-eo','pid,pcpu,comm,args'],text=True)
        occupied = set()
        for row in snapshot.splitlines()[1:]:
            fields = row.split(None,3)
            if len(fields)!=4: continue
            pid,pct,comm,args = fields
            if int(pid)==os.getpid(): continue
            science = any(s in comm.lower() for s in ('python','julia','wolfram','math','solver','mpirun'))
            system = any(s in args for s in ('unattended-upgrade','update-manager','check-new-release'))
            if (science and not system) or (float(pct)>20 and not args.startswith('[')):
                try: occupied.update(os.sched_getaffinity(int(pid)))
                except ProcessLookupError: pass
        available = []
        for cpu in sorted(os.sched_getaffinity(0)):
            path = LOCK/('cpu-'+str(cpu)+'.lock')
            if not path.exists(): continue
            try: f = take(path)
            except (BlockingIOError,PermissionError): occupied.add(cpu); continue
            if cpu in occupied:
                f.close(); handles.remove(f)
            else: available.append((cpu,f))
        mem = int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))
        if not available or len(occupied|{available[0][0]})>10 or mem<4*1024**2:
            raise RuntimeError('shared CPU or memory admission unavailable')
        cpu,lease = available[0]
        for _,f in available[1:]:
            f.close(); handles.remove(f)
        admission.close(); handles.remove(admission)
    except (OSError,RuntimeError) as exc:
        save('RESOURCE_HOLD.json',{'classification':'RESOURCE_HOLD','reason':repr(exc),'queued_launch':False})
        return 75
    os.sched_setaffinity(0,{cpu})
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
        os.environ[key]='1'
    os.environ.update(PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',PYTHONNOUSERSITE='1')
    resource.setrlimit(resource.RLIMIT_AS,(1024**3,1024**3))
    receipt={'start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
             'cpu':cpu,'core_count':1,'memory_available_kib':mem,'timeout_seconds':910,
             'resource_cap_bytes':1024**3,'occupied_cpus':sorted(occupied),
             'child_inherits_cpu_and_line_locks':True}
    save('RESOURCE_START.json',receipt)
    with (HERE/'run.log').open('x') as log:
        child = subprocess.Popen([sys.executable,'-I','-B',str(HERE/'producer.py')],
                    stdout=log,stderr=subprocess.STDOUT,start_new_session=True,
                    pass_fds=(line.fileno(),lease.fileno(),packet.fileno()))
        try:
            code = child.wait(timeout=910)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGTERM)
            try: code=child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGKILL); code=child.wait()
    save('EXECUTION.json',dict(receipt,exit_code=code,wall_seconds=time.monotonic()-start,
                               child_pid=child.pid,child_reaped=True))
    return code

try:
    exit_code=main()
finally:
    if child is not None and child.poll() is None:
        os.killpg(child.pid,signal.SIGTERM)
        try: child.wait(timeout=3)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL); child.wait()
    for f in handles:
        f.close()
raise SystemExit(exit_code)
