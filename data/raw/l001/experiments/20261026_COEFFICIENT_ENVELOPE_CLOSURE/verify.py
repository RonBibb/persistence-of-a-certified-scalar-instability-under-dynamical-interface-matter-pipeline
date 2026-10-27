"""Independent exact response/channel assembly and envelope contraction audit."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, traceback
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW'
FROZEN='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
PARENTS={
'COMPLEX_BACKGROUND_COLLAR':('a507b618d48b266f5ab2222d1114472f4a06150641b696779581f40c7f0dce68','28fddf9658edf1249429d3d89be878885a5a3af6ee176f0c453fe262f20e63dd'),
'RESPONSE_AUDIT':('6b87db74542432103ffef0ac54b78a9dc7cbecb6b40da8a4226410366c2a2385',None),
'TRACEFREE_SOURCE_BUDGET':('a03da75ab2f852014ff636a16d73849b11408c29f199d0bbc5fa28ad5ec62b51','f48a1106af8f914ca84f16bf8f8b2674b4bfcd9da499ea9d770feb993bc98be9'),
'MIXED_SOURCE_BUDGET':('8921c6fd7706c5f421aef069be664c519467beece8b8cc0649dc9bc18487dd19','bdf44703e299a230dd9646afd1171b11f41aa56ae4e174bd71db4c2ad10b54c9'),
'SCALAR_RADIAL_SOURCE_BUDGET':('12563a244eb46bef3f73c2d16a66a8a74d2eaa4b89179aaa40ed2b16c3de2858','85fa72f8c36d20d1c9e37902ca836ca33017f87a57e0e02699eb80b15963fba5'),
'SCALAR_NORMAL_WALL_BUDGET':('09dde715e8ecec2a07b21eaa311635e664bc6fd6d8c90e99b49ae0a8bf42f5f0','1c42f5aedc5e9759f0621d26d796b7c01a541fa091f54989f24f61ae6d7b1c83'),
'ISRAEL_OSCILLATOR_WALL_BUDGET':('b4f6b13f490ab95da0bc3a436bd77b836cfd5f64fe518e7ca5aa1de72f4bf993','cf6d109bb7580107cfc0f784ec4f09d84b85a8ed3074eee7000d17d6831d7061'),
'COMPLEX_WEIGHTED_RESPONSE':('771651f65699357af6f999ab393dfa0db885343551e24890b29ee2aa68bd118d','7076650f416c7b7c0c3b203a33f987c1afd5d05297d6ccbd59e03f799aced8e9')}
PINS={ROOT/'check.py':'a60ca5f732dacf7f08d71a479dc5bdf821cbc81c58fe0528c355241aad6c4f57',
      ROOT/'DERIVATION.md':'10c8965f562612edf750f0ab1c6e13970c755e95ec5ba4bdea31bb46e9923dc1',
      ROOT/'RESULT.json':'3aa11d9a779bba1f1a3efde5c632d43ef5e623178f033dd0f15e0a04b1c37906',
      ROOT/'BINDING.json':'eeb4b48a25781e9e8e39b613619f4b481dcd8fc79bfa45346e1bb28cb014c21e'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ceil(x):return -((-x.numerator)//x.denominator)
def put(name,value):
    dest=ROOT/name;temp=ROOT/(name+'.tmp')
    with temp.open('x') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(temp,0o444);os.link(temp,dest);temp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/s).exists() for s in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    paths={Path(__file__),ROOT/'check.py',ROOT/'DERIVATION.md',ROOT/'RESULT.json',ROOT/'TERMINAL.json',
        ROOT/'BINDING.json',FLOW/'FROZEN.json',FLOW/'production_TERMINAL.json',FLOW/'FLOW_primary.json',
        FLOW/'FLOW_independent.json',BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'}
    data={}
    for key,(rh,ah) in PARENTS.items():
        folder=BASE/('20261026_'+key)
        for result,terminal,digest in (('RESULT.json','TERMINAL.json',rh),('AUDIT_RESULT.json','AUDIT_TERMINAL.json',ah)):
            if digest is None:continue
            rp=folder/result;tp=folder/terminal
            assert sha(rp)==digest and read(rp)['pass']
            term=read(tp);assert term['pass'] and term['result_sha256']==digest
            paths.update({rp,tp})
            if 'binding_sha256' in term:
                bp=folder/'BINDING.json';assert sha(bp)==term['binding_sha256'];paths.add(bp)
        data[key]=read(folder/'RESULT.json')
    hashes={str(p):sha(p) for p in paths}
    for p,digest in PINS.items():assert sha(p)==digest
    assert sha(FLOW/'FROZEN.json')==FROZEN
    term=read(ROOT/'TERMINAL.json')
    assert term['pass'] and term['result_sha256']==sha(ROOT/'RESULT.json')
    assert term['binding_sha256']==sha(ROOT/'BINDING.json')
    binding=read(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py') and binding['derivation_sha256']==sha(ROOT/'DERIVATION.md')
    for p,digest in binding['inputs'].items():assert sha(p)==digest
    result=read(ROOT/'RESULT.json')
    assert result['pass'] and result['classification']=='COEFFICIENT_ENVELOPE_CLOSURE_DIAGNOSTIC'
    assert result['coefficient_envelope_closed'] and not result['physical_solution_domain_certified'] and not result['distance_tail_certified']
    rho=F(1,40000);A=F(160001);eps=F(1,1000)
    assert F(result['working_collar'])==rho and F(result['denominator_scale'])==A and result['denominator_power']==11
    real=data['RESPONSE_AUDIT'];assert real['scalar_constant']==3932 and real['unresolved']==[]
    assert F(data['COMPLEX_BACKGROUND_COLLAR']['rho'])==2*rho
    for key in ('TRACEFREE_SOURCE_BUDGET','MIXED_SOURCE_BUDGET','SCALAR_RADIAL_SOURCE_BUDGET','SCALAR_NORMAL_WALL_BUDGET','ISRAEL_OSCILLATOR_WALL_BUDGET'):
        assert F(data[key]['working_collar'])==rho
    alpha=rho*(F(1,2)+rho/4);absorption=1-6*alpha;assert absorption>0
    scalar=F(ceil(1+7*(F(2*3932)*(2+rho/2)+alpha)/absorption))
    ft=read(FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==FROZEN
    assert set(result['arms'])=={'primary','independent'}
    before=lease.observed();arms={};geometric=[];current=[]
    for name in ('primary','independent'):
        def ex(key):return {k:F(v) for k,v in data[key]['arms'][name]['exact'].items()}
        ext={k:F(v) for k,v in real['arms'][name]['extrema'].items()}
        co=ex('COMPLEX_BACKGROUND_COLLAR');rad=ex('SCALAR_RADIAL_SOURCE_BUDGET')
        wall=ex('ISRAEL_OSCILLATOR_WALL_BUDGET');normal=ex('SCALAR_NORMAL_WALL_BUDGET');mix=ex('MIXED_SOURCE_BUDGET')
        assert co['drift_absolute']<=5 and co['potential_over_n2_absolute']<=6
        path=FLOW/('FLOW_'+name+'.json');assert sha(path)==ft['artifacts'][path.name]
        flow=read(path);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        H,T,P,E,m=ext['H0']+eps,ext['T0']+eps,ext['P0']+eps,F(8)+eps,ext['m0']
        dd,do,ai=co['D_over_n2'],co['oscillator_over_n2'],co['inverse_A_absolute']
        assert min(dd,do,ai,kl,ext['e0'])>0 and rho*H<1
        tp=m*P+4*H*T;hp=T*T/3+ku*E*E
        realtp=m*ext['P0']+4*ext['H0']*ext['T0']
        anchor=max(F(1),ext['T0']+realtp)/(42*kl*ext['e0']*ext['e0'])
        b0=(anchor+rho*(T+3)/6)/(1-rho*H)
        b1=2*H*b0+T/3+1
        b2=2*(hp*b0+H*b1)+(tp+T)/3+12/rho
        metric=F(ceil(b0+b1+b2));channels={}
        for channel in ('geometric','current'):
            isgeom=channel=='geometric'
            ct=F(data['TRACEFREE_SOURCE_BUDGET']['arms'][name]['tracefree_constant']) if isgeom else F(0)
            sp=mix['metric_source_constant'] if isgeom else F(0)
            sc=rad['Sc_constant'] if isgeom else F(0);force=rad['F_constant'] if isgeom else F(0)
            xi=wall['graph_'+channel];j=normal['weighted_'+channel+'_constant']
            o=wall['oscillator_weighted'] if isgeom else F(0)
            rload=4*T*ct+(2*tp+21*T)*xi+2*j+o/do
            gload=ai*(rload/2+4*T*sc/dd)
            uf=scalar*(force+gload);up=metric*(sc+sp+uf);ub=ct+2*up
            osc=(uf+uf+T*xi+o)/do
            total=uf+up+ub+xi+osc
            vals={'Rload':rload,'gload':gload,'Uf':uf,'Up':up,'Ub':ub,'Qosc':osc,'K':total}
            assert {k:F(v) for k,v in result['arms'][name]['channels'][channel].items()}==vals
            channels[channel]={k:str(v) for k,v in vals.items()}
            (geometric if isgeom else current).append(total)
        assert F(result['arms'][name]['scalar_response'])==scalar
        assert F(result['arms'][name]['metric_response'])==metric
        arms[name]={'scalar_response':str(scalar),'metric_response':str(metric),'channels':channels}
    kg,kc=max(geometric),max(current);assert kg>0 and kc>0
    size=min(F(1)/(16*kg),F(1)/(88*A),F(1,1000000));radius=size/(16*kc)
    gap=1-A*size;assert gap>0 and size>0 and radius>0
    numerator=kg*size*size+kc*radius
    image=numerator/(gap**11)
    derivative=(2*kg*size*gap+11*A*numerator)/(gap**12)
    assert numerator<=size/8 and A*size<=F(1,88)
    assert image<size and derivative<F(1,2)
    exact={'KG':kg,'KC':kc,'s':size,'r_w':radius,'map_ratio':image/size,'derivative_bound':derivative}
    assert {k:F(v) for k,v in result['exact'].items()}==exact
    after=lease.observed();assert before==after
    assert all(sha(p)==digest for p,digest in hashes.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':'COEFFICIENT_ENVELOPE_CLOSURE_ARITHMETIC_VERIFIED',
        'source_sha256':sha(__file__),'inputs':hashes,'cpu':cpu,'occupied':occupied,'arms':arms,
        'exact':{k:str(v) for k,v in exact.items()},'runtime_before':before,'runtime_after':after,
        'scope':'Independent exact responses, channel assembly, maxima and complex contraction arithmetic; inherits analytic source and compatible inverse proofs. Coefficient-envelope radius only, not physical reconstruction or distance tail.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==FROZEN
        assert read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('closure_audit_lease',p)
        lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_120_SECONDS')))
        run(lease)
    except BaseException as error:
        if not (ROOT/'AUDIT_RESULT.json').exists():
            put('AUDIT_RESULT.json',{'pass':False,'classification':'TECHNICAL_INCOMPLETE',
                'source_sha256':sha(__file__),'error':repr(error),'traceback':traceback.format_exc()})
        if not (ROOT/'AUDIT_TERMINAL.json').exists():
            put('AUDIT_TERMINAL.json',{'pass':False,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
                'source_sha256':sha(__file__)})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()
