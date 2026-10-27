"""Read-only authentication of this goal's nine producer/audit pairs."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,os,signal,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent;GOAL=ROOT.parent;BASE=GOAL.parent
DEADLINE=1793047195
PINS={
'ANALYTIC_INVERSE':('7ec861cf5d45f7799f5f88d2d776445acf4c4f4ad7d6626c4ab5e06b3c640d99','d6dea65549d221cc69649b437b2f1b90cca5d3390f4696ee9e3bad37808d29ee'),
'ANALYTIC_SEED':('e89622e7c04b37bc68f529f684c823af464c8ceb6e86c5629b350d49a8f0df52','91372d768a2cbc8b48c101dd29648f0b00c4c8648f47472f24842f64eaf31dbe'),
'SOURCE_MAJORANT':('7081dcf2fce22ae857bd14b88da5a1a19e56208e35db1b08eadff469137501d7','aecbf787bc2a7d928e9ac4ce0918728e645213eeb82a3a6027c02a12c2bc9d8d'),
'WALL_IDENTITY':('f8820ce6d0f2871e7dcb1d236e33229123a37458f6849af2beb0dfe9b340d50b','cffef7fe3c3ca56d3286df026307f51c6f4e2f1b3f19ab060cde51dc7e245906'),
'PROPER_CLOCK_REMAINDER':('31438d2ae08e40ddb5c2b1788f36af57ddc9c4fc8a734dc3098e1e2e07ff7bcb','500f29806a2bb64734612ea303fb599be7b0d5503a03dda23c80b38206756d37'),
'RESPONSE_CONDITIONING':('f77d561f1681b91cd15b65cb2db626ff842ac061e879dcbe9f27981c54878c63','7c3fe1b97c6aaf4d2fe5218880bebbcc0bb5b0621e929910a92b96fd24cf5d84'),
'TWO_SIDED_DEPARTURE':('b79e63c2e6bcb547ce0fffb166c0bb8560f4722df9f90a884447860f47661ba3','6e79a0458106bc3105ebf135f39753c9f4a6344f86ff9af002bc51d1847d774d'),
'WEIGHTED_SOURCE_MAJORANT':('a514a572c03946c707cc6cff14624db74168f6803b818d6c8a849cda412176be','8fa71d9bc121462fd0effd5eb712d991ed5656b39c3706221df277dd9d20ff06'),
'CUBIC_CLOCK_TAIL':('97e01b5fd9e6513db28be3da9840e69932c284938bc5a3670aceb1145bba3ed9','82036edea79c9c85942594a2c00ae73ed558ba65e55da78c6ee13a50e1eff37d')}
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
def main():
    started=time.monotonic();expected={};verified={};pending=[];checks=0
    def bind(p,h):
        nonlocal checks
        p=str(Path(p));need(isinstance(h,str) and len(h)==64,'HASH_SCHEMA')
        need(p not in expected or expected[p]==h,'CONFLICT:'+p);expected[p]=h
        if p not in verified:
            need(time.time()<DEADLINE,'DEADLINE');need(sha(p)==h,'HASH:'+p);verified[p]=h;checks+=1
            if Path(p).name.endswith('BINDING.json'):pending.append(p)
    for suffix,(prod,au) in PINS.items():
        packet=BASE/('20261026_NEUTRAL_'+suffix)
        for root,prefix,pin in ((packet,'',prod),(packet/'audit','AUDIT_',au)):
            terminal=root/(prefix+'TERMINAL.json');bind(terminal,pin);t=read(terminal);need(t['pass_status'],'TERMINAL_PASS')
            source='verify.py' if prefix else ('run.py' if suffix=='ANALYTIC_SEED' else 'check.py')
            for n,key in ((prefix+'RESULT.json','result_sha256'),(prefix+'BINDING.json','binding_sha256'),(source,'source_sha256')):bind(root/n,t[key])
            if 'derivation_sha256' in t:bind(root/'DERIVATION.txt',t['derivation_sha256'])
            result=read(root/(prefix+'RESULT.json'));need(result.get('pass_status',result.get('pass')) is True,'RESULT_PASS')
            for n in (prefix+'TERMINAL.json',prefix+'RESULT.json',prefix+'BINDING.json'):
                need((root/n).stat().st_mode&0o222==0,'SEALED_PERMISSION:'+str(root/n))
        bad=[str(p) for p in packet.rglob('*') if p.name=='FAILURE.json' or p.name=='__pycache__' or p.name.endswith('.tmp') or p.suffix=='.pyc']
        need(not bad,'UNEXPECTED_FAILURE_OR_STAGING:'+repr(bad))
    seen=set()
    while pending:
        p=pending.pop()
        if p in seen:continue
        seen.add(p);data=read(p)
        for group in ('inputs','sources','runtime','parents','files'):
            table=data.get(group,{})
            if isinstance(table,dict):
                for path,h in table.items():
                    if isinstance(path,str) and path.startswith('/') and isinstance(h,str) and len(h)==64:bind(path,h)
    seed=BASE/'20261026_NEUTRAL_ANALYTIC_SEED';record=read(seed/'RESULT.json');chunks=0;cells={}
    for arm,entry in record['arms'].items():
        cells[arm]=entry['cells']
        for chunk in entry['chunks']:
            for key,hkey in (('file','sha256'),('checkpoint','checkpoint_sha256')):
                p=(seed/chunk[key]).resolve();need(p.is_relative_to(seed.resolve()),'SEED_PATH_SCOPE');bind(p,chunk[hkey])
            chunks+=1
    active=[]
    prefixes=[str(BASE/('20261026_NEUTRAL_'+s))+'/' for s in PINS]
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():continue
        try:argv=(proc/'cmdline').read_bytes().decode(errors='replace').split('\0')
        except (FileNotFoundError,PermissionError,ProcessLookupError):continue
        if argv and Path(argv[0]).name.startswith('python') and any(a.endswith('.py') and any(a.startswith(p) for p in prefixes) for a in argv):active.append(dict(pid=int(proc.name),argv=argv))
    need(not active,'LIVE_GOAL_WORKERS')
    # Rehash the small authoritative heads after reading their large dependency graph.
    for suffix,(prod,au) in PINS.items():
        packet=BASE/('20261026_NEUTRAL_'+suffix)
        need(sha(packet/'TERMINAL.json')==prod and sha(packet/'audit/AUDIT_TERMINAL.json')==au,'HEAD_CHANGED')
    put('BINDING.json',dict(inputs=verified,source_sha256=sha(__file__),deadline_unix=DEADLINE))
    result=dict(pass_status=True,classification='NINE_PACKET_AND_AUDIT_INTEGRITY_CLOSURE',producer_packets=len(PINS),audit_packets=len(PINS),distinct_files_verified=checks,binding_documents=len(seen),seed_chunks=chunks,seed_cells=cells,active_goal_workers=active,unexpected_failure_staging_cache_files=0,seconds=time.monotonic()-started,verified_at_unix=time.time(),scope='Authentication and process snapshot only. Mathematical claims depend on the signed review and its stated inherited premises.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps(result),flush=True)
if __name__=='__main__':
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_WINDOW');need(not any((ROOT/n).exists() for n in ('RESULT.json','TERMINAL.json','FAILURE.json')),'NO_OVERWRITE')
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('INTEGRITY_600_SECONDS')));signal.alarm(600);main()
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:signal.alarm(0)
