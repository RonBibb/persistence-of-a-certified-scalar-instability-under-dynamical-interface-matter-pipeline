"""Independent vector-response and positive-envelope rational audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
PIN='a514a572c03946c707cc6cff14624db74168f6803b818d6c8a849cda412176be'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';DEADLINE=1793047195
NAMES=('BT','BM','BK','BR','BI','BJ','BO')
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
def add(*vs):return tuple(sum(v[i] for v in vs) for i in range(7))
def scale(a,v):return tuple(a*x for x in v)
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
    def bound(name):
        p=BASE/name/'RESULT.json';gate(inputs.get(str(p))==sha(p),'AUTHORITY:'+name);return read(p)
    old=bound('20261026_NEUTRAL_SOURCE_MAJORANT');c={k:Q(v) for k,v in old['constants_exact'].items()}
    prior={k:Q(v) for k,v in bound('20261026_NEUTRAL_RESPONSE_CONDITIONING')['constants_exact'].items()}
    iv={k:Q(v) for k,v in bound('20261026_NEUTRAL_ANALYTIC_INVERSE')['constants_exact'].items()}
    dep=bound('20261026_NEUTRAL_TWO_SIDED_DEPARTURE');out=read(PACKET/'RESULT.json')
    rho=c['rho'];gap=c['gap'];x=c['a'];d0=iv['real_D_normalized_lower'];dc=iv['complex_D_normalized_lower'];anchor=Q(11,4)/d0
    basis=[tuple(Q(int(i==j)) for i in range(7)) for j in range(7)]
    trace=scale(c['Cc'],basis[0]);graph=scale(32768,basis[4])
    momentum=add(scale(Q(3,2),trace),scale(64,basis[1]))
    constraint=add(scale(18,momentum),scale(28,trace),basis[3]);kg=add(scale(2,trace),scale(6,momentum),basis[2])
    force=add(kg,scale(20/dc,constraint))
    wall=add(trace,scale(Q(39,4),graph),scale(2,basis[5]),scale(Q(1,2),basis[6]))
    robin=add(scale(Q(1,2)+1/(4*d0),wall),scale(1/d0,constraint))
    uf=scale(c['Cscalar'],add(force,robin))
    xp=scale(1/(1-3*rho/2),add(scale(anchor,add(constraint,uf,momentum)),scale(rho/6,uf),scale(rho/2,momentum)))
    yp=add(scale(3,xp),scale(Q(1,3),uf),momentum)
    up=add(scale(2,xp),scale(4,yp),scale(Q(5,2),uf),scale(9/rho,momentum))
    oscillator=scale(16384,add(scale(Q(1,2),uf),scale(Q(1,4),graph),basis[6]))
    weights=add(scale(3,up),trace,uf,scale(2,graph),scale(2,oscillator))
    gate(sum(weights)==prior['C'],'PARENT_UNIFORM_RESPONSE')
    gate(set(out['source_weights'])==set(NAMES),'WEIGHT_INVENTORY')
    for i,n in enumerate(NAMES):gate(weights[i]>0 and weights[i]==Q(out['source_weights'][n]),'WEIGHT:'+n)
    # Independently arranged rational source expressions, no producer import.
    reciprocal=1/(1-2*x);background=64*gap/(gap-4*x);exp1=1/(1-x)
    shift=4*x*reciprocal;shift_s=2*x*reciprocal;shift_t=shift+8*(x*reciprocal)**2
    first=x+shift*x;second=x+2*shift*x+shift*shift_s*x+shift_t*x+shift**2*x
    radial=x*reciprocal;radial2=x*reciprocal**2
    env={}
    env['BT']=3*(second+first)+6*first**2
    env['BM']=reciprocal*(x+shift_s*x+shift*x)+Q(4,3)*first*(background+radial)
    env['BK']=background**2*reciprocal*(second+3*first+3*first**2)+reciprocal*(background+radial2+(4*background+5*radial)*(background+radial))+background+x
    env['BR']=reciprocal*Q(13,2)*(background+radial)**2+6+(background+x)**2/2+background**2*reciprocal*(6+3*second+9*first+Q(7,2)*first**2)
    lapse0=background*exp1;v0=4*x*background*exp1**2;vt0=background*exp1**2*(4*x+8*x*x+16*background*x*x)
    gate(0<=v0<Q(1,2),'ENVELOPE_DOMAIN');boost=1/(1-v0*v0)
    env['BI']=lapse0*boost**2*vt0+lapse0*boost*v0*(2*first+1)+lapse0**2*boost*x*x/2
    env['BJ']=boost*exp1*(background+radial)+boost*v0*lapse0*first+1+Q(21,2)*(background+1+x)+x/2
    env['BO']=lapse0**2*boost*(4*x+8*background*x*x+2*x*x+v0*vt0*boost*x)+3*x+background+1
    zprime=256/gap
    # Hand differentiated as independent component sums, rather than Dual.
    table={'BT':(0,3+3),'BM':(0,1+Q(4,3)*64),'BK':(64+4*64**2+64,16384+32896+577+513*zprime+zprime+1),'BR':(Q(13,2)*64**2+6+Q(64**2,2)+6*64**2,54080+832*zprime+64+64*zprime+98304+768*zprime),'BI':(0,2*64*256),'BJ':(64+1+Q(21,2)*65,65+zprime+11+Q(21,2)*zprime),'BO':(65,4*64**2+3+zprime)}
    masses={};budget={}
    for i,n in enumerate(NAMES):
        zero,linear=map(Q,table[n]);gate(env[n]==Q(old['envelopes_exact'][n]),'UNCHANGED_ENVELOPE:'+n)
        gate([str(zero),str(linear)]==out['source_zero_linear'][n],'ZERO_LINEAR:'+n)
        mass=env[n]-zero-x*linear;gate(mass>=0 and mass==Q(out['source_masses'][n]),'POSITIVE_REMAINDER:'+n)
        masses[n]=mass;budget[n]=weights[i]*mass
    mass=sum(budget.values());gate(mass>0,'POSITIVE_TOTAL')
    for n in NAMES:gate(budget[n]/mass==Q(out['source_budget_shares'][n]),'BUDGET_SHARE:'+n)
    raw=max(Q(1),1/x,2*mass/x**2);K=Q((raw.numerator+raw.denominator-1)//raw.denominator)
    gate(K>=raw and K-1<raw and K<prior['K'],'OUTWARD_IMPROVEMENT')
    R=1/(96*K);rad=R/(8*c['seed']);MD=9*R/(1-R);z=K*R
    gate(Q(1,2)+z/(1-z)**2<1 and 2*z/(1-z)**2+2*z*z/(1-z)**3<Q(1,2),'CONTRACTION')
    gate(4*R<gap and 2*R<1,'CHART')
    bg=64*gap/(gap-4*R);vel=4*R*bg/(1-R)**2;lapse=bg/((1-R)*(1-vel**2));gate(vel<Q(1,2) and lapse<=128,'TIMELIKE_LAPSE')
    js=out['cubic_dyadic_halvings'];jc=out['clock_dyadic_halvings'];gate(isinstance(js,int) and isinstance(jc,int) and 1<=js<=8192 and 1<=jc<=8192,'DYADIC_DOMAIN')
    qs=Q(1,2**js);es=rad*qs;ts=MD*qs**4/(1-qs)
    qc=Q(1,2**jc);ec=rad*qc/2;MF=129*MD/32;tc=MF*qc**3/(1-qc);dt=MD*(qc/2)**2/(1-qc/2)
    gate(ts<=700*es**2 and ts<=20000*es**3 and tc<=10*ec**2 and dt<=25*ec,'REMAINDERS')
    if js>1:
        q=2*qs;e=rad*q;err=MD*q**4/(1-q);gate(err>700*e**2 or err>20000*e**3,'FIRST_CUBIC')
    if jc>1:
        q=2*qc;e=rad*q/2;err=MF*q**3/(1-q);derr=MD*(q/2)**2/(1-q/2);gate(err>10*e**2 or derr>25*e,'FIRST_CLOCK')
    qd=ec/rad;ct=R*qd**2/(1-qd);cet=R*(2*qd**2-qd**3)/(1-qd)**2
    gate(ct<=ec/40000 and cet<=ec/40000 and ec<Q(1,512) and 25*ec/64-60*ec**2>0,'TWO_SIDED_SCALAR_DEPARTURE')
    gate(set(dep['first_scalar_coefficient_enclosures'])=={'primary','independent'},'SCALAR_INVENTORY')
    for pair in dep['first_scalar_coefficient_enclosures'].values():
        lo,hi=map(Q,pair);gate(Q(1,20000)<lo<=hi<Q(1,10000),'SCALAR_SEED')
    expected=dict(a=x,weighted_source_mass=mass,K=K,R=R,eta_physical_radius=rad,observable_sup=MD,inverse_lapse_bound=lapse,cubic_q=qs,cubic_eta=es,cubic_tail=ts,clock_MF=MF,clock_q=qc,clock_eta=ec,clock_tail=tc,distance_tail_after_linear=dt,scalar_tail=ct,scalar_euler_tail=cet,scalar_departure_threshold=ec/40000,radius_gain=rad/prior['eta_physical_radius'])
    gate(set(expected)==set(out['constants_exact']),'CONSTANT_INVENTORY')
    for n,v in expected.items():gate(v==Q(out['constants_exact'][n]),'EXACT:'+n)
    gate(rad>prior['eta_physical_radius'] and ec>prior['clock_eta'],'RADII_IMPROVE')
    for n,d in out['display'].items():
        v=expected[n];ten=Q(10)**d['floor_log10'];gate(ten<=v<10*ten,'DECADE');z=v*10**6/ten;gate(z.numerator//z.denominator==d['mantissa_floor_millionths'],'DISPLAY')
    gate(out['pass_status'] and all(out['gates'].values()) and out['new_ode_solves']==0,'STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED')
    result=dict(pass_status=True,classification='INDEPENDENT_WEIGHTED_SOURCE_MAJORANT_AUDIT_PASS',checks=count,production_terminal_sha256=PIN,display=out['display'],seconds=time.monotonic()-start,scope='Independent vector response weights, hand-derived degree0/1 coefficients, rational envelopes, positive higher-source masses, majorant, remainder and scalar-departure replay. Analytic source bookkeeping reviewed separately; no new ODE or generic-data endpoint claim.')
    put('AUDIT_RESULT.json',result);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('weighted_majorant_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
