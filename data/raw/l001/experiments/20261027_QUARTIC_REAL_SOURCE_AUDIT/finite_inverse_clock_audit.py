"""Independent direct high-product tail and interval coefficient audit."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_FINITE_INVERSE_CLOCK_READOUT';CUTOFF=1793101111;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def ss(d):return {str(k):str(v) for k,v in d.items()}
def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def scale(a,k):return mul(a,(Q(k),Q(k)))
def packed(a):return list(map(str,a))
def pair(a):return tuple(map(Q,a))
def interval(v):return pair(v['exact_bounds'])
def main():
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'TERMINAL:'+n)
 bound={}
 for g in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[g].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_DISTANCE24_CLOCK_READOUT/RESULT.json');inv=auth('20261027_FINITE_INVERSE_LAPSE24/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');result=read(ROOT/'RESULT.json')
 inherited=prior['arms']['degree24'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 D={int(n):Q(v) for n,v in prior['distance16'].items()};D24={int(n):Q(v) for n,v in prior['distance24'].items()};F={int(n):Q(v) for n,v in prior['clock_bounds'].items()};E={int(n):Q(v) for n,v in prior['inverse_bounds'].items()};E24={int(n):Q(v) for n,v in inv['inverse_abs'].items()};C={int(n):Q(v) for n,v in prior['scalar_bounds'].items()}
 ck(inv['degree']==24 and set(D)==set(range(1,17)) and set(D24)==set(E24)==set(range(1,25)),'COVERAGE')
 ck({n:E24[n] for n in range(1,9)}==E and Q(inv['constants']['radius'])==R and Q(inv['constants']['tail_sup'])==JC,'UNCHANGED_PREFIX_DOMAIN')
 for key,val in [('distance16',D),('distance24',D24),('clock_bounds',F),('inverse8',E),('inverse24',E24),('scalar_bounds',C)]:ck(result[key]==ss(val),'BOUND_SELECTION:'+key)
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def evaluate(j,extended):
  a=R/Q(2**(j+1));q=a/R;options=[]
  for th,row in dp['contour_records'].items():
   theta=Q(th);z=a/(theta*R)
   if z<1:options.append((Q(row['both'])*z**10/(1-z),theta,Q(row['both'])))
  ct,theta,sup=min(options,key=lambda x:x[0])
  def direct(bounds,eb):
   N=max(bounds);M=max(eb);RJ=JC*q**(M+1)/(1-q);Efull=sum(v*a**n for n,v in eb.items())+RJ;cross={}
   for n,b in bounds.items():
    for m,e in eb.items():
     if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*b*e
   return dict(finite_distance=sum((n-1)*bounds[n]*a**n for n in range(10,N+1)),finite_cross=sum(v*a**n for n,v in cross.items()),distance_tail=MD*(N*q**(N+1)-(N-1)*q**(N+2))/(1-q)**2,unknown_distance_product=MD*((N+1)*q**(N+1)-N*q**(N+2))/(1-q)**2*Efull,unknown_lapse_product=sum(n*b*a**n for n,b in bounds.items())*RJ)
  p16,p24,pnew=direct(D,E),direct(D24,E),direct(D24,E24);t16,t24,tnew=[sum(p.values())/32 for p in (p16,p24,pnew)];tail=min(ct,t16,t24,tnew) if extended else min(ct,t16,t24)
  known={names[n]:v*a**n for n,v in F.items()};costs={k:v/(10*a*a) for k,v in known.items()};costs['unknown_tail']=tail/(10*a*a)
  ds={0:MD*q*q/(1-q),9:sum(D[n]*a**n for n in range(2,10))+MD*q**10/(1-q),16:sum(D[n]*a**n for n in range(2,17))+MD*q**17/(1-q),24:sum(D24[n]*a**n for n in range(2,25))+MD*q**25/(1-q)}
  dist=min(ds.values())
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(v*a**n for n,v in C.items())+Y*q**10/(1-q))
  sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*v*a**n for n,v in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dist,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+k:v for k,v in known.items()})
  candidates=dict(old=str(ds[0]),retained=str(ds[9]),retained16=str(ds[16]))
  candidates['retained24']=str(ds[24])
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=candidates)
  ev=dict(contour=str(ct),direct16=str(t16),direct24=str(t24),finite_inverse24=str(tnew),normalized_old=ss({k:v/(320*a*a) for k,v in p24.items()}),normalized_new=ss({k:v/(320*a*a) for k,v in pnew.items()}),selected=str(tail),theta_describes_fallback=True)
  return rec,ev
 summaries={}
 for name,extended in [('baseline',False),('finite_inverse24',True)]:
  for j in range(1,8193):
   rec,ev=evaluate(j,extended)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger,lev=evaluate(j-1,extended) if j>1 else (None,None)
  if larger:ck(not all(larger['gates'].values()),'FIRST_DYADIC')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger)
  ck(rec==result['arms'][name],'FULL_CERTIFICATE:'+name);ck(result['tail_evidence'][name]==dict(accepted=ev,next_larger=lev),'FULL_PARTITION:'+name)
  if not extended:ck(rec==dict(inherited,gain_exact='1'),'PARENT_REPLAY')
  summaries[name]=dict(eta=float(Q(rec['constants']['clock_eta'])),gain=float(Q(rec['gain_exact'])),ratios={k:float(Q(v)) for k,v in rec['ratios'].items()},costs={k:float(Q(v)) for k,v in rec['costs'].items()},next_ratios={k:float(Q(v)) for k,v in larger['ratios'].items()} if larger else None,next_costs={k:float(Q(v)) for k,v in larger['costs'].items()} if larger else None,tail_parts={k:float(Q(v)) for k,v in ev['normalized_new'].items()},next_tail_parts={k:float(Q(v)) for k,v in lev['normalized_new'].items()} if lev else None)
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=summaries,scope='Independent exact inverse-lapse coefficient selection, generalized two-polynomial convolution partition and complete paired first-dyadic certificates. Positive-distance, clock coefficients and analytic-family premises inherited; no new source solve or trajectory.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'FINITE_INVERSE_CLOCK_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');p=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('direct_product_review',p);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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


