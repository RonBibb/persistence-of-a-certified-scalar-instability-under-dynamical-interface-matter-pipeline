"""Exact reduced-load assembly and scalar coefficient majorant closure."""
import sys
sys.dont_write_bytecode = True
sys.set_int_max_str_digits(100000)
import importlib.util, hashlib, json, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
from math import ceil
ROOT = Path(__file__).resolve().parent
def load(name, path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
base=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
assert hashlib.sha256((base/'extract.py').read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('closure_io',base/'extract.py');io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('closure_lease',io.LEASE);lease.ROOT=ROOT
PINS={
'COMPLEX_BACKGROUND_COLLAR':('a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68','28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd'),
'RESPONSE_AUDIT':('6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',None),
'TRACEFREE_SOURCE_BUDGET':('a03da75ab2f852014ff636a16d73849b11408c29f199d0bbc5fa28ad5ec62b51','f48a1106af8f914ca84f16bf8f8b2674b4bfcd9da499ea9d770feb993bc98be9'),
'MIXED_SOURCE_BUDGET':('8921c6fd7706c5f421aef069be664c519467beece8b8cc0649dc9bc18487dd19','bdf44703e299a230dd9646afd1171b11f41aa56ae4e174bd71db4c2ad10b54c9'),
'SCALAR_RADIAL_SOURCE_BUDGET':('12563a244eb46bef3f73c2d16a66a8a74d2eaa4b89179aaa40ed2b16c3de2858','85fa72f8c36d20d1c9e37902ca836ca33017f87a57e0e02699eb80b15963fba5'),
'SCALAR_NORMAL_WALL_BUDGET':('09dde715e8ecec2a07b21eaa311635e664bc6fd6d8c90e99b49ae0a8bf42f5f0','1c42f5aedc5e9759f0621d26d796b7c01a541fa091f54989f24f61ae6d7b1c83'),
'ISRAEL_OSCILLATOR_WALL_BUDGET':('b4f6b13f490ab95da0bc3a436bd77b836cfd5f64fe518e7ca5aa1de72f4bf993','cf6d109bb7580107cfc0f784ec4f09d84b85a8ed3074eee7000d17d6831d7061'),
'COMPLEX_WEIGHTED_RESPONSE':('771651f65699357af6f999ab393dfa0db885343551e24890b29ee2aa68bd118d','7076650f416c7b7c0c3b203a33f987c1afd5d05297d6ccbd59e03f799aced8e9')}
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    inputs={};data={}
    for name,pair in PINS.items():
        folder=ROOT.parent/('20261026_'+name)
        for filename,digest in zip(('RESULT.json','AUDIT_RESULT.json'),pair):
            if digest is None:continue
            p=folder/filename;assert io.sha(p)==digest and io.read(p)['pass'];inputs[str(p)]=digest
        data[name]=io.read(folder/'RESULT.json')
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    for name in ('primary','independent'):
        p=io.FLOW/('FLOW_'+name+'.json');assert io.sha(p)==ft['artifacts'][p.name];inputs[str(p)]=io.sha(p)
    inputs[str(io.FLOW/'FROZEN.json')]=io.EXPECTED;inputs[str(io.LEASE)]=io.sha(io.LEASE)
    binding={'source_sha256':io.sha(__file__),'derivation_sha256':io.sha(ROOT/'DERIVATION.md'),'inputs':inputs,'runtime':lease.observed()}
    io.put('BINDING.json',binding)
    rho=Q(1,40000);A=Q(160001);eps=Q(1,1000)
    alpha=rho/2+rho*rho/4;assert 6*alpha<1
    S=Q(ceil(7*(7864*(2+rho/2)+alpha)/(1-6*alpha)+1))
    arms={};KG=Q(0);KC=Q(0)
    for name in ('primary','independent'):
        def exact(key):return {k:Q(v) for k,v in data[key]['arms'][name]['exact'].items()}
        ext={k:Q(v) for k,v in data['RESPONSE_AUDIT']['arms'][name]['extrema'].items()}
        co=exact('COMPLEX_BACKGROUND_COLLAR');rad=exact('SCALAR_RADIAL_SOURCE_BUDGET')
        wall=exact('ISRAEL_OSCILLATOR_WALL_BUDGET');normal=exact('SCALAR_NORMAL_WALL_BUDGET')
        mix=exact('MIXED_SOURCE_BUDGET')
        flow=io.read(io.FLOW/('FLOW_'+name+'.json'));kl,ku=io.iv(flow['parameters']['k'])
        H=ext['H0']+eps;T=ext['T0']+eps;P=ext['P0']+eps;m=ext['m0'];E=8+eps
        dD=co['D_over_n2'];dO=co['oscillator_over_n2'];Ai=co['inverse_A_absolute']
        assert min(dD,dO,Ai,kl,ext['e0'])>0 and rho*H<1
        Tp=m*P+4*H*T;Hp=T*T/3+ku*E*E
        U0=m*ext['P0']+4*ext['H0']*ext['T0'];d0=42*kl*ext['e0']**2
        A0=max(Q(1),ext['T0']+U0)/d0
        B0=(A0+rho*(T/6+Q(1,2)))/(1-rho*H)
        B1=2*H*B0+T/3+1
        B2=2*Hp*B0+2*H*B1+(Tp+T)/3+12/rho
        C=Q(ceil(B0+B1+B2));channels={}
        for channel in ('geometric','current'):
            geom=channel=='geometric'
            Ct=Q(data['TRACEFREE_SOURCE_BUDGET']['arms'][name]['tracefree_constant']) if geom else Q(0)
            Sp=mix['metric_source_constant'] if geom else Q(0)
            Sc=rad['Sc_constant'] if geom else Q(0);F=rad['F_constant'] if geom else Q(0)
            Xi=wall['graph_'+channel];J=normal['weighted_'+channel+'_constant']
            O=wall['oscillator_weighted'] if geom else Q(0)
            Rload=4*T*Ct+2*(Tp+21*T/2)*Xi+2*J+O/dO
            gload=Ai*Rload/2+4*T*Ai*Sc/dD
            Uf=S*(F+gload);Up=C*(Sc+Uf+Sp);Ub=Ct+2*Up
            Qosc=(2*Uf+T*Xi+O)/dO;K=Uf+3*Up+Ct+Xi+Qosc
            channels[channel]={k:str(v) for k,v in dict(Rload=Rload,gload=gload,Uf=Uf,Up=Up,Ub=Ub,Qosc=Qosc,K=K).items()}
            if geom:KG=max(KG,K)
            else:KC=max(KC,K)
        arms[name]={'scalar_response':str(S),'metric_response':str(C),'channels':channels}
    assert KG>0 and KC>0
    s=min(1/(16*KG),1/(88*A),Q(1,1000000));r=s/(16*KC)
    N=KG*s*s+KC*r;den=1-A*s
    image=N/den**11;derivative=2*KG*s/den**11+11*A*N/den**12
    assert s>0 and r>0 and den>0 and image<s and derivative<Q(1,2)
    vals=dict(KG=KG,KC=KC,s=s,r_w=r,map_ratio=image/s,derivative_bound=derivative)
    result={'pass':True,'classification':'COEFFICIENT_ENVELOPE_CLOSURE_DIAGNOSTIC','working_collar':str(rho),'denominator_scale':str(A),'denominator_power':11,'arms':arms,'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},'coefficient_envelope_closed':True,'physical_solution_domain_certified':False,'distance_tail_certified':False,'scope':'Conditional on inherited analytic source estimates and compatible inverse proofs; radius in w=z*C_N only.'}
    assert all(io.sha(p)==v for p,v in inputs.items())
    assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
    io.put('RESULT.json',result);io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print(json.dumps(result['display']),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CLOSURE_120_SECONDS')))
        run()
    except BaseException as exc:
        io.put('FAILURE.json',{'error':repr(exc),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
