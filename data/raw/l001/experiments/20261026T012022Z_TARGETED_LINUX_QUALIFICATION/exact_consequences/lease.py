"""Linux normal shared lease; reaps process-group descendants on every exit."""
import sys
sys.dont_write_bytecode = True
import ctypes
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
HERE=Path(__file__).resolve().parent
LOCK=Path('/tmp/research-20261012-astra-medium')
handles=[]
child=None
mode=sys.argv[1]
assert mode in ('freeze','run') and sys.platform=='linux'
assert ctypes.CDLL(None, use_errno=True).prctl(36,1,0,0,0)==0, 'SUBREAPER'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,r):
    with (HERE/n).open('x') as f:
        json.dump(r,f,indent=2);f.flush();os.fsync(f.fileno())
def take(p,create=False):
    f=p.open('a+' if create else 'r+')
    try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException: f.close();raise
    handles.append(f);return f
def check():
    ad=json.loads((HERE/'ADMISSION.json').read_text())
    assert ad['admitted'] is True and sha(HERE/'FROZEN.json')==ad['frozen_sha256']
    frozen=json.loads((HERE/'FROZEN.json').read_text())
    assert str(Path(sys.executable).resolve())==frozen['executable_realpath'],'ACTUAL_INTERPRETER_DIFFERS'
    files=frozen['files']
    for p,h in files.items(): assert sha(p)==h,p
    return len(files)
def cleanup():
    if child is None:return
    # Children never create a separate session. Stop the group even if leader exited.
    try:os.killpg(child.pid,signal.SIGTERM)
    except ProcessLookupError:pass
    grace=time.monotonic()+3
    while time.monotonic()<grace:
        child.poll()
        try:os.killpg(child.pid,0)
        except ProcessLookupError:break
        time.sleep(.02)
    try:os.killpg(child.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    child.wait()
    end=time.monotonic()+5
    while True:
        try:pid,_=os.waitpid(-1,os.WNOHANG)
        except ChildProcessError:return
        if not pid:
            assert time.monotonic()<end,'DESCENDANT_REAP_TIMEOUT'
            time.sleep(.02)
def main():
    global child
    assert (HERE/'SOURCE_REVIEW.md').is_file()
    assert not (HERE/(mode+'_EXECUTION.json')).exists()
    packet=take(HERE/'packet.lock',True)
    if mode=='run':assert not any((HERE/n).exists() for n in ('RESULT.json','FAILURE.json','RUNTIME_START.json'))
    admission=take(LOCK/'admission.lock')
    assert not any('hold' in p.name.lower() for p in LOCK.iterdir()),'HOLD'
    line=take(LOCK/'line-L001.lock',True)
    occupied=set()
    for row in subprocess.check_output(['ps','-eo','pid,pcpu,comm,args'],text=True).splitlines()[1:]:
        fields=row.split(None,3)
        if len(fields)!=4:continue
        pid,pct,comm,args=fields
        if int(pid)==os.getpid():continue
        science=any(s in comm.lower() for s in ('python','julia','wolfram','math','solver','mpirun'))
        system=any(s in args for s in ('unattended-upgrade','update-manager','check-new-release'))
        if (science and not system) or (float(pct)>20 and not args.startswith('[')):
            try:occupied.update(os.sched_getaffinity(int(pid)))
            except ProcessLookupError:pass
    available=[]
    for cpu in sorted(os.sched_getaffinity(0)):
        p=LOCK/('cpu-'+str(cpu)+'.lock')
        if not p.exists():continue
        try:f=take(p)
        except (BlockingIOError,PermissionError):occupied.add(cpu);continue
        if cpu in occupied:f.close();handles.remove(f)
        else:available.append((cpu,f))
    mem=int(next(s.split()[1] for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith('MemAvailable:')))
    assert available and len(occupied|{available[0][0]})<=2 and mem>=4*1024**2,'RESOURCE_HOLD'
    cpu,lease=available[0]
    for _,f in available[1:]:f.close();handles.remove(f)
    admission.close();handles.remove(admission)
    os.sched_setaffinity(0,{cpu})
    if mode=='run':check()
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
    os.environ.update(PYTHONDONTWRITEBYTECODE='1',PYTHONHASHSEED='0',PYTHONNOUSERSITE='1')
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    start=time.monotonic();cap=210 if mode=='run' else 120
    rec=dict(start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cpu=cpu,cores=1,mode=mode,
             occupied_cpus=sorted(occupied),timeout_seconds=cap,executable=sys.executable,executable_sha256=sha(sys.executable))
    save(mode+'_START.json',rec)
    with (HERE/(mode+'.log')).open('x') as log:
        child=subprocess.Popen([sys.executable,'-I','-B',str(HERE/('producer.py' if mode=='run' else 'freeze.py'))],
            stdout=log,stderr=subprocess.STDOUT,start_new_session=True,pass_fds=(line.fileno(),lease.fileno(),packet.fileno()))
        try:code=child.wait(timeout=cap)
        except subprocess.TimeoutExpired:code=124
        finally:cleanup()
    rec.update(exit_code=code,child_pid=child.pid,child_reaped=True,descendants_reaped=True,wall_seconds=time.monotonic()-start)
    if mode=='run':rec['post_frozen_files_verified']=check()
    save(mode+'_EXECUTION.json',rec)
    return code
def stop(s,f):raise InterruptedError('SUPERVISOR_SIGNAL_'+str(s))
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:code=main()
except BaseException as e:
    save(mode+'_SUPERVISOR_FAILURE.json',dict(error=repr(e)));raise
finally:
    cleanup()
    for f in handles:f.close()
raise SystemExit(code)
