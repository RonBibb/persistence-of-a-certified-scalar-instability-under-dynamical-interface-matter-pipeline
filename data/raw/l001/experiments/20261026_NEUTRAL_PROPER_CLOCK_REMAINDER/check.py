"""Exact proper-clock observable consequence of the neutral convergence bound."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
MAJOR=BASE/'20261026_NEUTRAL_SOURCE_MAJORANT';WALL=BASE/'20261026_NEUTRAL_WALL_IDENTITY';FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';DEADLINE=1793047195
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
def decade(q):
    need(q>0,'POSITIVE_DISPLAY');j=0
    while q<1:q*=10;j-=1
    while q>=10:q/=10;j+=1
    v=q*10**6;return dict(floor_log10=j,mantissa_floor_millionths=v.numerator//v.denominator)
def main(lease,wall_audit_pin):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    for root,pin in [(MAJOR,'7081dcf2fce22ae857bd14b88da5a1a19e56208e35db1b08eadff469137501d7'),(WALL,'f8820ce6d0f2871e7dcb1d236e33229123a37458f6849af2beb0dfe9b340d50b')]:
        bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
        for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:bind(root/n,t[k])
        for group in ('inputs','sources','runtime'):
            for p,h in read(root/'BINDING.json').get(group,{}).items():bind(p,h)
    for root,pin in [(MAJOR/'audit','aecbf787bc2a7d928e9ac4ce0918728e645213eeb82a3a6027c02a12c2bc9d8d'),(WALL/'audit',wall_audit_pin)]:
        bind(root/'AUDIT_TERMINAL.json',pin);t=read(root/'AUDIT_TERMINAL.json');need(t.get('pass_status',t.get('pass')),'AUDIT_PASS')
        for n,k in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:bind(root/n,t[k])
        if 'derivation_sha256' in t:bind(root/'DERIVATION.txt',t['derivation_sha256'])
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,wall_audit_pin=wall_audit_pin,deadline_unix=DEADLINE))
    for arm in ('primary','independent'):
        p=FRESH/('INITIAL_'+arm+'.json');need(inputs.get(str(p))==sha(p),'INITIAL_BINDING');initial=read(p)
        y=initial['initial_native'];pindex=5 if arm=='primary' else 4
        gate(y[0]['exact_bounds']==['0','0'],'BACKGROUND_LOG_A_ZERO:'+arm)
        gate(y[pindex]['exact_bounds']==['1','1'],'LOWER_P1_UNITY:'+arm)
        if arm=='primary':gate(y[4]['exact_bounds']==['1','1'],'LOWER_E_UNITY')
        rlo,rhi=map(Q,initial['parameters']['rate']['exact_bounds']);hlo,hhi=map(Q,initial['parameters']['h']['exact_bounds'])
        gate(Q(1,64)<rlo<=rhi<=Q(1,32) and hhi<rlo,'RATE_AND_FIRST_GRAPH_DIVISOR:'+arm)
    mr=read(MAJOR/'RESULT.json');c={k:Q(v) for k,v in mr['constants_exact'].items()}
    for key,pair in mr['coefficient_enclosures'].items():
        lo,hi=map(Q,pair)
        if key.endswith(':d1'):gate(-54<lo<=hi<-50,'LINEAR_SIGN:'+key)
        if key.endswith(':d2'):gate(hi<-1400,'QUADRATIC_SIGN:'+key)
    # Algebraic normalized clock coefficient is exactly one; rate bounds
    # and these interval inequalities imply F2<-1346/64<-21.
    gate(Q(-1346,64)<-21,'PROPER_CLOCK_QUADRATIC_MARGIN')
    R=c['R'];gap=c['gap'];rho_D=c['eta_physical_radius'];MD=c['observable_sup'];rho_F=rho_D/2
    gate(4*R<gap and R<1,'CHART_ENVELOPE_DOMAIN')
    Z=64/(1-4*R/gap);E1=1/(1-R);vbound=4*R*Z*E1**2
    gate(vbound<Q(1,2),'TIMELIKE_WALL')
    lapse_inverse_bound=Z*E1/(1-vbound**2);gate(lapse_inverse_bound<=128,'INVERSE_PROPER_LAPSE_BOUND')
    inv=read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact'];delta=Q(inv['delta'])
    gate(delta<Q(1,4),'REAL_BACKGROUND_E_POSITIVE')
    MF=Q(129,32)*MD;selected=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=rho_F*q;tail=MF*q**3/(1-q);qD=q/2;distance_tail=MD*qD**2/(1-qD)
        if tail<=10*eta**2 and distance_tail<=25*eta:selected=(j,q,eta,tail,distance_tail);break
    gate(selected is not None,'SIGNED_EXACT_CLOCK_SUBDISK');j,q,eta,tail,distance_tail=selected
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    exact=dict(rho_D=rho_D,rho_F=rho_F,MD=MD,MF=MF,lapse_inverse_bound=lapse_inverse_bound,velocity_bound=vbound,q=q,eta=eta,F_tail=tail,D_tail_after_linear=distance_tail)
    result=dict(pass_status=True,classification='LOCAL_EXACT_NEUTRAL_SHORTENING_REINFORCED_IN_LOWER_WALL_PROPER_TIME',constants_exact={k:str(v) for k,v in exact.items()},display={k:decade(exact[k]) for k in ('eta','F_tail','D_tail_after_linear')},selected_dyadic_halvings=j,gates=gates,conclusion='For every0<eta<=selected_eta, x=D-D0<=-25eta<0 and dx/dtau_a-rx<=-11eta²<0.',seconds=time.monotonic()-started,new_ode_solves=0,scope='Exact local analytic pure-growing branch in the selected homogeneous slicing and lower-wall proper clock, with fixed authenticated background/mode premises. No generic-data evolution, saturation, contact, horizon, or endpoint. Does not resolve the proper-clock cubic normal-form coefficient sign.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','display','selected_dyadic_halvings','conclusion','seconds')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_PIN_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_clock_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CLOCK_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
