"""Independent Fraction replay of weighted response constants; no ODE replay."""
import sys
sys.dont_write_bytecode=True
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
COLLAR=BASE/'20261026_COMPLEX_BACKGROUND_COLLAR'
REAL=BASE/'20261026_RESPONSE_AUDIT'
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
PINS={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
      COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
      REAL/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',
      FLOW/'FROZEN.json':'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'}
PINS.update({ROOT/'RESULT.json':'771651f65699357af6f999ab393dfa0db885343551e24890b29ee2aa68bd118d',
             ROOT/'BINDING.json':'0d41dbacb3c7f186227292499edaad80155ebdfb4595b692904366d4d7be41f4',
             ROOT/'check.py':'6204c4ef6091026cec6bcadecaeb0abba282922dee7f8f14bd42e0f06c84f90a'})
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def put(name,data):
    p=ROOT/name;t=ROOT/(name+'.tmp')
    with t.open('x') as f:
        json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def ceil(q): return -((-q.numerator)//q.denominator)
def terminal(folder,name,result):
    t=read(folder/name)
    assert t['pass'] and t['result_sha256']==sha(folder/result)
    if 'binding_sha256' in t:assert t['binding_sha256']==sha(folder/'BINDING.json')
    return t
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths=list(PINS)+[Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',
        ROOT/'TERMINAL.json',ROOT/'BINDING.json',COLLAR/'AUDIT_TERMINAL.json',
        COLLAR/'TERMINAL.json',COLLAR/'BINDING.json',REAL/'TERMINAL.json',REAL/'BINDING.json',
        FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',FLOW/'FLOW_independent.json',
        BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py']
    inputs={str(p):sha(p) for p in paths}
    for p,h in PINS.items():assert sha(p)==h
    terminal(ROOT,'TERMINAL.json','RESULT.json')
    terminal(COLLAR,'TERMINAL.json','RESULT.json')
    terminal(COLLAR,'AUDIT_TERMINAL.json','AUDIT_RESULT.json')
    terminal(REAL,'TERMINAL.json','RESULT.json')
    assert read(COLLAR/'AUDIT_RESULT.json')['pass']
    binding=read(ROOT/'BINDING.json')
    assert binding['source']==sha(ROOT/'check.py') and binding['derivation']==sha(ROOT/'DERIVATION.md')
    for p,h in binding['inputs'].items():assert sha(p)==h
    r=read(ROOT/'RESULT.json');c=read(COLLAR/'RESULT.json');real=read(REAL/'RESULT.json')
    assert r['pass'] and r['classification']=='WEIGHTED_COMPLEX_RESPONSE_DIAGNOSTIC'
    assert real['pass'] and real['unresolved']==[] and real['scalar_constant']==3932
    assert c['pass'] and not c['parameters_complexified']
    assert not r['nonlinear_majorant_complete'] and not r['amplitude_radius_certified']
    rho=F(1,20000);eps=F(1,1000)
    assert F(r['rho'])==F(c['rho'])==rho and F(c['epsilon'])==eps
    # Sum the two primitive inequalities, then use the scalar equation.
    primitive_sum=rho*(F(1,2)+rho/F(4))
    absorption=F(1)-F(6)*primitive_sum
    assert absorption>0
    anchor=F(2)*F(real['scalar_constant'])
    xy=(anchor*(F(2)+rho/F(2))+primitive_sum)/absorption
    scalar=F(7)*xy+1
    assert F(r['scalar_absorption_margin'])==absorption
    assert F(r['scalar_exact'])==scalar and r['scalar_integer']==ceil(scalar)
    ft=read(FLOW/'production_TERMINAL.json')
    assert ft['pass'] and ft['frozen_sha256']==PINS[FLOW/'FROZEN.json']
    assert set(r['arms'])==set(real['arms'])==set(c['arms'])=={'primary','independent'}
    runtime=lease.observed();arms={}
    for name in ('primary','independent'):
        coefficients=c['arms'][name]['exact']
        assert F(coefficients['drift_absolute'])<=5
        assert F(coefficients['potential_over_n2_absolute'])<=6
        path=FLOW/('FLOW_'+name+'.json')
        assert sha(path)==ft['artifacts'][path.name]
        kl,ku=map(F,read(path)['parameters']['k']['exact_bounds'])
        ext=real['arms'][name]['extrema']
        H,T,P,m,k,e=(F(ext[s]) for s in ('H0','T0','P0','m0','k0','e0'))
        assert 0<k==kl<=ku and e>0 and min(H,T,P,m)>=0
        hb,tb,pb,eb=H+eps,T+eps,P+eps,F(8)+eps
        real_tprime=m*P+F(4)*H*T
        anchor_metric=max(F(1),T+real_tprime)/(F(42)*k*e*e)
        margin=1-rho*hb;assert margin>0
        value=(anchor_metric+rho*(tb/F(6)+F(1,2)))/margin
        first=F(2)*hb*value+tb/F(3)+1
        hp=tb*tb/F(3)+ku*eb*eb
        tp=m*pb+F(4)*hb*tb
        second=F(2)*(hp*value+hb*first)+(tp+tb)/F(3)+F(12)/rho
        total=value+first+second
        vals={'real_anchor':anchor_metric,'metric_absorption':margin,'metric_value':value,
              'metric_first':first,'metric_second':second,'metric_sum':total}
        saved=r['arms'][name]
        assert {s:F(v) for s,v in saved['exact'].items()}==vals
        assert saved['metric_integer']==ceil(total)
        arms[name]={'exact':{s:str(v) for s,v in vals.items()},'metric_integer':ceil(total)}
    assert r['metric_integer']==max(a['metric_integer'] for a in arms.values())
    after=lease.observed();assert runtime==after
    assert all(sha(p)==h for p,h in inputs.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'WEIGHTED_COMPLEX_RESPONSE_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':inputs,'cpu':cpu,'occupied':occupied,
        'runtime_before':runtime,'runtime_after':after,'arms':arms,'scalar_exact':str(scalar),
        'scalar_integer':ceil(scalar),'metric_integer':r['metric_integer'],
        'scope':'A priori bounds for compatible holomorphic solutions; inherits audited background and real-axis inverse. No ODE replay, arbitrary metric-source solvability, nonlinear majorant, or amplitude radius.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        s=importlib.util.spec_from_file_location('weighted_audit_lease',p)
        lease=importlib.util.module_from_spec(s);s.loader.exec_module(lease);lease.ROOT=ROOT
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
