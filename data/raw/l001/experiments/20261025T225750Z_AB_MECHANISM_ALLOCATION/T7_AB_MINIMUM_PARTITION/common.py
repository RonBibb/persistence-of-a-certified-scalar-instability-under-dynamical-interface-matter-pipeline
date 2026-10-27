"""One frozen selected-neutral-oscillator characteristic and participation test.

No computational work at import; Linux-only under external lease wrapper.
The two copied bulk engines are unchanged. Only physical mode launch and
boundary evaluation adapt the manuscript's selected oscillator action.
"""
import hashlib, importlib.util, json, os, platform, signal, sys, time, traceback
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'

def need(x,why):
    if not x: raise RuntimeError(why)
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def put(name,obj):
    path=OUT/name; need(not path.exists(),'REFUSE_OVERWRITE:'+name)
    tmp=path.with_suffix(path.suffix+'.tmp'); need(not tmp.exists(),'STALE_STAGING:'+name)
    with tmp.open('x') as f: json.dump(obj,f,indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    os.link(tmp,path); tmp.unlink()
def pack(v):
    return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def sign(v): return 1 if v.lower()>0 else -1 if v.upper()<0 else 0
def overlaps(a,b): return a.lower()<=b.upper() and b.lower()<=a.upper()
def contains0(v): return v.lower()<=0<=v.upper()

def authenticate():
    need(sys.platform=='linux','LINUX_ONLY')
    gate=read(ROOT/'ADMISSION.json'); need(gate.get('admitted') is True,'ADMISSION')
    for rel,digest in gate['sources'].items(): need(sha(ROOT/rel)==digest,'SOURCE_HASH:'+rel)
    rt=read(ROOT/'RUNTIME_BINDINGS.json')
    need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,digest in rt['files'].items(): need(sha(path)==digest,'RUNTIME_HASH:'+path)
    need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')
    sys.path.insert(0,rt['flint_path'])
    import flint
    need(flint.__version__==rt['flint_version'],'FLINT_VERSION')
    flint.ctx.prec=768; flint.ctx.threads=1
    return flint

def load(name):
    s=importlib.util.spec_from_file_location('selected_'+name,ROOT/'engine'/f'{name}_interval.py')
    m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m

def physical(y,name):
    if name=='primary':
        W,H,P,T,E,psi,f,g=y
    else:
        W,H,P,T,psi,f,g=y; E=(-W).exp()
    return W,H,P,T,E,psi,f,g

def response(mu,E,beta):
    # omega²=eta=1; beta=0 supplies exact pure-potential control.
    d=1+beta-mu*E*E; need(d.lower()>0,'OSCILLATOR_DENOMINATOR')
    return 20+beta-beta*beta/d,d

def launch(m,name,A,mu,model,beta):
    from flint import arb
    y,p=m.initial(A,mu,model)
    W,H,P,T,E,psi,oldf,oldg=physical(y,name)
    G,d=response(mu,E,beta); B=G*T/2-(p['m2']*P-4*H*T)
    need(not contains0(B),'LOWER_LAUNCH_DENOMINATOR')
    f=3*(mu+4*p['k'])*E*E/B; g=G*f/2-2*T
    if name=='primary': y[6:8]=[f,g]
    else: y[5:7]=[f,g]
    u=beta*f/d
    need(contains0(2*(g+2*T)-(20+beta)*f+beta*u),'LOWER_UNDIVIDED_WALL')
    need(contains0(d*u-beta*f),'LOWER_OSCILLATOR_ROW')
    need(contains0(m.constraint(y,p)),'LOWER_CONSTRAINT')
    if beta==0:
        need(overlaps(f,oldf) and overlaps(g,oldg),'BASELINE_LAUNCH_REDUCTION')
    return y,p,u

def square(m,x):
    from flint import fmpq
    lo,hi=m.bounds(x)
    return m.interval(fmpq(0) if lo<=0<=hi else min(lo*lo,hi*hi),max(lo*lo,hi*hi))

def densities(m,y,name):
    W,H,P,T,E,psi,f,g=physical(y,name); a2=(2*W).exp()
    psi2=square(m,psi); f2=square(m,f)
    return {'Ipsi':psi,'Ipsi2':psi2,'Ig':a2*psi2,'Is':a2*f2,'Iinv':E*E}

def integral_piece(m,density,mandatory,optional):
    from flint import fmpq
    return density*mandatory+density*m.interval(fmpq(0),optional)

def dyadic_export(m,value):
    """Outward exact dyadic budget; only executed on admitted Linux runtime."""
    from flint import fmpq
    lo,hi=map(lambda x:Q(str(x)),m.bounds(value)); scale=1<<80
    low=(lo*scale).__floor__(); high=(hi*scale).__ceil__()
    qlo,qhi=Q(low,scale),Q(high,scale)
    need(qlo<=lo<=hi<=qhi,'DYADIC_EXPORT_CONTAINMENT')
    raw={'exact_bounds':[str(qlo),str(qhi)]}
    # Reimport the saved interval, not the original narrower Arb value.
    return raw,m.interval(fmpq(str(qlo)),fmpq(str(qhi)))

def semantic_controls(m):
    from flint import arb,fmpq
    # Exact constant warp a=2, psi=3, interval D=[2,3].
    tail=integral_piece(m,arb(3),fmpq(2),fmpq(1))
    need(tail.contains(6) and tail.contains(9),'CONSTANT_TAIL')
    neg=integral_piece(m,arb(-3),fmpq(2),fmpq(1))
    need(neg.contains(-9) and neg.contains(-6),'SIGNED_TAIL')
    I=arb(6); D=arb(2); Ip2=arb(18); Ig=arb(72); Iinv=arb('0.5')
    C=I*I/(D*Ip2); ew=I*I/(Iinv*Ig)
    Zg=12*Ig; Zext=Zg+arb(7); K=4*I*I/Zext
    identity=Iinv/3*(Zg/Zext)*ew
    need(C.contains(1) and ew.contains(1) and overlaps(K,identity),'COHERENCE_AND_IDENTITY')
    # Piecewise +1,-1 over equal halves has cancellation, not coherence1.
    zero=integral_piece(m,arb(1),fmpq(1),fmpq(0))+integral_piece(m,arb(-1),fmpq(1),fmpq(0))
    need(zero.is_zero(),'SIGN_CHANGING_CONTROL')
    test=m.interval(fmpq(-1),fmpq(2)); sqtest=square(m,test)
    tl,th=m.bounds(test); sl,sh=m.bounds(sqtest)
    need(sl<=0 and sh>=max(tl*tl,th*th),'CROSS_ZERO_SQUARE_RANGE_CONTAINMENT')
    coarse,_=dyadic_export(m,m.interval(fmpq(-1,3),fmpq(2,7)))
    qlo,qhi=map(Q,coarse['exact_bounds'])
    need(qlo<=Q(-1,3) and qhi>=Q(2,7),'DYADIC_MANUFACTURED_CONTAINMENT')
    # Raw versus shifted oscillator mass must be distinguishable.
    mu=arb('-0.001'); E=arb(2); k=arb('0.0003')
    raw=response(mu,E,1)[1]; wrong=response(mu+4*k,E,1)[1]
    need(not overlaps(raw,wrong),'SHIFTED_MASS_MUTATION_NOT_DETECTED')
    need(m.algebra_controls()['pass'],'INHERITED_ENGINE_CONTROLS')
    return {'constant_and_signed_uncertain_tail':True,'constant_warp_coherence':True,
            'weighted_identity':True,'sign_changing_overlap':True,'positive_square':True,
            'shifted_mass_mutation_rejected':True,'dyadic_coarsening_containment':True,'inherited_engine_controls':True}

def flow(name,mu_bounds,beta,label,budget_started,integrals=False):
    from flint import arb,fmpq
    m=load(name); binding=read(ROOT/'inputs/central_bindings.json'); cfg=binding['config']
    A=m.interval(*map(fmpq,cfg['A'])); Dlo,Dhi=map(fmpq,cfg['D'])
    mu=m.interval(*map(fmpq,mu_bounds)); y,p,ua=launch(m,name,A,mu,binding['model_exact'],beta)
    Wa,Ha,Pa,Ta,Ea,psia,fa,ga=physical(y,name); Ga,da=response(mu,Ea,beta)
    lower_event={'a_squared':pack((2*Wa).exp()),'f':pack(fa),'psi':pack(psia),'u':pack(ua),'Gamma':pack(Ga),'d':pack(da)}
    need(p['k'].lower()>0 and (mu+4*p['k']).upper()<0,'GENERIC_SHIFTED_NEGATIVE_SECTOR')
    h=fmpq(2,8192 if name=='primary' else 16384)
    n=(Q(str(Dhi))/Q(str(h))).__ceil__(); started=time.monotonic()
    sums={key:arb(0) for key in ('Ipsi','Ipsi2','Ig','Is','Iinv')}
    endpoints={}; covers=[]; psi_hull=None; maxpic=0; budget_rows=[]
    for j in range(n):
        if j%64==0:
            need(time.monotonic()-started<180,'FLOW_TIME_CAP')
            need(time.monotonic()-budget_started<1800,'PRODUCTION_TIME_CAP')
        s=j*h; y,cell=m.step(y,h,p); geo=m.geometry(cell,p)
        need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FLOW')
        need(contains0(geo['constraint']) and contains0(geo['first_integral']),'CONSTRAINT_OR_BACKGROUND')
        need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY')
        maxpic=max(maxpic,cell['picard_iterations'])
        psi_hull=geo['psi'] if psi_hull is None else m.hull(psi_hull,geo['psi'])
        if integrals:
            mandatory=max(fmpq(0),min(h,Dlo-s)); upto=max(fmpq(0),min(h,Dhi-s)); optional=upto-mandatory
            need(optional>=0,'TAIL_PARTITION')
            contributions={}
            for key,dens in densities(m,cell['box'],name).items():
                exported,reimported=dyadic_export(m,integral_piece(m,dens,mandatory,optional))
                contributions[key]=exported; sums[key]+=reimported
            budget_rows.append({'index':j,'s':str(s),'step':str(h),'mandatory':str(mandatory),
                                'optional':str(optional),'contributions':contributions})
        if s+h>=Dlo and s<=Dhi:
            lo=max(fmpq(0),Dlo-s); hi=min(h,Dhi-s); z=m.range_on_cell(cell,lo,hi)
            W,H,P,T,E,psi,f,g=physical(z,name); G,d=response(mu,E,beta); u=beta*f/d
            det=g+2*T*psi+G*f/2
            undiv=2*(g+2*T*psi)+(20+beta)*f-beta*u
            need(overlaps(undiv,2*det) and contains0(d*u-beta*f),'UPPER_UNDIVIDED_CONSISTENCY')
            vals={'determinant':det,'a_squared_b':(2*W).exp(),'psi_b':psi,'f_b':f,'u_b':u,'wall_b':(2*W).exp()*square(m,u),'Gamma_b':G,'d_b':d}
            for key,v in vals.items(): endpoints[key]=v if key not in endpoints else m.hull(endpoints[key],v)
            covers.append({'lo':str(s+lo),'hi':str(s+hi)})
    last=str(Dlo)
    for row in covers: need(Q(row['lo'])==Q(last),'EVENT_GAP'); last=row['hi']
    need(Q(last)==Q(str(Dhi)),'EVENT_END')
    result={'label':label,'engine':name,'beta':beta,'mu_bounds':list(mu_bounds),'cells':n,
            'event_cover':covers,'event':{k:pack(v) for k,v in endpoints.items()},'lower_event':lower_event,'K':pack(p['k']),
            'psi_whole_collar':pack(psi_hull),'max_picard_iterations':maxpic,
            'all_cell_checks_pass':True,'seconds':time.monotonic()-started}
    if integrals:
        budget_name=label+'_'+name+'_INTEGRAL_BUDGET.json'
        put(budget_name,{'engine':name,'mu_bounds':list(mu_bounds),'D_bounds':list(cfg['D']),
                        'dyadic_denominator_power':80,'cells':budget_rows,
                        'reported_sums':{k:pack(v) for k,v in sums.items()},
                        'premise':'Contributions enclose whole-cell Picard boxes from inherited outward Arb engines; saved dyadic sums do not independently recertify those boxes.'})
        result['integral_budget']={'path':budget_name,'sha256':sha(OUT/budget_name),'cells':len(budget_rows)}
        need(contains0(endpoints['determinant']),'ROOT_STRIP_DETERMINANT')
        Zg=12*sums['Ig']; Zs=2*sums['Is']; Zw=square(m,ua)+endpoints['wall_b']; Z=Zg+Zs+Zw
        need(Z.lower()>0 and sums['Ipsi2'].lower()>0 and sums['Ig'].lower()>0 and sums['Iinv'].lower()>0,'POSITIVE_INTEGRALS')
        D=m.interval(Dlo,Dhi); I=sums['Ipsi']; delta=-2*I
        Ksep=4*square(m,I)/Z; ew=square(m,I)/(sums['Iinv']*sums['Ig'])
        identity=sums['Iinv']/3*(Zg/Z)*ew
        need(overlaps(Ksep,identity),'WEIGHTED_IDENTITY_ENCLOSURES')
        obs={'deltaD_over_Q':delta,'Zg':Zg,'Zs':Zs,'Zw':Zw,'Zext':Z,
             'metric_fraction':Zg/Z,'scalar_fraction':Zs/Z,'oscillator_fraction':Zw/Z,
             'coherence_unweighted':square(m,I)/(D*sums['Ipsi2']),
             'coherence_weighted':ew,'Ksep':Ksep,'Ksep_factorized':identity}
        if not contains0(delta):
            obs.update(lower_radius_to_fractional_separation=D/delta,
                       upper_radius_to_fractional_separation=endpoints['psi_b']*D/delta)
        for k,v in sums.items(): obs[k]=v
        result['observables']={k:pack(v) for k,v in obs.items()}
        result['analytic_coherence_bounds']=[0,1]
        result['separation_nonzero']=not contains0(delta)
    put(label+'_'+name+'.json',result)
    print(json.dumps({'completed':label,'engine':name,'seconds':result['seconds']}),flush=True)
    return result

def ball_record(m,r):
    from flint import fmpq
    return m.interval(*map(fmpq,r['exact_bounds']))

def main():
    OUT.mkdir(exist_ok=True); need(not any((OUT/x).exists() for x in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic(); history=[]
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('HARD_PRODUCER_CAP_1800_SECONDS')))
        signal.alarm(1800)
        authenticate(); put('STARTED.json',{'utc':now(),'pid':os.getpid(),'admission_sha256':sha(ROOT/'ADMISSION.json')})
        controls={name:semantic_controls(load(name)) for name in ('primary','independent')}; put('CONTROLS.json',controls)
        for name in ('primary','independent'):
            r=flow(name,['-33/25000','-33/25000'],0,'baseline',begun)
            m=load(name); old=read(ROOT/'inputs'/f'{name}_low.json')['determinant']
            if 'exact_bounds' not in old: old={'exact_bounds':[old['lo_exact'],old['hi_exact']]}
            det=ball_record(m,r['event']['determinant']); saved=ball_record(m,old)
            need(sign(det)==sign(saved)==1 and overlaps(det,saved),'BASELINE_REPRODUCTION')
        bracket=[Q(-33,25000),Q(-131,100000)]
        for label,mass,expected in [('low',bracket[0],1),('high',bracket[1],-1)]:
            for name in ('primary','independent'):
                r=flow(name,[str(mass)]*2,1,label,begun); m=load(name)
                if sign(ball_record(m,r['event']['determinant']))!=expected:
                    put('RESULT.json',{'classification':'INCONCLUSIVE_SELECTED_BRACKET','record':label+'_'+name+'.json','history':history,'utc':now()}); return
        stop='MAX_EIGHT_BISECTIONS'
        for j in range(8):
            if bracket[1]-bracket[0]<=Q(1,25600000): stop='WIDTH_TARGET'; break
            mid=sum(bracket)/2; signs=[]; entry={'midpoint':str(mid),'before':list(map(str,bracket))}
            for name in ('primary','independent'):
                r=flow(name,[str(mid)]*2,1,f'mid_{j:02d}',begun); signs.append(sign(ball_record(load(name),r['event']['determinant'])))
            entry['signs']=signs; history.append(entry)
            if 0 in signs: stop='ZERO_CONTAINING_MIDPOINT'; break
            need(signs[0]==signs[1],'ENGINE_SIGN_DISAGREEMENT')
            bracket=[mid,bracket[1]] if signs[0]>0 else [bracket[0],mid]
            entry['after']=list(map(str,bracket))
        strips={name:flow(name,list(map(str,bracket)),1,'strip',begun,True) for name in ('primary','independent')}
        m=load('primary'); combined={}; common=set(strips['primary']['observables'])&set(strips['independent']['observables'])
        ratio_keys={'lower_radius_to_fractional_separation','upper_radius_to_fractional_separation'}
        sep=all(r['separation_nonzero'] for r in strips.values())
        if not sep: common-=ratio_keys
        for key in sorted(common):
            r=strips['primary']['observables'][key]
            a=ball_record(m,r); b=ball_record(m,strips['independent']['observables'][key])
            need(overlaps(a,b),'OBSERVABLE_DISAGREEMENT:'+key); combined[key]=pack(m.hull(a,b))
        put('RESULT.json',{'classification':'SELECTED_NEUTRAL_MODE_CHARACTERIZED' if sep else 'SELECTED_NEUTRAL_MODE_SEPARATION_INCONCLUSIVE',
             'mu_bracket':list(map(str,bracket)),'narrowing_stop':stop,'history':history,'combined':combined,
             'controls':controls,'seconds':time.monotonic()-begun,'utc':now(),'scope':'Selected neutral oscillator action; not charged trajectory or nonlinear evolution',
             'analytic_coherence_bounds':[0,1],'raw_bounds_not_clamped':True,
             'radius_ratio_status':'reported_both_engines' if sep else 'omitted_because_separation_not_excluded_from_zero_in_both_engines'})
    except BaseException as e:
        put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':now(),'error':repr(e),'traceback':traceback.format_exc(),'history':history})
        raise
    finally:
        signal.alarm(0)

if __name__=='__main__': main()
