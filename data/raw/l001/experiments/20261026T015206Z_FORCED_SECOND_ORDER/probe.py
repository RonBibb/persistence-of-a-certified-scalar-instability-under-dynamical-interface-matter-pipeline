"""Frozen short-domain augmented feasibility probe; Linux lease required."""
import sys
sys.dont_write_bytecode=True
import importlib.util, json, os, resource, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION'

def read(p): return json.loads(Path(p).read_text())
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);sys.modules[name]=mod;spec.loader.exec_module(mod);return mod
def put(name,data):
    path=ROOT/name;tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('x') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,path);tmp.unlink()
def pack(v):return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def zero(v):return v.lower()<=0<=v.upper()
def need(test,label):
    if not test:raise RuntimeError(label)

def initial(m,name):
    from flint import arb,fmpq
    t10=PARENT/'T10_AB_CURRENT_RADAR_RESPONSE'
    binding=read(t10/'inputs/central_bindings.json')
    def ball(x):return m.interval(*map(fmpq,x['exact_bounds']))
    model={key:m.exact(value) for key,value in binding['model_exact'].items()}
    A=m.interval(*map(fmpq,binding['config']['A']))
    H=-(model['lambda_a']+model['gamma']*(A-model['v0'])**2/2)/6
    T=model['gamma']*(A-model['v0'])/2
    k=H*H-1-T*T/12+model['m2']*A*A/12
    p=dict(m2=model['m2'],k=k,mu1=-18*k,mu2=-108*k)
    assembly=read(t10/'output'/('current_radar_'+name+'.json'))['full_forced_assembly']
    a1=ball(assembly['channels']['lower']['homogeneous_multiplier'])
    yh=read(t10/'output'/('homogeneous_'+name+'.json'))['lower_state']
    yp=read(t10/'output'/('particular_lower_'+name+'.json'))['lower_state']
    first=[a1*ball(a)+ball(b) for a,b in zip(yh[-3:],yp[-3:])]
    canonical=[arb(0),H,A,T,arb(1)]+first+[arb(0)]*6
    y=canonical if name=='primary' else canonical[:4]+canonical[5:]
    src=m.sources(y,p);sc=src[2] if name=='primary' else src['Sc']
    loads=read(PARENT/'T18_AB_COMPLETE_QUADRATIC_WALL_SOURCE_QUALIFICATION/RESULT.json')
    R=ball(loads['per_engine'][name]['lower']['lower']['undivided_Robin_load_Eulerian'])
    G=21-1/(2-p['mu2']);tp=p['m2']*A-4*H*T;B=G*T/2-tp
    need(not zero(B),'LOWER_LAUNCH_DIVISOR')
    blocks=[]
    for v,s,r in ((arb(0),sc,R),(arb(1),arb(0),arb(0))):
        f=(s+3*(p['mu2']+4*k)*v-T*r/2)/B
        g=G*f/2+r/2-2*T*v
        blocks += [v,f,g]
    canonical=canonical[:8]+blocks
    y=canonical if name=='primary' else canonical[:4]+canonical[5:]
    need(all(zero(v) for v in m.constraints(y,p).values()),'INITIAL_CONSTRAINTS')
    need(zero(m.first_integral(y,p)),'INITIAL_BACKGROUND')
    return y,p,{'A1':pack(a1),'R2_lower':pack(R),'lower_divisor':pack(B),'D':binding['config']['D'],'binding':str(t10/'inputs/central_bindings.json')}

def run():
    need(sys.platform=='linux','LINUX_ONLY')
    from flint import ctx,fmpq
    ctx.prec=768;ctx.threads=1
    m=load('forced_primary_probe',ROOT/'primary.py')
    y,p,inputs=initial(m,'primary');start=time.monotonic();records=[]
    before=[pack(v) for v in y];h=fmpq(2,8192)
    for j in range(64):
        need(time.monotonic()-start<600,'PROBE_OPERATIONAL_CAP')
        y,cell=m.step(y,h,p)
        need(all(v.is_finite() for v in y+cell['box']),'FINITE_AUGMENTED_FLOW')
        constraints=m.constraints(cell['box'],p)
        need(all(zero(v) for v in constraints.values()),'WHOLE_CELL_CONSTRAINTS')
        need(zero(m.first_integral(cell['box'],p)),'WHOLE_CELL_BACKGROUND')
        records.append({'cell':j,'picard_iterations':cell['picard_iterations'],'endpoint':[pack(v) for v in y],
                        'constraints':{k:pack(v) for k,v in constraints.items()}})
    seconds=time.monotonic()-start
    result={'classification':'SHORT_AUGMENTED_PROBE_PASS','cells':64,'step':str(h),'seconds':seconds,
            'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'initial':before,'final':[pack(v) for v in y],
            'inputs':inputs,'records':records,'full_domain_or_coefficient_certified':False,
            'primary_linear_work_projection_seconds':seconds*(8192+1)/64,
            'projection_is_not_full_domain_admission':True}
    put('PROBE_RESULT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('initial','final','inputs','records')}),flush=True)
    return result

if __name__=='__main__':
    try:run()
    except BaseException as exc:
        put('PROBE_FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','error':repr(exc),'traceback':traceback.format_exc()});raise
