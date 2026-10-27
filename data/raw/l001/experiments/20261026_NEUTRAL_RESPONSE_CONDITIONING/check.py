"""Source-preserving analytic response refinement; exact Linux arithmetic."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_NEUTRAL_PROPER_CLOCK_REMAINDER';MAJOR=BASE/'20261026_NEUTRAL_SOURCE_MAJORANT'
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
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    bind(PARENT/'TERMINAL.json','31438d2ae08e40ddb5c2b1788f36af57ddc9c4fc8a734dc3098e1e2e07ff7bcb');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(PARENT/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():bind(p,h)
    audit=PARENT/'audit';bind(audit/'AUDIT_TERMINAL.json','500f29806a2bb64734612ea303fb599be7b0d5503a03dda23c80b38206756d37');at=read(audit/'AUDIT_TERMINAL.json');need(at['pass_status'],'AUDIT_PASS')
    for n,k in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:bind(audit/n,at[k])
    if 'derivation_sha256' in at:bind(audit/'DERIVATION.txt',at['derivation_sha256'])
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE,method='Differentiate the mixed metric row once; retain Nagumo only on Sp'))
    old={k:Q(v) for k,v in read(MAJOR/'RESULT.json')['constants_exact'].items()}
    inv={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact'].items()}
    rho=old['rho'];Cm=Q(11,4)/inv['real_D_normalized_lower'];H=Q(3);T=Q(2)
    Uf=old['Uf'];Csc=old['Csc'];Csp=old['Csp']
    gate(Q(4,3)+Q(289,1024)<2 and 2+4*3*2==26,'BACKGROUND_DERIVATIVES')
    gate(rho*H/2<1,'PRIMITIVE_ABSORPTION')
    Xp=(Cm*(Csc+Uf+Csp)+rho*(T*Uf/12+Csp/2))/(1-rho*H/2)
    Yp=H*Xp+T*Uf/6+Csp
    Zp=Xp+3*Yp+Q(5,2)*Uf+9*Csp/rho
    Up=Xp+Yp+Zp
    gate(0<Up<old['Up'],'STRICTLY_SHARPER_METRIC_RESPONSE')
    C=3*Up+old['Cc']+Uf+2*32768+2*old['Uchi']
    a=old['a'];M=old['M'];s=old['seed'];K=Q(ceil(max(Q(1),1/a,2*C*M/a**2)))
    gate(K<old['K'] and K*a>=1 and K>=2*C*M/a**2,'MAJORANT_DOMINANCE_AND_IMPROVEMENT')
    R=1/(96*K);radius=R/(8*s);MD=9*R/(1-R);kr=K*R
    gate(Q(1,2)+kr/(1-kr)**2<1 and 2*kr/(1-kr)**2+2*kr**2/(1-kr)**3<Q(1,2),'CONTRACTION')
    gate(4*R<old['gap'] and 2*R<1,'CHART_DOMAIN')
    Z=64/(1-4*R/old['gap']);E1=1/(1-R);v=4*R*Z*E1**2
    gate(v<Q(1,2),'TIMELIKE_WALL');lapseinv=Z*E1/(1-v*v);gate(lapseinv<=128,'INVERSE_LAPSE')
    signed=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q;tail=MD*q**4/(1-q)
        if tail<=700*eta**2 and tail<=20000*eta**3:signed=(j,q,eta,tail);break
    gate(signed is not None,'SIGNED_CUBIC_REMAINDER');js,qs,etas,tails=signed
    MF=Q(129,32)*MD;clock=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q/2;tail=MF*q**3/(1-q);distance_tail=MD*(q/2)**2/(1-q/2)
        if tail<=10*eta**2 and distance_tail<=25*eta:clock=(j,q,eta,tail,distance_tail);break
    gate(clock is not None,'SIGNED_PROPER_CLOCK_REMAINDER');jc,qc,etac,tailc,dc=clock
    gate(radius>old['eta_physical_radius'] and etas>old['selected_eta'],'RADIUS_AND_CUBIC_SUBDISK_IMPROVE')
    oldclock=Q(read(PARENT/'RESULT.json')['constants_exact']['eta']);gate(etac>oldclock,'CLOCK_SUBDISK_IMPROVES')
    exact=dict(Cm=Cm,metric_X=Xp,metric_Y=Yp,metric_Z=Zp,Up=Up,C=C,K=K,R=R,eta_physical_radius=radius,observable_sup=MD,inverse_lapse_bound=lapseinv,cubic_q=qs,cubic_eta=etas,cubic_tail=tails,clock_MF=MF,clock_q=qc,clock_eta=etac,clock_tail=tailc,distance_tail_after_linear=dc,metric_bound_gain=old['Up']/Up,radius_gain=radius/old['eta_physical_radius'])
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='SHARPER_NEUTRAL_LOCAL_CONVERGENCE_AND_CLOCK_REMAINDER',constants_exact={k:str(v) for k,v in exact.items()},display={k:decade(exact[k]) for k in ('eta_physical_radius','cubic_eta','clock_eta','metric_bound_gain','radius_gain')},cubic_dyadic_halvings=js,clock_dyadic_halvings=jc,gates=gates,seconds=time.monotonic()-started,new_ode_solves=0,scope='Same local analytic neutral family and same source budget, with an improved sufficient metric response bound. Earlier certificates remain valid. This is not changed dynamics or a measured physical scale, and gives no nonlinear endpoint.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','display','cubic_dyadic_halvings','clock_dyadic_halvings','seconds')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_conditioning_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CONDITIONING_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
