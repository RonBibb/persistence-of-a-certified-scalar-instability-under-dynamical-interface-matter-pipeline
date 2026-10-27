"""Adapted neutral growing-mode quadratic engine. Temporal source constants
are explicit parameters; validated integration mechanics inherited unchanged.
No writes or computation at import.
"""
"""Independent direct-W augmented validated flow; no work or writes on import.

State: W,H,Phi,T,p1,f1,g1,p2part,f2part,g2part,p2hom,f2hom,g2hom.
Degree-four Taylor polynomial plus whole-cell fifth-derivative remainder.
"""
from fractions import Fraction
from flint import arb, fmpq

ORDER = 5
DIMENSION = 13
MAX_PICARD_ITERATIONS = 32

def exact(value):
    if isinstance(value, arb): return value
    if isinstance(value, fmpq): return arb(value)
    if isinstance(value, float): raise TypeError('Exact rational input required')
    q = Fraction(value)
    return arb(fmpq(q.numerator, q.denominator))

def bounds(value): return value.lower().fmpq(), value.upper().fmpq()

def interval(lo, hi):
    if lo > hi: raise ValueError('Reversed interval')
    return arb((lo+hi)/2, (hi-lo)/2)

def hull(a, b):
    al, ah = bounds(a); bl, bh = bounds(b)
    return interval(min(al,bl), max(ah,bh))

def physical(y):
    if len(y) != DIMENSION: raise ValueError('Expected thirteen independent states')
    return list(y[:4])+[(-y[0]).exp()]+list(y[4:])

def sources(y, p):
    if len(y) != DIMENSION: raise ValueError('Expected thirteen independent states')
    if not p.get('forcing', True):
        return {key:arb(0) for key in ('c2','c2prime','Sp','Sg','Sc','qK','qR')}
    W,H,Phi,T,a,f,g = y[:7]
    e = (-2*W).exp(); m=p['m2']; k=p['k']; mu=p['mu1']
    u = -2*H*a-T*f/3
    c = -p['c_factor']*(6*a*a+f*f)
    cp = -p['c_factor']*(12*a*u+2*f*g)
    sp = H*c-a*u-f*g/6
    qk = (4*m-6*mu*e)*a*f+6*u*g-8*m*Phi*a*a
    # T15 exact radial quadratic source, with h^2=k and e=exp(-2W).
    qr = (6*u*u-g*g/2+4*a*(12*H*u-T*g)
          +8*a*a*(6*H*H-T*T/2)+m*f*f/2
          -e*(p['radial_v2']*a*a+p['radial_f2']*f*f))
    sg = T*cp+2*m*Phi*c-6*T*sp-qk
    sc = 12*H*sp-(12*H*H-T*T)*c+qr
    return dict(c2=c,c2prime=cp,Sp=sp,Sg=sg,Sc=sc,qK=qk,qR=qr)

def rhs(y, p):
    if len(y) != DIMENSION: raise ValueError('Expected thirteen independent states')
    W,H,Phi,T = y[:4]; e=(-2*W).exp(); m=p['m2']
    output=[H,-T*T/3-p['k']*e,T,m*Phi-4*H*T]
    s=sources(y,p)
    for offset,mu,sp,sg in ((4,p['mu1'],arb(0),arb(0)),
                            (7,p['mu2'],s['Sp'],s['Sg']),
                            (10,p['mu2'],arb(0),arb(0))):
        a,f,g=y[offset:offset+3]
        output.extend([-2*H*a-T*f/3+sp,g,
            -4*H*g+(m-mu*e+2*T*T)*f+(12*H*T-4*m*Phi)*a+sg])
    return output

def convolution(a,b,n):
    total=arb(0)
    for j in range(n+1): total+=a[j]*b[n-j]
    return total

def exponential_coefficients(exponent, degree):
    out=[exponent[0].exp()]
    for n in range(1,degree+1):
        total=arb(0)
        for j in range(1,n+1): total+=j*exponent[j]*out[n-j]
        out.append(total/n)
    return out

def _jet_rhs(c,p,n):
    """Independent normalized series algebra; all input coefficients through n."""
    def add(*xs):return [sum((x[j] for x in xs),arb(0)) for j in range(n+1)]
    def scale(x,v):return [a*v for a in x]
    def mul(a,b):return [convolution(a,b,j) for j in range(n+1)]
    def constant(v):return [exact(v)]+[arb(0) for _ in range(n)]
    W,H,Phi,T=c[:4]; a,f,g=c[4:7]
    e=exponential_coefficients(scale(W,-2),n)
    tt=mul(T,T); ht=mul(H,T); hh=mul(H,H)
    u=add(scale(mul(H,a),-2),scale(mul(T,f),-exact(Fraction(1,3))))
    aa=mul(a,a); ff=mul(f,f)
    c2=scale(add(scale(aa,6),ff),-p['c_factor'])
    cp=scale(add(scale(mul(a,u),12),scale(mul(f,g),2)),-p['c_factor'])
    sp=add(mul(H,c2),scale(mul(a,u),-1),scale(mul(f,g),-exact(Fraction(1,6))))
    qk=add(mul(add(constant(4*p['m2']),scale(e,-6*p['mu1'])),mul(a,f)),
           scale(mul(u,g),6),scale(mul(Phi,aa),-8*p['m2']))
    sg=add(mul(T,cp),scale(mul(Phi,c2),2*p['m2']),scale(mul(T,sp),-6),scale(qk,-1))
    if not p.get('forcing',True):sp=constant(0);sg=constant(0)
    out=[H,add(scale(tt,-exact(Fraction(1,3))),scale(e,-p['k'])),T,
         add(scale(Phi,p['m2']),scale(ht,-4))]
    zero=constant(0)
    for offset,mu,loadp,loadg in ((4,p['mu1'],zero,zero),(7,p['mu2'],sp,sg),(10,p['mu2'],zero,zero)):
        a,f,g=c[offset:offset+3]
        out.extend([add(scale(mul(H,a),-2),scale(mul(T,f),-exact(Fraction(1,3))),loadp),g,
            add(scale(mul(H,g),-4),scale(f,p['m2']),scale(mul(e,f),-mu),
                scale(mul(tt,f),2),scale(mul(ht,a),12),scale(mul(Phi,a),-4*p['m2']),loadg)])
    if len(out)!=DIMENSION:raise ValueError('Derivative dimension mismatch')
    return out

def coeff(y,order,p):
    if len(y)!=DIMENSION or order<0:raise ValueError('Coefficient input invalid')
    c=[[v] for v in y]
    for n in range(order):
        values=_jet_rhs(c,p,n)
        for j in range(DIMENSION):c[j].append(values[j][n]/(n+1))
    return c

def _enlarge(v):
    lo,hi=bounds(v); pad=(hi-lo)/8+fmpq(1,2**640)
    return interval(lo-pad,hi+pad)

def _inside(inner,outer):
    il,ih=bounds(inner);ol,oh=bounds(outer)
    return ol<il and ih<oh

def picard(y,h,p):
    if h<=0 or len(y)!=DIMENSION:raise ValueError('Positive step and thirteen states required')
    dt=interval(fmpq(0),h)
    box=[_enlarge(hull(a,a+dt*b)) for a,b in zip(y,rhs(y,p))]
    for iteration in range(1,MAX_PICARD_ITERATIONS+1):
        image=[hull(a,a+dt*b) for a,b in zip(y,rhs(box,p))]
        if all(_inside(a,b) for a,b in zip(image,box)):return box,iteration
        box=[_enlarge(hull(a,b)) for a,b in zip(box,image)]
    raise RuntimeError('Independent augmented Picard inclusion failed')

def range_on_cell(cell,offset_lo,offset_hi):
    if not fmpq(0)<=offset_lo<=offset_hi<=cell['step']:raise ValueError('Offset outside cell')
    dt=interval(offset_lo,offset_hi);out=[]
    if len(cell['point_coefficients'])!=DIMENSION or len(cell['remainder_coefficient'])!=DIMENSION:
        raise ValueError('Cell dimension mismatch')
    for c,r in zip(cell['point_coefficients'],cell['remainder_coefficient']):
        v=r
        for a in reversed(c):v=v*dt+a
        out.append(v)
    return out

def step(y,h,p):
    box,j=picard(y,h,p)
    cell=dict(box=box,point_coefficients=coeff(y,ORDER-1,p),
        remainder_coefficient=[row[ORDER] for row in coeff(box,ORDER,p)],
        step=h,picard_iterations=j)
    return range_on_cell(cell,h,h),cell

def constraints(y,p):
    if len(y)!=DIMENSION:raise ValueError('Expected thirteen independent states')
    W,H,Phi,T=y[:4];e=(-2*W).exp();tp=p['m2']*Phi-4*H*T
    sc=sources(y,p)['Sc'];out={}
    for key,j,mu,source in (('first',4,p['mu1'],arb(0)),('particular',7,p['mu2'],sc),('homogeneous',10,p['mu2'],arb(0))):
        a,f,g=y[j:j+3]
        out[key]=T*g-tp*f+(2*T*T-3*(mu+4*p['k'])*e)*a-source
    return out

def first_integral(y,p):
    W,H,Phi,T=y[:4]
    return H*H-1-T*T/12+p['m2']*Phi*Phi/12-p['k']*(-2*W).exp()


