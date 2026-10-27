"""Independent Fraction convolution readout; no producer arithmetic imports."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_UNIFORM_POSITIVE_TAIL_BRACKET';CUTOFF=1793108564;COUNT=0
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
 prior=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');tails=auth('20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY/RESULT.json');inv=auth('20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION/RESULT.json');parent=auth('20261027_POSITIVE_TAIL_HALF_RADIUS_READOUT/RESULT.json');result=read(ROOT/'RESULT.json')
 pa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_HALF_READOUT_AUDIT.json');ck(pa['PASS'] and pa['producer_terminal']==sha(BASE/'20261027_POSITIVE_TAIL_HALF_RADIUS_READOUT/TERMINAL.json'),'PARENT_AUDIT')
 base={k:Q(v) for k,v in prior['arms']['both']['constants'].items()};R=base['physical_radius']
 def dic(k):return {int(n):Q(v) for n,v in prior[k].items()}
 D,E,C,F=map(dic,('new_distance24','inverse24','scalar_bounds','new_clock_bounds'))
 ck(set(D)==set(E)==set(range(1,25)) and set(F)==set(range(3,10)),'COVERAGE')
 ck(all(v>=0 for c in (D,E,C,F) for v in c.values()),'POSITIVE_FINITE')
 ck(0<R<min(Q(1,512),Q(25,3840)),'OPENING_DOMAIN')
 star=tails['points']['1/2'];istar=inv['points']['1/2'];ck(Q(star['eta'])==Q(istar['eta'])==R/2,'STAR_IDENTITY')
 tb={k:Q(v) for k,v in star['bounds'].items()};jt=Q(istar['selected_tail']);ck(jt>=0 and all(v>=0 for v in tb.values()),'POSITIVE_TAILS')
 z=list(map(Q,raw['majorant']));kap=Q(tails['weights'][1]);ck(len(z)==25 and Q(tails['constants']['R'])==R,'SAME_NORM_DOMAIN')
 scalar={n:min(C[n],kap*z[n]/n**3) if n in C else kap*z[n]/n**3 for n in range(2,25)}
 ck(result['scalar_coefficients']==ss(scalar),'SCALAR_PREFIX')
 cross={}
 for n,d in D.items():
  for m,e in E.items():
   if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*d*e
 # Fixed rational coefficients, conventional Fraction power evaluation.
 # No import of producer or common-integer-denominator Horner routine.
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def at(q):
  ck(0<q<=Q(1,2),'POINT_DOMAIN');a=R*q;factor=(2*q)**25
  unknownJ=jt*factor;efinite=sum(e*a**n for n,e in E.items());dfinite=sum(n*d*a**n for n,d in D.items())
  parts=dict(finite_distance=sum((n-1)*D[n]*a**n for n in range(10,25)),finite_cross=sum(v*a**n for n,v in cross.items()),unknown_distance=tb['euler_distance_tail']*factor*(1+efinite+unknownJ),unknown_lapse=dfinite*unknownJ)
  selected=dict(clock=sum(parts.values())/32,distance=sum(D[n]*a**n for n in range(2,25))+tb['distance_tail']*factor,scalar=sum(v*a**n for n,v in scalar.items())+tb['scalar_tail']*factor,scalar_derivative=sum(n*v*a**n for n,v in scalar.items())+tb['scalar_euler_tail']*factor)
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=selected['clock']/(10*a*a)
  ratios=dict(clock=sum(costs.values()),distance=selected['distance']/(25*a),scalar=selected['scalar']/(a/40000),scalar_derivative=selected['scalar_derivative']/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  return dict(q=str(q),eta=str(a),selected=ss(selected),costs=ss(costs),ratios=ss(ratios),gates=gates,parts=ss(parts))
 lo,hi=Q(1,4),Q(1,2);low,high=at(lo),at(hi)
 for k in ('selected','costs','ratios','gates'):ck(high[k]==parent['points']['1/2'][k],'EXACT_STAR:'+k)
 ck(all(low['gates'].values()) and not all(high['gates'].values()),'INITIAL_BRACKET')
 ck(result['iterations']==16 and len(result['checkpoints'])==16,'FIXED_COUNT')
 previous=sha(ROOT/'BINDING.json');cpins={}
 for step in range(1,17):
  q=(lo+hi)/2;rec=at(q);passed=all(rec['gates'].values());expected=dict(step=step,record=rec,passed=passed,predecessor_sha256=previous)
  cp=ROOT/('CHECKPOINT_'+str(step).zfill(2)+'.json');ck(read(cp)==expected and result['checkpoints'][step-1]==expected,'EXACT_CHECKPOINT:'+str(step))
  previous=sha(cp);cpins[str(cp)]=previous
  if passed:lo,low=q,rec
  else:hi,high=q,rec
 ck(hi-lo==Q(1,4)/2**16,'EXACT_WIDTH');ck(all(low['gates'].values()) and not all(high['gates'].values()),'FINAL_PASS_FAIL')
 ck(result['lower']==low and result['upper']==high and result['lower_q']==str(lo) and result['upper_q']==str(hi) and result['width_q']==str(hi-lo),'FINAL_RECORDS')
 ck(result['last_checkpoint_sha256']==previous and result['classification']=='UNIFORM_POSITIVE_TAIL_CERTIFICATE_BRACKET','CHAIN_CLASSIFICATION')
 def display(row):return dict(eta=float(Q(row['eta'])),q=float(Q(row['q'])),ratios={k:float(Q(v)) for k,v in row['ratios'].items()},costs={k:float(Q(v)) for k,v in row['costs'].items()},normalized_tail_parts={k:float(Q(v)/(320*Q(row['eta'])**2)) for k,v in row['parts'].items()},gates=row['gates'])
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for p,h in cpins.items():ck(sha(p)==h,'POST_CHECKPOINT:'+p)
 for n,k in files:ck(sha(ROOT/n)==term[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),lower=display(low),upper=display(high),scope='Independent ordinary Fraction convolution and all18 endpoint/midpoint evaluations, full five gates, star replay, sixteen predecessor-hashed checkpoints and exact width. Uniform order25 scaling relies on audited positive-tail domination; this is a sufficient-certificate bracket, not a physical threshold or new radius.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'UNIFORM_POSITIVE_TAIL_BRACKET_AUDIT.json'
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
