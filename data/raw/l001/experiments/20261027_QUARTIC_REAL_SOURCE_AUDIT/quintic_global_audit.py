"""Independent unrounded rational interval audit of global quintic probe."""
import sys,json,hashlib,time,signal,os,traceback,importlib.util
from pathlib import Path
from fractions import Fraction as Q
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(100000)
BASE=Path(__file__).resolve().parent.parent;ROOT=BASE/'20261027_QUINTIC_GLOBAL_BULK_PROBE';COUNT=0
def ck(v,n):
 global COUNT
 COUNT+=1
 if not v:raise AssertionError(n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def iv(x):return tuple(map(Q,x['exact_bounds']))
def add(a,b):return a[0]+b[0],a[1]+b[1]
def mul(a,b):
 v=[x*y for x in a for y in b];return min(v),max(v)
def scale(a,x):return mul(a,(Q(x),Q(x)))
def divide(a,b):
 ck(b[0]*b[1]>0,'NONZERO_DIVISOR');return mul(a,(1/b[1],1/b[0]))
def power(a,n):
 out=(Q(1),Q(1))
 for _ in range(n):out=mul(out,a)
 return out
def contains(a,b):return a[0]<=b[0]<=b[1]<=a[1]
def main():
 terminal=read(ROOT/'TERMINAL.json');pin=sha(ROOT/'TERMINAL.json');ck(terminal['pass_status'],'PRODUCER_PASS')
 for f,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('interval.py','interval_sha256'),('DERIVATION.txt','derivation_sha256')]:ck(sha(ROOT/f)==terminal[k],'TERMINAL:'+f)
 bound={}
 for group in ('inputs','sources','runtime'):
  for p,h in read(ROOT/'BINDING.json')[group].items():ck(sha(p)==h,'BOUND:'+p);bound[p]=h
 archive=BASE/'20261027_QUARTIC_REAL_SOURCE_ENCLOSURE';qualified=read(BASE/'20261027_QUINTIC_BULK_QUALIFICATION/RESULT.json');names=qualified['variables'];result=read(ROOT/'RESULT.json');reports={}
 for engine in ('primary','independent'):
  arm=read(archive/('ARM_'+engine+'.json'));saved=result['arms'][engine];cursor=0;hull=None;previous=None;step=Q(1,4096 if engine=='primary' else 8192)
  for item in arm['chunks']:
   p=archive/item['file'];ck(bound.get(str(p))==item['sha256']==sha(p),'CHUNK_PIN');chunk=read(p);cp=read(archive/item['checkpoint'])
   ck(chunk['previous_sha256']==previous and chunk['binding_sha256']==sha(archive/'production_BINDING.json'),'CHUNK_CHAIN');previous=item['sha256'];ck(cp['chunk_sha256']==previous and cp['binding_sha256']==chunk['binding_sha256'],'CHECKPOINT_CHAIN')
   for row in chunk['records']:
    ck(row['index']==cursor and Q(row['s'])==cursor*step and Q(row['step'])==step,'CELL_POSITION');box=list(map(iv,row['canonical_box']));ck(len(box)==23 and all(a<=b for a,b in box),'BOX_VALID')
    hull=box if hull is None else [(min(a,c),max(b,d)) for (a,b),(c,d) in zip(hull,box)];cursor+=1
   ck(cp['completed']==cursor and cp['total']==arm['cells'],'CHECKPOINT_COUNT')
  ck(cursor==arm['cells']==saved['cells'],'CELL_COUNT');ck((cursor-1)*step<Q(arm['D'][1])<=cursor*step,'FULL_DOMAIN')
  ck(hull==list(map(iv,saved['canonical_global_hull'])),'EXACT_GLOBAL_HULL')
  p={k:iv(v) for k,v in arm['parameters'].items()};z=hull
  P,F,G=[add(z[j],mul(p['A2'],z[j+3])) for j in (8,9,10)]
  p3,f3,g3=[add(add(z[j],mul(p['A2'],z[j+3])),mul(p['A3'],z[j+6])) for j in (14,15,16)]
  denominator=add(scale(p['rate'],5),scale(p['h'],-1));ck(denominator[0]>0,'TRACE_POSITIVE')
  v=dict(H=z[1],T=z[3],Phi=z[2],e=power(z[4],2),p=z[5],f=z[6],g=z[7],P=P,F=F,G=G,p3=p3,f3=f3,g3=g3,
   p4=(-Q(arm['p4_bound']),Q(arm['p4_bound'])),f4=(-Q(arm['f4_bound']),Q(arm['f4_bound'])),g4=(-Q(arm['f4prime_bound']),Q(arm['f4prime_bound'])),m=p['m2'],C=p['c_factor'],J=p['c3_factor'],L=p['c4_factor'],M=divide(p['rate'],scale(denominator,5)),r=p['rate'],h=p['h'],p5=(Q(0),Q(0)),f5=(Q(0),Q(0)),g5=(Q(0),Q(0)))
  for k in names:ck(contains(iv(saved['variables'][k]),v[k]),'VARIABLE_ENCLOSURE:'+k)
  # Evaluate over the saved, outward-rounded variables using NO additional rounding.
  v={k:iv(saved['variables'][k]) for k in names};maxima=[max((row['powers'][i] for rows in qualified['sources'].values() for row in rows),default=0) for i in range(len(names))];powers=[[power(v[k],j) for j in range(n+1)] for k,n in zip(names,maxima)]
  ranges={}
  for key in ('c5','Sp5','Sc5','Sg5'):
   total=(Q(0),Q(0))
   for row in qualified['sources'][key]:
    ck(all(row['powers'][names.index(k)]==0 for k in ('p5','f5','g5')),'LOWER_ONLY');c=Q(row['coefficient']);term=(c,c)
    for i,n in enumerate(row['powers']):
     if n:term=mul(term,powers[i][n])
    total=add(total,term)
   ck(contains(iv(saved['sources'][key]),total),'SOURCE_CONTAINMENT:'+engine+':'+key);ranges[key]=[float(q) for q in iv(saved['sources'][key])]
  reports[engine]=dict(cells=cursor,sources_display=ranges)
 for p,h in bound.items():ck(sha(p)==h,'POST_BOUND:'+p)
 ck(sha(ROOT/'TERMINAL.json')==pin,'TERMINAL_UNCHANGED')
 return dict(PASS=True,checks=COUNT,producer_terminal=pin,producer_result=sha(ROOT/'RESULT.json'),arms=reports,scope='Independent complete archive hull/coverage reconstruction and exact unrounded rational interval evaluation of authenticated fifth bulk polynomials. Source identities inherited from separately reviewed qualification; no inverse, wall enclosure, d5 or clock-amplitude claim.')
if __name__=='__main__':
 start=time.time();pin=sha(__file__);lease=None;dest=Path(__file__).parent/'QUINTIC_GLOBAL_AUDIT.json'
 if dest.exists():raise AssertionError('NO_RESTART')
 try:
  ck(sys.platform=='linux' and start<1793082611,'LINUX_CUTOFF');lp=BASE/'20261027_SHARED_ADMISSION/lease.py';ck(sha(lp)=='0dbc81af7a01cee5b1108105a95b5247b4553a14dc62df9f3e4efbe67c7d5862','LEASE_PIN')
  s=importlib.util.spec_from_file_location('global_review_lease',lp);lease=importlib.util.module_from_spec(s);s.loader.exec_module(lease);lease.ROOT=Path(__file__).parent;lease.acquire();ck(time.time()<1793082611,'POST_LEASE_CUTOFF')
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
