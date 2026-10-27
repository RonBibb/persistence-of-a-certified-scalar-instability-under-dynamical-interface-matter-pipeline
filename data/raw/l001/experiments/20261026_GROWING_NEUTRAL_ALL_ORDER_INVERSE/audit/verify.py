"""Independent exact-rational arithmetic audit of the real-axis inverse.
No ODE solves. Canonical interval background cells are inherited; this
recomputes scalar reductions and bounds, not their Picard existence proof.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(lease,pin):
    need(sha(PACKET/'TERMINAL.json')==pin,'TERMINAL_PIN');t=read(PACKET/'TERMINAL.json')
    need(t['pass'] and t['scientific_certificate'],'CERTIFICATE_PRESENT')
    need(sha(PACKET/'RESULT.json')==t['result_sha256'] and sha(PACKET/'BINDING.json')==t['binding_sha256'],'RESULT_BINDING')
    need(sha(PACKET/'check.py')==t['source_sha256'] and sha(PACKET/'DERIVATION.txt')==t['derivation_sha256'],'SOURCE_PIN')
    inputs={str(PACKET/'TERMINAL.json'):pin,str(Path(__file__)):sha(__file__)}
    for n in ('RESULT.json','BINDING.json','check.py','DERIVATION.txt'):inputs[str(PACKET/n)]=sha(PACKET/n)
    bind=read(PACKET/'BINDING.json')
    for group in ('inputs','sources','runtime'):
        for p,h in bind[group].items():need(sha(p)==h,'BOUND_PARENT:'+p);inputs[p]=h
    utility=QUAD/'audit/verify.py';need(sha(utility)==read(QUAD/'audit/AUDIT_TERMINAL.json')['source_sha256'],'INTERVAL_UTILITY')
    inputs[str(utility)]=sha(utility);u=load('inverse_exact_interval',utility);I,iv=u.I,u.iv
    def ab(v):return I(0 if v.zero() else min(abs(v.lo),abs(v.hi)),max(abs(v.lo),abs(v.hi)))
    def sq(v):return I(0 if v.zero() else min(v.lo*v.lo,v.hi*v.hi),max(v.lo*v.lo,v.hi*v.hi))
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG')
    need(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h,'AUDIT_RUNTIME:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=pin))
    result=read(PACKET/'RESULT.json');reports={};started=time.monotonic();checks=0
    def gate(v,label):
        nonlocal checks
        need(v,label);checks+=1
    for name in ('primary','independent'):
        prod=result['arms'][name];arm=read(FRESH/('ARM_'+name+'.json'));ini=read(FRESH/('INITIAL_'+name+'.json'))
        p={k:iv(v) for k,v in ini['parameters'].items()};m,k,r,h=[p[q] for q in ('m2','k','rate','h')]
        gate(r.lo>h.hi>0 and (sq(h)-k).zero(),'GROWTH_BACKGROUND')
        ext={key:Q(value) for key,value in prod['extrema'].items()};count=0
        low={n:tuple(Q(arm['methods']['inverse_warp_squared'][str(n)][key]) for key in ('V_min','V_abs_max','drift_abs_max','beta_min')) for n in range(2,9)}
        prior=None;last=ini['initial_native'][:ini['background_native_dimension']]
        for entry in arm['chunks']:
            gate(time.time()<DEADLINE and time.monotonic()-started<550,'TIME_BOUND')
            path=FRESH/entry['file'];gate(sha(path)==entry['sha256'],'CHUNK_DIGEST');chunk=read(path)
            gate(chunk['previous_sha256']==prior and chunk['first']==count and chunk['engine']==name,'CHUNK_CHAIN')
            for cell in chunk['records']:
                gate(cell['index']==count and cell['start_native_background']==last,'CELL_CHAIN')
                last=cell['end_native_background'];W,H,Phi,T,E=map(iv,cell['box_canonical_background'])
                gate(E.lo>0,'POSITIVE_WARP');e=sq(E);tt=sq(T);hh=sq(H)
                Tp=m*Phi-4*H*T;Hp=-tt/3-k*e;B=12*H*T-4*m*Phi
                denom=3*r.lo*r.lo*e.lo
                lower=dict(alpha=r.lo*r.lo*e.lo,b=3*r.lo*h.lo*e.lo,L0=(m+4*tt/3-2*k*e+4*hh).lo,beta0=Q(41,4)-2*ab(H).hi,E2lo=e.lo)
                upper=dict(K=ab(B*(Tp+2*H*T)).hi/denom,KA=ab(B*T).hi/denom,Kbeta=ab(2*T*Tp).hi/denom,E2hi=e.hi,H=ab(H).hi,Hp=ab(Hp).hi,U0=ab(m).hi+4*ab(tt).hi/3+2*ab(k*e).hi+4*ab(hh).hi)
                gate(all(ext[q]<=v for q,v in lower.items()),'CELL_LOWER_EXTREMA_'+name+'_'+str(count))
                gate(all(ext[q]>=v for q,v in upper.items()),'CELL_UPPER_EXTREMA_'+name+'_'+str(count))
                for n in range(2,9):
                    temporal=n*r*(n*r+3*h)*e;J=3*temporal-12*k*e;D=2*tt+J
                    gate(J.lo>0 and D.lo>0,'REDUCTION_DENOMINATOR')
                    V=m+temporal+2*tt+B*Tp/D;drift=4*H+B*T/D
                    transformed=V+2*Hp-4*hh+2*drift*H;driftt=drift-4*H
                    beta=(21-1/(2+temporal))*D/(2*J)-ab(2*T*Tp)/J-2*ab(H)
                    vmin,vmax,amax,bmin=low[n]
                    gate(vmin<=transformed.lo and vmax>=ab(transformed).hi and amax>=ab(driftt).hi and bmin<=beta.lo,'LOW_ORDER_CELL_'+name+'_'+str(count)+'_'+str(n))
                count+=1
            prior=entry['sha256']
            if count%2048==0:print('audit',name,count,round(time.monotonic()-started,1),flush=True)
        gate(count==arm['cells'] and last==arm['final_native_background'],'COMPLETE_CHAIN')
        L=Q(ini['D'][0]);N=prod['N'];lam=Q(prod['lambda']);alpha=ext['alpha'];c=alpha/2
        gate(9<=N<=128 and lam==Q(1,128) and Q(prod['c'])==c,'HIGH_CONTRACT')
        KA,K,bb,L0,beta0,Kbeta=[ext[q] for q in ('KA','K','b','L0','beta0','Kbeta')]
        u2=r.hi*r.hi*ext['E2hi'];u1=3*r.hi*h.hi*ext['E2hi'];U0=ext['U0']
        A=KA/(N*N);v_required=u2+u1/N+U0/(N*N)+K/(N**4);v=Q(prod['v'])
        margins=dict(coercivity=alpha*N*N/2+bb*N+L0-K/(N*N),robin=beta0-Kbeta/(N*N)-1,barrier=c-lam*lam-A*lam/N,boundary_separation=lam*N*L-1,taylor_segment=N*L-2,derivative_absorption=1-A/(2*N))
        gate(Q(prod['A'])==A and v>=v_required,'HIGH_COEFFICIENTS_OUTWARD')
        gate({q:str(v) for q,v in margins.items()}==prod['high_gates'],'HIGH_MARGIN_REPLAY')
        gate(all(v>=0 for v in margins.values()) and margins['derivative_absorption']>0,'HIGH_POSITIVITY')
        C0=max(1/c,4/lam);C1=((2+v/2)*C0+Q(1,2))/(1-A/(2*N));C2=A*C1/N+v*C0+1
        gate(prod['high_constants']==dict(value=str(C0),first=str(C1),second=str(C2),sum=str(C0+C1+C2)),'HIGH_CONSTANTS')
        values=[C0+C1+C2]
        gate(set(prod['finite_orders'])==set(map(str,range(2,N))),'FINITE_INVENTORY')
        for n in range(2,N):
            required=low[n] if n<=8 else (alpha*n*n+bb*n+L0-K/(n*n),u2*n*n+u1*n+U0+K/(n*n),KA/(n*n),beta0-Kbeta/(n*n))
            record=prod['finite_orders'][str(n)];bounds=tuple(map(Q,record['bounds']))
            gate(bounds[0]<=required[0] and bounds[1]>=required[1] and bounds[2]>=required[2] and bounds[3]<=required[3],'FINITE_BOUNDS_OUTWARD')
            V,U,A,beta=bounds;gate(V>0 and beta>0,'FINITE_POSITIVITY')
            ell=min(L/2,1/(A+1));a0=max(1/V,1/(n*beta));a1=((2/ell+ell*U/2)*a0+ell/2)/(1-A*ell/2);a2=A*a1+U*a0+1
            val=n*n*a0+n*a1+a2
            gate(Q(record['constant'])==val,'FINITE_CONSTANT_REPLAY');values.append(val)
        Cy=max(values);H0,Hp0=ext['H'],ext['Hp'];transfer=ext['E2hi']/ext['E2lo']*max(1+H0+H0*H0+Hp0/2,1+2*H0,Q(1));Cf=Cy*transfer;integer=-((-Cf.numerator)//Cf.denominator)
        gate(Q(prod['C_y'])==Cy and Q(prod['C_f'])==Cf and Q(prod['f_transfer_multiplier'])==transfer and prod['C_f_outward_integer']==integer,'TRANSFER_CONSTANT')
        reports[name]=dict(cells=count,N=N,C_f_outward_integer=integer,finite_orders_checked=N-2)
    gate(result['scientific_certificate'] and result['unresolved']==[] and result['common_C_f_outward_integer']==max(a['C_f_outward_integer'] for a in reports.values()),'FINAL_CLASSIFICATION')
    gate(lease.observed()==runtime,'RUNTIME_UNCHANGED');gate(all(sha(p)==h for p,h in inputs.items()),'INPUTS_UNCHANGED')
    out=dict(pass_status=True,classification='ALL_NEUTRAL_ORDER_EXACT_REDUCTION_AUDIT_PASS',production_terminal_sha256=pin,checks=checks,arms=reports,seconds=time.monotonic()-started,scope='Exact rational recomputation of cell scalar bounds, low-order positivity, high-order and finite-order inverse constants, and E-squared transfer. Canonical background tube existence and input eigenmode remain inherited; no new ODE solve or nonlinear convergence claim.')
    put('AUDIT_RESULT.json',out);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(out),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_PIN_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE_PIN')
        lease=load('inverse_exact_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('INVERSE_AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
