"""Bounded lower-order replay and actual quartic inverse enclosure."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793082611
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,s):
 if not v:raise AssertionError(s)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
 p=ROOT/n;t=ROOT/(n+'.tmp')
 with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(t,0o444);os.link(t,p);t.unlink();fd=os.open(ROOT,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)

def main(lease,mode):
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','flow.py','DERIVATION.txt')}
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 for packet,pin in [('20261027_QUARTIC_BULK_QUALIFICATION_R2','5caae5d65b28a66b0561e1560ce4162aa6f6d084674992db8c75639bda859f01'),('20261027_SIXTH_CLOCK_ENCLOSURE','d27583c253cb25cc9aad8fba81c391e7590caf93879ded528714d27abbf2eb30')]:
  root=BASE/packet;need(sha(root/'TERMINAL.json')==pin,'PARENT_TERMINAL:'+packet);t=read(root/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
  inputs[str(root/'TERMINAL.json')]=pin
  for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py' if 'BULK' in packet else 'check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:need(sha(root/n)==t[k],'PARENT_ARTIFACT');inputs[str(root/n)]=t[k]
  for group in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_BINDING:'+p);inputs[p]=h
 if mode=='production':
  disk=os.statvfs(ROOT);need(disk.f_bavail*disk.f_frsize>=2*1024**3,'TWO_GIB_OUTPUT_HEADROOM')
  terminal=read(ROOT/'probe_TERMINAL.json');need(terminal['pass_status'],'PROBE_PASS')
  for n,h in terminal['artifacts'].items():need(sha(ROOT/n)==h,'PROBE_ARTIFACT');inputs[str(ROOT/n)]=h
  need(read(ROOT/'probe_BINDING.json')['sources']==sources,'EXACT_PROBED_SOURCE')
  need(read(ROOT/'PROBE_RESULT.json')['production_admissible'],'RESOURCE_FORECAST')
  inputs[str(ROOT/'probe_TERMINAL.json')]=sha(ROOT/'probe_TERMINAL.json')
 cubic=BASE/'20261026_GROWING_MODE_CUBIC_AFFINE';quad=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
 sys.path.insert(0,'/home/parallels/research-runs/cap-interval-arb-2026-09-12');sys.path.insert(0,str(cubic))
 from flint import arb,fmpq,ctx
 ctx.prec=768;ctx.threads=1
 drv=load('quartic_replay_driver',cubic/'run.py');drv.arb=arb;drv.fmpq=fmpq
 drv.adapters=load('quartic_replay_adapters',cubic/'adapters.py');drv.engines={n:getattr(drv.adapters,n)() for n in ('primary','independent')}
 drv.quad=load('quartic_replay_quad',quad/'run.py');drv.quad.wall=load('quartic_replay_quadwall',quad/'wall.py')
 drv.wall=load('quartic_replay_cubicwall',BASE/'20261026_GROWING_MODE_CUBIC_WALL/wall.py');drv.wall_affine=load('quartic_replay_affinewall',cubic/'wall_affine.py')
 source=load('quartic_replay_source',BASE/'20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall4=load('quartic_replay_wall4',BASE/'20261027_QUARTIC_WALL_QUALIFICATION/wall.py');flow=load('quartic_replay_flow',ROOT/'flow.py')
 flow.setup(drv,source,wall4,arb,fmpq,read,put,BASE);flow.ROOT=ROOT;flow.SHA=sha
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put(mode+'_BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,precision_bits=768,mode=mode,cutoff_unix=CUTOFF));flow.BINDING=sha(ROOT/(mode+'_BINDING.json'))
 arms={name:flow.run(name,mode=='probe') for name in ('primary','independent')}
 if mode=='probe':
  projection=1.5*sum(row['projection_seconds'] for row in arms.values());out=dict(pass_status=True,production_admissible=projection<1800,projection_seconds=projection,arms=arms,scope='Resource/admission sizing only; no full-domain coefficient.')
  put('PROBE_RESULT.json',out)
 else:
  vals=[flow.iv(a['d4']) for a in arms.values()];need(flow.overlap(*vals),'TWO_ENGINE_D4_ENCLOSURE_AGREEMENT');d4=drv.engines['primary'].hull(*vals)
  out=dict(pass_status=True,classification='ACTUAL_QUARTIC_REAL_SOURCE_ENCLOSURE',d4=flow.pack(d4),arms={name:dict(file='ARM_'+name+'.json',sha256=sha(ROOT/('ARM_'+name+'.json'))) for name in arms},seconds=time.monotonic()-start,scope='Unsigned actual fourth-order coefficient enclosure from whole-cell lower-order solutions and certified n4 inverse, not a resolved sign or nonlinear trajectory.')
  put('RESULT.json',out)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
 artifacts={p.name:sha(p) for p in ROOT.glob('*.json') if not p.name.endswith('_START.json') and not p.name.endswith('_TERMINAL.json')}
 put(mode+'_TERMINAL.json',dict(pass_status=True,artifacts=artifacts,seconds=time.monotonic()-start))
 print(json.dumps(out),flush=True)

if __name__=='__main__':
 lease=None;mode=sys.argv[1]
 try:
  need(mode in ('probe','production') and sys.platform=='linux','MODE_LINUX')
  need(time.time()<CUTOFF,'LAUNCH_CUTOFF');need(not any(ROOT.glob('*FAILURE.json')) and not (ROOT/(mode+'_START.json')).exists(),'NO_RESTART')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('quartic_source_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('QUARTIC_SOURCE_RESOURCE_CAP')));signal.alarm(600 if mode=='probe' else 2400)
  put(mode+'_START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,mode)
 except BaseException as e:
  put(mode+'_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for f in lease.handles:f.close()
