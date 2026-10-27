"""Exact constants for Klein-Gordon, radial, and reconstructed bulk sources."""
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
io=load('scalar_radial_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('scalar_radial_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
MIXED=ROOT.parent/'20261026_MIXED_SOURCE_BUDGET'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
          MIXED/'RESULT.json':'8921c6fd7706c5f421aef069be664c519467beece8b8cc0649dc9bc18487dd19',
          MIXED/'AUDIT_RESULT.json':'bdf44703e299a230dd9646afd1171b11f41aa56ae4e174bd71db4c2ad10b54c9'}
    for p,d in pins.items():assert io.sha(p)==d and io.read(p)['pass']
    mixed=io.read(MIXED/'RESULT.json');real=io.read(REAL/'RESULT.json');collar=io.read(COLLAR/'RESULT.json')
    R=Q(collar['rho']);rho=Q(mixed['working_collar']);eps=Q(collar['epsilon'])
    assert R==Q(1,20000) and rho==R/2 and eps==Q(1,1000)
    a=2/rho;g=Q(3,25);h=Q(1,50);t=g*g+3*h*g;d=14*g*g+6*h*g
    assert a>=2 and g==6*h
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    inputs={str(p):v for p,v in pins.items()}
    for name in ('primary','independent'):
        p=io.FLOW/('FLOW_'+name+'.json');assert io.sha(p)==ft['artifacts'][p.name];inputs[str(p)]=io.sha(p)
    inputs[str(io.FLOW/'FROZEN.json')]=io.EXPECTED;inputs[str(io.LEASE)]=io.sha(io.LEASE)
    binding={'source_sha256':io.sha(__file__),'derivation_sha256':io.sha(ROOT/'DERIVATION.md'),
             'inputs':inputs,'runtime':lease.observed()}
    io.put('BINDING.json',binding)
    arms={}
    for name in ('primary','independent'):
        flow=io.read(io.FLOW/('FLOW_'+name+'.json'));kl,ku=io.iv(flow['parameters']['k'])
        ext={k:Q(v) for k,v in real['arms'][name]['extrema'].items()}
        H,T,P,E,m=ext['H0']+eps,ext['T0']+eps,ext['P0']+eps,8+eps,ext['m0']
        assert kl>0 and ku<h*h and m==max(abs(v) for v in io.iv(flow['parameters']['m2']))
        dc=Q(collar['arms'][name]['exact']['D_over_n2']);assert dc>0
        inherited=mixed['arms'][name]['exact'];Ct=Q(inherited['tracefree_constant']);Csp=Q(inherited['metric_source_constant'])
        assert Q(inherited['Hbar'])==H and Q(inherited['Tbar'])==T
        A=6*H*H+T*T/2
        kp={'temporal_change':E*E*((a+2)*t+d),'temporal_bilinear':12*E*E*g*g,
            'spatial_second':Q(4),'spatial_bilinear':Q(5),'background_jets':(4*H+5*T)*(a+3),
            'potential_remainder':m*P*(4+2*a)}
        rp={'background_exponential':A*(4+2*a),'background_jets':(12*H+T)*(a+3),
            'spatial_bilinear':Q(13,2),'potential_composition':m*P*a,'potential_quadratic':m/2,
            'temporal_background':6*ku*E*E*(4+2*a),'temporal_change':3*E*E*((a+2)*t+d),
            'temporal_bilinear':14*E*E*g*g}
        CK=sum(kp.values());CR=sum(rp.values())
        CSc=12*H*Csp+(12*H*H+T*T)*Ct+CR
        CSg=(T+2*m*P)*Ct+6*T*Csp+CK
        CF=CSg+(12*H*T+4*m*P)*CSc/dc
        vals={'Hbar':H,'Tbar':T,'Pbar':P,'Ebar':E,'mass_bound':m,'k_upper':ku,'D_lower':dc,
              'tracefree_constant':Ct,'mixed_source_constant':Csp,'KG_constant':CK,'radial_constant':CR,
              'Sc_constant':CSc,'Sg_constant':CSg,'F_constant':CF}
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
                    'KG_parts':{k:str(v) for k,v in kp.items()},'radial_parts':{k:str(v) for k,v in rp.items()}}
    result={'pass':True,'classification':'SCALAR_RADIAL_SOURCE_BUDGET_DIAGNOSTIC','working_collar':str(rho),
        'background_collar':str(R),'composition_scale':str(a),'denominator_power':4,
        'temporal_linear':str(t),'temporal_remainder':str(d),'arms':arms,
        'formal_coefficientwise':True,'numerical_evaluation_condition':'a*y<1',
        'full_majorant_closed':False,'amplitude_radius_certified':False,
        'scope':'KG and radial sources and compatible reconstructed bulk loads only; no wall sources or full closure.'}
    assert all(io.sha(p)==v for p,v in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({n:{k:v for k,v in x['display'].items() if k.endswith('_constant')} for n,x in arms.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('SCALAR_RADIAL_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
