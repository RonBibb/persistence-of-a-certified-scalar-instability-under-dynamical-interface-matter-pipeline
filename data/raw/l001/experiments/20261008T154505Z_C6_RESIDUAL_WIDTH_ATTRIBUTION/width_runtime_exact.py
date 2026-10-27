"""Read-only predecessor access and line-owned bounded diagnostic resources."""
from pathlib import Path
import sys,os,json,hashlib,platform,time,fcntl,resource
from fractions import Fraction as Q
from flint import arb,fmpq,ctx
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261008T133803Z_C6_PREPARATION_CERTIFICATE/launch-repair-r1'
sys.path.insert(0,str(PARENT));sys.path.insert(0,str(PARENT/'inherited'))
import records as rec
from inherited.series import bounds,interval
import physics
CFG=rec.read(ROOT/'CONTRACT.json')
def loc(s):
    p=Path(s)
    if platform.system()=='Linux' and str(p).startswith('/Users/ronbibb/'):
        return Path('/media/psf/Home')/p.relative_to('/Users/ronbibb')
    return p
REPOS=ROOT.parents[3]
SHARED=REPOS/'shared/integration/20261008T154505Z_C6_RESIDUAL_WIDTH_ATTRIBUTION'
AUTH=REPOS.parent/'program-hub/rounds/20261008T154505Z_CONCURRENT_LIN_OWNED_CHAKRABARTY'
def exact(x):
    z=Q(str(x));return fmpq(z.numerator,z.denominator)
def halfwidth(x):
    a,b=bounds(x);return (b-a)/2
def midpoint(x):
    a,b=bounds(x);return (b+a)/2
def magnitude(x):return max(abs(v) for v in bounds(x))
def record(x):
    a,b=bounds(x)
    return {'exact':[str(a),str(b)],'midpoint':str((a+b)/2),'halfwidth':str((b-a)/2),
       'decimal':[float(a),float(b)]}
def exact_record(pair):
    a,b=pair
    return {'exact':[str(a),str(b)],'midpoint':str((a+b)/2),'halfwidth':str((b-a)/2),'decimal':[float(a),float(b)]}
def overlap(a,b):return max(bounds(a)[0],bounds(b)[0])<=min(bounds(a)[1],bounds(b)[1])
def meet(a,b):
    lo=max(bounds(a)[0],bounds(b)[0]);hi=min(bounds(a)[1],bounds(b)[1])
    if lo>hi:raise ArithmeticError('Equivalent interval evaluations are disjoint')
    return interval(lo,hi)
def inputs():
    d={str(AUTH/n):rec.sha(AUTH/n) for n in ('CONTRACT.md','AUTHORIZATION.json','FOLDER_BINDINGS.json','INTEGRATION_VALUE_NOTE.md')}
    for n in ('AUDIT_PROTOCOL.md','OFF_SHELL_C2_IDENTITY.txt'):
        p=REPOS/'lines/L002-initial-data-boundary-construction/experiments/20261008T154505Z_C6_RESIDUAL_WIDTH_ATTRIBUTION_AUDIT'/n
        d[str(p)]=rec.sha(p)
    old=rec.read(PARENT/'BINDINGS.json')
    for n,h in old['sources'].items():d[str(PARENT/n)]=h
    for n in ('BINDINGS.json','FREEZE.json','PREFLIGHT.json','RESULT.json','TERMINAL.json','DECISION.json','RAW_DECISION_768.json','RAW_DECISION_1024.json','DESIGN.json','LOCAL_AUDIT.json','OWNER_REPORT.md'):
        d[str(PARENT/n)]=rec.sha(PARENT/n)
    for name in ('INITIAL_SCIENTIFIC_AUDIT.json','JOINT_RECEIPT.json'):
        p=REPOS/'shared/integration/20261008T133803Z_C6_PREPARATION_CERTIFICATE'/name;d[str(p)]=rec.sha(p)
    for bits in CFG['precisions']:
        out=PARENT/'output'/f'{bits}-center'
        for n in ('RESULT.json','TERMINAL.json','LATEST.json'):d[str(out/n)]=rec.sha(out/n)
        for p in sorted((out/'checkpoints').glob('*.json')):d[str(p)]=rec.sha(p)
    p=loc(old['inputs']['canonical_preparation']['path']);d[str(p)]=old['inputs']['canonical_preparation']['sha256']
    return d
def runtime():
    import flint
    base=Path(flint.__file__).resolve().parent
    return {'python':platform.python_version(),'flint':flint.__version__,'executable':str(Path(sys.executable).resolve()),
        'executable_sha256':rec.sha(Path(sys.executable).resolve()),
        'flint_native_hashes':{str(p):rec.sha(p) for p in sorted(base.rglob('*.so'))},'threads':int(ctx.threads)}
def freeze():
    if (ROOT/'BINDINGS_EXACT_ENDPOINTS.json').exists():raise RuntimeError('Already frozen')
    assert rec.sha(PARENT/'BINDINGS.json')==CFG['predecessor_guard']
    assert rec.read(PARENT/'TERMINAL.json')['result_sha256']==rec.sha(PARENT/'RESULT.json')
    paths=inputs()
    for p,h in paths.items():assert rec.sha(p)==h,p
    names=['CONTRACT.json','DERIVATION.txt','.gitignore','PREEXECUTION_CORRECTION.json']+[p.name for p in sorted(ROOT.glob('*.py'))]
    b={'utc':rec.now(),'sources':{n:rec.sha(ROOT/n) for n in names},'inputs':paths,'runtime':runtime(),
        'predecessor_guard':CFG['predecessor_guard'],'no_attribution_outcome_before_freeze':True}
    rec.atomic(ROOT/'BINDINGS_EXACT_ENDPOINTS.json',b,True)
    rec.atomic(ROOT/'FREEZE_EXACT_ENDPOINTS.json',{'utc':rec.now(),'guard':rec.sha(ROOT/'BINDINGS_EXACT_ENDPOINTS.json')},True)
    for n in names:(ROOT/n).chmod(0o444)
    return rec.sha(ROOT/'BINDINGS_EXACT_ENDPOINTS.json')
def guard():
    b=rec.read(ROOT/'BINDINGS_EXACT_ENDPOINTS.json');g=rec.sha(ROOT/'BINDINGS_EXACT_ENDPOINTS.json')
    assert rec.read(ROOT/'FREEZE_EXACT_ENDPOINTS.json')['guard']==g
    for n,h in b['sources'].items():assert rec.sha(ROOT/n)==h,n
    for p,h in b['inputs'].items():assert rec.sha(loc(p))==h,p
    assert runtime()==b['runtime']
    return g
def acquire():
    assert platform.system()=='Linux'
    for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):assert os.environ.get(key)=='1'
    resource.setrlimit(resource.RLIMIT_AS,(CFG['resources']['address_space_bytes'],)*2)
    SHARED.mkdir(parents=True,exist_ok=True);(ROOT/'progress').mkdir(exist_ok=True)
    held=[]
    for cpu in CFG['resources']['cpu_pool']:
        handles=[]
        try:
            for p,mode in [(Path('/media/psf/Home/Research/ClaudeCode/runtime')/f'compute-slot-{cpu+1}.lock','r'),(SHARED/f'cpu-{cpu}.lock','a+')]:
                f=p.open(mode);handles.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            held=handles;break
        except BlockingIOError:
            for f in handles:f.close()
    if not held:raise RuntimeError('No unclaimed research slot; no other worker interrupted')
    try:
        f=(ROOT/'progress'/'owner.lock').open('a+');held.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        os.sched_setaffinity(0,{cpu});ctx.threads=1
    except BaseException:
        for f in held:f.close()
        raise
    ident={'cpu':cpu,'slot':cpu+1,'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().split()[21],
       'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'locks':[str(f.name) for f in held],
       'active':True,'utc':rec.now(),'one_arithmetic_thread':True}
    rec.atomic(ROOT/'RESOURCE_ACQUIRED.json',ident,True)
    return held,ident
def release(held,ident,start):
    obj=dict(ident,active=False,utc=rec.now(),wall_seconds=time.monotonic()-start,
          cpu_seconds=time.process_time(),peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    rec.atomic(ROOT/'RESOURCE_RELEASED.json',obj,True)
    for f in reversed(held):fcntl.flock(f,fcntl.LOCK_UN);f.close()
def progress(state,**data):rec.atomic(ROOT/'progress'/'STATUS.json',dict(state=state,utc=rec.now(),pid=os.getpid(),**data))
def parent_result(bits):
    ctx.prec=bits;physics.Dual.size=5
    return rec.unpack(rec.read(PARENT/'output'/f'{bits}-center/RESULT.json'))
