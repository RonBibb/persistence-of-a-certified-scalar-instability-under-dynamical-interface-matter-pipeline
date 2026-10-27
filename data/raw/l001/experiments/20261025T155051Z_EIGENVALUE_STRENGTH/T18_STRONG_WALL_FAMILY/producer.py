import json,sys,math,signal
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import core,dirichlet
from interval import I,S,box,power
save=core.save
CTX={}
def sq(x):
    if x.lo<=0<=x.hi:return I(0,max(x.lo*x.lo,x.hi*x.hi)//S+1)
    return x*x
def sqrtbox(x):
    assert x.lo>=0
    lo=math.isqrt(x.lo*S);hi=math.isqrt(x.hi*S)
    return I(lo,hi+(hi*hi<x.hi*S))
def hull(xs):return I(min(x.lo for x in xs),max(x.hi for x in xs))
def absmax(x):return max(abs(x.lo),abs(x.hi))
def terms(z,mu):
    a,H,P,T,psi,f,g=z
    return [-4*H*g,(-1+12*P*P-mu/(a*a)+2*T*T)*f,
            (12*H*T-4*(1-P+4*P*P*P))*psi]
def evaluate(mu,n,rep):
    low=core.lower(n);a,H,P,T=low
    assert T.hi<0
    ta=box(0,F(1,101));ja=-(1-ta)/2;E=ta*core.bg(low)[3]+ja*T
    assert E.lo>0,'LOWER_COMPACT_DENOMINATOR'
    fa=-3*(mu+12)*ta/(a*a*E);L=3*(mu+12)*ja/(a*a*E)
    y=low+[I(1),fa,L if rep=='L' else L-2*T]
    assert (ta*L+ja*fa).contains(0),'LOWER_WALL'
    fun=(lambda z:core.full(z,mu)) if rep=='L' else (lambda z:dirichlet.fg(z,mu))
    toG=lambda z:z if rep=='g' else z[:6]+[z[6]-2*z[3]*z[4]]
    toL=lambda z:z if rep=='L' else dirichlet.asL(z)
    assert core.constraint(toL(y),mu).contains(0),'INITIAL_CONSTRAINT'
    rates=core.RBG+[I(10),I(1),I(10)];h=F(1,100*n)
    zf=I(0);zp=I(0);sep=I(0);ineg=I(0)
    fs=[];ps=[];gs=[];tts=[[],[],[]];acc=[];center=None
    for j in range(2*n):
        CTX.update(n=n,representation=rep,step=j+1)
        radii=[(I(h)*r).hi for r in rates]
        tube=[v+I(-r,r) for v,r in zip(y,radii)]
        assert all(x.in_exact(*lim) for x,lim in zip(tube[:4],core.LIMITS)),'BACKGROUND_TUBE'
        rhs=fun(tube)
        assert all(b.strict(v+box(0,h)*w) for b,v,w in zip(tube,y,rhs)),'TUBE_CONTAINMENT'
        y=[v+I(h)*w for v,w in zip(y,rhs)]
        assert core.constraint(toL(y),mu).contains(0),'CONSTRAINT'
        z=toG(tube);a,H,P,T,psi,f,g=z
        tt=terms(z,mu)
        for xs,v in zip(tts,tt):xs.append(v)
        acc.append(sum(tt,I(0)));fs.append(f);ps.append(psi);gs.append(g)
        zf=zf+I(h)*2*sq(a)*sq(f);zp=zp+I(h)*12*sq(a)*sq(psi)
        sep=sep-2*I(h)*psi;ineg=ineg+I(h)/sq(a)
        if j+1==n:center=toG(y)
    assert core.ham(y).contains(0),'HAMILTONIAN'
    assert zf.lo>=0 and zp.lo>0
    scalar=box(F(zf.lo,zf.lo+zp.hi),F(zf.hi,zf.hi+zp.lo))
    metric=1-scalar;Z=zf+zp
    eta=3*sq(sep)/(zp*ineg);assert eta.lo<=S,'CS_INCONSISTENCY'
    env=[hull(t) for t in tts];accel=hull(acc);psi=hull(ps)
    G=-accel;D=I(F(1,50))
    centerpsi=center[4]
    # Dirichlet comparison conditional on strict concavity; do not force its outcome.
    yu=toL(y)
    tb=box(0,F(1,101));Ub=core.bg(yu)[3]
    assert yu[3].lo>0 and Ub.lo>0,'UPPER_BACKGROUND_SIGNS'
    Eb=tb*Ub+(1-tb)*yu[3]/2
    assert Eb.lo>0,'UPPER_COMPACT_DENOMINATOR'
    quantities=dict(Z=Z,Zf=zf,Zpsi=zp,scalar_norm_share=scalar,metric_norm_share=metric,
        separation_overlap=sep,canonical_separation_overlap=sep/sqrtbox(Z),
        separation_efficiency_raw=eta,separation_efficiency=I(eta.lo,min(S,eta.hi)),
        f_envelope=hull(fs),psi_envelope=psi,g_envelope=hull(gs),f_second_derivative=accel,
        drag_term=env[0],scalar_term=env[1],metric_forcing_term=env[2],
        center_psi=centerpsi,center_f=center[5],lower_f=fa,upper_f=yu[-2])
    record=dict(n=n,representation=rep,quantities={k:v.record() for k,v in quantities.items()},
        upper_state=[v.record() for v in yu],center_state=[v.record() for v in center],
        constraint=core.constraint(yu,mu).record())
    save(rep+'_'+str(n)+'.json',record)
    return quantities
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'BINDINGS'
    assert sys.version_info[:3]==(3,12,3)
    assert core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    controls=dirichlet.controls()
    D=I(F(1,50));psi=I(1);zf=I(1);zp=I(6)
    assert (3*sq(-2*D*psi)/(12*D*sq(psi)*D)).contains(1),'CONSTANT_CS'
    assert (I(4)*D*D/(24*psi)).contains(F(1,15000)),'PARABOLIC_GAP_CONTROL'
    controls.update(constant_coherence=True,parabolic_gap=True)
    save('CONTROLS.json',controls)
    dd=json.loads((HERE.parent/'T12_DIRICHLET_CEILING/RESULT.json').read_text())['physical_mu_bracket']
    finite=json.loads((HERE.parent/'T15_COMPACT_WALL_COMPARISON/RESULT.json').read_text())['results']['equal_100']['physical_mu_bracket']
    mu=box(F(finite['lo']),F(dd['hi']));assert mu.hi<-12*S
    runs={}
    for rep in ('L','g'):
        for n in (4096,8192):runs[rep,n]=evaluate(mu,n,rep)
        assert runs[rep,4096].keys()==runs[rep,8192].keys(),'QUANTITY_SET'
        assert all(core.overlap(runs[rep,4096][k],runs[rep,8192][k]) for k in runs[rep,8192]),'LEVEL_OVERLAP'
    assert runs['L',8192].keys()==runs['g',8192].keys(),'REP_QUANTITY_SET'
    assert all(core.overlap(runs['L',8192][k],runs['g',8192][k]) for k in runs['g',8192]),'REP_OVERLAP'
    q={k:hull([runs['L',8192][k],runs['g',8192][k]]) for k in runs['g',8192]}
    concave=q['f_second_derivative'].hi<0;positive=q['psi_envelope'].lo>0
    forcing=q['metric_forcing_term']
    dominates=forcing.hi<0 and -forcing.hi>absmax(q['drag_term'])+absmax(q['scalar_term'])
    consequences=dict(psi_positive_everywhere=positive,scalar_strictly_concave_everywhere=concave,
        scalar_positive_interior_from_nonnegative_endpoints=concave and positive,metric_forcing_dominates=dominates,
        center_constraint_explains_negative_lambda=concave and positive)
    lower_bounds={}
    if concave and positive:
        Gmin=F(-q['f_second_derivative'].hi,S);D=F(1,50)
        zfloor=F(81,100)*Gmin*Gmin*D**5/60
        sharefloor=zfloor/F(q['Z'].hi,S)
        gapfloor=Gmin*D*D/(24*F(q['center_psi'].hi,S))
        assert 0<zfloor<=F(q['Zf'].hi,S),'SCALAR_FLOOR_INCONSISTENCY'
        assert gapfloor<=F((-mu-12).hi,S),'GAP_LOWER_INCONSISTENCY'
        lower_bounds=dict(scalar_norm=str(zfloor),scalar_norm_share=str(sharefloor),negative_lambda_gap=str(gapfloor))
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items()),'FINAL_BINDINGS'
    save('RESULT.json',dict(classification='CERTIFIED_STRONG_WALL_FAMILY_PROFILE_ENCLOSURE',
        quantities={k:v.record() for k,v in q.items()},consequences=consequences,
        mass_domain=mu.record(),compact_wall_domain=['0','1/101'],all_actual_roots_covered_by_monotonicity=True,
        actual_root_lower_bounds=lower_bounds,lower_bounds_are_not_observable_enclosures=True,
        all_gates_passed=True,structural_explanation_not_independent_mass_exclusion=True))
if __name__=='__main__':
    def timeout(s,f):raise TimeoutError('590s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(590)
    try:main()
    except BaseException as exc:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',context=CTX,error=repr(exc)));raise
    finally:signal.alarm(0)
