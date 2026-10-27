import sys,json,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core,taylor,scaled
from interval import I,S,box,power
RATES=scaled.RATES+[I(20),I(4),I(2),I(2)]
CTX={}
def get(v):return box(F(v['lo']),F(v['hi']))
def hull(v):return I(min(x.lo for x in v),max(x.hi for x in v))
def rhs(y,d,alpha,rep):
    a,H,P,t,psi,Fp,v=y[:7]
    return scaled.rhs(y[:7],d,alpha,rep)+[a*a*Fp*Fp,a*a*psi*psi,psi,1/(a*a)]
def jrhs(z,d,alpha,rep):
    m=taylor.mul;a,psi,Fp=z[0],z[4],z[5];a2=m(a,a)
    return scaled.jrhs(z[:7],d,alpha,rep)+[m(a2,m(Fp,Fp)),m(a2,m(psi,psi)),psi,taylor.inv(a2)]
def step(y,h,d,alpha,rep):
    rr=[(I(abs(h))*v).hi for v in RATES];tube=[v+I(-r,r) for v,r in zip(y,rr)]
    assert all(v.in_exact(*lim) for v,lim in zip(tube[:4],scaled.LIMITS)),'EXTENDED_BACKGROUND_BOX'
    assert scaled.bg(tube,d)[3].lo>0
    return taylor.step(y,h,lambda z:rhs(z,d,alpha,rep),lambda z:jrhs(z,d,alpha,rep),RATES,False,8)
def integrate(n,d,alpha,rep):
    low=scaled.background(n,-1,d);up=scaled.background(n,1,d)
    a,H,P,t=low;G=3*alpha/(a*a*t)
    y=low+[I(1),I(0),G if rep=='G' else G-2*t]+[I(0) for _ in range(4)]
    for j in range(2*n):
        CTX.update(n=n,representation=rep,step=j+1)
        y=step(y,F(1,n),d,alpha,rep)
        assert scaled.constraint(y[:7],d,alpha,rep).contains(0),'CONSTRAINT'
    assert scaled.ham(y,d).contains(0) and all(core.overlap(a,b) for a,b in zip(y[:4],up))
    return y
def quantities(y,d):
    IF,IP,SS,J=y[-4:]
    assert IF.lo>0 and IP.lo>0 and J.lo>0,'POSITIVE_INTEGRALS'
    den=power(d,4)*IF+6*IP
    sn=IF/(16*den);cn=SS*SS/den;eta=SS*SS/(IP*J)
    assert eta.lo<=S,'CS_INCONSISTENCY'
    return dict(IF=IF,IP=IP,S=SS,J=J,scalar_fraction_over_D4=sn,
        canonical_separation_squared_over_D=cn,
        scalar_fraction=power(d,4)*IF/den,canonical_separation_squared=2*d*cn,
        coherence_raw=eta,coherence=I(eta.lo,min(S,eta.hi)))
def outcome(v,w):
    return 'SUPPORTED' if w.contains(v) else ('CONTRADICTED' if max(w.lo,v.lo)>min(w.hi,v.hi) else 'INCONCLUSIVE')
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    for rep in ('G','W'):
        y=integrate(8,I(0),I(F(-2,3)),rep)
        assert all(v.contains(x) for v,x in zip(y[-4:],(F(64,15),F(2),F(2),F(2)))),'EXACT_PARABOLIC_INTEGRALS'
    sw=box(F(99,4500),F(101,4500));cw=box(F(99,300),F(101,300));out={}
    cfg=json.loads((HERE/'CONFIG.json').read_text())
    for case in cfg['cases']:
        name=case['name'];D=F(case['D']);d=I(D/2);CTX.update(case=name)
        parent=json.loads((HERE.parent/case['parent']/'RESULT.json').read_text());assert F(parent['width'])==D
        alpha=(get(parent['physical_mu_bracket'])+12)/(d*d);runs={}
        for rep in ('G','W'):
            for n in cfg['levels']:
                y=integrate(n,d,alpha,rep);q=quantities(y,d);runs[rep,n]=q
                core.save(name+'_'+rep+'_'+str(n)+'.json',dict(mass=parent['physical_mu_bracket'],
                    upper_state=[v.record() for v in y],quantities={k:v.record() for k,v in q.items()}))
            assert all(core.overlap(runs[rep,16][k],runs[rep,32][k]) for k in q),'LEVEL_OVERLAP'
        assert all(core.overlap(runs['G',32][k],runs['W',32][k]) for k in q),'REPRESENTATION_OVERLAP'
        q={k:hull([runs['G',32][k],runs['W',32][k]]) for k in q}
        out[name]=dict(D=str(D),quantities={k:v.record() for k,v in q.items()},
            scalar_limit_window_outcome=outcome(q['scalar_fraction_over_D4'],sw),
            separation_limit_window_outcome=outcome(q['canonical_separation_squared_over_D'],cw))
    a=out['full']['quantities'];b=out['half']['quantities']
    sr=get(a['scalar_fraction'])/get(b['scalar_fraction'])
    cr=get(a['canonical_separation_squared'])/get(b['canonical_separation_squared'])
    srw=box(F(396,25),F(404,25));crw=box(F(99,50),F(101,50))
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='CERTIFIED_WIDTH_MODE_NORM_COMPARISON',cases=out,
        scalar_fraction_ratio=sr.record(),scalar_ratio_outcome=outcome(sr,srw),
        separation_squared_ratio=cr.record(),separation_ratio_outcome=outcome(cr,crw),
        scalar_coefficient_window=sw.record(),separation_coefficient_window=cw.record(),
        all_technical_gates_passed=True,finite_width_accuracy_windows_are_empirical=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(e)));raise
    finally:signal.alarm(0)
