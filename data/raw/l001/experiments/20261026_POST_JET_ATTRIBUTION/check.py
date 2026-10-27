"""Exact positive-budget attribution, not a physical-mechanism decomposition.
No modified bound, new certificate, or ODE calculation.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,signal,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
boot=BASE/'20261026_JET_DOWNSTREAM/check.py'
assert hashlib.sha256(boot.read_bytes()).hexdigest()=='77baf9fcfac71c419f16c75e7f9ab6869c539fe677db01c8a622f0a2b7137009'
spec=importlib.util.spec_from_file_location('post_jet',boot);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
io,lease=m.io,m.lease;io.ROOT=ROOT;lease.ROOT=ROOT
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120);io.put('START.json',{'cpu':cpu,'occupied':occupied})
    parentroot=BASE/'20261026_JET_DOWNSTREAM'
    inputs={str(boot):io.sha(boot),str(parentroot/'RESULT.json'):'7351b7fe985384b71e2a01763a671fdc217cab44ebd89f7fcda6c86b21e02951',
            str(parentroot/'BINDING.json'):'3a26474338e194ccedcf6353ab91346b3197c80ebf485bc7e460f9ac1ebb2a73'}
    for p,h in inputs.items():assert io.sha(p)==h
    for p,h in io.read(parentroot/'BINDING.json')['inputs'].items():
        assert p not in inputs or inputs[p]==h
        inputs[p]=h
    for p,h in inputs.items():assert io.sha(p)==h
    t=io.read(parentroot/'TERMINAL.json');assert t['pass'] and t['result_sha256']==io.sha(parentroot/'RESULT.json') and t['binding_sha256']==io.sha(parentroot/'BINDING.json')
    inputs[str(parentroot/'TERMINAL.json')]=io.sha(parentroot/'TERMINAL.json')
    assert io.sha('/usr/lib/python3.12/_pylong.py')=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    before=lease.observed();source=io.sha(__file__)
    io.put('BINDING.json',{'inputs':inputs,'source_sha256':source,'runtime':before})
    def parent(n):return io.read(BASE/('20261026_'+n+'/RESULT.json'))
    down=io.read(parentroot/'RESULT.json')['variants']['cancellation_and_jets']
    diag=parent('CANCELLATION_JET_DIAGNOSTIC')['variants']['cancellation_and_jets']
    old=parent('COEFFICIENT_ENVELOPE_CLOSURE');split=parent('SPLIT_METRIC_RESPONSE')
    radial,collar,wall,normal=map(parent,('SCALAR_RADIAL_SOURCE_BUDGET','COMPLEX_BACKGROUND_COLLAR','ISRAEL_OSCILLATOR_WALL_BUDGET','SCALAR_NORMAL_WALL_BUDGET'))
    arms={}
    for name in ('primary','independent'):
        def exact(o):return {k:Q(v) for k,v in o['arms'][name]['exact'].items()}
        r,c,w,j=map(exact,(radial,collar,wall,normal));d={k:Q(v) for k,v in diag['arms'][name]['exact'].items()}
        H,T,P,mass=r['Hbar'],r['Tbar'],r['Pbar'],r['mass_bound'];Tp=mass*P+4*H*T
        S=Q(old['arms'][name]['scalar_response']);C=Q(old['arms'][name]['metric_response']);Cr=Q(split['arms'][name]['remainder_ceiling'])
        weight=1+3*Cr+2/c['oscillator_over_n2'];channels={}
        for channel in ('geometric','current'):
            geom=channel=='geometric';xi=w['graph_'+channel];osc=w['oscillator_weighted'] if geom else Q(0)
            loads={'bulk_F':d['F'] if geom else Q(0),
                   'Robin_constraint':4*T*c['inverse_A_absolute']*d['Sc']/c['D_over_n2'] if geom else Q(0),
                   'Robin_tracefree':2*T*c['inverse_A_absolute']*d['V0'] if geom else Q(0),
                   'Robin_graph':c['inverse_A_absolute']*(Tp+21*T/2)*xi,
                   'Robin_scalar_normal':c['inverse_A_absolute']*j['weighted_'+channel+'_constant'],
                   'Robin_oscillator':c['inverse_A_absolute']*osc/(2*c['oscillator_over_n2'])}
            pieces={k:weight*S*v for k,v in loads.items()}
            pieces.update({'direct_constraint':3*Cr*d['Sc'] if geom else Q(0),'direct_mixed':3*C*d['Sp'] if geom else Q(0),
                           'direct_tracefree':d['Ct'] if geom else Q(0),'direct_graph':xi,
                           'direct_oscillator_reconstruction':(T*xi+osc)/c['oscillator_over_n2']})
            K=Q(down['arms'][name][channel]);assert sum(pieces.values())==K and all(v>=0 for v in pieces.values())
            shares={k:v/K for k,v in pieces.items()};assert sum(shares.values())==1
            channels[channel]={'exact_shares':{k:str(v) for k,v in shares.items()},'display_shares':{k:float(v) for k,v in shares.items()}}
        E=Q(8001,1000);g=Q(3,25);h=Q(1,50);a=Q(80000);v=E*g
        coparts={'lapse':E**2*(g*g+3*h*g)*(a+2+2*v*v),'ordinary_friction':2*E**2*g*g*(H+1),
                 'velocity_friction':E**3*v*g**3*(3+H),'scalar_trace_tail':P*a*a}
        CO=sum(coparts.values());assert 24*CO==w['oscillator_weighted']
        oshares={k:v/CO for k,v in coparts.items()};assert sum(oshares.values())==1
        arms[name]={'channels':channels,'oscillator_source_shares':{k:str(v) for k,v in oshares.items()},
                    'oscillator_source_display':{k:float(v) for k,v in oshares.items()}}
    assert before==lease.observed() and io.sha(__file__)==source and all(io.sha(p)==h for p,h in inputs.items())
    result={'pass':True,'classification':'POST_JET_BOUND_ATTRIBUTION','arms':arms,
            'scope':'Shares of sufficient positive bound constants only. Not measured physical contributions, instability or a new amplitude certificate.'}
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({n:{'channels':{c:x['display_shares'] for c,x in v['channels'].items()},'oscillator':v['oscillator_source_display']} for n,v in arms.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ATTRIBUTION_120_SECONDS')))
        run()
    except BaseException as e:
        io.put('FAILURE.json',{'error':repr(e),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
