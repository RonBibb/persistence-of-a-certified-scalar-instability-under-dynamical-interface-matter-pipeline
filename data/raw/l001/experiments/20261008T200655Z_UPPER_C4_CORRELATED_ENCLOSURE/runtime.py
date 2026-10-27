"""Line-owned frozen inputs, native arithmetic recovery and CPU leases."""
from pathlib import Path
import sys, os, json, time, platform, resource, fcntl, hashlib
from fractions import Fraction as Q
from flint import arb, fmpq, ctx
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261008T133803Z_C6_PREPARATION_CERTIFICATE/launch-repair-r1'
WIDTH=ROOT.parent/'20261008T154505Z_C6_RESIDUAL_WIDTH_ATTRIBUTION'
LIN=ROOT.parents[3]
SHARED=LIN/'shared/integration'/ROOT.name
INITIAL=LIN/'lines/L002-initial-data-boundary-construction/experiments/20261008T200655Z_C4_ENCLOSURE_ADMISSION_C6_AUDIT'
AUTH=LIN.parent/'program-hub/rounds/20261008T200655Z_NEXT_STEPS/CONTRACT.md'
sys.path[:0]=[str(PARENT),str(PARENT/'inherited')]
import records as rec
import physics
from inherited.series import bounds, interval
CFG=rec.read(ROOT/'CONTRACT.json')
def loc(path):
    s=str(path)
    return Path(s.replace('/Users/ronbibb/','/media/psf/Home/',1)) if platform.system()=='Linux' and s.startswith('/Users/ronbibb/') else Path(s)
def exact(x):
    q=Q(str(x));return fmpq(q.numerator,q.denominator)
def mag(x):return max(abs(a) for a in bounds(x))
def record_pair(v):
    lo,hi=v
    return {'exact':[str(lo),str(hi)],'halfwidth':str((hi-lo)/2),'midpoint':str((hi+lo)/2),'decimal':[float(lo),float(hi)]}
def record(x):return record_pair(bounds(x))
def overlap(a,b):return max(bounds(a)[0],bounds(b)[0])<=min(bounds(a)[1],bounds(b)[1])
def literal(bits,kind):
    if kind=='F':return [list(map(exact,v)) for v in rec.read(PARENT/f'RAW_DECISION_{bits}.json')['residual_at_center']]
    return [list(map(exact,v['exact'])) for v in rec.read(PARENT/'DECISION.json')['producer_arb_decisions'][str(bits)]['center_displacement']]
def predecessor_intersections(bits,kind):
    out=literal(bits,kind);key='residuals' if kind=='F' else 'center_corrections'
    for mode in ('independent_jets','hamiltonian_linked','canonical_linked'):
        d=rec.read(WIDTH/'raw'/f'{bits}-{mode}.json')
        for i,row in enumerate(d[key]):
            lo,hi=map(exact,row['mean_value_enclosure']['exact']);a,b=out[i]
            out[i]=[max(a,lo),min(b,hi)];assert out[i][0]<=out[i][1]
    return out
def native_runtime():
    import flint
    return {'python':platform.python_version(),'flint':flint.__version__,
      'executable':str(Path(sys.executable).resolve()),'executable_sha256':rec.sha(Path(sys.executable).resolve()),
      'flint_native_hashes':{str(p):rec.sha(p) for p in sorted(Path(flint.__file__).resolve().parent.rglob('*.so'))},'threads':int(ctx.threads)}
def freeze():
    assert not (ROOT/'BINDINGS.json').exists()
    assert rec.sha(PARENT/'BINDINGS.json')==CFG['predecessor_guard']
    assert rec.sha(WIDTH/'BINDINGS_EXACT_ENDPOINTS.json')==CFG['width_guard']
    old=rec.read(WIDTH/'BINDINGS_EXACT_ENDPOINTS.json')
    inp={str(loc(p)):h for p,h in old['inputs'].items()}
    for n,h in old['sources'].items():inp[str(WIDTH/n)]=h
    for p in [AUTH,INITIAL/'ADMISSION_PROTOCOL.md',INITIAL/'FREEZE.json',INITIAL/'PREPRODUCTION_IDENTITY_REVIEW.md']:
        inp[str(p)]=rec.sha(p)
    for n in ('BINDINGS_EXACT_ENDPOINTS.json','FREEZE_EXACT_ENDPOINTS.json','RESULT.json','TERMINAL.json','LOCAL_AUDIT.json'):
        inp[str(WIDTH/n)]=rec.sha(WIDTH/n)
    for p in (LIN/'shared/integration'/WIDTH.name).glob('*AUDIT.json'):inp[str(p)]=rec.sha(p)
    p=LIN/'shared/integration'/WIDTH.name/'JOINT_RECEIPT.json';inp[str(p)]=rec.sha(p)
    for p in (WIDTH/'raw').glob('*.json'):inp[str(p)]=rec.sha(p)
    for p,h in inp.items():assert rec.sha(p)==h,p
    names=['CONTRACT.json','DERIVATION.txt','.gitignore']+[p.name for p in sorted(ROOT.glob('*.py'))]
    b={'utc':rec.now(),'inputs':inp,'sources':{n:rec.sha(ROOT/n) for n in names},'runtime':native_runtime(),
       'no_new_numerical_outcome_before_freeze':True}
    rec.atomic(ROOT/'BINDINGS.json',b,True)
    rec.atomic(ROOT/'FREEZE.json',{'utc':rec.now(),'guard':rec.sha(ROOT/'BINDINGS.json')},True)
    for n in names:(ROOT/n).chmod(0o444)
    return rec.sha(ROOT/'BINDINGS.json')
def guard():
    b=rec.read(ROOT/'BINDINGS.json');g=rec.sha(ROOT/'BINDINGS.json')
    assert rec.read(ROOT/'FREEZE.json')['guard']==g
    for n,h in b['sources'].items():assert rec.sha(ROOT/n)==h,n
    for p,h in b['inputs'].items():assert rec.sha(loc(p))==h,p
    assert b['runtime']==native_runtime()
    return g
def status(out,state,**kw):rec.atomic(out/'STATUS.json',dict(state=state,utc=rec.now(),pid=os.getpid(),**kw))
def case_id(g,bits,mode):
    return rec.fingerprint({'guard':g,'bits':bits,'mode':mode,'phase_order':CFG['restart']['phases']})
def commit(out,state,cid):
    body={'case_fingerprint':cid,'state':rec.pack(state)}
    state=rec.unpack(body['state']);digest=rec.fingerprint(body)
    path=f"checkpoints/{state['phase']:02d}-{digest}.json"
    if not (out/path).exists():rec.atomic(out/path,body,True)
    rec.atomic(out/'LATEST.json',{'case_fingerprint':cid,'path':path,'digest':digest})
    status(out,'RUNNING',phase=state['phase'],bits=state['bits'],mode=state['mode'],case_fingerprint=cid,last_checkpoint=path)
    return state
def load(out,cid):
    ptr=rec.read(out/'LATEST.json');assert ptr['case_fingerprint']==cid,'case fingerprint mismatch'
    p=(out/ptr['path']).resolve();assert p.parent==(out/'checkpoints').resolve()
    b=rec.read(p);assert b['case_fingerprint']==cid and rec.fingerprint(b)==ptr['digest']
    return rec.unpack(b['state'])
def acquire(out):
    assert platform.system()=='Linux'
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):assert os.environ.get(k)=='1'
    resource.setrlimit(resource.RLIMIT_AS,(CFG['resources']['address_space_bytes_per_worker'],)*2)
    SHARED.mkdir(parents=True,exist_ok=True);out.mkdir(parents=True,exist_ok=True)
    held=[]
    for cpu in CFG['resources']['cpu_pool']:
        fs=[]
        try:
            for p,m in [(Path('/media/psf/Home/Research/ClaudeCode/runtime')/f'compute-slot-{cpu+1}.lock','r'),(SHARED/f'cpu-{cpu}.lock','a+')]:
                f=p.open(m);fs.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            held=fs;break
        except BlockingIOError:
            for f in fs:f.close()
    if not held:raise RuntimeError('No available research CPU lease')
    try:
        f=(out/'worker.lock').open('a+');held.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        os.sched_setaffinity(0,{cpu});ctx.threads=1
    except BaseException:
        for f in held:f.close()
        raise
    ident={'cpu':cpu,'slot':cpu+1,'pid':os.getpid(),'start_ticks':Path('/proc/self/stat').read_text().split()[21],
       'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'locks':[str(f.name) for f in held],
       'utc':rec.now(),'active':True}
    rec.atomic(out/f'ACQUIRED-{os.getpid()}.json',ident,True)
    return held,ident
def release(out,held,ident,start):
    d=dict(ident,active=False,utc=rec.now(),wall_seconds=time.monotonic()-start,cpu_seconds=time.process_time(),
       peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    rec.atomic(out/f'RELEASED-{os.getpid()}.json',d,True)
    for f in reversed(held):fcntl.flock(f,fcntl.LOCK_UN);f.close()
