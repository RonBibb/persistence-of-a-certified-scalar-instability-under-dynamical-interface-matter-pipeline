"""Final read-only refresh of the nine-packet closure plus joint successor."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,os,signal,time,traceback
from pathlib import Path
GOAL=Path(__file__).resolve().parent;ROOT=GOAL/'final_verification';BASE=GOAL.parent
DEADLINE=1793047195;PACKET=BASE/'20261026_NEUTRAL_JOINT_SOURCE_FEASIBILITY'
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(prod_pin,audit_pin):
    started=time.monotonic();files={};pending=[];seen=set()
    def bind(p,h):
        p=str(Path(p));need(isinstance(h,str) and len(h)==64,'HASH_SCHEMA')
        need(p not in files or files[p]==h,'CONFLICT:'+p)
        if p not in files:
            need(time.time()<DEADLINE,'DEADLINE');need(sha(p)==h,'HASH:'+p);files[p]=h
            if Path(p).name.endswith('BINDING.json'):pending.append(p)
    old=GOAL/'verification';bind(old/'TERMINAL.json','97bf9d48c0200a8b11b0795b3bbc7f18190feaf08b3d33bdd832ae9203c1b09d')
    t=read(old/'TERMINAL.json');need(t['pass_status'],'PRIOR_CLOSURE_PASS')
    for n,k in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('verify.py','source_sha256')):bind(old/n,t[k])
    oldresult=read(old/'RESULT.json');need(oldresult['producer_packets']==oldresult['audit_packets']==9,'PRIOR_COUNT')
    for root,prefix,pin in ((PACKET,'',prod_pin),(PACKET/'audit','AUDIT_',audit_pin)):
        bind(root/(prefix+'TERMINAL.json'),pin);t=read(root/(prefix+'TERMINAL.json'));need(t['pass_status'],'JOINT_PASS')
        for n,k in ((prefix+'RESULT.json','result_sha256'),(prefix+'BINDING.json','binding_sha256'),('verify.py' if prefix else 'check.py','source_sha256')):bind(root/n,t[k])
        if 'derivation_sha256' in t:bind(root/'DERIVATION.txt',t['derivation_sha256'])
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);rec=read(p)
        for group in ('inputs','sources','runtime','parents','files'):
            d=rec.get(group,{})
            if isinstance(d,dict):
                for path,h in d.items():
                    if isinstance(path,str) and path.startswith('/') and isinstance(h,str) and len(h)==64:bind(path,h)
    dirs=sorted({Path(p).parent for p in files if Path(p).name=='TERMINAL.json' and Path(p).parent.name.startswith('20261026_NEUTRAL_')})
    need(len(dirs)==10,'TEN_PACKET_INVENTORY')
    for packet in dirs:
        bad=[str(p) for p in packet.rglob('*') if p.name in ('FAILURE.json','__pycache__') or p.name.endswith('.tmp') or p.suffix=='.pyc']
        need(not bad,'UNEXPECTED_ARTIFACT:'+repr(bad))
        for sub,pre in ((packet,''),(packet/'audit','AUDIT_')):
            for name in ('RESULT.json','BINDING.json','TERMINAL.json'):need((sub/(pre+name)).stat().st_mode&0o222==0,'SEALED_PERMISSION')
    active=[];prefixes=[str(p)+'/' for p in dirs]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:argv=(proc/'cmdline').read_bytes().decode(errors='replace').split('\0')
        except (FileNotFoundError,PermissionError,ProcessLookupError):continue
        if argv and Path(argv[0]).name.startswith('python') and any(a.endswith('.py') and any(a.startswith(p) for p in prefixes) for a in argv):active.append(dict(pid=int(proc.name),argv=argv))
    need(not active,'LIVE_GOAL_WORKER')
    docs={n:sha(GOAL/n) for n in ('CONTRACT.md','RESULTS.md','LOCAL_THEOREM.md','DEPENDENCIES.md','NEXT_TEST.md','TRACE_ROUTE_SCOPING.md','REVIEW.md')}
    put('BINDING.json',dict(inputs=files,documents=docs,source_sha256=sha(__file__),producer_pin=prod_pin,audit_pin=audit_pin,deadline_unix=DEADLINE))
    result=dict(pass_status=True,classification='TEN_PACKET_FINAL_INTEGRITY_CLOSURE',producer_packets=10,audit_packets=10,distinct_files_verified=len(files),binding_documents=len(seen),seed_chunks=oldresult['seed_chunks'],seed_cells=oldresult['seed_cells'],active_goal_workers=active,unexpected_failure_staging_cache_files=0,seconds=time.monotonic()-started,verified_at_unix=time.time(),scope='Final byte-identity and liveness refresh; mathematical conclusions remain those of the signed review and inherited premises.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(result),flush=True)
if __name__=='__main__':
    try:
        need(sys.platform=='linux' and len(sys.argv)==3 and time.time()+120<DEADLINE,'LINUX_WINDOW');ROOT.mkdir(exist_ok=True)
        need(not any((ROOT/n).exists() for n in ('RESULT.json','TERMINAL.json','FAILURE.json')),'NO_OVERWRITE')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('FINAL_REFRESH_120_SECONDS')));signal.alarm(120);main(*sys.argv[1:])
    except BaseException as e:
        if ROOT.exists():put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()))
        raise
    finally:signal.alarm(0)
