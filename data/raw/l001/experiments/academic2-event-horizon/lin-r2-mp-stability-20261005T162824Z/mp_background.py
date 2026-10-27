"""Genuinely multiprecision proper-distance background; no SciPy coefficients."""
import bisect
from fractions import Fraction
import mpmath as mp


def rational(value):
    q = Fraction(value)
    return mp.mpf(q.numerator) / q.denominator


def exact_float(value):
    return str(Fraction(float(value)))


def decimal(value):
    return mp.nstr(value, mp.mp.dps + 8, strip_zeros=False)


def convolution(a, b, n):
    return sum(a[j] * b[n-j] for j in range(n+1))


def coefficients(y, k, m2, degree):
    # y=(W,H,Phi,T,E=exp(-W),z), normalized Taylor coefficients.
    c = [[mp.mpf(x)] for x in y]
    W,H,P,T,E,z = c
    for n in range(degree):
        den = n+1
        next_values = [H[n], -convolution(T,T,n)/3-k*convolution(E,E,n),
                       T[n], m2*P[n]-4*convolution(H,T,n),
                       -convolution(H,E,n), E[n]]
        for row, value in zip(c, next_values):
            row.append(value / den)
    return c


def evaluate(c, h):
    result=[]
    for row in c:
        value=row[-1]
        for v in reversed(row[:-1]):
            value=value*h+v
        result.append(value)
    return result


def bracket_root(fun, lo, hi, tolerance, maximum=80):
    fl,fh=fun(lo),fun(hi)
    if not all(mp.isfinite(v) for v in [fl,fh]) or fl*fh>=0:
        raise RuntimeError('fixed bracket does not contain a sign change')
    endpoints=[decimal(fl),decimal(fh)]
    for iteration in range(maximum):
        x=(lo*fh-hi*fl)/(fh-fl)
        if not lo<x<hi or iteration%8==7:
            x=(lo+hi)/2
        fx=fun(x)
        if not mp.isfinite(fx):raise RuntimeError('nonfinite shooting value')
        if abs(fx)<=tolerance:
            return x,{'iterations':iteration+1,'residual':decimal(fx),'endpoint_values':endpoints}
        if fl*fx<0:hi,fh=x,fx
        else:lo,fl=x,fx
    raise RuntimeError('frozen shooting iteration limit')


class Solution:
    def __init__(self, segments, D):
        self.segments=segments
        self.starts=[x[0] for x in segments]
        self.D=D

    def at(self,s):
        s=mp.mpf(s)
        if s<0 or s>self.D+mp.mpf('1e-14'):
            raise RuntimeError('background query outside frozen interval')
        j=min(max(bisect.bisect_right(self.starts,s)-1,0),len(self.segments)-1)
        start,length,c=self.segments[j]
        return evaluate(c,s-start)

    def sol(self,s):
        # Binary64 conversion is confined to the separate numerical mode solver.
        import numpy as np
        if np.ndim(s)==0:
            vals=self.at(mp.mpf(float(s)))
            return np.array([float(vals[i]) for i in [0,1,2,3,5]])
        return np.array([[float(row[i]) for i in [0,1,2,3,5]]
                         for row in [self.at(mp.mpf(float(t))) for t in s]]).T

    @property
    def y(self):
        import numpy as np
        return np.array([[float(row[i]) for i in [0,1,2,3,5]]
                         for row in [self.at(0),self.at(self.D)]]).T


def launch(model,a):
    H=-(model['lambda_a']+model['gamma']*(a-model['v0'])**2/2)/6
    T=model['gamma']*(a-model['v0'])/2
    k=H*H-1-T*T/12+model['m2']*a*a/12
    return [mp.mpf(0),H,a,T,mp.mpf(1),mp.mpf(0)],k


def event(y,model):
    return y[1]-(model['lambda_b']+model['gamma']*(y[2]-model['v1'])**2/2)/6


def integrate(initial,k,model,control,stop_event=True,limit=mp.mpf(2)):
    h=mp.mpf(2)/control['step_denominator'];s=mp.mpf(0);y=list(initial);segments=[]
    tol=mp.mpf(control['shoot_tolerance'])
    if stop_event and event(y,model)<=0:raise RuntimeError('initial event not positive')
    while s<limit:
        length=min(h,limit-s)
        c=coefficients(y,k,model['m2'],control['degree'])
        endpoint=evaluate(c,length)
        if stop_event and event(endpoint,model)<=0:
            length,record=bracket_root(lambda x:event(evaluate(c,x),model),mp.mpf(0),length,tol)
            endpoint=evaluate(c,length);segments.append((s,length,c))
            return Solution(segments,s+length),record
        if stop_event:
            # Samples detect an earlier crossing within an accepted Taylor step.
            # The inherited R2 interval certificate supplies branch authority.
            if any(event(evaluate(c,length*j/4),model)<=0 for j in [1,2,3]):
                raise RuntimeError('nonmonotone event sampling requires a successor')
        segments.append((s,length,c));s+=length;y=endpoint
    if stop_event:raise RuntimeError('no first event before s=2')
    return Solution(segments,limit),None


def construct(exact_model,root_bracket,control):
    mp.mp.dps=control['dps']
    model={n:rational(v) for n,v in exact_model.items()}
    cache={}
    def shoot(a):
        initial,k=launch(model,a)
        if k<=0:raise RuntimeError('curvature not positive')
        solution,event_record=integrate(initial,k,model,control)
        end=solution.at(solution.D)
        residual=end[3]+model['gamma']*(end[2]-model['v1'])/2
        cache[decimal(a)]=(solution,k,event_record)
        return residual
    a,root_record=bracket_root(shoot,*map(rational,root_bracket),
                              mp.mpf(control['shoot_tolerance']))
    solution,k,event_record=cache[decimal(a)]
    nodes=[solution.D*j/2000 for j in range(2001)]
    values=[solution.at(s) for s in nodes]
    identity=max(abs(y[4]*mp.exp(y[0])-1) for y in values)
    payload={'schema':'mp-proper-background-v1','model_exact':exact_model,
             'control':control,'a':decimal(a),'k':decimal(k),'D':decimal(solution.D),
             'L':decimal(values[-1][5]),'s':[decimal(s) for s in nodes],
             'fields':[[decimal(y[i]) for y in values] for i in [0,1,2,3,5]],
             'E':[decimal(y[4]) for y in values],
             'auxiliary_identity_max':decimal(identity),'root_record':root_record,
             'event_record':event_record,'genuinely_mp_integration_and_storage':True,
             'scipy_background_used':False,'binary64_intermediate_used':False}
    return payload,solution


def restore(payload):
    # Reconstruct deterministic dense Taylor segments from the saved exact a;
    # completed mode cases are not recomputed. MP background samples stay intact.
    control=payload['control'];mp.mp.dps=control['dps']
    model={n:rational(v) for n,v in payload['model_exact'].items()}
    initial,k=launch(model,mp.mpf(payload['a']))
    solution,_=integrate(initial,k,model,control)
    if decimal(k)!=payload['k'] or decimal(solution.D)!=payload['D']:
        raise RuntimeError('background recovery not exact')
    return solution
