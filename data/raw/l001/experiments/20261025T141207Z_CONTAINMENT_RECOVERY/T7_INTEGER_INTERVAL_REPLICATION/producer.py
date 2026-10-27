import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import signal
import sys
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,S,box,power
CONTEXT={}
RATES=[I(x) for x in (3,5,F(1,10),2,F(1,10),2,2,12)]
LIMITS=[(F(9,10),F(11,10)),(F(-21,10),F(-19,10)),(F(-1,100),F(1,100)),(F(-1,50),F(1,50))]

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,data):
    with (HERE/n).open('x') as f:
        json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
def rhs(y):
    a,H,P,T=y[:4]
    tp=1-P+4*power(P,3)-4*H*T
    out=[H*a,-T*T/3-3/(a*a),T,tp]
    if len(y)==8:
        p,b,c,d=y[4:]
        A=a*a*T*tp/18; E=1-a*a*T*T/18
        C=-1+12*P*P+4*T*T/3+a*a*tp*tp/18; D=-4*H-A
        out += [A*p+E*c,A*b+E*d,C*p+D*c,C*b+D*d]
    return out
def ham(y):
    a,H,P,T=y[:4]
    return H*H-1-T*T/12+(P-P*P/2+power(P,4))/6-3/(a*a)
def step(y,hq,fun,rates,bg=False):
    h=I(hq); dt=box(min(F(0),hq),max(F(0),hq))
    radii=[(I(abs(hq))*r).hi for r in rates]
    tube=[v+I(-r,r) for v,r in zip(y,radii)]
    assert len(tube)==len(y)
    if bg: assert all(x.in_exact(*lim) for x,lim in zip(tube[:4],LIMITS)),'BACKGROUND_TUBE'
    f=fun(tube)
    assert len(f)==len(y)
    assert all(b.strict(v+dt*w) for b,v,w in zip(tube,y,f)),'TUBE_CONTAINMENT'
    return [v+h*w for v,w in zip(y,f)]
def bracket(fun):
    lo=F(0); hi=F(1,10)
    assert fun(lo)<0<fun(hi),'ROOT_BRACKET'
    for _ in range(48):
        mid=(lo+hi)/2
        if fun(mid)<0: lo=mid
        elif fun(mid)>0: hi=mid
        else: return mid,mid
    return lo,hi
def rec(bounds):
    a,b=bounds; return dict(lo=str(a),hi=str(b),width=str(b-a))
def controls():
    q=I(F(1,3)); assert q.bounds()[0]<=F(1,3)<=q.bounds()[1]
    assert I(2).bounds()==(F(2),F(2))
    boxes=[box(F(1,3),F(2,3)),box(F(-3,2),F(-1,4)),box(F(-1,7),F(2,9))]
    count=0
    for x,y in itertools.product(boxes,repeat=2):
        xl,xh=x.bounds(); yl,yh=y.bounds()
        for op,truth in ((lambda:x+y,[a+b for a in (xl,xh) for b in (yl,yh)]),
                         (lambda:x-y,[a-b for a in (xl,xh) for b in (yl,yh)]),
                         (lambda:x*y,[a*b for a in (xl,xh) for b in (yl,yh)])):
            lo,hi=op().bounds(); assert lo<=min(truth) and max(truth)<=hi; count+=1
        if not yl<=0<=yh:
            truth=[a/b for a in (xl,xh) for b in (yl,yh)]
            lo,hi=(x/y).bounds(); assert lo<=min(truth) and max(truth)<=hi; count+=1
    try: I(1)/box(-1,1)
    except AssertionError as exc: assert str(exc)=='ZERO_DIVISOR'
    else: raise AssertionError('ZERO_DIVISOR_ACCEPTED')
    for sign in (-1,1):
        h=F(sign,100)
        assert step([I(1)],h,lambda y:[I(1)],[I(2)])[0].contains(I(1+h))
        poly=sum((h**j/F(math.factorial(j)) for j in range(13)),F(0))
        rem=2*abs(h)**13/F(math.factorial(13))
        assert step([I(1)],h,lambda y:y,[I(2)])[0].contains(box(poly-rem,poly+rem))
    try: step([I(1)],F(1,100),lambda y:[I(1)],[I(0)])
    except AssertionError as exc: assert str(exc)=='TUBE_CONTAINMENT'
    else: raise AssertionError('SMALL_TUBE_ACCEPTED')
    seed=[I(x) for x in (1,-2,0,0,1,0,0,1)]
    expected=[I(x) for x in (-2,-3,0,1,0,1,F(-17,18),8)]
    assert all(x.contains(v) for x,v in zip(rhs(seed),expected))
    return dict(arithmetic_corner_controls=count,rational_rounding=True,zero_divisor_rejected=True,
                signed_constant_exponential=True,undersized_rejected=True,seed=True)
def level(n):
    y=[I(x) for x in (1,-2,0,0)]; h=F(1,100*n)
    for i in range(n):
        CONTEXT.update(n=n,phase='backward',step_one_based=i+1)
        y=step(y,-h,rhs,RATES[:4],True)
    assert ham(y).contains(0),'LOWER_HAMILTONIAN'
    lower=y[:]; y += [I(x) for x in (1,0,0,1)]
    for i in range(2*n):
        CONTEXT.update(n=n,phase='forward',step_one_based=i+1)
        y=step(y,h,rhs,RATES,True)
    assert ham(y).contains(0),'UPPER_HAMILTONIAN'
    p,b,c,d=y[4:]
    limits=[(F(249489,250000),F(250511,250000)),(F(4949,250000),F(6501,250000)),
            (F(-1,25),F(-81,5000)),(F(569,500),F(309,250))]
    assert all(x.in_exact(*lim) for x,lim in zip(y[4:],limits)),'ANALYTICAL_M'
    det=p*d-b*c; defect=det-power(lower[0]/y[0],4)
    assert det.lo>0 and defect.contains(0),'DETERMINANT'
    boxes=[x.bounds() for x in y[4:]]
    low=[v[0] for v in boxes]; high=[v[1] for v in boxes]
    def eq(coeff,k):
        a,b,c,d=coeff; return 2*c+(a+d)*k+b*k*k/2
    el=bracket(lambda k:eq(high,k)); eh=bracket(lambda k:eq(low,k))
    values={'lower_only':(-2*c/d).bounds(),'upper_only':(-2*c/p).bounds(),'equal_each':(el[0],eh[1])}
    assert all(lo>0 and hi-lo<=F(1,10000) for lo,hi in values.values()),'WIDTH'
    save('LEVEL_'+str(n)+'.json',dict(n=n,steps=3*n,lower_background=[x.record() for x in lower],
        upper_state=[x.record() for x in y],thresholds={k:rec(v) for k,v in values.items()},
        lower_hamiltonian=ham(lower).record(),upper_hamiltonian=ham(y).record(),
        determinant_defect=defect.record(),all_tubes_and_gates_passed=True))
    return y[4:],values
def main():
    admission=json.loads((HERE/'ADMISSION.json').read_text())
    assert all(digest(HERE/n)==h for n,h in admission['sources'].items())
    exe=Path(sys.executable).resolve(); rh=digest(exe)
    assert sys.version_info[:3]==(3,12,3) and rh=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    save('CONTROLS.json',controls())
    cm,cv=level(1024); fm,fv=level(2048)
    reference=json.loads((HERE.parent/'T4_CORRECTED_COORDINATES'/'LEVEL_2048.json').read_text())
    for k,(lo,hi) in fv.items():
        a,b=cv[k]; assert max(lo,a)<=min(hi,b) and hi-lo<=b-a,'LEVEL_COMPARISON'
        ref=reference['thresholds'][k]
        assert max(lo,F(ref['lo']))<=min(hi,F(ref['hi'])),'ARITHMETIC_DISJOINT'
    for x,ref in zip(fm,reference['upper_state'][4:]):
        lo,hi=x.bounds(); assert max(lo,F(ref['lo']))<=min(hi,F(ref['hi'])),'TRANSFER_DISJOINT'
    assert all(digest(HERE/n)==h for n,h in admission['sources'].items()) and digest(exe)==rh
    save('RESULT.json',dict(classification='PASS_INTEGER_INTERVAL_REPLICATION',
        thresholds={k:rec(v) for k,v in fv.items()},independent_arithmetic=True,
        fractional_bits=256,all_gates_passed=True,source_inputs_runtime_unchanged=True))
if __name__=='__main__':
    def timeout(signum,frame): raise TimeoutError('590second cap')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(590)
    try: main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CONTEXT,error=repr(exc)))
        raise
    finally: signal.alarm(0)
