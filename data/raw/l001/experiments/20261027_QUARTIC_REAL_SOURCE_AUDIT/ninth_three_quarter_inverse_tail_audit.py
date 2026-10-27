"""Exact endpoint positive-tail audit; no producer tail module imported."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_NINTH_THREE_QUARTER_INVERSE_TAIL';CUTOFF=1793121042;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
class I:
 def __init__(self,a,b=None):self.lo,self.hi=Q(a),Q(a if b is None else b);ck(self.lo<=self.hi,'ORDER')
 @staticmethod
 def cast(x):return x if isinstance(x,I) else I(x)
 def __add__(self,x):
  x=self.cast(x);return I(self.lo+x.lo,self.hi+x.hi)
 __radd__=__add__
 def __neg__(self):return I(-self.hi,-self.lo)
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  x=self.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.cast(x);ck(x.lo*x.hi>0,'DIVISOR');v=[a/b for a in (self.lo,self.hi) for b in (x.lo,x.hi)];return I(min(v),max(v))
 def __rtruediv__(self,x):return self.cast(x)/self
 def __pow__(self,n):
  ck(n>=0 and isinstance(n,int),'POWER');out=I(1)
  for _ in range(n):out=out*self
  return out
def iv(x):return I(*x['exact_bounds'])
def contains(saved,x,n):
 v=iv(saved);ck(v.lo<=x.lo<=x.hi<=v.hi,'CONTAIN:'+n)
def poly(c,x):return sum((v*x**n for n,v in enumerate(c)),Q(0))
def expbounds(x):
 ck(0<=x.lo<=x.hi<1,'EXP_DOMAIN')
 def trunc(t):
  term=Q(1);s=term
  for n in range(1,33):term*=t/n;s+=term
  return s,term*t/33/(1-t/34)
 low,_=trunc(x.lo);hi,rem=trunc(x.hi);return I(low,hi+rem)
def main():
 term=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(term['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('inverse.py','inverse_sha256'),('DERIVATION.txt','derivation_sha256'),('PINS.json','pins_sha256')]
 for n,k in files:ck(sha(ROOT/n)==term[k],'TERMINAL:'+n)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 old=auth('20261027_FINITE_INVERSE_LAPSE24/RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');halves=auth('20261027_NINTH_THREE_QUARTER_TAIL/RESULT.json');result=read(ROOT/'RESULT.json')
 review=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/NINTH_THREE_QUARTER_TAIL_AUDIT.json');ck(review['PASS'] and review['producer_terminal']==sha(BASE/'20261027_NINTH_THREE_QUARTER_TAIL/TERMINAL.json'),'HALF_AUDIT')
 prior=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json');fixed=auth('20261027_FINAL_FIXED_GRID_CERTIFICATE/RESULT.json')
 base=prior['arms']['both']['constants'];constants=dict(R=base['physical_radius'],seed=base['seed'],K=base['K'],Y=base['aggregate_bound'],JC=dp['global_departure']['coefficient_tail_sup'])
 weights=[fixed['selected']['refined'][k] for k in ('graph_weight','oscillator_weight')]
 ck(result['constants']==constants==halves['constants'] and result['weights']==weights==halves['weights'],'SAME_DOMAIN')
 R,JC=Q(constants['R']),Q(constants['JC']);lam=Q(weights[0]);gap=Q(old['constants']['gap'])
 ck(old['degree']==24 and Q(old['constants']['radius'])==R and Q(old['constants']['graph_weight'])==lam and old['constants']['rate_ceiling']=='1/32' and gap>0,'INVERSE_DOMAIN')
 series={k:list(map(Q,v)) for k,v in old['series'].items()};z=list(map(Q,raw['majorant']))
 ck(len(z)==25 and all(len(v)==25 and all(x>=0 for x in v) for v in series.values()),'PREFIX_SIZE_SIGN')
 ck(series['B']==[Q(0)]+[z[n]/n**2 for n in range(1,25)],'B_NORMALIZATION')
 ck(series['X']==[Q(0),Q(0)]+[lam*z[n]/n**3 for n in range(2,25)],'X_NORMALIZATION')
 ck(series['Jhat'][0]==1,'RAW_CONSTANT')
 # The entire raw composition prefix was independently qualified previously.
 finiteaudit=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/FINITE_INVERSE24_AUDIT.json');ck(finiteaudit['PASS'],'RAW_COMPOSITION_AUDIT')
 oldhalf=auth('20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION/RESULT.json');ck(result['points']['1/2']==oldhalf['points']['1/2'],'EXACT_HALF_REPLAY')
 declared=read(ROOT/'PINS.json');ck(declared['tail_terminal']==review['producer_terminal'] and declared['tail_audit']==sha(BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/NINTH_THREE_QUARTER_TAIL_AUDIT.json'),'DECLARED_PINS')
 ck(set(result['points'])=={'1/2','3/4'},'FIXED_POINTS');points={};pins={}
 for q in (Q(1,2),Q(3,4)):
  row=result['points'][str(q)];cp=ROOT/('POINT_'+str(q.denominator)+'.json');ck(read(cp)==row,'POINT_RECORD');pins[str(cp)]=sha(cp);a=R*q
  tr=halves['points'][str(q)];ck(Q(tr['eta'])==a and row['q']==str(q) and row['eta']==str(a),'SAME_POINT')
  delta=iv(tr['values']['delta']);vals=row['values'];v={k:iv(x) for k,x in vals.items()}
  contains(vals['B'],I(poly(series['B'],a))+delta/625,'B')
  contains(vals['X'],I(poly(series['X'],a))+lam*delta/15625,'X')
  contains(vals['EulerX'],I(poly([n*x for n,x in enumerate(series['X'])],a))+lam*delta/625,'EULER_X')
  contains(vals['U'],4*v['X']/gap,'U');ck(0<=v['U'].lo<=v['U'].hi<1,'BACKGROUND_DOMAIN')
  contains(vals['Ehat'],1+64*v['U']/(1-v['U']),'EHAT')
  contains(vals['expB'],expbounds(v['B']),'EXP_B');contains(vals['exp2B'],expbounds(2*v['B']),'EXP_2B')
  contains(vals['Vhat'],v['Ehat']*v['exp2B']*v['EulerX']/32,'VHAT');ck(0<=v['Vhat'].lo<=v['Vhat'].hi<1,'VELOCITY_DOMAIN')
  contains(vals['Jhat'],v['Ehat']*v['expB']/(1-v['Vhat']*v['Vhat']),'JHAT')
  contains(vals['prefix'],I(poly(series['Jhat'],a)),'ORIGINAL_PREFIX')
  contains(vals['difference'],v['Jhat']-v['prefix'],'DIFFERENCE');ck(v['difference'].hi>=0,'POSITIVE_UPPER')
  new=v['difference'].hi;fallback=JC*q**25/(1-q)
  ck(Q(row['new_tail'])==new and Q(row['old_tail'])==fallback and Q(row['selected_tail'])==min(new,fallback),'TAIL_AND_SELECTION')
  points[str(q)]=dict(eta=float(a),new_tail=float(new),old_tail=float(fallback),selected_tail=float(min(new,fallback)),U_upper=float(v['U'].hi),velocity_upper=float(v['Vhat'].hi))
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for p,h in pins.items():ck(sha(p)==h,'POST_POINT:'+p)
 for n,k in files:ck(sha(ROOT/n)==term[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),points=points,scope='Independent exact endpoint interval composition, exponential positive remainder, single-wall normalization, original prefix subtraction, denominator gates and fallback minima. Raw Jhat prefix and all-order composition/source domination inherited from independently qualified same-family records; not a new full-clock certificate or PDE solution.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'NINTH_THREE_QUARTER_INVERSE_TAIL_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('positive_tail_review',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)

