"""Separate R1 resource-control audit plus unchanged dictionary witness audit.

No producer polynomial engine is imported. The inherited reviewer implementation
is source-pinned in this report, while its arithmetic helper is authenticated by
the sealed eighth independent audit as required by the underlying audit.
"""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE/'20261027_NINTH_BULK_QUALIFICATION_R2';CUTOFF=1793121042
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
REVIEWER=HERE/'ninth_bulk_witness_r2.py';reviewer_pin=sha(REVIEWER);review=load('ninth_r1_witness_reviewer',REVIEWER);review.ROOT=ROOT;ck=review.ck
def main():
 t=read(ROOT/'TERMINAL.json');binding=read(ROOT/'BINDING.json');bound={}
 for group in ('inputs','sources','runtime'):bound.update(binding[group])
 extra=[('bounded_ring.py','ring_sha256'),('RING_EQUIVALENCE.json','ring_equivalence_sha256')]
 for f,k in extra:ck(sha(ROOT/f)==t[k],'R1_TERMINAL:'+f)
 original=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
 ck(bound.get(str(original))==sha(original),'ORIGINAL_RING_AUTH');ck(bound.get(str(ROOT/'bounded_ring.py'))==sha(ROOT/'bounded_ring.py'),'PRIVATE_RING_AUTH')
 text=original.read_text().split('\nclass S:')[0]
 text=text.replace('"""Exact Eulerian quadratic S6 source qualification, no n2 solution."""','"""Private n9 R1 ring: unchanged arithmetic, fixed200k multiplication-term cap."""',1)
 text=text.replace('ROOT=Path(__file__).resolve().parent',"ROOT=Path(__file__).resolve().parent.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'",1)
 ck(text.count("len(d)<=50000,'POLYNOMIAL_TERM_CAP'")==1,'ONE_DECLARED_RESOURCE_CHANGE')
 text=text.replace("len(d)<=50000,'POLYNOMIAL_TERM_CAP'","len(d)<=200000,'POLYNOMIAL_TERM_CAP'",1)
 ck((ROOT/'bounded_ring.py').read_text().rstrip()==text.rstrip(),'EXACT_PRIVATE_RING_PREFIX_DIFF')
 eq=read(ROOT/'RING_EQUIVALENCE.json');ck(eq==dict(pass_status=True,comparisons=76,term_cap=200000,product_pair_cap=1000000),'RING_CONTROL_RECORD')
 failed=BASE/'20261027_NINTH_BULK_QUALIFICATION'
 for name in ('run.py','bulk.py','series.py','DERIVATION.txt','FAILURE.json','STAGES.jsonl'):
  path=failed/name;ck(bound.get(str(path))==sha(path),'PRESERVED_FAILURE_AUTH:'+name)
 failure=read(failed/'FAILURE.json');ck(failure['classification']=='TECHNICAL_INCOMPLETE' and 'POLYNOMIAL_TERM_CAP' in failure['error'],'PRESERVED_TERM_CAP_FAILURE')
 failedr1=BASE/'20261027_NINTH_BULK_QUALIFICATION_R1'
 for name in ('run.py','bulk.py','series.py','bounded_ring.py','DERIVATION.txt','FAILURE.json','STAGES.jsonl'):
  path=failedr1/name;ck(bound.get(str(path))==sha(path),'PRESERVED_R1_TIMEOUT:'+name)
 ck('TimeoutError' in read(failedr1/'FAILURE.json')['error'],'PRESERVED_CLEARING_TIMEOUT')
 expected_cases=3+3*len(read(BASE/'20261027_EIGHTH_BULK_QUALIFICATION_R1/RESULT.json')['pseudo_elimination'])
 ck(read(ROOT/'RESULT.json')['clearing_equivalence']==dict(pass_status=True,cases=expected_cases),'CLEARING_SAMPLE_COVERAGE')
 result=review.main()
 for f,k in extra:ck(sha(ROOT/f)==t[k],'POST_R1_TERMINAL:'+f)
 ck(sha(REVIEWER)==reviewer_pin,'REVIEWER_UNCHANGED')
 result.update(checks=review.a.COUNT,reviewer_source_sha256=reviewer_pin,resource_control_scope='Exact source-prefix comparison establishes only fixed200k multiplication-term cap and explicit original common.py owner path changed. Other product/reduction bounds unchanged; recorded76 equivalence controls inherited producer evidence, not independently rerun here. Both failed packets authenticated and preserved. Independent full clearing uses cached dictionary powers and in-place coefficient accumulation, algebraically unchanged; producer clearing sample controls are recorded evidence, not independent full reexecution.')
 return result
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=HERE/'NINTH_BULK_AUDIT_R2.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_CUTOFF');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_r1_review_lease',lp);lease.ROOT=HERE;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=review.a.COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)

