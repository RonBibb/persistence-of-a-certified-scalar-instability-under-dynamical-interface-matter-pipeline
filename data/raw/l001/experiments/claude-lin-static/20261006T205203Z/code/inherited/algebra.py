"""Truncated ordinary Taylor algebra with outward Arb coefficients."""
import math
from flint import arb, fmpq
from series import bounds, interval, power


class Taylor:
    def __init__(self, values):
        self.c = [v if isinstance(v, arb) else arb(v) for v in values]
        self.N = len(self.c)-1
    def lift(self, x):
        if isinstance(x, Taylor):
            assert x.N == self.N
            return x
        return Taylor([x]+[0]*self.N)
    def __add__(self, x):
        x = self.lift(x)
        return Taylor([a+b for a,b in zip(self.c,x.c)])
    __radd__ = __add__
    def __neg__(self): return Taylor([-v for v in self.c])
    def __sub__(self,x): return self+-self.lift(x)
    def __rsub__(self,x): return self.lift(x)+-self
    def __mul__(self,x):
        x=self.lift(x)
        return Taylor([sum((self.c[j]*x.c[n-j] for j in range(n+1)),arb(0)) for n in range(self.N+1)])
    __rmul__=__mul__
    def reciprocal(self):
        out=[1/self.c[0]]
        for n in range(1,self.N+1):
            out.append(-sum((self.c[j]*out[n-j] for j in range(1,n+1)),arb(0))/self.c[0])
        return Taylor(out)
    def __truediv__(self,x):
        if isinstance(x,Taylor): return self*x.reciprocal()
        return Taylor([v/x for v in self.c])
    def __rtruediv__(self,x): return self.reciprocal()*x
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        out=self.lift(1)
        for _ in range(n): out=out*self
        return out
    def exp(self):
        out=[self.c[0].exp()]
        for n in range(1,self.N+1):
            out.append(sum((j*self.c[j]*out[n-j] for j in range(1,n+1)),arb(0))/n)
        return Taylor(out)
    def e2(self):
        e1=self.exp(); e1.c[0]=self.c[0]+stable_e2(self.c[0])
        out=[stable_e2(self.c[0])]
        for n in range(1,self.N+1):
            out.append(sum((j*self.c[j]*e1.c[n-j] for j in range(1,n+1)),arb(0))/n)
        return Taylor(out)
    def e1(self): return self+self.e2()


def stable_e2(x):
    """exp(x)-1-x; degree 14 plus rigorous scalar Lagrange remainder."""
    lo,hi=bounds(x); B=max(abs(lo),abs(hi))
    if B>fmpq(1,10): raise ArithmeticError('Frozen E2 argument bound 1/10 exceeded')
    v=arb(fmpq(1,math.factorial(14)))
    for n in range(13,1,-1): v=v*x+fmpq(1,math.factorial(n))
    v=x*x*v
    R=(arb(B).exp()*arb(B**15)/math.factorial(15)).upper().fmpq()
    return v+interval(-R,R)


def e2(x): return x.e2() if isinstance(x,Taylor) else stable_e2(x)
def e1(x): return x+e2(x)
def exp(x): return x.exp()
def ev(coeff,x,der=0):
    v=x*0
    for j in range(len(coeff)-1,der-1,-1):
        v=v*x+coeff[j]*math.prod(range(j-der+1,j+1))
    return v
def maxabs(x):
    lo,hi=bounds(x);return max(abs(lo),abs(hi))


def hermite_inverse():
    """Exact degree-seven unit-interval Hermite inverse, not a numeric fit."""
    a=[]
    for side in (0,1):
        for der in range(4):
            row=[fmpq(math.prod(range(j-der+1,j+1))*side**(j-der)) if j>=der else fmpq(0) for j in range(8)]
            row += [fmpq(int(len(a)==j)) for j in range(8)]
            a.append(row)
    for k in range(8):
        pivot=next(i for i in range(k,8) if a[i][k])
        a[k],a[pivot]=a[pivot],a[k]
        d=a[k][k];a[k]=[v/d for v in a[k]]
        for i in range(8):
            if i!=k:
                d=a[i][k];a[i]=[v-d*w for v,w in zip(a[i],a[k])]
    assert all(a[i][j]==int(i==j) for i in range(8) for j in range(8))
    return [row[8:] for row in a]
