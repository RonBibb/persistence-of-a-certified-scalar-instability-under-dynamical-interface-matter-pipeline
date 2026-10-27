"""Conditional nonlinear analytic-domain gates; not an amplitude certificate."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
io=load('source_domain_io',base/'extract.py')
assert io.sha(base/'extract.py')=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('source_domain_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
WEIGHTED=ROOT.parent/'20261026_COMPLEX_WEIGHTED_RESPONSE'
REAL=ROOT.parent/'20261026_RESPONSE_AUDIT'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          WEIGHTED/'AUDIT_RESULT.json':'7076650f416c7b7c0c3b203a33f987c1afd5d05297d6ccbd59e03f799aced8e9',
          REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'}
    for p,d in pins.items():assert io.sha(p)==d
    assert all(io.read(p)['pass'] for p in pins)
    collar=io.read(COLLAR/'RESULT.json');real=io.read(REAL/'RESULT.json')
    R=Q(collar['rho']);eps=Q(collar['epsilon']);eta=Q(1,100000)
    assert R==Q(1,20000) and eps==Q(1,1000)
    assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    binding={'source_sha256':io.sha(__file__),'inputs':{str(p):d for p,d in pins.items()},'runtime':lease.observed(),
             'eta_condition':'Y(16*abs(z)) <= 1/100000; not established for any numerical z'}
    io.put('BINDING.json',binding)
    arms={}
    for name in ('primary','independent'):
        p=io.FLOW/('FLOW_'+name+'.json');assert io.sha(p)==ft['artifacts'][p.name]
        flow=io.read(p);Dmin,Dmax=map(Q,flow['D']);kup=io.iv(flow['parameters']['k'])[1]
        ext={k:Q(v) for k,v in real['arms'][name]['extrema'].items()}
        Cx=1+R/(2*Dmin);shift=Cx*eta;Jdev=eta/Dmin;q=2*shift/R
        Ebar=8+eps;Tbar=ext['T0']+eps
        hupper=Q(1,50);assert kup<hupper*hupper
        speed=2*Ebar*6*hupper*eta
        coupling_dev=(Tbar+1)*eta/1000
        gates={'composition_reserve':R/4-shift,'jacobian_margin_to_quarter':Q(1,4)-Jdev,
               'composition_ratio_margin':Q(1,2)-q,'exponential_margin':Q(1,8)-eta,
               'speed_margin_to_quarter':Q(1,4)-speed,'coupling_margin_to_half':Q(1,2)-coupling_dev}
        assert all(v>0 for v in gates.values())
        # exp(2 eta)<=sum_j (2 eta)^j=1/(1-2 eta)<2, with exact rational check.
        assert 2*eta<1 and 1/(1-2*eta)<2
        vals=dict(Cx=Cx,shift_bound=shift,jacobian_deviation=Jdev,composition_ratio=q,
                  background_composition_coefficient_scale=2/R,composition_sum_factor=1/(1-q),
                  inverse_jacobian_bound=1/(1-Jdev),wall_speed_bound=speed,
                  inverse_one_minus_speed_squared=1/(1-speed*speed),coupling_deviation=coupling_dev,**gates)
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()}}
    result={'pass':True,'classification':'CONDITIONAL_NONLINEAR_DOMAIN_GATES_PASS','eta_max':str(eta),
        'outer_collar':str(R),'inner_collar':str(R/2),'arms':arms,
        'condition':'Finite truncation or convergent coefficient envelope Y(16|z|)<=eta_max; no such charge z has been certified.',
        'domain_accounting':{'shifted_collar':str(3*R/4),'perturbation_value_factor':1,
            'perturbation_first_radial_derivative_factor':4,'perturbation_second_radial_derivative_factor':16,
            'speed_and_coupling_scope':'Physical real walls only; general affine graph time derivatives require Cx.',
            'background_Taylor_bound':'For each background function separately, use its own verified supremum M; tail <= M*q**(m+1)/(1-q). The ODE vector-field bound is not such an M.'},
        'coefficient_germs':'exp(cu): |coefficient_j|<=|c|^j; inverse(1-u): coefficient_j=1; inverse_sqrt(1-u): coefficient_j<=1',
        'source_majorant_K_M_complete':False,'independent_arithmetic_replay':False,'amplitude_radius_certified':False}
    for p,d in pins.items():assert io.sha(p)==d
    assert io.sha(__file__)==binding['source_sha256']
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({'eta_max':str(eta),'arms':{k:v['display'] for k,v in arms.items()}}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DOMAIN_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
