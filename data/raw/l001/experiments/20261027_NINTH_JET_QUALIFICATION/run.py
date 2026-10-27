"""Bounded ninth spatial-jet qualification; authenticated wall parent required."""
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
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','jets.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 pins=read(ROOT/'PINS.json');sources[str(ROOT/'PINS.json')]=sha(ROOT/'PINS.json')
 parent=BASE/'20261027_NINTH_WALL_QUALIFICATION';bind(parent/'TERMINAL.json',pins['wall_terminal']);t=read(parent/'TERMINAL.json');need(t['pass_status'],'WALL_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('wall.py','wall_sha256'),('PINS.json','pins_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/NINTH_WALL_AUDIT.json';bind(ap,pins['wall_audit']);a=read(ap);need(a['PASS'] and a['producer_terminal']==pins['wall_terminal'],'WALL_AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 for n,h in [('EIGHTH_JET_AUDIT.json','8abaee44a6f7bca7033430dabd89702140fc680396fa8a87245f376738e0ab1b'),('SEVENTH_BULK_AUDIT.json','89f0d76a6d906e38d4954cd11c3ff75a1b92a3bc0d3965ee85c25eae895c63fb')]:
  ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(ap,h);need(read(ap)['PASS'],'AUDIT_PASS:'+n)
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
 need(inputs.get(str(ringpath))==sha(ringpath),'RING_AUTH')
 ring=load('ninth_jet_ring',ringpath);module=load('ninth_jet_new',ROOT/'jets.py')
 prior=auth('20261027_EIGHTH_JET_QUALIFICATION/RESULT.json');seventh=auth('20261027_SEVENTH_BULK_QUALIFICATION/RESULT.json');fifth=auth('20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json');seventhjets=auth('20261027_SEVENTH_JET_QUALIFICATION/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 result=module.build(ring,prior,seventh,fifth,seventhjets);need(result['pass_status'],'QUALIFIED');result['seconds']=time.monotonic()-start
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'run.py'),jets_sha256=sha(ROOT/'jets.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt'),pins_sha256=sha(ROOT/'PINS.json')))
 print(json.dumps(dict(pass_status=True,checks=len(result['checks']),seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_wall_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NINTH_JET_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
