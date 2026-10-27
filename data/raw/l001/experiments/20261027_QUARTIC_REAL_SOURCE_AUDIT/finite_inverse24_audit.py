"""Independent sparse rational series evaluation and degree24 reductions."""
import math
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_FINITE_INVERSE_LAPSE24';N=24;CUTOFF=1793101111;COUNT=0
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
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 high=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');raw=auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');result=read(ROOT/'RESULT.json')
 base={k:Q(v) for k,v in dp['arms']['both']['constants'].items()};R=base['physical_radius'];JC=Q(dp['global_departure']['coefficient_tail_sup']);gap=Q(raw['constants_exact']['gap']);lam=Q(fixed['selected']['refined']['graph_weight']);z=list(map(Q,high['majorant']))
 ck(high['degree']==N and len(z)==N+1 and all(v>=0 for v in z),'MAJORANT_PREFIX')
 ck(R>0 and JC>=0 and gap>0 and lam>0,'POSITIVE_PARAMETERS')
 for engine in ('primary','independent'):
  init=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');ck(init['initial_background'][0]['exact_bounds']==['0','0'] and init['initial_background'][4]['exact_bounds']==['1','1'],'LOWER_CLOCK_NORMALIZATION')
  lo,hi=map(Q,clock['arms'][engine]['values']['rate']['exact_bounds']);ck(0<lo<=hi<=Q(1,32),'RATE_BOUND')
  ck(list(map(Q,dp['inverse_intervals'][engine][1]))==[Q(-1),Q(-1)],'LINEAR_CLOCK_IDENTITY')
 B=P({n:z[n]/n**2 for n in range(1,N+1)});X=P({n:lam*z[n]/n**3 for n in range(2,N+1)});U=X*(4/gap)
 def exponential(poly):
  ck(poly.get(0)==0,'ZERO_EXP_CONSTANT');out=P(1);term=P(1)
  for k in range(1,N+1):term=term*poly*Q(1,k);out=out+term
  return out
 Eb=exponential(B);Ehat=P(1)+64*U*(1-U).inverse();Vhat=Ehat*exponential(2*B)*P({n:n*X.get(n) for n in range(1,N+1)})*Q(1,32);Jhat=Ehat*Eb*(1-Vhat*Vhat).inverse()
 for name,poly in [('B',B),('X',X),('Ehat',Ehat),('Vhat',Vhat),('Jhat',Jhat)]:
  ck(result['series'][name]==list(map(str,poly.dense())),'EXACT_SERIES:'+name);ck(all(v>=0 for v in poly.dense()),'POSITIVE_SERIES:'+name)
 ck(X.get(0)==X.get(1)==Vhat.get(0)==Vhat.get(1)==0 and Jhat.get(0)==Ehat.get(0)==1,'ORDERS_AND_CONSTANTS')
 old={int(n):Q(v) for n,v in dp['inverse_abs'].items()};new=dict(old)
 for n in range(9,N+1):new[n]=min(Jhat.get(n),JC/R**n);ck(0<=new[n]<=JC/R**n,'COEFFICIENT_FALLBACK')
 ck(result['retained_inverse']=={str(n):str(v) for n,v in old.items()} and result['inverse_abs']=={str(n):str(v) for n,v in new.items()},'BOUND_SELECTION')
 ck(result['constants']==dict(radius=str(R),tail_sup=str(JC),gap=str(gap),graph_weight=str(lam),rate_ceiling='1/32'),'CONSTANT_REPLAY');ck(result['degree']==N and all(result['gates'].values()),'SAVED_GATES')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),scope='Independent sparse polynomial exponentials and geometric reciprocals, all finite inverse-lapse majorants/normalizations/minima and immutable closure. Underlying analytic solution/norm/collar premises inherited; lower clock only, no amplitude certificate.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'FINITE_INVERSE24_AUDIT.json'
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


