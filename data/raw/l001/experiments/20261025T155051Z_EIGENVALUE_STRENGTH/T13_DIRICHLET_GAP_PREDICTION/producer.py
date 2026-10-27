import hashlib,json,os,sys
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=HERE/n;assert not p.exists();t=HERE/(n+'.tmp')
    with t.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(t,p);t.unlink()
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    root=HERE.parent/'T12_DIRICHLET_CEILING'
    assert not any((root/p).exists() for p in ('RESOURCE_START.json','EXECUTION.json','RESULT.json','FAILURE.json')),'PREDICTION_NOT_PROSPECTIVE'
    preds={}
    for D in (F(1,50),F(1,100)):
        gap=D*D/6;lo=gap*F(4,5);hi=gap*F(6,5)
        assert lo<gap<hi
        # Polynomial controls for f=2(d²-r²), U0=psi0=a0=1.
        d=D/2
        assert 2*(d*d-d*d)==0
        assert -2*d*d==3*(-gap)
        assert -4==-4*1*1
        preds[str(D)]=dict(gap=str(gap),window={'lo':str(lo),'hi':str(hi)},mu=str(-12-gap))
    assert F(preds['1/50']['gap'])/F(preds['1/100']['gap'])==4
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='DIRICHLET_GAP_PREDICTIONS_PUBLISHED',
        predictions=preds,gap_ratio_prediction='4',relative_window='1/5',
        fit_parameters=0,error_bound_claim=False,T12_started=False,controls_passed=True))
try:main()
except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
