"""First-current operational radar coefficient, with both moving interfaces."""
import importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); v=importlib.util.module_from_spec(s); s.loader.exec_module(v); return v
b=module('current_basis',ROOT/'basis.py'); c=b.c; c.ROOT=ROOT; c.OUT=ROOT/'output'; b.ROOT=ROOT
rc=module('inherited_radar',ROOT/'radar_controls.py')
T4=ROOT/'../T4_AB_FIRST_CURRENT'; T8=ROOT/'../T8_AB_NEUTRAL_RADAR_RESPONSE'

def controls():
    inherited=rc.exact_controls()
    r,u,P=Q(-2,3),Q(3,5),Q(4,7)
    J=(u*u-1)/r
    c.need((u-1)/r+(u*u-u)/r==J,'NEGATIVE_RATE_TWO_LEGS')
    c.need(-3*P*J+P*J==-2*P*J and J>0,'NEGATIVE_RATE_FLAT_CLOCK')
    Ea,Eb,xa,xb=Q(1),Q(3,2),Q(2,7),Q(-3,11)
    outbound=-Ea*xa+Eb*u*xb
    returning=-Ea*u*u*xa+Eb*u*xb
    c.need(outbound+returning==-Ea*(1+u*u)*xa+2*Eb*u*xb,'MOVING_GRAPH_TWO_LEGS')
    c.need(Q(0)*J==0,'ZERO_SOURCE_ZERO_CLOCK')
    return {'inherited_radar':inherited,'negative_rate_flat_clock':True,'moving_graph_two_legs':True,'zero_source':True}

def parent_gate():
    g=c.read(ROOT/'ADMISSION.json')
    c.need(g.get('t4_terminal_review_accepted') is True and g.get('t8_terminal_review_accepted') is True,'PARENT_REVIEW_REQUIRED')
    required=['../T4_AB_FIRST_CURRENT/TERMINAL_REVIEW.md','../T4_AB_FIRST_CURRENT/output/RESULT.json',
              '../T8_AB_NEUTRAL_RADAR_RESPONSE/TERMINAL_REVIEW.md','../T8_AB_NEUTRAL_RADAR_RESPONSE/output/RESULT.json']
    required+=['../T4_AB_FIRST_CURRENT/output/assembled_'+n+'.json' for n in ('primary','independent')]
    for rel in required: c.need(rel in g['sources'],'MISSING_BOUND_PARENT:'+rel)
    c.need(c.read(T4/'output/RESULT.json')['classification']=='FIRST_CURRENT_SEPARATION_COEFFICIENTS_ENCLOSED','T4_SCOPE')
    c.need(c.read(T8/'output/RESULT.json')['classification']=='NEUTRAL_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','T8_SCOPE')

def flow(name,kind,begun):
    from flint import arb,fmpq
    m=c.load(name); binding=c.read(ROOT/'inputs/central_bindings.json'); cfg=binding['config']
    y,p=b.initial(m,name,binding,kind); lower=y[:]; rate=-6*p['k'].sqrt()
    c.need(rate.upper()<0 and c.contains0(rate*(rate+3*p['k'].sqrt())+p['mu']),'CURRENT_MASS_RATE')
    Dlo,Dhi=map(fmpq,cfg['D']); h=fmpq(2,8192 if name=='primary' else 16384)
    n=(Q(str(Dhi))/Q(str(h))).__ceil__(); started=time.monotonic()
    L=arb(0); prefix=arb(0); Ipsi=arb(0); rows=[]; events={}; cover=[]; maxpic=0
    for j in range(n):
        if j%64==0:
            c.need(time.monotonic()-started<210,'CURRENT_RADAR_FLOW_CAP'); c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        pos=j*h; y,cell=m.step(y,h,p); geo=m.geometry(cell,p)
        c.need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FLOW')
        c.need(c.contains0(geo['constraint']) and c.contains0(geo['first_integral']),'CONSTRAINT_OR_BACKGROUND')
        c.need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY'); maxpic=max(maxpic,cell['picard_iterations'])
        W,H,P,T,E,ps,f,g=c.physical(cell['box'],name)
        Eraw,Er=c.dyadic_export(m,E); psraw,psr=c.dyadic_export(m,ps); fraw,fr=c.dyadic_export(m,f)
        c.need(Er.lower()>0,'OPTICAL_POSITIVITY')
        extent=max(fmpq(0),min(h,Dhi-pos)); mandatory=max(fmpq(0),min(h,Dlo-pos)); optional=extent-mandatory
        start_raw,start_back=c.dyadic_export(m,prefix)
        traw,tau=c.dyadic_export(m,start_back+Er*m.interval(fmpq(0),extent))
        Lraw,Lpart=c.dyadic_export(m,c.integral_piece(m,Er,mandatory,optional)); L+=Lpart
        prefixraw,prefixpart=c.dyadic_export(m,Er*h); prefix=start_back+prefixpart
        Iraw,Ipart=c.dyadic_export(m,c.integral_piece(m,psr,mandatory,optional)); Ipsi+=Ipart
        rows.append({'index':j,'s':str(pos),'step':str(h),'mandatory':str(mandatory),'optional':str(optional),
                     'E':Eraw,'psi':psraw,'f':fraw,'tau_start':start_raw,'tau_box':traw,'optical_D_contribution':Lraw,
                     'full_cell_prefix_contribution':prefixraw,'Ipsi_contribution':Iraw})
        if pos+h>=Dlo and pos<=Dhi:
            lo=max(fmpq(0),Dlo-pos); hi=min(h,Dhi-pos); z=m.range_on_cell(cell,lo,hi)
            W,H,P,T,E,ps,f,g=c.physical(z,name); G,d=c.response(p['mu'],E,1)
            vals={'W':W,'H':H,'Phi':P,'T':T,'E':E,'psi':ps,'f':f,'g':g,'F':g+2*T*ps+G*f/2}
            for key,v in vals.items(): events[key]=v if key not in events else m.hull(events[key],v)
            cover.append({'lo':str(pos+lo),'hi':str(pos+hi)})
    end=Dlo
    for row in cover: c.need(fmpq(row['lo'])==end,'EVENT_GAP'); end=fmpq(row['hi'])
    c.need(end==Dhi and L.lower()>0,'EVENT_END_AND_OPTICAL_LENGTH')
    weighted=arb(0)
    for j,row in enumerate(rows):
        if j%64==0:
            c.need(time.monotonic()-started<210,'CURRENT_RADAR_SECOND_PASS_CAP'); c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        tau=c.ball_record(m,row['tau_box']); E=c.ball_record(m,row['E']); ps=c.ball_record(m,row['psi'])
        kernel=(rate*tau).exp()+(rate*(2*L-tau)).exp(); kraw,kr=c.dyadic_export(m,kernel)
        wraw,wr=c.dyadic_export(m,c.integral_piece(m,E*ps*kr,fmpq(row['mandatory']),fmpq(row['optional'])))
        row['temporal_kernel']=kraw; row['weighted_contribution']=wraw; weighted+=wr
    c.need(time.monotonic()-started<210,'CURRENT_RADAR_FINAL_FLOW_CAP'); c.need(time.monotonic()-begun<900,'TOTAL_CAP')
    filename=kind+'_'+name+'_RADAR_BUDGET.json'
    c.put(filename,{'engine':name,'kind':kind,'D_bounds':list(cfg['D']),'rate':c.pack(rate),'L':c.pack(L),
                   'Ipsi':c.pack(Ipsi),'weighted_integral':c.pack(weighted),'cells':rows,'dyadic_denominator_power':80,
                   'premise':'Validated whole-cell E,psi and outward Arb exponentials; rational resummation alone does not certify transcendental kernels.'})
    result={'engine':name,'kind':kind,'mu':c.pack(p['mu']),'k':c.pack(p['k']),'rate':c.pack(rate),
            'lower_state':[c.pack(v) for v in lower],'upper':{key:c.pack(v) for key,v in events.items()},
            'Ipsi':c.pack(Ipsi),'L':c.pack(L),'weighted_integral':c.pack(weighted),'event_cover':cover,
            'all_cell_checks_pass':True,'cells':n,'max_picard_iterations':maxpic,
            'budget':{'path':filename,'sha256':c.sha(c.OUT/filename)},'seconds':time.monotonic()-started}
    c.put(kind+'_'+name+'.json',result); print(json.dumps({'completed':kind,'engine':name,'seconds':result['seconds']}),flush=True)
    return result

def assemble(name,H,P):
    from flint import arb,fmpq
    m=c.load(name); ball=lambda x:c.ball_record(m,x)
    full=b.combine(name,H,P); old=c.read(T4/'output'/('assembled_'+name+'.json'))
    c.need(c.overlaps(ball(H['L']),ball(P['L'])) and c.overlaps(ball(H['rate']),ball(P['rate'])),'BACKGROUND_BASIS_AGREEMENT')
    L=m.hull(ball(H['L']),ball(P['L'])); rate=m.hull(ball(H['rate']),ball(P['rate']))
    J=((2*rate*L).exp()-1)/rate; output={}
    D=m.interval(*map(fmpq,c.read(ROOT/'inputs/central_bindings.json')['config']['D']))
    for channel in ('lower','upper'):
        base=full['channels'][channel]; parent=old['channels'][channel]; amp=ball(base['homogeneous_multiplier'])
        weighted=amp*ball(H['weighted_integral'])+(ball(P['weighted_integral']) if channel=='lower' else arb(0))
        wa={k:ball(v) for k,v in base['walls']['lower'].items()}; wb={k:ball(v) for k,v in base['walls']['upper'].items()}
        aa=1/wa['E']; xa=wa['xi']; xb=wb['xi']
        graph=-wa['E']*(1+(2*rate*L).exp())*xa+2*wb['E']*(rate*L).exp()*xb
        optical=-3*weighted; clock=aa*(wa['psi']+wa['H']*xa)*J
        radar=aa*(graph+optical)+clock; half=radar/2
        delta=ball(parent['coefficient_total']); reproduced=ball(base['coefficient_total'])
        c.need(c.overlaps(delta,reproduced) and c.contains0(reproduced-delta),'T4_DISTANCE_REPRODUCTION')
        a6=ball(base['source_wall_a6'])
        values={'rate':rate,'optical_one_way_L':L,'background_roundtrip_proper_time':2*aa*L,
                'weighted_mode_integral':weighted,'coordinate_graph_coefficient':graph,
                'coordinate_bulk_coefficient':optical,'emitter_clock_coefficient':clock,
                'proper_roundtrip_coefficient':radar,'half_roundtrip_coefficient':half,
                'accepted_separation_coefficient':delta,'reproduced_separation_coefficient':reproduced,
                'proper_density_roundtrip_coefficient':a6*radar,'proper_density_half_roundtrip_coefficient':a6*half,
                'proper_density_separation_coefficient':a6*delta,'source_wall_a6':a6}
        if not c.contains0(delta):
            values['half_radar_over_separation_response']=half/delta
            values['fractional_clock_over_fractional_separation_response']=(radar/(2*aa*L))/(delta/D)
        output[channel]={'observables':{key:c.pack(v) for key,v in values.items()},'radar_sign':c.sign(radar),
                         'ratios_available':not c.contains0(delta)}
    return {'engine':name,'channels':output,'full_forced_assembly':full}

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('CURRENT_RADAR_CAP_900_SECONDS'))); signal.alarm(900)
        c.authenticate(); parent_gate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested={'radar':controls(),'current':b.exact_controls(),'inherited':{n:c.semantic_controls(c.load(n)) for n in ('primary','independent')}}
        c.put('CONTROLS.json',tested); per={}
        for name in ('primary','independent'):
            H=flow(name,'homogeneous',begun); P=flow(name,'particular_lower',begun)
            per[name]=assemble(name,H,P); c.put('current_radar_'+name+'.json',per[name])
        m=c.load('primary'); combined={}
        for channel in ('lower','upper'):
            a=per['primary']['channels'][channel]; d=per['independent']['channels'][channel]; obs={}
            keys=set(a['observables']) & set(d['observables'])
            for key in sorted(keys):
                x=c.ball_record(m,a['observables'][key]); y=c.ball_record(m,d['observables'][key])
                c.need(c.overlaps(x,y),'CURRENT_RADAR_ENGINE_DISAGREEMENT:'+channel+':'+key); obs[key]=c.pack(m.hull(x,y))
            sg=c.sign(c.ball_record(m,obs['proper_roundtrip_coefficient']))
            combined[channel]={'observables':obs,'radar_sign':sg,
                'classification':'SHORTER_ROUNDTRIP' if sg<0 else 'LONGER_ROUNDTRIP' if sg>0 else 'RADAR_SIGN_UNRESOLVED',
                'ratios_available':a['ratios_available'] and d['ratios_available']}
        c.put('RESULT.json',{'classification':'FIRST_CURRENT_OPERATIONAL_RADAR_RESPONSE_ENCLOSED','combined':combined,
               'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'First-current coefficient of ideal reflected radial pulse elapsed emitter proper time. Negative coefficient is shorter decaying offset, not continuing contraction. No finite charge, free-mode excitation or nonlinear evolution inferred.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
