"""Bounded whole-domain quintic bulk resource probe; no ODE or inverse."""
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

def main(lease):
 started=time.monotonic();inputs={};sources={str(ROOT/n):sha(ROOT/n) for n in ('run.py','interval.py','DERIVATION.txt')}
 def bind(p,h):
  need(sha(p)==h,'BIND:'+str(p));inputs[str(p)]=h
 def closure(p):
  for group in ('inputs','sources','runtime'):
   for path,h in read(p)[group].items():bind(path,h)
 parent=BASE/'20261027_QUINTIC_BULK_QUALIFICATION'
 bind(parent/'TERMINAL.json','9ea79c5e6713ff5ba04bec3a94c6b25f1459c4ca7cd5ef59883db852738fe409')
 t=read(parent/'TERMINAL.json');need(t['pass_status'],'BULK_PASS')
 for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('bulk.py','bulk_sha256'),('series.py','series_sha256'),('DERIVATION.txt','derivation_sha256')]:bind(parent/n,t[k])
 closure(parent/'BINDING.json')
 archive=BASE/'20261027_QUARTIC_REAL_SOURCE_ENCLOSURE'
 bind(archive/'production_TERMINAL.json','429d3c08cc3c95dc724c269bfcac60a8195e0d986445f4534fa707c1b30d796b')
 term=read(archive/'production_TERMINAL.json');need(term['pass_status'],'QUARTIC_PASS')
 for n,h in term['artifacts'].items():bind(archive/n,h)
 closure(archive/'production_BINDING.json')
 audit=BASE/'20261027_QUARTIC_REAL_SOURCE_AUDIT'
 bind(audit/'AUDIT_R3_TERMINAL.json','fae0daf4f748bf0622a565a54eb4cea1454268ea41430cff24323cec5422912e')
 bind(audit/'QUINTIC_BULK_AUDIT.json','7ad08c6c252bcbd7cff3b164c2f5d80ab295cc3edd86d283ee432980c9585af6')
 for n in ('lease.py','DESIGN.txt'):
  path=BASE/'20261027_SHARED_ADMISSION'/n;sources[str(path)]=sha(path)
 I=load('global_fifth_interval',ROOT/'interval.py').I
 len(str(10**20000));runtime=lease.observed()
 for path,h in runtime.items():need(inputs.get(path)==h or sources.get(path)==h,'RUNTIME:'+path)
 put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime))
 arithmetic_controls=[]
 for a,b in [(I(Q(-7,3),Q(11,7)),I(Q(-5,2),Q(13,11))),(I(Q(-1,10**180),Q(1,10**180)),I(Q(2,3),Q(9,7))),(I(Q(-17,13),Q(-2,19)),I(Q(-11,3),Q(-1,7)))]:
  exact=[x*y for x in (a.lo,a.hi) for y in (b.lo,b.hi)];v=a*b
  need(v.lo<=min(exact) and v.hi>=max(exact),'MULTIPLY_CONTAINMENT');arithmetic_controls.append('multiply')
  v=a+b;need(v.lo<=a.lo+b.lo and v.hi>=a.hi+b.hi,'ADD_CONTAINMENT');arithmetic_controls.append('add')
  if not b.lo<=0<=b.hi:
   exact=[x/y for x in (a.lo,a.hi) for y in (b.lo,b.hi)];v=a/b
   need(v.lo<=min(exact) and v.hi>=max(exact),'DIVISION_CONTAINMENT');arithmetic_controls.append('divide')
 for x in (Q(1,3),Q(-1,3),Q(2**900+1,7),Q(-1,10**250)):
  v=I.out(x,x);need(v.lo<=x<=v.hi,'ROUND_CONTAINMENT');arithmetic_controls.append('round')
 qualified=read(parent/'RESULT.json');names=qualified['variables'];reports={}
 for engine in ('primary','independent'):
  arm=read(archive/('ARM_'+engine+'.json'));hull=None;cursor=0;prior=None;step=Q(1,4096 if engine=='primary' else 8192)
  for item in arm['chunks']:
   path=archive/item['file'];need(inputs[str(path)]==item['sha256'],'CHUNK_AUTH')
   chunk=read(path);cp=read(archive/item['checkpoint'])
   need(chunk['previous_sha256']==prior and chunk['binding_sha256']==sha(archive/'production_BINDING.json'),'CHAIN')
   prior=item['sha256'];need(cp['chunk_sha256']==prior and cp['binding_sha256']==chunk['binding_sha256'],'CHECKPOINT')
   for row in chunk['records']:
    need(row['index']==cursor and Q(row['s'])==cursor*step and Q(row['step'])==step,'CELL_COVER')
    box=[tuple(map(Q,v['exact_bounds'])) for v in row['canonical_box']];need(len(box)==23 and all(a<=b for a,b in box),'CELL_BOX')
    hull=box if hull is None else [(min(a,c),max(b,d)) for (a,b),(c,d) in zip(hull,box)]
    cursor+=1
   need(cp['completed']==cursor and cp['total']==arm['cells'],'CHECKPOINT_COUNT')
  need(cursor==arm['cells'] and cursor*step>=Q(arm['D'][1]) and (cursor-1)*step<Q(arm['D'][1]),'FULL_DOMAIN')
  z=[I(a,b) for a,b in hull];p={k:I(*v['exact_bounds']) for k,v in arm['parameters'].items()}
  need((5*p['rate']-p['h']).lo>0,'FIFTH_TRACE_DIVISOR_POSITIVE')
  P,F,G=[z[j]+p['A2']*z[j+3] for j in (8,9,10)]
  p3,f3,g3=[z[j]+p['A2']*z[j+3]+p['A3']*z[j+6] for j in (14,15,16)]
  v=dict(H=z[1],T=z[3],Phi=z[2],e=z[4]**2,p=z[5],f=z[6],g=z[7],P=P,F=F,G=G,p3=p3,f3=f3,g3=g3,
    p4=I(-Q(arm['p4_bound']),Q(arm['p4_bound'])),f4=I(-Q(arm['f4_bound']),Q(arm['f4_bound'])),g4=I(-Q(arm['f4prime_bound']),Q(arm['f4prime_bound'])),
    m=p['m2'],C=p['c_factor'],J=p['c3_factor'],L=p['c4_factor'],M=p['rate']/(5*(5*p['rate']-p['h'])),r=p['rate'],h=p['h'],p5=I(0),f5=I(0),g5=I(0))
  maxima=[max((row['powers'][i] for rows in qualified['sources'].values() for row in rows),default=0) for i in range(len(names))]
  powers=[[v[k]**j for j in range(n+1)] for k,n in zip(names,maxima)]
  out={}
  for key in ('c5','Sp5','Sc5','Sg5'):
   value=I(0)
   for row in qualified['sources'][key]:
    need(all(row['powers'][names.index(k)]==0 for k in ('p5','f5','g5')),'LOWER_ONLY')
    term=I(Q(row['coefficient']))
    for i,n in enumerate(row['powers']):
     if n:term=term*powers[i][n]
    value=value+term
   out[key]=value.pack()
  reports[engine]=dict(cells=cursor,canonical_global_hull=[I(a,b).pack() for a,b in hull],variables={k:v[k].pack() for k in names},sources=out,seconds=time.monotonic()-started)
  put('PROBE_'+engine+'.json',reports[engine]);print(json.dumps(dict(engine=engine,cells=cursor,seconds=time.monotonic()-started)),flush=True)
 for path,h in dict(inputs,**sources).items():need(sha(path)==h,'POST_BINDING:'+path)
 need(lease.observed()==runtime,'RUNTIME_UNCHANGED')
 result=dict(pass_status=True,classification='GLOBAL_QUINTIC_BULK_RESOURCE_PROBE',arithmetic_controls=arithmetic_controls,arms=reports,seconds=time.monotonic()-started,scope='Conservative global bulk-source enclosures from authenticated full-domain cells and actual uniform fourth-order bounds. No inverse, wall bound, d5, new clock amplitude or physical trajectory.')
 put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(ROOT/'run.py'),interval_sha256=sha(ROOT/'interval.py'),derivation_sha256=sha(ROOT/'DERIVATION.txt')))
 print(json.dumps(dict(pass_status=True,seconds=result['seconds'])),flush=True)

if __name__=='__main__':
 lease=None
 try:
  need(sys.platform=='linux' and time.time()<CUTOFF,'LINUX_LAUNCH_CUTOFF')
  need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
  lp=BASE/'20261027_SHARED_ADMISSION/lease.py';need(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  lease=load('quartic_clock_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
  need(time.time()<CUTOFF,'POST_LEASE_CUTOFF')
  signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('QUINTIC_GLOBAL_PROBE_600_SECONDS')));signal.alarm(600)
  put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
 except BaseException as e:
  put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
 finally:
  signal.alarm(0)
  if lease:
   for h in lease.handles:h.close()


