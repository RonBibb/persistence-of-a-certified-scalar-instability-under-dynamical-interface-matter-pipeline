"""192-bit fixed-point closed intervals with outward INTEGER rounding only."""
from fractions import Fraction
BITS=192
SCALE=1<<BITS
class I:
    __slots__=('lo','hi')
    def __init__(self,lo,hi=None):
        self.lo=int(lo);self.hi=int(lo if hi is None else hi)
        if self.lo>self.hi:raise ValueError('Reversed interval')
    @classmethod
    def exact(cls,q):
        if isinstance(q,cls):return q
        if isinstance(q,float):raise TypeError('No binary floating scientific inputs')
        q=Fraction(q);n=q.numerator*SCALE;d=q.denominator
        return cls(n//d,-((-n)//d))
    @classmethod
    def endpoints(cls,lo,hi):
        lo,hi=Fraction(lo),Fraction(hi)
        if lo>hi:raise ValueError('Reversed rational interval')
        return cls((lo.numerator*SCALE)//lo.denominator,-((-hi.numerator*SCALE)//hi.denominator))
    def __add__(self,o):
        o=I.exact(o);return I(self.lo+o.lo,self.hi+o.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,o):return self+-I.exact(o)
    def __rsub__(self,o):return I.exact(o)+-self
    def __mul__(self,o):
        if isinstance(o,int):return I(min(self.lo*o,self.hi*o),max(self.lo*o,self.hi*o))
        o=I.exact(o);p=[self.lo*o.lo,self.lo*o.hi,self.hi*o.lo,self.hi*o.hi]
        return I(min(p)//SCALE,-((-max(p))//SCALE))
    __rmul__=__mul__
    def __truediv__(self,o):
        if isinstance(o,int):
            if o==0:raise ZeroDivisionError
            if o<0:return (-self)/(-o)
            return I(self.lo//o,-((-self.hi)//o))
        return self*I.exact(o).reciprocal()
    def reciprocal(self):
        if self.lo<=0<=self.hi:raise ZeroDivisionError('Interval contains zero')
        # Reciprocal decreases on either connected nonzero sign component.
        return I((SCALE*SCALE)//self.hi,-((-(SCALE*SCALE))//self.lo))
    def square(self):
        low=0 if self.lo<=0<=self.hi else min(self.lo*self.lo,self.hi*self.hi)
        high=max(self.lo*self.lo,self.hi*self.hi)
        return I(low//SCALE,-((-high)//SCALE))
    def dump(self):return [str(self.lo),str(self.hi)]
    @classmethod
    def load(cls,v):return cls(int(v[0]),int(v[1]))
    def contains(self,q):
        q=Fraction(q);return self.lo*q.denominator<=q.numerator*SCALE<=self.hi*q.denominator
    def inside(self,outer):return outer.lo<self.lo and self.hi<outer.hi
    def hull(self,o):return I(min(self.lo,o.lo),max(self.hi,o.hi))
    def pad(self):
        eps=(self.hi-self.lo+7)//8+(1<<(BITS-160))
        return I(self.lo-eps,self.hi+eps)
    def rational_bounds(self):return [str(Fraction(self.lo,SCALE)),str(Fraction(self.hi,SCALE))]
