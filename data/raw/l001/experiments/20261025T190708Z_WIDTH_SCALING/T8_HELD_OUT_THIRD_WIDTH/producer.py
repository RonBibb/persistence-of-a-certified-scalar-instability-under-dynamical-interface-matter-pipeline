import hashlib,json,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core,taylor
from interval import I,box
save=core.save
TRACE=[]
CTX={}
D=None
UPPER=None
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
    h=D/(2*n)
    for j in range(2*n):
        CTX.update(n=n,mu=str(mu),representation=rep,step=j+1)
        y=taylor.step(y,h,fun,lambda z:taylor.rhs(z,mu,rep),core.RBG+[I(10),I(1),I(10)],order=8)
        assert constraint(y).contains(0),'CONSTRAINT'
    assert core.ham(y).contains(0),'HAMILTONIAN'
    assert all(core.overlap(a,b) for a,b in zip(y[:4],UPPER[n])),'FRESH_UPPER_BACKGROUND'
    return y[-2],y,constraint(y)
def controls():
    c=core.controls()
    whole_background=[box(lo,hi) for lo,hi in core.LIMITS]
    U=core.bg(whole_background)[3]
    assert U.lo>0,'SINGLE_TURN_GLOBAL_BOX'
    for P,T in ((F(-1,1000),F(-1,100)),(F(0),F(0)),(F(1,1000),F(1,100))):
        for mu in (F(-12001,1000),F(-12)):
            z=[I(1),I(-2),I(P),I(T),I(1),I(F(1,100)),I(F(1,20))]
            zl=asL(z);a=fg(z,mu);b=core.full(zl,mu)
            assert all(core.overlap(x,y) for x,y in zip(a[:6],b[:6])),'FG_FIRST_EQUATIONS'
            assert core.overlap(a[-1],b[-1]-2*core.bg(z)[3]*z[4]-2*z[3]*b[4]),'FG_CHAIN_RULE'
    for lam in (F(-1,1000),F(-1,1000000),F(0)):
        a=I(1);T=I(F(-1,100));L=3*lam/(a*a*T)
        assert (T*L-3*lam/(a*a)).contains(0),'DIRICHLET_LAUNCH_CONTROL'
    for rep in ('L','g'):
        y=[I(x) for x in (1,-2,F(1,1000),F(-1,100),1,F(1,100),F(1,50))]
        for mu in (F(-12),F(-120001,10000)):
            j=taylor.rhs([taylor.const(v,1) for v in y],mu,rep)
            direct=core.full(y,mu) if rep=='L' else fg(y,mu)
            assert all(core.overlap(v[0],w) for v,w in zip(j,direct)),'JET_RHS_CONSTANT_CONTROL'
    c.update(fg_chain_rule=True,dirichlet_launch=True,shifted_zero_regular=True,global_positive_U=U.record())
    return c
def search(low,n,cfg):
    lo=F(cfg['search_lo']);hi=F(cfg['search_hi']);cache={}
    def ev(mu):
        if mu not in cache:
            r,y,c=propagate(low,n,mu,'L');cache[mu]=r
            TRACE.append(dict(n=n,mu=str(mu),residual=r.record(),sign=core.sign(r)))
        return cache[mu]
    s=core.sign(ev(lo));assert s and core.sign(ev(hi))==-s,'INITIAL_BRACKET'
    for j in range(40):
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
    global D,UPPER
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'BINDINGS'
    exe=Path(sys.executable).resolve()
    assert sys.version_info[:3]==(3,12,3)
    assert core.digest(exe)=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    cfg=json.loads((HERE/'CONFIG.json').read_text());D=F(cfg['width']);save('CONTROLS.json',controls())
    assert D==F(3,200),'WIDTH_CONTRACT'
    UPPER={};LOWER={}
    for n in cfg['levels']+[cfg['audit_n']]:
        LOWER[n]=taylor.background(n,-D/2);UPPER[n]=taylor.background(n,D/2)
        assert LOWER[n][3].hi<0 and UPPER[n][3].lo>0,'ONE_TURN_ENDPOINT_SIGNS'
        save('BACKGROUND_'+str(n)+'.json',dict(n=n,width=str(D),lower=[v.record() for v in LOWER[n]],upper=[v.record() for v in UPPER[n]]))
    envelope=json.loads((HERE.parent/'T6_UNIFORM_WIDTH_LEADING_BOUND/RESULT.json').read_text())
    assert envelope['uniform_twenty_percent_bound'],'UNIFORM_ANCHOR'
    assert F(cfg['search_lo'])==-12-F(1,5)*D*D and F(cfg['search_hi'])==-12-F(2,15)*D*D,'UNIFORM_BRACKET'
    results=[]
    for n in cfg['levels']:
        result=search(LOWER[n],n,cfg);save('LEVEL_'+str(n)+'.json',result);results.append(result)
    c,f=results
    assert max(F(c['lo']),F(f['lo']))<=min(F(c['hi']),F(f['hi'])),'LEVEL_DISJOINT'
    assert F(f['width'])<=F(c['width']),'LEVEL_WIDENED'
    assert F(f['hi'])<-12,'STRICT_NEGATIVE_LAMBDA'
    low=LOWER[cfg['audit_n']];audit=[]
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
    gap=-mass-12;leading=D*D/6;after4=gap-leading+5*D**4/36;coefficient=after4/D**6
    derived=json.loads((HERE.parent/'T7_SIXTH_ORDER_DERIVATION/RESULT.json').read_text())
    C6=F(derived['gap_fullwidth']['D6']);assert C6==F(cfg['predicted_C6'])
    window=box(F(cfg['coefficient_lo']),F(cfg['coefficient_hi']))
    outcome='SUPPORTED' if window.contains(coefficient) else ('CONTRADICTED' if max(window.lo,coefficient.lo)>min(window.hi,coefficient.hi) else 'INCONCLUSIVE')
    assert F(f['width'])<=F(cfg['target_width']),'FINAL_WIDTH'
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'FINAL_BINDINGS'
    core.save('RESULT.json',dict(classification='CERTIFIED_HELD_OUT_SIXTH_ORDER_TEST',
        physical_mu_bracket=f,negative_lambda_gap=gap.record(),width=str(D),
        measured_sixth_order_coefficient=coefficient.record(),predicted_C6=str(C6),
        prediction_window=window.record(),prediction_outcome=outcome,
        remainder_after_D6=(after4-C6*D**6).record(),
        full_fg_audit=audit,all_technical_gates_passed=True,
        finite_width_uniform_remainder_certified=False,parameters_fitted=0,held_out_width=True))

if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(exc),trace=TRACE));raise
    finally:signal.alarm(0)
