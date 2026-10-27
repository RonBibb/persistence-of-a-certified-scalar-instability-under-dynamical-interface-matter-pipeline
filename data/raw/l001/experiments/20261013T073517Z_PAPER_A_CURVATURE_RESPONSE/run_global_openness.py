"""Capture the second separately admitted execution without overwriting evidence."""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
root=Path(__file__).resolve().parent
targets=[root/name for name in ('GLOBAL_OPENNESS_RESULT.json','GLOBAL_OPENNESS_STDERR.txt','GLOBAL_OPENNESS_RUN.json')]
if any(p.exists() for p in targets): raise RuntimeError('Existing result; no automatic replay')
gate_path=root/'GLOBAL_OPENNESS_GATE.json'
gate=json.loads(gate_path.read_text())
if gate.get('decision')!='APPROVED_FOR_ONE_BOUNDED_EXECUTION': raise RuntimeError('Independent gate has not approved')
for name,digest in gate['frozen_hashes'].items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest: raise RuntimeError('Gate binding mismatch '+name)
env=os.environ.copy()
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'): env[key]='1'
start=datetime.now(timezone.utc).isoformat(); t=time.monotonic()
proc=subprocess.run([sys.executable,'-I',str(root/'global_openness.py')],env=env,capture_output=True,timeout=60)
targets[0].write_bytes(proc.stdout); targets[1].write_bytes(proc.stderr)
meta={'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-t,
      'returncode':proc.returncode,'python':sys.version,'executable':sys.executable,'blas_threads':1,
      'gate_sha256':hashlib.sha256(gate_path.read_bytes()).hexdigest(),
      'output_sha256':hashlib.sha256(proc.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(proc.stderr).hexdigest()}
targets[2].write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2)); print(proc.stdout.decode())
if proc.returncode: raise SystemExit(proc.returncode)
