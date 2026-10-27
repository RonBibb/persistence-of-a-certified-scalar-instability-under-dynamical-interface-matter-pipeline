import sys,json,math,signal
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(HERE))
import core
M=7;N=8
class P:
    def __init__(self,x=0):
        if isinstance(x,P):self.c=x.c
        elif isinstance(x,(tuple,list)):self.c=tuple(F(v) for v in x)+tuple(F(0) for _ in range(M-len(x)))
        else:self.c=(F(x),)+tuple(F(0) for _ in range(M-1))
        assert len(self.c)==M
    def __add__(self,o):
        o=P(o);return P([a+b for a,b in zip(self.c,o.c)])
    __radd__=__add__
    def __neg__(self):return P([-a for a in self.c])
    def __sub__(self,o):return self+-P(o)
    def __rsub__(self,o):return P(o)+-self
    def __mul__(self,o):
        o=P(o);return P([sum((self.c[k]*o.c[j-k] for k in range(j+1)),F(0)) for j in range(M)])
    __rmul__=__mul__
    def inverse(self):
        assert self.c[0]!=0
        y=[1/self.c[0]]+[F(0)]*(M-1)
        for j in range(1,M):y[j]=-sum((self.c[k]*y[j-k] for k in range(1,j+1)),F(0))/self.c[0]
        return P(y)
    def __truediv__(self,o):return self*P(o).inverse()
    def __rtruediv__(self,o):return P(o)*self.inverse()
    def shift(self,j):return P([F(0)]*j+list(self.c[:M-j])) if j<M else P(0)
def c(x):return [P(x)]+[P(0) for _ in range(N-1)]
def add(*xs):return [sum((x[j] for x in xs),P(0)) for j in range(N)]
def sc(x,s):return [v*s for v in x]
def mul(x,y):return [sum((x[k]*y[j-k] for k in range(j+1)),P(0)) for j in range(N)]
def inv(x):
    y=[1/x[0]]+[P(0) for _ in range(N-1)]
    for j in range(1,N):y[j]=-sum((x[k]*y[j-k] for k in range(1,j+1)),P(0))/x[0]
    return y
def rhs(z,mu):
    a,H,Phi,T,psi,f,g=z
    a2=mul(a,a);P2=mul(Phi,Phi);P3=mul(P2,Phi);T2=mul(T,T);HT=mul(H,T)
    vp=add(c(1),sc(Phi,-1),sc(P3,4))
    C=add(c(-1),sc(P2,12),sc(inv(a2),-mu),sc(T2,2))
    E=add(sc(HT,12),sc(vp,-4))
    return [mul(H,a),add(sc(T2,F(-1,3)),sc(inv(a2),-3)),T,
        add(vp,sc(HT,-4)),add(sc(mul(H,psi),-2),sc(mul(T,f),F(-1,3))),
        g,add(sc(mul(H,g),-4),mul(C,f),mul(E,psi))]
def boundary(lam,B):
    z=[c(v) for v in (1,-2,0,0,1,-3*lam,B)]
    for j in range(N-1):
        v=rhs(z,lam-12)
        for a,b in zip(z,v):a[j+1]=b[j]/(j+1)
    even=sum((z[5][j].shift(j) for j in range(0,N,2)),P(0))
    odd=sum((z[5][j].shift(j-1) for j in range(1,N,2)),P(0))
    return even,odd,z
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3) and core.digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    assert (P([1,1])*P([1,1]).inverse()).c==P(1).c,'POLY_RECIPROCAL'
    e,o,z=boundary(P(0),P(0))
    assert [z[5][j].c[0]*math.factorial(j) for j in (2,3,4)]==[-4,-72,-1256],'OLD_JET'
    lam=[F(0)]*M;B=[F(0)]*M;stages=[]
    for j in (2,4,6):
        e,o,z=boundary(P(lam),P(B));lam[j]=e.c[j]/3;B[j]=-o.c[j]
        e,o,z=boundary(P(lam),P(B))
        assert all(v==0 for v in e.c[:j+1]) and all(v==0 for v in o.c[:j+1]),'BOUNDARY_CANCELLATION'
        stages.append(dict(order=j,lambda_coefficient=str(lam[j]),B_coefficient=str(B[j]),even=[str(v) for v in e.c],odd_divided=[str(v) for v in o.c]))
    assert lam[2]==F(-2,3) and lam[4]==F(20,9) and B[2]==12,'ACCEPTED_LOWER_ORDERS'
    C6=-lam[6]/64;C4=-lam[4]/16
    assert all(core.digest(HERE/p)==h for p,h in ad['sources'].items())
    core.save('RESULT.json',dict(classification='CERTIFIED_LOCAL_SIXTH_ORDER_COEFFICIENT',
        lambda_halfwidth=[str(v) for v in lam],central_g_halfwidth=[str(v) for v in B],
        gap_fullwidth=dict(D2='1/6',D4=str(C4),D6=str(C6)),stages=stages,
        radial_order=7,halfwidth_order=6,finite_width_remainder_certified=False,
        retrospective_to_existing_sixth_order_diagnostics=True,all_gates_passed=True))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda s,f:(_ for _ in ()).throw(TimeoutError('590s cap')));signal.alarm(590)
    try:main()
    except BaseException as e:core.save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
