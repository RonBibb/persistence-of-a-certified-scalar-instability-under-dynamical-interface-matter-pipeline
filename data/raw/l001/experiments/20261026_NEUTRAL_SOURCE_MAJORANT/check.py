"""Exact rational nonlinear majorant and observable tail; Linux-only certificate."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
INV=BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE';SEED=BASE/'20261026_NEUTRAL_ANALYTIC_SEED'
FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1';CUBIC=BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'
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
    return dict(floor_log10=j,mantissa_floor_millionths=(q*10**6).numerator//(q*10**6).denominator)
def main(lease,auditpin):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    for root,pin in [(INV,'7ec861cf5d45f7799f5f88d2d776445acf4c4f4ad7d6626c4ab5e06b3c640d99'),(SEED,'e89622e7c04b37bc68f529f684c823af464c8ceb6e86c5629b350d49a8f0df52'),(BASE/'20261026_GROWING_NEUTRAL_COMPONENT_MAP','a189065e25d7f9eb386ca71ee4baf8d99c5a99a78cd60884e37afe7c40d48753'),(BASE/'20261026_GROWING_NEUTRAL_COMPATIBILITY','46a3b24af5e15aa9f08894fe5612b18efeb1fc2b33901b0894523e59eb841f6f')]:
        bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');need(t.get('pass_status',t.get('pass')),'PARENT_PASS')
        for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:bind(root/n,t[k])
        for group in ('inputs','sources','runtime'):
            for p,h in read(root/'BINDING.json').get(group,{}).items():bind(p,h)
    for root,pin in [(INV/'audit','d6dea65549d221cc69649b437b2f1b90cca5d3390f4696ee9e3bad37808d29ee'),(SEED/'audit',auditpin),(QUAD/'audit','61cfa897dec29277df1dc4783529a09cb4134eb5be13c8dc628945099c761282'),(CUBIC/'audit','4544f23bd218de5c9ae2d0cb7bd23b248f92669275023f65673f45449bc0dd6a')]:
        bind(root/'AUDIT_TERMINAL.json',pin);t=read(root/'AUDIT_TERMINAL.json');need(t.get('pass_status',t.get('pass')),'AUDIT_PASS')
        for n,k in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:bind(root/n,t[k])
    coeff={}
    for root,pin,orders in [(QUAD,'ffd7264e8bc8babbf511673c7a313e500f54746f67f1b0668069d3ad3cb727ec',(1,2)),(CUBIC,'4f59104039d4eff1c3d4ad976ff7987d1830ab1416b43911fb68a1f32b37bd57',(1,3))]:
        bind(root/'production_TERMINAL.json',pin);t=read(root/'production_TERMINAL.json');need(t['pass'],'COEFFICIENT_PASS')
        for n,h in t['artifacts'].items():bind(root/n,h)
        for arm in ('primary','independent'):
            r=read(root/('PRODUCTION_'+arm+'.json'))
            for order in orders:
                lo,hi=map(Q,r['d'+str(order)]['exact_bounds']);floor={1:50,2:1400,3:40000}[order]
                gate(lo<=hi<-floor,root.name+':'+arm+':D'+str(order)+'_NEGATIVE')
                coeff[root.name+':'+arm+':d'+str(order)]=[str(lo),str(hi)]
    sr=read(SEED/'RESULT.json')
    for arm,data in sr['arms'].items():
        bind(SEED/('ARM_'+arm+'.json'),sha(SEED/('ARM_'+arm+'.json')))
        need(read(SEED/('ARM_'+arm+'.json'))==data,'SEED_ARM_MATCH')
        for item in data['chunks']:
            bind(SEED/item['file'],item['sha256']);bind(SEED/item['checkpoint'],item['checkpoint_sha256'])
    for arm in ('primary','independent'):
        initial=read(FRESH/('INITIAL_'+arm+'.json'));lo,hi=map(Q,initial['D']);gate(1<=lo<=hi<=3,arm+':LENGTH_GATE')
    manuscript=BASE.parents[4]/'papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md'
    # Derive path from the shared mount root rather than a Mac-only pathname.
    need(manuscript.is_file(),'MANUSCRIPT_PATH');bind(manuscript,sha(manuscript))
    lemma=BASE/'20261026T162520Z_UNSTABLE_MODE_TWO_HOUR_GOAL/CONDITIONAL_MAJORANT.md';bind(lemma,sha(lemma))
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE,seed_audit_pin=auditpin,method='Exact rational envelope evaluation and reviewed analytic inequalities; no new ODE'))
    ir=read(INV/'RESULT.json');iv={k:Q(v) for k,v in ir['constants_exact'].items()}
    rho=iv['rho'];gap=iv['prior_radius']-rho;d0=iv['real_D_normalized_lower'];dc=iv['complex_D_normalized_lower']
    gate(0<rho<=Q(1,4) and gap>0,'COMMON_COLLAR')
    a=min(gap/16,Q(1,4096));x=a
    gate(1-2*x>0 and 1-4*x/gap>0 and 1-x>0,'RATIONAL_DENOMINATORS')
    G=1/(1-2*x);Z=64/(1-4*x/gap);E1=1/(1-x);E2=1/(1-2*x)
    w=4*x*G;wu=2*x*G;wt=4*x*G+8*x*x*G*G
    d=x*(1+w);dd=x*(1+2*w+w*wu+wt+w*w);l=G*x;ll=G*G*x
    BT=3*dd+3*d+6*d*d
    BM=G*x*(1+wu+w)+Q(4,3)*d*(Z+l)
    BK=Z*Z*E2*(dd+(3+3*d)*d)+E2*(Z+ll+(4*Z+5*l)*(Z+l))+Z+x
    BR=Q(13,2)*E2*(Z+l)**2+6+(Z+x)**2/2+Z*Z*E2*(6+3*(dd+3*d)+Q(7,2)*d*d)
    Ninv=Z*E1;v=4*x*Z*E1*E1;vt=Z*E1*E1*(4*x+(2*x+4*Z*x)*4*x)
    gate(0<=v<Q(1,2),'TIMELIKE_GRAPH_ENVELOPE');Bst=1/(1-v*v)
    BI=Ninv*Bst*(vt*Bst+v*(2*d+1))+Ninv*Ninv*Bst*x*x/2
    BJ=Bst*(E1*(Z+l)+v*Ninv*d)+(2+21*(Z+1+x)+x)/2
    BO=Ninv*Ninv*Bst*(x+(3+8*Z*x+2*x+v*vt*Bst)*x)+2*x+Z+1+x
    envelopes=dict(BT=BT,BM=BM,BK=BK,BR=BR,BI=BI,BJ=BJ,BO=BO)
    M=sum(envelopes.values());gate(all(v>=0 for v in envelopes.values()) and M>0,'POSITIVE_ENVELOPES')
    Cc=8192*(1+9/rho+81/rho**2);Cxi=Q(32768);Cchi=Q(16384)
    Csp=Q(3,2)*Cc+64;Csc=18*Csp+28*Cc+1;Csg=2*Cc+6*Csp+1
    CF=Csg+80*Csc/(4*dc);CR=Cc+Q(39,4)*Cxi+Q(5,2);CG=(Q(1,2)+1/(4*d0))*CR+Csc/d0
    Cf=Q(ceil(iv['scalar_C']));Cp=Q(ceil(iv['metric_C']));s=Q(ceil(Q(sr['seed_norm'])))
    Uf=Cf*(CF+CG);Up=Cp*(Csc+Uf+Csp);Uchi=Cchi*(Uf/2+Cxi/4+1)
    C=3*Up+Cc+Uf+2*Cxi+2*Uchi
    K=Q(ceil(max(Q(1),1/a,2*C*M/a**2)))
    gate(K>=1 and K*a>=1 and K>=2*C*M/a**2,'ALL_DEGREES_MAJORANT_DOMINANCE')
    R=1/(96*K);eta_radius=R/(2*s);rho_eta=eta_radius/4
    gate(s>0 and 0<R<1 and rho_eta>0,'POSITIVE_CONVERGENCE_RADIUS')
    kr=K*R;gate(Q(1,2)+kr/(1-kr)**2<1,'CONTRACTION_SELF_MAP')
    gate(2*kr/(1-kr)**2+2*kr*kr/(1-kr)**3<Q(1,2),'CONTRACTION_DERIVATIVE')
    MD=9*R/(1-R)
    # Predeclared dyadic subdisk selection; no production thresholds are changed.
    selected=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=rho_eta*q;tail=MD*q**4/(1-q)
        if tail<=Q(1400,2)*eta**2 and tail<=Q(40000,2)*eta**3:
            selected=(j,q,eta,tail);break
    gate(selected is not None,'REMAINDER_SMALLER_THAN_SIGNED_NONLINEAR_TERMS');j,q,eta,tail=selected
    constants=dict(rho=rho,gap=gap,a=a,M=M,Cc=Cc,Csp=Csp,Csc=Csc,Csg=Csg,CF=CF,CR=CR,CG=CG,Cscalar=Cf,Cmetric=Cp,seed=s,Uf=Uf,Up=Up,Uchi=Uchi,C=C,K=K,R=R,eta_majorant_radius=eta_radius,eta_physical_radius=rho_eta,observable_sup=MD,selected_q=q,selected_eta=eta,selected_tail=tail)
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='NEUTRAL_LOCAL_CONVERGENCE_AND_OBSERVABLE_REMAINDER_BOUND',constants_exact={k:str(v) for k,v in constants.items()},envelopes_exact={k:str(v) for k,v in envelopes.items()},display={k:decade(constants[k]) for k in ('K','eta_physical_radius','selected_eta','selected_tail')},selected_dyadic_halvings=j,gates=gates,coefficient_enclosures=coeff,seconds=time.monotonic()-started,new_ode_solves=0,scope='Local analytic pure-growing neutral family and proper-separation remainder, conditional on the separately recorded exact source identities and formal Codazzi/material-exchange induction premises. Positive eta has shortening beyond linear and quadratic truncations on the selected subdisk. No saturation, endpoint, horizon or global generic-data evolution claim.',remaining_premises=['Recorded all-order wall Codazzi/material-exchange identity premises must hold for the action and exact wall equations; numerical arithmetic does not independently prove them.'])
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','display','selected_dyadic_halvings','seconds','remaining_premises')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_PIN_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','TERMINAL.json','FAILURE.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_majorant_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('MAJORANT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
