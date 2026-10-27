"""Shared outward arithmetic primitives; no background or equation driver."""
import math
from flint import arb, fmpq


def power(x, n):
    out = arb(1)
    for _ in range(n):
        out = out*x
    return out


def mul(a, b, n):
    return sum((a[j]*b[n-j] for j in range(n+1)), arb(0))


def exp_coefficient(a, e, factor, n):
    if n == 0:
        return (factor*a[0]).exp()
    return sum((j*factor*a[j]*e[n-j] for j in range(1, n+1)), arb(0))/n


def linear_power(value, slope, degree, order):
    return [math.comb(degree,j)*power(value,degree-j)*power(arb(slope),j)
            if j<=degree else arb(0) for j in range(order+1)]


def shapes(s, D, order):
    """Own fifth jet is +1 at both endpoints; no monomial cancellation fit."""
    n = order+1
    p0=linear_power(s,1,5,n); p1=linear_power(D-s,-1,6,n)
    q0=linear_power(s,1,6,n); q1=linear_power(s-D,1,5,n)
    scale=120*power(D,6)
    eta=[[mul(a,b,j)/scale for j in range(n+1)] for a,b in ((p0,p1),(q0,q1))]
    return [(v[:order+1],[(j+1)*v[j+1] for j in range(order+1)]) for v in eta]


def bounds(x):
    return x.lower().fmpq(),x.upper().fmpq()


def interval(lo,hi):
    if lo>hi:
        raise ValueError("Reversed interval")
    return arb((lo+hi)/2,(hi-lo)/2)


def hull(a,b):
    al,ah=bounds(a);bl,bh=bounds(b)
    return interval(min(al,bl),max(ah,bh))


def inflate(x):
    lo,hi=bounds(x);delta=(hi-lo)/8+fmpq(1,2**640)
    return interval(lo-delta,hi+delta)


def record(x):
    lo,hi=bounds(x)
    return {"exact":[str(lo),str(hi)],"decimal":[float(lo),float(hi)]}


def det3(J):
    return (J[0][0]*(J[1][1]*J[2][2]-J[1][2]*J[2][1])
            -J[0][1]*(J[1][0]*J[2][2]-J[1][2]*J[2][0])
            +J[0][2]*(J[1][0]*J[2][1]-J[1][1]*J[2][0]))


def inverse3(J,det):
    out=[]
    for i in range(3):
        row=[]
        for j in range(3):
            rr=[r for r in range(3) if r!=j];cc=[c for c in range(3) if c!=i]
            co=J[rr[0]][cc[0]]*J[rr[1]][cc[1]]-J[rr[0]][cc[1]]*J[rr[1]][cc[0]]
            row.append(((-1)**(i+j))*co/det)
        out.append(row)
    return out
