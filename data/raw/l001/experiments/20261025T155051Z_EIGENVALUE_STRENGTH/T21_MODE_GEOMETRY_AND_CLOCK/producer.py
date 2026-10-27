import hashlib,json,os,sys,math
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
def get(v):return box(F(v['lo']),F(v['hi']))
def sqrtbox(x):
    assert x.lo>=0
    lo=math.isqrt(x.lo*S);hi=math.isqrt(x.hi*S)
    return I(lo,hi+(hi*hi<x.hi*S))
def rate(mu):return (sqrtbox(9-4*mu/3)-3)/2
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    root=HERE.parent
    extra=json.loads((root/'T11_UNIFORM_EXTRA_FAMILY/RESULT.json').read_text())
    persistent=json.loads((root/'T20_ALL_WALL_PERSISTENT_FAMILY/RESULT.json').read_text())
    ec=extra['consequences'];pc=persistent['global_consequences']
    assert ec['scalar_profile_positive_everywhere'] and ec['metric_profile_negative_everywhere'],'EXTRA_SIGN_PREMISE'
    assert pc['psi_positive_everywhere'] and pc['scalar_positive_interior_from_nonnegative_endpoints'],'PERSISTENT_SIGN_PREMISE'
    soft=get(json.loads((root/'T7_PERSISTENT_SOFT/RESULT.json').read_text())['physical_mu_bracket'])
    dd=get(json.loads((root/'T12_DIRICHLET_CEILING/RESULT.json').read_text())['physical_mu_bracket'])
    es=get(json.loads((root/'T1R2_SOFT_MODE/RESULT.json').read_text())['physical_mu_bracket'])
    pm=I(soft.lo,dd.hi);em=I(es.lo,0)
    pr=-3*(pm+12);er=-3*(em+12)
    assert pr.lo>0 and er.hi<0,'CENTER_RATIO_SIGNS'
    rs=rate(soft);rd=rate(dd)
    assert rs.lo>rd.hi and rd.lo>S,'GROWTH_ORDER'
    reduction=1-rd/rs
    assert reduction.lo>0,'GROWTH_SUPPRESSION'
    for mu,x in ((F(0),F(0)),(F(-12),F(1))):
        assert rate(I(mu)).contains(x),'CLOCK_ENDPOINT_CONTROL'
    for lam in (F(-1,1000),F(1)):
        for psi,amplitude in ((F(1),F(2)),(F(-1),F(-3))):
            f=-3*lam*psi;sep=-2*psi*F(1,50)
            prod=f*sep*amplitude*amplitude
            assert (prod>0)==(lam>0),'ORIENTATION_CONTROL'
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='CERTIFIED_BRANCH_GEOMETRY_AND_CLOCK_RELATIONS',
        center_scalar_to_metric_ratio=dict(persistent=pr.record(),extra=er.record()),
        relative_scalar_separation_product_sign=dict(persistent=-1,extra=1),
        persistent_growth=dict(soft=rs.record(),dirichlet=rd.record(),maximum_fractional_suppression=reduction.record()),
        growth_band=dict(extra='strictly_between_zero_and_one_Hubble_rate',persistent='strictly_above_one_Hubble_rate'),
        overall_amplitude_sign_free=True,nonlinear_or_excitation_claim=False,all_gates_passed=True))
try:main()
except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
