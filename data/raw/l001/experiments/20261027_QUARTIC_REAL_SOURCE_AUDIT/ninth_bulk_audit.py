"""Staged n9 dictionary-polynomial witness audit, not producer replay.

Direct PDE extraction remains source-reviewed qualifier evidence. This auditor
independently checks the saved algebraic compatibility witnesses and closure.
"""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE/'20261027_NINTH_BULK_QUALIFICATION';CUTOFF=1793121042
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
HELPER=HERE/'eighth_bulk_audit_r1.py';helper_pin=sha(HELPER)
a=load('ninth_independent_dictionary_arithmetic',HELPER)
ck,unpack,add,mul,power,variable,scalar=a.ck,a.unpack,a.add,a.mul,a.power,a.variable,a.scalar
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('bulk.py','bulk_sha256'),('series.py','series_sha256'),('DERIVATION.txt','derivation_sha256'),('GROUPING_EQUIVALENCE.json','equivalence_sha256'),('STAGES.jsonl','stages_sha256')]
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'AUTH:'+path);return read(p)
 previous_order=auth('20261027_EIGHTH_BULK_QUALIFICATION_R1/RESULT.json')
 pa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/EIGHTH_BULK_AUDIT_R1.json');ck(pa['PASS'] and pa['producer_terminal']==sha(BASE/'20261027_EIGHTH_BULK_QUALIFICATION_R1/TERMINAL.json'),'EIGHTH_AUDIT_MATCH')
 ck(helper_pin==pa['audit_source_sha256'],'AUTHENTICATED_HELPER_SOURCE')
 eq=read(ROOT/'GROUPING_EQUIVALENCE.json');cases=3+3*len(previous_order['pseudo_elimination'])
 ck(eq['pass_status'] and eq['cases']==cases and eq['variable_cases']==cases*len(previous_order['variables']),'GROUPING_EQUIVALENCE_COVERAGE')
 r=read(ROOT/'RESULT.json');names=r['variables'];ck(len(names)==len(set(names)),'UNIQUE_VARIABLES');a.ZERO=(0,)*len(names)
 T=variable(names.index('T'));rate=variable(names.index('r'));h=variable(names.index('h'))
 expected=['g8','g7','g6','g5','g4','g3','G','g'];ck([w['variable'] for w in r['pseudo_elimination']]==expected,'ELIMINATION_ORDER')
 previous=None;cumulative=0
 for w in r['pseudo_elimination']:
  before,after,c,q=[unpack(w[k]) for k in ('input','output','constraint','quotient')];i=names.index(w['variable']);N=w['power']
  if previous is not None:ck(before==previous,'WITNESS_CHAIN')
  ck(N==max((v[i] for v in before),default=0),'ACTUAL_VARIABLE_DEGREE')
  ck(add(add(mul(power(T,N),before),after,-1),mul(c,q),-1)=={},'PSEUDO_IDENTITY:'+w['variable'])
  ck(all(v[i]==0 for v in after),'VARIABLE_REMOVED:'+w['variable'])
  ct=add(c,mul(T,variable(i)),-1);ck(all(v[i]==0 for v in ct),'TRIANGULAR_CONSTRAINT')
  previous=after;cumulative+=N
 ck(cumulative==r['cumulative_T_power'],'CUMULATIVE_POWER')
 indices=[names.index(x) for x in ('C','J','L','M','N6','N7','N8','N9')]
 nums=[rate,mul(scalar(4),rate)]+[rate]*6
 dens=[mul(scalar(n),add(mul(scalar(n),rate),h,-1)) for n in range(2,10)]
 tops=[max((p[i] for p in previous),default=0) for i in indices]
 cached=[([power(num,j) for j in range(top+1)],[power(den,j) for j in range(top+1)]) for num,den,top in zip(nums,dens,tops)]
 cleared={}
 for p,v in previous.items():
  key=list(p);powers=[p[i] for i in indices]
  for i in indices:key[i]=0
  term={tuple(key):v}
  for n,top,(nump,denp) in zip(powers,tops,cached):term=mul(mul(term,nump[n]),denp[top-n])
  cleared=add(cleared,term)
 ck(cleared==unpack(r['compatibility_reduction_lhs']),'INDEPENDENT_RATIONAL_CLEARING')
 H=variable(names.index('H'));Phi=variable(names.index('Phi'));mass=variable(names.index('m'));e=variable(names.index('e'))
 bg=add(add(add(mul(scalar(6),power(H,2)),mul(scalar(Q(1,2)),power(T,2)),-1),scalar(6),-1),mul(scalar(Q(1,2)),mul(mass,power(Phi,2))))
 bg=add(bg,mul(scalar(6),mul(power(h,2),e)),-1)
 ck(len(r['compatibility_reduction_basis'])==len(r['compatibility_quotients'])==1 and unpack(r['compatibility_reduction_basis'][0])==bg,'ACTUAL_BACKGROUND_BASIS')
 remainder=unpack(r['compatibility_remainder']);ck(not remainder,'ZERO_REMAINDER');reconstructed=dict(remainder)
 for b,q in zip(r['compatibility_reduction_basis'],r['compatibility_quotients']):reconstructed=add(reconstructed,mul(unpack(b),unpack(q)))
 ck(reconstructed==cleared,'BACKGROUND_IDEAL_WITNESS')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 for engine in ('primary','independent'):
  initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');lo,hi=map(Q,initial['initial_native'][3]['exact_bounds']);ck(hi<0 or lo>0,'ANALYTIC_T_NOT_IDENTICALLY_ZERO')
  rlo=Q(clock['arms'][engine]['values']['rate']['exact_bounds'][0]);hhi=Q(initial['parameters']['h']['exact_bounds'][1]);ck(9*rlo>hhi,'TRACE9_POSITIVE_DIVISOR')
 required={f'{row}:{n}' for row in ('LOWER_TRACE','LOWER_MIXED','LOWER_SCALAR','LOWER_RADIAL') for n in range(1,9)}|{'TRACE9_POLYNOMIAL','TRACE9_DIVISOR','FULL_TRACE9','FULL_MIXED9','FULL_SCALAR9','FULL_RADIAL9','NINTH_BIANCHI_REMAINDER','BACKGROUND_RADIAL','BACKGROUND_SCALAR','MUTATION:TRACE_C4_C5','MUTATION:TRACE_P1C8'}
 required|={'EXACT_PSEUDO_ELIMINATION:'+x for x in expected}
 required|={'LOWER_ONLY:'+src+':'+v for src in ('c9','Sp9','Sc9','Sg9') for v in ('p9','f9','g9')}
 ck(required==set(r['checks']) and len(r['checks'])==len(required),'QUALIFIER_CONTROL_COVERAGE')
 for src in ('c9','Sp9','Sc9','Sg9'):
  poly=unpack(r['sources'][src])
  for v in ('p9','f9','g9'):ck(all(k[names.index(v)]==0 for k in poly),'INDEPENDENT_LOWER_ONLY:'+src+':'+v)
 c9=unpack(r['sources']['c9']);qt9=unpack(r['sources']['qT9']);nd=mul(scalar(9),add(mul(scalar(9),rate),h,-1))
 tracepoly=add(mul(mul(rate,nd),c9),qt9);ni=names.index('N9');top=max((p[ni] for p in tracepoly),default=0);traceclear={}
 for p,v in tracepoly.items():
  key=list(p);degree=key[ni];key[ni]=0;traceclear=add(traceclear,mul(mul({tuple(key):v},power(rate,degree)),power(nd,top-degree)))
 ck(not traceclear,'INDEPENDENT_TRACE_DIVISOR')
 for p,hsh in bound.items():ck(sha(p)==hsh,'POST_BOUND:'+p)
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'POST_TERMINAL:'+f)
 ck(sha(ROOT/'TERMINAL.json')==pin and sha(HELPER)==helper_pin,'TERMINAL_HELPER_UNCHANGED')
 return dict(PASS=True,checks=a.COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),helper_source_sha256=helper_pin,cumulative_T_power=cumulative,scope='Independent dictionary-polynomial saved pseudo-elimination, rational clearing, background-ideal and trace-divisor witnesses; lower-only checks and bound prerequisite closure. Direct nonlinear PDE extraction and full/lower rows are inherited source-reviewed qualifier evidence, not independently regenerated. Analytic selected-background extension across isolated T zeros; no ninth walls, field solve or physical trajectory.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=HERE/'NINTH_BULK_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_CUTOFF');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_review_lease',lp);lease.ROOT=HERE;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=a.COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
