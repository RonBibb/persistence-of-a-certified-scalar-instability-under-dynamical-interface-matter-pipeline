"""Leased bounded qualification, no full-flow admission."""
import sys
sys.dont_write_bytecode=True
import ast,datetime,importlib.util,os,signal,time,traceback,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T023331Z_CUBIC_GRAPH'
EXPECTED='e0e89f255d5c74a29b788976ab1f232358df496c800e022314664a58b20645de'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
base=load('accepted_graph_runner',PARENT/'runner.py');lease=base.lease;lease.ROOT=ROOT
read,sha,put=lease.read,lease.sha,lease.put
def verify():
    f=read(ROOT/'FROZEN.json')
    assert str(Path(sys.executable).resolve())==f['executable']
    for p,d in f['files'].items():assert sha(p)==d,'BOUND:'+p
    return f
def preload():
    sys.path.insert(0,str(lease.FLINT));sys.path.insert(0,str(ROOT))
    import flint
    flint.ctx.prec=768;flint.ctx.threads=1
    return load('qualifier',ROOT/'qualifier.py'),load('audit',ROOT/'audit.py')
def freeze():
    assert (ROOT/'SOURCE_REVIEW.md').is_file()
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert sha(PARENT/'FROZEN.json')==EXPECTED,'PARENT_FREEZE'
    files=dict(read(PARENT/'FROZEN.json')['files'])
    for p,d in files.items():assert sha(p)==d,'PARENT:'+p
    for mode in ('production','audit'):
        t=read(PARENT/(mode+'_TERMINAL.json'));assert t['pass'] and t['frozen_sha256']==EXPECTED
        assert sha(PARENT/t['artifact'])==t['artifact_sha256']
    for name in ('FROZEN.json','ADMISSION.json','RESULT.json','AUDIT_RESULT.json','production_TERMINAL.json','audit_TERMINAL.json','FINAL_REPORT.md','FINAL_REVIEW.md'):
        p=PARENT/name;files[str(p)]=sha(p)
    manuscript=Path('/media/psf/Home/Research/papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md');files[str(manuscript)]=sha(manuscript)
    for p in ROOT.iterdir():
        if p.suffix in ('.py','.md') and p.name!='STATUS.md':files[str(p)]=sha(p)
    files.update(lease.observed())
    put('FROZEN.json',{'files':files,'executable':str(Path(sys.executable).resolve()),'precision':768,'threads':1,'parent_frozen_sha256':EXPECTED})
    print(json.dumps({'frozen_sha256':sha(ROOT/'FROZEN.json'),'files':len(files)}),flush=True)
def execute(mode,qualifier,audit):
    frozen=verify();before=lease.observed();put(mode+'_RUNTIME_BEFORE.json',before)
    assert all(frozen['files'].get(p)==d for p,d in before.items()),'UNBOUND_BEFORE'
    start=time.monotonic()
    if mode=='production':result=qualifier.run();artifact='RESULT.json'
    else:
        t=read(ROOT/'production_TERMINAL.json');assert t['pass'] and t['frozen_sha256']==sha(ROOT/'FROZEN.json') and t['artifact_sha256']==sha(ROOT/'RESULT.json')
        result=audit.run();artifact='AUDIT_RESULT.json'
    assert result['pass'];put(artifact,result)
    after=lease.observed();put(mode+'_RUNTIME_AFTER.json',after)
    assert all(frozen['files'].get(p)==d for p,d in after.items()),'UNBOUND_AFTER'
    verify()
    if mode=='audit':assert read(ROOT/'production_TERMINAL.json')['artifact_sha256']==sha(ROOT/'RESULT.json')
    put(mode+'_TERMINAL.json',{'pass':True,'seconds':time.monotonic()-start,'runtime_coverage':True,'frozen_sha256':sha(ROOT/'FROZEN.json'),'artifact':artifact,'artifact_sha256':sha(ROOT/artifact)})
    print(json.dumps({'mode':mode,'pass':True,'classification':result['classification'],'seconds':time.monotonic()-start}),flush=True)
if __name__=='__main__':
    mode=sys.argv[1];assert mode in ('freeze','production','audit') and sys.platform=='linux'
    assert not any(ROOT.glob('*FAILURE.json')) and not (ROOT/(mode+'_START.json')).exists(),'NO_RESTART'
    try:
        cpu,occupied=lease.acquire()
        assert all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'))
        assert os.environ.get('PYTHONHASHSEED')=='0'
        remaining=int(300-(read(ROOT/'production_TERMINAL.json')['seconds'] if mode=='audit' else 0));assert remaining>0
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('QUALIFICATION_300_SECONDS')));signal.alarm(remaining)
        put(mode+'_START.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'cpu':cpu,'occupied_cpus':occupied})
        if mode!='freeze':
            a=read(ROOT/'ADMISSION.json');assert a['admitted'] and a['frozen_sha256']==sha(ROOT/'FROZEN.json');verify()
        qualifier,audit=preload()
        freeze() if mode=='freeze' else execute(mode,qualifier,audit)
    except BaseException as e:
        put(mode+'_FAILURE.json',{'classification':'QUALIFICATION_INCONCLUSIVE' if hasattr(e,'evidence') else 'TECHNICAL_INCOMPLETE','error':repr(e),'evidence':getattr(e,'evidence',None),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
