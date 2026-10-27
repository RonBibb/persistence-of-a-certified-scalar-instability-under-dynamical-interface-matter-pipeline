"""Direct dual-number linearization of the original time-jet equations.

Independent of the reduced beta formula. No predecessor module is imported.
Taylor coefficients are normalized spatial derivatives, through order five.
"""
import math
from flint import arb,fmpq
from series import mul as convolution


class Dual:
    def __init__(self,v=0,d=0):
        self.v=v if isinstance(v,arb) else arb(v)
        self.d=d if isinstance(d,arb) else arb(d)
    def __add__(self,o):
        o=asdual(o);return Dual(self.v+o.v,self.d+o.d)
    __radd__=__add__
    def __neg__(self):return Dual(-self.v,-self.d)
    def __sub__(self,o):return self+-asdual(o)
    def __rsub__(self,o):return asdual(o)+-self
    def __mul__(self,o):
        o=asdual(o);return Dual(self.v*o.v,self.d*o.v+self.v*o.d)
    __rmul__=__mul__
    def __truediv__(self,o):
        o=asdual(o);return Dual(self.v/o.v,(self.d*o.v-self.v*o.d)/(o.v*o.v))
    def exp(self):
        z=self.v.exp();return Dual(z,z*self.d)


def asdual(x):return x if isinstance(x,Dual) else Dual(x)
def con(x):return [asdual(x)]+[Dual() for _ in range(5)]
def add(*rows):return [sum((r[j] for r in rows),Dual()) for j in range(6)]
def scale(r,c):return [v*c for v in r]
def mul(a,b):return [sum((a[j]*b[n-j] for j in range(n+1)),Dual()) for n in range(6)]
def der(a):return [(j+1)*a[j+1] for j in range(5)]+[Dual()]
def truncate(a):return a[:4]+[Dual(),Dual()]
def exp_series(a):
    out=[a[0].exp()]
    for n in range(1,6):out.append(sum((j*a[j]*out[n-j] for j in range(1,n+1)),Dual())/n)
    return out


def field_jets(bg,h,v,fifth,m):
    W,H,P,T,q=bg
    c=[[x] for x in (W,H,P,T,q,h,v)]
    for n in range(5):
        w,hh,p,t,qq,u,vv=c
        rhs=[hh[n],-convolution(t,t,n)/3-qq[n],t[n],m*p[n]-4*convolution(hh,t,n),
             -2*convolution(hh,qq,n),vv[n],-4*convolution(hh,vv,n)-2*convolution(qq,u,n)]
        for row,value in zip(c,rhs):row.append(value/(n+1))
    A=[Dual(c[0][j],c[5][j]) for j in range(6)]
    ell=[Dual() for _ in range(6)]
    phi=[Dual(c[2][j],arb(fifth)/math.factorial(5) if j==5 else 0) for j in range(6)]
    return A,ell,phi


def rows(bg,h,v,fifth,k,m,cwall):
    A,e,f=field_jets(bg,h,v,fifth,m)
    a,b,t=map(der,(A,e,f));aa,bb,tt=map(der,(a,b,t))
    fac=exp_series(scale(A,2));rad=exp_series(scale(e,-2));curv=scale(exp_series(scale(A,-2)),k)
    potential=add(con(-6),scale(mul(f,f),m/2))
    TA=add(aa,scale(mul(a,a),4),scale(mul(b,a),-1))
    TB=add(scale(aa,4),scale(mul(a,a),4),scale(mul(b,a),-4),mul(t,t))
    TC=add(tt,mul(add(scale(a,4),scale(b,-1)),t))
    SA=add(mul(rad,TA),scale(curv,-2),scale(potential,arb(fmpq(2,3))))
    SB=add(mul(rad,TB),scale(potential,arb(fmpq(2,3))))
    SC=add(mul(rad,TC),scale(f,-m))
    second=[mul(fac,s) for s in (SA,SB,SC)]
    U,V,F=map(truncate,second);up,vp,fp=map(der,(U,V,F));upp,vpp,fpp=map(der,(up,vp,fp))
    DTA=add(upp,scale(mul(a,up),8),scale(mul(vp,a),-1),scale(mul(b,up),-1))
    DTB=add(scale(upp,4),scale(mul(a,up),8),scale(mul(vp,a),-4),scale(mul(b,up),-4),scale(mul(t,fp),2))
    DTC=add(fpp,mul(add(scale(up,4),scale(vp,-1)),t),mul(add(scale(a,4),scale(b,-1)),fp))
    DS_A=add(mul(rad,add(DTA,scale(mul(V,TA),-2))),scale(mul(curv,U),4),scale(mul(f,F),2*m/3))
    DS_B=add(mul(rad,add(DTB,scale(mul(V,TB),-2))),scale(mul(f,F),2*m/3))
    DS_C=add(mul(rad,add(DTC,scale(mul(V,TC),-2))),scale(F,-m))
    A4=add(scale(mul(V,U),-2),scale(U,-4*k),scale(mul(U,U),-2),mul(fac,DS_A))
    E4=add(scale(mul(U,V),-2),scale(V,-4*k),scale(mul(V,V),-2),mul(fac,DS_B))
    F4=add(scale(mul(U,F),-2),scale(mul(V,F),-2),scale(F,-4*k),mul(fac,DS_C))
    A2,E2,F2=second
    R4=F4[1]-E4[0]*f[1]-6*E2[0]*F2[1]+3*E2[0]*E2[0]*f[1]-cwall*F4[0]
    I4=A4[1]-E4[0]*A[1]-6*E2[0]*A2[1]+3*E2[0]*E2[0]*A[1]+bg[3]*F4[0]/3
    R2=F2[1]-E2[0]*f[1]-cwall*F2[0]
    alpha4=(4*bg[0]).exp()
    return {'R4':R4.d/alpha4,'I4':I4.d/alpha4,'R2':R2.d/(2*bg[0]).exp()}
