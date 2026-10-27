"""Independent dictionary differentiation; inherited qualified RHS anchoring."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_EIGHTH_JET_QUALIFICATION';COUNT=0;CUTOFF=1793110516
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
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('jets.py','jets_sha256'),('DERIVATION.txt','derivation_sha256')]
 if 'pins_sha256' in terminal:files.append(('PINS.json','pins_sha256'))
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,hsh in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==hsh,'BOUND:'+p);bound[p]=hsh
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_SEVENTH_JET_QUALIFICATION/RESULT.json');sixth=auth('20261027_SIXTH_BULK_QUALIFICATION/RESULT.json');quartic=auth('20261027_QUARTIC_BULK_QUALIFICATION_R2/RESULT.json')
 ck(prior['pass_status'] and sixth['pass_status'] and quartic['pass_status'],'ANCESTOR_PASSES')
 pa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_JET_AUDIT.json');ck(pa['PASS'] and pa['producer_terminal']==sha(BASE/'20261027_SEVENTH_JET_QUALIFICATION/TERMINAL.json'),'PRIOR_JET_AUDIT')
 sa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SIXTH_BULK_AUDIT.json');ck(sa['PASS'] and sa['producer_terminal']==sha(BASE/'20261027_SIXTH_BULK_QUALIFICATION/TERMINAL.json'),'SIXTH_AUDIT')
 saved=read(ROOT/'RESULT.json');names=tuple(saved['variables']);zero=(0,)*len(names)
 ck(names==tuple(prior['variables'])+('p6','f6','g6','N6') and len(names)==len(set(names)),'VARIABLE_EXTENSION')
 def const(q):return {zero:Q(q)} if q else {}
 def scale(poly,q):return {k:v*q for k,v in poly.items() if v*q}
 def var(k):
  v=list(zero);v[names.index(k)]=1;return {tuple(v):Q(1)}
 def square(p):return mul(p,p)
 def remap(rows,oldnames):
  oldpoly=unpack(rows);out={}
  for powers,c in oldpoly.items():
   ck(len(powers)==len(oldnames),'MONOMIAL_DIMENSION');key=[0]*len(names)
   for k,n in zip(oldnames,powers):
    if n:ck(k in names,'OLD_VARIABLE_PRESENT');key[names.index(k)]+=n
   key=tuple(key);out[key]=out.get(key,Q(0))+c
  return {k:v for k,v in out.items() if v}
 d={k:unpack(v) for k,v in saved['derivative_map'].items()};ck(set(d)==set(names),'MAP_COVERAGE')
 for k in prior['variables']:ck(d[k]==remap(prior['derivative_map'][k],prior['variables']),'INHERITED_MAP:'+k)
 H,T,Phi,e,m,r,h,p6,f6,g6=[var(k) for k in ('H','T','Phi','e','m','r','h','p6','f6','g6')]
 s6={k:remap(sixth['sources'][k],sixth['variables']) for k in ('c6','Sp6','Sg6')}
 pprime=add(add(scale(mul(H,p6),Q(-2)),scale(mul(T,f6),Q(-1,3))),s6['Sp6'])
 potential=add(add(m,scale(mul(mul(r,add(scale(r,Q(6)),scale(h,Q(3)))),e),Q(6))),scale(square(T),Q(2)))
 B=add(scale(mul(H,T),Q(12)),scale(mul(m,Phi),Q(-4)))
 gprime=add(add(add(scale(mul(H,g6),Q(-4)),mul(potential,f6)),mul(B,p6)),s6['Sg6'])
 ck(d['p6']==pprime and d['f6']==g6 and d['g6']==gprime and d['N6']=={},'SIXTH_EQUATIONS')
 ck(d['H']==add(scale(square(T),Q(-1,3)),scale(mul(square(h),e),Q(-1))),'BACKGROUND_H')
 ck(d['T']==add(mul(m,Phi),scale(mul(H,T),Q(-4))),'BACKGROUND_T')
 c2=scale(mul(var('C'),add(scale(square(var('p')),Q(6)),square(var('f')))),Q(-1))
 bases=dict(u6=pprime,g6prime=gprime,c6=s6['c6'],u4=d['p4'],g4prime=d['g4'],c4=remap(quartic['sources']['c4'],quartic['variables']),u2=d['P'],g2prime=d['G'],c2=c2,Hprime=d['H'],Tprime=d['T'])
 ck(set(saved['base_polynomials'])==set(bases),'BASE_COVERAGE')
 for k,v in bases.items():ck(unpack(saved['base_polynomials'][k])==v,'BASE_ANCHOR:'+k)
 specs={'u6':('u6',0),'g6prime':('g6prime',0),'c6prime':('c6',1),'u4prime':('u4',1),'g4second':('g4prime',1),'c4second':('c4',2),'u2second':('u2',2),'g2third':('g2prime',2),'c2third':('c2',3),'Hppp':('Hprime',2),'Tpppp':('Tprime',3)}
 ck(saved['derivative_specs']=={k:list(v) for k,v in specs.items()} and set(saved['sources'])==set(specs),'SPEC_COVERAGE')
 def derivative(poly):
  out={}
  for powers,c in poly.items():
   for j,n in enumerate(powers):
    if n:
     key=list(powers);key[j]-=1;out=add(out,mul({tuple(key):c*n},d[names[j]]))
  return out
 for k,(base,order) in specs.items():
  poly=bases[base]
  for _ in range(order):poly=derivative(poly)
  ck(poly==unpack(saved['sources'][k]),'DICTIONARY_DERIVATIVE:'+k)
 ck(set(saved['checks'])=={'EXACT_LEIBNIZ:'+k for k in specs} and len(saved['checks'])==len(specs),'CONTROL_COVERAGE')
 for p,hsh in bound.items():ck(sha(p)==hsh,'POST_BOUND:'+p)
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'POST_TERMINAL:'+f)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),scope='Independent dictionary-polynomial derivative reconstruction of all11 targets, exact inherited-map equality, separately rebuilt sixth reduced equations and explicit background H/T RHS anchoring. No new jets.py import. Earlier lower maps/source equations inherited from separately qualified and audited records; no interval enclosure or eighth coefficient.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'EIGHTH_JET_AUDIT.json'
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
