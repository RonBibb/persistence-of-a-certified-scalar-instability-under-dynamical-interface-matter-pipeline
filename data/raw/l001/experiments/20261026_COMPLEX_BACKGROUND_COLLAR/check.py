"""Fixed-radius polynomial background collar diagnostic; exact rational inequalities."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
io=load('collar_io',base/'extract.py')
assert io.sha(base/'extract.py')=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io.ROOT=ROOT
lease=load('collar_lease',io.LEASE);lease.ROOT=ROOT
AUDIT=ROOT.parent/'20261026_RESPONSE_AUDIT'
PIN='6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'
def run():
    assert sys.platform=='linux' and not any((ROOT/x).exists() for x in ('START.json','RESULT.json','FAILURE.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    assert io.sha(AUDIT/'RESULT.json')==PIN
    terminal=io.read(AUDIT/'TERMINAL.json')
    assert terminal['pass'] and terminal['result_sha256']==PIN
    assert terminal['binding_sha256']==io.sha(AUDIT/'BINDING.json')
    audit=io.read(AUDIT/'RESULT.json');assert audit['pass'] and not audit['unresolved']
    assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
    flowterm=io.read(io.FLOW/'production_TERMINAL.json')
    assert flowterm['pass'] and flowterm['frozen_sha256']==io.EXPECTED
    binding={'source_sha256':io.sha(__file__),'audit_result_sha256':PIN,'runtime':lease.observed(),
             'parent_frozen_sha256':io.EXPECTED,'tube_epsilon':'1/1000','collar_radius':'1/20000'}
    io.put('BINDING.json',binding)
    eps=Q(1,1000);rho=Q(1,20000);arms={}
    for name,record in audit['arms'].items():
        ext={k:Q(v) for k,v in record['extrema'].items()}
        flowpath=io.FLOW/('FLOW_'+name+'.json')
        assert io.sha(flowpath)==flowterm['artifacts'][flowpath.name]
        flow=io.read(flowpath);kup=io.iv(flow['parameters']['k'])[1]
        k0,e0,H0,T0,P0,m0=[ext[k] for k in ('k0','e0','H0','T0','P0','m0')]
        assert k0>0 and e0>0 and kup>=k0
        Hb,Tb,Pb,Eb=H0+eps,T0+eps,P0+eps,8+eps
        rows=[Hb,Tb*Tb/3+kup*Eb*Eb,Tb,m0*Pb+4*Hb*Tb,Hb*Eb]
        jac=[Q(1),2*Tb/3+2*kup*Eb,Q(1),m0+4*Tb+4*Hb,Eb+Hb]
        M=max(rows);L=max(jac)
        de=16*eps+eps*eps;dt=2*T0*eps+eps*eps
        d0=42*k0*e0*e0
        Dmin=d0-2*dt-108*kup*de
        Jmin=42*k0*(e0*e0-de)
        oscmin=18*k0*e0*e0-36*kup*de
        Bbar=12*Hb*Tb+4*m0*Pb;Tpbar=m0*Pb+4*Hb*Tb
        gates={'picard_self_map':eps-rho*M,'picard_contraction':1-rho*L,
               'E_nonzero':e0-eps,'E_squared_realpart':e0*e0-de,
               'D_over_n2':Dmin,'J_over_n2':Jmin,'oscillator_over_n2':oscmin}
        assert all(v>0 for v in gates.values()),'FIXED_COLLAR_GATE_FAILED'
        coefficients={'drift_absolute':4*Hb+Bbar*Tb/Dmin,
                      'potential_over_n2_absolute':m0+36*kup*Eb*Eb+2*Tb*Tb+Bbar*Tpbar/Dmin,
                      'inverse_A_absolute':(2*Tb*Tb+108*kup*Eb*Eb)/Jmin}
        vals=dict(vector_field_bound=M,jacobian_bound=L,**gates,**coefficients)
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
                    'all_gates_pass':True}
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(AUDIT/'RESULT.json')==PIN
    result={'classification':'FIXED_COMPLEX_BACKGROUND_COLLAR_DIAGNOSTIC','pass':True,'arms':arms,
            'epsilon':str(eps),'rho':str(rho),'inner_cauchy_radius':str(rho/2),
            'denominator_orders':'all integers n>=1','parameters_complexified':False,
            'scope':'Complex radial extension of the fixed real background with uniform denominator separation; no charged field complex inverse estimate.',
            'independent_arithmetic_replay':False,'nonlinear_majorant_constants_computed':False,'amplitude_radius_certified':False}
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({'rho':str(rho),'epsilon':str(eps),'arms':{k:v['display'] for k,v in arms.items()}}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COLLAR_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
