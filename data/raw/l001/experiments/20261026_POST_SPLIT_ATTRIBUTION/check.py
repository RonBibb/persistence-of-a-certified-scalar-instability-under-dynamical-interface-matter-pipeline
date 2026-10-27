"""Exact attribution of the accepted split bound; no new certificate."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import importlib.util,hashlib,json,signal
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
bootstrap=BASE/'20261026_SPLIT_METRIC_RESPONSE/check.py'
assert hashlib.sha256(bootstrap.read_bytes()).hexdigest()=='5fbb650408ef2a94986213f73493e2a4798cda683fcfbf12cc3ac235b5b58a60'
sp=importlib.util.spec_from_file_location('attribution_bootstrap',bootstrap)
m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
io=m.io;lease=m.lease;io.ROOT=ROOT;lease.ROOT=ROOT
def run():
    assert sys.platform=='linux' and not (ROOT/'RESULT.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    split=BASE/'20261026_SPLIT_METRIC_RESPONSE'
    pins={'RESULT.json':'fd57632ed9769362a99d985699be6250dbb499a99ef5d8e21d44875d8e2c41f0',
          'BINDING.json':'5b468c55a6da625f68662a8edfba400ca26d521e71921eb164cf5ede11d8a47b',
          'AUDIT_RESULT.json':'2fc315c4b56af4f6c67355823a557892bb2760eb50ea27a979f0fd4a0814ab00'}
    inputs={str(split/k):v for k,v in pins.items()}
    for p,h in inputs.items():assert io.sha(p)==h
    inputs.update(io.read(split/'BINDING.json')['inputs'])
    for p,h in inputs.items():assert io.sha(p)==h
    result=io.read(split/'RESULT.json');audit=io.read(split/'AUDIT_RESULT.json')
    assert result['pass'] and audit['pass'] and result['exact']==audit['exact']
    assert len(str(10**20000))==20001
    before=lease.observed();source=io.sha(__file__)
    def parent(n):return io.read(BASE/('20261026_'+n+'/RESULT.json'))
    old=parent('COEFFICIENT_ENVELOPE_CLOSURE');rad=parent('SCALAR_RADIAL_SOURCE_BUDGET')
    normal=parent('SCALAR_NORMAL_WALL_BUDGET');wall=parent('ISRAEL_OSCILLATOR_WALL_BUDGET')
    mixed=parent('MIXED_SOURCE_BUDGET');trace=parent('TRACEFREE_SOURCE_BUDGET')
    real=parent('RESPONSE_AUDIT');collar=parent('COMPLEX_BACKGROUND_COLLAR');arms={}
    for name in ('primary','independent'):
        def exact(o):return {k:Q(v) for k,v in o['arms'][name]['exact'].items()}
        cb,rb,nb,wb,mb=map(exact,(collar,rad,normal,wall,mixed))
        ext={k:Q(v) for k,v in real['arms'][name]['extrema'].items()}
        T=ext['T0']+Q(1,1000);H=ext['H0']+Q(1,1000);P=ext['P0']+Q(1,1000)
        Tp=ext['m0']*P+4*H*T
        ai,dd,do=cb['inverse_A_absolute'],cb['D_over_n2'],cb['oscillator_over_n2']
        S=Q(old['arms'][name]['scalar_response']);C=Q(old['arms'][name]['metric_response'])
        Cr=Q(result['arms'][name]['remainder_ceiling']);weight=1+3*Cr+2/do;channels={}
        for channel in ('geometric','current'):
            geom=channel=='geometric';saved={k:Q(v) for k,v in old['arms'][name]['channels'][channel].items()}
            ct=Q(trace['arms'][name]['tracefree_constant']) if geom else Q(0)
            sc=rb['Sc_constant'] if geom else Q(0);force=rb['F_constant'] if geom else Q(0)
            spc=mb['metric_source_constant'] if geom else Q(0)
            xi=wb['graph_'+channel];j=nb['weighted_'+channel+'_constant'];o=wb['oscillator_weighted'] if geom else Q(0)
            loads={'bulk_F':force,'Robin_constraint':4*T*ai*sc/dd,'Robin_tracefree':ai*2*T*ct,
                   'Robin_graph':ai*(Tp+21*T/2)*xi,'Robin_scalar_normal':ai*j,'Robin_oscillator':ai*o/(2*do)}
            assert sum(loads.values())*S==saved['Uf']
            pieces={k:weight*S*v for k,v in loads.items()}
            pieces.update({'direct_constraint':3*Cr*sc,'direct_mixed':3*C*spc,
                'direct_tracefree':ct,'direct_graph':xi,'direct_oscillator_reconstruction':(T*xi+o)/do})
            K=Q(result['arms'][name]['channels'][channel]['new_K']);assert sum(pieces.values())==K
            shares={k:v/K for k,v in pieces.items()};assert sum(shares.values())==1
            channels[channel]={'exact_shares':{k:str(v) for k,v in shares.items()},'display_shares':{k:float(v) for k,v in shares.items()}}
        ct=Q(trace['arms'][name]['tracefree_constant']);sc_parts={'mixed':12*H*mb['metric_source_constant'],
                 'tracefree':(12*H*H+T*T)*ct,'raw_radial':rb['radial_constant']}
        assert sum(sc_parts.values())==rb['Sc_constant']
        arms[name]={'channels':channels,'Sc_source_shares':{k:float(v/rb['Sc_constant']) for k,v in sc_parts.items()},
                    'Sc_source_shares_exact':{k:str(v/rb['Sc_constant']) for k,v in sc_parts.items()}}
    assert lease.observed()==before and io.sha(__file__)==source
    assert all(io.sha(p)==h for p,h in inputs.items())
    out={'pass':True,'classification':'POST_SPLIT_EXACT_ATTRIBUTION_DIAGNOSTIC','arms':arms,'inputs':inputs,
         'source_sha256':source,'runtime':before,'cpu':cpu,'occupied':occupied,
         'scope':'Shares of conservative bounds, not physical mechanism shares. No new radius or centered-remainder certificate.'}
    io.put('RESULT.json',out);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json')})
    print(json.dumps({n:{'channels':{c:v['display_shares'] for c,v in a['channels'].items()},'Sc_source_shares':a['Sc_source_shares']} for n,a in arms.items()}),flush=True)
try:
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ATTRIBUTION_120_SECONDS')))
    run()
finally:
    signal.alarm(0)
    for handle in lease.handles:handle.close()
