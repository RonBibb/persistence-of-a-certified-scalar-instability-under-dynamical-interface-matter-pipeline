"""Conditional degree-seven local clock enclosure; no new ODE."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793082611
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
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
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[1],-a[0]
def mul(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def sc(a,k):return mul(a,(Q(k),Q(k)))
def pack(a):return list(map(str,a))
def sym(a):return -a,a
def conv(a,b,N):return [sum((a[j]*b[i-j] for j in range(i+1)),Q(0)) for i in range(N+1)]
def power(a,m,N):
 v=[Q(1)]+[Q(0)]*N
 for _ in range(m):v=conv(v,a,N)
 return v
class Series:
 def __init__(self,a=0):self.v=tuple(map(Q,(list(a)+[Q(0)]*8)[:8])) if isinstance(a,(list,tuple)) else (Q(a),)+(Q(0),)*7
 @staticmethod
 def cast(a):return a if isinstance(a,Series) else Series(a)
 def __add__(self,a):return Series([x+y for x,y in zip(self.v,self.cast(a).v)])
 __radd__=__add__
 def __neg__(self):return Series([-x for x in self.v])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):return Series(conv(self.v,self.cast(a).v,7))
 __rmul__=__mul__
 def inverse(self):
  need(self.v[0]!=0,'SERIES_NONZERO_CONSTANT');v=[1/self.v[0]]
  for n in range(1,8):v.append(-sum(self.v[j]*v[n-j] for j in range(1,n+1))/self.v[0])
  return Series(v)
 def __truediv__(self,a):return self*self.cast(a).inverse()
 def __rtruediv__(self,a):return self.cast(a)*self.inverse()
 def __pow__(self,n):
  need(isinstance(n,int) and n>=0,'SERIES_POWER');v=Series(1)
  for _ in range(n):v=v*self
  return v

def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')};gates={}
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def gate(v,n):need(v,n);gates[n]=True
 parent=BASE/'20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE'
 need(sha(parent/'TERMINAL.json')=='a98e864571e564186b7679200427979be4f892f2d44ab8b9dc0fa78fe4eb0ba6','PARENT_TERMINAL')
 pt=read(parent/'TERMINAL.json');gate(pt['pass_status'],'PARENT_PASS');inputs[str(parent/'TERMINAL.json')]=sha(parent/'TERMINAL.json')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
  need(sha(parent/n)==pt[k],'PARENT_ARTIFACT');inputs[str(parent/n)]=pt[k]
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_BINDING');inputs[p]=h
 def auth(path):
  p=BASE/path;need(inputs.get(str(p))==sha(p),'AUTHENTICATED:'+path);return read(p)
 prior=read(parent/'RESULT.json');base={k:Q(v) for k,v in prior['constants_exact']['actual_quartic'].items()}
 gate(Q(prior['clock_costs']['unknown7'])==max(map(Q,prior['clock_costs'].values())),'MEASURED_UNKNOWN7_DOMINATES')
 sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json')
 old=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');row=old['selected']['refined']
 c={k:Q(v) for k,v in auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
 c['C0']=base['C0'];c['total']=base['Cscalar']
 M=load('seventh_sixth_source',BASE/'20261027_SIXTH_CLOCK_ENCLOSURE/check.py')
 ep=load('seventh_endpoint',BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py')
 prim=load('seventh_primitive',BASE/'20261026_ROUTED_SOURCE_BUDGET_R1/check.py').primitives
 envmod=load('seventh_environment',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
 ring=load('seventh_ring',BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=CUTOFF))
 lam=Q(row['graph_weight']);kap=Q(row['oscillator_weight']);K=base['K'];seed=base['seed']
 weights={out:list(map(Q,vals)) for out,vals in old['response_weights']['refined'].items()}
 test=Series([1,2,3,4,5,6,7,8]);gate((test*test.inverse()).v==Series(1).v,'SERIES_INVERSE')
 ps=M.finite_primitives(Series([0,1]),lam,kap,c,ep,prim,envmod)
 for i,x in enumerate(ps):
  gate(list(map(str,x.v[:7]))==sixth['finite_source_coefficients'][i],'SOURCE_PREFIX:'+str(i));gate(all(v>=0 for v in x.v),'SOURCE_POSITIVE:'+str(i))
 H=[Q(0)]*8;routed={}
 for m in range(2,8):
  raw=[x.v[m] for x in ps];r=[sum(k*v for k,v in zip(weights['B'],raw)),raw[1]/lam,sum(k*v for k,v in zip(weights['C'],raw))/kap]
  H[m]=m*max(r);routed[str(m)]=list(map(str,r));gate(0<=H[m]<=(m-1)*K**(m-1),'H_DOMINATION:'+str(m))
 gate(list(map(str,H[:7]))==sixth['sixth_H'],'H_PREFIX')
 z=[Q(0)]*8;w=[Q(0)]*8;z[1]=w[1]=seed
 for n in range(2,8):
  z[n]=sum(H[m]*power(z,m,7)[n] for m in range(2,n+1));w[n]=sum((m-1)*K**(m-1)*power(w,m,7)[n] for m in range(2,n+1));gate(0<=z[n]<=w[n],'Z_DOMINATION:'+str(n))
 gate(list(map(str,z[:7]))==sixth['sixth_majorant'],'Z_PREFIX')
 b=[Q(0)]+[z[n]/n**2 for n in range(1,8)];x=[Q(0)]+[2*lam*z[n]/n**3 for n in range(1,8)];x[1]=Q(0)
 ex=[Q(1)]
 for n in range(1,8):ex.append(sum(k*b[k]*ex[n-k] for k in range(1,n+1))/n)
 d=[Q(0)]+[3*(ex[n]+sum(ex[j]*x[n-j] for j in range(n+1))) for n in range(1,8)]
 gate(list(map(str,d[:7]))==sixth['sixth_distance'],'DISTANCE_PREFIX')
 ring.NAMES=('L2','L3','L4','L5','L6');ring.N=5;ring.ZERO=(0,)*5
 l2,l3,l4,l5,l6=[ring.variable(j) for j in range(5)];ls=[ring.P(0),ring.P(1),l2,l3,l4,l5,l6];ei=[ring.P(1)]
 for n in range(1,7):ei.append(-sum((k*ls[k]*ei[n-k] for k in range(1,n+1)),ring.P(0))/n)
 e6=-l6+l5+l2*l4+l3*l3/2-l4/2-l2*l3-l2*l2*l2/6+l3/6+l2*l2/4-l2/24+Q(1,720)
 gate((ei[6]-e6).iszero(),'E6_SYMBOLIC_IDENTITY')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');coeff={}
 for engine in ('primary','independent'):
  af=auth('20261026_GROWING_MODE_CUBIC_AFFINE/PRODUCTION_'+engine+'.json');data={k:iv(v) for k,v in af['walls']['lower']['data'].items()};vals=clock['arms'][engine]['values']
  one,two,three,rate=[iv(vals[k]) for k in ('d1','d2','d3','rate')];k=iv(af['parameters']['k'])
  hp=neg(add(sc(mul(data['T'],data['T']),Q(1,3)),mul(k,mul(data['E'],data['E']))))
  hpp=add(sc(mul(data['T'],data['Tp']),-Q(2,3)),sc(mul(mul(k,data['H']),mul(data['E'],data['E'])),2))
  xi2,xi3=data['xi2'],data['xi3'];xi4=sym(lam*z[4]/64);xi6=sym(lam*z[6]/216)
  v2=sc(mul(mul(rate,data['E']),xi2),2)
  v3=mul(mul(rate,data['E']),add(sc(xi3,3),sc(mul(data['p1'],xi2),-6)))
  vel2=add(add(data['c2'],sc(data['p2'],-3)),add(neg(mul(data['H'],xi2)),sc(mul(data['p1'],data['p1']),Q(9,2))))
  v4=mul(mul(rate,data['E']),add(add(sc(xi4,4),sc(mul(data['p1'],xi3),-9)),sc(mul(xi2,vel2),2)))
  L6=add(add(sym(b[6]),mul(data['H'],xi6)),add(add(mul(hp,add(mul(xi2,xi4),sc(mul(xi3,xi3),Q(1,2)))),sc(mul(hpp,mul(mul(xi2,xi2),xi2)),Q(1,6))),add(neg(mul(v2,v4)),sc(mul(v3,v3),-Q(1,2)))))
  record=sixth['sixth_coefficients'][engine];log=[(Q(0),Q(0)),(Q(1),Q(1))]+[tuple(map(Q,record[n])) for n in ('L2','L3','L4','L5')]+[L6];ee=[(Q(1),Q(1))]
  for n in range(1,7):
   term=(Q(0),Q(0))
   for j in range(1,n+1):term=add(term,sc(mul(log[j],ee[n-j]),-j))
   ee.append(sc(term,Q(1,n)))
  ds=[(Q(0),Q(0)),one,two,three,tuple(map(Q,prior['coefficient_intervals'][engine]['d4'])),sym(d[5]),sym(d[6]),sym(d[7])]
  term=sc(ds[7],6)
  for j in range(1,7):term=add(term,sc(mul(ds[j],ee[7-j]),j))
  f7=mul(rate,term);coeff[engine]=dict(L6=pack(L6),v4=pack(v4),F7=pack(f7),F7_abs=str(max(map(abs,f7))))
 B4=Q(prior['selected_quartic_abs']);B5=Q(sixth['quintic_abs']);B6=Q(sixth['sixth_abs']);B7=max(Q(v['F7_abs']) for v in coeff.values());C2=Q(sixth['scalar_abs']['chi2']);C3=Q(sixth['scalar_abs']['chi3'])
 R=base['physical_radius'];MF=base['clock_sup'];MD=base['observable_sup'];Y=base['aggregate_bound']
 def certify(seventh):
  selected=None
  for j in range(1,8193):
   q=Q(1,2**j);eta=R*q/2;qd=q/2;tail=MF*q**(8 if seventh else 7)/(1-q);a3=10000*eta**3;a4=B4*eta**4;a5=B5*eta**5;a6=B6*eta**6;a7=B7*eta**7 if seventh else Q(0)
   dt=MD*qd**2/(1-qd);st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd);se=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
   if a3+a4+a5+a6+a7+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:selected=j;break
  gate(selected is not None,'REMAINDER_GATES:'+str(seventh));gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_SIGN:'+str(seventh))
  out=dict(base,clock_eta=eta,clock_tail=tail,known_cubic=a3,known_quartic=a4,known_quintic=a5,known_sixth=a6,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
  if seventh:out['known_seventh']=a7
  costs={k:v/(10*eta**2) for k,v in dict(cubic=a3,quartic=a4,quintic=a5,sixth=a6,seventh=a7,unknown_tail=tail).items()}
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=se/(eta/40000))
  return out,costs,ratios,j
 baseline,_,_,oldj=certify(False);gate(baseline==base and oldj==prior['selected_dyadic'],'EXACT_PARENT_CERTIFICATE')
 refined,costs,ratios,j=certify(True)
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
 gate(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 out=dict(pass_status=True,classification='SEVENTH_ORDER_LOCAL_CLOCK_ENCLOSURE',constants_exact={'baseline':{k:str(v) for k,v in baseline.items()},'seventh':{k:str(v) for k,v in refined.items()}},gain_exact=str(refined['clock_eta']/baseline['clock_eta']),coefficients=coeff,seventh_abs=str(B7),H=list(map(str,H)),majorant=list(map(str,z)),distance=list(map(str,d)),source_coefficients=[list(map(str,v.v)) for v in ps],routed=routed,clock_costs={k:str(v) for k,v in costs.items()},gate_ratios={k:str(v) for k,v in ratios.items()},selected_dyadic=j,gates=gates,seconds=time.monotonic()-started,scope='Unsigned finite seventh coefficient and unchanged global analytic tail. Local sufficient certificate only.')
 put('RESULT.json',out);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=out['seconds'],clock_eta=float(refined['clock_eta']),gain=float(refined['clock_eta']/baseline['clock_eta']),clock_costs={k:float(v) for k,v in costs.items()},gate_ratios={k:float(v) for k,v in ratios.items()})),flush=True)

if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF,'LINUX_CUTOFF');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('seventh_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('SEVENTH_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
