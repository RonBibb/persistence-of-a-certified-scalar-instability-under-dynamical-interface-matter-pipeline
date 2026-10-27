"""Actual ninth source/inverse enclosure; bounded no-ODE calculation."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
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
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','flow.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def packet(name,pin,fields):
  root=BASE/name;bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS:'+name)
  for n,k in fields:bind(root/n,t[k])
  for g in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[g].items():bind(p,h)
 standard=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]
 pins=read(ROOT/'PINS.json');sources[str(ROOT/'PINS.json')]=sha(ROOT/'PINS.json')
 packet('20261027_NINTH_BULK_QUALIFICATION_R2',pins['bulk_terminal'],standard+[('bulk.py','bulk_sha256'),('series.py','series_sha256'),('bounded_ring.py','ring_sha256')])
 packet('20261027_NINTH_WALL_QUALIFICATION',pins['wall_terminal'],standard+[('wall.py','wall_sha256')])
 packet('20261027_NINTH_JET_QUALIFICATION',pins['jet_terminal'],standard+[('jets.py','jets_sha256')])
 packet('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE','f9cf4da45aec7f49c222878c9b6044aae66fd52eaea5eac60f24a6913c0cb8c1',standard+[('flow.py','flow_sha256')])
 packet('20261027_SIXTH_REAL_SOURCE_ENCLOSURE','4f1f3c44fee76ed158ebb40c773f29b82ce3e8b0fddfa6fd6ceb39231da56a85',standard+[('flow.py','flow_sha256')])
 packet('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE','107d629a3819ed40acb17a124728bddda08f17e3526f9277ad18bc7202a2b43f',standard+[('flow.py','flow_sha256')])
 for n,h in [('EIGHTH_REAL_AUDIT.json','8558df591fefd19b7f1176514b1fbcbcde799c1c78c32b64be606daee1e9e5e3'),('NINTH_BULK_AUDIT_R2.json',pins['bulk_audit']),('NINTH_WALL_AUDIT.json',pins['wall_audit']),('NINTH_JET_AUDIT.json',pins['jet_audit']),('SEVENTH_REAL_AUDIT.json','e78e7b081ccb4ef6075f09e20914ad701068eb9a073bea3f3c320d1b1da0c399'),('SIXTH_REAL_AUDIT_R1.json','440f106140813b08f21548128f735a1989dd1c3996ce9ad39b96268424db4b97')]:
  p=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(p,h);need(read(p)['PASS'],'AUDIT_PASS:'+n)
 for kind in ('bulk','wall','jet'):
  name={'bulk':'NINTH_BULK_AUDIT_R2.json','wall':'NINTH_WALL_AUDIT.json','jet':'NINTH_JET_AUDIT.json'}[kind]
  need(read(BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/name)['producer_terminal']==pins[kind+'_terminal'],'AUDIT_TERMINAL_MATCH:'+kind)
 authority=ROOT/'AUTHORITY.txt';sources[str(authority)]=sha(authority)
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 paths=['20261027_QUINTIC_GLOBAL_BULK_PROBE/interval.py','20261026_GROWING_MODE_CUBIC_FLOW/sources.py','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py','20261027_NINTH_WALL_QUALIFICATION/wall.py']
 for n in paths:need(inputs.get(str(BASE/n))==sha(BASE/n),'IMPORT_AUTH:'+n)
 interval,cubic,quartic,wall=[load('ninth_actual_'+str(i),BASE/n) for i,n in enumerate(paths)];flow=load('ninth_actual_flow',ROOT/'flow.py');qualified=auth('20261027_NINTH_BULK_QUALIFICATION_R2/RESULT.json');flow.setup(interval.I,cubic,quartic,wall,qualified,auth('20261027_NINTH_JET_QUALIFICATION/RESULT.json'))
 globaldata=auth('20261027_QUINTIC_GLOBAL_BULK_PROBE/RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');inverse=auth('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json');need(inverse['scientific_certificate'],'INVERSE_CERTIFIED')
 seventh=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');eighth=auth('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE/RESULT.json')
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py';need(inputs.get(str(ringpath))==sha(ringpath),'RING_AUTH');ring=load('transport_ring',ringpath)
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime));put('TRANSPORT_QUALIFICATION.json',flow.qualify_transport(ring,wall.S));arms={}
 for engine in ('primary','independent'):
  arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json')
  need(arm['D']==initial['D'],'DOMAIN_IDENTITY')
  for k,v in initial['parameters'].items():need(arm['parameters'][k]==v,'PARAMETER:'+k)
  out=flow.calculate(arm,eighth['arms'][engine],seventh['arms'][engine],sixth['arms'][engine],globaldata['arms'][engine],inverse['arms'][engine]);put('ARM_'+engine+'.json',out);arms[engine]=out
  print(json.dumps(dict(engine=engine,seconds=time.monotonic()-started,d9=[float(Q(x)) for x in out['bulk']['d9']['exact_bounds']])),flush=True)
 lo=[Q(v['bulk']['d9']['exact_bounds'][0]) for v in arms.values()];hi=[Q(v['bulk']['d9']['exact_bounds'][1]) for v in arms.values()];need(max(lo)<=min(hi),'COMPATIBILITY_NOT_ACCURACY')
 result=dict(pass_status=True,arms=arms,d9=dict(exact_bounds=[str(min(lo)),str(max(hi))]),seconds=time.monotonic()-started,scope='Unsigned actual ninth-distance coefficient enclosure; no ninth field profile, sign, trajectory or full clock certificate.')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'run.py'),flow_sha256=sha(ROOT/'flow.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt'),transport_sha256=sha(ROOT/'TRANSPORT_QUALIFICATION.json'),pins_sha256=sha(ROOT/'PINS.json')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_actual_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NINTH_ACTUAL_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
