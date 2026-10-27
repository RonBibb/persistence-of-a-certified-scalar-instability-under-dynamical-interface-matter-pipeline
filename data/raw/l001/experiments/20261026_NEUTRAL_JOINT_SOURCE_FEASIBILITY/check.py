"""Predeclared joint trace/background-jet proof-conditioning ladder."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_NEUTRAL_CUBIC_CLOCK_TAIL';WEIGHT=BASE/'20261026_NEUTRAL_WEIGHTED_SOURCE_MAJORANT'
MAJOR=BASE/'20261026_NEUTRAL_SOURCE_MAJORANT';GOAL=BASE/'20261026T183955Z_CONVERGENCE_TWO_HOUR_GOAL'
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
def ceil(q):return -((-q.numerator)//q.denominator)
def decade(q):
    need(q>0,'POSITIVE_DISPLAY');j=0
    while q<1:q*=10;j-=1
    while q>=10:q/=10;j+=1
    z=q*10**6;return dict(floor_log10=j,mantissa_floor_millionths=z.numerator//z.denominator)
def envelopes(x,gap):
    G=1/(1-2*x);Z=64+1320*x+37600*x*x+64*(4*x/gap)**3/(1-4*x/gap);E1=1/(1-x);E2=G
    w=4*x*G;wu=2*x*G;wt=4*x*G+8*x*x*G*G
    d=x*(1+w);dd=x*(1+2*w+w*wu+wt+w*w);l=G*x;ll=G*G*x
    out={}
    out['BM']=G*x*(1+wu+w)+Q(4,3)*d*(Z+l)
    out['BK']=Z*Z*E2*(dd+(3+3*d)*d)+E2*(Z+ll+(4*Z+5*l)*(Z+l))+Z+x
    out['BR']=Q(13,2)*E2*(Z+l)**2+6+(Z+x)**2/2+Z*Z*E2*(6+3*(dd+3*d)+Q(7,2)*d*d)
    Ni=Z*E1;v=4*x*Z*E1*E1;vt=Z*E1*E1*(4*x+(2*x+4*Z*x)*4*x);B=1/(1-v*v)
    out['BI']=Ni*B*(vt*B+v*(2*d+1))+Ni*Ni*B*x*x/2
    out['BJ']=B*(E1*(Z+l)+v*Ni*d)+(2+21*(Z+1+x)+x)/2
    out['BO']=Ni*Ni*B*(x+(3+8*Z*x+2*x+v*vt*B)*x)+2*x+Z+1+x
    return out
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    bind(PARENT/'TERMINAL.json','97e01b5fd9e6513db28be3da9840e69932c284938bc5a3670aceb1145bba3ed9');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
    for n,k in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')):bind(PARENT/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():bind(p,h)
    ar=PARENT/'audit';bind(ar/'AUDIT_TERMINAL.json','82036edea79c9c85942594a2c00ae73ed558ba65e55da78c6ee13a50e1eff37d');at=read(ar/'AUDIT_TERMINAL.json');need(at['pass_status'],'AUDIT_PASS')
    for n,k in (('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')):bind(ar/n,at[k])
    if 'derivation_sha256' in at:bind(ar/'DERIVATION.txt',at['derivation_sha256'])
    tracepath=GOAL/'TRACE_ROUTE_SCOPING.md';bind(tracepath,sha(tracepath))
    utilpath=WEIGHT/'check.py';need(inputs.get(str(utilpath))==sha(utilpath),'DUAL_AUTHORITY');Dual=load('joint_bound_dual',utilpath).Dual
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE))
    prior=read(PARENT/'RESULT.json');weighted=read(WEIGHT/'RESULT.json');old=read(MAJOR/'RESULT.json')
    c={k:Q(v) for k,v in old['constants_exact'].items()};rho=c['rho'];gap=c['gap'];s=c['seed']
    alpha={k:Q(v) for k,v in weighted['source_weights'].items()};ac=alpha['BT']/c['Cc']
    gate(rho<=1 and ac>0,'TRACE_WEIGHT_DOMAIN')
    jetbounds=dict(H2=Q(104,3)+Q(1734,1024),T2=Q(330),E2=Q(187),T3=Q(26+4*37*2+8*2*26+4*3*330))
    gate(jetbounds['H2']<37 and jetbounds['T2']<=330 and jetbounds['E2']<=4700 and jetbounds['T3']<4700,'BACKGROUND_LOW_JETS')
    zp=Q(1320);jet=envelopes(Dual(0,1),gap)
    table={'BM':(0,Q(259,3)),'BK':(16512,49858+514*zp),'BR':(53254,152448+1664*zp),'BI':(0,32768),'BJ':(Q(1495,2),76+Q(23,2)*zp),'BO':(65,16387+zp)}
    for name in table:gate((jet[name].a,jet[name].b)==tuple(map(Q,table[name])),'SOURCE_FIRST_JET:'+name)
    rows=[]
    for k in (64,72,80,88,96,104,112,120):
        a=Q(1,2**k);gate(4*a<gap and 2*a<1,'COMPOSITION_DOMAIN:'+str(k))
        ws=4*a*(1+2*a)/(1-2*a)**3;V=3*a+22*ws*a/rho;den=1-160*ws/rho-840*ws*ws/rho**2
        gate(den>0,'TRACE_DENOMINATOR:'+str(k));ct=138*V*V/den
        Z=64+1320*a+37600*a*a+64*(4*a/gap)**3/(1-4*a/gap)
        gate(4*a*Z/(1-a)**2<Q(1,2),'WALL_DOMAIN:'+str(k))
        vals=envelopes(a,gap);budget={'TRACE_RESPONSE':ac*ct}
        for name in table:
            mass=vals[name]-jet[name].a-a*jet[name].b;gate(mass>=0,'POSITIVE_SOURCE:'+str(k)+':'+name);budget[name]=alpha[name]*mass
        mass=sum(budget.values());K=Q(ceil(max(Q(1),1/a,2*mass/a**2)))
        gate(K*a>=1 and K>=2*mass/a**2,'MAJORANT_DOMINANCE:'+str(k))
        rows.append(dict(k=k,a=str(a),trace_denominator=str(den),trace_response=str(ct),weighted_mass=str(mass),K=str(K),budget={n:str(v) for n,v in budget.items()}))
    best=min(rows,key=lambda v:Q(v['K']));K=Q(best['K']);R=1/(96*K);radius=R/(8*s);MD=9*R/(1-R);kr=K*R
    gate(Q(1,2)+kr/(1-kr)**2<1 and 2*kr/(1-kr)**2+2*kr**2/(1-kr)**3<Q(1,2),'CONTRACTION')
    gate(4*R<gap and 2*R<1,'CHART_DOMAIN');Z=64/(1-4*R/gap);v=4*R*Z/(1-R)**2
    gate(v<Q(1,2),'TIMELIKE_WALL');lapseinv=Z/(1-R)/(1-v*v);gate(lapseinv<=128,'INVERSE_LAPSE')
    for name,rec in prior['coefficient_intervals'].items():
        f2=tuple(map(Q,rec['F2']));f3=tuple(map(Q,rec['F3']))
        gate(-50<f2[0]<=f2[1]<-21 and -10000<f3[0]<=f3[1]<10000,'INHERITED_CLOCK_COEFFICIENT:'+name)
    gate(set(prior['coefficient_intervals'])=={'primary','independent'},'COEFFICIENT_INVENTORY')
    MF=Q(129,32)*MD;chosen=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q/2;tail=MF*q**4/(1-q);cubic=10000*eta**3;qd=q/2
        dt=MD*qd**2/(1-qd);st=R*qd**2/(1-qd);se=R*qd**2*(2-qd)/(1-qd)**2
        if cubic+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:chosen=(j,q,eta,tail,cubic,dt,st,se);break
    gate(chosen is not None,'CLOCK_AND_SCALAR_TAILS');j,q,eta,tail,cubic,dt,st,se=chosen
    gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_REMAINS_POSITIVE')
    gate(radius>Q(weighted['constants_exact']['eta_physical_radius']) and eta>Q(prior['constants_exact']['eta']),'BOTH_BOUNDS_IMPROVE')
    exact=dict(K=K,R=R,eta_physical_radius=radius,observable_sup=MD,clock_MF=MF,clock_q=q,clock_eta=eta,clock_tail_after_cubic=tail,known_cubic_bound=cubic,distance_tail_after_linear=dt,scalar_tail=st,scalar_euler_tail=se,scalar_departure_threshold=eta/40000,radius_gain=radius/Q(weighted['constants_exact']['eta_physical_radius']),clock_gain=eta/Q(prior['constants_exact']['eta']),trace_response_weight=ac,inverse_lapse_bound=lapseinv)
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='JOINT_TRACE_BACKGROUND_JET_LOCAL_CERTIFICATE',constants_exact={k:str(v) for k,v in exact.items()},background_derivative_bounds={k:str(v) for k,v in jetbounds.items()},candidates=rows,selected_k=best['k'],clock_dyadic_halvings=j,gates=gates,display={k:decade(exact[k]) for k in ('eta_physical_radius','clock_eta','scalar_departure_threshold','radius_gain','clock_gain')},new_ode_solves=0,seconds=time.monotonic()-started,scope='Same local neutral analytic family and protected signed departure; improved sufficient estimates only. No practical-amplitude or endpoint claim.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','selected_k','display','seconds')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('joint_source_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('JOINT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
