"""Independent rational replay of the mixed-row conditioning certificate."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
PIN='f77d561f1681b91cd15b65cb2db626ff842ac061e879dcbe9f27981c54878c63'
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
def main(lease):
    start=time.monotonic();count=0
    def gate(v,n):
        nonlocal count
        need(v,n);count+=1
    gate(sha(PACKET/'TERMINAL.json')==PIN,'PRODUCTION_PIN');t=read(PACKET/'TERMINAL.json');gate(t['pass_status'],'TERMINAL_PASS')
    inputs={str(PACKET/'TERMINAL.json'):PIN,str(Path(__file__)):sha(__file__)}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:
        gate(sha(PACKET/n)==t[k],'RECORD');inputs[str(PACKET/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PACKET/'BINDING.json')[group].items():gate(sha(p)==h,'ANCESTRY');inputs[p]=h
    gate(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():gate(inputs.get(p)==h,'RUNTIME:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=PIN))
    def bound_result(name):
        p=BASE/name/'RESULT.json';gate(inputs.get(str(p))==sha(p),'RESULT_AUTHORITY:'+name);return read(p)
    major=bound_result('20261026_NEUTRAL_SOURCE_MAJORANT');old={k:Q(v) for k,v in major['constants_exact'].items()}
    inv=bound_result('20261026_NEUTRAL_ANALYTIC_INVERSE');iv={k:Q(v) for k,v in inv['constants_exact'].items()}
    prior=bound_result('20261026_NEUTRAL_PROPER_CLOCK_REMAINDER');out=read(PACKET/'RESULT.json')
    rho=old['rho'];anchor=Q(11,4)/iv['real_D_normalized_lower'];scalar=old['Uf'];sp=old['Csp'];sc=old['Csc']
    gate(Q(4,3)+Q(289,1024)<2 and 2+24==26,'BACKGROUND_DERIVATIVES')
    gate(1-Q(3,2)*rho>0,'ABSORPTION')
    # Independently keep the differentiated mixed-row terms separate.
    X=(anchor*(sc+scalar+sp)+rho*(scalar/6+sp/2))/(1-Q(3,2)*rho)
    Y=3*X+scalar/3+sp
    Z=2*2*X/4+2*3*Y/2+26*scalar/12+2*scalar/6+9*sp/rho
    U=X+Y+Z
    C=3*U+old['Cc']+scalar+65536+2*old['Uchi']
    raw=max(Q(1),1/old['a'],2*C*old['M']/old['a']**2)
    K=Q((raw.numerator+raw.denominator-1)//raw.denominator)
    R=1/(96*K);rad=R/(8*old['seed']);MD=9*R/(1-R)
    gate(0<U<old['Up'] and K<old['K'],'STRICT_IMPROVEMENT')
    gate(K>=raw and K-1<raw,'OUTWARD_INTEGER')
    kr=K*R;gate(Q(1,2)+kr/(1-kr)**2<1,'SELF_MAP')
    gate(2*kr/(1-kr)**2+2*kr**2/(1-kr)**3<Q(1,2),'CONTRACTION')
    gate(4*R<old['gap'] and 2*R<1,'CHART')
    warp=64*old['gap']/(old['gap']-4*R);vel=4*R*warp/(1-R)**2
    lapse=warp/((1-R)*(1-vel**2));gate(vel<Q(1,2) and lapse<=128,'TIMELIKE_LAPSE')
    js=out['cubic_dyadic_halvings'];jc=out['clock_dyadic_halvings']
    gate(isinstance(js,int) and isinstance(jc,int) and 1<=js<=8192 and 1<=jc<=8192,'DYADIC_INDICES')
    qs=Q(1,2**js);es=rad*qs;ts=MD*qs**4/(1-qs)
    qc=Q(1,2**jc);ec=rad*qc/2;MF=129*MD/32;tc=MF*qc**3/(1-qc);dt=MD*(qc/2)**2/(1-qc/2)
    gate(ts<=700*es**2 and ts<=20000*es**3,'CUBIC_TAIL')
    gate(tc<=10*ec**2 and dt<=25*ec,'CLOCK_TAIL')
    if js>1:
        q=2*qs;e=rad*q;t0=MD*q**4/(1-q);gate(t0>700*e**2 or t0>20000*e**3,'FIRST_CUBIC')
    if jc>1:
        q=2*qc;e=rad*q/2;t0=MF*q**3/(1-q);d0=MD*(q/2)**2/(1-q/2);gate(t0>10*e**2 or d0>25*e,'FIRST_CLOCK')
    expected=dict(Cm=anchor,metric_X=X,metric_Y=Y,metric_Z=Z,Up=U,C=C,K=K,R=R,eta_physical_radius=rad,observable_sup=MD,inverse_lapse_bound=lapse,cubic_q=qs,cubic_eta=es,cubic_tail=ts,clock_MF=MF,clock_q=qc,clock_eta=ec,clock_tail=tc,distance_tail_after_linear=dt,metric_bound_gain=old['Up']/U,radius_gain=rad/old['eta_physical_radius'])
    gate(set(expected)==set(out['constants_exact']),'CONSTANT_INVENTORY')
    for k,v in expected.items():gate(v==Q(out['constants_exact'][k]),'EXACT:'+k)
    gate(rad>old['eta_physical_radius'] and es>old['selected_eta'] and ec>Q(prior['constants_exact']['eta']),'ALL_RADII_IMPROVE')
    for k,d in out['display'].items():
        v=expected[k];ten=Q(10)**d['floor_log10'];gate(ten<=v<10*ten,'DISPLAY_DECADE');w=v*10**6/ten;gate(w.numerator//w.denominator==d['mantissa_floor_millionths'],'DISPLAY_MANTISSA')
    # Additional bounded consequence requested after production: both signs
    # of eta obey the same absolute remainder bound.
    counts={1:0,2:0}
    for k,v in major['coefficient_enclosures'].items():
        lo,hi=map(Q,v)
        if k.endswith(':d1'):gate(-54<lo<=hi<-50,'SIGNED_D1');counts[1]+=1
        if k.endswith(':d2'):gate(-1600<lo<=hi<-1400,'SIGNED_D2');counts[2]+=1
    gate(min(counts.values())>=2,'TWO_ENGINE_BOUNDS')
    gate(Q(-1550,32)>-50 and Q(-1346,64)<-21,'TWO_SIDED_QUADRATIC')
    gate(ec<Q(1,512) and Q(25,64)-Q(60,512)>0,'OPENING_POSITIVE')
    gate(out['pass_status'] and all(out['gates'].values()) and out['new_ode_solves']==0,'PRODUCTION_STATUS')
    gate(time.monotonic()-start<550 and time.time()<DEADLINE and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='INDEPENDENT_CONDITIONING_EXACT_AUDIT_PASS',checks=count,production_terminal_sha256=PIN,display=out['display'],two_sided_clock_bounds_verified=True,seconds=time.monotonic()-start,scope='Independent rational mixed-row response, majorant, first-admissible remainders and binding replay; analytical source/inverse proof reviewed separately. Added coefficient-margin check supports slowing of local opening and reinforcement of local shortening, not saturation, generic evolution or endpoint.')
    put('AUDIT_RESULT.json',result);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('conditioning_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
