"""Independent direct high-product tail and interval coefficient audit."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_SEVENTH_CERTIFICATE_BRACKET';CUTOFF=1793108564;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def ss(d):return {str(k):str(v) for k,v in d.items()}
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
 prior=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');result=read(ROOT/'RESULT.json')
 inherited=prior['arms']['both'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 D={int(n):Q(v) for n,v in prior['new_distance16'].items()};D24={int(n):Q(v) for n,v in prior['new_distance24'].items()};F={int(n):Q(v) for n,v in prior['new_clock_bounds'].items()};E={int(n):Q(v) for n,v in prior['inverse8'].items()};E24={int(n):Q(v) for n,v in prior['inverse24'].items()};C={int(n):Q(v) for n,v in prior['scalar_bounds'].items()}
 ck(set(D)==set(range(1,17)) and set(D24)==set(E24)==set(range(1,25)),'COVERAGE')
 ck(all(x>=0 for b in (D,D24,F,E,E24,C) for x in b.values()),'NONNEGATIVE_MONOTONE_BOUNDS')
 ck(0<R<min(Q(1,512),Q(25,3840)),'DOWNWARD_OPENING_DOMAIN')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 # Independently group the three fixed convolutions once. Evaluation below
 # remains conventional Fraction arithmetic, not producer integer Horner.
 crosses={}
 for bounds,eb in ((D,E),(D24,E),(D24,E24)):
  cross={}
  for n,b in bounds.items():
   for m,e in eb.items():
    if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*b*e
  crosses[(max(bounds),max(eb))]=cross
 def evaluate(q):
  a=R*q;options=[]
  for th,row in dp['contour_records'].items():
   theta=Q(th);z=a/(theta*R)
   if z<1:options.append((Q(row['both'])*z**10/(1-z),theta,Q(row['both'])))
  ct,theta,sup=min(options,key=lambda x:x[0])
  def direct(bounds,eb):
   N=max(bounds);M=max(eb);RJ=JC*q**(M+1)/(1-q);Efull=sum(v*a**n for n,v in eb.items())+RJ;cross=crosses[(N,M)]
   return dict(finite_distance=sum((n-1)*bounds[n]*a**n for n in range(10,N+1)),finite_cross=sum(v*a**n for n,v in cross.items()),distance_tail=MD*(N*q**(N+1)-(N-1)*q**(N+2))/(1-q)**2,unknown_distance_product=MD*((N+1)*q**(N+1)-N*q**(N+2))/(1-q)**2*Efull,unknown_lapse_product=sum(n*b*a**n for n,b in bounds.items())*RJ)
  p16,p24,pnew=direct(D,E),direct(D24,E),direct(D24,E24);t16,t24,tnew=[sum(p.values())/32 for p in (p16,p24,pnew)];tail=min(ct,t16,t24,tnew)
  known={names[n]:v*a**n for n,v in F.items()};costs={k:v/(10*a*a) for k,v in known.items()};costs['unknown_tail']=tail/(10*a*a)
  ds={0:MD*q*q/(1-q),9:sum(D[n]*a**n for n in range(2,10))+MD*q**10/(1-q),16:sum(D[n]*a**n for n in range(2,17))+MD*q**17/(1-q),24:sum(D24[n]*a**n for n in range(2,25))+MD*q**25/(1-q)}
  dist=min(ds.values())
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(v*a**n for n,v in C.items())+Y*q**10/(1-q))
  sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*v*a**n for n,v in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dist,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+k:v for k,v in known.items()})
  candidates=dict(old=str(ds[0]),retained=str(ds[9]),retained16=str(ds[16]))
  candidates['retained24']=str(ds[24])
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=candidates)
  ev=dict(contour=str(ct),direct16=str(t16),direct24=str(t24),finite_inverse24=str(tnew),normalized_old=ss({k:v/(320*a*a) for k,v in p24.items()}),normalized_new=ss({k:v/(320*a*a) for k,v in pnew.items()}),selected=str(tail),theta_describes_fallback=True)
  return rec,ev
 controls=[]
 for coeff in ({0:Q(2,3),1:-Q(1,7),3:Q(5,11)},{1:Q(7,13),4:Q(3,17),8:Q(5,19)}):
  for q in (Q(1,16),Q(3,32),Q(5,64)):controls.append(dict(q=str(q),coefficients=ss(coeff),value=str(sum(v*q**n for n,v in coeff.items()))))
 ck(result['controls']==controls,'GENERAL_RATIONAL_CONTROLS')
 lo=Q(inherited['constants']['clock_eta'])/R;hi=Q(inherited['next_larger']['constants']['clock_eta'])/R;origin=(lo,hi)
 ck(0<lo<hi<1 and hi==2*lo,'DYADIC_BRACKET')
 low,le=evaluate(lo);high,he=evaluate(hi)
 parentlow={k:v for k,v in inherited.items() if k not in ('gain_exact','selected_dyadic','next_larger')}
 ck(low==parentlow and high==inherited['next_larger'],'EXACT_PARENT_ENDPOINTS')
 ck(le==prior['tail_evidence']['both']['accepted'] and he==prior['tail_evidence']['both']['next_larger'],'PARENT_EVIDENCE')
 ck(all(low['gates'].values()) and not all(high['gates'].values()),'PARENT_PASS_FAIL')
 ck(result['iterations']==16 and len(result['checkpoints'])==16,'FIXED_ITERATIONS')
 predecessor=sha(ROOT/'BINDING.json');checkpoint_hashes={}
 for step in range(1,17):
  q=(lo+hi)/2;rec,ev=evaluate(q);passed=all(rec['gates'].values())
  expected=dict(step=step,q=str(q),eta=str(R*q),passed=passed,record=rec,evidence=ev,predecessor_sha256=predecessor)
  cp=ROOT/('CHECKPOINT_'+str(step).zfill(2)+'.json');ck(read(cp)==expected,'EXACT_MIDPOINT_CHECKPOINT:'+str(step));ck(result['checkpoints'][step-1]==expected,'RESULT_CHECKPOINT:'+str(step))
  predecessor=sha(cp);checkpoint_hashes[str(cp)]=predecessor
  if passed:lo,low,le=q,rec,ev
  else:hi,high,he=q,rec,ev
 ck(hi-lo==(origin[1]-origin[0])/2**16,'EXACT_WIDTH')
 ck(all(low['gates'].values()) and not all(high['gates'].values()),'FINAL_PASS_FAIL')
 ck(result['original_q']==list(map(str,origin)) and result['lower_q']==str(lo) and result['upper_q']==str(hi) and result['width_q']==str(hi-lo),'FINAL_ENDPOINTS')
 ck(result['lower']==low and result['upper']==high and result['lower_evidence']==le and result['upper_evidence']==he,'FULL_FINAL_RECORDS')
 ck(result['last_checkpoint_sha256']==predecessor and result['gain_over_dyadic']==str(lo/origin[0]),'FINAL_CHAIN_GAIN')
 summaries=dict(lower_eta=float(R*lo),upper_eta=float(R*hi),gain_over_dyadic=float(lo/origin[0]),lower_ratios={k:float(Q(v)) for k,v in low['ratios'].items()},upper_ratios={k:float(Q(v)) for k,v in high['ratios'].items()},lower_costs={k:float(Q(v)) for k,v in low['costs'].items()},upper_costs={k:float(Q(v)) for k,v in high['costs'].items()},lower_tail_parts={k:float(Q(v)) for k,v in le['normalized_new'].items()},upper_tail_parts={k:float(Q(v)) for k,v in he['normalized_new'].items()})
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for p,h in checkpoint_hashes.items():ck(sha(p)==h,'POST_CHECKPOINT:'+p)
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),bracket=summaries,scope='Independent ordinary Fraction convolution/evaluation of original endpoints and all16 fixed rational midpoints, all five gates, complete records, atomic checkpoint hash chain and exact bracket width. Fixed sufficient certificate only, not a physical threshold or actual convergence radius. Inherited field/coefficient/norm premises unchanged.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'SEVENTH_BRACKET_AUDIT.json'
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
