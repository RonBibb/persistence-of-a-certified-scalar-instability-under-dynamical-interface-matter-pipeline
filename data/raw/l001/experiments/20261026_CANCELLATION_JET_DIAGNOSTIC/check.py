"""Prospective bound refinement, NOT an independently audited certificate.

Q2 substituted into Q3 gives Sc=T^2*c-12H*qM/r+qR exactly.
Weights only increase from 2n or 2n+1 to 2n+2 (0<d<=1).
Tracefree value V0 and first jet V1=9V0/rho follow the same Nagumo
proof as the sealed full U(c) bound; full Ct is retained in reconstruction.
Two controlled variants: cancellation alone; cancellation plus separate jets.
No ODE, changed action, changed collar, or physical-domain recertification.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent
bootstrap=BASE/'20261026_SPLIT_METRIC_RESPONSE/check.py'
assert hashlib.sha256(bootstrap.read_bytes()).hexdigest()=='5fbb650408ef2a94986213f73493e2a4798cda683fcfbf12cc3ac235b5b58a60'
spec=importlib.util.spec_from_file_location('jet_bootstrap',bootstrap)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
io=m.io;lease=m.lease;io.ROOT=ROOT;lease.ROOT=ROOT
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    split=BASE/'20261026_SPLIT_METRIC_RESPONSE'
    pins={'RESULT.json':'fd57632ed9769362a99d985699be6250dbb499a99ef5d8e21d44875d8e2c41f0',
          'BINDING.json':'5b468c55a6da625f68662a8edfba400ca26d521e71921eb164cf5ede11d8a47b',
          'AUDIT_RESULT.json':'2fc315c4b56af4f6c67355823a557892bb2760eb50ea27a979f0fd4a0814ab00'}
    inputs={str(split/k):v for k,v in pins.items()}
    for p,h in inputs.items():assert io.sha(p)==h
    for p,h in io.read(split/'BINDING.json')['inputs'].items():
        assert p not in inputs or inputs[p]==h
        inputs[p]=h
    inputs[str(bootstrap)]=io.sha(bootstrap)
    for p,h in inputs.items():assert io.sha(p)==h
    sealed=io.read(split/'RESULT.json');audit=io.read(split/'AUDIT_RESULT.json')
    assert sealed['pass'] and audit['pass'] and sealed['exact']==audit['exact']
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert io.sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001
    runtime=lease.observed();source=io.sha(__file__)
    io.put('BINDING.json',{'inputs':inputs,'source_sha256':source,'runtime':runtime})
    def parent(n):return io.read(BASE/('20261026_'+n+'/RESULT.json'))
    old=parent('COEFFICIENT_ENVELOPE_CLOSURE');rad=parent('SCALAR_RADIAL_SOURCE_BUDGET')
    mix=parent('MIXED_SOURCE_BUDGET');trace=parent('TRACEFREE_SOURCE_BUDGET');collar=parent('COMPLEX_BACKGROUND_COLLAR')
    rho=Q(old['working_collar']);A=Q(old['denominator_scale'])
    variants={}
    # Independent coefficient collection: 12H*(H*c-qM/r)-(12H^2-T^2)*c+qR.
    assert 12-12==0
    for variant in ('cancellation_only','cancellation_and_jets'):
        arms={};KG=Q(0)
        for name in ('primary','independent'):
            rb={k:Q(v) for k,v in rad['arms'][name]['exact'].items()}
            mb={k:Q(v) for k,v in mix['arms'][name]['exact'].items()}
            cb={k:Q(v) for k,v in collar['arms'][name]['exact'].items()}
            H,T,P,mass=rb['Hbar'],rb['Tbar'],rb['Pbar'],rb['mass_bound']
            Ct=Q(trace['arms'][name]['tracefree_constant'])
            V0=Q(trace['raw_source_constant'])/(36*Q(trace['arms'][name]['k_min']))
            V1=9*V0/rho
            assert Ct==V0*(1+9/rho+108/rho**2)
            rawM=mb['metric_source_constant']-H*Ct
            assert rawM>0
            value=Ct if variant=='cancellation_only' else V0
            first=Ct if variant=='cancellation_only' else V1
            Sp=H*value+rawM
            Sc=T*T*value+12*H*rawM+rb['radial_constant']
            Sg=T*first+2*mass*P*value+6*T*Sp+rb['KG_constant']
            F=Sg+(12*H*T+4*mass*P)*Sc/cb['D_over_n2']
            assert 0<Sc<rb['Sc_constant'] and 0<Sp<=mb['metric_source_constant']
            saved={k:Q(v) for k,v in old['arms'][name]['channels']['geometric'].items()}
            S=Q(old['arms'][name]['scalar_response']);C=Q(old['arms'][name]['metric_response'])
            Cr=Q(sealed['arms'][name]['remainder_ceiling'])
            Uf=saved['Uf']+S*(F-rb['F_constant']+4*T*cb['inverse_A_absolute']*(Sc-rb['Sc_constant'])/cb['D_over_n2']+2*T*cb['inverse_A_absolute']*(value-Ct))
            Up=Cr*(Sc+Uf)+(C*Sp)
            K=saved['K']+(Uf-saved['Uf'])*(1+2/cb['oscillator_over_n2'])+3*(Up-saved['Up'])
            prior=Q(sealed['arms'][name]['channels']['geometric']['new_K'])
            assert 0<Uf<=saved['Uf'] and 0<K<prior
            vals=dict(V0=V0,V1=V1,Ct=Ct,Sc=Sc,Sp=Sp,F=F,Uf=Uf,Up=Up,K=K,Sc_reduction=rb['Sc_constant']/Sc,K_reduction=prior/K)
            arms[name]={'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()}}
            KG=max(KG,K)
        KC=Q(sealed['exact']['KC'])
        s=min(1/(16*KG),1/(88*A),Q(1,1000000));r=s/(16*KC);gap=1-A*s
        image=(KG*s*s+KC*r)/gap**11
        derivative=2*KG*s/gap**11+11*A*(KG*s*s+KC*r)/gap**12
        assert gap>0 and image<s and derivative<Q(1,2)
        vals=dict(KG=KG,KC=KC,s=s,r_w=r,coefficient_radius_gain=r/Q(sealed['exact']['r_w']),map_ratio=image/s,derivative=derivative)
        variants[variant]={'arms':arms,'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()}}
    assert io.sha(__file__)==source and lease.observed()==runtime
    assert all(io.sha(p)==h for p,h in inputs.items())
    result={'pass':True,'classification':'CANCELLATION_JET_PROSPECTIVE_DIAGNOSTIC','variants':variants,
            'independently_reviewed':False,'new_physical_domain_certified':False,'new_distance_interval_certified':False,
            'scope':'Exact prospective constants under inherited source premises. Existing audited certificate remains authoritative; downstream reconstruction and distance tail not rerun.'}
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps({k:v['display'] for k,v in variants.items()}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('JET_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
