"""Independent exact-endpoint fifth boundary/inverse audit; no producer flow import."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_QUINTIC_REAL_SOURCE_ENCLOSURE';COUNT=0
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
  x=self.cast(x);return I(self.lo+x.lo,self.hi+x.hi)
 __radd__=__add__
 def __neg__(self):return I(-self.hi,-self.lo)
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  x=self.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.cast(x);ck(x.lo*x.hi>0,'NONZERO_DIVISOR');v=[a/b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 def __pow__(self,n):
  ck(isinstance(n,int) and n>=0,'NONNEGATIVE_POWER');out=I(1)
  for _ in range(n):out=out*self
  return out
 def abs(self):return max(abs(self.lo),abs(self.hi))
def iv(v):return I(*v['exact_bounds'])
def square(x):return I(0 if x.lo<=0<=x.hi else min(x.lo*x.lo,x.hi*x.hi),max(x.lo*x.lo,x.hi*x.hi))
def enclosed(saved,x,label):
 y=iv(saved);ck(y.lo<=x.lo<=x.hi<=y.hi,label)
def polynomial(qual,v,key):
 names=qual['variables'];maximum=[max((row['powers'][j] for row in qual['sources'][key]),default=0) for j in range(len(names))]
 powers=[[v[k]**n for n in range(m+1)] for k,m in zip(names,maximum)];total=I(0)
 for row in qual['sources'][key]:
  term=I(Q(row['coefficient']))
  for j,n in enumerate(row['powers']):
   if n:term=term*powers[j][n]
  total+=term
 return total
def lower_sources(v,p,cubic,quartic):
 args=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')]
 return cubic.cubic(*args,p),quartic.quartic(*args,v['p3'],v['f3'],v['g3'],p,cubic)
def endpoint(saved,arm,old,p,side,sigma,cubic,quartic,wall,qual):
 z=list(map(iv,arm[side+'_canonical']));w={k:iv(x) for k,x in old['walls'][side]['data'].items()}
 H,T,E=w['H'],w['T'],w['E'];Phi=z[2];e=square(E);m,r,h=p['m2'],p['rate'],p['h'];ck((5*r-h).lo>0,'TRACE_DIVISOR_POSITIVE')
 v=dict(H=H,T=T,Phi=Phi,e=e,p=w['p1'],f=w['f1'],g=w['g1'],P=w['p2'],F=w['f2'],G=w['g2'],p3=w['p3'],f3=w['f3'],g3=w['g3'],p4=I(-Q(arm['p4_bound']),Q(arm['p4_bound'])),f4=I(-Q(arm['f4_bound']),Q(arm['f4_bound'])),g4=I(-Q(arm['f4prime_bound']),Q(arm['f4prime_bound'])),m=m,C=p['c_factor'],J=p['c3_factor'],L=p['c4_factor'],M=r/(5*(5*r-h)),r=r,h=h,p5=I(0),f5=I(0),g5=I(0))
 for k,x in v.items():enclosed(saved['source_variables'][k],x,'ENDPOINT_SOURCE_VARIABLE:'+k)
 s3,s4=lower_sources(v,p,cubic,quartic);a,f,g=v['p'],v['f'],v['g'];P,F,G=v['P'],v['F'],v['G']
 hp=-square(T)/3-p['k']*e;tp=m*Phi-4*H*T;B=12*H*T-4*m*Phi
 u=-2*H*a-T*f/3;c2=-p['c_factor']*(6*a*a+f*f);cp=-p['c_factor']*(12*a*u+2*f*g);sp2=H*c2-a*u-f*g/6
 qk2=(4*m-6*p['mu1']*e)*a*f+6*u*g-8*m*Phi*a*a;sg2=T*cp+2*m*Phi*c2-6*T*sp2-qk2
 U=-2*H*P-T*F/3+sp2;gp=-4*H*g+(m-p['mu1']*e+2*square(T))*f+B*a;Gp=-4*H*G+(m-p['mu2']*e+2*square(T))*F+B*P+sg2
 u3=-2*H*v['p3']-T*v['f3']/3+s3['Sp3'];gp3=-4*H*v['g3']+(m-p['mu3']*e+2*square(T))*v['f3']+B*v['p3']+s3['Sg3']
 c3p=-p['c3_factor']*(6*u*P+6*a*U+g*F+f*G-3*u*c2-3*a*cp)
 up=-2*hp*a-2*H*u-tp*f/3-T*g/3
 gpp=-4*hp*g-4*H*gp+(2*p['mu1']*H*e+4*T*tp)*f+(m-p['mu1']*e+2*square(T))*g+(12*hp*T+12*H*tp-4*m*T)*a+B*u
 xi4=iv(arm['walls'][side]['xi4']);o4=iv(arm['walls'][side]['o4']);dw4=2-p['mu4']*e;ck(dw4.lo>0,'OSCILLATOR4_POSITIVE')
 w.update(Hp=hp,Tp=tp,Tpp=m*T-4*hp*T-4*H*tp,u1=u,g1prime=gp,u2=U,g2prime=Gp,c2=c2,c2prime=cp,c3=s3['c3'],u3=u3,g3prime=gp3,c3prime=c3p,u1prime=up,g1second=gpp,p4=v['p4'],f4=v['f4'],g4=v['g4'],c4=s4['c4'],xi4=xi4,chi4=(v['f4']+T*xi4-o4)/dw4)
 for k,x in w.items():enclosed(saved['inputs'][k],x,'ENDPOINT_JET:'+side+':'+k)
 # Qualified wall algebra is inherited, evaluated independently without rounding.
 sw={k:iv(x) for k,x in saved['inputs'].items()};direct=wall.direct(sw,sigma);sq=saved['quantities']
 for key,row in [('o5','O'),('j5','J'),('qI5','graph')]:enclosed(sq[key],direct[row].a[5],'WALL_LOAD:'+side+':'+key)
 sv={k:iv(x) for k,x in saved['source_variables'].items()}
 for key in ('c5','Sc5'):enclosed(sq[key],polynomial(qual,sv,key),'WALL_POLYNOMIAL:'+key)
 # Reconstruct downstream reductions from saved containing inputs, matching each link.
 H,T,E=sw['H'],sw['T'],sw['E'];e=square(E);tp=sw['Tp'];r=p['rate'];h=p['h'];mu5=-5*r*(5*r+3*h)
 divisor=5*sigma*e*r*(5*r-h);ck(divisor.lo>0 or divisor.hi<0,'GRAPH_SIGN');enclosed(sq['graph_divisor'],divisor,'GRAPH_DIVISOR')
 xi5=-iv(sq['qI5'])/iv(sq['graph_divisor']);enclosed(sq['xi5'],xi5,'XI5')
 J=-3*(mu5+4*p['k'])*e;D=J+2*square(T);dw=2-mu5*e;ck(J.lo>0 and D.lo>0 and dw.lo>0,'ENDPOINT_POSITIVE')
 for k,x in [('J5',J),('D5',D),('d5_wall',dw),('d4_wall',dw4),('Hp',hp),('Tp',tp)]:enclosed(sq[k],x,'ENDPOINT_QUANTITY:'+k)
 x5=iv(sq['xi5']);gamma=21-I(1)/iv(sq['d5_wall']);R=2*sigma*(T*iv(sq['c5'])-tp*x5-iv(sq['j5']))+gamma*T*x5+iv(sq['o5'])/iv(sq['d5_wall']);enclosed(sq['R5'],R,'ROBIN_LOAD')
 robin=-iv(sq['D5'])*iv(sq['R5'])/(2*iv(sq['J5']))+2*sigma*T*iv(sq['Sc5'])/iv(sq['J5']);enclosed(sq['robin'],robin,'ROBIN_REDUCTION')
 # The transport uses the original reconstructed c2/c3 and actual endpoint fields.
 b1=-2*a;b2=c2-2*P;b3=s3['c3']-2*v['p3']
 transport=x5+xi4*b1+w['xi3']*(b2+b1*b1/2)+w['xi2']*(b3+b1*b2+b1**3/6)+w['xi2']**2*(-2*u)/2
 enclosed(sq['transport'],transport,'ENDPOINT_TRANSPORT')
def main(mode):
 terminal=read(ROOT/(mode+'_TERMINAL.json'));pin=sha(ROOT/(mode+'_TERMINAL.json'));ck(terminal['pass_status'],'PASS')
 for file,key in [(mode+'_RESULT.json','result_sha256'),(mode+'_BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('AUTHORITY.txt','authority_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/file)==terminal[key],'TERMINAL:'+file)
 binding=read(ROOT/(mode+'_BINDING.json'));bound={}
 for group in ('inputs','sources','runtime'):
  for path,hsh in binding[group].items():ck(sha(path)==hsh,'BOUND:'+path);bound[path]=hsh
 def auth(path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'AUTH:'+path);return read(p)
 def module(name,path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'MODULE_AUTH');return load(name,p)
 cubic=module('quintic_review_cubic','20261026_GROWING_MODE_CUBIC_FLOW/sources.py');quartic=module('quintic_review_quartic','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall=module('quintic_review_wall','20261027_QUINTIC_WALL_QUALIFICATION/wall.py')
 qual=auth('20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json');globaldata=auth('20261027_QUINTIC_GLOBAL_BULK_PROBE/RESULT.json');inverse=auth('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json');result=read(ROOT/(mode+'_RESULT.json'));reports={}
 for engine in ('primary','independent'):
  arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');old=auth('20261026_GROWING_MODE_CUBIC_AFFINE/PRODUCTION_'+engine+'.json');initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');saved=result['arms'][engine]
  ck(arm['D']==initial['D'],'DOMAIN_IDENTITY')
  for k,vv in initial['parameters'].items():ck(arm['parameters'][k]==vv,'PARAMETER_IDENTITY:'+k)
  p={k:iv(x) for k,x in arm['parameters'].items()};row=globaldata['arms'][engine];v={k:iv(x) for k,x in row['variables'].items()};sources={k:iv(x) for k,x in row['sources'].items()}
  H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];r,h,m=p['rate'],p['h'],p['m2'];mu=-5*r*(5*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*square(T)
  ck((r-h).lo>0 and h.lo>0 and e.lo>0 and J.lo>0 and D.lo>0,'GLOBAL_POSITIVE');B=12*H*T-4*m*Phi;tp=m*Phi-4*H*T;sb=saved['bulk']
  for k,x in [('J5',J),('D5',D),('B0',B),('Tp',tp)]:enclosed(sb[k],x,'BULK:'+k)
  force=sources['Sg5']+B*sources['Sc5']/D;enclosed(sb['forcing'],force,'GLOBAL_FORCING')
  for side,sg in [('lower',1),('upper',-1)]:endpoint(saved['walls'][side],arm,old,p,side,sg,cubic,quartic,wall,qual)
  cf=Q(inverse['arms'][engine]['finite_orders']['5']['constant'])*Q(inverse['arms'][engine]['f_transfer_multiplier']);G=max(iv(w['quantities']['robin']).abs() for w in saved['walls'].values());size=iv(sb['forcing']).abs()+5*G;fb=cf*size/25;gb=cf*size/5;pb=(sources['Sc5'].abs()+T.abs()*gb+iv(sb['Tp']).abs()*fb)/iv(sb['D5']).lo;length=I(*arm['D']);metric=2*length.hi*pb
  for k,x in dict(Cf5=cf,Robin_abs=G,source_size=size,f5_bound=fb,f5prime_bound=gb,p5_bound=pb,metric_integral_bound=metric).items():ck(Q(saved['constants'][k])==x,'EXACT_INVERSE:'+k)
  s3,s4=lower_sources(v,p,cubic,quartic);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f']);b1=-2*v['p'];b2=c2-2*v['P'];b3=s3['c3']-2*v['p3'];b4=s4['c4']-2*v['p4']
  density=sources['c5']+b1*b4+b2*b3+(b1*b1*b3+b1*b2*b2)/2+b1**3*b2/6+b1**5/120;enclosed(sb['density'],density,'DENSITY');enclosed(sb['integral'],iv(sb['density'])*length,'SIGNED_LENGTH_INTEGRAL')
  known=iv(saved['walls']['upper']['quantities']['transport'])-iv(saved['walls']['lower']['quantities']['transport'])+iv(sb['integral']);enclosed(sb['known'],known,'KNOWN_DISTANCE');enclosed(sb['d5'],iv(sb['known'])+I(-metric,metric),'FINAL_D5')
  reports[engine]=dict(d5_display=[float(x) for x in (iv(sb['d5']).lo,iv(sb['d5']).hi)],source_size_display=float(size))
 values=[iv(result['arms'][e]['bulk']['d5']) for e in ('primary','independent')];ck(max(x.lo for x in values)<=min(x.hi for x in values),'ENCLOSURE_COMPATIBILITY');enclosed(result['d5'],I(min(x.lo for x in values),max(x.hi for x in values)),'FINAL_HULL')
 prior=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');old_bound=Q(prior['distance'][5]);new_bound=iv(result['d5']).abs();ck(old_bound>0 and new_bound>0,'COMPARISON_POSITIVE')
 if mode=='production':
  probe=read(ROOT/'probe_RESULT.json');ck(probe['arms']==result['arms'] and probe['d5']==result['d5'],'PROBE_EXACT_REPLAY');ck(probe['seconds']<120,'RESOURCE_ADMISSION')
  for name in ('probe_RESULT.json','probe_BINDING.json','probe_TERMINAL.json'):ck(bound.get(str(ROOT/name))==sha(ROOT/name),'PROBE_PIN')
 for path,hsh in bound.items():ck(sha(path)==hsh,'POST_BOUND:'+path)
 ck(sha(ROOT/(mode+'_TERMINAL.json'))==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/(mode+'_RESULT.json')),arms=reports,distance_bound_comparison=dict(old_generic=str(old_bound),new_actual_unsigned=str(new_bound),ratio=str(old_bound/new_bound),ratio_display=float(old_bound/new_bound),scope='Coefficient bound comparison only; no clock-amplitude gain established.'),scope='Independent exact unrounded endpoint/derivative, Robin, inverse, signed integration and distance reconstruction; inherited qualified cubic/quartic/wall formulas evaluated without producer flow import. No fresh ODE propagation or independently generated nonlinear wall oracle.')
if __name__=='__main__':
 mode=sys.argv[1];start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/('QUINTIC_REAL_'+mode.upper()+'_AUDIT.json')
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and mode in ('probe','production'),'LINUX_MODE');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('fifth_actual_review_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire()
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main(mode);ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
