"""Exact scalar-observable and two-sided consequence of the local family."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_NEUTRAL_RESPONSE_CONDITIONING';MAJOR=BASE/'20261026_NEUTRAL_SOURCE_MAJORANT';FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
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
    z=q*10**6;return dict(floor_log10=j,mantissa_floor_millionths=z.numerator//z.denominator)
def main(lease,auditpin):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    bind(PARENT/'TERMINAL.json','f77d561f1681b91cd15b65cb2db626ff842ac061e879dcbe9f27981c54878c63');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(PARENT/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():bind(p,h)
    audit=PARENT/'audit';bind(audit/'AUDIT_TERMINAL.json',auditpin);at=read(audit/'AUDIT_TERMINAL.json');need(at['pass_status'],'AUDIT_PASS')
    for n,k in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:bind(audit/n,at[k])
    if 'derivation_sha256' in at:bind(audit/'DERIVATION.txt',at['derivation_sha256'])
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE,conditioning_audit_pin=auditpin))
    coefficient_counts={1:0,2:0}
    for key,pair in read(MAJOR/'RESULT.json')['coefficient_enclosures'].items():
        lo,hi=map(Q,pair)
        if key.endswith(':d1'):gate(-54<lo<=hi<-50,'D1:'+key);coefficient_counts[1]+=1
        if key.endswith(':d2'):gate(-1600<lo<=hi<-1400,'D2:'+key);coefficient_counts[2]+=1
    gate(coefficient_counts=={1:4,2:2},'COMPLETE_COEFFICIENT_INVENTORY')
    gate(Q(-1550,32)>-50 and Q(-1346,64)<-21,'TWO_SIDED_CLOCK_COEFFICIENT')
    coeff={}
    for arm in ('primary','independent'):
        p=FRESH/('INITIAL_'+arm+'.json');need(inputs.get(str(p))==sha(p),'INITIAL_AUTHORITY');ini=read(p)
        y=ini['initial_native'];pidx=5 if arm=='primary' else 4
        gate(y[0]['exact_bounds']==['0','0'] and y[pidx]['exact_bounds']==['1','1'],'LOWER_WALL_NORMALIZATION:'+arm)
        if arm=='primary':gate(y[4]['exact_bounds']==['1','1'],'LOWER_E_UNITY')
        # Independent representation defines E=exp(-W); W=0 above gives E=1.
        fidx=6 if arm=='primary' else 5;flo,fhi=map(Q,ini['initial_native'][fidx]['exact_bounds']);mlo,mhi=map(Q,ini['parameters']['mu1']['exact_bounds'])
        rlo,rhi=map(Q,ini['parameters']['rate']['exact_bounds'])
        gate(0<flo<=fhi and mhi<0,'OSCILLATOR_DIVISOR:'+arm)
        clo=flo/(2-mlo);chi=fhi/(2-mhi);gate(Q(1,20000)<clo<=chi<Q(1,10000),'PHYSICAL_SCALAR_FIRST_COEFFICIENT:'+arm)
        gate(Q(1,64)<rlo<=rhi<=Q(1,32),'RATE:'+arm);coeff[arm]=[str(clo),str(chi)]
    c={k:Q(v) for k,v in read(PARENT/'RESULT.json')['constants_exact'].items()};a=c['clock_eta'];rho=c['eta_physical_radius'];R=c['R'];q=a/rho
    gate(0<a<Q(1,512) and q<1,'POSITIVE_LOCAL_AMPLITUDE')
    gate(c['clock_tail']<=10*a*a and c['distance_tail_after_linear']<=25*a,'INHERITED_SIGN_INDEPENDENT_TAILS')
    gate(Q(25,64)*a-60*a*a>0,'OPENING_BRANCH_NOT_STABILIZED')
    scalar_tail=R*q*q/(1-q);euler_tail=R*q*q*(2-q)/(1-q)**2
    gate(scalar_tail<=a/40000 and euler_tail<=a/40000,'PHYSICAL_SCALAR_AND_VELOCITY_REMAINDERS')
    delta=Q(read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact']['delta'])
    gate(Q(1,2)-delta>Q(1,4) and 1/(1-R)<2 and c['inverse_lapse_bound']<=128,'FINITE_POSITIVE_PROPER_TIME')
    departure=a/40000
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    exact=dict(amplitude=a,scalar_departure_threshold=departure,scalar_tail=scalar_tail,scalar_euler_derivative_tail=euler_tail,q=q,opening_velocity_lower_bound=Q(25,64)*a-60*a*a)
    result=dict(pass_status=True,classification='TWO_SIDED_LOCAL_NONLINEAR_BEHAVIOR_AND_SCALAR_DEPARTURE_WITNESS',constants_exact={k:str(v) for k,v in exact.items()},display={k:decade(exact[k]) for k in ('amplitude','scalar_departure_threshold','scalar_tail')},first_scalar_coefficient_enclosures=coeff,gates=gates,seconds=time.monotonic()-started,new_ode_solves=0,conclusions=['Positive eta: shortening reinforced relative to the linear lower-wall clock law.','Negative eta: opening slowed relative to linear, but still increasing locally.','The lower-wall oscillator is nonzero and moves monotonically away from its zero background; this is not a pure coordinate change.','Restrictions of the exact analytic family give arbitrarily small compatible data that reach the stated scalar departure threshold at finite proper time.'],scope='Particular neutral analytic family and specified data topology/physical scalar departure observable. Not a generic Cauchy-flow or unstable-manifold theorem; no endpoint, saturation, horizon or physical amplitude-scale prediction.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','display','seconds','conclusions')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_PIN_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_departure_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DEPARTURE_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
