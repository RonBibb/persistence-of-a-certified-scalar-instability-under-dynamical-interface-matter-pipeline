"""Ordinary degree-eight series over a commutative exact coefficient algebra."""
from fractions import Fraction as Q
def div(a,n):return Q(a,n) if isinstance(a,int) else a/n
class S:
 def __init__(self,a):self.a=tuple((list(a)+[0]*9)[:9])
 @staticmethod
 def cast(a):return a if isinstance(a,S) else S([a])
 def __add__(self,a):return S([x+y for x,y in zip(self.a,self.cast(a).a)])
 __radd__=__add__
 def __neg__(self):return S([-x for x in self.a])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):
  b=self.cast(a).a;return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(9)])
 __rmul__=__mul__
 def __truediv__(self,n):return S([div(x,n) for x in self.a])
 def dt(self,r):return S([n*r*x for n,x in enumerate(self.a)])
 def expzero(self):
  out=[1]
  for n in range(1,9):out.append(div(sum((j*self.a[j]*out[n-j] for j in range(1,n+1)),0),n))
  return S(out)
