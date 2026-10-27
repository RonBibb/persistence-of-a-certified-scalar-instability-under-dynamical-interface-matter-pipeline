"""Bounded replay of authenticated engines to certify analytic first-mode size."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1';FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1';INV=BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json';DEADLINE=1793047195
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def main(lease,pin):
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    def pack(v):return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
    need(sha(INV/'TERMINAL.json')==pin,'INVERSE_PIN');it=read(INV/'TERMINAL.json');need(it['pass_status'],'INVERSE_PASS')
    inputs={str(INV/'TERMINAL.json'):pin}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:need(sha(INV/n)==it[k],'INVERSE_RECORD');inputs[str(INV/n)]=it[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(INV/'BINDING.json')[group].items():need(sha(p)==h,'INVERSE_CLOSURE');inputs[p]=h
    audit=INV/'audit/AUDIT_TERMINAL.json';need(sha(audit)=='d6dea65549d221cc69649b437b2f1b90cca5d3390f4696ee9e3bad37808d29ee','AUDIT_PIN');inputs[str(audit)]=sha(audit)
    at=read(audit);need(at['pass_status'],'AUDIT_PASS')
    for n,k in [('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')]:need(sha(INV/'audit'/n)==at[k],'AUDIT_RECORD');inputs[str(INV/'audit'/n)]=at[k]
    for n in ('run.py','wall.py','primary.py','independent.py'):need(inputs.get(str(QUAD/n))==sha(QUAD/n),'ENGINE_AUTHORITY')
    quad=load('analytic_seed_initial',QUAD/'run.py');quad.wall=load('analytic_seed_wall',QUAD/'wall.py')
    engines={n:load('analytic_seed_'+n,QUAD/(n+'.py')) for n in ('primary','independent')}
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,precision_bits=768,steps={'primary':'1/4096','independent':'1/8192'},time_cap_seconds=900))
    binding=sha(ROOT/'BINDING.json');arms={};started=time.monotonic()
    for name,eng in engines.items():
        y,p,D=quad.initial(eng,name);original=read(FRESH/('INITIAL_'+name+'.json'))
        need([pack(v) for v in y]==original['initial_native'] and {k:pack(v) for k,v in p.items()}==original['parameters'] and D==original['D'],'EXACT_INITIAL_IDENTITY')
        step=fmpq(original['step']);count=original['cells'];M=Q(0);pending=[];chunks=[];previous=None
        for i in range(count):
            need(time.time()<DEADLINE and time.monotonic()-started<870,'TIME_BOUND')
            before=[pack(v) for v in y];y,cell=eng.step(y,step,p);z=eng.physical(cell['box'])
            need(all(v.is_finite() for v in y+cell['box']),'FINITE')
            need(all(v.contains(0) for v in eng.constraints(cell['box'],p).values()) and eng.first_integral(cell['box'],p).contains(0),'WHOLE_CELL_CONSTRAINTS')
            local=max(Q(str(abs(v).upper().fmpq())) for v in z[5:8]);M=max(M,local)
            pending.append(dict(index=i,start_native=before,end_native=[pack(v) for v in y],box_native=[pack(v) for v in cell['box']],box_canonical=[pack(v) for v in z],mode_abs_upper=str(local),constraints_pass=True))
            if len(pending)==128 or i+1==count:
                filename=f'CHUNK_{name}_{i+1:06d}.json';put(filename,dict(engine=name,binding_sha256=binding,previous_sha256=previous,first=pending[0]['index'],last=i,records=pending));digest=sha(ROOT/filename)
                cp=f'CHECKPOINT_{name}_{i+1:06d}.json';put(cp,dict(engine=name,completed=i+1,total=count,binding_sha256=binding,chunk_sha256=digest,previous_sha256=previous,last_native=[pack(v) for v in y],mode_abs_upper=str(M),resume_supported=False))
                chunks.append(dict(file=filename,sha256=digest,checkpoint=cp,checkpoint_sha256=sha(ROOT/cp)));previous=digest;pending=[]
            if (i+1)%2048==0:print(name,i+1,'cells',round(time.monotonic()-started,1),flush=True)
        need((count-1)*Q(original['step'])<Q(D[1])<=count*Q(original['step']),'COMPLETE_DOMAIN')
        arms[name]=dict(cells=count,mode_real_abs_upper=str(M),chunks=chunks,final_native=[pack(v) for v in y]);put('ARM_'+name+'.json',arms[name])
    rho=Q(read(INV/'RESULT.json')['constants_exact']['rho']);need(104*rho<1,'SEED_COMPLEX_ABSORPTION')
    M=max(Q(a['mode_real_abs_upper']) for a in arms.values());mc=M/(1-104*rho);s=300*mc
    need(lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='SELECTED_NEUTRAL_FIRST_MODE_ANALYTIC_NORM_CERTIFIED',arms=arms,rho=str(rho),real_mode_bound=str(M),complex_mode_bound=str(mc),seed_norm=str(s),seed_norm_outward_integer=-((-s.numerator)//s.denominator),seconds=time.monotonic()-started,scope='Full radial validated replay plus analytic linear first-mode continuation; fixed selected mode and full parameters. No nonlinear source or convergence certificate yet.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')));print(json.dumps({k:v for k,v in result.items() if k!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+900<DEADLINE,'LINUX_PIN_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','TERMINAL.json','FAILURE.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('analytic_seed_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();sys.path.insert(0,str(lease.FLINT))
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('ANALYTIC_SEED_900_SECONDS')));signal.alarm(900)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
