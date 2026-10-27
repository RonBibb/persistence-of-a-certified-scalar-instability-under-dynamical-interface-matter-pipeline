"""Shared configuration, paths, exact conversions and records for run 20261007T030034Z.

Line 02_lin_static. Linux only. Archive paths are read-only inputs; outputs stay in this run.
"""
import hashlib
import json
import math
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
INHERITED = CODE / 'inherited'
OUT = RUN / 'outputs'
VER = RUN / 'verification'
RESEARCH = Path('/media/psf/Home/Research')
BRANCH = Path('/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/'
              'collapse-horizon-research/branches')
PACKET = {
    'identity': BRANCH / '02-event-horizon/lin-c4-evolution-identity-r1-20261006T051000Z',
    'connected': BRANCH / '02-event-horizon/lin-c4-connected-branch-20261006T004500Z',
    'finite': BRANCH / '02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z',
    'native': BRANCH / '01-horizon-core/d1-native-cauchy-20261005T201829Z',
    'spatial': BRANCH / '01-horizon-core/d1-spatial-evolution-20261005T232000Z',
    'admission': BRANCH / '01-horizon-core/d1-evolution-admission-20261005T214600Z',
}
RUN3 = RESEARCH / 'ClaudeCode/lines/02_lin_static/runs/20261006T230904Z'

CONFIG = {
    'cases': ['positive', 'negative'],
    'epsilon': {'positive': '1/200000', 'negative': '-1/200000'},
    'case_of': {'positive': 3, 'negative': 4},
    'phases': ['center', 'box'],
    'D_prime': ['33513605/16777216', '67027255/33554432'],
    'D_K': ['32727/16384', '32729/16384'],
    'step': '1/8192',
    'source_total_cells': 16365,
    'source_restart_cell': 16128,
    'source_event_cells': [16363, 16364],
    'finite_guard': '3e790eafe0a899d900e94ed8bf4adf2e268e5bab6bf96676ffd4680dc05845b4',
    'preconditioner_diagonal': ['-24/23', '1', '1'],
    'arb_bits': 768,
    'subcells': 64,
    'checkpoint_cells': 256,
    'degrees': [160, 192],
    'closure_radius_relative_log2': -27,
    'closure_absolute_log2': -600,
    'verifier_sample_blocks': [0, 31, 63],
    'address_space_bytes': 3 * 1024 ** 3,
    'job_wall_seconds': 3600,
    'verifier_wall_seconds': 3600,
    'minimum_available_bytes': 8 * 1024 ** 3,
    'prediction': {
        'P1': {'quantity': 'Q_c7(D_prime) / Q_c7(K)', 'interval': ['99/100', '1001/1000']},
        'P2': {'quantity': 'rad W0 and rad W1, D_prime / K', 'interval': ['99/100', '1001/1000']},
        'P3': {'quantity': 'rad G(c) new / accepted, for a, b0 and b1', 'interval': ['98/100', '102/100']},
        'P4': {'quantity': 'widths of X_prime(D_prime) / widths of X_prime(K), for a, b0 and b1', 'interval': ['98/100', '102/100']},
        'P5': {'quantity': 'a width of X_prime(D_prime) / a width of X', 'interval': ['90/100', '99/100']},
        'P6': {'quantity': 'A bound / run 3, with STATE_RADIUS dominant', 'interval': ['93/100', '1']},
        'P7': {'quantity': 'Phi bound / run 3, with STATE_RADIUS dominant', 'interval': ['98/100', '1']},
        'P8': {'quantity': 'rho_F <= 1/10 and rho_D >= 99/100 for Q_c7, Q_W0 and Q_W1, D_prime and K', 'rho_F_max': '1/10', 'rho_D_min': '99/100'},
        'P9': {'quantity': 'label', 'label': 'REPREPARED__A_DOMINATED_BY_STATE_RADIUS__PHI_DOMINATED_BY_STATE_RADIUS'},
        'denominator_floor_log2': -500},
    'attribution': {'floor_log2': -500, 'decisive_max': '1/10', 'other_min': '9/10', 'mu_bracket_max': '1/10',
                    'groups': ['F', 'S', 'B', 'Z', 'D'], 'variants': ['FULL', 'F', 'S', 'B', 'Z', 'D', 'ALL'],
                    'classes': {'F': 'MODE_JET_RADIUS', 'D': 'WALL_POSITION', 'S': 'BACKGROUND_JET_RADIUS', 'B': 'BACKGROUND_JET_RADIUS',
                                'Z': 'BACKGROUND_JET_RADIUS'}},
    'latest_campaign_start_utc': '2026-10-07T06:20:00Z',
    'layout': ('four phase jobs (center/box for each signed amplitude) launched together, then one material job per amplitude '
               'after all four phases exit 0, each an independent single-thread process through slot_run.sh (line cap 3); '
               'then the assembly job; then one verifier job per amplitude and one final verifier job; driven by code/campaign.sh, '
               'which waits only on the recorded PIDs of its own children'),
}

ENV = {'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONHASHSEED': '0', 'PYTHONNOUSERSITE': '1',
       'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}



def now():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def plain(x):
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


def atomic_bytes(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError('Refuse to overwrite immutable record: ' + str(path))
    fd, name = tempfile.mkstemp(prefix=path.name + '.uncommitted-', dir=path.parent)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(name, path)
    path.chmod(0o444)


def Q(text):
    return Fraction(str(text))


def fq(x):
    """flint fmpq to Fraction, exactly."""
    return Fraction(int(x.p), int(x.q))


def up_float(x):
    """Smallest binary64 not below the exact rational x."""
    x = Fraction(x)
    f = float(x)
    if Fraction(f) < x:
        f = math.nextafter(f, math.inf)
    return f


def down_float(x):
    x = Fraction(x)
    f = float(x)
    if Fraction(f) > x:
        f = math.nextafter(f, -math.inf)
    return f


def show(x, digits=4):
    """Upward-rounded decimal display of a nonnegative exact rational; signed values shown by magnitude."""
    if x is None:
        return None
    x = Fraction(x)
    if x == 0:
        return '0'
    sign = '-' if x < 0 else ''
    x = abs(x)
    e = len(str(x.numerator)) - len(str(x.denominator))
    p10 = (lambda k: Fraction(10) ** k if k >= 0 else Fraction(1, 10 ** (-k)))
    while p10(e) > x:
        e -= 1
    while p10(e + 1) <= x:
        e += 1
    m = x / p10(e - digits + 1)
    n = m.numerator // m.denominator + (1 if m.numerator % m.denominator else 0)
    if n >= 10 ** digits:
        n //= 10
        e += 1
    t = str(n)
    return f'{sign}{t[0]}.{t[1:]}e{e:+d}' if len(t) > 1 else f'{sign}{t}e{e:+d}'


def check_environment():
    for key, value in ENV.items():
        if os.environ.get(key) != value:
            raise RuntimeError('Runtime environment ' + key + ' must be ' + value)


def limit_address_space():
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
    import mpmath
    rows = {'python': platform.python_version(), 'mpmath': mpmath.__version__,
            'executable': str(Path(sys.executable).resolve())}
    paths = list(Path(mpmath.__file__).resolve().parent.rglob('*.py'))
    import flint
    root = Path(flint.__file__).resolve().parent
    rows['flint'] = flint.__version__
    paths += list(root.rglob('*.so'))
    sibling = root.parent / 'python_flint.libs'
    if sibling.exists():
        paths += list(sibling.glob('*'))
    paths.append(Path(sys.executable).resolve())
    rows['libraries'] = {str(p): sha(p) for p in sorted(paths) if p.is_file()}
    return rows


def source_hashes():
    rows = {str(p.relative_to(RUN)): sha(p) for p in sorted(list(CODE.rglob('*.py')) + list(CODE.glob('*.sh')))}
    rows['CONTRACT.md'] = sha(RUN / 'CONTRACT.md')
    return rows


def freeze_guard(path=None, sources=None, runtime=None):
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
