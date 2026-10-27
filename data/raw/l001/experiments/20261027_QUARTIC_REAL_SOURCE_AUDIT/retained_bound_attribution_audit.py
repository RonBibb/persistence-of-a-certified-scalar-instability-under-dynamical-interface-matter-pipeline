"""Independent Fraction convolution readout; no producer arithmetic imports."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_RETAINED_BOUND_ATTRIBUTION';CUTOFF=1793108564;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ss(d):return {str(k):str(v) for k,v in d.items()}
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 term=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(term['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]
 for n,k in files:ck(sha(ROOT/n)==term[k],'TERMINAL:'+n)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 path=BASE/'20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json';ck(bound.get(str(path))==sha(path),'DATA_AUTH');data=read(path);result=read(ROOT/'RESULT.json')
 a=Q(data['arms']['both']['constants']['physical_radius'])/2;ck(Q(result['eta'])==a and set(result['rows'])=={'8','9'},'POINT_ORDERS');summary={}
 for n in (8,9):
  ck(set(result['rows'][str(n)])=={'primary','independent'},'ENGINES');summary[str(n)]={}
  for engine in ('primary','independent'):
   rec=data['coefficient_records'][str(n)][engine];terms=rec['new_terms'];ck(set(terms)=={'leading'}|set(map(str,range(1,n))),'TERM_COVERAGE')
   intervals={k:tuple(map(Q,v)) for k,v in terms.items()};ck(all(len(v)==2 and v[0]<=v[1] for v in intervals.values()),'INTERVAL_ORDER')
   absbounds={k:max(-v[0],v[1]) for k,v in intervals.items()};L=absbounds['leading'];P=sum(absbounds[str(j)] for j in range(1,n));T=L+P;ck(T>0,'POSITIVE_TRIANGLE')
   lower=sum(intervals[k][0] for k in intervals);upper=sum(intervals[k][1] for k in intervals);saved=tuple(map(Q,rec['new']))
   ck(lower<=saved[0]<=saved[1]<=upper,'INTERVAL_CONTAINMENT');ck(max(-saved[0],saved[1])==Q(rec['new_abs']),'STORED_ABSOLUTE')
   scale=a**(n-2)/10
   expected=dict(component_absolute_bounds=ss(absbounds),leading_bound=str(L),lower_product_bound=str(P),triangle_bound=str(T),leading_share_of_triangle=str(L/T),normalized_leading=str(L*scale),normalized_lower_products=str(P*scale),normalized_triangle=str(T*scale),stored_coefficient_bound=rec['new_abs'],adopted_bound=data['new_clock_bounds'][str(n)],distributed_interval=list(map(str,(lower,upper))),stored_interval=list(map(str,saved)),intervals_exactly_equal=(lower,upper)==saved,distributed_contains_stored=True)
   ck(result['rows'][str(n)][engine]==expected,'COMPLETE_ATTRIBUTION')
   summary[str(n)][engine]=dict(leading_share=float(L/T),normalized_leading=float(L*scale),normalized_lower_products=float(P*scale),normalized_triangle=float(T*scale),normalized_stored=float(Q(rec['new_abs'])*scale),normalized_adopted=float(Q(data['new_clock_bounds'][str(n)])*scale),intervals_exactly_equal=(lower,upper)==saved)
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for n,k in files:ck(sha(ROOT/n)==term[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),eta=float(a),rows=summary,scope='Independent exact saved-interval absolute/triangle/share/normalization and containment arithmetic, four records and provenance. No new field coefficient, cancellation inference, physical contribution attribution or amplitude certificate.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'RETAINED_BOUND_ATTRIBUTION_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('positive_tail_full_review',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
