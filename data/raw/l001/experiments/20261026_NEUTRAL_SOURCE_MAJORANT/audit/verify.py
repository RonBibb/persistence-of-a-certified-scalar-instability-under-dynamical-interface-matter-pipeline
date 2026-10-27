"""Independent rational envelope, contraction and observable-tail replay."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent; PACKET=ROOT.parent; BASE=PACKET.parent
INV=BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE'; SEED=BASE/'20261026_NEUTRAL_ANALYTIC_SEED'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
PIN='7081dcf2fce22ae857bd14b88da5a1a19e56208e35db1b08eadff469137501d7'; DEADLINE=1793047195
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def ceil(v):return -((-v.numerator)//v.denominator)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;tmp=ROOT/(n+'.tmp')
    with tmp.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,p);tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(lease):
    start=time.monotonic();checks=0
    def gate(v,n):
        nonlocal checks
        need(v,n);checks+=1
    gate(sha(PACKET/'TERMINAL.json')==PIN,'PRODUCTION_PIN');t=read(PACKET/'TERMINAL.json');gate(t['pass_status'],'PRODUCTION_PASS')
    inputs={str(PACKET/'TERMINAL.json'):PIN,str(Path(__file__)):sha(__file__)}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
        gate(sha(PACKET/n)==t[k],'PRODUCTION_RECORD');inputs[str(PACKET/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PACKET/'BINDING.json')[group].items():gate(sha(p)==h,'BOUND_INPUT');inputs[p]=h
    pylong=Path('/usr/lib/python3.12/_pylong.py');gate(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');gate(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items():gate(inputs.get(p)==h,'RUNTIME_AUTHORITY:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=PIN))
    result=read(PACKET/'RESULT.json');iv={k:Q(v) for k,v in read(INV/'RESULT.json')['constants_exact'].items()};seed=read(SEED/'RESULT.json')
    rho=iv['rho'];gap=iv['prior_radius']-rho;d0=iv['real_D_normalized_lower'];dc=iv['complex_D_normalized_lower']
    gate(0<rho<=Q(1,4) and gap>0,'COLLAR')
    for name in ('primary','independent'):
        ini=read(BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+name+'.json'))
        lo,hi=map(Q,ini['D']);gate(1<=lo<=hi<=3,'INTERVAL_LENGTH')
    x=min(Q(1,4096),gap/16)
    gate(1-2*x>0 and 1-x>0 and gap-4*x>0,'ENVELOPE_DOMAINS')
    reciprocal=1/(1-2*x); background=64*gap/(gap-4*x); exp1=1/(1-x); exp2=reciprocal
    shift=4*x*reciprocal; shift_s=2*x*reciprocal; shift_t=4*x*reciprocal+8*(x*reciprocal)**2
    first=x+shift*x; second=x+2*shift*x+shift*shift_s*x+shift_t*x+shift**2*x
    radial=x*reciprocal; radial2=x*reciprocal**2
    env={}
    env['BT']=3*(second+first)+6*first**2
    env['BM']=reciprocal*(x+shift_s*x+shift*x)+first*(background+radial)+first*(background+radial)/3
    env['BK']=background**2*exp2*(second+3*first+3*first**2)+exp2*(background+radial2+(4*background+5*radial)*(background+radial))+background+x
    env['BR']=exp2*(6*(background+radial)**2+(background+radial)**2/2)+6+(background+x)**2/2+background**2*exp2*(6+3*second+9*first+3*first**2+first**2/2)
    lapseinv=background*exp1; velocity=4*x*background*exp1**2
    velocity_t=background*exp1**2*(4*x+8*x*x+16*background*x*x)
    gate(0<=velocity<Q(1,2),'BOOST_DOMAIN');boost=1/(1-velocity**2)
    env['BI']=lapseinv*boost**2*velocity_t+lapseinv*boost*velocity*(2*first+1)+lapseinv**2*boost*x*x/2
    env['BJ']=boost*exp1*(background+radial)+boost*velocity*lapseinv*first+1+Q(21,2)*(background+1+x)+x/2
    env['BO']=lapseinv**2*boost*(x+3*x+8*background*x*x+2*x*x+velocity*velocity_t*boost*x)+3*x+background+1
    gate(set(env)==set(result['envelopes_exact']),'ENVELOPE_INVENTORY')
    for k,v in env.items():gate(v>0 and Q(result['envelopes_exact'][k])==v,'ENVELOPE:'+k)
    mass=sum(env.values()); trace=Q(8192)*(1+9/rho+81/rho**2); graph=Q(32768); oscillator=Q(16384)
    momentum=3*trace/2+64; constraint=18*momentum+28*trace+1; scalar=2*trace+6*momentum+1
    force=scalar+20*constraint/dc; robinraw=trace+39*graph/4+Q(5,2)
    robin=(Q(1,2)+1/(4*d0))*robinraw+constraint/d0
    Cf=Q(ceil(iv['scalar_C']));Cp=Q(ceil(iv['metric_C']));s=Q(ceil(Q(seed['seed_norm'])))
    uf=Cf*(force+robin);up=Cp*(constraint+uf+momentum);uc=oscillator*(uf/2+graph/4+1)
    response=3*up+trace+uf+2*(graph+uc)
    K=Q(ceil(max(Q(1),1/x,2*response*mass/x**2)))
    gate(K*x>=1 and K>=2*response*mass/x**2,'ALL_M_COEFFICIENT_DOMINATION')
    R=1/(96*K);radius=R/(2*s);physical=radius/4
    # Full contraction formulas, not just the conservative lemma constants.
    qK=K*R;gate(R>0 and s>0 and qK<1,'MAJORANT_DOMAIN')
    gate(s*radius+K*R**2/(1-qK)**2<R,'DISK_SELF_MAP')
    gate(2*K*R/(1-qK)**2+2*K*K*R*R/(1-qK)**3<Q(1,2),'UNIFORM_CONTRACTION')
    gate(4*R<gap and 2*R<1,'CHART_COMPOSITION_DOMAIN')
    observable=3*3*R/(1-R)
    j=result['selected_dyadic_halvings'];gate(isinstance(j,int) and 1<=j<=8192,'DYADIC_RANGE')
    q=Q(1,2**j);eta=physical*q;tail=observable*q**4/(1-q)
    def passes(z):
        amplitude=physical*z;error=observable*z**4/(1-z)
        return error<=700*amplitude**2 and error<=20000*amplitude**3
    gate(passes(q),'QUADRATIC_AND_CUBIC_TAIL_SIGN')
    gate(j==1 or not passes(2*q),'FIRST_ADMISSIBLE_DYADIC')
    expected=dict(rho=rho,gap=gap,a=x,M=mass,Cc=trace,Csp=momentum,Csc=constraint,Csg=scalar,CF=force,CR=robinraw,CG=robin,Cscalar=Cf,Cmetric=Cp,seed=s,Uf=uf,Up=up,Uchi=uc,C=response,K=K,R=R,eta_majorant_radius=radius,eta_physical_radius=physical,observable_sup=observable,selected_q=q,selected_eta=eta,selected_tail=tail)
    gate(set(expected)==set(result['constants_exact']),'CONSTANT_INVENTORY')
    for k,v in expected.items():gate(Q(result['constants_exact'][k])==v,'CONSTANT:'+k)
    for k,display in result['display'].items():
        v=expected[k];exponent=display['floor_log10'];ten=Q(10)**exponent
        gate(ten<=v<10*ten,'DISPLAY_DECADE:'+k)
        scaled=v*10**6/ten;gate(display['mantissa_floor_millionths']==scaled.numerator//scaled.denominator,'DISPLAY_MANTISSA:'+k)
    inventory={}
    for folder,orders in [('20261026_GROWING_MODE_QUADRATIC_R1',(1,2)),('20261026_GROWING_MODE_CUBIC_AFFINE',(1,3))]:
        for engine in ('primary','independent'):
            path=BASE/folder/('PRODUCTION_'+engine+'.json');gate(inputs.get(str(path))==sha(path),'COEFFICIENT_AUTHORITY')
            r=read(path)
            for order in orders:
                lo,hi=map(Q,r['d'+str(order)]['exact_bounds']);floor={1:50,2:1400,3:40000}[order]
                gate(lo<=hi<-floor,'SIGNED_COEFFICIENT');inventory[folder+':'+engine+':d'+str(order)]=[str(lo),str(hi)]
    gate(inventory==result['coefficient_enclosures'],'COEFFICIENT_INVENTORY')
    gate(result['pass_status'] and all(result['gates'].values()) and result['new_ode_solves']==0,'RESULT_STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE,'RESOURCE_LIMIT')
    gate(lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED_AUTHORITY')
    output=dict(pass_status=True,classification='INDEPENDENT_NEUTRAL_SOURCE_MAJORANT_EXACT_AUDIT_PASS',checks=checks,production_terminal_sha256=PIN,selected_dyadic_halvings=j,display=result['display'],seconds=time.monotonic()-start,scope='Independent exact rational seven-envelope, response-chain, contraction, chart-domain, coefficient-binding and observable-tail arithmetic. Source-envelope proof and all-order residual identities reviewed analytically; canonical background/spectral premises and standard analytic theorems inherited. No new ODE or global nonlinear endpoint claim.')
    put('AUDIT_RESULT.json',output);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps(output),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('majorant_independent_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('MAJORANT_AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
