"""Independent dictionary-polynomial witness audit, not producer replay."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_SEVENTH_BULK_QUALIFICATION';COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def unpack(rows):
 d={tuple(v['powers']):Q(v['coefficient']) for v in rows};ck(len(d)==len(rows),'NO_DUPLICATE_MONOMIAL');return {k:v for k,v in d.items() if v}
def add(a,b,sign=1):
 d=dict(a)
 for k,v in b.items():
  d[k]=d.get(k,Q(0))+sign*v
  if not d[k]:del d[k]
 return d
def mul(a,b):
 d={}
 for x,u in a.items():
  for y,v in b.items():
   key=tuple(i+j for i,j in zip(x,y));d[key]=d.get(key,Q(0))+u*v
 return {k:v for k,v in d.items() if v}
def power(a,n):
 out={ZERO:Q(1)}
 for _ in range(n):out=mul(out,a)
 return out
def variable(j):
 k=list(ZERO);k[j]=1;return {tuple(k):Q(1)}
def scalar(a):return {ZERO:Q(a)} if a else {}
def main():
 global ZERO
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('bulk.py','bulk_sha256'),('series.py','series_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 binding=read(ROOT/'BINDING.json');bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in binding[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 r=read(ROOT/'RESULT.json');names=r['variables'];ZERO=(0,)*len(names);T=variable(names.index('T'));rate=variable(names.index('r'));h=variable(names.index('h'))
 expected=['g6','g5','g4','g3','G','g'];ck([w['variable'] for w in r['pseudo_elimination']]==expected,'ELIMINATION_ORDER')
 previous=None;cumulative=0
 for w in r['pseudo_elimination']:
  a,b,c,q=[unpack(w[k]) for k in ('input','output','constraint','quotient')];i=names.index(w['variable']);N=w['power']
  if previous is not None:ck(a==previous,'WITNESS_CHAIN')
  ck(N==max((v[i] for v in a),default=0),'ACTUAL_VARIABLE_DEGREE')
  ck(add(add(mul(power(T,N),a),b,-1),mul(c,q),-1)=={},'PSEUDO_IDENTITY:'+w['variable'])
  ck(all(v[i]==0 for v in b),'VARIABLE_REMOVED:'+w['variable'])
  ct=add(c,mul(T,variable(i)),-1);ck(all(v[i]==0 for v in ct),'TRIANGULAR_CONSTRAINT')
  previous=b;cumulative+=N
 ck(cumulative==r['cumulative_T_power'],'CUMULATIVE_POWER')
 # Independent rational substitution with a common exact polynomial denominator.
 indices=[names.index(x) for x in ('C','J','L','M','N6','N7')]
 nums=[rate,mul(scalar(4),rate),rate,rate,rate,rate]
 dens=[mul(scalar(2),add(mul(scalar(2),rate),h,-1)),mul(scalar(3),add(mul(scalar(3),rate),h,-1)),mul(scalar(4),add(mul(scalar(4),rate),h,-1)),mul(scalar(5),add(mul(scalar(5),rate),h,-1)),mul(scalar(6),add(mul(scalar(6),rate),h,-1)),mul(scalar(7),add(mul(scalar(7),rate),h,-1))]
 tops=[max((p[i] for p in previous),default=0) for i in indices]
 cached=[([power(num,j) for j in range(top+1)],[power(den,j) for j in range(top+1)]) for num,den,top in zip(nums,dens,tops)]
 cleared={}
 for p,v in previous.items():
  key=list(p);powers=[p[i] for i in indices]
  for i in indices:key[i]=0
  term={tuple(key):v}
  for n,top,(nump,denp) in zip(powers,tops,cached):term=mul(mul(term,nump[n]),denp[top-n])
  cleared=add(cleared,term)
 ck(cleared==unpack(r['compatibility_reduction_lhs']),'RATIONAL_CLEARING')
 H=variable(names.index('H'));Phi=variable(names.index('Phi'));mass=variable(names.index('m'));e=variable(names.index('e'))
 bg=add(add(add(mul(scalar(6),power(H,2)),mul(scalar(Q(1,2)),power(T,2)),-1),scalar(6),-1),mul(scalar(Q(1,2)),mul(mass,power(Phi,2))))
 bg=add(bg,mul(scalar(6),mul(power(h,2),e)),-1)
 ck(len(r['compatibility_reduction_basis'])==len(r['compatibility_quotients'])==1 and unpack(r['compatibility_reduction_basis'][0])==bg,'ACTUAL_BACKGROUND_BASIS')
 remainder=unpack(r['compatibility_remainder']);ck(not remainder,'ZERO_REMAINDER');reconstructed=dict(remainder)
 for b,q in zip(r['compatibility_reduction_basis'],r['compatibility_quotients']):reconstructed=add(reconstructed,mul(unpack(b),unpack(q)))
 ck(reconstructed==cleared,'BACKGROUND_IDEAL_WITNESS')
 for engine in ('primary','independent'):
  ip=BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+engine+'.json');ck(bound.get(str(ip))==sha(ip),'INITIAL_PIN');lo,hi=map(Q,read(ip)['initial_native'][3]['exact_bounds']);ck(hi<0 or lo>0,'ANALYTIC_T_NONZERO')
 required={f'{row}:{n}' for row in ('LOWER_TRACE','LOWER_MIXED','LOWER_SCALAR','LOWER_RADIAL') for n in range(1,7)}|{'TRACE7_POLYNOMIAL','TRACE7_DIVISOR','FULL_TRACE7','FULL_MIXED7','FULL_SCALAR7','FULL_RADIAL7','SEVENTH_BIANCHI_REMAINDER'}
 required|={'BACKGROUND_RADIAL','BACKGROUND_SCALAR','MUTATION:TRACE_C3C4','MUTATION:TRACE_P1C6'}
 required|={'EXACT_PSEUDO_ELIMINATION:'+x for x in expected}
 required|={'LOWER_ONLY:'+src+':'+v for src in ('c7','Sp7','Sc7','Sg7') for v in ('p7','f7','g7')}
 ck(required==set(r['checks']) and len(r['checks'])==len(required),'QUALIFIER_CONTROL_COVERAGE')
 for src in ('c7','Sp7','Sc7','Sg7'):
  poly=unpack(r['sources'][src])
  for v in ('p7','f7','g7'):ck(all(k[names.index(v)]==0 for k in poly),'INDEPENDENT_LOWER_ONLY:'+src+':'+v)
 # The trace row must cancel exactly after multiplying by its declared divisor.
 c7=unpack(r['sources']['c7']);qt7=unpack(r['sources']['qT7'])
 tracepoly=add(mul(mul(scalar(7),mul(rate,add(mul(scalar(7),rate),h,-1))),c7),qt7)
 # Substitute N7 alone, clearing its denominator independently.
 ni=names.index('N7');top=max((p[ni] for p in tracepoly),default=0)
 nd=mul(scalar(7),add(mul(scalar(7),rate),h,-1));traceclear={}
 for p,v in tracepoly.items():
  key=list(p);degree=key[ni];key[ni]=0
  traceclear=add(traceclear,mul(mul({tuple(key):v},power(rate,degree)),power(nd,top-degree)))
 ck(not traceclear,'INDEPENDENT_TRACE_DIVISOR')
 for p,hsh in bound.items():ck(sha(p)==hsh,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),cumulative_T_power=cumulative,scope='Independent dictionary-polynomial verification of every saved pseudo-elimination witness, rational denominator clearing and final background-ideal reconstruction, plus authority/input closure. Direct nonlinear extraction and full/lower equation checks are source-reviewed inherited qualifier evidence, not independently regenerated here. Selected analytic-background extension across isolated T zeros; no walls or physical solution.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'SEVENTH_BULK_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<1793101111-600,'LINUX_CUTOFF');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  s=importlib.util.spec_from_file_location('seventh_review_lease',lp);lease=importlib.util.module_from_spec(s);s.loader.exec_module(lease);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<1793101111-600,'POST_LEASE_CUTOFF')
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
