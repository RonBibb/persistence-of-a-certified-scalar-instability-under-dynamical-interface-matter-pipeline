"""Exact source/recurrence controls and two short validated augmented flows."""
import sys,json,time,resource
from pathlib import Path
from fractions import Fraction as Q
from flint import arb,fmpq
import adapters,sources
ROOT=Path(__file__).resolve().parent
PARENT=adapters.PARENT
SYSTEM=ROOT.parent/'20261026T025505Z_CUBIC_SYSTEM'
bulk=adapters.load('bound_cubic_bulk',SYSTEM/'bulk.py')
primary=adapters.primary();independent=adapters.independent()
ENGINES={'primary':primary,'independent':independent}
def read(p):return json.loads(Path(p).read_text())
def need(v,label):
    if not v:raise AssertionError(label)
def pack(v):
    need(v.is_finite(),'FINITE_EXPORT');return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def iv(r):return primary.interval(*map(fmpq,r['exact_bounds']))
def zero(v):return v.lower()<=0<=v.upper()
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def source_at(z,p):return adapters.cubic_from_canonical(z,p)
def initial(name):
    record=read(PARENT/('PRODUCTION_'+name+'.json'));z=list(map(iv,record['raw_lower']))
    params={k:iv(v) for k,v in record['parameters'].items()};params['A2']=iv(record['A2']);params['mu3']=-270*params['k']
    W,H,Phi,T,E=z[:5];k=params['k'];Tp=params['m2']*Phi-4*H*T
    load=iv(read(SYSTEM/'RESULT.json')['per_engine'][name]['lower']['R3'])
    s=source_at(z,params);bound=read(SYSTEM/'RESULT.json')['per_engine'][name]['lower']
    for key in ('Sc3','Sp3','Sg3'):need(overlap(s[key],iv(bound[key])),'ACCEPTED_LOWER_SOURCE:'+name+key)
    d3=2+270*k*E*E;need(d3.lower()>0,'D3_POSITIVE');Gamma=21-1/d3
    B=Gamma*T/2-Tp;need(not zero(B),'CUBIC_LAUNCH_DIVISOR')
    for v,sc,r in ((arb(0),s['Sc3'],load),(arb(1),arb(0),arb(0))):
        f=(sc-T*r/2+3*(params['mu3']+4*k)*E*E*v)/B
        g=Gamma*f/2+r/2-2*T*v;z.extend((v,f,g))
    rows={}
    for key,j,r in (('particular',14,load),('homogeneous',17,arb(0))):
        a,f,g=z[j:j+3];rows[key]=2*(g+2*T*a)-Gamma*f-r;need(zero(rows[key]),'LOWER_ROBIN:'+name+key)
    m=ENGINES[name];y=z if name=='primary' else z[:4]+z[5:]
    need(all(zero(v) for v in m.constraints(y,params).values()),'INITIAL_CONSTRAINTS:'+name)
    need(zero(m.first_integral(y,params)),'INITIAL_BACKGROUND:'+name)
    return y,params,{'launch_divisor':pack(B),'R3_lower':pack(load),'rows':{k:pack(v) for k,v in rows.items()},'D':record['inputs']['D']}
def controls():
    bulk.setup();b=bulk;checks=[]
    actual=sources.cubic(b.H,b.T,b.Phi,b.e,b.p,b.f,b.g,b.P,b.F,b.G,{'m2':b.m,'k':b.h*b.h})
    certified=read(SYSTEM/'RESULT.json')['bulk'];need(tuple(certified['variables'])==b.ring.NAMES,'POLYNOMIAL_VARIABLE_ORDER')
    for key,value in actual.items():
        expected=b.ring.P({tuple(row['powers']):Q(row['coefficient']) for row in certified['sources'][key]})
        need((value-expected).iszero(),'EXACT_CUBIC_SOURCE:'+key);checks.append('EXACT_CUBIC_SOURCE:'+key)
    y,p,launch=initial('primary');yi=y[:4]+y[5:]
    # Same exact interval input for cross-engine recurrence controls.
    cp=primary.coeff(y,5,p);ci=independent.coeff(yi,5,p)
    ei=independent.lower.exponential_coefficients([-v for v in ci[0]],5)
    ci=ci[:4]+[ei]+ci[4:]
    for j in range(20):
        for n in range(6):need(overlap(cp[j][n],ci[j][n]),'COEFFICIENT_OVERLAP:'+str(j)+':'+str(n));checks.append('COEFFICIENT_OVERLAP:'+str(j)+':'+str(n))
    for name,m in ENGINES.items():
        z,params,_=initial(name);n=14 if name=='primary' else 13
        low=m.lower.rhs(z[:n],params);new=m.rhs(z,params)[:n]
        for j,(a,v) in enumerate(zip(low,new)):
            need(a.lower()==v.lower() and a.upper()==v.upper(),'UNCHANGED_LOWER_RHS:'+name+str(j));checks.append('UNCHANGED_LOWER_RHS:'+name+str(j))
    return {'pass':True,'checks':checks,'launch_primary':launch,'scope':'Exact cubic source identity and same-input two-representation coefficient controls; no full-domain inverse.'}
def flow(name):
    m=ENGINES[name];y,p,launch=initial(name);start=time.monotonic();initial_y=list(y)
    count=64 if name=='primary' else 128;h=fmpq(2,8192 if name=='primary' else 16384);records=[];maxpic=0;maxwidths=[fmpq(0) for _ in y]
    for j in range(count):
        before=list(y);y,cell=m.step(y,h,p)
        need(all(v.is_finite() for v in y+cell['box']),'FINITE_CELL:'+name)
        constraints=m.constraints(cell['box'],p);need(all(zero(v) for v in constraints.values()),'WHOLE_CELL_CONSTRAINT:'+name+str(j))
        bg=m.first_integral(cell['box'],p);need(zero(bg),'WHOLE_CELL_BACKGROUND:'+name+str(j))
        rhsbox=m.rhs(cell['box'],p);maxpic=max(maxpic,cell['picard_iterations'])
        for k,v in enumerate(cell['box']):maxwidths[k]=max(maxwidths[k],v.upper().fmpq()-v.lower().fmpq())
        records.append({'index':j,'start':[pack(v) for v in before],'end':[pack(v) for v in y],'box':[pack(v) for v in cell['box']],'rhs_box':[pack(v) for v in rhsbox],
                        'point_coefficients':[[pack(v) for v in row] for row in cell['point_coefficients']],'remainder_coefficient':[pack(v) for v in cell['remainder_coefficient']],
                        'constraints':{k:pack(v) for k,v in constraints.items()},'background':pack(bg),'picard_iterations':cell['picard_iterations']})
        if j%16==15:print(name,j+1,'/',count,flush=True)
    seconds=time.monotonic()-start;full_cells=(Q(launch['D'][1])/Q(str(h))).__ceil__()
    final=m.physical(y)
    return {'pass':True,'engine':name,'cells':count,'step':str(h),'interval_length':str(h*count),'seconds':seconds,'max_picard_iterations':maxpic,
            'initial':[pack(v) for v in initial_y],'final':[pack(v) for v in y],'physical_final':[pack(v) for v in final],
            'parameters':{k:pack(v) for k,v in p.items()},'launch':launch,'records':records,
            'initial_widths':[str(v.upper().fmpq()-v.lower().fmpq()) for v in initial_y],'final_widths':[str(v.upper().fmpq()-v.lower().fmpq()) for v in y],'max_box_widths':[str(v) for v in maxwidths],
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'projected_full_cells':full_cells,'linear_work_projection_seconds':seconds*full_cells/count,
            'projection_is_not_full_domain_admission':True}
def run(save):
    need(sys.platform=='linux','LINUX_ONLY');c=controls();save('CONTROLS_RESULT.json',c)
    results={}
    for name in ENGINES:results[name]=flow(name);save('PROBE_'+name+'.json',results[name])
    for j,(a,b) in enumerate(zip(results['primary']['physical_final'],results['independent']['physical_final'])):
        need(overlap(iv(a),iv(b)),'PHYSICAL_ENDPOINT_OVERLAP:'+str(j))
    return {'pass':True,'classification':'CUBIC_SHORT_FLOW_FEASIBILITY_PASS','source_and_recurrence_checks':len(c['checks']),
            'arms':{name:{key:r[key] for key in ('cells','step','interval_length','seconds','max_picard_iterations','peak_rss_kib','linear_work_projection_seconds')} for name,r in results.items()},
            'combined_linear_work_projection_seconds':sum(r['linear_work_projection_seconds'] for r in results.values()),
            'scope':'Short validated cubic particular/homogeneous flows only. No upper inverse A3 or full d_sep3. Projection is not full-domain admission.'}
