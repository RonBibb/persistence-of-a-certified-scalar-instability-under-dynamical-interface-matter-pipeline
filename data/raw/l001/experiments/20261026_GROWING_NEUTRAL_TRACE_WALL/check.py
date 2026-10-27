"""General-rate principal trace/wall qualification and conditional closure."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
METRIC=BASE/'20261026_GROWING_NEUTRAL_METRIC_RESPONSE'
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
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
def qualify(ring,S):
    names=('E','H','T','Tp','h','rate','p','f','g','c','xi','chi','QT','QI','o','j')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    E,H,T,Tp,h,rate,p,f,g,c,xi,chi,QT,QI,o,j=[ring.variable(i) for i in range(len(names))]
    gates={}
    def eq(n,v):gates[n]=ring.P.cast(v).iszero();need(gates[n],n)
    ps=S([0,p]);bs=S([0,c-2*p]);fs=S([0,f]);shift=S([0,xi]);osc=S([0,chi])
    pt,bt,ft=ps.dt(rate),bs.dt(rate),fs.dt(rate)
    trace=(bs+2*ps).dt(rate).dt(rate)-h*(bs+2*ps).dt(rate)+bt*bt-2*pt*bt-2*pt*pt+ft*ft
    eq('EXACT_GENERAL_RATE_BULK_TRACE_PRINCIPAL',trace.a[1]-rate*(rate-h)*c)
    invN=(-H*shift-ps).expzero()*E;velocity=bs.expzero()*invN*shift.dt(rate)
    deltaPhi=S([0,f+T*xi]);chid=osc.dt(rate)
    oscillator=invN*invN*(chid.dt(rate)+(S([3*h])+2*H*shift.dt(rate)+2*ps.dt(rate))*chid)+2*osc-deltaPhi
    d=2+rate*(rate+3*h)*E*E
    eq('EXACT_GENERAL_RATE_OSCILLATOR_PRINCIPAL',oscillator.a[1]-(d*chi-f-T*xi))
    normal=(-bs).expzero()*(S([T])+Tp*shift+S([0,g]))+velocity*invN*fs.dt(rate)
    for sigma in (-1,1):
        graph=sigma*invN*(velocity.dt(rate)+velocity*(bs.dt(rate)-h-ps.dt(rate)))-(invN*invN*chid*chid)/2
        eq('EXACT_GENERAL_RATE_GRAPH_PRINCIPAL_'+str(sigma),graph.a[1]-sigma*E*E*rate*(rate-h)*xi)
        junction=normal-(S([2*sigma*T])+21*deltaPhi-osc)*sigma/2
        J=g+Tp*xi-T*c+2*T*p-sigma*(21*(f+T*xi)-chi)/2
        eq('EXACT_GENERAL_RATE_NORMAL_PRINCIPAL_'+str(sigma),junction.a[1]-J)
        # Scalar row has source j, oscillator row has source o. Exact
        # elimination is polynomial after multiplying by the oscillator d.
        Rtimesd=2*sigma*d*(T*c-Tp*xi-j)+(21*d-1)*T*xi+o
        RobinTimesd=2*sigma*d*(g+2*T*p)-(21*d-1)*f-Rtimesd
        eq('EXACT_RAW_SOURCE_ROBIN_ELIMINATION_'+str(sigma),2*sigma*d*(J+j)-(d*chi-f-T*xi+o)-RobinTimesd)
    return gates
def main(lease,pin):
    need(sha(METRIC/'TERMINAL.json')==pin,'METRIC_TERMINAL_PIN');term=read(METRIC/'TERMINAL.json');need(term['pass'],'METRIC_PASS')
    inputs={str(METRIC/'TERMINAL.json'):pin}
    metric_audit=METRIC/'audit/AUDIT_TERMINAL.json'
    need(sha(metric_audit)=='06c64b772c6765b90a2cbfe43576ac14220793915635fbaa8d8cc572b7057847','METRIC_ARITHMETIC_AUDIT_PIN')
    mat=read(metric_audit);mar=METRIC/'audit/AUDIT_RESULT.json'
    need(mat['pass_status'] and sha(mar)==mat['result_sha256'] and read(mar)['production_terminal_sha256']==pin,'METRIC_ARITHMETIC_AUDIT')
    inputs[str(metric_audit)]=sha(metric_audit);inputs[str(mar)]=sha(mar)
    for n,k in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')):need(sha(METRIC/n)==term[k],'METRIC_RECORD');inputs[str(METRIC/n)]=term[k]
    binding=read(METRIC/'BINDING.json')
    for group in ('inputs','sources','runtime'):
        for p,h in binding[group].items():need(sha(p)==h,'METRIC_CLOSURE');inputs[p]=h
    # The independent all-order scalar audit is an additional prerequisite.
    inverseaudit=BASE/'20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE/audit'
    need(sha(inverseaudit/'AUDIT_TERMINAL.json')=='970f11cb9734c3dfe725788de8957a4b5ca0fced0727ec1ae6a4f8da14907c35','INDEPENDENT_INVERSE_AUDIT_PIN')
    # Audit schema is handled by binding its pinned terminal and each
    # referenced result, rather than guessing acceptance from file presence.
    at=read(inverseaudit/'AUDIT_TERMINAL.json');need(at.get('pass',at.get('pass_status')) is True,'INVERSE_AUDIT_PASS')
    inputs[str(inverseaudit/'AUDIT_TERMINAL.json')]=sha(inverseaudit/'AUDIT_TERMINAL.json')
    for name,key in (('AUDIT_RESULT.json','result_sha256'),('AUDIT_BINDING.json','binding_sha256'),('verify.py','source_sha256')):
        need(sha(inverseaudit/name)==at[key],'INVERSE_AUDIT_RECORD');inputs[str(inverseaudit/name)]=at[key]
    ringpath=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
    wallpath=BASE/'20261026_GROWING_MODE_CUBIC_WALL/wall.py'
    need(inputs.get(str(ringpath))==sha(ringpath) and inputs.get(str(wallpath))==sha(wallpath),'QUALIFIED_ALGEBRA_AUTHORITY')
    ring=load('neutral_trace_wall_ring',ringpath);S=load('neutral_trace_wall_series',wallpath).S
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP')
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h or (p==str(pylong) and h==sha(pylong)),'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,metric_terminal_pin=pin))
    gates=qualify(ring,S);mr=read(METRIC/'RESULT.json');need(mr['pass'],'METRIC_RESULT');arms={}
    for name,a in mr['arms'].items():
        T0=Q(a['background_extrema']['T0']);Tp0=Q(a['background_extrema']['Tp0']);rmin=Q(a['r_min']);emin2=Q(a['E2_min']);need(rmin>0 and emin2>0,'POSITIVE_DENOMINATOR_CONSTANTS')
        Cc=2/(rmin*rmin);Cxi=Cc/emin2;Cchi=1/(rmin*rmin*emin2)
        # n max|R| <= loadfactor times the supplied raw-source norm M_n.
        loadfactor=max(Q(1),T0*Cc,(Tp0+Q(21,2)*T0)*Cxi,Q(2),Cchi/2)
        Cscalar=Q(a['constants_exact']['scalar_from_compatible_loads'])*loadfactor
        Cp=Q(a['constants_exact']['metric_from_compatible_loads'])*loadfactor
        Cb=Cc+2*Cp
        Cosc=Cchi*(1+Cscalar/4+T0*Cxi/4)
        constants=dict(trace=Cc,graph=Cxi,oscillator_raw=Cchi,raw_to_R_metric_norm=loadfactor,scalar=Cscalar,metric_p=Cp,metric_b=Cb,wall_oscillator=Cosc)
        arms[name]={'constants_exact':{k:str(v) for k,v in constants.items()},'constants_outward_integer':{k:-((-v.numerator)//v.denominator) for k,v in constants.items()}}
    need(lease.observed()==runtime,'RUNTIME_UNCHANGED');need(all(sha(p)==h for p,h in dict(inputs,**sources).items()),'INPUTS_UNCHANGED')
    out={'pass':True,'classification':'CONDITIONAL_ALL_NEUTRAL_ORDER_REAL_AXIS_TRACE_METRIC_WALL_CLOSURE','exact_controls':gates,'arms':arms,'norm':'M_n=||Sc||+||Sg||+n||Sp||+||Sp_prime||+||QT||+||QT_prime||/n+||QT_second||/n²+max|QI|+n max|j|+max|o|; U_n(v)=n²||v||+n||v_prime||+||v_second||','bounds':'U_n(c),U_n(f),U_n(p),U_n(b),n²max|xi|,n²max|chi| each bounded by its stated constant times M_n. b=c-2p.','regularity':'QT has two radial derivatives, Sp one, Sc one for the pointwise compatibility identity. These are supplied source norms, not free derivative gains.','scope':'Conditional real-axis linear homological response for all n>=2. General-rate principal variation plus triangular positive-power counting; lower-order nonlinear sources are not bounded here. Assumes compatible sources and inherited scalar/background certificates. No complex-norm majorant, analytic-family convergence, finite-amplitude radius or endpoint claim.','new_ode_solves':0}
    put('RESULT.json',out);put('TERMINAL.json',{'pass':True,'result_sha256':sha(ROOT/'RESULT.json'),'binding_sha256':sha(ROOT/'BINDING.json'),'source_sha256':sha(__file__),'derivation_sha256':sha(ROOT/'DERIVATION.txt')})
    print(json.dumps({k:v for k,v in out.items() if k!='arms'}),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and len(sys.argv)==2 and time.time()+180<DEADLINE,'LINUX_PIN_BOUND_FITS');need(not any((ROOT/n).exists() for n in ('START.json','RESULT.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN')
        lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(read(FROZEN)['files'][str(lp)]==sha(lp),'LEASE');lease=load('neutral_trace_wall_lease',lp);lease.ROOT=ROOT
        cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('TRACE_WALL_180_SECONDS')));signal.alarm(180)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease,sys.argv[1])
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
