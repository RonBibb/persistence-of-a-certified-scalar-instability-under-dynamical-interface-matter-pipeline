"""Separate exact derivative-identity / interval-dependency diagnostic. No rescoring."""
import sys,json,time,signal,os,traceback,hashlib,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;HERE=Path(__file__).parent;ROOT=BASE/'20261027_SIXTH_REAL_SOURCE_ENCLOSURE';CUTOFF=1793101111
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def need(v,n):
 if not v:raise AssertionError(n)
def expanded(v,w,p,s3):
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];m,k=p['m2'],p['k'];mu1,mu2=p['mu1'],p['mu2']
 Hp,Tp,u,U,gp,Gp,up=[w[x] for x in ('Hp','Tp','u1','u2','g1prime','g2prime','u1prime')];c,cp=w['c2'],w['c2prime'];B=12*H*T-4*m*Phi
 Hpp=-2*T*Tp/3+2*k*H*e;Tppp=m*Tp-4*Hpp*T-8*Hp*Tp-4*H*w['Tpp']
 cpp=-p['c_factor']*(12*(u*u+a*up)+2*(g*g+f*gp))
 sp=H*c-a*u-f*g/6;spprime=Hp*c+H*cp-u*u-a*up-(g*g+f*gp)/6
 Upp=-2*Hp*P-2*H*U-Tp*F/3-T*G/3+spprime
 qkp=12*mu1*H*e*a*f+(4*m-6*mu1*e)*(u*f+a*g)+6*up*g+6*u*gp-8*m*T*a*a-16*m*Phi*a*u
 sgp=Tp*cp+T*cpp+2*m*T*c+2*m*Phi*cp-6*Tp*sp-6*T*spprime-qkp
 Bp=12*Hp*T+12*H*Tp-4*m*T
 # For exact intervals the independently reviewed T^2 enclosure is supplied.
 T2=p.get('_T2',T*T)
 Gpp=-4*Hp*G-4*H*Gp+(2*mu2*H*e+4*T*Tp)*F+(m-mu2*e+2*T2)*G+Bp*P+B*U+sgp
 innerp=36*(u*v['p3']+a*w['u3'])+48*P*U+6*(g*v['f3']+f*v['g3'])+8*F*G-18*(u*s3['c3']+a*w['c3prime'])-24*(U*c+P*cp)+8*c*cp
 return dict(c2second=cpp,sp2prime=spprime,qk2prime=qkp,sg2prime=sgp,u2prime=Upp,Bprime=Bp,g2second=Gpp,Hpp=Hpp,Tppp=Tppp,c4prime=-p['c4_factor']*innerp)
def identities(ring):
 names=('H','T','Phi','e','p','f','g','P','F','G','Hp','Tp','u','U','gp','Gp','up','c','cp','Tpp','p3','f3','g3','u3','c3','c3p','m','k','mu1','mu2','C','L')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);a={k:ring.variable(i) for i,k in enumerate(names)}
 class D:
  def __init__(self,v,d=0):self.v=ring.P.cast(v);self.d=ring.P.cast(d)
  @staticmethod
  def cast(x):return x if isinstance(x,D) else D(x)
  def __add__(self,x):
   x=self.cast(x);return D(self.v+x.v,self.d+x.d)
  __radd__=__add__
  def __neg__(self):return D(-self.v,-self.d)
  def __sub__(self,x):return self+-self.cast(x)
  def __rsub__(self,x):return self.cast(x)+-self
  def __mul__(self,x):
   x=self.cast(x);return D(self.v*x.v,self.d*x.v+self.v*x.d)
  __rmul__=__mul__
  def __truediv__(self,n):return D(self.v/n,self.d/n)
 def d(n,p=None):return D(a[n],a[p] if p else 0)
 hd,td,pd,ed=d('H','Hp'),d('T','Tp'),d('Phi','T'),D(a['e'],-2*a['H']*a['e'])
 ad,fd,gd,ud=d('p','u'),d('f','g'),d('g','gp'),d('u','up');cd=d('c','cp');md,kd,mu1,mu2,C,L=[d(n) for n in ('m','k','mu1','mu2','C','L')]
 sp=hd*cd-ad*ud-fd*gd/6;cpp=(-C*(12*ad*ud+2*fd*gd)).d
 qk=(4*md-6*mu1*ed)*ad*fd+6*ud*gd-8*md*pd*ad*ad
 sg=td*D(a['cp'],cpp)+2*md*pd*cd-6*td*sp-qk;Bd=12*hd*td-4*md*pd
 Hpp=(-td*td/3-kd*ed).d
 tppd=md*td-4*D(a['Hp'],Hpp)*td-4*hd*D(a['Tp'],a['Tpp'])
 dual=dict(c2second=cpp,sp2prime=sp.d,qk2prime=qk.d,sg2prime=sg.d,u2prime=(-2*hd*d('P','U')-td*d('F','G')/3+sp).d,Bprime=Bd.d,g2second=(-4*hd*d('G','Gp')+(md-mu2*ed+2*td*td)*d('F','G')+Bd*d('P','U')+sg).d,Hpp=Hpp,Tppp=tppd.d,c4prime=(-L*(36*ad*d('p3','u3')+24*d('P','U')*d('P','U')+6*fd*d('f3','g3')+4*d('F','G')*d('F','G')-18*ad*d('c3','c3p')-24*d('P','U')*cd+4*cd*cd)).d)
 v={k:a[k] for k in ('H','T','Phi','e','p','f','g','P','F','G','p3','f3','g3')};w={k:a[n] for k,n in dict(Hp='Hp',Tp='Tp',u1='u',u2='U',g1prime='gp',g2prime='Gp',u1prime='up',c2='c',c2prime='cp',Tpp='Tpp',u3='u3',c3prime='c3p').items()};p={k:a[n] for k,n in dict(m2='m',k='k',mu1='mu1',mu2='mu2',c_factor='C',c4_factor='L').items()}
 ex=expanded(v,w,p,dict(c3=a['c3']));checks=[]
 for key,x in dual.items():need((x-ex[key]).iszero(),'DERIVATIVE_IDENTITY:'+key);checks.append(key)
 return checks
def main():
 ap=HERE/'sixth_real_audit.py';need(sha(ap)=='c8143e105bd872883a17e6ff057d64099a3e2c4bbc14a4050f9541cac9fb1c13','FAILED_AUDITOR_PIN');old=load('failed_sixth_auditor',ap)
 failure=read(HERE/'SIXTH_REAL_AUDIT.json');need(not failure['PASS'] and 'g2second' in failure['error'],'FAILURE_PRESERVED')
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');need(sha(ROOT/'RESULT.json')==terminal['result_sha256'],'RESULT_PIN');binding=read(ROOT/'BINDING.json');need(sha(ROOT/'BINDING.json')==terminal['binding_sha256'],'BINDING_PIN');bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in binding[group].items():need(sha(p)==h,'BOUND:'+p);bound[p]=h
 def module(n,path):
  p=BASE/path;need(bound.get(str(p))==sha(p),'IMPORT_AUTH');return load(n,p)
 ring=module('jet_ring','20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py');checks=identities(ring)
 cubic=module('jet_cubic','20261026_GROWING_MODE_CUBIC_FLOW/sources.py');quartic=module('jet_quartic','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall=module('jet_wall','20261027_SIXTH_WALL_QUALIFICATION/wall.py')
 result=read(ROOT/'RESULT.json');fifth=read(BASE/'20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');qual=read(BASE/'20261027_SIXTH_BULK_QUALIFICATION/RESULT.json');records={};orig=old.enclosed
 class Capture(Exception):pass
 for engine in ('primary','independent'):
  arm=read(BASE/('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json'));p={k:old.iv(x) for k,x in arm['parameters'].items()};records[engine]={}
  for side,sigma in [('lower',1),('upper',-1)]:
   previous=fifth['arms'][engine]['walls'][side];saved=result['arms'][engine]['walls'][side];captured={}
   def intercept(s,x,label):
    if label=='DUAL_OR_ENDPOINT_JET:g2second':captured['dual']=x;raise Capture()
    orig(s,x,label)
   old.enclosed=intercept
   try:old.endpoint(saved,previous,fifth['arms'][engine]['constants'],p,sigma,cubic,quartic,wall,qual)
   except Capture:pass
   need('dual' in captured,'CAPTURE_GPP');old.enclosed=orig
   v={k:old.iv(x) for k,x in previous['source_variables'].items()};w={k:old.iv(x) for k,x in previous['inputs'].items()};s3,_=old.lower(v,p,cubic,quartic);px=dict(p,_T2=old.square(v['T']));ex=expanded(v,w,px,s3)
   jet_keys=('c2second','u2prime','g2second','Hpp','Tppp','c4prime')
   for key in jet_keys:orig(saved['inputs'][key],ex[key],'EXPANDED_CONTAINMENT:'+key)
   sv=old.iv(saved['inputs']['g2second']);dv=captured['dual'];ev=ex['g2second']
   records[engine][side]=dict(saved=[str(sv.lo),str(sv.hi)],dual=[str(dv.lo),str(dv.hi)],expanded=[str(ev.lo),str(ev.hi)],dual_contained=sv.lo<=dv.lo<=dv.hi<=sv.hi,expanded_contained=sv.lo<=ev.lo<=ev.hi<=sv.hi,display=dict(saved=[float(sv.lo),float(sv.hi)],dual=[float(dv.lo),float(dv.hi)],expanded=[float(ev.lo),float(ev.hi)]))
 for p,h in bound.items():need(sha(p)==h,'POST_BOUND:'+p)
 need(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,identities=checks,records=records,producer_terminal=pin,scope='Exact dual-versus-expanded polynomial identities plus strict expanded interval containment; preserves failed differently grouped interval auditor. Not full sixth source audit.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=HERE/'SIXTH_JET_DIAGNOSTIC.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  need(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('jet_diagnostic_lease',lp);lease.ROOT=HERE;lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DIAGNOSTIC_600_SECONDS')));signal.alarm(600);report=main();need(sha(__file__)==pin,'SOURCE_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc())
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps({k:v for k,v in report.items() if k!='records'}),flush=True)
 if not report['PASS']:raise SystemExit(1)
