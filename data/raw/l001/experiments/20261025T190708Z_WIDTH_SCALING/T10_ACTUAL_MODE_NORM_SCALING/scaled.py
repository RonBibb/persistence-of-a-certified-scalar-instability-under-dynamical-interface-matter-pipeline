from fractions import Fraction as F
from interval import I,box,power
import core,taylor
LIMITS=[(F(9,10),F(11,10)),(F(-21,10),F(-19,10)),(F(-1,100),F(1,100)),(F(-3,2),F(3,2))]
RBG=[I(F(3,100)),I(F(1,20)),I(F(1,1000)),I(2)]
RATES=RBG+[I(F(1,5)),I(10),I(10)]
def bg(y,d):
    a,H,P,t=y[:4];T=d*t
    return [d*H*a,d*(-T*T/3-3/(a*a)),d*d*t,1-P+4*power(P,3)-4*H*T]
def ham(y,d):
    a,H,P,t=y[:4]
    return H*H-1-d*d*t*t/12+(P-P*P/2+power(P,4))/6-3/(a*a)
def rhs(y,d,alpha,rep):
    a,H,P,t,psi,Fp,v=y;U=bg(y,d)[3];mu=-12+d*d*alpha
    psip=-2*d*H*psi-power(d,4)*t*Fp/3
    if rep=='G':
        return bg(y,d)+[psip,v-2*t*psi,
            -4*d*H*v+d*d*(-1+12*P*P-mu/(a*a)+4*d*d*t*t/3)*Fp-2*U*psi]
    assert rep=='W'
    return bg(y,d)+[psip,v,-4*d*H*v+d*d*(-1+12*P*P-mu/(a*a)+2*d*d*t*t)*Fp+(12*d*H*t-4*(1-P+4*power(P,3)))*psi]
def asG(y,rep):
    return y if rep=='G' else y[:6]+[y[6]+2*y[3]*y[4]]
def constraint(y,d,alpha,rep):
    a,H,P,t,psi,Fp,G=asG(y,rep)
    return t*G-bg(y,d)[3]*Fp-3*alpha*psi/(a*a)
def jrhs(z,d,alpha=None,rep='bg'):
    N=len(z[0]);c=lambda x:taylor.const(x,N)
    add,mul,sc,inv=taylor.add,taylor.mul,taylor.scale,taylor.inv
    a,H,P,t=z[:4];a2=mul(a,a);P2=mul(P,P);P3=mul(P2,P);t2=mul(t,t);Ht=mul(H,t)
    U=add(c(1),sc(P,-1),sc(P3,4),sc(Ht,-4*d))
    b=[sc(mul(H,a),d),sc(add(sc(t2,-d*d/3),sc(inv(a2),-3)),d),sc(t,d*d),U]
    if rep=='bg':return b
    psi,Fp,v=z[4:];mu=-12+d*d*alpha
    pp=add(sc(mul(H,psi),-2*d),sc(mul(t,Fp),-power(d,4)/3))
    if rep=='G':
        fp=add(v,sc(mul(t,psi),-2));C=add(c(-1),sc(P2,12),sc(inv(a2),-mu),sc(t2,4*d*d/3))
        vp=add(sc(mul(H,v),-4*d),sc(mul(C,Fp),d*d),sc(mul(U,psi),-2))
    else:
        assert rep=='W'
        fp=v;C=add(c(-1),sc(P2,12),sc(inv(a2),-mu),sc(t2,2*d*d))
        E=add(sc(Ht,12*d),sc(add(c(1),sc(P,-1),sc(P3,4)),-4))
        vp=add(sc(mul(H,v),-4*d),sc(mul(C,Fp),d*d),mul(E,psi))
    return b+[pp,fp,vp]
def step(y,h,d,alpha=None,rep='bg'):
    rates=RBG if rep=='bg' else RATES
    rr=[(I(abs(h))*v).hi for v in rates];tube=[v+I(-r,r) for v,r in zip(y,rr)]
    assert all(v.in_exact(*lim) for v,lim in zip(tube[:4],LIMITS)),'SCALED_BACKGROUND_BOX'
    assert bg(tube,d)[3].lo>0,'SINGLE_TURN_U'
    fun=(lambda z:bg(z,d)) if rep=='bg' else (lambda z:rhs(z,d,alpha,rep))
    return taylor.step(y,h,fun,lambda z:jrhs(z,d,alpha,rep),rates,False,8)
def background(n,endpoint,d):
    y=[I(x) for x in (1,-2,0,0)]
    for j in range(n):
        y=step(y,F(endpoint,n),d)
        assert ham(y,d).contains(0),'SCALED_HAMILTONIAN'
    return y
