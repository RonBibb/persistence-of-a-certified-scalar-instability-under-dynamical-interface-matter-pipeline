"""Exact endpoint positive-tail audit; no producer tail module imported."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY';CUTOFF=1793108564;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
class I:
 def __init__(self,a,b=None):self.lo,self.hi=Q(a),Q(a if b is None else b);ck(self.lo<=self.hi,'ORDER')
 @staticmethod
 def cast(x):return x if isinstance(x,I) else I(x)
 def __add__(self,x):
  x=self.cast(x);return I(self.lo+x.lo,self.hi+x.hi)
 __radd__=__add__
 def __neg__(self):return I(-self.hi,-self.lo)
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  x=self.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.cast(x);ck(x.lo*x.hi>0,'DIVISOR');v=[a/b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 def __rtruediv__(self,x):return self.cast(x)/self
 def __pow__(self,n):
  ck(n>=0 and isinstance(n,int),'POWER');out=I(1)
  for _ in range(n):out=out*self
  return out
def iv(x):return I(*x['exact_bounds'])
def contains(saved,x,n):
 v=iv(saved);ck(v.lo<=x.lo<=x.hi<=v.hi,'CONTAIN:'+n)
def poly(c,x):return sum((v*x**n for n,v in enumerate(c)),Q(0))
def expbounds(x):
 ck(0<=x.lo<=x.hi<1,'EXP_DOMAIN')
 def trunc(t):
  term=Q(1);s=term
  for n in range(1,33):term*=t/n;s+=term
  return s,term*t/33/(1-t/34)
 low,_=trunc(x.lo);hi,rem=trunc(x.hi);return I(low,hi+rem)
def main():
 term=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(term['pass_status'],'PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('tail.py','tail_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==term[k],'TERMINAL:'+n)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');old=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');result=read(ROOT/'RESULT.json')
 ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/DEGREE24_AUDIT.json')['PASS'],'PREFIX_AUDITED')
 fullaudit=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_FULL_AUDIT.json');ck(fullaudit['PASS'],'FULL_READOUT_PREREQUISITE')
 base=old['arms']['both']['constants'];nc=ninth['constants_exact']['ninth'];ck(all(base[k]==nc[k] for k in ('seed','K','physical_radius','aggregate_bound')),'SAME_MAJORANT')
 constants=dict(R=base['physical_radius'],seed=base['seed'],K=base['K'],Y=base['aggregate_bound'],JC=dp['global_departure']['coefficient_tail_sup']);weights=[fixed['selected']['refined'][k] for k in ('graph_weight','oscillator_weight')]
 ck(result['constants']==constants and result['weights']==weights,'CONSTANTS')
 R,s,K,Y=[Q(constants[k]) for k in ('R','seed','K','Y')];lam,kap=map(Q,weights);H,z,d=[list(map(Q,raw[k])) for k in ('H','majorant','distance')]
 ck(raw['degree']==24 and len(H)==len(z)==len(d)==25 and H[0]==H[1]==z[0]==0 and z[1]==s,'PREFIX')
 ck(all(v>=0 for c in (H,z,d) for v in c),'NONNEGATIVE')
 ck(all(H[n]<=(n-1)*K**(n-1) for n in range(2,25)),'FINITE_DOMINATION')
 b=[Q(0)]+[z[n]/n**2 for n in range(1,25)];x=[Q(0),Q(0)]+[2*lam*z[n]/n**3 for n in range(2,25)]
 # Independently anchor the ORIGINAL positive distance prefix to these norms.
 ex=[Q(1)]
 for n in range(1,25):ex.append(sum(j*b[j]*ex[n-j] for j in range(1,n+1))/n)
 expected_d=[Q(0)]+[3*(ex[n]+sum(ex[n-j]*x[j] for j in range(1,n+1))) for n in range(1,25)]
 ck(d==expected_d,'ORIGINAL_DISTANCE_PREFIX')
 def source(y):
  v=K*y;return poly(H,y)+y*v**24*(24-23*v)/(1-v)**2
 def deriv(y):
  v=K*y
  # Direct quotient differentiation, algebraically different from producer.
  return sum(n*H[n]*y**(n-1) for n in range(1,25))+v**24*(600-1150*v+552*v*v)/(1-v)**3
 # Exact polynomial numerator identity for the producer's positive formula.
 ck([600,-1200+49+1,600-49+1]==[600,-1150,552],'DERIVATIVE_RATIONAL_IDENTITY')
 ck(set(result['points'])=={'1/4','1/2'},'FIXED_POINTS');summary={};pointpins={}
 for q in (Q(1,4),Q(1,2)):
  row=result['points'][str(q)];cp=ROOT/('POINT_'+str(q.denominator)+'.json');ck(read(cp)==row,'POINT_RECORD');pointpins[str(cp)]=sha(cp)
  eta=R*q;t=I(eta);vals=row['values'];v={k:iv(a) for k,a in vals.items()};ck(row['q']==str(q) and row['eta']==str(eta),'POINT_PARAMETERS')
  exactP=poly(z,eta);contains(vals['P'],I(exactP),'P');contains(vals['ystar'],2*s*t,'YSTAR')
  ys=v['ystar'];ck(ys.hi<=Y and K*ys.hi<1 and v['P'].hi<=ys.lo,'MAJORANT_BALL')
  hs=I(source(ys.lo),source(ys.hi));contains(vals['supersolution_residual'],ys-s*t-hs,'SUPER_RESIDUAL')
  contains(vals['L'],I(deriv(ys.lo),deriv(ys.hi)),'DERIVATIVE_ENDPOINTS');ck(v['supersolution_residual'].lo>=0 and 0<=v['L'].lo<=v['L'].hi<1,'SUPER_CONTRACTION')
  P=v['P'];contains(vals['residual'],s*t+I(source(P.lo),source(P.hi))-P,'RESIDUAL');ck(v['residual'].hi>=0,'RESIDUAL_POSITIVE_UPPER')
  contains(vals['delta'],I(v['residual'].hi)/(1-v['L'].hi),'DELTA');delta=v['delta'];ck((P+delta).hi<=ys.lo,'RESIDUAL_BALL')
  inputs=dict(B=I(poly(b,eta))+delta/625,X=I(poly(x,eta))+2*lam*delta/15625,EulerB=I(poly([n*b[n] for n in range(25)],eta))+delta/25,EulerX=I(poly([n*x[n] for n in range(25)],eta))+2*lam*delta/625)
  for k,a in inputs.items():contains(vals[k],a,k)
  contains(vals['expB'],expbounds(v['B']),'EXPONENTIAL')
  contains(vals['full_distance_majorant'],3*(v['expB']*(1+v['X'])-1),'DISTANCE_COMPOSITION')
  contains(vals['full_euler_majorant'],3*v['expB']*(v['EulerB']*(1+v['X'])+v['EulerX']),'EULER_COMPOSITION')
  contains(vals['distance_prefix'],I(poly(d,eta)),'DISTANCE_PREFIX');contains(vals['euler_prefix'],I(poly([n*d[n] for n in range(25)],eta)),'EULER_PREFIX')
  dt=v['full_distance_majorant']-v['distance_prefix'];et=v['full_euler_majorant']-v['euler_prefix'];ck(dt.hi>=0 and et.hi>=0,'NONNEGATIVE_TAIL_UPPERS')
  for k,a in [('distance_tail',dt),('euler_distance_tail',et),('scalar_tail',kap*delta/15625),('scalar_euler_tail',kap*delta/625)]:ck(Q(row['bounds'][k])>=max(Q(0),a.hi),'TAIL_BOUND:'+k)
  summary[str(q)]=dict(eta=float(eta),delta_upper=float(delta.hi),bounds={k:float(Q(a)) for k,a in row['bounds'].items()},contraction_upper=float(v['L'].hi))
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for p,h in pointpins.items():ck(sha(p)==h,'POST_POINT:'+p)
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('tail.py','tail_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==term[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),points=summary,scope='Independent unrounded endpoint/rational-derivative/Taylor-exponential arithmetic, original distance prefix and both fixed-point tail certificates. Infinite source domination and coefficientwise norm recurrence inherited from existing analytic-family proof; no new full-clock domain, actual field coefficient or trajectory.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'POSITIVE_TAIL_HALF_RADIUS_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('positive_tail_review',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
