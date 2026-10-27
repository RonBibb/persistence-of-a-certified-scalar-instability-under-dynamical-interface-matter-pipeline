"""Independent exact saved-record audit of isolated actual-d5 clock readout."""
import sys,json,hashlib,time,signal,importlib.util,traceback,os
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent
ROOT=BASE/'20261027_ACTUAL_QUINTIC_CLOCK_CERTIFICATE'
COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
class I:
 def __init__(self,a,b=None):self.a,self.b=Q(a),Q(a if b is None else b)
 @staticmethod
 def cast(v):return v if isinstance(v,I) else I(v)
 def __add__(self,v):
  v=self.cast(v);return I(self.a+v.a,self.b+v.b)
 __radd__=__add__
 def __neg__(self):return I(-self.b,-self.a)
 def __sub__(self,v):return self+-self.cast(v)
 def __rsub__(self,v):return self.cast(v)+-self
 def __mul__(self,v):
  v=self.cast(v);z=[a*b for a in (self.a,self.b) for b in (v.a,v.b)];return I(min(z),max(z))
 __rmul__=__mul__
 def pair(self):return [str(self.a),str(self.b)]
 def abs(self):return max(abs(self.a),abs(self.b))
def iv(v):return I(*v['exact_bounds'])
def main():
 t=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(t['pass_status'],'PRODUCER_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('AUTHORITY.txt','authority_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/n)==t[k],'TERMINAL:'+n)
 bound={}
 for g,items in read(ROOT/'BINDING.json').items():
  ck(g in ('inputs','sources','runtime'),'BINDING_GROUP')
  for p,h in items.items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 result=read(ROOT/'RESULT.json');parent=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json')
 sixth=auth('20261027_SIXTH_CLOCK_ENCLOSURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');actual=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json')
 oldbound=Q(sixth['quintic_abs']);newbounds=[];oldbounds=[]
 for e in ('primary','independent'):
  v=clock['arms'][e]['values'];d1,d2,d3,r=[iv(v[k]) for k in ('d1','d2','d3','rate')]
  s=sixth['finite_coefficients'][e];l2,l3,l4,d4=[I(*s[k]) for k in ('L2','L3','L4','d4')]
  e2=I(Q(1,2))-l2;e3=-l3+l2-Q(1,6)
  e4=(-l4+l3)+(Q(1,2)*(l2*l2)-Q(1,2)*l2)+Q(1,24)
  def fifth(d5):return r*((4*d5-4*d4)+((3*(d3*e2)+2*(d2*e3))+d1*e4))
  b=Q(sixth['finite_distance'][5]);old=fifth(I(-b,b));newd=iv(actual['arms'][e]['bulk']['d5']);new=fifth(newd)
  ck(old.pair()==s['F5'] and old.abs()==Q(s['F5_abs']),'OLD_F5:'+e)
  expected=dict(d5=newd.pair(),d4_unchanged=d4.pair(),L4_unchanged=l4.pair(),inverse2=e2.pair(),inverse3=e3.pair(),inverse4=e4.pair(),baseline_F5=old.pair(),candidate_F5=new.pair(),candidate_abs=str(new.abs()))
  ck(result['coefficients'][e]==expected,'ALL_INTERVAL_RECORDS:'+e);newbounds.append(new.abs());oldbounds.append(old.abs())
 ck(max(oldbounds)==oldbound,'OLD_MAX');candidate=max(newbounds);chosen=min(candidate,oldbound)
 for k,v in [('candidate_quintic_abs',candidate),('selected_quintic_abs',chosen),('old_quintic_abs',oldbound)]:ck(Q(result[k])==v,k)
 fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');seventh=auth('20261027_SEVENTH_CLOCK_ENCLOSURE/RESULT.json');eighth=auth('20261027_EIGHTH_CLOCK_ENCLOSURE/RESULT.json')
 bs={3:Q(10000),4:Q(fourth['selected_quartic_abs']),6:Q(sixth['sixth_abs']),7:Q(seventh['seventh_abs']),8:Q(eighth['eighth_abs']),9:Q(parent['ninth_abs'])}
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 base={k:Q(v) for k,v in parent['constants_exact']['ninth'].items()};R=base['physical_radius'];Y=base['aggregate_bound'];MD=base['observable_sup'];MF=base['clock_sup'];c2,c3=[Q(sixth['scalar_abs'][k]) for k in ('chi2','chi3')]
 def evaluate(j,five):
  q=Q(1,2**j);eta=R*q/2;qd=q/2;b=dict(bs);b[5]=five
  terms={names[n]:coef*eta**n for n,coef in b.items()};tail=MF*q**10/(1-q)
  dist=MD*qd**2/(1-qd);sc=c2*eta**2+c3*eta**3+Y*qd**4/(1-qd);sd=2*c2*eta**2+3*c3*eta**3+Y*qd**4*(4-3*qd)/(1-qd)**2
  costs={k:v/(10*eta**2) for k,v in terms.items()};costs['unknown_tail']=tail/(10*eta**2)
  ratios=dict(clock=sum(costs.values()),distance=dist/(25*eta),scalar=sc/(eta/40000),scalar_derivative=sd/(eta/40000))
  gates={k:v<=1 for k,v in ratios.items()};gates['opening']=eta<Q(1,512) and Q(25,64)*eta-60*eta**2>0
  constants=dict(base,clock_eta=eta,clock_tail=tail,distance_tail=dist,scalar_tail=sc,scalar_derivative_tail=sd,scalar_departure=eta/40000)
  constants.update({'known_'+k:v for k,v in terms.items()})
  return constants,costs,ratios,gates
 def first(five):
  for j in range(1,8193):
   vals=evaluate(j,five)
   if all(vals[3].values()):return j,vals
  raise AssertionError('NO_CERTIFICATE')
 def strings(d):return {k:str(v) for k,v in d.items()}
 j0,old=first(oldbound);ck(old[0]==base and j0==parent['selected_dyadic'],'OLD_FULL_CERTIFICATE');ck(strings(old[1])==parent['clock_costs'] and strings(old[2])==parent['gate_ratios'],'OLD_COSTS')
 j,new=first(chosen);ck(j==result['selected_dyadic'],'FIRST_PASSING_DYADIC')
 ck(result['constants_exact']==dict(baseline=strings(old[0]),actual_d5=strings(new[0])),'BOTH_FULL_CERTIFICATES')
 for key,data in [('clock_costs',new[1]),('gate_ratios',new[2])]:ck(result[key]==strings(data),key)
 ck(result['gates']==new[3] and all(new[3].values()),'ALL_GATES');gain=new[0]['clock_eta']/base['clock_eta'];ck(Q(result['gain_exact'])==gain and gain>=1,'GAIN')
 if j>1:
  larger=evaluate(j-1,chosen);ck(not all(larger[3].values()),'NEXT_LARGER_FAILS')
  expected=dict(eta=str(larger[0]['clock_eta']),costs=strings(larger[1]),ratios=strings(larger[2]),gates=larger[3]);ck(result['next_larger']==expected,'NEXT_LARGER_COMPLETE')
 else:ck(result['next_larger'] is None,'NO_LARGER')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),eta_display=float(new[0]['clock_eta']),gain_display=float(gain),ratios={k:float(v) for k,v in new[2].items()},costs={k:float(v) for k,v in new[1].items()},next_larger_gates=result['next_larger']['gates'] if j>1 else None,scope='Independent exact interval F5 substitution and full baseline/refined dyadic certificate, costs and binding replay. Actual d5, analytic family, higher coefficients and source/ODE qualification inherited; no new evolution or source re-derivation.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'ACTUAL_QUINTIC_CLOCK_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux','LINUX_ONLY');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('actual_quintic_clock_audit_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire()
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDIT_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
