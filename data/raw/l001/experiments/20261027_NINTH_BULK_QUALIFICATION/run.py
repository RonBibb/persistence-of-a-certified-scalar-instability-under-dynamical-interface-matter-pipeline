"""Bounded actual ninth bulk identities; no field solve."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793121042
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def need(v,n):
 if not v:raise AssertionError(n)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
 p=ROOT/n;t=ROOT/(n+'.tmp')
 with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(t,0o444);os.link(t,p);t.unlink();fd=os.open(ROOT,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main(lease):
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','bulk.py','series.py','DERIVATION.txt')}
 def progress(stage,**data):
  row=dict(stage=stage,elapsed_seconds=time.monotonic()-start,**data)
  with (ROOT/'STAGES.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
  print(json.dumps(row),flush=True)
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_ACTUAL_EIGHTH_FULL_BUDGET';bind(parent/'TERMINAL.json','9ff596a88beb1b1947f81e8deb73d630a6033a4b577728b3c958305baab23532');t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for g in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[g].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/ACTUAL_EIGHTH_FULL_BUDGET_AUDIT.json';bind(ap,'84bd2bface15205ec12306299c3e2c298b42d67dab1bb5a36696d7318e915450');need(read(ap)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 from fractions import Fraction as Q
 next_arm=read(parent/'RESULT.json')['upper'];initials={engine:auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json') for engine in ('primary','independent')}
 paths=['20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py','20261026_GROWING_MODE_CUBIC_FLOW/sources.py','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py']
 for n in paths:need(inputs.get(str(BASE/n))==sha(BASE/n),'AUTH_MODULE:'+n)
 ring,cubic,quartic=[load('ninth_'+str(i),BASE/n) for i,n in enumerate(paths)]
 module=load('ninth_bulk',ROOT/'bulk.py');S=load('ninth_series',ROOT/'series.py').S;fifth=auth('20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json');need(fifth['pass_status'],'FIFTH_PASS');sixth=auth('20261027_SIXTH_BULK_QUALIFICATION/RESULT.json');need(sixth['pass_status'],'SIXTH_PASS')
 eighth=auth('20261027_EIGHTH_BULK_QUALIFICATION_R1/RESULT.json');need(eighth['pass_status'],'EIGHTH_PASS')
 seventh=auth('20261027_SEVENTH_BULK_QUALIFICATION/RESULT.json');need(seventh['pass_status'],'SEVENTH_PASS')
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_BULK_AUDIT.json';bind(ap,'89f0d76a6d906e38d4954cd11c3ff75a1b92a3bc0d3965ee85c25eae895c63fb');need(read(ap)['PASS'],'SEVENTH_AUDIT')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 costs=next_arm['costs'];need(Q(costs['ninth'])>Q(99,100) and all(v for k,v in next_arm['gates'].items() if k!='clock'),'NINTH_INDIVIDUAL_OBSTRUCTION')
 for engine in ('primary','independent'):
  lo,hi=map(Q,initials[engine]['initial_native'][3]['exact_bounds']);need(hi<0 or lo>0,'T_NOT_IDENTICALLY_ZERO')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 for engine in ('primary','independent'):
  vals=clock['arms'][engine]['values'];rlo=Q(vals['rate']['exact_bounds'][0]);hhi=Q(initials[engine]['parameters']['h']['exact_bounds'][1])
  need(9*rlo>hhi,'POSITIVE_TRACE9_DIVISOR')
 progress('grouping_equivalence_start')
 eq=module.verify_grouping(ring,eighth);put('GROUPING_EQUIVALENCE.json',eq);progress('grouping_equivalence_pass',**eq)
 result=module.qualify(ring,S,cubic,quartic,fifth,sixth,seventh,eighth,progress);need(result['pass_status'],'QUALIFIED');result['seconds']=time.monotonic()-start
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'run.py'),bulk_sha256=sha(ROOT/'bulk.py'),series_sha256=sha(ROOT/'series.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt'),equivalence_sha256=sha(ROOT/'GROUPING_EQUIVALENCE.json'),stages_sha256=sha(ROOT/'STAGES.jsonl')))
 print(json.dumps(dict(pass_status=True,checks=len(result['checks']),seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NINTH_BULK_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc(),evidence=getattr(e,'evidence',None)));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
