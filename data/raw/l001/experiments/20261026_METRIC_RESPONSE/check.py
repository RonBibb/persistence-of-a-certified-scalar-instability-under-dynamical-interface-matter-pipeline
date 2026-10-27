"""Exact conditional real-axis metric response constants; no ODE."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,hashlib,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
io=load('metric_io',BASE/'extract.py')
assert io.sha(BASE/'extract.py')=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io.ROOT=ROOT
lease=load('metric_lease',io.LEASE);lease.ROOT=ROOT
def checked(folder):
    t=io.read(folder/'TERMINAL.json');assert t['pass']
    assert io.sha(folder/'RESULT.json')==t['result_sha256']
    return io.read(folder/'RESULT.json')
def main():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    lowfolder=ROOT.parent/'20261026_LOW_ORDER_RESPONSE'
    highfolder=ROOT.parent/'20261026_HIGH_ORDER_RESPONSE'
    low=checked(lowfolder);high=checked(highfolder)
    assert io.sha(BASE/'RESULT.json')=='23605bfbe42485d19e9f952ebd8f791984955ad04926eba697f283d6bc5aab38'
    background=io.read(BASE/'RESULT.json')
    assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
    t=io.read(io.FLOW/'production_TERMINAL.json');assert t['pass'] and t['frozen_sha256']==io.EXPECTED
    binding={'source':io.sha(__file__),'runtime':lease.observed(),'inputs':{str(f/'RESULT.json'):io.sha(f/'RESULT.json') for f in (BASE,lowfolder,highfolder)}}
    io.put('BINDING.json',binding)
    arms={};Cf=Q(3932)
    for name in ('primary','independent'):
        orders=low['arms'][name];assert set(orders)==set(map(str,range(1,39)))
        assert all(r['positive_gate'] and Q(r['C_sum_exact'])<=Cf for r in orders.values())
        assert high['arms'][name]['N']==39 and high['arms'][name]['outward_integer_C_sum']<=Cf
        assert high['arms'][name]['E_upper']==8
        path=io.FLOW/('FLOW_'+name+'.json');assert io.sha(path)==t['artifacts'][path.name]
        data=io.read(path);kup=io.iv(data['parameters']['k'])[1]
        e={k:Q(v) for k,v in background['arms'][name]['extrema_exact'].items()}
        constants={k:Q(v) for k,v in background['arms'][name]['cutoff']['constants'].items()}
        H,T,U,d=e['H0'],e['T0'],constants['U0'],constants['d0']
        assert d>0
        Hp=T*T/3+64*kup
        P0=(1+(T+U)*Cf)/d
        P1=2*H*P0+T*Cf/3+1
        P2=2*Hp*P0+2*H*P1+(U+T)*Cf/3+1
        total=P0+P1+P2
        vals=dict(Hprime_bound=Hp,P_value=P0,P_first=P1,P_second=P2,P_sum=total)
        arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
                    'outward_integer_P_sum':-(-total.numerator//total.denominator)}
    assert io.sha(__file__)==binding['source']
    for p,digest in binding['inputs'].items():assert io.sha(p)==digest
    result={'classification':'CONDITIONAL_REAL_AXIS_METRIC_RESPONSE_DIAGNOSTIC','arms':arms,
       'common_P_constant':max(v['outward_integer_P_sum'] for v in arms.values()),
       'R':'||Sc|| + ||F|| + n max_i |g_i| + n ||Sp|| + ||Spprime||',
       'p_bound':'n^2 ||p|| + n ||pprime|| + ||psecond|| <= common_P_constant R',
       'b_bound':'norm_n(b) <= norm_n(c) + 2 common_P_constant R, b=c-2p',
       'valid_orders':'all integers n >= 1; compatible real sources with required regularity',
       'divides_by_scalar_gradient':False,'independent_arithmetic_replay':False,
       'complex_collar_bound':False,'amplitude_radius_certified':False}
    io.put('RESULT.json',result)
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({'common_P_constant':result['common_P_constant'],'arms':{n:v['display'] for n,v in arms.items()}}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('METRIC_120_SECONDS')))
        main()
    except BaseException as exc:
        io.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()})
        raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
