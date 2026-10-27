"""Neutral growing-mode radial radar-time response on actual AB background.

The light pulse is a negligible-energy idealized probe with instantaneous
upper-wall reflection. Time dependence is sampled along both background
null legs; a frozen lapse ratio is not substituted for elapsed proper time.
"""
import importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('radar_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT; c.OUT=ROOT/'output'
T2=ROOT/'../T2R1_AB_SELECTED_MODE'

def exact_controls():
    P,L,r,u=Q(3,7),Q(5,11),Q(2,3),Q(7,5)
    # u denotes exp(rL); exact algebra, not a numerical exponential claim.
    outbound=(u-1)/r; returning=(u*u-u)/r; J=(u*u-1)/r
    c.need(outbound+returning==J,'TWO_LEG_TIME_WEIGHT_IDENTITY')
    c.need(-3*P*(outbound+returning)+P*J==-2*P*J,'FLAT_TIME_DEPENDENT_CLOCK')
    c.need(-3*P*(2*L)+P*(2*L)==2*(-2*P*L),'FLAT_STATIC_LIMIT')
    xa,xb=Q(2,7),Q(-3,11)
    c.need(-(1+Q(1))*xa+2*Q(1)*xb==2*(xb-xa),'STATIC_MOVING_BOUNDARIES')
    # General radial relabeling: P=-Halpha,B=-alpha',C=-r alpha.
    # With x=Ealpha and x'=E(alpha'-Halpha), the optical integrand
    # is exactly -d[x(wout+wret)]/ds, including the shift term.
    E,H,alpha,ap,wo,wr=map(Q,('2/3','-3/5','5/7','7/11','11/13','13/17'))
    x=E*alpha; xp=E*(ap-H*alpha)
    integrand=E*(H*alpha-ap)*(wo+wr)-r*alpha*E*E*(wo-wr)
    derivative=-(xp*(wo+wr)+x*r*E*(wo-wr))
    c.need(integrand==derivative,'GENERAL_SHIFT_GAUGE_DERIVATIVE')
    Ea,Eb,aa,ab=map(Q,('1','3/2','2/5','-4/7'))
    endpoints=-Ea*(1+u*u)*aa+2*Eb*u*ab
    integral=-2*Eb*ab*u+Ea*aa*(1+u*u)
    c.need(endpoints+integral==0,'PURE_RADIAL_GAUGE_ENDPOINT_CANCELLATION')
    c.need(-H*alpha+H*alpha==0,'PURE_RADIAL_GAUGE_CLOCK')
    # Arbitrary temporal gauge requires C=a² beta'; its coordinate
    # duration beta_a(exp(2rL)-1) cancels Pa=-r beta_a clock contribution.
    beta=Q(3,11)
    c.need(beta*(u*u-1)-r*beta*J==0,'PURE_TEMPORAL_GAUGE_CLOCK')
    return {'two_leg_temporal_sampling':True,'flat_time_dependent_constant_mode':True,
            'flat_static_limit':True,'moving_boundary_static_limit':True,
            'general_shift_radial_gauge_identity':True,'radial_gauge_endpoints_and_clock':True,
            'temporal_gauge_clock':True}

def parent_gate():
    g=c.read(ROOT/'ADMISSION.json'); c.need(g.get('t2_terminal_review_accepted') is True,'T2_NOT_ACCEPTED')
    for rel in ('../T2R1_AB_SELECTED_MODE/TERMINAL_REVIEW.md','../T2R1_AB_SELECTED_MODE/output/RESULT.json',
                '../T2R1_AB_SELECTED_MODE/output/strip_primary.json','../T2R1_AB_SELECTED_MODE/output/strip_independent.json'):
        c.need(rel in g['sources'],'MISSING_BOUND_PARENT:'+rel)
    r=c.read(T2/'output/RESULT.json'); c.need(r['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED','SELECTED_MODE_REQUIRED')
    return r

def flow(name,parent,begun):
    from flint import arb,fmpq
    m=c.load(name); binding=c.read(ROOT/'inputs/central_bindings.json'); cfg=binding['config']
    A=m.interval(*map(fmpq,cfg['A'])); mu=m.interval(*map(fmpq,parent['mu_bracket']))
    y,p,ua=c.launch(m,name,A,mu,binding['model_exact'],1)
    c.need(p['k'].lower()>0 and (mu+4*p['k']).upper()<0,'NEUTRAL_GROWING_MODE_SECTOR')
    gamma=(-3*p['k'].sqrt()+(9*p['k']-4*mu).sqrt())/2
    c.need(gamma.lower()>0,'POSITIVE_GROWTH_RATE')
    c.need(c.contains0(gamma*(gamma+3*p['k'].sqrt())+mu),'GROWTH_MASS_RELATION')
    W0,H0,P0,T0,E0,psi0,f0,g0=c.physical(y,name); aa=W0.exp()
    c.need(aa.contains(1) and psi0.contains(1),'LOWER_NORMALIZATION')
    Dlo,Dhi=map(fmpq,cfg['D']); h=fmpq(2,8192 if name=='primary' else 16384)
    n=(Q(str(Dhi))/Q(str(h))).__ceil__(); started=time.monotonic()
    L=arb(0); prefix=arb(0); rows=[]; event=None; cover=[]; maxpic=0
    for j in range(n):
        if j%64==0:
            c.need(time.monotonic()-started<360,'RADAR_FLOW_CAP'); c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        pos=j*h; y,cell=m.step(y,h,p); geo=m.geometry(cell,p)
        c.need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FLOW')
        c.need(c.contains0(geo['constraint']) and c.contains0(geo['first_integral']),'CONSTRAINT_OR_BACKGROUND')
        c.need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY'); maxpic=max(maxpic,cell['picard_iterations'])
        W,H,P,T,E,ps,f,g=c.physical(cell['box'],name)
        Eraw,Er=c.dyadic_export(m,E); psraw,psr=c.dyadic_export(m,ps)
        c.need(Er.lower()>0,'POSITIVE_OPTICAL_DENSITY')
        extent=max(fmpq(0),min(h,Dhi-pos))
        start_raw,start_back=c.dyadic_export(m,prefix)
        traw,tau=c.dyadic_export(m,start_back+Er*m.interval(fmpq(0),extent))
        mandatory=max(fmpq(0),min(h,Dlo-pos)); optional=extent-mandatory
        Lraw,Lpart=c.dyadic_export(m,c.integral_piece(m,Er,mandatory,optional)); L+=Lpart
        prefixraw,prefixpart=c.dyadic_export(m,Er*h)
        rows.append({'index':j,'s':str(pos),'step':str(h),'mandatory':str(mandatory),'optional':str(optional),
                     'E':Eraw,'psi':psraw,'tau_start':start_raw,'tau_box':traw,'optical_D_contribution':Lraw,
                     'full_cell_prefix_contribution':prefixraw})
        prefix=start_back+prefixpart
        if pos+h>=Dlo and pos<=Dhi:
            lo=max(fmpq(0),Dlo-pos); hi=min(h,Dhi-pos); v=m.range_on_cell(cell,lo,hi)
            Wb,Hb,Pb,Tb,Eb,psb,fb,gb=c.physical(v,name); G,d=c.response(mu,Eb,1)
            det=gb+2*Tb*psb+G*fb/2; event=det if event is None else m.hull(event,det)
            cover.append({'lo':str(pos+lo),'hi':str(pos+hi)})
    c.need(L.lower()>0 and c.contains0(event),'OPTICAL_LENGTH_AND_ROOT_STRIP')
    end=Dlo
    for row in cover: c.need(fmpq(row['lo'])==end,'EVENT_GAP'); end=fmpq(row['hi'])
    c.need(end==Dhi,'EVENT_END')
    weighted=arb(0)
    for row in rows:
        if row['index']%64==0:
            c.need(time.monotonic()-started<360,'RADAR_FLOW_CAP')
            c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        tau=c.ball_record(m,row['tau_box']); E=c.ball_record(m,row['E']); ps=c.ball_record(m,row['psi'])
        # Outbound t-te=tau, return t-te=2L-tau, no frozen-time substitution.
        kernel=(gamma*tau).exp()+(gamma*(2*L-tau)).exp()
        kraw,kr=c.dyadic_export(m,kernel)
        dens=E*ps*kr
        wraw,wr=c.dyadic_export(m,c.integral_piece(m,dens,fmpq(row['mandatory']),fmpq(row['optional'])))
        row['temporal_kernel']=kraw; row['weighted_contribution']=wraw; weighted+=wr
    # J is analytic at zero; this selected mode has gamma strictlypositive.
    J=((2*gamma*L).exp()-1)/gamma
    coord=-3*weighted; clock=aa*psi0*J; full=aa*coord+clock; half=full/2
    old=c.read(T2/'output'/('strip_'+name+'.json'))
    c.need(old['mu_bounds']==parent['mu_bracket'] and old['beta']==1,'PARENT_MODE_LINKAGE')
    delta=c.ball_record(m,old['observables']['deltaD_over_Q']); c.need(not c.contains0(delta),'NONZERO_MATCHED_SEPARATION')
    D=m.interval(Dlo,Dhi)
    observables={'gamma':gamma,'optical_one_way_L':L,'background_roundtrip_proper_time':2*aa*L,
                 'weighted_mode_integral':weighted,'coordinate_roundtrip_coefficient':coord,
                 'emitter_clock_conversion_coefficient':clock,'proper_roundtrip_coefficient':full,
                 'half_roundtrip_coefficient':half,'deltaD_over_Q':delta,
                 'half_radar_over_separation_response':half/delta,
                 'fractional_clock_over_fractional_separation_response':(full/(2*aa*L))/(delta/D)}
    budget=name+'_RADAR_BUDGET.json'
    c.need(time.monotonic()-started<360,'RADAR_FLOW_CAP')
    c.need(time.monotonic()-begun<900,'TOTAL_CAP')
    c.put(budget,{'engine':name,'D_bounds':list(cfg['D']),'mu_bounds':parent['mu_bracket'],
                  'gamma':c.pack(gamma),'L':c.pack(L),'weighted_integral':c.pack(weighted),'cells':rows,
                  'dyadic_denominator_power':80,'premise':'Saved E,psi boxes inherit validated whole-cell flow. Exponentials use outward Arb; rational audit alone does not establish transcendental enclosures.'})
    result={'engine':name,'mu_bounds':parent['mu_bracket'],'K':c.pack(p['k']),'lower_warp_a':c.pack(aa),
            'lower_psi':c.pack(psi0),'all_cell_checks_pass':True,'cells':n,'max_picard_iterations':maxpic,
            'event_cover':cover,'upper_determinant':c.pack(event),'observables':{k:c.pack(v) for k,v in observables.items()},
            'budget':{'path':budget,'sha256':c.sha(c.OUT/budget)},'seconds':time.monotonic()-started}
    c.put('radar_'+name+'.json',result); print(json.dumps({'completed':name,'seconds':result['seconds']}),flush=True)
    return result

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('RADAR_RESPONSE_CAP_900_SECONDS'))); signal.alarm(900)
        c.authenticate(); parent=parent_gate()
        c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested={'radar':exact_controls(),'inherited':{name:c.semantic_controls(c.load(name)) for name in ('primary','independent')}}
        c.put('CONTROLS.json',tested); per={name:flow(name,parent,begun) for name in ('primary','independent')}
        m=c.load('primary'); combined={}
        for key in per['primary']['observables']:
            a=c.ball_record(m,per['primary']['observables'][key]); d=c.ball_record(m,per['independent']['observables'][key])
            c.need(c.overlaps(a,d),'RADAR_ENGINE_DISAGREEMENT:'+key); combined[key]=c.pack(m.hull(a,d))
        c.put('RESULT.json',{'classification':'NEUTRAL_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','combined':combined,
              'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
              'scope':'Linear response of ideal reflected radial light-pulse elapsed lower-observer proper time, neutral selected growing mode. No finite amplitude, event horizon, charged response or universal space-time law.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
