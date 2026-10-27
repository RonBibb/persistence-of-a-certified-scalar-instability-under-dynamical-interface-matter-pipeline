"""Exact tracefree source budget; no evolution or full nonlinear closure."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
import hashlib
assert hashlib.sha256((base/'extract.py').read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('tracefree_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('tracefree_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'}
    for p,d in pins.items():assert io.sha(p)==d and io.read(p)['pass']
    R=Q(io.read(COLLAR/'RESULT.json')['rho']);rho=R/2
    assert R==Q(1,20000)
    g=Q(3,25);h=Q(1,50)
    a=[18*g*g+4*h*g,16*g*g-4*h*g,6*g*g]
    assert all(x>0 for x in a) and sum(a)==40*g*g
    # Independent symbolic collection of the primitive seven summands.
    primitive=[(8*g*g,-8*g*g,0),(0,4*g*g,0),
               (4*g*g,-4*g*g,0),(0,4*g*g,0),
               (4*h*g,-4*h*g,0),(0,8*g*g,0),(6*g*g,12*g*g,6*g*g)]
    assert [sum(t[i] for t in primitive) for i in range(3)]==a
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    inputs={str(p):d for p,d in pins.items()}
    for name in ('primary','independent'):
        p=io.FLOW/('FLOW_'+name+'.json');assert io.sha(p)==ft['artifacts'][p.name];inputs[str(p)]=io.sha(p)
    inputs[str(io.FLOW/'FROZEN.json')]=io.EXPECTED
    inputs[str(io.LEASE)]=io.sha(io.LEASE)
    binding={'source_sha256':io.sha(__file__),'derivation_sha256':io.sha(ROOT/'DERIVATION.md'),
             'inputs':inputs,'runtime':lease.observed()}
    io.put('BINDING.json',binding)
    arms={}
    for name in ('primary','independent'):
        flow=io.read(io.FLOW/('FLOW_'+name+'.json'))
        Dmin,Dmax=map(Q,flow['D']);kl,ku=io.iv(flow['parameters']['k'])
        assert Dmax>=Dmin>1 and 1+rho/Dmin<2 and 0<kl<=ku<h*h
        C=(1+9/rho+108/(rho*rho))/(36*kl)
        arms[name]={'k_min':str(kl),'raw_to_c':str(C),'tracefree_constant':str(40*g*g*C),
                    'display_constant':float(40*g*g*C)}
    result={'pass':True,'classification':'TRACEFREE_SOURCE_BUDGET_DIAGNOSTIC',
        'background_collar':str(R),'working_collar':str(rho),'norm_convention':'All Y and U on fixed working collar, not inherited outer-collar norms.',
        'numerator_coefficients':list(map(str,a)),'raw_source_constant':str(40*g*g),'arms':arms,
        'full_majorant_closed':False,'amplitude_radius_certified':False,
        'scope':'Tracefree bulk source and c reconstruction only; all-order bound justified in DERIVATION.md, exact constants checked here.'}
    assert all(io.sha(p)==v for p,v in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps(result),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('TRACEFREE_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
