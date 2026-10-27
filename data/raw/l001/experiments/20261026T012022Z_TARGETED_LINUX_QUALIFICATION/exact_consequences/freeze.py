"""Administrative Linux freeze only; imports no scientific programs."""
import sys
sys.dont_write_bytecode = True
import datetime
import hashlib
import json
import os
from pathlib import Path
import platform
import fractions
import decimal
import math
import _decimal
import _hashlib
import copy
import functools
import signal
import subprocess
import time
import ctypes
import fcntl
import resource

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[1]
OWNER = EXPERIMENTS.parent
ROOTS = [EXPERIMENTS / n for n in ('20261013T073517Z_PAPER_A_CURVATURE_RESPONSE',
                                  '20261013T081618Z_PAPER_A_STIFFNESS_COEFFICIENTS')]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sys.platform == 'linux' and sys.version_info[:3] == (3, 12, 3)
assert (HERE / 'SOURCE_REVIEW.md').is_file()
paths = set()
pending = [p for root in ROOTS for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
while pending:
    p = pending.pop().resolve()
    if p in paths: continue
    paths.add(p)
    if p.suffix != '.json': continue
    record = json.loads(p.read_text())
    if not isinstance(record, dict): continue
    for key, base in (('sources', OWNER), ('frozen_hashes', p.parent)):
        mapping = record.get(key, {})
        if not isinstance(mapping, dict): continue
        for name, expected in mapping.items():
            assert isinstance(name, str) and isinstance(expected, str), str(p)
            target = (base / name).resolve()
            assert sha(target) == expected, str(target)
            pending.append(target)
paths.update(HERE / n for n in ('PLAN.md', 'producer.py', 'freeze.py', 'lease.py', 'SOURCE_REVIEW.md'))
paths.add(Path(sys.executable).resolve())
modules = {}
runtime_paths = set()
for name, module in list(sys.modules.items()):
    value = getattr(module, '__file__', None)
    if value and Path(value).is_file():
        path = Path(value).resolve()
        runtime_paths.add(path)
        modules[name] = str(path)
paths.update(runtime_paths)
mapped = set()
for line in Path('/proc/self/maps').read_text().splitlines():
    tail = line.split(maxsplit=5)
    if len(tail) == 6 and tail[5].startswith('/'):
        p = Path(tail[5])
        if p.is_file(): mapped.add(p.resolve())
paths.update(mapped)
record = dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    files={str(p): sha(p) for p in sorted(paths)},
    runtime_files={str(p): sha(p) for p in sorted(runtime_paths | mapped | {Path(sys.executable).resolve()})},
    platform=platform.platform(), python=sys.version, executable=sys.executable,
    executable_realpath=str(Path(sys.executable).resolve()), modules=modules,
    mapped_files=[str(p) for p in sorted(mapped)],
    scope='administrative binding; original historical metadata preserved; no scientific imports')
with (HERE / 'FROZEN.json').open('x') as f:
    json.dump(record, f, indent=2); f.flush(); os.fsync(f.fileno())
print(json.dumps(dict(frozen_sha256=sha(HERE/'FROZEN.json'), files=len(paths))))
