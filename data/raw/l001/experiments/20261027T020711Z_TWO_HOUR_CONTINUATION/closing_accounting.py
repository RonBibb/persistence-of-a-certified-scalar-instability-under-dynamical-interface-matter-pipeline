"""Read-only numerical packet inventory and cumulative certificate accounting; Linux only."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import json,hashlib,os,importlib.util,time
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def require(v,s):
 if not v:raise AssertionError(s)
def main():
 require(sys.platform=='linux','LINUX_ONLY')
 lp=BASE/'20261027_SHARED_ADMISSION/lease.py'
 require(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE')
 lease=load('summary_lease',lp);lease.ROOT=ROOT
 cpu,occupied=lease.acquire()
 try:
  actual={};records=[];prelaunch_failures=[]
  def check(p,h):
   p=Path(p)
   if str(p) not in actual:actual[str(p)]=sha(p)
   require(actual[str(p)]==h,'HASH:'+str(p))
  for p in sorted(BASE.glob('20261027_*')):
   if not p.is_dir() or p==ROOT:continue
   st=p/'START.json'
   if not st.exists():
    if (p/'FAILURE.json').exists():prelaunch_failures.append(dict(packet=p.name,failure=read(p/'FAILURE.json'),scope='date-prefix inventory; no START, no window-start assertion'))
    continue
   start=read(st)
   if not (1793066831<=start.get('time',0)<1793074031):continue
   rec=dict(packet=p.name,start=start)
   if (p/'TERMINAL.json').exists():
    t=read(p/'TERMINAL.json');require(t['pass_status'],'TERMINAL_PASS')
    for fn,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
     check(p/fn,t[key])
    binding=read(p/'BINDING.json')
    for group in ('inputs','sources','runtime'):
     for path,h in binding[group].items():check(path,h)
    result=read(p/'RESULT.json')
    rec.update(status='PRODUCER_PASS',terminal_sha256=sha(p/'TERMINAL.json'),result_sha256=t['result_sha256'],classification=result.get('classification'),gates=len(result.get('gates',{})),seconds=result.get('seconds'),review_present=(p/'REVIEW.txt').exists(),audit_exception=(p/'AUDIT_EXCEPTION.txt').read_text() if (p/'AUDIT_EXCEPTION.txt').exists() else None,certificates={})
    for lane,c in result.get('constants_exact',{}).items():
     if isinstance(c,dict) and 'physical_radius' in c:
      rec['certificates'][lane]={k:c[k] for k in ('physical_radius','clock_eta')}
    if 'physical_radius' in result.get('constants_exact',{}):
     rec['certificates']['constants_exact']={k:result['constants_exact'][k] for k in ('physical_radius','clock_eta')}
   elif (p/'FAILURE.json').exists():rec.update(status='TECHNICAL_INCOMPLETE',failure=read(p/'FAILURE.json'))
   else:rec.update(status='NO_TERMINAL')
   records.append(rec)
  original=BASE/'20261027_REAL_PAYMENT_MATCHED_CERTIFICATE'
  final=BASE/'20261027_FINAL_FIXED_GRID_CERTIFICATE'
  for p in (original,final):
   t=read(p/'TERMINAL.json')
   require(t['pass_status'],'ACCOUNTING_PASS')
   check(p/'RESULT.json',t['result_sha256'])
  first=read(original/'RESULT.json')
  last=read(final/'RESULT.json')
  initial_lane='constants_exact'
  init=first['constants_exact'];end=last['constants_exact']['refined']
  require('physical_radius' in init and 'clock_eta' in init,'FLAT_STARTING_CERTIFICATE')
  ratios={k:Q(end[k])/Q(init[k]) for k in ('physical_radius','clock_eta')}
  out=dict(time=time.time(),cpu=cpu,occupied=occupied,cutoff_unix=1793074031,unique_authenticated_files=len(actual),records=records,initial_packet=original.name,initial_lane=initial_lane,final_packet=final.name,initial=init,final=end,cumulative_ratios_exact={k:str(v) for k,v in ratios.items()},cumulative_ratios_display={k:float(v) for k,v in ratios.items()},final_display={k:float(Q(end[k])) for k in ('physical_radius','clock_eta')})
  out['prelaunch_failures']=prelaunch_failures
  out['final_selected']=last['selected']['refined']
  out['final_branches']=last['active_K_branches']['refined']
  out['final_budget_shares']={channel:{name:float(Q(value)/sum(map(Q,values.values()))) for name,value in values.items()} for channel,values in last['source_budgets']['refined'].items()}
  rho=Q(end['physical_radius']);eta=Q(end['clock_eta']);q=2*eta/rho
  MD=Q(end['observable_sup']);MF=Q(end['clock_sup']);Y=Q(end['aggregate_bound'])
  out['remainder_gate_ratios']={}
  for label,factor in [('accepted',1),('next_coarser_dyadic',2)]:
   qq=q*factor;ee=eta*factor;qd=qq/2
   require(0<qq<1,'REMAINDER_COMPARISON_DOMAIN')
   vals=dict(clock=(10000*ee**3+MF*qq**4/(1-qq))/(10*ee**2),distance=(MD*qd**2/(1-qd))/(25*ee),scalar=(Y*qd**2/(1-qd))/(ee/40000),scalar_derivative=(Y*qd**2*(2-qd)/(1-qd)**2)/(ee/40000))
   out['remainder_gate_ratios'][label]={k:dict(exact=str(v),display=float(v),passes=v<=1) for k,v in vals.items()}
  dest=ROOT/'CLOSING_INTEGRITY_AND_ACCOUNTING.json';tmp=ROOT/'CLOSING_INTEGRITY_AND_ACCOUNTING.json.tmp'
  with tmp.open('x') as f:json.dump(out,f,indent=2);f.flush();os.fsync(f.fileno())
  os.chmod(tmp,0o444);os.link(tmp,dest);tmp.unlink()
  print(json.dumps({k:out[k] for k in ('unique_authenticated_files','initial_lane','cumulative_ratios_display','final_display')}))
  print(json.dumps([dict(packet=r['packet'],status=r['status'],review_present=r.get('review_present')) for r in records]))
 finally:
  for h in lease.handles:h.close()
if __name__=='__main__':main()
