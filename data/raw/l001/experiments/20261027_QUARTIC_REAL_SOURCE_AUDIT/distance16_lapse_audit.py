"""Independent saved readout audit; audited coefficient generation inherited."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_DISTANCE16_LAPSE_DEPARTURE';CUTOFF=1793101111;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def ss(d):return {k:str(v) for k,v in d.items()}
def main():
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'TERMINAL:'+n)
 bound={}
 for g in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[g].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_CANCELLATION_CONTOUR_CERTIFICATE/RESULT.json');high=auth('20261027_DEGREE16_DISTANCE_MAJORANT/RESULT.json');raw=auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json');result=read(ROOT/'RESULT.json')
 base={k:Q(v) for k,v in prior['arms']['scalar_small']['constants'].items()};B={int(n):Q(v) for n,v in prior['distance_bounds'].items()};B16=dict(B);B16.update({n:Q(high['distance'][n]) for n in range(10,17)});eb={int(n):Q(v) for n,v in prior['inverse_abs'].items()};cb={int(n):Q(v) for n,v in prior['scalar_bounds'].items()};F={int(n):Q(v) for n,v in auth('20261027_CONTOUR_DISTANCE_CERTIFICATE/RESULT.json')['clock_bounds'].items()}
 for key in ('inverse_intervals','inverse_abs','scalar_bounds','distance_bounds'):ck(result[key]==prior[key],'UNCHANGED:'+key)
 ck(result['distance16_bounds']=={str(n):str(v) for n,v in B16.items()} and high['degree']==16,'D16_INPUTS')
 for n in range(6,10):ck(B[n]==Q(high['distance'][n]),'D16_PREFIX')
 norm={}
 for e in ('primary','independent'):
  initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+e+'.json');ck(initial['initial_background'][0]['exact_bounds']==['0','0'] and initial['initial_background'][4]['exact_bounds']==['1','1'],'LOWER_NORMALIZATION');norm[e]=dict(log_a=['0','0'],E=['1','1'])
 ck(result['normalization']==norm,'NORMALIZATION_RECORD')
 R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];gap=Q(raw['constants_exact']['gap']);u=4*Y/gap;ck(0<=u<1 and 0<=Y<1,'COLLAR');v=256*Y/((1-u)*(1-Y)**2);ck(v<1,'BOOST_BRANCH');e=64*u/(1-u);p=Y/(1-Y);boost=v*v/(1-v*v)
 # Independently expand the three-factor departure polynomial.
 JD=e+p+boost+e*p+e*boost+p*boost+e*p*boost;J=min(Q(128),JD)
 ck(result['global_departure']==dict(u=str(u),vmax=str(v),background=str(e),metric=str(p),boost=str(boost),bound=str(JD),coefficient_tail_sup=str(J)),'GLOBAL_DEPARTURE')
 contours=list(map(Q,['1/128','1/64','1/32','1/16','1/8','1/4','1/3','2/5','1/2','2/3','3/4','4/5','9/10','10/11','15/16']));records={}
 for theta in contours:
  x=theta*R
  def sums(b,N):
   return (sum(z*x**n for n,z in b.items())+MD*theta**(N+1)/(1-theta),sum(n*z*x**n for n,z in b.items())+MD*((N+1)*theta**(N+1)-N*theta**(N+2))/(1-theta)**2,sum((n-1)*z*x**n for n,z in b.items() if n>=2)+MD*(N*theta**(N+1)-(N-1)*theta**(N+2))/(1-theta)**2)
  V,W,A=sums(B,9);V16,W16,A16=sums(B16,16);ep=sum(z*x**n for n,z in eb.items());E=ep+128*theta**9/(1-theta);EJ=ep+J*theta**9/(1-theta)
  old=min(MD*(1+128*theta/(1-theta))/32,(128*W+V)/32,(A+W*E)/32)
  records[str(theta)]=dict(value=str(V),euler_derivative=str(W),cancelled_distance=str(A),value16=str(V16),euler_derivative16=str(W16),cancelled_distance16=str(A16),inverse_departure=str(E),inverse_departure_refined=str(EJ),baseline=str(old),distance16=str(min(old,(A16+W16*E)/32)),lapse=str(min(old,(A+W*EJ)/32)),both=str(min(old,(A16+W16*EJ)/32)))
 ck(records==result['contour_records'],'ALL_CONTOUR_BOUNDS')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def evaluate(j,mode):
  a=R/Q(2**(j+1));q=a/R;choices=[]
  for theta in contours:
   z=a/(theta*R)
   if z<1:
    sup=Q(records[str(theta)][mode]);choices.append((sup*z**10/(1-z),theta,sup))
  ck(bool(choices),'VALID_CONTOUR');tail,theta,sup=min(choices,key=lambda x:x[0]);terms={names[n]:b*a**n for n,b in F.items()};costs={k:v/(10*a*a) for k,v in terms.items()};costs['unknown_tail']=tail/(10*a*a)
  d0=MD*q*q/(1-q);d9=sum(B[n]*a**n for n in range(2,10))+MD*q**10/(1-q);candidates=dict(old=str(d0),retained=str(d9));dt=min(d0,d9)
  if mode in ('distance16','both'):
   d16=sum(B16[n]*a**n for n in range(2,17))+MD*q**17/(1-q);candidates['retained16']=str(d16);dt=min(dt,d16)
  st=min(cb[2]*a*a+cb[3]*a**3+Y*q**4/(1-q),sum(cb[n]*a**n for n in range(2,10))+Y*q**10/(1-q));sd=min(2*cb[2]*a*a+3*cb[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*cb[n]*a**n for n in range(2,10))+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+k:v for k,v in terms.items()})
  return dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=candidates)
 summaries={}
 for mode in ('baseline','distance16','lapse','both'):
  for j in range(1,8193):
   rec=evaluate(j,mode)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger=evaluate(j-1,mode) if j>1 else None
  if larger:ck(not all(larger['gates'].values()),'FIRST_DYADIC')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);ck(rec==result['arms'][mode],'FULL_ARM:'+mode)
  if mode=='baseline':ck(rec==dict(prior['arms']['scalar_small'],gain_exact='1'),'BASELINE_GAIN_RESET')
  summaries[mode]=dict(eta=float(Q(rec['constants']['clock_eta'])),gain=float(Q(rec['gain_exact'])),theta=rec['theta'],ratios={k:float(Q(v)) for k,v in rec['ratios'].items()},costs={k:float(Q(v)) for k,v in rec['costs'].items()},next_ratios={k:float(Q(v)) for k,v in larger['ratios'].items()} if larger else None,next_gates=larger['gates'] if larger else None)
 for path,h in bound.items():ck(sha(path)==h,'POST_BOUND:'+path)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=summaries,scope='Independent product-departure identity, normalized lower background, all degree9/16 contour sums and four full certificate/binding reconstructions. Audited physical/majorant coefficients and original analytic-family premises inherited.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'DISTANCE16_LAPSE_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');p=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('distance16_lapse_review',p);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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
