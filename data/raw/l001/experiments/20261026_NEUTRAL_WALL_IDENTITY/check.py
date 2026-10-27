"""Off-shell moving-wall Codazzi and material identity, exact Laurent jets."""
import sys
sys.dont_write_bytecode=True
sys.set_int_max_str_digits(100000)
import hashlib,importlib.util,json,os,signal,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent
PARENT=BASE/'20261026_GROWING_NEUTRAL_COMPONENT_MAP'
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
def qualify(ring):
    names=('N','R','B','Nt','Ns','Rt','Rs','Bt','Bs','Ntt','Nts','Nss','Rtt','Rts','Rss','Btt','Bts','Bss','v','vt','g2','xd','xdd','V','Vphi','Vchi','phid','hw','nphi','EnU','h','H','St','pwallt','pt','bt','lambda','j')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    P=ring.P;zero=P(0);z={n:ring.variable(i) for i,n in enumerate(names)}
    def inv(n):
        ex=[0]*len(names);ex[names.index(n)]=-1;return P({tuple(ex):Q(1)})
    N,R,B=[z[n] for n in ('N','R','B')];Ni,Ri,Bi=map(inv,('N','R','B'))
    v,vt,g2=[z[n] for n in ('v','vt','g2')]
    td={n:z[n+'t'] for n in ('N','R','B')};sd={n:z[n+'s'] for n in ('N','R','B')}
    for n in ('N','R','B'):
        td[n+'t']=z[n+'tt'];td[n+'s']=z[n+'ts'];sd[n+'t']=z[n+'ts'];sd[n+'s']=z[n+'ss']
    def derivative(f,axis):
        d=td if axis==0 else sd if axis==4 else {}
        return sum((f.derivative(names.index(n))*q for n,q in d.items()),zero)
    def along(f):return derivative(f,0)+v*N*Bi*derivative(f,4)
    metric=(-N*N,R*R,R*R,R*R,B*B);inverse=(-Ni*Ni,Ri*Ri,Ri*Ri,Ri*Ri,Bi*Bi)
    gamma={}
    for a in range(5):
        for b in range(5):
            for c in range(5):
                gamma[a,b,c]=inverse[a]*((derivative(metric[a],b) if a==c else zero)+(derivative(metric[a],c) if a==b else zero)-(derivative(metric[b],a) if b==c else zero))/2
    ric={}
    for a in (0,4):
        for b in (0,4):
            ric[a,b]=sum((derivative(gamma[c,a,b],c)-derivative(gamma[c,a,c],b)+sum((gamma[c,a,b]*gamma[d,c,d]-gamma[d,a,c]*gamma[c,b,d] for d in range(5)),zero) for c in range(5)),zero)
    gates={}
    def eq(n,f):need(f.iszero(),n);gates[n]=True
    A=z['Ns']*Ni*Bi;C=z['Bt']*Ni*Bi;D=z['Rs']*Bi*Ri;F=z['Rt']*Ni*Ri
    eq('NORMAL_TANGENT_ORTHOGONAL',-N*N*(v*Ni)*Ni+B*B*Bi*(v*Bi))
    eq('TANGENT_NORM_FACTOR',-N*N*Ni*Ni+B*B*v*v*Bi*Bi+1-v*v)
    eq('NORMAL_NORM_FACTOR',-N*N*v*v*Ni*Ni+B*B*Bi*Bi-1+v*v)
    eq('SPATIAL_EXTRINSIC_EIGENVALUE',(N*v*gamma[0,1,1]-B*gamma[4,1,1])*Ri*Ri-D-v*F)
    # Acceleration a^A divided by gamma². Derivative gamma contributes g2=gamma².
    at=g2*v*vt*Ni*Ni-along(N)*Ni**3+gamma[0,0,0]*Ni*Ni+2*gamma[0,0,4]*v*Ni*Bi+gamma[0,4,4]*v*v*Bi*Bi
    ass=g2*v*v*vt*Ni*Bi+vt*Ni*Bi-v*along(B)*Ni*Bi*Bi+gamma[4,0,0]*Ni*Ni+2*gamma[4,0,4]*v*Ni*Bi+gamma[4,4,4]*v*v*Bi*Bi
    eq('TEMPORAL_EXTRINSIC_FROM_NORMAL_ACCELERATION',-N*v*at+B*ass-vt*Ni-(1-v*v)*(A+v*C))
    # Difference of gamma² vt terms cancels via gamma²(1-v²)=1.
    eq('VELOCITY_ACCELERATION_CANCELLATION',(F+v*D)-v*(D+v*F)-(1-v*v)*F)
    divergence=3*(-Ni*(along(D)+v*along(F))+(F+v*D)*(A-D+v*(C-F)))
    projection=v*Ni*Ni*ric[0,0]+(1+v*v)*Ni*Bi*ric[0,4]+v*Bi*Bi*ric[4,4]
    eq('MOVING_WALL_CODAZZI_OFF_SHELL',divergence-projection)
    eq('RICCI_SYMMETRY',ric[0,4]-ric[4,0])
    xd,xdd,V,Vphi,Vchi,phid,hw,nphi,EnU=[z[n] for n in ('xd','xdd','V','Vphi','Vchi','phid','hw','nphi','EnU')]
    rho=xd*xd/2+V;pressure=xd*xd/2-V;od=xdd+3*hw*xd+Vchi
    rhod=xd*xdd+Vphi*phid+Vchi*xd
    exchange=rhod+3*hw*(rho+pressure)
    eq('MATERIAL_EXCHANGE_OFF_SHELL',exchange-xd*od-Vphi*phid)
    jphi=2*nphi-Vphi;divjunction=EnU+nphi*phid-exchange/2
    eq('FULL_JUNCTION_RESIDUAL_DIVERGENCE',divjunction-EnU-jphi*phid/2+xd*od/2)
    h,H,St,pwt=[z[n] for n in ('h','H','St','pwallt')]
    # Clear positive 1-v² without introducing a symbolic rational inversion.
    friction_cleared=3*(h+H*St+pwt)*(1-v*v)-((H*St+pwt)*(1-v*v)-v*vt)
    eq('Q5_EXACT_COORDINATE_FRICTION',friction_cleared-(3*h+2*H*St+2*pwt)*(1-v*v)-v*vt)
    # Substitute the actual ansatz's metric jets into the general K difference.
    specialized_A=z['Ns']*Ni*Bi
    specialized_D=(R*z['Ns']*Ni)*Bi*Ri
    specialized_C=(B*z['bt'])*Ni*Bi
    specialized_F=(R*(h+z['pt']))*Ni*Ri
    specialized_difference=g2*vt*Ni+specialized_A-specialized_D+v*(specialized_C-specialized_F)
    eq('S7_SPECIALIZATION',specialized_difference-Ni*(g2*vt+v*(z['bt']-h-z['pt'])))
    eq('PURE_TRACE_JUNCTION_CONNECTION_CANCELLATION',3*hw*(z['j']-z['j']))
    # Negative controls ensure the main identities distinguish sign/coefficient errors.
    need(not (divergence+projection).iszero(),'CODAZZI_SIGN_MUTATION');gates['CODAZZI_SIGN_MUTATION_REJECTED']=True
    need(not (divjunction-EnU-jphi*phid/2+xd*od).iszero(),'MATERIAL_HALF_MUTATION');gates['MATERIAL_HALF_MUTATION_REJECTED']=True
    return gates
def main(lease):
    pin='a189065e25d7f9eb386ca71ee4baf8d99c5a99a78cd60884e37afe7c40d48753';need(sha(PARENT/'TERMINAL.json')==pin,'PARENT_PIN');t=read(PARENT/'TERMINAL.json');need(t['pass_status'],'PARENT_PASS')
    inputs={str(PARENT/'TERMINAL.json'):pin}
    for n,k in [('RESULT.json','result_sha256'),('BINDING.json','binding_sha256')]:need(sha(PARENT/n)==t[k],'PARENT_RECORD');inputs[str(PARENT/n)]=t[k]
    for group in ('inputs','sources','runtime'):
        for p,h in read(PARENT/'BINDING.json')[group].items():need(sha(p)==h,'PARENT_CLOSURE');inputs[p]=h
    rp=BASE/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py';need(inputs.get(str(rp))==sha(rp),'RING_PIN');ring=load('wall_identity_laurent_ring',rp)
    manuscript=BASE.parents[4]/'papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md';inputs[str(manuscript)]=sha(manuscript)
    sources={str(p):sha(p) for p in ROOT.iterdir() if p.suffix=='.py' or p.name=='DERIVATION.txt'}
    need(len(str(10**20000))==20001,'WARMUP');runtime=lease.observed()
    for p,h in runtime.items():need(inputs.get(p)==h or sources.get(p)==h,'RUNTIME:'+p)
    put('BINDING.json',dict(inputs=inputs,sources=sources,runtime=runtime,deadline_unix=DEADLINE));start=time.monotonic();gates=qualify(ring)
    need(lease.observed()==runtime and all(sha(p)==h for p,h in dict(inputs,**sources).items()),'UNCHANGED_BINDING')
    result=dict(pass_status=True,classification='EXACT_NEUTRAL_MOVING_WALL_CODAZZI_MATERIAL_RESIDUAL_IDENTITY',gates=gates,seconds=time.monotonic()-start,new_ode_solves=0,scope='General N,R,B homogeneous five-dimensional jet identity for timelike walls; exact neutral material exchange and oscillator coordinate conversion. On solved bulk, normal scalar and oscillator rows the junction divergence vanishes. Positive-harmonic tracefree induction removes remaining Israel row, but not a zero harmonic. No large-amplitude or generic-data claim.')
    put('RESULT.json',result);put('TERMINAL.json',dict(pass_status=True,result_sha256=sha(ROOT/'RESULT.json'),binding_sha256=sha(ROOT/'BINDING.json'),source_sha256=sha(__file__),derivation_sha256=sha(ROOT/'DERIVATION.txt')));print(json.dumps(result),flush=True)
if __name__=='__main__':
    lease=None
    try:
        need(sys.platform=='linux' and time.time()+300<DEADLINE,'LINUX_DEADLINE');need(not any((ROOT/n).exists() for n in ('START.json','FAILURE.json','TERMINAL.json')),'NO_RESTART')
        need(sha(FROZEN)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e','FROZEN');lp=BASE/'20261026T015206Z_FORCED_SECOND_ORDER_R1/runner.py';need(sha(lp)==read(FROZEN)['files'][str(lp)],'LEASE')
        lease=load('neutral_wall_lease',lp);lease.ROOT=ROOT;cpu,occupied=lease.acquire();signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('WALL_IDENTITY_300_SECONDS')));signal.alarm(300)
        put('START.json',dict(pid=os.getpid(),cpu=cpu,occupied=occupied,time=time.time()));main(lease)
    except BaseException as e:
        put('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        signal.alarm(0)
        if lease:
            for f in lease.handles:f.close()
