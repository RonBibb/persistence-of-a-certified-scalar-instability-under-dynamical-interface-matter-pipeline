"""Same-process runtime witnesses around an unchanged original phase driver."""
import datetime
import hashlib
import json
import os
import platform
import runpy
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
SOURCE = BASE/'source'
OUT = BASE/'output'
name, entry = sys.argv[1:]
assert name=='phase' and entry=='test1_phase_v3.py'
sys.path.insert(0, '/anonymous/linux-user/research-runs/cap-interval-arb-2026-09-12')
sys.path.insert(0, str(SOURCE))
import flint

if sys.version_info[:3] != (3,12,3) or flint.__version__ != '0.9.0':
    raise RuntimeError('UNADMITTED_RUNTIME_VERSION')
flint.ctx.threads=1
flint.ctx.prec=768


def witness(label):
    loaded=set()
    for row in Path('/proc/self/maps').read_text().splitlines():
        fields=row.split()
        if len(fields)>=6 and fields[-1].startswith('/'):
            p=Path(fields[-1])
            if p.is_file():loaded.add(p)
    loaded.add(Path(sys.executable).resolve())
    modules={}
    for key,module in list(sys.modules.items()):
        filename=getattr(module,'__file__',None)
        if key=='flint' or key.startswith('flint.'):
            if filename and Path(filename).is_file():
                p=Path(filename).resolve()
                modules[key]={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    value={'witness':label,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'monotonic_seconds':time.monotonic(),
           'pid':os.getpid(),'python':sys.version,'executable':sys.executable,
           'platform':platform.platform(),'python_flint':flint.__version__,
           'flint_module':flint.__file__,'precision_bits':flint.ctx.prec,
           'arithmetic_threads':flint.ctx.threads,'affinity':sorted(os.sched_getaffinity(0)),
           'phase_output_exists':(SOURCE/'test1_v3').exists(),
           'mapped_binary_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(loaded)},
           'flint_imports':modules,
           'source_sha256':{rel:hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()
                            for rel in json.loads((BASE/'EXECUTION_SOURCE_BINDINGS.json').read_text())},
           'scope':'Same producer process at before/after boundaries; identity/provenance, not arithmetic validation or continuous load surveillance.'}
    (OUT/f'runtime_{label}.json').write_text(json.dumps(value,indent=2)+'\n')


if (SOURCE/'test1_v3').exists():
    raise RuntimeError('FRESH_PHASE_OUTPUT_NOT_ABSENT')
witness('before')
try:
    runpy.run_path(str(SOURCE/entry),run_name='__main__')
finally:
    witness('after')
