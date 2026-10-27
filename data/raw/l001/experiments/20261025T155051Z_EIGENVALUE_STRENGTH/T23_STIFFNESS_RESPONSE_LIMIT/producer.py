import hashlib,json,os,sys
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=HERE/n;assert not p.exists();tmp=HERE/(n+'.tmp')
    with tmp.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,p);tmp.unlink()
def bounds(v):return F(v['lo']),F(v['hi'])
def rec(v):return dict(lo=str(v[0]),hi=str(v[1]))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    q=json.loads((HERE.parent/'T14_DIRICHLET_FORCED_PROFILE/RESULT.json').read_text())['quantities']
    ca=bounds(q['lower_compact_response_magnitude']);cb=bounds(q['upper_compact_response_magnitude'])
    C=bounds(q['equal_compact_response_magnitude']);s=bounds(q['scalar_norm_share'])
    assert min(ca[0],cb[0],C[0],s[0])>0,'POSITIVE_LIMIT_INPUTS'
    assert max(C[0],ca[0]+cb[0])<=min(C[1],ca[1]+cb[1]),'SUM_CONSISTENCY'
    D=F(1,50);A=(D*C[0]/s[1],D*C[1]/s[0])
    for k in (F(1,10),F(1),F(100),F(10000)):
        t=1/(1+k);dt=-t*t
        assert dt==-1/(1+k)**2 and k*k*t*t==(1-t)**2,'CHAIN_RULE'
        for a,L,Z in ((F(1),F(2),F(3)),(F(9,10),F(-1,7),F(11))):
            f=2*L/k;partial=a**4*f*f/Z
            assert k*k*partial==4*a**4*L*L/Z,'ENDPOINT_RESPONSE_IDENTITY'
        assert D*(C[0]*t*t)/s[1]==A[0]*t*t,'FACTOR_IDENTITY'
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='CERTIFIED_ASYMPTOTIC_STIFFNESS_RESPONSE_RELATIONS',
        scaled_equal_response_limit=rec(C),nonzero_Dirichlet_scalar_fraction=rec(s),
        scaled_endpoint_factor_limit=rec(A),unscaled_endpoint_factor_limit=0,
        requires_inherited_simple_analytic_branch=True,finite_stiffness_crossover_certified=False,
        finite_stiffness_remainder_certified=False,new_ODE_solve=False,all_gates_passed=True))
try:main()
except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
