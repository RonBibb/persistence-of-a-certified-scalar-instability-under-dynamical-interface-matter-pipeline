"""Independent exact split-metric response and downstream recertification."""
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
PINS={
'20261026_COEFFICIENT_ENVELOPE_CLOSURE/RESULT.json':'3aa11d9a779bba1f1a3efde5c632d43ef5e623178f033dd0f15e0a04b1c37906',
'20261026_COEFFICIENT_ENVELOPE_CLOSURE/BINDING.json':'eeb4b48a25781e9e8e39b613619f4b481dcd8fc79bfa45346e1bb28cb014c21e',
'20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1/AUDIT_RESULT.json':'fa805f5eff415c6ec019ec9f111a3f4c52e70f8d70c3481b9e012e8b781319db',
'20261026_RECONSTRUCTION_DOMAIN/RESULT.json':'33b94170c6d6eb66bb1da7c64149c2fcc34efe379419f4fda6067710b0f148c4',
'20261026_RECONSTRUCTION_DOMAIN/AUDIT_RESULT.json':'fd5cc36371250132b07e2291242ce465cf7d7a1c711fb3273b70b99d547ab8d4',
'20261026_DISTANCE_TAIL/RESULT.json':'447b19af1290cffd82fdff0e3c7f3b78bffe24d1be088dc65dd6aeb3ac6ac608',
'20261026_DISTANCE_TAIL/BINDING.json':'c9f5c0a763cff1ab1b093db78f76b08e03053a4d05e57d4d3e2ec8586f2edc2a',
'20261026_DISTANCE_TAIL/AUDIT_RESULT.json':'2c419e8bec3ee81f7588c6e1d4c9d0e12f3acea21f25754b27730c43e0e21c5e'}
SELF_PINS={ROOT/'check.py':'5fbb650408ef2a94986213f73493e2a4798cda683fcfbf12cc3ac235b5b58a60',
           ROOT/'RESULT.json':'fd57632ed9769362a99d985699be6250dbb499a99ef5d8e21d44875d8e2c41f0',
           ROOT/'BINDING.json':'5b468c55a6da625f68662a8edfba400ca26d521e71921eb164cf5ede11d8a47b'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def ceil(x):return -((-x.numerator)//x.denominator)
def put(name,value):
    p=ROOT/name;t=ROOT/(name+'.tmp')
    with t.open('x') as f:
        json.dump(value,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def run(lease):
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('AUDIT_RESULT.json','AUDIT_TERMINAL.json'))
    cpu,occupied=lease.acquire();signal.alarm(120)
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001 and Path(sys.modules['_pylong'].__file__).resolve()==pylong
    inputs={str(BASE/p):digest for p,digest in PINS.items()}
    for p,digest in inputs.items():assert sha(p)==digest
    for name in ('20261026_COEFFICIENT_ENVELOPE_CLOSURE','20261026_DISTANCE_TAIL'):
        oldbinding=read(BASE/name/'BINDING.json')
        for p,digest in oldbinding['inputs'].items():
            assert sha(p)==digest and (p not in inputs or inputs[p]==digest)
            inputs[p]=digest
    terminals=[
        ('20261026_COEFFICIENT_ENVELOPE_CLOSURE','TERMINAL.json','RESULT.json'),
        ('20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1','AUDIT_TERMINAL.json','AUDIT_RESULT.json'),
        ('20261026_RECONSTRUCTION_DOMAIN','TERMINAL.json','RESULT.json'),
        ('20261026_RECONSTRUCTION_DOMAIN','AUDIT_TERMINAL.json','AUDIT_RESULT.json'),
        ('20261026_DISTANCE_TAIL','TERMINAL.json','RESULT.json'),
        ('20261026_DISTANCE_TAIL','AUDIT_TERMINAL.json','AUDIT_RESULT.json')]
    for folder,t,r in terminals:
        termpath=BASE/folder/t;ter=read(termpath)
        assert ter['pass'] and ter['result_sha256']==sha(BASE/folder/r)
        inputs[str(termpath)]=sha(termpath)
        if 'binding_sha256' in ter:
            bp=BASE/folder/'BINDING.json';assert ter['binding_sha256']==sha(bp);inputs[str(bp)]=sha(bp)
    for p,digest in SELF_PINS.items():assert sha(p)==digest
    for p in (Path(__file__),ROOT/'check.py',ROOT/'RESULT.json',ROOT/'BINDING.json',ROOT/'TERMINAL.json',pylong):
        inputs[str(p)]=sha(p)
    result=read(ROOT/'RESULT.json');binding=read(ROOT/'BINDING.json');terminal=read(ROOT/'TERMINAL.json')
    assert terminal['pass'] and terminal['result_sha256']==sha(ROOT/'RESULT.json')
    if 'binding_sha256' in terminal:assert terminal['binding_sha256']==sha(ROOT/'BINDING.json')
    assert binding['source_sha256']==sha(ROOT/'check.py')
    for p,digest in binding['inputs'].items():assert sha(p)==digest
    def parent(name):return read(BASE/('20261026_'+name)/'RESULT.json')
    old=parent('COEFFICIENT_ENVELOPE_CLOSURE');tail=parent('DISTANCE_TAIL');real=parent('RESPONSE_AUDIT')
    radial=parent('SCALAR_RADIAL_SOURCE_BUDGET');mixed=parent('MIXED_SOURCE_BUDGET')
    assert all(o['pass'] for o in (old,tail,real,radial,mixed,result))
    for rel,obj in (('20261026_COEFFICIENT_ENVELOPE_CLOSURE_AUDIT_R1/AUDIT_RESULT.json',old),
                    ('20261026_DISTANCE_TAIL/AUDIT_RESULT.json',tail)):
        audited=read(BASE/rel);assert audited['pass'] and audited['exact']==obj['exact']
    rho=F(1,40000);A=F(160001);L=F(12)/rho;eps=F(1,1000)
    assert F(old['working_collar'])==rho and F(old['denominator_scale'])==A and L.denominator==1
    assert sha(FLOW/'FROZEN.json')==FROZEN
    ft=read(FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==FROZEN
    inputs[str(FLOW/'production_TERMINAL.json')]=sha(FLOW/'production_TERMINAL.json')
    before=lease.observed();arms={};geoms=[];currents=[];flows={}
    for name in ('primary','independent'):
        p=FLOW/('FLOW_'+name+'.json');assert sha(p)==ft['artifacts'][p.name]
        flow=read(p);flows[name]=flow;kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        e={k:F(v) for k,v in real['arms'][name]['extrema'].items()}
        H,T,P,E,m=e['H0']+eps,e['T0']+eps,e['P0']+eps,F(8)+eps,e['m0']
        assert kl>0 and e['e0']>0 and rho*H<1
        realtp=m*e['P0']+4*e['H0']*e['T0']
        anchor=max(F(1),e['T0']+realtp)/(42*kl*e['e0']*e['e0'])
        tp=m*P+4*H*T;hp=T*T/3+ku*E*E
        b0=(anchor+rho*(T+3)/6)/(1-rho*H);b1=2*H*b0+T/3+1
        remainder=(1+2*hp)*b0+(1+2*H)*b1+(tp+T)/3
        oldC=F(old['arms'][name]['metric_response']);rem=oldC-L
        assert oldC==ceil(remainder+L) and 0<remainder<=rem
        assert rem==ceil(remainder)
        channels={}
        for channel in ('geometric','current'):
            saved={k:F(v) for k,v in old['arms'][name]['channels'][channel].items()}
            sc=F(radial['arms'][name]['exact']['Sc_constant']) if channel=='geometric' else F(0)
            sp=F(mixed['arms'][name]['exact']['metric_source_constant']) if channel=='geometric' else F(0)
            assert saved['Up']==oldC*(sc+saved['Uf']+sp)
            up=rem*(sc+saved['Uf'])+oldC*sp
            newK=saved['K']-3*saved['Up']+3*up
            assert 0<up<=saved['Up'] and 0<newK<=saved['K']
            vals={'new_Up':up,'new_K':newK,'old_K':saved['K'],'K_reduction_factor':saved['K']/newK}
            channels[channel]={k:str(v) for k,v in vals.items()}
            (geoms if channel=='geometric' else currents).append(newK)
        arms[name]={'unrounded_remainder':str(remainder),'remainder_ceiling':str(rem),
                    'mixed_derivative_cost':str(L),'channels':channels}
    kg,kc=max(geoms),max(currents);assert kg>0 and kc>0
    size=min(F(1)/(16*kg),F(1)/(88*A),F(1,1000000));r=size/(16*kc)
    gap=1-A*size;numerator=kg*size*size+kc*r
    image=numerator/gap**11;derivative=(2*kg*size*gap+11*A*numerator)/gap**12
    assert gap>0 and image<size and derivative<F(1,2)
    radius=r/32;assert radius>0 and 16*radius==r/2 and 0<size<1 and 2*size<1
    domains={};g=F(3,25);E=F(8001,1000)
    for name,flow in flows.items():
        lo,hi=map(F,flow['D']);kl,ku=map(F,flow['parameters']['k']['exact_bounds'])
        assert hi>=lo>1 and 0<kl<=ku<F(1,2500)
        T=F(real['arms'][name]['extrema']['T0'])+eps
        shift=size*(2*lo+rho)/(2*lo);ratio=shift/(rho/2)
        speed=2*E*g*size;coupling=size*(T+1)/1000
        gates={'shift_margin':rho/4-shift,'composition_margin':F(1,2)-ratio,
            'jacobian_lower':(lo-size)/lo,'separation_lower':lo-size,'speed_margin':F(1,4)-speed,
            'boost_squared_margin':1-speed*speed,'coupling_lower':1-coupling,
            'coupling_margin':F(1,2)-coupling,'exponential_margin':(1-4*size)/(1-2*size)}
        assert all(v>0 for v in gates.values())
        domains[name]={k:str(v) for k,v in gates.items()}
    dmin=min(F(flow['D'][0]) for flow in flows.values());dmax=max(F(flow['D'][1]) for flow in flows.values())
    bound=dmax*size*(1+F(1)/dmin)/(1-size)
    coeff={k:tuple(map(F,v['exact_bounds'])) for k,v in tail['coefficients'].items()}
    assert set(coeff)=={'d1','d2','d3'} and all(lo<=hi<0 for lo,hi in coeff.values()) and tail['direction']==[1,0]
    strength=-coeff['d1'][1];history=result['radius_construction'];assert 1<=len(history)<=513
    capped=result['classification']=='SPLIT_METRIC_SUFFICIENT_INTERVAL_UNRESOLVED'
    for i,row in enumerate(history):
        x=F(1,2**(i+1));ratio=bound*x*x*x/(radius*(1-x));ok=ratio<=strength/2
        assert row=={'halvings':i,'x':str(x),'tail_per_z':str(ratio),'pass':ok}
        assert ok==((i==len(history)-1) and not capped)
    if capped:
        assert len(history)==513
        exact={};classification='SPLIT_METRIC_UNRESOLVED_ARITHMETIC_VERIFIED'
    else:
        assert result['classification']=='SPLIT_METRIC_SHORTENING_DIAGNOSTIC'
        x=F(1,2**len(history));zmax=radius*x;tailbound=bound*x*x*x*x/(1-x)
        poly=zmax*(coeff['d1'][1]+zmax*(coeff['d2'][1]+zmax*coeff['d3'][1]))
        assert tailbound<=strength*zmax/2 and poly+tailbound<=-strength*zmax/2<0
        exact={'KG':kg,'KC':kc,'s':size,'r_w':r,'reconstruction_radius':radius,'z_upper':zmax,
            'distance_bound':bound,'contraction_derivative':derivative,'map_ratio':image/size,
            'tail_per_z':tailbound/zmax,'uniform_shortening_per_z':strength/2,
            'coefficient_radius_gain':r/F(old['exact']['r_w']),'shortening_radius_gain':zmax/F(tail['exact']['z_upper'])}
        assert {k:F(v) for k,v in result['exact'].items()}==exact
        assert result['arms']==arms and result['domains']==domains and result['coefficients']==tail['coefficients']
        classification='SPLIT_METRIC_SHORTENING_ARITHMETIC_VERIFIED'
    after=lease.observed();assert before==after
    assert all(sha(p)==digest for p,digest in inputs.items())
    put('AUDIT_RESULT.json',{'pass':True,'classification':classification,'source_sha256':sha(__file__),
        'inputs':inputs,'cpu':cpu,'occupied':occupied,'arms':arms,'domains':domains,
        'exact':{k:str(v) for k,v in exact.items()},'runtime_before':before,'runtime_after':after,
        'scope':'Same-norm split metric response with unchanged Sp derivative cost; exact downstream contraction, reconstruction and inherited-coefficient distance-tail arithmetic. Conditional fixed-time shortening only, not time contraction or stability.'})
    put('AUDIT_TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),
        'source_sha256':sha(__file__),'producer_result_sha256':sha(ROOT/'RESULT.json')})
if __name__=='__main__':
    lease=None
    try:
        p=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'
        assert sha(FLOW/'FROZEN.json')==FROZEN and read(FLOW/'FROZEN.json')['files'][str(p)]==sha(p)
        spec=importlib.util.spec_from_file_location('split_audit_lease',p)
        lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_120_SECONDS')))
        run(lease)
    except BaseException as error:
        if not (ROOT/'AUDIT_RESULT.json').exists():
            put('AUDIT_RESULT.json',{'pass':False,'classification':'TECHNICAL_INCOMPLETE',
                'source_sha256':sha(__file__),'error':repr(error),'traceback':traceback.format_exc()})
        if not (ROOT/'AUDIT_TERMINAL.json').exists():
            put('AUDIT_TERMINAL.json',{'pass':False,'result_sha256':sha(ROOT/'AUDIT_RESULT.json'),'source_sha256':sha(__file__)})
        raise
    finally:
        signal.alarm(0)
        if lease is not None:
            for handle in lease.handles:handle.close()

