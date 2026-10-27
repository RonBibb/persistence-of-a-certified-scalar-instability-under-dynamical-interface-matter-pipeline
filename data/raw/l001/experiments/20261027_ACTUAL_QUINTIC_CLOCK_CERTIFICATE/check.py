"""Isolated substitution of audited actual d5 into unchanged ninth clock certificate."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
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
def iv(x):return tuple(map(Q,x['exact_bounds']))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def neg(a):return -a[1],-a[0]
def mul(a,b):
 z=[x*y for x in a for y in b];return min(z),max(z)
def sc(a,k):return mul(a,(Q(k),Q(k)))
def pack(a):return list(map(str,a))
def absbound(a):return max(map(abs,a))
def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','AUTHORITY.txt','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def closure(p):
  for g in ('inputs','sources','runtime'):
   for path,h in read(p)[g].items():bind(path,h)
 parent=BASE/'20261027_NINTH_CLOCK_ENCLOSURE'
 bind(parent/'TERMINAL.json','656717ab05667a55001a3f687a0a684dd3701d76d5f9b676ee8c5ce4f2e922b1')
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 closure(parent/'BINDING.json')
 actual=BASE/'20261027_QUINTIC_REAL_SOURCE_ENCLOSURE'
 bind(actual/'production_TERMINAL.json','4493283c8bca0cb37368edc1bde313509516025919c62862e84e55ad02ce7c8e')
 t=read(actual/'production_TERMINAL.json');need(t['pass_status'],'ACTUAL_PASS')
 for n,k in [('production_RESULT.json','result_sha256'),('production_BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('AUTHORITY.txt','authority_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(actual/n,t[k])
 closure(actual/'production_BINDING.json')
 audit=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'
 bind(audit/'QUINTIC_REAL_PRODUCTION_AUDIT.json','eb509f1f6ad89cfcf62d0e1d1a84befdc93b1d5d7b146f44a3c55e7c8a7c3f73')
 bind(audit/'20261027_NINTH_CLOCK_ENCLOSURE_AUDIT.json','3d210241319e630cae08650bb6d2419bcec7b40b35de8eb5694836241167937d')
 for n in ('lease.py','DESIGN.txt'):
  path=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(path)]=sha(path)
 def auth(n):
  path=BASE/n;need(inputs.get(str(path))==sha(path),'AUTH:'+n);return read(path)
 prior=read(parent/'RESULT.json');fifth=read(actual/'production_RESULT.json')
 sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json')
 seventh=auth('20261027_SEVENTH_CLOCK_ENCLOSURE/RESULT.json');eighth=auth('20261027_EIGHTH_CLOCK_ENCLOSURE/RESULT.json')
 fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 len(str(10**20000));runtime=lease.observed()
 for path,h in runtime.items():need(inputs.get(path)==h or sources.get(path)==h,'RUNTIME:'+path)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 records={}
 old_d5=Q(sixth['finite_distance'][5]);old_f5max=Q(sixth['quintic_abs'])
 for engine in ('primary','independent'):
  old=sixth['finite_coefficients'][engine];vals=clock['arms'][engine]['values']
  one,two,three,rate=[iv(vals[k]) for k in ('d1','d2','d3','rate')]
  l2,l3,l4=[tuple(map(Q,old[k])) for k in ('L2','L3','L4')];four=tuple(map(Q,old['d4']))
  inv2=add((Q(1,2),Q(1,2)),neg(l2));inv3=add(add(neg(l3),l2),(-Q(1,6),-Q(1,6)))
  inv4=add(add(add(neg(l4),l3),add(sc(mul(l2,l2),Q(1,2)),sc(l2,-Q(1,2)))),(Q(1,24),Q(1,24)))
  def f5(d5):
   return mul(rate,add(add(sc(d5,4),sc(four,-4)),add(add(sc(mul(three,inv2),3),sc(mul(two,inv3),2)),mul(one,inv4))))
  baseline=f5((-old_d5,old_d5));need(pack(baseline)==old['F5'] and absbound(baseline)==Q(old['F5_abs']),'EXACT_F5_BASELINE:'+engine)
  newd=iv(fifth['arms'][engine]['bulk']['d5']);candidate=f5(newd)
  records[engine]=dict(d5=pack(newd),d4_unchanged=pack(four),L4_unchanged=pack(l4),inverse2=pack(inv2),inverse3=pack(inv3),inverse4=pack(inv4),baseline_F5=pack(baseline),candidate_F5=pack(candidate),candidate_abs=str(absbound(candidate)))
 need(max(absbound(tuple(map(Q,x['baseline_F5']))) for x in records.values())==old_f5max,'EXACT_OLD_F5_MAX')
 candidate=max(Q(x['candidate_abs']) for x in records.values());selected=min(candidate,old_f5max)
 base={k:Q(v) for k,v in prior['constants_exact']['ninth'].items()}
 fixed=dict(cubic=Q(10000),quartic=Q(fourth['selected_quartic_abs']),sixth=Q(sixth['sixth_abs']),seventh=Q(seventh['seventh_abs']),eighth=Q(eighth['eighth_abs']),ninth=Q(prior['ninth_abs']))
 C2=Q(sixth['scalar_abs']['chi2']);C3=Q(sixth['scalar_abs']['chi3'])
 R=base['physical_radius'];MF=base['clock_sup'];MD=base['observable_sup'];Y=base['aggregate_bound']
 def at(j,B5):
  q=Q(1,2**j);eta=R*q/2;qd=q/2
  terms={k:fixed[k]*eta**n for k,n in [('cubic',3),('quartic',4),('sixth',6),('seventh',7),('eighth',8),('ninth',9)]}
  terms['quintic']=B5*eta**5;terms['unknown_tail']=MF*q**10/(1-q)
  dt=MD*qd**2/(1-qd);st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd);se=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  costs={k:v/(10*eta**2) for k,v in terms.items()}
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=se/(eta/40000))
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  result=dict(base,clock_eta=eta,clock_tail=terms['unknown_tail'],distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
  for k,v in terms.items():
   if k!='unknown_tail':result['known_'+k]=v
  return result,costs,ratios,gates
 def certify(B5):
  for j in range(1,8193):
   out,costs,ratios,gates=at(j,B5)
   if all(gates.values()):return out,costs,ratios,gates,j
  raise AssertionError('NO_DYADIC_CERTIFICATE')
 baseline,bc,br,bg,bj=certify(old_f5max)
 need(baseline==base and bj==prior['selected_dyadic'],'EXACT_F9_BASELINE')
 need({k:str(v) for k,v in bc.items()}==prior['clock_costs'] and {k:str(v) for k,v in br.items()}==prior['gate_ratios'],'EXACT_F9_BUDGET')
 refined,costs,ratios,gates,j=certify(selected);need(refined['clock_eta']>=base['clock_eta'],'NO_LOSS_OF_VALID_BOUND')
 larger=None
 if j>1:
  out,cs,rs,gs=at(j-1,selected);need(not all(gs.values()),'FIRST_DYADIC_CERTIFICATE')
  larger=dict(eta=str(out['clock_eta']),costs={k:str(v) for k,v in cs.items()},ratios={k:str(v) for k,v in rs.items()},gates=gs)
 for path,h in dict(inputs,**sources).items():need(sha(path)==h,'POST_BINDING:'+path)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 result=dict(pass_status=True,classification='ACTUAL_D5_ISOLATED_FULL_CLOCK_READOUT',coefficients=records,candidate_quintic_abs=str(candidate),selected_quintic_abs=str(selected),old_quintic_abs=str(old_f5max),constants_exact={'baseline':{k:str(v) for k,v in baseline.items()},'actual_d5':{k:str(v) for k,v in refined.items()}},clock_costs={k:str(v) for k,v in costs.items()},gate_ratios={k:str(v) for k,v in ratios.items()},gates=gates,selected_dyadic=j,gain_exact=str(refined['clock_eta']/base['clock_eta']),next_larger=larger,seconds=time.monotonic()-started,scope='Only d5 substituted in inherited F5 enclosure; d4,L4,all other coefficient bounds,global radius/tail and acceptance gates unchanged. Local sufficient amplitude, not finite nonlinear trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),authority_sha256=sha(ROOT/'AUTHORITY.txt'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'],eta=float(refined['clock_eta']),gain=float(refined['clock_eta']/base['clock_eta']),ratios={k:float(v) for k,v in ratios.items()},costs={k:float(v) for k,v in costs.items()},next_larger_gates=larger['gates'] if larger else None)),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  path=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(path)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('actual_fifth_clock_lease',path);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('READOUT_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()

