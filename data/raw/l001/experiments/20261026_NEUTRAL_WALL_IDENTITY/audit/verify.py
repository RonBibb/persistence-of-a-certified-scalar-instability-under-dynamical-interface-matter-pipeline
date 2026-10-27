"""Independent two-dimensional warped-product wall qualification."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;PACKET=ROOT.parent;BASE=PACKET.parent
FROZEN=BASE/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
PIN='f8820ce6d0f2871e7dcb1d236e33229123a37458f6849af2beb0dfe9b340d50b';DEADLINE=1793047195
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,n):
    if not v:raise AssertionError(n)
def load(n,p):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def put(n,v):
    p=ROOT/n;tmp=ROOT/(n+'.tmp')
    with tmp.open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
    os.chmod(tmp,0o444);os.link(tmp,p);tmp.unlink()
    fd=os.open(ROOT,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)
def qualify(ring):
    names=('N','B','R','Nt','Ns','Bt','Bs','Rt','Rs','Rtt','Rts','Rss','v','vt','h','H','st','pwt','bt','pt','A0','lambda','j','xd','xdd','V','Vp','Vx','phid','Hw','nphi','EnU','g2')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);P=ring.P
    z={key:ring.variable(i) for i,key in enumerate(names)}
    def inverse(key):
        a=[0]*len(names);a[names.index(key)]=-1;return P({tuple(a):Q(1)})
    N,B,R=z['N'],z['B'],z['R'];ni,bi,ri=map(inverse,('N','B','R'));v=z['v']
    time_map={'N':z['Nt'],'B':z['Bt'],'R':z['Rt'],'Rt':z['Rtt'],'Rs':z['Rts']}
    space_map={'N':z['Ns'],'B':z['Bs'],'R':z['Rs'],'Rt':z['Rts'],'Rs':z['Rss']}
    def partial(f,mapping):return sum((f.derivative(names.index(key))*value for key,value in mapping.items()),P(0))
    def along(f):return partial(f,time_map)+v*N*bi*partial(f,space_map)
    checks=[]
    def eq(a,b,label):need((a-b).iszero(),label);checks.append(label)
    # Hessian from the six explicit base Christoffels, not 5D Ricci loops.
    htt=z['Rtt']-z['Nt']*ni*z['Rt']-N*z['Ns']*bi*bi*z['Rs']
    hts=z['Rts']-z['Ns']*ni*z['Rt']-z['Bt']*bi*z['Rs']
    hss=z['Rss']-B*z['Bt']*ni*ni*z['Rt']-z['Bs']*bi*z['Rs']
    warped=-3*ri*(v*ni*ni*htt+(1+v*v)*ni*bi*hts+v*bi*bi*hss)
    A=z['Ns']*ni*bi;C=z['Bt']*ni*bi;D=z['Rs']*bi*ri;F=z['Rt']*ni*ri
    geometric=3*(-ni*(along(D)+v*along(F))+(F+v*D)*(A-D+v*(C-F)))
    eq(warped,geometric,'INDEPENDENT_WARPED_HESSIAN_CODAZZI')
    need(not (warped+geometric).iszero(),'CODAZZI_SIGN_NEGATIVE_CONTROL');checks.append('CODAZZI_SIGN_NEGATIVE_CONTROL')
    eq((F+v*D)-v*(D+v*F),(1-v*v)*F,'ACCELERATION_CANCELLATION')
    # Actual longitudinal metric-jet substitution, done monomialwise.
    def sub(f,replacements):
        ans=P(0)
        for powers,coefficient in f.t.items():
            term=P(coefficient)
            for key,power in zip(names,powers):
                if not power:continue
                if key in replacements:
                    need(power>=0,'SUBSTITUTED_JET_NONNEGATIVE');term*=replacements[key]**power
                else:
                    ex=[0]*len(names);ex[names.index(key)]=power;term*=P({tuple(ex):Q(1)})
            ans+=term
        return ans
    replacements={'Ns':N*z['A0'],'Rs':R*z['A0'],'Bt':B*z['bt'],'Rt':R*(z['h']+z['pt'])}
    eq(sub(A-D,replacements),P(0),'S7_RADIAL_CANCELLATION')
    eq(sub(C-F,replacements),ni*(z['bt']-z['h']-z['pt']),'S7_TEMPORAL_SPECIALIZATION')
    eq(sub(z['g2']*z['vt']*ni+A-D+v*(C-F),replacements),ni*(z['g2']*z['vt']+v*(z['bt']-z['h']-z['pt'])),'FULL_S7_SPECIALIZATION')
    xd,xdd,V,Vp,Vx,phid,Hw,nphi,EnU=[z[key] for key in ('xd','xdd','V','Vp','Vx','phid','Hw','nphi','EnU')]
    density=xd*xd/2+V;pressure=xd*xd/2-V
    energy=xd*xdd+Vp*phid+Vx*xd+3*Hw*(density+pressure)
    oscillator=xdd+3*Hw*xd+Vx
    eq(energy,xd*oscillator+Vp*phid,'INDEPENDENT_MATERIAL_ENERGY_IDENTITY')
    junction=EnU+nphi*phid-energy/2
    eq(junction,EnU+(2*nphi-Vp)*phid/2-xd*oscillator/2,'JUNCTION_RESIDUAL_HALF_FACTOR')
    need(not (junction-EnU-(2*nphi-Vp)*phid/2+xd*oscillator).iszero(),'HALF_FACTOR_NEGATIVE_CONTROL');checks.append('HALF_FACTOR_NEGATIVE_CONTROL')
    lr=z['h']+z['H']*z['st']+z['pwt'];ln=z['H']*z['st']+z['pwt']
    eq(3*lr*(1-v*v)-ln*(1-v*v)+v*z['vt'],(3*z['h']+2*z['H']*z['st']+2*z['pwt'])*(1-v*v)+v*z['vt'],'Q5_FRICTION_CONVERSION')
    eq(3*Hw*(z['j']-z['j'])+z['lambda']*z['j'],z['lambda']*z['j'],'PURE_TRACE_POSITIVE_HARMONIC')
    need(not (z['lambda']*z['j']).iszero(),'NONZERO_HARMONIC_REQUIRED');checks.append('NONZERO_HARMONIC_REQUIRED')
    return checks
def main(lease):
    start=time.monotonic();need(sha(PACKET/'TERMINAL.json')==PIN,'PRODUCTION_PIN');t=read(PACKET/'TERMINAL.json');need(t['pass_status'],'PRODUCTION_PASS')
    inputs={str(PACKET/'TERMINAL.json'):PIN,str(Path(__file__)):sha(__file__),str(ROOT/'DERIVATION.txt'):sha(ROOT/'DERIVATION.txt')}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256'),('check.py','source_sha256'),('DERIVATION.txt','derivation_sha256')]:need(sha(PACKET/n)==t[k],'PRODUCTION_RECORD');inputs[str(PACKET/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PACKET/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_CLOSURE');inputs[p]=h
    rp=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py';need(inputs.get(str(rp))==sha(rp),'POLYNOMIAL_HELPER_AUTHORITY');ring=load('independent_wall_polynomial_helper',rp)
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h,'RUNTIME:'+p)
    put('AUDIT_BINDING.json',dict(inputs=inputs,runtime=runtime,production_terminal_sha256=PIN));checks=qualify(ring)
    prod=read(PACKET/'RESULT.json');need(prod['pass_status'] and all(prod['gates'].values()),'PRODUCTION_GATES')
    need(time.time()<DEADLINE and time.monotonic()-start<550 and lease.observed()==runtime and all(sha(p)==h for p,h in inputs.items()),'UNCHANGED_BINDING')
    out=dict(pass_status=True,classification='INDEPENDENT_NEUTRAL_WALL_WARPED_PRODUCT_IDENTITY_AUDIT_PASS',checks=checks,check_count=len(checks),production_terminal_sha256=PIN,seconds=time.monotonic()-start,scope='Independent two-dimensional Hessian/warped-product route, actual S7 jet substitution and neutral material identity. Qualifies wall compatibility for the same homogeneous timelike neutral canonical-oscillator ansatz. Standard warped-product curvature theorem inherited; production separately computes full5D Ricci. No general-geometry or nonzero-current theorem, zero-harmonic elimination, or ODE calculation.')
    put('AUDIT_RESULT.json',out);put('AUDIT_TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'AUDIT_RESULT.json'),binding_sha256=sha(ROOT/'AUDIT_BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')));print(json.dumps(out),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+600<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','AUDIT_FAILURE.json','AUDIT_TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('wall_independent_audit_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('WALL_AUDIT_600_SECONDS')));signal.alarm(600)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('AUDIT_FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
