"""Bound inputs, exact records, and exclusive resources for this experiment."""
from pathlib import Path
import sys, os, json, hashlib, platform, resource, fcntl, time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'inherited'))
import records as rec
from flint import arb, fmpq, ctx
from fractions import Fraction as Q
CFG=rec.read(ROOT/'CONTRACT.json')
def loc(path):
    p=Path(path)
    if platform.system()=='Linux' and str(p).startswith('/Users/ronbibb/'):
        return Path('/media/psf/Home')/p.relative_to('/Users/ronbibb')
    return p
def exact(x):
    q=Q(str(x)); return fmpq(q.numerator,q.denominator)
def source(name): return loc(CFG['sources'][name])
def inputs():
    auth=Path('/media/psf/Home/Research' if platform.system()=='Linux' else '/Users/ronbibb/Research')/'research_repositories/program-hub/rounds/20261008T133803Z_LIN_C6_CERTIFICATE'
    return {
      'authorization':auth/'AUTHORIZATION.json','governing_contract':auth/'CERTIFICATE_CONTRACT.md',
      'c4_binding':source('c4')/'BINDINGS.json','c4_result':source('c4')/'RESULT.json',
      'c4_audit':source('c4')/'INDEPENDENT_AUDIT.json',
      'native_binding':source('native')/'BINDINGS.json','native_seed':source('native')/'results/fine_c4/SEED.json',
      'native_old':source('native')/'results/fine_c4/case_3.dense.json',
      'c6_result':source('c6')/'RESULT.json','c6_integrity':source('c6')/'INTEGRITY.json',
      'c6_model':source('c6')/'code/model.py','c6_p100':source('c6')/'results/p100/CANDIDATE.json',
      'c6_dense100':source('c6')/'results/p100/case_3.dense.json',
      'c6_matrix100':source('c6')/'results/p100/MATRICES.json',
      'c6_readback100':source('c6')/'results/p100/INDEPENDENT_READBACK.json',
      'source_binding':source('contracted_source')/'BINDINGS.json',
      'source_result':source('contracted_source')/'RESULT.json',
      'source_integrity':source('contracted_source')/'RESULT_INTEGRITY.json',
      'source_terminal':source('contracted_source')/'TERMINAL.json',
      'source_flow_result':source('contracted_source')/'output/contracted_source/RESULT.json',
      'canonical_preparation':source('contracted_source')/'output/PREPARATION.json',
      'bridge_packet':source('prior_bridge')/'STATIC_BRIDGE_PACKET.json',
      'bridge_result':source('prior_bridge')/'RESULT.json',
      'bridge_audit':source('prior_bridge')/'AUDIT.json',
      'initial_analytic_review':loc('/Users/ronbibb/Research/research_repositories/lin/shared/integration/20261008T133803Z_C6_PREPARATION_CERTIFICATE/INITIAL_ANALYTIC_REVIEW.json'),
      'initial_analytic_notes':loc('/Users/ronbibb/Research/research_repositories/lin/lines/L009-initial-data-boundary-construction/experiments/20261008T133803Z_C6_PREPARATION_CERTIFICATE_AUDIT/INDEPENDENT_CORNER_AND_MAP_NOTES.txt')
    }
def loadin(key,native=False):
    d=rec.read(inputs()[key]); return rec.unpack(d) if native else d
def sourcelist():
    names=['CONTRACT.json','DERIVATION.txt','DESIGN.json']
    return names+[str(p.relative_to(ROOT)) for p in sorted(ROOT.glob('*.py'))]+[str(p.relative_to(ROOT)) for p in sorted((ROOT/'inherited').glob('*.py'))]
def runtime():
    import flint,mpmath
    base=Path(flint.__file__).resolve().parent
    native=sorted(base.rglob('*.so'))+sorted((base.parent/'python_flint.libs').glob('*'))
    return {'python':platform.python_version(),'flint':flint.__version__,'mpmath':mpmath.__version__,
      'executable':str(Path(sys.executable).resolve()),'executable_sha256':rec.sha(Path(sys.executable).resolve()),
      'flint_path':str(Path(flint.__file__).resolve()),'flint_init_sha256':rec.sha(flint.__file__),
      'native_library_hashes':{str(p):rec.sha(p) for p in native if p.is_file()},
      'threads':int(ctx.threads)}
def guard(full=True):
    b=rec.read(ROOT/'BINDINGS.json'); g=rec.sha(ROOT/'BINDINGS.json')
    assert rec.read(ROOT/'FREEZE.json')['bindings_sha256']==g
    for n,h in b['sources'].items(): assert rec.sha(ROOT/n)==h, n
    assert runtime()==b['runtime'], 'Runtime changed'
    if full:
        for entry in b['inputs'].values(): assert rec.sha(loc(entry['path']))==entry['sha256'],entry['path']
        for entry in b['source_transitive']:
            assert rec.sha(loc(entry['path']))==entry['sha256'],entry['path']
    return g
def resources(cpu,job):
    assert platform.system()=='Linux' and cpu in CFG['execution']['cpu_pool']
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):
        assert os.environ.get(k)=='1',k
    resource.setrlimit(resource.RLIMIT_AS,(CFG['execution']['worker_address_space_bytes'],)*2)
    os.sched_setaffinity(0,{cpu}); ctx.threads=1
    shared=loc('/Users/ronbibb/Research/research_repositories/lin/shared/integration/20261008T133803Z_C6_PREPARATION_CERTIFICATE')
    # Existing coordinator tokens are numbered 1..11; use CPU+1, without rewriting them.
    paths=[shared/f'cpu-{cpu}.lock',Path('/media/psf/Home/Research/ClaudeCode/runtime')/f'compute-slot-{cpu+1}.lock']
    handles=[]
    try:
        for i,p in enumerate(paths):
            f=p.open('a+' if i==0 else 'r');handles.append(f)
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        mine=ROOT/'progress'/f'{job}.lock'; mine.parent.mkdir(exist_ok=True)
        f=mine.open('a+');handles.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:
        for f in reversed(handles):f.close()
        raise
    identity={'pid':os.getpid(),'cpu':cpu,'job':job,'start_ticks':Path('/proc/self/stat').read_text().split()[21],
      'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'locks':[str(p) for p in paths],
      'one_arithmetic_thread':True,'address_space_bytes':CFG['execution']['worker_address_space_bytes']}
    rec.atomic(ROOT/'progress'/f'{job}.resource.json',dict(identity,active=True,utc=rec.now()))
    return handles,identity
def release(handles,identity,start):
    rec.atomic(ROOT/'progress'/f"{identity['job']}.release.json",dict(identity,active=False,
      utc=rec.now(),wall_seconds=time.monotonic()-start,process_cpu_seconds=time.process_time(),
      peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
    for f in reversed(handles):fcntl.flock(f,fcntl.LOCK_UN);f.close()
