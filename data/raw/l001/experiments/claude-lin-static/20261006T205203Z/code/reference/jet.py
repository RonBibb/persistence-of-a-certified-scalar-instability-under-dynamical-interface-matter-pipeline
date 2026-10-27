"""Truncated spatial Taylor algebra; coefficients, not derivatives."""
import mpmath as mp
from math import comb

class Jet:
    order = 7
    def __init__(self, value=0):
        if isinstance(value, Jet): value=value.c
        if not isinstance(value,(list,tuple)): value=[value]
        self.c=[mp.mpf(v) for v in value[:self.order+1]]
        self.c += [mp.mpf(0)]*(self.order+1-len(self.c))
    def __add__(self, other):
        other=Jet(other); return Jet([a+b for a,b in zip(self.c,other.c)])
    __radd__=__add__
    def __neg__(self): return Jet([-a for a in self.c])
    def __sub__(self,other): return self+-Jet(other)
    def __rsub__(self,other): return Jet(other)+-self
    def __mul__(self,other):
        other=Jet(other)
        return Jet([mp.fsum(self.c[j]*other.c[i-j] for j in range(i+1)) for i in range(self.order+1)])
    __rmul__=__mul__
    def __truediv__(self,other): return self*(1/mp.mpf(other))
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        r=Jet(1)
        for _ in range(n): r=r*self
        return r
    def exp(self):
        c=[mp.exp(self.c[0])]
        for i in range(1,self.order+1): c.append(mp.fsum(j*self.c[j]*c[i-j] for j in range(1,i+1))/i)
        return Jet(c)
    def d(self): return Jet([(i+1)*self.c[i+1] for i in range(self.order)])
    def val(self): return self.c[0]

def shift(c,z,n):
    return [mp.fsum(c[j]*comb(j,i)*z**(j-i) for j in range(i,len(c))) for i in range(n+1)]

def horner(c,z):
    v=mp.mpf(0)
    for a in reversed(c): v=v*z+a
    return v

def exp_series(c):
    r=[mp.exp(c[0])]
    for n in range(1,len(c)): r.append(mp.fsum(j*c[j]*r[n-j] for j in range(1,n+1))/n)
    return r
