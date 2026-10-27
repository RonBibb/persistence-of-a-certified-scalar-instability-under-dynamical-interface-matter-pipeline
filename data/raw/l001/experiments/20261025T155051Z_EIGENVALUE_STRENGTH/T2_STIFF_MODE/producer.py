import hashlib,itertools,json,os,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,box,power
CONTEXT={}
RBG=[I(x) for x in (3,5,F(1,10),2)]
LIMITS=[(F(9,10),F(11,10)),(F(-21,10),F(-19,10)),(F(-1,100),F(1,100)),(F(-1,50),F(1,50))]
TRACE=[]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):
    dest=HERE/name
    assert not dest.exists(),'OVERWRITE'
    tmp=HERE/(name+'.tmp')
    with tmp.open('x') as f:
        json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
    os.link(tmp,dest); tmp.unlink()
def bg(y):
    a,H,P,T=y[:4]
    return [H*a,-T*T/3-3/(a*a),T,1-P+4*power(P,3)-4*H*T]
def ham(y):
    a,H,P,T=y[:4]
    return H*H-1-T*T/12+(P-P*P/2+power(P,4))/6-3/(a*a)
def coeff(y,mu):
    a,H,P,T=y[:4]; U=bg(y)[3]; K=a*a/(3*(mu+12))
    A=2*K*T*U; E=1-2*K*T*T
    C=-1+12*P*P-mu/(a*a)+4*T*T/3+2*K*U*U
    return A,E,C,-4*H-A
def reduced(y,mu):
    A,E,C,D=coeff(y,mu); f,L=y[4:]
    return bg(y)+[A*f+E*L,C*f+D*L]
def full(y,mu):
    a,H,P,T,psi,f,L=y; U=bg(y)[3]
    return bg(y)+[-2*H*psi-T*f/3,L-2*T*psi,
                  -4*H*L+(-1+12*P*P-mu/(a*a)+4*T*T/3)*f-2*U*psi]
def constraint(y,mu):
    a,H,P,T,psi,f,L=y
    return T*L-bg(y)[3]*f-3*(mu+12)*psi/(a*a)
def step(y,hq,fun,rates,check_bg=True):
    assert len(y)==len(rates)
    h=I(hq); dt=box(min(F(0),hq),max(F(0),hq))
    radii=[(I(abs(hq))*r).hi for r in rates]
    tube=[v+I(-r,r) for v,r in zip(y,radii)]
    if check_bg: assert all(x.in_exact(*lim) for x,lim in zip(tube[:4],LIMITS)),'BACKGROUND_TUBE'
    rhs=fun(tube)
    assert len(rhs)==len(y)
    assert all(b.strict(v+dt*w) for b,v,w in zip(tube,y,rhs)),'TUBE_CONTAINMENT'
    return [v+h*w for v,w in zip(y,rhs)]
def lower(n):
    y=[I(x) for x in (1,-2,0,0)]; h=F(-1,100*n)
    for j in range(n):
        CONTEXT.update(phase='background',n=n,step=j+1)
        y=step(y,h,bg,RBG)
    assert ham(y).contains(0),'LOWER_HAMILTONIAN'
    return y
def propagate(low,n,mu,ka,kb,representation='reduced'):
    assert -12<mu<=0
    a,H,P,T=low; f=I(1); L=I(ka/2)
    if representation=='reduced':
        y=low+[f,L]; fun=lambda z:reduced(z,mu); rates=RBG+[I(1),I(5)]
    else:
        psi=a*a*(T*L-bg(low)[3]*f)/(3*(mu+12))
        y=low+[psi,f,L]; fun=lambda z:full(z,mu); rates=RBG+[I(1),I(1),I(5)]
    h=F(1,100*n)
    for j in range(2*n):
        CONTEXT.update(phase=representation,n=n,mu=str(mu),step=j+1)
        y=step(y,h,fun,rates)
        if representation!='reduced': assert constraint(y,mu).contains(0),'CONSTRAINT'
    assert ham(y).contains(0),'UPPER_HAMILTONIAN'
    return y[-1]+kb*y[-2]/2,y
def sign(x): return 1 if x.lo>0 else (-1 if x.hi<0 else 0)
def overlap(x,y): return max(x.lo,y.lo)<=min(x.hi,y.hi)
def controls():
    count=0
    for xa,xb,ya,yb in ((F(-1,3),F(2,3),F(1,5),F(4,5)),(-2,-1,-3,-2),(0,1,-1,1)):
        x=box(xa,xb);y=box(ya,yb); xl,xh=x.bounds();yl,yh=y.bounds()
        for out,vals in ((x+y,[a+b for a in (xl,xh) for b in (yl,yh)]),
                         (x-y,[a-b for a in (xl,xh) for b in (yl,yh)]),
                         (x*y,[a*b for a in (xl,xh) for b in (yl,yh)])):
            lo,hi=out.bounds();assert lo<=min(vals) and max(vals)<=hi;count+=1
    try: I(1)/box(-1,1)
    except AssertionError: pass
    else: raise AssertionError('ZERO_DIVISOR_CONTROL')
    for h in (F(-1,100),F(1,100)):
        assert step([I(1)],h,lambda z:[I(1)],[I(2)],False)[0].contains(I(1+h))
    try: step([I(1)],F(1,100),lambda z:[I(1)],[I(0)],False)
    except AssertionError: pass
    else: raise AssertionError('UNDERSIZED_CONTROL')
    for mu in (F(-2),F(-1),F(-1,10),F(0)):
        y=[I(x) for x in (1,-2,0,0)]
        A,E,C,D=coeff(y,mu)
        assert A.contains(0) and E.contains(1) and C.contains(-1-mu+F(2,3)/(mu+12)) and D.contains(8)
        for P,T in ((F(-1,1000),F(-1,100)),(F(0),F(0)),(F(1,1000),F(1,100))):
            z=[I(1),I(-2),I(P),I(T)];f=I(1);L=I(F(1,100));U=bg(z)[3]
            psi=z[0]*z[0]*(z[3]*L-U*f)/(3*(mu+12))
            rr=reduced(z+[f,L],mu); ff=full(z+[psi,f,L],mu)
            assert overlap(rr[-2],ff[-2]) and overlap(rr[-1],ff[-1])
            aa,ee,cc,dd=coeff(z,mu);assert (aa+dd+4*z[1]).contains(0)
    return dict(arithmetic_corners=count,signed_step=True,undersized_rejected=True,
                rational_seed_coefficients=True,constrained_reduction_identity=True,trace_identity=True)
def search(low,n,cfg):
    ka=F(cfg['kappa_a']);kb=F(cfg['kappa_b']);lo=F(cfg['search_lo']);hi=F(cfg['search_hi'])
    cache={}
    def ev(m):
        if m not in cache:
            r,y=propagate(low,n,m,ka,kb);cache[m]=r
            TRACE.append(dict(n=n,mu=str(m),residual=r.record(),sign=sign(r)))
        return cache[m]
    s=sign(ev(lo)); assert s and sign(ev(hi))==-s,'INITIAL_BRACKET'
    ambiguous=0
    for j in range(24):
        if hi-lo<=F(cfg['target_width']): break
        mid=(lo+hi)/2; sm=sign(ev(mid))
        if sm==s: lo=mid
        elif sm==-s: hi=mid
        else:
            ambiguous+=1; a=(lo+mid)/2;b=(mid+hi)/2;sa=sign(ev(a));sb=sign(ev(b))
            if sa==s: lo=a
            if sb==-s: hi=b
            if hi-lo<=F(cfg['target_width']): break
            assert ambiguous<=3,'AMBIGUITY_LIMIT'
    assert hi-lo<=F(cfg['target_width']),'BRACKET_WIDTH'
    return dict(n=n,lo=str(lo),hi=str(hi),width=str(hi-lo),
                lo_residual=ev(lo).record(),hi_residual=ev(hi).record(),
                endpoint_signs=[sign(ev(lo)),sign(ev(hi))],evaluations=len(cache))
def main():
    admission=json.loads((HERE/'ADMISSION.json').read_text())
    assert admission['admitted'] is True
    assert all(digest(HERE/p)==h for p,h in admission['sources'].items()),'BINDINGS'
    exe=Path(sys.executable).resolve();rh=digest(exe)
    assert sys.version_info[:3]==(3,12,3) and rh=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    cfg=json.loads((HERE/'CONFIG.json').read_text());save('CONTROLS.json',controls())
    results=[]
    for n in cfg['levels']:
        low=lower(n);result=search(low,n,cfg);save('LEVEL_'+str(n)+'.json',result);results.append(result)
        if n==cfg['levels'][-1]:
            r,y=propagate(low,n,F(0),F(0),F(0))
            ref=json.loads((HERE.parent.parent/'20261025T141207Z_CONTAINMENT_RECOVERY/T4_CORRECTED_COORDINATES/LEVEL_2048.json').read_text())
            c=ref['upper_state'][6];assert overlap(r,box(F(c['lo']),F(c['hi']))),'ZERO_MASS_ANCHOR'
    c,f=results
    assert max(F(c['lo']),F(f['lo']))<=min(F(c['hi']),F(f['hi'])),'LEVEL_DISJOINT'
    assert F(f['width'])<=F(c['width']),'LEVEL_WIDENED'
    low=lower(cfg['audit_n']);audit=[]
    for key in ('lo','hi'):
        m=F(f[key]);r,y=propagate(low,cfg['audit_n'],m,F(cfg['kappa_a']),F(cfg['kappa_b']),'full')
        old=f[key+'_residual'];assert overlap(r,box(F(old['lo']),F(old['hi']))),'REPRESENTATION_DISJOINT'
        assert sign(r)==f['endpoint_signs'][0 if key=='lo' else 1],'AUDIT_SIGN'
        audit.append(dict(mu=str(m),residual=r.record(),constraint=constraint(y,m).record(),sign=sign(r)))
    save('AUDIT_ENDPOINTS.json',audit);save('SEARCH_TRACE.json',TRACE)
    assert all(digest(HERE/p)==h for p,h in admission['sources'].items()) and digest(exe)==rh,'FINAL_BINDINGS'
    save('RESULT.json',dict(classification='CERTIFIED_UNIQUE_EXTRA_MODE_BRACKET',case=cfg['case'],
        physical_mu_bracket=f,full_system_audit=audit,all_gates_passed=True,
        persistent_below_minus_12_mode=True,clock_conversion_performed=False))
if __name__=='__main__':
    def timeout(s,f): raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:
        save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CONTEXT,error=repr(exc),trace=TRACE));raise
    finally:signal.alarm(0)
