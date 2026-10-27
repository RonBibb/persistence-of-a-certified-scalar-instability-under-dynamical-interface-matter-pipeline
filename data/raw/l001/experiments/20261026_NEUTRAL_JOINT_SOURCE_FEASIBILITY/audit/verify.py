"""Independent eight-arm trace/background-jet certificate audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
PIN='f164d8db500b34978362137d2d6b68e18ab3ec6780e69a8652fc73a19b873a70'
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
    def bound(folder):
        p=BASE/folder/'RESULT.json';gate(inputs.get(str(p))==sha(p),'AUTHORITY:'+folder);return read(p)
    old=bound('20261026_NEUTRAL_SOURCE_MAJORANT');c={k:Q(v) for k,v in old['constants_exact'].items()}
    weighted=bound('20261026_NEUTRAL_WEIGHTED_SOURCE_MAJORANT');alpha={k:Q(v) for k,v in weighted['source_weights'].items()}
    prior=bound('20261026_NEUTRAL_CUBIC_CLOCK_TAIL');iv={k:Q(v) for k,v in bound('20261026_NEUTRAL_ANALYTIC_INVERSE')['constants_exact'].items()}
    out=read(PACKET/'RESULT.json');rho=c['rho'];gap=c['gap'];d0=iv['real_D_normalized_lower'];dc=iv['complex_D_normalized_lower']
    # Reconstruct response to one unit of trace norm, rather than assuming
    # division by the old trace-source constant has the intended meaning.
    sp=Q(3,2);sc=55;sg=11
    uf=c['Cscalar']*(sg+20*sc/dc+Q(1,2)+1/(4*d0)+sc/d0)
    xp=((Q(11,4)/d0)*(sc+uf+sp)+rho*(uf/6+sp/2))/(1-3*rho/2)
    yp=3*xp+uf/3+sp;up=2*xp+4*yp+Q(5,2)*uf+9*sp/rho
    ac=3*up+1+16385*uf
    gate(ac==alpha['BT']/c['Cc'],'TRACE_WEIGHT_REMOVAL')
    jets=dict(H2=Q(2,3)*2*26+Q(2*17*51,1024),T2=Q(2+4*2*2+4*3*26),E2=Q(2*17+3*51),T3=Q(26+4*37*2+8*2*26+4*3*330))
    gate(jets['H2']<37 and jets['T2']<=330 and jets['E2']<=330 and jets['T3']<4700,'DERIVATIVE_BOUNDS')
    gate({k:str(v) for k,v in jets.items()}==out['background_derivative_bounds'],'DERIVATIVE_RECORDS')
    gate(330*4==1320 and Q(4700,2)*16==37600 and rho<=1,'LOW_JET_COMPOSITION')
    zprime=Q(1320)
    first={'BM':(0,Q(259,3)),'BK':(16512,16384+32896+577+513*zprime+zprime+1),'BR':(53254,54080+832*zprime+64+64*zprime+98304+768*zprime),'BI':(0,32768),'BJ':(Q(1495,2),65+zprime+11+Q(21,2)*zprime),'BO':(65,16384+3+zprime)}
    ks=(64,72,80,88,96,104,112,120);gate([v['k'] for v in out['candidates']]==list(ks),'ALL_DECLARED_CANDIDATES')
    rows=[]
    for k,record in zip(ks,out['candidates']):
        x=Q(1,2**k);gate(4*x<gap and 2*x<1,'COMPOSITION_DOMAIN')
        inv=1/(1-2*x);ws=4*x*(1+2*x)*inv**3
        temporal=3*x+22*ws*x/rho;den=1-160*ws/rho-840*(ws/rho)**2
        gate(den>0,'TRACE_CLOSURE');trace=138*temporal**2/den
        # Bounds on transported response terms, with slack preserved.
        gate(40+120/rho<=160/rho and 20+180/rho+600/rho**2<=840/rho**2,'TRANSPORT_CONSTANTS')
        bg=64+330*(4*x)+Q(4700,2)*(4*x)**2+64*(4*x/gap)**3/(1-4*x/gap)
        ex=1/(1-x);shift=4*x*inv;shift_s=2*x*inv;shift_t=shift+8*(x*inv)**2
        f=x+shift*x;f2=x+2*shift*x+shift*shift_s*x+shift_t*x+shift**2*x
        radial=x*inv;radial2=x*inv**2
        env={}
        env['BM']=inv*(x+shift_s*x+shift*x)+Q(4,3)*f*(bg+radial)
        env['BK']=bg**2*inv*(f2+3*f+3*f*f)+inv*(bg+radial2+(4*bg+5*radial)*(bg+radial))+bg+x
        env['BR']=Q(13,2)*inv*(bg+radial)**2+6+(bg+x)**2/2+bg**2*inv*(6+3*f2+9*f+Q(7,2)*f*f)
        ni=bg*ex;v=4*x*bg*ex**2;vt=bg*ex**2*(4*x+8*x*x+16*bg*x*x)
        gate(0<=v<Q(1,2),'BOOST_DOMAIN');boost=1/(1-v*v)
        env['BI']=ni*boost**2*vt+ni*boost*v*(2*f+1)+ni**2*boost*x*x/2
        env['BJ']=boost*ex*(bg+radial)+boost*v*ni*f+1+Q(21,2)*(bg+1+x)+x/2
        env['BO']=ni**2*boost*(4*x+8*bg*x*x+2*x*x+v*vt*boost*x)+3*x+bg+1
        budget={'TRACE_RESPONSE':ac*trace}
        for name,(zero,linear) in first.items():
            mass=env[name]-zero-x*linear;gate(mass>=0,'POSITIVE_HIGHER_SOURCE');budget[name]=alpha[name]*mass
        mass=sum(budget.values());raw=max(Q(1),1/x,2*mass/x**2);K=Q((raw.numerator+raw.denominator-1)//raw.denominator)
        gate(K>=raw and K-1<raw,'OUTWARD_MAJORANT')
        row=dict(k=k,a=str(x),trace_denominator=str(den),trace_response=str(trace),weighted_mass=str(mass),K=str(K),budget={n:str(v) for n,v in budget.items()})
        gate(row==record,'EXACT_CANDIDATE:'+str(k));rows.append(row)
    best=min(rows,key=lambda v:Q(v['K']));gate(best['k']==out['selected_k'],'DECLARED_OPTIMALITY')
    K=Q(best['K']);R=1/(96*K);rad=R/(8*c['seed']);MD=9*R/(1-R);z=K*R
    gate(Q(1,2)+z/(1-z)**2<1 and 2*z/(1-z)**2+2*z*z/(1-z)**3<Q(1,2),'CONTRACTION')
    gate(4*R<gap and 2*R<1,'CHART')
    bg=64*gap/(gap-4*R);v=4*R*bg/(1-R)**2;linv=bg/((1-R)*(1-v*v))
    gate(v<Q(1,2) and linv<=128,'TIMELIKE_AND_LAPSE')
    gate(set(prior['coefficient_intervals'])=={'primary','independent'},'COEFFICIENT_INVENTORY')
    for row in prior['coefficient_intervals'].values():
        f2=list(map(Q,row['F2']));f3=list(map(Q,row['F3']));gate(-50<f2[0]<=f2[1]<-21 and -10000<f3[0]<=f3[1]<10000,'CLOCK_JETS')
    MF=129*MD/32;j=out['clock_dyadic_halvings'];gate(isinstance(j,int) and 1<=j<=8192,'DYADIC_INDEX')
    q=Q(1,2**j);eta=rad*q/2;tail=MF*q**4/(1-q);cubic=10000*eta**3;u=q/2
    dt=MD*u*u/(1-u);st=R*u*u/(1-u);se=R*(2*u*u-u**3)/(1-u)**2
    def passes(v):
        e=rad*v/2;w=v/2
        return 10000*e**3+MF*v**4/(1-v)<=10*e*e and MD*w*w/(1-w)<=25*e and R*w*w/(1-w)<=e/40000 and R*(2*w*w-w**3)/(1-w)**2<=e/40000
    gate(passes(q) and (j==1 or not passes(2*q)),'FIRST_ADMISSIBLE_ALL_TAILS')
    gate(eta<Q(1,512) and 25*eta/64-60*eta*eta>0,'OPENING_SIGN')
    oldrad=Q(weighted['constants_exact']['eta_physical_radius']);olde=Q(prior['constants_exact']['eta'])
    gate(rad>oldrad and eta>olde,'BOTH_IMPROVE')
    expected=dict(K=K,R=R,eta_physical_radius=rad,observable_sup=MD,clock_MF=MF,clock_q=q,clock_eta=eta,clock_tail_after_cubic=tail,known_cubic_bound=cubic,distance_tail_after_linear=dt,scalar_tail=st,scalar_euler_tail=se,scalar_departure_threshold=eta/40000,radius_gain=rad/oldrad,clock_gain=eta/olde,trace_response_weight=ac,inverse_lapse_bound=linv)
    gate(set(expected)==set(out['constants_exact']),'CONSTANT_INVENTORY')
    for n,v in expected.items():gate(v==Q(out['constants_exact'][n]),'EXACT:'+n)
    for n,d in out['display'].items():
        v=expected[n];ten=Q(10)**d['floor_log10'];gate(ten<=v<10*ten,'DECADE');z=v*10**6/ten;gate(z.numerator//z.denominator==d['mantissa_floor_millionths'],'DISPLAY')
    gate(out['pass_status'] and all(out['gates'].values()) and out['new_ode_solves']==0,'STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED')
    result=dict(pass_status=True,classification='INDEPENDENT_JOINT_TRACE_BACKGROUND_JET_AUDIT_PASS',checks=count,production_terminal_sha256=PIN,selected_k=best['k'],display=out['display'],seconds=time.monotonic()-start,scope='Independent trace-response weight, background derivative bounds, six positive source envelopes, all eight exact candidate budgets and declared optimality, full remainder and departure gates. Retained-transport analytical proof reviewed separately; same equations and local family, no new ODE or practical-amplitude/endpoint claim.')
    put('AUDIT_RESULT.json',result);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('joint_source_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
