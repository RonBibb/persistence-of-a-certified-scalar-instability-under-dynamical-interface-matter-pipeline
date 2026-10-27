"""Exact seven-load response weighting and local remainder certificates."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_NEUTRAL_TWO_SIDED_DEPARTURE';COND=BASE/'20261026_NEUTRAL_RESPONSE_CONDITIONING';MAJOR=BASE/'20261026_NEUTRAL_SOURCE_MAJORANT'
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
class Dual:
    def __init__(self,a,b=0):self.a=Q(a);self.b=Q(b)
    @staticmethod
    def cast(v):return v if isinstance(v,Dual) else Dual(v)
    def __add__(self,v):v=self.cast(v);return Dual(self.a+v.a,self.b+v.b)
    __radd__=__add__
    def __neg__(self):return Dual(-self.a,-self.b)
    def __sub__(self,v):return self+-self.cast(v)
    def __rsub__(self,v):return self.cast(v)+-self
    def __mul__(self,v):v=self.cast(v);return Dual(self.a*v.a,self.a*v.b+self.b*v.a)
    __rmul__=__mul__
    def __truediv__(self,v):
        v=self.cast(v);need(v.a!=0,'DUAL_DIVISOR');return Dual(self.a/v.a,(self.b*v.a-self.a*v.b)/v.a**2)
    def __rtruediv__(self,v):return self.cast(v)/self
    def __pow__(self,n):
        need(isinstance(n,int) and n>=0,'DUAL_POWER');out=Dual(1)
        for _ in range(n):out=out*self
        return out
def envelopes(x,gap):
    G=1/(1-2*x);Z=64/(1-4*x/gap);E1=1/(1-x);E2=G
    w=4*x*G;wu=2*x*G;wt=4*x*G+8*x*x*G*G
    d=x*(1+w);dd=x*(1+2*w+w*wu+wt+w*w);l=G*x;ll=G*G*x
    out={}
    out['BT']=3*dd+3*d+6*d*d
    out['BM']=G*x*(1+wu+w)+Q(4,3)*d*(Z+l)
    out['BK']=Z*Z*E2*(dd+(3+3*d)*d)+E2*(Z+ll+(4*Z+5*l)*(Z+l))+Z+x
    out['BR']=Q(13,2)*E2*(Z+l)**2+6+(Z+x)**2/2+Z*Z*E2*(6+3*(dd+3*d)+Q(7,2)*d*d)
    Ninv=Z*E1;v=4*x*Z*E1*E1;vt=Z*E1*E1*(4*x+(2*x+4*Z*x)*4*x);Bst=1/(1-v*v)
    out['BI']=Ninv*Bst*(vt*Bst+v*(2*d+1))+Ninv*Ninv*Bst*x*x/2
    out['BJ']=Bst*(E1*(Z+l)+v*Ninv*d)+(2+21*(Z+1+x)+x)/2
    out['BO']=Ninv*Ninv*Bst*(x+(3+8*Z*x+2*x+v*vt*Bst)*x)+2*x+Z+1+x
    return out
def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    bind(PARENT/'TERMINAL.json','b79e63c2e6bcb547ce0fffb166c0bb8560f4722df9f90a884447860f47661ba3');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(PARENT/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():bind(p,h)
    audit=PARENT/'audit';bind(audit/'AUDIT_TERMINAL.json','6e79a0458106bc3105ebf135f39753c9f4a6344f86ff9af002bc51d1847d774d');at=read(audit/'AUDIT_TERMINAL.json');need(at['pass_status'],'AUDIT_PASS')
    for n,k in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:bind(audit/n,at[k])
    if 'derivation_sha256' in at:bind(audit/'DERIVATION.txt',at['derivation_sha256'])
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE))
    old=read(MAJOR/'RESULT.json');c={k:Q(v) for k,v in old['constants_exact'].items()};conditioned={k:Q(v) for k,v in read(COND/'RESULT.json')['constants_exact'].items()}
    inv={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE/RESULT.json')['constants_exact'].items()}
    rho=c['rho'];a=c['a'];gap=c['gap'];dc=inv['complex_D_normalized_lower'];d0=inv['real_D_normalized_lower'];Cm=Q(11,4)/d0;Cf=c['Cscalar']
    def response(load):
        qt,qm,qk,qr,qi,j,o=load;cn=c['Cc']*qt;xi=32768*qi
        sp=Q(3,2)*cn+64*qm;sc=18*sp+28*cn+qr;sg=2*cn+6*sp+qk
        force=sg+80*sc/(4*dc);rw=cn+Q(39,4)*xi+2*j+o/2;g=(Q(1,2)+1/(4*d0))*rw+sc/d0
        uf=Cf*(force+g);xp=(Cm*(sc+uf+sp)+rho*(uf/6+sp/2))/(1-Q(3,2)*rho)
        yp=3*xp+uf/3+sp;up=2*xp+4*yp+Q(5,2)*uf+9*sp/rho;uc=16384*(uf/2+xi/4+o)
        return 3*up+cn+uf+2*xi+2*uc
    names=('BT','BM','BK','BR','BI','BJ','BO');alpha={}
    for i,name in enumerate(names):alpha[name]=response([Q(int(i==j)) for j in range(7)])
    gate(all(x>0 for x in alpha.values()),'POSITIVE_DIRECTIONAL_RESPONSE')
    gate(sum(alpha.values())==response([Q(1)]*7)==conditioned['C'],'UNIFORM_LOAD_REPRODUCES_PARENT_RESPONSE')
    vals=envelopes(a,gap);jet=envelopes(Dual(0,1),gap);zp=256/gap
    table={'BT':(0,6),'BM':(0,Q(259,3)),'BK':(16512,49858+514*zp),'BR':(53254,152448+1664*zp),'BI':(0,32768),'BJ':(Q(1495,2),76+Q(23,2)*zp),'BO':(65,16387+zp)}
    masses={};budget={}
    for name in names:
        gate(vals[name]==Q(old['envelopes_exact'][name]),'IDENTICAL_SOURCE_ENVELOPE:'+name)
        gate((jet[name].a,jet[name].b)==tuple(map(Q,table[name])),'CONSTANT_LINEAR_TABLE:'+name)
        masses[name]=vals[name]-jet[name].a-a*jet[name].b;gate(masses[name]>=0,'NONNEGATIVE_HIGHER_SOURCE:'+name)
        budget[name]=alpha[name]*masses[name]
    mass=sum(budget.values());gate(mass>0,'POSITIVE_WEIGHTED_SOURCE');K=Q(ceil(max(Q(1),1/a,2*mass/a**2)))
    gate(K<conditioned['K'] and K*a>=1 and K>=2*mass/a**2,'IMPROVED_ALL_ORDER_DOMINANCE')
    s=c['seed'];R=1/(96*K);radius=R/(8*s);MD=9*R/(1-R);kr=K*R
    gate(Q(1,2)+kr/(1-kr)**2<1 and 2*kr/(1-kr)**2+2*kr**2/(1-kr)**3<Q(1,2),'CONTRACTION')
    gate(4*R<gap and 2*R<1,'CHART_DOMAIN');Z=64/(1-4*R/gap);E1=1/(1-R);v=4*R*Z*E1**2
    gate(v<Q(1,2),'TIMELIKE_WALL');lapseinv=Z*E1/(1-v*v);gate(lapseinv<=128,'INVERSE_LAPSE')
    signed=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q;tail=MD*q**4/(1-q)
        if tail<=700*eta**2 and tail<=20000*eta**3:signed=(j,q,eta,tail);break
    gate(signed is not None,'CUBIC_SIGN_REMAINDER');js,qs,etas,tails=signed
    MF=Q(129,32)*MD;clock=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q/2;tail=MF*q**3/(1-q);dtail=MD*(q/2)**2/(1-q/2)
        if tail<=10*eta**2 and dtail<=25*eta:clock=(j,q,eta,tail,dtail);break
    gate(clock is not None,'CLOCK_SIGN_REMAINDER');jc,qc,etac,tailc,dtail=clock
    gate(etac<Q(1,512) and Q(25,64)*etac-60*etac**2>0,'OPENING_REMAINS_INCREASING')
    qd=etac/radius;chi_tail=R*qd**2/(1-qd);chie_tail=R*qd**2*(2-qd)/(1-qd)**2
    gate(chi_tail<=etac/40000 and chie_tail<=etac/40000,'PHYSICAL_SCALAR_DEPARTURE_TAILS')
    depart=read(PARENT/'RESULT.json')
    for arm,pair in depart['first_scalar_coefficient_enclosures'].items():
        lo,hi=map(Q,pair);gate(Q(1,20000)<lo<=hi<Q(1,10000),'AUTHENTICATED_SCALAR_COEFFICIENT:'+arm)
    gate(set(depart['first_scalar_coefficient_enclosures'])=={'primary','independent'},'SCALAR_INVENTORY')
    gate(radius>conditioned['eta_physical_radius'] and etac>conditioned['clock_eta'],'BOTH_RADII_IMPROVE')
    exact=dict(a=a,weighted_source_mass=mass,K=K,R=R,eta_physical_radius=radius,observable_sup=MD,inverse_lapse_bound=lapseinv,cubic_q=qs,cubic_eta=etas,cubic_tail=tails,clock_MF=MF,clock_q=qc,clock_eta=etac,clock_tail=tailc,distance_tail_after_linear=dtail,scalar_tail=chi_tail,scalar_euler_tail=chie_tail,scalar_departure_threshold=etac/40000,radius_gain=radius/conditioned['eta_physical_radius'])
    need(time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='WEIGHTED_SOURCE_LOCAL_CONVERGENCE_REMAINDER_AND_PHYSICAL_DEPARTURE',constants_exact={k:str(v) for k,v in exact.items()},source_weights={k:str(v) for k,v in alpha.items()},source_masses={k:str(v) for k,v in masses.items()},source_budget_shares={k:str(v/mass) for k,v in budget.items()},source_zero_linear={k:[str(jet[k].a),str(jet[k].b)] for k in names},display={k:decade(exact[k]) for k in ('eta_physical_radius','cubic_eta','clock_eta','scalar_departure_threshold','radius_gain')},cubic_dyadic_halvings=js,clock_dyadic_halvings=jc,gates=gates,seconds=time.monotonic()-started,new_ode_solves=0,scope='Same certified neutral analytic family; a directional positive source estimate sharpens its sufficient bounds. Proof-budget shares are not physical force shares. Both signs and scalar departure retain the previous qualified scope; no endpoint or generic-flow theorem.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps({k:result[k] for k in ('pass_status','classification','display','cubic_dyadic_halvings','clock_dyadic_halvings','seconds')}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_weighted_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('WEIGHTED_SOURCE_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
