"""D1 source plus its mu derivative; background/wall fixed during differentiation."""
from flint import arb
from series import mul
import source_flow


def rhs(y, p):
    W,H,P,T,E,psi,f,g,s,u,v,w=y
    m,mu=p['m2'],p['mu']
    return source_flow.rhs(y[:9],p)+[
        -2*H*u-T*v/3,
        w,
        -4*H*w+m*v-mu*E*E*v-E*E*f+2*T*T*v
        +12*H*T*u-4*m*P*u]


def coeff(y, N, p):
    c=source_flow.coeff(y[:9],N,p)+[[v] for v in y[9:]]
    W,H,P,T,E,psi,f,g,s,u,v,w=c
    m,mu=p['m2'],p['mu']
    ee=[];tt=[];ht=[]
    for n in range(N):
        ee.append(mul(E,E,n));tt.append(mul(T,T,n));ht.append(mul(H,T,n))
        out=[-2*mul(H,u,n)-mul(T,v,n)/3,w[n],
             -4*mul(H,w,n)+m*v[n]-mu*mul(ee,v,n)-mul(ee,f,n)
             +2*mul(tt,v,n)+12*mul(ht,u,n)-4*m*mul(P,u,n)]
        for row,value in zip(c[9:],out):row.append(value/(n+1))
    return c


def determinant(y,p):
    return y[7]+2*y[3]*y[5]+p['gamma']*y[6]/2


def determinant_mu(y,p):
    return y[11]+2*y[3]*y[9]+p['gamma']*y[10]/2
