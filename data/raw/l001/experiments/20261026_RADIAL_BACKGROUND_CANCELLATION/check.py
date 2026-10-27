"""Background-subtracted radial envelope; same coupled-bound gates, no ODE."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_TAIL_FEASIBILITY_ORACLE';JOINT=BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1048576):h.update(b)
    return h.hexdigest()
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
def response(w,lam,kap,c,env):
    B=w;X=lam*w;C=kap*w;Y=B+X+C;rho=c['rho'];gap=c['gap'];d0=Q(3,16384);dc=d0/2
    J=1/(1-2*X);W=4*X*J;d=B*(1+W)
    Z=64+1320*X+37600*X*X+64*(4*X/gap)**3/(1-4*X/gap);v=Z*X/(1-B)**2
    I=(2+v*v)*2*d*X+(Z+2*J*B)*X*X+v*v*X+C*C/(2*(1-B)*(1-v*v))
    ws=4*Y*(1+2*Y)/(1-2*Y)**3;V=3*Y+22*ws*Y/rho
    cn=138*V*V/(1-160*ws/rho-840*ws*ws/rho**2)
    e=env(Y,gap);xn=8192*I;sp=Q(3,2)*cn+64*e['BM'];sc=18*sp+28*cn+e['BR'];sg=2*cn+6*sp+e['BK']
    force=sg+80*sc/(4*dc);rw=cn+Q(39,4)*xn+2*e['BJ']+e['BO']/2;g=(Q(1,2)+1/(4*d0))*rw+sc/d0
    uf=c['Cscalar']*(force+g);Cm=Q(11,4)/d0
    xp=(Cm*(sc+uf+sp)+rho*(uf/6+sp/2))/(1-Q(3,2)*rho)
    yp=3*xp+uf/3+sp;up=2*xp+4*yp+Q(5,2)*uf+9*sp/rho
    return (3*up+cn+uf,xn,32768*(uf/2+xn/4+e['BO']))
def domain(a,lam,kap,c):
    X=lam*a;Y=(1+lam+kap)*a;gap=c['gap'];rho=c['rho']
    if not (2*Y<1 and 4*Y<gap):return False
    ws=4*Y*(1+2*Y)/(1-2*Y)**3
    if 1-160*ws/rho-840*ws*ws/rho**2<=0:return False
    z=lambda x:64+1320*x+37600*x*x+64*(4*x/gap)**3/(1-4*x/gap)
    return z(X)*X/(1-a)**2<Q(1,2) and 4*Y*z(Y)/(1-Y)**2<Q(1,2)

class Poly:
    def __init__(self,d=0):
        self.d=d if isinstance(d,dict) else {():Q(d)}
        self.d={k:v for k,v in self.d.items() if v}
    @staticmethod
    def cast(x):return x if isinstance(x,Poly) else Poly(x)
    def __add__(self,x):
        d=self.d.copy()
        for k,v in self.cast(x).d.items():d[k]=d.get(k,Q(0))+v
        return Poly(d)
    __radd__=__add__
    def __neg__(self):return Poly({k:-v for k,v in self.d.items()})
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        d={}
        for k,v in self.d.items():
            for l,w in self.cast(x).d.items():
                key=tuple(sorted(k+l));d[key]=d.get(key,Q(0))+v*w
        return Poly(d)
    __rmul__=__mul__
    def __pow__(self,n):
        out=Poly(1)
        for _ in range(n):out=out*self
        return out
def radial_identity():
    eb,ep,H,T,Lp,Lf,phi,f,E,h,m,D2p,Dp,Df=[Poly({(n,):Q(1)}) for n in ('eb','ep','H','T','Lp','Lf','phi','f','E','h','m','D2p','Dp','Df')]
    a0=6*H**2-Q(1,2)*T**2
    original=eb*(6*(H+Lp)**2-Q(1,2)*(T+Lf)**2)-6+Q(1,2)*m*(phi+f)**2-E**2*ep*(6*h**2+3*(D2p+3*h*Dp)+3*Dp**2+Q(1,2)*Df**2)
    rewritten=(eb-1)*a0+eb*(12*H*Lp-T*Lf+6*Lp**2-Q(1,2)*Lf**2)+m*phi*f+Q(1,2)*m*f**2-6*h**2*E**2*(ep-1)-E**2*ep*(3*D2p+9*h*Dp+3*Dp**2+Q(1,2)*Df**2)
    background=a0-6+Q(1,2)*m*phi**2-6*h**2*E**2
    return not (original-rewritten-background).d
def radial_envelope(x,gap):
    G=1/(1-2*x);Z=64+1320*x+37600*x*x+64*(4*x/gap)**3/(1-4*x/gap)
    w=4*x*G;wu=2*x*G;wt=4*x*G+8*x*x*G*G
    d=x*(1+w);dd=x*(1+2*w+w*wu+wt+w*w);l=G*x
    return Q(25,2)*Z*Z*(G-1)+G*(13*Z*l+Q(13,2)*l*l)+Z*x+x*x/2+Z*Z*G*(3*dd+9*d+Q(7,2)*d*d)

def main(lease):
    started=time.monotonic();inputs={};gates={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    def gate(v,n):need(v,n);gates[n]=True
    bind(PARENT/'TERMINAL.json','cb18ff625e7727f3c4425d80c90d96018c0675c51c283daab8582748e3628988');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256')]:bind(PARENT/n,t[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():bind(p,h)
    for n in ('review.txt','NORMALIZED_GRAPH_CANDIDATE.txt'):bind(PARENT/n,sha(PARENT/n))
    recent=BASE/'20261026_NORMALIZED_COUPLED_MAJORANT'
    bind(recent/'TERMINAL.json','e37fb26ee9c3fb8625887852c28bed63674d18e9e20a50a3ede78ee6d717627f')
    rt=read(recent/'TERMINAL.json')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(recent/n,rt[k])
    for group in ('inputs','sources','runtime'):
        for p,h in read(recent/'BINDING.json')[group].items():bind(p,h)
    u=load('coupled_util',PARENT/'check.py');par=load('coupled_six_sources',JOINT/'check.py')
    old_envelopes=par.envelopes
    def replacement(x,gap):
        out=old_envelopes(x,gap);new=radial_envelope(x,gap)
        z=64+1320*x+37600*x*x+64*(4*x/gap)**3/(1-4*x/gap)
        diff=out['BR']-new-13*z*z-6
        need(all(v==0 for v in diff.v) if isinstance(diff,u.Jet) else diff==0,'ENVELOPE_DIFFERENCE_IDENTITY')
        out['BR']=new;return out
    par.envelopes=replacement
    gate(radial_identity(),'EXACT_RADIAL_POLYNOMIAL_IDENTITY')
    gate((u.Jet(1)+u.Jet(0,1)).v==(1,1,0),'JET_CONTROL')
    check=radial_envelope(u.Jet(0,1),Q(1,2**24))
    gate(check.v[0]==0 and check.v[1]>0 and check.v[2]>0,'RADIAL_LEADING_COEFFICIENTS')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','CONTRACT.json','DERIVATION.txt')}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
    cfg=read(ROOT/'CONTRACT.json');c={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    seed_evidence={}
    for engine in ('primary','independent'):
        q=read(BASE/'20261026_GROWING_MODE_QUADRATIC_R1'/('PRODUCTION_'+engine+'.json'));sums=Q(0);bounds={}
        for side in ('lower','upper'):
            v=max(abs(Q(x)) for x in q['walls'][side]['loads']['chi1']['exact_bounds']);bounds[side]=str(v);sums+=v
        gate(sums<=Q(cfg['summed_wall_seed_bound']),'WALL_SEED_'+engine);seed_evidence[engine]=dict(bounds=bounds,sum=str(sums))
    rows=[]
    for lam in map(Q,cfg['graph_weights']):
        for kap in map(Q,cfg['oscillator_weights']):
            jets=response(u.Jet(0,1),lam,kap,c,par.envelopes)
            gate(jets[1].v[0]==jets[1].v[1]==0,'GRAPH_ORDER_'+str(lam)+'_'+str(kap))
            gate(jets[1].v[2]==8192*(4*lam+64*lam*lam+kap*kap/2),'GRAPH_QUADRATIC_'+str(lam)+'_'+str(kap))
            for exponent in cfg['evaluation_exponents']:
                a=Q(1,2**exponent);row=dict(graph_weight=str(lam),oscillator_weight=str(kap),exponent=exponent,a=str(a))
                if not domain(a,lam,kap,c):row['admitted']=False;row['reason']='POSITIVE_DOMAIN';rows.append(row);continue
                vals=response(a,lam,kap,c,par.envelopes)
                masses=[(v-j.v[0]-a*j.v[1])/scale for v,j,scale in zip(vals,jets,(Q(1),lam,kap))]
                gate(all(v>=0 for v in masses),'POSITIVE_MASSES_'+str(len(rows)))
                M=max(masses);K=Q(ceil(max(Q(1),1/a,2*M/a**2)))
                gate(K*a>=1 and K>=2*M/a**2,'MAJORANT_'+str(len(rows)))
                row.update(admitted=True,masses=[str(v) for v in masses],K=str(K));rows.append(row)
    admitted=[v for v in rows if v['admitted']];gate(bool(admitted),'ADMITTED_RAY')
    best=min(admitted,key=lambda v:Q(v['K']));K=Q(best['K']);lam=Q(best['graph_weight']);kap=Q(best['oscillator_weight'])
    seed=max(Q(cfg['bulk_seed_bound']),Q(cfg['summed_wall_seed_bound'])/kap);gate(seed==16444,'SEPARATE_SEED')
    R=1/(96*K);Y=(1+lam+kap)*R;radius=R/(8*seed);kr=K*R
    gate(Q(1,2)+kr/(1-kr)**2<1 and 2*kr/(1-kr)**3<Q(1,2),'CONTRACTION')
    gate(4*Y<c['gap'] and 2*Y<1,'AGGREGATE_CHART')
    Z=64/(1-4*Y/c['gap']);v=4*Y*Z/(1-Y)**2;gate(v<Q(1,2),'TIMELIKE')
    lapseinv=Z/(1-Y)/(1-v*v);gate(lapseinv<=128,'LAPSE')
    MD=9*Y/(1-Y);MF=Q(129,32)*MD
    coeff=read(BASE/'20261026_NEUTRAL_CUBIC_CLOCK_TAIL/RESULT.json')['coefficient_intervals']
    gate(set(coeff)=={'primary','independent'},'BOTH_COEFFICIENT_ENGINES')
    for name,rec in coeff.items():
        a,b=map(Q,rec['F2']);aa,bb=map(Q,rec['F3']);gate(-50<a<=b<-21 and -10000<aa<=bb<10000,'CLOCK_COEFFICIENT_'+name)
    chosen=None
    for j in range(1,8193):
        q=Q(1,2**j);eta=radius*q/2;tail=MF*q**4/(1-q);known=10000*eta**3;qd=q/2
        dt=MD*qd**2/(1-qd);st=Y*qd**2/(1-qd);se=Y*qd**2*(2-qd)/(1-qd)**2
        if known+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:chosen=(j,q,eta,tail,known,dt,st,se);break
    gate(chosen is not None,'FULL_CLOCK_AND_SCALAR_TAILS');j,q,eta,tail,known,dt,st,se=chosen
    gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_SIGN')
    prior={k:Q(v) for k,v in read(recent/'RESULT.json')['constants_exact'].items()}
    gate(radius>prior['physical_radius'] and eta>prior['clock_eta'],'BOTH_BOUNDS_IMPROVE')
    exact=dict(K=K,seed=seed,R=R,aggregate_bound=Y,physical_radius=radius,clock_eta=eta,observable_sup=MD,clock_sup=MF,clock_tail=tail,known_cubic=known,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000,radius_gain=radius/prior['physical_radius'],clock_gain=eta/prior['clock_eta'])
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
    result=dict(pass_status=True,classification='BACKGROUND_SUBTRACTED_RADIAL_LOCAL_MAJORANT',selected=best,candidates=rows,seed_evidence=seed_evidence,constants_exact={k:str(v) for k,v in exact.items()},gates=gates,seconds=time.monotonic()-started,ode_solves=0,scope='Conservative bound for same local neutral family; useful amplitude and endpoint remain unestablished.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
    print(json.dumps(dict(seconds=result['seconds'],selected={k:best[k] for k in ('graph_weight','oscillator_weight','exponent')},display={k:float(exact[k]) for k in ('physical_radius','clock_eta','radius_gain','clock_gain')})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        lease=load('coupled_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COUPLED_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()

