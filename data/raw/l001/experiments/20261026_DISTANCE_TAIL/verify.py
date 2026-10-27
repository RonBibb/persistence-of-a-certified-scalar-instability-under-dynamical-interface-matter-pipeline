"""Independent exact distance-tail and first-passing dyadic-radius audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
RECON=BASE/'20261026_RECONSTRUCTION_DOMAIN'
SECOND=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
CUBIC=BASE/'20261026T100400Z_CUBIC_DISTANCE'
FROZEN='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
PINS={
RECON/'RESULT.json':'33b94170c6d6eb66bb1da7c64149c2fcc34efe379419f4fda6067710b0f148c4',
RECON/'AUDIT_RESULT.json':'fd5cc36371250132b07e2291242ce465cf7d7a1c711fb3273b70b99d547ab8d4',
SECOND/'PRODUCTION_RESULT.json':'4334b96168adc171dbaf14cb8aae492a8b9bc9550a6d1421283be0e8bce78241',
SECOND/'PRODUCTION_primary.json':'a0a12b5b2d7ae4ecf0fd167b547c47f960ac31ac5d1b79f62923fe39ba860ac2',
SECOND/'PRODUCTION_independent.json':'40577bac466df999b62af892acfd7b7bb8e3a43367d8d922c9e8d7415cbc1b99',
SECOND/'terminal_audit/AUDIT_RESULT.json':'5cfe74a338d44c3d760eabdd668407df7cee5e9dd8ad4a0968628d88a77fec55',
SECOND/'terminal_audit/TERMINAL.json':'d42e701108019ca50b2e9ede4adfbcf346bf66c94fbca560a246f35188db918f',
SECOND/'CONTRACT.md':'0aaaa012df848d662d688156b67e6c68bba538221ab769137fb5cb7edbcaeb22',
SECOND/'production_TERMINAL.json':'3f73c729b68fb27ce842670bcd1e6b7e4537099ba81ceb5a81979f329d7934b6',
CUBIC/'RESULT.json':'a9d4b4bc67b65021fbd3ecfdcbfe0ceb49bfa1572e9821e7e45b9bebf6940647',
CUBIC/'AUDIT_RESULT.json':'0b11deb93d18e7e1f3bae9b66d5f8245327a07e51fc822c26536834c630c0a02',
CUBIC/'production_TERMINAL.json':'0994c2ea5a63f4f36eb3d671edbdaefc7daf002123af4ea61913eec155741282',
CUBIC/'audit_TERMINAL.json':'ff334496fa45e2b5501229b9269399e88e8e182ec205be44cae82ecb5cbcdb4a',
CUBIC/'INDEPENDENT_TERMINAL_CHECK.json':'3c2bad23f68484c3bf85b0357c05c6e7c4df5b3fd304893ae18613ae83921d28',
CUBIC/'CONTRACT.md':'7ac66bdb3487891528021f75fd5dc3e05c09fb27163225a029f10cc45491d08e'}
PINS.update({ROOT/'check.py':'1cba3a85fd214b95cb3c4d70b2b847a8890dd614c6e042a5b60bb6579d678564',
             ROOT/'DERIVATION.md':'e65143f09dd0984691a3f6efa3689d3e7143c14481956af7e5e3827b9d688097',
             ROOT/'RESULT.json':'447b19af1290cffd82fdff0e3c7f3b78bffe24d1be088dc65dd6aeb3ac6ac608',
             ROOT/'BINDING.json':'c9f5c0a763cff1ab1b093db78f76b08e03053a4d05e57d4d3e2ec8586f2edc2a'})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def iv(obj):
    lo,hi=map(F,obj['exact_bounds']);assert lo<=hi;return lo,hi
def put(name,obj):
    p=ROOT/name;t=ROOT/(name+'.tmp')
    with t.open('x') as f:
        json.dump(obj,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001 and Path(sys.modules['_pylong'].__file__).resolve()==pylong
    paths=set(PINS)|{Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',ROOT/'TERMINAL.json',ROOT/'BINDING.json',
        RECON/'TERMINAL.json',RECON/'AUDIT_TERMINAL.json',RECON/'BINDING.json',pylong,
        FLOW/'FROZEN.json',FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    hashes={str(p):sha(p) for p in paths}
    for p,digest in PINS.items():assert sha(p)==digest
    for folder,term,res in ((ROOT,'TERMINAL.json','RESULT.json'),(RECON,'TERMINAL.json','RESULT.json'),(RECON,'AUDIT_TERMINAL.json','AUDIT_RESULT.json')):
        t=read(folder/term);assert t['pass'] and t['result_sha256']==sha(folder/res)
        if 'binding_sha256' in t:assert t['binding_sha256']==sha(folder/'BINDING.json')
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py') and binding['derivation_sha256']==sha(ROOT/'DERIVATION.md')
    assert binding['direction']==[1,0] and binding['factorial_convention']=='none'
    for p,digest in binding['inputs'].items():assert sha(p)==digest
    rec=read(RECON/'RESULT.json');ra=read(RECON/'AUDIT_RESULT.json')
    assert rec['pass'] and ra['pass'] and rec['normalized_radius']==ra['normalized_radius']
    second=read(SECOND/'PRODUCTION_RESULT.json');sa=read(SECOND/'terminal_audit/AUDIT_RESULT.json')
    st=read(SECOND/'production_TERMINAL.json');sat=read(SECOND/'terminal_audit/TERMINAL.json')
    assert second['all_gates'] and sa['status']=='PASS_SAVED_RECORD_CONSISTENCY'
    assert st['pass'] and sat['pass'] and st['frozen_sha256']==sat['producer_frozen_sha256']
    cubic=read(CUBIC/'RESULT.json')
    assert cubic['pass'] and read(CUBIC/'AUDIT_RESULT.json')['pass'] and read(CUBIC/'INDEPENDENT_TERMINAL_CHECK.json')['pass']
    for term,artifact in (('production_TERMINAL.json','RESULT.json'),('audit_TERMINAL.json','AUDIT_RESULT.json')):
        t=read(CUBIC/term);assert t['pass'] and t['artifacts'][artifact]==sha(CUBIC/artifact)
    ft=read(FLOW/'production_TERMINAL.json')
    assert sha(FLOW/'FROZEN.json')==FROZEN and ft['pass'] and ft['frozen_sha256']==FROZEN
    before=lease.observed();d1s=[];lengths=[];parameter_containment={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);lo,hi=map(F,flow['D']);assert 0<lo<=hi;lengths.append((lo,hi))
        production=read(SECOND/('PRODUCTION_'+name+'.json'));assert production['all_gates']
        sourcepath=SECOND/('PRODUCTION_'+name+'.json')
        assert read(FLOW/'FROZEN.json')['files'][str(sourcepath)]==PINS[sourcepath]
        original=iv(production['parameters']['k']);parent=iv(flow['parameters']['k'])
        assert parent[0]<=original[0]<=original[1]<=parent[1]
        parameter_containment[name]={'second':list(map(str,original)),'fullflow':list(map(str,parent))}
        d1=iv(production['d1']);d1s.append(d1)
        reconstructed=next(e for e in sa['engines'] if e['engine']==name)
        alo,ahi=iv(reconstructed['reconstructed']['d1'])
        assert d1[0]<=alo<=ahi<=d1[1]
    d1=(min(v[0] for v in d1s),max(v[1] for v in d1s))
    d2=iv(second['d2']);d3=iv(cubic['distance'])
    result=read(ROOT/'RESULT.json')
    assert result['pass']
    def unresolved(reason):
        assert result['classification']=='DISTANCE_SHORTENING_SUFFICIENT_TEST_UNRESOLVED'
        assert result['reason']==reason and result['shortening_certified'] is False
        after=lease.observed();assert before==after
        assert all(sha(p)==digest for p,digest in hashes.items())
        put('AUDIT_RESULT.json',{'pass':True,'classification':'DISTANCE_SUFFICIENT_TEST_UNRESOLVED_VERIFIED',
            'reason':reason,'shortening_certified':False,'source_sha256':sha(__file__),
            'inputs':hashes,'runtime_before':before,'runtime_after':after,
            'scope':'Verified unresolved sufficient test; not evidence against shortening or the branch.'})
        put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
            'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
    if not (d1[1]<0 and d2[1]<0 and d3[1]<0):
        assert {k:iv(v) for k,v in result['coefficients'].items()}=={'d1':d1,'d2':d2,'d3':d3}
        unresolved('SIGN_PREREQUISITE_NOT_MET');return
    lo=min(v[0] for v in lengths);hi=max(v[1] for v in lengths)
    s=F(rec['envelope_bound']);radius=F(rec['normalized_radius'])
    assert 0<s<1 and radius>0
    bound=hi*s*(1+F(1)/lo)/(1-s)
    strength=-d1[1]
    capped=result['classification']=='DISTANCE_SHORTENING_SUFFICIENT_TEST_UNRESOLVED'
    if capped:
        assert result['reason']=='NO_SUFFICIENT_RADIUS_WITHIN_512_HALVINGS'
    else:
        assert result['classification']=='DISTANCE_TAIL_SHORTENING_DIAGNOSTIC' and result['direction']==[1,0]
    history=result['radius_construction']
    assert 1<=len(history)<=513
    for i,row in enumerate(history):
        x=F(1,2**(i+1))
        ratio=bound*x*x*x/(radius*(1-x))
        accepted=ratio<=strength/2
        assert row=={'halvings':i,'x':str(x),'tail_per_z':str(ratio),'pass':accepted}
        assert accepted==((i==len(history)-1) and not capped)
    if capped:
        assert len(history)==513
        unresolved('NO_SUFFICIENT_RADIUS_WITHIN_512_HALVINGS');return
    x=F(1,2**len(history));zmax=radius*x
    tail=(bound*x*x*x*x)/(1-x)
    poly=zmax*(d1[1]+zmax*(d2[1]+zmax*d3[1]))
    assert 0<zmax<radius and tail<=strength*zmax/2
    assert poly+tail<=-strength*zmax/2<0
    vals={'distance_disk_radius':radius,'field_bound':s,'Dmin':lo,'Dmax':hi,'distance_bound':bound,
        'z_upper':zmax,'dyadic_fraction':x,'linear_strength':strength,'tail_at_upper':tail,
        'tail_per_z_at_upper':tail/zmax,'uniform_shortening_per_z':strength/2,
        'polynomial_upper_at_z_upper':poly,'total_upper_at_z_upper':poly+tail}
    assert {k:F(v) for k,v in result['exact'].items()}==vals
    assert {k:iv(v) for k,v in result['coefficients'].items()}=={'d1':d1,'d2':d2,'d3':d3}
    after=lease.observed();assert before==after
    assert all(sha(p)==digest for p,digest in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'DISTANCE_TAIL_SHORTENING_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,
        'runtime_before':before,'runtime_after':after,'exact':{k:str(v) for k,v in vals.items()},
        'parameter_containment':parameter_containment,'halvings':len(history)-1,
        'scope':'Exact inherited-coefficient hull, complex distance bound, first-passing dyadic construction and uniform shortening arithmetic. Inherits chart identity and analytic/ODE certificates; fixed lower-unit-current direction, not time contraction, stability or formation.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==FROZEN and read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('distance_tail_audit_lease',p)
        lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_120_SECONDS')))
        run(lease)
    except BaseException as error:
        if not (ROOT/'AUDIT_RESULT.json').exists():
            put('AUDIT_RESULT.json',{'pass':False,'classification':'TECHNICAL_INCOMPLETE',
                'source_sha256':sha(__file__),'error':repr(error),'traceback':traceback.format_exc()})
        if not (ROOT/'AUDIT_TERMINAL.json').exists():
            put('AUDIT_TERMINAL.json',{'pass':False,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),'source_sha256':sha(__file__)})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()

