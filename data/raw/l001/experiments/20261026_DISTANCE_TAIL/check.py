"""Exact distance-tail certificate in the fixed lower-unit-current direction."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, signal, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
helper=BASE/'20261026_BACKGROUND_CUTOFF/extract.py'
assert hashlib.sha256(helper.read_bytes()).hexdigest()=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io=load('distance_tail_io',helper);io.ROOT=ROOT
assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
assert io.read(io.FLOW/'FROZEN.json')['files'][str(io.LEASE)]==io.sha(io.LEASE)
lease=load('distance_tail_lease',io.LEASE);lease.ROOT=ROOT
RECON=BASE/'20261026_RECONSTRUCTION_DOMAIN'
SECOND=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
CUBIC=BASE/'20261026T100400Z_CUBIC_DISTANCE'
PINS={
RECON/'RESULT.json':'33b94170c6d6eb66bb1da7c64149c2fcc34efe379419f4fda6067710b0f148c4',
RECON/'AUDIT_RESULT.json':'fd5cc36371250132b07e2291242ce465cf7d7a1c711fb3273b70b99d547ab8d4',
SECOND/'PRODUCTION_RESULT.json':'4334b96168adc171dbaf14cb8aae492a8b9bc9550a6d1421283be0e8bce78241',
SECOND/'PRODUCTION_primary.json':'a0a12b5b2d7ae4ecf0fd167b547c47f960ac31ac5d1b79f62923fe39ba860ac2',
SECOND/'PRODUCTION_independent.json':'40577bac466df999b62af892acfd7b7bb8e3a43367d8d922c9e8d7415cbc1b99',
SECOND/'terminal_audit/AUDIT_RESULT.json':'5cfe74a338d44c3d760eabdd668407df7cee5e9dd8ad4a0968628d88a77fec55',
SECOND/'terminal_audit/TERMINAL.json':'d42e701108019ca50b2e9ede4adfbcf346bf66c94fbca560a246f35188db918f',
SECOND/'CONTRACT.md':'0aaaa012df848d662d688156b67e6c68bba538221ab769137fb5cb7edbcaeb22',
SECOND/'production_TERMINAL.json':'3f73c729b68fb27ce842670bcd1e6b7e4537099ba81ceb5a81979f329d7934b6',
CUBIC/'RESULT.json':'a9d4b4bc67b65021fbd3ecfdcbfe0ceb49bfa1572e9821e7e45b9bebf6940647',
CUBIC/'AUDIT_RESULT.json':'0b11deb93d18e7e1f3bae9b66d5f8245327a07e51fc822c26536834c630c0a02',
CUBIC/'production_TERMINAL.json':'0994c2ea5a63f4f36eb3d671edbdaefc7daf002123af4ea61913eec155741282',
CUBIC/'audit_TERMINAL.json':'ff334496fa45e2b5501229b9269399e88e8e182ec205be44cae82ecb5cbcdb4a',
CUBIC/'INDEPENDENT_TERMINAL_CHECK.json':'3c2bad23f68484c3bf85b0357c05c6e7c4df5b3fd304893ae18613ae83921d28',
CUBIC/'CONTRACT.md':'7ac66bdb3487891528021f75fd5dc3e05c09fb27163225a029f10cc45491d08e'}
def interval(value):
    lo,hi=map(Q,value['exact_bounds']);assert lo<=hi;return lo,hi
def run():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(120)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    for path,digest in PINS.items():assert io.sha(path)==digest
    rec=io.read(RECON/'RESULT.json');ra=io.read(RECON/'AUDIT_RESULT.json')
    assert rec['pass'] and ra['pass'] and rec['normalized_radius']==ra['normalized_radius']
    second=io.read(SECOND/'PRODUCTION_RESULT.json');sa=io.read(SECOND/'terminal_audit/AUDIT_RESULT.json')
    assert second['all_gates'] and sa['status']=='PASS_SAVED_RECORD_CONSISTENCY'
    assert io.read(SECOND/'terminal_audit/TERMINAL.json')['pass']
    assert io.read(SECOND/'production_TERMINAL.json')['pass']
    cubic=io.read(CUBIC/'RESULT.json');assert cubic['pass'] and io.read(CUBIC/'AUDIT_RESULT.json')['pass']
    assert io.read(CUBIC/'INDEPENDENT_TERMINAL_CHECK.json')['pass']
    for filename,artifact in [('production_TERMINAL.json','RESULT.json'),('audit_TERMINAL.json','AUDIT_RESULT.json')]:
        term=io.read(CUBIC/filename)
        assert term['pass'] and term['artifacts'][artifact]==io.sha(CUBIC/artifact)
    inputs={str(p):v for p,v in PINS.items()}
    ft=io.read(io.FLOW/'production_TERMINAL.json');assert ft['pass'] and ft['frozen_sha256']==io.EXPECTED
    flows={}
    for name in ('primary','independent'):
        path=io.FLOW/('FLOW_'+name+'.json');assert io.sha(path)==ft['artifacts'][path.name]
        inputs[str(path)]=io.sha(path);flows[name]=io.read(path)
    inputs[str(io.FLOW/'FROZEN.json')]=io.EXPECTED;inputs[str(io.LEASE)]=io.sha(io.LEASE)
    pylong=Path('/usr/lib/python3.12/_pylong.py')
    assert io.sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c'
    assert len(str(10**20000))==20001;inputs[str(pylong)]=io.sha(pylong)
    runtime=lease.observed()
    binding={'source_sha256':io.sha(__file__),'derivation_sha256':io.sha(ROOT/'DERIVATION.md'),
        'inputs':inputs,'runtime':runtime,'direction':[1,0],'factorial_convention':'none'}
    io.put('BINDING.json',binding)
    def publish(result):
        assert lease.observed()==runtime and all(io.sha(p)==h for p,h in inputs.items())
        assert io.sha(__file__)==binding['source_sha256'] and io.sha(ROOT/'DERIVATION.md')==binding['derivation_sha256']
        io.put('RESULT.json',result)
        io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    Dvalues=[tuple(map(Q,flows[n]['D'])) for n in flows]
    Dmin=min(v[0] for v in Dvalues);Dmax=max(v[1] for v in Dvalues)
    assert 0<Dmin<=Dmax
    s=Q(rec['envelope_bound']);R=Q(rec['normalized_radius']);assert 0<s<1 and R>0
    BD=Dmax*(s/Dmin+s)/(1-s)
    d1s=[]
    for name in ('primary','independent'):
        production=io.read(SECOND/('PRODUCTION_'+name+'.json'));assert production['all_gates']
        d1=interval(production['d1']);d1s.append(d1)
        audited=next(v for v in sa['engines'] if v['engine']==name)
        alo,ahi=interval(audited['reconstructed']['d1'])
        assert d1[0]<=alo<=ahi<=d1[1]
        # Full flow binds these exact parents and may export wider bounds.
        inherited=io.read(io.FLOW/'FROZEN.json')['files']
        assert inherited[str(SECOND/('PRODUCTION_'+name+'.json'))]==PINS[SECOND/('PRODUCTION_'+name+'.json')]
        klo,khi=interval(production['parameters']['k']);flo,fhi=interval(flows[name]['parameters']['k'])
        assert flo<=klo<=khi<=fhi
    d1=(min(v[0] for v in d1s),max(v[1] for v in d1s))
    d2=interval(second['d2']);d3=interval(cubic['distance'])
    if not (d1[1]<0 and d2[1]<0 and d3[1]<0):
        publish({'pass':True,'classification':'DISTANCE_SHORTENING_SUFFICIENT_TEST_UNRESOLVED',
                 'reason':'SIGN_PREREQUISITE_NOT_MET','shortening_certified':False,
                 'coefficients':{key:{'exact_bounds':[str(v) for v in val]} for key,val in [('d1',d1),('d2',d2),('d3',d3)]}})
        return
    a=-d1[1];history=[];x=Q(1,2)
    for step in range(513):
        ratio=BD*x**3/(R*(1-x));passed=ratio<=a/2
        history.append({'halvings':step,'x':str(x),'tail_per_z':str(ratio),'pass':passed})
        if passed:break
        x/=2
    else:
        publish({'pass':True,'classification':'DISTANCE_SHORTENING_SUFFICIENT_TEST_UNRESOLVED',
                 'reason':'NO_SUFFICIENT_RADIUS_WITHIN_512_HALVINGS','shortening_certified':False,
                 'radius_construction':history})
        return
    z0=R*x;tail=BD*x**4/(1-x)
    assert 0<z0<R and tail/z0<=a/2
    assert all(not entry['pass'] for entry in history[:-1])
    polynomial=d1[1]*z0+d2[1]*z0**2+d3[1]*z0**3
    assert polynomial+tail<=-a*z0/2<0
    vals=dict(distance_disk_radius=R,field_bound=s,Dmin=Dmin,Dmax=Dmax,distance_bound=BD,
              z_upper=z0,dyadic_fraction=x,linear_strength=a,tail_at_upper=tail,
              tail_per_z_at_upper=tail/z0,uniform_shortening_per_z=a/2,
              polynomial_upper_at_z_upper=polynomial,total_upper_at_z_upper=polynomial+tail)
    result={'pass':True,'classification':'DISTANCE_TAIL_SHORTENING_DIAGNOSTIC','direction':[1,0],
        'exact':{k:str(v) for k,v in vals.items()},'display':{k:float(v) for k,v in vals.items()},
        'coefficients':{key:{'exact_bounds':[str(v) for v in val]} for key,val in [('d1',d1),('d2',d2),('d3',d3)]},
        'radius_construction':history,'uniform_statement':'For every real 0<z<=z_upper, D(z)-D0 <= -uniform_shortening_per_z*z < 0.',
        'scope':'Conditional inherited analytic branch and validated coefficient enclosures; fixed-time lower-unit-current direction. Sufficient interval, not optimal radius, time contraction, global stability or formation.'}
    publish(result)
    print(json.dumps({'display':result['display'],'halvings':history[-1]['halvings']}),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('DISTANCE_TAIL_120_SECONDS')))
        run()
    except BaseException as error:
        io.put('FAILURE.json',{'error':repr(error),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for handle in lease.handles:handle.close()
