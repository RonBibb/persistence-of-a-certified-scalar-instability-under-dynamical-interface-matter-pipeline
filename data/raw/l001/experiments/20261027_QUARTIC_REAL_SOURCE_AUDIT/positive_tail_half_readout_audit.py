"""Independent Fraction convolution readout; no producer arithmetic imports."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_POSITIVE_TAIL_HALF_RADIUS_READOUT';CUTOFF=1793108564;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ss(d):return {str(k):str(v) for k,v in d.items()}
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 term=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(term['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]
 for n,k in files:ck(sha(ROOT/n)==term[k],'TERMINAL:'+n)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');tails=auth('20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY/RESULT.json');result=read(ROOT/'RESULT.json')
 audit=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_HALF_RADIUS_AUDIT.json');ck(audit['PASS'] and audit['producer_terminal']==sha(BASE/'20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY/TERMINAL.json'),'TAIL_AUDIT_MATCH')
 inv=auth('20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION/RESULT.json');ia=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_INVERSE_TAIL_AUDIT.json');ck(ia['PASS'] and ia['producer_terminal']==sha(BASE/'20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION/TERMINAL.json'),'INVERSE_AUDIT_MATCH')
 inherited=prior['arms']['both'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 def dic(k):return {int(n):Q(v) for n,v in prior[k].items()}
 D,D24,E,E24,C,F=map(dic,('new_distance16','new_distance24','inverse8','inverse24','scalar_bounds','new_clock_bounds'))
 ck(set(D)==set(range(1,17)) and set(D24)==set(E24)==set(range(1,25)) and set(F)==set(range(3,10)),'COVERAGE')
 ck(all(x>=0 for b in (D,D24,E,E24,C,F) for x in b.values()),'POSITIVE_BOUNDS')
 z=list(map(Q,raw['majorant']));kap=Q(tails['weights'][1]);ck(len(z)==25 and raw['degree']==24,'MAJORANT_PREFIX')
 ck(Q(tails['constants']['R'])==R and Q(tails['constants']['Y'])==Y and Q(tails['constants']['K'])==base['K'] and Q(tails['constants']['seed'])==base['seed'],'SAME_FAMILY_DOMAIN')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 cross={}
 for b,e in ((D,E),(D24,E),(D24,E24)):
  c={}
  for n,v in b.items():
   for m,w in e.items():
    if n+m>=10:c[n+m]=c.get(n+m,Q(0))+n*v*w
  cross[max(b),max(e)]=c
 def direct(b,e,q,a):
  N,M=max(b),max(e);jt=JC*q**(M+1)/(1-q);ef=sum(v*a**n for n,v in e.items())+jt
  return dict(finite_distance=sum((n-1)*b[n]*a**n for n in range(10,N+1)),finite_cross=sum(v*a**n for n,v in cross[N,M].items()),distance_tail=MD*(N*q**(N+1)-(N-1)*q**(N+2))/(1-q)**2,unknown_distance_product=MD*((N+1)*q**(N+1)-N*q**(N+2))/(1-q)**2*ef,unknown_lapse_product=sum(n*v*a**n for n,v in b.items())*jt)
 def old_at(q):
  a=R*q;options=[]
  for th,row in dp['contour_records'].items():
   theta=Q(th);w=q/theta
   if w<1:options.append((Q(row['both'])*w**10/(1-w),theta,Q(row['both'])))
  ct,theta,sup=min(options,key=lambda v:v[0]);p16,p24,pnew=direct(D,E,q,a),direct(D24,E,q,a),direct(D24,E24,q,a);t16,t24,tnew=[sum(v.values())/32 for v in (p16,p24,pnew)];tail=min(ct,t16,t24,tnew)
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=tail/(10*a*a)
  ds=dict(old=MD*q*q/(1-q),retained=sum(D[n]*a**n for n in range(2,10))+MD*q**10/(1-q),retained16=sum(D[n]*a**n for n in range(2,17))+MD*q**17/(1-q),retained24=sum(D24[n]*a**n for n in range(2,25))+MD*q**25/(1-q));dist=min(ds.values())
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(v*a**n for n,v in C.items())+Y*q**10/(1-q));sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*v*a**n for n,v in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dist,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+names[n]:v*a**n for n,v in F.items()})
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=ss(ds))
  ev=dict(contour=str(ct),direct16=str(t16),direct24=str(t24),finite_inverse24=str(tnew),normalized_old=ss({k:v/(320*a*a) for k,v in p24.items()}),normalized_new=ss({k:v/(320*a*a) for k,v in pnew.items()}),selected=str(tail),theta_describes_fallback=True)
  return rec,ev
 ck(result['controls']==['1/16','1/8'],'CONTROLS')
 for qq in (Q(1,16),Q(1,8)):
  rr,ee=old_at(qq);parent=inherited if qq==Q(1,16) else inherited['next_larger'];parent={k:v for k,v in parent.items() if k not in ('selected_dyadic','gain_exact','next_larger')};ck(rr==parent,'FULL_PARENT_CONTROL')
 ck(set(result['points'])=={'1/4','1/2'},'FIXED_POINTS');summary={};pointpins={}
 for q in (Q(1,4),Q(1,2)):
  row=result['points'][str(q)];cp=ROOT/('POINT_'+str(q.denominator)+'.json');ck(read(cp)==row,'POINT_RECORD');pointpins[str(cp)]=sha(cp);a=R*q
  old,ev=old_at(q);ck(row['old']==old and row['old_evidence']==ev,'NEW_POINT_BASELINE_REPLAY')
  tr=tails['points'][str(q)];ck(Q(tr['eta'])==a,'SAME_POINT');tb={k:Q(v) for k,v in tr['bounds'].items()};ck(all(v>=0 for v in tb.values()),'TAIL_NONNEGATIVE')
  jt=JC*q**25/(1-q);ef=sum(v*a**n for n,v in E24.items())+jt
  parts=dict(finite_distance=sum((n-1)*D24[n]*a**n for n in range(10,25)),finite_cross=sum(v*a**n for n,v in cross[24,24].items()),unknown_distance=tb['euler_distance_tail']*(1+ef),unknown_lapse=sum(n*v*a**n for n,v in D24.items())*jt)
  oldparts=dict(parts);oldcandidate=sum(parts.values())/32
  ir=inv['points'][str(q)];ck(Q(ir['eta'])==a and Q(ir['old_tail'])==jt,'INVERSE_SAME_POINT');ij=Q(ir['selected_tail']);ck(0<=ij<=jt,'INVERSE_DOMINATION')
  parts['unknown_distance']=tb['euler_distance_tail']*(1+sum(v*a**n for n,v in E24.items())+ij)
  parts['unknown_lapse']=sum(n*v*a**n for n,v in D24.items())*ij
  ck(sum(parts.values())/32<=oldcandidate,'CLOCK_CANDIDATE_DOMINATION')
  scalar={n:min(C[n],kap*z[n]/n**3) if n in C else kap*z[n]/n**3 for n in range(2,25)}
  cand=dict(clock=sum(parts.values())/32,distance=sum(D24[n]*a**n for n in range(2,25))+tb['distance_tail'],scalar=sum(scalar[n]*a**n for n in range(2,25))+tb['scalar_tail'],scalar_derivative=sum(n*scalar[n]*a**n for n in range(2,25))+tb['scalar_euler_tail'])
  keys=dict(clock='clock_tail',distance='distance_tail',scalar='scalar_tail',scalar_derivative='scalar_derivative_tail');sel={k:min(v,Q(old['constants'][keys[k]])) for k,v in cand.items()}
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=sel['clock']/(10*a*a)
  ratios=dict(clock=sum(costs.values()),distance=sel['distance']/(25*a),scalar=sel['scalar']/(a/40000),scalar_derivative=sel['scalar_derivative']/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  expected=dict(q=str(q),eta=str(a),old=old,old_evidence=ev,costs=ss(costs),ratios=ss(ratios),gates=gates,scalar_coefficients=ss(scalar),old_inverse_parts=ss(oldparts),old_inverse_clock_candidate=str(oldcandidate),inverse_tail=str(ij),tail_parts=ss(parts),normalized_parts=ss({k:v/(320*a*a) for k,v in parts.items()}),candidates=ss(cand),selected=ss(sel))
  ck(row==expected,'COMPLETE_POINT_RECORD');ck(all(v<=Q(old['ratios'][k]) for k,v in ratios.items()),'NO_WORSENING')
  summary[str(q)]=dict(eta=float(a),ratios={k:float(v) for k,v in ratios.items()},gates=gates,costs={k:float(v) for k,v in costs.items()},tail_parts={k:float(v/(320*a*a)) for k,v in parts.items()})
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for p,h in pointpins.items():ck(sha(p)==h,'POST_POINT:'+p)
 for n,k in files:ck(sha(ROOT/n)==term[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),points=summary,scope='Independent ordinary Fraction grouped convolution, complete baseline and two-point new records, all five gates and bindings. Positive unresolved tails and analytic/source/coefficient premises inherited from separately audited packets; no independent PDE solution or radius enlargement.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'POSITIVE_TAIL_HALF_READOUT_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('positive_tail_full_review',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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
