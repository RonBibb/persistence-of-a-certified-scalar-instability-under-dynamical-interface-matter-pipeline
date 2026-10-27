"""Independent ordinary-Fraction full d8 budget audit; no producer imports."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_ACTUAL_EIGHTH_FULL_BUDGET';CUTOFF=1793112729;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ss(d):return {str(k):str(v) for k,v in d.items()}
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def pair(x):
 y=tuple(map(Q,x['exact_bounds'] if isinstance(x,dict) else x));ck(len(y)==2 and y[0]<=y[1],'INTERVAL_ORDER');return y
def add(x,y):return x[0]+y[0],x[1]+y[1]
def mul(x,y):
 z=[a*b for a in x for b in y];return min(z),max(z)
def times(x,n):return mul(x,(Q(n),Q(n)))
def ab(x):return max(abs(x[0]),abs(x[1]))
def packed(x):return list(map(str,x))
def main():
 term=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(term['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]
 for n,k in files:ck(sha(ROOT/n)==term[k],'TERMINAL:'+n)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 prior=auth('20261027_ACTUAL_SEVENTH_CLOCK_CERTIFICATE/RESULT.json');oldbr=auth('20261027_UNIFORM_POSITIVE_TAIL_BRACKET/RESULT.json');raw=auth('20261027_DEGREE24_DISTANCE_MAJORANT/RESULT.json');tails=auth('20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY/RESULT.json');inv=auth('20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION/RESULT.json');half=auth('20261027_POSITIVE_TAIL_HALF_RADIUS_READOUT/RESULT.json');result=read(ROOT/'RESULT.json')
 for folder,name in [('20261027_UNIFORM_POSITIVE_TAIL_BRACKET','UNIFORM_POSITIVE_TAIL_BRACKET_AUDIT'),('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE','EIGHTH_REAL_AUDIT'),('20261027_POSITIVE_TAIL_HALF_RADIUS_FEASIBILITY','POSITIVE_TAIL_HALF_RADIUS_AUDIT'),('20261027_POSITIVE_INVERSE_TAIL_QUALIFICATION','POSITIVE_INVERSE_TAIL_AUDIT')]:
  audit=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/'+name+'.json');ck(audit['PASS'] and audit['producer_terminal']==sha(BASE/folder/'TERMINAL.json'),'PARENT_AUDIT:'+name)
 actual=auth('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE/RESULT.json');clock=auth('20261026_GROWING_MODE_CLOCK_READOUT/RESULT.json');fourth=auth('20261027_ACTUAL_QUARTIC_CLOCK_CERTIFICATE/RESULT.json');fifth=auth('20261027_QUINTIC_REAL_SOURCE_ENCLOSURE/production_RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');seventh=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');ninth=auth('20261027_NINTH_CLOCK_ENCLOSURE/RESULT.json');dp=auth('20261027_DISTANCE16_LAPSE_DEPARTURE/RESULT.json')
 base={k:Q(v) for k,v in prior['arms']['both']['constants'].items()};R=base['physical_radius'];ck(Q(result['physical_radius'])==R,'UNCHANGED_RADIUS')
 def dic(k):return {int(n):Q(v) for n,v in prior[k].items()}
 D,E,C,F=map(dic,('new_distance24','inverse24','scalar_bounds','new_clock_bounds'));D16=dic('new_distance16')
 ck(set(D)==set(E)==set(range(1,25)) and set(F)==set(range(3,10)) and set(D16)==set(range(1,17)),'COVERAGE')
 ck(all(v>=0 for c in (D,D16,E,C,F) for v in c.values()),'POSITIVE_FINITE');ck(0<R<min(Q(1,512),Q(25,3840)),'OPENING_DOMAIN')
 star=tails['points']['1/2'];istar=inv['points']['1/2'];ck(Q(star['eta'])==Q(istar['eta'])==R/2,'STAR_IDENTITY')
 tb={k:Q(v) for k,v in star['bounds'].items()};jt=Q(istar['selected_tail']);ck(jt>=0 and all(v>=0 for v in tb.values()),'POSITIVE_TAILS')
 z=list(map(Q,raw['majorant']));kap=Q(tails['weights'][1]);ck(len(z)==25 and Q(tails['constants']['R'])==R,'SAME_NORM_DOMAIN')
 scalar={n:min(C[n],kap*z[n]/n**3) if n in C else kap*z[n]/n**3 for n in range(2,25)};ck(result['scalar_coefficients']==ss(scalar),'UNCHANGED_SCALAR_PREFIX')
 names={3:'cubic',4:'quartic',5:'quintic',6:'sixth',7:'seventh',8:'eighth',9:'ninth'}
 def evaluator(distance,coefficients):
  cross={}
  for n,d in distance.items():
   for m,e in E.items():
    if n+m>=10:cross[n+m]=cross.get(n+m,Q(0))+n*d*e
  def at(q):
   ck(0<q<=Q(1,2),'POINT_DOMAIN');a=R*q;factor=(2*q)**25
   unknownJ=jt*factor;efinite=sum(e*a**n for n,e in E.items());dfinite=sum(n*d*a**n for n,d in distance.items())
   parts=dict(finite_distance=sum((n-1)*distance[n]*a**n for n in range(10,25)),finite_cross=sum(v*a**n for n,v in cross.items()),unknown_distance=tb['euler_distance_tail']*factor*(1+efinite+unknownJ),unknown_lapse=dfinite*unknownJ)
   selected=dict(clock=sum(parts.values())/32,distance=sum(distance[n]*a**n for n in range(2,25))+tb['distance_tail']*factor,scalar=sum(v*a**n for n,v in scalar.items())+tb['scalar_tail']*factor,scalar_derivative=sum(n*v*a**n for n,v in scalar.items())+tb['scalar_euler_tail']*factor)
   costs={names[n]:v*a**n/(10*a*a) for n,v in coefficients.items()};costs['unknown_tail']=selected['clock']/(10*a*a)
   ratios=dict(clock=sum(costs.values()),distance=selected['distance']/(25*a),scalar=selected['scalar']/(a/40000),scalar_derivative=selected['scalar_derivative']/(a/40000));gates={k:v<=1 for k,v in ratios.items()};gates['opening']=a<Q(1,512) and Q(25,64)*a-60*a*a>0
   return dict(q=str(q),eta=str(a),selected=ss(selected),costs=ss(costs),ratios=ss(ratios),gates=gates,parts=ss(parts))
  return at
 baseline=evaluator(dict(D),dict(F));oldlo,oldhi=Q(1,4),Q(1,2);low,high=baseline(oldlo),baseline(oldhi)
 for k in ('selected','costs','ratios','gates'):ck(high[k]==half['points']['1/2'][k],'OLD_STAR:'+k)
 ck(oldbr['iterations']==16 and len(oldbr['checkpoints'])==16,'OLD_FIXED_COUNT')
 for step,row in enumerate(oldbr['checkpoints'],1):
  q=(oldlo+oldhi)/2;rec=baseline(q);passed=all(rec['gates'].values());ck(row['step']==step and row['record']==rec and row['passed']==passed,'OLD_MIDPOINT:'+str(step))
  if passed:oldlo,low=q,rec
  else:oldhi,high=q,rec
 ck(oldbr['lower']==low and oldbr['upper']==high and Q(oldbr['lower_q'])==oldlo and Q(oldbr['upper_q'])==oldhi,'OLD_FINAL_BRACKET')
 expectedbaseline=dict(lower=low,upper=high,star=baseline(Q(1,2)));ck(result['baseline']==expectedbaseline,'EXACT_BASELINE')
 oldF,oldD,oldD16=dict(F),dict(D),dict(D16);generic=list(map(Q,ninth['distance']));records={}
 for n in (8,9):
  records[str(n)]={};envelopes=[]
  for engine in ('primary','independent'):
   vals=clock['arms'][engine]['values'];ds={j:pair(vals['d'+str(j)]) for j in range(1,4)}
   ds.update({j:(-generic[j],generic[j]) for j in range(4,n+1)});ds[4]=pair(fourth['coefficient_intervals'][engine]['d4']);ds[5]=pair(fifth['arms'][engine]['bulk']['d5']);ds[6]=pair(sixth['arms'][engine]['bulk']['d6']);ds[7]=pair(seventh['arms'][engine]['bulk']['d7'])
   ei=[pair(v) for v in dp['inverse_intervals'][engine]];rate=pair(vals['rate'])
   def coefficient(distance):
    terms={j:times(mul(distance[j],ei[n-j]),j) for j in range(1,n)};leading=times(distance[n],n-1);total=leading
    for j in range(1,n):total=add(total,terms[j])
    termsout={'leading':packed(mul(rate,leading))};termsout.update({str(j):packed(mul(rate,terms[j])) for j in range(1,n)})
    return mul(rate,total),termsout
   before,beforeterms=coefficient(ds);savedold=prior['coefficient_records'][str(n)][engine];ck(packed(before)==savedold['new'] and ab(before)==Q(savedold['new_abs']),'OLD_F'+str(n)+':'+engine)
   ds[8]=pair(actual['arms'][engine]['bulk']['d8']);after,afterterms=coefficient(ds);envelopes.append(ab(after))
   records[str(n)][engine]=dict(old=packed(before),new=packed(after),old_abs=str(ab(before)),new_abs=str(ab(after)),old_terms=beforeterms,new_terms=afterterms)
  F[n]=min(oldF[n],max(envelopes))
 ck(records==result['coefficient_records'],'EXACT_F8_F9_RECORDS')
 d8=max(ab(pair(actual['arms'][engine]['bulk']['d8'])) for engine in ('primary','independent'));D[8]=min(D[8],d8);D16[8]=min(D16[8],d8)
 for key,value in [('old_clock_bounds',oldF),('new_clock_bounds',F),('old_distance16',oldD16),('new_distance16',D16),('old_distance24',oldD),('new_distance24',D)]:ck(result[key]==ss(value),'EXACT_BOUND_MAP:'+key)
 ck(Q(result['actual_d8_bound'])==d8,'ACTUAL_D8_ABS');ck(all(F[n]<=oldF[n] for n in F) and all(D[n]<=oldD[n] for n in D),'NONINCREASING_BOUNDS')
 at=evaluator(D,F);lo,hi=oldlo,Q(1,2);low,high=at(lo),at(hi);initialwidth=hi-lo;ck(all(low['gates'].values()),'RETAIN_OLD_ADMISSION')
 for k,v in low['ratios'].items():ck(Q(v)<=Q(expectedbaseline['lower']['ratios'][k]),'NO_WORSENING:'+k)
 previous=sha(ROOT/'BINDING.json');cpins={};domainpass=all(high['gates'].values())
 if domainpass:
  ck(result['classification']=='PREDECLARED_DOMAIN_ENDPOINT_ADMITTED' and result['iterations']==0 and result['checkpoints']==[],'DOMAIN_ONLY_CLASSIFICATION');lo=hi;low=high
 else:
  ck(result['classification']=='ACTUAL_EIGHTH_COMPLETE_CERTIFICATE_BRACKET' and result['iterations']==16 and len(result['checkpoints'])==16,'FIXED_COUNT_CLASSIFICATION')
  for step in range(1,17):
   q=(lo+hi)/2;rec=at(q);passed=all(rec['gates'].values());expected=dict(step=step,record=rec,passed=passed,predecessor_sha256=previous)
   cp=ROOT/('CHECKPOINT_'+str(step).zfill(2)+'.json');ck(read(cp)==expected and result['checkpoints'][step-1]==expected,'EXACT_CHECKPOINT:'+str(step));previous=sha(cp);cpins[str(cp)]=previous
   if passed:lo,low=q,rec
   else:hi,high=q,rec
  ck(hi-lo==initialwidth/2**16 and not all(high['gates'].values()),'EXACT_PASS_FAIL_WIDTH')
 ck(all(low['gates'].values()),'FINAL_ADMISSION');ck(result['lower']==low and result['upper']==high and result['lower_q']==str(lo) and result['upper_q']==str(hi) and result['width_q']==str(hi-lo),'FINAL_RECORDS')
 ck(Q(result['initial_width_q'])==initialwidth and result['last_checkpoint_sha256']==previous,'WIDTH_CHAIN')
 gain=Q(low['eta'])/Q(expectedbaseline['lower']['eta']);ck(Q(result['gain_exact'])==gain,'EXACT_GAIN')
 def display(row):return dict(eta=float(Q(row['eta'])),q=float(Q(row['q'])),ratios={k:float(Q(v)) for k,v in row['ratios'].items()},costs={k:float(Q(v)) for k,v in row['costs'].items()},normalized_tail_parts={k:float(Q(v)/(320*Q(row['eta'])**2)) for k,v in row['parts'].items()},gates=row['gates'])
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for p,h in cpins.items():ck(sha(p)==h,'POST_CHECKPOINT:'+p)
 for n,k in files:ck(sha(ROOT/n)==term[k],'POST_TERMINAL:'+n)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),gain_exact=str(gain),gain_display=float(gain),physical_radius=str(R),baseline=display(expectedbaseline['lower']),lower=display(low),upper=display(high),domain_endpoint_admitted=domainpass,scope='Independent exact interval F8/F9 convolution; ordinary Fraction positive finite convolution and all five gates; sealed old16 midpoint replay and new fixed16 bracket or domain-only endpoint. Original qualified tails, source coefficients and analytic-family premises inherited. No producer arithmetic imported, no new physical threshold or larger analytic radius.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'ACTUAL_EIGHTH_FULL_BUDGET_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');len(str(10**20000));lease=load('eighth_budget_review_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
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
