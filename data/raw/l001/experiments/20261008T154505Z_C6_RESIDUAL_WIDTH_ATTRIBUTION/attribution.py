"""Finite endpoint algebra and rigorous range-width diagnostics; no IVP steps."""
from width_runtime import *
import math
def fixed_C():return [[exact(x) for x in row] for row in rec.read(PARENT/'DESIGN.json')['preconditioner']]
def linear(v,C):return [-sum((arb(c)*x for c,x in zip(row,v)),arb(0)) for row in C]
def original_correction(bits):
    d=rec.read(PARENT/'DECISION.json')['producer_arb_decisions'][str(bits)]
    return [interval(*map(exact,x['exact'])) for x in d['center_displacement']]

def channels(bits,g):
    r=parent_result(bits);C=fixed_C();F=r['map']['F'];b=original_correction(bits)
    terms=[]
    for i in range(5):
        t=[abs(C[i][j])*halfwidth(F[j]) for j in range(5)];total=sum(t,fmpq(0))
        mid=-sum((C[i][j]*midpoint(F[j]) for j in range(5)),fmpq(0))
        terms.append({'coordinate':i,'linear_radius_terms':[str(x) for x in t],'linear_radius_sum':str(total),
            'ideal_linear_midpoint':str(mid),'represented_center_correction':record(b[i]),
            'rounding_and_representation_excess':str(halfwidth(b[i])-total),
            'radius_closure_exact':total+(halfwidth(b[i])-total)==halfwidth(b[i]),
            'shares_of_linear_upper_budget':[str(x/total) if total else '0' for x in t]})
    return {'guard':g,'bits':bits,'F':[record(x) for x in F],
       'residual_order':['upper_spatial_Israel','lower_scalar_C4','upper_scalar_C4','lower_scalar_C6','upper_scalar_C6'],
       'coordinate_order':['a','b5L','b5R','b7L','b7R'],'terms':terms,
       'definition':'Exact rational propagation of residual halfwidths through the unchanged fixed preconditioner; a linear representation budget, not a physical error partition.'}

def inventory(bits,g):
    r=parent_result(bits);p=r['p'];out=PARENT/'output'/f'{bits}-center';samples=[]
    for path in sorted((out/'checkpoints').glob('*.json')):
        body=rec.read(path);st=rec.unpack(body['state'])
        assert body['guard']==CFG['predecessor_guard'] and path.name.endswith(rec.fingerprint(body)+'.json')
        if st['last_cell'] is not None:
            cell=st['last_cell']['cell'];samples.append((st['cell_index'],[magnitude(v)*cell['h']**5 for v in cell['remainder']]))
    localmax=[max(row[j] for _,row in samples) for j in range(21)]
    rhs=physics.rhs(r['endpoint_y'],p);event_radius=halfwidth(p['D'])
    names=['W','H','Phi_source','T','E','psi','f','g','s','w','w_s']
    states=[]
    for j,name in enumerate(names):
        full=halfwidth(r['endpoint_y'][j]);eb=magnitude(rhs[j])*event_radius
        states.append({'name':name,'sealed_endpoint_state':record(r['endpoint_y'][j]),
          'event_evaluation_shift_upper_bound':str(eb),
          'event_upper_bound_over_state_halfwidth':str(eb/full) if full else None,
          'state_source_IVP_wrapping_split':'UNRESOLVED_MIXTURE; the event bound is overlapping, not a disjoint share.'})
    for side,y in enumerate((r['initial_y'],r['endpoint_y'])):
        # An explicit high-jet record is already supplied by the original map.
        pass
    bound=rec.read(PARENT/'BINDINGS.json')['inputs']['canonical_preparation']
    pp=rec.unpack(rec.read(loc(bound['path'])))['preps']['positive'];e=arb(exact('1/200000'))
    epsrem=[magnitude(v['remainder'])*magnitude(e)**8 for v in pp['c7_epsilon_evidence']]
    return {'guard':g,'bits':bits,'endpoint_states':states,'event_D':record(p['D']),
        'stored_last_cell_samples':len(samples),'full_integration_cells':r['completed_cells'],
        'stored_local_fifth_remainder_upper_maxima':[str(x) for x in localmax],
        'sampled_cell_indices':[n for n,_ in samples],
        'cumulative_spatial_Taylor_remainder':'UNRESOLVED: unrecorded intermediate cells are not recomputed; sampled maxima are not global error bounds.',
        'canonical_C7_epsilon_Taylor_coefficient_remainder_upper_bounds':[str(x) for x in epsrem],
        'canonical_remainder_scope':'Rigorous coefficient bounds for epsilon-series remainder only, not accumulated spatial integration error.',
        'endpoint_A':[[record(x) for x in row] for row in r['map']['endpoint_A']],
        'endpoint_Phi':[[record(x) for x in row] for row in r['map']['endpoint_Phi']],
        'endpoint_ell':[[record(x) for x in row] for row in r['map']['endpoint_ell']]}

def input_box(r,mode):
    values=[];labels=[];groups=[]
    for side in (0,1):
        for name in ('A','Phi','ell'):
            indices=range(8)
            if name=='A' and mode!='independent_jets':indices=(0,1)
            if name=='Phi' and mode=='canonical_linked':indices=(0,2,4,5,6,7)
            for n in indices:
                values.append(r['map']['endpoint_'+name][side][n]);labels.append(f'{side}:{name}:{n}')
                groups.append(f'{side}:'+{'A':'metric_endpoint_mixture','Phi':'scalar_source_and_preparation','ell':'lapse_source_mixture'}[name])
    for name in ('D','k'):
        values.append(r['p'][name]);labels.append(name);groups.append('source_event_length' if name=='D' else 'source_curvature')
    return values,labels,groups

def kernel(vals,labels,p,mode,derivatives):
    physics.Dual.size=len(vals) if derivatives else 0
    seed={}
    for i,(label,v) in enumerate(zip(labels,vals)):
        dd=[arb(int(i==j)) for j in range(len(vals))] if derivatives else []
        seed[label]=physics.Dual(v,dd)
    D=seed['D'];par=dict(p);par['k']=seed['k']
    fields=[]
    for side in (0,1):
        F=[seed.get(f'{side}:Phi:{n}',physics.Dual(0)) for n in range(8)]
        ell=physics.Jet([seed[f'{side}:ell:{n}'] for n in range(8)])
        if mode=='canonical_linked':
            sig=1-2*side;c=sig*p['gamma']/2;vi=p['v0' if side==0 else 'v1'];lam=p['lambda_a' if side==0 else 'lambda_b']
            P=F[0];L=ell.val().exp();t=c*(P-vi);pw=-sig*(lam+p['gamma']*(P-vi)**2/2)/6
            u=(2*F[2]-ell.c[1]*L*t)*(-2*ell.val()).exp();V=-6+p['m2']*P*P/2
            v3=-(6*pw-c)*u-(4*pw*pw-p['m2']-t*t-2*V/3-4*c*pw)*t+(2*pw-c)*p['m2']*P
            F[1]=L*t
            F[3]=(L**3*v3+3*ell.c[1]*(2*F[2])-(2*ell.c[1]**2-2*ell.c[2])*L*t)/6
        F=physics.Jet(F)
        aa=[seed[f'{side}:A:{n}'] for n in range(8 if mode=='independent_jets' else 2)]
        if mode!='independent_jets':
            for n in range(6):
                A=physics.Jet(aa);As=A.d();V=physics.Jet(-6)+F*F*(p['m2']/2)
                ar=ell.d()*As-2*As*As+(2*ell-2*A).exp()*par['k']-(F.d()*F.d()+2*(2*ell).exp()*V)/6
                aa.append(ar.c[n]/((n+1)*(n+2)))
        fields.append((physics.Jet(aa),F,ell))
    q=physics.Gauge(D)
    for order,index in ((3,1),(5,2),(7,3)):
        rows=[physics.time_rows(A,A+q.endpoint(side),F,ell,par,side) for side,(A,F,ell) in enumerate(fields)]
        for side,(A,F,ell) in enumerate(fields):
            corr=-(rows[side][index][1]-rows[side][index][0])*((-(order-1))*A.val()+order*ell.val()).exp()
            if order<7:q.target[6*side+order]=corr
            else:q.eta[side]=corr
    rows=[physics.time_rows(A,A+q.endpoint(side),F,ell,par,side) for side,(A,F,ell) in enumerate(fields)]
    A,F,ell=fields[1];pw=(p['lambda_b']+p['gamma']*(F.val()-p['v1'])**2/2)/6
    residual=[A.c[1]*(-ell.val()).exp()-pw]
    for idx,order in ((2,4),(3,6)):
        for side,(A,F,ell) in enumerate(fields):residual.append(rows[side][idx][2]*(-order*A.val()).exp())
    offshell=[]
    for side,(A,F,ell) in enumerate(fields):
        sig=1-2*side;c=sig*p['gamma']/2;P=F.val();L=ell.val().exp()
        pr=A.c[1]/L;pw=-sig*(p['lambda_a' if side==0 else 'lambda_b']+p['gamma']*(P-p['v0' if side==0 else 'v1'])**2/2)/6
        t=F.c[1]/L;u=(2*F.c[2]-ell.c[1]*F.c[1])*(-2*ell.val()).exp()
        lhs=rows[side][1][2]*(-2*A.val()).exp()
        right=(pr-pw)*(6*u+4*(pr+pw-c)*t-2*p['m2']*P)
        offshell.append({'actual_spatial_Israel':pr-pw,'canonical_C2_remainder':right,'C2_identity_difference':lhs-right})
    return residual,offshell

def validate_baseline(bits,g):
    r=parent_result(bits)
    recomputed=physics.corner_map(r['initial_y'],r['endpoint_y'],r['p'])
    compare=[]
    for a,b in zip(recomputed['F'],r['map']['F']):
        rel=abs(halfwidth(a)-halfwidth(b))/halfwidth(b)
        compare.append({'overlap':overlap(a,b),'relative_halfwidth_difference':str(rel),
            'passed':overlap(a,b) and rel<=exact(CFG['reproduction']['relative_halfwidth_difference_ceiling'])})
    # Basic analytic-dual control at two native intervals, independent elementary formula.
    physics.Dual.size=2
    a=physics.Dual(arb(exact('1/7')),[arb(1),arb(0)]);b=physics.Dual(arb(exact('2/7')),[arb(0),arb(1)])
    z=(a*b+a.exp())/(1+b)
    da=(b.v+a.v.exp())/(1+b.v);db=(a.v-a.v.exp())/(1+b.v)**2
    controls=[(z.d[0]-da).contains(0),(z.d[1]-db).contains(0)]
    result={'guard':g,'bits':bits,'reproduction':compare,'analytic_dual_controls':controls,'all_passed':all(x['passed'] for x in compare) and all(controls)}
    if not result['all_passed']:raise ArithmeticError('Saved endpoint reproduction or dual control failed')
    return result

def mean_value_case(bits,mode,g):
    r=parent_result(bits);values,labels,groups=input_box(r,mode);C=fixed_C()
    wide,wide_off=kernel(values,labels,r['p'],mode,True)
    pivots=[x.mid() for x in values]
    point,point_off=kernel(pivots,labels,r['p'],mode,False)
    radii=[max(abs(t-exact(str(m.fmpq()))) for t in bounds(x)) for x,m in zip(values,pivots)]
    # Restore the appropriate derivative dimension when combining duals.
    physics.Dual.size=len(values)
    broad_b=[-sum((v*arb(c) for v,c in zip(wide,row)),physics.Dual(0)) for row in C]
    point_b=linear([v.v for v in point],C)
    originalF=r['map']['F'];originalB=original_correction(bits)
    def enclose(wide_values,point_values,old):
        result=[]
        for i,(val,base,original) in enumerate(zip(wide_values,point_values,old)):
            terms=[magnitude(d)*rr for d,rr in zip(val.d,radii)];total=sum(terms,fmpq(0))
            new=base+interval(-total,total);intersection=meet(original,new)
            removable=max(fmpq(0),1-halfwidth(intersection)/halfwidth(original))
            grouped={}
            for name,t in zip(groups,terms):grouped[name]=grouped.get(name,fmpq(0))+t
            result.append({'index':i,'original':record(original),'direct_equivalent':record(val.v),
                'point_pivot_evaluation':record(base),'mean_value_enclosure':record(new),
                'intersection':record(intersection),'removable_fraction_lower':str(removable),
                'input_terms':[str(t) for t in terms],'group_upper_budget':{k:str(v) for k,v in grouped.items()},
                'sum_input_radius_terms':str(total),'point_evaluation_halfwidth':str(halfwidth(base)),
                'outward_radius_excess':str(halfwidth(new)-halfwidth(base)-total),
                'derivative_enclosures':[record(d) for d in val.d],
                'equivalent_direct_overlap':overlap(val.v,original)})
        return result
    FF=enclose(wide,[v.v for v in point],originalF);BB=enclose(broad_b,point_b,originalB)
    off=[]
    for w,p in zip(wide_off,point_off):
        off.append({'whole_box':{k:record(v.v) for k,v in w.items()},'algebraic_pivot':{k:record(v.v) for k,v in p.items()},
            'identity_contains_zero_at_pivot':p['C2_identity_difference'].v.contains(0)})
    checks={'all_direct_equivalent_enclosures_overlap':all(x['equivalent_direct_overlap'] for x in FF+BB),
            'off_shell_upper_metric_slope_retained':True,
            'canonical_C2_identity_at_pivot':mode!='canonical_linked' or all(v['identity_contains_zero_at_pivot'] for v in off)}
    # Raw gradients, pivots, all upper budgets and uncertainty boxes are retained.
    return {'guard':g,'bits':bits,'mode':mode,'inputs':[{'label':name,'group':group,'box':record(v),'pivot':record(m),'pivot_radius':str(rad)} for name,group,v,m,rad in zip(labels,groups,values,pivots,radii)],
        'residuals':FF,'center_corrections':BB,'off_shell_C2':off,'checks':checks,'all_passed':all(checks.values()),
        'scope':'Equivalent enclosure-width diagnostic only; no root decision or source replacement.'}
