"""Exact rational endpoints, outward dyadic rounding after each operation."""
from fractions import Fraction as Q
BITS=512
def down(x):
 x=Q(x)
 if not x:return Q(0)
 e=abs(x.numerator).bit_length()-x.denominator.bit_length()-BITS
 step=Q(2**e) if e>=0 else Q(1,2**(-e))
 q=x/step
 return (q.numerator//q.denominator)*step
def up(x):return -down(-Q(x))
class I:
 def __init__(self,a,b=None):
  self.lo=Q(a);self.hi=Q(a if b is None else b)
  if self.lo>self.hi:raise AssertionError('INTERVAL_ORDER')
 @staticmethod
 def cast(x):return x if isinstance(x,I) else I(x)
 @staticmethod
 def out(a,b):return I(down(a),up(b))
 def __add__(self,x):
  x=self.cast(x);return self.out(self.lo+x.lo,self.hi+x.hi)
 __radd__=__add__
 def __neg__(self):return I(-self.hi,-self.lo)
 def __sub__(self,x):return self+-self.cast(x)
 def __rsub__(self,x):return self.cast(x)+-self
 def __mul__(self,x):
  x=self.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)]
  return self.out(min(v),max(v))
 __rmul__=__mul__
 def __truediv__(self,x):
  x=self.cast(x)
  if x.lo<=0<=x.hi:raise AssertionError('DIVISOR_ZERO')
  v=[a/b for a in (self.lo,self.hi) for b in (x.lo,x.hi)]
  return self.out(min(v),max(v))
 def __pow__(self,n):
  if not isinstance(n,int) or n<0:raise AssertionError('POWER')
  y=I(1)
  for _ in range(n):y=y*self
  return y
 def pack(self):return dict(exact_bounds=[str(self.lo),str(self.hi)])

