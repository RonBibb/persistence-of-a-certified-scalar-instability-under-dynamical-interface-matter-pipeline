"""STAGED: independent exact endpoint eighth audit; never imports producer flow.

Qualified source and wall expressions, and previously audited interval helpers,
are inherited. No new PDE extraction or eighth field profile is claimed.
Fresh authorized bounded window ends 2026-10-27 14:52:09 UTC.
"""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
ROOT=BASE/'20261027_EIGHTH_REAL_SOURCE_ENCLOSURE';CUTOFF=1793112729
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
# Reviewer-owned helper source is pinned in every report, not producer arithmetic.
HELPER=HERE/'seventh_real_audit.py';helper_pin=sha(HELPER)
a=load('eighth_review_exact_helpers',HELPER)
I,iv,ck,enclosed,poly=a.I,a.iv,a.ck,a.enclosed,a.polynomial
def extend(old,fc,p):
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h'];ck((8*r-h).lo>0,'TRACE8_POSITIVE')
 for k,c in [('p7','p7_bound'),('f7','f7_bound'),('g7','f7prime_bound')]:v[k]=I(-Q(fc[c]),Q(fc[c]))
 v.update(N8=r/(8*(8*r-h)),p8=I(0),f8=I(0),g8=I(0));return v
def conv(x,y,N):return [sum((x[j]*y[n-j] for j in range(n+1)),0) for n in range(N+1)]
def transport(E,Ep,Epp,x):
 return x[8]+sum((x[8-n]*E[n] for n in range(1,7)),0)+x[2]**2*Ep[4]/2+x[2]*x[3]*Ep[3]+(x[2]*x[4]+x[3]**2/2)*Ep[2]+(x[2]*x[5]+x[3]*x[4])*Ep[1]+x[2]**3*Epp[2]/6+x[2]**2*x[3]*Epp[1]/2
def qualify_transport(ring):
 names=tuple(['e'+str(n) for n in range(1,7)]+['d'+str(n) for n in range(1,5)]+['t1','t2']+['x'+str(n) for n in range(2,9)])
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(i) for i,k in enumerate(names)};z=ring.P(0)
 E=[ring.P(1)]+[v['e'+str(n)] for n in range(1,7)]+[z,z]
 Ep=[z]+[v['d'+str(n)] for n in range(1,5)]+[z]*4;Epp=[z,v['t1'],v['t2']]+[z]*6
 x={n:v['x'+str(n)] for n in range(2,9)};X=[z,z]+[x[n] for n in range(2,9)];X2=conv(X,X,8);X3=conv(X2,X,8)
 direct=conv(X,E,8)[8]+conv(X2,Ep,8)[8]/2+conv(X3,Epp,8)[8]/6
 ck((direct-transport(E,Ep,Epp,x)).iszero(),'INDEPENDENT_TRANSPORT8_CONVOLUTION')
 ck(not (direct-transport(E,Ep,Epp,x)+x[2]**3*Epp[2]/6).iszero(),'TRANSPORT8_MUTATION')
def endpoint(saved,old,fc,p,sigma,wall,qual,jets):
 v=extend(old['source_variables'],fc,p);w={k:iv(x) for k,x in old['inputs'].items()};q={k:iv(x) for k,x in old['quantities'].items()}
 for k,x in v.items():enclosed(saved['source_variables'][k],x,'ENDPOINT_VARIABLE:'+k)
 T,e,r,h=v['T'],v['e'],p['rate'],p['h'];ck(q['d7_wall'].lo>0,'INHERITED_WALL7_DIVISOR')
 updates=dict(p7=v['p7'],f7=v['f7'],g7=v['g7'],c7=q['c7'],xi7=q['xi7'],chi7=(v['f7']+T*q['xi7']-q['o7'])/q['d7_wall'])
 for k in ('u6','g6prime','c6prime','u4prime','g4second','c4second','u2second','g2third','c2third','Hppp','Tpppp'):
  updates[k]=poly(jets,v,k);enclosed(saved['jets'][k],updates[k],'QUALIFIED_JET:'+k)
 for k,x in updates.items():enclosed(saved['inputs'][k],x,'NEW_WALL_INPUT:'+k)
 for k in w:
  if k not in updates:ck(saved['inputs'][k]==old['inputs'][k],'UNCHANGED_WALL_INPUT:'+k)
 sw={k:iv(x) for k,x in saved['inputs'].items()};sv={k:iv(x) for k,x in saved['source_variables'].items()};sq=saved['quantities'];direct=wall.direct(sw,sigma)
 for k,row in [('o8','O'),('j8','J'),('qI8','graph')]:enclosed(sq[k],direct[row].a[8],'QUALIFIED_WALL_LOAD:'+k)
 for k in ('c8','Sc8'):enclosed(sq[k],poly(qual,sv,k),'WALL_SOURCE:'+k)
 div=8*sigma*e*r*(8*r-h);mu=-8*r*(8*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*a.square(T);dw=2-mu*e
 ck((div.lo>0 or div.hi<0) and J.lo>0 and D.lo>0 and dw.lo>0,'WALL8_POSITIVITY')
 for k,x in [('graph_divisor',div),('J8',J),('D8',D),('d8_wall',dw)]:enclosed(sq[k],x,'WALL_DIVISOR:'+k)
 enclosed(sq['xi8'],-iv(sq['qI8'])/iv(sq['graph_divisor']),'XI8')
 xi=iv(sq['xi8']);gamma=21-I(1)/iv(sq['d8_wall']);R=2*sigma*(T*iv(sq['c8'])-w['Tp']*xi-iv(sq['j8']))+gamma*T*xi+iv(sq['o8'])/iv(sq['d8_wall'])
 enclosed(sq['R8'],R,'R8');enclosed(sq['robin'],-iv(sq['D8'])*iv(sq['R8'])/(2*iv(sq['J8']))+2*sigma*T*iv(sq['Sc8'])/iv(sq['J8']),'ROBIN8')
 bs=[I(0),-2*sw['p1']]+[sw['c'+str(n)]-2*sw['p'+str(n)] for n in range(2,7)]
 E=a.expcoeff(bs,6)+[I(0),I(0)];bp=[I(0),-2*sw['u1']]+[sw['c'+str(n)+'prime']-2*sw['u'+str(n)] for n in range(2,5)]+[I(0)]*4
 bpp=[I(0),-2*sw['u1prime'],sw['c2second']-2*sw['u2prime']]+[I(0)]*6
 Ep=conv(E,bp,8);Epp=conv(E,[x+y for x,y in zip(bpp,conv(bp,bp,8))],8);xs={n:sw['xi'+str(n)] for n in range(2,8)};xs[8]=xi
 enclosed(sq['transport'],transport(E,Ep,Epp,xs),'IDENTITY_QUALIFIED_TRANSPORT8')
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('DERIVATION.txt','derivation_sha256'),('TRANSPORT_QUALIFICATION.json','transport_sha256')]:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 def module(n,path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'MODULE_AUTH:'+path);return load(n,p)
 ring=module('eighth_audit_ring','20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py');qualify_transport(ring)
 cubic=module('eighth_audit_cubic','20261026_GROWING_MODE_CUBIC_FLOW/sources.py');quartic=module('eighth_audit_quartic','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall=module('eighth_audit_wall','20261027_EIGHTH_WALL_QUALIFICATION/wall.py')
 qual=auth('20261027_EIGHTH_BULK_QUALIFICATION_R1/RESULT.json');jets=auth('20261027_EIGHTH_JET_QUALIFICATION/RESULT.json');globaldata=auth('20261027_QUINTIC_GLOBAL_BULK_PROBE/RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');seventh=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');inverse=auth('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json')
 ck(qual['pass_status'] and jets['pass_status'] and inverse['scientific_certificate'],'QUALIFICATIONS')
 for n in ('EIGHTH_BULK_AUDIT_R1','EIGHTH_WALL_AUDIT','EIGHTH_JET_AUDIT','SEVENTH_REAL_AUDIT','SIXTH_REAL_AUDIT_R1'):ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/'+n+'.json')['PASS'],'INHERITED_AUDIT:'+n)
 ck(auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/SEVENTH_REAL_AUDIT.json')['audit_source_sha256']==helper_pin,'AUDITED_HELPER_IDENTITY')
 ck(read(ROOT/'TRANSPORT_QUALIFICATION.json')['pass_status'],'PRODUCER_TRANSPORT_PASS')
 result=read(ROOT/'RESULT.json');reports={}
 for engine in ('primary','independent'):
  arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');old=seventh['arms'][engine];saved=result['arms'][engine]
  ck(read(ROOT/('ARM_'+engine+'.json'))==saved,'ARM_COPY');ck(arm['D']==initial['D'],'DOMAIN')
  for k,x in initial['parameters'].items():ck(arm['parameters'][k]==x,'PARAMETER:'+k)
  p={k:iv(x) for k,x in arm['parameters'].items()};v=extend(old['source_variables'],old['constants'],p)
  for k,x in v.items():enclosed(saved['source_variables'][k],x,'GLOBAL_VARIABLE:'+k)
  for k in ('c8','Sp8','Sc8','Sg8'):enclosed(saved['sources'][k],poly(qual,v,k),'GLOBAL_SOURCE:'+k)
  H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];r,h,m=p['rate'],p['h'],p['m2'];mu=-8*r*(8*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*a.square(T);B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;sb=saved['bulk'];src={k:iv(x) for k,x in saved['sources'].items()}
  ck(J.lo>0 and D.lo>0,'GLOBAL8_POSITIVITY')
  for k,x in [('J8',J),('D8',D),('B0',B),('Tp',Tp)]:enclosed(sb[k],x,'GLOBAL_QUANTITY:'+k)
  enclosed(sb['forcing'],src['Sg8']+B*src['Sc8']/D,'FORCING8')
  for side,sg in [('lower',1),('upper',-1)]:endpoint(saved['walls'][side],old['walls'][side],old['constants'],p,sg,wall,qual,jets)
  cf=Q(inverse['arms'][engine]['finite_orders']['8']['constant'])*Q(inverse['arms'][engine]['f_transfer_multiplier']);G=max(iv(w['quantities']['robin']).abs() for w in saved['walls'].values());size=iv(sb['forcing']).abs()+8*G;fb=cf*size/64;gb=cf*size/8;pb=(src['Sc8'].abs()+T.abs()*gb+iv(sb['Tp']).abs()*fb)/iv(sb['D8']).lo;length=I(*arm['D']);metric=2*length.hi*pb
  ck(cf>0 and length.lo>0,'INVERSE_DOMAIN')
  for k,x in dict(Cf8=cf,Robin_abs=G,source_size=size,f8_bound=fb,f8prime_bound=gb,p8_bound=pb,metric_integral_bound=metric).items():ck(Q(saved['constants'][k])==x,'EXACT_INVERSE:'+k)
  s3,s4=a.lower(v,p,cubic,quartic);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f'])
  bs=[I(0),-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],iv(globaldata['arms'][engine]['sources']['c5'])-2*v['p5'],iv(sixth['arms'][engine]['sources']['c6'])-2*v['p6'],iv(old['sources']['c7'])-2*v['p7'],src['c8']]
  enclosed(sb['density'],a.expcoeff(bs,8)[8],'DENSITY8');enclosed(sb['integral'],iv(sb['density'])*length,'INTEGRAL8')
  known=iv(saved['walls']['upper']['quantities']['transport'])-iv(saved['walls']['lower']['quantities']['transport'])+iv(sb['integral']);enclosed(sb['known'],known,'KNOWN8');enclosed(sb['d8'],iv(sb['known'])+I(-metric,metric),'DISTANCE8')
  reports[engine]=dict(d8_display=[float(iv(sb['d8']).lo),float(iv(sb['d8']).hi)],source_size_display=float(size))
 vals=[iv(result['arms'][e]['bulk']['d8']) for e in ('primary','independent')];ck(max(x.lo for x in vals)<=min(x.hi for x in vals),'COMPATIBILITY_ONLY');enclosed(result['d8'],I(min(x.lo for x in vals),max(x.hi for x in vals)),'FINAL_HULL')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin and sha(HELPER)==helper_pin,'SOURCE_TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=a.COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=reports,helper_source_sha256=helper_pin,scope='Independent exact interval arithmetic for qualified expanded 11 jets, sources, wall loads, finite-n8 inverse and distance. Transport8 independently checked by coefficient convolution. Source/wall formulas and lower-order certificates inherited; no producer flow import, no new PDE oracle or eighth profile/sign.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=HERE/'EIGHTH_REAL_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('eighth_audit_lease',lp);lease.ROOT=HERE;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=a.COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
