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
def win(x):
    y=x+box(F(-1,1000),F(1,1000));return I(max(0,y.lo),min(S,y.hi))
def getbox(v):return box(F(v['lo']),F(v['hi']))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    roots=json.loads((HERE.parent/'T5_LEADING_MODEL/RESULT.json').read_text())['cases']
    old=json.loads((HERE.parent/'T3_MODE_PARTICIPATION/RESULT.json').read_text())['results']
    D=I(F(1,50));g2=I(F(2,3));g=sqrtbox(g2);preds={};retro={}
    for k,rr in roots.items():
        w=F(k)/F(1,50);preds[k]={}
        for branch in ('extra','persistent'):
            mu=getbox(rr[branch]);lam=mu+12;chi=-g/lam
            assert ((-1+w)-g*chi-mu).contains(0),'MATRIX_SCALAR'
            assert (-g-12*chi-mu*chi).contains(0),'MATRIX_METRIC'
            scalar=lam*lam/(lam*lam+g2);metric=g2/(lam*lam+g2)
            assert (scalar+metric).contains(1) and scalar.lo>0 and metric.lo>0
            sep=(2*D/(3*lam))/sqrtbox(2*D*(1+g2/(lam*lam)))
            assert (sep*sep-D*metric/3).contains(0),'SEPARATION_IDENTITY'
            preds[k][branch]=dict(scalar_norm_share=scalar.record(),metric_norm_share=metric.record(),
                scalar_prediction_window=win(scalar).record(),metric_prediction_window=win(metric).record(),
                equal_wall_response=(scalar/D).record(),canonical_separation=sep.record())
            if branch=='extra' and k in ('0','9/500'):
                parent='T1R2_SOFT_MODE' if k=='0' else 'T2_STIFF_MODE'
                retro[k]=dict(scalar_signed_difference=(scalar-getbox(old[parent]['scalar_norm_share'])).record(),
                    metric_signed_difference=(metric-getbox(old[parent]['metric_norm_share'])).record(),retrospective=True)
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='TWO_COMPONENT_PREDICTIONS_PUBLISHED',predictions=preds,
        extra_retrospective_comparisons=retro,fit_parameters=0,persistent_profile_test_started=False,
        exact_effective_action_claim=False,controls_passed=True))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
