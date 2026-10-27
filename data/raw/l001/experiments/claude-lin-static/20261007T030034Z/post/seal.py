"""Publication-only sealing for run 20261007T030034Z: terminal process check by recorded PIDs, and manifest.

Computes no scientific quantity; not one of the frozen sources in code/. Usage: python3 -B post/seal.py
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
NAMES = ('reprep.py', 'assemble4.py', 'verify4.py', 'preflight4.py', 'campaign.sh', 'slot_run.sh')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def recorded_pids():
    pids = set()
    for p in (RUN / 'logs').glob('*.pid'):
        text = p.read_text().strip()
        if text.isdigit():
            pids.add(int(text))
    for p in list((RUN / 'outputs').glob('*/*.json')) + list((RUN / 'verification').glob('*.json')):
        try:
            body = json.loads(p.read_text())
        except ValueError:
            continue
        if isinstance(body, dict) and isinstance(body.get('pid'), int):
            pids.add(body['pid'])
    return sorted(pids)


def live(pids):
    rows = []
    for pid in pids:
        try:
            cmd = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode(errors='replace')
        except OSError:
            continue
        if RUN.name in cmd and any(n in cmd for n in NAMES):
            rows.append([pid, cmd])
    return rows


def main():
    utc = datetime.now(timezone.utc).isoformat()
    pids = recorded_pids()
    alive = live(pids)
    check = {'utc': utc, 'run': RUN.name, 'recorded_pids_checked': pids, 'live_recorded_processes': alive, 'terminal': not alive,
             'method': 'recorded PIDs only (logs/*.pid and record pid fields), /proc/<pid>/cmdline; no process-name search',
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
