from fractions import Fraction as F
S=1<<256

def ceildiv(a,b): return -((-a)//b)

class I:
    def __init__(self,x=0,hi=None):
        if hi is not None:
            self.lo,self.hi=x,hi
        else:
            x=F(x); self.lo=x.numerator*S//x.denominator
            self.hi=ceildiv(x.numerator*S,x.denominator)
        assert self.lo<=self.hi
    @staticmethod
    def coerce(x): return x if isinstance(x,I) else I(x)
    def __add__(self,y):
        y=I.coerce(y); return I(self.lo+y.lo,self.hi+y.hi)
    __radd__=__add__
    def __neg__(self): return I(-self.hi,-self.lo)
    def __sub__(self,y): return self+-I.coerce(y)
    def __rsub__(self,y): return I.coerce(y)+-self
    def __mul__(self,y):
        y=I.coerce(y)
        v=[self.lo*y.lo,self.lo*y.hi,self.hi*y.lo,self.hi*y.hi]
        return I(min(v)//S,ceildiv(max(v),S))
    __rmul__=__mul__
    def inverse(self):
        assert not self.lo<=0<=self.hi,'ZERO_DIVISOR'
        return I((S*S)//self.hi,ceildiv(S*S,self.lo))
    def __truediv__(self,y): return self*I.coerce(y).inverse()
    def __rtruediv__(self,y): return I.coerce(y)*self.inverse()
    def bounds(self): return F(self.lo,S),F(self.hi,S)
    def contains(self,y):
        y=I.coerce(y); return self.lo<=y.lo and y.hi<=self.hi
    def strict(self,y): return self.lo<y.lo and y.hi<self.hi
    def in_exact(self,lo,hi):
        a,b=self.bounds(); return F(lo)<=a and b<=F(hi)
    def record(self):
        a,b=self.bounds(); return dict(lo=str(a),hi=str(b),width=str(b-a))

def box(lo,hi): return I(I(lo).lo,I(hi).hi)
def power(x,n):
    result=I(1)
    for _ in range(n): result=result*x
    return result
