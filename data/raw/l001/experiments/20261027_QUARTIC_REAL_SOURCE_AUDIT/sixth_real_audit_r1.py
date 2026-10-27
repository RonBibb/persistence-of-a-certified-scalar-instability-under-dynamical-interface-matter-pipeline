"""Exact endpoint sixth audit; qualified algebra inherited, producer flow not imported."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_SIXTH_REAL_SOURCE_ENCLOSURE';COUNT=0;CUTOFF=1793101111
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
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h']
 v.update(p5=I(-Q(fc['p5_bound']),Q(fc['p5_bound'])),f5=I(-Q(fc['f5_bound']),Q(fc['f5_bound'])),g5=I(-Q(fc['f5prime_bound']),Q(fc['f5prime_bound'])),N6=r/(6*(6*r-h)),p6=I(0),f6=I(0),g6=I(0));return v
def endpoint(saved,old,fc,p,sigma,cubic,quartic,wall,qual):
 v=extended_variables(old['source_variables'],fc,p);w={k:iv(x) for k,x in old['inputs'].items()};q={k:iv(x) for k,x in old['quantities'].items()}
 for k,x in v.items():enclosed(saved['source_variables'][k],x,'ENDPOINT_VARIABLE:'+k)
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];m,r,h=p['m2'],p['rate'],p['h'];k=p['k']
 Hp,Tp,u,U,gp,Gp,up=[w[x] for x in ('Hp','Tp','u1','u2','g1prime','g2prime','u1prime')];c,cp=w['c2'],w['c2prime'];s3,s4=lower(v,p,cubic,quartic)
 # Independently differentiate lower expressions by dual arithmetic.
 hd,td,pd,ed=Dual(H,Hp),Dual(T,Tp),Dual(Phi,T),Dual(e,-2*H*e)
 ad,fd,gd,ud=Dual(a,u),Dual(f,g),Dual(g,gp),Dual(u,up)
 cd=Dual(c,cp);sp=hd*cd-ad*ud-fd*gd/6
 cpp=(-p['c_factor']*(12*ad*ud+2*fd*gd)).d
 sg=td*Dual(cp,cpp)+2*m*pd*cd-6*td*sp-((4*m-6*p['mu1']*ed)*ad*fd+6*ud*gd-8*m*pd*ad*ad)
 Upp=(-2*hd*Dual(P,U)-td*Dual(F,G)/3+sp).d
 Bd=12*hd*td-4*m*pd
 Gpp=(-4*hd*Dual(G,Gp)+(m-p['mu2']*ed+2*td*td)*Dual(F,G)+Bd*Dual(P,U)+sg).d
 Hpp=(-td*td/3-p['k']*ed).d
 Tppp=m*Tp-4*(Hpp*T+2*Hp*Tp+H*w['Tpp'])
 c4p=(-p['c4_factor']*(36*ad*Dual(v['p3'],w['u3'])+24*Dual(P,U)*Dual(P,U)+6*fd*Dual(v['f3'],v['g3'])+4*Dual(F,G)*Dual(F,G)-18*ad*Dual(s3['c3'],w['c3prime'])-24*Dual(P,U)*cd+4*cd*cd)).d
 B=12*H*T-4*m*Phi;mu4=-4*r*(4*r+3*h)
 u4=-2*H*v['p4']-T*v['f4']/3+s4['Sp4'];g4p=-4*H*v['g4']+(m-mu4*e+2*square(T))*v['f4']+B*v['p4']+s4['Sg4']
 ck(q['d5_wall'].lo>0,'FIFTH_DIVISOR')
 updates=dict(p5=v['p5'],f5=v['f5'],g5=v['g5'],c5=q['c5'],xi5=q['xi5'],chi5=(v['f5']+T*q['xi5']-q['o5'])/q['d5_wall'],u4=u4,g4prime=g4p,c4prime=c4p,u2prime=Upp,g2second=Gpp,c2second=cpp,Hpp=Hpp,Tppp=Tppp)
 # These six derivatives use exact-symbolically-qualified expanded grouping; no tolerance.
 expanded=JETS.expanded(v,w,dict(p,_T2=square(T)),s3)
 for key in ('c2second','u2prime','g2second','Hpp','Tppp','c4prime'):updates[key]=expanded[key]
 for key,x in updates.items():enclosed(saved['inputs'][key],x,'DUAL_OR_ENDPOINT_JET:'+key)
 for key,x in w.items():
  if key not in updates:ck(saved['inputs'][key]==old['inputs'][key],'UNCHANGED_JET:'+key)
 sw={k:iv(x) for k,x in saved['inputs'].items()};sv={k:iv(x) for k,x in saved['source_variables'].items()};sq=saved['quantities'];direct=wall.direct(sw,sigma)
 for key,row in [('o6','O'),('j6','J'),('qI6','graph')]:enclosed(sq[key],direct[row].a[6],'QUALIFIED_WALL_LOAD:'+key)
 for key in ('c6','Sc6'):enclosed(sq[key],polynomial(qual,sv,key),'QUALIFIED_WALL_POLYNOMIAL:'+key)
 divisor=6*sigma*e*r*(6*r-h);mu6=-6*r*(6*r+3*h);J=-3*(mu6+4*p['k'])*e;D=J+2*square(T);dw=2-mu6*e
 ck((divisor.lo>0 or divisor.hi<0) and J.lo>0 and D.lo>0 and dw.lo>0,'WALL_POSITIVITY')
 for key,x in [('graph_divisor',divisor),('J6',J),('D6',D),('d6_wall',dw)]:enclosed(sq[key],x,'WALL_DIVISOR:'+key)
 enclosed(sq['xi6'],-iv(sq['qI6'])/iv(sq['graph_divisor']),'XI6')
 xi=iv(sq['xi6']);gamma=21-I(1)/iv(sq['d6_wall']);R=2*sigma*(T*iv(sq['c6'])-Tp*xi-iv(sq['j6']))+gamma*T*xi+iv(sq['o6'])/iv(sq['d6_wall']);enclosed(sq['R6'],R,'R6')
 enclosed(sq['robin'],-iv(sq['D6'])*iv(sq['R6'])/(2*iv(sq['J6']))+2*sigma*T*iv(sq['Sc6'])/iv(sq['J6']),'ROBIN6')
 b1=-2*a;b2=c-2*P;b3=s3['c3']-2*v['p3'];b4=s4['c4']-2*v['p4'];ex=expcoeff([I(0),b1,b2,b3,b4],4)
 transport=xi+sw['xi5']*b1+sw['xi4']*ex[2]+sw['xi3']*ex[3]+sw['xi2']*ex[4]+sw['xi2']*sw['xi3']*(-2*u)+sw['xi2']**2*(cp-2*U+b1*(-2*u))/2
 enclosed(sq['transport'],transport,'MOVING_ENDPOINT6')
def main():
 global JETS
 here=Path(__file__).parent
 jp=here/'sixth_jet_diagnostic.py';jr=here/'SIXTH_JET_DIAGNOSTIC.json'
 ck(sha(jp)=='1822352fb48046d6571416c272d117c8d6db20442b5f33173b9ab23f6b52a04d','IDENTITY_SOURCE_PIN')
 ck(sha(jr)=='f1ea12aafd6f87575e5d0cfee2c468ee91095a28a2f5711718f5515e3c914e96','IDENTITY_RESULT_PIN')
 ck(read(jr)['PASS'] and set(read(jr)['identities'])=={'c2second','sp2prime','qk2prime','sg2prime','u2prime','Bprime','g2second','Hpp','Tppp','c4prime'},'EXACT_DERIVATIVE_IDENTITIES')
 ck(sha(here/'sixth_real_audit.py')=='c8143e105bd872883a17e6ff057d64099a3e2c4bbc14a4050f9541cac9fb1c13' and not read(here/'SIXTH_REAL_AUDIT.json')['PASS'],'FAILED_AUDIT_PRESERVED')
 JETS=load('qualified_sixth_jet_expansion',jp)
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 binding=read(ROOT/'BINDING.json');bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in binding[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'AUTH:'+path);return read(p)
 def module(name,path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'MODULE_AUTH');return load(name,p)
 cubic=module('sixth_audit_cubic','20261026_GROWING_MODE_CUBIC_FLOW/sources.py');quartic=module('sixth_audit_quartic','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall=module('sixth_audit_wall','20261027_SIXTH_WALL_QUALIFICATION/wall.py')
 qual=auth('20261027_SIXTH_BULK_QUALIFICATION/RESULT.json');globaldata=auth('20261027_QUINTIC_GLOBAL_BULK_PROBE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');inverse=auth('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json');ck(inverse['scientific_certificate'],'INVERSE_CERTIFIED');result=read(ROOT/'RESULT.json');reports={}
 for engine in ('primary','independent'):
  arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');old=fifth['arms'][engine];saved=result['arms'][engine]
  ck(read(ROOT/('ARM_'+engine+'.json'))==saved,'ARM_COPY');ck(arm['D']==initial['D'],'DOMAIN')
  for key,x in initial['parameters'].items():ck(arm['parameters'][key]==x,'PARAMETER:'+key)
  p={k:iv(x) for k,x in arm['parameters'].items()};v=extended_variables(globaldata['arms'][engine]['variables'],old['constants'],p)
  for key,x in v.items():enclosed(saved['source_variables'][key],x,'GLOBAL_VARIABLE:'+key)
  for key in ('c6','Sp6','Sc6','Sg6'):enclosed(saved['sources'][key],polynomial(qual,v,key),'GLOBAL_SOURCE:'+key)
  H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];r,h,m=p['rate'],p['h'],p['m2'];mu=-6*r*(6*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*square(T);B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;sb=saved['bulk'];src={k:iv(x) for k,x in saved['sources'].items()}
  ck((6*r-h).lo>0 and J.lo>0 and D.lo>0,'GLOBAL_POSITIVITY')
  for key,x in [('J6',J),('D6',D),('B0',B),('Tp',Tp)]:enclosed(sb[key],x,'GLOBAL_QUANTITY:'+key)
  enclosed(sb['forcing'],src['Sg6']+B*src['Sc6']/D,'FORCING6')
  for side,sg in [('lower',1),('upper',-1)]:endpoint(saved['walls'][side],old['walls'][side],old['constants'],p,sg,cubic,quartic,wall,qual)
  cf=Q(inverse['arms'][engine]['finite_orders']['6']['constant'])*Q(inverse['arms'][engine]['f_transfer_multiplier']);G=max(iv(w['quantities']['robin']).abs() for w in saved['walls'].values());size=iv(sb['forcing']).abs()+6*G;fb=cf*size/36;gb=cf*size/6;pb=(src['Sc6'].abs()+T.abs()*gb+iv(sb['Tp']).abs()*fb)/iv(sb['D6']).lo;length=I(*arm['D']);metric=2*length.hi*pb
  ck(cf>0 and length.lo>0,'INVERSE_DOMAIN')
  for key,x in dict(Cf6=cf,Robin_abs=G,source_size=size,f6_bound=fb,f6prime_bound=gb,p6_bound=pb,metric_integral_bound=metric).items():ck(Q(saved['constants'][key])==x,'EXACT_INVERSE:'+key)
  s3,s4=lower(v,p,cubic,quartic);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f']);bs=[I(0),-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],iv(globaldata['arms'][engine]['sources']['c5'])-2*v['p5'],src['c6']]
  enclosed(sb['density'],expcoeff(bs,6)[6],'DENSITY6');enclosed(sb['integral'],iv(sb['density'])*length,'INTEGRAL6')
  known=iv(saved['walls']['upper']['quantities']['transport'])-iv(saved['walls']['lower']['quantities']['transport'])+iv(sb['integral']);enclosed(sb['known'],known,'KNOWN6');enclosed(sb['d6'],iv(sb['known'])+I(-metric,metric),'DISTANCE6')
  reports[engine]=dict(d6_display=[float(x) for x in (iv(sb['d6']).lo,iv(sb['d6']).hi)],source_size_display=float(size))
 vals=[iv(result['arms'][e]['bulk']['d6']) for e in ('primary','independent')];ck(max(x.lo for x in vals)<=min(x.hi for x in vals),'COMPATIBILITY_ONLY');enclosed(result['d6'],I(min(x.lo for x in vals),max(x.hi for x in vals)),'FINAL_HULL')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 ck(sha(jp)=='1822352fb48046d6571416c272d117c8d6db20442b5f33173b9ab23f6b52a04d' and sha(jr)=='f1ea12aafd6f87575e5d0cfee2c468ee91095a28a2f5711718f5515e3c914e96','POST_IDENTITY_PINS')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=reports,identity_diagnostic_sha256=sha(jr),identity_source_sha256=sha(jp),expanded_derivative_checks=['c2second','u2prime','g2second','Hpp','Tppp','c4prime'],scope='Independent exact endpoint arithmetic, exactly dual-qualified expanded new spatial derivatives (original nonnested audit preserved), polynomial enclosure, finite-n6 inverse and moving-endpoint distance reconstruction. Qualified cubic/quartic/wall/source expressions and inherited lower enclosures reused; no independent PDE extraction or new ODE.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'SIXTH_REAL_AUDIT_R1.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('sixth_actual_audit_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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

