"""Independent scalar-normal wall arithmetic, with inherited analytic count proof."""
import sys
sys.dont_write_bytecode=True
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
COLLAR=BASE/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=BASE/'20261026_RESPONSE_AUDIT'
BULK=BASE/'20261026_SCALAR_RADIAL_SOURCE_BUDGET'
PINS={FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',
      COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
      BULK/'RESULT.json':'12563a244eb46bef3f73c2d16a66a8a74d2eaa4b89179aaa40ed2b16c3de2858',
      BULK/'AUDIT_RESULT.json':'85fa72f8c36d20d1c9e37902ca836ca33017f87a57e0e02699eb80b15963fba5'}
PINS.update({ROOT/'check.py':'c3fd92b86dd7dc30c02c72a998628a72f84ab005ace8d9343594335907b7489f',
             ROOT/'DERIVATION.md':'1f64f89df5ad0812ac68fb283165941a9efdf03a34f3fa289364d1235d0e0a7f',
             ROOT/'RESULT.json':'09dde715e8ecec2a07b21eaa311635e664bc6fd6d8c90e99b49ae0a8bf42f5f0',
             ROOT/'BINDING.json':'6ad49478fafa3d35842629998de8ef1889a068d646ff56717d7c1ff417e1f99b'})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def put(name,value):
    dest=ROOT/name;tmp=ROOT/(name+'.tmp')
    with tmp.open('x') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,dest);tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/s).exists() for s in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths=set(PINS)|{Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',
        FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    terms=[]
    for folder in (ROOT,COLLAR,REAL,BULK):
        paths.update({folder/'TERMINAL.json',folder/'BINDING.json'})
        terms.append((folder,'TERMINAL.json','RESULT.json'))
    for folder in (COLLAR,BULK):
        paths.add(folder/'AUDIT_TERMINAL.json');terms.append((folder,'AUDIT_TERMINAL.json','AUDIT_RESULT.json'))
    hashes={str(p):sha(p) for p in paths}
    for p,h in PINS.items():assert sha(p)==h
    for folder,t,r in terms:
        term=read(folder/t);assert term['pass'] and term['result_sha256']==sha(folder/r)
        if 'binding_sha256' in term:assert term['binding_sha256']==sha(folder/'BINDING.json')
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py')
    assert binding['derivation_sha256']==sha(ROOT/'DERIVATION.md')
    for p,h in binding['inputs'].items():assert sha(p)==h
    result=read(ROOT/'RESULT.json');bulk=read(BULK/'RESULT.json')
    real=read(REAL/'RESULT.json');collar=read(COLLAR/'RESULT.json')
    assert all(o['pass'] for o in (result,bulk,real,collar,read(BULK/'AUDIT_RESULT.json'),read(COLLAR/'AUDIT_RESULT.json')))
    assert real['unresolved']==[]
    assert result['classification']=='SCALAR_NORMAL_WALL_BUDGET_DIAGNOSTIC'
    assert result['formal_coefficientwise'] and result['numerical_evaluation_condition']=='A*y<1'
    assert not any(result[k] for k in ('full_wall_budget_complete','full_majorant_closed','amplitude_radius_certified'))
    assert result['outer_order_weight_included'] is True and result['two_wall_geometric_factor']==2
    selected=result['selected_action']
    assert selected=={'tau_hessian':20,'oscillator_coupling':1,
        'current_coupling_derivative':'-1/1000','scalar_half_factor':'1/2'}
    radius,rho,eps,g=F(1,20000),F(1,40000),F(1,1000),F(3,25)
    assert F(result['background_collar'])==F(collar['rho'])==radius
    assert F(result['working_collar'])==F(bulk['working_collar'])==rho
    assert F(collar['epsilon'])==eps
    a=F(2)/rho;E=F(8)+eps;c=E*g;A=2*a+1
    assert a>=6 and 0<c<1 and A>=2*a+c
    assert F(result['composition_scale'])==a and F(result['wall_denominator_scale'])==A
    assert result['denominator_power']==6
    # Seven and three are exact primitive-count factors, not sampled coefficients.
    geometric_count=2+5;current_count=1+2
    current_half=abs(F(selected['current_coupling_derivative']))*F(selected['scalar_half_factor'])
    current=E*E*E*E*E*E*current_half
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(result['arms'])==set(real['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);lo,hi=map(F,flow['D']);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        assert hi>=lo>1 and 0<kl<=ku<F(1,2500)
        ext=real['arms'][name]['extrema'];T=F(ext['T0'])+eps;P=F(ext['P0'])+eps
        parts={'normal_background':T*a*a+T*a+T,'normal_radial':F(1)+F(1),
            'boost_correction':(E*g)*(E*g)*T+(E*g)*(E*g),
            'velocity_scalar':2*(E*g)*(E*g),
            'wall_potential':F(selected['tau_hessian']+selected['oscillator_coupling'])*F(selected['scalar_half_factor'])*P*a*a}
        raw=sum(parts.values())
        vals={'Tbar':T,'Pbar':P,'Ebar':E,'speed_coefficient':c,'raw_geometric_constant':raw,
            'raw_current_constant':current,'weighted_geometric_constant':2*geometric_count*raw,
            'weighted_current_constant':current_count*current}
        saved=result['arms'][name]
        assert {k:F(v) for k,v in saved['parts'].items()}==parts
        assert {k:F(v) for k,v in saved['exact'].items()}==vals
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'parts':{k:str(v) for k,v in parts.items()}}
    after=lease.observed();assert before==after
    assert all(sha(p)==h for p,h in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'SCALAR_NORMAL_WALL_BUDGET_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'runtime_before':before,'runtime_after':after,'geometric_primitive_count_factor':geometric_count,
        'current_primitive_count_factor':current_count,
        'scope':'Exact selected-action scalar-normal constants and factor-count arithmetic. Inherits reviewed analytic primitive-count proof, not a sampled sequence claim. Numerical evaluation requires A*y<1; no complete wall budget, majorant closure, or amplitude radius.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PINS[FLOW/'FROZEN.json']
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('scalar_normal_audit_lease',p)
        lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_120_SECONDS')))
        run(lease)
    except BaseException as error:
        if not (ROOT/'AUDIT_RESULT.json').exists():
            put('AUDIT_RESULT.json',{'pass':False,'classification':'TECHNICAL_INCOMPLETE',
                'source_sha256':sha(__file__),'error':repr(error),'traceback':traceback.format_exc()})
        if not (ROOT/'AUDIT_TERMINAL.json').exists():
            put('AUDIT_TERMINAL.json',{'pass':False,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
                'source_sha256':sha(__file__)})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()
