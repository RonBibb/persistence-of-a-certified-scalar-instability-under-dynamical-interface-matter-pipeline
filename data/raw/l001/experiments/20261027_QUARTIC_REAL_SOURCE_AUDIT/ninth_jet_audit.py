"""Independent dictionary differentiation and seventh-equation anchoring.

No producer jets.py import. Inherited lower maps are separately authenticated.
"""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE/'20261027_NINTH_JET_QUALIFICATION';CUTOFF=1793121042
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
HELPER=HERE/'eighth_jet_audit.py';helper_pin=sha(HELPER);a=load('ninth_jet_independent_helpers',HELPER)
ck,unpack,add,mul=a.ck,a.unpack,a.add,a.mul
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('jets.py','jets_sha256'),('DERIVATION.txt','derivation_sha256')]
 if 'pins_sha256' in terminal:files.append(('PINS.json','pins_sha256'))
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_EIGHTH_JET_QUALIFICATION/RESULT.json');seventh=auth('20261027_SEVENTH_BULK_QUALIFICATION/RESULT.json');fifth=auth('20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json');oldjets=auth('20261027_SEVENTH_JET_QUALIFICATION/RESULT.json')
 ck(all(x['pass_status'] for x in (prior,seventh,fifth,oldjets)),'ANCESTOR_PASSES')
 pa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/EIGHTH_JET_AUDIT.json');ck(pa['PASS'] and pa['producer_terminal']==sha(BASE/'20261027_EIGHTH_JET_QUALIFICATION/TERMINAL.json'),'PRIOR_JET_AUDIT');ck(helper_pin==pa['audit_source_sha256'],'AUTHENTICATED_HELPER')
 sa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_BULK_AUDIT.json');ck(sa['PASS'] and sa['producer_terminal']==sha(BASE/'20261027_SEVENTH_BULK_QUALIFICATION/TERMINAL.json'),'SEVENTH_BULK_AUDIT')
 saved=read(ROOT/'RESULT.json');names=tuple(saved['variables']);zero=(0,)*len(names)
 ck(names==tuple(prior['variables'])+('p7','f7','g7','N7') and len(names)==len(set(names)),'VARIABLE_EXTENSION')
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
 H,T,Phi,e,m,r,h,p7,f7,g7=[var(k) for k in ('H','T','Phi','e','m','r','h','p7','f7','g7')]
 s7={k:remap(seventh['sources'][k],seventh['variables']) for k in ('c7','Sp7','Sg7')}
 pprime=add(add(scale(mul(H,p7),Q(-2)),scale(mul(T,f7),Q(-1,3))),s7['Sp7'])
 potential=add(add(m,scale(mul(mul(r,add(scale(r,Q(7)),scale(h,Q(3)))),e),Q(7))),scale(square(T),Q(2)))
 B=add(scale(mul(H,T),Q(12)),scale(mul(m,Phi),Q(-4)));gprime=add(add(add(scale(mul(H,g7),Q(-4)),mul(potential,f7)),mul(B,p7)),s7['Sg7'])
 ck(d['p7']==pprime and d['f7']==g7 and d['g7']==gprime and d['N7']=={},'INDEPENDENT_SEVENTH_EQUATIONS')
 ck(d['H']==add(scale(square(T),Q(-1,3)),scale(mul(square(h),e),Q(-1))),'BACKGROUND_H');ck(d['T']==add(mul(m,Phi),scale(mul(H,T),Q(-4))),'BACKGROUND_T')
 bases=dict(u7=pprime,g7prime=gprime,c7=s7['c7'],u5=d['p5'],g5prime=d['g5'],c5=remap(fifth['sources']['c5'],fifth['variables']),u3=d['p3'],g3prime=d['g3'],c3=remap(oldjets['base_polynomials']['c3'],oldjets['variables']),u1=d['p'],g1prime=d['g'])
 ck(set(saved['base_polynomials'])==set(bases),'BASE_COVERAGE')
 for k,v in bases.items():ck(unpack(saved['base_polynomials'][k])==v,'BASE_ANCHOR:'+k)
 specs={'u7':('u7',0),'g7prime':('g7prime',0),'c7prime':('c7',1),'u5prime':('u5',1),'g5second':('g5prime',1),'c5second':('c5',2),'u3second':('u3',2),'g3third':('g3prime',2),'c3third':('c3',3),'u1third':('u1',3),'g1fourth':('g1prime',3)}
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
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'POST_TERMINAL:'+f)
 ck(sha(ROOT/'TERMINAL.json')==pin and sha(HELPER)==helper_pin,'TERMINAL_HELPER_UNCHANGED')
 return dict(PASS=True,checks=a.COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),helper_source_sha256=helper_pin,scope='Independent dictionary differentiation of all11 targets and inherited-map equality, separately reconstructed n7 RHS and explicit background H/T anchors. g1fourth denotes fourth derivative of g1=f1prime, hence fifth scalar derivative. No new jets.py import; lower map/source equations inherited from audited records. No interval enclosure or ninth coefficient.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=HERE/'NINTH_JET_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('ninth_jet_review_lease',lp);lease.ROOT=HERE;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDIT_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=a.COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
