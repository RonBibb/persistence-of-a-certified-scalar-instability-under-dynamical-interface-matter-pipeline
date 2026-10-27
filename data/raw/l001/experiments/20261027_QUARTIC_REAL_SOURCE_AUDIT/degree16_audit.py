"""Independent sparse rational series evaluation and degree16 reductions."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_DEGREE16_DISTANCE_MAJORANT';N=16;CUTOFF=1793101111;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
class P:
 def __init__(self,v=0):self.v={i:Q(x) for i,x in v.items() if x and i<=N} if isinstance(v,dict) else ({0:Q(v)} if v else {})
 @staticmethod
 def cast(v):return v if isinstance(v,P) else P(v)
 def get(self,n):return self.v.get(n,Q(0))
 def dense(self):return [self.get(i) for i in range(N+1)]
 def __add__(self,v):
  v=self.cast(v);out=dict(self.v)
  for i,x in v.v.items():out[i]=out.get(i,Q(0))+x
  return P(out)
 __radd__=__add__
 def __neg__(self):return P({i:-x for i,x in self.v.items()})
 def __sub__(self,v):return self+-self.cast(v)
 def __rsub__(self,v):return self.cast(v)+-self
 def __mul__(self,v):
  v=self.cast(v);out={}
  for i,x in self.v.items():
   for j,y in v.v.items():
    if i+j<=N:out[i+j]=out.get(i+j,Q(0))+x*y
  return P(out)
 __rmul__=__mul__
 def inverse(self):
  c=self.get(0);ck(c!=0,'NONZERO_CONSTANT');res=P(1);term=P(1);tail=P(1)-self*(1/c)
  for _ in range(1,N+1):term=term*tail;res=res+term
  return res*(1/c)
 def __truediv__(self,v):return self*self.cast(v).inverse()
 def __rtruediv__(self,v):return self.cast(v)*self.inverse()
 def __pow__(self,n):
  ck(isinstance(n,int) and n>=0,'POWER');out=P(1);base=self
  while n:
   if n%2:out=out*base
   n//=2
   if n:base=base*base
  return out
def main():
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'TERMINAL:'+n)
 bound={}
 for g in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[g].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 def module(n,path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'MODULE_AUTH:'+path);return load(n,p)
 old=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');raw=auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json');result=read(ROOT/'RESULT.json')
 M=module('d16_review_primitive','20261027_SIXTH_CLOCK_ENCLOSURE/check.py');ep=module('d16_review_endpoint','20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py');prim=module('d16_review_raw','20261026_ROUTED_SOURCE_BUDGET_R1/check.py').primitives;env=module('d16_review_env','20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
 c={k:Q(v) for k,v in raw['constants_exact'].items()};base={k:Q(v) for k,v in old['constants_exact']['ninth'].items()};c['C0']=base['C0'];c['total']=base['Cscalar'];row=fixed['selected']['refined'];lam,kap=Q(row['graph_weight']),Q(row['oscillator_weight']);weights={k:list(map(Q,v)) for k,v in fixed['response_weights']['refined'].items()};K,seed=base['K'],base['seed']
 trial=P({i:Q(i+1) for i in range(N+1)});ck((trial*trial.inverse()).dense()==P(1).dense(),'SPARSE_INVERSE_CONTROL')
 ps=M.finite_primitives(P({1:1}),lam,kap,c,ep,prim,env);coeff=[p.dense() for p in ps]
 ck(result['source_coefficients']==[list(map(str,v)) for v in coeff],'ALL_SOURCE_COEFFICIENTS')
 for i,v in enumerate(coeff):ck(all(x>=0 for x in v) and list(map(str,v[:10]))==old['source_coefficients'][i],'SOURCE_PREFIX:'+str(i))
 H=[Q(0)]*(N+1);routed={}
 for m in range(2,N+1):
  loads=[v[m] for v in coeff];values=[sum(a*b for a,b in zip(weights['B'],loads)),loads[1]/lam,sum(a*b for a,b in zip(weights['C'],loads))/kap];routed[str(m)]=list(map(str,values));H[m]=m*max(values);ck(0<=H[m]<=(m-1)*K**(m-1),'H_DOMINATION')
 ck(list(map(str,H))==result['H'] and routed==result['routed'],'ROUTING')
 z=P({1:seed});w=P({1:seed})
 for n in range(2,N+1):
  zn=sum(H[m]*(z**m).get(n) for m in range(2,n+1));wn=sum((m-1)*K**(m-1)*(w**m).get(n) for m in range(2,n+1));ck(0<=zn<=wn,'Z_DOMINATION');z=z+P({n:zn});w=w+P({n:wn})
 ck(list(map(str,z.dense()))==result['majorant'] and list(map(str,w.dense()))==result['scalar_comparator'],'BOTH_RECURRENCES')
 b=P({n:z.get(n)/n**2 for n in range(1,N+1)});x=P({n:2*lam*z.get(n)/n**3 for n in range(2,N+1)})
 ex=P(1);term=P(1)
 for n in range(1,N+1):term=term*b*(Q(1,n));ex=ex+term
 d=3*(ex*(1+x)-1);distance=d.dense();ck(list(map(str,distance))==result['distance'],'INDEPENDENT_EXP_DISTANCE')
 for name,values in [('H',H),('majorant',z.dense()),('distance',distance)]:ck(list(map(str,values[:10]))==old[name],'PREFIX:'+name)
 ck(result['degree']==N and all(result['gates'].values()),'SAVED_GATES')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),scope='Independent sparse rational series arithmetic, geometric-series reciprocals, polynomial exponential, all seven source coefficients, routing/recurrences/distance and bindings. Inherited qualified primitive formula functions reused; no independent all-order source derivation, signed coefficients or new ODE.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'DEGREE16_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');p=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('d16_review_lease',p);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDIT_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
