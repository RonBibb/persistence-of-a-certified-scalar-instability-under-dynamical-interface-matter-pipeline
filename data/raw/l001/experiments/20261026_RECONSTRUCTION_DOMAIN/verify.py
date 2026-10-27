"""Independent exact conditional reconstruction-domain audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
ENV=BASE/'20261026_COEFFICIENT_ENVELOPE_CLOSURE'
ENV_AUDIT=BASE/'20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1'
COLLAR=BASE/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=BASE/'20261026_RESPONSE_AUDIT'
FROZEN='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
PINS={ENV/'RESULT.json':'3aa11d9a779bba1f1a3efde5c632d43ef5e623178f033dd0f15e0a04b1c37906',
      ENV_AUDIT/'AUDIT_RESULT.json':'fa805f5eff415c6ec019ec9f111a3f4c52e70f8d70c3481b9e012e8b781319db',
      COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'}
PINS.update({ROOT/'check.py':'1417117f77a042ae7f60d509468324afbb4c3e0aa493b2f2b05b46fa3b9ecb57',
             ROOT/'DERIVATION.md':'9d2bdbd7ffffae0c361ad809c6fcdf13e5cacac25903016ba204dc4e91af3634',
             ROOT/'RESULT.json':'33b94170c6d6eb66bb1da7c64149c2fcc34efe379419f4fda6067710b0f148c4',
             ROOT/'BINDING.json':'ec62ddffb38d0a5eba3185ba520c5489b1efdd427251cb7f4e72867570fd4271'})
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
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    assert Path(sys.modules['_pylong'].__file__).resolve()==pylong
    paths=set(PINS)|{Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',pylong,
        FLOW/'FROZEN.json',FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    terms=[]
    for folder in (ROOT,ENV,COLLAR,REAL):
        paths.update({folder/'TERMINAL.json',folder/'BINDING.json'})
        terms.append((folder,'TERMINAL.json','RESULT.json'))
    for folder in (ENV_AUDIT,COLLAR):
        paths.add(folder/'AUDIT_TERMINAL.json');terms.append((folder,'AUDIT_TERMINAL.json','AUDIT_RESULT.json'))
    hashes={str(p):sha(p) for p in paths}
    for p,digest in PINS.items():assert sha(p)==digest
    for folder,t,r in terms:
        term=read(folder/t);assert term['pass'] and term['result_sha256']==sha(folder/r)
        if 'binding_sha256' in term:assert term['binding_sha256']==sha(folder/'BINDING.json')
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py') and binding['derivation_sha256']==sha(ROOT/'DERIVATION.md')
    for p,digest in binding['inputs'].items():assert sha(p)==digest
    result=read(ROOT/'RESULT.json');env=read(ENV/'RESULT.json');env_audit=read(ENV_AUDIT/'AUDIT_RESULT.json')
    collar=read(COLLAR/'RESULT.json');real=read(REAL/'RESULT.json')
    assert all(o['pass'] for o in (result,env,env_audit,collar,real,read(COLLAR/'AUDIT_RESULT.json')))
    assert env_audit['exact']==env['exact'] and env['coefficient_envelope_closed']
    assert real['unresolved']==[]
    assert result['classification']=='RECONSTRUCTION_DOMAIN_GATES_DIAGNOSTIC'
    assert not result['distance_tail_certified'] and not result['scalar_turn_certified']
    rho=F(1,40000);radius=F(1,20000)
    assert F(env['working_collar'])==F(result['working_collar'])==rho
    assert F(collar['rho'])==F(result['background_collar'])==radius
    assert F(result['starting_collar'])==rho/2 and F(result['shifted_collar_ceiling'])==3*rho/4
    s=F(env['exact']['s']);r=F(env['exact']['r_w']);physical=r/F(32)
    assert 0<s<F(1,1000000) and 16*physical==r/2 and r/2<r
    assert F(result['normalized_radius'])==physical and F(result['envelope_radius'])==r
    assert F(result['envelope_bound'])==s
    g=F(3,25);E=F(8001,1000)
    bounds={'bulk_value':s,'bulk_radial_first':4*s,'bulk_radial_second':16*s,
        'bulk_D0_first':g*s,'bulk_D0_second':g*g*s,'bulk_radial_D0':4*g*s,
        'finite_value':s,'finite_time_first':g*s,'finite_time_second':g*g*s}
    assert {k:F(v) for k,v in result['bounds'].items()}==bounds
    ft=read(FLOW/'production_TERMINAL.json')
    assert sha(FLOW/'FROZEN.json')==FROZEN and ft['pass'] and ft['frozen_sha256']==FROZEN
    assert set(result['arms'])==set(real['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);lo,hi=map(F,flow['D']);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        assert hi>=lo>1 and 0<kl<=ku<F(1,2500)
        T=F(real['arms'][name]['extrema']['T0'])+F(1,1000)
        cx=(2*lo+rho)/(2*lo);shift=s*cx;jacobian=s/lo;ratio=shift/(rho/2)
        speed=(2*E*g)*s;coupling=s*(T+1)/1000
        assert 2*s<1
        gates={'shift_margin':rho/4-shift,'composition_margin':F(1,2)-ratio,
            'jacobian_lower':(lo-s)/lo,'separation_lower':lo-s,'speed_margin':F(1,4)-speed,
            'boost_squared_margin':1-speed*speed,'coupling_lower':1-coupling,
            'coupling_margin':F(1,2)-coupling,'exponential_margin':(1-4*s)/(1-2*s)}
        assert all(v>0 for v in gates.values())
        values={'Cx':cx,'shift_bound':shift,'jacobian_deviation':jacobian,'composition_ratio':ratio,
            'inverse_jacobian_bound':lo/(lo-s),'wall_speed_bound':speed,'coupling_deviation':coupling,**gates}
        assert {k:F(v) for k,v in result['arms'][name]['exact'].items()}==values
        arms[name]={'exact':{k:str(v) for k,v in values.items()},'positive_gates':len(gates)}
    after=lease.observed();assert before==after
    assert all(sha(p)==digest for p,digest in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'RECONSTRUCTION_DOMAIN_GATES_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'normalized_radius':str(physical),'bounds':{k:str(v) for k,v in bounds.items()},
        'runtime_before':before,'runtime_after':after,
        'scope':'Exact reconstruction margins from authenticated envelope; inherits compatible all-order proofs. Complex separation is a modulus bound, D0 derivatives use pulled coordinates, finite bounds are graph/oscillator endpoint bounds. No scalar-turn, global-evolution or distance-tail certificate.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==FROZEN
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('reconstruction_audit_lease',p)
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
