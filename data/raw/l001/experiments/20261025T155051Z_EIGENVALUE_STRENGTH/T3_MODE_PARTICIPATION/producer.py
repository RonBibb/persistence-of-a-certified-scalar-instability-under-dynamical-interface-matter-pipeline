import hashlib,json,os,signal,sys,math
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core
from interval import I,S,box,power
CTX={}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
save=core.save
def sq(x):
    if x.lo<=0<=x.hi:return I(0,max(x.lo*x.lo,x.hi*x.hi)//S+1)
    return x*x
def sqrtbox(x):
    assert x.lo>=0,'SQRT_DOMAIN'
    lo=math.isqrt(x.lo*S);hi=math.isqrt(x.hi*S)
    if hi*hi<x.hi*S:hi+=1
    return I(lo,hi)
def weights(y,mu,rep):
    a,H,P,T=y[:4]
    if rep=='reduced':
        f,L=y[4:];psi=a*a*(T*L-core.bg(y)[3]*f)/(3*(mu+12))
    else:psi,f,L=y[4:]
    return 2*sq(a)*sq(f),12*sq(a)*sq(psi),f,psi
def cell(y,h,fun,rates):
    radii=[(I(h)*r).hi for r in rates]
    tube=[v+I(-r,r) for v,r in zip(y,radii)]
    assert all(x.in_exact(*lim) for x,lim in zip(tube[:4],core.LIMITS)),'BACKGROUND_TUBE'
    rhs=fun(tube);dt=box(0,h)
    assert all(b.strict(v+dt*w) for b,v,w in zip(tube,y,rhs)),'TUBE_CONTAINMENT'
    return [v+I(h)*w for v,w in zip(y,rhs)],tube
def enclose(vals):return I(min(x.lo for x in vals),max(x.hi for x in vals))
def evaluate(parent,n,rep):
    cfg=json.loads((parent/'CONFIG.json').read_text());result=json.loads((parent/'RESULT.json').read_text())
    br=result['physical_mu_bracket'];mu=box(F(br['lo']),F(br['hi']))
    assert mu.in_exact(-2,0),'MASS_DOMAIN'
    ka=F(cfg['kappa_a']);kb=F(cfg['kappa_b']);low=core.lower(n)
    a,H,P,T=low;f=I(1);L=I(ka/2)
    if rep=='reduced':y=low+[f,L];fun=lambda z:core.reduced(z,mu);rates=core.RBG+[I(1),I(5)]
    else:
        psi=a*a*(T*L-core.bg(low)[3]*f)/(3*(mu+12))
        y=low+[psi,f,L];fun=lambda z:core.full(z,mu);rates=core.RBG+[I(1),I(1),I(5)]
    bins=[[I(0),I(0)] for _ in range(4)];fenv=[];penv=[];h=F(1,100*n);sep=I(0)
    for j in range(2*n):
        CTX.update(case=cfg['case'],n=n,representation=rep,step=j+1)
        y,tube=cell(y,h,fun,rates)
        wf,wp,f,p=weights(tube,mu,rep);bi=j//(n//2)
        bins[bi][0]=bins[bi][0]+I(h)*wf;bins[bi][1]=bins[bi][1]+I(h)*wp
        sep=sep-2*I(h)*p
        fenv.append(f);penv.append(p)
        if rep=='full':assert core.constraint(y,mu).contains(0),'CONSTRAINT'
    zf=sum((b[0] for b in bins),I(0));zp=sum((b[1] for b in bins),I(0));z=zf+zp
    assert z.lo>0 and core.ham(y).contains(0),'NORM_BACKGROUND'
    fa=I(1);fb=y[-2];aa=power(low[0],4);bb=power(y[0],4)*sq(fb)
    assert bb.lo>0,'ENDPOINT_NONZERO'
    quantities=dict(Z=z,Zf=zf,Zpsi=zp,scalar_norm_share=zf/z,metric_norm_share=zp/z,
        lower_response=aa/z,upper_response=bb/z,equal_response=(aa+bb)/z,
        lower_to_upper_response=aa/bb,f_envelope=enclose(fenv),psi_envelope=enclose(penv),
        separation_overlap=sep,canonical_separation_overlap=sep/sqrtbox(z))
    for j,b in enumerate(bins):quantities['bin_'+str(j)+'_share']=(b[0]+b[1])/z
    out=dict(case=cfg['case'],n=n,representation=rep,mass_box=mu.record(),
        quantities={k:v.record() for k,v in quantities.items()},bins=[[v.record() for v in b] for b in bins],
        lower_background=[v.record() for v in low],upper_state=[v.record() for v in y],
        constraint=core.constraint(y,mu).record() if rep=='full' else None)
    save(cfg['case']+'_'+rep+'_'+str(n)+'.json',out)
    return quantities
def controls():
    core.controls()
    for p in (F(0),F(1,3)):
        y=[I(1),I(0),I(0),I(0),I(p),I(1),I(0)]
        wf,wp,_,_=weights(y,I(0),'full');z=I(F(1,50))*(wf+wp)
        exact=F(1,25)*(1+6*p*p)
        assert z.contains(exact) and (I(1)/z).contains(1/exact)
        bins=[I(F(1,200))*(wf+wp) for _ in range(4)]
        assert core.overlap(sum(bins,I(0)),z)
        sep=-2*I(F(1,50))*I(p);assert sep.contains(-F(1,25)*p)
    for x in (F(0),F(1),F(4),F(1,9),F(2)):
        v=I(x);s=sqrtbox(v)
        assert s.lo*s.lo<=v.lo*S and s.hi*s.hi>=v.hi*S
    for lo,hi in ((-1,2),(-3,-2),(1,3)):
        s=sq(box(lo,hi));v=[F(lo*lo),F(hi*hi)]+([F(0)] if lo<=0<=hi else [])
        assert s.bounds()[0]<=min(v) and max(v)<=s.bounds()[1]
    return dict(inherited=True,constant_norm_and_sensitivity=True,partition=True,square_control=True)
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    exe=Path(sys.executable).resolve();assert sys.version_info[:3]==(3,12,3)
    assert digest(exe)=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    save('CONTROLS.json',controls());results={}
    for name in ('T1R2_SOFT_MODE','T2_STIFF_MODE'):
        runs={}
        for rep in ('reduced','full'):
            for n in (4096,8192):runs[rep,n]=evaluate(HERE.parent/name,n,rep)
            assert all(core.overlap(runs[rep,4096][k],runs[rep,8192][k]) for k in runs[rep,8192]),'LEVEL_OVERLAP'
        assert all(core.overlap(runs['reduced',8192][k],runs['full',8192][k]) for k in runs['full',8192]),'REP_OVERLAP'
        q={k:enclose([runs['reduced',8192][k],runs['full',8192][k]]) for k in runs['full',8192]}
        results[name]={k:v.record() for k,v in q.items()}
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items()),'FINAL_BINDINGS'
    save('RESULT.json',dict(classification='CERTIFIED_MODE_PARTICIPATION',results=results,
        reported_bounds='hull_of_two_fine_representations',all_gates_passed=True))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(exc)));raise
    finally:signal.alarm(0)
