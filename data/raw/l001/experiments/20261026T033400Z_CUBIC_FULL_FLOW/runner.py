"""Bounded full cubic execution; inherited leases and frozen runtime."""
import sys
sys.dont_write_bytecode=True
import ast,datetime,importlib.util,json,os,shutil,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T033000Z_CUBIC_PROBE_R1'
EXPECTED='1b8bed527169756b4dfcafaca2a916bfd804f74761a81f20032f212ce82a5a2a'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
base=load('accepted_probe_runner',PARENT/'runner.py');lease=base.lease;lease.ROOT=ROOT
store=load('storage',ROOT/'storage.py');sha,read,put=store.sha,store.read,store.put
def verify():
    f=read(ROOT/'FROZEN.json');assert str(Path(sys.executable).resolve())==f['executable']
    for p,d in f['files'].items():assert sha(p)==d,'BOUND:'+p
    return f
def preload():
    sys.path.insert(0,str(lease.FLINT));sys.path.insert(0,str(ROOT))
    import flint
    flint.ctx.prec=768;flint.ctx.threads=1
    flow=load('flow',ROOT/'flow.py');audit=load('audit',ROOT/'audit.py')
    if hasattr(audit,'setup'):audit.setup()
    return flow,audit
def freeze():
    assert (ROOT/'SOURCE_REVIEW.md').is_file() and sha(PARENT/'FROZEN.json')==EXPECTED
    files=dict(read(PARENT/'FROZEN.json')['files'])
    for p,d in files.items():assert sha(p)==d,'PARENT:'+p
    for mode in ('production','audit'):
        t=read(PARENT/(mode+'_TERMINAL.json'));assert t['pass'] and t['frozen_sha256']==EXPECTED
        for p,d in t['artifacts'].items():assert sha(PARENT/p)==d;files[str(PARENT/p)]=d
    for name in ('FROZEN.json','ADMISSION.json','production_TERMINAL.json','audit_TERMINAL.json','FINAL_REPORT.md','FINAL_REVIEW.md','INDEPENDENT_TERMINAL_CHECK.json','READOUT.json','ARCHIVE_READOUT.json'):
        files[str(PARENT/name)]=sha(PARENT/name)
    for p in ROOT.iterdir():
        if p.suffix in ('.py','.md') and p.name!='STATUS.md':files[str(p)]=sha(p)
    files.update(lease.observed())
    put('FROZEN.json',{'files':files,'executable':str(Path(sys.executable).resolve()),'precision':768,'threads':1,'parent_frozen_sha256':EXPECTED})
    print(json.dumps({'frozen_sha256':sha(ROOT/'FROZEN.json'),'files':len(files)}),flush=True)
def production_terminal():
    t=read(ROOT/'production_TERMINAL.json');assert t['pass'] and t['frozen_sha256']==sha(ROOT/'FROZEN.json')
    for p,d in t['artifacts'].items():assert sha(ROOT/p)==d,'RESULT_BINDING:'+p
    return t
def execute(mode,flow,audit):
    frozen=verify();before=lease.observed();put(mode+'_RUNTIME_BEFORE.json',before)
    assert all(frozen['files'].get(p)==d for p,d in before.items()),'UNBOUND_BEFORE'
    start=time.monotonic()
    if mode=='production':
        result=flow.run();artifact='RESULT.json';names=['RESULT.json','CONTROLS_RESULT.json','FLOW_primary.json','FLOW_independent.json']
    else:
        production_terminal();result=audit.run();artifact='AUDIT_RESULT.json';names=[artifact]
    assert result['pass'];put(artifact,result)
    after=lease.observed();put(mode+'_RUNTIME_AFTER.json',after)
    assert all(frozen['files'].get(p)==d for p,d in after.items()),'UNBOUND_AFTER'
    verify()
    if mode=='audit':production_terminal()
    put(mode+'_TERMINAL.json',{'pass':True,'seconds':time.monotonic()-start,'runtime_coverage':True,'frozen_sha256':sha(ROOT/'FROZEN.json'),'artifacts':{n:sha(ROOT/n) for n in names}})
    print(json.dumps({'mode':mode,'pass':True,'seconds':time.monotonic()-start,'classification':result['classification']}),flush=True)
if __name__=='__main__':
    mode=sys.argv[1];assert mode in ('freeze','production','audit') and sys.platform=='linux'
    assert not any(ROOT.glob('*FAILURE.json')) and not (ROOT/(mode+'_START.json')).exists(),'NO_RESTART'
    try:
        cpu,occupied=lease.acquire()
        assert all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'))
        assert os.environ.get('PYTHONHASHSEED')=='0'
        if mode=='production':assert shutil.disk_usage(ROOT).free>=10*1024**3,'OUTPUT_SPACE_HOLD'
        remaining=int(3000-(read(ROOT/'production_TERMINAL.json')['seconds'] if mode=='audit' else 0));assert remaining>0
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('FULL_CUBIC_OPERATIONAL_3000_SECONDS')));signal.alarm(remaining)
        put(mode+'_START.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pid':os.getpid(),'cpu':cpu,'occupied_cpus':occupied})
        if mode!='freeze':
            a=read(ROOT/'ADMISSION.json');assert a['admitted'] and a['frozen_sha256']==sha(ROOT/'FROZEN.json');verify()
        for p in ROOT.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
        flow,audit=preload();freeze() if mode=='freeze' else execute(mode,flow,audit)
    except BaseException as e:
        put(mode+'_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
