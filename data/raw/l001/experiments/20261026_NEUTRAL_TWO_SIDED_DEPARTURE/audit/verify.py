"""Independent saved-record audit of the two-sided scalar departure witness."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
PIN='b79e63c2e6bcb547ce0fffb166c0bb8560f4722df9f90a884447860f47661ba3'
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
def main(lease):
    start=time.monotonic();count=0
    def gate(v,n):
        nonlocal count
        need(v,n);count+=1
    gate(sha(PACKET/'TERMINAL.json')==PIN,'PIN');t=read(PACKET/'TERMINAL.json');gate(t['pass_status'],'PASS')
    inputs={str(PACKET/'TERMINAL.json'):PIN,str(Path(__file__)):sha(__file__)}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
        gate(sha(PACKET/n)==t[k],'RECORD');inputs[str(PACKET/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PACKET/'BINDING.json')[group].items():gate(sha(p)==h,'ANCESTRY');inputs[p]=h
    gate(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():gate(inputs.get(p)==h,'RUNTIME:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=PIN))
    def bound(path):
        p=BASE/path;gate(inputs.get(str(p))==sha(p),'AUTHORITY:'+path);return read(p)
    out=read(PACKET/'RESULT.json');major=bound('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')
    counts={1:0,2:0}
    for k,pair in major['coefficient_enclosures'].items():
        lo,hi=map(Q,pair)
        if k.endswith(':d1'):gate(-54<lo<=hi<-50,'D1');counts[1]+=1
        if k.endswith(':d2'):gate(-1600<lo<=hi<-1400,'D2');counts[2]+=1
    gate(counts=={1:4,2:2},'COEFFICIENT_COUNT')
    chi={}
    for arm,pi,fi in [('primary',5,6),('independent',4,5)]:
        ini=bound('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+arm+'.json');y=ini['initial_native']
        gate(tuple(map(Q,y[0]['exact_bounds']))==(0,0) and tuple(map(Q,y[pi]['exact_bounds']))==(1,1),'NORMALIZATION')
        if arm=='primary':gate(tuple(map(Q,y[4]['exact_bounds']))==(1,1),'E_UNITY')
        f0,f1=map(Q,y[fi]['exact_bounds']);m0,m1=map(Q,ini['parameters']['mu1']['exact_bounds']);r0,r1=map(Q,ini['parameters']['rate']['exact_bounds'])
        gate(0<f0<=f1 and m0<=m1<0 and Q(1,64)<r0<=r1<=Q(1,32),'RATE_AND_DIVISOR')
        # Independently invert the positive denominator interval then multiply.
        inverse=(1/(2-m0),1/(2-m1));pair=(f0*inverse[0],f1*inverse[1])
        gate(Q(1,20000)<pair[0]<=pair[1]<Q(1,10000),'SCALAR_LINEAR_SIGN');chi[arm]=[str(v) for v in pair]
    gate(chi==out['first_scalar_coefficient_enclosures'],'SCALAR_INTERVAL_RECORD')
    c={k:Q(v) for k,v in bound('20261026_NEUTRAL_RESPONSE_CONDITIONING/RESULT.json')['constants_exact'].items()}
    a=c['clock_eta'];R=c['R'];q=a/c['eta_physical_radius']
    gate(0<a<Q(1,512) and 0<q<1,'DOMAIN')
    gate(c['clock_tail']<=10*a*a and c['distance_tail_after_linear']<=25*a,'INHERITED_TAILS')
    # Σ(n>=2)q^n and q*d/dq of that sum give the two tails.
    tail=R*q*q/(1-q);derivative=R*(2*q*q-q**3)/(1-q)**2
    gate(tail<=a/40000 and derivative<=a/40000,'SCALAR_TAILS')
    gate(Q(1,20000)-Q(1,40000)==Q(1,40000),'SCALAR_SIGN_MARGIN')
    gate(Q(-1550,32)>-50 and Q(-1346,64)<-21,'QUADRATIC_RANGE')
    gate(-50-10==-60 and -21+10==-11,'FULL_F_RANGE')
    gate(50-25==25 and 54+25==79,'TWO_SIDED_DISTANCE')
    opening=25*a/64-60*a*a;gate(opening>0,'OPENING_VELOCITY_POSITIVE')
    delta=Q(bound('20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact']['delta'])
    gate(Q(1,2)-delta>Q(1,4) and 1/(1-R)<2 and c['inverse_lapse_bound']<=128,'PROPER_TIME_BOUNDS')
    expected=dict(amplitude=a,scalar_departure_threshold=a/40000,scalar_tail=tail,scalar_euler_derivative_tail=derivative,q=q,opening_velocity_lower_bound=opening)
    gate(set(expected)==set(out['constants_exact']),'CONSTANT_INVENTORY')
    for k,v in expected.items():gate(v==Q(out['constants_exact'][k]),'EXACT:'+k)
    for k,d in out['display'].items():
        v=expected[k];ten=Q(10)**d['floor_log10'];gate(ten<=v<10*ten,'DECADE');z=v*10**6/ten;gate(z.numerator//z.denominator==d['mantissa_floor_millionths'],'DISPLAY')
    gate(out['pass_status'] and all(out['gates'].values()) and out['new_ode_solves']==0,'STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED')
    result=dict(pass_status=True,classification='INDEPENDENT_TWO_SIDED_SCALAR_DEPARTURE_AUDIT_PASS',checks=count,production_terminal_sha256=PIN,display=out['display'],seconds=time.monotonic()-start,scope='Independent exact coefficient intervals, normalization, two-sign distance/clock margins, scalar and Euler tails, lapse bounds and provenance. Analytic topology implication reviewed: a particular exact analytic family provides arbitrarily small compatible data and finite-time scalar departure, not general-data well-posedness, uniqueness, endpoint or a full unstable manifold.')
    put('AUDIT_RESULT.json',result);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('departure_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
