"""Neutral n=2..8 maximum-principle readiness; authenticated background only.
Linux only. No ODE solve, no all-order certificate, no resonance inference.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
FLOW=BASE/'20261026T033400Z_CUBIC_FULL_FLOW';QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
DEADLINE=1793039120
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    p=ROOT/n;t=ROOT/(n+'.tmp')
    with t.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def need(v,n):
    if not v:raise AssertionError(n)
def exact_bounds(v):return tuple(map(Q,v['exact_bounds']))
def main(lease):
    from flint import arb,fmpq,ctx
    ctx.prec=768;ctx.threads=1
    def ball(v):
        a,b=exact_bounds(v);need(a<=b,'BOUNDS');return arb(fmpq(str((a+b)/2)),fmpq(str((b-a)/2)))
    def lo(v):need(v.is_finite(),'FINITE');return Q(str(v.lower().fmpq()))
    def hi(v):need(v.is_finite(),'FINITE');return Q(str(v.upper().fmpq()))
    def endpoint(v):return {'exact_bounds':[str(lo(v)),str(hi(v))]}
    pins={str(FLOW/'FROZEN.json'):'625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e',str(QUAD/'production_TERMINAL.json'):'ffd7264e8bc8babbf511673c7a313e500f54746f67f1b0668069d3ad3cb727ec',str(QUAD/'audit/AUDIT_TERMINAL.json'):'61cfa897dec29277df1dc4783529a09cb4134eb5be13c8dc628945099c761282'}
    pins.update({str(FLOW/'production_TERMINAL.json'):'1f51293d75c7ff5eb9c4179e9884c1fb7c70b3892ccc2473cb629e5a1a9059fe',str(FLOW/'audit_TERMINAL.json'):'ffc458be1fb24c08c2564e257300925526d083cca8ba4d631195ac92ddfaf40c'})
    for p,h in pins.items():need(sha(p)==h,'PIN:'+p)
    inputs=dict(pins);inputs[str(Path(__file__))]=sha(__file__)
    for p,h in read(FLOW/'FROZEN.json')['files'].items():need(sha(p)==h,'FROZEN_INPUT');inputs[p]=h
    for root,tn in ((FLOW,'production_TERMINAL.json'),(FLOW,'audit_TERMINAL.json'),(QUAD,'production_TERMINAL.json')):
        t=read(root/tn);need(t['pass'],'PARENT_PASS');inputs[str(root/tn)]=sha(root/tn)
        for n,h in t['artifacts'].items():need(sha(root/n)==h,'PARENT_ARTIFACT');inputs[str(root/n)]=h
    qt=read(QUAD/'audit/AUDIT_TERMINAL.json');need(qt['pass'] and sha(QUAD/'audit/AUDIT_RESULT.json')==qt['result_sha256'],'QUAD_AUDIT')
    inputs[str(QUAD/'audit/AUDIT_RESULT.json')]=qt['result_sha256']
    qb=read(QUAD/'production_BINDING.json')
    for p,h in qb['sources'].items():need(sha(p)==h,'QUAD_SOURCE');inputs[p]=h
    parent=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION';manifest=parent/'CLOSURE_MANIFEST.json'
    need(sha(manifest)==qb['parent_closure_sha256'],'CLOSURE');inputs[str(manifest)]=sha(manifest)
    for n,h in read(manifest)['files'].items():need(sha(parent/n)==h,'CLOSURE_FILE');inputs[str(parent/n)]=h
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP')
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or (p==str(pylong) and h==sha(pylong)),'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,runtime=runtime,precision_bits=768,threads=1,orders=list(range(2,9))))
    started=time.monotonic();arms={};unresolved=[]
    for name,dimension in (('primary',20),('independent',19)):
        flow=read(FLOW/('FLOW_'+name+'.json'));new=read(QUAD/('PRODUCTION_'+name+'.json'))
        need(flow['pass'] and new['pass'],'ARMS_PASS')
        # The autonomous background is determined by this complete initial
        # state and m2,k. Require EXACT enclosure equality, never mere overlap.
        nbg=5 if name=='primary' else 4
        for j in range(nbg):need(exact_bounds(flow['initial'][j])==exact_bounds(new['walls']['lower']['state'][j]),'EXACT_BACKGROUND_INITIAL_'+name+'_'+str(j))
        for k in ('m2','k'):need(exact_bounds(flow['parameters'][k])==exact_bounds(new['parameters'][k]),'EXACT_BACKGROUND_PARAMETER_'+name+'_'+k)
        need(flow['D']==new['D'],'EXACT_DOMAIN')
        need(exact_bounds(flow['initial'][0])==(0,0),'W_ORIGIN')
        p=new['parameters'];m,k,r,h=map(ball,(p['m2'],p['k'],p['rate'],p['h']))
        need(lo(r-h)>0 and lo(11*h/10-r)>0,'GROWING_RATE')
        need(lo(h*h-k)<=0<=hi(h*h-k),'H_K_RELATION')
        low={n:None for n in range(2,9)};previous=None;last=flow['initial'];index=0
        ph=hashlib.sha256(json.dumps(flow['parameters'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        need(ph==flow['parameters_sha256'],'PARAMETER_HASH')
        step=Q(flow['step']);need(step==Q(1,4096 if name=='primary' else 8192),'STEP')
        for entry in flow['chunks']:
            need(time.time()<DEADLINE and time.monotonic()-started<880,'TIME_BOUND')
            path=FLOW/entry['file'];cp_path=FLOW/entry['checkpoint']
            need(path.resolve().is_relative_to(FLOW.resolve()) and cp_path.resolve().is_relative_to(FLOW.resolve()),'PATH_SCOPE')
            need(sha(path)==entry['sha256'] and sha(cp_path)==entry['checkpoint_sha256'],'CHUNK_HASH')
            inputs[str(path)]=entry['sha256'];inputs[str(cp_path)]=entry['checkpoint_sha256']
            chunk=read(path);cp=read(cp_path)
            need(chunk['engine']==name and chunk['binding_sha256']==pins[str(FLOW/'FROZEN.json')] and chunk['parameters_sha256']==ph and chunk['previous_sha256']==previous,'CHUNK_BINDING')
            need(chunk['first']==entry['first']==index and chunk['last']==entry['last'],'CHUNK_ORDER')
            for cell in chunk['records']:
                need(cell['index']==index and cell['start']==last,'CELL_CHAIN');last=cell['end'];box=cell['box'];need(len(box)==dimension,'DIMENSION')
                W,H,P,T=map(ball,box[:4]);E=ball(box[4]) if name=='primary' else (-W).exp();need(lo(E)>0,'WARP')
                Tp=m*P-4*H*T;B=12*H*T-4*m*P;e2=E*E;tt=2*T*T
                for n in low:
                    temporal=n*r*(n*r+3*h)*e2;J=3*temporal-12*k*e2;D=tt+J
                    need(lo(J)>0 and lo(D)>0,'REGULAR_DENOMINATORS')
                    V=m+temporal+tt+B*Tp/D;drift=4*H+B*T/D
                    beta=(21-1/(2+temporal))*D/(2*J)-abs(2*T*Tp)/J
                    row=(lo(V),hi(abs(V)),hi(abs(drift)),lo(beta));old=low[n]
                    low[n]=row if old is None else (min(old[0],row[0]),max(old[1],row[1]),max(old[2],row[2]),min(old[3],row[3]))
                index+=1
            need(index==entry['last']+1 and cp['completed']==index and cp['total']==flow['cells'] and cp['state']==last,'CHECKPOINT_STATE')
            need(cp['engine']==name and cp['binding_sha256']==pins[str(FLOW/'FROZEN.json')] and cp['parameters_sha256']==ph and cp['chunk_sha256']==entry['sha256'] and cp['resume_supported'] is False,'CHECKPOINT_BINDING')
            previous=entry['sha256']
            if index%1024==0:
                put('PROGRESS_'+name+'_'+str(index).zfill(6)+'.json',dict(completed=index,total=flow['cells'],seconds=time.monotonic()-started,resumable=False))
                print(name,index,'cells',flush=True)
        need(index==flow['cells'] and last==flow['final'],'COMPLETE_CHAIN')
        need((index-1)*step<Q(flow['D'][1])<=index*step,'COMPLETE_DOMAIN_COVER')
        rows={}
        for n,v in low.items():
            positive=v[0]>0 and v[3]>0
            if not positive:unresolved.append(name+':n='+str(n))
            rows[str(n)]={'V_min':str(v[0]),'V_abs_max':str(v[1]),'drift_abs_max':str(v[2]),'beta_min':str(v[3]),'constant_barrier_admissible':positive}
        arms[name]=dict(cells=index,exact_same_background=True,full_rate_interval=p['rate'],orders=rows)
        put('ARM_'+name+'.json',arms[name])
    need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(all(sha(p)==h for p,h in inputs.items()),'INPUTS_UNCHANGED')
    put('INPUT_MANIFEST.json',inputs)
    out={'pass':True,'classification':'NEUTRAL_LOW_ORDER_CONSTANT_BARRIER_READY' if not unresolved else 'NEUTRAL_CONSTANT_BARRIER_METHOD_INCONCLUSIVE','method_admissible':not unresolved,'unresolved_orders':unresolved,'arms':arms,'seconds':time.monotonic()-started,'new_ode_solves':0,'scope':'Only n=2..8 real-axis potential and conservative Robin positivity on authenticated same-background archives. Nonpositive positivity bound is method inconclusiveness, not resonance or no-solution. No all-order inverse constant, complex collar or nonlinear convergence certificate.'}
    put('RESULT.json',out);put('TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'RESULT.json'),'binding_sha256':sha(ROOT/'BINDING.json'),'input_manifest_sha256':sha(ROOT/'INPUT_MANIFEST.json'),'source_sha256':sha(__file__)})
    print(json.dumps({k:v for k,v in out.items() if k!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FLOW/'FROZEN.json')=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FLOW/'FROZEN.json')['files'][str(lp)]==sha(lp),'LEASE_PIN')
        s=importlib.util.spec_from_file_location('neutral_readiness_lease',lp);lease=importlib.util.module_from_spec(s);sys.modules[s.name]=lease;s.loader.exec_module(lease);lease.ROOT=ROOT
        cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('READINESS_900_SECONDS')));signal.alarm(min(900,int(DEADLINE-time.time())))
        put('START.json',dict(cpu=cpu,occupied=occupied,pid=os.getpid()))
        sys.path.insert(0,str(lease.FLINT));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
