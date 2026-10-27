import hashlib
import itertools
import json
import os
from pathlib import Path
from fractions import Fraction as F
import signal
import sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
T4=HERE.parent/'T4_CORRECTED_COORDINATES'

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,data):
    with (HERE/n).open('x') as f:
        json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
def readball(x): return F(x['lo']),F(x['hi'])
def fmt(x,digits=12,upper=False):
    scale=10**digits
    n=x.numerator*scale//x.denominator
    if upper and F(n,scale)<x: n+=1
    sign='-' if n<0 else ''; n=abs(n)
    return sign+str(n//scale)+'.'+str(n%scale).zfill(digits)
def rec(pair):
    lo,hi=pair
    return dict(lo=str(lo),hi=str(hi),width=str(hi-lo),decimal_lo=fmt(lo),decimal_hi=fmt(hi,upper=True))
def bisect(fun,lo,hi):
    assert fun(lo)<0<fun(hi),'ROOT_BRACKET'
    for _ in range(48):
        mid=(lo+hi)/2
        if fun(mid)<0: lo=mid
        elif fun(mid)>0: hi=mid
        else: return mid,mid
    return lo,hi
def S(coeff,x,y):
    a,b,c,d=coeff
    return 2*c+d*x+a*y+b*x*y/2

def main():
    admission=json.loads((HERE/'ADMISSION.json').read_text())
    assert all(digest(HERE/n)==h for n,h in admission['sources'].items())
    runtime=Path(sys.executable).resolve()
    rh=digest(runtime)
    assert sys.version_info[:3]==(3,12,3) and rh=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    result=json.loads((T4/'RESULT.json').read_text())
    assert result['classification']=='PASS_IMPLEMENTATION_CORRECTED_TRANSITION_COORDINATES'
    level=json.loads((T4/'LEVEL_2048.json').read_text())
    boxes=[readball(v) for v in level['upper_state'][4:]]
    (al,ah),(bl,bh),(cl,ch),(dl,dh)=boxes
    assert al>0 and bl>0 and ch<0 and dl>0
    low=[x[0] for x in boxes]; high=[x[1] for x in boxes]
    assert bisect(lambda x:x-F(1,4),F(0),F(1))==(F(1,4),F(1,4))
    assert bisect(lambda x:x*x-F(1,4),F(0),F(1))==(F(1,2),F(1,2))
    try: bisect(lambda x:x+1,F(0),F(1))
    except AssertionError as exc: assert str(exc)=='ROOT_BRACKET'
    else: raise AssertionError('INVALID_BRACKET_NOT_REJECTED')
    for x,y in ((F(0),F(0)),(F(1,50),F(1,40)),(F(1,10),F(1,5))):
        values=[S(v,x,y) for v in itertools.product(*boxes)]
        assert min(values)==S(low,x,y) and max(values)==S(high,x,y)
    lower=(-2*ch/dh,-2*cl/dl); upper=(-2*ch/ah,-2*cl/al)
    eqlo=bisect(lambda x:S(high,x,x),F(0),F(1,10))
    eqhi=bisect(lambda x:S(low,x,x),F(0),F(1,10))
    equal=(eqlo[0],eqhi[1])
    for name,interval in (('lower_only',lower),('upper_only',upper),('equal_each',equal)):
        ref=readball(result['thresholds'][name])
        assert interval[0]>0 and interval[1]-interval[0]<=F(1,10000)
        assert max(ref[0],interval[0])<=min(ref[1],interval[1])
    detlow=al*dl-bl*ch
    denomhigh=ah+bh*lower[1]/2
    slope_margin=detlow-denomhigh*denomhigh
    assert slope_margin>0,'GLOBAL_SLOPE_NOT_CERTIFIED'
    K=F(19,500)
    all_upper=(S(low,F(0),K),S(high,F(0),K))
    all_lower=(S(low,K,F(0)),S(high,K,F(0)))
    derivative_lower=dl-ah-bh*K/2
    assert all_upper[1]<0<all_lower[0] and derivative_lower>0
    mixlo=bisect(lambda x:S(high,x,K-x),F(0),K)
    mixhi=bisect(lambda x:S(low,x,K-x),F(0),K)
    mixed=(mixlo[0],mixhi[1])
    assert mixed[1]-mixed[0]<=F(1,10000)
    assert all(digest(HERE/n)==h for n,h in admission['sources'].items()) and digest(runtime)==rh
    save('RESULT.json',dict(classification='PASS_WALL_ALLOCATION_CERTIFICATE',
        thresholds={'lower_only':rec(lower),'upper_only':rec(upper),'equal_each':rec(equal)},
        phase_envelope_coefficients={'lower':[str(v) for v in low],'upper':[str(v) for v in high]},
        det_lower=str(detlow),slope_denominator_upper=str(denomhigh),
        global_slope_margin=str(slope_margin),global_slope_less_than_minus_one=True,
        every_allocation_two_modes_if_total_less_than=str(lower[0]),
        every_allocation_one_mode_if_total_greater_than=str(upper[1]),
        fixed_total=str(K),fixed_total_lower_wall_threshold=rec(mixed),
        fixed_total_all_upper_S=rec(all_upper),fixed_total_all_lower_S=rec(all_lower),
        fixed_total_monotonicity_margin=str(derivative_lower),controls_passed=True,
        inputs_sources_runtime_unchanged=True,remaining_negative_mode=True))

if __name__=='__main__':
    def timeout(signum,frame): raise TimeoutError('590second cap')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(590)
    try: main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(exc)))
        raise
    finally: signal.alarm(0)
