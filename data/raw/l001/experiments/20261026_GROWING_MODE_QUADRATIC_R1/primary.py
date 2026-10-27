"""Adapted neutral growing-mode quadratic engine. Temporal source constants
are explicit parameters; validated integration mechanics inherited unchanged.
No writes or computation at import.
"""
"""Polynomial-E augmented Eulerian flow, order-five validated Taylor steps.

Canonical state: W,H,Phi,T,E,p1,f1,g1,p2_part,f2_part,g2_part,
p2_hom,f2_hom,g2_hom. No initializer, shooting, or scientific execution here.
"""
from fractions import Fraction
from flint import arb, fmpq

ORDER = 5
STATE_SIZE = 14


def exact(value):
    if isinstance(value, arb):
        return value
    if isinstance(value, fmpq):
        return arb(value)
    if isinstance(value, float):
        raise TypeError('Exact input required')
    q = Fraction(value)
    return arb(fmpq(q.numerator, q.denominator))


def bounds(value):
    return value.lower().fmpq(), value.upper().fmpq()


def interval(lo, hi):
    if lo > hi:
        raise ValueError('Reversed interval')
    return arb((lo + hi) / 2, (hi - lo) / 2)


def hull(x, y):
    a, b = bounds(x)
    c, d = bounds(y)
    return interval(min(a, c), max(b, d))


def physical(y):
    if len(y) != STATE_SIZE:
        raise ValueError('Primary augmented state must have fourteen entries')
    return list(y)


class _Series:
    """Truncated normalized radial Taylor coefficients; polynomial products only."""
    def __init__(self, coefficients):
        self.a = tuple(coefficients)

    def _cast(self, other):
        if isinstance(other, _Series):
            if len(other.a) != len(self.a):
                raise ValueError('Series orders differ')
            return other
        return _Series((exact(other),) + tuple(arb(0) for _ in self.a[1:]))

    def __add__(self, other):
        other = self._cast(other)
        return _Series(tuple(a + b for a, b in zip(self.a, other.a)))

    __radd__ = __add__

    def __neg__(self):
        return _Series(tuple(-a for a in self.a))

    def __sub__(self, other):
        return self + -self._cast(other)

    def __rsub__(self, other):
        return self._cast(other) + -self

    def __mul__(self, other):
        other = self._cast(other)
        return _Series(tuple(sum((self.a[j] * other.a[n-j]
                                  for j in range(n+1)), arb(0))
                             for n in range(len(self.a))))

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, _Series):
            raise TypeError('Only scalar series divisors are permitted')
        other = exact(other)
        if other.contains(0):
            raise ZeroDivisionError('Unresolved scalar divisor')
        return _Series(tuple(a / other for a in self.a))


def sources(y, p):
    """Qualified T15 source polynomials; return Sp,Sg,Sc,c2 in that order.

    m2 is the mass-squared model parameter; E is inverse warp, not E squared.
    No division by T, and c2prime is formed using the first-order ODE.
    """
    W,H,Phi,T,E,v,f,g,_,_,_,_,_,_ = physical(y)
    zero = v * 0
    if not p.get('forcing', True):
        return zero, zero, zero, zero
    # Lift parameters when evaluating formal series: do not ask a native Arb
    # scalar's multiplication dispatcher to understand a custom series type.
    m, k, mu = zero+p['m2'], zero+p['k'], zero+p['mu1']
    e2 = E*E
    u = -2*H*v-T*f/3
    c2 = -(6*v*v+f*f)*p['c_factor']
    c2prime = -(12*v*u+2*f*g)*p['c_factor']
    Sp = H*c2-v*u-f*g/6
    qK = (4*m-6*mu*e2)*v*f+6*u*g-8*m*Phi*v*v
    qR = (6*u*u-g*g/2+4*v*(12*H*u-T*g)
          +8*v*v*(6*H*H-T*T/2)+m*f*f/2
          -e2*(v*v*p['radial_v2']+f*f*p['radial_f2']))
    Sc = 12*H*Sp-(12*H*H-T*T)*c2+qR
    Sg = T*c2prime+2*m*Phi*c2-6*T*Sp-qK
    return Sp, Sg, Sc, c2


def rhs(y, p):
    W,H,Phi,T,E,v,f,g,vp,fp,gp,vh,fh,gh = physical(y)
    zero = W*0
    m, k = zero+p['m2'], zero+p['k']
    e2, t2 = E*E, T*T
    B = 12*H*T-4*m*Phi
    Sp,Sg,Sc,c2 = sources(y,p)
    def mode(a,b,c,mu):
        mu = zero+mu
        return [-2*H*a-T*b/3, c,
                -4*H*c+(m-mu*e2+2*t2)*b+B*a]
    first = mode(v,f,g,p['mu1'])
    loaded = mode(vp,fp,gp,p['mu2'])
    loaded[0] = loaded[0]+Sp
    loaded[2] = loaded[2]+Sg
    homogeneous = mode(vh,fh,gh,p['mu2'])
    return [H,-t2/3-k*e2,T,m*Phi-4*H*T,-H*E] + first + loaded + homogeneous


def coeff(y, order, p):
    """Normalized derivatives through order, via polynomial-E convolution.

    At recursion n all state coefficients through n are known. Evaluate the
    complete polynomial RHS at that truncation; coefficient n divided by n+1
    is the next state coefficient. No sampling or numerical differentiation.
    """
    physical(y)
    if not isinstance(order, int) or order < 0:
        raise ValueError('Nonnegative integer Taylor order required')
    rows = [[v] for v in y]
    for n in range(order):
        deriv = rhs([_Series(row) for row in rows], p)
        for row, value in zip(rows, deriv):
            row.append(value.a[n]/(n+1))
    return rows


def padded(x):
    lo,hi = bounds(x)
    eps = (hi-lo)/8+fmpq(1,2**640)
    return interval(lo-eps,hi+eps)


def picard(y,h,p):
    physical(y)
    if h <= 0:
        raise ValueError('Positive step required')
    dt = interval(fmpq(0),h)
    box = [padded(hull(a,a+dt*v)) for a,v in zip(y,rhs(y,p))]
    for iteration in range(1,33):
        image = [hull(a,a+dt*v) for a,v in zip(y,rhs(box,p))]
        if all(bounds(b)[0] < bounds(a)[0] and bounds(a)[1] < bounds(b)[1]
               for a,b in zip(image,box)):
            return box,iteration
        box = [padded(hull(a,b)) for a,b in zip(box,image)]
    raise RuntimeError('Primary augmented Picard inclusion failed')


def range_on_cell(cell,offset_lo,offset_hi):
    if not fmpq(0) <= offset_lo <= offset_hi <= cell['step']:
        raise ValueError('Range outside validated cell')
    t = interval(offset_lo,offset_hi)
    result=[]
    for point,remainder in zip(cell['point_coefficients'],cell['remainder_coefficient']):
        value=remainder
        for a in reversed(point):
            value=value*t+a
        result.append(value)
    return result


def step(y,h,p):
    box,iterations=picard(y,h,p)
    cell={'box':box,'point_coefficients':coeff(y,ORDER-1,p),
          'remainder_coefficient':[c[ORDER] for c in coeff(box,ORDER,p)],
          'step':h,'picard_iterations':iterations}
    return range_on_cell(cell,h,h),cell


def constraints(y,p):
    W,H,Phi,T,E,v,f,g,vp,fp,gp,vh,fh,gh=physical(y)
    Tp=p['m2']*Phi-4*H*T
    def row(a,b,c,mu):
        return T*c-Tp*b+(2*T*T-3*(mu+4*p['k'])*E*E)*a
    Sp,Sg,Sc,c2=sources(y,p)
    return {'first':row(v,f,g,p['mu1']),
            'second_particular':row(vp,fp,gp,p['mu2'])-Sc,
            'second_homogeneous':row(vh,fh,gh,p['mu2'])}


def first_integral(y,p):
    W,H,Phi,T,E,*unused=physical(y)
    return H*H-1-T*T/12+p['m2']*Phi*Phi/12-p['k']*E*E


