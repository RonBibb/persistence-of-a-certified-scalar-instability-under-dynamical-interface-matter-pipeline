"""Immutable ninth wall replay plus independent manual Taylor/boost review.

This is not a second independently generated nonlinear wall source oracle.
The exact spatial jets remain formal until a separately audited qualification.
"""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_NINTH_WALL_QUALIFICATION';CUTOFF=1793121042;COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def load(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 files=[('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('wall.py','wall_sha256'),('DERIVATION.txt','derivation_sha256'),('PINS.json','pins_sha256')]
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 pins=read(ROOT/'PINS.json');bp=BASE/'20261027_NINTH_BULK_QUALIFICATION_R2/TERMINAL.json';ap=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/NINTH_BULK_AUDIT_R2.json'
 ck(bound.get(str(ROOT/'PINS.json'))==sha(ROOT/'PINS.json'),'PINS_BINDING')
 ck(bound.get(str(bp))==sha(bp)==pins['bulk_terminal'] and bound.get(str(ap))==sha(ap)==pins['bulk_audit'],'BULK_PINS')
 ba=read(ap);ck(read(bp)['pass_status'] and ba['PASS'] and ba['producer_terminal']==pins['bulk_terminal'],'BULK_AUDIT_MATCH')
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py';oldpath=BASE/'20261027_EIGHTH_WALL_QUALIFICATION/wall.py'
 for p in (ringpath,oldpath,ROOT/'wall.py'):ck(bound.get(str(p))==sha(p),'IMPORT_AUTH')
 oldauditpath=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT/EIGHTH_WALL_AUDIT.json';ck(bound.get(str(oldauditpath))==sha(oldauditpath),'EIGHTH_AUDIT_AUTH')
 oldaudit=read(oldauditpath);ck(oldaudit['PASS'] and oldaudit['producer_terminal']==sha(BASE/'20261027_EIGHTH_WALL_QUALIFICATION/TERMINAL.json'),'EIGHTH_AUDIT_MATCH')
 ring=load('ninth_wall_review_ring',ringpath);old=load('ninth_wall_review_old',oldpath);new=load('ninth_wall_review_new',ROOT/'wall.py')
 replay=new.qualify(ring,old);saved=read(ROOT/'RESULT.json');expected={k:v for k,v in saved.items() if k!='seconds'}
 ck(isinstance(replay['variables'],tuple) and isinstance(expected['variables'],list),'JSON_VARIABLES_CONTAINER')
 ck({k:v for k,v in replay.items() if k!='variables'}=={k:v for k,v in expected.items() if k!='variables'},'ONLY_VARIABLE_CONTAINER_DIFFERS')
 ck(list(replay['variables'])==expected['variables'],'EXACT_VARIABLE_SEQUENCE');ck(json.loads(json.dumps(replay))==expected,'EXACT_JSON_REPLAY')
 required={f'EIGHTH_REPLAY:{sg}:{row}:{n}' for sg in (-1,1) for row in ('O','J','graph','pwall','bwall','deltaPhi','normal','v') for n in range(9)}
 required|={f'{row}:{sg}' for sg in (-1,1) for row in ('NEW_OSCILLATOR','NEW_SCALAR','NEW_GRAPH','ELIMINATED_ROBIN','BOOST_CONVOLUTION','QUARTIC_BOOST','QUARTIC_BOOST_OMISSION_DETECTED','FIRST_JET7','SECOND_JET5','THIRD_JET3','THIRD_TRACE3','THIRD_RADIAL3','FOURTH_METRIC1','FOURTH_RADIAL1','FOURTH_SCALAR1')}
 required|={f'LOWER_ONLY:{sg}:{row}:{v}' for sg in (-1,1) for row in ('O','J','I') for v in ('p9','f9','g9','chi9','xi9','c9')}
 ck(required==set(saved['checks']) and len(required)==len(saved['checks']),'EXPLICIT_CONTROL_COVERAGE');ck(set(saved['orientations'])=={'-1','1'},'BOTH_ORIENTATIONS')
 # An independently expanded order9 quartic-boost identity:
 # 3/8 [A*v^4]_9 =3/8(A1*v2^4 +4*A0*v2^3*v3).
 names=('a0','a1','v2','v3');ring.NAMES=names;ring.N=4;ring.ZERO=(0,)*4
 A0,A1,V2,V3=[ring.variable(j) for j in range(4)];zero=ring.P(0)
 coeff=[zero,zero,V2,V3]+[zero]*6
 square=[sum((coeff[j]*coeff[n-j] for j in range(n+1)),zero) for n in range(10)]
 fourth=[sum((square[j]*square[n-j] for j in range(n+1)),zero) for n in range(10)]
 ck((3*(A0*fourth[9]+A1*fourth[8])/8-3*(A1*V2**4+4*A0*V2**3*V3)/8).iszero(),'INDEPENDENT_QUARTIC_BOOST9_COMBINATORICS')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 for f,k in files:ck(sha(ROOT/f)==terminal[k],'POST_TERMINAL:'+f)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,qualifier_controls=len(saved['checks']),producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),scope='Immutable binding and exact replay of source-reviewed ninth moving-wall qualifier; independent manual Taylor/fixed-time derivative review and separate quartic-boost9 coefficient convolution. Not a second nonlinear wall PDE extraction. Formal higher spatial jets await qualification/enclosure; no ninth field solve or distance coefficient.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'NINTH_WALL_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<CUTOFF-600,'LINUX_CUTOFF');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('ninth_wall_review_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<CUTOFF-600,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600);report=main();ck(sha(__file__)==pin,'AUDITOR_UNCHANGED')
 except BaseException as e:report=dict(PASS=False,error=repr(e),traceback=traceback.format_exc(),checks=COUNT)
 finally:
  signal.alarm(0)
  if lease:
   for handle in lease.handles:handle.close()
 report.update(audit_source_sha256=pin,seconds=time.time()-start)
 with dest.open('x') as f:json.dump(report,f,indent=2);f.flush();os.fsync(f.fileno())
 os.chmod(dest,0o444);print(json.dumps(report),flush=True)
 if not report['PASS']:raise SystemExit(1)
