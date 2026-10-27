import importlib.util
import json
from pathlib import Path
import signal
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
T4=HERE.parent/'T4_CORRECTED_COORDINATES'
spec=importlib.util.spec_from_file_location('corrected',T4/'producer.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)
from recorder import publish,raw
CONTEXT={}

def det(m):
    a,b,c,d=m
    return a*d-b*c
def inv(m):
    determinant=det(m)
    assert determinant.is_finite() and not determinant.contains(0),'SINGULAR_MATRIX'
    a,b,c,d=m
    return [d/determinant,-b/determinant,-c/determinant,a/determinant]
def mul(m,n):
    a,b,c,d=m; e,f,g,h=n
    return [a*e+b*g,a*f+b*h,c*e+d*g,c*f+d*h]
def overlap(x,y):
    lo,hi=p.bounds(x)
    return max(lo,p.fmpq(y['lo']))<=min(hi,p.fmpq(y['hi']))

def branch(n,sign):
    y=[p.q(s) for s in ('1','-2','0','0','1','0','0','1')]
    h=p.fmpq(sign,100*n)
    for i in range(n):
        CONTEXT.update(n=n,sign=sign,step_one_based=i+1)
        y=p.step(y,h,p.rhs,p.RATES,True)
    assert p.ham(y).contains(0),'HAMILTONIAN'
    defect=det(y[4:])-p.ipow(1/y[0],4)
    assert det(y[4:]).lower()>0 and defect.contains(0),'DIRECTIONAL_DETERMINANT'
    return y,defect

def level(n):
    lower,ld=branch(n,-1); upper,ud=branch(n,1)
    m=mul(upper[4:],inv(lower[4:])); a,b,c,d=m
    limits=[(p.fmpq(249489,250000),p.fmpq(250511,250000)),
            (p.fmpq(4949,250000),p.fmpq(6501,250000)),
            (p.fmpq(-1,25),p.fmpq(-81,5000)),(p.fmpq(569,500),p.fmpq(309,250))]
    assert all(p.inside_exact(x,l) for x,l in zip(m,limits)),'ANALYTICAL_M'
    defect=det(m)-p.ipow(lower[0]/upper[0],4)
    assert det(m).lower()>0 and defect.contains(0),'COMPOSED_DETERMINANT'
    values={'lower_only':-2*c/d,'upper_only':-2*c/a,
            'equal_each':-4*c/(a+d+(p.ipow(a+d,2)-4*b*c).sqrt())}
    for x in values.values():
        lo,hi=p.bounds(x); assert lo>0 and hi-lo<=p.fmpq(1,10000),'WIDTH'
    publish(HERE/('LEVEL_'+str(n)+'.json'),dict(n=n,steps=2*n,
        lower_state=[p.record(x) for x in lower],upper_state=[p.record(x) for x in upper],
        transfer=[p.record(x) for x in m],thresholds={k:p.record(x) for k,x in values.items()},
        lower_hamiltonian=p.record(p.ham(lower)),upper_hamiltonian=p.record(p.ham(upper)),
        lower_det_defect=p.record(ld),upper_det_defect=p.record(ud),composed_det_defect=p.record(defect),
        all_tubes_and_level_gates_passed=True))
    return m,values

def main():
    admission=json.loads((HERE/'ADMISSION.json').read_text())
    assert all(p.helpers.digest(HERE/n)==h for n,h in admission['sources'].items())
    before=p.helpers.inventory(); p.helpers.load_parent(); runtime=p.runtime()
    publish(HERE/'RUNTIME_START.json',dict(parent=before,runtime=runtime,sources=admission['sources']))
    controls=p.controls()
    A=[p.q(s) for s in ('1','1','0','1')]; B=[p.q(s) for s in ('2','1','1','1')]
    wanted=[p.q(s) for s in ('2','-1','1','0')]
    assert all(x.is_exact() and x.contains(y) for x,y in zip(mul(B,inv(A)),wanted))
    identity=[p.q(s) for s in ('1','0','0','1')]
    assert all(x.is_exact() and x.contains(y) for x,y in zip(inv(identity),identity))
    try: inv([p.q('1')]*4)
    except AssertionError as exc: assert str(exc)=='SINGULAR_MATRIX'
    else: raise AssertionError('SINGULAR_ACCEPTED')
    publish(HERE/'CONTROLS.json',dict(inherited=controls,composition=True,identity=True,singular_rejected=True))
    cm,cv=level(1024); fm,fv=level(2048)
    reference=json.loads((T4/'LEVEL_2048.json').read_text())
    for k,x in fv.items():
        lo,hi=p.bounds(x); cl,ch=p.bounds(cv[k])
        assert max(lo,cl)<=min(hi,ch) and hi-lo<=ch-cl,'LEVEL_COMPARISON'
        assert overlap(x,reference['thresholds'][k]),'T4_THRESHOLD_DISJOINT'
    assert all(overlap(x,y) for x,y in zip(fm,reference['upper_state'][4:])),'T4_TRANSFER_DISJOINT'
    assert before==p.helpers.inventory() and runtime==p.runtime()
    assert all(p.helpers.digest(HERE/n)==h for n,h in admission['sources'].items())
    publish(HERE/'RESULT.json',dict(classification='PASS_SPLIT_TRANSFER_CERTIFICATE',
        thresholds={k:p.record(x) for k,x in fv.items()},transfer=[p.record(x) for x in fm],
        independent_propagation_route=True,independent_arithmetic_library=False,
        all_gates_passed=True,parent_source_runtime_unchanged=True))

if __name__=='__main__':
    def timeout(signum,frame): raise TimeoutError('590second cap')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(590)
    try: main()
    except BaseException as exc:
        publish(HERE/'FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CONTEXT,error=repr(exc)))
        raise
    finally: signal.alarm(0)
