import hashlib,json,math,os,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,S,box
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=HERE/n;assert not p.exists();tmp=HERE/(n+'.tmp')
    with tmp.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,p);tmp.unlink()
def sqrtbox(x):
    assert x.lo>=0
    lo=math.isqrt(x.lo*S);hi=math.isqrt(x.hi*S)
    if hi*hi<x.hi*S:hi+=1
    return I(lo,hi)
def absbox(x):
    if x.lo>=0:return x
    if x.hi<=0:return -x
    return I(0,max(-x.lo,x.hi))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    cases={};comparisons={}
    for k in (F(0),F(9,1000),F(9,500)):
        w=k/F(1,50);disc=(11+w)*(11+w)+F(8,3)
        assert disc==(13-w)*(13-w)-4*(12*(1-w)-F(2,3))
        root=sqrtbox(I(disc));extra=(-(13-w)+root)/2;persistent=(-(13-w)-root)/2
        assert (extra+persistent).contains(-(13-w))
        assert (extra*persistent).contains(12*(1-w)-F(2,3))
        for m in (extra,persistent):assert ((m+1-w)*(m+12)-F(2,3)).contains(0)
        assert F(-12+1-w)*0-F(2,3)==-F(2,3)
        assert extra.lo>-12*S and persistent.hi<-12*S
        cases[str(k)]=dict(extra=extra.record(),persistent=persistent.record(),
            extra_prediction_window=(extra+box(F(-1,500),F(1,500))).record(),
            persistent_prediction_window=(persistent+box(F(-1,500),F(1,500))).record())
        parent={F(0):'T1R2_SOFT_MODE',F(9,500):'T2_STIFF_MODE'}.get(k)
        if parent:
            r=json.loads((HERE.parent/parent/'RESULT.json').read_text())['physical_mu_bracket']
            actual=box(F(r['lo']),F(r['hi']));err=extra-actual;abserr=absbox(err)
            comparisons[str(k)]=dict(signed_error=err.record(),absolute_error=abserr.record(),
                relative_absolute_error=(abserr/absbox(actual)).record(),retrospective=True)
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='LEADING_MODEL_PREDICTIONS_PUBLISHED',cases=cases,
        known_case_comparisons=comparisons,held_out_equal_hessian='9/1000',
        fitted_parameters=0,rigorous_asymptotic_remainder_bound=False,controls_passed=True))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
