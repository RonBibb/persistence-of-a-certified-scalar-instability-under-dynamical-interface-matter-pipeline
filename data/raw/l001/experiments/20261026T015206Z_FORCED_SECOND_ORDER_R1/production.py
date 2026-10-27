"""Conditional full forced solve. Requires separate production admission."""
import sys
sys.dont_write_bytecode=True
import time
from fractions import Fraction as Q
from pathlib import Path
import probe as c
ROOT=Path(__file__).resolve().parent

def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def flow(name):
    from flint import arb,fmpq
    m=c.load('production_'+name,ROOT/(name+'.py'));wall=c.load('production_wall_'+name,ROOT/'wall.py')
    y,p,inputs=c.initial(m,name);start=time.monotonic();lower=m.physical(y)
    dlo,dhi=map(fmpq,inputs['D']);D=m.interval(dlo,dhi)
    h=fmpq(2,8192 if name=='primary' else 16384);count=(Q(str(dhi))/Q(str(h))).__ceil__()
    totals={key:arb(0) for key in ('p1','p2P','p2H','c2','p1sq','transport')}
    budgets=[];cover=[];endpoint=None;maxpic=0
    lowwall=wall.reconstruct(lower,p,1,1)
    # Lower-current direction has xi_b,1=0 exactly.
    xp=-lowwall['xi']/D
    def exported(v):
        lo,hi=map(lambda x:Q(str(x)),m.bounds(v));scale=1<<80
        a=Q((lo*scale).__floor__(),scale);b=Q((hi*scale).__ceil__(),scale)
        c.need(a<=lo<=hi<=b,'OUTWARD_BUDGET')
        return {'exact_bounds':[str(a),str(b)]},m.interval(fmpq(str(a)),fmpq(str(b)))
    for j in range(count):
        c.need(time.monotonic()-start<1700,'ENGINE_OPERATIONAL_CAP')
        pos=j*h;y,cell=m.step(y,h,p);z=m.physical(cell['box']);maxpic=max(maxpic,cell['picard_iterations'])
        c.need(all(v.is_finite() for v in y+cell['box']),'FINITE_FLOW')
        c.need(all(c.zero(v) for v in m.constraints(cell['box'],p).values()),'WHOLE_CONSTRAINTS')
        c.need(c.zero(m.first_integral(cell['box'],p)),'WHOLE_BACKGROUND')
        W,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=z
        c.need(E.lower()>0,'POSITIVE_WARP')
        sc=m.sources(cell['box'],p);c2=sc[3] if name=='primary' else sc['c2']
        X=lowwall['xi']+xp*m.interval(pos,pos+h);u=-2*H*a-T*f/3
        den=dict(p1=a,p2P=ap,p2H=ah,c2=c2,p1sq=a*a,transport=X*(-2*u)+xp*(-2*a))
        mandatory=max(fmpq(0),min(h,dlo-pos));optional=max(fmpq(0),min(h,dhi-pos))-mandatory
        row={'index':j,'s':str(pos),'step':str(h),'mandatory':str(mandatory),'optional':str(optional),'budgets':{}}
        for key,density in den.items():
            raw,re=exported(density*mandatory+density*m.interval(fmpq(0),optional))
            row['budgets'][key]=raw;totals[key]+=re
        budgets.append(row)
        if pos+h>=dlo and pos<=dhi:
            aoff=max(fmpq(0),dlo-pos);boff=min(h,dhi-pos)
            event=m.physical(m.range_on_cell(cell,aoff,boff))
            endpoint=event if endpoint is None else [m.hull(a,b) for a,b in zip(endpoint,event)]
            cover.append({'lo':str(pos+aoff),'hi':str(pos+boff)})
        if j%128==0:print(name,'cell',j,'/',count,flush=True)
    last=Q(str(dlo))
    for piece in cover:c.need(Q(piece['lo'])==last,'COVER_GAP');last=Q(piece['hi'])
    c.need(last==Q(str(dhi)),'COVER_END')
    highwall=wall.reconstruct(endpoint,p,-1,0)
    def ball(record):return m.interval(*map(fmpq,record['exact_bounds']))
    parent=c.read(c.PARENT/'T10_AB_CURRENT_RADAR_RESPONSE/output'/('current_radar_'+name+'.json'))
    ch=parent['full_forced_assembly']['channels']['lower']
    loads=c.read(c.PARENT/'T18_AB_COMPLETE_QUADRATIC_WALL_SOURCE_QUALIFICATION/RESULT.json')['per_engine'][name]['lower']
    graphs=c.read(c.PARENT/'T17_AB_COMPLETE_QUADRATIC_GRAPH_SUBSYSTEM/RESULT.json')['per_engine'][name]['lower']['walls']
    for side,w in (('lower',lowwall),('upper',highwall)):
        for key in ('E','H','Phi','T','Tp','psi','f','g','chi','n','xi'):
            c.need(overlap(w[key],ball(ch['walls'][side][key])),'FIRST_WALL_REPLAY:'+side+':'+key)
        for key,parentkey in (('R2','undivided_Robin_load_Eulerian'),('o2','o2_Eulerian'),('j2','j2_Eulerian')):
            c.need(overlap(w[key],ball(loads[side][parentkey])),'SECOND_LOAD_REPLAY:'+side+':'+key)
        c.need(overlap(w['xi2'],ball(graphs[side]['values']['xi_second'])),'GRAPH_REPLAY:'+side)
    d1=highwall['xi']-lowwall['xi']-2*totals['p1']
    c.need(overlap(d1,ball(ch['coefficient_total'])),'FIRST_DISTANCE_REPLAY')
    W,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=endpoint
    G=highwall['Gamma2'];FH=gh+2*T*ah+G*fh/2;FP=gp+2*T*ap+G*fp/2
    c.need(not c.zero(FH),'UPPER_INVERSE_ZERO')
    t20=c.read(c.PARENT/'T20_AB_SECOND_HARMONIC_HOMOGENEOUS_INVERSE/output'/(name+'.json'))
    c.need(overlap(FH,ball(t20['endpoint']['F'])),'HOMOGENEOUS_PARENT_REPLAY')
    # Bind the original full T18 upper load; fresh reconstructed load is checked
    # above and retained as evidence, never intersected with the bound input.
    Rb=ball(loads['upper']['undivided_Robin_load_Eulerian'])
    A2=(-Rb/2-FP)/FH
    walls={}
    for side,z,w,sigma in (('lower',lower,lowwall,1),('upper',endpoint,highwall,-1)):
        full=z[:8]+[z[i]+A2*z[i+3] for i in (8,9,10)]+z[11:]
        residual=wall.residuals(full,w,p,sigma)
        c.need(all(c.zero(v) for v in residual['rows'].values()),'PHYSICAL_WALL_ROWS:'+side)
        bridge=wall.pullback_bridge(full,w,sigma,xp)
        c.need(all(c.zero(v) for v in bridge['rows'].values()),'WALL_CHART_BRIDGE:'+side)
        walls[side]={'state':[c.pack(v) for v in full],'fresh':{k:c.pack(v) for k,v in w.items()},
                     'rows':{k:c.pack(v) for k,v in residual['rows'].items()},'chi2':c.pack(residual['chi2'])}
    graph=highwall['xi2']-lowwall['xi2']
    endpoint_transport=-2*endpoint[5]*highwall['xi']+2*lower[5]*lowwall['xi']
    c.need(overlap(totals['transport'],endpoint_transport),'INTEGRATED_CHART_PRODUCT_RULE')
    bulk=-2*(totals['p2P']+A2*totals['p2H'])+totals['c2']+2*totals['p1sq']
    d2=graph+bulk+endpoint_transport;pulled=graph+bulk+totals['transport']
    c.need(overlap(d2,pulled),'COMPLETE_CHART_DISTANCE')
    result={'engine':name,'seconds':time.monotonic()-start,'cells':count,'step':str(h),'cover':cover,
            'max_picard_iterations':maxpic,'all_gates':True,'inputs':inputs,'walls':walls,
            'A2':c.pack(A2),'FH':c.pack(FH),'FP':c.pack(FP),'Rb_bound':c.pack(Rb),
            'raw_lower':[c.pack(v) for v in lower],'raw_upper':[c.pack(v) for v in endpoint],
            'parameters':{k:c.pack(v) for k,v in p.items()},
            'd1':c.pack(d1),'d2':c.pack(d2),'pulled_d2':c.pack(pulled),
            'graph':c.pack(graph),'bulk':c.pack(bulk),'endpoint_transport':c.pack(endpoint_transport),
            'totals':{k:c.pack(v) for k,v in totals.items()},'budgets':budgets}
    c.put('PRODUCTION_'+name+'.json',result);return result

def run():
    c.need(sys.platform=='linux','LINUX_ONLY')
    from flint import fmpq
    results={name:flow(name) for name in ('primary','independent')}
    m=c.load('production_hull',ROOT/'primary.py')
    values=[m.interval(*map(fmpq,r['d2']['exact_bounds'])) for r in results.values()]
    c.need(overlap(*values),'ENGINE_DISTANCE_DISAGREEMENT')
    hull=m.hull(*values);sign=1 if hull.lower()>0 else -1 if hull.upper()<0 else 0
    result={'classification':'SECOND_ORDER_OPPOSES_SHORTENING' if sign>0 else 'SECOND_ORDER_REINFORCES_SHORTENING' if sign<0 else 'SECOND_ORDER_SIGN_UNRESOLVED',
            'd2':c.pack(hull),'sign':sign,'all_gates':True,'independent_terminal_audit_pending':True,
            'scope':'One lower-unit-current formal second-order coefficient; not finite-charge saturation or evolution stability.'}
    c.put('PRODUCTION_RESULT.json',result);return result
