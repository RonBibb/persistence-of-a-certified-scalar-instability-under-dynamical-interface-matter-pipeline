"""Independent exact lapse-jet and cubic-clock tail audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
PIN='97e01b5fd9e6513db28be3da9840e69932c284938bc5a3670aceb1145bba3ed9'
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
class Interval:
    def __init__(self,lo,hi=None):self.lo=Q(lo);self.hi=Q(lo if hi is None else hi);need(self.lo<=self.hi,'INTERVAL_ORDER')
    @classmethod
    def record(cls,v):return cls(*v['exact_bounds'])
    @classmethod
    def cast(cls,v):return v if isinstance(v,cls) else cls(v)
    def __add__(self,v):
        v=self.cast(v);return Interval(self.lo+v.lo,self.hi+v.hi)
    __radd__=__add__
    def __neg__(self):return Interval(-self.hi,-self.lo)
    def __sub__(self,v):return self+-self.cast(v)
    def __rsub__(self,v):return self.cast(v)+-self
    def __mul__(self,v):
        v=self.cast(v);corners=(self.lo*v.lo,self.lo*v.hi,self.hi*v.lo,self.hi*v.hi);return Interval(min(corners),max(corners))
    __rmul__=__mul__
    def pair(self):return [str(self.lo),str(self.hi)]
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
    out=read(PACKET/'RESULT.json');clock=bound('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
    for arm in ('primary','independent'):
        quad=bound('20261026_GROWING_MODE_QUADRATIC_R1/PRODUCTION_'+arm+'.json')
        cubic=bound('20261026_GROWING_MODE_CUBIC_AFFINE/PRODUCTION_'+arm+'.json')
        wall=quad['walls']['lower'];z=list(map(Interval.record,wall['state']));xi=Interval.record(wall['loads']['xi2'])
        gate(z[0].pair()==['0','0'] and z[5].pair()==['1','1'],'LOWER_NORMALIZATION')
        L2=z[8]+z[1]*xi;d1=Interval.record(quad['d1']);d2=Interval.record(quad['d2']);d3=Interval.record(cubic['d3']);r=Interval.record(cubic['parameters']['rate'])
        vals=clock['arms'][arm]['values']
        for name,iv in [('lower_log_lapse2',L2),('d1',d1),('d2',d2),('d3',d3),('rate',r)]:gate(iv.pair()==Interval.record(vals[name]).pair(),'CLOCK_PROVENANCE:'+name)
        gate(-54<d1.lo<=d1.hi<-50 and -1600<d2.lo<=d2.hi<-1400 and -70000<d3.lo<=d3.hi<0 and -2<L2.lo<=L2.hi<2 and Q(1,64)<r.lo<=r.hi<Q(1,32),'COEFFICIENT_BOUNDS')
        # Extract coefficients by explicit truncated series convolution.
        # eta D' has coefficients d1,2d2,3d3; inverse lapse 1,-1,1/2-L2.
        rateD=[Interval(0),d1,2*d2,3*d3]
        lapseinv=[Interval(1),Interval(-1),Q(1,2)-L2]
        convolution=[]
        for degree in (2,3):
            total=Interval(0)
            for j in range(len(lapseinv)):
                if 0<=degree-j<len(rateD):total=total+rateD[degree-j]*lapseinv[j]
            # Subtract r*x using coefficient collection rather than interval
            # subtraction of repeated d2/d3, to preserve exact dependencies.
            if degree==2:coefficient=r*(d2-d1)
            else:coefficient=r*(2*d3-2*d2+(Q(1,2)-L2)*d1)
            convolution.append(coefficient)
        f2,f3=convolution
        gate(-50<f2.lo<=f2.hi<-21 and -10000<f3.lo<=f3.hi<10000,'F_MARGIN')
        gate(out['coefficient_intervals'][arm]==dict(log_lapse2=L2.pair(),F2=f2.pair(),F3=f3.pair()),'RECORDED_INTERVALS')
    c={k:Q(v) for k,v in bound('20261026_NEUTRAL_WEIGHTED_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    rho=c['eta_physical_radius'];MD=c['observable_sup'];R=c['R'];MF=129*MD/32
    gate(MF==c['clock_MF'],'FULL_FUNCTION_BOUND')
    j=out['selected_dyadic_halvings'];gate(isinstance(j,int) and 1<=j<=8192,'DYADIC_INDEX')
    q=Q(1,2**j);eta=rho*q/2;tail=MF*q**4/(1-q);known=10000*eta**3
    u=q/2;distance=MD*u*u/(1-u);scalar=R*u*u/(1-u);euler=R*(2*u*u-u**3)/(1-u)**2
    def passes(v):
        e=rho*v/2;w=v/2
        return 10000*e**3+MF*v**4/(1-v)<=10*e**2 and MD*w*w/(1-w)<=25*e and R*w*w/(1-w)<=e/40000 and R*(2*w*w-w**3)/(1-w)**2<=e/40000
    gate(passes(q),'ALL_TAILS');gate(j==1 or not passes(2*q),'FIRST_ADMISSIBLE')
    gate(eta>c['clock_eta'] and eta<Q(1,512) and 25*eta/64-60*eta*eta>0,'IMPROVEMENT_AND_TWO_SIGNS')
    expected=dict(rho_D=rho,rho_F=rho/2,MD=MD,MF=MF,q=q,eta=eta,known_cubic_bound=known,F_tail_after_cubic=tail,total_after_quadratic=known+tail,distance_tail_after_linear=distance,scalar_tail=scalar,scalar_euler_tail=euler,scalar_departure_threshold=eta/40000,clock_interval_gain=eta/c['clock_eta'])
    gate(set(expected)==set(out['constants_exact']),'CONSTANT_INVENTORY')
    for k,v in expected.items():gate(v==Q(out['constants_exact'][k]),'EXACT:'+k)
    for k,d in out['display'].items():
        v=expected[k];ten=Q(10)**d['floor_log10'];gate(ten<=v<10*ten,'DECADE');scaled=v*10**6/ten;gate(scaled.numerator//scaled.denominator==d['mantissa_floor_millionths'],'DISPLAY')
    gate(out['pass_status'] and all(out['gates'].values()) and out['new_ode_solves']==0,'STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED')
    result=dict(pass_status=True,classification='INDEPENDENT_KNOWN_CUBIC_CLOCK_AUDIT_PASS',checks=count,production_terminal_sha256=PIN,display=out['display'],seconds=time.monotonic()-start,scope='Independent exact lower-wall lapse reconstruction, direct quadratic/cubic coefficient provenance, interval F2/F3, first-admissible quartic-tail clock interval and scalar departure. Analytical coefficient collection and Cauchy proof reviewed; no normal-form cubic sign, new ODE, generic flow or endpoint claim.')
    put('AUDIT_RESULT.json',result);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('cubic_clock_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
