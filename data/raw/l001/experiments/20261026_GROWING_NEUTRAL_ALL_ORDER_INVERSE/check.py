"""Bounded all-neutral-order real-axis scalar inverse from fresh saved tubes.
Linux only. python -I -B check.py PINNED_FRESH_READINESS_TERMINAL_SHA256
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
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
def low_constant(n,V,U,A,beta,L):
    if V<=0 or beta<=0:return None
    length=min(L/2,1/(A+1));den=1-A*length/2
    need(length>0 and den>0,'LOW_ABSORPTION')
    c0=max(1/V,1/(n*beta));c1=((2/length+length*U/2)*c0+length/2)/den;c2=A*c1+U*c0+1
    return n*n*c0+n*c1+c2
def main(lease,pin):
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    def ball(v):
        a,b=map(Q,v['exact_bounds']);return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))
    def lo(v):need(v.is_finite(),'FINITE');return Q(str(v.lower().fmpq()))
    def hi(v):need(v.is_finite(),'FINITE');return Q(str(v.upper().fmpq()))
    need(sha(PARENT/'TERMINAL.json')==pin,'FRESH_TERMINAL_PIN');term=read(PARENT/'TERMINAL.json');need(term['pass'],'FRESH_PASS')
    inputs={str(PARENT/'TERMINAL.json'):pin}
    for n,h in term['artifacts'].items():need(sha(PARENT/n)==h,'FRESH_ARTIFACT:'+n);inputs[str(PARENT/n)]=h
    need(sha(PARENT/'BINDING.json')==term['binding_sha256'] and sha(PARENT/'RESULT.json')==term['result_sha256'],'FRESH_RECORD_PINS')
    parentbinding=read(PARENT/'BINDING.json')
    for group in ('sources','parents','runtime'):
        for p,h in parentbinding[group].items():need(sha(p)==h,'PARENT_BINDING');inputs[p]=h
    need(parentbinding['predeclared_methods']==['constant','inverse_warp_squared'],'METHOD_CONTRACT')
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP')
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h or (p==str(pylong) and h==sha(pylong)),'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,fresh_terminal_pin=pin,precision_bits=768,max_cutoff=128,fixed_lambda='1/128'))
    started=time.monotonic();reports={};unresolved=[]
    need(low_constant(1,Q(1),Q(1),Q(0),Q(1),Q(2))==6,'EXACT_LOW_CONSTANT_CONTROL')
    for name in ('primary','independent'):
        arm=read(PARENT/('ARM_'+name+'.json'));initialpath=PARENT/('INITIAL_'+name+'.json');initial=read(initialpath)
        need(sha(initialpath)==arm['initial_identity_sha256'],'INITIAL_PIN')
        p={k:ball(v) for k,v in initial['parameters'].items()};m,k,r,h=[p[key] for key in ('m2','k','rate','h')]
        rlo,rhi,hlo,hhi=lo(r),hi(r),lo(h),hi(h);need(rlo>hhi>0,'STRICT_GROWING_RATE')
        L,Lhi=map(Q,initial['D']);need(L>0,'DOMAIN_POSITIVE');nbg=initial['background_native_dimension']
        ext={'alpha':None,'b':None,'L0':None,'K':Q(0),'KA':Q(0),'beta0':None,'Kbeta':Q(0),'E2lo':None,'E2hi':Q(0),'H':Q(0),'Hp':Q(0),'U0':Q(0)}
        index=0;last=initial['initial_native'][:nbg];previous=None;step=Q(initial['step'])
        for entry in arm['chunks']:
            need(time.time()<DEADLINE and time.monotonic()-started<570,'TIME_BOUND')
            path=PARENT/entry['file'];cp_path=PARENT/entry['checkpoint']
            need(path.resolve().is_relative_to(PARENT.resolve()) and cp_path.resolve().is_relative_to(PARENT.resolve()),'PATH_SCOPE')
            need(sha(path)==entry['sha256'] and sha(cp_path)==entry['checkpoint_sha256'],'CHUNK_PIN')
            chunk=read(path);cp=read(cp_path)
            need(chunk['engine']==name and chunk['binding_sha256']==term['binding_sha256'] and chunk['initial_identity_sha256']==arm['initial_identity_sha256'] and chunk['previous_sha256']==previous,'CHUNK_BINDING')
            need(chunk['first']==entry['first']==index and chunk['last']==entry['last'],'CHUNK_ORDER')
            for cell in chunk['records']:
                need(cell['index']==index and Q(cell['s'])==index*step and Q(cell['step'])==step and cell['start_native_background']==last,'CELL_CHAIN')
                last=cell['end_native_background'];native=cell['box_native_background'];canonical=cell['box_canonical_background']
                need(len(native)==nbg and len(canonical)==5 and native[:4]==canonical[:4],'BACKGROUND_REPRESENTATION')
                need(cell['whole_cell_constraints_contain_zero'] and cell['background_first_integral_contains_zero'],'INHERITED_CELL_CERTIFICATES')
                W,H,Phi,T=map(ball,native[:4]);E=ball(native[4]) if name=='primary' else (-W).exp()
                if name=='primary':need(native==canonical,'PRIMARY_BACKGROUND')
                e2=E*E;elo=lo(e2);ehi=hi(e2);need(elo>0,'POSITIVE_WARP')
                Tp=m*Phi-4*H*T;Hp=-T*T/3-k*e2;B=12*H*T-4*m*Phi
                alpha=rlo*rlo*elo;b=3*rlo*hlo*elo
                L0=lo(m+4*T*T/3-2*k*e2+4*H*H)
                K=hi(abs(B*(Tp+2*H*T)))/(3*rlo*rlo*elo)
                KA=hi(abs(B*T))/(3*rlo*rlo*elo);Kbeta=hi(abs(2*T*Tp))/(3*rlo*rlo*elo)
                Hb=hi(abs(H));beta0=Q(41,4)-2*Hb
                for key,val in dict(alpha=alpha,b=b,L0=L0,beta0=beta0,E2lo=elo).items():ext[key]=val if ext[key] is None else min(ext[key],val)
                U0=hi(abs(m))+4*hi(abs(T*T))/3+2*hi(abs(k*e2))+4*hi(abs(H*H))
                for key,val in dict(K=K,KA=KA,Kbeta=Kbeta,E2hi=ehi,H=Hb,Hp=hi(abs(Hp)),U0=U0).items():ext[key]=max(ext[key],val)
                index+=1
            need(index==entry['last']+1 and cp['completed']==index and cp['total']==initial['cells'] and cp['last_native_background']==last,'CHECKPOINT_STATE')
            need(cp['engine']==name and cp['binding_sha256']==term['binding_sha256'] and cp['initial_identity_sha256']==arm['initial_identity_sha256'] and cp['chunk_sha256']==entry['sha256'] and cp['previous_chunk_sha256']==previous and cp['resume_supported'] is False,'CHECKPOINT_BINDING')
            previous=entry['sha256']
            if index%2048==0:print(name,index,'cells',round(time.monotonic()-started,1),flush=True)
        need(index==arm['cells']==initial['cells'] and last==arm['final_native_background'] and (index-1)*step<Lhi<=index*step,'COMPLETE_COVER')
        alpha,b,L0,K,KA,beta0,Kbeta=[ext[key] for key in ('alpha','b','L0','K','KA','beta0','Kbeta')]
        need(alpha>0 and b>0,'HIGH_POSITIVE_COEFFICIENTS')
        u2=rhi*rhi*ext['E2hi'];u1=3*rhi*hhi*ext['E2hi'];U0=ext['U0']
        def lower(n):return alpha*n*n+b*n+L0-K/(n*n)
        def upper(n):return u2*n*n+u1*n+U0+K/(n*n)
        lam=Q(1,128);c=alpha/2;selected=None;attempts={}
        for N in range(9,129):
            A=KA/(N*N);v=u2+u1/N+U0/(N*N)+K/(N**4)
            checks=dict(coercivity=alpha*N*N/2+b*N+L0-K/(N*N),robin=beta0-Kbeta/(N*N)-1,barrier=c-lam*lam-A*lam/N,boundary_separation=lam*N*L-1,taylor_segment=N*L-2,derivative_absorption=1-A/(2*N))
            ok=all(value>=0 for key,value in checks.items() if key!='derivative_absorption') and checks['derivative_absorption']>0
            attempts[str(N)]={key:str(value) for key,value in checks.items()}
            if ok:selected=(N,A,v,checks);break
        if selected is None:
            unresolved.append(name+':NO_HIGH_CUTOFF_THROUGH_128');reports[name]={'cells':index,'extrema':{k:str(v) for k,v in ext.items()},'attempts':attempts};put('ARM_'+name+'.json',reports[name]);continue
        N,A,v,checks=selected
        C0=max(1/c,4/lam);C1=((2+v/2)*C0+Q(1,2))/checks['derivative_absorption'];C2=A*C1/N+v*C0+1;high=C0+C1+C2
        finite={};finite_values=[]
        for n in range(2,N):
            if n<=8:
                row=arm['methods']['inverse_warp_squared'][str(n)]
                values=tuple(Q(row[key]) for key in ('V_min','V_abs_max','drift_abs_max','beta_min'));origin='inherited_fresh_readiness_direct_cell_reduction'
            else:values=(lower(n),upper(n),KA/(n*n),beta0-Kbeta/(n*n));origin='analytic_global_envelope'
            Cn=low_constant(n,*values,L)
            finite[str(n)]={'origin':origin,'bounds':list(map(str,values)),'constant':None if Cn is None else str(Cn)}
            if Cn is None:unresolved.append(name+':LOW_BOUND_INCONCLUSIVE:'+str(n))
            else:finite_values.append(Cn)
        Cy=max([high]+finite_values)
        multiplier=max(1+ext['H']+ext['H']*ext['H']+ext['Hp']/2,1+2*ext['H'],Q(1))
        Cf=ext['E2hi']/ext['E2lo']*multiplier*Cy
        reports[name]={'cells':index,'extrema':{k:str(v) for k,v in ext.items()},'N':N,'lambda':str(lam),'c':str(c),'A':str(A),'v':str(v),'high_gates':{k:str(v) for k,v in checks.items()},'high_constants':dict(value=str(C0),first=str(C1),second=str(C2),sum=str(high)),'finite_orders':finite,'C_y':str(Cy),'f_transfer_multiplier':str(ext['E2hi']/ext['E2lo']*multiplier),'C_f':str(Cf),'C_f_outward_integer':-((-Cf.numerator)//Cf.denominator),'scope':'Inverse for rescaled scalar y transferred to f; no metric reconstruction or nonlinear source bound.'}
        put('ARM_'+name+'.json',reports[name])
    need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(all(sha(p)==h for p,h in dict(inputs,**sources).items()),'INPUTS_UNCHANGED')
    passed=not unresolved
    out={'pass':True,'scientific_certificate':passed,'classification':'ALL_NEUTRAL_ORDER_REAL_AXIS_SCALAR_INVERSE_CERTIFIED' if passed else 'NEUTRAL_ALL_ORDER_INVERSE_METHOD_INCONCLUSIVE','unresolved':unresolved,'arms':reports,'common_C_f_outward_integer':max(a['C_f_outward_integer'] for a in reports.values()) if passed else None,'seconds':time.monotonic()-started,'new_ode_solves':0,'scope':'Conditional on authenticated fresh ODE enclosures, selected mode and compatible scalar reduction. All integer n>=2 real-axis constrained scalar BVP inverse estimate. No complex collar, all-order nonlinear source majorant, finite-amplitude analytic-family convergence or endpoint claim. Constant is conservative, not measured amplification.'}
    put('RESULT.json',out);put('TERMINAL.json',{'pass':True,'scientific_certificate':passed,'result_sha256':sha(ROOT/'RESULT.json'),'binding_sha256':sha(ROOT/'BINDING.json'),'source_sha256':sha(__file__),'derivation_sha256':sha(ROOT/'DERIVATION.txt')})
    print(json.dumps({k:v for k,v in out.items() if k!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_PIN_BOUND_FITS')
        need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE')
        s=importlib.util.spec_from_file_location('neutral_all_order_lease',lp);lease=importlib.util.module_from_spec(s);sys.modules[s.name]=lease;s.loader.exec_module(lease);lease.ROOT=ROOT
        cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NEUTRAL_INVERSE_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));sys.path.insert(0,str(lease.FLINT));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
