"""Separate arithmetic reconstruction of jet loads and downstream margins.

This is a same-author verification, not independent scientific review.
Rebuild K from primitive positive loads rather than the diagnostic's deltas.
Keep the full tracefree U norm in final reconstruction and Sp derivative cost.
No claim beyond conditional fixed-time proper-distance shortening.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,signal,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
boot=BASE/'20261026_SPLIT_METRIC_RESPONSE/check.py'
assert hashlib.sha256(boot.read_bytes()).hexdigest()=='5fbb650408ef2a94986213f73493e2a4798cda683fcfbf12cc3ac235b5b58a60'
sp=importlib.util.spec_from_file_location('downstream_io',boot);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
io,lease=mod.io,mod.lease;io.ROOT=ROOT;lease.ROOT=ROOT
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    prior=BASE/'20261026_CANCELLATION_JET_DIAGNOSTIC'
    inputs={str(prior/'RESULT.json'):'875e89a033d2f2d1eceb4077e29cde87dcc3c2a9b9ebef703ad214266fa8d4c8',
            str(prior/'BINDING.json'):'7d0db30268901bad971d65248bc26d6dea7117a9f8742f561cf42f07cbe9c539',
            str(prior/'check.py'):'39691f07580446fdb3475b59837c9bd4f4a60cd09cc91579f48398540401f7fb'}
    for p,h in inputs.items():assert io.sha(p)==h
    pb=io.read(prior/'BINDING.json');assert pb['source_sha256']==inputs[str(prior/'check.py')]
    for p,h in pb['inputs'].items():
        assert p not in inputs or inputs[p]==h
        inputs[p]=h
    for p,h in inputs.items():assert io.sha(p)==h
    terminal=io.read(prior/'TERMINAL.json')
    assert terminal['pass'] and terminal['result_sha256']==io.sha(prior/'RESULT.json') and terminal['binding_sha256']==io.sha(prior/'BINDING.json')
    inputs[str(prior/'TERMINAL.json')]=io.sha(prior/'TERMINAL.json')
    assert io.sha('/usr/lib/python3.12/_pylong.py')=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    runtime=lease.observed();source=io.sha(__file__)
    io.put('BINDING.json',{'inputs':inputs,'source_sha256':source,'runtime':runtime})
    def parent(n):return io.read(BASE/('20261026_'+n+'/RESULT.json'))
    diag=io.read(prior/'RESULT.json');old=parent('COEFFICIENT_ENVELOPE_CLOSURE');split=parent('SPLIT_METRIC_RESPONSE')
    rad,mix,trace,cb,normal,wall,real,tail=[parent(n) for n in ('SCALAR_RADIAL_SOURCE_BUDGET','MIXED_SOURCE_BUDGET','TRACEFREE_SOURCE_BUDGET','COMPLEX_BACKGROUND_COLLAR','SCALAR_NORMAL_WALL_BUDGET','ISRAEL_OSCILLATOR_WALL_BUDGET','RESPONSE_AUDIT','DISTANCE_TAIL')]
    rho=Q(1,40000);A=Q(160001);eps=Q(1,1000);variants={}
    flows={n:io.read(io.FLOW/('FLOW_'+n+'.json')) for n in ('primary','independent')}
    for variant,prediction in diag['variants'].items():
        kg=[];kc=[];arms={}
        for name in flows:
            def exact(obj):return {k:Q(v) for k,v in obj['arms'][name]['exact'].items()}
            r,m,c,j,w=map(exact,(rad,mix,cb,normal,wall))
            H,T,P,mass=r['Hbar'],r['Tbar'],r['Pbar'],r['mass_bound']
            V0=Q(trace['raw_source_constant'])/(36*Q(trace['arms'][name]['k_min']))
            full=Q(trace['arms'][name]['tracefree_constant'])
            raw=Q(3,25)*(Q(20,3)+(H+T/3)*(2/rho+2))/Q(6,100)
            assert m['metric_source_constant']==H*full+raw
            v=full if variant=='cancellation_only' else V0
            jet=full if variant=='cancellation_only' else 9*V0/rho
            sc=T*T*v+12*H*raw+r['radial_constant']
            spc=H*v+raw;sg=T*jet+2*mass*P*v+6*T*spc+r['KG_constant']
            force=sg+(12*H*T+4*mass*P)*sc/c['D_over_n2']
            channels={}
            for channel in ('geometric','current'):
                geom=channel=='geometric';xi=w['graph_'+channel];osc=w['oscillator_weighted'] if geom else Q(0)
                load=(force+4*T*c['inverse_A_absolute']*sc/c['D_over_n2']+2*T*c['inverse_A_absolute']*v) if geom else Q(0)
                load+=c['inverse_A_absolute']*((mass*P+4*H*T+21*T/2)*xi+j['weighted_'+channel+'_constant']+osc/(2*c['oscillator_over_n2']))
                uf=Q(old['arms'][name]['scalar_response'])*load
                up=Q(split['arms'][name]['remainder_ceiling'])*(uf+(sc if geom else 0))+Q(old['arms'][name]['metric_response'])*(spc if geom else 0)
                K=uf+3*up+(full if geom else 0)+xi+(2*uf+T*xi+osc)/c['oscillator_over_n2']
                if geom:
                    expected=prediction['arms'][name]['exact']
                    assert all(Q(expected[k])==val for k,val in dict(Sc=sc,Sp=spc,F=force,Uf=uf,Up=up,K=K).items())
                    kg.append(K)
                else:
                    assert K==Q(split['arms'][name]['channels'][channel]['new_K']);kc.append(K)
                channels[channel]=str(K)
            arms[name]=channels
        KG,KC=max(kg),max(kc);s=min(1/(16*KG),1/(88*A),Q(1,1000000));rw=s/(16*KC)
        gap=1-A*s;num=KG*s*s+KC*rw
        derivative=(2*KG*s*gap+11*A*num)/gap**12
        assert gap>0 and num/gap**11<s and derivative<Q(1,2)
        assert all(Q(prediction['exact'][k])==v for k,v in dict(KG=KG,KC=KC,s=s,r_w=rw).items())
        R=rw/32;domains={}
        for name,flow in flows.items():
            lo,hi=map(Q,flow['D']);assert hi>=lo>1
            T=Q(real['arms'][name]['extrema']['T0'])+eps
            shift=s*(1+rho/(2*lo));speed=2*Q(8001,1000)*Q(3,25)*s;coupling=s*(T+1)/1000
            gates={'shift':rho/4-shift,'composition':Q(1,2)-2*shift/rho,'jacobian':1-s/lo,'separation':lo-s,
                   'speed':Q(1,4)-speed,'boost':1-speed**2,'coupling':1-coupling,'coupling_margin':Q(1,2)-coupling,'exponential':2-1/(1-2*s)}
            assert 0<2*s<1 and all(v>0 for v in gates.values())
            domains[name]={k:str(v) for k,v in gates.items()}
        dmin=min(Q(f['D'][0]) for f in flows.values());dmax=max(Q(f['D'][1]) for f in flows.values())
        BD=dmax*s*(1+1/dmin)/(1-s)
        coeff={k:tuple(map(Q,v['exact_bounds'])) for k,v in tail['coefficients'].items()}
        assert tail['direction']==[1,0] and all(lo<=hi<0 for lo,hi in coeff.values())
        strength=-coeff['d1'][1];history=[]
        for i in range(513):
            x=Q(1,2**(i+1));ratio=BD*x**3/(R*(1-x));ok=ratio<=strength/2
            history.append({'halvings':i,'x':str(x),'tail_per_z':str(ratio),'pass':ok})
            if ok:break
        else:raise RuntimeError('PREDECLARED_DYADIC_SEARCH_EXHAUSTED_NO_INTERVAL')
        z=R*x;remainder=BD*x**4/(1-x)
        assert sum(coeff['d'+str(i)][1]*z**i for i in (1,2,3))+remainder<=-strength*z/2<0
        vals=dict(KG=KG,KC=KC,s=s,r_w=rw,reconstruction_radius=R,z_upper=z,distance_bound=BD,tail_per_z=remainder/z,
                  uniform_shortening_per_z=strength/2,shortening_gain_over_split=z/Q(split['exact']['z_upper']))
        variants[variant]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},'domains':domains,'arms':arms,'radius_construction':history}
    assert lease.observed()==runtime and io.sha(__file__)==source and all(io.sha(p)==h for p,h in inputs.items())
    result={'pass':True,'classification':'JET_DOWNSTREAM_SAME_AUTHOR_ARITHMETIC_VERIFIED','variants':variants,
            'independent_review_complete':False,'scope':'Candidate conditional fixed-time shortening interval. Separate direct-load arithmetic agrees with prior delta arithmetic. All-order jet refinement awaits independent analytic review. No time contraction, stability or formation claim.'}
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({k:v['display'] for k,v in variants.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DOWNSTREAM_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
