"""Actual sixth coefficient propagation factorial."""
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
def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):
 z=[x*y for x in a for y in b];return min(z),max(z)
def sc(a,k):return mul(a,(Q(k),Q(k)))
def ab(a):return max(map(abs,a))
def pair(a):return list(map(str,a))
def iv(v):return tuple(map(Q,v['exact_bounds']))
def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_SIXTH_REAL_SOURCE_ENCLOSURE';bind(parent/'TERMINAL.json','4f1f3c44fee76ed158ebb40c773f29b82ce3e8b0fddfa6fd6ceb39231da56a85');t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for g in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[g].items():bind(p,h)
 a=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/SIXTH_REAL_AUDIT_R1.json';bind(a,'440f106140813b08f21548128f735a1989dd1c3996ce9ad39b96268424db4b97');audit=read(a);need(audit['PASS'] and audit['producer_terminal']==sha(parent/'TERMINAL.json'),'AUDIT_PASS_AND_TARGET')
 bind(BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/sixth_real_audit_r1.py',audit['audit_source_sha256'])
 bind(BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/SIXTH_JET_DIAGNOSTIC.json',audit['identity_diagnostic_sha256'])
 bind(BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/sixth_jet_diagnostic.py',audit['identity_source_sha256'])
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 actual=read(parent/'RESULT.json');prior=auth('20261027_DIRECT_PRODUCT_CLOCK_REMAINDER/RESULT.json');distanceparent=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json')
 docs={n:auth('20261027_'+name+'_CLOCK_ENCLOSURE/RESULT.json') for n,name in [(6,'SIXTH'),(7,'SEVENTH'),(8,'EIGHTH'),(9,'NINTH')]};fc=auth('20261027_CONTOUR_DISTANCE_CERTIFICATE/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['both'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(distanceparent['global_departure']['coefficient_tail_sup'])
 D={int(n):Q(v) for n,v in distanceparent['distance16_bounds'].items()};E={int(n):Q(v) for n,v in distanceparent['inverse_abs'].items()};C={int(n):Q(v) for n,v in distanceparent['scalar_bounds'].items()};F={int(n):Q(v) for n,v in prior['new_clock_bounds'].items()}
 generic=list(map(Q,docs[9]['distance']));records={};newF=dict(F)
 for n in range(6,10):
  records[str(n)]={};oldabs=[];newabs=[]
  for engine in ('primary','independent'):
   vals=clock['arms'][engine]['values'];ds=[(Q(0),Q(0))]+[iv(vals['d'+str(j)]) for j in range(1,4)]+[(-generic[j],generic[j]) for j in range(4,n+1)]
   d4=tuple(map(Q,fourth['coefficient_intervals'][engine]['d4']));d5=iv(fifth['arms'][engine]['bulk']['d5']);rate=iv(vals['rate']);ei=[tuple(map(Q,x)) for x in distanceparent['inverse_intervals'][engine]]
   ds[4]=d4;ds[5]=d5
   def evaluate(arr):
    term=sc(arr[n],n-1);parts={'leading':pair(mul(rate,term))}
    for j in range(1,n):
     part=sc(mul(arr[j],ei[n-j]),j);term=add(term,part);parts[str(j)]=pair(mul(rate,part))
    return mul(rate,term),parts
   old,oldparts=evaluate(ds);stored=prior['coefficient_records'][str(n)][engine]
   need(pair(old)==stored['new'] and ab(old)==Q(stored['new_abs']),'EXACT_OLD_COEFFICIENT:'+str(n)+':'+engine)
   changed=list(ds);changed[6]=iv(actual['arms'][engine]['bulk']['d6']);new,newparts=evaluate(changed)
   records[str(n)][engine]=dict(old=pair(old),new=pair(new),old_abs=str(ab(old)),new_abs=str(ab(new)),old_terms=oldparts,new_terms=newparts);oldabs.append(ab(old));newabs.append(ab(new))
  need(min(max(oldabs),Q(prior['old_clock_bounds'][str(n)]))==F[n],'EXACT_OLD_BOUND:'+str(n));newF[n]=min(F[n],max(newabs))
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'};evidence={}
 newD=dict(D);newD[6]=min(D[6],max(ab(iv(actual['arms'][e]['bulk']['d6'])) for e in ('primary','independent')))
 def at(j,propagate,coeff):
  DD=newD if propagate else D
  eta=R/Q(2**(j+1));q=eta/R;options=[]
  for th,row in distanceparent['contour_records'].items():
   theta=Q(th);z=eta/(theta*R)
   if z<1:
    sup=Q(row['both']);options.append((sup*z**10/(1-z),theta,sup))
  oldtail,theta,sup=min(options,key=lambda x:x[0]);jt=JC*q**9/(1-q);ed=sum(v*eta**m for m,v in E.items())+jt;wd=sum(n*v*eta**n for n,v in DD.items())
  pieces=dict(finite_distance=sum((n-1)*DD[n]*eta**n for n in range(10,17)),finite_cross=sum(n*b*e*eta**(n+m) for n,b in DD.items() for m,e in E.items() if n+m>=10),distance_tail=MD*q**17*(16-15*q)/(1-q)**2,unknown_distance_product=MD*q**17*(17-16*q)/(1-q)**2*ed,unknown_lapse_product=wd*jt)
  dtail=sum(pieces.values())/32;tail=min(oldtail,dtail);bf=newF if coeff else F;known={names[n]:v*eta**n for n,v in bf.items()};costs={k:v/(10*eta**2) for k,v in known.items()};costs['unknown_tail']=tail/(10*eta**2)
  d0=MD*q*q/(1-q);d9=sum(DD[n]*eta**n for n in range(2,10))+MD*q**10/(1-q);d16=sum(DD[n]*eta**n for n in range(2,17))+MD*q**17/(1-q);distance=min(d0,d9,d16)
  st=min(C[2]*eta**2+C[3]*eta**3+Y*q**4/(1-q),sum(b*eta**n for n,b in C.items())+Y*q**10/(1-q));sd=min(2*C[2]*eta**2+3*C[3]*eta**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*b*eta**n for n,b in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=distance,scalar=st,scalar_derivative=sd);ratios['distance']/=25*eta;ratios['scalar']/=eta/40000;ratios['scalar_derivative']/=eta/40000
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  out=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=distance,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=eta/40000);out.update({'known_'+k:v for k,v in known.items()})
  rec=dict(constants=ss(out),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(d0),retained=str(d9),retained16=str(d16)))
  ev=dict(contour_tail=str(oldtail),direct_tail=str(dtail),direct_pieces_before_rate=ss(pieces),used='direct' if dtail<oldtail else 'contour',theta_describes_fallback=True)
  return rec,ev
 arms={}
 for name,direct,coeff in [('baseline',False,False),('distance_only',True,False),('clock_only',False,True),('both',True,True)]:
  for j in range(1,8193):
   rec,ev=at(j,direct,coeff)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE')
  larger,lev=at(j-1,direct,coeff) if j>1 else (None,None);rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=larger);arms[name]=rec;evidence[name]=dict(accepted=ev,next_larger=lev)
 need(arms['baseline']==dict(inherited,gain_exact='1'),'EXACT_BASELINE_GAIN_RESET');need(all(Q(v['gain_exact'])>=1 for v in arms.values()),'NO_LOSS')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,classification='ACTUAL_SIXTH_COEFFICIENT_PROPAGATION_FACTORIAL',coefficient_records=records,old_distance_bounds={str(n):str(v) for n,v in D.items()},new_distance_bounds={str(n):str(v) for n,v in newD.items()},old_clock_bounds={str(n):str(v) for n,v in F.items()},new_clock_bounds={str(n):str(v) for n,v in newF.items()},arms=arms,tail_evidence=evidence,seconds=time.monotonic()-started,scope='Unsigned actual d6 substituted in retained clock and/or distance remainder independently. No new physical evolution or coefficient sign.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=result['seconds'],arms={k:dict(eta=float(Q(v['constants']['clock_eta'])),gain=float(Q(v['gain_exact'])),ratios={n:float(Q(x)) for n,x in v['ratios'].items()},costs={n:float(Q(x)) for n,x in v['costs'].items()},next_gates=v['next_larger']['gates'] if v['next_larger'] else None) for k,v in arms.items()})),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('direct_product_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CAP_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
