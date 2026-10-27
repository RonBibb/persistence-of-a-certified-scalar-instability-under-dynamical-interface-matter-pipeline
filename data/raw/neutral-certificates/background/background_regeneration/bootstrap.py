"""Import-path/runtime witness only; execute an unchanged frozen producer."""
import hashlib
import json
import os
import platform
import runpy
import sys
from pathlib import Path

base = Path(__file__).resolve().parent
name, entry = sys.argv[1:]
runtime_root = Path('/home/parallels/research-runs/cap-interval-arb-2026-09-12')
sys.path.insert(0, str(runtime_root))
sys.path.insert(0, str(base / 'source' / name))
import flint

if sys.version_info[:3] != (3, 12, 3) or flint.__version__ != '0.9.0':
    raise RuntimeError('UNADMITTED_RUNTIME_VERSION')
flint.ctx.threads = 1
loaded = set()
for row in Path('/proc/self/maps').read_text().splitlines():
    parts = row.split()
    if len(parts) >= 6 and parts[-1].startswith('/'):
        p = Path(parts[-1])
        if p.is_file():
            loaded.add(p)
loaded.add(Path(sys.executable).resolve())
witness = {
    'python': sys.version, 'executable': sys.executable,
    'platform': platform.platform(), 'python_flint': flint.__version__,
    'flint_module': flint.__file__, 'arithmetic_threads': flint.ctx.threads,
    'affinity': sorted(os.sched_getaffinity(0)),
    'mapped_binary_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted(loaded)},
    'scope': 'Actual pre-producer loaded mappings; identity, not independent arithmetic validation.'
}
(base / 'output' / f'{name}_runtime.json').write_text(json.dumps(witness, indent=2)+'\n')
runpy.run_path(str(base / 'source' / name / entry), run_name='__main__')
