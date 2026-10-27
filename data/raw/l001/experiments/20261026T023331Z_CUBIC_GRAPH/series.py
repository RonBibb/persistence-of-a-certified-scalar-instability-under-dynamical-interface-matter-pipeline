"""Degree-three direct S7 extraction; generic exact polynomial/Arb scalars."""
from math import factorial
from fractions import Fraction

class S:
    def __init__(self,values):self.a=tuple((list(values)+[0]*4)[:4])
    def cast(self,x):return x if isinstance(x,S) else S([x])
    def __add__(self,x):return S([a+b for a,b in zip(self.a,self.cast(x).a)])
    __radd__=__add__
    def __neg__(self):return S([-x for x in self.a])
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        b=self.cast(x).a
        return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(4)])
    __rmul__=__mul__
    def __truediv__(self,n):return S([0 if isinstance(v,int) and v==0 else Fraction(v,n) if isinstance(v,int) else v/n for v in self.a])
    def dt(self,r):return S([a*(n*r) for n,a in enumerate(self.a)])
    def expzero(self):
        # Callers construct an exactly zero constant term.
        result=S([1]);power=S([1])
        for n in range(1,4):power=power*self;result=result+power/factorial(n)
        return result

def extract(w,sigma,boost=True,affine=True):
    E,h,x,y,p,p2,H,Hp,u,c2,T,Tp,f,f2,g,chi,chi2,n=[w[k] for k in
        ('E','h','xi1','xi2','p1','p2','H','Hp','u','c2','T','Tp','f1','f2','g1','chi1','chi2','n')]
    r=-6*h
    A=H*x+p;B=H*y+Hp*x*x/2+p2+x*u
    L=S([0,A,B,w.get('L3',0)])
    b=S([0,-2*p,c2-2*p2-2*x*u,w.get('b3',0)])
    St=S([0,r*x,2*r*y,3*r*w.get('xi3',0)])
    invN=(-L).expzero()*E
    v=(b-L).expzero()*E*St
    v2=v*v
    invone=1+v2 if boost else S([1])
    invsqrt=1+v2/2 if boost else S([1])
    fixed=S([-h,-3*r*p,2*r*(c2-3*p2)-3*r*x*u,w.get('fixed3',0)])
    geom=invN*invsqrt*(v.dt(r)*invone+v*fixed)*sigma
    dphi=S([0,T*x+f,T*y+Tp*x*x/2+f2+x*g,w.get('phi3',0)])
    material=1-dphi/1000 if affine else (-dphi/1000).expzero()
    rho=S([0,n])*material*(-6*L).expzero()
    chid=S([0,chi,chi2,w.get('chi3',0)]).dt(r)
    kinetic=chid*chid*invN*invN*invone/2
    return {'geometric':geom,'current':-rho,'oscillator':-kinetic,'total':geom-rho-kinetic}
