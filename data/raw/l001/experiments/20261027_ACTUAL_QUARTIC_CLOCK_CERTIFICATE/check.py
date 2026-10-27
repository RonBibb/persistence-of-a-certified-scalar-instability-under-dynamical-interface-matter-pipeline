"""Same-family quartic proper-clock coefficient enclosure and full remainder test."""
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
def iv(v):return tuple(map(Q,v['exact_bounds']))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[1],-a[0]
def mul(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def sc(a,k):return mul(a,(Q(k),Q(k)))
def packed(a):return list(map(str,a))

def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 current=BASE/'20261027_SIXTH_CLOCK_ENCLOSURE'
 need(sha(current/'TERMINAL.json')=='d27583c253cb25cc9aad8fba81c391e7590caf93879ded528714d27abbf2eb30','SIXTH_TERMINAL')
 t=read(current/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 inputs[str(current/'TERMINAL.json')]=sha(current/'TERMINAL.json')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
  need(sha(current/n)==t[k],'SIXTH_ARTIFACT');inputs[str(current/n)]=t[k]
 for group in ('inputs','sources','runtime'):
  for p,h in read(current/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_BINDING');inputs[p]=h
 real=BASE/'20261027_QUARTIC_REAL_SOURCE_ENCLOSURE'
 need(sha(real/'production_TERMINAL.json')=='429d3c08cc3c95dc724c269bfcac60a8195e0d986445f4534fa707c1b30d796b','QUARTIC_TERMINAL')
 qt=read(real/'production_TERMINAL.json');need(qt['pass_status'],'QUARTIC_PASS')
 inputs[str(real/'production_TERMINAL.json')]=sha(real/'production_TERMINAL.json')
 for n,h in qt['artifacts'].items():need(sha(real/n)==h,'QUARTIC_ARTIFACT:'+n);inputs[str(real/n)]=h
 for group in ('inputs','sources','runtime'):
  for p,h in read(real/'production_BINDING.json')[group].items():need(sha(p)==h,'QUARTIC_BINDING');inputs[p]=h
 prior=read(current/'RESULT.json');base={k:Q(v) for k,v in prior['constants_exact']['sixth'].items()}
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=CUTOFF))
 gates={}
 def gate(v,n):need(v,n);gates[n]=True
 clock=read(BASE/'20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 coeff={};candidate=[]
 for name in ('primary','independent'):
  arm=read(real/('ARM_'+name+'.json'));d4=iv(arm['d4']);vals=clock['arms'][name]['values']
  d1,d2,d3,rate=[iv(vals[k]) for k in ('d1','d2','d3','rate')]
  inherited=prior['sixth_coefficients'][name];L2=tuple(map(Q,inherited['L2']));L3=tuple(map(Q,inherited['L3']))
  F4=mul(rate,add(add(sc(d4,3),sc(d3,-3)),add(mul(add((Q(1),Q(1)),sc(L2,-2)),d2),mul(add(add(neg(L3),L2),(-Q(1,6),-Q(1,6))),d1))))
  coeff[name]=dict(d4=packed(d4),F4=packed(F4),F4_abs=str(max(map(abs,F4))))
  candidate.append(max(map(abs,F4)))
 gate(max(Q(v['d4'][0]) for v in coeff.values())<=min(Q(v['d4'][1]) for v in coeff.values()),'TWO_ENGINE_D4_OVERLAP')
 oldB4=Q(prior['quartic_abs']);newB4=max(candidate);B5=Q(prior['quintic_abs']);B6=Q(prior['sixth_abs']);C2=Q(prior['scalar_abs']['chi2']);C3=Q(prior['scalar_abs']['chi3'])
 R=base['physical_radius'];MF=base['clock_sup'];MD=base['observable_sup'];Y=base['aggregate_bound']
 def certify(B4,label):
  selected=None
  for j in range(1,8193):
   q=Q(1,2**j);eta=R*q/2;qd=q/2
   tail=MF*q**7/(1-q);k3=10000*eta**3;k4=B4*eta**4;k5=B5*eta**5;k6=B6*eta**6
   dt=MD*qd**2/(1-qd);st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd);se=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
   if k3+k4+k5+k6+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:selected=j;break
  gate(selected is not None,label+':ALL_REMAINDER_GATES');gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,label+':OPENING_SIGN')
  c=dict(base,clock_eta=eta,clock_tail=tail,known_cubic=k3,known_quartic=k4,known_quintic=k5,known_sixth=k6,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
  costs={k:v/(10*eta**2) for k,v in dict(cubic=k3,quartic=k4,quintic=k5,sixth=k6,unknown7=tail).items()}
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=se/(eta/40000))
  return c,costs,ratios,selected
 baseline,oldcost,oldratio,oldj=certify(oldB4,'BASELINE')
 gate(baseline==base and oldj==prior['selected_dyadics']['sixth'],'EXACT_PARENT_FULL_CERTIFICATE')
 chosen=min(oldB4,newB4);refined,costs,ratios,j=certify(chosen,'ACTUAL_QUARTIC')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
 gate(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 out=dict(pass_status=True,classification='ACTUAL_QUARTIC_FULL_CLOCK_CERTIFICATE',coefficient_intervals=coeff,old_quartic_abs=str(oldB4),actual_quartic_abs=str(newB4),selected_quartic_abs=str(chosen),constants_exact={label:{k:str(v) for k,v in c.items()} for label,c in [('baseline',baseline),('actual_quartic',refined)]},gain_exact=str(refined['clock_eta']/baseline['clock_eta']),clock_costs={k:str(v) for k,v in costs.items()},gate_ratios={k:str(v) for k,v in ratios.items()},selected_dyadic=j,gates=gates,seconds=time.monotonic()-started,scope='Sufficient local proper-clock certificate using actual source-informed unsigned d4 enclosure. No sign-resolved quartic profile or finite trajectory.')
 put('RESULT.json',out);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=out['seconds'],clock_eta=float(refined['clock_eta']),gain=float(refined['clock_eta']/baseline['clock_eta']),F4_bound=float(chosen),clock_costs={k:float(v) for k,v in costs.items()},gate_ratios={k:float(v) for k,v in ratios.items()})),flush=True)

if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF,'LINUX_LAUNCH_CUTOFF')
  need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('quartic_clock_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
  need(time.time()<CUTOFF,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('QUARTIC_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()

