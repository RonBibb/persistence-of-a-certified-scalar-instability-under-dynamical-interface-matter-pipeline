"""Complete clock readout with separately qualified distance24 bound."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793101111
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
def ss(d):return {k:str(v) for k,v in d.items()}
def main(lease):
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def packet(n,pin):
  root=BASE/n;bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
  for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(root/fn,t[key])
  for group in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[group].items():bind(p,h)
 packet('20261027_ACTUAL_SIXTH_CLOCK_CERTIFICATE','4802a78f0f6a04193792d4f9d58d3f8e7f27c6813cd6c4772090ee84551ee51b')
 packet('20261027_DEGREE24_DISTANCE_MAJORANT','313f7292e1ba87e35d264c14f9af74c46719596ca0c77e7e7100f6ca84de7c4b')
 for n,pin in [('ACTUAL_SIXTH_CLOCK_AUDIT.json','03a2a326000d28327bc26b4f7dc645860bd632a444b085c5a6d6ef6d48b30e17'),('DEGREE24_AUDIT.json','13f7bda89664924f9b82e01711ee3976708c5208e05dbef4ea1f1c9b777e8ff0')]:
  p=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(p,pin);need(read(p)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_ACTUAL_SIXTH_CLOCK_CERTIFICATE/RESULT.json');high=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['both'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 D={int(k):Q(v) for k,v in prior['new_distance_bounds'].items()};D24=dict(D);D24.update({n:min(Q(high['distance'][n]),MD/R**n) for n in range(17,25)})
 E={int(k):Q(v) for k,v in dp['inverse_abs'].items()};C={int(k):Q(v) for k,v in dp['scalar_bounds'].items()};F={int(k):Q(v) for k,v in prior['new_clock_bounds'].items()};names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 need(high['degree']==24 and all(v>=0 for v in D24.values()),'HIGH_COEFFICIENTS')
 def at(j,extended):
  a=R/Q(2**(j+1));q=a/R;options=[]
  for th,row in dp['contour_records'].items():
   theta=Q(th);z=a/(theta*R)
   if z<1:
    sup=Q(row['both']);options.append((sup*z**10/(1-z),theta,sup))
  ct,theta,sup=min(options,key=lambda x:x[0]);jt=JC*q**9/(1-q);ed=sum(v*a**m for m,v in E.items())+jt
  def direct(bounds,N):
   wd=sum(n*v*a**n for n,v in bounds.items())
   return dict(finite_distance=sum((n-1)*bounds[n]*a**n for n in range(10,N+1)),finite_cross=sum(n*b*e*a**(n+m) for n,b in bounds.items() for m,e in E.items() if n+m>=10),distance_tail=MD*q**(N+1)*(N-(N-1)*q)/(1-q)**2,unknown_distance_product=MD*q**(N+1)*(N+1-N*q)/(1-q)**2*ed,unknown_lapse_product=wd*jt)
  p16,p24=direct(D,16),direct(D24,24);t16,t24=sum(p16.values())/32,sum(p24.values())/32;tail=min(ct,t16,t24) if extended else min(ct,t16)
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=tail/(10*a*a)
  d0=MD*q*q/(1-q);d9=sum(D[n]*a**n for n in range(2,10))+MD*q**10/(1-q);d16=sum(D[n]*a**n for n in range(2,17))+MD*q**17/(1-q);d24=sum(D24[n]*a**n for n in range(2,25))+MD*q**25/(1-q);dist=min(d0,d9,d16,d24) if extended else min(d0,d9,d16)
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(v*a**n for n,v in C.items())+Y*q**10/(1-q));sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*v*a**n for n,v in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dist,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+names[n]:v*a**n for n,v in F.items()})
  candidates=dict(old=str(d0),retained=str(d9),retained16=str(d16))
  if extended:candidates['retained24']=str(d24)
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=candidates)
  ev=dict(contour=str(ct),direct16=str(t16),direct24=str(t24),parts16=ss(p16),parts24=ss(p24),normalized16=ss({k:v/(320*a*a) for k,v in p16.items()}),normalized24=ss({k:v/(320*a*a) for k,v in p24.items()}),selected=str(tail),theta_describes_fallback=True)
  return rec,ev
 arms={};evidence={}
 for name,extended in [('baseline',False),('degree24',True)]:
  for j in range(1,8193):
   rec,ev=at(j,extended)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger,lev=at(j-1,extended) if j>1 else (None,None);rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);arms[name]=rec;evidence[name]=dict(accepted=ev,next_larger=lev)
 need(arms['baseline']==dict(inherited,gain_exact='1'),'EXACT_PARENT_REPLAY');need(Q(arms['degree24']['gain_exact'])>=1,'NO_LOSS')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,arms=arms,tail_evidence=evidence,distance16=ss(D),distance24=ss(D24),clock_bounds=ss(F),inverse_bounds=ss(E),scalar_bounds=ss(C),seconds=time.monotonic()-start,scope='Same complete sufficient certificate with distance tail24; no changed physical solution or global analytic radius.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=result['seconds'],arms={n:dict(eta=float(Q(a['constants']['clock_eta'])),gain=float(Q(a['gain_exact'])),costs={k:float(Q(v)) for k,v in a['costs'].items()},next_costs={k:float(Q(v)) for k,v in a['next_larger']['costs'].items()},tail_parts={k:float(Q(v)) for k,v in evidence[n]['accepted']['normalized24'].items()}) for n,a in arms.items()})),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('d24_readout_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('D24_READOUT_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
