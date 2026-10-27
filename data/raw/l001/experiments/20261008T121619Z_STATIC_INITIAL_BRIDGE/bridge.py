"""Saved-data static bridge only. No experiment imports, IVPs, or evolution."""
from pathlib import Path
from datetime import datetime, timezone
from fractions import Fraction
from math import comb, factorial
import argparse, bisect, hashlib, json, os, resource, signal, time

ROOT=Path(__file__).resolve().parent
def read(p): return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def local(p): return Path(str(p).replace('/Users/ronbibb/','/media/psf/Home/',1)) if os.uname().sysname=='Linux' else Path(p)
def write(name,obj):
    p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True)
    t=p.with_name(p.name+'.partial')
    with t.open('w') as f:
        json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444)
    os.replace(t,p)
def status(phase,**kw):write('STATUS.json',{'utc':now(),'phase':phase,'pid':os.getpid(),**kw})
def guard():
    b=read(ROOT/'BINDINGS.json')
    for x in b['inputs']: assert sha(local(x['path']))==x['sha256'],x['id']
    for x in b['sources']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
    return b,{x['id']:local(x['path']) for x in b['inputs']}
def exact(x):return Fraction(str(x))
def rational_shape(D,j,side):
    a=[Fraction(0)]*(2*j+2)
    if side==0:
        for r in range(j+2):a[j+r]=Fraction(comb(j+1,r)*(-1)**r,factorial(j))/D**r
    else:
        for r in range(j+1):a[j+1+r]=Fraction(comb(j,r),factorial(j))*(-D)**(j-r)/D**(j+1)
    return a
def preflight(paths):
    import sympy as sp
    A,B,l,sig=sp.symbols('A B l sig',real=True)
    dx=sp.exp(l-B)
    controls={'metric_pullback':sp.simplify(sp.exp(2*B)*dx**2-sp.exp(2*l))==0,
      'oriented_normal':sp.simplify(-sig*sp.exp(-B)/dx+sig*sp.exp(-l))==0,
      'proper_length':sp.simplify(sp.exp(B)*dx-sp.exp(l))==0}
    D=Fraction(2)
    for j in (5,7):
        for side in (0,1):
            a=rational_shape(D,j,side)
            for endpoint in (0,1):
                for d in range(j+1):
                    # Exact Hermite construction controls, independent of C6 coefficients.
                    want=int(endpoint==side and d==j)
                    got=sum((v*Fraction(factorial(n),factorial(n-d))*(endpoint*D)**(n-d)
                             for n,v in enumerate(a) if n>=d),Fraction(0))
                    controls[f'H{j}_{side}_endpoint{endpoint}_d{d}']=got==want
    a=read(paths['static_binding'])['model_exact'];b=read(paths['native_binding'])['model_exact']
    controls['six_exact_action_literals']=set(a)==set(b) and all(exact(a[k])==exact(b[k]) for k in a)
    controls['C4_authority']=read(paths['C4_result'])['classification']=='CONNECTED_SIGNED_C4_BRANCH_CERTIFIED'
    controls['C6_authority']=read(paths['C6_result'])['classification']=='NEW_PHYSICAL_C6_MEMBER_NUMERICALLY_ADMITTED'
    controls['E01_authority']=read(paths['E01'])['classification']=='COMPARISON_ONLY_REFINEMENT_USEFUL_BOTH_SIGNS'
    out={'utc':now(),'checks':controls,'all_passed':all(controls.values()),'new_scientific_outcomes_used':False}
    write('PREFLIGHT.json',out);assert out['all_passed']

def analyze_level(dps,paths,binding):
    import mpmath as mp
    from flint import arb,fmpq,ctx
    mp.mp.dps=dps;ctx.prec=384
    started=time.monotonic()
    def m(x):
        if isinstance(x,Fraction):return mp.mpf(x.numerator)/x.denominator
        return mp.mpf(str(x))
    def r(x):return fmpq(str(exact(x)))
    def ar(x):return arb(r(x))
    def out(x):return mp.nstr(x,dps+5)
    def bounds(x):return x.lower().fmpq(),x.upper().fmpq()
    def record(x):
        a,b=bounds(x);return {'exact':[str(a),str(b)],'decimal':[float(a),float(b)]}
    def interval(a,b):return arb((a+b)/2,(b-a)/2)
    def horner(a,z):
        v=z*0
        for c in reversed(a):v=v*z+c
        return v
    def shift(a,z,n):
        return [sum((a[j]*comb(j,d)*z**(j-d) for j in range(d,len(a))),z*0) for d in range(n+1)]
    def exp_series(c):
        e=[mp.exp(c[0])]
        for n in range(1,len(c)):e.append(mp.fsum(j*c[j]*e[n-j] for j in range(1,n+1))/n)
        return e
    seed=read(paths['seed']);dense=read(paths[f'dense{dps}']);candidate=read(paths[f'candidate{dps}'])
    D=m(seed['D']);Df=r(seed['D']);cells=len(dense['segments']);n=len(dense['segments'][0][0])-1
    h=D/cells;hf=Df/cells;eps=m(dense['epsilon']);epsa=ar(dense['epsilon']);oldcells=seed['cells']
    q=list(map(m,candidate['q']));qa=list(map(ar,candidate['q']));corr=list(map(m,dense['correction']))
    roots=[[[m(v) for v in row] for row in cell] for cell in seed['segments']]
    nodes,weights=mp.gauss_quadrature(16,'legendre')
    Xq=mp.mpf(0);Lq=mp.mpf(0);XI=arb(0);LI=arb(0);Jlo=None;Jhi=None
    polys=[];xpoly=[];knots=[mp.mpf(0)]
    for i,block in enumerate(dense['segments']):
        parent=i*oldcells//cells;sf=Df*i/cells;offset=sf-Df*parent/oldcells;s=m(Fraction(str(sf)));z=m(Fraction(str(offset)))
        A=list(map(m,block[0]));ell=[-2*eps*v for v in shift(roots[parent][5],z,n)]
        Q=shift(q,s,n);B=[a+c for a,c in zip(A,Q)]
        F=[v+eps*w+c for v,w,c in zip(shift(roots[parent][2],z,n),shift(roots[parent][6],z,n),shift(corr,s,n))]
        W=shift(roots[parent][0],z,n);polys.append([A,B,F,ell,W])
        c=[a-b for a,b in zip(ell,B)];exp=exp_series(c)
        integral=[mp.mpf(0)]+[v/(j+1) for j,v in enumerate(exp)]
        xpoly.append(integral);knots.append(knots[-1]+horner(integral,h))
        Xq+=h/2*mp.fsum(weights[j]*mp.exp(horner(c,h*(nodes[j]+1)/2)) for j in range(16))
        Lq+=h/2*mp.fsum(weights[j]*mp.exp(horner(ell,h*(nodes[j]+1)/2)) for j in range(16))
        # Every coefficient below starts from its exact serialized decimal.
        aa=list(map(ar,block[0]));ea=[-2*epsa*v for v in shift(list(map(ar,seed['segments'][parent][5])),arb(offset),n)]
        qq=shift(qa,arb(sf),n);arg=[e-a-v for e,a,v in zip(ea,aa,qq)];domain=interval(fmpq(0),hf)
        ji=horner(arg,domain).exp();li=horner(ea,domain).exp();jl,jh=bounds(ji)
        Jlo=jl if Jlo is None else min(Jlo,jl);Jhi=jh if Jhi is None else max(Jhi,jh)
        XI+=arb(hf)*ji;LI+=arb(hf)*li
        if i%64==0:status('MAP',dps=dps,completed_cells=i,cells=cells,checkpoint_interval='completed precision level')
    X=knots[-1];samples=[];inverse_error=mp.mpf(0);metric_error=mp.mpf(0)
    for label in range(65):
        x=X*label/64;i=max(0,min(bisect.bisect_right(knots,x)-1,cells-1));target=x-knots[i]
        c=xpoly[i];dc=[j*c[j] for j in range(1,len(c))];z=h*target/(knots[i+1]-knots[i])
        for _ in range(30):
            error=horner(c,z)-target;step=error/horner(dc,z);z-=step
            if abs(step)<mp.mpf('1e-60'):break
        inverse_error=max(inverse_error,abs(horner(c,z)-target))
        vals=[horner(p,z) for p in polys[i]];A,B,F,ell,W=vals
        metric_error=max(metric_error,abs(mp.exp(B-ell)*horner(dc,z)-1))
        samples.append({'label':label,'normalized_x':out(mp.mpf(label)/64),'s':out(i*h+z),
          'A':out(A),'B':out(B),'Phi':out(F),'ell':out(ell),'R':out(mp.exp(A)/mp.sqrt(m(seed['k']))),
          'normalized_clock_rate':out(mp.exp(B-W))})
    par={k:m(exact(v)) for k,v in read(paths['native_binding'])['model_exact'].items()}
    walls=[];wallmax=mp.mpf(0);qmax=mp.mpf(0)
    for side in (0,1):
        i=0 if side==0 else cells-1;z=mp.mpf(0) if side==0 else h
        vals=[horner(p,z) for p in polys[i]];ders=[horner([j*p[j] for j in range(1,len(p))],z) for p in polys[i]]
        A,B,F,ell,W=vals;Ad,Bd,Fd,_,_=ders;sig=1-2*side;v=par['v0' if side==0 else 'v1'];lam=par['lambda_a' if side==0 else 'lambda_b']
        U=lam+par['gamma']*(F-v)**2/2;Up=par['gamma']*(F-v)
        rows=[mp.exp(-ell)*Ad+sig*U/6,mp.exp(-ell)*Bd+sig*U/6,mp.exp(-ell)*Fd-sig*Up/2]
        wallmax=max(wallmax,*map(abs,rows));qmax=max(qmax,abs(B-A),abs(Bd-Ad))
        walls.append({'side':side,'sigma':sig,'spatial_rows':list(map(out,rows)),
          'q':out(B-A),'q_s':out(Bd-Ad),'A':out(A),'Phi':out(F),'R':out(mp.exp(A)/mp.sqrt(m(seed['k']))),
          'normalized_clock_rate':out(mp.exp(B-W))})
    xb=bounds(XI);lb=bounds(LI);quaderr=abs(X-Xq)
    checks={'positive_represented_Jacobian':Jlo>0,'X_inside_interval':m(Fraction(str(xb[0])))<=Xq<=m(Fraction(str(xb[1]))),
      'L_inside_interval':m(Fraction(str(lb[0])))<=Lq<=m(Fraction(str(lb[1]))),
      'Taylor_vs_Gauss16':quaderr<=mp.mpf('1e-20'),'inverse_roundtrip':inverse_error<=mp.mpf('1e-20'),
      'metric_pullback_at_diagnostic_nodes':metric_error<=mp.mpf('1e-20'),
      'original_spatial_wall_rows':wallmax<=mp.mpf('1e-20'),'wall_lapse_identity':qmax<=mp.mpf('1e-20')}
    outp={'dps':dps,'cells':cells,'polynomial_degree':n,'seconds':time.monotonic()-started,
      'X_Taylor':out(X),'X_Gauss16':out(Xq),'proper_distance_Gauss16':out(Lq),
      'X_interval':record(XI),'proper_distance_interval':record(LI),'Jacobian_lower_exact':str(Jlo),
      'Jacobian_upper_exact':str(Jhi),'Jacobian_lower_decimal':float(Jlo),
      'errors':{'quadrature':out(quaderr),'inverse':out(inverse_error),'metric':out(metric_error),'walls':out(wallmax),'q_walls':out(qmax)},
      'samples':samples,'walls':walls,'checks':checks,'all_passed':all(checks.values()),
      'binding_sha256':binding,'scope':'Outward enclosures of exact saved polynomial representation; not continuum C6 error bounds.'}
    write(f'CHECKPOINT_p{dps}.json',outp);assert outp['all_passed'],outp['errors']
    return outp

def membership_and_bounds(paths):
    from flint import arb,fmpq,ctx
    ctx.prec=384
    def ar(x):return arb(fmpq(str(exact(x))))
    def bnd(x):return x.lower().fmpq(),x.upper().fmpq()
    def record(x):
        a,b=bnd(x);return {'exact':[str(a),str(b)],'decimal':[float(a),float(b)]}
    seed=read(paths['seed']);D=exact(seed['D']);old=read(paths['old_dense']);c=read(paths['candidate100']);dense=read(paths['dense100'])
    delta=list(map(exact,c['delta_c5_c7']));shapes=[rational_shape(D,j,s) for j,s in ((5,0),(5,1),(7,0),(7,1))]
    change=[sum((delta[i]*(shapes[i][j] if j<len(shapes[i]) else 0) for i in range(4)),Fraction(0)) for j in range(16)]
    target=change[15];actual=exact(dense['correction'][15])
    coerrors=[abs(exact(dense['correction'][j])-(exact(old['correction'][j]) if j<len(old['correction']) else 0)-change[j]) for j in range(16)]
    midpoint=sum((a*(D/2)**j for j,a in enumerate(change)),Fraction(0))
    exactw={'degree15_nonzero':actual!=0,'seventh_shape_sum_nonzero':delta[2]+delta[3]!=0,
      'coefficient_identity_within_1e40':max(coerrors)<=Fraction(1,10**40),
      'common_proper_distance_midpoint_nonzero':midpoint!=0,
      'saved_epsilon_in_original_amplitude_interval':-Fraction(1,200000)<=exact(dense['epsilon'])<=Fraction(1,200000)}
    E=read(paths['E01'])['material']['positive']['fields'];P=read(paths['P01'])['neighborhood']
    EA=ar(E['A']['bound_exact']);EL=ar(E['ell']['bound_exact']);k=ar(seed['k'])
    kl,kh=map(fmpq,P['curvature']['exact_bounds']);dl,dh=map(fmpq,P['event_bracket_exact'])
    EK=max(abs((arb(kl)/k).log()).upper().fmpq(),abs((arb(kh)/k).log()).upper().fmpq())
    ED=max(abs((arb(dl)/ar(D)).log()).upper().fmpq(),abs((arb(dh)/ar(D)).log()).upper().fmpq())
    return {'checks':exactw,'all_passed':all(exactw.values()),'degree15_exact_saved':str(actual),
      'degree15_from_H7':str(target),'coefficient_reconstruction_max_exact':str(max(coerrors)),
      'delta_Phi_at_common_material_midpoint_exact':str(midpoint),'delta_Phi_midpoint_decimal':float(midpoint),
      'C4_fixed_saved_source_ansatz_membership':'EXCLUDED_BY_NONZERO_DEGREE_15_CORRECTION',
      'continuum_C6_family_membership':'NOT_CERTIFIED_BY_THE_IMPORTED_C4_THEOREM',
      'saved_epsilon_minus_target':str(exact(dense['epsilon'])-Fraction(1,200000)),
      'old_saved_epsilon_minus_target':str(exact(old['epsilon'])-Fraction(1,200000)),
      'C4_only_transfer':{'EA':record(EA),'Eell':record(EL),
        'radius_relative_bound':record((EA+arb(EK)/2).exp()-1),
        'lower_clock_relative_bound':record(EA.exp()-1),
        'proper_distance_relative_bound':record((arb(ED)+EL).exp()-1),
        'source_of_D_k':'Conservative P01 neighborhood enclosures containing the same central background; action not changed.',
        'applies_to_C6':False,'rigorous_q_error_bound':None,'rigorous_inverse_map_error_bound':None,
        'missing':'Validated physical C6 family and high-jet/lapse error propagation; observed 80/100 agreement is not that bound.'}}

def main():
    assert os.uname().sysname=='Linux' and os.sched_getaffinity(0)=={4}
    assert all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'))
    assert not (ROOT/'RESULT.json').exists()
    started=time.monotonic();cutoff=datetime.fromisoformat('2026-10-08T13:16:19+00:00').timestamp();remaining=cutoff-time.time();assert remaining>0
    resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
    def timeout(*_):raise TimeoutError('Shared Lin absolute deadline; no reset')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,remaining)
    b,paths=guard();binding=sha(ROOT/'BINDINGS.json');status('PREFLIGHT',cutoff_utc='2026-10-08T13:16:19Z')
    import sys,mpmath,flint,sympy
    assert flint.__version__=='0.9.0' and mpmath.__version__=='1.3.0' and sympy.__version__=='1.14.0'
    write('RUNTIME.json',{'utc':now(),'python':sys.version,'executable':sys.executable,
      'modules':{m.__name__:{'version':m.__version__,'path':m.__file__,'sha256':sha(m.__file__)} for m in (mpmath,flint,sympy)},
      'cpu_affinity':sorted(os.sched_getaffinity(0)),'address_space_limit':4*1024**3,
      'deadline_utc':'2026-10-08T13:16:19Z','output_root':str(ROOT)})
    preflight(paths);levels=[]
    for dps in (80,100):
        p=ROOT/f'CHECKPOINT_p{dps}.json'
        if p.exists():
            r=read(p);assert r['binding_sha256']==binding and r['all_passed']
        else:r=analyze_level(dps,paths,binding)
        levels.append(r)
    import mpmath as mp
    mp.mp.dps=110
    paired={k:str(abs(mp.mpf(levels[0][k])-mp.mpf(levels[1][k]))) for k in ('X_Taylor','proper_distance_Gauss16')}
    paired['sample_fields']=str(max(abs(mp.mpf(a[k])-mp.mpf(c[k])) for a,c in zip(levels[0]['samples'],levels[1]['samples']) for k in ('s','A','B','Phi','ell','R','normalized_clock_rate')))
    assert all(mp.mpf(v)<=mp.mpf('1e-20') for v in paired.values()),paired
    structural=membership_and_bounds(paths);assert structural['all_passed']
    guard()
    result={'utc':now(),'classification':'STATIC_INITIAL_BRIDGE_INCOMPLETE',
      'positive_result':'Explicit action-consistent initial coordinate/normal/clock map passes saved-representation checks.',
      'controlling_gap':'The imported C4 family has no independent physical H7 directions; exact C6 family and lapse/inverse continuum error bounds are absent.',
      'paired':paired,'membership_and_bounds':structural,'levels':[{'dps':l['dps'],'checks':l['checks'],'seconds':l['seconds']} for l in levels],
      'all_local_checks_passed':True,'binding_sha256':binding,'runtime_seconds':time.monotonic()-started,
      'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'cpu_affinity':sorted(os.sched_getaffinity(0)),
      'evolution_steps':0,'new_root_solves':0,'new_metric_solves':0,'successor_launched':False,
      'claim_boundary':'Not a continuum C6 exclusion, no-go for integration, evolution admission, P16 identification, horizon or child-universe result.'}
    write('RESULT.json',result);status('LOCAL_CHECKS_COMPLETE',classification=result['classification'],running=False)
    signal.setitimer(signal.ITIMER_REAL,0);print(json.dumps({k:v for k,v in result.items() if k not in ('membership_and_bounds','levels')}),flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:
        write('FAILURE.json',{'utc':now(),'error':repr(e),'classification':'STATIC_INITIAL_BRIDGE_INCOMPLETE','scientific_negative':False})
        status('FAILED_CLOSED',running=False);raise
