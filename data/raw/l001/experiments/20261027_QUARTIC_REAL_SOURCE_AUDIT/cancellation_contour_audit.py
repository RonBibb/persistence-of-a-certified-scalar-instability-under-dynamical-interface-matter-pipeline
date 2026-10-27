"""Independent cancellation, inverse-lapse and scalar remainder audit."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_CANCELLATION_CONTOUR_CERTIFICATE';CUTOFF=1793101111;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def ss(d):return {k:str(v) for k,v in d.items()}
def plus(a,b):return a[0]+b[0],a[1]+b[1]
def times(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def scale(a,k):return times(a,(Q(k),Q(k)))
def main():
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'TERMINAL:'+n)
 bound={}
 for g in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[g].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_FINITE_CONTOUR_CERTIFICATE_R1/RESULT.json');sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json');seventh=auth('20261027_SEVENTH_CLOCK_ENCLOSURE/RESULT.json');eighth=auth('20261027_EIGHTH_CLOCK_ENCLOSURE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');result=read(ROOT/'RESULT.json')
 base={k:Q(v) for k,v in prior['arms']['finite_extended']['constants'].items()};B={int(n):Q(v) for n,v in prior['distance_bounds'].items()};F={int(n):Q(v) for n,v in auth('20261027_CONTOUR_DISTANCE_CERTIFICATE/RESULT.json')['clock_bounds'].items()}
 ck(result['distance_bounds']=={str(n):str(v) for n,v in B.items()},'DISTANCE_INPUTS')
 inverse={}
 for engine in ('primary','independent'):
  logs=[(Q(0),Q(0)),(Q(1),Q(1))]+[tuple(map(Q,sixth['sixth_coefficients'][engine][k])) for k in ('L2','L3','L4','L5')]+[tuple(map(Q,doc['coefficients'][engine][key])) for doc,key in [(seventh,'L6'),(eighth,'L7'),(ninth,'L8')]]
  inverse[engine]=[(Q(1),Q(1))]
  for n in range(1,9):
   total=(Q(0),Q(0))
   for k in range(1,n+1):total=plus(total,scale(times(logs[k],inverse[engine][n-k]),-k))
   inverse[engine].append(scale(total,Q(1,n)))
  ck(inverse[engine][1]==(-1,-1),'NORMALIZATION')
 ck(result['inverse_intervals']=={e:[list(map(str,x)) for x in v] for e,v in inverse.items()},'ALL_INVERSE_COEFFICIENTS')
 eb={n:max(abs(x) for v in inverse.values() for x in v[n]) for n in range(1,9)};ck(result['inverse_abs']=={str(n):str(v) for n,v in eb.items()},'INVERSE_ABS')
 kap=Q(fixed['selected']['refined']['oscillator_weight']);cb={2:Q(sixth['scalar_abs']['chi2']),3:Q(sixth['scalar_abs']['chi3'])};cb.update({n:kap*Q(ninth['majorant'][n])/n**3 for n in range(4,10)});ck(result['scalar_bounds']=={str(n):str(v) for n,v in cb.items()},'SCALAR_INPUTS')
 R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')]
 old=list(map(Q,['1/8','1/4','1/3','2/5','1/2','2/3','3/4','4/5','9/10','10/11','15/16']));extended=list(map(Q,['1/128','1/64','1/32','1/16']))+old;records={}
 for theta in extended:
  x=theta*R;V=sum(B[n]*x**n for n in range(1,10))+MD*theta**10/(1-theta);W=sum(n*B[n]*x**n for n in range(1,10))+MD*(10*theta**10-9*theta**11)/(1-theta)**2
  A=sum((n-1)*B[n]*x**n for n in range(2,10))+MD*(9*theta**10-8*theta**11)/(1-theta)**2
  E=sum(eb[n]*x**n for n in range(1,9))+128*theta**9/(1-theta)
  generic=MD*(1+128*theta/(1-theta))/32;finite=(128*W+V)/32;cancel=(A+W*E)/32
  records[str(theta)]=dict(value=str(V),euler_derivative=str(W),generic_sup=str(generic),finite_sup=str(finite),selected_sup=str(min(generic,finite)),cancelled_distance=str(A),inverse_departure=str(E),cancel_sup=str(cancel),best_sup=str(min(generic,finite,cancel)))
 ck(records==result['contour_records'],'ALL_FIFTEEN_CONTOUR_RECORDS')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def evaluate(j,cancel,small,scalar):
  eta=R/Q(2**(j+1));q=eta/R;choices=[]
  for theta in extended if small else old:
   z=eta/(theta*R)
   if z<1:
    sup=Q(records[str(theta)]['best_sup' if cancel else 'selected_sup']);choices.append((sup*z**10/(1-z),theta,sup))
  ck(bool(choices),'VALID_CONTOUR');tail,theta,sup=min(choices,key=lambda x:x[0]);terms={names[n]:b*eta**n for n,b in F.items()};costs={k:v/(10*eta**2) for k,v in terms.items()};costs['unknown_tail']=tail/(10*eta**2)
  olddt=MD*q*q/(1-q);newdt=sum(B[n]*eta**n for n in range(2,10))+MD*q**10/(1-q);dt=min(olddt,newdt)
  st=cb[2]*eta**2+cb[3]*eta**3+Y*q**4/(1-q);sd=2*cb[2]*eta**2+3*cb[3]*eta**3+Y*q**4*(4-3*q)/(1-q)**2
  if scalar:
   st=min(st,sum(cb[n]*eta**n for n in range(2,10))+Y*q**10/(1-q));sd=min(sd,sum(n*cb[n]*eta**n for n in range(2,10))+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=sd/(eta/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  constants=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=eta/40000);constants.update({'known_'+k:v for k,v in terms.items()})
  return dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(olddt),retained=str(newdt)))
 summaries={}
 for name,cancel,small,scalar in [('baseline',False,False,False),('cancellation_same',True,False,False),('cancellation_small',True,True,False),('scalar_small',True,True,True)]:
  for j in range(1,8193):
   rec=evaluate(j,cancel,small,scalar)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger=evaluate(j-1,cancel,small,scalar) if j>1 else None
  if larger:ck(not all(larger['gates'].values()),'FIRST_DYADIC')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);ck(rec==result['arms'][name],'FULL_ARM:'+name)
  if name=='baseline':ck(rec==prior['arms']['finite_extended'],'BASELINE_EXACT')
  summaries[name]=dict(eta=float(Q(rec['constants']['clock_eta'])),gain=float(Q(rec['gain_exact'])),theta=rec['theta'],ratios={k:float(Q(v)) for k,v in rec['ratios'].items()},costs={k:float(Q(v)) for k,v in rec['costs'].items()},next_ratios={k:float(Q(v)) for k,v in larger['ratios'].items()} if larger else None,next_gates=larger['gates'] if larger else None)
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=summaries,scope='Independent inverse-lapse interval recurrence, scalar coefficient payment, cancellation suprema and complete four-arm certificate/binding replay. Same-family analytic, physical coefficient and ODE premises inherited; no new physical evolution.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'CANCELLATION_CONTOUR_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');p=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('cancel_review_lease',p);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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
