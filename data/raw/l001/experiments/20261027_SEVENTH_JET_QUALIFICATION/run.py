"""Bounded seventh spatial-jet qualification; no field solve."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793108564
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
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','jets.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 authority=BASE/'20261027_SEVENTH_COEFFICIENT_CAMPAIGN/AUTHORITY.txt';sources[str(authority)]=sha(authority)
 parent=BASE/'20261027_FINITE_INVERSE_CLOCK_READOUT_R1';bind(parent/'TERMINAL.json','021554e08ab49c101029b120d1614924805cf81fd2d4b140df0cfd48f5509605');t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for g in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[g].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/FINITE_INVERSE_CLOCK_AUDIT_R1.json';bind(ap,'481904b7050ad17cf68d9326cc40a9d075fdbafd10573097f3cc1feeed3fd196');need(read(ap)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 from fractions import Fraction as Q
 next_arm=read(parent/'RESULT.json')['arms']['finite_inverse24']['next_larger'];initials={engine:auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json') for engine in ('primary','independent')}
 wp=BASE/'20261027_SEVENTH_WALL_QUALIFICATION';bind(wp/'TERMINAL.json','d59ed9a465d3e067efd4838d2777ba50a76268dd6357a50746ccf8af4c9a502d');wt=read(wp/'TERMINAL.json');need(wt['pass_status'],'WALL_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('wall.py','wall_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(wp/n,wt[k])
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_WALL_AUDIT.json';bind(ap,'7141ba421b94422024179f48e67765f08c4f410d2e66a0b86630c81e1c17c224');need(read(ap)['PASS'],'WALL_AUDIT_PASS')
 paths=['20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py','20261026_GROWING_MODE_CUBIC_FLOW/sources.py','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py','20261027_SEVENTH_WALL_QUALIFICATION/wall.py']
 for n in paths:need(inputs.get(str(BASE/n))==sha(BASE/n),'AUTH_MODULE:'+n)
 ring,cubic,quartic,wall=[load('seventh_jets_'+str(i),BASE/n) for i,n in enumerate(paths)]
 module=load('seventh_jets_new',ROOT/'jets.py');fifth=auth('20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 costs=next_arm['costs'];need(Q(costs['seventh'])>1 and all(v for k,v in next_arm['gates'].items() if k!='clock'),'SEVENTH_INDIVIDUAL_OBSTRUCTION')
 for engine in ('primary','independent'):
  lo,hi=map(Q,initials[engine]['initial_native'][3]['exact_bounds']);need(hi<0 or lo>0,'T_NOT_IDENTICALLY_ZERO')
 result=module.build(ring,cubic,quartic,fifth,wall);need(result['pass_status'],'QUALIFIED');result['seconds']=time.monotonic()-start
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'run.py'),jets_sha256=sha(ROOT/'jets.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,checks=len(result['checks']),seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('seventh_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('SEVENTH_JETS_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc(),evidence=getattr(e,'evidence',None)));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
