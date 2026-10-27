"""Independent exact Israel/oscillator source and graph reconstruction audit."""
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
NORMAL=BASE/'20261026_SCALAR_NORMAL_WALL_BUDGET'
PINS={FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',
      COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
      NORMAL/'RESULT.json':'09dde715e8ecec2a07b21eaa311635e664bc6fd6d8c90e99b49ae0a8bf42f5f0',
      NORMAL/'AUDIT_RESULT.json':'1c42f5aedc5e9759f0621d26d796b7c01a541fa091f54989f24f61ae6d7b1c83'}
PINS.update({ROOT/'check.py':'16062d0415d2e15eb7807bf8c8181d89157a84b0804e8722909831c17a00acc2',
             ROOT/'DERIVATION.md':'a7138d7a1f4ca6da349b8e4317fd1e5934502902b668306f061ec2d0ef90a56c',
             ROOT/'RESULT.json':'b4f6b13f490ab95da0bc3a436bd77b836cfd5f64fe518e7ca5aa1de72f4bf993',
             ROOT/'BINDING.json':'5a41200bc20eef30f43f46980c7b76977592a8ecd7c87f4ccf770be0a9faa120'})
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
    for folder in (ROOT,COLLAR,REAL,NORMAL):
        paths.update({folder/'TERMINAL.json',folder/'BINDING.json'})
        terms.append((folder,'TERMINAL.json','RESULT.json'))
    for folder in (COLLAR,NORMAL):
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
    result=read(ROOT/'RESULT.json');normal=read(NORMAL/'RESULT.json')
    real=read(REAL/'RESULT.json');collar=read(COLLAR/'RESULT.json')
    assert all(o['pass'] for o in (result,normal,real,collar,read(NORMAL/'AUDIT_RESULT.json'),read(COLLAR/'AUDIT_RESULT.json')))
    assert real['unresolved']==[]
    assert result['classification']=='ISRAEL_OSCILLATOR_WALL_BUDGET_DIAGNOSTIC'
    assert result['formal_coefficientwise'] and result['numerical_evaluation_condition']=='A*y<1'
    assert not any(result[k] for k in ('reduced_robin_load_complete','full_majorant_closed','amplitude_radius_certified'))
    assert result['outer_order_weights_included'] is True and result['two_wall_geometric_factor']==2
    selected=normal['selected_action']
    assert selected=={'tau_hessian':20,'oscillator_coupling':1,'current_coupling_derivative':'-1/1000','scalar_half_factor':'1/2'}
    radius,rho,eps,g,h=F(1,20000),F(1,40000),F(1,1000),F(3,25),F(1,50)
    assert F(result['background_collar'])==F(collar['rho'])==radius
    assert F(result['working_collar'])==F(normal['working_collar'])==rho
    assert F(collar['epsilon'])==eps
    a=F(2)/rho;E=F(8)+eps;c=E*g;A=2*a+1;t=g*(g+3*h)
    assert a>=6 and 0<c<1 and A>=2*a+c
    assert F(result['composition_scale'])==a
    assert F(result['wall_denominator_scale'])==F(normal['wall_denominator_scale'])==A
    assert result['israel_denominator_power']==9 and result['oscillator_denominator_power']==11
    israel_factor=2*(2+8);current_factor=1+3;oscillator_factor=2*(2+10)
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(result['arms'])==set(real['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);lo,hi=map(F,flow['D']);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        assert hi>=lo>1 and 0<kl<=ku<h*h
        ext=real['arms'][name]['extrema'];H=F(ext['H0'])+eps;P=F(ext['P0'])+eps;emin=F(ext['e0'])
        assert emin>0
        e2=E*E;g2=g*g
        acceleration=e2*g2*((a+4+H)+(a+1)+3*c*c)
        ip={'acceleration':acceleration,'drift':h*e2*g*(a+3)+h*e2*g*c*c,
            'physical_derivatives':e2*(2*g)*(2*g),'oscillator_stress':F(1,2)*e2*g2}
        coupling=(P*a+1)*abs(F(selected['current_coupling_derivative']))
        current=(E*E*E*E*E*E)*(A+coupling)/A
        ci=sum(ip.values())
        op={'lapse':e2*t*(a+2)+2*e2*t*c*c,
            'ordinary_friction':2*e2*g2*H+2*e2*g2,
            'velocity_friction':(E*E*E)*(E*g)*(g*g*g)*(3+H),'scalar_trace':P*a*a}
        co=sum(op.values())
        divisor=6*6*kl*emin*emin
        vals={'Hbar':H,'Pbar':P,'Ebar':E,'speed_coefficient':c,'k_min':kl,'E_min':emin,
            'velocity_time_constant':E*g2*(3+H),'velocity_time_remainder_constant':E*g2*(a+4+H),
            'israel_raw_geometric':ci,'current_coupling_constant':coupling,'israel_raw_current':current,
            'israel_weighted_geometric':israel_factor*ci,'israel_weighted_current':current_factor*current,
            'graph_divisor':divisor,'graph_geometric':israel_factor*ci/divisor,
            'graph_current':current_factor*current/divisor,'oscillator_raw':co,'oscillator_weighted':oscillator_factor*co}
        saved=result['arms'][name]
        assert {k:F(v) for k,v in saved['israel_parts'].items()}==ip
        assert {k:F(v) for k,v in saved['oscillator_parts'].items()}==op
        assert {k:F(v) for k,v in saved['exact'].items()}==vals
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},
            'israel_parts':{k:str(v) for k,v in ip.items()},'oscillator_parts':{k:str(v) for k,v in op.items()}}
    after=lease.observed();assert before==after
    assert all(sha(p)==h for p,h in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'ISRAEL_OSCILLATOR_WALL_BUDGET_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'runtime_before':before,'runtime_after':after,
        'outer_factors':{'israel_geometry':israel_factor,'israel_current':current_factor,'oscillator':oscillator_factor},
        'scope':'Exact row constants, primitive-count factors and graph reconstruction. Inherits analytic wall identities and endpoint norms; no sampled all-order inference, oscillator inversion, Robin reconstruction, complete closure or amplitude certificate.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PINS[FLOW/'FROZEN.json']
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('israel_oscillator_audit_lease',p)
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
