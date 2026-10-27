"""Private n9 R1 ring: unchanged arithmetic, fixed200k multiplication-term cap."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'
s=importlib.util.spec_from_file_location('source_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT
NAMES=('g','H','T','Phi','e','p','f','m2','h'); N=len(NAMES); ZERO=(0,)*N

class P:
    """Bounded sparse rational polynomial; lex order, no symbolic dependency."""
    def __init__(self,v=0):
        if isinstance(v,P): self.t=dict(v.t)
        elif isinstance(v,dict): self.t={a:Q(b) for a,b in v.items() if b}
        else: self.t={} if not v else {ZERO:Q(v)}
    @staticmethod
    def cast(v): return v if isinstance(v,P) else P(v)
    def __add__(self,v):
        if not isinstance(v,(P,int,Q)): return NotImplemented
        v=P.cast(v); d=dict(self.t)
        for a,b in v.t.items(): d[a]=d.get(a,Q(0))+b
        return P(d)
    __radd__=__add__
    def __neg__(self): return P({a:-b for a,b in self.t.items()})
    def __sub__(self,v):
        if not isinstance(v,(P,int,Q)): return NotImplemented
        return self+-P.cast(v)
    def __rsub__(self,v): return P.cast(v)+-self
    def __mul__(self,v):
        if not isinstance(v,(P,int,Q)): return NotImplemented
        v=P.cast(v); d={}
        c.need(len(self.t)*len(v.t)<=1000000,'POLYNOMIAL_PRODUCT_CAP')
        for a,b in self.t.items():
            for q,r in v.t.items():
                key=tuple(x+y for x,y in zip(a,q)); d[key]=d.get(key,Q(0))+b*r
        c.need(len(d)<=200000,'POLYNOMIAL_TERM_CAP'); return P(d)
    __rmul__=__mul__
    def __truediv__(self,v):
        c.need(isinstance(v,(int,Q)) and v!=0,'SCALAR_RATIONAL_DIVISION_ONLY')
        return self*(1/Q(v))
    def __pow__(self,n):
        c.need(isinstance(n,int) and n>=0,'POWER_DOMAIN'); r=P(1)
        for _ in range(n): r=r*self
        return r
    def derivative(self,j):
        d={}
        for a,b in self.t.items():
            if a[j]:
                q=list(a); q[j]-=1; d[tuple(q)]=b*a[j]
        return P(d)
    def iszero(self): return not self.t
    def pack(self): return [{'powers':list(a),'coefficient':str(b)} for a,b in sorted(self.t.items(),reverse=True)]

def variable(j):
    a=[0]*N; a[j]=1; return P({tuple(a):Q(1)})
def initialize():
    global g,H,T,Phi,e,p,f,m,h,mu1,R,mu2,Tp,Hp,u,B0,gp,DERIV
    g,H,T,Phi,e,p,f,m,h=[variable(j) for j in range(N)]
    mu1=-18*h*h; R=-6*h; mu2=-108*h*h
    Tp=m*Phi-4*H*T; Hp=-T*T/3-h*h*e
    u=-2*H*p-T*f/3; B0=12*H*T-4*m*Phi
    gp=-4*H*g+(m-mu1*e+2*T*T)*f+B0*p
    DERIV=(gp,Hp,Tp,T,-2*H*e,u,g,P(0),P(0))
def ds(v): return sum((v.derivative(j)*q for j,q in enumerate(DERIV)),P(0))
def divide(v,divisors):
    """Return exact identity v=sum(q_i*d_i)+remainder, not a sampled test."""
    q=[P(0) for _ in divisors]; rem=P(0); work=P(v); count=0
    while work.t:
        count+=1; c.need(count<100000,'REDUCTION_CAP')
        a=max(work.t); b=work.t[a]; reduced=False
        for j,d in enumerate(divisors):
            da=max(d.t); db=d.t[da]
            if all(x>=y for x,y in zip(a,da)):
                term=P({tuple(x-y for x,y in zip(a,da)):b/db})
                q[j]=q[j]+term; work=work-term*d; reduced=True; break
        if not reduced:
            term=P({a:b}); rem=rem+term; work=work-term
    c.need((v-sum((a*b for a,b in zip(q,divisors)),P(0))-rem).iszero(),'REDUCTION_RECONSTRUCTION')
    return q,rem
