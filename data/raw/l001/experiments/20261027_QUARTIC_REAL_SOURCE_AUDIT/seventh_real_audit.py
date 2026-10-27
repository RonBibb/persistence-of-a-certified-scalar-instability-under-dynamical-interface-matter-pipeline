"""Exact endpoint seventh audit; qualified algebra inherited, producer flow not imported."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_SEVENTH_REAL_SOURCE_ENCLOSURE';COUNT=0;CUTOFF=1793108564
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
class I:
 def __init__(self,a,b=None):self.lo,self.hi=Q(a),Q(a if b is None else b);ck(self.lo<=self.hi,'INTERVAL_ORDER')
 @staticmethod
 def cast(x):return x if isinstance(x,I) else I(x)
 def __add__(self,x):
  if isinstance(x,Dual):return NotImplemented
  x=self.cast(x);return I(self.lo+x.lo,self.hi+x.hi)
 __radd__=__add__
 def __neg__(self):return I(-self.hi,-self.lo)
 def __sub__(self,x):
  if isinstance(x,Dual):return NotImplemented
  return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  if isinstance(x,Dual):return NotImplemented
  x=self.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.cast(x);ck(x.lo*x.hi>0,'NONZERO_DIVISOR');v=[a/b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 def __pow__(self,n):
  ck(isinstance(n,int) and n>=0,'NONNEGATIVE_POWER');out=I(1)
  for _ in range(n):out=out*self
  return out
 def abs(self):return max(abs(self.lo),abs(self.hi))
def iv(x):return I(*x['exact_bounds'])
def square(x):return I(0 if x.lo<=0<=x.hi else min(x.lo*x.lo,x.hi*x.hi),max(x.lo*x.lo,x.hi*x.hi))
def enclosed(saved,x,label):
 y=iv(saved);ck(y.lo<=x.lo<=x.hi<=y.hi,label)
def polynomial(qual,v,key):
 rows=qual['sources'][key];names=qual['variables'];maxima=[max((a['powers'][j] for a in rows),default=0) for j in range(len(names))]
 powers=[[v[k]**n for n in range(m+1)] for k,m in zip(names,maxima)];out=I(0)
 for row in rows:
  term=I(Q(row['coefficient']))
  for j,n in enumerate(row['powers']):
   if n:term=term*powers[j][n]
  out+=term
 return out
class Dual:
 def __init__(self,v,d=0):self.v=I.cast(v);self.d=I.cast(d)
 @staticmethod
 def cast(x):return x if isinstance(x,Dual) else Dual(x)
 def __add__(self,x):
  x=self.cast(x);return Dual(self.v+x.v,self.d+x.d)
 __radd__=__add__
 def __neg__(self):return Dual(-self.v,-self.d)
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  x=self.cast(x);return Dual(self.v*x.v,self.d*x.v+self.v*x.d)
 __rmul__=__mul__
 def __truediv__(self,n):return Dual(self.v/n,self.d/n)
def lower(v,p,cubic,quartic):
 args=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')]
 return cubic.cubic(*args,p),quartic.quartic(*args,v['p3'],v['f3'],v['g3'],p,cubic)
def expcoeff(bs,N):
 a=[I(1)]
 for n in range(1,N+1):a.append(sum((j*bs[j]*a[n-j] for j in range(1,n+1)),I(0))/n)
 return a
def extended_variables(old,fc,p):
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h'];ck((7*r-h).lo>0,'TRACE7_DIVISOR')
 v.update(p6=I(-Q(fc['p6_bound']),Q(fc['p6_bound'])),f6=I(-Q(fc['f6_bound']),Q(fc['f6_bound'])),g6=I(-Q(fc['f6prime_bound']),Q(fc['f6prime_bound'])),N7=r/(7*(7*r-h)),p7=I(0),f7=I(0),g7=I(0));return v
def transport_identity(ring):
 names=tuple(['x'+str(n) for n in range(2,8)]+['b'+str(n) for n in range(1,6)]+['b1p','b2p','b3p','b1pp'])
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(i) for i,k in enumerate(names)};z=ring.P(0)
 def product(a,b):return [sum((a[j]*b[n-j] for j in range(n+1)),z) for n in range(8)]
 bs=[z]+[v['b'+str(n)] for n in range(1,6)]+[z,z];ex=[ring.P(1)]
 for n in range(1,8):ex.append(sum((j*bs[j]*ex[n-j] for j in range(1,n+1)),z)/n)
 bp=[z,v['b1p'],v['b2p'],v['b3p'],z,z,z,z];ep=product(ex,bp)
 bpp=[z,v['b1pp'],z,z,z,z,z,z];epp=product(ex,[x+y for x,y in zip(bpp,product(bp,bp))])
 xi=[z,z]+[v['x'+str(n)] for n in range(2,8)];x2=product(xi,xi);x3=product(x2,xi)
 direct=product(xi,ex)[7]+product(x2,ep)[7]/2+product(x3,epp)[7]/6
 x,y,w=[v[k] for k in ('x2','x3','x4')];b=v['b1'];b1p=v['b1p']
 expanded=v['x7']+v['x6']*b+v['x5']*ex[2]+w*ex[3]+y*ex[4]+x*ex[5]+x*x*(v['b3p']+b1p*v['b2']+b*v['b2p']+b*b*b1p/2)/2+x*y*(v['b2p']+b*b1p)+(x*w+y*y/2)*b1p+x*x*x*v['b1pp']/6
 ck((direct-expanded).iszero(),'INDEPENDENT_TRANSPORT7_COEFFICIENT')
 ck(not (direct-expanded-x*x*x*v['b1pp']/6).iszero(),'THIRD_TRANSPORT_MUTATION')
def endpoint(saved,old,fc,p,sigma,wall,qual,jets):
 v=extended_variables(old['source_variables'],fc,p);w={k:iv(x) for k,x in old['inputs'].items()};q={k:iv(x) for k,x in old['quantities'].items()}
 for k,x in v.items():enclosed(saved['source_variables'][k],x,'ENDPOINT_VARIABLE:'+k)
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];r,h=p['rate'],p['h'];Tp=w['Tp']
 ck(q['d6_wall'].lo>0,'SIXTH_WALL_DIVISOR')
 updates=dict(p6=v['p6'],f6=v['f6'],g6=v['g6'],c6=q['c6'],xi6=q['xi6'],chi6=(v['f6']+T*q['xi6']-q['o6'])/q['d6_wall'])
 for k in ('u5','g5prime','c5prime','u3prime','g3second','c3second','u1second','g1third'):
  x=polynomial(jets,v,k);updates[k]=x;enclosed(saved['jets'][k],x,'QUALIFIED_EXPANDED_JET:'+k)
 for k,x in updates.items():enclosed(saved['inputs'][k],x,'NEW_ENDPOINT_INPUT:'+k)
 for k in w:
  if k not in updates:ck(saved['inputs'][k]==old['inputs'][k],'UNCHANGED_ENDPOINT_INPUT:'+k)
 sw={k:iv(x) for k,x in saved['inputs'].items()};sv={k:iv(x) for k,x in saved['source_variables'].items()};sq=saved['quantities'];direct=wall.direct(sw,sigma)
 for k,row in [('o7','O'),('j7','J'),('qI7','graph')]:enclosed(sq[k],direct[row].a[7],'QUALIFIED_WALL_LOAD:'+k)
 for k in ('c7','Sc7'):enclosed(sq[k],polynomial(qual,sv,k),'WALL_SOURCE:'+k)
 div=7*sigma*e*r*(7*r-h);mu=-7*r*(7*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*square(T);dw=2-mu*e
 ck((div.lo>0 or div.hi<0) and J.lo>0 and D.lo>0 and dw.lo>0,'WALL_POSITIVITY')
 for k,x in [('graph_divisor',div),('J7',J),('D7',D),('d7_wall',dw)]:enclosed(sq[k],x,'WALL_DIVISOR:'+k)
 enclosed(sq['xi7'],-iv(sq['qI7'])/iv(sq['graph_divisor']),'XI7')
 xi=iv(sq['xi7']);gamma=21-I(1)/iv(sq['d7_wall']);R=2*sigma*(T*iv(sq['c7'])-Tp*xi-iv(sq['j7']))+gamma*T*xi+iv(sq['o7'])/iv(sq['d7_wall'])
 enclosed(sq['R7'],R,'R7');enclosed(sq['robin'],-iv(sq['D7'])*iv(sq['R7'])/(2*iv(sq['J7']))+2*sigma*T*iv(sq['Sc7'])/iv(sq['J7']),'ROBIN7')
 b1=-2*a;b2=sw['c2']-2*P;b3=sw['c3']-2*v['p3'];b4=sw['c4']-2*v['p4'];b5=sw['c5']-2*v['p5'];ex=expcoeff([I(0),b1,b2,b3,b4,b5],5)
 b1p=-2*sw['u1'];b2p=sw['c2prime']-2*sw['u2'];b3p=sw['c3prime']-2*sw['u3'];ep2=b2p+b1*b1p;ep3=b3p+b1p*b2+b1*b2p+b1*b1*b1p/2
 x2,x3,x4=sw['xi2'],sw['xi3'],sw['xi4']
 transport=xi+sw['xi6']*b1+sw['xi5']*ex[2]+x4*ex[3]+x3*ex[4]+x2*ex[5]+x2*x2*ep3/2+x2*x3*ep2+(x2*x4+x3*x3/2)*b1p+x2*x2*x2*(-2*sw['u1prime'])/6
 enclosed(sq['transport'],transport,'EXACT_IDENTITY_QUALIFIED_TRANSPORT7')
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,hsh in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==hsh,'BOUND:'+p);bound[p]=hsh
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 def module(n,path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'MODULE_AUTH:'+path);return load(n,p)
 ring=module('seventh_transport_ring','20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py');transport_identity(ring)
 cubic=module('seventh_old_cubic','20261026_GROWING_MODE_CUBIC_FLOW/sources.py');quartic=module('seventh_old_quartic','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall=module('seventh_qualified_wall','20261027_SEVENTH_WALL_QUALIFICATION/wall.py')
 qual=auth('20261027_SEVENTH_BULK_QUALIFICATION/RESULT.json');jets=auth('20261027_SEVENTH_JET_QUALIFICATION/RESULT.json');globaldata=auth('20261027_QUINTIC_GLOBAL_BULK_PROBE/RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');inverse=auth('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json')
 ck(qual['pass_status'] and jets['pass_status'] and inverse['scientific_certificate'],'QUALIFICATIONS')
 ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_JET_AUDIT.json')['PASS'],'JET_AUDIT_PASS')
 ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_BULK_AUDIT.json')['PASS'],'BULK_AUDIT_PASS')
 ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_WALL_AUDIT.json')['PASS'],'WALL_AUDIT_PASS')
 ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SIXTH_REAL_AUDIT_R1.json')['PASS'],'SIXTH_AUDIT_PASS')
 result=read(ROOT/'RESULT.json');reports={}
 for engine in ('primary','independent'):
  arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');old=sixth['arms'][engine];saved=result['arms'][engine]
  ck(read(ROOT/('ARM_'+engine+'.json'))==saved,'ARM_COPY');ck(arm['D']==initial['D'],'DOMAIN')
  for k,x in initial['parameters'].items():ck(arm['parameters'][k]==x,'PARAMETER:'+k)
  p={k:iv(x) for k,x in arm['parameters'].items()};v=extended_variables(old['source_variables'],old['constants'],p)
  for k,x in v.items():enclosed(saved['source_variables'][k],x,'GLOBAL_VARIABLE:'+k)
  for k in ('c7','Sp7','Sc7','Sg7'):enclosed(saved['sources'][k],polynomial(qual,v,k),'GLOBAL_SOURCE:'+k)
  H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];r,h,m=p['rate'],p['h'],p['m2'];mu=-7*r*(7*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*square(T);B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;sb=saved['bulk'];src={k:iv(x) for k,x in saved['sources'].items()}
  ck((7*r-h).lo>0 and J.lo>0 and D.lo>0,'GLOBAL_POSITIVITY')
  for k,x in [('J7',J),('D7',D),('B0',B),('Tp',Tp)]:enclosed(sb[k],x,'GLOBAL_QUANTITY:'+k)
  enclosed(sb['forcing'],src['Sg7']+B*src['Sc7']/D,'FORCING7')
  for side,sg in [('lower',1),('upper',-1)]:endpoint(saved['walls'][side],old['walls'][side],old['constants'],p,sg,wall,qual,jets)
  cf=Q(inverse['arms'][engine]['finite_orders']['7']['constant'])*Q(inverse['arms'][engine]['f_transfer_multiplier']);G=max(iv(w['quantities']['robin']).abs() for w in saved['walls'].values());size=iv(sb['forcing']).abs()+7*G;fb=cf*size/49;gb=cf*size/7;pb=(src['Sc7'].abs()+T.abs()*gb+iv(sb['Tp']).abs()*fb)/iv(sb['D7']).lo;length=I(*arm['D']);metric=2*length.hi*pb
  ck(cf>0 and length.lo>0,'INVERSE_DOMAIN')
  for k,x in dict(Cf7=cf,Robin_abs=G,source_size=size,f7_bound=fb,f7prime_bound=gb,p7_bound=pb,metric_integral_bound=metric).items():ck(Q(saved['constants'][k])==x,'EXACT_INVERSE:'+k)
  s3,s4=lower(v,p,cubic,quartic);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f'])
  bs=[I(0),-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],iv(globaldata['arms'][engine]['sources']['c5'])-2*v['p5'],iv(old['sources']['c6'])-2*v['p6'],src['c7']]
  enclosed(sb['density'],expcoeff(bs,7)[7],'DENSITY7');enclosed(sb['integral'],iv(sb['density'])*length,'INTEGRAL7')
  known=iv(saved['walls']['upper']['quantities']['transport'])-iv(saved['walls']['lower']['quantities']['transport'])+iv(sb['integral']);enclosed(sb['known'],known,'KNOWN7');enclosed(sb['d7'],iv(sb['known'])+I(-metric,metric),'DISTANCE7')
  reports[engine]=dict(d7_display=[float(iv(sb['d7']).lo),float(iv(sb['d7']).hi)],source_size_display=float(size))
 vals=[iv(result['arms'][e]['bulk']['d7']) for e in ('primary','independent')];ck(max(x.lo for x in vals)<=min(x.hi for x in vals),'COMPATIBILITY_ONLY');enclosed(result['d7'],I(min(x.lo for x in vals),max(x.hi for x in vals)),'FINAL_HULL')
 for p,hsh in bound.items():ck(sha(p)==hsh,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=reports,scope='Independent unrounded interval arithmetic for expanded qualified jets and sources, seventh wall loads, finite-n7 inverse and distance. Transport7 independently qualified by exact symbolic convolution then strictly checked in expanded grouping. No producer flow imported; original source/wall expressions and lower enclosures inherited. No seventh profile or signed coefficient.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'SEVENTH_REAL_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('seventh_actual_audit_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
