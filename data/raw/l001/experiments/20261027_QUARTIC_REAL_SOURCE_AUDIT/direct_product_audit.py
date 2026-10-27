"""Independent direct high-product tail and interval coefficient audit."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_DIRECT_PRODUCT_CLOCK_REMAINDER';CUTOFF=1793101111;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def ss(d):return {k:str(v) for k,v in d.items()}
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
 prior=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');result=read(ROOT/'RESULT.json');docs={n:auth('20261027_'+label+'_CLOCK_ENCLOSURE/RESULT.json') for n,label in [(6,'SIXTH'),(7,'SEVENTH'),(8,'EIGHTH'),(9,'NINTH')]}
 base={k:Q(v) for k,v in prior['arms']['both']['constants'].items()};F={int(n):Q(v) for n,v in auth('20261027_CONTOUR_DISTANCE_CERTIFICATE/RESULT.json')['clock_bounds'].items()};newF=dict(F);records={};generic=list(map(Q,docs[9]['distance']))
 for n in range(6,10):
  records[str(n)]={};olds=[];news=[]
  for engine in ('primary','independent'):
   v=clock['arms'][engine]['values'];r=interval(v['rate']);ds=[(Q(0),Q(0))]+[interval(v['d'+str(j)]) for j in range(1,4)]+[(-generic[j],generic[j]) for j in range(4,n+1)];d4=pair(fourth['coefficient_intervals'][engine]['d4']);d5=interval(fifth['arms'][engine]['bulk']['d5']);ei=[pair(x) for x in prior['inverse_intervals'][engine]]
   if n>=7:ds[4]=d4
   def coefficient(values):
    total=scale(values[n],n-1);parts={'leading':packed(mul(r,total))}
    for j in range(1,n):
     contribution=scale(mul(values[j],ei[n-j]),j);total=add(total,contribution);parts[str(j)]=packed(mul(r,contribution))
    return mul(r,total),parts
   old,op=coefficient(ds);saved=docs[n]['sixth_coefficients' if n==6 else 'coefficients'][engine];ck(packed(old)==saved['F'+str(n)] and max(map(abs,old))==Q(saved['F'+str(n)+'_abs']),'OLD_INTERVAL_REPLAY')
   ds[4],ds[5]=d4,d5;new,np=coefficient(ds);oa,na=max(map(abs,old)),max(map(abs,new));records[str(n)][engine]=dict(old=packed(old),new=packed(new),old_abs=str(oa),new_abs=str(na),old_terms=op,new_terms=np);olds.append(oa);news.append(na)
  ck(max(olds)==F[n],'OLD_COMMON_BOUND');newF[n]=min(F[n],max(news))
 ck(records==result['coefficient_records'],'ALL_COEFFICIENT_RECORDS');ck(result['old_clock_bounds']=={str(n):str(v) for n,v in F.items()} and result['new_clock_bounds']=={str(n):str(v) for n,v in newF.items()},'BOUND_SELECTION')
 R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(prior['global_departure']['coefficient_tail_sup']);D={int(n):Q(v) for n,v in prior['distance16_bounds'].items()};E={int(n):Q(v) for n,v in prior['inverse_abs'].items()};C={int(n):Q(v) for n,v in prior['scalar_bounds'].items()};names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def evaluate(j,direct,changed):
  a=R/Q(2**(j+1));q=a/R;choices=[]
  for th,row in prior['contour_records'].items():
   theta=Q(th);z=a/(theta*R)
   if z<1:
    sup=Q(row['both']);choices.append((sup*z**10/(1-z),theta,sup))
  ck(bool(choices),'VALID_CONTOUR');oldtail,theta,sup=min(choices,key=lambda v:v[0]);RJ=JC*q**9/(1-q);Efull=sum(E[m]*a**m for m in range(1,9))+RJ;Dprime=sum(n*D[n]*a**n for n in range(1,17))
  # Independent convolution, collecting by total degree before evaluation.
  cross={}
  for n in range(1,17):
   for m in range(1,9):
    if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*D[n]*E[m]
  pieces=dict(finite_distance=sum((n-1)*D[n]*a**n for n in range(10,17)),finite_cross=sum(v*a**n for n,v in cross.items()),distance_tail=MD*(16*q**17-15*q**18)/(1-q)**2,unknown_distance_product=MD*(17*q**17-16*q**18)/(1-q)**2*Efull,unknown_lapse_product=Dprime*RJ)
  dtail=sum(pieces.values())/32;tail=min(oldtail,dtail) if direct else oldtail;bf=newF if changed else F;known={names[n]:v*a**n for n,v in bf.items()};costs={k:v/(10*a*a) for k,v in known.items()};costs['unknown_tail']=tail/(10*a*a)
  d0=MD*q*q/(1-q);d9=sum(D[n]*a**n for n in range(2,10))+MD*q**10/(1-q);d16=sum(D[n]*a**n for n in range(2,17))+MD*q**17/(1-q);dt=min(d0,d9,d16)
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(C[n]*a**n for n in range(2,10))+Y*q**10/(1-q));sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*C[n]*a**n for n in range(2,10))+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+k:v for k,v in known.items()})
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(d0),retained=str(d9),retained16=str(d16)));ev=dict(contour_tail=str(oldtail),direct_tail=str(dtail),direct_pieces_before_rate=ss(pieces),used='direct' if direct and dtail<oldtail else 'contour',theta_describes_fallback=True)
  return rec,ev
 summaries={}
 for name,direct,changed in [('baseline',False,False),('direct_only',True,False),('coefficients_only',False,True),('both',True,True)]:
  for j in range(1,8193):
   rec,ev=evaluate(j,direct,changed)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger,lev=evaluate(j-1,direct,changed) if j>1 else (None,None)
  if larger:ck(not all(larger['gates'].values()),'FIRST_DYADIC')
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);ck(rec==result['arms'][name],'FULL_ARM:'+name);ck(result['tail_evidence'][name]==dict(accepted=ev,next_larger=lev),'TAIL_PARTITION:'+name)
  if name=='baseline':ck(rec==dict(prior['arms']['both'],gain_exact='1'),'PARENT_REPLAY')
  summaries[name]=dict(eta=float(Q(rec['constants']['clock_eta'])),gain=float(Q(rec['gain_exact'])),ratios={k:float(Q(v)) for k,v in rec['ratios'].items()},costs={k:float(Q(v)) for k,v in rec['costs'].items()},next_ratios={k:float(Q(v)) for k,v in larger['ratios'].items()} if larger else None,next_costs={k:float(Q(v)) for k,v in larger['costs'].items()} if larger else None,tail_used=ev['used'])
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=summaries,coefficient_improvements={str(n):float(F[n]/newF[n]) for n in range(6,10)},scope='Independent interval old/new F6..9 reconstruction, convolution-based direct tail partition, full four-arm certificate and provenance replay. Analytic-family, physical distance and majorant premises inherited; no new ODE or signed high-order solve.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'DIRECT_PRODUCT_AUDIT.json'
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
