"""Independent exact scalar/radial contribution and reconstruction audit."""
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
MIXED=BASE/'20261026_MIXED_SOURCE_BUDGET'
PINS={FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',
      COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
      MIXED/'RESULT.json':'8921c6fd7706c5f421aef069be664c519467beece8b8cc0649dc9bc18487dd19',
      MIXED/'AUDIT_RESULT.json':'bdf44703e299a230dd9646afd1171b11f41aa56ae4e174bd71db4c2ad10b54c9'}
PINS.update({ROOT/'check.py':'cea2f00f6fb8ad243da1de93473af2a16d0dd36d330310df6ef4124750d08120',
             ROOT/'DERIVATION.md':'8fb9c4b394c76cbde5b9e9144fb5dad0640d8122ed496c28a9e61228b231ab41',
             ROOT/'RESULT.json':'12563a244eb46bef3f73c2d16a66a8a74d2eaa4b89179aaa40ed2b16c3de2858',
             ROOT/'BINDING.json':'2072eca3e3f5f1951cf6aef13dec1425df61a42ecc95a90bbb95ba3f406fc651'})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def put(name,value):
    dest=ROOT/name;temp=ROOT/(name+'.tmp')
    with temp.open('x') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(temp,0o444);os.link(temp,dest);temp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths=set(PINS)|{Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',
        FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    terms=[]
    for folder in (ROOT,COLLAR,REAL,MIXED):
        paths.update({folder/'TERMINAL.json',folder/'BINDING.json'})
        terms.append((folder,'TERMINAL.json','RESULT.json'))
    for folder in (COLLAR,MIXED):
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
    result=read(ROOT/'RESULT.json');mixed=read(MIXED/'RESULT.json')
    real=read(REAL/'RESULT.json');collar=read(COLLAR/'RESULT.json')
    assert all(o['pass'] for o in (result,mixed,real,collar,read(COLLAR/'AUDIT_RESULT.json'),read(MIXED/'AUDIT_RESULT.json')))
    assert real['unresolved']==[]
    assert result['classification']=='SCALAR_RADIAL_SOURCE_BUDGET_DIAGNOSTIC'
    assert result['formal_coefficientwise'] and result['numerical_evaluation_condition']=='a*y<1'
    assert not result['full_majorant_closed'] and not result['amplitude_radius_certified']
    rho,R,eps,g,h=F(1,40000),F(1,20000),F(1,1000),F(3,25),F(1,50)
    a=F(2)/rho
    t=g*(g+3*h);d=2*g*(7*g+3*h)
    assert F(result['working_collar'])==F(mixed['working_collar'])==rho
    assert F(result['background_collar'])==F(collar['rho'])==R
    assert F(collar['epsilon'])==eps and F(result['composition_scale'])==a
    assert F(result['temporal_linear'])==t and F(result['temporal_remainder'])==d
    assert result['denominator_power']==4 and a>=2 and g==6*h
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(result['arms'])==set(mixed['arms'])==set(real['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        ml,mu=map(F,flow['parameters']['m2']['exact_bounds']);assert ml<=mu
        ext=real['arms'][name]['extrema']
        H,T,P,E,m=F(ext['H0'])+eps,F(ext['T0'])+eps,F(ext['P0'])+eps,F(8)+eps,F(ext['m0'])
        assert 0<kl<=ku<h*h and m==max(abs(ml),abs(mu))
        dlower=F(collar['arms'][name]['exact']['D_over_n2']);assert dlower>0
        old=mixed['arms'][name]['exact'];ct=F(old['tracefree_constant']);sp=F(old['metric_source_constant'])
        assert ct>0 and sp>0 and F(old['Hbar'])==H and F(old['Tbar'])==T
        e2=E*E;common_time=(a*t+2*t+d)*e2
        # Named terms separately follow each removed-linear-row source group.
        kg={'temporal_change':common_time,'temporal_bilinear':3*(2*g)*(2*g)*e2,
            'spatial_second':F(2)+F(2),'spatial_bilinear':F(4)+F(1),
            'background_jets':4*H*a+12*H+5*T*a+15*T,
            'potential_remainder':2*m*P*(a+2)}
        ab=6*H*H+T*T/2
        radial={'background_exponential':2*ab*(a+2),
            'background_jets':12*H*a+36*H+T*a+3*T,
            'spatial_bilinear':F(6)+F(1,2),'potential_composition':a*m*P,
            'potential_quadratic':m/F(2),'temporal_background':12*ku*e2*(a+2),
            'temporal_change':common_time+common_time+common_time,
            'temporal_bilinear':(F(3)+F(1,2))*(2*g)*(2*g)*e2}
        ck=sum(kg.values());cr=sum(radial.values())
        # Different grouping independently checks the compact formula too.
        assert ck==e2*((a+2)*t+d+12*g*g)+9+(4*H+5*T)*(a+3)+m*P*(4+2*a)
        assert cr==ab*(4+2*a)+(12*H+T)*(a+3)+F(13,2)+m*P*a+m/2+6*ku*e2*(4+2*a)+3*e2*((a+2)*t+d)+14*e2*g*g
        sc=12*H*(sp+H*ct)+T*T*ct+cr
        sg=T*(ct+6*sp)+2*m*P*ct+ck
        reduced=sg+4*(3*H*T+m*P)*sc/dlower
        vals={'Hbar':H,'Tbar':T,'Pbar':P,'Ebar':E,'mass_bound':m,'k_upper':ku,'D_lower':dlower,
            'tracefree_constant':ct,'mixed_source_constant':sp,'KG_constant':ck,'radial_constant':cr,
            'Sc_constant':sc,'Sg_constant':sg,'F_constant':reduced}
        saved=result['arms'][name]
        assert {k:F(v) for k,v in saved['KG_parts'].items()}==kg
        assert {k:F(v) for k,v in saved['radial_parts'].items()}==radial
        assert {k:F(v) for k,v in saved['exact'].items()}==vals
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},
            'KG_parts':{k:str(v) for k,v in kg.items()},'radial_parts':{k:str(v) for k,v in radial.items()}}
    after=lease.observed();assert before==after
    assert all(sha(p)==h for p,h in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'SCALAR_RADIAL_SOURCE_BUDGET_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'runtime_before':before,'runtime_after':after,
        'scope':'Independent exact named-part and regrouped constant reconstruction, conditional on audited background and analytic source decomposition. Bulk only; formal coefficients or numerical a*y<1, not walls, full closure, or an amplitude radius.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PINS[FLOW/'FROZEN.json']
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('scalar_radial_audit_lease',p)
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
