"""One-shot authenticated archive reduction; no evolution or inverse certificate."""
import sys
sys.dont_write_bytecode = True
import hashlib, importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT = Path(__file__).resolve().parent
FLOW = ROOT.parent / '20261026T033400Z_CUBIC_FULL_FLOW'
EXPECTED = '625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
LEASE = ROOT.parent / '20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'

def sha(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''): h.update(b)
    return h.hexdigest()

def read(p): return json.loads(Path(p).read_text())

def put(name, value):
    p = ROOT / name
    t = ROOT / (name + '.tmp')
    with t.open('x') as f:
        json.dump(value, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.chmod(t, 0o444); os.link(t, p); t.unlink()
    fd = os.open(ROOT, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)

def iv(v):
    a,b = map(Q,v['exact_bounds'])
    assert a <= b
    return a,b

def absmax(v): return max(abs(x) for x in iv(v))

def cutoff(ext):
    k,e,H,T,P,m = (ext[x] for x in ('k0','e0','H0','T0','P0','m0'))
    assert k > 0 and e > 0
    U = m*P+4*H*T
    B = 12*H*T+4*m*P
    d = 42*k*e*e; c = 9*k*e*e
    C = B*U/d; Cb = 2*T*U/d
    n = 1
    while c*n*n < m+C or Cb > Q(37,4)*n*n:
        n += 1
        assert n <= 100000, 'CUTOFF_RESOURCE_CEILING'
    return {'N':n, 'finite_low_orders':list(range(1,n)),
            'constants':{k:str(v) for k,v in dict(U0=U,B0max=B,d0=d,c0=c,C0=C,Cb=Cb,drift_bound=4*H+B*T/d).items()},
            'potential_margin':str(c*n*n-m-C),
            'boundary_margin':str(Q(37,4)*n*n-Cb),
            'previous_order_fails_sufficient_gate': n==1 or c*(n-1)**2 < m+C or Cb > Q(37,4)*(n-1)**2}

def arm(name, terminals, binding, arb, fmpq):
    path = FLOW / ('FLOW_'+name+'.json')
    assert sha(path) == terminals['production']['artifacts'][path.name]
    data = read(path); assert data['pass'] and data['matching']['resolved']
    ext = dict(H0=Q(0),T0=Q(0),P0=Q(0),m0=absmax(data['parameters']['m2']),k0=iv(data['parameters']['k'])[0])
    e0 = None; wmax = None; j = 0; prev = None
    for entry in data['chunks']:
        path = FLOW/entry['file']; digest = sha(path)
        assert digest == entry['sha256']
        chunk = read(path)
        assert chunk['engine']==name and chunk['binding_sha256']==binding
        assert chunk['previous_sha256']==prev and chunk['parameters_sha256']==data['parameters_sha256']
        assert chunk['first']==entry['first']==j and chunk['last']==entry['last']
        cp = FLOW/entry['checkpoint']; assert sha(cp)==entry['checkpoint_sha256']
        checkpoint=read(cp)
        assert checkpoint['binding_sha256']==binding and checkpoint['engine']==name
        assert checkpoint['chunk_sha256']==digest and checkpoint['completed']==entry['last']+1
        assert checkpoint['parameters_sha256']==data['parameters_sha256'] and checkpoint['total']==data['cells']
        for cell in chunk['records']:
            assert cell['index']==j
            box=cell['box']; assert len(box)==(20 if name=='primary' else 19)
            for label,idx in (('H0',1),('P0',2),('T0',3)):
                ext[label]=max(ext[label],absmax(box[idx]))
            if name=='primary':
                e=iv(box[4])[0]; e0=e if e0 is None else min(e0,e)
            else:
                w=iv(box[0])[1]; wmax=w if wmax is None else max(wmax,w)
            j+=1
        assert j==entry['last']+1
        prev=digest
        if j%2048==0: print(name,j,flush=True)
    assert j==data['cells']
    h=Q(data['step']); dlo,dhi=map(Q,data['D'])
    assert 0<dlo<=dhi<=j*h and (j-1)*h<dhi
    if name=='independent':
        x=arb(fmpq(str(-wmax))).exp()
        e0=Q(str(x.lower().fmpq()))
    ext['e0']=e0
    result={'engine':name,'cells':j,'chunks':len(data['chunks']),
            'extrema_exact':{k:str(v) for k,v in ext.items()},
            'extrema_approximate':{k:float(v) for k,v in ext.items()},
            'domain':data['D'],'covered_to':str(j*h),
            'extra_terminal_cover_included':True,
            'cutoff':cutoff(ext)}
    if wmax is not None: result['maximum_W_upper_exact']=str(wmax)
    put('ARM_'+name+'.json',result)
    print(name,'cutoff',result['cutoff']['N'],result['extrema_approximate'],flush=True)
    return result

def main():
    assert sys.platform=='linux'
    assert not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json')),'NO_RESTART'
    assert sha(FLOW/'FROZEN.json')==EXPECTED
    parent=read(FLOW/'FROZEN.json')
    assert parent['files'][str(LEASE)]==sha(LEASE)
    spec=importlib.util.spec_from_file_location('cutoff_lease',LEASE)
    lease=importlib.util.module_from_spec(spec);spec.loader.exec_module(lease);lease.ROOT=ROOT
    try:
        cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('EXTRACTION_900_SECONDS')))
        signal.alarm(900)
        for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
            assert os.environ[key]=='1'
        assert os.environ['PYTHONHASHSEED']=='0'
        started=time.monotonic()
        sys.path.insert(0,str(lease.FLINT))
        from flint import arb,fmpq,ctx
        ctx.prec=768;ctx.threads=1
        terminals={}
        for mode in ('production','audit'):
            t=read(FLOW/(mode+'_TERMINAL.json'))
            assert t['pass'] and t['frozen_sha256']==EXPECTED
            for path,digest in t['artifacts'].items(): assert sha(FLOW/path)==digest
            terminals[mode]=t
        # Authenticate all inherited frozen dependencies, not merely the flow filenames.
        for path,digest in parent['files'].items(): assert sha(path)==digest,path
        binding={'source_sha256':sha(__file__),'parent_frozen_sha256':EXPECTED,
                 'parent_terminals':{m:sha(FLOW/(m+'_TERMINAL.json')) for m in terminals},
                 'runtime':lease.observed(),'precision':768,'threads':1,
                 'claim':'diagnostic real-axis sufficient cutoff; not uniform inverse or amplitude certificate'}
        put('BINDING.json',binding)
        put('START.json',{'pid':os.getpid(),'cpu':cpu,'occupied':occupied})
        # Exact simple arithmetic controls, including a deliberately false candidate cutoff.
        control=cutoff(dict(k0=Q(1),e0=Q(1),H0=Q(0),T0=Q(0),P0=Q(0),m0=Q(10)))
        assert control['N']==2 and Q(9)<10
        arms={name:arm(name,terminals,EXPECTED,arb,fmpq) for name in ('primary','independent')}
        for path,digest in parent['files'].items(): assert sha(path)==digest,path
        assert sha(__file__)==binding['source_sha256']
        after=lease.observed()
        assert after==binding['runtime'],'RUNTIME_CHANGED'
        result={'classification':'DIAGNOSTIC_BACKGROUND_CUTOFF_EXTRACTED','arms':arms,
                'common_N':max(a['cutoff']['N'] for a in arms.values()),
                'seconds':time.monotonic()-started,'parent_bindings_verified':True,
                'independent_source_review_completed':False,
                'uniform_inverse_constant_certified':False,'amplitude_radius_certified':False}
        put('RESULT.json',result)
        put('TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'RESULT.json'),
                            'binding_sha256':sha(ROOT/'BINDING.json')})
        print(json.dumps({k:v for k,v in result.items() if k!='arms'}),flush=True)
    except BaseException as exc:
        put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()})
        raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()

if __name__=='__main__': main()
