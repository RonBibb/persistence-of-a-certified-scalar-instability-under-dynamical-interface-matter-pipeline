"""Diagnostic exact checks of a real-axis scalar response estimate."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,time
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
helper=load('response_io',BASE/'extract.py')
assert helper.sha(BASE/'extract.py')=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
helper.ROOT=ROOT
lease=load('response_lease',helper.LEASE);lease.ROOT=ROOT
def run():
    assert sys.platform=='linux'
    assert not (ROOT/'START.json').exists() and not (ROOT/'RESULT.json').exists()
    cpu,occupied=lease.acquire()
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('RESPONSE_120_SECONDS')))
    signal.alarm(120)
    helper.put('START.json',{'cpu':cpu,'occupied':occupied})
    assert helper.sha(BASE/'RESULT.json')=='23605bfbe42485d19e9f952ebd8f791984955ad04926eba697f283d6bc5aab38'
    assert helper.sha(helper.FLOW/'FROZEN.json')==helper.EXPECTED
    terminal=helper.read(helper.FLOW/'production_TERMINAL.json')
    assert terminal['pass'] and terminal['frozen_sha256']==helper.EXPECTED
    sys.path.insert(0,str(lease.FLINT))
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    binding={'source_sha256':helper.sha(__file__),'input_sha256':helper.sha(BASE/'RESULT.json'),
             'runtime':lease.observed(),'parent_manifest':helper.EXPECTED}
    helper.put('BINDING.json',binding)
    results={}
    for name,arm in helper.read(BASE/'RESULT.json')['arms'].items():
        p=helper.FLOW/('FLOW_'+name+'.json')
        assert helper.sha(p)==terminal['artifacts'][p.name]
        data=helper.read(p)
        assert helper.iv(data['initial'][0])==(0,0)
        lo,hi=map(Q,data['D'])
        e={k:Q(v) for k,v in arm['extrema_exact'].items()}
        C={k:Q(v) for k,v in arm['cutoff']['constants'].items()}
        N=39;lam=Q(1,64);c=C['c0'];A=C['drift_bound']
        # W(0)=0 and |Wprime|=|H|<=H0 imply E<=exp(H0 Lmax).
        upper=arb(fmpq(str(e['H0']*hi))).exp()
        assert Q(str(upper.upper().fmpq()))<8
        kup=helper.iv(data['parameters']['k'])[1]
        v=e['m0']+36*kup*64+2*e['T0']**2+C['C0']
        gates={'barrier':c-lam*lam-A*lam/N,'boundary_separation':lam*N*lo-1,
               'taylor_segment':N*lo-2,'derivative_absorption':1-A/(2*N)}
        assert all(x>=0 for x in gates.values()) and gates['derivative_absorption']>0
        q0=max(1/c,4/lam)
        q1=((2+v/2)*q0+Q(1,2))/gates['derivative_absorption']
        q2=A*q1/N+v*q0+1
        total=q0+q1+q2
        results[name]={'N':N,'lambda':str(lam),'E_upper':8,
            'gates_exact':{k:str(x) for k,x in gates.items()},
            'constants_exact':{k:str(x) for k,x in dict(c=c,A=A,v=v,C_value=q0,C_first=q1,C_second=q2,C_sum=total).items()},
            'constants_display':{k:float(x) for k,x in dict(c=c,A=A,v=v,C_value=q0,C_first=q1,C_second=q2,C_sum=total).items()},
            'outward_integer_C_sum':-(-total.numerator//total.denominator)}
    helper.put('RESULT.json',{'classification':'REAL_AXIS_RESPONSE_BOUND_DIAGNOSTIC',
         'arms':results,'bound':'n^2 ||f|| + n ||fprime|| + ||fsecond|| <= C (||F|| + n max_i |g_i|)',
         'valid_orders':'integer n >= 39','independent_arithmetic_replay':False,
         'complex_collar_bound':False,'amplitude_radius_certified':False})
    assert binding['source_sha256']==helper.sha(__file__)
    helper.put('TERMINAL.json',{'pass':True,'result_sha256':helper.sha(ROOT/'RESULT.json'),
                              'binding_sha256':helper.sha(ROOT/'BINDING.json')})
    print(json.dumps({k:r['constants_display'] for k,r in results.items()}),flush=True)
try:
    if __name__=='__main__':run()
finally:
    signal.alarm(0)
    for f in lease.handles:f.close()
