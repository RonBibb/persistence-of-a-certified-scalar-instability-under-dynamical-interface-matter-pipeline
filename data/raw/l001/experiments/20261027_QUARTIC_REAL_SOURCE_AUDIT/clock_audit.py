"""Independent saved-record clock audit; Linux only, no producer imports/ODE."""
import sys, json, hashlib, time, signal, importlib.util, traceback, os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent
CHECKS=0
def ck(v,n):
 global CHECKS
 CHECKS+=1
 if not v: raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
class I:
 def __init__(self,a,b=None):
  if isinstance(a,I):self.a,self.b=a.a,a.b
  else:self.a,self.b=Q(a),Q(a if b is None else b)
 @staticmethod
 def cast(x):return x if isinstance(x,I) else I(x)
 def __add__(self,x):
  x=self.cast(x);return I(self.a+x.a,self.b+x.b)
 __radd__=__add__
 def __neg__(self):return I(-self.b,-self.a)
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  x=self.cast(x);z=[a*b for a in (self.a,self.b) for b in (x.a,x.b)];return I(min(z),max(z))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.cast(x);ck(x.a*x.b>0,'NONZERO_DIVISOR');return self*I(1/x.b,1/x.a)
 def __pow__(self,n):
  z=I(1)
  for _ in range(n):z=z*self
  return z
 def abs(self):return max(abs(self.a),abs(self.b))
 def pair(self):return [str(self.a),str(self.b)]
def iv(x):return I(*x['exact_bounds'])
def pair(x):return I(*x)
def sym(x):return I(-x,x)
def mulseries(a,b,N):return [sum((a[j]*b[n-j] for j in range(n+1)),Q(0)) for n in range(N+1)]
def powseries(a,m,N):
 z=[Q(1)]+[Q(0)]*N
 for _ in range(m):z=mulseries(z,a,N)
 return z
def main(name):
 root=BASE/name;term=read(root/'TERMINAL.json');pin=sha(root/'TERMINAL.json')
 ck(term['pass_status'],'PRODUCER_PASS')
 for file,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(root/file)==term[key],'TERMINAL:'+file)
 bind=read(root/'BINDING.json');bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in bind[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 result=read(root/'RESULT.json');ck(all(result['gates'].values()),'SAVED_GATES')
 sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json')
 clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json')
 actual_mode='ACTUAL_QUARTIC_CLOCK' in name
 N=6 if actual_mode else {'SEVENTH':7,'EIGHTH':8,'NINTH':9}[next(s for s in ('SEVENTH','EIGHTH','NINTH') if s in name)]
 label={6:'actual_quartic',7:'seventh',8:'eighth',9:'ninth'}[N]
 actual=result if actual_mode else auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json')
 base={k:Q(v) for k,v in result['constants_exact']['baseline'].items()}
 b=None;z=None;d=None;lam=None
 if N>=7:
  fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json');row=fixed['selected']['refined'];lam=Q(row['graph_weight']);kap=Q(row['oscillator_weight'])
  weights={k:list(map(Q,v)) for k,v in fixed['response_weights']['refined'].items()};raw=[list(map(Q,v)) for v in result['source_coefficients']]
  ck(len(raw)==7 and all(len(v)==N+1 for v in raw),'RAW_SHAPE');ck(all(v>=0 for r in raw for v in r),'RAW_POSITIVE')
  H=[Q(0)]*(N+1)
  for m in range(2,N+1):
   loads=[v[m] for v in raw];r=[sum(x*y for x,y in zip(weights['B'],loads)),loads[1]/lam,sum(x*y for x,y in zip(weights['C'],loads))/kap]
   H[m]=m*max(r);ck(list(map(str,r))==result['routed'][str(m)],'ROUTED:'+str(m));ck(H[m]<=(m-1)*base['K']**(m-1),'H_BOUND')
  ck(list(map(str,H))==result['H'],'H_REDUCTION')
  z=[Q(0)]*(N+1);z[1]=base['seed']
  for n in range(2,N+1):z[n]=sum(H[m]*powseries(z,m,N)[n] for m in range(2,n+1))
  ck(list(map(str,z))==result['majorant'],'FINITE_RECURRENCE')
  b=[Q(0)]+[z[n]/n**2 for n in range(1,N+1)];x=[Q(0)]+[2*lam*z[n]/n**3 for n in range(1,N+1)];x[1]=0
  ex=[Q(1)]
  for n in range(1,N+1):ex.append(sum(j*b[j]*ex[n-j] for j in range(1,n+1))/n)
  d=[Q(0)]+[3*(ex[n]+sum(ex[j]*x[n-j] for j in range(n+1))) for n in range(1,N+1)]
  ck(list(map(str,d))==result['distance'],'DISTANCE_REDUCTION')
  if N==7:
   preceding=sixth;prefix_keys=('finite_source_coefficients','sixth_H','sixth_majorant','sixth_distance')
  else:
   preceding=auth('20261027_'+{8:'SEVENTH',9:'EIGHTH'}[N]+'_CLOCK_ENCLOSURE/RESULT.json');prefix_keys=('source_coefficients','H','majorant','distance')
  ck([list(map(str,v[:N])) for v in raw]==preceding[prefix_keys[0]],'RAW_PARENT_PREFIX')
  for v,key in zip((H,z,d),prefix_keys[1:]):ck(list(map(str,v[:N]))==preceding[key],'PARENT_PREFIX:'+key)
 bounds=[]
 for engine in ('primary','independent'):
  vals=clock['arms'][engine]['values'];d1,d2,d3,r=[iv(vals[k]) for k in ('d1','d2','d3','rate')]
  lower=sixth['sixth_coefficients'][engine];L2,L3=pair(lower['L2']),pair(lower['L3'])
  if actual_mode:
   arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');d4=iv(arm['d4'])
   f4=r*(3*d4-3*d3+(1-2*L2)*d2+(-L3+L2-Q(1,6))*d1)
   saved=result['coefficient_intervals'][engine]
   ck(saved['d4']==d4.pair() and saved['F4']==f4.pair() and Q(saved['F4_abs'])==f4.abs(),'ACTUAL_F4:'+engine);bounds.append(f4.abs());continue
  af=auth('20261026_GROWING_MODE_CUBIC_AFFINE/PRODUCTION_'+engine+'.json');a={k:iv(v) for k,v in af['walls']['lower']['data'].items()};k=iv(af['parameters']['k']);m=iv(af['parameters']['m2']);h=iv(af['parameters']['h'])
  H,T,E,Tp=a['H'],a['T'],a['E'],a['Tp'];hp=-(T*T/3+k*E*E);hpp=-Q(2,3)*T*Tp+2*k*H*E*E
  xi={2:a['xi2'],3:a['xi3']}
  for j in range(4,N):xi[j]=sym(lam*z[j]/j**3)
  p1=a['p1'];a1=-3*p1;a2=a['c2']-3*a['p2']-H*xi[2];a3=a['c3']-3*a['p3']-3*a['u1']*xi[2]-H*xi[3]
  e2=a2+a1*a1/2;e3=a3+a1*a2+a1*a1*a1/6
  v2=2*r*E*xi[2];v3=r*E*(3*xi[3]-6*p1*xi[2]);v4=r*E*(4*xi[4]-9*p1*xi[3]+2*xi[2]*e2)
  L6=sym(b[6])+H*xi[6]+hp*(xi[2]*xi[4]+xi[3]*xi[3]/2)+hpp*xi[2]*xi[2]*xi[2]/6-v2*v4-v3*v3/2
  logs=[I(0),I(1),L2,L3,pair(lower['L4']),pair(lower['L5']),L6]
  if N>=8:
   v5=r*E*(5*xi[5]-12*p1*xi[4]+3*xi[3]*e2+2*xi[2]*e3)
   L7=sym(b[7])+H*xi[7]+hp*(xi[2]*xi[5]+xi[3]*xi[4])+hpp*xi[2]*xi[2]*xi[3]/2-v2*v5-v3*v4;logs.append(L7)
  if N>=9:
   Tpp=m*T-4*hp*T-4*H*Tp;hppp=-Q(2,3)*(Tp*Tp+T*Tpp)+2*k*E*E*(hp-2*H*H)
   inner=36*p1*a['p3']+24*a['p2']*a['p2']+6*a['f1']*a['f3']+4*a['f2']*a['f2']-18*p1*a['c3']-24*a['p2']*a['c2']+4*a['c2']*a['c2']
   den=4*(4*r-h);ck(den.a>0,'C4_DENOM');c4=-(r/den)*inner;c2p=-iv(af['parameters']['c_factor'])*(12*p1*a['u1']+2*a['f1']*a['g1'])
   a4=c4-3*sym(b[4])+xi[2]*c2p-H*xi[4]-hp*xi[2]*xi[2]/2;e4=a4+a1*a3+a2*a2/2+a1*a1*a2/2+a1**4/24
   v6=r*E*(6*xi[6]+5*xi[5]*a1+4*xi[4]*e2+3*xi[3]*e3+2*xi[2]*e4)
   L8=sym(b[8])+H*xi[8]+hp*(xi[2]*xi[6]+xi[3]*xi[5]+xi[4]*xi[4]/2)+hpp*(xi[2]*xi[2]*xi[4]+xi[2]*xi[3]*xi[3])/2+hppp*xi[2]**4/24-v2*v6-v3*v5-v4*v4/2-v2**4/4;logs.append(L8)
   ck(result['coefficients'][engine]['c4']==c4.pair(),'C4_RECONSTRUCTION')
  ck(result['coefficients'][engine]['L'+str(N-1)]==logs[-1].pair(),'LAPSE_RECONSTRUCTION:'+engine)
  # The coefficient recurrence is independently evaluated with interval pairs.
  ei=[I(1)]
  for n in range(1,N):ei.append(-sum((j*logs[j]*ei[n-j] for j in range(1,n+1)),I(0))/n)
  ds=[I(0),d1,d2,d3,pair(actual['coefficient_intervals'][engine]['d4'])]+[sym(d[j]) for j in range(5,N+1)]
  f=r*((N-1)*ds[N]+sum((j*ds[j]*ei[N-j] for j in range(1,N)),I(0)))
  saved=result['coefficients'][engine];ck(saved['F'+str(N)]==f.pair(),'CLOCK_COEFFICIENT:'+engine);ck(Q(saved['F'+str(N)+'_abs'])==f.abs(),'CLOCK_ABS');bounds.append(f.abs())
 B={3:Q(10000),4:Q(actual['selected_quartic_abs']),5:Q(sixth['quintic_abs']),6:Q(sixth['sixth_abs'])}
 if actual_mode:
  ck(Q(result['actual_quartic_abs'])==max(bounds),'ACTUAL_BOUND');ck(B[4]==min(Q(sixth['quartic_abs']),max(bounds)),'MIN_OLD_NEW')
 else:
  for j,nm in [(7,'SEVENTH'),(8,'EIGHTH')]:
   if j<N:B[j]=Q(auth('20261027_'+nm+'_CLOCK_ENCLOSURE/RESULT.json')[nm.lower()+'_abs'])
  B[N]=max(bounds);ck(Q(result[label+'_abs'])==B[N],'NEW_BOUND')
 C2,C3=Q(sixth['scalar_abs']['chi2']),Q(sixth['scalar_abs']['chi3'])
 def certificate(bb,degree):
  for j in range(1,8193):
   q=Q(1,2**j);eta=base['physical_radius']*q/2;t=q/2;tail=base['clock_sup']*q**(degree+1)/(1-q)
   known={n:bb[n]*eta**n for n in range(3,degree+1)};dt=base['observable_sup']*t*t/(1-t)
   st=C2*eta**2+C3*eta**3+base['aggregate_bound']*t**4/(1-t);se=2*C2*eta**2+3*C3*eta**3+base['aggregate_bound']*t**4*(4-3*t)/(1-t)**2
   costs={str(n):v/(10*eta**2) for n,v in known.items()};costs['tail']=tail/(10*eta**2)
   ratios={'clock':sum(costs.values()),'distance':dt/(25*eta),'scalar':st/(eta/40000),'scalar_derivative':se/(eta/40000)}
   if all(v<=1 for v in ratios.values()):break
  ck(j<=8192 and all(v<=1 for v in ratios.values()),'GATE_ADMISSION');ck(eta<Q(1,512) and Q(25,64)*eta-60*eta*eta>0,'OPENING')
  out=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=dt,scalar_tail=st,scalar_derivative_tail=se,scalar_departure=eta/40000)
  for n,key in [(3,'cubic'),(4,'quartic'),(5,'quintic'),(6,'sixth'),(7,'seventh'),(8,'eighth'),(9,'ninth')]:
   if n<=degree:out['known_'+key]=known[n]
  return out,j,costs,ratios
 oldB=dict(B)
 if actual_mode:oldB[4]=Q(sixth['quartic_abs'])
 old,_,_,_=certificate(oldB,6 if actual_mode else N-1);ck(old==base,'BASELINE_FULL_CERTIFICATE')
 now,j,costs,ratios=certificate(B,N);ck({k:str(v) for k,v in now.items()}==result['constants_exact'][label],'FULL_CERTIFICATE');ck(j==result['selected_dyadic'],'FIRST_DYADIC')
 costnames={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 namedcosts={costnames[int(k)] if k!='tail' else ('unknown7' if actual_mode else 'unknown_tail'):str(v) for k,v in costs.items()}
 ck(namedcosts==result['clock_costs'],'PER_TERM_CLOCK_COSTS')
 ck({k:str(v) for k,v in ratios.items()}==result['gate_ratios'],'GATE_RATIOS');ck(Q(result['gain_exact'])==now['clock_eta']/base['clock_eta'],'GAIN')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(root/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=CHECKS,producer_terminal=pin,producer_result=sha(root/'RESULT.json'),clock_eta=str(now['clock_eta']),clock_eta_decimal=float(now['clock_eta']),costs={k:float(v) for k,v in costs.items()},gate_ratios={k:float(v) for k,v in ratios.items()},scope='Independent exact saved-source coefficient reductions, interval lapse/clock arithmetic and full first-dyadic certificates. Raw nonlinear source coefficients, ODE enclosure, source formulas and analytic-family premises inherited; no ODE rerun or fresh nonlinear source expansion.')
if __name__=='__main__':
 name=sys.argv[1];start=time.time();lease=None;dest=Path(__file__).parent/(name+'_AUDIT.json');pin=sha(__file__)
 if dest.exists():raise AssertionError('NO_AUDIT_RESTART')
 try:
  ck(sys.platform=='linux' and start<1793082611,'LINUX_CUTOFF')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  spec=importlib.util.spec_from_file_location('clock_review_lease',lp);lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=Path(__file__).parent;lease.acquire()
  ck(time.time()<1793082611,'POST_LEASE_CUTOFF');signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
  report=main(name);ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=CHECKS)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
