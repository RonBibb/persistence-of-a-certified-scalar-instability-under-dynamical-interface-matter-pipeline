"""Exact rational audit of compatible scalar-to-metric response constants."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
FRESH=BASE/'20261026_GROWING_INVERSE_READINESS_R1';INV=BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE'
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1';FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
DEADLINE=1793039120
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
    need(sha(PACKET/'TERMINAL.json')==pin,'TERMINAL_PIN');term=read(PACKET/'TERMINAL.json');need(term['pass'],'PASS')
    inputs={str(PACKET/'TERMINAL.json'):pin,str(Path(__file__)):sha(__file__)}
    for n,key in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')):
        need(sha(PACKET/n)==term[key],'PACKET_HASH');inputs[str(PACKET/n)]=term[key]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PACKET/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_PIN');inputs[p]=h
    ip=INV/'audit/AUDIT_TERMINAL.json';need(sha(ip)=='970f11cb9734c3dfe725788de8957a4b5ca0fced0727ec1ae6a4f8da14907c35','INVERSE_AUDIT')
    need(read(ip)['pass_status'] and sha(INV/'audit/AUDIT_RESULT.json')==read(ip)['result_sha256'],'INVERSE_AUDIT_RESULT')
    utility=QUAD/'audit/verify.py';need(sha(utility)==read(QUAD/'audit/AUDIT_TERMINAL.json')['source_sha256'],'UTILITY');inputs[str(utility)]=sha(utility)
    util=load('metric_exact_intervals',utility);I,iv=util.I,util.iv
    def ab(v):return max(abs(v.lo),abs(v.hi))
    def sq(v):return I(0 if v.zero() else min(v.lo*v.lo,v.hi*v.hi),max(v.lo*v.lo,v.hi*v.hi))
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h,'RUNTIME:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=pin))
    result=read(PACKET/'RESULT.json');inv=read(INV/'RESULT.json');checks=0;arms={};started=time.monotonic()
    def gate(v,label):
        nonlocal checks
        need(v,label);checks+=1
    gate(all(result['exact_controls'].values()) and len(result['exact_controls'])==5,'INHERITED_POLYNOMIAL_CONTROLS')
    for name in ('primary','independent'):
        rec=result['arms'][name];a=read(FRESH/('ARM_'+name+'.json'));ini=read(FRESH/('INITIAL_'+name+'.json'))
        pars={q:iv(v) for q,v in ini['parameters'].items()};m,k=pars['m2'],pars['k'];count=0;emin=Q(rec['E2_min']);rmin=Q(rec['r_min']);ext={q:Q(v) for q,v in rec['background_extrema'].items()}
        gate(0<rmin<=pars['rate'].lo and emin>0,'RATE_WARP_LOWER')
        for entry in a['chunks']:
            gate(time.time()<DEADLINE and time.monotonic()-started<550,'TIME_BOUND');p=FRESH/entry['file'];gate(sha(p)==entry['sha256'],'CHUNK_HASH')
            for row in read(p)['records']:
                W,H,Phi,T,E=map(iv,row['box_canonical_background']);e=sq(E);Hp=-sq(T)/3-k*e;Tp=m*Phi-4*H*T;B=12*H*T-4*m*Phi
                gate(row['index']==count and e.lo>=emin,'CELL_INDEX_E2')
                gate(all(ext[q]>=ab(v) for q,v in dict(H0=H,Hp0=Hp,T0=T,Tp0=Tp,B0=B).items()),'CELL_EXTREMA')
                count+=1
            if count%4096==0:print(name,count,round(time.monotonic()-started,1),flush=True)
        gate(count==rec['cells']==a['cells'],'CELL_INVENTORY')
        H,Hp,T,Tp,B=[ext[q] for q in ('H0','Hp0','T0','Tp0','B0')];d=3*rmin*rmin*emin
        Cs=max(Q(1),B/(4*d)+T/d,Q(1,2)+T*T/(4*d));Cf=Q(inv['arms'][name]['C_f']);Cfnew=Cf*Cs
        P0=max(Q(1),T/2+Tp/4)/d;P1=H*P0+T/6+1;P2=Hp*P0/2+H*P1+Tp/12+T/6+1;Cp=P0+P1+P2;Cm=Cp*(1+Cfnew)
        vals=dict(d0=d,forcing_transfer=Cs,scalar_original=Cf,scalar_from_compatible_loads=Cfnew,P_value=P0,P_first=P1,P_second=P2,P_sum=Cp,metric_from_compatible_loads=Cm,combined=Cfnew+Cm)
        gate(rec['constants_exact']=={q:str(v) for q,v in vals.items()},'EXACT_CONSTANTS')
        ints={q:-((-v.numerator)//v.denominator) for q,v in vals.items()};gate(rec['constants_outward_integer']==ints,'INTEGER_OUTWARD')
        arms[name]=dict(cells=count,combined=ints['combined'])
    gate(result['common_combined_outward_integer']==max(a['combined'] for a in arms.values()),'COMMON_BOUND')
    gate(lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'RUNTIME_INPUT_UNCHANGED')
    out=dict(pass_status=True,classification='COMPATIBLE_METRIC_RESPONSE_EXACT_ARITHMETIC_AUDIT_PASS',production_terminal_sha256=pin,checks=checks,arms=arms,seconds=time.monotonic()-started,scope='Independent exact rational cell-extrema and response-constant audit. Polynomial identity controls and validated background existence inherited with source review; no nonlinear-family convergence claim.')
    put('AUDIT_RESULT.json',out);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(out),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+600<DEADLINE,'LINUX_PIN_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE')
        lease=load('metric_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('METRIC_AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
