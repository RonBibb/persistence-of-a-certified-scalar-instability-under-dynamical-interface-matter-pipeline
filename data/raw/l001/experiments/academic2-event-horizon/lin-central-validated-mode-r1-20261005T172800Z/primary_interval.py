"""Primary polynomial validated flow; E=exp(-W) is a separate state.

No independent implementation or prior numerical profile is imported.
States: W,H,Phi,T,E,psi,f,g. Parameters are fixed outward Arb balls.
"""
from fractions import Fraction
from flint import arb, fmpq

ORDER = 5


def exact(value):
    if isinstance(value, arb):
        return value
    if isinstance(value, fmpq):
        return arb(value)
    if isinstance(value, float):
        raise TypeError("Exact input required")
    q = Fraction(value)
    return arb(fmpq(q.numerator, q.denominator))


def bounds(x):
    return x.lower().fmpq(), x.upper().fmpq()


def interval(lo, hi):
    if lo > hi:
        raise ValueError("Reversed interval")
    return arb((lo + hi) / 2, (hi - lo) / 2)


def hull(x, y):
    a, b = bounds(x)
    c, d = bounds(y)
    return interval(min(a, c), max(b, d))


def initial(A, mu, model):
    p = {key: exact(val) for key, val in model.items()}
    p["mu"] = exact(mu)
    a = exact(A)
    displacement = a - p["v0"]
    H = -(p["lambda_a"] + p["gamma"] * displacement * displacement / 2) / 6
    T = p["gamma"] * (a - p["v0"]) / 2
    p["k"] = H*H - 1 - T*T/12 + p["m2"]*a*a/12
    p["B0"] = p["gamma"]*T/2 - p["m2"]*a + 4*H*T
    lo, hi = bounds(p["B0"])
    if lo <= 0 <= hi:
        raise RuntimeError("Lower normalization singular")
    f = 3*(p["mu"] + 4*p["k"])/p["B0"]
    g = p["gamma"]*f/2 - 2*T
    return [arb(0), H, a, T, arb(1), arb(1), f, g], p


def rhs(y, p):
    W,H,P,T,E,u,f,g = y
    return [H, -T*T/3-p["k"]*E*E, T, p["m2"]*P-4*H*T,
            -H*E, -2*H*u-T*f/3, g,
            -4*H*g+(p["m2"]-p["mu"]*E*E+2*T*T)*f
            +(12*H*T-4*p["m2"]*P)*u]


def product(a, b, n):
    return sum((a[i]*b[n-i] for i in range(n+1)), arb(0))


def coeff(y, order, p):
    c = [[v] for v in y]
    W,H,P,T,E,u,f,g = c
    ee,tt,ht = [],[],[]
    for n in range(order):
        ee.append(product(E,E,n)); tt.append(product(T,T,n)); ht.append(product(H,T,n))
        v = [H[n], -tt[n]/3-p["k"]*ee[n], T[n], p["m2"]*P[n]-4*ht[n],
             -product(H,E,n), -2*product(H,u,n)-product(T,f,n)/3, g[n],
             -4*product(H,g,n)+p["m2"]*f[n]-p["mu"]*product(ee,f,n)
             +2*product(tt,f,n)+12*product(ht,u,n)-4*p["m2"]*product(P,u,n)]
        for row, val in zip(c,v):
            row.append(val/(n+1))
    return c


def padded(x):
    lo, hi = bounds(x)
    eps = (hi-lo)/8+fmpq(1,2**640)
    return interval(lo-eps,hi+eps)


def picard(y,h,p):
    dt = interval(fmpq(0),h)
    box = [padded(hull(a,a+dt*v)) for a,v in zip(y,rhs(y,p))]
    for j in range(1,33):
        image = [hull(a,a+dt*v) for a,v in zip(y,rhs(box,p))]
        if all(bounds(b)[0] < bounds(a)[0] and bounds(a)[1] < bounds(b)[1]
               for a,b in zip(image,box)):
            return box,j
        box = [padded(hull(a,b)) for a,b in zip(box,image)]
    raise RuntimeError("Primary Picard inclusion failed")


def range_on_cell(cell,offset_lo,offset_hi):
    if not fmpq(0)<=offset_lo<=offset_hi<=cell["step"]:
        raise ValueError("Cell interval outside validated step")
    t = interval(offset_lo,offset_hi)
    result = []
    for c,r in zip(cell["point_coefficients"],cell["remainder_coefficient"]):
        v = r
        for a in reversed(c):
            v = v*t+a
        result.append(v)
    return result


def step(y,h,p):
    box,j = picard(y,h,p)
    cell = {"box":box,"point_coefficients":coeff(y,ORDER-1,p),
            "remainder_coefficient":[c[ORDER] for c in coeff(box,ORDER,p)],
            "step":h,"picard_iterations":j}
    return range_on_cell(cell,h,h),cell


def determinant(y,p):
    W,H,P,T,E,u,f,g = y
    return g+2*T*u+p["gamma"]*f/2


def constraint(y,p):
    W,H,P,T,E,u,f,g = y
    return T*g-(p["m2"]*P-4*H*T)*f+(2*T*T-3*(p["mu"]+4*p["k"])*E*E)*u


def first_integral(y,p):
    W,H,P,T,E,u,f,g = y
    return H*H-1-T*T/12+p["m2"]*P*P/12-p["k"]*E*E


def geometry(cell,p):
    W,H,P,T,E,u,f,g = cell["box"]
    return {"W":W,"psi":u,"f":f,"warp_squared":(2*W).exp(),
            "norm_density":2*(2*W).exp()*(f*f+6*u*u),
            "displacement_density":-2*u,
            "constraint":constraint(cell["box"],p),
            "first_integral":first_integral(cell["box"],p)}


def algebra_controls():
    p = {"m2":arb(fmpq(41,100)),"mu":arb(0),"k":arb(0),"gamma":arb(20)}
    y = [arb(0),arb(-1),arb(0),arb(0),arb(1),arb(1),arb(0),arb(0)]
    c = coeff(y,5,p)
    factorial = 1
    checks = []
    for n in range(6):
        if n: factorial *= n
        for index,numerator in ((4,1),(5,2**n)):
            q = fmpq(numerator,factorial)
            lo,hi = bounds(c[index][n]); checks.append(lo<=q<=hi)
    return {"vacuum_E_and_psi_coefficients":all(checks),"pass":all(checks)}
