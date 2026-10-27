"""Exact weighted-response inequalities on an authenticated complex background collar."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
io=load('weighted_io',base/'extract.py')
assert io.sha(base/'extract.py')=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io.ROOT=ROOT
lease=load('weighted_lease',io.LEASE);lease.ROOT=ROOT
COLLAR=ROOT.parent/'20261026_COMPLEX_BACKGROUND_COLLAR'
AUDIT=ROOT.parent/'20261026_RESPONSE_AUDIT'
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    pins={COLLAR/'RESULT.json':'a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68',
          COLLAR/'AUDIT_RESULT.json':'28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd',
          AUDIT/'RESULT.json':'6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385'}
    for p,d in pins.items():assert io.sha(p)==d
    assert io.read(COLLAR/'AUDIT_RESULT.json')['pass']
    assert io.read(COLLAR/'AUDIT_TERMINAL.json')['result_sha256']==pins[COLLAR/'AUDIT_RESULT.json']
    collar=io.read(COLLAR/'RESULT.json');real=io.read(AUDIT/'RESULT.json')
    assert collar['pass'] and real['pass'] and real['scalar_constant']==3932
    rho=Q(collar['rho']);eps=Q(collar['epsilon']);assert rho==Q(1,20000)
    alpha=rho/2+rho*rho/4
    assert 1-6*alpha>0
    scalar=7*(7864*(2+rho/2)+alpha)/(1-6*alpha)+1
    binding={'source':io.sha(__file__),'derivation':io.sha(ROOT/'DERIVATION.md'),
             'inputs':{str(p):d for p,d in pins.items()},'runtime':lease.observed()}
    io.put('BINDING.json',binding)
    arms={}
    assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    for name in ('primary','independent'):
        cb={k:Q(v) for k,v in collar['arms'][name]['exact'].items()}
        assert cb['drift_absolute']<=5 and cb['potential_over_n2_absolute']<=6
        e={k:Q(v) for k,v in real['arms'][name]['extrema'].items()}
        flowpath=io.FLOW/('FLOW_'+name+'.json');assert io.sha(flowpath)==ft['artifacts'][flowpath.name]
        kup=io.iv(io.read(flowpath)['parameters']['k'])[1]
        H,T,P,m,k,emin=[e[v] for v in ('H0','T0','P0','m0','k0','e0')]
        Hb,Tb,Pb,Eb=H+eps,T+eps,P+eps,8+eps
        U=m*P+4*H*T;d0=42*k*emin*emin
        Hp=Tb*Tb/3+kup*Eb*Eb;Tp=m*Pb+4*Hb*Tb
        A0=max(Q(1),T+U)/d0
        margin=1-rho*Hb;assert margin>0
        B0=(A0+rho*(Tb/6+Q(1,2)))/margin
        B1=2*Hb*B0+Tb/3+1
        B2=2*Hp*B0+2*Hb*B1+(Tp+Tb)/3+12/rho
        total=B0+B1+B2
        vals=dict(real_anchor=A0,metric_absorption=margin,metric_value=B0,metric_first=B1,metric_second=B2,metric_sum=total)
        arms[name]={'exact':{a:str(v) for a,v in vals.items()},'display':{a:float(v) for a,v in vals.items()},
                    'metric_integer':-(-total.numerator//total.denominator)}
    result={'pass':True,'classification':'WEIGHTED_COMPLEX_RESPONSE_DIAGNOSTIC','rho':str(rho),
       'scalar_exact':str(scalar),'scalar_integer':-(-scalar.numerator//scalar.denominator),
       'scalar_absorption_margin':str(1-6*alpha),'arms':arms,
       'metric_integer':max(a['metric_integer'] for a in arms.values()),
       'independent_arithmetic_replay':False,'nonlinear_majorant_complete':False,'amplitude_radius_certified':False}
    for p,d in pins.items():assert io.sha(p)==d
    assert binding['source']==io.sha(__file__) and binding['derivation']==io.sha(ROOT/'DERIVATION.md')
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({'scalar_integer':result['scalar_integer'],'metric_integer':result['metric_integer'],'arms':{n:a['display'] for n,a in arms.items()}}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('WEIGHTED_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
