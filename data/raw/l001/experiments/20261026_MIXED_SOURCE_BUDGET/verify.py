"""Independent exact mixed-row budget replay; no scientific producer imports."""
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
TRACE=BASE/'20261026_TRACEFREE_SOURCE_BUDGET'
PINS={FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',
      COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
      TRACE/'RESULT.json':'a03da75ab2f852014ff636a16d73849b11408c29f199d0bbc5fa28ad5ec62b51',
      TRACE/'AUDIT_RESULT.json':'f48a1106af8f914ca84f16bf8f8b2674b4bfcd9da499ea9d770feb993bc98be9'}
PINS.update({ROOT/'check.py':'6600bff73faf3cc65b5fe434450e560aeeea16f21636fc3ca5638e47d5f8f4ec',
             ROOT/'DERIVATION.md':'05c210bff3c993c77fcefcae452c70f5c84ac4e066a4a632676d131491d812cf',
             ROOT/'RESULT.json':'8921c6fd7706c5f421aef069be664c519467beece8b8cc0649dc9bc18487dd19',
             ROOT/'BINDING.json':'b4675bc2f477f0c767082c60ea4678c966abbfc0b95c2cb93eb240d80b7b8d8c'})
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def put(name,value):
    p=ROOT/name;t=ROOT/(name+'.tmp')
    with t.open('x') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/s).exists() for s in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths=set(PINS)|{Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',
        ROOT/'TERMINAL.json',ROOT/'BINDING.json',FLOW/'production_TERMINAL.json',
        FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    terminals=[]
    for folder in (ROOT,COLLAR,REAL,TRACE):
        paths.update({folder/'TERMINAL.json',folder/'BINDING.json'})
        terminals.append((folder,'TERMINAL.json','RESULT.json'))
    for folder in (COLLAR,TRACE):
        paths.add(folder/'AUDIT_TERMINAL.json');terminals.append((folder,'AUDIT_TERMINAL.json','AUDIT_RESULT.json'))
    hashes={str(p):sha(p) for p in paths}
    for p,h in PINS.items():assert sha(p)==h
    for folder,t,r in terminals:
        term=read(folder/t)
        assert term['pass'] and term['result_sha256']==sha(folder/r)
        if 'binding_sha256' in term:assert term['binding_sha256']==sha(folder/'BINDING.json')
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py')
    assert binding['derivation_sha256']==sha(ROOT/'DERIVATION.md')
    for p,h in binding['inputs'].items():assert sha(p)==h
    r=read(ROOT/'RESULT.json');trace=read(TRACE/'RESULT.json')
    real=read(REAL/'RESULT.json');collar=read(COLLAR/'RESULT.json')
    assert all(x['pass'] for x in (r,trace,real,collar,read(TRACE/'AUDIT_RESULT.json'),read(COLLAR/'AUDIT_RESULT.json')))
    assert real['unresolved']==[]
    assert r['classification']=='MIXED_SOURCE_BUDGET_DIAGNOSTIC'
    assert r['formal_coefficientwise'] and r['numerical_evaluation_condition']=='a*y<1'
    assert not r['full_majorant_closed'] and not r['amplitude_radius_certified']
    radius,rho,eps,g,hmin=F(1,20000),F(1,40000),F(1,1000),F(3,25),F(1,100)
    assert F(r['background_collar'])==F(collar['rho'])==radius
    assert F(r['working_collar'])==F(trace['working_collar'])==rho
    assert F(collar['epsilon'])==eps
    scale=F(2)/rho;assert scale>=1 and F(r['composition_scale'])==scale
    assert F(r['h_lower'])==hmin
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(r['arms'])==set(real['arms'])==set(trace['arms'])=={'primary','independent'}
    before=lease.observed();arms={}
    for name in ('primary','independent'):
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);kl,ku=map(F,flow['parameters']['k']['exact_bounds']);lo,hi=map(F,flow['D'])
        assert hi>=lo>1 and hmin*hmin<kl<=ku<F(1,2500)
        ext=real['arms'][name]['extrema'];hb=F(ext['H0'])+eps;tb=F(ext['T0'])+eps
        background=hb+tb/F(3)
        # Separate transport, composed-background, and bilinear row contributions.
        transport_first=g;transport_second=F(3)*g
        composed_difference=background*g*scale
        composed_transport=F(2)*background*g
        bilinear=(F(1)+F(1,3))*g*F(2)
        parts=[transport_first,transport_second,composed_difference,composed_transport,bilinear]
        mixed=sum(parts)
        assert mixed==g*(F(20,3)+(hb+tb/F(3))*(scale+2))
        # Reconstruct inherited C_T independently rather than only copying it.
        ct=F(40)*g*g*(rho*rho+9*rho+108)/(36*kl*rho*rho)
        assert ct==F(trace['arms'][name]['tracefree_constant'])
        source=hb*ct+mixed/(F(6)*hmin)
        vals={'Hbar':hb,'Tbar':tb,'background_combination':background,
              'mixed_constant':mixed,'tracefree_constant':ct,'metric_source_constant':source}
        saved=r['arms'][name]
        assert list(map(F,saved['raw_contributions']))==parts
        assert {k:F(v) for k,v in saved['exact'].items()}==vals
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'raw_contributions':list(map(str,parts))}
    after=lease.observed();assert before==after
    assert all(sha(p)==h for p,h in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'MIXED_SOURCE_BUDGET_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'runtime_before':before,'runtime_after':after,
        'scope':'Exact mixed-row contribution and S_p reconstruction constants on the fixed working collar. Inherits analytic coefficient/index reasoning and compatibility. Numerical rational evaluation requires a*y<1. No full closure or amplitude radius.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==PINS[FLOW/'FROZEN.json']
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('mixed_audit_lease',p)
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
