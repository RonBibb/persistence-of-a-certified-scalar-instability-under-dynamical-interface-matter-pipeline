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
    assert chosen is not None and len(occupied|{chosen})<=2,'RESOURCE_HOLD'
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
def freeze():
    assert (ROOT/'SOURCE_REVIEW.md').is_file()
    import ast
    for source in ROOT.glob('*.py'):
        ast.parse(source.read_text(),filename=str(source))
    closure=PARENT/'CLOSURE_MANIFEST.json'
    assert sha(closure)=='2ab20917e9e8d56fc8c285f10099c1fc1e6cc74836e1ebb51716ab13b8fa0751'
    for relative,digest in read(closure)['files'].items():
        assert sha(PARENT/relative)==digest,'PARENT_CLOSURE:'+relative
    paths={p for p in PARENT.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    rt=read(QUAL/'mass_audit_runtime_r1/FROZEN.json')
    for p,d in rt['files'].items():assert sha(p)==d,p;paths.add(Path(p))
    paths.update(p for p in ROOT.iterdir() if p.suffix in ('.py','.md') and p.name!='STATUS.md')
    paths.update(p for p in QUAL.rglob('*') if p.is_file() and p.suffix in ('.json','.md','.py'))
    paths.update(Path(p) for p in observed())
    record={'files':{str(p.resolve()):sha(p) for p in sorted(paths)},'executable':str(Path(sys.executable).resolve()),
            'precision':768,'threads':1,'parent_manifest_sha256':sha(closure),'platform':platform.platform()}
    put('FROZEN.json',record);print(json.dumps({'files':len(paths),'frozen_sha256':sha(ROOT/'FROZEN.json')}),flush=True)
def verify():
    f=read(ROOT/'FROZEN.json')
    assert str(Path(sys.executable).resolve())==f['executable']
    for p,d in f['files'].items():assert sha(p)==d,p
    return f
def module(name):
    s=importlib.util.spec_from_file_location(name,ROOT/(name+'.py'));m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def execute(mode):
    admission=read(ROOT/'ADMISSION.json');assert admission['admitted'] is True
    assert admission['frozen_sha256']==sha(ROOT/'FROZEN.json')
    frozen=verify();sys.path.insert(0,str(FLINT));sys.path.insert(0,str(ROOT))
    import flint
    flint.ctx.prec=768;flint.ctx.threads=1
    before=observed();put(mode+'_RUNTIME_BEFORE.json',before)
    assert all(frozen['files'].get(p)==d for p,d in before.items()),'UNBOUND_RUNTIME_BEFORE'
    started=time.monotonic()
    if mode=='controls':
        result=module('controls').run(ROOT)
        result['pass']=result['all_gates']
        put('CONTROLS_RESULT.json',result)
    elif mode=='probe':
        assert read(ROOT/'CONTROLS_RESULT.json')['pass'] is True
        module('probe').run()
    else:
        production=read(ROOT/'PRODUCTION_ADMISSION.json')
        assert production['admitted'] is True and production['frozen_sha256']==sha(ROOT/'FROZEN.json')
        assert production['projected_seconds']<3600
        assert read(ROOT/'probe_TERMINAL.json')['pass'] is True
        module('production').run()
    after=observed();put(mode+'_RUNTIME_AFTER.json',after)
    assert all(frozen['files'].get(p)==d for p,d in after.items()),'UNBOUND_RUNTIME_AFTER'
    verify();put(mode+'_TERMINAL.json',{'pass':True,'seconds':time.monotonic()-started,'frozen_sha256':sha(ROOT/'FROZEN.json'),'runtime_coverage':True})

if __name__=='__main__':
    mode=sys.argv[1];assert mode in ('freeze','controls','probe','production') and sys.platform=='linux'
    try:
        cpu,occupied=acquire()
        for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[k]='1'
        os.environ.update(PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',PYTHONHASHSEED='0')
        put(mode+'_START.json',{'cpu':cpu,'occupied_cpus':occupied,'pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BOUNDED_'+mode)))
        signal.alarm(3500 if mode=='production' else 600 if mode=='probe' else 300)
        freeze() if mode=='freeze' else execute(mode)
    except BaseException as exc:
        put(mode+'_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in handles:f.close()
