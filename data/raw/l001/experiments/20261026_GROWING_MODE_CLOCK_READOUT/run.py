"""Exact formal distance dynamics readout, not a finite-amplitude solution."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_MODE_CUBIC_AFFINE'
QUAD=BASE/'20261026_GROWING_MODE_QUADRATIC_R1'
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
def main(lease,pin,auditpin):
    need(sha(PARENT/'production_TERMINAL.json')==pin,'PRODUCTION_PIN')
    need(sha(PARENT/'audit/AUDIT_TERMINAL.json')==auditpin,'AUDIT_PIN')
    terminal=read(PARENT/'production_TERMINAL.json');audit=read(PARENT/'audit/AUDIT_TERMINAL.json')
    need(terminal['pass'] and audit['pass'],'PARENT_PASS')
    files={str(PARENT/'production_TERMINAL.json'):pin,str(PARENT/'audit/AUDIT_TERMINAL.json'):auditpin}
    for n,h in terminal['artifacts'].items():need(sha(PARENT/n)==h,'ARTIFACT');files[str(PARENT/n)]=h
    for group in ('sources','parents','runtime'):
        for p,h in read(PARENT/'production_BINDING.json')[group].items():need(sha(p)==h,'PARENT_BINDING');files[p]=h
    need(sha(PARENT/'audit/AUDIT_RESULT.json')==audit['result_sha256'],'AUDIT_RESULT')
    ar=read(PARENT/'audit/AUDIT_RESULT.json');need(ar['pass'] and ar['production_terminal_sha256']==pin,'AUDIT_OWNERSHIP')
    files[str(PARENT/'audit/AUDIT_RESULT.json')]=audit['result_sha256']
    utility=QUAD/'audit/verify.py';need(sha(utility)==read(QUAD/'audit/AUDIT_TERMINAL.json')['source_sha256'],'INTERVAL_UTILITY')
    files[str(utility)]=sha(utility);u=load('clock_exact_interval',utility);I,iv,dec=u.I,u.iv,u.decimal_outward
    ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
    need(str(ringpath) in files and sha(ringpath)==files[str(ringpath)],'EXACT_RING_AUTHORITY')
    ring=load('clock_polynomial_ring',ringpath);ring.NAMES=('b','c','a1','A');ring.N=4;ring.ZERO=(0,)*4
    b,c,a1,A=[ring.variable(j) for j in range(4)]
    seriespath=BASE/'20261026_GROWING_MODE_CUBIC_WALL/wall.py'
    need(str(seriespath) in files and sha(seriespath)==files[str(seriespath)],'SERIES_AUTHORITY')
    S=load('clock_series',seriespath).S
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG')
    need(len(str(10**20000))==20001,'WARMUP');files[str(pylong)]=sha(pylong)
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='CONTRACT.json'}
    runtime=lease.observed()
    for p,h in runtime.items():need(files.get(p)==h or sources.get(p)==h,'UNBOUND_RUNTIME:'+p)
    put('BINDING.json',dict(inputs=files,sources=sources,runtime=runtime,production_pin=pin,audit_pin=auditpin))
    checks=[]
    def eq(s,t,label):
        need(all(ring.P.cast(x-y).iszero() for x,y in zip(s.a,t.a)),label);checks.append(label)
    y=S([0,1]);eta=S([0,1,-b,2*b*b-c]);eta2=eta*eta;eta3=eta2*eta
    eq(eta+b*eta2+c*eta3,y,'EXACT_SERIES_REVERSION')
    coordinate=eta+2*b*eta2+3*c*eta3
    eq(coordinate,S([0,1,b,2*c-2*b*b]),'EXACT_COORDINATE_CLOCK')
    inverse_lapse=S([1])-a1*eta+(a1*a1/2-A)*eta2
    proper=coordinate*inverse_lapse
    eq(proper,S([0,1,b-a1,2*c-2*b*b+a1*a1/2-A]),'EXACT_PROPER_CLOCK')
    # Re-expanding the logarithmic lapse verifies the inverse to required order.
    lapse=S([0,a1,A]).expzero();inv=S([0,-a1,-A]).expzero()
    eq(lapse*inv,S([1]),'EXACT_INVERSE_LAPSE_THROUGH_CUBIC')
    rows={}
    for name in ('primary','independent'):
        rec=read(PARENT/('PRODUCTION_'+name+'.json'));qrec=read(QUAD/('PRODUCTION_'+name+'.json'))
        d1=iv(qrec['d1']);d2=iv(qrec['d2']);d3=iv(rec['d3']);rate=iv(rec['parameters']['rate'])
        need(not d1.zero() and rate.lo>0,'LOCAL_INVERTIBILITY')
        wall=qrec['walls']['lower'];z=list(map(iv,wall['state']))
        xi2=iv(wall['loads']['xi2']) if 'loads' in wall else iv(wall['xi2'])
        lapseA=z[8]+z[1]*xi2;linear=z[5]
        need(linear.lo==linear.hi==1 and z[0].lo==z[0].hi==0,'LOWER_CLOCK_NORMALIZATION')
        d1sq=d1*d1;d1cu=d1sq*d1;d1four=d1sq*d1sq
        ct2=d2/d1sq;ct3=2*d3/d1cu-2*d2*d2/d1four
        proper2=(d2-linear*d1)/d1sq
        proper3=ct3+(linear*linear/2-lapseA)/d1sq
        vals=dict(d1=d1,d2=d2,d3=d3,rate=rate,lower_log_lapse2=lapseA,coordinate_quadratic=ct2,coordinate_cubic=ct3,proper_quadratic=proper2,proper_cubic=proper3,proper_quadratic_rate=rate*proper2,proper_cubic_rate=rate*proper3)
        rows[name]={'values':{k:v.pack() for k,v in vals.items()},'outward_decimal_bounds':{k:dec(v) for k,v in vals.items()},'signs':{k:1 if v.lo>0 else -1 if v.hi<0 else 0 for k,v in vals.items()}}
    need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(all(sha(p)==h for p,h in dict(files,**sources).items()),'INPUT_UNCHANGED')
    out=dict(pass_status=True,classification='FORMAL_LOCAL_GROWING_DISTANCE_CLOCK_JET',exact_checks=checks,arms=rows,scope=read(ROOT/'CONTRACT.json')['scope'],new_radial_integrations=0)
    put('RESULT.json',out);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__)))
    print(json.dumps(dict(classification=out['classification'],checks=checks,arms={n:r['outward_decimal_bounds'] for n,r in rows.items()})),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==3 and time.time()+180<DEADLINE,'LINUX_PINS_DEADLINE')
        need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE')
        lease=load('clock_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('CLOCK_180_SECONDS')));signal.alarm(180)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,*sys.argv[1:])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
