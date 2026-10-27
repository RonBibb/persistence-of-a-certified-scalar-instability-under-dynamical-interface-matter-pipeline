"""Read-only, source-bound low-order archive feasibility inventory; no ODE solve."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent; BASE=ROOT.parent
GOAL=BASE/'20261026T183955Z_CONVERGENCE_TWO_HOUR_GOAL'
SEED=BASE/'20261026_NEUTRAL_ANALYTIC_SEED'
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
CUBIC=BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'
def read(p): return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        while b:=f.read(1024*1024): h.update(b)
    return h.hexdigest()
def need(v,n):
    if not v: raise AssertionError(n)
def put(n,v):
    p=ROOT/n; t=ROOT/(n+'.tmp')
    with t.open('x') as f: json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(t,0o444);os.link(t,p);t.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
def intervals(v,n):
    need(len(v)==n,'STATE_DIMENSION')
    for x in v:
        a,b=map(Q,x['exact_bounds']);need(a<=b,'ORDERED_INTERVAL')
def main(lease):
    started=time.monotonic(); old=GOAL/'final_verification'
    need(sha(old/'TERMINAL.json')=='d69e87b371131bba179dd35ee26435e75bc26c3bd6b8502373b6873401551950','CLOSURE_PIN')
    t=read(old/'TERMINAL.json');need(t['pass_status'],'CLOSURE_PASS')
    inputs={str(old/'TERMINAL.json'):sha(old/'TERMINAL.json')}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:
        need(sha(old/n)==t[k],'CLOSURE_RECORD');inputs[str(old/n)]=t[k]
    inputs.update(read(old/'BINDING.json')['inputs'])
    inputs.update({str(GOAL/n):h for n,h in read(old/'BINDING.json')['documents'].items()})
    for p,h in inputs.items():need(sha(p)==h,'INPUT:'+p)
    sources={str(ROOT/n):sha(ROOT/n) for n in ('check.py','CONTRACT.md')}
    need(len(str(10**20000))==20001,'WARMUP')
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'UNBOUND_RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,scope='Structural archive inventory, not a new numerical solution'))
    seed=read(SEED/'RESULT.json');seedbinding=sha(SEED/'BINDING.json');arms={}
    for name in ('primary','independent'):
        arm=seed['arms'][name];expected=0;prev=None;previous_state=None;native=14 if name=='primary' else 13
        for row in arm['chunks']:
            need(sha(SEED/row['file'])==row['sha256'],'CHUNK_HASH')
            chunk=read(SEED/row['file']);need(chunk['engine']==name and chunk['binding_sha256']==seedbinding and chunk['previous_sha256']==prev,'CHUNK_BINDING')
            need(chunk['first']==expected,'CHUNK_START')
            for rec in chunk['records']:
                need(rec['index']==expected and rec['constraints_pass'],'CONTIGUOUS_CELL')
                intervals(rec['start_native'],native);intervals(rec['end_native'],native)
                intervals(rec['box_native'],native);intervals(rec['box_canonical'],14)
                if previous_state is not None:need(rec['start_native']==previous_state,'STATE_CHAIN')
                previous_state=rec['end_native']
                expected+=1
            need(chunk['last']==expected-1,'CHUNK_END')
            cp=read(SEED/row['checkpoint']);need(sha(SEED/row['checkpoint'])==row['checkpoint_sha256'],'CHECKPOINT_HASH')
            need(cp['completed']==expected and cp['binding_sha256']==seedbinding and cp['chunk_sha256']==row['sha256'],'CHECKPOINT_BINDING')
            need(cp['last_native']==previous_state and cp['previous_sha256']==prev,'CHECKPOINT_STATE_CHAIN')
            prev=row['sha256']
        need(expected==arm['cells'],'COMPLETE_SEED')
        need(arm['final_native']==previous_state,'FINAL_STATE')
        qp=read(QUAD/('PRODUCTION_'+name+'.json'));cu=read(CUBIC/('PRODUCTION_'+name+'.json'))
        need(qp['pass'] and cu['pass'] and qp['cells']==cu['cells']==expected,'LOW_ORDER_COUNTS')
        step=Q(1,4096 if name=='primary' else 8192);dlo,dhi=map(Q,qp['D'])
        need((expected-1)*step<dhi<=expected*step and qp['D']==cu['D'],'DOMAIN')
        intervals([qp['A2'],cu['A3']],2)
        for prod in (qp,cu):
            need(len(prod['budgets'])==expected,'BUDGET_COUNT')
            for i,row in enumerate(prod['budgets']):
                need(row['index']==i and Q(row['s'])==i*step and Q(row['step'])==step,'BUDGET_GRID')
                intervals(list(row['budgets'].values()),len(row['budgets']))
        keys=set(cu['budgets'][0]['budgets'])
        need(all(set(row['budgets'])==keys for row in cu['budgets']),'CONSISTENT_CUBIC_BUDGET_SCHEMA')
        need(not any(k in keys for k in ('f3','g3','f30','g30','f31','g31','f3H','g3H')),'UNEXPECTED_SCALAR_PROFILE_REQUIRES_REVIEW')
        need(not any('box_canonical' in row or 'state' in row for row in cu['budgets']),'UNEXPECTED_FULL_PROFILE_REQUIRES_REVIEW')
        progress=sorted(CUBIC.glob('PROGRESS_'+name+'_*.json'))
        need(all(read(p).get('resumable') is False and 'state' not in read(p) for p in progress),'PROGRESS_SCHEMA')
        arms[name]=dict(cells=expected,seed_chunks=len(arm['chunks']),seed_canonical_state_size=14,seed_native_state_size=native,quadratic_profile_channels_available=True,quadratic_A2_authenticated=True,cubic_integral_budget_keys=sorted(keys),cubic_full_state_boxes_available=False,cubic_scalar_profile_available=False,cubic_progress_records=len(progress),cubic_progress_resumable=False,quadratic_original_seconds=qp['seconds'],cubic_original_seconds=cu['seconds'])
    need(lease.observed()==runtime,'RUNTIME_DRIFT')
    for p,h in dict(inputs,**sources).items():need(sha(p)==h,'POST_INPUT:'+p)
    result=dict(pass_status=True,classification='QUADRATIC_PROFILE_REUSABLE_CUBIC_PROFILE_EXPORT_REQUIRED',arms=arms,all_required_profile_data_available=False,finite_amplitude_certificate_ready=False,ode_solves_launched=0,source_files_verified=len(inputs),seconds=time.monotonic()-started,remaining_mathematical_gate='Verified coupled inverse and nonlinear correction in a closed residual norm; archive completeness alone would not satisfy this gate.',scope='Existing local convergence theorem unchanged. This records data readiness, not a failure of the nonlinear family.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux','LINUX_ONLY');need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','TERMINAL.json','FAILURE.json')),'NO_RESTART')
        frozen=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
        need(sha(frozen)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(frozen)['files'][str(lp)],'LEASE_PIN')
        s=importlib.util.spec_from_file_location('profile_inventory_lease',lp);lease=importlib.util.module_from_spec(s);sys.modules[s.name]=lease;s.loader.exec_module(lease);lease.ROOT=ROOT
        cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('INVENTORY_300_SECONDS')));signal.alarm(300)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
