"""Saved interval-term attribution, not a coefficient or physical test."""
import sys,os,json,time,signal,hashlib,importlib.util,traceback
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
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
 os.chmod(t,0o444);os.link(t,p);t.unlink()
def main(lease):
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'HASH:'+str(p));inputs[str(p)]=h
 def packet(n,h):
  p=BASE/n;bind(p/'TERMINAL.json',h);t=read(p/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
  for fn,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(p/fn,t[k])
  for g in ('inputs','sources','runtime'):
   for f,v in read(p/'BINDING.json')[g].items():bind(f,v)
 packet('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE','7a52079f0b25cb3866af673880a12083aeb7aa98cb0be378fed13d47e8d43b80')
 packet('20261027_POSITIVE_TAIL_HALF_RADIUS_READOUT','c43f66888ac5708ad65230b1d02edcb4b42984a68c1c0ce50b4e39c047d98be1')
 for n,h in [('ACTUAL_SEVENTH_CLOCK_AUDIT.json','2ea421a29c59c6e4371857531b5e9675b51e9116b6e9863add64c1a7849b8337'),('POSITIVE_TAIL_HALF_READOUT_AUDIT.json','c331ba14b4d11354681a11aa7ca0cd0de7ffaed3a033203b63b53dcd90770851')]:
  p=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(p,h);need(read(p)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 p=BASE/'20261027_SEVENTH_COEFFICIENT_CAMPAIGN/AUTHORITY.txt';sources[str(p)]=sha(p)
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME')
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 data=read(BASE/'20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');R=Q(data['arms']['both']['constants']['physical_radius']);a=R/2;rows={}
 for n in (8,9):
  rows[str(n)]={}
  for engine in ('primary','independent'):
   rec=data['coefficient_records'][str(n)][engine];parts={k:tuple(map(Q,v)) for k,v in rec['new_terms'].items()};need(set(parts)=={'leading'}|{str(j) for j in range(1,n)},'TERM_COVERAGE');need(all(lo<=hi for lo,hi in parts.values()),'INTERVAL_ORDER')
   bounds={k:max(abs(lo),abs(hi)) for k,(lo,hi) in parts.items()};leading=bounds['leading'];lower=sum(v for k,v in bounds.items() if k!='leading');total=leading+lower;need(total>0,'POSITIVE_TOTAL')
   factor=a**n/(10*a*a)
   summed=(sum(v[0] for v in parts.values()),sum(v[1] for v in parts.values()));saved=tuple(map(Q,rec['new']));need(summed[0]<=saved[0]<=saved[1]<=summed[1],'DISTRIBUTED_INTERVAL_CONTAINS_GROUPED');need(max(map(abs,saved))==Q(rec['new_abs']),'STORED_ABSOLUTE')
   row=dict(component_absolute_bounds={k:str(v) for k,v in bounds.items()},leading_bound=str(leading),lower_product_bound=str(lower),triangle_bound=str(total),leading_share_of_triangle=str(leading/total),normalized_leading=str(leading*factor),normalized_lower_products=str(lower*factor),normalized_triangle=str(total*factor),stored_coefficient_bound=rec['new_abs'],adopted_bound=data['new_clock_bounds'][str(n)])
   row.update(distributed_interval=list(map(str,summed)),stored_interval=list(map(str,saved)),intervals_exactly_equal=summed==saved,distributed_contains_stored=True)
   rows[str(n)][engine]=row
   print(json.dumps(dict(order=n,engine=engine,leading_share=float(leading/total),normalized_leading=float(leading*factor),normalized_lower_products=float(lower*factor))),flush=True)
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_HASH')
 need(lease.observed()==runtime and time.time()<CUTOFF,'RUNTIME_WINDOW')
 result=dict(pass_status=True,eta=str(a),rows=rows,seconds=time.monotonic()-start,scope='Attribution of archived interval triangle bounds only. Not physical coefficient shares, cancellations, a hypothetical recomputed certificate, new field enclosure or amplitude admission.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('attribution_lease',p);lease.ROOT=ROOT;lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ATTRIBUTION_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
