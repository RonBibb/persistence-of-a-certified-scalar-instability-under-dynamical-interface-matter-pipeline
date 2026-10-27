"""Audited actual eighth coefficient propagated through the complete budget."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
import math,hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793112729
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
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE';bind(parent/'TERMINAL.json','7a52079f0b25cb3866af673880a12083aeb7aa98cb0be378fed13d47e8d43b80');t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/fn,t[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/ACTUAL_SEVENTH_CLOCK_AUDIT.json';bind(ap,'2ea421a29c59c6e4371857531b5e9675b51e9116b6e9863add64c1a7849b8337');ar=read(ap);need(ar['PASS'] and ar['producer_terminal']==sha(parent/'TERMINAL.json'),'AUDIT_MATCH')
 bind(ap.with_name('actual_seventh_clock_audit.py'),ar['audit_source_sha256'])
 authority=ROOT/'AUTHORITY.txt';sources[str(authority)]=sha(authority)
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=read(parent/'RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json')

 tr=BASE/'20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY';bind(tr/'TERMINAL.json','dc5d2b4e5675c4ec97231ca431c3833f5f6ab917c903abddf11e8059a28249d5');tt=read(tr/'TERMINAL.json');need(tt['pass_status'],'TAIL_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('tail.py','tail_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(tr/fn,tt[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(tr/'BINDING.json')[group].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_HALF_RADIUS_AUDIT.json';bind(ap,'7a58097c76c301cfac3c214843da695546c9599f8f6a0ab3acaf02b80ea29e47');ar=read(ap);need(ar['PASS'] and ar['producer_terminal']==sha(tr/'TERMINAL.json'),'TAIL_AUDIT')
 bind(ap.with_name('positive_tail_half_radius_audit.py'),ar['audit_source_sha256'])
 tails=read(tr/'RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json')


 ir=BASE/'20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION';bind(ir/'TERMINAL.json','244db5773ee28fde29bdc2e3d240d2a414ce80a6c743a9bd6546b4c21f0a6ded');it=read(ir/'TERMINAL.json');need(it['pass_status'],'INVERSE_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('inverse.py','inverse_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(ir/fn,it[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(ir/'BINDING.json')[group].items():bind(p,h)
 ia=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_INVERSE_TAIL_AUDIT.json';bind(ia,'4aeb5c97acbc551ea955f7d227790c8f52207fd2727bba9295df88103740f082');need(read(ia)['PASS'] and read(ia)['producer_terminal']==sha(ir/'TERMINAL.json'),'INVERSE_AUDIT')
 invtails=read(ir/'RESULT.json')

 finalparent=BASE/'20261027_POSITIVE_TAIL_HALF_RADIUS_READOUT';bind(finalparent/'TERMINAL.json','c43f66888ac5708ad65230b1d02edcb4b42984a68c1c0ce50b4e39c047d98be1');pt=read(finalparent/'TERMINAL.json');need(pt['pass_status'],'READOUT_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(finalparent/fn,pt[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(finalparent/'BINDING.json')[group].items():bind(p,h)
 pa=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_HALF_READOUT_AUDIT.json';bind(pa,'c331ba14b4d11354681a11aa7ca0cd0de7ffaed3a033203b63b53dcd90770851');need(read(pa)['PASS'] and read(pa)['producer_terminal']==sha(finalparent/'TERMINAL.json'),'READOUT_AUDIT')
 parentread=read(finalparent/'RESULT.json')

 def additional(name,pin,fields,auditname,auditpin):
  root=BASE/name;bind(root/'TERMINAL.json',pin);tt=read(root/'TERMINAL.json');need(tt['pass_status'],'ADDITIONAL_PASS')
  for fn,key in fields:bind(root/fn,tt[key])
  for group in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[group].items():bind(p,h)
  ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/auditname;bind(ap,auditpin);ar=read(ap);need(ar['PASS'] and ar['producer_terminal']==pin,'ADDITIONAL_AUDIT')
  return read(root/'RESULT.json')
 std=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('DERIVATION.txt','derivation_sha256')]
 oldbracket=additional('20261027_UNIFORM_POSITIVE_TAIL_BRACKET','50ddb33ca4c0e0b8288cd444f5f80e7673dc8f9a31f3be620ab6c97c932ae11e',std+[('check.py','source_sha256')],'UNIFORM_POSITIVE_TAIL_BRACKET_AUDIT.json','db4e02fa3fa966ed440bca1da1907d23becdd39212fcda35a3bb3abf980bfe46')
 actual8=additional('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE','f9cf4da45aec7f49c222878c9b6044aae66fd52eaea5eac60f24a6913c0cb8c1',std+[('run.py','source_sha256'),('flow.py','flow_sha256'),('TRANSPORT_QUALIFICATION.json','transport_sha256')],'EIGHTH_REAL_AUDIT.json','8558df591fefd19b7f1176514b1fbcbcde799c1c78c32b64be606daee1e9e5e3')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');seventh=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json')

 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inherited=prior['arms']['both'];base={k:Q(v) for k,v in inherited['constants'].items()};R,MD,Y=[base[k] for k in ('physical_radius','observable_sup','aggregate_bound')];JC=Q(dp['global_departure']['coefficient_tail_sup'])
 newD={int(k):Q(v) for k,v in prior['new_distance16'].items()};newD24={int(k):Q(v) for k,v in prior['new_distance24'].items()};D,D24=newD,newD24
 E={int(k):Q(v) for k,v in prior['inverse8'].items()};E24={int(k):Q(v) for k,v in prior['inverse24'].items()};C={int(k):Q(v) for k,v in prior['scalar_bounds'].items()};newF={int(k):Q(v) for k,v in prior['new_clock_bounds'].items()};F=newF;names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 need(all(x>=0 for bounds in (D,D24,E,E24,C,F) for x in bounds.values()),'NONNEGATIVE_CERTIFICATE_BOUNDS')
 need(0<R<Q(1,512) and R<Q(25,3840),'OPENING_DOWNWARD_ON_DOMAIN')
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
 prepared={}
 for changed,da,db in [(True,newD,newD24)]:
  for bounds,eb in [(da,E),(db,E),(db,E24)]:prepared[changed,max(bounds),max(eb)]=prepare(bounds,eb)
 def at(q):
  propagate=coeff=True
  da,db=(newD,newD24) if propagate else (D,D24);fb=newF if coeff else F
  a=R*q;options=[]
  for th,row in dp['contour_records'].items():
   theta=Q(th);z=a/(theta*R)
   if z<1:options.append((Q(row['both'])*z**10/(1-z),theta,Q(row['both'])))
  ct,theta,sup=min(options,key=lambda x:x[0])
  def direct(bounds,eb):
   N=max(bounds);M=max(eb);polys=prepared[propagate,N,M];jt=JC*q**(M+1)/(1-q);ed=polys['inverse'](q)+jt;wd=polys['euler'](q)
   return dict(finite_distance=polys['distance'](q),finite_cross=polys['cross'](q),distance_tail=MD*q**(N+1)*(N-(N-1)*q)/(1-q)**2,unknown_distance_product=MD*q**(N+1)*(N+1-N*q)/(1-q)**2*ed,unknown_lapse_product=wd*jt)
  p16,p24,pnew=direct(da,E),direct(db,E),direct(db,E24);t16,t24,tnew=[sum(p.values())/32 for p in (p16,p24,pnew)];old=min(ct,t16,t24);tail=min(old,tnew)
  costs={names[n]:v*a**n/(10*a*a) for n,v in fb.items()};costs['unknown_tail']=tail/(10*a*a)
  d0=MD*q*q/(1-q);d9=sum(da[n]*a**n for n in range(2,10))+MD*q**10/(1-q);d16=sum(da[n]*a**n for n in range(2,17))+MD*q**17/(1-q);d24=sum(db[n]*a**n for n in range(2,25))+MD*q**25/(1-q);dist=min(d0,d9,d16,d24)
  st=min(C[2]*a*a+C[3]*a**3+Y*q**4/(1-q),sum(v*a**n for n,v in C.items())+Y*q**10/(1-q));sd=min(2*C[2]*a*a+3*C[3]*a**3+Y*q**4*(4-3*q)/(1-q)**2,sum(n*v*a**n for n,v in C.items())+Y*q**10*(10-9*q)/(1-q)**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*a),scalar=st/(a/40000),scalar_derivative=sd/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  constants=dict(base,clock_eta=a,clock_tail=tail,distance_tail=dist,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=a/40000);constants.update({'known_'+names[n]:v*a**n for n,v in fb.items()})
  rec=dict(constants=ss(constants),costs=ss(costs),ratios=ss(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates=dict(old=str(d0),retained=str(d9),retained16=str(d16),retained24=str(d24)))
  ev=dict(contour=str(ct),direct16=str(t16),direct24=str(t24),finite_inverse24=str(tnew),normalized_old=ss({k:v/(320*a*a) for k,v in p24.items()}),normalized_new=ss({k:v/(320*a*a) for k,v in pnew.items()}),selected=str(tail),theta_describes_fallback=True)
  return rec,ev

 # Uniform fixed-radius tails, each beginning at order25.
 star=tails['points']['1/2'];istar=invtails['points']['1/2'];need(Q(star['eta'])==Q(istar['eta'])==R/2,'STAR_POINT')
 tb={k:Q(v) for k,v in star['bounds'].items()};jtstar=Q(istar['selected_tail']);need(jtstar>=0 and all(v>=0 for v in tb.values()),'POSITIVE_STAR_TAILS')
 z=list(map(Q,raw['majorant']));kap=Q(tails['weights'][1]);scalar={n:min(C[n],kap*z[n]/n**3) if n in C else kap*z[n]/n**3 for n in range(2,25)}
 sc=polynomial({n:v*R**n for n,v in scalar.items()});sd=polynomial({n:n*v*R**n for n,v in scalar.items()});ds=polynomial({n:v*R**n for n,v in D24.items() if n>=2})
 pp=prepared[True,24,24]
 def uniform(q):
  need(0<q<=Q(1,2),'UNIFORM_DOMAIN');a=R*q;scale=(2*q)**25;jt=jtstar*scale
  parts=dict(finite_distance=pp['distance'](q),finite_cross=pp['cross'](q),unknown_distance=tb['euler_distance_tail']*scale*(1+pp['inverse'](q)+jt),unknown_lapse=pp['euler'](q)*jt)
  selected=dict(clock=sum(parts.values())/32,distance=ds(q)+tb['distance_tail']*scale,scalar=sc(q)+tb['scalar_tail']*scale,scalar_derivative=sd(q)+tb['scalar_euler_tail']*scale)
  costs={names[n]:v*a**n/(10*a*a) for n,v in F.items()};costs['unknown_tail']=selected['clock']/(10*a*a)
  ratios=dict(clock=sum(costs.values()),distance=selected['distance']/(25*a),scalar=selected['scalar']/(a/40000),scalar_derivative=selected['scalar_derivative']/(a/40000))
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
  return dict(q=str(q),eta=str(a),selected=ss(selected),costs=ss(costs),ratios=ss(ratios),gates=gates,parts=ss(parts))

 oldlo,oldhi=Q(oldbracket['lower_q']),Q(oldbracket['upper_q'])
 need(uniform(oldlo)==oldbracket['lower'] and uniform(oldhi)==oldbracket['upper'],'EXACT_OLD_BRACKET_REPLAY')
 oldstar=uniform(Q(1,2))
 for k in ('selected','costs','ratios','gates'):need(oldstar[k]==parentread['points']['1/2'][k],'EXACT_STAR_READOUT:'+k)
 baseline=dict(lower=uniform(oldlo),upper=uniform(oldhi),star=oldstar)
 oldD,oldD24,oldF=dict(newD),dict(newD24),dict(newF)
 def pair(v):return tuple(map(Q,v['exact_bounds']))
 def mul(x,y):
  products=[a*b for a in x for b in y];return min(products),max(products)
 def scale(x,n):return mul(x,(Q(n),Q(n)))
 def ab(x):return max(map(abs,x))
 def packed(x):return list(map(str,x))
 generic=list(map(Q,ninth['distance']));records={}
 for n in (8,9):
  records[str(n)]={};bound=[]
  for engine in ('primary','independent'):
   vals=clock['arms'][engine]['values'];arr=[(Q(0),Q(0))]+[pair(vals['d'+str(j)]) for j in range(1,4)]+[(-generic[j],generic[j]) for j in range(4,n+1)]
   arr[4]=tuple(map(Q,fourth['coefficient_intervals'][engine]['d4']));arr[5]=pair(fifth['arms'][engine]['bulk']['d5']);arr[6]=pair(sixth['arms'][engine]['bulk']['d6']);arr[7]=pair(seventh['arms'][engine]['bulk']['d7'])
   ei=[tuple(map(Q,x)) for x in dp['inverse_intervals'][engine]];rate=pair(vals['rate'])
   def evaluate(a):
    total=scale(a[n],n-1);parts={'leading':packed(mul(rate,total))}
    for j in range(1,n):
     term=scale(mul(a[j],ei[n-j]),j);total=(total[0]+term[0],total[1]+term[1]);parts[str(j)]=packed(mul(rate,term))
    return mul(rate,total),parts
   old,oldparts=evaluate(arr);stored=prior['coefficient_records'][str(n)][engine]
   need(packed(old)==stored['new'] and ab(old)==Q(stored['new_abs']),'EXACT_OLD_CLOCK_COEFFICIENT')
   arr[8]=pair(actual8['arms'][engine]['bulk']['d8']);new,parts=evaluate(arr);bound.append(ab(new))
   records[str(n)][engine]=dict(old=packed(old),new=packed(new),old_abs=str(ab(old)),new_abs=str(ab(new)),old_terms=oldparts,new_terms=parts)
  newF[n]=min(oldF[n],max(bound))
 d8=max(ab(pair(actual8['arms'][engine]['bulk']['d8'])) for engine in ('primary','independent'))
 newD[8]=min(oldD[8],d8);newD24[8]=min(oldD24[8],d8)
 for bounds,eb in [(newD,E),(newD24,E),(newD24,E24)]:prepared[True,max(bounds),max(eb)]=prepare(bounds,eb)
 pp=prepared[True,24,24];ds=polynomial({n:v*R**n for n,v in newD24.items() if n>=2})
 lower,upper=uniform(oldlo),uniform(Q(1,2));need(all(lower['gates'].values()),'RETAIN_OLD_ADMISSION')
 for key in lower['ratios']:need(Q(lower['ratios'][key])<=Q(baseline['lower']['ratios'][key]),'NO_WORSENING')
 lo,hi=oldlo,Q(1,2);initial_width=hi-lo;chain=[];previous=sha(ROOT/'BINDING.json');domain_pass=all(upper['gates'].values())
 if domain_pass:
  lower=upper;lo=hi;classification='PREDECLARED_DOMAIN_ENDPOINT_ADMITTED'
 else:
  classification='ACTUAL_EIGHTH_COMPLETE_CERTIFICATE_BRACKET'
  for step in range(1,17):
   q=(lo+hi)/2;record=uniform(q);passed=all(record['gates'].values());row=dict(step=step,record=record,passed=passed,predecessor_sha256=previous)
   name='CHECKPOINT_'+str(step).zfill(2)+'.json';put(name,row);previous=sha(ROOT/name);chain.append(row)
   if passed:lo,lower=q,record
   else:hi,upper=q,record
   print(json.dumps(dict(step=step,q=float(q),passed=passed,clock=float(Q(record['ratios']['clock'])))),flush=True)
  need(hi-lo==initial_width/2**16 and all(lower['gates'].values()) and not all(upper['gates'].values()),'FINAL_BRACKET')
 gain=Q(lower['eta'])/Q(baseline['lower']['eta'])
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime and time.time()<CUTOFF,'RUNTIME_AND_WINDOW')
 result=dict(pass_status=True,classification=classification,baseline=baseline,lower=lower,upper=upper,iterations=len(chain),lower_q=str(lo),upper_q=str(hi),width_q=str(hi-lo),initial_width_q=str(initial_width),gain_exact=str(gain),physical_radius=str(R),coefficient_records=records,old_clock_bounds=ss(oldF),new_clock_bounds=ss(newF),old_distance16=ss(oldD),new_distance16=ss(newD),old_distance24=ss(oldD24),new_distance24=ss(newD24),actual_d8_bound=str(d8),scalar_coefficients=ss(scalar),checkpoints=chain,last_checkpoint_sha256=previous,seconds=time.monotonic()-start,scope='Actual d8 propagated through full uniform positive-tail certificate. Fixed radius, inverse/scalar/tail bounds and five gates. Amplitude gain is sufficient-certificate improvement, not a physical threshold or nonlinear trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'],eta_lower=float(R*lo),eta_upper=float(R*hi),lower_ratios={k:float(Q(v)) for k,v in lower['ratios'].items()})),flush=True)

if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('seventh_bracket_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('BRACKET_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
