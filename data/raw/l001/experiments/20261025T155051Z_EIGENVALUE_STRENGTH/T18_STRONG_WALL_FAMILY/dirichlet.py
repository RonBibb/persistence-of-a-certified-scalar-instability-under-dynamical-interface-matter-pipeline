import hashlib,json,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core
from interval import I,box
save=core.save
TRACE=[]
CTX={}
def fg(y,mu):
    a,H,P,T,psi,f,g=y
    vp=1-P+4*P*P*P
    return core.bg(y)+[-2*H*psi-T*f/3,g,
        -4*H*g+(-1+12*P*P-mu/(a*a)+2*T*T)*f+(12*H*T-4*vp)*psi]
def asL(y):
    a,H,P,T,psi,f,g=y
    return [a,H,P,T,psi,f,g+2*T*psi]
def propagate(low,n,mu,rep):
    assert F(-12001,1000)<=mu<=F(-12),'MASS_DOMAIN'
    a,H,P,T=low
    assert T.hi<0,'LOWER_T_NONZERO'
    L=3*(mu+12)/(a*a*T)
    y=low+[I(1),I(0),L if rep=='L' else L-2*T]
    fun=(lambda z:core.full(z,mu)) if rep=='L' else (lambda z:fg(z,mu))
    constraint=lambda z:core.constraint(z if rep=='L' else asL(z),mu)
    assert constraint(y).contains(0),'INITIAL_CONSTRAINT'
    h=F(1,100*n)
    for j in range(2*n):
        CTX.update(n=n,mu=str(mu),representation=rep,step=j+1)
        y=core.step(y,h,fun,core.RBG+[I(10),I(1),I(10)])
        assert constraint(y).contains(0),'CONSTRAINT'
    assert core.ham(y).contains(0),'HAMILTONIAN'
    return y[-2],y,constraint(y)
def controls():
    c=core.controls()
    for P,T in ((F(-1,1000),F(-1,100)),(F(0),F(0)),(F(1,1000),F(1,100))):
        for mu in (F(-12001,1000),F(-12)):
            z=[I(1),I(-2),I(P),I(T),I(1),I(F(1,100)),I(F(1,20))]
            zl=asL(z);a=fg(z,mu);b=core.full(zl,mu)
            assert all(core.overlap(x,y) for x,y in zip(a[:6],b[:6])),'FG_FIRST_EQUATIONS'
            assert core.overlap(a[-1],b[-1]-2*core.bg(z)[3]*z[4]-2*z[3]*b[4]),'FG_CHAIN_RULE'
    for lam in (F(-1,1000),F(-1,1000000),F(0)):
        a=I(1);T=I(F(-1,100));L=3*lam/(a*a*T)
        assert (T*L-3*lam/(a*a)).contains(0),'DIRICHLET_LAUNCH_CONTROL'
    c.update(fg_chain_rule=True,dirichlet_launch=True,shifted_zero_regular=True)
    return c
def search(low,n,cfg):
    lo=F(cfg['search_lo']);hi=F(cfg['search_hi']);cache={}
    def ev(mu):
        if mu not in cache:
            r,y,c=propagate(low,n,mu,'L');cache[mu]=r
            TRACE.append(dict(n=n,mu=str(mu),residual=r.record(),sign=core.sign(r)))
        return cache[mu]
    s=core.sign(ev(lo));assert s and core.sign(ev(hi))==-s,'INITIAL_BRACKET'
    for j in range(24):
        if hi-lo<=F(cfg['target_width']):break
        before=(lo,hi);mid=(lo+hi)/2;sm=core.sign(ev(mid))
        if sm==s:lo=mid
        elif sm==-s:hi=mid
        else:
            a=(lo+mid)/2;b=(mid+hi)/2
            if core.sign(ev(a))==s:lo=a
            if core.sign(ev(b))==-s:hi=b
            if hi-lo<=F(cfg['target_width']):break
            assert (lo,hi)!=before,'NO_CERTIFIED_CONTRACTION'
    assert hi-lo<=F(cfg['target_width']),'BRACKET_WIDTH'
    return dict(n=n,lo=str(lo),hi=str(hi),width=str(hi-lo),
        lo_residual=ev(lo).record(),hi_residual=ev(hi).record(),
        endpoint_signs=[core.sign(ev(lo)),core.sign(ev(hi))],evaluations=len(cache))
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'BINDINGS'
    exe=Path(sys.executable).resolve()
    assert sys.version_info[:3]==(3,12,3)
    assert core.digest(exe)=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    cfg=json.loads((HERE/'CONFIG.json').read_text());save('CONTROLS.json',controls())
    results=[]
    for n in cfg['levels']:
        result=search(core.lower(n),n,cfg);save('LEVEL_'+str(n)+'.json',result);results.append(result)
    c,f=results
    assert max(F(c['lo']),F(f['lo']))<=min(F(c['hi']),F(f['hi'])),'LEVEL_DISJOINT'
    assert F(f['width'])<=F(c['width']),'LEVEL_WIDENED'
    assert F(f['hi'])<-12,'STRICT_NEGATIVE_LAMBDA'
    low=core.lower(cfg['audit_n']);audit=[]
    for key in ('lo','hi'):
        m=F(f[key]);r,y,con=propagate(low,cfg['audit_n'],m,'g')
        old=f[key+'_residual']
        assert core.overlap(r,box(F(old['lo']),F(old['hi']))),'REPRESENTATION_DISJOINT'
        assert core.sign(r)==f['endpoint_signs'][0 if key=='lo' else 1],'AUDIT_SIGN'
        audit.append(dict(mu=str(m),residual=r.record(),constraint=con.record(),sign=core.sign(r)))
    rz,yz,cz=propagate(low,cfg['audit_n'],F(-12),'g')
    assert core.sign(rz)!=0,'SHIFTED_ZERO_EXCLUSION_CHECK'
    save('AUDIT_ENDPOINTS.json',audit)
    save('SHIFTED_ZERO.json',dict(residual=rz.record(),constraint=cz.record(),physical_root=False))
    save('SEARCH_TRACE.json',TRACE)
    from math import isqrt
    from interval import S
    def sqrtbox(x):
        assert x.lo>=0
        lo=isqrt(x.lo*S);hi=isqrt(x.hi*S)
        return I(lo,hi+(hi*hi<x.hi*S))
    mass=box(F(f['lo']),F(f['hi']));rate=(sqrtbox(9-4*mass/3)-3)/2
    assert rate.lo>S,'GROWTH_ABOVE_H'
    parents={}
    for name in ('T7_PERSISTENT_SOFT','T8_PERSISTENT_STIFF'):
        q=json.loads((HERE.parent/name/'RESULT.json').read_text())['physical_mu_bracket']
        old=box(F(q['lo']),F(q['hi']));shift=mass-old
        assert shift.lo>0,'STIFFNESS_ORDER'
        parents[name]=dict(mass_shift=shift.record(),fractional_mass_squared_suppression=(shift/(-old)).record())
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'FINAL_BINDINGS'
    save('RESULT.json',dict(classification='CERTIFIED_DOUBLE_DIRICHLET_PERSISTENT_CEILING',
        physical_mu_bracket=f,negative_lambda_gap=(-mass-12).record(),
        conditional_growth_rate_over_H=rate.record(),finite_wall_comparison=parents,
        full_fg_audit=audit,all_gates_passed=True,normalization='psi_a_1',
        global_nonnegative_wall_ceiling_inherited=True))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(exc),trace=TRACE));raise
    finally:signal.alarm(0)
