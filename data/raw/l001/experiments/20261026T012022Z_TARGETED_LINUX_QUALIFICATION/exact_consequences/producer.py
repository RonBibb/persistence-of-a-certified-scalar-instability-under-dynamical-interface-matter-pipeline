"""Linux-only replay of unchanged complete saved-data consequence/checker programs."""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[1]
PYTHON_HASH = 'c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
CASES = (
    ('curvature', '20261013T073517Z_PAPER_A_CURVATURE_RESPONSE',
     'curvature_response.py', 'RESULT.json', 'reviewer_audit.py'),
    ('openness', '20261013T073517Z_PAPER_A_CURVATURE_RESPONSE',
     'global_openness.py', 'GLOBAL_OPENNESS_RESULT.json', 'reviewer_openness_audit.py'),
    ('stiffness', '20261013T081618Z_PAPER_A_STIFFNESS_COEFFICIENTS',
     'stiffness.py', 'RESULT.json', 'reviewer_audit.py'),
)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, obj):
    dest = HERE / name
    tmp = HERE / (name + '.tmp')
    with tmp.open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.flush()
        os.fsync(f.fileno())
    os.link(tmp, dest)
    tmp.unlink()

def verify(admission):
    assert admission['admitted'] is True
    assert digest(HERE/'FROZEN.json') == admission['frozen_sha256']
    frozen = json.loads((HERE/'FROZEN.json').read_text())
    assert str(Path(sys.executable).resolve()) == frozen['executable_realpath'], 'ACTUAL_INTERPRETER_DIFFERS'
    for name, value in frozen['files'].items():
        assert digest(Path(name)) == value, name
    assert sys.platform == 'linux' and sys.version_info[:3] == (3, 12, 3)
    assert digest(Path(sys.executable).resolve()) == PYTHON_HASH
    return frozen['runtime_files']

def run(path, label):
    started = time.monotonic()
    result = subprocess.run([sys.executable, '-I', '-B', str(path)],
        capture_output=True, text=True, timeout=50, check=False)
    record = dict(source=str(path), returncode=result.returncode,
                  stdout=result.stdout, stderr=result.stderr,
                  seconds=time.monotonic()-started)
    save(label + '_EXECUTION.json', record)
    assert result.returncode == 0 and result.stderr == '', label
    output = json.loads(result.stdout)
    save(label + '_OUTPUT.json', output)
    return output

def main():
    start = time.monotonic()
    admission = json.loads((HERE / 'ADMISSION.json').read_text())
    runtime_files = verify(admission)
    save('RUNTIME_START.json', dict(platform=sys.platform, version=sys.version,
        executable=str(Path(sys.executable).resolve()), python_sha256=PYTHON_HASH, runtime_files=runtime_files,
        scientific_arithmetic='unchanged Fraction programs; historical float conversions preserved'))
    rows = []
    for name, directory, owner, result_name, auditor in CASES:
        original = EXPERIMENTS / directory
        fresh = run(original / owner, name + '_producer')
        sealed = json.loads((original / result_name).read_text())
        assert fresh == sealed, name + '_COMPLETE_JSON_REPRODUCTION'
        checked = run(original / auditor, name + '_independent')
        assert checked['status'] == 'PASS', name + '_INDEPENDENT_CHECK'
        rows.append(dict(case=name, complete_producer_reproduced=True,
            complete_original_independent_checker_passed=True,
            historical_result=str(original / result_name)))
    assert verify(admission) == runtime_files
    save('RUNTIME_END.json', dict(runtime_files=runtime_files, all_file_hashes_rechecked=True))
    save('RESULT.json', dict(classification='PASS_COMPLETE_SAVED_CONSEQUENCES_LINUX',
        cases=rows, seconds=time.monotonic()-start, ode_executed=False,
        root_existence_reproved=False, historical_mac_provenance_unchanged=True,
        source_runtime_gates_passed=True))

if __name__ == '__main__':
    signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(TimeoutError('180-second total cap')))
    signal.alarm(180)
    try:
        main()
    except BaseException as exc:
        save('FAILURE.json', dict(classification='QUALIFICATION_INCOMPLETE', error=repr(exc),
             no_rescore=True, no_successor_authorized=True))
        raise
    finally:
        signal.alarm(0)
