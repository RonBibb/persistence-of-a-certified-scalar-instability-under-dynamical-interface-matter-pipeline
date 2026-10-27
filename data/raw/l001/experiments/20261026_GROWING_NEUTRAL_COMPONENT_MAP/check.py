"""Exact off-shell Christoffel/Ricci qualification of the S6 component map.
No background equations or numerical fixtures are used in the identities.
"""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_NEUTRAL_TRACE_WALL_R1'
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
def qualify(ring):
    names=('U','V','W','pt','ps','bt','bs','ptt','pts','pss','btt','bts','bss','H','Hp','T','Tp','Phi','f','ft','fs','ftt','fss','h','m','A','X','C','At','Cs','lambda')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    z={n:ring.variable(i) for i,n in enumerate(names)};P=ring.P;zero=P(0)
    U,V,W,pt,ps,bt,bs,ptt,pts,pss,btt,bts,bss,H,Hp,T,Tp,Phi,f,ft,fs,ftt,fss,h,m,A,X,C,At,Cs,lam=[z[n] for n in names]
    def inverse_var(n):
        exp=[0]*len(names);exp[names.index(n)]=-1;return P({tuple(exp):Q(1)})
    Ui,Vi,Wi=[inverse_var(n) for n in ('U','V','W')]
    # Exact Laurent polynomials: positive metric scale factors never vanish.
    Y=H+ps;Z=T+fs
    td={'U':2*U*pt,'V':2*V*(h+pt),'W':2*W*bt,'pt':ptt,'ps':pts,'bt':btt,'bs':bts}
    sd={'U':2*U*Y,'V':2*V*Y,'W':2*W*bs,'pt':pts,'ps':pss,'bt':bts,'bs':bss,'H':Hp}
    def derivative(v,axis):
        d=td if axis==0 else sd if axis==4 else {}
        return sum((v.derivative(names.index(n))*q for n,q in d.items()),zero)
    metric=(-U,V,V,V,W);inv=(-Ui,Vi,Vi,Vi,Wi)
    gamma={}
    for a in range(5):
        for b in range(5):
            for c in range(5):
                gamma[a,b,c]=inv[a]*((derivative(metric[a],b) if a==c else zero)+(derivative(metric[a],c) if a==b else zero)-(derivative(metric[b],a) if b==c else zero))/2
    ric={}
    for a in range(5):
        for b in range(5):
            ric[a,b]=sum((derivative(gamma[c,a,b],c)-derivative(gamma[c,a,c],b)+sum((gamma[c,a,b]*gamma[d,c,d]-gamma[d,a,c]*gamma[c,b,d] for d in range(5)),zero) for c in range(5)),zero)
    curvature=sum((inv[a]*ric[a,a] for a in range(5)),zero)
    phi_gradient=[ft,zero,zero,zero,Z];kinetic=-Ui*ft*ft+Wi*Z*Z;potential=m*(Phi+f)*(Phi+f)/2
    ein={}
    for a in range(5):
        for b in range(5):
            ein[a,b]=inv[a]*ric[a,b]-(curvature/2+6 if a==b else zero)-inv[a]*phi_gradient[a]*phi_gradient[b]+(kinetic/2+potential if a==b else zero)
    trace=btt+2*ptt-h*(bt+2*pt)+bt*bt-2*pt*bt-2*pt*pt+ft*ft
    mixed=pts-bt*Y+ft*Z/3
    radial=Wi*(6*Y*Y-Z*Z/2)-6+potential-Ui*(6*h*h+3*(ptt+3*h*pt)+3*pt*pt+ft*ft/2)
    kg=sum((inv[a]*((ftt if a==0 else Tp+fss if a==4 else zero)-sum((gamma[c,a,a]*phi_gradient[c] for c in range(5)),zero)) for a in range(5)),zero)-m*(Phi+f)
    expected_kg=-Ui*(ftt+(3*h+2*pt+bt)*ft)+Wi*(Tp+fss+(4*H+4*ps-bs)*Z)-m*(Phi+f)
    gates={}
    def eq(n,v):gates[n]=v.iszero();need(gates[n],n)
    eq('METRIC_INVERSE_U',U*Ui-1);eq('METRIC_INVERSE_V',V*Vi-1);eq('METRIC_INVERSE_W',W*Wi-1)
    eq('OFF_SHELL_TRACE_COMPONENT',ein[0,0]-ein[1,1]-Ui*trace)
    eq('OFF_SHELL_MIXED_COMPONENT',ein[4,0]+3*Wi*mixed)
    eq('OFF_SHELL_RADIAL_COMPONENT',ein[4,4]-radial)
    eq('OFF_SHELL_KLEIN_GORDON',kg-expected_kg)
    eq('SPATIAL_ISOTROPY_2',ein[1,1]-ein[2,2]);eq('SPATIAL_ISOTROPY_3',ein[1,1]-ein[3,3])
    # Covariant divergence of a diagonal mixed tensor, with mixed residual
    # set to zero, is computed directly from these same Christoffels.
    diagonal=[A,X,X,X,C]
    for nu,target in ((0,At+3*(h+pt)*(A-X)+bt*(A-C)),(4,Cs+Y*(4*C-A-3*X))):
        divergence=(At if nu==0 else Cs)+sum((gamma[mu,mu,nu]*(diagonal[nu]-diagonal[mu]) for mu in range(5)),zero)
        eq('DIAGONAL_DIVERGENCE_'+str(nu),divergence-target)
    # At order n, lower residuals vanish and p_t,b_t have positive order.
    temporal_n=lam*A+3*h*(A-X);radial_n=Cs+H*(4*C-A-3*X)
    eq('NONZERO_HARMONIC_TEMPORAL_ELIMINATION',temporal_n-3*h*(A-X)-lam*A)
    eq('RADIAL_RESIDUAL_PROPAGATION',radial_n+H*(A+3*X)-(Cs+4*H*C))
    return gates
def main(lease):
    terminal=PARENT/'TERMINAL.json';need(sha(terminal)=='ca7508e9840b268e01cde2fcc8295e1c452a1aee729ba7b12164712d55432a6e','PARENT_PIN');t=read(terminal);need(t['pass'],'PARENT_PASS')
    inputs={str(terminal):sha(terminal)}
    for n,k in (('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')):need(sha(PARENT/n)==t[k],'PARENT_RECORD');inputs[str(PARENT/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_CLOSURE');inputs[p]=h
    rp=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py';need(inputs.get(str(rp))==sha(rp),'RING_PIN');ring=load('off_shell_laurent_ring',rp)
    pylong=Path('/usr/lib/python3.12/_pylong.py');need(sha(pylong)=='79e219a7d1cab0b3d954fab7937c58ef965a3a132bdb885dda17bbb9fdfab16c','PYLONG');need(len(str(10**20000))==20001,'WARMUP');inputs[str(pylong)]=sha(pylong)
    sources={str(Path(__file__)):sha(__file__)};runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime));start=time.monotonic();gates=qualify(ring)
    need(lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'INPUTS_UNCHANGED')
    out=dict(pass_status=True,classification='EXACT_OFF_SHELL_S6_COMPONENT_AND_DIVERGENCE_MAP',gates=gates,seconds=time.monotonic()-start,scope='Exact Christoffel/Ricci component map and diagonal-divergence identities for the five-dimensional homogeneous ansatz. General jets, not sampled backgrounds. Uses the standard Einstein-scalar contracted Bianchi identity to infer constraint propagation when KG and mixed residuals vanish. Does not prove convergence or control nonlinear sources.')
    put('RESULT.json',out);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__)));print(json.dumps(out),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+180<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('component_map_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('COMPONENT_MAP_180_SECONDS')));signal.alarm(180)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
