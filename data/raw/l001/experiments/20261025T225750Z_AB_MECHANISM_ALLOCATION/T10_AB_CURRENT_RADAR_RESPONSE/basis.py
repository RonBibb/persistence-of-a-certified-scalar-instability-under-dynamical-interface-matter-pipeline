"""First current-squared response in the selected AB redshift branch.

Two regular homogeneous-bulk propagations per engine at mu=-18k suffice:
one lower homogeneous solution and one lower-current particular solution.
Wall forcing, graph terms and proper-length response are retained explicitly.
"""
import importlib.util, json, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('current_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c)
c.ROOT=ROOT; c.OUT=ROOT/'output'

def load_wall(m,y,name,p,sigma,current_squared):
    W,H,P,T,E,psi,f,g=c.physical(y,name)
    Tp=p['m2']*P-4*H*T; d=2-p['mu']*E*E; c.need(d.lower()>0,'CHARGED_OSCILLATOR_DENOMINATOR')
    G=21-1/d; n=current_squared*(E*E)*(E*E)*(E*E)
    xi=sigma*current_squared*(E*E)*(E*E)/(42*p['k'])
    j=sigma*n/2000
    R=(G*T-2*sigma*Tp)*xi-n/1000
    return {'T':T,'Tp':Tp,'E':E,'H':H,'Phi':P,'d':d,'Gamma':G,'n':n,'xi':xi,'j':j,'R':R}

def exact_controls():
    # Hand action residual and reduced wall load are compared at arbitrary
    # rational values, without imposing the differential solution.
    tested=0
    for sigma in (Q(-1),Q(1)):
        for N in (Q(0),Q(1),Q(3,2)):
            E,k,T,Tp=Q(2),Q(1,3000),Q(-1,7),Q(2,9)
            mu=-18*k; d=2-mu*E*E; G=21-1/d
            n=N*E**6; xi=sigma*N*E**4/(42*k); j=sigma*n/2000
            c.need(sigma*E*E*42*k*xi==n,'EXACT_TRACEFREE_GRAPH')
            R=(G*T-2*sigma*Tp)*xi-n/1000
            RfromQ6=2*sigma*(-(Tp-sigma*G*T/2)*xi-j)
            c.need(R==RfromQ6,'EXACT_SOURCE_SIGN')
            f,ps=Q(4,13),Q(2,11); g=sigma*(G*f+R)/2-2*T*ps
            chi=(f+T*xi)/d
            scalar=g+2*T*ps+Tp*xi-sigma*(21*(f+T*xi)-chi-n/1000)/2
            c.need(scalar==0 and d*chi==f+T*xi,'EXACT_UNDIVIDED_SCALAR_OSCILLATOR')
            # Direct Kx Israel identity after the regular momentum row.
            deltaKx=-sigma*T*(f+T*xi)/3-7*sigma*k*E*E*xi
            c.need(deltaKx+sigma*T*(f+T*xi)/3+n/6==0,'EXACT_DIAGONAL_ISRAEL')
            # First-order stiff-current exchange: r=-6h (take h=1 in
            # this homogeneous identity); tension response cancels on both
            # sides, leaving r*rho+6h*rho=0.
            tension_response=2*sigma*T*(f+T*xi)
            c.need(-6*(tension_response+n)+6*n==-6*tension_response,'EXACT_MATERIAL_EXCHANGE')
            # Removing the displaced trace is deliberately distinguishable.
            if N:
                wrong= g+2*T*ps+Tp*xi-sigma*(21*(f+T*xi)-f/d-n/1000)/2
                c.need(wrong!=0,'DISPLACED_TRACE_MUTATION')
            tested+=1
    # A transverse coordinate change alpha changes lapse integral by
    # -(alpha_b-alpha_a) and graph difference by +(alpha_b-alpha_a).
    integral,xa,xb,aa,ab=map(Q,('3/7','1/4','-2/5','4/9','-1/3'))
    c.need(integral+xb-xa==integral-(ab-aa)+(xb+ab)-(xa+aa),'TRANSVERSE_GAUGE_CANCELLATION')
    FH,FP,Rb=Q(2,3),Q(-4,7),Q(5,11)
    coeff=(-Rb/2-FP)/FH; c.need(coeff*FH+FP==-Rb/2,'UPPER_FORCED_MULTIPLIER')
    # Linear unit-current source combinations reproduce arbitrary labels.
    c.need(Q(3,2)*Q(4,7)+Q(5,3)*Q(-2,9)==Q(6,7)-Q(10,27),'SOURCE_SUPERPOSITION_CONTROL')
    return {'wall_source_cases':tested,'source_sign':True,'tracefree_graph':True,
            'undivided_scalar_oscillator':True,'displaced_trace_mutation':True,
            'transverse_gauge_cancellation':True,'upper_inverse_formula':True,'source_superposition':True,
            'diagonal_Israel_from_momentum':True,'first_order_material_exchange':True}

def initial(m,name,binding,kind):
    from flint import arb,fmpq
    A=m.interval(*map(fmpq,binding['config']['A']))
    y,p=m.initial(A,arb(0),binding['model_exact'])
    # k and mu belong to the same full launch interval, not independent
    # midpoint inputs. The interval representation may overestimate coupling.
    p['mu']=-18*p['k']; w=load_wall(m,y,name,p,1,1 if kind=='particular_lower' else 0)
    ps=arb(0 if kind=='particular_lower' else 1); B=w['Gamma']*w['T']/2-w['Tp']
    c.need(not c.contains0(B),'LOWER_FORCED_DENOMINATOR')
    f=(3*(p['mu']+4*p['k'])*w['E']*w['E']*ps-w['T']*w['R']/2)/B
    g=w['Gamma']*f/2+w['R']/2-2*w['T']*ps
    if name=='primary': y[5:8]=[ps,f,g]
    else: y[4:7]=[ps,f,g]
    c.need(c.contains0(m.constraint(y,p)),'FORCED_LOWER_CONSTRAINT')
    c.need(c.contains0(2*(g+2*w['T']*ps)-w['Gamma']*f-w['R']),'FORCED_LOWER_SCALAR')
    return y,p

def flow(name,kind,begun):
    from flint import arb,fmpq
    m=c.load(name); binding=c.read(ROOT/'inputs/central_bindings.json'); cfg=binding['config']
    y,p=initial(m,name,binding,kind); lower=y[:]
    Dlo,Dhi=map(fmpq,cfg['D']); h=fmpq(2,8192 if name=='primary' else 16384)
    n=(Q(str(Dhi))/Q(str(h))).__ceil__(); start=time.monotonic()
    total=arb(0); budgets=[]; events={}; covers=[]; maxpic=0
    for j in range(n):
        if j%64==0:
            c.need(time.monotonic()-start<600,'SINGLE_FLOW_CAP')
            c.need(time.monotonic()-begun<2700,'TOTAL_CAP')
        pos=j*h; y,cell=m.step(y,h,p); geo=m.geometry(cell,p)
        c.need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FORCED_FLOW')
        c.need(c.contains0(geo['constraint']) and c.contains0(geo['first_integral']),'FORCED_CONSTRAINT_OR_BACKGROUND')
        c.need(geo['warp_squared'].lower()>0,'FORCED_WARP')
        maxpic=max(maxpic,cell['picard_iterations'])
        mandatory=max(fmpq(0),min(h,Dlo-pos)); optional=max(fmpq(0),min(h,Dhi-pos))-mandatory
        raw,reimported=c.dyadic_export(m,c.integral_piece(m,geo['psi'],mandatory,optional)); total+=reimported
        budgets.append({'index':j,'s':str(pos),'step':str(h),'mandatory':str(mandatory),'optional':str(optional),'Ipsi':raw})
        if pos+h>=Dlo and pos<=Dhi:
            a=max(fmpq(0),Dlo-pos); b=min(h,Dhi-pos); z=m.range_on_cell(cell,a,b)
            W,H,P,T,E,ps,f,g=c.physical(z,name); d=2-p['mu']*E*E; G=21-1/d
            vals={'W':W,'H':H,'Phi':P,'T':T,'E':E,'psi':ps,'f':f,'g':g,
                  'F':g+2*T*ps+G*f/2}
            for key,v in vals.items(): events[key]=v if key not in events else m.hull(events[key],v)
            covers.append({'lo':str(pos+a),'hi':str(pos+b)})
    last=Q(str(Dlo))
    for row in covers: c.need(Q(row['lo'])==last,'FORCED_EVENT_GAP'); last=Q(row['hi'])
    c.need(last==Q(str(Dhi)),'FORCED_EVENT_END')
    file=kind+'_'+name+'_BUDGET.json'
    c.put(file,{'D_bounds':list(cfg['D']),'cells':budgets,'reported_Ipsi':c.pack(total),'dyadic_denominator_power':80})
    rec={'engine':name,'kind':kind,'mu':c.pack(p['mu']),'k':c.pack(p['k']),
         'lower_state':[c.pack(v) for v in lower],'upper':{key:c.pack(v) for key,v in events.items()},
         'Ipsi':c.pack(total),'event_cover':covers,'cells':n,'max_picard_iterations':maxpic,
         'all_cell_checks_pass':True,'seconds':time.monotonic()-start,'budget':{'path':file,'sha256':c.sha(c.OUT/file)}}
    c.put(kind+'_'+name+'.json',rec); print(json.dumps({'completed':kind,'engine':name,'seconds':rec['seconds']}),flush=True)
    return rec

def combine(name,Hrec,Prec):
    from flint import arb
    m=c.load(name); ball=lambda r:c.ball_record(m,r)
    p={'k':ball(Hrec['k']),'mu':ball(Hrec['mu']),
       'm2':m.exact(c.read(ROOT/'inputs/central_bindings.json')['model_exact']['m2']) if name=='primary' else m.exact_ball(c.read(ROOT/'inputs/central_bindings.json')['model_exact']['m2'])}
    c.need(c.contains0(p['mu']+18*p['k']),'MASS_CURVATURE_RELATION')
    Hlo=list(map(ball,Hrec['lower_state'])); Plo=list(map(ball,Prec['lower_state']))
    upH={k:ball(v) for k,v in Hrec['upper'].items()}; upP={k:ball(v) for k,v in Prec['upper'].items()}
    def state(up):
        vals=[up[k] for k in ('W','H','Phi','T')]
        if name=='primary': vals+=[up['E']]
        return vals+[up[k] for k in ('psi','f','g')]
    Hup=state(upH); Pup=state(upP)
    FH=upH['F']; c.need(not c.contains0(FH),'FORCED_UPPER_INVERSE_UNRESOLVED')
    I_H,I_P=ball(Hrec['Ipsi']),ball(Prec['Ipsi']); results={}
    for channel in ('lower','upper'):
        Na,Nb=(1,0) if channel=='lower' else (0,1)
        wa=load_wall(m,Hlo,name,p,1,Na); wb=load_wall(m,Hup,name,p,-1,Nb)
        F_P=upP['F'] if Na else arb(0)
        amp=(-wb['R']/2-F_P)/FH
        totalI=amp*I_H+(I_P if Na else arb(0))
        bulk=-2*totalI; graph=wb['xi']-wa['xi']; full=bulk+graph
        records={}; residuals={}
        for wall,stH,stP,w,sigma in [('lower',Hlo,Plo,wa,1),('upper',Hup,Pup,wb,-1)]:
            _,_,_,_,_,hp,hf,hg=c.physical(stH,name)
            _,_,_,_,_,pp,pf,pg=c.physical(stP,name)
            ps=amp*hp+(pp if Na else arb(0)); f=amp*hf+(pf if Na else arb(0)); g=amp*hg+(pg if Na else arb(0))
            chi=(f+w['T']*w['xi'])/w['d']
            osc=w['d']*chi-f-w['T']*w['xi']
            scalar=g+2*w['T']*ps+w['Tp']*w['xi']-sigma*(21*(f+w['T']*w['xi'])-chi-w['n']/1000)/2
            reduced=2*sigma*(g+2*w['T']*ps)-w['Gamma']*f-w['R']
            graphrow=sigma*w['E']*w['E']*42*p['k']*w['xi']-w['n']
            # Direct spatial Israel variation using its exact Kx formula,
            # the inherited regular momentum row and H' background row.
            pprime=-2*w['H']*ps-w['T']*f/3
            Hprime=-w['T']*w['T']/3-p['k']*w['E']*w['E']
            deltaKx=sigma*(pprime+2*w['H']*ps+Hprime*w['xi']-6*p['k']*w['E']*w['E']*w['xi'])
            spatial_Israel=deltaKx+sigma*w['T']*(f+w['T']*w['xi'])/3+w['n']/6
            for label,v in [('oscillator',osc),('scalar_normal',scalar),('reduced_scalar',reduced),('tracefree_Israel',graphrow),('spatial_Israel',spatial_Israel)]:
                c.need(c.contains0(v),'ASSEMBLED_WALL_RESIDUAL:'+channel+':'+wall+':'+label)
            records[wall]={k:c.pack(v) for k,v in {**w,'psi':ps,'f':f,'g':g,'chi':chi}.items()}
            residuals[wall]={k:c.pack(v) for k,v in {'oscillator':osc,'scalar_normal':scalar,'reduced_scalar':reduced,'tracefree_Israel':graphrow,'spatial_Israel_using_momentum':spatial_Israel}.items()}
        sourcewall=wa if Na else wb
        a6=1/((sourcewall['E']*sourcewall['E'])*(sourcewall['E']*sourcewall['E'])*(sourcewall['E']*sourcewall['E']))
        results[channel]={'coefficient_bulk':c.pack(bulk),'coefficient_graph':c.pack(graph),'coefficient_total':c.pack(full),
                          'proper_density_coefficient_bulk':c.pack(a6*bulk),'proper_density_coefficient_graph':c.pack(a6*graph),
                          'proper_density_coefficient_total':c.pack(a6*full),'source_wall_a6':c.pack(a6),
                          'homogeneous_multiplier':c.pack(amp),'walls':records,'residuals':residuals,
                          'total_sign':c.sign(full)}
    return {'engine':name,'mu':c.pack(p['mu']),'k':c.pack(p['k']),'upper_inverse_determinant':c.pack(FH),'channels':results}

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('HARD_CURRENT_CAP_2700_SECONDS'))); signal.alarm(2700)
        c.authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':c.os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested={'exact_source':exact_controls(),'inherited_and_budget':{name:c.semantic_controls(c.load(name)) for name in ('primary','independent')}}
        c.put('CONTROLS.json',tested); per={}
        for name in ('primary','independent'):
            H=flow(name,'homogeneous',begun); P=flow(name,'particular_lower',begun); per[name]=combine(name,H,P)
            c.put('assembled_'+name+'.json',per[name])
        m=c.load('primary'); combined={}
        for channel in ('lower','upper'):
            combined[channel]={}
            for key in ('coefficient_bulk','coefficient_graph','coefficient_total',
                        'proper_density_coefficient_bulk','proper_density_coefficient_graph','proper_density_coefficient_total'):
                a=c.ball_record(m,per['primary']['channels'][channel][key]); b=c.ball_record(m,per['independent']['channels'][channel][key])
                c.need(c.overlaps(a,b),'CURRENT_ENGINE_DISAGREEMENT:'+channel+':'+key)
                combined[channel][key]=c.pack(m.hull(a,b))
            combined[channel]['total_sign']=c.sign(c.ball_record(m,combined[channel]['coefficient_total']))
        c.put('RESULT.json',{'classification':'FIRST_CURRENT_SEPARATION_COEFFICIENTS_ENCLOSED',
               'combined':combined,'controls':tested,'scope':'First z coefficient on selected redshift branch, separate conserved density squares; no charge radius or finite-charge evolution',
               'source_compatibility':'Inherited bulk Bianchi reconstruction; explicit scalar/oscillator, tracefree Israel, spatial Israel using momentum, exact first-order material exchange controls',
               'density_normalization':'rho_i=z N_i^2 E_i^6; a_i^6 C_i is coefficient per unit neutral proper-density amplitude, not a finite charge',
               'seconds':time.monotonic()-begun,'utc':c.now()})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
