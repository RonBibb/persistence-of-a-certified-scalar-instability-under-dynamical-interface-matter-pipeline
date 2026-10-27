"""Fixed two-point positive tail feasibility; no new physical solution."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
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
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','tail.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_ACTUAL_EIGHTH_FULL_BUDGET';bind(parent/'TERMINAL.json','9ff596a88beb1b1947f81e8deb73d630a6033a4b577728b3c958305baab23532');t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/fn,t[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/ACTUAL_EIGHTH_FULL_BUDGET_AUDIT.json';bind(ap,'84bd2bface15205ec12306299c3e2c298b42d67dab1bb5a36696d7318e915450');need(read(ap)['PASS'] and read(ap)['producer_terminal']==sha(parent/'TERMINAL.json'),'EIGHTH_FULL_AUDIT')
 for n,h in [('ACTUAL_SEVENTH_CLOCK_AUDIT.json','2ea421a29c59c6e4371857531b5e9675b51e9116b6e9863add64c1a7849b8337'),('DEGREE24_AUDIT.json','13f7bda89664924f9b82e01711ee3976708c5208e05dbef4ea1f1c9b777e8ff0')]:
  p=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(p,h);need(read(p)['PASS'],'AUDIT_PASS')
 priorfull=BASE/'20261027_POSITIVE_TAIL_FULL_READOUT';bind(priorfull/'TERMINAL.json','8b4f152a0e9bd3feb292d1a7834126dac87c8d585692dd37f99242f2c42fb5ac')
 ft=read(priorfull/'TERMINAL.json');need(ft['pass_status'],'FULL_PASS')
 for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(priorfull/fn,ft[key])
 for group in ('inputs','sources','runtime'):
  for p,h in read(priorfull/'BINDING.json')[group].items():bind(p,h)
 need(all(read(priorfull/'RESULT.json')['points']['1/8']['gates'].values()),'PRIOR_DOUBLING_ADMITTED')
 pa=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/POSITIVE_TAIL_FULL_AUDIT.json';bind(pa,'40c7798f1dd6f085fcaeb861b9dbf7dfe6d91a23b42ad89e8329622269ebc5c1');need(read(pa)['PASS'] and read(pa)['producer_terminal']==sha(priorfull/'TERMINAL.json'),'PREVIOUS_FULL_AUDIT')
 authority=BASE/'20261027_NINTH_COEFFICIENT_CAMPAIGN/AUTHORITY.txt';sources[str(authority)]=sha(authority)
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json')
 need(raw['pass_status'] and raw['degree']==24,'DEGREE24_PASS')
 bc=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json')['arms']['both']['constants'];nc=ninth['constants_exact']['ninth'];need(all(bc[k]==nc[k] for k in ('seed','K','physical_radius','aggregate_bound')),'SAME_MAJORANT_DOMAIN')
 constants=dict(R=bc['physical_radius'],seed=bc['seed'],K=bc['K'],Y=bc['aggregate_bound'],JC=dp['global_departure']['coefficient_tail_sup']);weights=[fixed['selected']['refined'][k] for k in ('graph_weight','oscillator_weight')]
 ip=BASE/'20261027_QUINTIC_GLOBAL_BULK_PROBE/interval.py';need(inputs.get(str(ip))==sha(ip),'INTERVAL_AUTH');interval=load('positive_tail_interval',ip);module=load('positive_tail',ROOT/'tail.py');module.setup(interval.I)
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime));rows={}
 for q in (Q(1,2),Q(3,4)):
  row=module.calculate(q,constants,raw,weights)
  if q==Q(1,2):need(row==auth('20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY/RESULT.json')['points']['1/2'],'EXACT_HALF_REPLAY')
  rows[str(q)]=row;put('POINT_'+str(q.denominator)+'.json',row)
  print(json.dumps(dict(q=str(q),bounds={k:float(Q(v)) for k,v in row['bounds'].items()},delta_upper=float(Q(row['values']['delta']['exact_bounds'][1])))),flush=True)
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime and time.time()<CUTOFF,'RUNTIME_AND_WINDOW')
 result=dict(pass_status=True,constants=constants,weights=weights,points=rows,seconds=time.monotonic()-start,scope='Half-radius replay and fresh three-quarter-radius residual tail certificates within unchanged analytic radius. No new actual coefficient, full-clock certificate or physical trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),tail_sha256=sha(ROOT/'tail.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'])),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('positive_tail_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('POSITIVE_TAIL_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
