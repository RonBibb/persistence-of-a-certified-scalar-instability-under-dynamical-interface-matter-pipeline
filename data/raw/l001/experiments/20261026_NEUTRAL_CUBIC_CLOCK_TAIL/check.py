"""Exact known-cubic tail certificate; source-bound, no ODE solves."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_NEUTRAL_WEIGHTED_SOURCE_MAJORANT'
CLOCK=BASE/'20261026_GROWING_MODE_CLOCK_READOUT'
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
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
def iv(v):return tuple(map(Q,v['exact_bounds']))
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def neg(a):return (-a[1],-a[0])
def mul(a,b):
    c=[x*y for x in a for y in b];return min(c),max(c)
def scale(a,k):return mul(a,(Q(k),Q(k)))
def pack(a):return list(map(str,a))
def decade(q):
    need(q>0,'POSITIVE_DISPLAY');j=0
    while q<1:q*=10;j-=1
    while q>=10:q/=10;j+=1
    z=q*10**6;return dict(floor_log10=j,mantissa_floor_millionths=z.numerator//z.denominator)
def main(lease,auditpin):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    for root,pin in ((PARENT,'a514a572c03946c707cc6cff14624db74168f6803b818d6c8a849cda412176be'),(CLOCK,'2990c175d97b42698c2f27ab34219a9755690711d5ff45d0dd1e9b949baa7a9d')):
        bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
        source='check.py' if root==PARENT else 'run.py'
        for n,k in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),(source,'source_sha256')):bind(root/n,t[k])
        if 'derivation_sha256' in t:bind(root/'DERIVATION.txt',t['derivation_sha256'])
        for group in ('inputs','sources','runtime'):
            for p,h in read(root/'BINDING.json')[group].items():bind(p,h)
    ar=PARENT/'audit';bind(ar/'AUDIT_TERMINAL.json',auditpin);at=read(ar/'AUDIT_TERMINAL.json');need(at['pass_status'],'AUDIT_PASS')
    for n,k in (('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')):bind(ar/n,at[k])
    if 'derivation_sha256' in at:bind(ar/'DERIVATION.txt',at['derivation_sha256'])
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE))
    clock=read(CLOCK/'RESULT.json');coeff={}
    for arm in ('primary','independent'):
        p=QUAD/('PRODUCTION_'+arm+'.json');need(str(p) in inputs,'QUADRATIC_BOUND')
        rec=read(p);wall=rec['walls']['lower'];z=list(map(iv,wall['state']))
        xi=iv(wall['loads']['xi2']) if 'loads' in wall else iv(wall['xi2'])
        L2=add(z[8],mul(z[1],xi));vals=clock['arms'][arm]['values']
        gate(z[0]==(0,0) and z[5]==(1,1),'LOWER_NORMALIZATION:'+arm)
        gate(L2==iv(vals['lower_log_lapse2']),'RECOMPUTED_LOG_LAPSE:'+arm)
        d1,d2,d3,r=[iv(vals[k]) for k in ('d1','d2','d3','rate')]
        gate(d1==iv(rec['d1']) and d2==iv(rec['d2']),'QUADRATIC_COEFFICIENTS:'+arm)
        gate(-54<d1[0]<=d1[1]<-50 and -1600<d2[0]<=d2[1]<-1400 and -70000<d3[0]<=d3[1]<0 and -2<L2[0]<=L2[1]<2 and Q(1,64)<r[0]<=r[1]<Q(1,32),'BROAD_COEFFICIENT_GATES:'+arm)
        F2=mul(r,add(d2,neg(d1)))
        F3=mul(r,add(add(scale(d3,2),scale(d2,-2)),mul(add((Q(1,2),Q(1,2)),neg(L2)),d1)))
        gate(-50<F2[0]<=F2[1]<-21,'QUADRATIC_MARGIN:'+arm)
        gate(-10000<F3[0]<=F3[1]<10000,'CUBIC_ABSOLUTE_BOUND:'+arm)
        coeff[arm]=dict(log_lapse2=pack(L2),F2=pack(F2),F3=pack(F3))
    old=read(PARENT/'RESULT.json');c={k:Q(v) for k,v in old['constants_exact'].items()}
    rho=c['eta_physical_radius'];MD=c['observable_sup'];MF=c['clock_MF'];R=c['R'];selected=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=rho*q/2;tail=MF*q**4/(1-q);cubic=10000*eta**3
        qd=q/2;dtail=MD*qd**2/(1-qd);stail=R*qd**2/(1-qd);setail=R*qd**2*(2-qd)/(1-qd)**2
        if cubic+tail<=10*eta**2 and dtail<=25*eta and stail<=eta/40000 and setail<=eta/40000:
            selected=(j,q,eta,tail,cubic,dtail,stail,setail);break
    gate(selected is not None,'DYADIC_SELECTION');j,q,eta,tail,cubic,dtail,stail,setail=selected
    gate(eta>c['clock_eta'],'STRICT_INTERVAL_IMPROVEMENT')
    gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_STILL_POSITIVE')
    exact=dict(rho_D=rho,rho_F=rho/2,MD=MD,MF=MF,q=q,eta=eta,known_cubic_bound=cubic,F_tail_after_cubic=tail,total_after_quadratic=cubic+tail,distance_tail_after_linear=dtail,scalar_tail=stail,scalar_euler_tail=setail,scalar_departure_threshold=eta/40000,clock_interval_gain=eta/c['clock_eta'])
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='KNOWN_CUBIC_IMPROVES_FULL_PROPER_CLOCK_REMAINDER',constants_exact={k:str(v) for k,v in exact.items()},coefficient_intervals=coeff,gates=gates,selected_dyadic_halvings=j,display={k:decade(exact[k]) for k in ('eta','F_tail_after_cubic','scalar_departure_threshold','clock_interval_gain')},seconds=time.monotonic()-started,new_ode_solves=0,scope='Same local analytic neutral family, both signs and physical scalar departure. No endpoint, generic-flow theorem or resolution of the proper-clock separation-normal-form cubic sign.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','display','selected_dyadic_halvings','seconds')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('known_cubic_clock_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CLOCK_TAIL_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
