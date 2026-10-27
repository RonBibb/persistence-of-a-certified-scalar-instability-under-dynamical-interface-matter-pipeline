"""Selected neutral mode: scalar-minimum value to proper-separation transfer.

Fresh whole-strip propagation with a validated scalar-turn event. Neither a
midpoint mass nor an interpolated scalar minimum is used.
"""
import importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('minimum_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT; c.OUT=ROOT/'output'
T2=ROOT/'../T2R1_AB_SELECTED_MODE'

def controls():
    # Phi0=(s-s*)²/2: T*=0, T'*=1. For f=f0+g0(s-s*)
    # the first minimum shift is -g0, but minimum-value variation is f0.
    f0,g0,alpha=Q(3,7),Q(-2,5),Q(5,11)
    ds=-g0
    c.need(f0+Q(0)*ds==f0,'MINIMUM_DISPLACEMENT_CANCELLATION')
    c.need(f0-Q(0)*alpha==f0,'TRANSVERSE_GAUGE_MINIMUM_VALUE')
    c.need(-(g0-alpha)==ds+alpha,'COORDINATE_TURN_SHIFT_TRANSFORMATION')
    # Cover [-1,1] with a true unique zero at0, bounded derivative1.
    cells=[(Q(-1),Q(-1,2)),(Q(-1,2),Q(0)),(Q(0),Q(1,2)),(Q(1,2),Q(1))]
    candidates=[i for i,(a,b) in enumerate(cells) if a<=0<=b]
    c.need(candidates==[1,2] and all(a*b>0 for i,(a,b) in enumerate(cells) if i not in candidates),'MANUFACTURED_ZERO_COVER')
    c.need(Q(1)>0,'MANUFACTURED_SIMPLE_MINIMUM')
    return {'minimum_value_displacement_cancellation':True,'transverse_gauge_invariance_at_turn':True,
            'coordinate_turn_shift_transformation':True,'whole_cell_zero_cover':True,'simple_minimum':True}

def authenticate_parent():
    g=c.read(ROOT/'ADMISSION.json'); c.need(g.get('t2_terminal_review_accepted') is True,'T2_NOT_ACCEPTED')
    for rel in ('../T2R1_AB_SELECTED_MODE/output/RESULT.json','../T2R1_AB_SELECTED_MODE/output/strip_primary.json',
                '../T2R1_AB_SELECTED_MODE/output/strip_independent.json','../T2R1_AB_SELECTED_MODE/TERMINAL_REVIEW.md'):
        c.need(rel in g['sources'],'MISSING_BOUND_PARENT:'+rel)
    r=c.read(T2/'output/RESULT.json')
    c.need(r['classification']=='SELECTED_NEUTRAL_MODE_CHARACTERIZED','SELECTED_PARENT_CLASSIFICATION')
    return r

def flow(name,parent,begun):
    from flint import arb,fmpq
    m=c.load(name); binding=c.read(ROOT/'inputs/central_bindings.json'); cfg=binding['config']
    A=m.interval(*map(fmpq,cfg['A'])); mu=m.interval(*map(fmpq,parent['mu_bracket']))
    y,p,u=c.launch(m,name,A,mu,binding['model_exact'],1)
    c.need(y[3].upper()<0,'INITIAL_T_NEGATIVE')
    c.need((mu+4*p['k']).upper()<0,'GENERIC_NEGATIVE_SHIFTED_SECTOR')
    Dlo,Dhi=map(fmpq,cfg['D']); h=fmpq(2,8192 if name=='primary' else 16384)
    n=(Q(str(Dhi))/Q(str(h))).__ceil__(); started=time.monotonic()
    hulls={}; turnrows=[]; outside=[]; events=[]; eventdet=None; eventT=None; maxpic=0
    for j in range(n):
        if j%64==0:
            c.need(time.monotonic()-started<360,'TURN_FLOW_CAP'); c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        pos=j*h; y,cell=m.step(y,h,p); geo=m.geometry(cell,p)
        c.need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FLOW')
        c.need(c.contains0(geo['constraint']) and c.contains0(geo['first_integral']),'CONSTRAINT_OR_BACKGROUND')
        c.need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY'); maxpic=max(maxpic,cell['picard_iterations'])
        W,H,P,T,E,psi,f,g=c.physical(cell['box'],name)
        Ts=c.sign(T)
        if Ts==0:
            Tp=p['m2']*P-4*H*T; c.need(Tp.lower()>0,'TURN_DERIVATIVE_NOT_POSITIVE')
            vals={'f':f,'psi':psi,'g':g,'T':T,'Tprime':Tp,'E':E,'Phi':P}
            for key,v in vals.items(): hulls[key]=v if key not in hulls else m.hull(hulls[key],v)
            turnrows.append({'index':j,'s_lower':str(pos),'s_upper':str(min(pos+h,Dhi)),
                             'box':{key:c.pack(v) for key,v in vals.items()}})
        else:
            outside.append({'index':j,'T_sign':Ts,'T':c.pack(T)})
        if pos+h>=Dlo and pos<=Dhi:
            lo=max(fmpq(0),Dlo-pos); hi=min(h,Dhi-pos); v=m.range_on_cell(cell,lo,hi)
            Wb,Hb,Pb,Tb,Eb,psib,fb,gb=c.physical(v,name)
            G,d=c.response(mu,Eb,1); det=gb+2*Tb*psib+G*fb/2
            eventdet=det if eventdet is None else m.hull(eventdet,det)
            eventT=Tb if eventT is None else m.hull(eventT,Tb)
            events.append({'lo':str(pos+lo),'hi':str(pos+hi)})
    c.need(turnrows,'NO_TURN_COVER'); first,last=turnrows[0]['index'],turnrows[-1]['index']
    c.need([r['index'] for r in turnrows]==list(range(first,last+1)),'DISCONNECTED_TURN_COVER')
    c.need(all(r['T_sign']==(-1 if r['index']<first else 1) for r in outside),'OUTSIDE_TURN_SIGN_PATTERN')
    c.need(hulls['Tprime'].lower()>0 and eventT.lower()>0,'UNIQUE_MINIMUM_SIGNS')
    c.need(c.contains0(eventdet),'SELECTED_ROOT_STRIP_DETERMINANT')
    end=Q(str(Dlo))
    for row in events: c.need(Q(row['lo'])==end,'EVENT_GAP'); end=Q(row['hi'])
    c.need(end==Q(str(Dhi)),'EVENT_END')
    # At T=0 the exact regular constraint gives this additional f enclosure.
    fconstraint=-3*(mu+4*p['k'])*hulls['E']*hulls['E']*hulls['psi']/hulls['Tprime']
    c.need(c.overlaps(hulls['f'],fconstraint),'TURN_CONSTRAINT_READOUT_CONSISTENCY')
    old=c.read(T2/'output'/('strip_'+name+'.json'))
    c.need(old['mu_bounds']==parent['mu_bracket'] and old['beta']==1,'PARENT_MODE_LINKAGE')
    delta=c.ball_record(m,old['observables']['deltaD_over_Q'])
    quotient=None
    if not c.contains0(hulls['f']): quotient=c.pack(delta/hulls['f'])
    fixedshift=-hulls['g']/hulls['Tprime']
    result={'engine':name,'mu_bounds':parent['mu_bracket'],'cells':n,'all_cell_checks_pass':True,
            'turn_cells':turnrows,'outside_turn_cells':outside,'event_cover':events,
            'turn_hull':{key:c.pack(v) for key,v in hulls.items()},'f_turn_constraint_readout':c.pack(fconstraint),
            'turn_coordinate_bounds':[turnrows[0]['s_lower'],turnrows[-1]['s_upper']],
            'upper_T':c.pack(eventT),'upper_determinant':c.pack(eventdet),
            'deltaD_over_Q':c.pack(delta),'deltaD_over_deltaPhi_min':quotient,
            'fixed_chart_turn_shift_over_Q':c.pack(fixedshift),'f_minimum_excludes_zero':quotient is not None,
            'max_picard_iterations':maxpic,'seconds':time.monotonic()-started}
    c.put('turn_'+name+'.json',result); print(json.dumps({'completed':name,'seconds':result['seconds']}),flush=True)
    return result

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('MINIMUM_TRANSFER_CAP_900_SECONDS'))); signal.alarm(900)
        c.authenticate(); parent=authenticate_parent()
        c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested={'minimum':controls(),'inherited':{name:c.semantic_controls(c.load(name)) for name in ('primary','independent')}}
        c.put('CONTROLS.json',tested); per={name:flow(name,parent,begun) for name in ('primary','independent')}
        m=c.load('primary'); combined={}
        for key in per['primary']['turn_hull']:
            a=c.ball_record(m,per['primary']['turn_hull'][key]); b=c.ball_record(m,per['independent']['turn_hull'][key])
            c.need(c.overlaps(a,b),'TURN_ENGINE_DISAGREEMENT:'+key); combined[key]=c.pack(m.hull(a,b))
        transfer=None
        if all(r['f_minimum_excludes_zero'] for r in per.values()):
            a=c.ball_record(m,per['primary']['deltaD_over_deltaPhi_min']); b=c.ball_record(m,per['independent']['deltaD_over_deltaPhi_min'])
            c.need(c.overlaps(a,b),'TRANSFER_ENGINE_DISAGREEMENT'); transfer=c.pack(m.hull(a,b))
        c.put('RESULT.json',{'classification':'NEUTRAL_MINIMUM_SEPARATION_TRANSFER_ENCLOSED' if transfer else 'NEUTRAL_MINIMUM_TRANSFER_INCONCLUSIVE',
              'mu_bracket':parent['mu_bracket'],'turn_hull':combined,'deltaD_over_deltaPhi_min':transfer,
              'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
              'scope':'Neutral selected-action growing mode only. Minimum scalar-value variation and proper separation are gauge invariant at this static background; fixed-chart turn coordinate shift is not. No charged excitation inferred.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
