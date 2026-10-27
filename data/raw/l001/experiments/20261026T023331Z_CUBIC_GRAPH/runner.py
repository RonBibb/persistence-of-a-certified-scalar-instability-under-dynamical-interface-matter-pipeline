"""Bounded leased Linux execution; immutable parent/source/runtime binding."""
import sys
sys.dont_write_bytecode=True
import ast,datetime,hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
EXPECTED_PARENT='27b9c8799f3bedef8f49788284549e4ba7cffe5adf7cc5b7c85425c324bb5566'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
lease=load('cubic_lease',PARENT/'runner.py');lease.ROOT=ROOT
read,sha,put=lease.read,lease.sha,lease.put
def preload():
    sys.path.insert(0,str(lease.FLINT));sys.path.insert(0,str(ROOT))
    import flint
    flint.ctx.prec=768;flint.ctx.threads=1
    producer=load('producer',ROOT/'producer.py');audit=load('audit',ROOT/'audit.py')
    return producer,audit
def verify():
    f=read(ROOT/'FROZEN.json')
    assert str(Path(sys.executable).resolve())==f['executable']
    for p,d in f['files'].items():assert sha(p)==d,'BINDING:'+p
    return f
def freeze():
    assert (ROOT/'SOURCE_REVIEW.md').is_file()
    for p in ROOT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
    assert sha(PARENT/'FROZEN.json')==EXPECTED_PARENT,'PARENT_FREEZE'
    parent=read(PARENT/'terminal_audit/ADMISSION.json')
    files=dict(parent['files'])
    files.update(read(PARENT/'FROZEN.json')['files'])
    for p,d in files.items():assert sha(p)==d,'PARENT_BINDING:'+p
    assert read(PARENT/'production_TERMINAL.json')['pass'] is True
    assert read(PARENT/'terminal_audit/TERMINAL.json')['pass'] is True
    for name in ('PRODUCTION_primary.json','PRODUCTION_independent.json','PRODUCTION_RESULT.json','production_TERMINAL.json','FROZEN.json','FINAL_REPORT.md','FINAL_REVIEW.md','terminal_audit/ADMISSION.json','terminal_audit/AUDIT_RESULT.json','terminal_audit/TERMINAL.json'):
        p=PARENT/name;files[str(p)]=sha(p)
    for p in ROOT.iterdir():
        if p.suffix in ('.py','.md') and p.name!='STATUS.md':files[str(p)]=sha(p)
    files.update(lease.observed())
    put('FROZEN.json',{'files':files,'executable':str(Path(sys.executable).resolve()),'precision':768,'threads':1,'parent_frozen_sha256':EXPECTED_PARENT})
    print(json.dumps({'frozen_sha256':sha(ROOT/'FROZEN.json'),'files':len(files)}),flush=True)
def execute(mode,producer,audit):
    assert not any(ROOT.glob('*FAILURE.json')),'FAILED_CLOSED'
    admission=read(ROOT/'ADMISSION.json');assert admission['admitted'] is True and admission['frozen_sha256']==sha(ROOT/'FROZEN.json')
    frozen=verify();before=lease.observed();put(mode+'_RUNTIME_BEFORE.json',before)
    assert all(frozen['files'].get(p)==d for p,d in before.items()),'UNBOUND_BEFORE'
    started=time.monotonic()
    if mode=='production':
        result=producer.run();put('RESULT.json',result)
    else:
        assert read(ROOT/'production_TERMINAL.json')['pass'] is True
        assert read(ROOT/'production_TERMINAL.json')['artifact_sha256']==sha(ROOT/'RESULT.json'),'RESULT_BINDING'
        result=audit.run();assert result['pass'] is True;put('AUDIT_RESULT.json',result)
    after=lease.observed();put(mode+'_RUNTIME_AFTER.json',after)
    assert all(frozen['files'].get(p)==d for p,d in after.items()),'UNBOUND_AFTER'
    artifact='RESULT.json' if mode=='production' else 'AUDIT_RESULT.json'
    if mode=='audit':assert read(ROOT/'production_TERMINAL.json')['artifact_sha256']==sha(ROOT/'RESULT.json'),'RESULT_UNCHANGED'
    verify();put(mode+'_TERMINAL.json',{'pass':True,'seconds':time.monotonic()-started,'frozen_sha256':sha(ROOT/'FROZEN.json'),'runtime_coverage':True,'artifact':artifact,'artifact_sha256':sha(ROOT/artifact)})
    print(json.dumps({'mode':mode,'pass':True,'seconds':time.monotonic()-started,'classification':result.get('classification')}),flush=True)
if __name__=='__main__':
    mode=sys.argv[1];assert mode in ('freeze','production','audit') and sys.platform=='linux'
    assert not (ROOT/(mode+'_START.json')).exists(),'NO_RESTART'
    try:
        cpu,occupied=lease.acquire()
        assert all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')),'SINGLE_THREAD_ENV'
        assert os.environ.get('PYTHONHASHSEED')=='0','HASH_SEED'
        prior=read(ROOT/'production_TERMINAL.json')['seconds'] if mode=='audit' else 0
        remaining=int(300-prior);assert remaining>0,'AGGREGATE_OPERATIONAL_CAP'
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CUBIC_OPERATIONAL_300_SECONDS')));signal.alarm(remaining)
        put(mode+'_START.json',{'cpu':cpu,'occupied_cpus':occupied,'pid':os.getpid(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
        if mode!='freeze':
            assert not any(ROOT.glob('*FAILURE.json')),'FAILED_CLOSED'
            admission=read(ROOT/'ADMISSION.json')
            assert admission['admitted'] is True and admission['frozen_sha256']==sha(ROOT/'FROZEN.json'),'ADMISSION'
            verify()
        producer,audit=preload()
        freeze() if mode=='freeze' else execute(mode,producer,audit)
    except BaseException as exc:
        put(mode+'_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
