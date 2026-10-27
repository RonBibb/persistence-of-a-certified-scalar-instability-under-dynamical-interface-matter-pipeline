"""Bounded fresh continuation: fifth inverse/endpoint probe then frozen repeat."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
MODE=sys.argv[1] if len(sys.argv)==2 else ''
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def need(v,n):
 if not v:raise AssertionError(n)
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
 p=ROOT/(MODE+'_'+n);t=Path(str(p)+'.tmp')
 with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(t,0o444);os.link(t,p);t.unlink()
 fd=os.open(ROOT,os.O_RDONLY)
 try:os.fsync(fd)
 finally:os.close(fd)
def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','flow.py','AUTHORITY.txt','DERIVATION.txt')}
 def bind(p,h):
  need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def closure(p):
  for group in ('inputs','sources','runtime'):
   for path,h in read(p)[group].items():bind(path,h)
 parent=BASE/'20261027_QUINTIC_GLOBAL_BULK_PROBE'
 bind(parent/'TERMINAL.json','f8557fe17948db2cac2cf4240ce094f61304bb6eed50c556bf42c7727f4ffb85')
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'GLOBAL_SOURCE_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('interval.py','interval_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 closure(parent/'BINDING.json')
 wall=BASE/'20261027_QUINTIC_WALL_QUALIFICATION'
 bind(wall/'TERMINAL.json','b8735f32838bb5072e3089917c98adeba0ec95cea8a15e8c5da6c48f7f3a153f')
 t=read(wall/'TERMINAL.json');need(t['pass_status'],'WALL_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('wall.py','wall_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(wall/n,t[k])
 closure(wall/'BINDING.json')
 audits=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'
 bind(audits/'QUINTIC_GLOBAL_AUDIT.json','903dbf07bf1828364d7a2273fd28e4e4d4a36d5a910662581729213fbe1c821a')
 bind(audits/'QUINTIC_WALL_AUDIT_R1.json','6e98b74ce3b98c5d5b5defca5963f8ce4c06fde5ac8fe97a97f3c0fdd5bede96')
 for n in ('lease.py','DESIGN.txt'):
  path=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(path)]=sha(path)
 archive=BASE/'20261027_QUARTIC_REAL_SOURCE_ENCLOSURE'
 cubicpath=BASE/'20261026_GROWING_MODE_CUBIC_FLOW/sources.py';quarticpath=BASE/'20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py'
 inversepath=BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json'
 for path in (cubicpath,quarticpath,inversepath,parent/'interval.py'):need(inputs.get(str(path))==sha(path),'QUALIFIED_IMPORT')
 interval=load('fifth_interval',parent/'interval.py');cubic=load('fifth_cubic',cubicpath);quartic=load('fifth_quartic',quarticpath);wall5=load('fifth_wall',wall/'wall.py');flow=load('fifth_flow',ROOT/'flow.py')
 qp=BASE/'20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json';need(inputs.get(str(qp))==sha(qp),'QUALIFIED_POLYNOMIAL')
 flow.setup(interval.I,cubic,quartic,wall5,read(qp))
 len(str(10**20000));runtime=lease.observed()
 for path,h in runtime.items():need(inputs.get(path)==h or sources.get(path)==h,'RUNTIME:'+path)
 if MODE=='production':
  need(not (ROOT/'probe_FAILURE.json').exists(),'NO_FAILED_PROBE')
  pt=read(ROOT/'probe_TERMINAL.json');need(pt['pass_status'],'PROBE_PASS')
  need(sha(ROOT/'probe_RESULT.json')==pt['result_sha256'] and sha(ROOT/'probe_BINDING.json')==pt['binding_sha256'],'PROBE_ARTIFACTS')
  pb=read(ROOT/'probe_BINDING.json');need(pb==dict(inputs=inputs,sources=sources,runtime=runtime),'FROZEN_PROBE_BINDING')
  for n,k in [('run.py','source_sha256'),('flow.py','flow_sha256'),('AUTHORITY.txt','authority_sha256'),('DERIVATION.txt','derivation_sha256')]:need(sources[str(ROOT/n)]==pt[k],'PROBE_SOURCE:'+n)
  need(read(ROOT/'probe_RESULT.json')['seconds']<120,'PROBE_RESOURCE_ADMISSION')
  for n in ('probe_TERMINAL.json','probe_RESULT.json','probe_BINDING.json'):bind(ROOT/n,sha(ROOT/n))
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 inv=read(inversepath);need(inv['scientific_certificate'],'INVERSE_CERTIFIED')
 globaldata=read(parent/'RESULT.json');arms={}
 for engine in ('primary','independent'):
  ap=archive/('ARM_'+engine+'.json');op=BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'/('PRODUCTION_'+engine+'.json');ip=BASE/'20261026_GROWING_INVERSE_READINESS_R1'/('INITIAL_'+engine+'.json')
  for path in (ap,op,ip):need(inputs.get(str(path))==sha(path),'ENGINE_INPUT_AUTH')
  arm,old,initial=read(ap),read(op),read(ip)
  need(arm['D']==initial['D'],'INVERSE_DOMAIN_IDENTITY')
  for k,v in initial['parameters'].items():need(arm['parameters'][k]==v,'INVERSE_PARAMETER_IDENTITY:'+k)
  out=flow.calculate(arm,old,globaldata['arms'][engine],inv['arms'][engine])
  put('ARM_'+engine+'.json',out);arms[engine]=out
  print(json.dumps(dict(mode=MODE,engine=engine,seconds=time.monotonic()-started,d5=[float(Q(x)) for x in out['bulk']['d5']['exact_bounds']])),flush=True)
 lo=[Q(arms[e]['bulk']['d5']['exact_bounds'][0]) for e in arms];hi=[Q(arms[e]['bulk']['d5']['exact_bounds'][1]) for e in arms]
 need(max(lo)<=min(hi),'ENCLOSURE_COMPATIBILITY_NOT_ACCURACY')
 hull=interval.I(min(lo),max(hi)).pack()
 if MODE=='production':
  previous=read(ROOT/'probe_RESULT.json');need(previous['arms']==arms and previous['d5']==hull,'EXACT_PROBE_REPRODUCTION')
 for path,h in dict(inputs,**sources).items():need(sha(path)==h,'POST_BINDING:'+path)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 result=dict(pass_status=True,mode=MODE,arms=arms,d5=hull,seconds=time.monotonic()-started,scope='Unsigned actual fifth coefficient enclosure conditional on inherited authenticated lower fields and analytic-family/inverse premises. No fifth profile, sign, finite trajectory or new full-clock certificate.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/(MODE+'_RESULT.json')),binding_sha256=sha(ROOT/(MODE+'_BINDING.json')),source_sha256=sha(ROOT/'run.py'),flow_sha256=sha(ROOT/'flow.py'),authority_sha256=sha(ROOT/'AUTHORITY.txt'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,mode=MODE,seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and MODE in ('probe','production'),'LINUX_AND_MODE')
  need(not any((ROOT/(MODE+'_'+n)).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('fifth_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('FIFTH_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  if MODE in ('probe','production'):put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()))
  raise
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()

