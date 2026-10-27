"""Read-only exact attribution of conservative coefficient-envelope constants."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
helper=BASE/'20261026_BACKGROUND_CUTOFF/extract.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('loss_io',helper);io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('loss_lease',io.LEASE);lease.ROOT=ROOT
PINS={
'20261026_COEFFICIENT_ENVELOPE_CLOSURE/RESULT.json':'3aa11d9a779bba1f1a3efde5c632d43ef5e623178f033dd0f15e0a04b1c37906',
'20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1/AUDIT_RESULT.json':'fa805f5eff415c6ec019ec9f111a3f4c52e70f8d70c3481b9e012e8b781319db',
'20261026_SCALAR_RADIAL_SOURCE_BUDGET/RESULT.json':'12563a244eb46bef3f73c2d16a66a8a74d2eaa4b89179aaa40ed2b16c3de2858',
'20261026_MIXED_SOURCE_BUDGET/RESULT.json':'8921c6fd7706c5f421aef069be664c519467beece8b8cc0649dc9bc18487dd19',
'20261026_TRACEFREE_SOURCE_BUDGET/RESULT.json':'a03da75ab2f852014ff636a16d73849b11408c29f199d0bbc5fa28ad5ec62b51',
'20261026_ISRAEL_OSCILLATOR_WALL_BUDGET/RESULT.json':'b4f6b13f490ab95da0bc3a436bd77b836cfd5f64fe518e7ca5aa1de72f4bf993',
'20261026_DISTANCE_TAIL/RESULT.json':'447b19af1290cffd82fdff0e3c7f3b78bffe24d1be088dc65dd6aeb3ac6ac608',
'20261026_DISTANCE_TAIL/AUDIT_RESULT.json':'2c419e8bec3ee81f7588c6e1d4c9d0e12f3acea21f25754b27730c43e0e21c5e'}
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    data={}
    for rel,digest in PINS.items():
        p=BASE/rel;assert io.sha(p)==digest;data[rel]=io.read(p);assert data[rel]['pass']
    closure=data['20261026_COEFFICIENT_ENVELOPE_CLOSURE/RESULT.json']
    radial=data['20261026_SCALAR_RADIAL_SOURCE_BUDGET/RESULT.json']
    mixed=data['20261026_MIXED_SOURCE_BUDGET/RESULT.json']
    trace=data['20261026_TRACEFREE_SOURCE_BUDGET/RESULT.json']
    wall=data['20261026_ISRAEL_OSCILLATOR_WALL_BUDGET/RESULT.json']
    tail=data['20261026_DISTANCE_TAIL/RESULT.json']
    assert data['20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1/AUDIT_RESULT.json']['exact']==closure['exact']
    assert data['20261026_DISTANCE_TAIL/AUDIT_RESULT.json']['exact']==tail['exact']
    assert len(str(10**20000))==20001
    runtime=lease.observed();source=io.sha(__file__)
    io.put('BINDING.json',{'source_sha256':source,'inputs':PINS,'runtime':runtime})
    arms={}
    for name in ('primary','independent'):
        C=Q(closure['arms'][name]['metric_response']);rho=Q(closure['working_collar']);channels={}
        for channel in ('geometric','current'):
            geom=channel=='geometric'
            saved={k:Q(v) for k,v in closure['arms'][name]['channels'][channel].items()}
            Sc=Q(radial['arms'][name]['exact']['Sc_constant']) if geom else Q(0)
            Sp=Q(mixed['arms'][name]['exact']['metric_source_constant']) if geom else Q(0)
            Ct=Q(trace['arms'][name]['tracefree_constant']) if geom else Q(0)
            Xi=Q(wall['arms'][name]['exact']['graph_'+channel])
            parts={'direct_scalar':saved['Uf'],'metric_from_scalar':3*C*saved['Uf'],
                   'metric_from_constraint':3*C*Sc,'metric_from_mixed':3*C*Sp,
                   'tracefree':Ct,'graph':Xi,'oscillator':saved['Qosc']}
            assert C*(Sc+Sp+saved['Uf'])==saved['Up']
            assert sum(parts.values())==saved['K']
            shares={k:v/saved['K'] for k,v in parts.items()}
            assert sum(shares.values())==1
            # In the accepted proof 12/rho arises only from differentiating Sp.
            # This is attribution of the old bound, NOT a replacement inverse.
            attributed=(3*(12/rho)*saved['Uf'])/saved['K']
            channels[channel]={'parts':{k:str(v) for k,v in parts.items()},
                 'shares':{k:str(v) for k,v in shares.items()},'display_shares':{k:float(v) for k,v in shares.items()},
                 'Sp_derivative_constant_applied_to_scalar_share':str(attributed),
                 'display_Sp_derivative_constant_applied_to_scalar_share':float(attributed)}
        arms[name]={'metric_response':str(C),'mixed_derivative_term':str(12/rho),
            'remaining_metric_constant':str(C-12/rho),'channels':channels}
    te={k:Q(v) for k,v in tail['exact'].items()}
    chain={'coefficient_radius':closure['exact']['r_w'],'reconstruction_radius':str(te['distance_disk_radius']),
           'shortening_radius':str(te['z_upper']),
           'reconstruction_loss_factor':str(Q(closure['exact']['r_w'])/te['distance_disk_radius']),
           'distance_tail_loss_factor':str(te['distance_disk_radius']/te['z_upper'])}
    assert lease.observed()==runtime and io.sha(__file__)==source
    assert all(io.sha(BASE/p)==h for p,h in PINS.items())
    result={'pass':True,'classification':'EXACT_BOUND_LOSS_ATTRIBUTION_DIAGNOSTIC','arms':arms,'radius_chain':chain,
            'new_radius_certified':False,'scope':'Exact decomposition of accepted upper bounds, not physical mechanism shares or a revised inverse certificate.'}
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({'arms':{n:{c:v['display_shares'] for c,v in a['channels'].items()} for n,a in arms.items()},'radius_chain':chain}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('LOSS_120_SECONDS')))
        run()
    except BaseException as error:
        io.put('FAILURE.json',{'error':repr(error),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
