"""Uniform positive finite source majorant extended through degree24."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793101111;N=24
PARENT_PIN='d1a75f309d47ea127e12ff7ab4405debc71add158ae8e752ed19c8b23c25abea';AUDIT_PIN='13c9b299b41c5b5192aeaac1d1b6f8a30b29a8c9fed60065b22b138d942b0f54'
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
def conv(a,b):return [sum((a[k]*b[n-k] for k in range(n+1)),Q(0)) for n in range(N+1)]
def power(a,m):
 out=[Q(1)]+[Q(0)]*N
 for _ in range(m):out=conv(out,a)
 return out
class Series:
 def __init__(self,a=0):self.v=tuple(map(Q,(list(a)+[Q(0)]*(N+1))[:N+1])) if isinstance(a,(tuple,list)) else (Q(a),)+(Q(0),)*N
 @staticmethod
 def cast(x):return x if isinstance(x,Series) else Series(x)
 def __add__(self,x):return Series([a+b for a,b in zip(self.v,self.cast(x).v)])
 __radd__=__add__
 def __neg__(self):return Series([-x for x in self.v])
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):return Series(conv(self.v,self.cast(x).v))
 __rmul__=__mul__
 def inverse(self):
  need(self.v[0]!=0,'NONZERO_CONSTANT');a=[1/self.v[0]]
  for n in range(1,N+1):a.append(-sum(self.v[k]*a[n-k] for k in range(1,n+1))/self.v[0])
  return Series(a)
 def __truediv__(self,x):return self*self.cast(x).inverse()
 def __rtruediv__(self,x):return self.cast(x)*self.inverse()
 def __pow__(self,n):
  need(isinstance(n,int) and n>=0,'NONNEGATIVE_INTEGER_POWER');return Series(power(self.v,n))
def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')};gates={}
 def gate(v,n):need(v,n);gates[n]=True
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_DEGREE16_DISTANCE_MAJORANT';bind(parent/'TERMINAL.json',PARENT_PIN);t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 audit=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/DEGREE16_AUDIT.json';bind(audit,AUDIT_PIN);gate(read(audit)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 parent16=read(parent/'RESULT.json');prior=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');rawc=auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')
 for path in ('20261027_SIXTH_CLOCK_ENCLOSURE/check.py','20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py','20261026_ROUTED_SOURCE_BUDGET_R1/check.py','20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py'):need(inputs.get(str(BASE/path))==sha(BASE/path),'MODULE_BIND:'+path)
 M=load('d16_finite_sources',BASE/'20261027_SIXTH_CLOCK_ENCLOSURE/check.py');ep=load('d16_endpoint',BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py');prim=load('d16_primitive',BASE/'20261026_ROUTED_SOURCE_BUDGET_R1/check.py').primitives;env=load('d16_environment',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 base={k:Q(v) for k,v in prior['constants_exact']['ninth'].items()};c={k:Q(v) for k,v in rawc['constants_exact'].items()};c['C0']=base['C0'];c['total']=base['Cscalar']
 row=fixed['selected']['refined'];lam=Q(row['graph_weight']);kap=Q(row['oscillator_weight']);K=base['K'];seed=base['seed'];weights={k:list(map(Q,v)) for k,v in fixed['response_weights']['refined'].items()}
 test=Series(list(range(1,N+2)));gate((test*test.inverse()).v==Series(1).v,'SERIES_INVERSE');gate((Series([0,1])**N).v==tuple([Q(0)]*N+[Q(1)]),'SERIES_ORDER24')
 ps=M.finite_primitives(Series([0,1]),lam,kap,c,ep,prim,env)
 for i,p in enumerate(ps):gate(list(map(str,p.v[:17]))==parent16['source_coefficients'][i],'SOURCE_PREFIX:'+str(i));gate(all(v>=0 for v in p.v),'SOURCE_POSITIVE:'+str(i))
 H=[Q(0)]*(N+1);routed={}
 for m in range(2,N+1):
  raw=[p.v[m] for p in ps];loads=[sum(k*v for k,v in zip(weights['B'],raw)),raw[1]/lam,sum(k*v for k,v in zip(weights['C'],raw))/kap];H[m]=m*max(loads);routed[str(m)]=list(map(str,loads));gate(0<=H[m]<=(m-1)*K**(m-1),'H_DOMINATION:'+str(m))
 def recurrence(coeff):
  vals=[Q(0),seed]+[Q(0)]*(N-1);table=[[Q(0)]*(N+1) for _ in range(N+1)];table[1][1]=seed
  for n in range(2,N+1):
   for m in range(2,n+1):table[m][n]=sum(vals[j]*table[m-1][n-j] for j in range(1,n))
   vals[n]=sum(coeff[m]*table[m][n] for m in range(2,n+1));table[1][n]=vals[n]
  return vals
 z=recurrence(H);w=recurrence([Q(0),Q(0)]+[(m-1)*K**(m-1) for m in range(2,N+1)])
 for n in range(2,N+1):gate(0<=z[n]<=w[n],'Z_DOMINATION:'+str(n))
 b=[Q(0)]+[z[n]/n**2 for n in range(1,N+1)];x=[Q(0)]+[2*lam*z[n]/n**3 for n in range(1,N+1)];x[1]=Q(0);ex=[Q(1)]
 for n in range(1,N+1):ex.append(sum(k*b[k]*ex[n-k] for k in range(1,n+1))/n)
 d=[Q(0)]+[3*(ex[n]+sum(ex[j]*x[n-j] for j in range(n+1))) for n in range(1,N+1)]
 for name,vals in [('H',H),('majorant',z),('distance',d)]:gate(list(map(str,vals[:17]))==parent16[name],'EXACT_PREFIX:'+name)
 gate(all(v>=0 for v in d),'DISTANCE_POSITIVE')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 observed=lease.observed()
 if observed!=runtime:put('RUNTIME_DIFFERENCE.json',dict(added={p:h for p,h in observed.items() if p not in runtime},removed={p:h for p,h in runtime.items() if p not in observed}))
 need(observed==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,classification='DEGREE24_POSITIVE_DISTANCE_MAJORANT',degree=N,source_coefficients=[list(map(str,p.v)) for p in ps],H=list(map(str,H)),routed=routed,majorant=list(map(str,z)),scalar_comparator=list(map(str,w)),distance=list(map(str,d)),gates=gates,seconds=time.monotonic()-started,scope='Unsigned finite majorant extension; no new signed physical coefficients, no full-clock certificate or evolution.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,degree=N,gates=len(gates),seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('d16_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CAP_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
