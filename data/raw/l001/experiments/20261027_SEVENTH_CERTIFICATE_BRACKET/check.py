"""Actual seventh coefficient propagation under latest finite-inverse certificate."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
import math,hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793108564
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def need(v,n):
 if not v:raise AssertionError(n)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
 p=ROOT/n;t=ROOT/(n+'.tmp')
 with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(t,0o444);os.link(t,p);t.unlink();fd=os.open(ROOT,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def ss(d):return {str(k):str(v) for k,v in d.items()}
def main(lease):
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE';bind(parent/'TERMINAL.json','7a52079f0b25cb3866af673880a12083aeb7aa98cb0be378fed13d47e8d43b80');t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/fn,t[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/ACTUAL_SEVENTH_CLOCK_AUDIT.json';bind(ap,'2ea421a29c59c6e4371857531b5e9675b51e9116b6e9863add64c1a7849b8337');ar=read(ap);need(ar['PASS'] and ar['producer_terminal']==sha(parent/'TERMINAL.json'),'AUDIT_MATCH')
 bind(ap.with_name('actual_seventh_clock_audit.py'),ar['audit_source_sha256'])
 authority=BASE/'20261027_SEVENTH_COEFFICIENT_CAMPAIGN/AUTHORITY.txt';sources[str(authority)]=sha(authority)
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=read(parent/'RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['both'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 newD={int(k):Q(v) for k,v in prior['new_distance16'].items()};newD24={int(k):Q(v) for k,v in prior['new_distance24'].items()};D,D24=newD,newD24
 E={int(k):Q(v) for k,v in prior['inverse8'].items()};E24={int(k):Q(v) for k,v in prior['inverse24'].items()};C={int(k):Q(v) for k,v in prior['scalar_bounds'].items()};newF={int(k):Q(v) for k,v in prior['new_clock_bounds'].items()};F=newF;names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 need(all(x>=0 for bounds in (D,D24,E,E24,C,F) for x in bounds.values()),'NONNEGATIVE_CERTIFICATE_BOUNDS')
 need(0<R<Q(1,512) and R<Q(25,3840),'OPENING_DOWNWARD_ON_DOMAIN')
 def polynomial(coeff):
  N=max(coeff);den=1
  for v in coeff.values():den=den*v.denominator//math.gcd(den,v.denominator)
  ints=[coeff.get(n,Q(0)).numerator*(den//coeff.get(n,Q(0)).denominator) for n in range(N+1)]
  def value(q):
   need(0<q<1,'RATIONAL_EVALUATION_DOMAIN')
   p,d=q.numerator,q.denominator;num=ints[-1];power=d
   for n in range(N-1,-1,-1):num=num*p+ints[n]*power;power*=d
   return Q(num,den*d**N)
  return value
 def prepare(bounds,eb):
  bd={n:v*R**n for n,v in bounds.items()};be={n:v*R**n for n,v in eb.items()};cross={}
  for n,b in bd.items():
   for m,e in be.items():
    if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*b*e
  return dict(distance=polynomial({n:(n-1)*b for n,b in bd.items() if n>=10}),cross=polynomial(cross),euler=polynomial({n:n*b for n,b in bd.items()}),inverse=polynomial(be))
 prepared={}
 for changed,da,db in [(True,newD,newD24)]:
  for bounds,eb in [(da,E),(db,E),(db,E24)]:prepared[changed,max(bounds),max(eb)]=prepare(bounds,eb)
 def at(q):
  propagate=coeff=True
  da,db=(newD,newD24) if propagate else (D,D24);fb=newF if coeff else F
  a=R*q;options=[]
  for th,row in dp['contour_records'].items():
   theta=Q(th);z=a/(theta*R)
   if z<1:options.append((Q(row['both'])*z**10/(1-z),theta,Q(row['both'])))
  ct,theta,sup=min(options,key=lambda x:x[0])
  def direct(bounds,eb):
   N=max(bounds);M=max(eb);polys=prepared[propagate,N,M];jt=JC*q**(M+1)/(1-q);ed=polys['inverse'](q)+jt;wd=polys['euler'](q)
   return dict(finite_distance=polys['distance'](q),finite_cross=polys['cross'](q),distance_tail=MD*q**(N+1)*(N-(N-1)*q)/(1-q)**2,unknown_distance_product=MD*q**(N+1)*(N+1-N*q)/(1-q)**2*ed,unknown_lapse_product=wd*jt)
  p16,p24,pnew=direct(da,E),direct(db,E),direct(db,E24);t16,t24,tnew=[sum(p.values())/32 for p in (p16,p24,pnew)];old=min(ct,t16,t24);tail=min(old,tnew)
  costs={names[n]:v*a**n/(10*a*a) for n,v in fb.items()};costs['unknown_tail']=tail/(10*a*a)
  d0=MD*q*q/(1-q);d9=sum(da[n]*a**n for n in range(2,10))+MD*q**10/(1-q);d16=sum(da[n]*a**n for n in range(2,17))+MD*q**17/(1-q);d24=sum(db[n]*a**n for n in range(2,25))+MD*q**25/(1-q);dist=min(d0,d9,d16,d24)
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(v*a**n for n,v in C.items())+Y*q**10/(1-q));sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*v*a**n for n,v in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dist,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+names[n]:v*a**n for n,v in fb.items()})
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(d0),retained=str(d9),retained16=str(d16),retained24=str(d24)))
  ev=dict(contour=str(ct),direct16=str(t16),direct24=str(t24),finite_inverse24=str(tnew),normalized_old=ss({k:v/(320*a*a) for k,v in p24.items()}),normalized_new=ss({k:v/(320*a*a) for k,v in pnew.items()}),selected=str(tail),theta_describes_fallback=True)
  return rec,ev

 controls=[]
 for coeff in ({0:Q(2,3),1:-Q(1,7),3:Q(5,11)},{1:Q(7,13),4:Q(3,17),8:Q(5,19)}):
  fn=polynomial(coeff)
  for q in (Q(1,16),Q(3,32),Q(5,64)):
   expected=sum(v*q**n for n,v in coeff.items());need(fn(q)==expected,'GENERAL_RATIONAL_CONTROL');controls.append(dict(q=str(q),coefficients=ss(coeff),value=str(expected)))
 lo=Q(inherited['constants']['clock_eta'])/R;hi=Q(inherited['next_larger']['constants']['clock_eta'])/R
 need(0<lo<hi<1 and hi==2*lo,'ORIGINAL_DYADIC_BRACKET')
 low,le=at(lo);high,he=at(hi)
 parent_low={k:v for k,v in inherited.items() if k not in ('selected_dyadic','gain_exact','next_larger')}
 need(low==parent_low and high==inherited['next_larger'],'EXACT_ENDPOINT_REPLAY')
 need(le==prior['tail_evidence']['both']['accepted'] and he==prior['tail_evidence']['both']['next_larger'],'EXACT_ENDPOINT_EVIDENCE')
 need(all(low['gates'].values()) and not all(high['gates'].values()),'BRACKET_GATES')
 origin=(lo,hi);rows=[];previous=sha(ROOT/'BINDING.json')
 for step in range(1,17):
  q=(lo+hi)/2;rec,ev=at(q);passed=all(rec['gates'].values())
  row=dict(step=step,q=str(q),eta=str(R*q),passed=passed,record=rec,evidence=ev,predecessor_sha256=previous)
  name='CHECKPOINT_'+str(step).zfill(2)+'.json';put(name,row);previous=sha(ROOT/name);rows.append(row)
  if passed:lo,low,le=q,rec,ev
  else:hi,high,he=q,rec,ev
  print(json.dumps(dict(step=step,passed=passed,eta=float(R*q))),flush=True)
 need(hi-lo==(origin[1]-origin[0])/2**16 and all(low['gates'].values()) and not all(high['gates'].values()),'FINAL_BRACKET')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime and time.time()<CUTOFF,'RUNTIME_AND_WINDOW')
 result=dict(pass_status=True,classification='SAME_CERTIFICATE_RATIONAL_BRACKET',iterations=16,controls=controls,original_q=list(map(str,origin)),lower_q=str(lo),upper_q=str(hi),width_q=str(hi-lo),lower=low,upper=high,lower_evidence=le,upper_evidence=he,checkpoints=rows,last_checkpoint_sha256=previous,gain_over_dyadic=str(lo/origin[0]),seconds=time.monotonic()-start,scope='Fixed unchanged sufficient-certificate boundary bracket. Not a physical threshold, actual convergence radius, optimized proof domain or new field result.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'],eta_lower=float(R*lo),eta_upper=float(R*hi),gain=float(lo/origin[0]),ratios_lower={k:float(Q(v)) for k,v in low['ratios'].items()},ratios_upper={k:float(Q(v)) for k,v in high['ratios'].items()})),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('seventh_bracket_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BRACKET_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
