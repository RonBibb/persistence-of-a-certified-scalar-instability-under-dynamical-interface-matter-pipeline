import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path
HERE = Path(__file__).resolve().parent
target = HERE / 'RUN_METADATA.json'
if target.exists(): raise RuntimeError('do not overwrite completed run')
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
before = time.monotonic()
command = [sys.executable, '-I', '-B', str(HERE / 'trace_test.py')]
run = subprocess.run(command, capture_output=True, timeout=90)
(HERE / 'RESULT.json').write_bytes(run.stdout)
(HERE / 'STDERR.txt').write_bytes(run.stderr)
meta = {'command': command, 'cwd': str(Path.cwd()), 'started_utc': started, 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic()-before, 'returncode': run.returncode, 'python': sys.version}
for key, name in [('code','trace_test.py'),('design','DESIGN.md'),('bindings','SOURCE_BINDINGS.json'),('stdout','RESULT.json'),('stderr','STDERR.txt')]: meta[key+'_sha256'] = hashlib.sha256((HERE/name).read_bytes()).hexdigest()
target.write_text(json.dumps(meta, indent=2)+'\n')
print(json.dumps(meta))
raise SystemExit(run.returncode)
