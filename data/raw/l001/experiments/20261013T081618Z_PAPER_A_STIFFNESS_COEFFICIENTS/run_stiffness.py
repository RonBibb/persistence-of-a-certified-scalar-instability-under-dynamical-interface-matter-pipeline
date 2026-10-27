"""Run the once-admitted checker, retaining raw output and runtime evidence."""
import hashlib,json,os,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parent
targets=[root/name for name in ('RESULT.json','STDERR.txt','RUN_METADATA.json')]
if any(x.exists() for x in targets): raise RuntimeError('Existing evidence; no automatic retry')
gatepath=root/'INDEPENDENT_GATE.json'; gate=json.loads(gatepath.read_text())
if gate.get('decision')!='APPROVED_FOR_ONE_BOUNDED_EXECUTION': raise RuntimeError('Gate not approved')
for name,sha in gate['frozen_hashes'].items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=sha: raise RuntimeError('Frozen bytes changed: '+name)
env=os.environ.copy()
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'): env[key]='1'
start=datetime.now(timezone.utc).isoformat(); t=time.monotonic()
proc=subprocess.run([sys.executable,'-I',str(root/'stiffness.py')],capture_output=True,env=env,timeout=120)
targets[0].write_bytes(proc.stdout); targets[1].write_bytes(proc.stderr)
meta={'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-t,'returncode':proc.returncode,'python':sys.version,'executable':sys.executable,'blas_threads':1,'gate_sha256':hashlib.sha256(gatepath.read_bytes()).hexdigest(),'stdout_sha256':hashlib.sha256(proc.stdout).hexdigest(),'stderr_sha256':hashlib.sha256(proc.stderr).hexdigest()}
targets[2].write_text(json.dumps(meta,indent=2)+'\n'); print(json.dumps(meta,indent=2))
if proc.returncode:
    print(proc.stderr.decode()); raise SystemExit(proc.returncode)
r=json.loads(proc.stdout)['result']; print(json.dumps({'classification':r['classification'],'combined':{k:v['outward_decimal_18'] for k,v in r['combined'].items()},'upper_wall_dominates':r['upper_wall_dominates']},indent=2))
