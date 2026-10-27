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
 def packet(n,pin):
  root=BASE/n;bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
  for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(root/fn,t[key])
  for group in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[group].items():bind(p,h)
 packet('20261027_FINITE_INVERSE_CLOCK_READOUT_R1','021554e08ab49c101029b120d1614924805cf81fd2d4b140df0cfd48f5509605')
 actualroot=BASE/'20261027_SEVENTH_REAL_SOURCE_ENCLOSURE';bind(actualroot/'TERMINAL.json','107d629a3819ed40acb17a124728bddda08f17e3526f9277ad18bc7202a2b43f');t=read(actualroot/'TERMINAL.json');need(t['pass_status'],'ACTUAL_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(actualroot/fn,t[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(actualroot/'BINDING.json')[group].items():bind(p,h)
 for n,pin in [('FINITE_INVERSE_CLOCK_AUDIT_R1.json','481904b7050ad17cf68d9326cc40a9d075fdbafd10573097f3cc1feeed3fd196'),('SEVENTH_REAL_AUDIT.json','e78e7b081ccb4ef6075f09e20914ad701068eb9a073bea3f3c320d1b1da0c399')]:
  p=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(p,pin);need(read(p)['PASS'],'AUDIT_PASS');bind(p.with_name(n.lower().replace('.json','.py')),read(p)['audit_source_sha256'])
 authority=BASE/'20261027_SEVENTH_COEFFICIENT_CAMPAIGN/AUTHORITY.txt';sources[str(authority)]=sha(authority)
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_FINITE_INVERSE_CLOCK_READOUT_R1/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json')
 actual=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');previous=auth('20261027_ACTUAL_SIXTH_CLOCK_CERTIFICATE/RESULT.json')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['finite_inverse24'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 D={int(k):Q(v) for k,v in prior['distance16'].items()};D24={int(k):Q(v) for k,v in prior['distance24'].items()};E={int(k):Q(v) for k,v in prior['inverse8'].items()};E24={int(k):Q(v) for k,v in prior['inverse24'].items()};C={int(k):Q(v) for k,v in prior['scalar_bounds'].items()};F={int(k):Q(v) for k,v in prior['clock_bounds'].items()};names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def pair(v):return tuple(map(Q,v['exact_bounds']))
 def mul(x,y):
  z=[a*b for a in x for b in y];return min(z),max(z)
 def scale(x,n):return mul(x,(Q(n),Q(n)))
 def ab(x):return max(map(abs,x))
 def packed(x):return list(map(str,x))
 generic=list(map(Q,ninth['distance']));records={};newF=dict(F)
 for n in (7,8,9):
  records[str(n)]={};absnew=[]
  for engine in ('primary','independent'):
   vals=clock['arms'][engine]['values'];ds=[(Q(0),Q(0))]+[pair(vals['d'+str(j)]) for j in range(1,4)]+[(-generic[j],generic[j]) for j in range(4,n+1)]
   ds[4]=tuple(map(Q,fourth['coefficient_intervals'][engine]['d4']));ds[5]=pair(fifth['arms'][engine]['bulk']['d5']);ds[6]=pair(sixth['arms'][engine]['bulk']['d6'])
   ei=[tuple(map(Q,x)) for x in dp['inverse_intervals'][engine]];rate=pair(vals['rate'])
   def evaluate(arr):
    term=scale(arr[n],n-1);parts={'leading':packed(mul(rate,term))}
    for j in range(1,n):
     p=scale(mul(arr[j],ei[n-j]),j);term=(term[0]+p[0],term[1]+p[1]);parts[str(j)]=packed(mul(rate,p))
    return mul(rate,term),parts
   old,oldparts=evaluate(ds);stored=previous['coefficient_records'][str(n)][engine]
   need(packed(old)==stored['new'] and ab(old)==Q(stored['new_abs']),'EXACT_SIXTH_COEFFICIENT:'+str(n)+':'+engine)
   ds[7]=pair(actual['arms'][engine]['bulk']['d7']);new,parts=evaluate(ds);absnew.append(ab(new))
   records[str(n)][engine]=dict(old=packed(old),new=packed(new),old_abs=str(ab(old)),new_abs=str(ab(new)),old_terms=oldparts,new_terms=parts)
  need(F[n]==Q(previous['new_clock_bounds'][str(n)]),'EXACT_INHERITED_BOUND:'+str(n));newF[n]=min(F[n],max(absnew))
 d7=max(ab(pair(actual['arms'][e]['bulk']['d7'])) for e in ('primary','independent'));newD=dict(D);newD24=dict(D24);newD[7]=min(D[7],d7);newD24[7]=min(D24[7],d7)
 def polynomial(coeff):
  N=max(coeff);den=1
  for v in coeff.values():den=den*v.denominator//math.gcd(den,v.denominator)
  ints=[coeff.get(n,Q(0)).numerator*(den//coeff.get(n,Q(0)).denominator) for n in range(N+1)]
  def value(q):
   need(q.numerator==1 and q.denominator>1,'DYADIC_EVALUATION')
   d=q.denominator;num=ints[-1];power=d
   for n in range(N-1,-1,-1):num+=ints[n]*power;power*=d
   return Q(num,den*d**N)
  return value
 def prepare(bounds,eb):
  bd={n:v*R**n for n,v in bounds.items()};be={n:v*R**n for n,v in eb.items()};cross={}
  for n,b in bd.items():
   for m,e in be.items():
    if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*b*e
  return dict(distance=polynomial({n:(n-1)*b for n,b in bd.items() if n>=10}),cross=polynomial(cross),euler=polynomial({n:n*b for n,b in bd.items()}),inverse=polynomial(be))
 prepared={}
 for changed,da,db in [(False,D,D24),(True,newD,newD24)]:
  for bounds,eb in [(da,E),(db,E),(db,E24)]:prepared[changed,max(bounds),max(eb)]=prepare(bounds,eb)
 def at(j,propagate,coeff):
  da,db=(newD,newD24) if propagate else (D,D24);fb=newF if coeff else F
  a=R/Q(2**(j+1));q=a/R;options=[]
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
 arms={};evidence={}
 for name,propagate,coeff in [('baseline',False,False),('distance_only',True,False),('clock_only',False,True),('both',True,True)]:
  for j in range(1,8193):
   rec,ev=at(j,propagate,coeff)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger,lev=at(j-1,propagate,coeff) if j>1 else (None,None);rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);arms[name]=rec;evidence[name]=dict(accepted=ev,next_larger=lev)
 need(arms['baseline']==dict(inherited,gain_exact='1'),'EXACT_PARENT_REPLAY');need(all(Q(a['gain_exact'])>=1 for a in arms.values()),'NO_LOSS')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,arms=arms,tail_evidence=evidence,distance16=ss(D),distance24=ss(D24),inverse8=ss(E),inverse24=ss(E24),clock_bounds=ss(F),new_clock_bounds=ss(newF),new_distance16=ss(newD),new_distance24=ss(newD24),coefficient_records=records,scalar_bounds=ss(C),seconds=time.monotonic()-start,scope='Actual d7 propagated into retained F7..F9 and distance tails in a factorial. Same full gates, inverse bounds, radius and physical family; no new trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=result['seconds'],arms={n:dict(eta=float(Q(a['constants']['clock_eta'])),gain=float(Q(a['gain_exact'])),costs={k:float(Q(v)) for k,v in a['costs'].items()},next_costs={k:float(Q(v)) for k,v in a['next_larger']['costs'].items()},tail_parts={k:float(Q(v)) for k,v in evidence[n]['accepted']['normalized_new'].items()},next_tail_parts={k:float(Q(v)) for k,v in evidence[n]['next_larger']['normalized_new'].items()}) for n,a in arms.items()})),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('inverse_clock_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('INVERSE_CLOCK_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
