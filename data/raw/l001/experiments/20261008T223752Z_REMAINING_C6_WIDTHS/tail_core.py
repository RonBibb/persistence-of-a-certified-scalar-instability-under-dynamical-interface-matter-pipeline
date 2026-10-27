"""Exact correction-width ledger and one same-source mode-correlated enclosure."""
from pathlib import Path
import sys,os,time,platform,fcntl,resource,types,math
ROOT=Path(__file__).resolve().parent
C4=ROOT.parent/'20261008T200655Z_UPPER_C4_CORRELATED_ENCLOSURE'
sys.path.insert(0,str(C4))
import runtime as oldrt
import enclosure as base
from runtime import arb,fmpq,ctx,rec,physics,bounds,interval,exact,record,record_pair,loc,overlap,mag,Q
PARENT=oldrt.PARENT;WIDTH=oldrt.WIDTH;LIN=ROOT.parents[3]
PREV_INITIAL=oldrt.INITIAL
SHARED=LIN/'shared/integration'/ROOT.name
CFG=rec.read(ROOT/'CONTRACT.json')
MODE=CFG['mode']
commit=oldrt.commit;load=oldrt.load;status=oldrt.status
native_runtime=oldrt.native_runtime;release=oldrt.release
def cid(g,bits):return rec.fingerprint({'guard':g,'bits':bits,'mode':MODE,'phase_order':CFG['recovery']['phase_order']})
def certificate(bits):return rec.read(PREV_INITIAL/'raw'/f'certificate-{bits}.json')
def prior_corrections(bits):return [[exact(x) for x in a] for a in certificate(bits)['exact_fraction']['center_displacement']]
def freeze():
    assert not (ROOT/'BINDINGS.json').exists()
    assert rec.sha(C4/'BINDINGS.json')=='a0b18baf3d93e1bed5439049345604e42251ca386a998a36abef38e3ee9fad48'
    b=rec.read(C4/'BINDINGS.json');inp={str(loc(p)):h for p,h in b['inputs'].items()}
    for n,h in b['sources'].items():inp[str(C4/n)]=h
    for p in [LIN.parent/'program-hub/rounds/20261008T223752Z_NON_PORTAL_LIN_CHAKRABARTY/CONTRACT.md',
              LIN/'shared/integration'/C4.name/'JOINT_RECEIPT.json']:
        inp[str(p)]=rec.sha(p)
    for n in ('BINDINGS.json','FREEZE.json','PREFLIGHT.json','RESULT.json','TERMINAL.json','STATIC_SUBMISSION.json'):
        inp[str(C4/n)]=rec.sha(C4/n)
    for n in ('ADMISSION.json','TERMINAL.json','SCIENTIFIC_AUDIT.json','RESULT_REPORT.md','RADIUS_DOMAIN_RESOLUTION.md',
              'SOURCE_MODE_CONSTRAINT_NOTE.md','results/INCLUSION_DECISION.json','raw/certificate-768.json','raw/certificate-1024.json'):
        inp[str(PREV_INITIAL/n)]=rec.sha(PREV_INITIAL/n)
    for p,h in inp.items():assert rec.sha(p)==h,p
    names=['CONTRACT.json','DERIVATION.txt','.gitignore']+[p.name for p in sorted(ROOT.glob('*.py'))]
    obj={'utc':rec.now(),'sources':{n:rec.sha(ROOT/n) for n in names},'inputs':inp,'runtime':native_runtime(),
       'prior_upper_C4_results_known':True,'new_mode_correlated_results_not_evaluated_before_freeze':True}
    rec.atomic(ROOT/'BINDINGS.json',obj,True);g=rec.sha(ROOT/'BINDINGS.json')
    rec.atomic(ROOT/'FREEZE.json',{'guard':g,'utc':rec.now()},True)
    for n in names:(ROOT/n).chmod(0o444)
    return g
def guard():
    g=rec.sha(ROOT/'BINDINGS.json');b=rec.read(ROOT/'BINDINGS.json');assert rec.read(ROOT/'FREEZE.json')['guard']==g
    for n,h in b['sources'].items():assert rec.sha(ROOT/n)==h,n
    for p,h in b['inputs'].items():assert rec.sha(loc(p))==h,p
    assert b['runtime']==native_runtime()
    return g
def acquire(out):
    assert platform.system()=='Linux';out.mkdir(parents=True,exist_ok=True);SHARED.mkdir(parents=True,exist_ok=True)
    for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):assert os.environ.get(k)=='1'
    resource.setrlimit(resource.RLIMIT_AS,(CFG['resources']['per_worker_address_space_bytes'],)*2)
    held=[]
    for cpu in CFG['resources']['cpu_pool']:
        fs=[]
        try:
            for p,mode in [(Path('/media/psf/Home/Research/ClaudeCode/runtime')/f'compute-slot-{cpu+1}.lock','r'),(SHARED/f'cpu-{cpu}.lock','a+')]:
                f=p.open(mode);fs.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
            held=fs;break
        except BlockingIOError:
            for f in fs:f.close()
    if not held:raise RuntimeError('No unclaimed research CPU')
    try:
        f=(out/'worker.lock').open('a+');held.append(f);fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        os.sched_setaffinity(0,{cpu});ctx.threads=1
    except BaseException:
        for f in held:f.close()
        raise
    ident={'utc':rec.now(),'pid':os.getpid(),'cpu':cpu,'slot':cpu+1,'active':True,
       'start_ticks':Path('/proc/self/stat').read_text().split()[21],
       'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'locks':[str(f.name) for f in held]}
    rec.atomic(out/f'ACQUIRED-{os.getpid()}.json',ident,True)
    return held,ident

def attribution(bits,g):
    packet=certificate(bits);F=[[exact(x) for x in v] for v in packet['packet']['residual_at_center']]
    C=[[exact(x) for x in v] for v in packet['packet']['preconditioner']];B=prior_corrections(bits);rows=[]
    for i in (1,4):
        terms=[abs(c)*(b-a)/2 for c,(a,b) in zip(C[i],F)];total=sum(terms,fmpq(0))
        mid=-sum((c*(a+b)/2 for c,(a,b) in zip(C[i],F)),fmpq(0))
        raw=[mid-total,mid+total];current=B[i]
        assert raw[0]<=current[0]<=current[1]<=raw[1]
        rows.append({'coordinate':i,'name':CFG['targets'][str(i)],'residual_radius_terms':[str(x) for x in terms],
            'linear_budget_sum':str(total),'linear_center_interval':record_pair(raw),'current_admitted_correction':record_pair(current),
            'direct_intersection_halfwidth_reduction':str(total-(current[1]-current[0])/2),
            'shares_before_direct_intersection':[str(x/total) for x in terms],
            'scope':'Exact linear upper budget before independent direct correction intersections, not a physical error partition.'})
    inv=rec.read(WIDTH/'raw'/f'inventory-{bits}.json')
    return {'guard':g,'bits':bits,'residual_order':['upper_Israel','lower_C4','upper_C4','lower_C6','upper_C6'],
       'F':[record_pair(x) for x in F],'rows':rows,
       'inherited_evidence':{'path':str(WIDTH/'raw'/f'inventory-{bits}.json'),'sha256':rec.sha(WIDTH/'raw'/f'inventory-{bits}.json'),
         'stored_last_cell_samples':inv['stored_last_cell_samples'],'full_integration_cells':inv['full_integration_cells'],
         'source_root_integration_wrapping':'UNRESOLVED_MIXTURE retained in original primitive boxes; no zero assignment or invented disjoint split.',
         'event_localization':'Retained in D and source endpoint enclosures; prior overlapping event-shift bounds remain unchanged.',
         'finite_amplitude':'Same exact canonical C7 function; no epsilon truncation. Existing epsilon remainder evidence remains separately bound.'}}

def prepare(bits):
    st=base.prepare(bits,'static_hamiltonian');st['mode']=MODE
    keep=[i for i,n in enumerate(st['labels']) if not n.endswith(':f')]
    st['labels']=[st['labels'][i] for i in keep];target=[st['values'][i] for i in keep]
    st['target_original_boxes']=[[str(a),str(b)] for a,b in map(bounds,target)]
    st['pivots']=[v.mid() for v in target]
    st['radii']=[max(abs(x-m.fmpq()) for x in bounds(v)) for v,m in zip(target,st['pivots'])]
    st['values']=[rec.unpack(rec.pack(interval(m.fmpq()-r,m.fmpq()+r))) for m,r in zip(st['pivots'],st['radii'])]
    st['domain_proof']=domain_proof(st)
    return st
def domain_proof(st):
    checks=[]
    for pair,m,r,x in zip(st['target_original_boxes'],st['pivots'],st['radii'],st['values']):
        a,b=map(exact,pair);q=m.fmpq();lo,hi=bounds(x)
        checks.append(lo<=q-r<=a<=b<=q+r<=hi)
    if not all(checks):raise ArithmeticError('Primitive target-radius-derivative containment failed')
    return {'all_passed':True,'checks':checks,'meaning':'Original input subset exact radius rectangle subset saved derivative domain.'}

def make_fields(vals,state,derivatives):
    p=state['p'];N=len(vals) if derivatives else 0;physics.Dual.size=N
    d={name:physics.Dual(v,[arb(int(i==j)) for j in range(N)]) for i,(name,v) in enumerate(zip(state['labels'],vals))}
    par=dict(p,D=d['D'],k=d['k'],mu=d['mu']);D=d['D']
    if bounds(D.v)[0]<=0 or bounds(d['k'].v)[0]<=0:raise ArithmeticError('Nonpositive D or k')
    coeff=[];raw=[];source=[];domain=[]
    for side in (0,1):
        v=lambda name:d[f'{side}:{name}'];sig=1-2*side;c=sig*p['gamma']/2;P=v('P')
        vi=p['v0' if side==0 else 'v1'];lam=p['lambda_a' if side==0 else 'lambda_b']
        H=-sig*(lam+p['gamma']*(P-vi)**2/2)/6;T=c*(P-vi)
        rad=(H*H-T*T/12+(-6+p['m2']*P*P/2)/6)/d['k'];E=base.sqrt_dual(rad)
        B=c*T-p['m2']*P+4*H*T
        if B.v.contains(0):raise ArithmeticError('Full-box source-mode denominator includes zero')
        f=3*(d['mu']+4*d['k'])*E*E*v('psi')/B;g=c*f-2*T*v('psi')
        z=[v('W'),H,P,T,E,v('psi'),f,g,D*side];source.append(z)
        cc=base.source_flow.coeff(z,7,par);coeff.append(cc)
        j={name:[cc[idx][n]*math.factorial(n) for n in range(6)] for name,idx in [('Phi',2),('psi',5),('f',6)]}
        j.update(H=H,T=T,qbg=d['k']*E*E,sigma=sig,vi=vi,lam=lam)
        raw.append(base.preparation.endpoint_raw(p['eps'],j,par))
        ident=B*f-3*(d['mu']+4*d['k'])*E*E*v('psi')
        domain.append({'radicand':rad.v,'E':E.v,'mode_denominator':B.v,'mode_identity_difference':ident.v,
                       'mode_identity_gradient_differences':list(ident.d)})
    hinv=physics.hermite_inverse(4);rhs=[raw[side][-1][n]*D**n for side in (0,1) for n in range(4)]
    co=[sum((rhs[i]*hinv[n][i] for i in range(8)),physics.Dual(0))/D**n for n in range(8)]
    fields=[];hermite=[]
    for side in (0,1):
        cc=coeff[side];ph,el,L,pt,t,u,delta=raw[side];F=[]
        for n in range(8):
            val=cc[2][n]+p['eps']*cc[6][n]+base.polynomial_endpoint(co,side,n,D)
            for i,(j,owner) in enumerate(((5,0),(5,1),(7,0),(7,1))):val+=p['x'][i+1]*physics.shape_endpoint(j,owner,side,n,D)/math.factorial(n)
            if n==0:val=ph[0]
            elif n==1:val=L*t
            elif n==2:val=ph[2]/2
            elif n==3:val=(ph[3]+delta[3])/6
            F.append(val)
        F=physics.Jet(F);ell=physics.Jet([-2*p['eps']*cc[5][n] for n in range(8)])
        aa=[source[side][0]+p['eps']*source[side][5]+d[f'{side}:w'],source[side][1]+p['eps']*cc[5][1]+d[f'{side}:v']]
        for n in range(6):
            A=physics.Jet(aa);As=A.d();V=physics.Jet(-6)+F*F*(p['m2']/2)
            ar=ell.d()*As-2*As*As+(2*ell-2*A).exp()*d['k']-(F.d()*F.d()+2*(2*ell).exp()*V)/6
            aa.append(ar.c[n]/((n+1)*(n+2)))
        fields.append((physics.Jet(aa),F,ell))
        hermite.append([(base.polynomial_endpoint(co,side,n,D)*math.factorial(n)-delta[n]).v for n in range(4)])
    return fields,par,{'source':[[x.v for x in z] for z in source],
       'fields':{name:[[x.v for x in f[j].c] for f in fields] for j,name in enumerate(('A','Phi','ell'))},
       'canonical_c7':[v.v for v in co],'hermite_identity_remainders':hermite,'domain':domain}

# Exact residual-driver reuse with an explicit, private field-builder dependency.
# Neither the frozen module globals nor any parent file is modified.
kernel=types.FunctionType(base.kernel.__code__,dict(base.kernel.__globals__,make_fields=make_fields),'mode_correlated_kernel')

def postprocess(st):
    out=base.postprocess(st);out['domain_proof']=domain_proof(st);out['target_original_boxes']=st['target_original_boxes']
    out['checks']['target_radius_derivative_containment']=out['domain_proof']['all_passed']
    for label in ('wide','point'):
        out['checks'][label+'_source_mode_identity']=all(row['mode_identity_difference'].contains(0) and
          all(x.contains(0) for x in row['mode_identity_gradient_differences']) for row in st[label]['meta']['domain'])
    current=prior_corrections(st['bits']);targets={}
    for i in (1,4):
        row=out['center_corrections'][i];a,b=map(exact,row['mean_value']['exact']);lo,hi=current[i]
        nl,nh=max(lo,a),min(hi,b)
        if nl>nh:raise ArithmeticError('New correction disjoint from exact current admitted correction')
        targets[str(i)]={'name':CFG['targets'][str(i)],'prior':record_pair((lo,hi)),
          'candidate':row['mean_value'],'intersection':record_pair((nl,nh)),
          'strict_tightening':nh-nl<hi-lo,'width_ratio':str((nh-nl)/(hi-lo))}
    out['targets']=targets;out['all_passed']=all(out['checks'].values())
    out['new_full_vector_not_admitted_by_producer']=True
    return out
def step(st):
    ctx.prec=st['bits'];domain_proof(st)
    if st['phase']==0:st['wide']=kernel(st,True)
    elif st['phase']==1:st['point']=kernel(st,False)
    elif st['phase']==2:st['case_result']=postprocess(st)
    else:raise RuntimeError('Already complete')
    st['phase']+=1;return st
