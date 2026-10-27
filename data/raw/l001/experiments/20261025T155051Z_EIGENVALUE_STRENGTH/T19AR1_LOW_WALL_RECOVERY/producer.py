import hashlib,json,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core
from interval import I,box
def save(name,data):return core.save((CASE+'_' if CASE else '')+name,data)
TRACE=[]
CASE=None
TA=TB=None
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
    assert F(-12061,1000)<=mu<=F(-12),'MASS_DOMAIN'
    a,H,P,T=low
    assert T.hi<0,'LOWER_T_NONZERO'
    ja=-(1-TA)/2;E=TA*core.bg(low)[3]+ja*T
    assert E.lo>0,'COMPACT_LAUNCH_DENOMINATOR'
    f=-3*(mu+12)*TA/(a*a*E);L=3*(mu+12)*ja/(a*a*E)
    y=low+[I(1),f,L if rep=='L' else L-2*T]
    assert (TA*L+ja*f).contains(0),'LOWER_WALL'
    fun=(lambda z:core.full(z,mu)) if rep=='L' else (lambda z:fg(z,mu))
    constraint=lambda z:core.constraint(z if rep=='L' else asL(z),mu)
    assert constraint(y).contains(0),'INITIAL_CONSTRAINT'
    h=F(1,100*n)
    for j in range(2*n):
        CTX.update(n=n,mu=str(mu),representation=rep,step=j+1)
        y=core.step(y,h,fun,core.RBG+[I(10),I(1),I(10)])
        assert constraint(y).contains(0),'CONSTRAINT'
    assert core.ham(y).contains(0),'HAMILTONIAN'
    yl=y if rep=='L' else asL(y)
    return TB*yl[-1]+(1-TB)*yl[-2]/2,y,constraint(y)
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
    global CASE,TA,TB
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'BINDINGS'
    exe=Path(sys.executable).resolve()
    assert sys.version_info[:3]==(3,12,3)
    assert core.digest(exe)=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    cfg=json.loads((HERE/'CONFIG.json').read_text());save('CONTROLS.json',controls())
    # Verify general compact lower launch on exact rational central-independent endpoint data.
    for ta in (F(0),F(1,101),F(1)):
        for lam in (F(-1,1000),F(-1,1000000),F(0)):
            a=I(1);T=I(F(-1,100));U=I(1);ja=-(1-ta)/2;E=ta*U+ja*T
            f=-3*lam*ta/(a*a*E);L=3*lam*ja/(a*a*E)
            assert (ta*L+ja*f).contains(0) and (T*L-U*f-3*lam/(a*a)).contains(0)
    results={}
    for case in cfg['cases']:
        CASE=case['name'];TA=F(case['t_a']);TB=F(case['t_b']);TRACE.clear()
        levels=[]
        for n in cfg['levels']:
            levelcfg=dict(cfg,**case)
            if n==cfg['levels'][0]:levelcfg['target_width']=cfg['coarse_target_width']
            r=search(core.lower(n),n,levelcfg);save('LEVEL_'+str(n)+'.json',r);levels.append(r)
        c,f=levels
        assert F(f['width'])<=F(cfg['target_width']),'FINAL_WIDTH'
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
        save('AUDIT_ENDPOINTS.json',audit);save('SEARCH_TRACE.json',TRACE)
        save('SHIFTED_ZERO.json',dict(residual=rz.record(),constraint=cz.record()))
        mass=box(F(f['lo']),F(f['hi']))
        results[CASE]=dict(physical_mu_bracket=f,negative_lambda_gap=(-mass-12).record(),
            t_a=str(TA),t_b=str(TB),full_fg_audit=audit)
    CASE=None
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'FINAL_BINDINGS'
    save('RESULT.json',dict(classification='CERTIFIED_LOWER_WALL_ROOT_ENVELOPES',
        results=results,all_gates_passed=True,normalization='psi_a_1'))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(exc),trace=TRACE));raise
    finally:signal.alarm(0)
