"""Bounded leased exact-symbolic qualification. No numerical evolution."""
import sys
sys.dont_write_bytecode=True
import ast,hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
lease=None
if __name__=='__main__':
    assert sys.platform=='linux'
    frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
    assert sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
    files=read(frozen)['files']
    for p,d in files.items():assert sha(p)==d,'PARENT:'+p
    lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
    assert files[str(lp)]==sha(lp)
    lease=load('cubic_general_lease',lp);lease.ROOT=ROOT
    try:
        assert not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json')),'NO_RESTART'
        assert time.time()<1793039120,'HARD_GOAL_DEADLINE'
        cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('QUALIFICATION_300_SECONDS')))
        signal.alarm(min(300,int(1793039120-time.time())))
        lease.put('START.json',{'pid':os.getpid(),'cpu':cpu,'occupied':occupied,'scope':'exact symbolic algebra only'})
        for p in ROOT.glob('*.py'):
            ast.parse(p.read_text());files[str(p)]=sha(p)
        b=load('general_cubic_wall',ROOT/'wall.py')
        # Load the qualified polynomial ring before runtime binding.
        load('wall_ring_warmup',BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py')
        before=lease.observed()
        for p,d in before.items():assert files.get(p)==d,'UNBOUND_RUNTIME:'+p
        lease.put('BINDING.json',{'files':files,'runtime':before})
        started=time.monotonic();result=b.qualify()
        assert result['pass']
        result.update(classification='GENERAL_RATE_CUBIC_WALL_QUALIFIED',seconds=time.monotonic()-started)
        assert lease.observed()==before,'RUNTIME_CHANGED'
        for p,d in files.items():assert sha(p)==d,'INPUT_CHANGED:'+p
        lease.put('RESULT.json',result)
        lease.put('TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'RESULT.json'),'binding_sha256':sha(ROOT/'BINDING.json')})
        print(json.dumps({'pass':True,'checks':len(result['checks']),'seconds':result['seconds']}),flush=True)
    except BaseException as e:
        lease.put('FAILURE.json',{'classification':'QUALIFICATION_INCONCLUSIVE','error':repr(e),'traceback':traceback.format_exc(),'evidence':getattr(e,'evidence',None)});raise
    finally:
        signal.alarm(0)
        if lease:
            for h in lease.handles:h.close()

