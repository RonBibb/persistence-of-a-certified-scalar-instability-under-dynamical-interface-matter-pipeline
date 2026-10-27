"""Retained-distance bound for the full clock supremum on fixed contours."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793101111
ORIGINAL=tuple(map(Q,('1/2','2/3','3/4','4/5','9/10','10/11','15/16')))
PREVIOUS=tuple(map(Q,('1/8','1/4','1/3','2/5')))+ORIGINAL
EXTENDED=tuple(map(Q,('1/128','1/64','1/32','1/16')))+PREVIOUS
# Parent pins populated only after its independent audit, before launch.
PARENT_PIN='ad39518b3c879f18124b23a573110cc272bd90e09beb254b448790337ee17348'
AUDIT_PIN='9d3bcc285ed22fb11b56b32d58ed02dfc956bd372999e5f58974bd3878fa86ab'
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
def ss(d):return {k:str(v) for k,v in d.items()}
def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_FINITE_CONTOUR_CERTIFICATE_R1';bind(parent/'TERMINAL.json',PARENT_PIN)
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 audit=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/FINITE_CONTOUR_AUDIT_R1.json';bind(audit,AUDIT_PIN);need(read(audit)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=read(parent/'RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json')
 len(str(10**20000)) # preload inherited authenticated _pylong before runtime freeze
 runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['finite_extended'];base={k:Q(v) for k,v in inherited['constants'].items()}
 B={int(n):Q(v) for n,v in prior['distance_bounds'].items()};B[1]=max(abs(Q(x)) for e in ('primary','independent') for x in clock['arms'][e]['values']['d1']['exact_bounds'])
 F={int(n):Q(v) for n,v in auth('20261027_CONTOUR_DISTANCE_CERTIFICATE/RESULT.json')['clock_bounds'].items()};need(all(v>=0 for v in B.values()),'DISTANCE_POSITIVE')
 R=base['physical_radius'];MD=base['observable_sup'];Y=base['aggregate_bound'];C2=Q(sixth['scalar_abs']['chi2']);C3=Q(sixth['scalar_abs']['chi3'])
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 seventh=auth('20261027_SEVENTH_CLOCK_ENCLOSURE/RESULT.json');eighth=auth('20261027_EIGHTH_CLOCK_ENCLOSURE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json')
 def add(a,b):return (a[0]+b[0],a[1]+b[1])
 def mul(a,b):
  z=[x*y for x in a for y in b];return (min(z),max(z))
 def scale(a,k):return mul(a,(Q(k),Q(k)))
 inverse={}
 for engine in ('primary','independent'):
  logs=[(Q(0),Q(0)),(Q(1),Q(1))]+[tuple(map(Q,sixth['sixth_coefficients'][engine][k])) for k in ('L2','L3','L4','L5')]+[tuple(map(Q,seventh['coefficients'][engine]['L6'])),tuple(map(Q,eighth['coefficients'][engine]['L7'])),tuple(map(Q,ninth['coefficients'][engine]['L8']))]
  ee=[(Q(1),Q(1))]
  for n in range(1,9):
   term=(Q(0),Q(0))
   for k in range(1,n+1):term=add(term,scale(mul(logs[k],ee[n-k]),k))
   ee.append(scale(term,-Q(1,n)))
  need(ee[1]==(-1,-1),'EXACT_LINEAR_INVERSE');inverse[engine]=ee
 Eb={n:max(abs(x) for ee in inverse.values() for x in ee[n]) for n in range(1,9)}
 kap=Q(fixed['selected']['refined']['oscillator_weight']);scalar_bounds={2:C2,3:C3};scalar_bounds.update({n:kap*Q(ninth['majorant'][n])/n**3 for n in range(4,10)})
 need(all(v>=0 for v in scalar_bounds.values()),'SCALAR_POSITIVE')
 contour_records={}
 for theta in EXTENDED:
  x=theta*R;v=sum(b*x**n for n,b in B.items())+MD*theta**10/(1-theta)
  w=sum(n*b*x**n for n,b in B.items())+MD*theta**10*(10-9*theta)/(1-theta)**2
  generic=MD*(1+128*theta/(1-theta))/32;finite=(128*w+v)/32
  aa=sum((n-1)*b*x**n for n,b in B.items() if n>=2)+MD*theta**10*(9-8*theta)/(1-theta)**2
  ee=sum(b*x**n for n,b in Eb.items())+128*theta**9/(1-theta);cancel=(aa+w*ee)/32
  contour_records[str(theta)]=dict(value=str(v),euler_derivative=str(w),generic_sup=str(generic),finite_sup=str(finite),selected_sup=str(min(generic,finite)),cancelled_distance=str(aa),inverse_departure=str(ee),cancel_sup=str(cancel),best_sup=str(min(generic,finite,cancel)))
 def at(j,cancel,small,scalar):
  eta=R/Q(2**(j+1));qd=eta/R;options=[]
  for theta in EXTENDED if small else PREVIOUS:
   z=eta/(theta*R)
   if z<1:
    sup=Q(contour_records[str(theta)]['best_sup' if cancel else 'selected_sup']);options.append((sup*z**10/(1-z),theta,sup))
  tail,theta,sup=min(options,key=lambda v:v[0]);terms={names[n]:v*eta**n for n,v in F.items()};costs={k:v/(10*eta**2) for k,v in terms.items()};costs['unknown_tail']=tail/(10*eta**2)
  olddt=MD*qd**2/(1-qd);newdt=sum(b*eta**n for n,b in B.items() if n>=2)+MD*qd**10/(1-qd);dt=min(olddt,newdt)
  st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd);sd=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  if scalar:
   st=min(st,sum(b*eta**n for n,b in scalar_bounds.items())+Y*qd**10/(1-qd))
   sd=min(sd,sum(n*b*eta**n for n,b in scalar_bounds.items())+Y*qd**10*(10-9*qd)/(1-qd)**2)
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=sd/(eta/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  out=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=eta/40000);out.update({'known_'+k:v for k,v in terms.items()})
  return dict(constants=ss(out),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(olddt),retained=str(newdt)))
 arms={}
 for name,cancel,small,scalar in [('baseline',False,False,False),('cancellation_same',True,False,False),('cancellation_small',True,True,False),('scalar_small',True,True,True)]:
  for j in range(1,8193):
   rec=at(j,cancel,small,scalar)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=at(j-1,cancel,small,scalar) if j>1 else None);arms[name]=rec
 need(arms['baseline']==inherited,'EXACT_ENTIRE_PARENT_ARM');need(all(Q(a['gain_exact'])>=1 for a in arms.values()),'NO_LOSS')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 observed=lease.observed()
 if observed!=runtime:put('RUNTIME_DIFFERENCE.json',dict(added={p:h for p,h in observed.items() if p not in runtime},removed={p:h for p,h in runtime.items() if p not in observed},changed={p:[h,observed[p]] for p,h in runtime.items() if p in observed and h!=observed[p]}))
 need(observed==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,classification='CANCELLATION_PRESERVING_CLOCK_SUPREMUM',inverse_intervals={e:[list(map(str,v)) for v in ee] for e,ee in inverse.items()},inverse_abs={str(n):str(v) for n,v in Eb.items()},scalar_bounds={str(n):str(v) for n,v in scalar_bounds.items()},distance_bounds={str(n):str(v) for n,v in B.items()},contour_records=contour_records,arms=arms,seconds=time.monotonic()-started,scope='Larger sufficient local amplitude only; global radius, family and physical parameters unchanged.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=result['seconds'],arms={k:dict(eta=float(Q(v['constants']['clock_eta'])),gain=float(Q(v['gain_exact'])),theta=v['theta'],ratios={n:float(Q(x)) for n,x in v['ratios'].items()},next_gates=v['next_larger']['gates'] if v['next_larger'] else None) for k,v in arms.items()})),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('finite_contour_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CAP_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
