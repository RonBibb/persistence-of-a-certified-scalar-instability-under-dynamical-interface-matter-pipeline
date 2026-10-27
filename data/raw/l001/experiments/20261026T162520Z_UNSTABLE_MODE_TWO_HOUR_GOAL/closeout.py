"""One-shot read-only evidence verification and local closeout publication."""
import sys
sys.dont_write_bytecode = True
import hashlib, json, os, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
DEADLINE = 1793039120
checks = 0

def need(value, label):
    global checks
    if not value:
        raise AssertionError(label)
    checks += 1

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def put(name, obj):
    target = ROOT / name
    temporary = ROOT / (name + '.tmp')
    with temporary.open('x') as stream:
        json.dump(obj, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    os.chmod(temporary, 0o444)
    os.link(temporary, target)
    temporary.unlink()
    fd = os.open(ROOT, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def closure(binding):
    obj = read(binding)
    for group in ('inputs', 'sources', 'runtime'):
        for path, digest in obj.get(group, {}).items():
            need(sha(path) == digest, 'BOUND_FILE:' + path)

def main():
    need(sys.platform == 'linux', 'LINUX_ONLY')
    need(time.time() < DEADLINE, 'WITHIN_GOAL')
    need(not (ROOT / 'CLOSEOUT.json').exists(), 'ONE_SHOT')
    terminal = ROOT / 'VERIFICATION_TERMINAL.json'
    need(sha(terminal) == '99a84f01a1f86cd79802bb573bea76d0d1975fcc21e60fadaf18522ca6c9310a', 'VERIFICATION_PIN')
    record = read(terminal)
    need(record['pass_status'], 'VERIFICATION_PASS')
    for name, key in [('VERIFICATION.json','result_sha256'), ('VERIFICATION_BINDING.json','binding_sha256'), ('verify_results.py','source_sha256')]:
        need(sha(ROOT/name) == record[key], 'VERIFICATION_RECORD:' + name)
    closure(ROOT/'VERIFICATION_BINDING.json')
    terminals = read(ROOT/'VERIFICATION.json')['terminals']
    for path, entry in terminals.items():
        need(sha(BASE/path) == entry['sha256'], 'PREVIOUS_TERMINAL:' + path)
    for name, pin, source in [
        ('20261026_GROWING_NEUTRAL_COMPONENT_MAP', 'a189065e25d7f9eb386ca71ee4baf8d99c5a99a78cd60884e37afe7c40d48753', 'check.py'),
        ('20261026_GROWING_NEUTRAL_COMPATIBILITY', '46a3b24af5e15aa9f08894fe5612b18efeb1fc2b33901b0894523e59eb841f6f', 'run.py')]:
        directory = BASE/name
        need(sha(directory/'TERMINAL.json') == pin, 'NEW_TERMINAL_PIN:' + name)
        entry = read(directory/'TERMINAL.json')
        need(entry['pass_status'], 'NEW_TERMINAL_PASS:' + name)
        for filename, key in [('RESULT.json','result_sha256'), ('BINDING.json','binding_sha256'), (source,'source_sha256')]:
            need(sha(directory/filename) == entry[key], 'NEW_RECORD:' + name + '/' + filename)
        if 'derivation_sha256' in entry:
            need(sha(directory/'DERIVATION.txt') == entry['derivation_sha256'], 'DERIVATION_PIN')
        closure(directory/'BINDING.json')
        terminals[name+'/TERMINAL.json'] = dict(sha256=pin, pass_status=True)
    active = []
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit() or int(directory.name) == os.getpid():
            continue
        try:
            cmd = (directory/'cmdline').read_bytes().split(b'\0')
        except (FileNotFoundError, PermissionError, ProcessLookupError):
            continue
        if cmd and b'python' in cmd[0] and any(b'/experiments/20261026_GROWING_' in arg for arg in cmd):
            active.append(dict(pid=int(directory.name), command=[x.decode(errors='replace') for x in cmd if x]))
    need(not active, 'NO_GOAL_NUMERICAL_WORKERS')
    documents = {name:sha(ROOT/name) for name in ['RESULTS.md','NEXT_TEST.md','CONDITIONAL_MAJORANT.md','SOURCE_NORM_SCOPING.md','REVIEW.md']}
    output = dict(pass_status=True, classification='TWO_HOUR_GROWING_MODE_BOUNDED_PROGRESS_CLOSEOUT',
                  checked_at_unix=time.time(), deadline_unix=DEADLINE,
                  checks=checks, terminal_count=len(terminals), terminals=terminals,
                  documents=documents, active_goal_numerical_workers=active,
                  verification_terminal_sha256=sha(terminal),
                  scope='Hash closure and operational closeout, not a new ODE or independent replay of the full analytic proof.',
                  unresolved='Common analytic inverse/source estimate, convergence and quantitative finite-amplitude remainder.')
    put('CLOSEOUT.json', output)
    put('CLOSEOUT_TERMINAL.json', dict(pass_status=True, closeout_sha256=sha(ROOT/'CLOSEOUT.json'), source_sha256=sha(__file__)))
    print(json.dumps(dict(pass_status=True, checks=checks, terminal_count=len(terminals), active_goal_numerical_workers=active)), flush=True)

if __name__ == '__main__':
    main()
