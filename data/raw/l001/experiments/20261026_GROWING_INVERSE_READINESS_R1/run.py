"""Fresh same-lineage background archive and neutral inverse readiness.
Linux only; independent predecessor mismatch remains preserved.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,s):
    if not v:raise AssertionError(s)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def pack(v):need(v.is_finite(),'FINITE_EXPORT');return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def zero(v):return v.lower()<=0<=v.upper()
def main(lease):
    import flint
    flint.ctx.prec=768;flint.ctx.threads=1;fmpq=flint.fmpq
    parents={};pins={str(FROZEN):'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',str(PARENT/'production_TERMINAL.json'):'ffd7264e8bc8babbf511673c7a313e500f54746f67f1b0668069d3ad3cb727ec',str(PARENT/'audit/AUDIT_TERMINAL.json'):'61cfa897dec29277df1dc4783529a09cb4134eb5be13c8dc628945099c761282'}
    for p,h in pins.items():need(sha(p)==h,'PIN');parents[p]=h
    for p,h in read(FROZEN)['files'].items():need(sha(p)==h,'FROZEN_PARENT');parents[p]=h
    terminal=read(PARENT/'production_TERMINAL.json');need(terminal['pass'],'PARENT_PASS')
    for n,h in terminal['artifacts'].items():need(sha(PARENT/n)==h,'PARENT_ARTIFACT');parents[str(PARENT/n)]=h
    pb=read(PARENT/'production_BINDING.json')
    for p,h in pb['sources'].items():need(sha(p)==h,'PARENT_SOURCE');parents[p]=h
    a=read(PARENT/'audit/AUDIT_TERMINAL.json');need(a['pass'] and sha(PARENT/'audit/AUDIT_RESULT.json')==a['result_sha256'],'AUDIT');parents[str(PARENT/'audit/AUDIT_RESULT.json')]=a['result_sha256']
    closure=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/CLOSURE_MANIFEST.json'
    need(sha(closure)==pb['parent_closure_sha256'],'CLOSURE');parents[str(closure)]=sha(closure)
    for n,h in read(closure)['files'].items():p=closure.parent/n;need(sha(p)==h,'CLOSURE_FILE');parents[str(p)]=h
    quad=load('fresh_neutral_initial',PARENT/'run.py');quad.wall=load('fresh_neutral_wall',PARENT/'wall.py')
    engines={n:load('fresh_neutral_'+n,PARENT/(n+'.py')) for n in ('primary','independent')}
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP')
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='CONTRACT.json'}
    runtime=lease.observed()
    for p,h in runtime.items():need(parents.get(p)==h or sources.get(p)==h or (p==str(pylong) and h==sha(pylong)),'RUNTIME:'+p)
    put('BINDING.json',dict(sources=sources,parents=parents,runtime=runtime,precision_bits=768,orders=list(range(2,9)),predeclared_methods=['constant','inverse_warp_squared'],operator_convention="L f = -f''-A f'+V f; f=exp(-2W)y gives Atilde=A-4H, Vtilde=V+2Hprime-4H^2+2AH"))
    binding_hash=sha(ROOT/'BINDING.json');started=time.monotonic();arms={};unresolved=[]
    def bound(v,upper=False):need(v.is_finite(),'FINITE_BOUND');return Q(str(v.upper().fmpq() if upper else v.lower().fmpq()))
    for name,eng in engines.items():
        armstart=time.monotonic();y,p,D=quad.initial(eng,name);initial=y[:];canonical=eng.physical(y);nbg=5 if name=='primary' else 4
        prior=read(PARENT/('PRODUCTION_'+name+'.json'))
        need([pack(v) for v in canonical[:5]]==prior['walls']['lower']['state'][:5],'EXACT_CURRENT_INITIAL')
        need({k:pack(v) for k,v in p.items()}==prior['parameters'],'EXACT_CURRENT_PARAMETERS')
        need(D==prior['D'],'EXACT_CURRENT_DOMAIN')
        dlo,dhi=map(fmpq,D);step=fmpq(1,4096 if name=='primary' else 8192);count=(Q(str(dhi))/Q(str(step))).__ceil__()
        identity={'engine':name,'initial_native':[pack(v) for v in initial],'initial_background':[pack(v) for v in canonical[:5]],'parameters':{k:pack(v) for k,v in p.items()},'D':D,'step':str(step),'cells':count,'background_native_dimension':nbg}
        put('INITIAL_'+name+'.json',identity);identity_hash=sha(ROOT/('INITIAL_'+name+'.json'))
        low={method:{n:None for n in range(2,9)} for method in ('constant','inverse_warp_squared')};chunks=[];pending=[];previous=None;maxpic=0
        m,k,r,h=[p[q] for q in ('m2','k','rate','h')]
        need(bound(r-h)>0,'POSITIVE_GROWING_RATE')
        for i in range(count):
            need(time.time()<DEADLINE and time.monotonic()-armstart<600 and time.monotonic()-started<1180,'TIME_BOUND')
            startbg=[pack(v) for v in y[:nbg]];y,cell=eng.step(y,step,p);z=eng.physical(cell['box'])
            need(all(v.is_finite() for v in y+cell['box']),'FINITE_CELL')
            need(all(zero(v) for v in eng.constraints(cell['box'],p).values()),'WHOLE_CELL_CONSTRAINTS')
            need(zero(eng.first_integral(cell['box'],p)) and z[4].lower()>0,'BACKGROUND_WARP')
            maxpic=max(maxpic,cell['picard_iterations']);W,H,Phi,T,E=z[:5]
            Tp=m*Phi-4*H*T;B=12*H*T-4*m*Phi;e2=E*E;tt=2*T*T
            for n in range(2,9):
                temporal=n*r*(n*r+3*h)*e2;J=3*temporal-12*k*e2;dn=tt+J
                need(bound(J)>0 and bound(dn)>0,'POSITIVE_DENOMINATORS')
                V=m+temporal+tt+B*Tp/dn;drift=4*H+B*T/dn
                beta=(21-1/(2+temporal))*dn/(2*J)-abs(2*T*Tp)/J
                Hp=-T*T/3-k*e2
                transformedV=V+2*Hp-4*H*H+2*drift*H
                transformedA=drift-4*H
                transformedBeta=beta-2*abs(H)
                for method,v,a,beta0 in (('constant',V,drift,beta),('inverse_warp_squared',transformedV,transformedA,transformedBeta)):
                    row=(bound(v),bound(abs(v),True),bound(abs(a),True),bound(beta0));old=low[method][n]
                    low[method][n]=row if old is None else (min(old[0],row[0]),max(old[1],row[1]),max(old[2],row[2]),min(old[3],row[3]))
            pending.append(dict(index=i,s=str(i*step),step=str(step),start_native_background=startbg,end_native_background=[pack(v) for v in y[:nbg]],box_native_background=[pack(v) for v in cell['box'][:nbg]],box_canonical_background=[pack(v) for v in z[:5]],whole_cell_constraints_contain_zero=True,background_first_integral_contains_zero=True,picard_iterations=cell['picard_iterations']))
            if len(pending)==128 or i+1==count:
                filename='CHUNK_'+name+'_'+str(i+1).zfill(6)+'.json'
                chunk=dict(engine=name,binding_sha256=binding_hash,initial_identity_sha256=identity_hash,previous_sha256=previous,first=pending[0]['index'],last=i,records=pending)
                put(filename,chunk);digest=sha(ROOT/filename)
                checkpoint='CHECKPOINT_'+name+'_'+str(i+1).zfill(6)+'.json'
                put(checkpoint,dict(engine=name,binding_sha256=binding_hash,initial_identity_sha256=identity_hash,chunk_sha256=digest,previous_chunk_sha256=previous,completed=i+1,total=count,last_native_background=[pack(v) for v in y[:nbg]],seconds=time.monotonic()-armstart,resume_supported=False))
                chunks.append(dict(file=filename,sha256=digest,checkpoint=checkpoint,checkpoint_sha256=sha(ROOT/checkpoint),first=pending[0]['index'],last=i));pending=[];previous=digest
                if (i+1)%1024==0 or i+1==count:print(name,i+1,'/',count,round(time.monotonic()-armstart,1),flush=True)
        rows={}
        for method,orders in low.items():
            rows[method]={}
            for n,v in orders.items():
                admissible=v[0]>0 and v[3]>0
                if not admissible:unresolved.append(name+':'+method+':n='+str(n))
                rows[method][str(n)]={'V_min':str(v[0]),'V_abs_max':str(v[1]),'drift_abs_max':str(v[2]),'beta_min':str(v[3]),'barrier_admissible':admissible}
        arms[name]=dict(cells=count,seconds=time.monotonic()-armstart,maxpic=maxpic,step=str(step),D=D,initial_identity_sha256=identity_hash,final_native_background=[pack(v) for v in y[:nbg]],chunks=chunks,methods=rows,full_rate_interval=pack(r),exact_current_background_identity=True)
        put('ARM_'+name+'.json',arms[name])
    need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(all(sha(p)==h for p,h in dict(parents,**sources).items()),'SOURCE_PARENT_UNCHANGED')
    method_ready={method:all(arms[name]['methods'][method][str(n)]['barrier_admissible'] for name in arms for n in range(2,9)) for method in ('constant','inverse_warp_squared')}
    out={'pass':True,'classification':'NEUTRAL_LOW_ORDER_BARRIER_READY' if any(method_ready.values()) else 'NEUTRAL_BARRIER_METHODS_INCONCLUSIVE','method_admissible':method_ready,'unresolved_orders':unresolved,'arms':{n:{k:v for k,v in a.items() if k!='chunks'} for n,a in arms.items()},'seconds':time.monotonic()-started,'scope':'Fresh authenticated same-lineage validated background replay and n=2..8 real-axis sufficient positivity tests for two predeclared barriers, constant and inverse warp squared. Both retained separately. Nonpositive bounds imply method inconclusiveness, not resonance or nonexistence. No all-order inverse, complex-collar bound or nonlinear-family convergence certificate.'}
    put('RESULT.json',out)
    put('TERMINAL.json',{'pass':True,'binding_sha256':binding_hash,'result_sha256':sha(ROOT/'RESULT.json'),'artifacts':{p.name:sha(p) for p in ROOT.glob('*.json') if p.name!='START.json'}})
    print(json.dumps({k:v for k,v in out.items() if k!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+1200<DEADLINE,'LINUX_COMPLETE_BOUND_FITS')
        need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN_PIN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE_PIN')
        lease=load('fresh_neutral_lease',lp);lease.ROOT=ROOT
        cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('FRESH_INVERSE_1200_SECONDS')));signal.alarm(min(1200,int(DEADLINE-time.time())))
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()))
        sys.path.insert(0,str(lease.FLINT));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
