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

class Series:
 N=5
 def __init__(self,a=0):
  self.v=tuple(map(Q,(list(a)+[Q(0)]*6)[:6])) if isinstance(a,(list,tuple)) else (Q(a),)+(Q(0),)*5
 @staticmethod
 def cast(a):return a if isinstance(a,Series) else Series(a)
 def __add__(self,a):return Series([x+y for x,y in zip(self.v,self.cast(a).v)])
 __radd__=__add__
 def __neg__(self):return Series([-x for x in self.v])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):return Series(conv(self.v,self.cast(a).v,5))
 __rmul__=__mul__
 def inverse(self):
  need(self.v[0]!=0,'SERIES_NONZERO_CONSTANT');v=[1/self.v[0]]
  for n in range(1,6):v.append(-sum(self.v[j]*v[n-j] for j in range(1,n+1))/self.v[0])
  return Series(v)
 def __truediv__(self,a):return self*self.cast(a).inverse()
 def __rtruediv__(self,a):return self.cast(a)*self.inverse()
 def __pow__(self,n):
  need(isinstance(n,int) and n>=0,'SERIES_POWER')
  out=Series(1)
  for _ in range(n):out=out*self
  return out

def finite_primitives(w,lam,kap,c,ep,prim,envmod):
 def env(x,gap):
  e=envmod.envelopes(x,gap);e['BR']=ep.radial_envelope(x,gap);e['BM']=ep.mixed_envelope(x,gap)
  H,T,Phi,E=ep.field_jets(x,gap);TP=26+1320*x+37600*x*x+64*(4*x/gap)**3/(1-4*x/gap)
  G=1/(1-2*x);v=4*x*G;vu=2*x*G;vt=4*x*G+8*x*x*G*G
  d=x*(1+v);dd=x*(1+2*v+v*vu+vt+v*v);l=G*x;ll=G*G*x
  e['BK']=E*E*G*(dd+(Q(3,32)+3*d)*d)+G*(TP+ll+(4*H+5*l)*(T+l))+Phi+x
  return e
 original=prim(w,lam,kap,c,env)
 W=w+lam*w;rho=c['rho'];ws=4*W*(1+2*W)/(1-2*W)**3;V=3*W+22*ws*W/rho
 cn=138*V*V/(1-160*ws/rho-840*ws*ws/rho**2);e=env(W,c['gap'])
 return (cn,original[1],e['BM'],e['BK'],e['BR'],e['BJ'],original[6])

def main(lease):
 started=time.monotonic();inputs={};gates={}
 sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','DERIVATION.txt')}
 for n in ('lease.py','DESIGN.txt'):
  p=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(p)]=sha(p)
 def bind(p,h):need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def gate(v,n):need(v,n);gates[n]=True
 parent=BASE/'20261027_QUINTIC_CLOCK_SCALAR_FACTORIAL'
 bind(parent/'TERMINAL.json','594b235f89d6ab8fc7b0a97370c31eda875076a985ff96e4724de689c3508f54')
 t=read(parent/'TERMINAL.json');gate(t['pass_status'],'PARENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(parent/'BINDING.json')[group].items():bind(p,h)
 def authenticated(path):
  p=BASE/path;gate(inputs.get(str(p))==sha(p),'AUTHENTICATED:'+path);return read(p)
 current=BASE/'20261027_REAL_AXIS_CLOCK_COEFFICIENTS'
 bind(current/'TERMINAL.json','c2e10b6756e68bbfdada50034d212a13f56d7a09ad95827c72ab89477088351b')
 ct=read(current/'TERMINAL.json');gate(ct['pass_status'],'CURRENT_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(current/n,ct[k])
 for group in ('inputs','sources','runtime'):
  for p,h in read(current/'BINDING.json')[group].items():bind(p,h)
 current_result=read(current/'RESULT.json')
 new_parent_result=read(parent/'RESULT.json');parent_result=authenticated('20261027_COMPONENT_QUARTIC_CLOCK_ENCLOSURE/RESULT.json');old=authenticated('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');prior=old['constants_exact']['refined']
 c={k:Q(v) for k,v in authenticated('20261026_NEUTRAL_SOURCE_MAJORANT/RESULT.json')['constants_exact'].items()}
 c['C0']=Q(prior['C0']);c['total']=Q(prior['Cscalar'])
 cfg=dict(authenticated('20261027_SPLIT_NORM_GRID/CONTRACT.json'),bulk_seed_bound=Q(prior['seed']))
 prior_module=load('quartic_parent_certificate',BASE/'20261027_FINAL_FIXED_GRID_CERTIFICATE/check.py')
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
 gate(inputs.get(str(ringpath))==sha(ringpath),'POLYNOMIAL_RING_AUTHORITY')
 ring=load('quartic_symbolic_ring',ringpath);ring.NAMES=('d1','d2','d3','d4','d5','L2','L3','L4','r');ring.N=9;ring.ZERO=(0,)*9
 ep=load('finite_endpoint',BASE/'20261026_REAL_AXIS_OSCILLATOR_ENDPOINT/check.py')
 prim=load('finite_primitive',BASE/'20261026_ROUTED_SOURCE_BUDGET_R1/check.py').primitives
 envmod=load('finite_environment',BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY/check.py')
 Jet=load('finite_priorjet',BASE/'20261026_TAIL_FEASIBILITY_ORACLE/check.py').Jet
 auth=BASE/'20261027T043011Z_TWO_HOUR_CLOCK_CONTINUATION/AUTHORITY.txt';bind(auth,sha(auth))
 len(str(10**20000));runtime=lease.observed()
 for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,cutoff_unix=CUTOFF))
 baseline=prior_module.certify(old['selected']['refined'],'baseline',c,cfg,gate)
 gate({k:str(v) for k,v in baseline.items()}==prior,'FULL_BASELINE_REPLAY')
 d1,d2,d3,d4,d5,L2,L3,L4,r=[ring.variable(j) for j in range(9)]
 ell=[ring.P(0),ring.P(-1),-L2,-L3,-L4];inverse=[ring.P(1)]
 for n in range(1,5):inverse.append(sum((k*ell[k]*inverse[n-k] for k in range(1,n+1)),ring.P(0))/n)
 D=[ring.P(0),d1,d2,d3,d4,d5]
 F=[r*(sum((j*D[j]*inverse[n-j] for j in range(1,n+1)),ring.P(0))-D[n]) for n in range(1,6)]
 expected=[ring.P(0),r*(d2-d1),r*(2*d3-2*d2+(Q(1,2)-L2)*d1),r*(3*d4-3*d3+(1-2*L2)*d2+(-L3+L2-Q(1,6))*d1),r*(4*d5-4*d4+3*d3*(Q(1,2)-L2)+2*d2*(-L3+L2-Q(1,6))+d1*(-L4+L3+L2*L2/2-L2/2+Q(1,24)))]
 for n,(a,b) in enumerate(zip(F,expected),1):gate((a-b).iszero(),'SYMBOLIC_CLOCK_DEGREE:'+str(n))
 gate(not (F[3]-r*(3*d4-3*d3+(1-2*L2)*d2+(-L3+L2)*d1)).iszero(),'MUTATION_OMITTED_ONE_SIXTH')
 # Genuine coefficient recurrence, not a Cauchy coefficient bound.
 K=baseline['K'];seed=baseline['seed'];row=old['selected']['refined']
 A=1+Q(row['graph_weight'])+Q(row['oscillator_weight']);N=5
 w=[Q(0)]*(N+1);w[1]=seed
 for n in range(2,N+1):
  w[n]=sum((m-1)*K**(m-1)*power(w,m,N)[n] for m in range(2,n+1))
 gate(w==[0,seed,K*seed**2,4*K**2*seed**3,18*K**3*seed**4,90*K**4*seed**5],'RECURRENCE_CLOSED_FORM')
 U=[A*4**n*w[n] for n in range(N+1)]
 distance=[9*sum(power(U,m,N)[n] for m in range(1,N+1)) for n in range(N+1)]
 bound_d4=distance[4]
 formula=2304*seed**4*(18*A*K**3+9*A*A*K*K+3*A**3*K+A**4)
 gate(bound_d4==formula and bound_d4>0,'DISTANCE_QUARTIC_ENCLOSURE')
 gate(list(map(str,w[:5]))==parent_result['majorant_coefficients'] and list(map(str,distance[:5]))==parent_result['aggregate_distance_coefficients'],'PARENT_MAJORANT_REPLAY')
 old_d4=bound_d4
 lam=Q(row['graph_weight'])
 bhat=[Q(0)]+[4**n*w[n]/n**2 for n in range(1,N+1)]
 xhat=[Q(0)]+[2*lam*4**n*w[n]/n**3 for n in range(1,N+1)];xhat[1]=Q(0)
 exponential=[Q(1)]
 for n in range(1,N+1):exponential.append(sum(k*bhat[k]*exponential[n-k] for k in range(1,n+1))/n)
 component_distance=[Q(0)]+[3*(exponential[n]+sum(exponential[j]*xhat[n-j] for j in range(n+1))) for n in range(1,N+1)]
 bound_d4=component_distance[4]
 gate(0<bound_d4<=old_d4,'COMPONENT_QUARTIC_DOMINATION')
 gate(list(map(str,component_distance[:5]))==parent_result['distance_coefficients'],'COMPONENT_PARENT_REPLAY')
 bound_d5=component_distance[5]
 gate(list(map(str,component_distance))==new_parent_result['distance_coefficients'],'FULL_FIFTH_COEFFICIENT_REPLAY')
 real_bhat=[Q(0)]+[w[n]/n**2 for n in range(1,N+1)]
 real_xhat=[Q(0)]+[2*lam*w[n]/n**3 for n in range(1,N+1)];real_xhat[1]=Q(0)
 real_exp=[Q(1)]
 for n in range(1,N+1):real_exp.append(sum(k*real_bhat[k]*real_exp[n-k] for k in range(1,n+1))/n)
 real_distance=[Q(0)]+[3*(real_exp[n]+sum(real_exp[j]*real_xhat[n-j] for j in range(n+1))) for n in range(1,N+1)]
 real_d4,real_d5=real_distance[4:6]
 gate(all(0<=x<=y for x,y in zip(real_distance,component_distance)),'REAL_AXIS_COEFFICIENT_DOMINATION')
 clock=authenticated('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 cubic=authenticated('20261026_NEUTRAL_CUBIC_CLOCK_TAIL/RESULT.json')
 coefficients={};real_coefficients={}
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
  old_f4=mul(rate,add(add(sc((-bound_d4,bound_d4),3),sc(three,-3)),add(mul(add((Q(1),Q(1)),sc(l2,-2)),two),mul(add(add(neg(l3),l2),(-Q(1,6),-Q(1,6))),one))))
  gate(packed(old_f4)==parent_result['coefficient_intervals'][engine]['F4'],'PARENT_F4_REPLAY:'+engine)
  gate(data['E']==(Q(1),Q(1)),'LOWER_E_NORMALIZATION:'+engine)
  k=iv(affine['parameters']['k'])
  hp=neg(add(sc(mul(data['T'],data['T']),Q(1,3)),mul(k,mul(data['E'],data['E']))))
  xi4_bound=Q(row['graph_weight'])*4**4*w[4]/4**3
  p4_bound=bhat[4];xi2sq=mul(data['xi2'],data['xi2'])
  v2=sc(mul(mul(rate,data['E']),data['xi2']),2)
  l4=add(add((-p4_bound,p4_bound),mul(data['H'],(-xi4_bound,xi4_bound))),add(sc(mul(hp,xi2sq),Q(1,2)),sc(mul(v2,v2),-Q(1,2))))
  inv2=add((Q(1,2),Q(1,2)),neg(l2))
  inv3=add(add(neg(l3),l2),(-Q(1,6),-Q(1,6)))
  inv4=add(add(add(neg(l4),l3),add(sc(mul(l2,l2),Q(1,2)),sc(l2,-Q(1,2)))),(Q(1,24),Q(1,24)))
  f5=mul(rate,add(add(sc((-bound_d5,bound_d5),4),sc((-bound_d4,bound_d4),-4)),add(add(sc(mul(three,inv2),3),sc(mul(two,inv3),2)),mul(one,inv4))))
  gate(Q(1,20000)<data['chi1'][0]<=data['chi1'][1]<Q(1,10000),'SCALAR_LINEAR_WITNESS:'+engine)
  coefficients[engine]=dict(L4=packed(l4),F5=packed(f5),F5_abs=str(max(map(abs,f5))),chi1=packed(data['chi1']),chi2=packed(data['chi2']),chi3=packed(data['chi3']),L2=packed(l2),L3=packed(l3),d4=packed((-bound_d4,bound_d4)),F2=packed(f2),F3=packed(f3),F4=packed(f4),F4_abs=str(max(map(abs,f4))))
  gate(coefficients[engine]==new_parent_result['coefficient_intervals'][engine],'PARENT_ALL_COEFFICIENTS:'+engine)
  real_xi4=Q(row['graph_weight'])*w[4]/4**3
  real_l4=add(add((-real_bhat[4],real_bhat[4]),mul(data['H'],(-real_xi4,real_xi4))),add(sc(mul(hp,xi2sq),Q(1,2)),sc(mul(v2,v2),-Q(1,2))))
  real_f4=mul(rate,add(add(sc((-real_d4,real_d4),3),sc(three,-3)),add(mul(add((Q(1),Q(1)),sc(l2,-2)),two),mul(add(add(neg(l3),l2),(-Q(1,6),-Q(1,6))),one))))
  real_inv4=add(add(add(neg(real_l4),l3),add(sc(mul(l2,l2),Q(1,2)),sc(l2,-Q(1,2)))),(Q(1,24),Q(1,24)))
  real_f5=mul(rate,add(add(sc((-real_d5,real_d5),4),sc((-real_d4,real_d4),-4)),add(add(sc(mul(three,inv2),3),sc(mul(two,inv3),2)),mul(one,real_inv4))))
  real_coefficients[engine]=dict(coefficients[engine],L4=packed(real_l4),F4=packed(real_f4),F4_abs=str(max(map(abs,real_f4))),F5=packed(real_f5),F5_abs=str(max(map(abs,real_f5))),d4=packed((-real_d4,real_d4)))

 gate(max(Q(coefficients[e]['L3'][0]) for e in coefficients)<=min(Q(coefficients[e]['L3'][1]) for e in coefficients),'L3_ENGINE_OVERLAP')
 B4=max(Q(v['F4_abs']) for v in coefficients.values())
 gate(B4==Q(parent_result['quartic_abs']),'PARENT_B4')
 B5=max(Q(v['F5_abs']) for v in coefficients.values())
 C2=max(abs(Q(x)) for v in coefficients.values() for x in v['chi2']);C3=max(abs(Q(x)) for v in coefficients.values() for x in v['chi3'])
 radius=baseline['physical_radius'];MD=baseline['observable_sup'];MF=baseline['clock_sup'];Y=baseline['aggregate_bound']
 def select(fifth,scalar):
  found=False
  for j in range(1,8193):
   q=Q(1,2**j);eta=radius*q/2;tail=MF*q**(6 if fifth else 5)/(1-q);known3=10000*eta**3;known4=B4*eta**4;known5=B5*eta**5 if fifth else Q(0);qd=q/2
   dt=MD*qd**2/(1-qd)
   if scalar:
    st=C2*eta**2+C3*eta**3+Y*qd**4/(1-qd)
    se=2*C2*eta**2+3*C3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
   else:st=Y*qd**2/(1-qd);se=Y*qd**2*(2-qd)/(1-qd)**2
   if known3+known4+known5+tail<=10*eta**2 and dt<=25*eta and st<=eta/40000 and se<=eta/40000:found=True;break
  gate(found,'FULL_REMAINDER_SELECTION:'+str((fifth,scalar)))
  gate(eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0,'OPENING_SIGN:'+str((fifth,scalar)))
  out=dict(baseline,clock_eta=eta,clock_tail=tail,known_cubic=known3,known_quartic=known4,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
  if fifth:out['known_quintic']=known5
  return out,j,dict(clock=(known3+known4+known5+tail)/(10*eta**2),distance=dt/(25*eta),scalar=st/(eta/40000),scalar_derivative=se/(eta/40000))
 lanes={'baseline':(False,False),'clock5':(True,False),'scalar3':(False,True),'joint':(True,True)}
 constants={};dyadics={};ratios={}
 for name,args in lanes.items():constants[name],dyadics[name],ratios[name]=select(*args)
 gate({k:str(v) for k,v in constants['baseline'].items()}==parent_result['constants_exact']['quartic'],'FULL_QUARTIC_PARENT_REPLAY')
 for name,cvals in constants.items():gate({k:str(v) for k,v in cvals.items()}==new_parent_result['constants_exact'][name],'FULL_FACTORIAL_PARENT_REPLAY:'+name)
 original_constants=constants;original_ratios=ratios;original_dyadics=dyadics
 original_B4,original_B5=B4,B5
 B4=max(Q(v['F4_abs']) for v in real_coefficients.values());B5=max(Q(v['F5_abs']) for v in real_coefficients.values())
 gate(B4<=original_B4 and B5<=original_B5,'REAL_CLOCK_BOUND_DOMINATION')
 real_constants={};real_ratios={};real_dyadics={}
 for name,args in lanes.items():real_constants[name],real_dyadics[name],real_ratios[name]=select(*args)
 constants={'baseline':original_constants['joint'],'real':real_constants['joint']};ratios={'baseline':original_ratios['joint'],'real':real_ratios['joint']};dyadics={'baseline':original_dyadics['joint'],'real':real_dyadics['joint']}

 gate({k:str(v) for k,v in real_constants['joint'].items()}==current_result['constants_exact']['real'],'CURRENT_FULL_CERTIFICATE_REPLAY')
 # Frozen map, finite Taylor coefficients; pay primitive Euler degree m.
 test_series=Series([1,2,3,4,5,6]);gate((test_series*test_series.inverse()).v==Series(1).v,'SERIES_INVERSE_IDENTITY')
 kap=Q(row['oscillator_weight']);a=Q(row['a']);weights={out:list(map(Q,vals)) for out,vals in old['response_weights']['refined'].items()}
 pv=finite_primitives(a,lam,kap,c,ep,prim,envmod)
 pj=finite_primitives(Jet(0,1),lam,kap,c,ep,prim,envmod)
 ps=finite_primitives(Series([Q(0),Q(1)]),lam,kap,c,ep,prim,envmod)
 for i,(v,j,tj) in enumerate(zip(pv,pj,ps)):
  gate(tuple(tj.v[:2])==tuple(j.v[:2]),'SOURCE_FIRST_JET:'+str(i))
  gate(all(x>=0 for x in tj.v),'POSITIVE_SOURCE_COEFFICIENTS:'+str(i))
 loads=[v-j.v[0]-a*j.v[1] for v,j in zip(pv,pj)]
 masses=[sum(k*v for k,v in zip(weights['B'],loads)),loads[1]/lam,sum(k*v for k,v in zip(weights['C'],loads))/kap]
 gate(list(map(str,masses))==row['masses'],'FROZEN_MAP_MASSES')
 H=[Q(0)]*6;components={}
 for m in range(2,6):
  raw=[x.v[m] for x in ps]
  routed=[sum(k*v for k,v in zip(weights['B'],raw)),raw[1]/lam,sum(k*v for k,v in zip(weights['C'],raw))/kap]
  components[str(m)]=list(map(str,routed));H[m]=m*max(routed)
  gate(0<=H[m]<=(m-1)*K**(m-1),'GEOMETRIC_COEFFICIENT_DOMINATION:'+str(m))
 z=[Q(0)]*6;z[1]=seed
 for n in range(2,6):
  z[n]=sum(H[m]*power(z,m,5)[n] for m in range(2,n+1))
  gate(0<=z[n]<=w[n],'FINITE_RECURRENCE_DOMINATION:'+str(n))
 new_b=[Q(0)]+[z[n]/n**2 for n in range(1,6)]
 new_x=[Q(0)]+[2*lam*z[n]/n**3 for n in range(1,6)];new_x[1]=Q(0)
 new_exp=[Q(1)]
 for n in range(1,6):new_exp.append(sum(k*new_b[k]*new_exp[n-k] for k in range(1,n+1))/n)
 new_d=[Q(0)]+[3*(new_exp[n]+sum(new_exp[j]*new_x[n-j] for j in range(n+1))) for n in range(1,6)]
 gate(all(x<=y for x,y in zip(new_d,real_distance)),'FINITE_DISTANCE_DOMINATION')
 finite_coefficients={}
 for engine,record in real_coefficients.items():
  affine=authenticated('20261026_GROWING_MODE_CUBIC_AFFINE/PRODUCTION_'+engine+'.json')
  data={k:iv(v) for k,v in affine['walls']['lower']['data'].items()}
  vals=clock['arms'][engine]['values'];one,two,three,rate=[iv(vals[k]) for k in ('d1','d2','d3','rate')]
  l2=tuple(map(Q,record['L2']));l3=tuple(map(Q,record['L3']))
  k=iv(affine['parameters']['k']);hp=neg(add(sc(mul(data['T'],data['T']),Q(1,3)),mul(k,mul(data['E'],data['E']))))
  xi2=data['xi2'];v2=sc(mul(mul(rate,data['E']),xi2),2);xi4=lam*z[4]/64
  l4=add(add((-new_b[4],new_b[4]),mul(data['H'],(-xi4,xi4))),add(sc(mul(hp,mul(xi2,xi2)),Q(1,2)),sc(mul(v2,v2),-Q(1,2))))
  inv2=add((Q(1,2),Q(1,2)),neg(l2));inv3=add(add(neg(l3),l2),(-Q(1,6),-Q(1,6)))
  inv4=add(add(add(neg(l4),l3),add(sc(mul(l2,l2),Q(1,2)),sc(l2,-Q(1,2)))),(Q(1,24),Q(1,24)))
  f4=mul(rate,add(add(sc((-new_d[4],new_d[4]),3),sc(three,-3)),add(mul(add((Q(1),Q(1)),sc(l2,-2)),two),mul(inv3,one))))
  f5=mul(rate,add(add(sc((-new_d[5],new_d[5]),4),sc((-new_d[4],new_d[4]),-4)),add(add(sc(mul(three,inv2),3),sc(mul(two,inv3),2)),mul(one,inv4))))
  finite_coefficients[engine]=dict(record,L4=packed(l4),F4=packed(f4),F4_abs=str(max(map(abs,f4))),F5=packed(f5),F5_abs=str(max(map(abs,f5))),d4=packed((-new_d[4],new_d[4])))
 B4=max(Q(v['F4_abs']) for v in finite_coefficients.values());B5=max(Q(v['F5_abs']) for v in finite_coefficients.values())
 gate(B4<=Q(current_result['quartic_abs']) and B5<=Q(current_result['quintic_abs']),'FINITE_CLOCK_DOMINATION')
 finite_constants={};finite_ratios={};finite_dyadics={}
 for name,args in lanes.items():finite_constants[name],finite_dyadics[name],finite_ratios[name]=select(*args)
 constants={'baseline':real_constants['joint'],'finite':finite_constants['joint']};ratios={'baseline':real_ratios['joint'],'finite':finite_ratios['joint']};dyadics={'baseline':real_dyadics['joint'],'finite':finite_dyadics['joint']}

 for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_BINDING:'+p)
 gate(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 out=dict(pass_status=True,classification='FINITE_SOURCE_COEFFICIENT_CLOCK_ENCLOSURE',finite_source_coefficients=[list(map(str,x.v)) for x in ps],finite_routed_coefficients=components,finite_H=list(map(str,H)),finite_majorant=list(map(str,z)),finite_distance=list(map(str,new_d)),finite_coefficients=finite_coefficients,finite_controls={name:{k:str(v) for k,v in vals.items()} for name,vals in finite_constants.items()},coefficient_intervals=finite_coefficients,parent_coefficient_intervals=real_coefficients,majorant_coefficients=list(map(str,z)),parent_majorant_coefficients=list(map(str,w)),bulk_coefficients=list(map(str,new_b)),graph_slope_coefficients=list(map(str,new_x)),distance_coefficients=list(map(str,new_d)),quartic_abs=str(B4),quintic_abs=str(B5),scalar_abs={'chi2':str(C2),'chi3':str(C3)},constants_exact={name:{k:str(v) for k,v in c.items()} for name,c in constants.items()},gains_exact={name:str(c['clock_eta']/constants['baseline']['clock_eta']) for name,c in constants.items()},selected_dyadics=dyadics,gate_ratios={name:{k:str(v) for k,v in d.items()} for name,d in ratios.items()},symbolic_F5=F[4].pack(),factorial_controls={name:{k:str(v) for k,v in cvals.items()} for name,cvals in real_constants.items()},gates=gates,seconds=time.monotonic()-started,ode_solves=0,scope='Symmetric F5 enclosure and archived scalar jets; no resolved quintic sign or finite trajectory.')
 put('RESULT.json',out);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(seconds=out['seconds'],gates=len(gates),d5_bound=float(new_d[5]),F5_abs=float(B5),scalar_abs={k:float(Q(v)) for k,v in out['scalar_abs'].items()},display={name:dict(clock_eta=float(c['clock_eta']),gain=float(c['clock_eta']/constants['baseline']['clock_eta']),gate_ratios={k:float(v) for k,v in ratios[name].items()}) for name,c in constants.items()})),flush=True)

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

