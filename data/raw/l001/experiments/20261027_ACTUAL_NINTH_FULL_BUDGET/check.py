"""Audited actual ninth coefficient propagated through the complete budget."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
import math,hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793121042
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
def ss(d):return {str(k):str(v) for k,v in d.items()}
def main(lease):
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt','PINS.json','AUTHORITY.txt')}
 pins=read(ROOT/'PINS.json')
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 std=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('DERIVATION.txt','derivation_sha256')]
 def packet(name,pin,extra,auditname,apin):
  root=BASE/name;bind(root/'TERMINAL.json',pin);term=read(root/'TERMINAL.json');need(term['pass_status'],'PARENT_PASS')
  for n,k in std+extra:bind(root/n,term[k])
  for group in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[group].items():bind(p,h)
  ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/auditname;bind(ap,apin);a=read(ap);need(a['PASS'] and a['producer_terminal']==pin,'AUDIT_MATCH')
  return read(root/'RESULT.json')
 old=packet('20261027_ACTUAL_EIGHTH_FULL_BUDGET','9ff596a88beb1b1947f81e8deb73d630a6033a4b577728b3c958305baab23532',[('check.py','source_sha256')],'ACTUAL_EIGHTH_FULL_BUDGET_AUDIT.json','84bd2bface15205ec12306299c3e2c298b42d67dab1bb5a36696d7318e915450')
 actual9=packet('20261027_NINTH_REAL_SOURCE_ENCLOSURE',pins['real_terminal'],[('run.py','source_sha256'),('flow.py','flow_sha256'),('TRANSPORT_QUALIFICATION.json','transport_sha256'),('PINS.json','pins_sha256')],'NINTH_REAL_AUDIT.json',pins['real_audit'])
 tails=packet('20261027_NINTH_THREE_QUARTER_TAIL',pins['tail_terminal'],[('check.py','source_sha256'),('tail.py','tail_sha256')],'NINTH_THREE_QUARTER_TAIL_AUDIT.json',pins['tail_audit'])
 invtails=packet('20261027_NINTH_THREE_QUARTER_INVERSE_TAIL',pins['inverse_terminal'],[('check.py','source_sha256'),('inverse.py','inverse_sha256'),('PINS.json','pins_sha256')],'NINTH_THREE_QUARTER_INVERSE_TAIL_AUDIT.json',pins['inverse_audit'])
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json')
 actual8=auth('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');seventh=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');generic9=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 R=Q(old['physical_radius']);need(R==Q(tails['constants']['R'])==Q(invtails['constants']['R']),'SAME_RADIUS')
 D={int(k):Q(v) for k,v in old['new_distance16'].items()};D24={int(k):Q(v) for k,v in old['new_distance24'].items()};F={int(k):Q(v) for k,v in old['new_clock_bounds'].items()}
 E24={int(k):Q(v) for k,v in prior['inverse24'].items()};scalar={int(k):Q(v) for k,v in old['scalar_coefficients'].items()};names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 need(all(x>=0 for d in (D,D24,F,E24,scalar) for x in d.values()),'NONNEGATIVE')
 need(0<R<Q(1,512) and R<Q(25,3840),'OPENING_DOWNWARD')
 def polynomial(coeff):
  N=max(coeff);den=1
  for v in coeff.values():den=den*v.denominator//math.gcd(den,v.denominator)
  ints=[coeff.get(n,Q(0)).numerator*(den//coeff.get(n,Q(0)).denominator) for n in range(N+1)]
  def value(q):
   need(0<q<1,'RATIONAL_EVALUATION_DOMAIN')
   p,d=q.numerator,q.denominator;num=ints[-1];power=d
   for n in range(N-1,-1,-1):num=num*p+ints[n]*power;power*=d
   return Q(num,den*d**N)
  return value
 def prepare(bounds,eb):
  bd={n:v*R**n for n,v in bounds.items()};be={n:v*R**n for n,v in eb.items()};cross={}
  for n,b in bd.items():
   for m,e in be.items():
    if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*b*e
  return dict(distance=polynomial({n:(n-1)*b for n,b in bd.items() if n>=10}),cross=polynomial(cross),euler=polynomial({n:n*b for n,b in bd.items()}),inverse=polynomial(be))
 sc=polynomial({n:v*R**n for n,v in scalar.items()});sd=polynomial({n:n*v*R**n for n,v in scalar.items()})
 pp=prepare(D24,E24);ds=polynomial({n:v*R**n for n,v in D24.items() if n>=2})
 qstar=Q(1,2);tb={k:Q(v) for k,v in tails['points']['1/2']['bounds'].items()};jtstar=Q(invtails['points']['1/2']['selected_tail'])
 def uniform(q):
  need(0<q<=qstar,'UNIFORM_DOMAIN');a=R*q;scale=(q/qstar)**25;jt=jtstar*scale
  parts=dict(finite_distance=pp['distance'](q),finite_cross=pp['cross'](q),unknown_distance=tb['euler_distance_tail']*scale*(1+pp['inverse'](q)+jt),unknown_lapse=pp['euler'](q)*jt)
  selected=dict(clock=sum(parts.values())/32,distance=ds(q)+tb['distance_tail']*scale,scalar=sc(q)+tb['scalar_tail']*scale,scalar_derivative=sd(q)+tb['scalar_euler_tail']*scale)
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=selected['clock']/(10*a*a)
  ratios=dict(clock=sum(costs.values()),distance=selected['distance']/(25*a),scalar=selected['scalar']/(a/40000),scalar_derivative=selected['scalar_derivative']/(a/40000))
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  return dict(q=str(q),eta=str(a),selected=ss(selected),costs=ss(costs),ratios=ss(ratios),gates=gates,parts=ss(parts))

 oldlo,oldhi=Q(old['lower_q']),Q(old['upper_q'])
 need(uniform(oldlo)==old['lower'] and uniform(oldhi)==old['upper'],'EXACT_EIGHTH_BRACKET_REPLAY')
 baseline=dict(lower=uniform(oldlo),upper=uniform(oldhi),star=uniform(Q(1,2)))
 oldD,oldD24,oldF=dict(D),dict(D24),dict(F)
 def pair(v):return tuple(map(Q,v['exact_bounds']))
 def mul(x,y):
  p=[a*b for a in x for b in y];return min(p),max(p)
 def scale(x,n):return mul(x,(Q(n),Q(n)))
 def ab(x):return max(map(abs,x))
 def packed(x):return list(map(str,x))
 generic=list(map(Q,generic9['distance']));records={'9':{}};bounds=[]
 for engine in ('primary','independent'):
  vals=clock['arms'][engine]['values'];arr=[(Q(0),Q(0))]+[pair(vals['d'+str(j)]) for j in range(1,4)]+[(-generic[j],generic[j]) for j in range(4,10)]
  arr[4]=tuple(map(Q,fourth['coefficient_intervals'][engine]['d4']));arr[5]=pair(fifth['arms'][engine]['bulk']['d5']);arr[6]=pair(sixth['arms'][engine]['bulk']['d6']);arr[7]=pair(seventh['arms'][engine]['bulk']['d7']);arr[8]=pair(actual8['arms'][engine]['bulk']['d8'])
  ei=[tuple(map(Q,x)) for x in dp['inverse_intervals'][engine]];rate=pair(vals['rate'])
  def evaluate(a):
   total=scale(a[9],8);parts={'leading':packed(mul(rate,total))}
   for j in range(1,9):
    term=scale(mul(a[j],ei[9-j]),j);total=(total[0]+term[0],total[1]+term[1]);parts[str(j)]=packed(mul(rate,term))
   return mul(rate,total),parts
  before,beforeparts=evaluate(arr);stored=old['coefficient_records']['9'][engine]
  need(packed(before)==stored['new'] and ab(before)==Q(stored['new_abs']),'EXACT_OLD_F9')
  arr[9]=pair(actual9['arms'][engine]['bulk']['d9']);after,afterparts=evaluate(arr);bounds.append(ab(after))
  records['9'][engine]=dict(old=packed(before),new=packed(after),old_abs=str(ab(before)),new_abs=str(ab(after)),old_terms=beforeparts,new_terms=afterparts)
 F[9]=min(F[9],max(bounds));d9=max(ab(pair(actual9['arms'][engine]['bulk']['d9'])) for engine in ('primary','independent'))
 D[9]=min(D[9],d9);D24[9]=min(D24[9],d9)
 pp=prepare(D24,E24);ds=polynomial({n:v*R**n for n,v in D24.items() if n>=2})
 halfcontrol=dict(lower=uniform(oldlo),upper=uniform(oldhi),star=uniform(Q(1,2)))
 for k,v in halfcontrol['lower']['ratios'].items():need(Q(v)<=Q(baseline['lower']['ratios'][k]),'HALF_NO_WORSENING:'+k)
 qstar=Q(3,4);star=tails['points']['3/4'];istar=invtails['points']['3/4'];need(Q(star['eta'])==Q(istar['eta'])==R*qstar,'NEW_STAR')
 tb={k:Q(v) for k,v in star['bounds'].items()};jtstar=Q(istar['selected_tail']);need(jtstar>=0 and all(v>=0 for v in tb.values()),'POSITIVE_STAR')
 lo,hi=oldlo,qstar;lower,upper=uniform(lo),uniform(hi);need(all(lower['gates'].values()),'RETAIN_ADMISSION_ON_NEW_TAIL_DOMAIN')
 initial_width=hi-lo;chain=[];previous=sha(ROOT/'BINDING.json')
 if all(upper['gates'].values()):
  lower=upper;lo=hi;classification='PREDECLARED_THREE_QUARTER_ENDPOINT_ADMITTED'
 else:
  classification='ACTUAL_NINTH_COMPLETE_CERTIFICATE_BRACKET'
  for step in range(1,17):
   q=(lo+hi)/2;record=uniform(q);passed=all(record['gates'].values());row=dict(step=step,record=record,passed=passed,predecessor_sha256=previous)
   name='CHECKPOINT_'+str(step).zfill(2)+'.json';put(name,row);previous=sha(ROOT/name);chain.append(row)
   if passed:lo,lower=q,record
   else:hi,upper=q,record
   print(json.dumps(dict(step=step,q=float(q),passed=passed,clock=float(Q(record['ratios']['clock'])))),flush=True)
  need(hi-lo==initial_width/2**16 and all(lower['gates'].values()) and not all(upper['gates'].values()),'FINAL_BRACKET')
 gain=Q(lower['eta'])/Q(baseline['lower']['eta'])
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime and time.time()<CUTOFF,'RUNTIME_WINDOW')
 result=dict(pass_status=True,classification=classification,baseline=baseline,halfcontrol=halfcontrol,lower=lower,upper=upper,iterations=len(chain),lower_q=str(lo),upper_q=str(hi),width_q=str(hi-lo),initial_width_q=str(initial_width),gain_exact=str(gain),physical_radius=str(R),coefficient_records=records,old_clock_bounds=ss(oldF),new_clock_bounds=ss(F),old_distance16=ss(oldD),new_distance16=ss(D),old_distance24=ss(oldD24),new_distance24=ss(D24),actual_d9_bound=str(d9),scalar_coefficients=ss(scalar),checkpoints=chain,last_checkpoint_sha256=previous,seconds=time.monotonic()-start,scope='Actual d9 propagated through full budget with freshly qualified3/4 positive tails. Same analytic radius and five gates. Endpoint admission is not maximal physical amplitude or nonlinear trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt'),pins_sha256=sha(ROOT/'PINS.json')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'],gain=float(gain),eta_lower=float(R*lo),eta_upper=float(R*hi),lower_ratios={k:float(Q(v)) for k,v in lower['ratios'].items()})),flush=True)

if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_bracket_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BRACKET_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
