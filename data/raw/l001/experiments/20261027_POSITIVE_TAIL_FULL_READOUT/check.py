"""Two-point full certificate using audited positive series tails."""
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

 tr=BASE/'20261027_POSITIVE_TAIL_FEASIBILITY_R1';bind(tr/'TERMINAL.json','dd5bf303a54b2a7e1434238cdc84e4f124c3fa09163bd8c15a97a2f11c73ab38');tt=read(tr/'TERMINAL.json');need(tt['pass_status'],'TAIL_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('tail.py','tail_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(tr/fn,tt[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(tr/'BINDING.json')[group].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_AUDIT.json';bind(ap,'5f91cea76ab3e8985bb22d2dd84bc0be34a5ddcccc4abb8d726b0797d998f986');ar=read(ap);need(ar['PASS'] and ar['producer_terminal']==sha(tr/'TERMINAL.json'),'TAIL_AUDIT')
 bind(ap.with_name('positive_tail_audit.py'),ar['audit_source_sha256'])
 tails=read(tr/'RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json')

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

 rows={}
 for q in (Q(1,16),Q(1,8)):
  old,oe=at(q);expected=inherited if q==Q(1,16) else inherited['next_larger']
  expected={k:v for k,v in expected.items() if k not in ('selected_dyadic','gain_exact','next_larger')}
  need(old==expected,'EXACT_PARENT_REPLAY')
  a=R*q;row=tails['points'][str(q)];need(Q(row['eta'])==a,'TAIL_SAME_POINT')
  tb={k:Q(v) for k,v in row['bounds'].items()};pp=prepared[True,24,24]
  jt=JC*q**25/(1-q);efull=pp['inverse'](q)+jt
  parts=dict(finite_distance=pp['distance'](q),finite_cross=pp['cross'](q),
    unknown_distance=tb['euler_distance_tail']*(1+efull),
    unknown_lapse=pp['euler'](q)*jt)
  candidate=sum(parts.values())/32;tail=min(Q(old['constants']['clock_tail']),candidate)
  dist_candidate=sum(v*a**n for n,v in D24.items() if n>=2)+tb['distance_tail']
  dist=min(Q(old['constants']['distance_tail']),dist_candidate)
  z=list(map(Q,raw['majorant']));kap=Q(tails['weights'][1])
  scalar={n:min(C[n],kap*z[n]/n**3) if n in C else kap*z[n]/n**3 for n in range(2,25)}
  st_candidate=sum(v*a**n for n,v in scalar.items())+tb['scalar_tail']
  sd_candidate=sum(n*v*a**n for n,v in scalar.items())+tb['scalar_euler_tail']
  st=min(Q(old['constants']['scalar_tail']),st_candidate);sd=min(Q(old['constants']['scalar_derivative_tail']),sd_candidate)
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=tail/(10*a*a)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000))
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  need(all(v<=Q(old['ratios'][k]) for k,v in ratios.items()),'NO_WORSENING')
  rec=dict(q=str(q),eta=str(a),old=old,old_evidence=oe,costs=ss(costs),ratios=ss(ratios),gates=gates,
   scalar_coefficients=ss(scalar),tail_parts=ss(parts),normalized_parts=ss({k:v/(320*a*a) for k,v in parts.items()}),
   candidates=ss(dict(clock=candidate,distance=dist_candidate,scalar=st_candidate,scalar_derivative=sd_candidate)),
   selected=ss(dict(clock=tail,distance=dist,scalar=st,scalar_derivative=sd)))
  rows[str(q)]=rec;put('POINT_'+str(q.denominator)+'.json',rec)
  print(json.dumps(dict(q=str(q),ratios={k:float(v) for k,v in ratios.items()},gates=gates)),flush=True)
 need(all(rows['1/16']['gates'].values()),'RETAIN_ENTRY_CERTIFICATE')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime and time.time()<CUTOFF,'RUNTIME_AND_WINDOW')
 result=dict(pass_status=True,points=rows,seconds=time.monotonic()-start,scope='Two fixed-amplitude complete-certificate evaluations using audited positive unresolved tails. Technical pass does not assert either point passes all scientific gates. Same analytic family, radius, actual coefficients and five gates; no physical threshold or trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'])),flush=True)

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
