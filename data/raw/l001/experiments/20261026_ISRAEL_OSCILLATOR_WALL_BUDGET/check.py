"""Exact Israel, oscillator, and graph source constants for selected action."""
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
io=load('israel_oscillator_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('israel_oscillator_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
NORMAL=ROOT.parent/'20261026_SCALAR_NORMAL_WALL_BUDGET'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
          NORMAL/'RESULT.json':'09dde715e8ecec2a07b21eaa311635e664bc6fd6d8c90e99b49ae0a8bf42f5f0',
          NORMAL/'AUDIT_RESULT.json':'1c42f5aedc5e9759f0621d26d796b7c01a541fa091f54989f24f61ae6d7b1c83'}
    for p,digest in pins.items():assert io.sha(p)==digest and io.read(p)['pass']
    normal=io.read(NORMAL/'RESULT.json');real=io.read(REAL/'RESULT.json');collar=io.read(COLLAR/'RESULT.json')
    R=Q(collar['rho']);rho=Q(normal['working_collar']);eps=Q(collar['epsilon'])
    assert R==Q(1,20000) and rho==R/2 and eps==Q(1,1000)
    a=2/rho;g=Q(3,25);h=Q(1,50);E=8+eps;c=E*g;A=2*a+1;t=g*g+3*h*g
    assert a>=6 and 0<c<1 and A>=2*a+c and A==Q(normal['wall_denominator_scale'])
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
        Dmin,Dmax=map(Q,flow['D']);assert Dmax>=Dmin>1 and 0<kl<=ku<h*h
        ext={k:Q(v) for k,v in real['arms'][name]['extrema'].items()}
        H,P,emin=ext['H0']+eps,ext['P0']+eps,ext['e0'];assert emin>0
        ip={'acceleration':E*E*g*g*(2*a+5+H+3*c*c),
            'drift':h*E*E*g*(a+3+c*c),'physical_derivatives':4*E*E*g*g,
            'oscillator_stress':E*E*g*g/2}
        K=(P*a+1)/1000;Icur=E**6*(1+K/A);CI=sum(ip.values())
        op={'lapse':E*E*t*(a+2+2*c*c),'ordinary_friction':2*E*E*g*g*(H+1),
            'velocity_friction':E**3*c*g**3*(3+H),'scalar_trace':P*a*a}
        CO=sum(op.values());divisor=36*kl*emin*emin
        vals={'Hbar':H,'Pbar':P,'Ebar':E,'speed_coefficient':c,'k_min':kl,'E_min':emin,
              'velocity_time_constant':E*g*g*(3+H),'velocity_time_remainder_constant':E*g*g*(a+4+H),
              'israel_raw_geometric':CI,'current_coupling_constant':K,'israel_raw_current':Icur,
              'israel_weighted_geometric':20*CI,'israel_weighted_current':4*Icur,
              'graph_divisor':divisor,'graph_geometric':20*CI/divisor,'graph_current':4*Icur/divisor,
              'oscillator_raw':CO,'oscillator_weighted':24*CO}
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
                    'israel_parts':{k:str(v) for k,v in ip.items()},'oscillator_parts':{k:str(v) for k,v in op.items()}}
    result={'pass':True,'classification':'ISRAEL_OSCILLATOR_WALL_BUDGET_DIAGNOSTIC',
        'working_collar':str(rho),'background_collar':str(R),'composition_scale':str(a),
        'wall_denominator_scale':str(A),'israel_denominator_power':9,'oscillator_denominator_power':11,
        'arms':arms,'outer_order_weights_included':True,'two_wall_geometric_factor':2,
        'formal_coefficientwise':True,'numerical_evaluation_condition':'A*y<1',
        'reduced_robin_load_complete':False,'full_majorant_closed':False,'amplitude_radius_certified':False,
        'scope':'Raw Israel and oscillator source bounds and graph reconstruction, conditional on inherited exact rows and endpoint primitive norms.'}
    assert all(io.sha(p)==v for p,v in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({n:{k:v for k,v in x['display'].items() if k.startswith(('israel_','graph_','oscillator_'))} for n,x in arms.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ISRAEL_OSCILLATOR_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
