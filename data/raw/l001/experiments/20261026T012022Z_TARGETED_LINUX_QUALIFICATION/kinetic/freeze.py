"""Linux administrative binding only; never imports scientific checkers."""
import sys
sys.dont_write_bytecode = True
import hashlib
import json
import os
from pathlib import Path
import platform
import datetime
import argparse
import fractions
import gzip
import signal
import traceback
import importlib.util
import resource
import fcntl
import subprocess
import time

HERE = Path(__file__).resolve().parent
RESEARCH = Path('/media/psf/Home/Research')
PACKET = RESEARCH / 'papers/ab-bridge-feasibility/20261019_continuum_kinetic_143342'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

assert sys.platform == 'linux'
assert (HERE / 'SOURCE_REVIEW.md').is_file()
paths = [p for p in PACKET.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
paths += [HERE / n for n in ('qualify.py', 'freeze.py', 'lease.py', 'CONTRACT.md', 'SOURCE_REVIEW.md')]
paths += [Path(sys.executable).resolve()]
modules = {}
for name, module in list(sys.modules.items()):
    value = getattr(module, '__file__', None)
    if value and Path(value).is_file():
        p = Path(value).resolve()
        paths.append(p)
        modules[name] = str(p)
mapped = []
for row in Path('/proc/self/maps').read_text().splitlines():
    fields = row.split(None, 5)
    if len(fields) == 6 and fields[5].startswith('/') and Path(fields[5]).is_file():
        paths.append(Path(fields[5])); mapped.append(fields[5])
for item in json.loads((PACKET / 'INPUTS.json').read_text())['files']:
    paths.append(RESEARCH / Path(item['source']).relative_to('/Users/ronbibb/Research'))
record = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'files': {str(p): sha(p) for p in sorted(set(paths))},
          'platform': platform.platform(), 'python': sys.version,
          'executable': sys.executable, 'executable_realpath': str(Path(sys.executable).resolve()),
          'modules': modules, 'mapped_files': sorted(set(mapped)), 'pid': os.getpid(),
          'scope': 'administrative pre-execution binding; no scientific checker imported'}
with (HERE / 'FROZEN.json').open('x') as f:
    json.dump(record, f, indent=2)
    f.flush()
    os.fsync(f.fileno())
print(json.dumps({'frozen_sha256': sha(HERE / 'FROZEN.json'), 'files': len(record['files'])}))
