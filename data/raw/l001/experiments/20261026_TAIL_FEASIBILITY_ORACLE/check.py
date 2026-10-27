"""Exact optimistic scalar feasibility, not a physical continuation test."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
GOAL=BASE/'20261026T183955Z_CONVERGENCE_TWO_HOUR_GOAL'
JOINT=BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY'
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
class Jet:
    def __init__(self,a=0,b=0,c=0):self.v=(Q(a),Q(b),Q(c))
    @staticmethod
    def cast(x):return x if isinstance(x,Jet) else Jet(x)
    def __add__(self,x):return Jet(*(a+b for a,b in zip(self.v,self.cast(x).v)))
    __radd__=__add__
    def __neg__(self):return Jet(*(-a for a in self.v))
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        b=self.cast(x).v;return Jet(*(sum(self.v[j]*b[n-j] for j in range(n+1)) for n in range(3)))
    __rmul__=__mul__
    def reciprocal(self):
        a,b,c=self.v;need(a!=0,'JET_POLE');return Jet(1/a,-b/a**2,b*b/a**3-c/a**2)
    def __truediv__(self,x):return self*self.cast(x).reciprocal()
    def __rtruediv__(self,x):return self.cast(x)*self.reciprocal()
    def __pow__(self,n):
        need(isinstance(n,int),'INTEGER_POWER')
        if n<0:return self.reciprocal()**(-n)
        out=Jet(1)
        for _ in range(n):out=out*self
        return out
def f(q):return q*q/(1-q)**2
def df(q):return 2*q/(1-q)**3
def classify(u,lo,hi):
    if u>=1:return dict(classification='DOMAIN_FAIL')
    if df(u)>=1:return dict(classification='NECESSARY_CONTRACTION_FAIL',derivative=str(df(u)))
    c=u-u*u-2*u**3
    lower=f(lo)-lo+(df(lo)-1)*(hi-lo)+c
    upper=f(lo)-lo+c
    out=dict(minimum_lower=str(lower),candidate_self_map_excess=str(upper))
    if lo>u and upper<=0:
        out.update(classification='OPTIMISTIC_SCALAR_PASS',q=str(lo),scaled_delta=str(lo-u),contraction=str(df(lo)))
    elif lower>0:out['classification']='NO_SCALAR_SELF_MAP'
    else:out['classification']='UNRESOLVED'
    return out
def main(lease):
    started=time.monotonic();old=GOAL/'final_verification';inputs={}
    def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
    bind(old/'TERMINAL.json','d69e87b371131bba179dd35ee26435e75bc26c3bd6b8502373b6873401551950')
    t=read(old/'TERMINAL.json');need(t['pass_status'],'CLOSURE_PASS')
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:bind(old/n,t[k])
    for p,h in read(old/'BINDING.json')['inputs'].items():bind(p,h)
    design=BASE/'20261026T205600Z_TAIL_MAJORANT_DESIGN_R1'
    for n in ('DESIGN.md','REVIEW.md'):bind(design/n,sha(design/n))
    need(inputs.get(str(JOINT/'check.py'))==sha(JOINT/'check.py'),'ENVELOPE_SOURCE_PIN')
    parent=load('oracle_joint_envelopes',JOINT/'check.py')
    need(len(str(10**20000))==20001,'WARMUP')
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','CONTRACT.json')};runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'UNBOUND_RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
    cfg=read(ROOT/'CONTRACT.json');joint=read(JOINT/'RESULT.json');K=Q(joint['constants_exact']['K']);seed=Q(cfg['seed']);oldradius=Q(joint['constants_exact']['eta_physical_radius'])
    need(oldradius==1/(768*K*seed),'NORMALIZATION')
    need(df(Q(1,8))==Q(128,343) and df(Q(1,4))==Q(32,27),'DERIVATIVE_CONTROLS')
    x=Jet(0,1);need((1/(1-x)).v==(1,1,1) and ((1-2*x)**-2).v==(1,4,12),'JET_CONTROLS')
    lo,hi=Q(1,8),Q(1,4)
    for _ in range(cfg['critical_point_bisections']):
        mid=(lo+hi)/2
        if df(mid)<1:lo=mid
        else:hi=mid
    need(df(lo)<1<=df(hi),'CRITICAL_BRACKET')
    rows=[]
    for label,eta in [('gain_'+str(g),g*oldradius) for g in cfg['gain_targets']]+[('absolute_'+a,Q(a)) for a in cfg['absolute_amplitude_targets']]:
        u=4*K*seed*eta;rec=classify(u,lo,hi)
        if rec['classification']=='OPTIMISTIC_SCALAR_PASS':
            q=Q(rec['q']);delta=(q-u)/K;p=u/K
            G=lambda w:K*w*w/(1-K*w)**2
            varrho=4*eta;e=G(p)-K*seed**2*varrho**2-2*K*K*seed**3*varrho**3
            need(e>=0 and e+G(p+delta)-G(p)<=delta and df(q)<1,'ORIGINAL_SELF_MAP_CHECK')
        rows.append(dict(target=label,physical_radius=str(eta),gain=str(eta/oldradius),u=str(u),**rec))
    # Ordinary Taylor coefficient two of the inherited positive budgets.
    c={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
    alpha={k:Q(v) for k,v in read(BASE/'20261026_NEUTRAL_WEIGHTED_SOURCE_MAJORANT/RESULT.json')['source_weights'].items()}
    vals=parent.envelopes(x,c['gap']);ws=4*x*(1+2*x)/(1-2*x)**3;V=3*x+22*ws*x/c['rho']
    ct=138*V*V/(1-160*ws/c['rho']-840*ws*ws/c['rho']**2)
    need(ct.v[:2]==(0,0) and ct.v[2]==1242,'TRACE_QUADRATIC_CONTROL')
    budget={'TRACE_RESPONSE':alpha['BT']/c['Cc']*ct.v[2]}
    budget.update({n:alpha[n]*v.v[2] for n,v in vals.items()})
    need(all(v>=0 for v in budget.values()),'POSITIVE_QUADRATIC_BUDGET')
    mass=sum(budget.values());need(K>=2*mass>0,'K_QUADRATIC_DOMINANCE')
    selected=next(r for r in joint['candidates'] if r['k']==joint['selected_k']);a=Q(selected['a'])
    for n,v in budget.items():need(Q(selected['budget'][n])>=v*a*a,'FINITE_VS_QUADRATIC:'+n)
    largest=max(budget,key=budget.get);remainder=mass-budget[largest];need(remainder>0,'REMAINING_BUDGET')
    source_report=dict(quadratic_coefficients={n:str(v) for n,v in budget.items()},shares={n:str(v/mass) for n,v in budget.items()},largest=largest,total=str(mass),K_over_twice_quadratic_mass=str(K/(2*mass)),perfect_largest_removal_quadratic_gain=str(mass/remainder),interpretation='Shares and hypothetical deletion describe sufficient estimates only; deleting a source is not an authorized physical or mathematical change.')
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
    result=dict(pass_status=True,classification='FIXED_BOUND_OPTIMISTIC_FEASIBILITY_AND_ESTIMATE_BUDGET',K=str(K),seed=str(seed),old_radius=str(oldradius),critical_q_bracket=[str(lo),str(hi)],oracle=rows,source_budget=source_report,seconds=time.monotonic()-started,ode_solves=0,new_physical_certificate=False,scope='Optimistic scalar feasibility and proof-conditioning diagnosis; no actual a2/a3 norm bounds, useful-amplitude result or physical source attribution.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps(dict(seconds=result['seconds'],arms=[{k:r[k] for k in ('target','classification')} for r in rows],largest_source=largest,K_over_twice_quadratic_mass=float(K/(2*mass)),largest_share=float(budget[largest]/mass),perfect_largest_removal_gain=float(mass/remainder))),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','TERMINAL.json','FAILURE.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        lease=load('oracle_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ORACLE_300_SECONDS')));signal.alarm(300)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
