"""Publication-only sealing for run 20261006T205203Z: terminal process check and manifest.

Computes no scientific quantity; not one of the frozen sources in code/. Usage: python3 -B post/seal.py
"""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    utc = datetime.now(timezone.utc).isoformat()
    ps = subprocess.run(['ps', '-eo', 'pid,etimes,args'], capture_output=True, text=True, check=True).stdout.splitlines()
    live = [line.strip() for line in ps if RUN.name in line and any(k in line for k in ('budget.py', 'verify2.py', 'preflight2.py', 'assemble.py'))]
    check = {'utc': utc, 'run': RUN.name, 'matching_processes': live, 'terminal': not live,
             'scope': 'Processes of this run only; other lines and jobs were not inspected or disturbed.'}
    target = RUN / 'FINAL_PROCESS_CHECK.json'
    if target.exists():
        raise RuntimeError('Process check already recorded')
    target.write_text(json.dumps(check, indent=1, sort_keys=True) + '\n')
    target.chmod(0o444)
    freeze = json.loads((RUN / 'FREEZE.json').read_text())
    unchanged_sources = all(sha(RUN / k) == v for k, v in freeze['sources'].items())
    unchanged_inputs = all(sha(k) == v for k, v in freeze['inputs'].items())
    verification = json.loads((RUN / 'verification' / 'VERIFICATION.json').read_text())
    entries = [{'path': str(p.relative_to(RUN)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
               for p in sorted(RUN.rglob('*')) if p.is_file() and p.name != 'MANIFEST.json' and '.uncommitted-' not in p.name]
    manifest = {'sealed_utc': utc, 'run': RUN.name, 'line': '02_lin_static', 'guard': sha(RUN / 'FREEZE.json'),
                'classification': verification['classification'], 'verifier_resolved': verification['resolved'],
                'frozen_sources_unchanged': unchanged_sources, 'frozen_inputs_unchanged': unchanged_inputs,
                'terminal_process_check': check['terminal'], 'entries': entries,
                'note': 'Integrity record of this run directory; not a scientific certificate.'}
    (RUN / 'MANIFEST.json').write_text(json.dumps(manifest, indent=1, sort_keys=True) + '\n')
    (RUN / 'MANIFEST.json').chmod(0o444)
    print(json.dumps({'entries': len(entries), 'terminal': check['terminal'], 'sources_unchanged': unchanged_sources,
                      'inputs_unchanged': unchanged_inputs, 'classification': manifest['classification']}))


if __name__ == '__main__':
    main()
