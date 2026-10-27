"""Exact gates for reconstruction from the audited coefficient envelope."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import importlib.util, hashlib, json, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
assert hashlib.sha256((base/'extract.py').read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('reconstruction_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('reconstruction_lease',io.LEASE);lease.ROOT=ROOT
ENVELOPE=ROOT.parent/'20261026_COEFFICIENT_ENVELOPE_CLOSURE'
AUDIT=ROOT.parent/'20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1'
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={ENVELOPE/'RESULT.json':'3aa11d9a779bba1f1a3efde5c632d43ef5e623178f033dd0f15e0a04b1c37906',
          AUDIT/'AUDIT_RESULT.json':'fa805f5eff415c6ec019ec9f111a3f4c52e70f8d70c3481b9e012e8b781319db',
          COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'}
    for path,digest in pins.items():assert io.sha(path)==digest and io.read(path)['pass']
    parent=io.read(ENVELOPE/'RESULT.json');audit=io.read(AUDIT/'AUDIT_RESULT.json')
    assert audit['exact']==parent['exact'] and parent['coefficient_envelope_closed']
    rho=Q(parent['working_collar']);R=Q(io.read(COLLAR/'RESULT.json')['rho'])
    assert rho==Q(1,40000) and R==2*rho
    s=Q(parent['exact']['s']);r=Q(parent['exact']['r_w']);rphys=r/32
    assert 0<s<Q(1,1000000) and 0<16*rphys<r
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    inputs={str(p):d for p,d in pins.items()}
    for name in ('primary','independent'):
        path=io.FLOW/('FLOW_'+name+'.json');assert io.sha(path)==ft['artifacts'][path.name];inputs[str(path)]=io.sha(path)
    inputs[str(io.FLOW/'FROZEN.json')]=io.EXPECTED;inputs[str(io.LEASE)]=io.sha(io.LEASE)
    # Qualify lazy integer-text conversion before taking a runtime baseline.
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert io.sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    inputs[str(pylong)]=io.sha(pylong)
    runtime=lease.observed()
    binding={'source_sha256':io.sha(__file__),'derivation_sha256':io.sha(ROOT/'DERIVATION.md'),'inputs':inputs,'runtime':runtime}
    io.put('BINDING.json',binding)
    real=io.read(REAL/'RESULT.json');arms={};g=Q(3,25);E=Q(8001,1000)
    for name in ('primary','independent'):
        flow=io.read(io.FLOW/('FLOW_'+name+'.json'));Dmin,Dmax=map(Q,flow['D']);_,ku=io.iv(flow['parameters']['k'])
        assert Dmax>=Dmin>1 and ku<Q(1,2500)
        T=Q(real['arms'][name]['extrema']['T0'])+Q(1,1000)
        Cx=1+rho/(2*Dmin);shift=Cx*s;Jdev=s/Dmin
        q=2*shift/rho;speed=2*E*g*s;coupling=(T+1)*s/1000
        gates={'shift_margin':rho/4-shift,'composition_margin':Q(1,2)-q,
               'jacobian_lower':1-Jdev,'separation_lower':Dmin-s,
               'speed_margin':Q(1,4)-speed,'boost_squared_margin':1-speed*speed,
               'coupling_lower':1-coupling,'coupling_margin':Q(1,2)-coupling,
               'exponential_margin':2-1/(1-2*s)}
        assert all(v>0 for v in gates.values())
        vals=dict(Cx=Cx,shift_bound=shift,jacobian_deviation=Jdev,composition_ratio=q,
                  inverse_jacobian_bound=1/(1-Jdev),wall_speed_bound=speed,coupling_deviation=coupling,**gates)
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()}}
    result={'pass':True,'classification':'RECONSTRUCTION_DOMAIN_GATES_DIAGNOSTIC',
            'working_collar':str(rho),'background_collar':str(R),'starting_collar':str(rho/2),'shifted_collar_ceiling':str(3*rho/4),
            'normalized_radius':str(rphys),'envelope_radius':str(r),'envelope_bound':str(s),
            'display':{'normalized_radius':float(rphys),'envelope_bound':float(s)},
            'bounds':{k:str(v) for k,v in dict(bulk_value=s,bulk_radial_first=4*s,bulk_radial_second=16*s,
                bulk_D0_first=g*s,bulk_D0_second=g*g*s,bulk_radial_D0=4*g*s,finite_value=s,finite_time_first=g*s,finite_time_second=g*g*s).items()},
            'arms':arms,'distance_tail_certified':False,'scalar_turn_certified':False,
            'scope':'Explicit sufficient local reconstruction domain, conditional on inherited coefficient/source/inverse and compatibility proofs; D0 temporal bounds are in pulled coordinates.'}
    assert lease.observed()==runtime
    assert all(io.sha(p)==h for p,h in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps(result['display']),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('RECONSTRUCTION_120_SECONDS')))
        run()
    except BaseException as error:
        io.put('FAILURE.json',{'error':repr(error),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
