"""Selected-action scalar-normal wall source constants, exact arithmetic."""
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
io=load('wall_normal_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('wall_normal_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
BULK=ROOT.parent/'20261026_SCALAR_RADIAL_SOURCE_BUDGET'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
          BULK/'RESULT.json':'12563a244eb46bef3f73c2d16a66a8a74d2eaa4b89179aaa40ed2b16c3de2858',
          BULK/'AUDIT_RESULT.json':'85fa72f8c36d20d1c9e37902ca836ca33017f87a57e0e02699eb80b15963fba5'}
    for p,digest in pins.items():assert io.sha(p)==digest and io.read(p)['pass']
    bulk=io.read(BULK/'RESULT.json');real=io.read(REAL/'RESULT.json');collar=io.read(COLLAR/'RESULT.json')
    R=Q(collar['rho']);rho=Q(bulk['working_collar']);eps=Q(collar['epsilon'])
    assert R==Q(1,20000) and rho==R/2 and eps==Q(1,1000)
    a=2/rho;g=Q(3,25);E=8+eps;c=E*g;A=2*a+1
    assert a>=6 and 0<c<1 and A>=2*a+c
    Ccur=E**6/2000
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
        Dmin,Dmax=map(Q,flow['D']);assert Dmax>=Dmin>1 and 0<kl<=ku<Q(1,2500)
        ext=real['arms'][name]['extrema'];T=Q(ext['T0'])+eps;P=Q(ext['P0'])+eps
        parts={'normal_background':T*(a*a+a+1),'normal_radial':Q(2),
               'boost_correction':c*c*(T+1),'velocity_scalar':2*c*E*g,
               'wall_potential':Q(21,2)*P*a*a}
        Cj=sum(parts.values())
        vals={'Tbar':T,'Pbar':P,'Ebar':E,'speed_coefficient':c,'raw_geometric_constant':Cj,
              'raw_current_constant':Ccur,'weighted_geometric_constant':14*Cj,
              'weighted_current_constant':3*Ccur}
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
                    'parts':{k:str(v) for k,v in parts.items()}}
    result={'pass':True,'classification':'SCALAR_NORMAL_WALL_BUDGET_DIAGNOSTIC',
        'working_collar':str(rho),'background_collar':str(R),'composition_scale':str(a),
        'wall_denominator_scale':str(A),'denominator_power':6,'arms':arms,
        'selected_action':{'tau_hessian':20,'oscillator_coupling':1,'current_coupling_derivative':'-1/1000','scalar_half_factor':'1/2'},
        'outer_order_weight_included':True,'two_wall_geometric_factor':2,
        'formal_coefficientwise':True,'numerical_evaluation_condition':'A*y<1',
        'full_wall_budget_complete':False,'full_majorant_closed':False,'amplitude_radius_certified':False,
        'scope':'Scalar-normal residual only; both walls, independent squared current labels, outer n included.'}
    assert all(io.sha(p)==v for p,v in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({n:x['display'] for n,x in arms.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('WALL_NORMAL_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
