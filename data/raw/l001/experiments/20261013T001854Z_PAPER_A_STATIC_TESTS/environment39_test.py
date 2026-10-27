"""Second-interpreter test of two immutable, previously replayed entrypoints."""
import datetime
import hashlib
import json
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / '20261012T203556Z_PAPER_A_PORTABLE_ARCHIVE'
ARCHIVE = PRIOR / 'archive'
PYTHON = '/usr/bin/python3'
ENTRIES = {
    'authority': 'branches/02-event-horizon/lin-static-theorem-publication-upgrade-20261005T050426Z/verify_upgrade.py',
    'consolidation': 'branches/02-event-horizon/lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py',
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main():
    if Path.cwd().resolve() != Path('/private/tmp').resolve():
        raise ValueError('run from unrelated /private/tmp')
    target = HERE / 'ENVIRONMENT39_RESULT.json'
    if target.exists():
        raise RuntimeError('refuse to overwrite result')
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    version = subprocess.run([PYTHON, '-I', '-B', '-c', 'import sys; print(sys.version)'], capture_output=True, text=True, timeout=15)
    if version.returncode or not version.stdout.startswith('3.9.6 '):
        raise RuntimeError('unexpected interpreter: ' + version.stdout + version.stderr)
    manifests, checked = {}, set()
    for layer in ENTRIES:
        path = PRIOR / (layer.upper() + '_ARTIFACT_MANIFEST.json')
        manifests[layer] = sha(path.read_bytes())
        manifest = json.loads(path.read_text())
        for record in manifest['files']:
            relative = Path(record['archive_path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('unsafe archive path')
            source = ARCHIVE / relative
            if any(p.is_symlink() for p in [source, *source.parents]):
                raise ValueError('archive symlink')
            source.resolve().relative_to(ARCHIVE.resolve())
            if sha(source.read_bytes()) != record['sha256']:
                raise ValueError('immutable archive byte mismatch')
            checked.add(str(relative))
    runs = []
    output = HERE / 'runs'
    output.mkdir(exist_ok=True)
    for layer, entrypoint in ENTRIES.items():
        old_stdout = (PRIOR / 'runs' / (layer + '_primary.stdout.json')).read_bytes()
        old_metadata_path = PRIOR / 'runs' / (layer + '_primary.metadata.json')
        old_metadata = json.loads(old_metadata_path.read_text())
        if sha(old_stdout) != old_metadata['stdout_sha256'] or not old_metadata['python_version'].startswith('3.14.4 ') or old_metadata['returncode'] != 0:
            raise ValueError('prior reference output invalid')
        command = [PYTHON, '-I', '-B', str(ARCHIVE / entrypoint)]
        before = time.monotonic()
        run_started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        completed = subprocess.run(command, capture_output=True, timeout=120)
        elapsed = time.monotonic() - before
        stem = output / ('environment39_' + layer)
        stem.with_suffix('.stdout.json').write_bytes(completed.stdout)
        stem.with_suffix('.stderr.txt').write_bytes(completed.stderr)
        try:
            status = json.loads(completed.stdout).get('status')
        except (ValueError, AttributeError):
            status = None
        metadata = {'layer': layer, 'command': command, 'cwd': str(Path.cwd()), 'started_utc': run_started, 'elapsed_seconds': elapsed, 'returncode': completed.returncode, 'python_version': version.stdout.strip(), 'stdout_sha256': sha(completed.stdout), 'stderr_sha256': sha(completed.stderr), 'prior_metadata_sha256': sha(old_metadata_path.read_bytes()), 'prior_python_version': old_metadata['python_version'], 'prior_stdout_sha256': sha(old_stdout), 'stdout_byte_identical_to_314': completed.stdout == old_stdout, 'status': status, 'passed': completed.returncode == 0 and completed.stderr == b'' and status == 'PASS' and completed.stdout == old_stdout}
        stem.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        runs.append(metadata)
    result = {'schema': 'paper-a-second-interpreter-test/v1', 'status': 'PASS' if all(x['passed'] for x in runs) else 'FAIL', 'started_utc': started, 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'integrity_prerequisite_unique_files': len(checked), 'prior_manifest_sha256': manifests, 'code_sha256': sha(Path(__file__).read_bytes()), 'design_sha256': sha((HERE / 'ENVIRONMENT39_TEST_DESIGN.md').read_bytes()), 'runs': runs, 'claim_boundary': 'Two original saved-evidence entrypoints on macOS Python3.9.6 versus sealed3.14.4 outputs; no Linux or numerical producer test.'}
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'files_checked': len(checked), 'runs': len(runs)}))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)

if __name__ == '__main__':
    main()
