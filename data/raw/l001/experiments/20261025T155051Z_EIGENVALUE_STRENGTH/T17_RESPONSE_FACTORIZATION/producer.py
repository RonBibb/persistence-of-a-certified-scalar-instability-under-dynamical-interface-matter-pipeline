import hashlib,json,os,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,S,box,power
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=HERE/n;assert not p.exists();tmp=HERE/(n+'.tmp')
    with tmp.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,p);tmp.unlink()
def get(v):return box(F(v['lo']),F(v['hi']))
def sq(x):
    if x.lo<=0<=x.hi:return I(0,max(x.lo*x.lo,x.hi*x.hi)//S+1)
    return x*x
def direct_factor(folder,case):
    uniform=folder=='T11_UNIFORM_EXTRA_FAMILY'
    cfg=None if uniform else json.loads((HERE.parent/case/'CONFIG.json').read_text())
    label='uniform_surviving_extra' if uniform else cfg['case']
    values=[]
    for rep in ('reduced','full'):
        r=json.loads((HERE.parent/folder/(label+'_'+rep+'_8192.json')).read_text())
        a,H,P,T=[get(v) for v in r['lower_background']]
        y=[get(v) for v in r['upper_state']]
        fa=I(1)
        if folder=='T10_PERSISTENT_PARTICIPATION':
            mu=get(r['mass_box']);ka=F(cfg['kappa_a']);U=1-P+4*power(P,3)-4*H*T
            fa=3*(mu+12)/(a*a*(T*ka/2-U))
        B=power(a,4)*sq(fa)+power(y[0],4)*sq(y[-2])
        values.append(I(F(1,50))*B/get(r['quantities']['Zf']))
    return I(min(x.lo for x in values),max(x.hi for x in values))
def outcome(x,w):
    if w.contains(x):return 'SUPPORTED'
    if max(x.lo,w.lo)>min(x.hi,w.hi):return 'CONTRADICTED'
    return 'INCONCLUSIVE'
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    D=I(F(1,50));window=box(F(99,100),F(101,100))
    results={}
    for folder in ('T3_MODE_PARTICIPATION','T10_PERSISTENT_PARTICIPATION','T11_UNIFORM_EXTRA_FAMILY'):
        rr=json.loads((HERE.parent/folder/'RESULT.json').read_text())['results']
        for case,q in rr.items():
            # Conservative input intervals are not intersected or rescaled in their sealed parents.
            share=get(q['scalar_norm_share']);response=get(q['equal_response'])
            ratio_E=D*response/share
            E=direct_factor(folder,case)
            assert max(E.lo,ratio_E.lo)<=min(E.hi,ratio_E.hi),'RAW_RATIO_CONSISTENCY'
            results[folder+'/'+case]=dict(scalar_norm_share=share.record(),
                equal_response=response.record(),endpoint_to_bulk_factor=E.record(),
                response_ratio_crosscheck=ratio_E.record(),
                one_percent_window_outcome=outcome(E,window))
    pairs={}
    for label,extra,persistent in (('soft','T1R2_SOFT_MODE','T7_PERSISTENT_SOFT'),
                                  ('equal_018','T2_STIFF_MODE','T8_PERSISTENT_STIFF')):
        e=results['T3_MODE_PARTICIPATION/'+extra];p=results['T10_PERSISTENT_PARTICIPATION/'+persistent]
        response_ratio=get(p['equal_response'])/get(e['equal_response'])
        share_ratio=get(p['scalar_norm_share'])/get(e['scalar_norm_share'])
        factor_ratio=get(p['endpoint_to_bulk_factor'])/get(e['endpoint_to_bulk_factor'])
        product=share_ratio*factor_ratio
        assert max(response_ratio.lo,product.lo)<=min(response_ratio.hi,product.hi),'IDENTITY_CONSISTENCY'
        pairs[label]=dict(response_ratio=response_ratio.record(),scalar_share_ratio=share_ratio.record(),
            endpoint_factor_ratio=factor_ratio.record(),factor_ratio_one_percent_outcome=outcome(factor_ratio,window))
    for zf,zp,B in ((F(2),F(12),F(4)),(F(1,100),F(3),F(1,10))):
        Z=zf+zp;share=zf/Z;resp=B/Z;E=F(1,50)*B/zf
        assert F(1,50)*resp==share*E,'EXACT_FACTORIZATION'
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='CERTIFIED_RESPONSE_FACTORIZATION',results=results,pairs=pairs,
        endpoint_factor_window=window.record(),identity_independent_of_model=True,
        component_independence_or_energy_fraction_claim=False,all_gates_passed=True))
try:main()
except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
