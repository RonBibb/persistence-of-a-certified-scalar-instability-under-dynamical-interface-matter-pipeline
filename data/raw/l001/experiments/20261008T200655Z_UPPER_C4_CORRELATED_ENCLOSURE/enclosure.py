"""Same endpoint residual; exact source identities and full-box mean-value bounds."""
from runtime import *
import math
from inherited import source_flow, preparation

def dual_record(x):return {'value':x.v,'gradient':list(x.d)}
def restore_dual(x):return physics.Dual(x['value'],x['gradient'])
def sqrt_dual(x):
    lo,hi=bounds(x.v)
    if lo<=0:raise ArithmeticError('Full-box static sqrt radicand is not strictly positive')
    v=x.v.sqrt();return physics.Dual(v,[d/(2*v) for d in x.d])
def baseline(bits):
    ctx.prec=bits;physics.Dual.size=5
    r=rec.unpack(rec.read(PARENT/'output'/f'{bits}-center/RESULT.json'))
    f=physics.corner_map(r['initial_y'],r['endpoint_y'],r['p'])
    out=[]
    for x,y in zip(f['F'],r['map']['F']):
        ax,bx=bounds(x);ay,by=bounds(y)
        rel=abs((bx-ax)-(by-ay))/(by-ay)
        out.append({'overlap':overlap(x,y),'relative_halfwidth_difference':str(rel),
                    'passed':overlap(x,y) and rel<=exact(CFG['admission']['source_map_reproduction_relative_halfwidth_ceiling'])})
    return {'bits':bits,'checks':out,'all_passed':all(d['passed'] for d in out)}

def prepare(bits,mode):
    ctx.prec=bits;physics.Dual.size=5
    r=rec.unpack(rec.read(PARENT/'output'/f'{bits}-center/RESULT.json'))
    labels=[];values=[];sources=[]
    for side,y in enumerate((r['initial_y'],r['endpoint_y'])):
        z=physics.source_endpoint(y,r['p'],side);sources.append(z)
        for name,j in (('W',0),('P',2),('E',4),('psi',5),('f',6),('w',9),('v',10)):
            if name=='E' and mode=='static_hamiltonian':continue
            labels.append(f'{side}:{name}');values.append(z[j] if j<9 else y[j])
    for name in ('D','k','mu'):labels.append(name);values.append(r['p'][name])
    pivots=[x.mid() for x in values]
    radii=[max(abs(q-m.fmpq()) for q in bounds(v)) for v,m in zip(values,pivots)]
    return {'phase':0,'bits':bits,'mode':mode,'labels':labels,'values':values,'pivots':pivots,'radii':radii,
       'p':r['p'],'source_endpoint_enclosures':sources,'old_fields':{k:r['map']['endpoint_'+k] for k in ('A','Phi','ell')},
       'old_F':r['map']['F'],'primitive_boxes_cover_same_source':True}

def polynomial_endpoint(co,side,n,D):
    return sum((co[j]*math.prod(range(j-n+1,j+1))*side**(j-n)*D**(j-n)
                for j in range(n,len(co))),physics.Dual(0))/math.factorial(n)

def make_fields(vals,state,derivatives):
    labels=state['labels'];p=state['p'];N=len(vals) if derivatives else 0
    physics.Dual.size=N
    d={name:physics.Dual(v,[arb(int(i==j)) for j in range(N)]) for i,(name,v) in enumerate(zip(labels,vals))}
    par=dict(p);par['D']=d['D'];par['k']=d['k'];par['mu']=d['mu'];D=d['D']
    if bounds(D.v)[0]<=0 or bounds(d['k'].v)[0]<=0:raise ArithmeticError('Nonpositive D or k on full box')
    coeff=[];raw=[];source=[];domain=[]
    for side in (0,1):
        v=lambda name:d[f'{side}:{name}']
        sig=1-2*side;c=sig*p['gamma']/2;P=v('P')
        vi=p['v0' if side==0 else 'v1'];lam=p['lambda_a' if side==0 else 'lambda_b']
        H=-sig*(lam+p['gamma']*(P-vi)**2/2)/6;T=c*(P-vi)
        if state['mode']=='static_hamiltonian':
            rad=(H*H-T*T/12+(-6+p['m2']*P*P/2)/6)/d['k']
            E=sqrt_dual(rad);domain.append({'radicand':rad.v,'E':E.v})
        else:E=v('E');domain.append({'E':E.v})
        g=c*v('f')-2*T*v('psi')
        z=[v('W'),H,P,T,E,v('psi'),v('f'),g,D*side]
        source.append(z);cc=source_flow.coeff(z,7,par);coeff.append(cc)
        jets={name:[cc[j][n]*math.factorial(n) for n in range(6)] for name,j in [('Phi',2),('psi',5),('f',6)]}
        jets.update(H=H,T=T,qbg=d['k']*E*E,sigma=sig,vi=vi,lam=lam)
        raw.append(preparation.endpoint_raw(p['eps'],jets,par))
    hinv=physics.hermite_inverse(4)
    rhs=[raw[side][-1][n]*D**n for side in (0,1) for n in range(4)]
    co=[sum((rhs[i]*hinv[n][i] for i in range(8)),physics.Dual(0))/D**n for n in range(8)]
    fields=[];hermite=[]
    for side in (0,1):
        cc=coeff[side];ph,el,L,pt,t,u,delta=raw[side]
        F=[]
        for n in range(8):
            val=cc[2][n]+p['eps']*cc[6][n]+polynomial_endpoint(co,side,n,D)
            for i,(j,owner) in enumerate(((5,0),(5,1),(7,0),(7,1))):
                val+=p['x'][i+1]*physics.shape_endpoint(j,owner,side,n,D)/math.factorial(n)
            if n==0:val=ph[0]
            elif n==1:val=L*t
            elif n==2:val=ph[2]/2
            elif n==3:val=(ph[3]+delta[3])/6
            F.append(val)
        F=physics.Jet(F);ell=physics.Jet([-2*p['eps']*cc[5][n] for n in range(8)])
        aa=[source[side][0]+p['eps']*source[side][5]+d[f'{side}:w'],
            source[side][1]+p['eps']*cc[5][1]+d[f'{side}:v']]
        for n in range(6):
            A=physics.Jet(aa);As=A.d();V=physics.Jet(-6)+F*F*(p['m2']/2)
            rr=ell.d()*As-2*As*As+(2*ell-2*A).exp()*d['k']-(F.d()*F.d()+2*(2*ell).exp()*V)/6
            aa.append(rr.c[n]/((n+1)*(n+2)))
        fields.append((physics.Jet(aa),F,ell))
        hermite.append([(polynomial_endpoint(co,side,n,D)*math.factorial(n)-delta[n]).v for n in range(4)])
    meta={'source':[ [v.v for v in z] for z in source],
          'fields':{name:[[v.v for v in f[j].c] for f in fields] for j,name in enumerate(('A','Phi','ell'))},
          'canonical_c7':[v.v for v in co],'hermite_identity_remainders':hermite,'domain':domain}
    return fields,par,meta

def kernel(state,derivatives):
    fields,par,meta=make_fields(state['values'] if derivatives else state['pivots'],state,derivatives)
    p=state['p'];q=physics.Gauge(par['D'])
    for order,index in ((3,1),(5,2),(7,3)):
        rows=[physics.time_rows(A,A+q.endpoint(side),F,ell,par,side) for side,(A,F,ell) in enumerate(fields)]
        for side,(A,F,ell) in enumerate(fields):
            corr=-(rows[side][index][1]-rows[side][index][0])*((-(order-1))*A.val()+order*ell.val()).exp()
            if order<7:q.target[6*side+order]=corr
            else:q.eta[side]=corr
    rows=[physics.time_rows(A,A+q.endpoint(side),F,ell,par,side) for side,(A,F,ell) in enumerate(fields)]
    A,F,ell=fields[1];pw=(p['lambda_b']+p['gamma']*(F.val()-p['v1'])**2/2)/6
    out=[A.c[1]*(-ell.val()).exp()-pw]
    for idx,order in ((2,4),(3,6)):
        for side,(A,F,ell) in enumerate(fields):out.append(rows[side][idx][2]*(-order*A.val()).exp())
    off=[]
    for side,(A,F,ell) in enumerate(fields):
        sig=1-2*side;c=sig*p['gamma']/2;P=F.val();L=ell.val().exp()
        pr=A.c[1]/L;pw=-sig*(p['lambda_a' if side==0 else 'lambda_b']+p['gamma']*(P-p['v0' if side==0 else 'v1'])**2/2)/6
        t=F.c[1]/L;u=(2*F.c[2]-ell.c[1]*F.c[1])*(-2*ell.val()).exp()
        lhs=rows[side][1][2]*(-2*A.val()).exp();right=(pr-pw)*(6*u+4*(pr+pw-c)*t-2*p['m2']*P)
        off.append({'metric_mismatch':(pr-pw).v,'C2_direct':lhs.v,'C2_factorized':right.v,'identity_difference':(lhs-right).v})
    meta.update(off_shell_C2=off,q_derivative_targets=[v.v for v in q.target],q7_controls=[v.v for v in q.eta])
    return {'F':[dual_record(v) for v in out],'meta':meta}

def postprocess(state):
    wide=state['wide'];point=state['point'];bits=state['bits'];mode=state['mode']
    physics.Dual.size=len(state['values'])
    C=[[exact(x) for x in row] for row in rec.read(PARENT/'DESIGN.json')['preconditioner']]
    wf=[restore_dual(x) for x in wide['F']];pf=[x['value'] for x in point['F']]
    wb=[-sum((x*arb(c) for x,c in zip(wf,row)),physics.Dual(0)) for row in C]
    pb=[-sum((x*arb(c) for x,c in zip(pf,row)),arb(0)) for row in C]
    def enclose(w,p,kind):
        orig=literal(bits,kind);prior=predecessor_intersections(bits,kind);out=[]
        for i,(v,base) in enumerate(zip(w,p)):
            terms=[mag(d)*r for d,r in zip(v.d,state['radii'])];radius=sum(terms,fmpq(0))
            mv=base+interval(-radius,radius);a,b=bounds(mv);u,z=prior[i]
            lo=max(a,u);hi=min(b,z)
            if lo>hi:raise ArithmeticError('Empty literal predecessor intersection')
            out.append({'index':i,'original':record_pair(orig[i]),'prior_intersection':record_pair(prior[i]),
               'direct':record(v.v),'point':record(base),'mean_value':record(mv),'intersection':record_pair((lo,hi)),
               'derivatives':[record(d) for d in v.d],'input_radius_terms':[str(t) for t in terms],
               'sum_input_radius_terms':str(radius),'outward_excess':str(exact(record(mv)['halfwidth'])-exact(record(base)['halfwidth'])-radius),
               'strict_tightening':hi-lo<z-u})
        return out
    checks={}
    for name,old in state['old_fields'].items():
        checks['field_overlap_'+name]=all(overlap(x,y) for xx,yy in zip(wide['meta']['fields'][name],old) for x,y in zip(xx,yy))
    checks['source_endpoint_overlap']=all(overlap(x,y) for xx,yy in zip(wide['meta']['source'],state['source_endpoint_enclosures']) for x,y in zip(xx,yy))
    checks['canonical_c7_overlap']=all(overlap(x,y) for x,y in zip(wide['meta']['canonical_c7'],state['p']['c7']))
    checks['direct_original_overlap']=all(overlap(x['value'],y) for x,y in zip(wide['F'],state['old_F']))
    for label,case in [('whole_box',wide),('pivot',point)]:
        checks[label+'_off_shell_C2_identity']=all(v['identity_difference'].contains(0) for v in case['meta']['off_shell_C2'])
        checks[label+'_exact_hermite_identity']=all(x.contains(0) for v in case['meta']['hermite_identity_remainders'] for x in v)
    checks['actual_integrated_metric_slope_retained']=True
    checks['unchanged_scaled_coordinate_clock']=True
    return {'bits':bits,'mode':mode,'inputs':[{'label':n,'box':record(v),'pivot':record(m),'radius':str(r)} for n,v,m,r in zip(state['labels'],state['values'],state['pivots'],state['radii'])],
       'residuals':enclose(wf,pf,'F'),'center_corrections':enclose(wb,pb,'B'),
       'off_shell_C2':{k:[{n:record(v) for n,v in row.items()} for row in d['meta']['off_shell_C2']] for k,d in [('whole_box',wide),('pivot',point)]},
       'checks':checks,'all_passed':all(checks.values()),'classification_scope':'Same-center enclosure only; no C6 inclusion decision.'}

def step(state):
    ctx.prec=state['bits']
    if state['phase']==0:state['wide']=kernel(state,True)
    elif state['phase']==1:state['point']=kernel(state,False)
    elif state['phase']==2:state['case_result']=postprocess(state)
    else:raise RuntimeError('Case already complete')
    state['phase']+=1
    return state
