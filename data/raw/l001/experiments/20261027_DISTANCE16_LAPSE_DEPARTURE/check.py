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
PARENT_PIN='d1a75f309d47ea127e12ff7ab4405debc71add158ae8e752ed19c8b23c25abea'
AUDIT_PIN='13c9b299b41c5b5192aeaac1d1b6f8a30b29a8c9fed60065b22b138d942b0f54'
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
 parent=BASE/'20261027_DEGREE16_DISTANCE_MAJORANT';bind(parent/'TERMINAL.json',PARENT_PIN)
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 audit=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/DEGREE16_AUDIT.json';bind(audit,AUDIT_PIN);need(read(audit)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 high=read(parent/'RESULT.json');prior=auth('20261027_CANCELLATION_CONTOUR_CERTIFICATE/RESULT.json');rawc=auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json')
 len(str(10**20000)) # preload inherited authenticated _pylong before runtime freeze
 runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['scalar_small'];base={k:Q(v) for k,v in inherited['constants'].items()}
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
 normalization={}
 for engine in ('primary','independent'):
  initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json')
  need(initial['initial_background'][0]['exact_bounds']==['0','0'],'LOWER_LOG_A_ZERO:'+engine)
  need(initial['initial_background'][4]['exact_bounds']==['1','1'],'LOWER_BACKGROUND_E_ONE:'+engine)
  normalization[engine]=dict(log_a=['0','0'],E=['1','1'])
 gap=Q(rawc['constants_exact']['gap']);u=4*Y/gap;need(0<=u<1 and 0<=Y<1,'COLLAR');Z=64/(1-u);vmax=4*Y*Z/(1-Y)**2;need(vmax<1,'COMPLEX_VELOCITY')
 ed=64*u/(1-u);pd=Y/(1-Y);vd=vmax**2/(1-vmax**2);JD=(1+ed)*(1+pd)*(1+vd)-1;need(JD>=0,'DEPARTURE_POSITIVE');J=min(Q(128),JD)
 B16=dict(B);B16.update({n:Q(high['distance'][n]) for n in range(10,17)})
 need(high['degree']==16 and all(v>=0 for v in B16.values()),'HIGH_DEGREE')
 for n in range(6,10):need(B[n]==Q(high['distance'][n]),'HIGH_PREFIX:'+str(n))
 contour_records={}
 for theta in EXTENDED:
  x=theta*R
  def data(bs,N):
   value=sum(b*x**n for n,b in bs.items())+MD*theta**(N+1)/(1-theta)
   w=sum(n*b*x**n for n,b in bs.items())+MD*theta**(N+1)*(N+1-N*theta)/(1-theta)**2
   a=sum((n-1)*b*x**n for n,b in bs.items() if n>=2)+MD*theta**(N+1)*(N-(N-1)*theta)/(1-theta)**2
   return value,w,a
  v,w,a=data(B,9);v16,w16,a16=data(B16,16)
  e=sum(b*x**n for n,b in Eb.items())+128*theta**9/(1-theta)
  ej=sum(b*x**n for n,b in Eb.items())+J*theta**9/(1-theta)
  generic=MD*(1+128*theta/(1-theta))/32;finite=(128*w+v)/32;old=min(generic,finite,(a+w*e)/32)
  contour_records[str(theta)]=dict(value=str(v),euler_derivative=str(w),cancelled_distance=str(a),value16=str(v16),euler_derivative16=str(w16),cancelled_distance16=str(a16),inverse_departure=str(e),inverse_departure_refined=str(ej),baseline=str(old),distance16=str(min(old,(a16+w16*e)/32)),lapse=str(min(old,(a+w*ej)/32)),both=str(min(old,(a16+w16*ej)/32)))
 def at(j,mode):
  eta=R/Q(2**(j+1));qd=eta/R;options=[]
  for theta in EXTENDED:
   z=eta/(theta*R)
   if z<1:
    sup=Q(contour_records[str(theta)][mode]);options.append((sup*z**10/(1-z),theta,sup))
  tail,theta,sup=min(options,key=lambda v:v[0]);terms={names[n]:v*eta**n for n,v in F.items()};costs={k:v/(10*eta**2) for k,v in terms.items()};costs['unknown_tail']=tail/(10*eta**2)
  olddt=MD*qd**2/(1-qd);newdt=sum(b*eta**n for n,b in B.items() if n>=2)+MD*qd**10/(1-qd);dt=min(olddt,newdt)
  if mode in ('distance16','both'):dt=min(dt,sum(b*eta**n for n,b in B16.items() if n>=2)+MD*qd**17/(1-qd))
  st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd);sd=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  if True:
   st=min(st,sum(b*eta**n for n,b in scalar_bounds.items())+Y*qd**10/(1-qd))
   sd=min(sd,sum(n*b*eta**n for n,b in scalar_bounds.items())+Y*qd**10*(10-9*qd)/(1-qd)**2)
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=sd/(eta/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  out=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=eta/40000);out.update({'known_'+k:v for k,v in terms.items()})
  candidates=dict(old=str(olddt),retained=str(newdt))
  if mode in ('distance16','both'):candidates['retained16']=str(sum(b*eta**n for n,b in B16.items() if n>=2)+MD*qd**17/(1-qd))
  return dict(constants=ss(out),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=candidates)
 arms={}
 for name in ('baseline','distance16','lapse','both'):
  for j in range(1,8193):
   rec=at(j,name)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=at(j-1,name) if j>1 else None);arms[name]=rec
 need(arms['baseline']==dict(inherited,gain_exact='1'),'EXACT_ENTIRE_PARENT_ARM_GAIN_RESET');need(all(Q(a['gain_exact'])>=1 for a in arms.values()),'NO_LOSS')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 observed=lease.observed()
 if observed!=runtime:put('RUNTIME_DIFFERENCE.json',dict(added={p:h for p,h in observed.items() if p not in runtime},removed={p:h for p,h in runtime.items() if p not in observed},changed={p:[h,observed[p]] for p,h in runtime.items() if p in observed and h!=observed[p]}))
 need(observed==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,classification='DEGREE16_DISTANCE_LAPSE_DEPARTURE_FACTORIAL',normalization=normalization,global_departure=dict(u=str(u),vmax=str(vmax),background=str(ed),metric=str(pd),boost=str(vd),bound=str(JD),coefficient_tail_sup=str(J)),distance16_bounds={str(n):str(v) for n,v in B16.items()},inverse_intervals={e:[list(map(str,v)) for v in ee] for e,ee in inverse.items()},inverse_abs={str(n):str(v) for n,v in Eb.items()},scalar_bounds={str(n):str(v) for n,v in scalar_bounds.items()},distance_bounds={str(n):str(v) for n,v in B.items()},contour_records=contour_records,arms=arms,seconds=time.monotonic()-started,scope='Larger sufficient local amplitude only; global radius, family and physical parameters unchanged.')
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
