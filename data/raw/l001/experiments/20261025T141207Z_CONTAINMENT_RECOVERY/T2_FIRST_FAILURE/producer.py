import importlib.util
import json
from pathlib import Path
import signal
import sys
import time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
T1=HERE.parent/'T1_RECORDER'
sys.path.insert(0,str(T1))
from recorder import raw,detailed,publish,attempt
spec=importlib.util.spec_from_file_location('qualification',T1/'producer.py')
helpers=importlib.util.module_from_spec(spec); spec.loader.exec_module(helpers)
START=time.monotonic()

def main():
    admitted=json.loads((HERE/'ADMISSION.json').read_text())
    assert all(helpers.digest(HERE/n)==h for n,h in admitted['sources'].items())
    assert json.loads((T1/'RESULT.json').read_text())['classification']=='PASS_RECORDER_QUALIFIED'
    before=helpers.inventory(); p=helpers.load_parent(); runtime=p.runtime()
    publish(HERE/'RUNTIME_START.json',dict(parent=before,runtime=runtime,sources=admitted['sources']))
    publish(HERE/'CONTROLS.json',p.controls())
    y=[p.q(s) for s in ('1','-2','0','0')]; hq=p.fmpq(-1,102400)
    captured=None
    for i in range(1024):
        try: next_y=p.step(y,hq,p.rhs,p.BG_RATES,True)
        except RuntimeError as exc:
            publish(HERE/'FAILURE_IDENTITY.json',dict(step_one_based=i+1,completed_steps=i,
                time_before=str(i*hq),h=str(hq),exception=repr(exc),input=[raw(v) for v in y]))
            assert str(exc)=='TUBE_CONTAINMENT'
            tb=exc.__traceback__; frame=None
            while tb:
                if tb.tb_frame.f_code is p.step.__code__: frame=tb.tb_frame
                tb=tb.tb_next
            assert frame is not None,'ORIGINAL_STEP_FRAME_MISSING'
            state=frame.f_locals
            tube=state['tube']; dt=state['dt']; deriv=state['f']
            publish(HERE/'ORIGINAL_RAW.json',dict(dt=raw(dt),tube=[raw(v) for v in tube],derivatives=[raw(v) for v in deriv]))
            rows=[]
            for j,(v,b,w,r) in enumerate(zip(y,tube,deriv,p.BG_RATES)):
                c=v+dt*w
                row=dict(component=('a','H','Phi','T')[j],index=j,
                    candidate_raw=raw(c),strict_library=bool(b.contains_interior(c)))
                publish(HERE/('COMPONENT_'+str(j)+'_RAW.json'),row)
                for name,x in (('input',v),('tube',b),('derivative',w),('rate',r),('candidate',c)):
                    row[name]=detailed(x)
                def margins():
                    vl,vu=p.bounds(v); bl,bu=p.bounds(b); cl,cu=p.bounds(c)
                    wl,wu=p.bounds(w); rl,ru=p.bounds(r)
                    return dict(lower_inward=str(cl-bl),upper_inward=str(bu-cu),
                        strict_exact=bool(bl<cl and cu<bu),
                        desired_tube_lo=str(vl-abs(hq)*ru),desired_tube_hi=str(vu+abs(hq)*ru),
                        represented_tube_contains_desired=bool(bl<=vl-abs(hq)*ru and vu+abs(hq)*ru<=bu),
                        exact_product_lo=str(vl+min(hq*wl,hq*wu,p.fmpq(0))),
                        exact_product_hi=str(vu+max(hq*wl,hq*wu,p.fmpq(0))))
                row['margins']=attempt(margins)
                if 'value' in row['margins']:
                    assert row['margins']['value']['strict_exact']==row['strict_library']
                publish(HERE/('COMPONENT_'+str(j)+'_DETAIL.json'),row)
                rows.append(row)
            captured=dict(step_one_based=i+1,completed_steps=i,
                failing_components=[r['component'] for r in rows if not r['strict_library']],
                dt=detailed(dt),components=rows,constructor_doc=p.arb.__doc__,
                contains_interior_doc=p.arb.contains_interior.__doc__)
            assert captured['failing_components'],'FAILURE_NOT_REPRODUCED_IN_CAPTURE'
            publish(HERE/'FIRST_FAILURE.json',captured)
            break
        y=next_y
    assert captured is not None,'NO_FAILURE_IN_ORIGINAL_PHASE'
    assert before==helpers.inventory() and runtime==p.runtime()
    assert all(helpers.digest(HERE/n)==h for n,h in admitted['sources'].items())
    publish(HERE/'RESULT.json',dict(classification='PASS_FAILURE_CAPTURE',
        first_failure_step=captured['step_one_based'],failing_components=captured['failing_components'],
        parent_unchanged=True,source_unchanged=True,runtime_unchanged=True,seconds=time.monotonic()-START,
        coordinate_result=False))

if __name__=='__main__':
    def timeout(signum,frame): raise TimeoutError('590 second cap')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(590)
    try: main()
    except BaseException as exc:
        publish(HERE/'FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(exc)))
        raise
    finally: signal.alarm(0)
