"""Certified regular D1 background and physical-mode IVP, nine states."""
from flint import arb
from series import mul


def rhs(y,p):
    W,H,P,T,E,psi,f,g,s=y[:9];k=p['k'];m=p['m2'];mu=p['mu']
    return [H,-T*T/3-k*E*E,T,m*P-4*H*T,-H*E,
            -2*H*psi-T*f/3,g,-4*H*g+m*f-mu*E*E*f+2*T*T*f+12*H*T*psi-4*m*P*psi,arb(1)]


def coeff(y,N,p):
    c=[[v] for v in y[:9]];W,H,P,T,E,psi,f,g,s=c
    ee=[];tt=[];ht=[];k=p['k'];m=p['m2'];mu=p['mu']
    for n in range(N):
        ee.append(mul(E,E,n));tt.append(mul(T,T,n));ht.append(mul(H,T,n))
        out=[H[n],-tt[n]/3-k*ee[n],T[n],m*P[n]-4*ht[n],-mul(H,E,n),
             -2*mul(H,psi,n)-mul(T,f,n)/3,g[n],
             -4*mul(H,g,n)+m*f[n]-mu*mul(ee,f,n)+2*mul(tt,f,n)+12*mul(ht,psi,n)-4*m*mul(P,psi,n),arb(int(n==0))]
        for row,v in zip(c,out):row.append(v/(n+1))
    return c
