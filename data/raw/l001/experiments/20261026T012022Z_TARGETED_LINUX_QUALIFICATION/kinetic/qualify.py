"""Linux exact saved-witness replay; unchanged mathematical checker."""
import sys
sys.dont_write_bytecode = True
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import signal
import time
import traceback

HERE = Path(__file__).resolve().parent
RESEARCH = Path('/media/psf/Home/Research')
PACKET = RESEARCH / 'papers/ab-bridge-feasibility/20261019_continuum_kinetic_143342'
CHECKER = PACKET / 'action_review/fraction_verifier/verify_saved_certificate.py'
OUTPUT = HERE / 'output'

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(name, value):
    target = HERE / name
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())

def runtime():
    modules = {}
    for name, module in list(sys.modules.items()):
        value = getattr(module, '__file__', None)
        if value and Path(value).is_file():
            modules[name] = {'path': str(Path(value).resolve()), 'sha256': digest(value)}
    native = {}
    for row in Path('/proc/self/maps').read_text().splitlines():
        fields = row.split(None, 5)
        if len(fields) == 6 and fields[5].startswith('/') and Path(fields[5]).is_file():
            native[fields[5]] = digest(fields[5])
    return {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'platform': platform.platform(), 'uname': list(os.uname()),
            'pid': os.getpid(), 'python': sys.version, 'executable': sys.executable,
            'executable_sha256': digest(sys.executable), 'affinity': sorted(os.sched_getaffinity(0)),
            'modules': modules, 'mapped_files': native}

def main():
    assert sys.platform == 'linux' and sys.version_info[:3] == (3, 12, 3)
    assert not OUTPUT.exists(), 'fresh output required'
    OUTPUT.mkdir()
    spec = importlib.util.spec_from_file_location('historical_fraction_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)

    def adapted_guard():
        admission_path = PACKET / 'FRACTION_VERIFIER_ADMISSION.json'
        admission = json.loads(admission_path.read_text())
        assert admission['admitted'] is True
        candidate = checker.bounded_path(PACKET, admission['candidate'])
        assert digest(candidate) == admission['candidate_sha256']
        for name, expected in json.loads(candidate.read_text())['files'].items():
            assert digest(checker.bounded_path(PACKET, name)) == expected, name
        for name, expected in admission['review_receipts'].items():
            assert digest(checker.bounded_path(PACKET, name)) == expected, name
        for item in json.loads((PACKET / 'INPUTS.json').read_text())['files']:
            source = Path(item['source'])
            relative = source.relative_to('/Users/ronbibb/Research')
            assert digest(RESEARCH / relative) == item['sha256'], str(source)
            assert digest(checker.bounded_path(PACKET, item['snapshot'])) == item['sha256']
        return digest(candidate), digest(admission_path)

    checker.guard = adapted_guard
    checker.DEADLINE = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=900)
    signal.signal(signal.SIGALRM, checker.interruption)
    signal.setitimer(signal.ITIMER_REAL, 900)
    save('RUNTIME_BEFORE.json', runtime())
    start = time.monotonic()
    try:
        result = checker.check_saved(PACKET / 'certificate',
                   'c3b725099ddd7683a49aaf8563cd13b5f09f5c7118942e728c2eb384bc1dfe81', OUTPUT)
        assert result['status'] == 'PASS_EXACT_FRACTION_SAVED_CERTIFICATE_AND_COARSE_GATES'
        assert result['complete'] is True
        assert result['verified_cells'] == result['total_cells'] == 16365
        assert all(result['gates'].values()) and result['certified_half_S_gate'] is True
        adapted_guard()
        save('RUNTIME_AFTER.json', runtime())
        save('RESULT.json', {'status': 'PASS_COMPLETE_LINUX_KINETIC_WITNESS',
             'verified_cells': result['verified_cells'], 'wall_seconds': time.monotonic()-start,
             'historical_checker_sha256': digest(CHECKER), 'new_ode_solves': 0,
             'root_existence': 'inherited, separately linked',
             'verifier_result_sha256': digest(OUTPUT / 'VERIFICATION_RESULT.json')})
    except BaseException as exc:
        save('FAILURE.json', {'type': type(exc).__name__, 'message': str(exc),
             'stage': checker.STAGE, 'traceback': traceback.format_exc(),
             'classification': 'UNACCEPTED_REQUIRES_FAILURE_TRIAGE'})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)

if __name__ == '__main__':
    main()
