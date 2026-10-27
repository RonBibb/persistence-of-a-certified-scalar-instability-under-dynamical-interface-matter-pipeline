"""Physical-minimum partition of first-current proper distance.

Fresh frozen T4 basis flows with a validated background-turn event and signed
uncertain-cutoff integrals. Only combined moving-endpoint lengths are physical
observables; metric and graph components separately depend on the chart.
"""
import importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('partition_basis',ROOT/'basis.py')
b=importlib.util.module_from_spec(s); s.loader.exec_module(b); c=b.c
c.ROOT=ROOT; c.OUT=ROOT/'output'; b.ROOT=ROOT
T4=ROOT/'../T4_AB_FIRST_CURRENT'

def controls():
    # Algebraic tests of complete moving-endpoint lengths and gauge shifts.
    pL,pR,xa,xb,xs=map(Q,('2/7','-3/11','4/13','-5/17','6/19'))
    left=-2*pL+xs-xa; right=-2*pR+xb-xs
    c.need(left+right==-2*(pL+pR)+xb-xa,'EXACT_PARTITION_SUM')
    aa,ab,astar=Q(3,5),Q(-2,3),Q(7,11)
    # b1=-2p changes by -alpha'; hence p integral gains alpha-difference/2.
    newL=-2*(pL+(astar-aa)/2)+(xs+astar)-(xa+aa)
    newR=-2*(pR+(ab-astar)/2)+(xb+ab)-(xs+astar)
    c.need(newL==left and newR==right,'MOVING_MINIMUM_GAUGE_CANCELLATION')
    f,g,Tp=Q(2,5),Q(-3,7),Q(11,13)
    shift=-g/Tp; c.need(f+Q(0)*shift==f,'MINIMUM_VALUE_DISPLACEMENT_CANCELLATION')
    c.need(-(g-Tp*astar)/Tp==shift+astar,'MINIMUM_COORDINATE_GAUGE')
    # Signed integral over [0,s*], s* in[1,2], and [s*,D], D in[3,4].
    c.need(Q(-3)*Q(1)>=Q(-3)*Q(2),'SIGNED_OPTIONAL_PREFIX_ORDER')
    return {'partition_sum':True,'moving_minimum_gauge_cancellation':True,
            'minimum_value_variation':True,'coordinate_minimum_transformation':True,'signed_optional_prefix':True}

def parent_gate():
    g=c.read(ROOT/'ADMISSION.json'); c.need(g.get('t4_terminal_review_accepted') is True,'T4_NOT_ACCEPTED')
    required=['../T4_AB_FIRST_CURRENT/TERMINAL_REVIEW.md','../T4_AB_FIRST_CURRENT/output/RESULT.json']
    required += ['../T4_AB_FIRST_CURRENT/output/assembled_'+n+'.json' for n in ('primary','independent')]
    for rel in required: c.need(rel in g['sources'],'MISSING_BOUND_PARENT:'+rel)
    c.need(c.read(T4/'output/RESULT.json')['classification']=='FIRST_CURRENT_SEPARATION_COEFFICIENTS_ENCLOSED','T4_SCOPE')

def flow(name,kind,begun):
    from flint import arb,fmpq
    m=c.load(name); binding=c.read(ROOT/'inputs/central_bindings.json'); cfg=binding['config']
    y,p=b.initial(m,name,binding,kind); lower=y[:]; c.need(y[3].upper()<0,'INITIAL_T_NEGATIVE')
    Dlo,Dhi=map(fmpq,cfg['D']); h=fmpq(2,8192 if name=='primary' else 16384)
    n=(Q(str(Dhi))/Q(str(h))).__ceil__(); started=time.monotonic()
    density_rows=[]; turns=[]; outside=[]; turnhulls={}; events={}; cover=[]; maxpic=0
    for j in range(n):
        if j%64==0:
            c.need(time.monotonic()-started<210,'PARTITION_FLOW_CAP'); c.need(time.monotonic()-begun<900,'TOTAL_CAP')
        pos=j*h; y,cell=m.step(y,h,p); geo=m.geometry(cell,p)
        c.need(all(v.is_finite() for v in y+list(geo.values())),'FINITE_FLOW')
        c.need(c.contains0(geo['constraint']) and c.contains0(geo['first_integral']),'CONSTRAINT_OR_BACKGROUND')
        c.need(geo['warp_squared'].lower()>0,'WARP_POSITIVITY'); maxpic=max(maxpic,cell['picard_iterations'])
        W,H,P,T,E,ps,f,g=c.physical(cell['box'],name); sg=c.sign(T)
        density_rows.append((pos,ps))
        if sg==0:
            Tp=p['m2']*P-4*H*T; c.need(Tp.lower()>0,'SIMPLE_TURN_DERIVATIVE')
            vals={'T':T,'Tprime':Tp,'f':f,'g':g,'psi':ps,'Phi':P}
            for key,v in vals.items(): turnhulls[key]=v if key not in turnhulls else m.hull(turnhulls[key],v)
            turns.append({'index':j,'s_lower':str(pos),'s_upper':str(min(pos+h,Dhi)),
                          'box':{key:c.pack(v) for key,v in vals.items()}})
        else: outside.append({'index':j,'T_sign':sg,'T':c.pack(T)})
        if pos+h>=Dlo and pos<=Dhi:
            lo=max(fmpq(0),Dlo-pos); hi=min(h,Dhi-pos); z=m.range_on_cell(cell,lo,hi)
            W,H,P,T,E,ps,f,g=c.physical(z,name); G,d=c.response(p['mu'],E,1)
            vals={'W':W,'H':H,'Phi':P,'T':T,'E':E,'psi':ps,'f':f,'g':g,'F':g+2*T*ps+G*f/2}
            for key,v in vals.items(): events[key]=v if key not in events else m.hull(events[key],v)
            cover.append({'lo':str(pos+lo),'hi':str(pos+hi)})
    c.need(turns and events['T'].lower()>0,'EXISTENCE_TURN_SIGNS')
    first,last=turns[0]['index'],turns[-1]['index']
    c.need([row['index'] for row in turns]==list(range(first,last+1)),'TURN_COVER_CONNECTED')
    c.need(all(r['T_sign']==(-1 if r['index']<first else 1) for r in outside),'OUTSIDE_TURN_SIGN_PATTERN')
    Slo,Shi=fmpq(turns[0]['s_lower']),fmpq(turns[-1]['s_upper'])
    c.need(fmpq(0)<Slo<=Shi<Dlo,'STRICT_INTERIOR_TURN')
    prev=Dlo
    for row in cover: c.need(fmpq(row['lo'])==prev,'WALL_EVENT_GAP'); prev=fmpq(row['hi'])
    c.need(prev==Dhi,'WALL_EVENT_END')
    sums={key:arb(0) for key in ('Ipsi','Ileft','Iright')}; budgets=[]
    for j,(pos,dens) in enumerate(density_rows):
        # Guaranteed core and all possible support of each uncertain interval.
        widths={
          'Ipsi':(max(fmpq(0),min(h,Dlo-pos)),max(fmpq(0),min(h,Dhi-pos))),
          'Ileft':(max(fmpq(0),min(h,Slo-pos)),max(fmpq(0),min(h,Shi-pos))),
          'Iright':(max(fmpq(0),min(pos+h,Dlo)-max(pos,Shi)),
                    max(fmpq(0),min(pos+h,Dhi)-max(pos,Slo)))}
        contributions={}; serialized={}
        for key,(mandatory,possible) in widths.items():
            c.need(0<=mandatory<=possible<=h,'UNCERTAIN_PARTITION_MEASURE')
            optional=possible-mandatory
            raw,back=c.dyadic_export(m,c.integral_piece(m,dens,mandatory,optional)); sums[key]+=back
            contributions[key]=raw; serialized[key]={'mandatory':str(mandatory),'optional':str(optional)}
        budgets.append({'index':j,'s':str(pos),'step':str(h),'widths':serialized,'contributions':contributions})
    c.need(c.overlaps(sums['Ileft']+sums['Iright'],sums['Ipsi']),'BASIS_PARTITION_SUM')
    filename=kind+'_'+name+'_BUDGET.json'
    c.put(filename,{'D_bounds':list(cfg['D']),'turn_bounds':[str(Slo),str(Shi)],'cells':budgets,
                    'reported_sums':{key:c.pack(v) for key,v in sums.items()},'dyadic_denominator_power':80})
    rec={'engine':name,'kind':kind,'mu':c.pack(p['mu']),'k':c.pack(p['k']),
         'lower_state':[c.pack(v) for v in lower],'upper':{key:c.pack(v) for key,v in events.items()},
         **{key:c.pack(v) for key,v in sums.items()},'event_cover':cover,'cells':n,'max_picard_iterations':maxpic,
         'all_cell_checks_pass':True,'seconds':time.monotonic()-started,'budget':{'path':filename,'sha256':c.sha(c.OUT/filename)},
         'turn_cells':turns,'outside_turn_cells':outside,'turn_hull':{key:c.pack(v) for key,v in turnhulls.items()},
         'turn_coordinate_bounds':[str(Slo),str(Shi)]}
    c.put(kind+'_'+name+'.json',rec); print(json.dumps({'completed':kind,'engine':name,'seconds':rec['seconds']}),flush=True)
    return rec

def assemble(name,H,P):
    from flint import arb,fmpq
    m=c.load(name); ball=lambda r:c.ball_record(m,r)
    full=b.combine(name,H,P); inherited=c.read(T4/'output'/('assembled_'+name+'.json'))
    HT={k:ball(v) for k,v in H['turn_hull'].items()}; PT={k:ball(v) for k,v in P['turn_hull'].items()}
    c.need(c.overlaps(HT['Tprime'],PT['Tprime']),'BASIS_TURN_BACKGROUND_OVERLAP')
    hpos=m.interval(*map(fmpq,H['turn_coordinate_bounds'])); ppos=m.interval(*map(fmpq,P['turn_coordinate_bounds']))
    c.need(c.overlaps(hpos,ppos),'BASIS_TURN_POSITION_OVERLAP')
    Tp=m.hull(HT['Tprime'],PT['Tprime']); c.need(Tp.lower()>0,'ASSEMBLED_SIMPLE_TURN')
    output={}
    for channel in ('lower','upper'):
        base=full['channels'][channel]; old=inherited['channels'][channel]
        amp=ball(base['homogeneous_multiplier']); Na=channel=='lower'
        f=amp*HT['f']+(PT['f'] if Na else arb(0)); g=amp*HT['g']+(PT['g'] if Na else arb(0))
        xi_star=-g/Tp
        c.need(c.contains0(Tp*xi_star+g),'PERTURBED_MINIMUM_CONDITION')
        IL=amp*ball(H['Ileft'])+(ball(P['Ileft']) if Na else arb(0))
        IR=amp*ball(H['Iright'])+(ball(P['Iright']) if Na else arb(0))
        xa=ball(base['walls']['lower']['xi']); xb=ball(base['walls']['upper']['xi'])
        left=-2*IL+xi_star-xa; right=-2*IR+xb-xi_star
        total=left+right; own_total=ball(base['coefficient_total']); parent_total=ball(old['coefficient_total'])
        c.need(c.overlaps(own_total,parent_total),'T4_TOTAL_REPRODUCTION')
        c.need(c.overlaps(total,own_total) and c.overlaps(total,parent_total),'PARTITION_TOTAL_RECONSTRUCTION')
        c.need(c.contains0(total-parent_total),'PARTITION_SUM_ZERO_RESIDUAL')
        a6=ball(base['source_wall_a6'])
        vals={'left_proper_length':left,'right_proper_length':right,'partition_sum':total,
              'parent_total':parent_total,'partition_sum_residual':total-parent_total,
              'minimum_scalar_value':f,'fixed_chart_minimum_shift':xi_star,'minimum_condition_residual':Tp*xi_star+g,
              'proper_density_left':a6*left,'proper_density_right':a6*right,
              'proper_density_minimum_scalar_value':a6*f}
        signs=[c.sign(left),c.sign(right)]
        classification='TWO_SIDED_SHORTENING' if signs==[-1,-1] else 'TWO_SIDED_LENGTHENING' if signs==[1,1] else 'OPPOSITE_SIGN_REDISTRIBUTION' if signs[0]*signs[1]==-1 else 'PARTITION_SIGNS_UNRESOLVED'
        output[channel]={'observables':{key:c.pack(v) for key,v in vals.items()},'left_right_signs':signs,'classification':classification}
    return {'engine':name,'channels':output,'full_forced_assembly':full}

def main():
    c.OUT.mkdir(exist_ok=True); c.need(not any((c.OUT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART')
    begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('MINIMUM_PARTITION_CAP_900_SECONDS'))); signal.alarm(900)
        c.authenticate(); parent_gate()
        c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        tested={'partition':controls(),'first_current':b.exact_controls(),
                'inherited':{n:c.semantic_controls(c.load(n)) for n in ('primary','independent')}}
        c.put('CONTROLS.json',tested); per={}
        for name in ('primary','independent'):
            H=flow(name,'homogeneous',begun); P=flow(name,'particular_lower',begun)
            per[name]=assemble(name,H,P); c.put('partition_'+name+'.json',per[name])
        m=c.load('primary'); combined={}
        for channel in ('lower','upper'):
            obs={}
            for key in per['primary']['channels'][channel]['observables']:
                a=c.ball_record(m,per['primary']['channels'][channel]['observables'][key]); d=c.ball_record(m,per['independent']['channels'][channel]['observables'][key])
                c.need(c.overlaps(a,d),'PARTITION_ENGINE_DISAGREEMENT:'+channel+':'+key); obs[key]=c.pack(m.hull(a,d))
            signs=[c.sign(c.ball_record(m,obs[key])) for key in ('left_proper_length','right_proper_length')]
            label='TWO_SIDED_SHORTENING' if signs==[-1,-1] else 'TWO_SIDED_LENGTHENING' if signs==[1,1] else 'OPPOSITE_SIGN_REDISTRIBUTION' if signs[0]*signs[1]==-1 else 'PARTITION_SIGNS_UNRESOLVED'
            combined[channel]={'observables':obs,'left_right_signs':signs,'classification':label}
        c.put('RESULT.json',{'classification':'FIRST_CURRENT_PHYSICAL_MINIMUM_PARTITION_ENCLOSED','combined':combined,
               'controls':tested,'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'First-current proper lengths to physical scalar minimum on specified redshift cuts. Fixed-chart minimum coordinate shift is not separately invariant. Negative coefficients are shorter offsets, not continuing contraction.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
