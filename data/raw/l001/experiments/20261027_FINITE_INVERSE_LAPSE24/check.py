"""Positive finite lower-wall inverse-clock coefficients; no readout."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793101111;N=24
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
 start=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')};gates={}
 def gate(v,n):need(v,n);gates[n]=True
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def packet(n,pin):
  root=BASE/n;bind(root/'TERMINAL.json',pin);t=read(root/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS:'+n)
  for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(root/fn,t[key])
  for group in ('inputs','sources','runtime'):
   for p,h in read(root/'BINDING.json')[group].items():bind(p,h)
 packet('20261027_DEGREE24_DISTANCE_MAJORANT','313f7292e1ba87e35d264c14f9af74c46719596ca0c77e7e7100f6ca84de7c4b')
 packet('20261027_DISTANCE16_LAPSE_DEPARTURE','d281d26a7a44ea246ea419df675603033c9314aa44660e4444c4006c42ea691b')
 for n,pin in [('DEGREE24_AUDIT.json','13f7bda89664924f9b82e01711ee3976708c5208e05dbef4ea1f1c9b777e8ff0'),('DISTANCE16_LAPSE_AUDIT.json','db81ec05112d81dee4723b38d4f4905ec07a22e8475ef999eb96f2e6cdad5d19')]:
  p=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/n;bind(p,pin);gate(read(p)['PASS'],'AUDIT:'+n)
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 high=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');raw=auth('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json')
 module=BASE/'20261027_DEGREE24_DISTANCE_MAJORANT/check.py';need(inputs.get(str(module))==sha(module),'MODULE_AUTH');M=load('inverse24_series',module);S=M.Series
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 base={k:Q(v) for k,v in dp['arms']['both']['constants'].items()};R=base['physical_radius'];JC=Q(dp['global_departure']['coefficient_tail_sup']);gap=Q(raw['constants_exact']['gap']);lam=Q(fixed['selected']['refined']['graph_weight']);z=list(map(Q,high['majorant']))
 gate(high['degree']==N and len(z)==N+1 and all(v>=0 for v in z),'POSITIVE_MAJORANT');gate(R>0 and gap>0 and lam>0 and JC>=0,'PARAMETERS')
 for engine in ('primary','independent'):
  initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');gate(initial['initial_background'][0]['exact_bounds']==['0','0'] and initial['initial_background'][4]['exact_bounds']==['1','1'],'LOWER_NORMALIZATION:'+engine)
  clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');rate=list(map(Q,clock['arms'][engine]['values']['rate']['exact_bounds']));gate(0<rate[0]<=rate[1]<=Q(1,32),'RATE_CEILING:'+engine);gate(list(map(Q,dp['inverse_intervals'][engine][1]))==[Q(-1),Q(-1)],'EXACT_INVERSE_LINEAR:'+engine)
 B=S([0]+[z[n]/n**2 for n in range(1,N+1)]);X=S([0,0]+[lam*z[n]/n**3 for n in range(2,N+1)]);U=4*X/gap;Ehat=1+64*U/(1-U)
 def exp(v):
  gate(v.v[0]==0,'EXP_ZERO:'+str(len(gates)));out=[Q(1)]
  for n in range(1,N+1):out.append(sum(k*v.v[k]*out[n-k] for k in range(1,n+1))/n)
  return S(out)
 EulerX=S([n*v for n,v in enumerate(X.v)]);V=Ehat*exp(2*B)*EulerX/32;Jhat=Ehat*exp(B)/(1-V*V)
 gate((exp(B)*exp(-B)).v==S(1).v,'EXP_INVERSE_CONTROL');gate((Jhat*(1-V*V)).v==(Ehat*exp(B)).v,'GEOMETRIC_INVERSE_CONTROL')
 gate(X.v[0]==X.v[1]==V.v[0]==V.v[1]==0,'QUADRATIC_SHIFT_VELOCITY');gate(Ehat.v[0]==Jhat.v[0]==1,'CONSTANT_ONE')
 for label,poly in [('B',B),('X',X),('Ehat',Ehat),('Vhat',V),('Jhat',Jhat)]:gate(all(v>=0 for v in poly.v),'POSITIVE:'+label)
 old={int(n):Q(v) for n,v in dp['inverse_abs'].items()};new=dict(old)
 for n in range(9,N+1):new[n]=min(Jhat.v[n],JC/R**n);gate(0<=new[n]<=JC/R**n,'CAUCHY_FALLBACK:'+str(n))
 gate({n:new[n] for n in range(1,9)}==old,'RETAINED_ACTUAL_PREFIX')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,degree=N,series={k:list(map(str,v.v)) for k,v in [('B',B),('X',X),('Ehat',Ehat),('Vhat',V),('Jhat',Jhat)]},inverse_abs={str(n):str(v) for n,v in new.items()},retained_inverse={str(n):str(v) for n,v in old.items()},constants=dict(radius=str(R),tail_sup=str(JC),gap=str(gap),graph_weight=str(lam),rate_ceiling='1/32'),gates=gates,seconds=time.monotonic()-start,scope='Unsigned finite lower-clock coefficients9..24 only; actual1..8 preserved, global radius unchanged, no amplitude certificate.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')));print(json.dumps(dict(PASS=True,seconds=result['seconds'],gates=len(gates))),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('inverse24_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire();need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('INVERSE24_600_SECONDS')));signal.alarm(600);put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
