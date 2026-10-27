"""Independent exact-interval ninth coefficient audit; producer flow not imported.

Qualified expanded sources/wall formulas and inherited lower enclosures remain
explicit premises. Independent transport coefficient convolution is included.
"""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;ROOT=BASE/'20261027_NINTH_REAL_SOURCE_ENCLOSURE';CUTOFF=1793121042
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
HELPER=HERE/'eighth_real_audit.py';helper_pin=sha(HELPER);a=load('ninth_exact_interval_helpers',HELPER)
I,iv,ck,enclosed,poly=a.I,a.iv,a.ck,a.enclosed,a.poly
def extend(old,fc,p):
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h'];ck((9*r-h).lo>0,'TRACE9_POSITIVE')
 for k,c in [('p8','p8_bound'),('f8','f8_bound'),('g8','f8prime_bound')]:v[k]=I(-Q(fc[c]),Q(fc[c]))
 v.update(N9=r/(9*(9*r-h)),p9=I(0),f9=I(0),g9=I(0));return v
def conv(x,y,N):return [sum((x[j]*y[n-j] for j in range(n+1)),0) for n in range(N+1)]
def transport(E,Ep,Epp,Eppp,x):
 out=x[9]+sum((x[9-n]*E[n] for n in range(1,8)),0)
 for n in range(1,6):out+=Ep[n]*sum((x[i]*x[9-n-i] for i in range(2,8) if 2<=9-n-i<=8),0)/2
 for n in range(1,4):out+=Epp[n]*sum((x[i]*x[j]*x[9-n-i-j] for i in range(2,8) for j in range(2,8) if 2<=9-n-i-j<=8),0)/6
 return out+Eppp[1]*x[2]**4/24
def qualify_transport(ring):
 names=tuple(['e'+str(n) for n in range(1,8)]+['d'+str(n) for n in range(1,6)]+['t'+str(n) for n in range(1,4)]+['u1']+['x'+str(n) for n in range(2,10)])
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(i) for i,k in enumerate(names)};z=ring.P(0)
 E=[ring.P(1)]+[v['e'+str(n)] for n in range(1,8)]+[z,z];Ep=[z]+[v['d'+str(n)] for n in range(1,6)]+[z]*4;Epp=[z]+[v['t'+str(n)] for n in range(1,4)]+[z]*6;Eppp=[z,v['u1']]+[z]*8
 x={n:v['x'+str(n)] for n in range(2,10)};X=[z,z]+[x[n] for n in range(2,10)];X2=conv(X,X,9);X3=conv(X2,X,9);X4=conv(X2,X2,9)
 direct=conv(X,E,9)[9]+conv(X2,Ep,9)[9]/2+conv(X3,Epp,9)[9]/6+conv(X4,Eppp,9)[9]/24
 ck((direct-transport(E,Ep,Epp,Eppp,x)).iszero(),'INDEPENDENT_TRANSPORT9_CONVOLUTION')
 expanded=x[9]+sum((x[9-n]*E[n] for n in range(1,8)),z)+Ep[5]*x[2]**2/2+Ep[4]*x[2]*x[3]+Ep[3]*(x[2]*x[4]+x[3]**2/2)+Ep[2]*(x[2]*x[5]+x[3]*x[4])+Ep[1]*(x[2]*x[6]+x[3]*x[5]+x[4]**2/2)+Epp[3]*x[2]**3/6+Epp[2]*x[2]**2*x[3]/2+Epp[1]*(x[2]**2*x[4]+x[2]*x[3]**2)/2+Eppp[1]*x[2]**4/24
 ck((direct-expanded).iszero(),'EXPLICIT_TRANSPORT9_PARTITIONS')
 ck(not (direct-expanded-Eppp[1]*x[2]**4/24).iszero(),'FOURTH_SHIFT_MUTATION')
def endpoint(saved,old,fc,p,sigma,wall,qual,jets):
 v=extend(old['source_variables'],fc,p);w={k:iv(x) for k,x in old['inputs'].items()};q={k:iv(x) for k,x in old['quantities'].items()}
 for k,x in v.items():enclosed(saved['source_variables'][k],x,'ENDPOINT_VARIABLE:'+k)
 T,e,r,h=v['T'],v['e'],p['rate'],p['h'];ck(q['d8_wall'].lo>0,'INHERITED_WALL8_DIVISOR')
 updates=dict(p8=v['p8'],f8=v['f8'],g8=v['g8'],c8=q['c8'],xi8=q['xi8'],chi8=(v['f8']+T*q['xi8']-q['o8'])/q['d8_wall'])
 for k in ('u7','g7prime','c7prime','u5prime','g5second','c5second','u3second','g3third','c3third','u1third','g1fourth'):
  updates[k]=poly(jets,v,k);enclosed(saved['jets'][k],updates[k],'QUALIFIED_JET:'+k)
 for k,x in updates.items():enclosed(saved['inputs'][k],x,'NEW_WALL_INPUT:'+k)
 for k in w:
  if k not in updates:ck(saved['inputs'][k]==old['inputs'][k],'UNCHANGED_WALL_INPUT:'+k)
 sw={k:iv(x) for k,x in saved['inputs'].items()};sv={k:iv(x) for k,x in saved['source_variables'].items()};sq=saved['quantities'];direct=wall.direct(sw,sigma)
 for k,row in [('o9','O'),('j9','J'),('qI9','graph')]:enclosed(sq[k],direct[row].a[9],'QUALIFIED_WALL_LOAD:'+k)
 for k in ('c9','Sc9'):enclosed(sq[k],poly(qual,sv,k),'WALL_SOURCE:'+k)
 div=9*sigma*e*r*(9*r-h);mu=-9*r*(9*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*a.a.square(T);dw=2-mu*e
 ck((div.lo>0 or div.hi<0) and J.lo>0 and D.lo>0 and dw.lo>0,'WALL9_POSITIVITY')
 for k,x in [('graph_divisor',div),('J9',J),('D9',D),('d9_wall',dw)]:enclosed(sq[k],x,'WALL_DIVISOR:'+k)
 enclosed(sq['xi9'],-iv(sq['qI9'])/iv(sq['graph_divisor']),'XI9')
 xi=iv(sq['xi9']);gamma=21-I(1)/iv(sq['d9_wall']);R=2*sigma*(T*iv(sq['c9'])-w['Tp']*xi-iv(sq['j9']))+gamma*T*xi+iv(sq['o9'])/iv(sq['d9_wall'])
 enclosed(sq['R9'],R,'R9');enclosed(sq['robin'],-iv(sq['D9'])*iv(sq['R9'])/(2*iv(sq['J9']))+2*sigma*T*iv(sq['Sc9'])/iv(sq['J9']),'ROBIN9')
 bs=[I(0),-2*sw['p1']]+[sw['c'+str(n)]-2*sw['p'+str(n)] for n in range(2,8)];E=a.a.expcoeff(bs,7)+[I(0),I(0)]
 bp=[I(0),-2*sw['u1']]+[sw['c'+str(n)+'prime']-2*sw['u'+str(n)] for n in range(2,6)]+[I(0)]*4
 bpp=[I(0),-2*sw['u1prime']]+[sw['c'+str(n)+'second']-2*sw['u'+str(n)+'prime'] for n in range(2,4)]+[I(0)]*6
 bppp=[I(0),-2*sw['u1second']]+[I(0)]*8;bp2=conv(bp,bp,9)
 Ep=conv(E,bp,9);Epp=conv(E,[x+y for x,y in zip(bpp,bp2)],9)
 mixed=conv([3*x for x in bp],bpp,9);cube=conv(bp2,bp,9);Eppp=conv(E,[x+y+z for x,y,z in zip(bppp,mixed,cube)],9)
 xs={n:sw['xi'+str(n)] for n in range(2,9)};xs[9]=xi
 enclosed(sq['transport'],transport(E,Ep,Epp,Eppp,xs),'IDENTITY_QUALIFIED_TRANSPORT9')
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('flow.py','flow_sha256'),('DERIVATION.txt','derivation_sha256'),('TRANSPORT_QUALIFICATION.json','transport_sha256'),('PINS.json','pins_sha256')]
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 def auth(n):
  p=BASE/n;ck(bound.get(str(p))==sha(p),'AUTH:'+n);return read(p)
 def module(n,path):
  p=BASE/path;ck(bound.get(str(p))==sha(p),'MODULE_AUTH:'+path);return load(n,p)
 pins=read(ROOT/'PINS.json')
 for kind,folder,name in [('bulk','20261027_NINTH_BULK_QUALIFICATION_R2','NINTH_BULK_AUDIT_R2'),('wall','20261027_NINTH_WALL_QUALIFICATION','NINTH_WALL_AUDIT'),('jet','20261027_NINTH_JET_QUALIFICATION','NINTH_JET_AUDIT')]:
  audit=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/'+name+'.json');ck(audit['PASS'] and audit['producer_terminal']==pins[kind+'_terminal']==sha(BASE/folder/'TERMINAL.json'),'AUDIT_TERMINAL:'+kind);ck(sha(BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'/(name+'.json'))==pins[kind+'_audit'],'AUDIT_PIN:'+kind)
 pa=auth('20261027_QUARTIC_REAL_SOURCE_AUDIT/EIGHTH_REAL_AUDIT.json');ck(pa['PASS'] and pa['audit_source_sha256']==helper_pin,'AUTHENTICATED_INTERVAL_HELPER');ck(pa['helper_source_sha256']==sha(a.HELPER),'AUTHENTICATED_NESTED_HELPER')
 ring=module('ninth_audit_ring','20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py');qualify_transport(ring)
 cubic=module('ninth_audit_cubic','20261026_GROWING_MODE_CUBIC_FLOW/sources.py');quartic=module('ninth_audit_quartic','20261027_QUARTIC_BULK_QUALIFICATION_R2/sources.py');wall=module('ninth_audit_wall','20261027_NINTH_WALL_QUALIFICATION/wall.py')
 qual=auth('20261027_NINTH_BULK_QUALIFICATION_R2/RESULT.json');jets=auth('20261027_NINTH_JET_QUALIFICATION/RESULT.json');globaldata=auth('20261027_QUINTIC_GLOBAL_BULK_PROBE/RESULT.json');sixth=auth('20261027_SIXTH_REAL_SOURCE_ENCLOSURE/RESULT.json');seventh=auth('20261027_SEVENTH_REAL_SOURCE_ENCLOSURE/RESULT.json');eighth=auth('20261027_EIGHTH_REAL_SOURCE_ENCLOSURE/RESULT.json');inverse=auth('20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/RESULT.json')
 ck(qual['pass_status'] and jets['pass_status'] and inverse['scientific_certificate'],'QUALIFICATIONS');ck(pa['producer_terminal']==sha(BASE/'20261027_EIGHTH_REAL_SOURCE_ENCLOSURE/TERMINAL.json'),'EIGHTH_AUDIT_MATCH')
 result=read(ROOT/'RESULT.json');reports={}
 for engine in ('primary','independent'):
  arm=auth('20261027_QUARTIC_REAL_SOURCE_ENCLOSURE/ARM_'+engine+'.json');initial=auth('20261026_GROWING_INVERSE_READINESS_R1/INITIAL_'+engine+'.json');old=eighth['arms'][engine];saved=result['arms'][engine]
  ck(read(ROOT/('ARM_'+engine+'.json'))==saved,'ARM_COPY');ck(arm['D']==initial['D'],'DOMAIN')
  for k,x in initial['parameters'].items():ck(arm['parameters'][k]==x,'PARAMETER:'+k)
  p={k:iv(x) for k,x in arm['parameters'].items()};v=extend(old['source_variables'],old['constants'],p)
  for k,x in v.items():enclosed(saved['source_variables'][k],x,'GLOBAL_VARIABLE:'+k)
  for k in ('c9','Sp9','Sc9','Sg9'):enclosed(saved['sources'][k],poly(qual,v,k),'GLOBAL_SOURCE:'+k)
  H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];r,h,m=p['rate'],p['h'],p['m2'];mu=-9*r*(9*r+3*h);J=-3*(mu+4*p['k'])*e;D=J+2*a.a.square(T);B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;sb=saved['bulk'];src={k:iv(x) for k,x in saved['sources'].items()}
  ck(J.lo>0 and D.lo>0,'GLOBAL9_POSITIVITY')
  for k,x in [('J9',J),('D9',D),('B0',B),('Tp',Tp)]:enclosed(sb[k],x,'GLOBAL_QUANTITY:'+k)
  enclosed(sb['forcing'],src['Sg9']+B*src['Sc9']/D,'FORCING9')
  for side,sg in [('lower',1),('upper',-1)]:endpoint(saved['walls'][side],old['walls'][side],old['constants'],p,sg,wall,qual,jets)
  cf=Q(inverse['arms'][engine]['finite_orders']['9']['constant'])*Q(inverse['arms'][engine]['f_transfer_multiplier']);G=max(iv(w['quantities']['robin']).abs() for w in saved['walls'].values());size=iv(sb['forcing']).abs()+9*G;fb=cf*size/81;gb=cf*size/9;pb=(src['Sc9'].abs()+T.abs()*gb+iv(sb['Tp']).abs()*fb)/iv(sb['D9']).lo;length=I(*arm['D']);metric=2*length.hi*pb
  ck(cf>0 and length.lo>0,'INVERSE_DOMAIN')
  for k,x in dict(Cf9=cf,Robin_abs=G,source_size=size,f9_bound=fb,f9prime_bound=gb,p9_bound=pb,metric_integral_bound=metric).items():ck(Q(saved['constants'][k])==x,'EXACT_INVERSE:'+k)
  s3,s4=a.a.lower(v,p,cubic,quartic);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f'])
  bs=[I(0),-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],iv(globaldata['arms'][engine]['sources']['c5'])-2*v['p5'],iv(sixth['arms'][engine]['sources']['c6'])-2*v['p6'],iv(seventh['arms'][engine]['sources']['c7'])-2*v['p7'],iv(old['sources']['c8'])-2*v['p8'],src['c9']]
  enclosed(sb['density'],a.a.expcoeff(bs,9)[9],'DENSITY9');enclosed(sb['integral'],iv(sb['density'])*length,'INTEGRAL9')
  known=iv(saved['walls']['upper']['quantities']['transport'])-iv(saved['walls']['lower']['quantities']['transport'])+iv(sb['integral']);enclosed(sb['known'],known,'KNOWN9');enclosed(sb['d9'],iv(sb['known'])+I(-metric,metric),'DISTANCE9')
  reports[engine]=dict(d9_display=[float(iv(sb['d9']).lo),float(iv(sb['d9']).hi)],source_size_display=float(size))
 vals=[iv(result['arms'][e]['bulk']['d9']) for e in ('primary','independent')];ck(max(x.lo for x in vals)<=min(x.hi for x in vals),'COMPATIBILITY_ONLY');enclosed(result['d9'],I(min(x.lo for x in vals),max(x.hi for x in vals)),'FINAL_HULL')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'POST_TERMINAL:'+f)
 ck(sha(ROOT/'TERMINAL.json')==pin and sha(HELPER)==helper_pin and sha(a.HELPER)==pa['helper_source_sha256'],'HELPERS_TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=a.a.COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=reports,helper_source_sha256=helper_pin,nested_helper_source_sha256=pa['helper_source_sha256'],scope='Independent exact interval arithmetic for qualified expanded11 jets, bulk and wall sources, finite-n9 inverse and distance. Independent transport9 convolution plus explicit partitions retains E1third*xi2fourth/24. Strict containment uses identity-qualified grouping; source/wall formulas and lower certificates inherited, no producer flow import or new PDE oracle. Unsigned d9 only, not a field profile or physical trajectory.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=HERE/'NINTH_REAL_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_WINDOW');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_real_audit_lease',lp);lease.ROOT=HERE;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_WINDOW')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=a.a.COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
