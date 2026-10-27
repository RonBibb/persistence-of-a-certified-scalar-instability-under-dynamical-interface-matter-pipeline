"""Finite-contour and retained-distance factorial certificate, no ODE."""
import sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent;CUTOFF=1793101111
CONTOURS=tuple(map(Q,('1/2','2/3','3/4','4/5','9/10','10/11','15/16')))
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
def strings(d):return {k:str(v) for k,v in d.items()}
def ab(v):return max(abs(Q(x)) for x in v)
def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 parent=BASE/'20261027_ACTUAL_QUINTIC_CLOCK_CERTIFICATE'
 bind(parent/'TERMINAL.json','9dac567ccea7866dafad7d96c1b7433d7f0926d446dfefe27138ba04aefca907')
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('AUTHORITY.txt','authority_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 audit=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/ACTUAL_QUINTIC_CLOCK_AUDIT.json'
 bind(audit,'58c2c048b3eafad68cc044cc5e050162b041d377271ec1443bab8d009b3e81f7');need(read(audit)['PASS'],'AUDIT_PASS')
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def auth(n):
  p=BASE/n;need(inputs.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=read(parent/'RESULT.json');base={k:Q(v) for k,v in prior['constants_exact']['actual_d5'].items()}
 sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json')
 fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');actual5=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 B={2:max(ab(clock['arms'][e]['values']['d2']['exact_bounds']) for e in ('primary','independent')),3:max(ab(clock['arms'][e]['values']['d3']['exact_bounds']) for e in ('primary','independent')),4:max(ab(v['d4']) for v in fourth['coefficient_intervals'].values()),5:max(ab(v['bulk']['d5']['exact_bounds']) for v in actual5['arms'].values())}
 B.update({n:Q(ninth['distance'][n]) for n in range(6,10)});need(all(v>=0 for v in B.values()),'POSITIVE_DISTANCE_BOUNDS')
 R=base['physical_radius'];MD=base['observable_sup'];MF=base['clock_sup'];Y=base['aggregate_bound'];C2=Q(sixth['scalar_abs']['chi2']);C3=Q(sixth['scalar_abs']['chi3'])
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 # Recover each accepted coefficient bound from its exact stored contribution.
 F={n:base['known_'+k]/base['clock_eta']**n for n,k in names.items()}
 need(MD*Q(129,32)==MF,'HALF_CONTOUR_BASELINE')
 def at(j,dist,contour):
  eta=R/Q(2**(j+1));q=2*eta/R;qd=eta/R
  choices=[]
  for theta in CONTOURS if contour else (Q(1,2),):
   z=eta/(theta*R)
   if z<1:
    sup=MD*(1+128*theta/(1-theta))/32
    choices.append((sup*z**10/(1-z),theta,sup))
  tail,theta,sup=min(choices,key=lambda v:v[0])
  terms={names[n]:v*eta**n for n,v in F.items()};costs={k:v/(10*eta**2) for k,v in terms.items()};costs['unknown_tail']=tail/(10*eta**2)
  olddt=MD*qd**2/(1-qd);newdt=sum(v*eta**n for n,v in B.items())+MD*qd**10/(1-qd);dt=min(olddt,newdt) if dist else olddt
  st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd);sd=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  ratios=dict(clock=sum(costs.values()),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=sd/(eta/40000))
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  out=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=sd,scalar_departure=eta/40000)
  out.update({'known_'+k:v for k,v in terms.items()})
  return dict(constants=strings(out),costs=strings(costs),ratios=strings(ratios),gates=gates,theta=str(theta),contour_sup=str(sup),distance_candidates={'old':str(olddt),'retained':str(newdt)})
 arms={}
 for name,dist,contour in [('baseline',False,False),('distance_only',True,False),('contour_only',False,True),('both',True,True)]:
  for j in range(1,8193):
   rec=at(j,dist,contour)
   if all(rec['gates'].values()):break
  else:raise AssertionError('NO_CERTIFICATE:'+name)
  rec.update(selected_dyadic=j,gain_exact=str(Q(rec['constants']['clock_eta'])/base['clock_eta']),next_larger=at(j-1,dist,contour) if j>1 else None);arms[name]=rec
 b=arms['baseline'];need(b['constants']==strings(base) and b['selected_dyadic']==prior['selected_dyadic'],'EXACT_BASELINE')
 need(b['costs']==prior['clock_costs'] and b['ratios']==prior['gate_ratios'] and b['gates']==prior['gates'],'EXACT_BASELINE_GATES_COSTS')
 need(all(Q(v['gain_exact'])>=1 for v in arms.values()),'NO_BOUND_LOSS')
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BIND:'+p)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(time.time()<CUTOFF,'WINDOW')
 result=dict(pass_status=True,classification='CONTOUR_DISTANCE_FACTORIAL',contours=list(map(str,CONTOURS)),distance_bounds={str(n):str(v) for n,v in B.items()},clock_bounds={str(n):str(v) for n,v in F.items()},arms=arms,seconds=time.monotonic()-started,scope='Same local sufficient family certificate; contour and distance estimates only, no evolution or radius extension.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'check.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=result['seconds'],arms={k:dict(eta=float(Q(v['constants']['clock_eta'])),gain=float(Q(v['gain_exact'])),theta=v['theta'],ratios={n:float(Q(x)) for n,x in v['ratios'].items()},next_gates=v['next_larger']['gates'] if v['next_larger'] else None) for k,v in arms.items()})),flush=True)
if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF-600,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  p=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(p)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('contour_lease',p);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
  need(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CAP_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
