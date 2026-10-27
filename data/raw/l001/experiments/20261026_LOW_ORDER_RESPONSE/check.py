"""Direct saved-cell low-order positivity and conditional response diagnostics."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261026_BACKGROUND_CUTOFF'
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
io=load('low_io',BASE/'extract.py')
assert io.sha(BASE/'extract.py')=='9accc8fffdd3700ed83b20900cdff88055fa503d4d0a28e2d8b66418b10964e5'
io.ROOT=ROOT
lease=load('low_lease',io.LEASE);lease.ROOT=ROOT
def main():
    assert sys.platform=='linux' and not (ROOT/'START.json').exists()
    cpu,occupied=lease.acquire();signal.alarm(900)
    io.put('START.json',{'cpu':cpu,'occupied':occupied})
    sys.path.insert(0,str(lease.FLINT))
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    def iv(x):
        lo,hi=map(fmpq,x['exact_bounds']);assert lo<=hi
        return arb((lo+hi)/2,(hi-lo)/2)
    def lower(x):assert x.is_finite();return Q(str(x.lower().fmpq()))
    def upper(x):assert x.is_finite();return Q(str(x.upper().fmpq()))
    assert io.sha(io.FLOW/'FROZEN.json')==io.EXPECTED
    frozen=io.read(io.FLOW/'FROZEN.json')
    for p,d in frozen['files'].items():assert io.sha(p)==d,p
    terminal=io.read(io.FLOW/'production_TERMINAL.json')
    assert terminal['pass'] and terminal['frozen_sha256']==io.EXPECTED
    binding={'source_sha256':io.sha(__file__),'parent':io.EXPECTED,'runtime':lease.observed(),
             'orders':[1,38],'status':'diagnostic; inherits saved cell certificates'}
    io.put('BINDING.json',binding)
    start=time.monotonic();arms={}
    for name in ('primary','independent'):
        path=io.FLOW/('FLOW_'+name+'.json');assert io.sha(path)==terminal['artifacts'][path.name]
        data=io.read(path);assert data['pass']
        m,k=iv(data['parameters']['m2']),iv(data['parameters']['k'])
        bounds={n:None for n in range(1,39)};j=0;previous=None
        for entry in data['chunks']:
            p=io.FLOW/entry['file'];assert io.sha(p)==entry['sha256']
            chunk=io.read(p)
            assert chunk['previous_sha256']==previous and chunk['binding_sha256']==io.EXPECTED
            assert chunk['parameters_sha256']==data['parameters_sha256'] and chunk['engine']==name
            assert chunk['first']==entry['first']==j
            cp=io.FLOW/entry['checkpoint'];assert io.sha(cp)==entry['checkpoint_sha256']
            receipt=io.read(cp)
            assert receipt['chunk_sha256']==entry['sha256'] and receipt['binding_sha256']==io.EXPECTED
            assert receipt['completed']==entry['last']+1 and receipt['total']==data['cells']
            for cell in chunk['records']:
                assert cell['index']==j
                box=cell['box'];assert len(box)==(20 if name=='primary' else 19)
                W,H,P,T=map(iv,box[:4]);E=iv(box[4]) if name=='primary' else (-W).exp()
                Tp=m*P-4*H*T;B=12*H*T-4*m*P
                for n in bounds:
                    mu=-18*n*(2*n-1)*k
                    J=-3*(mu+4*k)*E*E;assert lower(J)>0
                    D=2*T*T+J;assert lower(D)>0
                    V=m-mu*E*E+2*T*T+B*Tp/D
                    drift=-4*H-B*T/D
                    # Conservative lower bound for either wall orientation, over the entire covered domain.
                    Gamma=21-1/(2-mu*E*E)
                    beta=Gamma*D/(2*J)-2*abs(T*Tp)/J
                    values=(lower(V),upper(abs(V)),upper(abs(drift)),lower(beta))
                    old=bounds[n]
                    bounds[n]=values if old is None else (min(old[0],values[0]),max(old[1],values[1]),max(old[2],values[2]),min(old[3],values[3]))
                j+=1
            assert j==entry['last']+1;previous=entry['sha256']
            if j%2048==0:print(name,j,round(time.monotonic()-start,1),flush=True)
        h=Q(data['step']);Llo,Lhi=map(Q,data['D'])
        assert j==data['cells'] and 0<Llo<=Lhi<=j*h and (j-1)*h<Lhi
        results={}
        for n,(vmin,vmax,A,bmin) in bounds.items():
            row={'bounds_exact':dict(zip(('V_min','V_abs_max','drift_abs_max','beta_lower'),map(str,(vmin,vmax,A,bmin)))),
                 'bounds_display':dict(zip(('V_min','V_abs_max','drift_abs_max','beta_lower'),map(float,(vmin,vmax,A,bmin)))),
                 'positive_gate':vmin>0 and bmin>0}
            if row['positive_gate']:
                delta=min(Llo/2,1/(A+1));den=1-A*delta/2;assert delta>0 and den>0
                C0=max(1/vmin,1/(n*bmin))
                C1=((2/delta+delta*vmax/2)*C0+delta/2)/den
                C2=A*C1+vmax*C0+1
                total=n*n*C0+n*C1+C2
                row.update(C_sum_exact=str(total),C_sum_integer=-(-total.numerator//total.denominator))
            results[str(n)]=row
        arms[name]=results
        io.put('ARM_'+name+'.json',results)
        print(name,'positive',[n for n,v in results.items() if v['positive_gate']],flush=True)
    assert io.sha(__file__)==binding['source_sha256']
    for p,d in frozen['files'].items():assert io.sha(p)==d,p
    io.put('RESULT.json',{'classification':'LOW_ORDER_REAL_AXIS_DIAGNOSTIC','arms':arms,'seconds':time.monotonic()-start,
         'independent_arithmetic_replay':False,'complex_collar_bound':False,'amplitude_radius_certified':False})
    io.put('TERMINAL.json',{'pass':True,'result_sha256':io.sha(ROOT/'RESULT.json'),'binding_sha256':io.sha(ROOT/'BINDING.json')})
    print('COMPLETE',round(time.monotonic()-start,1),flush=True)
if __name__=='__main__':
    try:
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('LOW_ORDER_900_SECONDS')))
        main()
    except BaseException as e:
        io.put('FAILURE.json',{'error':repr(e),'traceback':traceback.format_exc()});raise
    finally:
        signal.alarm(0)
        for f in lease.handles:f.close()
