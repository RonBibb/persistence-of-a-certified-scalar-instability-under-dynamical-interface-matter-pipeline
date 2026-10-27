"""Independent dictionary differentiation; inherited qualified RHS anchoring."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_SEVENTH_JET_QUALIFICATION';COUNT=0;CUTOFF=1793108564
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def unpack(rows):
 d={tuple(x['powers']):Q(x['coefficient']) for x in rows};ck(len(d)==len(rows),'UNIQUE_MONOMIALS');return {k:v for k,v in d.items() if v}
def add(a,b):
 out=dict(a)
 for k,v in b.items():out[k]=out.get(k,Q(0))+v
 return {k:v for k,v in out.items() if v}
def mul(a,b):
 out={}
 for i,x in a.items():
  for j,y in b.items():
   k=tuple(u+v for u,v in zip(i,j));out[k]=out.get(k,Q(0))+x*y
 return {k:v for k,v in out.items() if v}
def main():
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PRODUCER_PASS')
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('jets.py','jets_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/f)==t[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return p
 paths=['20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py','20261026_GROWING_MODE_CUBIC_FLOW/sources.py','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py']
 ring,cubic,quartic=[load('jet_anchor_'+str(i),auth(n)) for i,n in enumerate(paths)]
 saved=read(ROOT/'RESULT.json');names=tuple(saved['variables']);ck(len(names)==len(set(names)),'UNIQUE_VARIABLES')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(i) for i,k in enumerate(names)};zero=ring.P(0)
 H,T,Phi,e,p,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];r,h,m=v['r'],v['h'],v['m']
 mus={n:-n*r*(n*r+3*h) for n in range(1,6)};B=12*H*T-4*m*Phi
 u=-2*H*p-T*f/3;gp=-4*H*g+(m-mus[1]*e+2*T*T)*f+B*p
 c2=-v['C']*(6*p*p+f*f);cp=-v['C']*(12*p*u+2*f*g);sp2=H*c2-p*u-f*g/6
 sg2=T*cp+2*m*Phi*c2-6*T*sp2-((4*m-6*mus[1]*e)*p*f+6*u*g-8*m*Phi*p*p)
 params=dict(m2=m,k=h*h,rate=r,h=h,c_factor=v['C'],c3_factor=v['J'],c4_factor=v['L'],**{'mu'+str(n):mus[n] for n in mus})
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params)
 s4=quartic.quartic(H,T,Phi,e,p,f,g,P,F,G,v['p3'],v['f3'],v['g3'],params,cubic)
 fifth=read(auth('20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json'));ck(fifth['pass_status'],'FIFTH_PASS')
 def remap(key):
  out=zero
  for row in fifth['sources'][key]:
   term=ring.P(Q(row['coefficient']))
   for k,n in zip(fifth['variables'],row['powers']):
    if n:term*=v[k]**n
   out+=term
  return out
 s5={k:remap(k) for k in ('c5','Sp5','Sg5')}
 rhs={k:zero for k in names};rhs.update(H=-T*T/3-h*h*e,T=m*Phi-4*H*T,Phi=T,e=-2*H*e,p=u,f=g,g=gp,P=-2*H*P-T*F/3+sp2,F=G,G=-4*H*G+(m-mus[2]*e+2*T*T)*F+B*P+sg2)
 for n,s in ((3,s3),(4,s4),(5,s5)):
  pn,fn,gn=[v[k+str(n)] for k in ('p','f','g')]
  rhs['p'+str(n)]=-2*H*pn-T*fn/3+s['Sp'+str(n)];rhs['f'+str(n)]=gn;rhs['g'+str(n)]=-4*H*gn+(m-mus[n]*e+2*T*T)*fn+B*pn+s['Sg'+str(n)]
 ck(set(saved['derivative_map'])==set(names),'MAP_COVERAGE')
 d={k:unpack(rows) for k,rows in saved['derivative_map'].items()}
 for k,poly in rhs.items():ck(d[k]==unpack(poly.pack()),'RHS_ANCHOR:'+k)
 bases=dict(c5=s5['c5'],c3=s3['c3'],u1=u,g1prime=gp,u3=rhs['p3'],g3prime=rhs['g3'])
 ck(set(saved['base_polynomials'])==set(bases),'BASE_COVERAGE')
 for k,poly in bases.items():ck(unpack(saved['base_polynomials'][k])==unpack(poly.pack()),'BASE_ANCHOR:'+k)
 def derivative(poly):
  out={}
  for powers,c in poly.items():
   for j,n in enumerate(powers):
    if n:
     key=list(powers);key[j]-=1;out=add(out,mul({tuple(key):c*n},d[names[j]]))
  return out
 specs=[('c5prime','c5',1),('u3prime','u3',1),('g3second','g3prime',1),('c3second','c3',2),('u1second','u1',2),('g1third','g1prime',2)]
 ck(set(saved['sources'])=={'u5','g5prime'}|{s[0] for s in specs},'SOURCE_COVERAGE')
 ck(unpack(saved['sources']['u5'])==d['p5'],'U5_RHS');ck(unpack(saved['sources']['g5prime'])==d['g5'],'G5_RHS')
 for name,base,order in specs:
  poly=unpack(saved['base_polynomials'][base])
  for _ in range(order):poly=derivative(poly)
  ck(poly==unpack(saved['sources'][name]),'DICTIONARY_DERIVATIVE:'+name)
 ck(set(saved['checks'])=={'EXACT_LEIBNIZ:'+x[0] for x in specs} and len(saved['checks'])==6,'CONTROL_COVERAGE')
 for p,hsh in bound.items():ck(sha(p)==hsh,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),scope='Independent dictionary-polynomial differentiation of all six derivative targets and two direct RHS jets, with full reduced-equation map/base anchoring using authenticated older source algebra. Does not import new jets.py. Original reduced PDE/source formulas inherited and manually reviewed; no interval enclosure or seventh solution.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'SEVENTH_JET_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('jet_review_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDIT_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
