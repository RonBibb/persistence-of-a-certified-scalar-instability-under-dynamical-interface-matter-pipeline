import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import sys
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from recorder import raw,detailed,publish
ROOT=HERE.parent.parent
PARENT=ROOT/'20261025T115424Z_TRANSITION_COORDINATES'
PREVIOUS=ROOT/'20261025T124003Z_CONTAINMENT_DIAGNOSTIC'
START=time.monotonic()

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def inventory():
    return {str(p.relative_to(ROOT)):digest(p) for folder in (PARENT,PREVIOUS) for p in sorted(folder.iterdir()) if p.is_file()}
def load_parent():
    assert digest(PARENT/'producer.py')=='adc749e5ddbb448d55d70d8e004f41c47f5ec372197553d71b00fba0b0a1d93f'
    spec=importlib.util.spec_from_file_location('original',PARENT/'producer.py')
    p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
    expected={'/usr/bin/python3.12':'c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960',
        '/home/parallels/research-runs/cap-interval-arb-2026-09-12/flint/types/arb.abi3.so':'6abaed2e09f6b60e4b26d9c6eb71345ae5e69fc9162fc42e5ff232ef8be75145'}
    assert p.runtime()['hashes']==expected and sys.version_info[:3]==(3,12,3)
    assert p.flint.__version__=='0.9.0' and p.ctx.prec==256 and p.ctx.threads==1
    return p

def main():
    before=inventory(); p=load_parent(); runtime=p.runtime()
    source={n:digest(HERE/n) for n in ('PLAN.md','producer.py','lease_run.py','recorder.py')}
    publish(HERE/'RUNTIME_START.json',dict(parent=before,runtime=runtime,source=source))
    class Broken:
        def __repr__(self): return 'IntentionalEndpointConversionFailure'
        def lower(self): return self
        def upper(self): return self
        def fmpq(self): raise ValueError('intentional recorder control')
    cases=[('exact',p.arb(1),True),('ball',p.arb(0,1),True),
           ('nan',p.arb('nan'),False),('infinity',p.arb('inf'),False),('broken',Broken(),False)]
    results=[]
    for name,x,finite in cases:
        path=HERE/(name+'_RAW.json')
        publish(path,dict(case=name,raw=raw(x)))
        entry=detailed(x)
        if finite:
            assert 'value' in entry['lo'] and 'value' in entry['hi']
            assert p.fmpq(entry['lo']['value'])<=p.fmpq(entry['hi']['value'])
        else:
            assert 'error' in entry['lo'] and 'error' in entry['hi']
        publish(HERE/(name+'_DETAIL.json'),entry)
        assert json.loads(path.read_text())['case']==name
        try: publish(path,{'overwrite':'forbidden'})
        except FileExistsError: pass
        else: raise AssertionError('overwrite not refused')
        assert json.loads(path.read_text())['case']==name
        results.append(dict(case=name,pass_control=True))
    observations=[]
    for denom in (128,100,102400):
        h=p.fmpq(-1,denom)
        x=p.interval(h,p.fmpq(0))
        observations.append(dict(h=str(h),interval=detailed(x)))
    publish(HERE/'CONSTRUCTOR_OBSERVATIONS.json',observations)
    assert inventory()==before and runtime==p.runtime()
    assert source=={n:digest(HERE/n) for n in source}
    publish(HERE/'RESULT.json',dict(classification='PASS_RECORDER_QUALIFIED',controls=results,
        parent_unchanged=True,source_unchanged=True,runtime_unchanged=True,seconds=time.monotonic()-START))

if __name__=='__main__':
    def timeout(signum,frame): raise TimeoutError('590 second cap')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(590)
    try: main()
    except BaseException as exc:
        publish(HERE/'FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(exc)))
        raise
    finally: signal.alarm(0)
