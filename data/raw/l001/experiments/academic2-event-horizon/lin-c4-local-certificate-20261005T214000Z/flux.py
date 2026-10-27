"""Separately written divergence-form variations; no primary imports.

State W,H,Phi,T,s,h_A,Q_A,h_0,Q_0,h_1,Q_1, with Q=exp(4W)h_s.
Shares basic series arithmetic and the validated driver with the direct form.
"""
from flint import arb
from series import mul,shapes,exp_coefficient


def initial(H,P,T):
    return [arb(0),H,P,T,arb(0),arb(1),arb(0),arb(0),arb(0),arb(0),arb(0)]


def rhs(y,p):
    W,H,P,T,s=y[:5];eta=shapes(s,p['D'],0);m=p['m2'];k=p['k']
    em2=(-2*W).exp();em4=(-4*W).exp();ep2=(2*W).exp();ep4=(4*W).exp()
    out=[H,-T*T/3-k*em2,T,m*P-4*H*T,arb(1)]
    for col in range(3):
        u,Q=y[5+2*col:7+2*col]
        force=arb(0) if col==0 else (m*P*eta[col-1][0][0]+T*eta[col-1][1][0])/3
        out.extend([em4*Q,-2*k*ep2*u-ep4*force])
    return out


def coeff(y,N,p):
    c=[[v] for v in y];W,H,P,T,s=c[:5];eta=shapes(s[0],p['D'],N-1)
    em2=[];em4=[];ep2=[];ep4=[];forces=[[],[],[]];m=p['m2'];k=p['k']
    for n in range(N):
        for factor,series in ((-2,em2),(-4,em4),(2,ep2),(4,ep4)):
            series.append(exp_coefficient(W,series,factor,n))
        out=[H[n],-mul(T,T,n)/3-k*em2[n],T[n],m*P[n]-4*mul(H,T,n),arb(int(n==0))]
        for col in range(3):
            u,Q=c[5+2*col:7+2*col]
            forces[col].append(arb(0) if col==0 else (m*mul(P,eta[col-1][0],n)+mul(T,eta[col-1][1],n))/3)
            out.extend([mul(em4,Q,n),-2*k*mul(ep2,u,n)-mul(ep4,forces[col],n)])
        for row,value in zip(c,out):
            row.append(value/(n+1))
    return c


def fields(y,p):
    W,H,P,T,s=y[:5];em2=(-2*W).exp()
    return {'W':W,'H':H,'Phi':P,'T':T,'exp_minus_2W':em2,'q':p['k']*em2,
            'first_integral':H*H-1-T*T/12+p['m2']*P*P/12-p['k']*em2}


def columns(y):
    return [(y[5+2*j],(-4*y[0]).exp()*y[6+2*j]) for j in range(3)]
