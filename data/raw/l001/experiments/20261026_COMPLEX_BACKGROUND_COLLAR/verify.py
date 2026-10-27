"""Independent exact-rational collar arithmetic audit; no background ODE replay."""
import sys
sys.dont_write_bytecode = True
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from fractions import Fraction as F
import signal
import traceback

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
FLOW = BASE / '20261026T033400Z_CUBIC_FULL_FLOW'
RESPONSE = BASE / '20261026_RESPONSE_AUDIT'
PRODUCER = '94ee07c44112592f13fdd5a16e440bf45fcea50b0d0e2971fc80d3b79d1619e0'
RESPONSE_HASH = '6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'
FROZEN = '625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read(path):
    return json.loads(Path(path).read_text())

def put(name, obj):
    dest = ROOT / name
    temp = ROOT / (name + '.tmp')
    with temp.open('x') as f:
        json.dump(obj, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.chmod(temp, 0o444)
    os.link(temp, dest)
    temp.unlink()
    fd = os.open(ROOT, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)

def run(lease):
    assert sys.platform == 'linux'
    assert not any((ROOT / n).exists() for n in ('AUDIT_RESULT.json', 'AUDIT_TERMINAL.json'))
    cpu, occupied = lease.acquire()
    signal.alarm(120)
    paths = [Path(__file__), ROOT/'check.py', ROOT/'RESULT.json', ROOT/'TERMINAL.json',
             ROOT/'BINDING.json', RESPONSE/'RESULT.json', RESPONSE/'TERMINAL.json',
             RESPONSE/'BINDING.json', FLOW/'FROZEN.json', FLOW/'production_TERMINAL.json',
             FLOW/'FLOW_primary.json', FLOW/'FLOW_independent.json',
             BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py']
    hashes = {str(p): sha(p) for p in paths}
    assert sha(ROOT/'check.py') == PRODUCER
    assert sha(ROOT/'RESULT.json') == 'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68'
    assert sha(ROOT/'BINDING.json') == 'e3be586835520d2d52f55e79741166d0b612fa8eab69fac016a457b9845dced7'
    assert sha(RESPONSE/'RESULT.json') == RESPONSE_HASH
    assert sha(FLOW/'FROZEN.json') == FROZEN
    terminal = read(ROOT/'TERMINAL.json')
    assert terminal['pass'] and terminal['result_sha256'] == sha(ROOT/'RESULT.json')
    assert terminal['binding_sha256'] == sha(ROOT/'BINDING.json')
    binding = read(ROOT/'BINDING.json')
    assert binding['source_sha256'] == PRODUCER and binding['audit_result_sha256'] == RESPONSE_HASH
    assert binding['parent_frozen_sha256'] == FROZEN
    rt = read(RESPONSE/'TERMINAL.json')
    assert rt['pass'] and rt['result_sha256'] == RESPONSE_HASH
    assert rt['binding_sha256'] == sha(RESPONSE/'BINDING.json')
    response = read(RESPONSE/'RESULT.json')
    assert response['pass'] and response['unresolved'] == []
    ft = read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256'] == FROZEN
    result = read(ROOT/'RESULT.json')
    assert result['pass'] and result['classification'] == 'FIXED_COMPLEX_BACKGROUND_COLLAR_DIAGNOSTIC'
    assert result['parameters_complexified'] is False
    assert result['nonlinear_majorant_constants_computed'] is False
    assert result['amplitude_radius_certified'] is False
    eps, radius = F(1, 1000), F(1, 20000)
    assert F(result['epsilon']) == eps and F(result['rho']) == radius
    assert F(result['inner_cauchy_radius']) == radius/2
    assert binding['tube_epsilon'] == str(eps) and binding['collar_radius'] == str(radius)
    assert set(response['arms']) == set(result['arms']) == {'primary', 'independent'}
    runtime_before = lease.observed()
    verified = {}
    for name in ('primary', 'independent'):
        path = FLOW / ('FLOW_' + name + '.json')
        assert sha(path) == ft['artifacts'][path.name]
        flow = read(path)
        klo, khi = map(F, flow['parameters']['k']['exact_bounds'])
        ext = response['arms'][name]['extrema']
        k, e, H, T, P, mass = (F(ext[s]) for s in ('k0', 'e0', 'H0', 'T0', 'P0', 'm0'))
        assert 0 < k == klo <= khi and e > 0
        assert min(H, T, P, mass) >= 0
        h, t, p, z = H+eps, T+eps, P+eps, F(8)+eps
        # Sup-norm polynomial vector field and Jacobian row sums.
        vector = max(h, t*t/F(3)+khi*z*z, t, mass*p+F(4)*h*t, h*z)
        jacobian = max(F(1), F(2)*t/F(3)+F(2)*khi*z,
                       mass+F(4)*(t+h), z+h)
        e2_change = eps*(F(16)+eps)
        t2_change = eps*(F(2)*T+eps)
        d = F(42)*k*e*e - F(2)*t2_change - F(108)*khi*e2_change
        j = F(42)*k*(e*e-e2_change)
        oscillator = F(18)*k*e*e-F(36)*khi*e2_change
        margins = {'picard_self_map':eps-radius*vector,
                   'picard_contraction':1-radius*jacobian,
                   'E_nonzero':e-eps, 'E_squared_realpart':e*e-e2_change,
                   'D_over_n2':d, 'J_over_n2':j, 'oscillator_over_n2':oscillator}
        assert all(v > 0 for v in margins.values())
        b = F(4)*(F(3)*h*t+mass*p)
        tprime = mass*p+F(4)*h*t
        values = {'vector_field_bound':vector, 'jacobian_bound':jacobian, **margins,
                  'drift_absolute':F(4)*h+b*t/d,
                  'potential_over_n2_absolute':mass+F(36)*khi*z*z+F(2)*t*t+b*tprime/d,
                  'inverse_A_absolute':(F(2)*t*t+F(108)*khi*z*z)/j}
        saved = result['arms'][name]
        assert saved['all_gates_pass'] is True
        assert {key:F(v) for key,v in saved['exact'].items()} == values
        verified[name] = {'exact':{key:str(v) for key,v in values.items()},
                          'positive_gates':len(margins), 'exact_fields':len(values)}
    runtime_after = lease.observed()
    assert runtime_before == runtime_after, 'RUNTIME_CHANGED'
    assert all(sha(p) == digest for p,digest in hashes.items()), 'INPUT_CHANGED'
    report = {'pass':True, 'classification':'BACKGROUND_COLLAR_ARITHMETIC_VERIFIED',
              'arms':verified, 'source_sha256':hashes[str(Path(__file__))],
              'producer_result_sha256':hashes[str(ROOT/'RESULT.json')],
              'inputs':hashes, 'cpu':cpu, 'occupied':occupied,
              'runtime_before':runtime_before, 'runtime_after':runtime_after,
              'scope':'Independent exact rational recomputation from authenticated audited extrema; inherited background ODE and E<=8 evidence, not ODE replay or a charged complex inverse/majorant/amplitude certificate.'}
    put('AUDIT_RESULT.json', report)
    put('AUDIT_TERMINAL.json', {'pass':True, 'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
                              'source_sha256':sha(__file__), 'producer_result_sha256':sha(ROOT/'RESULT.json')})

if __name__ == '__main__':
    lease = None
    try:
        # Lock helper only: no producer scientific implementation is imported.
        path = BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        spec = importlib.util.spec_from_file_location('collar_audit_lease', path)
        lease = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lease)
        lease.ROOT = ROOT
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('AUDIT_120_SECONDS')))
        run(lease)
    except BaseException as error:
        if not (ROOT/'AUDIT_RESULT.json').exists():
            put('AUDIT_RESULT.json', {'pass':False, 'classification':'TECHNICAL_INCOMPLETE',
                                     'error':repr(error), 'traceback':traceback.format_exc(),
                                     'source_sha256':sha(__file__)})
        if not (ROOT/'AUDIT_TERMINAL.json').exists():
            put('AUDIT_TERMINAL.json', {'pass':False, 'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
                                       'source_sha256':sha(__file__)})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:
                handle.close()
