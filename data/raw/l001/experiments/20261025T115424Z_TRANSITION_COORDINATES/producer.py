"""One frozen two-level outward interval enclosure. No adaptive rescue."""
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import sys
import time

sys.dont_write_bytecode = True
sys.path.insert(0, '/home/parallels/research-runs/cap-interval-arb-2026-09-12')
import flint
from flint import arb, fmpq, ctx

ctx.prec = 256
ctx.threads = 1
HERE = Path(__file__).resolve().parent
START = time.monotonic()

def q(s):
    return arb(fmpq(str(s)))

def interval(lo, hi):
    return arb((lo+hi)/2, (hi-lo)/2)

def bounds(x):
    return x.lower().fmpq(), x.upper().fmpq()

def record(x):
    lo, hi = bounds(x)
    return {'lo':str(lo), 'hi':str(hi), 'width':str(hi-lo), 'display':str(x)}

def save(name, value):
    path = HERE / name
    with path.open('x') as stream:
        json.dump(value, stream, indent=2)
        stream.flush()
        os.fsync(stream.fileno())

def need(ok, message):
    if not ok:
        raise RuntimeError(message)

def rhs(y):
    a,H,P,T = y[:4]
    tp = 1-P+4*P**3-4*H*T
    out = [H*a, -T*T/3-3/(a*a), T, tp]
    if len(y)==8:
        p,b,c,d = y[4:]
        A = a*a*T*tp/18
        E = 1-a*a*T*T/18
        C = -1+12*P*P+4*T*T/3+a*a*tp*tp/18
        D = -4*H-A
        out += [A*p+E*c, A*b+E*d, C*p+D*c, C*b+D*d]
    return out

BG_RATES = [q('3'),q('5'),q('1/10'),q('2')]
RATES = BG_RATES+[q('1/10'),q('2'),q('2'),q('12')]
BG_LIMITS = [(fmpq(9,10),fmpq(11,10)),
             (fmpq(-21,10),fmpq(-19,10)),
             (fmpq(-1,100),fmpq(1,100)),
             (fmpq(-1,50),fmpq(1,50))]

def inside_exact(x, limits):
    lo,hi=bounds(x)
    return limits[0]<=lo and hi<=limits[1]

def step(y, hq, fun, rates, check_background=False):
    h = arb(hq)
    dt = interval(min(fmpq(0),hq),max(fmpq(0),hq))
    tube = [v+arb(0,(abs(h)*r).upper()) for v,r in zip(y,rates)]
    need(len(tube)==len(y), 'RATE_DIMENSION')
    if check_background:
        need(all(inside_exact(v,limit) for limit,v in zip(BG_LIMITS,tube[:4])), 'BACKGROUND_TUBE')
    f = fun(tube)
    need(len(f)==len(y), 'RHS_DIMENSION')
    need(all(b.contains_interior(v+dt*w) for b,v,w in zip(tube,y,f)), 'TUBE_CONTAINMENT')
    result = [v+h*w for v,w in zip(y,f)]
    need(all(v.is_finite() for v in result), 'NONFINITE')
    return result

def controls():
    tests = {}
    for sign in (-1,1):
        h = fmpq(sign,100)
        val = step([q('1')],h,lambda y:[q('1')],[q('2')])[0]
        need(val.contains(arb(1+h)), 'CONSTANT_CONTROL')
        val = step([q('1')],h,lambda y:y,[q('2')])[0]
        need(val.contains(arb(h).exp()), 'EXPONENTIAL_CONTROL')
        tests[str(sign)] = 'constant and exponential contained'
    try:
        step([q('1')],fmpq(1,100),lambda y:[q('1')],[q('0')])
    except RuntimeError as exc:
        need(str(exc)=='TUBE_CONTAINMENT','WRONG_REJECTION')
    else:
        raise RuntimeError('TOO_SMALL_TUBE_NOT_REJECTED')
    seed = [q(s) for s in ('1','-2','0','0','1','0','0','1')]
    expected = [q(s) for s in ('-2','-3','0','1','0','1','-17/18','8')]
    need(all(x.contains(v) for x,v in zip(rhs(seed),expected)), 'EXACT_SEED_RHS')
    tests['too_small_tube'] = 'rejected'
    tests['exact_seed_rhs'] = 'all eight entries contained'
    return tests

def ham(y):
    a,H,P,T = y[:4]
    V = P-P*P/2+P**4
    return H*H-1-T*T/12+V/6-3/(a*a)

def runtime():
    locations = [Path(sys.executable).resolve(),
        Path('/home/parallels/research-runs/cap-interval-arb-2026-09-12/flint/types/arb.abi3.so')]
    return {'python':sys.version,'flint':flint.__version__,'precision_bits':ctx.prec,
            'threads':ctx.threads,'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in locations}}

def level(n):
    y = [q(s) for s in ('1','-2','0','0')]
    h = fmpq(1,100*n)
    for i in range(n):
        y = step(y,-h,rhs,BG_RATES,True)
    need(ham(y).contains(0), 'LOWER_HAMILTONIAN')
    lower = y[:]
    y += [q(s) for s in ('1','0','0','1')]
    for i in range(2*n):
        y = step(y,h,rhs,RATES,True)
        if (i+1)%512==0:
            print(json.dumps({'n':n,'forward_steps':i+1,'seconds':time.monotonic()-START}),flush=True)
    need(ham(y).contains(0), 'UPPER_HAMILTONIAN')
    p,b,c,d = y[4:]
    analytical = [(fmpq(249489,250000),fmpq(250511,250000)),
                  (fmpq(4949,250000),fmpq(6501,250000)),
                  (fmpq(-1,25),fmpq(-81,5000)),
                  (fmpq(569,500),fmpq(309,250))]
    need(all(inside_exact(x,limit) for x,limit in zip(y[4:],analytical)), 'ANALYTICAL_M_BOUNDS')
    determinant = p*d-b*c
    determinant_defect = determinant-(lower[0]/y[0])**4
    need(determinant.lower()>0 and determinant_defect.contains(0), 'DETERMINANT_IDENTITY')
    values = {'lower_only':-2*c/d, 'upper_only':-2*c/p,
              'equal_each':-4*c/(p+d+((p+d)**2-4*b*c).sqrt())}
    for key,x in values.items():
        lo,hi = bounds(x)
        need(lo>0 and hi-lo<=fmpq(1,10000), 'THRESHOLD_WIDTH_'+key)
    output = {'n':n,'steps':3*n,'lower_background':[record(x) for x in lower],
              'upper_state':[record(x) for x in y],
              'thresholds':{k:record(v) for k,v in values.items()},
              'determinant_defect':record(determinant_defect),
              'hamiltonian_lower':record(ham(lower)), 'hamiltonian_upper':record(ham(y)),
              'all_tubes_passed':True, 'all_level_gates_passed':True}
    save('LEVEL_'+str(n)+'.json',output)
    return values

def main():
    before = runtime()
    expected_runtime_hashes = {
        '/usr/bin/python3.12':'c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960',
        '/home/parallels/research-runs/cap-interval-arb-2026-09-12/flint/types/arb.abi3.so':
            '6abaed2e09f6b60e4b26d9c6eb71345ae5e69fc9162fc42e5ff232ef8be75145'}
    need(before['hashes']==expected_runtime_hashes,'UNADMITTED_RUNTIME_HASHES')
    bindings = {name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                for name in ('producer.py','lease_run.py','PLAN.md')}
    need(sys.version_info[:3]==(3,12,3) and flint.__version__=='0.9.0','RUNTIME_VERSION')
    save('RUNTIME_START.json',{'runtime':before,'source_hashes':bindings})
    save('CONTROLS.json',controls())
    coarse = level(1024)
    fine = level(2048)
    for key,x in fine.items():
        lo,hi = bounds(x)
        a,b = bounds(coarse[key])
        need(max(lo,a)<=min(hi,b), 'LEVEL_DISJOINT_'+key)
        need(hi-lo<=b-a, 'REFINEMENT_WIDENED_'+key)
    after = runtime()
    need(before==after,'RUNTIME_CHANGED')
    need(bindings=={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in bindings},'SOURCE_CHANGED')
    save('RESULT.json',{'classification':'PASS_VALIDATED_TRANSITION_COORDINATES',
         'thresholds':{k:record(v) for k,v in fine.items()},'controls_passed':True,
         'both_levels_passed':True,'overlap_and_width_checks_passed':True,
         'runtime':after,'source_hashes':bindings,'seconds':time.monotonic()-START,
         'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss})

if __name__=='__main__':
    def timeout(signum, frame):
        raise TimeoutError('independent child 590-second wall cap')
    signal.signal(signal.SIGALRM,timeout)
    signal.alarm(590)
    try:
        main()
    except BaseException as exc:
        save('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),
                            'seconds':time.monotonic()-START})
        raise
    finally:
        signal.alarm(0)
