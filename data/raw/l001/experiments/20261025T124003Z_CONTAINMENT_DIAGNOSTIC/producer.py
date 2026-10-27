"""One diagnostic replay; original numerical method is never repaired here."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PARENT = HERE.parent/'20261025T115424Z_TRANSITION_COORDINATES'
START = time.monotonic()

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def inventory():
    return {p.name:digest(p) for p in sorted(PARENT.iterdir()) if p.is_file()}

def save(name,data):
    with (HERE/name).open('x') as f:
        json.dump(data,f,indent=2)
        f.flush()
        os.fsync(f.fileno())

def main():
    before = inventory()
    assert before['producer.py']=='adc749e5ddbb448d55d70d8e004f41c47f5ec372197553d71b00fba0b0a1d93f'
    spec=importlib.util.spec_from_file_location('frozen_parent',PARENT/'producer.py')
    p=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(p)
    runtime=p.runtime()
    expected={
        '/usr/bin/python3.12':'c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960',
        '/home/parallels/research-runs/cap-interval-arb-2026-09-12/flint/types/arb.abi3.so':'6abaed2e09f6b60e4b26d9c6eb71345ae5e69fc9162fc42e5ff232ef8be75145'}
    assert runtime['hashes']==expected and sys.version_info[:3]==(3,12,3)
    assert p.flint.__version__=='0.9.0' and p.ctx.prec==256 and p.ctx.threads==1
    sources={n:digest(HERE/n) for n in ('producer.py','lease_run.py','PLAN.md')}
    save('RUNTIME_START.json',dict(runtime=runtime,parent=before,sources=sources))
    controls=p.controls()
    semantic=[]
    for lo,hi,expected_strict in ((-1,1,True),(-2,2,False),(-3,1,False)):
        outer=p.arb(0,2)
        inner=p.interval(p.fmpq(lo),p.fmpq(hi))
        a,b=p.bounds(outer); c,d=p.bounds(inner)
        strict=bool(outer.contains_interior(inner))
        exact=(a<c and d<b)
        assert strict==exact==expected_strict
        semantic.append(dict(lo=lo,hi=hi,strict=strict,exact=exact))
    save('CONTROLS.json',dict(inherited=controls,semantics=semantic))
    y=[p.q(s) for s in ('1','-2','0','0')]
    hq=p.fmpq(-1,102400)
    failure=None
    for i in range(1024):
        try:
            next_y=p.step(y,hq,p.rhs,p.BG_RATES,True)
        except RuntimeError as exc:
            if str(exc)!='TUBE_CONTAINMENT': raise
            h=p.arb(hq)
            dt=p.interval(hq,p.fmpq(0))
            tube=[v+p.arb(0,(abs(h)*r).upper()) for v,r in zip(y,p.BG_RATES)]
            deriv=p.rhs(tube)
            rows=[]
            for j,(v,r,b,w) in enumerate(zip(y,p.BG_RATES,tube,deriv)):
                candidate=v+dt*w
                vl,vu=p.bounds(v); bl,bu=p.bounds(b); cl,cu=p.bounds(candidate)
                wl,wu=p.bounds(w); rl,ru=p.bounds(r)
                desired_radius=abs(hq)*ru
                products=[hq*wl,hq*wu,p.fmpq(0)]
                ideal_lo=vl+min(products); ideal_hi=vu+max(products)
                rows.append(dict(index=j,component=('a','H','Phi','T')[j],
                    input=p.record(v),rate=p.record(r),derivative=p.record(w),
                    tube=p.record(b),candidate=p.record(candidate),
                    lower_inward_margin=str(cl-bl),upper_inward_margin=str(bu-cu),
                    strict_library=bool(b.contains_interior(candidate)),
                    strict_exact_endpoints=bool(bl<cl and cu<bu),
                    desired_tube_lo=str(vl-desired_radius),desired_tube_hi=str(vu+desired_radius),
                    tube_contains_desired=bool(bl<=vl-desired_radius and vu+desired_radius<=bu),
                    exact_product_candidate_lo=str(ideal_lo),exact_product_candidate_hi=str(ideal_hi),
                    exact_product_strict_in_tube=bool(bl<ideal_lo and ideal_hi<bu)))
            failure=dict(step_one_based=i+1,completed_steps=i,time_before=str(i*hq),h=str(hq),
                         dt=p.record(dt),components=rows,
                         failing_components=[r['component'] for r in rows if not r['strict_library']],
                         constructor_doc=p.arb.__doc__,contains_interior_doc=p.arb.contains_interior.__doc__)
            save('FIRST_FAILURE.json',failure)
            break
        y=next_y
    assert failure is not None,'FAILURE_NOT_REPRODUCED_WITHIN_FROZEN_BACKWARD_PHASE'
    assert before==inventory(),'PARENT_CHANGED'
    assert sources=={n:digest(HERE/n) for n in sources},'SOURCE_CHANGED'
    assert runtime==p.runtime(),'RUNTIME_CHANGED'
    save('RESULT.json',dict(classification='PASS_DIAGNOSTIC_REPRODUCTION',
        first_failure_step=failure['step_one_based'],failing_components=failure['failing_components'],
        parent_unchanged=True,source_unchanged=True,runtime_unchanged=True,
        coordinate_result=False,seconds=time.monotonic()-START))

if __name__=='__main__':
    def timeout(signum,frame):
        raise TimeoutError('independent child 590-second wall cap')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(590)
    try:
        main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(exc),seconds=time.monotonic()-START))
        raise
    finally:
        signal.alarm(0)
