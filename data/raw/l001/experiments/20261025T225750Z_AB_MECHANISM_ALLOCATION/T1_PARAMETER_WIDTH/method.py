"""Fourth parameter derivatives, scaled by s=1/100, with rigorous spatial remainders."""
from fractions import Fraction as F
from interval import I,box,power
import core,taylor,scaled
PORDER=4
SCALE=F(1,100)
CONTEXT={}
class Jet:
    def __init__(self,c):
        self.c=list(c);self.n=len(self.c)
        assert self.n>=1
    def cast(self,o):
        if isinstance(o,Jet):
            assert o.n==self.n
            return o
        z=self.c[0]*0
        return Jet([z+o]+[z]*(self.n-1))
    def __add__(self,o):
        o=self.cast(o);return Jet([a+b for a,b in zip(self.c,o.c)])
    __radd__=__add__
    def __neg__(self):return Jet([-a for a in self.c])
    def __sub__(self,o):return self+-self.cast(o)
    def __rsub__(self,o):return self.cast(o)+-self
    def __mul__(self,o):
        o=self.cast(o);z=self.c[0]*0
        return Jet([sum((self.c[k]*o.c[j-k] for k in range(j+1)),z) for j in range(self.n)])
    __rmul__=__mul__
    def inverse(self):
        z=self.c[0]*0
        out=[1/self.c[0]]+[z]*(self.n-1)
        for j in range(1,self.n):
            out[j]=-sum((self.c[k]*out[j-k] for k in range(1,j+1)),z)/self.c[0]
        return Jet(out)
    def __truediv__(self,o):return self*self.cast(o).inverse()
    def __rtruediv__(self,o):return self.cast(o)*self.inverse()
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        out=self.cast(1)
        for _ in range(n):out=out*self
        return out
def seed(q):return Jet([q,I(SCALE),I(0),I(0),I(0)])
def constant(x):return Jet([I(x)]+[I(0)]*4)
def group(y):return [Jet(y[i:i+5]) for i in range(0,len(y),5)]
def flatten(y):return [v for a in y for v in a.c]
def alpha(d,beta):return -F(2,3)+F(20,9)*d**2+beta*d**4
def equations(y,d,beta,rep):
    a,H,P,t=y[:4]
    U=1-P+4*P**3-4*H*d*t
    bg=[d*H*a,d*(-d*d*t*t/3-3/(a*a)),d*d*t,U]
    if rep=='bg':return bg
    psi,Fp,v=y[4:];mu=-12+d*d*alpha(d,beta)
    pp=-2*d*H*psi-d**4*t*Fp/3
    if rep=='G':
        return bg+[pp,v-2*t*psi,-4*d*H*v+d*d*(-1+12*P*P-mu/(a*a)+F(4,3)*d*d*t*t)*Fp-2*U*psi]
    assert rep=='W'
    return bg+[pp,v,-4*d*H*v+d*d*(-1+12*P*P-mu/(a*a)+2*d*d*t*t)*Fp+(12*d*H*t-4*(1-P+4*P**3))*psi]
def rhs(y,q,beta,rep):return flatten(equations(group(y),seed(q),beta,rep))
def jrhs(z,q,beta,rep):
    n=len(z[0]);sj=lambda x:Jet([x]+[I(0)]*(n-1))
    y=[Jet([Jet(z[i+k]) for k in range(5)]) for i in range(0,len(z),5)]
    d=Jet([sj(q),sj(I(SCALE)),sj(I(0)),sj(I(0)),sj(I(0))])
    return [v.c for a in equations(y,d,beta,rep) for v in a.c]
def ham(y,q):
    a,H,P,t=group(y)[:4];d=seed(q)
    return H*H-1-d*d*t*t/12+(P-P*P/2+P**4)/6-3/(a*a)
def constraint(y,q,beta,rep):
    a,H,P,t,psi,Fp,v=group(y);d=seed(q);U=1-P+4*P**3-4*H*d*t
    G=v if rep=='G' else v+2*t*psi
    return t*G-U*Fp-3*alpha(d,beta)*psi/(a*a)
def rates(rep):
    base=scaled.RBG if rep=='bg' else scaled.RATES
    return [b*f for b in base for f in (1,2,1,1,1)]
def step(y,h,q,beta,rep,n):
    rr=[(I(abs(h))*r).hi for r in rates(rep)]
    tube=[v+I(-r,r) for v,r in zip(y,rr)]
    vals=[tube[5*i] for i in range(4)]
    assert all(v.in_exact(*lim) for v,lim in zip(vals,scaled.LIMITS)),'DERIVATIVE_BACKGROUND_BOX'
    assert scaled.bg(vals,q)[3].lo>0,'SINGLE_TURN_U'
    return taylor.step(y,h,lambda v:rhs(v,q,beta,rep),
        lambda z:jrhs(z,q,beta,rep),rates(rep),False,8)
def background(n,endpoint,q):
    y=flatten([constant(v) for v in (1,-2,0,0)])
    for j in range(n):
        CONTEXT.update(phase='background',endpoint=endpoint,n=n,step=j+1)
        y=step(y,F(endpoint,n),q,F(0),'bg',n)
        assert all(v.contains(0) for v in ham(y,q).c),'PARAMETER_HAMILTONIAN'
    return y
def propagate(n,q,beta,rep,progress=None):
    low=background(n,-1,q);up=background(n,1,q)
    a,H,P,t=group(low);d=seed(q)
    assert t.c[0].hi<0 and group(up)[3].c[0].lo>0,'ENDPOINT_TURN_SIGNS'
    G=3*alpha(d,beta)/(a*a*t)
    y=low+flatten([constant(1),constant(0),G if rep=='G' else G-2*t])
    for j in range(2*n):
        CONTEXT.update(phase='profile',n=n,representation=rep,step=j+1)
        y=step(y,F(1,n),q,beta,rep,n)
        assert all(v.contains(0) for v in constraint(y,q,beta,rep).c),'PARAMETER_CONSTRAINT'
    assert all(v.contains(0) for v in ham(y,q).c),'UPPER_HAMILTONIAN'
    assert all(core.overlap(a,b) for a,b in zip(y[:20],up)),'BACKGROUND_ENDPOINT_OVERLAP'
    return dict(lower=low,upper_background=up,upper=y)
