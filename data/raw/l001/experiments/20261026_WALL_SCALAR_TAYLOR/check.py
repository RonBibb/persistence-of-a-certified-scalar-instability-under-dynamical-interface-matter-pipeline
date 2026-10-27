"""Equation-based scalar composition tail; prospective conditional refinement.

On prior collar |Phi''|=|m Phi-4HT|<=B2=mbar Pbar+4Hbar Tbar.
A rho-disk about a working-collar point remains in the prior collar.
Cauchy applied to Phi'' gives |Phi^(j)|/j!<=B2/[j(j-1)rho^(j-2)]
for j>=2. With |X| majorized by 2y, the scalar Taylor remainder
is <=2B2*y^2/(1-a*y), a=2/rho, coefficientwise in primitive degree.
This is promoted to the unchanged wall denominator and primitive-count
factors 24 (oscillator) and 14 (normal). No y-derivative of Y is assumed.
Compare oscillator-only and shared-Phi-tail refinements. All other terms
including the normal T-composition tail and current load remain unchanged.
Same-author arithmetic only; independent analytic review still required.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,signal,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
boot=BASE/'20261026_JET_DOWNSTREAM/check.py'
assert hashlib.sha256(boot.read_bytes()).hexdigest()=='77baf9fcfac71c419f16c75e7f9ab6869c539fe677db01c8a622f0a2b7137009'
sp=importlib.util.spec_from_file_location('scalar_tail_io',boot);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
io,lease=mod.io,mod.lease;io.ROOT=ROOT;lease.ROOT=ROOT
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120);io.put('START.json',{'cpu':cpu,'occupied':occupied})
    p=BASE/'20261026_JET_DOWNSTREAM'
    inputs={str(boot):io.sha(boot),str(p/'RESULT.json'):'7351b7fe985384b71e2a01763a671fdc217cab44ebd89f7fcda6c86b21e02951',
            str(p/'BINDING.json'):'3a26474338e194ccedcf6353ab91346b3197c80ebf485bc7e460f9ac1ebb2a73'}
    for path,h in inputs.items():assert io.sha(path)==h
    for path,h in io.read(p/'BINDING.json')['inputs'].items():
        assert path not in inputs or inputs[path]==h
        inputs[path]=h
    for path,h in inputs.items():assert io.sha(path)==h
    term=io.read(p/'TERMINAL.json');assert term['pass'] and term['result_sha256']==io.sha(p/'RESULT.json') and term['binding_sha256']==io.sha(p/'BINDING.json')
    assert io.sha('/usr/lib/python3.12/_pylong.py')=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    runtime=lease.observed();source=io.sha(__file__)
    io.put('BINDING.json',{'inputs':inputs,'source_sha256':source,'runtime':runtime})
    def parent(n):return io.read(BASE/('20261026_'+n+'/RESULT.json'))
    prior=io.read(p/'RESULT.json')['variants']['cancellation_and_jets']
    diag=parent('CANCELLATION_JET_DIAGNOSTIC')['variants']['cancellation_and_jets']
    old=parent('COEFFICIENT_ENVELOPE_CLOSURE');split=parent('SPLIT_METRIC_RESPONSE')
    rad,cb,wall,normal,real,tail=map(parent,('SCALAR_RADIAL_SOURCE_BUDGET','COMPLEX_BACKGROUND_COLLAR','ISRAEL_OSCILLATOR_WALL_BUDGET','SCALAR_NORMAL_WALL_BUDGET','RESPONSE_AUDIT','DISTANCE_TAIL'))
    flows={n:io.read(io.FLOW/('FLOW_'+n+'.json')) for n in ('primary','independent')}
    rho=Q(1,40000);a=2/rho;A=2*a+1;variants={}
    for variant in ('oscillator_only','shared_scalar_tail'):
        arms={};kg=[]
        for name in flows:
            def exact(o):return {k:Q(v) for k,v in o['arms'][name]['exact'].items()}
            r,c,w,j=map(exact,(rad,cb,wall,normal));d={k:Q(v) for k,v in diag['arms'][name]['exact'].items()}
            H,T,P,mass=r['Hbar'],r['Tbar'],r['Pbar'],r['mass_bound']
            B2=mass*P+4*H*T;newtrace=2*B2;oldtrace=P*a*a
            assert 0<newtrace<oldtrace
            osc=w['oscillator_weighted']-24*(oldtrace-newtrace)
            J=j['weighted_geometric_constant']
            if variant=='shared_scalar_tail':J-=14*Q(21,2)*(oldtrace-newtrace)
            assert 0<osc<w['oscillator_weighted'] and 0<J<=j['weighted_geometric_constant']
            xi=w['graph_geometric'];S=Q(old['arms'][name]['scalar_response']);C=Q(old['arms'][name]['metric_response']);Cr=Q(split['arms'][name]['remainder_ceiling'])
            load=d['F']+c['inverse_A_absolute']*(4*T*d['Sc']/c['D_over_n2']+2*T*d['V0']+(B2+21*T/2)*xi+J+osc/(2*c['oscillator_over_n2']))
            uf=S*load;up=Cr*(uf+d['Sc'])+C*d['Sp']
            K=uf+3*up+d['Ct']+xi+(2*uf+T*xi+osc)/c['oscillator_over_n2']
            # Distinct delta assembly must agree exactly with the direct assembly.
            deltao=osc-w['oscillator_weighted'];deltaj=J-j['weighted_geometric_constant']
            deltau=S*c['inverse_A_absolute']*(deltaj+deltao/(2*c['oscillator_over_n2']))
            alternate=Q(prior['arms'][name]['geometric'])+(1+3*Cr+2/c['oscillator_over_n2'])*deltau+deltao/c['oscillator_over_n2']
            assert K==alternate and 0<K<Q(prior['arms'][name]['geometric'])
            vals=dict(B2=B2,old_trace=oldtrace,new_trace=newtrace,oscillator=osc,normal=J,K=K,trace_gain=oldtrace/newtrace)
            arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()}}
            kg.append(K)
        KG=max(kg);KC=Q(prior['exact']['KC']);s=min(1/(16*KG),1/(88*A),Q(1,1000000));rw=s/(16*KC);R=rw/32
        gap=1-A*s;num=KG*s*s+KC*rw;derivative=(2*KG*s*gap+11*A*num)/gap**12
        assert gap>0 and num/gap**11<s and derivative<Q(1,2)
        domains={}
        for name,flow in flows.items():
            lo,hi=map(Q,flow['D']);assert hi>=lo>1
            T=Q(real['arms'][name]['extrema']['T0'])+Q(1,1000)
            shift=s*(1+rho/(2*lo));speed=2*Q(8001,1000)*Q(3,25)*s;coupling=s*(T+1)/1000
            gates={'shift':rho/4-shift,'composition':Q(1,2)-2*shift/rho,'jacobian':1-s/lo,'separation':lo-s,
                   'speed':Q(1,4)-speed,'boost':1-speed**2,'coupling':1-coupling,'coupling_margin':Q(1,2)-coupling,'exponential':2-1/(1-2*s)}
            assert 0<2*s<1 and all(v>0 for v in gates.values())
            domains[name]={k:str(v) for k,v in gates.items()}
        dmin=min(Q(f['D'][0]) for f in flows.values());dmax=max(Q(f['D'][1]) for f in flows.values());BD=dmax*s*(1+1/dmin)/(1-s)
        coeff={k:tuple(map(Q,v['exact_bounds'])) for k,v in tail['coefficients'].items()}
        assert tail['direction']==[1,0] and all(lo<=hi<0 for lo,hi in coeff.values())
        strength=-coeff['d1'][1];history=[]
        for i in range(513):
            x=Q(1,2**(i+1));ratio=BD*x**3/(R*(1-x));ok=ratio<=strength/2
            history.append({'halvings':i,'x':str(x),'tail_per_z':str(ratio),'pass':ok})
            if ok:break
        else:raise RuntimeError('DYADIC_SEARCH_EXHAUSTED')
        z=R*x;remainder=BD*x**4/(1-x)
        assert sum(coeff['d'+str(i)][1]*z**i for i in (1,2,3))+remainder<=-strength*z/2<0
        vals=dict(KG=KG,KC=KC,s=s,r_w=rw,z_upper=z,reconstruction_radius=R,tail_per_z=remainder/z,uniform_shortening_per_z=strength/2,
                  shortening_gain_over_jet=z/Q(prior['exact']['z_upper']))
        variants[variant]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},'arms':arms,'domains':domains,'radius_construction':history}
    assert io.sha(__file__)==source and lease.observed()==runtime and all(io.sha(path)==h for path,h in inputs.items())
    out={'pass':True,'classification':'WALL_SCALAR_TAYLOR_PROSPECTIVE_SHORTENING','variants':variants,'independent_review_complete':False,
         'scope':'Candidate equation-based Phi composition bound. Direct and delta arithmetic agree. All-order proof and independent review required before promotion. Fixed-time conditional shortening only.'}
    io.put('RESULT.json',out);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({k:v['display'] for k,v in variants.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('WALL_TAIL_120_SECONDS')))
        run()
    except BaseException as e:
        io.put('FAILURE.json',{'error':repr(e),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
