"""Shared paths, frozen configuration, exact encodings and atomic records.

Line 02_lin_static, run 20261006T185122Z. Linux only. Every archive path below is
read-only input; every output is written inside this run directory.
"""
import hashlib
import json
import os
import platform
import resource
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
CODE = RUN / 'code'
OUT = RUN / 'outputs'
VER = RUN / 'verification'
RESEARCH = Path('/media/psf/Home/Research')
BRANCH = Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/'
              'collapse-horizon-research/branches')
NAMES = {
    'identity': '02-event-horizon/lin-c4-evolution-identity-r1-20261006T051000Z',
    'connected': '02-event-horizon/lin-c4-connected-branch-20261006T004500Z',
    'finite': '02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z',
    'native': '01-horizon-core/d1-native-cauchy-20261005T201829Z',
    'admission': '01-horizon-core/d1-evolution-admission-20261005T214600Z',
    'spatial': '01-horizon-core/d1-spatial-evolution-20261005T232000Z',
}
PACKET = {k: BRANCH / v for k, v in NAMES.items()}

CONFIG = {
    'level': 'fine_c4',
    'cases': [0, 3, 4],
    'epsilon_targets': {'0': '0', '3': '1/200000', '4': '-1/200000'},
    'degrees': [160, 192],
    'dps': [80, 100],
    'old_rule_dps': 80,
    'rules': ['canonical', 'old80', 'floor_at_p'],
    'cells': 256,
    'degree': 28,
    'gate_absolute': '1e-50',
    'ambiguity_margin': '1e-40',
    'inherited_wall_row_gate_orders_0_2': '1e-10',
    'inherited_wall_row_gate_order_4': '1e-12',
    'arb_bits': 768,
    'address_space_bytes': 3 * 1024 ** 3,
    'producer_wall_seconds': 1200,
    'verifier_wall_seconds': 1800,
    'minimum_available_bytes': 8 * 1024 ** 3,
    'layout': 'sequential: one producer process, then one verifier process; one arithmetic thread each',
}

ENV = {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0', 'PYTHONNOUSERSITE': '1',
       'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}


def real_paths():
    """Input/output locations of the production replay (all inputs read-only)."""
    return {'native': PACKET['native'], 'grid_dir': PACKET['spatial'] / 'inputs',
            'spatial_root': PACKET['spatial'], 'admission_verification': PACKET['admission'] / 'VERIFICATION.json',
            'finite': PACKET['finite'], 'connected_audit': PACKET['connected'] / 'INDEPENDENT_AUDIT.json',
            'identity': PACKET['identity'], 'out': OUT, 'verification': VER, 'status': RUN / 'status.json',
            'level': CONFIG['level'], 'cases': CONFIG['cases'], 'degrees': CONFIG['degrees'], 'dps': CONFIG['dps'],
            'old_rule_dps': CONFIG['old_rule_dps'], 'freeze': RUN / 'FREEZE.json', 'fixture': False}

GATE = Fraction(1, 10 ** 50)
AMBIGUITY = Fraction(1, 10 ** 40)


def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def plain(x):
    """Cast numpy/flint/Fraction scalars to JSON-native values; reject floats that are not finite."""
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    if isinstance(x, bool) or x is None or isinstance(x, (int, str)):
        return x
    if type(x).__module__ == 'numpy' and type(x).__name__ in ('bool', 'bool_'):
        return bool(x)
    if isinstance(x, Fraction):
        return str(x)
    if isinstance(x, float):
        if x != x or x in (float('inf'), float('-inf')):
            raise ArithmeticError('Nonfinite float in record')
        return x
    raise TypeError('Unserializable record value of type ' + type(x).__name__)


def atomic(path, data, immutable=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if immutable and path.exists():
        raise RuntimeError('Refuse to overwrite immutable record: ' + str(path))
    text = json.dumps(plain(data), indent=1, sort_keys=True, allow_nan=False) + '\n'
    fd, name = tempfile.mkstemp(prefix=path.name + '.uncommitted-', dir=path.parent)
    with os.fdopen(fd, 'w') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(name, path)
    if immutable:
        path.chmod(0o444)


def exact_mpf(x):
    """Exact rational value of a finite mpmath mpf (sign, mantissa, exponent, bitcount)."""
    sign, man, exp, bc = x._mpf_
    if bc < 0 or (man == 0 and exp != 0):
        raise ArithmeticError('Nonfinite mpf')
    value = Fraction(man) * (Fraction(2) ** exp if exp >= 0 else Fraction(1, 2 ** (-exp)))
    return -value if sign else value


def encode_mpf(x):
    """Lossless [signed mantissa, binary exponent] encoding of a finite mpf."""
    sign, man, exp, bc = x._mpf_
    if bc < 0 or (man == 0 and exp != 0):
        raise ArithmeticError('Nonfinite mpf')
    return [-man if sign else man, exp]


def decode_pair(pair):
    man, exp = int(pair[0]), int(pair[1])
    return Fraction(man) * (Fraction(2) ** exp if exp >= 0 else Fraction(1, 2 ** (-exp)))


def exact_decimal(text):
    """Exact rational value of a stored decimal, scientific or rational literal."""
    return Fraction(str(text))


def check_environment():
    for key, value in ENV.items():
        if os.environ.get(key) != value:
            raise RuntimeError('Runtime environment ' + key + ' must be ' + value)


def limit_address_space():
    """Apply the declared ceiling, keeping any stricter inherited limit."""
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    target = CONFIG['address_space_bytes']
    for inherited in (soft, hard):
        if inherited != resource.RLIM_INFINITY and inherited < target:
            target = inherited
    resource.setrlimit(resource.RLIMIT_AS, (target, target))
    return list(resource.getrlimit(resource.RLIMIT_AS))


def capacity():
    info = Path('/proc/meminfo').read_text().splitlines()
    available = int(next(line.split()[1] for line in info if line.startswith('MemAvailable:'))) * 1024
    return {'utc': now(), 'available_bytes': available, 'load1': os.getloadavg()[0], 'cpus': os.cpu_count()}


def runtime_fingerprint():
    """Interpreter and arithmetic-library bytes, bound as the predecessor bound them."""
    import mpmath
    rows = {'python': platform.python_version(), 'mpmath': mpmath.__version__,
            'executable': str(Path(sys.executable).resolve())}
    paths = list(Path(mpmath.__file__).resolve().parent.rglob('*.py'))
    try:
        import flint
        root = Path(flint.__file__).resolve().parent
        rows['flint'] = flint.__version__
        rows['flint_path'] = str(root)
        paths += list(root.rglob('*.so'))
        sibling = root.parent / 'python_flint.libs'
        if sibling.exists():
            paths += list(sibling.glob('*'))
    except ImportError:
        rows['flint'] = None
    paths.append(Path(sys.executable).resolve())
    rows['libraries'] = {str(p): sha(p) for p in sorted(paths) if p.is_file()}
    return rows


def source_hashes():
    files = sorted(p for p in CODE.rglob('*.py'))
    rows = {str(p.relative_to(RUN)): sha(p) for p in files}
    rows['CONTRACT.md'] = sha(RUN / 'CONTRACT.md')
    return rows


def freeze_guard(path=None, sources=None, runtime=None):
    """Recheck the frozen binding; return its SHA-256 and content.

    The optional arguments exist only so preflight can exercise rejections on a fixture.
    """
    path = RUN / 'FREEZE.json' if path is None else Path(path)
    if not path.exists():
        raise RuntimeError('Run is not frozen')
    frozen = read(path)
    if frozen['config'] != CONFIG:
        raise RuntimeError('Changed configuration')
    if frozen['sources'] != (source_hashes() if sources is None else sources):
        raise RuntimeError('Changed source')
    for name, digest in frozen['inputs'].items():
        if sha(name) != digest:
            raise RuntimeError('Changed input ' + name)
    if frozen['runtime'] != (runtime_fingerprint() if runtime is None else runtime):
        raise RuntimeError('Changed runtime')
    return sha(path), frozen
