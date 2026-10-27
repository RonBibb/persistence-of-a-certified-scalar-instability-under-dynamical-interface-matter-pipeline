"""Independent finite-contour saved-record arithmetic; no producer imports."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_FINITE_CONTOUR_CERTIFICATE';CUTOFF=1793101111;COUNT=0
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
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PRODUCER_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'TERMINAL:'+n)
 bound={}
 for g in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[g].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_CONTOUR_DISTANCE_CERTIFICATE/RESULT.json');sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');result=read(ROOT/'RESULT.json')
 base={k:Q(v) for k,v in prior['arms']['both']['constants'].items()};B={int(n):Q(v) for n,v in prior['distance_bounds'].items()};B[1]=max(abs(Q(x)) for e in ('primary','independent') for x in clock['arms'][e]['values']['d1']['exact_bounds']);ck(result['distance_bounds']=={str(n):str(v) for n,v in B.items()},'INPUT_COEFFICIENTS')
 F={int(n):Q(v) for n,v in prior['clock_bounds'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];c2,c3=[Q(sixth['scalar_abs'][k]) for k in ('chi2','chi3')]
 original=[Q(1,2),Q(2,3),Q(3,4),Q(4,5),Q(9,10),Q(10,11),Q(15,16)];extended=[Q(1,8),Q(1,4),Q(1,3),Q(2,5)]+original
 records={}
 for theta in extended:
  value=sum(B[n]*(theta*R)**n for n in range(1,10))+MD*theta**10/(1-theta)
  derivative=sum(n*B[n]*(theta*R)**n for n in range(1,10))+MD*(10*theta**10-9*theta**11)/(1-theta)**2
  old=MD*(1+128*theta/(1-theta))/32;new=(128*derivative+value)/32
  records[str(theta)]=dict(value=str(value),euler_derivative=str(derivative),generic_sup=str(old),finite_sup=str(new),selected_sup=str(min(old,new)))
 ck(records==result['contour_records'],'ALL_ELEVEN_CONTOUR_BOUNDS')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def evaluate(j,finite,extra):
  a=R/Q(2**(j+1));qd=a/R;candidates=[]
  for theta in extended if extra else original:
   z=a/(theta*R)
   if z<1:
    sup=Q(records[str(theta)]['selected_sup' if finite else 'generic_sup']);candidates.append((sup*z**10/(1-z),theta,sup))
  ck(bool(candidates),'ADMISSIBLE_CONTOUR');tail,theta,sup=min(candidates,key=lambda x:x[0]);terms={names[n]:v*a**n for n,v in F.items()};costs={k:v/(10*a*a) for k,v in terms.items()};costs['unknown_tail']=tail/(10*a*a)
  olddt=MD*qd**2/(1-qd);newdt=sum(B[n]*a**n for n in range(2,10))+MD*qd**10/(1-qd);dt=min(olddt,newdt)
  st=c2*a*a+c3*a**3+Y*qd**4/(1-qd);sd=2*c2*a*a+3*c3*a**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+k:v for k,v in terms.items()})
  return dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(olddt),retained=str(newdt)))
 summaries={}
 for name,finite,extra in [('baseline',False,False),('extended_only',False,True),('finite_original',True,False),('finite_extended',True,True)]:
  for j in range(1,8193):
   rec=evaluate(j,finite,extra)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger=evaluate(j-1,finite,extra) if j>1 else None
  if larger:ck(not all(larger['gates'].values()),'FIRST_DYADIC')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);ck(rec==result['arms'][name],'WHOLE_ARM:'+name)
  if name=='baseline':ck(rec==prior['arms']['both'],'PARENT_FULL_REPLAY')
  summaries[name]=dict(eta=float(Q(rec['constants']['clock_eta'])),gain=float(Q(rec['gain_exact'])),theta=rec['theta'],ratios={k:float(Q(v)) for k,v in rec['ratios'].items()},costs={k:float(Q(v)) for k,v in rec['costs'].items()},next_ratios={k:float(Q(v)) for k,v in larger['ratios'].items()} if larger else None,next_gates=larger['gates'] if larger else None)
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=summaries,scope='Independent exact eleven contour supremum reductions, first passing dyadics, four full certificates, costs and source bindings. Inherited physical coefficient and full-disk analytic/lapse premises; no new ODE or physical evolution.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'FINITE_CONTOUR_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');p=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('finite_contour_review_lease',p);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
