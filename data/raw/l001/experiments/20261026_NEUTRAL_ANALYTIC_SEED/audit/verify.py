"""Independent exact saved-record seed audit; no producer import or ODE."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib, importlib.util, json, os, signal, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent; PACKET=ROOT.parent; BASE=PACKET.parent
FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1'
INV=BASE/'20261026_NEUTRAL_ANALYTIC_INVERSE'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
PIN='e89622e7c04b37bc68f529f684c823af464c8ceb6e86c5629b350d49a8f0df52'
DEADLINE=1793047195
def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v: raise AssertionError(n)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); sys.modules[n]=m; s.loader.exec_module(m); return m
def put(n,v):
    p=ROOT/n; tmp=ROOT/(n+'.tmp')
    with tmp.open('x') as f: json.dump(v,f,indent=2); f.flush(); os.fsync(f.fileno())
    os.chmod(tmp,0o444); os.link(tmp,p); tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
def interval(v):
    a,b=map(Q,v['exact_bounds']); need(a<=b,'ORDERED_BOUNDS'); return a,b
def absolute(v):
    a,b=interval(v); return max(abs(a),abs(b))

def main(lease):
    start=time.monotonic(); countchecks=0
    def gate(v,n):
        nonlocal countchecks
        need(v,n); countchecks+=1
    gate(sha(PACKET/'TERMINAL.json')==PIN,'PRODUCTION_PIN')
    t=read(PACKET/'TERMINAL.json'); gate(t['pass_status'],'PRODUCTION_PASS')
    inputs={str(PACKET/'TERMINAL.json'):PIN,str(Path(__file__)):sha(__file__)}
    for name,key in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('run.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
        gate(sha(PACKET/name)==t[key],'PRODUCTION_RECORD'); inputs[str(PACKET/name)]=t[key]
    binding=read(PACKET/'BINDING.json')
    for group in ('inputs','sources','runtime'):
        for p,h in binding[group].items(): gate(sha(p)==h,'PARENT_CLOSURE'); inputs[p]=h
    result=read(PACKET/'RESULT.json')
    for name,arm in result['arms'].items():
        path=PACKET/('ARM_'+name+'.json'); gate(read(path)==arm,'ARM_RECORD'); inputs[str(path)]=sha(path)
        for entry in arm['chunks']:
            for key,hashkey in [('file','sha256'),('checkpoint','checkpoint_sha256')]:
                path=PACKET/entry[key]; gate(path.resolve().is_relative_to(PACKET.resolve()),'PATH_SCOPE')
                gate(sha(path)==entry[hashkey],'ARTIFACT_HASH'); inputs[str(path)]=entry[hashkey]
    pylong=Path('/usr/lib/python3.12/_pylong.py'); gate(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG')
    gate(len(str(10**20000))==20001,'WARMUP'); inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items(): gate(inputs.get(p)==h,'RUNTIME_AUTHORITY:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=PIN))
    reports={}
    for name in ('primary','independent'):
        arm=result['arms'][name]; ini=read(FRESH/('INITIAL_'+name+'.json'))
        gate(inputs.get(str(FRESH/('INITIAL_'+name+'.json')))==sha(FRESH/('INITIAL_'+name+'.json')),'INITIAL_AUTHORITY')
        last=ini['initial_native']; previous=None; count=0; maximum=Q(0)
        gate(len(last)==(14 if name=='primary' else 13),'STATE_DIMENSION')
        for entry in arm['chunks']:
            gate(time.monotonic()-start<550 and time.time()<DEADLINE,'RESOURCE_BOUND')
            chunk=read(PACKET/entry['file']); cp=read(PACKET/entry['checkpoint'])
            gate(chunk['engine']==name and chunk['binding_sha256']==t['binding_sha256'],'CHUNK_BINDING')
            gate(chunk['previous_sha256']==previous and chunk['first']==count,'CHUNK_CHAIN')
            gate(1<=len(chunk['records'])<=128,'CHECKPOINT_SIZE')
            for cell in chunk['records']:
                gate(cell['index']==count and cell['start_native']==last,'CELL_CHAIN')
                native=cell['box_native']; canonical=cell['box_canonical']
                gate(len(native)==len(last) and len(canonical)==14,'BOX_DIMENSIONS')
                gate(canonical==native if name=='primary' else canonical[:4]+canonical[5:]==native,'PHYSICAL_NONEXP_MAP')
                for box,left,right in zip(native,cell['start_native'],cell['end_native']):
                    lo,hi=interval(box); llo,lhi=interval(left); rlo,rhi=interval(right)
                    gate(lo<=llo<=lhi<=hi and lo<=rlo<=rhi<=hi,'WHOLE_CELL_ENDPOINT_CONTAINMENT')
                gate(cell['constraints_pass'],'INHERITED_CONSTRAINT_ADMISSION')
                H,Phi,T,E=canonical[1:5]
                gate(absolute(H)<=2 and absolute(Phi)<=1 and absolute(T)<=1 and Q(1,2)<=interval(E)[0]<=interval(E)[1]<=16,'BACKGROUND_BROAD_ENCLOSURE')
                exact=max(map(absolute,canonical[5:8])); recorded=Q(cell['mode_abs_upper'])
                gate(recorded>=exact,'MODE_MAXIMUM_OUTWARD'); maximum=max(maximum,recorded)
                last=cell['end_native']; count+=1
            gate(chunk['last']==count-1 and cp['completed']==count and cp['total']==ini['cells'],'CHUNK_END')
            gate(cp['binding_sha256']==t['binding_sha256'] and cp['chunk_sha256']==entry['sha256'] and cp['previous_sha256']==previous,'CHECKPOINT_BINDING')
            gate(cp['last_native']==last and Q(cp['mode_abs_upper'])==maximum and cp['resume_supported'] is False,'CHECKPOINT_STATE_AND_BOUND')
            previous=entry['sha256']
        gate(count==arm['cells']==ini['cells'] and last==arm['final_native'],'COMPLETE_CHAIN')
        step=Q(ini['step']); dlo,dhi=map(Q,ini['D'])
        gate(0<dlo<=dhi and (count-1)*step<dhi<=count*step,'COMPLETE_DOMAIN')
        gate(Q(arm['mode_real_abs_upper'])==maximum,'ARM_MAXIMUM')
        reports[name]=dict(cells=count,real_mode_bound=str(maximum))
        print('seed audit',name,count,round(time.monotonic()-start,2),flush=True)
    rho=Q(read(INV/'RESULT.json')['constants_exact']['rho'])
    # Independent matrix and differentiated-momentum bound from broad box.
    H,T,Phi,E=Q(3),Q(2),Q(2),Q(17)
    mu=Q(1,32)*(Q(1,32)+3*Q(1,32))
    B=12*H*T+4*Phi
    rows=(2*H+T/3,Q(1),4*H+1+mu*E**2+2*T**2+B)
    gate(max(rows)<=104,'FIRST_MODE_MATRIX_104')
    gate(T*T/3+E*E/1024<=2 and Phi+4*H*T<=26,'BACKGROUND_DERIVATIVES')
    pfirst=2*H+T/3
    psecond=2*2+2*H*pfirst+Q(26,3)+T/3
    gate(pfirst<=7 and psecond<56,'MODE_DERIVATIVES')
    gate(1+7+56==64 and 2*64==128 and 1+1+104==106,'JET_CONSTANTS')
    gate(64+128+106+1<=300,'AGGREGATE_WITH_TWO_OSCILLATORS')
    gate(104*rho<1,'COMPLEX_ABSORPTION')
    M=max(Q(a['real_mode_bound']) for a in reports.values()); Mc=M/(1-104*rho); seed=300*Mc
    gate(Q(result['rho'])==rho and Q(result['real_mode_bound'])==M and Q(result['complex_mode_bound'])==Mc and Q(result['seed_norm'])==seed,'ANALYTIC_BOUND_REPLAY')
    rounded=-((-seed.numerator)//seed.denominator); gate(result['seed_norm_outward_integer']==rounded,'OUTWARD_SEED')
    gate(lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'BINDING_UNCHANGED')
    output=dict(pass_status=True,classification='INDEPENDENT_ANALYTIC_SEED_SAVED_RECORD_AUDIT_PASS',checks=countchecks,arms=reports,seed_norm=str(seed),seed_norm_outward_integer=rounded,production_terminal_sha256=PIN,seconds=time.monotonic()-start,scope='Every saved cell, native/canonical mode mapping, endpoint containment, immutable checkpoint chain and outward mode maximum; independent rational analytic seed constants. Validated tube existence and selected spectral mode inherited. No ODE rerun or nonlinear convergence claim.')
    put('AUDIT_RESULT.json',output); put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps({k:v for k,v in output.items() if k!='seed_norm'}),flush=True)

if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py'; need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('analytic_seed_audit_lease',lp); lease.ROOT=ROOT; cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('SEED_AUDIT_600_SECONDS'))); signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time())); main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc())); raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
