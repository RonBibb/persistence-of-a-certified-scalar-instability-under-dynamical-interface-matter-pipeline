"""Independent exact tracefree rational-function and reconstruction audit."""
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
PINS={FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',
      COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'}
PINS.update({ROOT/'check.py':'010e224a5e84e5954113f73ec469e409d520325aac4427f753fc45ef8e6c6ee5',
             ROOT/'DERIVATION.md':'05a758af8a0e2a847a3577b41aff2e1aeed6b6d95a72e157d14ad10601fb6060',
             ROOT/'RESULT.json':'a03da75ab2f852014ff636a16d73849b11408c29f199d0bbc5fa28ad5ec62b51',
             ROOT/'BINDING.json':'20184befff1c3e0db1663d6c4a852cfa82bc62a23e9cac375c8b1feaef9ea3dc'})
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
def terminal(folder,t,r):
    value=read(folder/t)
    assert value['pass'] and value['result_sha256']==sha(folder/r)
    if 'binding_sha256' in value:assert value['binding_sha256']==sha(folder/'BINDING.json')
def add(*ps):
    return [sum(p[i] if i<len(p) else F(0) for p in ps) for i in range(max(map(len,ps)))]
def mul(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return out
def scale(a,c):return [F(c)*v for v in a]
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/p).exists() for p in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths=set(PINS)|{Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'BINDING.json',
        ROOT/'RESULT.json',ROOT/'TERMINAL.json',COLLAR/'TERMINAL.json',COLLAR/'BINDING.json',
        COLLAR/'AUDIT_TERMINAL.json',REAL/'TERMINAL.json',REAL/'BINDING.json',
        FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    hashes={str(p):sha(p) for p in paths}
    for p,h in PINS.items():assert sha(p)==h
    for folder,t,r in ((ROOT,'TERMINAL.json','RESULT.json'),(COLLAR,'TERMINAL.json','RESULT.json'),
        (COLLAR,'AUDIT_TERMINAL.json','AUDIT_RESULT.json'),(REAL,'TERMINAL.json','RESULT.json')):
        terminal(folder,t,r)
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py')
    assert binding['derivation_sha256']==sha(ROOT/'DERIVATION.md')
    for p,h in binding['inputs'].items():assert sha(p)==h
    result=read(ROOT/'RESULT.json')
    assert result['pass'] and result['classification']=='TRACEFREE_SOURCE_BUDGET_DIAGNOSTIC'
    assert not result['full_majorant_closed'] and not result['amplitude_radius_certified']
    radius=F(1,20000);rho=F(1,40000);g=F(3,25);h=F(1,50)
    assert F(read(COLLAR/'RESULT.json')['rho'])==F(result['background_collar'])==radius
    assert F(result['working_collar'])==rho
    # Independently build B's full numerator over (1-y)^2 by polynomial operations.
    y=[F(0),F(1)];one_minus_y=[F(1),F(-1)]
    wnum=scale(y,2*g);wrnum=scale(y,g)
    dtwnum=add(mul(scale(y,2*g*g),one_minus_y),scale(mul(y,y),2*g*g))
    transport=mul(y,add(scale(mul(wnum,one_minus_y),4*g),
        scale(mul(wnum,wrnum),2),scale(dtwnum,2),
        scale(mul(wnum,one_minus_y),2*h),scale(mul(wnum,wnum),2)))
    temporal_numerator=add(scale(one_minus_y,g),wnum)
    bulk=scale(mul(mul(temporal_numerator,temporal_numerator),mul(y,y)),6)
    numerator=add(transport,bulk)
    assert numerator[:2]==[0,0] and len(numerator)==5
    a=numerator[2:];assert all(v>0 for v in a)
    assert list(map(F,result['numerator_coefficients']))==a
    total=sum(a);assert total==40*g*g==F(result['raw_source_constant'])
    # Positive numerator plus decreasing shifted coefficients of (1-y)^-2
    # gives the all-order bound, not a sampled finite-series assertion.
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(result['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);lo,hi=map(F,flow['D']);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        assert hi>=lo>1 and 1+rho/lo<2 and 0<kl<=ku<h*h
        reconstruction=(rho*rho+9*rho+108)/(36*kl*rho*rho)
        saved=result['arms'][name]
        assert F(saved['k_min'])==kl and F(saved['raw_to_c'])==reconstruction
        assert F(saved['tracefree_constant'])==total*reconstruction
        arms[name]={'k_min':str(kl),'raw_to_c':str(reconstruction),'tracefree_constant':str(total*reconstruction)}
    after=lease.observed();assert before==after
    assert all(sha(p)==v for p,v in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'TRACEFREE_SOURCE_BUDGET_ARITHMETIC_VERIFIED',
        'inputs':hashes,'source_sha256':sha(__file__),'cpu':cpu,'occupied':occupied,
        'runtime_before':before,'runtime_after':after,'numerator_coefficients':list(map(str,a)),
        'raw_source_constant':str(total),'arms':arms,
        'scope':'Exact rational-function identity, positive coefficient bound, and Nagumo constants on rho=1/40000; inherited analytic index argument. Tracefree only, no full nonlinear closure or amplitude radius.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PINS[FLOW/'FROZEN.json']
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('tracefree_audit_lease',p)
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
