"""Exact independent conditional source-domain gate audit, not amplitude certification."""
import sys
sys.dont_write_bytecode=True
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
COLLAR=BASE/'20261026_COMPLEX_BACKGROUND_COLLAR'
WEIGHTED=BASE/'20261026_COMPLEX_WEIGHTED_RESPONSE'
REAL=BASE/'20261026_RESPONSE_AUDIT'
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
PINS={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      WEIGHTED/'AUDIT_RESULT.json':'7076650f416c7b7c0c3b203a33f987c1afd5d05297d6ccbd59e03f799aced8e9',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
      FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'}
PINS.update({ROOT/'check.py':'468ed96d38758abcff2d73a359e3faf9caf180dde72b6138b5d3fe48fd834ac8',
             ROOT/'RESULT.json':'80102cbcf32c23873abe089f41e1435baf91eea255384af5807bf19c3df00e8d',
             ROOT/'BINDING.json':'f4ffff357ba97832b8b539bbea5acb7c7611d148536f19714532fb46e4b27450'})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def put(name,obj):
    dest=ROOT/name;tmp=ROOT/(name+'.tmp')
    with tmp.open('x') as f:
        json.dump(obj,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,dest);tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def check_terminal(folder,name,result):
    t=read(folder/name)
    assert t['pass'] and t['result_sha256']==sha(folder/result)
    if 'binding_sha256' in t:assert t['binding_sha256']==sha(folder/'BINDING.json')
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/s).exists() for s in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths=set(PINS)|{Path(__file__),ROOT/'DERIVATION.md',ROOT/'check.py',ROOT/'RESULT.json',ROOT/'TERMINAL.json',
        ROOT/'BINDING.json',COLLAR/'TERMINAL.json',COLLAR/'BINDING.json',
        COLLAR/'AUDIT_TERMINAL.json',WEIGHTED/'AUDIT_TERMINAL.json',REAL/'TERMINAL.json',
        REAL/'BINDING.json',FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',
        FLOW/'FLOW_independent.json',BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    hashes={str(p):sha(p) for p in paths}
    for p,h in PINS.items():assert sha(p)==h
    for folder,term,res in ((ROOT,'TERMINAL.json','RESULT.json'),
        (COLLAR,'TERMINAL.json','RESULT.json'),(COLLAR,'AUDIT_TERMINAL.json','AUDIT_RESULT.json'),
        (WEIGHTED,'AUDIT_TERMINAL.json','AUDIT_RESULT.json'),(REAL,'TERMINAL.json','RESULT.json')):
        check_terminal(folder,term,res)
    for p in (COLLAR/'AUDIT_RESULT.json',WEIGHTED/'AUDIT_RESULT.json'):assert read(p)['pass']
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py')
    for p,h in binding['inputs'].items():assert sha(p)==h
    r=read(ROOT/'RESULT.json');collar=read(COLLAR/'RESULT.json');real=read(REAL/'RESULT.json')
    assert r['pass'] and r['classification']=='CONDITIONAL_NONLINEAR_DOMAIN_GATES_PASS'
    assert not r['source_majorant_K_M_complete'] and not r['amplitude_radius_certified']
    assert real['pass'] and real['unresolved']==[] and collar['pass']
    radius,epsilon,eta=F(1,20000),F(1,1000),F(1,100000)
    assert F(collar['rho'])==F(r['outer_collar'])==radius
    assert F(collar['epsilon'])==epsilon and F(r['eta_max'])==eta
    assert F(r['inner_collar'])==radius/2
    assert 'Y(16' in r['condition'] and 'Y(16' in binding['eta_condition']
    domain=r['domain_accounting']
    assert F(domain['shifted_collar'])==3*radius/4
    assert [domain[k] for k in ('perturbation_value_factor','perturbation_first_radial_derivative_factor',
        'perturbation_second_radial_derivative_factor')]==[1,4,16]
    assert 'Physical real walls only' in domain['speed_and_coupling_scope']
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(r['arms'])==set(real['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);length_low,length_high=map(F,flow['D'])
        assert 0<length_low<=length_high
        kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        assert 0<kl<=ku<F(1,50)*F(1,50)
        tmax=F(real['arms'][name]['extrema']['T0'])+epsilon
        cx=(2*length_low+radius)/(2*length_low)
        displacement=cx*eta;jacobian=eta/length_low
        ratio=displacement/(radius/2)
        speed=F(12)*(F(8)+epsilon)*eta/F(50)
        coupling=(tmax+1)*eta/F(1000)
        margins={'composition_reserve':radius/4-displacement,
            'jacobian_margin_to_quarter':F(1,4)-jacobian,
            'composition_ratio_margin':F(1,2)-ratio,
            'exponential_margin':F(1,8)-eta,
            'speed_margin_to_quarter':F(1,4)-speed,
            'coupling_margin_to_half':F(1,2)-coupling}
        assert all(v>0 for v in margins.values())
        assert 2*eta<1 and F(1)/(1-2*eta)<2
        vals={'Cx':cx,'shift_bound':displacement,'jacobian_deviation':jacobian,
            'composition_ratio':ratio,'background_composition_coefficient_scale':F(2)/radius,
            'composition_sum_factor':F(1)/(1-ratio),'inverse_jacobian_bound':F(1)/(1-jacobian),
            'wall_speed_bound':speed,'inverse_one_minus_speed_squared':F(1)/(1-speed*speed),
            'coupling_deviation':coupling,**margins}
        assert {k:F(v) for k,v in r['arms'][name]['exact'].items()}==vals
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'positive_gates':len(margins)}
    after=lease.observed();assert before==after
    assert all(sha(p)==h for p,h in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'CONDITIONAL_NONLINEAR_DOMAIN_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'runtime_before':before,'runtime_after':after,
        'scope':'Exact conditional domain inequalities only; assumes finite truncation or convergent Y(16|z|) envelope. No charge value, assembled nonlinear majorant, amplitude radius, or new ODE certificate.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PINS[FLOW/'FROZEN.json']
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('domain_audit_lease',p)
        lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_120_SECONDS')))
        run(lease)
    except BaseException as error:
        if not (ROOT/'AUDIT_RESULT.json').exists():
            put('AUDIT_RESULT.json',{'pass':False,'classification':'TECHNICAL_INCOMPLETE',
                'error':repr(error),'traceback':traceback.format_exc(),'source_sha256':sha(__file__)})
        if not (ROOT/'AUDIT_TERMINAL.json').exists():
            put('AUDIT_TERMINAL.json',{'pass':False,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
                'source_sha256':sha(__file__)})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()
