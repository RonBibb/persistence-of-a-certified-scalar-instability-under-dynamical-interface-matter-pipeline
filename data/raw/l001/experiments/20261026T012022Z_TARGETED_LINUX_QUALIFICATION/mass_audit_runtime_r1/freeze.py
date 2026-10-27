"""Administrative-only Linux binding; no flint/scientific imports."""
import sys
sys.dont_write_bytecode=True
import argparse, contextlib, datetime, fractions, hashlib, importlib.util, json, math, os, platform, signal, time, traceback
import subprocess, selectors, inspect
from pathlib import Path
HERE=Path(__file__).resolve().parent
PACKET=Path('/media/psf/Home/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z')
FLINT=Path('/home/parallels/research-runs/cap-interval-arb-2026-09-12')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
assert sys.platform=='linux' and (HERE/'SOURCE_REVIEW.md').is_file()
b=read(PACKET/'BINDINGS.json'); rt=b['runtime']
assert str(Path(sys.executable).resolve())==rt['executable']
assert sha(sys.executable)==rt['executable_sha256']
assert (FLINT/'flint/__init__.py').is_file()
paths={p for p in PACKET.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
paths.update(p for p in (FLINT/'flint').rglob('*') if p.is_file() and '__pycache__' not in p.parts)
paths.update(HERE/n for n in ('qualify.py','freeze.py','lease.py','PLAN.md','SOURCE_REVIEW.md','PROPOSED_FIX.md'))
for name in ('RUNTIME_BEFORE.json','RUNTIME_AFTER.json'):
    receipt=HERE.parent/'mass_audit'/name
    paths.add(receipt)
    observed=json.loads(receipt.read_text())
    for item in observed['modules'].values():
        p=Path(item['path']); assert sha(p)==item['sha256'],str(p); paths.add(p)
    for p,d in observed['mapped_files'].items():
        assert sha(p)==d,p; paths.add(Path(p))
paths.add(Path(sys.executable).resolve())
for p,d in rt['libraries'].items(): assert sha(p)==d,p; paths.add(Path(p))
for key in ('source','review_sources'):
    for p,d in b[key].items(): assert sha(PACKET/p)==d,p; paths.add(PACKET/p)
for item in b['inputs'].values():
    p=(PACKET/item['path']).resolve(); assert sha(p)==item['sha256'],str(p); paths.add(p)
mp=PACKET/b['inputs']['previous_manifest']['path']; entries=read(mp)['files']
if isinstance(entries,dict): entries=[{'path':k,'sha256':v if isinstance(v,str) else v['sha256']} for k,v in entries.items()]
for item in entries:
    p=(mp.parent/item['path']).resolve(); assert sha(p)==item['sha256'],str(p); paths.add(p)
platform_value=platform.platform()
modules={}; mapped=[]
for n,m in list(sys.modules.items()):
    p=getattr(m,'__file__',None)
    if p and Path(p).is_file(): paths.add(Path(p).resolve()); modules[n]=str(Path(p).resolve())
for row in Path('/proc/self/maps').read_text().splitlines():
    f=row.split(None,5)
    if len(f)==6 and f[5].startswith('/') and Path(f[5]).is_file(): paths.add(Path(f[5])); mapped.append(f[5])
record={'files':{str(p):sha(p) for p in sorted(paths)},'executable_realpath':str(Path(sys.executable).resolve()),'packet':str(PACKET),'flint_root':str(FLINT),'platform':platform_value,'python':sys.version,'pid':os.getpid(),'modules':modules,'mapped_files':mapped,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Administrative binding including freshly verified previous runtime inventories; native package not imported.'}
with (HERE/'FROZEN.json').open('x') as f: json.dump(record,f,indent=2); f.flush(); os.fsync(f.fileno())
print(json.dumps({'frozen_sha256':sha(HERE/'FROZEN.json'),'files':len(paths)}))
