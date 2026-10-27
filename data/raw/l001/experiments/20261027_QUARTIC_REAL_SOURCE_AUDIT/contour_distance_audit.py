"""Independent rational reconstruction of four contour/distance certificate arms."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'20261027_CONTOUR_DISTANCE_CERTIFICATE'
CUTOFF=1793101111
COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def strs(d):return {k:str(v) for k,v in d.items()}
def magnitude(v):return max(abs(Q(x)) for x in v)
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==terminal[k],'TERMINAL:'+n)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_ACTUAL_QUINTIC_CLOCK_CERTIFICATE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');result=read(ROOT/'RESULT.json')
 base={k:Q(v) for k,v in prior['constants_exact']['actual_d5'].items()}
 distance={n:max(magnitude(clock['arms'][e]['values']['d'+str(n)]['exact_bounds']) for e in ('primary','independent')) for n in (2,3)}
 distance[4]=max(magnitude(v['d4']) for v in fourth['coefficient_intervals'].values());distance[5]=max(magnitude(v['bulk']['d5']['exact_bounds']) for v in fifth['arms'].values())
 distance.update({n:Q(ninth['distance'][n]) for n in range(6,10)})
 ck(result['distance_bounds']=={str(n):str(v) for n,v in distance.items()},'DISTANCE_INPUTS')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 fs={3:Q(10000),4:Q(fourth['selected_quartic_abs']),5:Q(prior['selected_quintic_abs']),6:Q(sixth['sixth_abs']),7:Q(auth('20261027_SEVENTH_CLOCK_ENCLOSURE/RESULT.json')['seventh_abs']),8:Q(auth('20261027_EIGHTH_CLOCK_ENCLOSURE/RESULT.json')['eighth_abs']),9:Q(ninth['ninth_abs'])}
 for n,v in fs.items():ck(base['known_'+names[n]]==v*base['clock_eta']**n,'COEFFICIENT_PARENT:'+str(n))
 ck(result['clock_bounds']=={str(n):str(v) for n,v in fs.items()},'CLOCK_INPUTS')
 contours=[Q(1,2),Q(2,3),Q(3,4),Q(4,5),Q(9,10),Q(10,11),Q(15,16)]
 ck(result['contours']==list(map(str,contours)),'FIXED_CONTOURS')
 R,MD,MF,Y=[base[k] for k in ('physical_radius','observable_sup','clock_sup','aggregate_bound')];c2,c3=[Q(sixth['scalar_abs'][k]) for k in ('chi2','chi3')]
 ck(MF==129*MD/32,'BASELINE_CONTOUR')
 def evaluate(j,retained,optimize):
  a=R/Q(2**(j+1));qd=a/R;options=[]
  for theta in contours if optimize else [Q(1,2)]:
   z=a/(theta*R)
   if z<1:options.append((MD*(1+128*theta/(1-theta))/32*z**10/(1-z),theta))
  ck(bool(options),'VALID_CONTOUR');tail,theta=min(options,key=lambda v:v[0]);sup=MD*(1+128*theta/(1-theta))/32
  known={names[n]:v*a**n for n,v in fs.items()};costs={k:v/(10*a*a) for k,v in known.items()};costs['unknown_tail']=tail/(10*a*a)
  old=MD*qd**2/(1-qd);new=sum(v*a**n for n,v in distance.items())+MD*qd**10/(1-qd);dt=min(old,new) if retained else old
  st=c2*a*a+c3*a**3+Y*qd**4/(1-qd);sd=2*c2*a*a+3*c3*a**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  out=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);out.update({'known_'+k:v for k,v in known.items()})
  return dict(constants=strs(out),costs=strs(costs),ratios=strs(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(old),retained=str(new)))
 summaries={}
 for name,retained,optimize in [('baseline',False,False),('distance_only',True,False),('contour_only',False,True),('both',True,True)]:
  for j in range(1,8193):
   rec=evaluate(j,retained,optimize)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger=evaluate(j-1,retained,optimize) if j>1 else None
  if larger:ck(not all(larger['gates'].values()),'FIRST_PASS:'+name)
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger)
  ck(result['arms'][name]==rec,'ENTIRE_ARM:'+name)
  if name=='baseline':
   ck(rec['constants']==strs(base) and j==prior['selected_dyadic'],'BASELINE_FULL');ck(rec['costs']==prior['clock_costs'] and rec['ratios']==prior['gate_ratios'] and rec['gates']==prior['gates'],'BASELINE_COSTS')
  summaries[name]=dict(eta=float(Q(rec['constants']['clock_eta'])),gain=float(Q(rec['gain_exact'])),theta=rec['theta'],ratios={k:float(Q(v)) for k,v in rec['ratios'].items()},costs={k:float(Q(v)) for k,v in rec['costs'].items()},next_ratios={k:float(Q(v)) for k,v in larger['ratios'].items()} if larger else None,next_gates=larger['gates'] if larger else None)
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=summaries,scope='Independent exact four-arm coefficient inputs, all preceding dyadic failures, contour minimization, full certificates/costs and bindings. Underlying analytic family, lapse bound, physical coefficient enclosures and source/ODE qualifications inherited; no new evolution.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'CONTOUR_DISTANCE_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');p=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('contour_review_lease',p);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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
