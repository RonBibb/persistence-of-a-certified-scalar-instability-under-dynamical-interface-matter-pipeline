"""Bounded exact quintic moving-wall source qualification."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
CUTOFF=1793082611
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def need(v,n):
 if not v:raise AssertionError(n)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
 p=ROOT/n;t=ROOT/(n+'.tmp')
 with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(t,0o444);os.link(t,p);t.unlink()
 fd=os.open(ROOT,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)

def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','wall.py','DERIVATION.txt')}
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 parent=BASE/'20261027_QUARTIC_WALL_QUALIFICATION'
 need(sha(parent/'TERMINAL.json')=='ee482b3c718d111cbd0e7f0091ba95b3747fb52ab6d5d1f2b5d10b1062410f7c','PARENT_TERMINAL')
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('wall.py','wall_sha256'),('DERIVATION.txt','derivation_sha256')]:
  need(sha(parent/n)==t[k],'PARENT_ARTIFACT');inputs[str(parent/n)]=t[k]
 inputs[str(parent/'TERMINAL.json')]=sha(parent/'TERMINAL.json')
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_BINDING:'+p);inputs[p]=h
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
 oldpath=parent/'wall.py'
 for p in (ringpath,oldpath):need(inputs.get(str(p))==sha(p),'INHERITED_SOURCE')
 ring=load('quartic_wall_ring',ringpath);old=load('quartic_old_wall',oldpath);module=load('quartic_new_wall',ROOT/'wall.py')
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=CUTOFF))
 result=module.qualify(ring,old);need(result['pass_status'],'QUALIFICATION_PASS');result['seconds']=time.monotonic()-started
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'run.py'),wall_sha256=sha(ROOT/'wall.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,checks=len(result['checks']),seconds=result['seconds'])),flush=True)

if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF,'LINUX_LAUNCH_CUTOFF')
  need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('quartic_clock_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
  need(time.time()<CUTOFF,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('QUINTIC_WALL_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()


