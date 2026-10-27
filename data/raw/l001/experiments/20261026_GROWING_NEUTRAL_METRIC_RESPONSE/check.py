"""Compatible neutral scalar/metric reconstruction; no new ODE solve."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
INVERSE=BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def qualify(ring):
    names=('H','T','Phi','e','m','k','mu','f','g','Sc','Scp','Sp','Sg','Rw','Gamma')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    H,T,Phi,e,m,k,mu,f,g,Sc,Scp,Sp,Sg,Rw,Gamma=[ring.variable(j) for j in range(len(names))]
    Tp=m*Phi-4*H*T;Hp=-T*T/3-k*e;Tpp=m*T-4*Hp*T-4*H*Tp
    B=12*H*T-4*m*Phi;D=2*T*T-3*(mu+4*k)*e;J=D-2*T*T
    Dp=4*T*Tp+6*H*(mu+4*k)*e;N=Sc-T*g+Tp*f
    gpD=D*(-4*H*g+(m-mu*e+2*T*T)*f+Sg)+B*N
    reduced=-(4*H*D+B*T)*g+((m-mu*e+2*T*T)*D+B*Tp)*f+B*Sc+D*Sg
    compat=Scp+4*H*Sc-T*Sg-D*Sp
    derivativeD2=D*(Scp+Tpp*f)-T*gpD-N*Dp
    desiredD2=D*(-2*H*N-D*T*f/3+D*Sp)
    gates={}
    def eq(key,v):gates[key]=v.iszero();need(gates[key],key)
    eq('EXACT_REDUCED_SCALAR_FORCING',gpD-reduced)
    eq('EXACT_METRIC_RECONSTRUCTION_COMPATIBILITY',derivativeD2-desiredD2-D*compat)
    for sigma in (-1,1):
        originalD=2*sigma*(D*g+2*T*N)-Gamma*D*f-D*Rw
        robin2J=-2*sigma*J*g+(Gamma*D-4*sigma*T*Tp)*f+D*Rw-4*sigma*T*Sc
        eq('EXACT_OUTWARD_ROBIN_SIGN_'+str(sigma),originalD+robin2J)
    gates['MUTATION_MISSING_SOURCE_DERIVATIVE_DETECTED']=not (D*Scp).iszero()
    need(gates['MUTATION_MISSING_SOURCE_DERIVATIVE_DETECTED'],'MUTATION')
    return gates
def main(lease):
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    def ball(v):
        a,b=map(Q,v['exact_bounds']);return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))
    def lo(v):need(v.is_finite(),'FINITE');return Q(str(v.lower().fmpq()))
    def hi(v):need(v.is_finite(),'FINITE');return Q(str(v.upper().fmpq()))
    pins={str(FRESH/'TERMINAL.json'):'f8a27fa6aeccb8f6b63af588d02fe8dd9a97c201956adbcf9544decb0a319445',str(INVERSE/'TERMINAL.json'):'1d756bb367a3e8c55452bfa95120b809ef08a2d681c7be1bf040fa0d0eb02bb4'}
    inputs=dict(pins)
    for p,h in pins.items():need(sha(p)==h,'PIN')
    auditpath=INVERSE/'audit/AUDIT_TERMINAL.json'
    need(sha(auditpath)=='970f11cb9734c3dfe725788de8957a4b5ca0fced0727ec1ae6a4f8da14907c35','INDEPENDENT_INVERSE_AUDIT_PIN')
    audit=read(auditpath);auditresult=INVERSE/'audit/AUDIT_RESULT.json'
    need(audit['pass_status'] and sha(auditresult)==audit['result_sha256'],'INDEPENDENT_INVERSE_AUDIT')
    need(read(auditresult)['production_terminal_sha256']==pins[str(INVERSE/'TERMINAL.json')],'INDEPENDENT_AUDIT_OWNERSHIP')
    inputs[str(auditpath)]=sha(auditpath);inputs[str(auditresult)]=sha(auditresult)
    ft=read(FRESH/'TERMINAL.json');it=read(INVERSE/'TERMINAL.json')
    need(ft['pass'] and it['pass'] and it['scientific_certificate'],'INVERSE_ADMITTED')
    for n,h in ft['artifacts'].items():need(sha(FRESH/n)==h,'FRESH_ARTIFACT');inputs[str(FRESH/n)]=h
    for root,t in ((FRESH,ft),(INVERSE,it)):
        for name,key in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')):need(sha(root/name)==t[key],'RESULT_BINDING');inputs[str(root/name)]=t[key]
    ib=read(INVERSE/'BINDING.json');need(ib['fresh_terminal_pin']==pins[str(FRESH/'TERMINAL.json')],'INVERSE_FRESH_IDENTITY')
    for group in ('inputs','sources','runtime'):
        for p,h in ib[group].items():need(sha(p)==h,'INVERSE_CLOSURE');inputs[p]=h
    ir=read(INVERSE/'RESULT.json');need(ir['scientific_certificate'] and not ir['unresolved'],'ALL_N_CERTIFICATE')
    ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
    need(inputs.get(str(ringpath))==sha(ringpath),'RING_AUTHORITY');ring=load('neutral_metric_exact_ring',ringpath)
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP')
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h or (p==str(pylong) and h==sha(pylong)),'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,precision_bits=768))
    gates=qualify(ring);started=time.monotonic();arms={}
    for name in ('primary','independent'):
        arm=read(FRESH/('ARM_'+name+'.json'));initialpath=FRESH/('INITIAL_'+name+'.json');need(sha(initialpath)==arm['initial_identity_sha256'],'INITIAL_PIN');initial=read(initialpath)
        pars={k:ball(v) for k,v in initial['parameters'].items()};mass=pars['m2'];k=pars['k'];rlo=lo(pars['rate'])
        nbg=initial['background_native_dimension'];last=initial['initial_native'][:nbg];previous=None;index=0;step=Q(initial['step'])
        ext={key:Q(0) for key in ('H0','Hp0','T0','Tp0','B0')};emin2=None
        for entry in arm['chunks']:
            need(time.time()<DEADLINE and time.monotonic()-started<570,'TIME_BOUND')
            path=FRESH/entry['file'];cp_path=FRESH/entry['checkpoint'];need(path.resolve().is_relative_to(FRESH.resolve()) and cp_path.resolve().is_relative_to(FRESH.resolve()),'PATH_SCOPE')
            need(sha(path)==entry['sha256'] and sha(cp_path)==entry['checkpoint_sha256'],'CHUNK_HASH');chunk=read(path);cp=read(cp_path)
            need(chunk['engine']==name and chunk['binding_sha256']==ft['binding_sha256'] and chunk['initial_identity_sha256']==arm['initial_identity_sha256'] and chunk['previous_sha256']==previous,'CHUNK_BINDING')
            need(chunk['first']==entry['first']==index and chunk['last']==entry['last'],'CHUNK_ORDER')
            for cell in chunk['records']:
                need(cell['index']==index and Q(cell['s'])==index*step and Q(cell['step'])==step and cell['start_native_background']==last,'CELL_CHAIN');last=cell['end_native_background']
                native=cell['box_native_background'];need(len(native)==nbg and len(cell['box_canonical_background'])==5 and native[:4]==cell['box_canonical_background'][:4],'BG_REPRESENTATION')
                need(cell['whole_cell_constraints_contain_zero'] and cell['background_first_integral_contains_zero'],'CELL_CERTIFICATES')
                W,H,Phi,T=map(ball,native[:4]);E=ball(native[4]) if name=='primary' else (-W).exp();e2=E*E;need(lo(e2)>0,'POSITIVE_E2')
                Hp=-T*T/3-k*e2;Tp=mass*Phi-4*H*T;B=12*H*T-4*mass*Phi
                for key,v in dict(H0=H,Hp0=Hp,T0=T,Tp0=Tp,B0=B).items():ext[key]=max(ext[key],hi(abs(v)))
                emin2=lo(e2) if emin2 is None else min(emin2,lo(e2));index+=1
            need(index==entry['last']+1 and cp['completed']==index and cp['total']==initial['cells'] and cp['last_native_background']==last,'CHECKPOINT_STATE')
            need(cp['engine']==name and cp['binding_sha256']==ft['binding_sha256'] and cp['initial_identity_sha256']==arm['initial_identity_sha256'] and cp['chunk_sha256']==entry['sha256'] and cp['previous_chunk_sha256']==previous and cp['resume_supported'] is False,'CHECKPOINT_BINDING')
            previous=entry['sha256']
        dlo,dhi=map(Q,initial['D']);need(index==arm['cells']==initial['cells'] and last==arm['final_native_background'] and (index-1)*step<dhi<=index*step,'COMPLETE_COVER')
        d0=3*rlo*rlo*emin2;need(d0>0,'DENOMINATOR_BOUND');H0,Hp0,T0,Tp0,B0=[ext[key] for key in ('H0','Hp0','T0','Tp0','B0')]
        # D,J >=d0*n²; every numerical bound is rebuilt for neutral rates.
        Csource=max(Q(1),B0/(4*d0)+T0/d0,Q(1,2)+T0*T0/(4*d0))
        Cf=Q(ir['arms'][name]['C_f']);need(Cf>0,'SCALAR_CONSTANT')
        Cscalar=Cf*Csource
        P0=max(Q(1),T0/2+Tp0/4)/d0
        P1=H0*P0+T0/6+1
        P2=Hp0*P0/2+H0*P1+Tp0/12+T0/6+1
        Cp=P0+P1+P2
        Cmetric=Cp*(1+Cscalar);Ccombined=Cscalar+Cmetric
        constants=dict(d0=d0,forcing_transfer=Csource,scalar_original=Cf,scalar_from_compatible_loads=Cscalar,P_value=P0,P_first=P1,P_second=P2,P_sum=Cp,metric_from_compatible_loads=Cmetric,combined=Ccombined)
        arms[name]={'cells':index,'background_extrema':{key:str(v) for key,v in ext.items()},'E2_min':str(emin2),'r_min':str(rlo),'constants_exact':{key:str(v) for key,v in constants.items()},'constants_outward_integer':{key:-((-v.numerator)//v.denominator) for key,v in constants.items()}}
        put('ARM_'+name+'.json',arms[name]);print(name,'complete',round(time.monotonic()-started,1),flush=True)
    need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(all(sha(p)==h for p,h in dict(inputs,**sources).items()),'INPUTS_UNCHANGED')
    out={'pass':True,'classification':'ALL_NEUTRAL_ORDER_COMPATIBLE_REAL_AXIS_SCALAR_METRIC_RESPONSE','exact_controls':gates,'arms':arms,'common_combined_outward_integer':max(v['constants_outward_integer']['combined'] for v in arms.values()),'seconds':time.monotonic()-started,'new_ode_solves':0,'norm':'Q_n=||Sc||+||Sg||+n max|R_wall|+n||Sp||+||Sp_prime||; U_n(v)=n²||v||+n||v_prime||+||v_second||','compatibility':'Sc_prime+4H Sc-T Sg-D Sp=0; must hold pointwise for compatible source data. Sc needs one derivative, Sp one derivative for U_n(p). No derivative estimated for free.','scope':'Conditional real-axis inverse and p-metric reconstruction for every n>=2 on the authenticated neutral growing background. Does not bound trace c or b=c-2p, complex analytic norms, nonlinear source maps or convergence. Constants are conservative worst-case bounds, not physical gains.'}
    put('RESULT.json',out);put('TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'RESULT.json'),'binding_sha256':sha(ROOT/'BINDING.json'),'source_sha256':sha(__file__),'derivation_sha256':sha(ROOT/'DERIVATION.txt')})
    print(json.dumps({key:v for key,v in out.items() if key!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_BOUND_FITS');need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN_PIN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE_PIN');lease=load('neutral_metric_lease',lp);lease.ROOT=ROOT
        cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NEUTRAL_METRIC_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));sys.path.insert(0,str(lease.FLINT));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
