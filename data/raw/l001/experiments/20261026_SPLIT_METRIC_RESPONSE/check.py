"""Sharper same-norm metric inverse and complete downstream recertification.

Before the final common-source broadening, the accepted momentum proof gives
U(p) <= Brem*(Sc+Uf+Sp) + L*Sp, L=12/rho,
Brem=B0+B1+2Hp*B0+2H*B1+(Tp+T)/3.
Sp here already includes n||Sp||_(2n+1). Only its derivative pays L.
For integer L, ceil(Brem+L)-L bounds Brem. Check this unrounded inequality
explicitly. No derivative is removed and the weighted norm is unchanged.
Recompute both envelope channels, contraction, all reconstruction margins,
and the fixed dyadic Cauchy-tail condition using authenticated old coefficients.
All conclusions inherit the original compatible analytic and ODE premises.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
from math import ceil
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
def load(name,p):
    sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
helper=BASE/'20261026_BACKGROUND_CUTOFF/extract.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('split_io',helper);io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('split_lease',io.LEASE);lease.ROOT=ROOT
PINS={
'20261026_COEFFICIENT_ENVELOPE_CLOSURE/RESULT.json':'3aa11d9a779bba1f1a3efde5c632d43ef5e623178f033dd0f15e0a04b1c37906',
'20261026_COEFFICIENT_ENVELOPE_CLOSURE/BINDING.json':'eeb4b48a25781e9e8e39b613619f4b481dcd8fc79bfa45346e1bb28cb014c21e',
'20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1/AUDIT_RESULT.json':'fa805f5eff415c6ec019ec9f111a3f4c52e70f8d70c3481b9e012e8b781319db',
'20261026_RECONSTRUCTION_DOMAIN/RESULT.json':'33b94170c6d6eb66bb1da7c64149c2fcc34efe379419f4fda6067710b0f148c4',
'20261026_RECONSTRUCTION_DOMAIN/AUDIT_RESULT.json':'fd5cc36371250132b07e2291242ce465cf7d7a1c711fb3273b70b99d547ab8d4',
'20261026_DISTANCE_TAIL/RESULT.json':'447b19af1290cffd82fdff0e3c7f3b78bffe24d1be088dc65dd6aeb3ac6ac608',
'20261026_DISTANCE_TAIL/BINDING.json':'c9f5c0a763cff1ab1b093db78f76b08e03053a4d05e57d4d3e2ec8586f2edc2a',
'20261026_DISTANCE_TAIL/AUDIT_RESULT.json':'2c419e8bec3ee81f7588c6e1d4c9d0e12f3acea21f25754b27730c43e0e21c5e'}
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120);io.put('START.json',{'cpu':cpu,'occupied':occupied})
    inputs={str(BASE/p):h for p,h in PINS.items()}
    for p,h in inputs.items():assert io.sha(p)==h
    for rel in ('20261026_COEFFICIENT_ENVELOPE_CLOSURE/BINDING.json','20261026_DISTANCE_TAIL/BINDING.json'):
        for p,h in io.read(BASE/rel)['inputs'].items():
            assert io.sha(p)==h and (p not in inputs or inputs[p]==h);inputs[p]=h
    old=io.read(BASE/'20261026_COEFFICIENT_ENVELOPE_CLOSURE/RESULT.json')
    tail=io.read(BASE/'20261026_DISTANCE_TAIL/RESULT.json')
    rec=io.read(BASE/'20261026_RECONSTRUCTION_DOMAIN/RESULT.json')
    assert old['pass'] and tail['pass'] and rec['pass']
    for rel,key,obj in [('20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1/AUDIT_RESULT.json','exact',old),
                        ('20261026_DISTANCE_TAIL/AUDIT_RESULT.json','exact',tail)]:
        audit=io.read(BASE/rel);assert audit['pass'] and audit[key]==obj[key]
    assert io.read(BASE/'20261026_RECONSTRUCTION_DOMAIN/AUDIT_RESULT.json')['pass']
    assert len(str(10**20000))==20001
    runtime=lease.observed();source=io.sha(__file__)
    binding={'source_sha256':source,'inputs':inputs,'runtime':runtime}
    io.put('BINDING.json',binding)
    def parent(name):return io.read(BASE/('20261026_'+name+'/RESULT.json'))
    real=parent('RESPONSE_AUDIT');radial=parent('SCALAR_RADIAL_SOURCE_BUDGET');mixed=parent('MIXED_SOURCE_BUDGET')
    rho=Q(old['working_collar']);A=Q(old['denominator_scale']);L=12/rho;eps=Q(1,1000)
    assert rho==Q(1,40000) and A==160001 and L.denominator==1
    arms={};KG=Q(0);KC=Q(0);flows={}
    for name in ('primary','independent'):
        flow=io.read(io.FLOW/('FLOW_'+name+'.json'));flows[name]=flow
        kl,ku=io.iv(flow['parameters']['k'])
        e={k:Q(v) for k,v in real['arms'][name]['extrema'].items()}
        H,T,P,E,m=e['H0']+eps,e['T0']+eps,e['P0']+eps,8+eps,e['m0']
        anchor=max(Q(1),e['T0']+m*e['P0']+4*e['H0']*e['T0'])/(42*kl*e['e0']**2)
        Hp=T*T/3+ku*E*E;Tp=m*P+4*H*T
        assert rho*H<1
        B0=(anchor+rho*(T/6+Q(1,2)))/(1-rho*H);B1=2*H*B0+T/3+1
        remainder=B0+B1+2*Hp*B0+2*H*B1+(Tp+T)/3
        C=Q(old['arms'][name]['metric_response']);Crem=C-L
        assert C==ceil(remainder+L) and 0<remainder<=Crem
        channels={}
        for channel in ('geometric','current'):
            saved={k:Q(v) for k,v in old['arms'][name]['channels'][channel].items()}
            Sc=Q(radial['arms'][name]['exact']['Sc_constant']) if channel=='geometric' else Q(0)
            Sp=Q(mixed['arms'][name]['exact']['metric_source_constant']) if channel=='geometric' else Q(0)
            assert C*(Sc+saved['Uf']+Sp)==saved['Up']
            Up=Crem*(Sc+saved['Uf']+Sp)+L*Sp
            K=saved['K']+3*(Up-saved['Up'])
            assert 0<Up<=saved['Up'] and 0<K<=saved['K']
            channels[channel]={'new_Up':str(Up),'new_K':str(K),'old_K':str(saved['K']),
                                'K_reduction_factor':str(saved['K']/K)}
            if channel=='geometric':KG=max(KG,K)
            else:KC=max(KC,K)
        arms[name]={'unrounded_remainder':str(remainder),'remainder_ceiling':str(Crem),'mixed_derivative_cost':str(L),'channels':channels}
    assert KG>0 and KC>0
    s=min(1/(16*KG),1/(88*A),Q(1,1000000));r=s/(16*KC);gap=1-A*s
    N=KG*s*s+KC*r;image=N/gap**11;derivative=2*KG*s/gap**11+11*A*N/gap**12
    assert gap>0 and image<s and derivative<Q(1,2)
    R=r/32;assert 0<16*R<r and 0<s<1
    g=Q(3,25);E=Q(8001,1000);domains={}
    for name in arms:
        lo,hi=map(Q,flows[name]['D']);assert 1<lo<=hi
        _,ku=io.iv(flows[name]['parameters']['k']);assert ku<Q(1,2500)
        T=Q(real['arms'][name]['extrema']['T0'])+eps
        cx=1+rho/(2*lo);shift=cx*s;j=s/lo;q=2*shift/rho;speed=2*E*g*s;coupling=(T+1)*s/1000
        gates={'shift_margin':rho/4-shift,'composition_margin':Q(1,2)-q,'jacobian_lower':1-j,
               'separation_lower':lo-s,'speed_margin':Q(1,4)-speed,'boost_squared_margin':1-speed*speed,
               'coupling_lower':1-coupling,'coupling_margin':Q(1,2)-coupling,'exponential_margin':2-1/(1-2*s)}
        assert 2*s<1 and all(v>0 for v in gates.values())
        domains[name]={k:str(v) for k,v in gates.items()}
    Dmin=min(Q(f['D'][0]) for f in flows.values());Dmax=max(Q(f['D'][1]) for f in flows.values())
    BD=Dmax*(s/Dmin+s)/(1-s)
    coeffs={k:tuple(map(Q,v['exact_bounds'])) for k,v in tail['coefficients'].items()}
    assert tail['direction']==[1,0] and all(lo<=hi<0 for lo,hi in coeffs.values())
    strength=-coeffs['d1'][1];history=[];x=Q(1,2)
    for step in range(513):
        ratio=BD*x**3/(R*(1-x));ok=ratio<=strength/2
        history.append({'halvings':step,'x':str(x),'tail_per_z':str(ratio),'pass':ok})
        if ok:break
        x/=2
    else:
        result={'pass':True,'classification':'SPLIT_METRIC_SUFFICIENT_INTERVAL_UNRESOLVED','radius_construction':history}
        assert lease.observed()==runtime and all(io.sha(p)==h for p,h in inputs.items()) and io.sha(__file__)==source
        io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json')});return
    z0=R*x;bound=BD*x**4/(1-x)
    poly=sum(coeffs['d'+str(i)][1]*z0**i for i in (1,2,3))
    assert bound/z0<=strength/2 and poly+bound<=-strength*z0/2<0
    values=dict(KG=KG,KC=KC,s=s,r_w=r,reconstruction_radius=R,z_upper=z0,distance_bound=BD,
        contraction_derivative=derivative,map_ratio=image/s,tail_per_z=bound/z0,
        uniform_shortening_per_z=strength/2,coefficient_radius_gain=r/Q(old['exact']['r_w']),
        shortening_radius_gain=z0/Q(tail['exact']['z_upper']))
    result={'pass':True,'classification':'SPLIT_METRIC_SHORTENING_DIAGNOSTIC','arms':arms,'domains':domains,
        'exact':{k:str(v) for k,v in values.items()},'display':{k:float(v) for k,v in values.items()},
        'coefficients':tail['coefficients'],'radius_construction':history,
        'scope':'Same action, norm, direction and inherited compatible proofs. Only metric-source broadening is sharpened. Conditional fixed-time distance shortening, not time contraction or global stability.'}
    assert lease.observed()==runtime and all(io.sha(p)==h for p,h in inputs.items()) and io.sha(__file__)==source
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps(result['display']),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('SPLIT_120_SECONDS')))
        run()
    except BaseException as error:
        io.put('FAILURE.json',{'error':repr(error),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
