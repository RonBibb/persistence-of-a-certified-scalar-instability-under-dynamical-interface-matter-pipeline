import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
stem = HERE / 'runs/mode'
if stem.with_suffix('.metadata.json').exists():
    raise RuntimeError('refuse to overwrite completed run')
stem.parent.mkdir(exist_ok=True)
command = [sys.executable, '-I', '-B', str(HERE / 'mode_test.py')]
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
before = time.monotonic()
result = subprocess.run(command, capture_output=True, timeout=120)
stem.with_suffix('.stdout.json').write_bytes(result.stdout)
stem.with_suffix('.stderr.txt').write_bytes(result.stderr)
metadata = {'command': command, 'cwd': str(Path.cwd()), 'started_utc': started, 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - before, 'returncode': result.returncode, 'python_version': sys.version}
for key, path in [('code', HERE / 'mode_test.py'), ('design', HERE / 'MODE_TEST_DESIGN.md'), ('bindings', HERE / 'MODE_SOURCE_BINDINGS.json')]:
    metadata[key + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
metadata['stdout_sha256'] = hashlib.sha256(result.stdout).hexdigest()
metadata['stderr_sha256'] = hashlib.sha256(result.stderr).hexdigest()
stem.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
print(json.dumps(metadata))
raise SystemExit(result.returncode)
