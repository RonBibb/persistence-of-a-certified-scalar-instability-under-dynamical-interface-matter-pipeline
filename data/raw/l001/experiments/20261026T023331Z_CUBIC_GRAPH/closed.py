"""Independent closed cubic S7 source, excluding the linear new xi3 row.

Generic rational-polynomial or Arb scalar arithmetic; no series machinery,
native imports, file operations, or scientific computation on import.
"""
from fractions import Fraction


def _div(value, denominator):
    # Python int/int must not silently introduce a binary floating-point value.
    if isinstance(value, int):
        return Fraction(value, denominator)
    return value / denominator


def extract(w, sigma):
    """Return geometric/current/oscillator/total coefficients of z^3.

    Unlike the direct series evaluator, values here are scalar coefficients.
    xi3 and arbitrary third-order bulk/oscillator entries are deliberately
    unused: the separately removed row is 342*sigma*k*E^2*xi3.
    """
    if sigma not in (-1, 1):
        raise ValueError('Expected lower +1 or upper -1 orientation')
    E,h,x,y,p,p2,H,Hp,u,c2,T,Tp,f,f2,g,chi,chi2,n = [w[key] for key in
        ('E','h','xi1','xi2','p1','p2','H','Hp','u','c2','T','Tp',
         'f1','f2','g1','chi1','chi2','n')]
    r=-6*h

    # Wall log N coefficients. p2 is Eulerian, so its pulled value includes xu.
    A=H*x+p
    B=H*y+_div(Hp*x*x,2)+p2+x*u
    C=-3*p-H*x
    J=c2-3*p2-3*x*u-H*y-_div(Hp*x*x,2)

    # v_t is the total derivative of the wall velocity. By contrast w1,w2
    # represent fixed-s Db-Dp evaluated on the wall, NOT its total derivative.
    v1=E*r*x
    v2=E*(2*r*y+r*x*C)
    v3=E*(2*r*y*C+r*x*(J+_div(C*C,2)))
    w1=-3*r*p
    w2=2*r*(c2-3*p2)-3*r*x*u
    t1=(r-h)*v1
    t2=(2*r-h)*v2+v1*w1
    t3=(3*r-h)*v3+r*v1*v1*v1+v2*w1+v1*w2
    geometric=sigma*E*(t3-A*t2+(_div(A*A,2)-B+_div(v1*v1,2))*t1)

    phi1=T*x+f
    phi2=T*y+_div(Tp*x*x,2)+f2+x*g
    # c(Phi) is AFFINE. An exponential replacement would add a spurious
    # phi1^2/(2*10^6) contribution inside the current-stress coefficient.
    current=-n*(-_div(phi2,1000)-6*B+18*A*A+_div(6*A*phi1,1000))

    # Surface chi2 is intrinsic: no radial transport term is added to it.
    # 1/(1-v^2) first contributes to this stress at z^4, not z^3.
    oscillator=-_div(E*E*r*r*(4*chi*chi2-2*A*chi*chi),2)
    return {'geometric':geometric,'current':current,'oscillator':oscillator,
            'total':geometric+current+oscillator}


def remote(w, sigma):
    """Independent remote-wall restriction n=xi1=0, retaining xi2.

    Caller must establish that restriction; this helper intentionally leaves
    xi2 and chi2 free, making it useful as a symbolic polynomial control.
    """
    if sigma not in (-1, 1):
        raise ValueError('Expected wall orientation')
    E,h,y,p,chi,chi2=[w[key] for key in ('E','h','xi2','p1','chi1','chi2')]
    k=h*h
    geometric=-1056*sigma*k*E*E*y*p
    current=geometric*0
    oscillator=-72*k*E*E*chi*chi2+36*k*E*E*p*chi*chi
    return {'geometric':geometric,'current':current,'oscillator':oscillator,
            'total':geometric+current+oscillator}
