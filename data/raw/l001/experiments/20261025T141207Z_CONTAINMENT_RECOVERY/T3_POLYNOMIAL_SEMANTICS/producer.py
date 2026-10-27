import importlib.util
import json
from pathlib import Path
import signal
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
T1=HERE.parent/'T1_RECORDER'; T2=HERE.parent/'T2_FIRST_FAILURE'
sys.path.insert(0,str(T1))
from recorder import raw,detailed,publish
spec=importlib.util.spec_from_file_location('qualification',T1/'producer.py')
helpers=importlib.util.module_from_spec(spec); spec.loader.exec_module(helpers)

def ipow(x,n):
    assert n in (2,3,4)
    result=x
    for _ in range(n-1): result=result*x
    return result

def main():
    admitted=json.loads((HERE/'ADMISSION.json').read_text())
    assert all(helpers.digest(HERE/n)==h for n,h in admitted['sources'].items())
    before=helpers.inventory(); p=helpers.load_parent(); runtime=p.runtime()
    publish(HERE/'RUNTIME_START.json',dict(parent=before,runtime=runtime,sources=admitted['sources']))
    seed=[p.q(s) for s in ('1','-2','0','0')]; hq=p.fmpq(-1,102400); h=p.arb(hq)
    tube=[v+p.arb(0,(abs(h)*r).upper()) for v,r in zip(seed,p.BG_RATES)]
    original=json.loads((T2/'ORIGINAL_RAW.json').read_text())
    assert [raw(v) for v in tube]==original['tube']
    a,H,P,T=tube
    cases=[('minus_one',p.arb(-1)),('zero',p.arb(0)),('plus_one',p.arb(1)),
           ('crossing_one',p.arb(0,1)),('actual_phi',P),
           ('positive',p.arb(1,p.q('1/4'))),('negative',p.arb(-1,p.q('1/4')))]
    controls=[]
    for name,x in cases:
        lo,hi=p.bounds(x)
        for n in (2,3,4):
            wanted_lo=min(lo**n,hi**n); wanted_hi=max(lo**n,hi**n)
            if n%2==0 and lo<=0<=hi: wanted_lo=p.fmpq(0)
            poly=ipow(x,n); ol=x**n
            pl,pu=p.bounds(poly)
            assert poly.is_finite() and pl<=wanted_lo and wanted_hi<=pu
            if ol.is_finite():
                ll,uu=p.bounds(ol); assert ll<=wanted_lo and wanted_hi<=uu
            controls.append(dict(case=name,power=n,input=detailed(x),original=detailed(ol),
                multiplication=detailed(poly),exact_range_lo=str(wanted_lo),exact_range_hi=str(wanted_hi)))
    publish(HERE/'POLYNOMIAL_CONTROLS.json',controls)
    original_cube=P**3; multiplied_cube=ipow(P,3)
    summands=[1-P,4*original_cube,-4*H*T]
    old=p.rhs(tube)[3]
    new=1-P+4*multiplied_cube-4*H*T
    dt=p.interval(hq,p.fmpq(0)); candidate=seed[3]+dt*new
    publish(HERE/'EXPRESSION_DIAGNOSIS.json',dict(original_cube=detailed(original_cube),
        multiplied_cube=detailed(multiplied_cube),summands=[detailed(v) for v in summands],
        original_Tprime=detailed(old),corrected_Tprime=detailed(new),
        corrected_candidate=detailed(candidate),original_tube=detailed(tube[3]),
        candidate_strict_in_original_tube=bool(tube[3].contains_interior(candidate)),
        power_doc=p.arb.__pow__.__doc__))
    assert summands[0].is_finite() and not summands[1].is_finite() and summands[2].is_finite()
    assert not old.is_finite() and new.is_finite() and tube[3].contains_interior(candidate)
    seed_tp=1-seed[2]+4*ipow(seed[2],3)-4*seed[1]*seed[3]
    assert seed_tp.contains(p.rhs(seed)[3]) and seed_tp.is_exact()
    assert before==helpers.inventory() and runtime==p.runtime()
    assert all(helpers.digest(HERE/n)==h for n,h in admitted['sources'].items())
    publish(HERE/'RESULT.json',dict(classification='PASS_POLYNOMIAL_EVALUATION_QUALIFIED',
        controls_passed=len(controls),failed_original_power_cases=[{'case':r['case'],'power':r['power']} for r in controls if not r['original']['finite']['value']],
        cause='original cube evaluation nonfinite on captured zero-crossing Phi ball',
        corrected_candidate_inside_unchanged_tube=True,coordinate_result=False,
        parent_unchanged=True,source_unchanged=True,runtime_unchanged=True))

if __name__=='__main__':
    def timeout(signum,frame): raise TimeoutError('590 second cap')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(590)
    try: main()
    except BaseException as exc:
        publish(HERE/'FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(exc)))
        raise
    finally: signal.alarm(0)
