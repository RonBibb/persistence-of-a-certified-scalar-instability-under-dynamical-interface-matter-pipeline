from fractions import Fraction as F
from interval import I,box
import core

def const(x,N):return [x if isinstance(x,I) else I(x)]+[I(0) for _ in range(N-1)]
def add(*xs):return [sum((x[j] for x in xs),I(0)) for j in range(len(xs[0]))]
def scale(x,s):return [v*s for v in x]
def mul(x,y):return [sum((x[k]*y[j-k] for k in range(j+1)),I(0)) for j in range(len(x))]
def inv(x):
    assert not x[0].contains(0),'JET_ZERO_DIVISOR'
    y=[I(1)/x[0]]+[I(0) for _ in range(len(x)-1)]
    for j in range(1,len(x)):y[j]=-sum((x[k]*y[j-k] for k in range(1,j+1)),I(0))/x[0]
    return y
def rhs(z,mu=None,rep='bg'):
    N=len(z[0]);c=lambda x:const(x,N)
    a,H,P,T=z[:4];a2=mul(a,a);P2=mul(P,P);P3=mul(P2,P);T2=mul(T,T);HT=mul(H,T)
    U=add(c(1),scale(P,-1),scale(P3,4),scale(HT,-4))
    bg=[mul(H,a),add(scale(T2,F(-1,3)),scale(inv(a2),-3)),T,U]
    if rep=='bg':return bg
    psi,f,v=z[4:];psip=add(scale(mul(H,psi),-2),scale(mul(T,f),F(-1,3)))
    if rep=='L':
        fp=add(v,scale(mul(T,psi),-2))
        C=add(c(-1),scale(P2,12),scale(inv(a2),-mu),scale(T2,F(4,3)))
        vp=add(scale(mul(H,v),-4),mul(C,f),scale(mul(U,psi),-2))
    else:
        assert rep=='g'
        fp=v;C=add(c(-1),scale(P2,12),scale(inv(a2),-mu),scale(T2,2))
        E=add(scale(HT,12),scale(add(c(1),scale(P,-1),scale(P3,4)),-4))
        vp=add(scale(mul(H,v),-4),mul(C,f),mul(E,psi))
    return bg+[psip,fp,vp]
def coefficients(y,order,jfun):
    z=[const(v,order+1) for v in y]
    for j in range(order):
        r=jfun(z)
        assert len(r)==len(y) and all(len(v)==order+1 for v in r)
        for x,v in zip(z,r):x[j+1]=v[j]/(j+1)
    return z
def step(y,h,fun,jfun,rates,check_bg=True,order=8):
    assert order>=1 and len(y)==len(rates)
    dt=box(min(F(0),h),max(F(0),h))
    radii=[(I(abs(h))*r).hi for r in rates]
    tube=[v+I(-r,r) for v,r in zip(y,radii)]
    if check_bg:assert all(v.in_exact(*lim) for v,lim in zip(tube[:4],core.LIMITS)),'BACKGROUND_TUBE'
    r=fun(tube)
    assert all(b.strict(v+dt*w) for b,v,w in zip(tube,y,r)),'TUBE_CONTAINMENT'
    start=coefficients(y,order-1,jfun) if order>1 else [[v] for v in y]
    rem=coefficients(tube,order,jfun)
    return [sum((v[j]*h**j for j in range(order)),I(0))+w[order]*h**order for v,w in zip(start,rem)]
def background(n,endpoint,order=8):
    y=[I(x) for x in (1,-2,0,0)];h=endpoint/n
    for j in range(n):
        y=step(y,h,core.bg,lambda z:rhs(z),core.RBG,order=order)
        assert core.ham(y).contains(0),'BACKGROUND_HAMILTONIAN'
    return y
