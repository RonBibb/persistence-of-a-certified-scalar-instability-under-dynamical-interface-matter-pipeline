#!/usr/bin/env python3
"""Independent exact-Fraction validation of SAVED cells; never advances an IVP."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
from fractions import Fraction as F
import argparse
import datetime
import gzip
import hashlib
import json
import os
import signal
import subprocess
import traceback

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent.parent
DEADLINE = datetime.datetime.fromisoformat('2026-10-19T16:03:42+00:00')
BITS = 192
DENOMINATOR = 1 << BITS
STEP = F(1, 8192)
NAMES = ['W', 'H', 'Phi', 'T', 'Ewarp', 'q']
STAGE = {'stage': 'startup'}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def utc():
    return datetime.datetime.now(datetime.timezone.utc)


def write_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('wb') as stream:
        stream.write(canonical(data) + b'\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def rational(value):
    if isinstance(value, float):
        raise TypeError('Binary floating input forbidden')
    return F(value)


class Segment:
    """Exact rational endpoint interval: no grid rounding or producer imports."""
    __slots__ = ('left', 'right')

    def __init__(self, left, right=None):
        self.left = rational(left)
        self.right = self.left if right is None else rational(right)
        if self.left > self.right:
            raise ValueError('Reversed rational segment')

    @staticmethod
    def of(value):
        return value if isinstance(value, Segment) else Segment(value)

    def __add__(self, other):
        other = Segment.of(other)
        return Segment(self.left + other.left, self.right + other.right)

    __radd__ = __add__

    def __neg__(self):
        return Segment(-self.right, -self.left)

    def __sub__(self, other):
        return self + -Segment.of(other)

    def __rsub__(self, other):
        return Segment.of(other) + -self

    def __mul__(self, other):
        other = Segment.of(other)
        values = [a * b for a in (self.left, self.right)
                  for b in (other.left, other.right)]
        return Segment(min(values), max(values))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = Segment.of(other)
        if other.left <= 0 <= other.right:
            raise ZeroDivisionError('Rational denominator contains zero')
        return self * Segment(1 / other.right, 1 / other.left)

    def squared(self):
        ends = (self.left * self.left, self.right * self.right)
        lower = F(0) if self.left <= 0 <= self.right else min(ends)
        return Segment(lower, max(ends))

    def contains(self, other):
        other = Segment.of(other)
        return self.left <= other.left and other.right <= self.right

    def strictly_contains(self, other):
        other = Segment.of(other)
        return self.left < other.left and other.right < self.right

    def union(self, other):
        return Segment(min(self.left, other.left), max(self.right, other.right))

    def exact_equal(self, other):
        return self.left == other.left and self.right == other.right

    def dump(self):
        return [str(self.left), str(self.right)]


def saved_vector(value):
    if not isinstance(value, list) or len(value) != 6:
        raise ValueError('Saved state must have six components')
    result = []
    for pair in value:
        if not isinstance(pair, list) or len(pair) != 2:
            raise ValueError('Malformed saved dyadic component')
        result.append(Segment(F(int(pair[0]), DENOMINATOR),
                              F(int(pair[1]), DENOMINATOR)))
    return result


def vector_contains(outer, inner, strict=False):
    if len(outer) != 6 or len(inner) != 6:
        return False
    test = 'strictly_contains' if strict else 'contains'
    return all(getattr(a, test)(b) for a, b in zip(outer, inner))


def vector_union(first, second):
    return [a.union(b) for a, b in zip(first, second)]


def initial_exact(model):
    constants = {name: Segment(value)
                 for name, value in model['model_exact'].items()}
    phi = Segment(*model['A'])
    shift = phi - constants['v0']
    H = -(constants['lambda_a'] + constants['gamma'] * shift.squared() / 2) / 6
    T = constants['gamma'] * shift / 2
    k = H.squared() - 1 - T.squared() / 12 + constants['m2'] * phi.squared() / 12
    return [Segment(0), H, phi, T, Segment(1), Segment(0)], k, constants


def vector_field(values, k, mass):
    W, H, phi, T, E, q = values
    return [H, -T.squared() / 3 - k * E.squared(), T,
            mass * phi - 4 * H * T, -H * E, E]


def coefficient_product(left, right, order):
    answer = Segment(0)
    for power in range(order + 1):
        answer = answer + left[power] * right[order - power]
    return answer


def exact_taylor(values, degree, k, mass):
    """Polynomial jet identity, independently evaluated in exact Fractions."""
    jets = [[value] for value in values]
    for n in range(degree):
        W, H, phi, T, E, q = jets
        T_squared = coefficient_product(T, T, n)
        E_squared = coefficient_product(E, E, n)
        H_T = coefficient_product(H, T, n)
        H_E = coefficient_product(H, E, n)
        derivative = [H[n], -T_squared / 3 - k * E_squared,
                      T[n], mass * phi[n] - 4 * H_T, -H_E, E[n]]
        for component in range(6):
            jets[component].append(derivative[component] / (n + 1))
    return jets


def exact_tube(point, fifth, low, high):
    """Same Horner enclosure form, exact arithmetic rather than rounded backend."""
    offset = Segment(low, high)
    result = []
    for polynomial, remainder in zip(point, fifth):
        value = remainder
        for coefficient in reversed(polynomial):
            value = coefficient + offset * value
        result.append(value)
    return result


def bounded_path(base, relative):
    path = Path(relative)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe saved relative path')
    return base / path


def guard():
    admission = json.loads((PACKET / 'FRACTION_VERIFIER_ADMISSION.json').read_text())
    if not admission['admitted']:
        raise RuntimeError('No independent saved-verifier admission')
    candidate = bounded_path(PACKET, admission['candidate'])
    if digest(candidate) != admission['candidate_sha256']:
        raise RuntimeError('Changed admitted verifier candidate')
    for name, expected in json.loads(candidate.read_text())['files'].items():
        if digest(bounded_path(PACKET, name)) != expected:
            raise RuntimeError('Changed verifier source or frozen input: ' + name)
    sources = json.loads((PACKET / 'INPUTS.json').read_text())
    for item in sources['files']:
        if (digest(Path(item['source'])) != item['sha256'] or
                digest(PACKET / item['snapshot']) != item['sha256']):
            raise RuntimeError('Changed original/input pair')
    return digest(candidate), digest(PACKET / 'FRACTION_VERIFIER_ADMISSION.json')


def check_saved(certificate, expected_pointer, output):
    STAGE.update(stage='admission_and_saved_input_guard')
    candidate_hash, admission_hash = guard()
    pointer_path = certificate / 'LATEST.json'
    if digest(pointer_path) != expected_pointer:
        raise RuntimeError('Saved pointer changed after its explicit freeze')
    pointer = json.loads(pointer_path.read_text())
    if not pointer['path'].startswith('checkpoints/'):
        raise RuntimeError('Saved payload outside checkpoint subtree')
    payload_path = bounded_path(certificate, pointer['path'])
    if digest(payload_path) != pointer['sha256']:
        raise RuntimeError('Saved payload digest mismatch')
    state = json.loads(payload_path.read_text())
    if (state['guard']['bits'] != BITS or state['guard']['order'] != 5 or
            F(state['guard']['step']) != STEP or state['guard']['chunk_cells'] != 256):
        raise RuntimeError('Unexpected saved proof protocol')
    guard_hash = hashlib.sha256(canonical(state['guard'])).hexdigest()
    if guard_hash != state['fingerprint']:
        raise RuntimeError('Producer guard self-consistency mismatch')
    for name, expected in state['guard']['files'].items():
        if digest(bounded_path(PACKET, name)) != expected:
            raise RuntimeError('Changed producer guard file: ' + name)
    if digest(certificate / 'CONTROLS.json') != state['control_sha256']:
        raise RuntimeError('Changed producer controls')
    model = json.loads((PACKET / 'inputs/14_21_14_04_MODEL.json').read_text())
    previous, k, constants = initial_exact(model)
    initial = previous[:]
    Dlo, Dhi = map(F, model['D'])
    if F(state['D_lo']) != Dlo or F(state['D_hi']) != Dhi:
        raise RuntimeError('Inherited endpoint box mismatch')
    expected_cells = (Dhi.numerator * STEP.denominator + Dhi.denominator - 1) // Dhi.denominator
    if state['total_cells'] != expected_cells:
        raise RuntimeError('Unexpected frozen cell count')
    time_value = F(0)
    index = 0
    collar = initial[:]
    event = None
    max_iterations = 0
    verified = []
    for chunk in state['completed_chunks']:
        if utc() >= DEADLINE:
            raise TimeoutError('Original saved-verifier deadline reached')
        path = bounded_path(certificate, chunk['path'])
        if digest(path) != chunk['sha256'] or chunk['start'] != index:
            raise RuntimeError('Saved chunk digest or ordering mismatch')
        records = json.loads(gzip.decompress(path.read_bytes()))
        if len(records) != chunk['end'] - chunk['start'] or not records:
            raise RuntimeError('Saved chunk length mismatch')
        for cell in records:
            if utc() >= DEADLINE:
                raise TimeoutError('Original saved-verifier deadline reached')
            STAGE.update(stage='exact_saved_cell_validation', index=index, s=str(time_value))
            if cell['index'] != index or F(cell['s']) != time_value:
                raise RuntimeError('Discontinuous saved cell index/time')
            width = F(cell['h'])
            if width != min(STEP, Dhi - time_value) or width <= 0:
                raise RuntimeError('Changed cell width or endpoint domain')
            box = saved_vector(cell['picard_box'])
            dt = Segment(0, width)
            image = [start + dt * rate for start, rate in
                     zip(previous, vector_field(box, k, constants['m2']))]
            if not vector_contains(box, image, strict=True):
                raise RuntimeError('Exact rational Picard image not strictly inside saved box')
            leading = exact_taylor(previous, 4, k, constants['m2'])
            fifth = [series[5] for series in exact_taylor(box, 5, k, constants['m2'])]
            required_whole = exact_tube(leading, fifth, F(0), width)
            required_end = exact_tube(leading, fifth, width, width)
            whole = saved_vector(cell['whole_cell'])
            endpoint = saved_vector(cell['endpoint'])
            if not vector_contains(whole, required_whole) or not vector_contains(endpoint, required_end):
                raise RuntimeError('Saved tube/endpoint fails exact rational Taylor enclosure')
            invariant = (whole[1].squared() - 1 - whole[3].squared() / 12 +
                         constants['m2'] * whole[2].squared() / 12 - k * whole[4].squared())
            if not invariant.contains(0) or whole[4].left <= 0:
                raise RuntimeError('Cell invariant/positive-coordinate consistency failed')
            overlap = time_value + width >= Dlo and time_value <= Dhi
            if overlap:
                required_event = exact_tube(leading, fifth, max(F(0), Dlo - time_value),
                                            min(width, Dhi - time_value))
                saved_event = saved_vector(cell['D_event_overlap'])
                if not vector_contains(saved_event, required_event):
                    raise RuntimeError('Saved moving-endpoint event misses rational enclosure')
                event = saved_event if event is None else vector_union(event, saved_event)
            elif 'D_event_overlap' in cell:
                raise RuntimeError('Spurious saved event cell')
            if not 1 <= cell['picard_iterations'] <= 32:
                raise RuntimeError('Invalid declared inclusion iteration count')
            max_iterations = max(max_iterations, cell['picard_iterations'])
            collar = vector_union(collar, whole)
            previous = endpoint
            time_value += width
            index += 1
        verified.append({'path': chunk['path'], 'sha256': chunk['sha256'],
                         'start': chunk['start'], 'end': index})
        write_atomic(output / 'PROGRESS.json', {'utc': utc().isoformat(),
                     'status': 'VERIFYING_SAVED_CERTIFICATE', 'verified_cells': index,
                     'total_cells': expected_cells, 'last_chunk': chunk['path'],
                     'new_background_or_response_solves': 0})
    if state['completed_cells'] != index or F(state['s']) != time_value:
        raise RuntimeError('Final saved endpoint count/time mismatch')
    if not all(a.exact_equal(b) for a, b in zip(previous, saved_vector(state['state']))):
        raise RuntimeError('Final payload endpoint differs from certified last cell')
    if state['max_picard_iterations'] != max_iterations:
        raise RuntimeError('Final payload inclusion iteration mismatch')
    saved_collar = saved_vector(state['whole_collar'])
    if not vector_contains(saved_collar, collar):
        raise RuntimeError('Final collar omits a saved certified tube')
    saved_event = saved_vector(state['D_event']) if state['D_event'] is not None else None
    if ((event is None) != (saved_event is None) or
            (event is not None and not vector_contains(saved_event, event))):
        raise RuntimeError('Final event omits a saved endpoint overlap')
    report = json.loads((certificate / 'RESULTS.json').read_text())
    if report['fingerprint'] != state['fingerprint'] or report['completed_unique_cells'] != index:
        raise RuntimeError('Producer result/payload mismatch')
    for name, segment in zip(NAMES, saved_collar):
        if not Segment(*report['whole_collar_state_bounds'][name]).contains(segment):
            raise RuntimeError('Reported collar bound omits certified component ' + name)
    if saved_event is not None:
        for name, segment in zip(NAMES, saved_event):
            if not Segment(*report['D_event_state_bounds'][name]).contains(segment):
                raise RuntimeError('Reported event bound omits certified component ' + name)
    reported_k = Segment(*report['k_bounds'])
    if not reported_k.contains(k):
        raise RuntimeError('Producer k bound misses exact launch image')
    W, H, phi, T, Ewarp, q = saved_collar
    mass_phi = constants['m2'] * phi.squared()
    gates = {'positive_k': reported_k.left > 0,
             'k_below_1_over_3000': reported_k.right < F(1, 3000),
             'positive_warp_reciprocal': Ewarp.left > 0,
             'Ewarp_below_8': Ewarp.right < 8,
             'mPhi_squared_below_1': mass_phi.right < 1,
             'negative_H': H.right < 0}
    if saved_event is not None:
        gates['positive_event_width'] = saved_event[5].left > 0
        ephi, eT, eH = saved_event[2], saved_event[3], saved_event[1]
        scalar = eT + constants['gamma'] * (ephi - constants['v1']) / 2
        metric = eH - (constants['lambda_b'] + constants['gamma'] *
                       (ephi - constants['v1']).squared() / 2) / 6
        for name, residual in [('upper_scalar_residual', scalar), ('upper_metric_residual', metric)]:
            if not residual.contains(0):
                raise RuntimeError('Exact-root upper-wall consistency enclosure excludes zero')
            if not Segment(*report['upper_wall_residual_rectangle_enclosures'][name]).contains(residual):
                raise RuntimeError('Reported upper-wall residual enclosure is too narrow')
    a = Segment(1) / Ewarp
    alpha = a * a * a
    coefficients = {'a': a, 'alpha': alpha, 'sigma_r': a * H, 'Phi_r': a * T,
                    'alpha_r': 3 * a * a * a * a * H,
                    'alpha_rr': alpha * (9 * reported_k + a * a * (12 - mass_phi)),
                    'first_integral': H.squared() - 1 - T.squared() / 12 + mass_phi / 12 - reported_k * Ewarp.squared(),
                    'mPhi_squared': mass_phi}
    for name, segment in coefficients.items():
        if not Segment(*report['whole_collar_coefficient_bounds'][name]).contains(segment):
            raise RuntimeError('Reported derived coefficient bound too narrow: ' + name)
    complete = time_value == Dhi and index == expected_cells
    if report['complete'] != complete or report['gates'] != gates:
        raise RuntimeError('Producer completion/gate booleans disagree with exact audit')
    x = F(1024, 165000)
    delta = F(39, 4) * x * (F(21, 5) + F(9, 2) * x)
    if not delta < F(1, 2) or F(report['strict_Delta_upper_rational']) != delta:
        raise RuntimeError('Rational all-mode comparison mismatch')
    passed = complete and all(gates.values())
    if report['certified_K_at_least_half_S'] != passed:
        raise RuntimeError('Producer theorem flag does not match certified gates')
    if digest(pointer_path) != expected_pointer or digest(payload_path) != pointer['sha256']:
        raise RuntimeError('Saved certificate changed during verification')
    output_data = {'utc': utc().isoformat(), 'status':
                   'PASS_EXACT_FRACTION_SAVED_CERTIFICATE_AND_COARSE_GATES' if passed else
                   'VALIDATED_SAVED_PREFIX_OR_INCONCLUSIVE_GATES',
                   'complete': complete, 'gates': gates,
                   'verified_cells': index, 'total_cells': expected_cells,
                   'verified_chunks': verified, 'pointer_sha256': expected_pointer,
                   'payload_sha256': pointer['sha256'], 'producer_result_sha256': digest(certificate / 'RESULTS.json'),
                   'verifier_candidate_sha256': candidate_hash, 'admission_sha256': admission_hash,
                   'backend': 'stdlib Fraction exact endpoints, no producer imports or dyadic rounding',
                   'certified_half_S_gate': passed, 'exact_root_existence': 'inherited; not re-solved',
                   'upper_wall_equalities': 'only inherited actual root subset',
                   'producer_coefficient_digest': 'not compared across different arithmetic backends',
                   'new_background_or_response_solves': 0,
                   'operation': 'inductive verification of saved Picard/Taylor certificates only',
                   'scope': 'numerical enclosure gate; final scientific acceptance remains separate'}
    write_atomic(output / 'VERIFICATION_RESULT.json', output_data)
    return output_data


def interruption(signum, frame):
    raise TimeoutError('Absolute verifier deadline during ' + STAGE['stage'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--expected-pointer-sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--worker', action='store_true')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not args.worker:
        guard()
        if any(output.iterdir()):
            raise RuntimeError('Require a fresh verifier output directory; preserve prior failures')
        duration = (DEADLINE - utc()).total_seconds() - 2
        if duration <= 0:
            raise TimeoutError('Original deadline elapsed; refusing saved verification')
        command = [sys.executable, '-B', str(Path(__file__).resolve()), '--worker',
                   '--certificate', args.certificate, '--expected-pointer-sha256',
                   args.expected_pointer_sha256, '--output', str(output)]
        with (output / 'worker.stdout').open('w') as stdout, (output / 'worker.stderr').open('w') as stderr:
            finished = subprocess.run(command, stdout=stdout, stderr=stderr,
                                      timeout=duration, check=False)
        if finished.returncode:
            raise RuntimeError('Saved certificate verification failed; see immutable failure records')
        print((output / 'VERIFICATION_RESULT.json').read_text())
        return
    remaining = (DEADLINE - utc()).total_seconds()
    if remaining <= 0:
        raise TimeoutError('Original deadline elapsed')
    signal.signal(signal.SIGALRM, interruption)
    signal.setitimer(signal.ITIMER_REAL, remaining)
    try:
        check_saved(Path(args.certificate).resolve(), args.expected_pointer_sha256, output)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        # A worker failure and a supervisor failure use separate files.
        if '--output' in sys.argv:
            destination = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
            suffix = 'WORKER_FAILURE.json' if '--worker' in sys.argv else 'SUPERVISOR_FAILURE.json'
            failure_path = destination / suffix
            serial = 0
            while failure_path.exists():
                serial += 1
                failure_path = destination / (suffix[:-5] + '_' + str(serial) + '.json')
            write_atomic(failure_path, {'utc': utc().isoformat(), 'stage': dict(STAGE),
                         'type': type(error).__name__, 'error': str(error),
                         'traceback': traceback.format_exc(), 'scientific_acceptance': False})
        raise
