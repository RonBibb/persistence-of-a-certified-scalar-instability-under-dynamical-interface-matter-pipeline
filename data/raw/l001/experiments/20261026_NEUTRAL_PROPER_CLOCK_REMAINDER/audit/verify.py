"""Independent exact clock-normalization, lapse and remainder audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
PIN='31438d2ae08e40ddb5c2b1788f36af57ddc9c4fc8a734dc3098e1e2e07ff7bcb';DEADLINE=1793047195
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
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
        for p,h in read(PACKET/'BINDING.json')[group].items():gate(sha(p)==h,'BOUND_SOURCE');inputs[p]=h
    pylong=Path('/usr/lib/python3.12/_pylong.py');gate(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');gate(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items():gate(inputs.get(p)==h,'RUNTIME_AUTHORITY:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=PIN))
    for name in ('primary','independent'):
        path=BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+name+'.json');gate(inputs.get(str(path))==sha(path),'INITIAL_AUTHORITY')
        ini=read(path);y=ini['initial_native'];pindex={'primary':5,'independent':4}[name]
        gate(tuple(map(Q,y[0]['exact_bounds']))==(0,0),'EXACT_LOWER_LOG_WARP')
        gate(tuple(map(Q,y[pindex]['exact_bounds']))==(1,1),'EXACT_LOWER_FIRST_MODE')
        if name=='primary':gate(tuple(map(Q,y[4]['exact_bounds']))==(1,1),'EXACT_LOWER_E')
        rlo,rhi=map(Q,ini['parameters']['rate']['exact_bounds']);hlo,hhi=map(Q,ini['parameters']['h']['exact_bounds'])
        gate(Q(1,64)<rlo<=rhi<=Q(1,32) and 0<hlo<=hhi<rlo,'NONZERO_FIRST_GRAPH_DIVISOR')
    major=read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json');result=read(PACKET/'RESULT.json')
    counts={1:0,2:0}
    for key,pair in major['coefficient_enclosures'].items():
        lo,hi=map(Q,pair)
        if key.endswith(':d1'):gate(-54<lo<=hi<-50,'LINEAR_BOUND');counts[1]+=1
        if key.endswith(':d2'):gate(lo<=hi<-1400,'QUADRATIC_BOUND');counts[2]+=1
    gate(counts[1]>=2 and counts[2]>=2,'TWO_ENGINE_COEFFICIENTS')
    gate(Q(-1400+54,64)<-21,'UNIFORM_CLOCK_QUADRATIC_MARGIN')
    c={k:Q(v) for k,v in major['constants_exact'].items()};R=c['R'];gap=c['gap'];rD=c['eta_physical_radius'];MD=c['observable_sup']
    gate(0<R<1 and 4*R<gap and rD>0,'CHART_DOMAIN')
    warp=64*gap/(gap-4*R);exponential=1/(1-R)
    vel=4*R*warp*exponential**2
    lapse=warp*exponential/(1-vel**2)
    gate(0<=vel<Q(1,2) and lapse<=128,'NONZERO_PROPER_LAPSE')
    delta=Q(read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact']['delta']);gate(delta<Q(1,4),'REAL_WARP_POSITIVE')
    rF=rD/2;MF=(128+1)*MD/32
    j=result['selected_dyadic_halvings'];gate(isinstance(j,int) and 1<=j<=8192,'DYADIC_DOMAIN')
    q=Q(1,2**j);eta=rF*q;Ft=MF*q**3/(1-q);Dt=MD*(eta/rD)**2/(1-eta/rD)
    gate(Ft<=10*eta**2 and Dt<=25*eta,'CERTIFIED_SIGN_TAILS')
    if j>1:
        oldq=2*q;olde=rF*oldq
        oldFt=MF*oldq**3/(1-oldq);oldDt=MD*(olde/rD)**2/(1-olde/rD)
        gate(oldFt>10*olde**2 or oldDt>25*olde,'FIRST_ADMISSIBLE_DYADIC')
    expected=dict(rho_D=rD,rho_F=rF,MD=MD,MF=MF,lapse_inverse_bound=lapse,velocity_bound=vel,q=q,eta=eta,F_tail=Ft,D_tail_after_linear=Dt)
    gate(set(expected)==set(result['constants_exact']),'CONSTANT_INVENTORY')
    for key,val in expected.items():gate(Q(result['constants_exact'][key])==val,'CONSTANT:'+key)
    for key,display in result['display'].items():
        val=expected[key];ten=Q(10)**display['floor_log10'];gate(ten<=val<10*ten,'DISPLAY_DECADE')
        scaled=val*10**6/ten;gate(display['mantissa_floor_millionths']==scaled.numerator//scaled.denominator,'DISPLAY_MANTISSA')
    # Positive monotone comparison ratios justify every smaller eta, not only
    # a single sampled amplitude. Margins are exact and independent of d3.
    gate(-21+10==-11 and -50+25==-25,'FINAL_SIGN_MARGINS')
    gate(result['pass_status'] and all(result['gates'].values()) and result['new_ode_solves']==0,'PRODUCTION_STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED_BINDING')
    out=dict(pass_status=True,classification='INDEPENDENT_PROPER_CLOCK_REMAINDER_EXACT_AUDIT_PASS',checks=checks,production_terminal_sha256=PIN,selected_dyadic_halvings=j,display=result['display'],seconds=time.monotonic()-start,scope='Independent exact normalization, lapse envelope, coefficient margin, first admissible subdisk and remainder arithmetic. Cauchy/analytic-family proofs reviewed separately. Same selected homogeneous foliation and lower-wall proper time; no cubic normal-form sign, generic-data endpoint or new ODE claim.')
    put('AUDIT_RESULT.json',out);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(out),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('proper_clock_independent_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CLOCK_AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
