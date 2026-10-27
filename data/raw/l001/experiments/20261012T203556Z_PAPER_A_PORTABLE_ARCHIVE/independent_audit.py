#!/usr/bin/env python3
"""Independent byte audit and direct saved-record verifier replay, after owner runs."""
import datetime
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAYERS = {
    "authority": ("AUTHORITY_ARTIFACT_MANIFEST.json", "lin-static-theorem-publication-upgrade-20261005T050426Z/verify_upgrade.py"),
    "consolidation": ("CONSOLIDATION_ARTIFACT_MANIFEST.json", "lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py"),
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    assert Path.cwd().resolve() == Path('/private/tmp')
    out = HERE / 'independent_runs'
    out.mkdir(exist_ok=True)
    records = []
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for layer, (manifest_name, entry) in LAYERS.items():
        manifest = json.loads((HERE / manifest_name).read_text())
        for location, archive in [('primary', HERE / 'archive'), ('relocated', HERE / 'relocated/archive')]:
            checked = []
            for item in manifest['files']:
                relative = Path(item['archive_path'])
                assert not relative.is_absolute() and '..' not in relative.parts
                target = archive / relative
                assert not any(x.is_symlink() for x in [target, *target.parents])
                target.resolve().relative_to(archive.resolve())
                source = HERE.parent / item['origin_relative_to_experiments']
                data = target.read_bytes()
                assert data == source.read_bytes()
                assert digest(data) == item['sha256']
                checked.append(str(relative))
            stem = f'{layer}_{location}'
            owner_out = (HERE / 'runs' / (stem + '.stdout.json')).read_bytes()
            owner_err = (HERE / 'runs' / (stem + '.stderr.txt')).read_bytes()
            owner_meta = json.loads((HERE / 'runs' / (stem + '.metadata.json')).read_text())
            assert owner_meta['returncode'] == 0 and not owner_err
            assert owner_meta['stdout_sha256'] == digest(owner_out)
            assert owner_meta['stderr_sha256'] == digest(owner_err)
            assert Path(owner_meta['cwd']).resolve() == Path('/private/tmp')
            assert owner_meta['command'][-1] == str(archive)
            command = [sys.executable, '-I', '-B', str(archive / 'branches/02-event-horizon' / entry)]
            before = time.monotonic()
            result = subprocess.run(command, capture_output=True, timeout=120, cwd='/private/tmp')
            elapsed = time.monotonic() - before
            (out / (stem + '.stdout.json')).write_bytes(result.stdout)
            (out / (stem + '.stderr.txt')).write_bytes(result.stderr)
            assert result.returncode == 0 and not result.stderr
            assert result.stdout == owner_out
            payload = json.loads(result.stdout)
            assert payload['status'] == 'PASS'
            if layer == 'authority':
                assert payload['checks_passed'] == payload['checks_total'] == 23
                assert all(payload['checks'].values())
            else:
                assert Path(payload['root']) == archive
                assert len(payload['hash_checks']) == 14 and all(x['matches'] for x in payload['hash_checks'])
                assert len(payload['manifest_checks']) == 6
                assert all(not x['file_mismatches'] and x['terminal_manifest_binding_matches'] for x in payload['manifest_checks'])
                assert len(payload['d1_checks']) == 11 and all(payload['d1_checks'].values())
                assert len(payload['d2a_checks']) == 12 and all(payload['d2a_checks'].values())
            records.append({'layer': layer, 'location': location, 'files_checked': len(checked), 'canonical_bytes_match': True, 'confined_no_symlinks': True, 'owner_metadata_valid': True, 'owner_stdout_identical': True, 'command': command, 'cwd': '/private/tmp', 'returncode': result.returncode, 'elapsed_seconds': elapsed, 'stdout_sha256': digest(result.stdout), 'stderr_sha256': digest(result.stderr), 'status': payload['status']})
    report = {'schema': 'paper-a-independent-terminal-audit/v1', 'status': 'PASS', 'started_utc': started, 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'python_version': sys.version, 'audit_script_sha256': digest(Path(__file__).read_bytes()), 'runs': records, 'claim_boundary': 'Portable authority and exact saved-record reconstruction only; no new ODE producer, global-cover producer, spectrum, parameter, or physical evolution execution.'}
    (HERE / 'INDEPENDENT_TERMINAL_AUDIT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
