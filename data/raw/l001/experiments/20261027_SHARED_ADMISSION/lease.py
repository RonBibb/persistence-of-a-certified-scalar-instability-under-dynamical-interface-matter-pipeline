"""Single-core Linux lease, immutable binding, bounded qualification/probe."""
import sys
sys.dont_write_bytecode=True
import argparse, contextlib, datetime, fractions, hashlib, importlib.util, inspect, json, math, os, platform, resource, selectors, signal, subprocess, time, traceback, fcntl
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION'
QUAL=ROOT.parent/'20261026T012022Z_TARGETED_LINUX_QUALIFICATION'
LOCK=Path('/tmp/research-20261012-astra-medium')
FLINT=Path('/home/parallels/research-runs/cap-interval-arb-2026-09-12')
handles=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def put(name,value):
    path=ROOT/name;tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x') as f:json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,path);tmp.unlink()
def lock(p,create=False):
    f=p.open('a+' if create else 'r+')
    try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:f.close();raise
    handles.append(f);return f
def acquire():
    lock(ROOT/'packet.lock',True);ad=lock(LOCK/'admission.lock')
    assert not any('hold' in x.name.lower() for x in LOCK.iterdir()),'HOLD'
    lock(LOCK/'line-L001.lock',True)
    occupied=set()
    for row in subprocess.check_output(['ps','-eo','pid,pcpu,comm,args'],text=True).splitlines()[1:]:
        f=row.split(None,3)
        if len(f)!=4:continue
        pid,pct,comm,args=f
        if int(pid)==os.getpid():continue
        science=any(s in comm.lower() for s in ('python','julia','wolfram','math','solver','mpirun'))
        system=any(s in args for s in ('unattended-upgrade','update-manager','check-new-release'))
        if (science and not system) or (float(pct)>20 and not args.startswith('[')):
            try:occupied.update(os.sched_getaffinity(int(pid)))
            except ProcessLookupError:pass
    chosen=None
    for cpu in sorted(os.sched_getaffinity(0)):
        if cpu in occupied or not (LOCK/f'cpu-{cpu}.lock').exists():continue
        try:lease=lock(LOCK/f'cpu-{cpu}.lock')
        except BlockingIOError:continue
        chosen=cpu;break
    assert chosen is not None and len(occupied|{chosen})<=10,'RESOURCE_HOLD'
    mem=int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))
    assert mem>=4*1024**2,'MEMORY_HOLD'
    os.sched_setaffinity(0,{chosen});ad.close();handles.remove(ad)
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    return chosen,sorted(occupied)
def observed():
    platform.platform()
    paths={Path(sys.executable).resolve()}
    for mod in list(sys.modules.values()):
        p=getattr(mod,'__file__',None)
        if p and Path(p).is_file():paths.add(Path(p).resolve())
    for row in Path('/proc/self/maps').read_text().splitlines():
        f=row.split(None,5)
        if len(f)==6 and f[5].startswith('/') and Path(f[5]).is_file():paths.add(Path(f[5]).resolve())
    return {str(p):sha(p) for p in sorted(paths)}
