"""Exact mixed Einstein source constants on the fixed working collar."""
import sys
sys.dont_write_bytecode=True
import importlib.util,hashlib,json,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
assert hashlib.sha256((base/'extract.py').read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('mixed_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('mixed_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
TRACE=ROOT.parent/'20261026_TRACEFREE_SOURCE_BUDGET'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
          TRACE/'RESULT.json':'a03da75ab2f852014ff636a16d73849b11408c29f199d0bbc5fa28ad5ec62b51',
          TRACE/'AUDIT_RESULT.json':'f48a1106af8f914ca84f16bf8f8b2674b4bfcd9da499ea9d770feb993bc98be9'}
    for p,d in pins.items():assert io.sha(p)==d and io.read(p)['pass']
    trace=io.read(TRACE/'RESULT.json');real=io.read(REAL/'RESULT.json');collar=io.read(COLLAR/'RESULT.json')
    R=Q(collar['rho']);rho=Q(trace['working_collar']);eps=Q(collar['epsilon'])
    assert R==Q(1,20000) and rho==R/2 and eps==Q(1,1000)
    a=2/rho;g=Q(3,25);hmin=Q(1,100);assert a>=1
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    inputs={str(p):d for p,d in pins.items()}
    for name in ('primary','independent'):
        p=io.FLOW/('FLOW_'+name+'.json');assert io.sha(p)==ft['artifacts'][p.name];inputs[str(p)]=io.sha(p)
    inputs[str(io.FLOW/'FROZEN.json')]=io.EXPECTED;inputs[str(io.LEASE)]=io.sha(io.LEASE)
    binding={'source_sha256':io.sha(__file__),'derivation_sha256':io.sha(ROOT/'DERIVATION.md'),
             'inputs':inputs,'runtime':lease.observed()}
    io.put('BINDING.json',binding)
    arms={}
    for name in ('primary','independent'):
        flow=io.read(io.FLOW/('FLOW_'+name+'.json'));kl,ku=io.iv(flow['parameters']['k'])
        Dmin,Dmax=map(Q,flow['D']);assert Dmax>=Dmin>1 and kl>hmin*hmin and ku<Q(1,2500)
        ext=real['arms'][name]['extrema'];Hb=Q(ext['H0'])+eps;Tb=Q(ext['T0'])+eps
        B=Hb+Tb/3;parts=[g,3*g,B*g*a,2*B*g,8*g/3]
        Cm=sum(parts);assert Cm==g*(Q(20,3)+B*(a+2))
        Ct=Q(trace['arms'][name]['tracefree_constant']);assert Ct>0
        Csp=Hb*Ct+Cm/(6*hmin)
        vals={'Hbar':Hb,'Tbar':Tb,'background_combination':B,'mixed_constant':Cm,
              'tracefree_constant':Ct,'metric_source_constant':Csp}
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
                    'raw_contributions':list(map(str,parts))}
    result={'pass':True,'classification':'MIXED_SOURCE_BUDGET_DIAGNOSTIC','working_collar':str(rho),
        'background_collar':str(R),'composition_scale':str(a),'h_lower':str(hmin),'arms':arms,
        'formal_coefficientwise':True,'numerical_evaluation_condition':'a*y<1',
        'full_majorant_closed':False,'amplitude_radius_certified':False,
        'scope':'Mixed Einstein q_M and reconstructed S_p only, using compatible recursion and independently audited tracefree bound.'}
    assert all(io.sha(p)==d for p,d in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({n:x['display'] for n,x in arms.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('MIXED_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
