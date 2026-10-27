"""Source-reviewed moving-wall qualification replay and immutable record audit."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_QUINTIC_WALL_QUALIFICATION';COUNT=0
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
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('wall.py','wall_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 binding=read(ROOT/'BINDING.json');bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in binding[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py';oldpath=BASE/'20261027_QUARTIC_WALL_QUALIFICATION/wall.py'
 for p in (ringpath,oldpath,ROOT/'wall.py'):ck(bound.get(str(p))==sha(p),'IMPORT_AUTH')
 ring=load('wall_review_ring',ringpath);old=load('wall_review_old',oldpath);new=load('wall_review_new',ROOT/'wall.py')
 replay=new.qualify(ring,old);saved=read(ROOT/'RESULT.json')
 expected={k:v for k,v in saved.items() if k!='seconds'}
 ck(isinstance(replay['variables'],tuple) and isinstance(expected['variables'],list),'JSON_TYPE_DIAGNOSTIC')
 ck({k:v for k,v in replay.items() if k!='variables'}=={k:v for k,v in expected.items() if k!='variables'},'ONLY_VARIABLES_CONTAINER_DIFFERS')
 ck(list(replay['variables'])==expected['variables'],'VARIABLES_EXACT_SEQUENCE')
 ck(json.loads(json.dumps(replay))==expected,'EXACT_JSON_QUALIFIER_REPLAY')
 expected={f'QUARTIC_REPLAY:{sg}:{row}:{n}' for sg in (-1,1) for row in ('O','J','graph','pwall','bwall','deltaPhi','normal') for n in range(5)}
 expected|={f'{row}:{sg}' for sg in (-1,1) for row in ('NEW_OSCILLATOR','NEW_SCALAR','NEW_GRAPH','ELIMINATED_ROBIN','BOOST_CORRECTION','BOOST_OMISSION_DETECTED')}
 ck(expected<=set(saved['checks']),'EXPLICIT_CONTROL_COVERAGE');ck(set(saved['orientations'])=={'-1','1'},'BOTH_ORIENTATIONS')
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,qualifier_controls=len(saved['checks']),producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),scope='Immutable binding and exact replay audit of source-reviewed fifth wall qualifier, with independent manual Taylor/fixed-time/boost derivation review. Not a second independently generated nonlinear wall source oracle; no field solve or d5 enclosure.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'QUINTIC_WALL_AUDIT_R1.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<1793082611,'LINUX_CUTOFF');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN');lease=load('wall_review_lease',lp);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<1793082611,'POST_LEASE_CUTOFF')
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

