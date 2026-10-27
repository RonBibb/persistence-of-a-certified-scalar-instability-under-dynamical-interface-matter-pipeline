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
def conv(a,b,N):return [sum((a[j]*b[i-j] for j in range(i+1)),Q(0)) for i in range(N+1)]
def power(a,m,N):
 v=[Q(1)]+[Q(0)]*N
 for _ in range(m):v=conv(v,a,N)
 return v
def main(lease):
 started=time.monotonic();inputs={};gates={}
 sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def gate(v,n):need(v,n);gates[n]=True
 parent=BASE/'20261027_QUARTIC_CLOCK_ENCLOSURE'
 bind(parent/'TERMINAL.json','4cc42f0c8228af1f93196c303d262fd4931b26df944bc56b623be9eafa30f257')
 t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 def authenticated(path):
  p=BASE/path;gate(inputs.get(str(p))==sha(p),'AUTHENTICATED:'+path);return read(p)
 parent_result=read(parent/'RESULT.json');old=authenticated('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');prior=old['constants_exact']['refined']
 c={k:Q(v) for k,v in authenticated('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
 c['C0']=Q(prior['C0']);c['total']=Q(prior['Cscalar'])
 cfg=dict(authenticated('20261027_SPLIT_NORM_GRID/CONTRACT.json'),bulk_seed_bound=Q(prior['seed']))
 prior_module=load('quartic_parent_certificate',BASE/'20261027_FINAL_FIXED_GRID_CERTIFICATE/check.py')
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
 gate(inputs.get(str(ringpath))==sha(ringpath),'POLYNOMIAL_RING_AUTHORITY')
 ring=load('quartic_symbolic_ring',ringpath);ring.NAMES=('d1','d2','d3','d4','L2','L3','r');ring.N=7;ring.ZERO=(0,)*7
 auth=BASE/'20261027T043011Z_TWO_HOUR_CLOCK_CONTINUATION/AUTHORITY.txt';bind(auth,sha(auth))
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=CUTOFF))
 baseline=prior_module.certify(old['selected']['refined'],'baseline',c,cfg,gate)
 gate({k:str(v) for k,v in baseline.items()}==prior,'FULL_BASELINE_REPLAY')
 d1,d2,d3,d4,L2,L3,r=[ring.variable(j) for j in range(7)]
 ell=[ring.P(0),ring.P(-1),-L2,-L3];inverse=[ring.P(1)]
 for n in range(1,4):inverse.append(sum((k*ell[k]*inverse[n-k] for k in range(1,n+1)),ring.P(0))/n)
 D=[ring.P(0),d1,d2,d3,d4]
 F=[r*(sum((j*D[j]*inverse[n-j] for j in range(1,n+1)),ring.P(0))-D[n]) for n in range(1,5)]
 expected=[ring.P(0),r*(d2-d1),r*(2*d3-2*d2+(Q(1,2)-L2)*d1),r*(3*d4-3*d3+(1-2*L2)*d2+(-L3+L2-Q(1,6))*d1)]
 for n,(a,b) in enumerate(zip(F,expected),1):gate((a-b).iszero(),'SYMBOLIC_CLOCK_DEGREE:'+str(n))
 gate(not (F[3]-r*(3*d4-3*d3+(1-2*L2)*d2+(-L3+L2)*d1)).iszero(),'MUTATION_OMITTED_ONE_SIXTH')
 # Genuine coefficient recurrence, not a Cauchy coefficient bound.
 K=baseline['K'];seed=baseline['seed'];row=old['selected']['refined']
 A=1+Q(row['graph_weight'])+Q(row['oscillator_weight']);N=4
 w=[Q(0)]*(N+1);w[1]=seed
 for n in range(2,N+1):
  w[n]=sum((m-1)*K**(m-1)*power(w,m,N)[n] for m in range(2,n+1))
 gate(w==[0,seed,K*seed**2,4*K**2*seed**3,18*K**3*seed**4],'RECURRENCE_CLOSED_FORM')
 U=[A*4**n*w[n] for n in range(N+1)]
 distance=[9*sum(power(U,m,N)[n] for m in range(1,N+1)) for n in range(N+1)]
 bound_d4=distance[4]
 formula=2304*seed**4*(18*A*K**3+9*A*A*K*K+3*A**3*K+A**4)
 gate(bound_d4==formula and bound_d4>0,'DISTANCE_QUARTIC_ENCLOSURE')
 gate(list(map(str,w))==parent_result['majorant_coefficients'] and list(map(str,distance))==parent_result['distance_coefficients'],'PARENT_MAJORANT_REPLAY')
 old_d4=bound_d4
 lam=Q(row['graph_weight'])
 bhat=[Q(0)]+[4**n*w[n]/n**2 for n in range(1,N+1)]
 xhat=[Q(0)]+[2*lam*4**n*w[n]/n**3 for n in range(1,N+1)];xhat[1]=Q(0)
 exponential=[Q(1)]
 for n in range(1,N+1):exponential.append(sum(k*bhat[k]*exponential[n-k] for k in range(1,n+1))/n)
 component_distance=[Q(0)]+[3*(exponential[n]+sum(exponential[j]*xhat[n-j] for j in range(n+1))) for n in range(1,N+1)]
 bound_d4=component_distance[4]
 gate(0<bound_d4<=old_d4,'COMPONENT_QUARTIC_DOMINATION')
 clock=authenticated('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 cubic=authenticated('20261026_NEUTRAL_CUBIC_CLOCK_TAIL/RESULT.json')
 coefficients={}
 for engine in ('primary','independent'):
  vals=clock['arms'][engine]['values']
  one,two,three,rate=[iv(vals[k]) for k in ('d1','d2','d3','rate')]
  quad=authenticated('20261026_GROWING_MODE_QUADRATIC_R1/PRODUCTION_'+engine+'.json')
  z=list(map(iv,quad['walls']['lower']['state']));wall=quad['walls']['lower']
  xi2=iv(wall['loads']['xi2']) if 'loads' in wall else iv(wall['xi2'])
  l2=add(z[8],mul(z[1],xi2))
  gate(l2==iv(vals['lower_log_lapse2']),'L2_REPLAY:'+engine)
  affine=authenticated('20261026_GROWING_MODE_CUBIC_AFFINE/PRODUCTION_'+engine+'.json')
  data={k:iv(v) for k,v in affine['walls']['lower']['data'].items()}
  l3=add(add(data['p3'],mul(data['H'],data['xi3'])),mul(data['u1'],data['xi2']))
  f2=mul(rate,add(two,neg(one)))
  f3=mul(rate,add(add(sc(three,2),sc(two,-2)),mul(add((Q(1,2),Q(1,2)),neg(l2)),one)))
  gate(packed(f2)==cubic['coefficient_intervals'][engine]['F2'],'F2_REPLAY:'+engine)
  gate(packed(f3)==cubic['coefficient_intervals'][engine]['F3'],'F3_REPLAY:'+engine)
  gate(-50<f2[0]<=f2[1]<-21 and -10000<f3[0]<=f3[1]<10000,'LOWER_COEFFICIENT_GATES:'+engine)
  f4=mul(rate,add(add(sc((-bound_d4,bound_d4),3),sc(three,-3)),add(mul(add((Q(1),Q(1)),sc(l2,-2)),two),mul(add(add(neg(l3),l2),(-Q(1,6),-Q(1,6))),one))))
  old_f4=mul(rate,add(add(sc((-old_d4,old_d4),3),sc(three,-3)),add(mul(add((Q(1),Q(1)),sc(l2,-2)),two),mul(add(add(neg(l3),l2),(-Q(1,6),-Q(1,6))),one))))
  gate(packed(old_f4)==parent_result['coefficient_intervals'][engine]['F4'],'PARENT_F4_REPLAY:'+engine)
  coefficients[engine]=dict(L2=packed(l2),L3=packed(l3),d4=packed((-bound_d4,bound_d4)),F2=packed(f2),F3=packed(f3),F4=packed(f4),F4_abs=str(max(map(abs,f4))))
 gate(max(Q(coefficients[e]['L3'][0]) for e in coefficients)<=min(Q(coefficients[e]['L3'][1]) for e in coefficients),'L3_ENGINE_OVERLAP')
 B4=max(Q(v['F4_abs']) for v in coefficients.values())
 radius=baseline['physical_radius'];MD=baseline['observable_sup'];MF=baseline['clock_sup'];Y=baseline['aggregate_bound']
 def select_quartic(b4):
  found=False
  for j in range(1,8193):
   q=Q(1,2**j);eta=radius*q/2;tail=MF*q**5/(1-q);known3=10000*eta**3;known4=b4*eta**4;qd=q/2
   dt=MD*qd**2/(1-qd);st=Y*qd**2/(1-qd);se=Y*qd**2*(2-qd)/(1-qd)**2
   if known3+known4+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:found=True;break
  gate(found,'FULL_REMAINDER_SELECTION:'+str(b4))
  gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_SIGN:'+str(b4))
  return dict(baseline,clock_eta=eta,clock_tail=tail,known_cubic=known3,known_quartic=known4,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000),j
 parent_bound=Q(parent_result['quartic_abs'])
 parent_replay,_=select_quartic(parent_bound)
 gate({k:str(v) for k,v in parent_replay.items()}==parent_result['constants_exact']['quartic'],'FULL_QUARTIC_PARENT_REPLAY')
 new,j=select_quartic(B4)
 eta=new['clock_eta'];tail=new['clock_tail'];known3=new['known_cubic'];known4=new['known_quartic'];dt=new['distance_tail'];st=new['scalar_tail'];se=new['scalar_derivative_tail']
 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
 gate(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 out=dict(pass_status=True,classification='COMPONENT_QUARTIC_CLOCK_ENCLOSURE',coefficient_intervals=coefficients,majorant_coefficients=list(map(str,w)),aggregate_coefficients=list(map(str,U)),distance_coefficients=list(map(str,component_distance)),aggregate_distance_coefficients=list(map(str,distance)),bulk_coefficients=list(map(str,bhat)),graph_slope_coefficients=list(map(str,xhat)),quartic_abs=str(B4),constants_exact={'baseline':{k:str(v) for k,v in parent_replay.items()},'quartic':{k:str(v) for k,v in new.items()}},gain_exact=str(eta/parent_replay['clock_eta']),selected_dyadic=j,symbolic_F4=F[3].pack(),gates=gates,seconds=time.monotonic()-started,ode_solves=0,scope='Symmetric quartic enclosure, not resolved sign or finite physical evolution.')
 put('RESULT.json',out);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=out['seconds'],gates=len(gates),d4_bound=float(bound_d4),F4_abs=float(B4),clock_eta=float(eta),baseline_eta=float(parent_replay['clock_eta']),gain=float(eta/parent_replay['clock_eta']),L3={k:[float(Q(x)) for x in v['L3']] for k,v in coefficients.items()},gate_ratios=dict(clock=float((known3+known4+tail)/(10*eta**2)),distance=float(dt/(25*eta)),scalar=float(st/(eta/40000)),scalar_derivative=float(se/(eta/40000))))),flush=True)
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
