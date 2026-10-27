"""Capture one reviewer-approved saved-proof test without changing its inputs."""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test', choices=('global', 'isolation'))
    args = parser.parse_args()
    script = HERE / (args.test + '_test.py')
    design = HERE / (args.test.upper() + '_TEST_DESIGN.md')
    output = HERE / 'runs'
    output.mkdir(exist_ok=True)
    stem = output / args.test
    if stem.with_suffix('.metadata.json').exists():
        raise RuntimeError('refuse to overwrite a completed frozen run')
    command = [sys.executable, '-I', '-B', str(script)]
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    before = time.monotonic()
    completed = subprocess.run(command, capture_output=True, timeout=120)
    stem.with_suffix('.stdout.json').write_bytes(completed.stdout)
    stem.with_suffix('.stderr.txt').write_bytes(completed.stderr)
    meta = {'command': command, 'cwd': str(Path.cwd()), 'started_utc': start, 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'elapsed_seconds': time.monotonic() - before, 'returncode': completed.returncode, 'python_version': sys.version, 'code_sha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'design_sha256': hashlib.sha256(design.read_bytes()).hexdigest(), 'bindings_sha256': hashlib.sha256((HERE / 'SOURCE_BINDINGS.json').read_bytes()).hexdigest(), 'stdout_sha256': hashlib.sha256(completed.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(completed.stderr).hexdigest()}
    stem.with_suffix('.metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
    print(json.dumps(meta))
    raise SystemExit(completed.returncode)

if __name__ == '__main__':
    main()
