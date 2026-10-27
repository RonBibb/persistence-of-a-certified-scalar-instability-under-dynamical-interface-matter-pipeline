"""Direct metric variations with polynomial E=exp(-W); no flux imports.

State W,H,Phi,T,E,s,h_A,v_A,h_0,v_0,h_1,v_1.
"""
from flint import arb
from series import mul,shapes


def initial(H,P,T):
    return [arb(0),H,P,T,arb(1),arb(0),arb(1),arb(0),arb(0),arb(0),arb(0),arb(0)]


def rhs(y,p):
    W,H,P,T,E,s=y[:6];eta=shapes(s,p['D'],0);k=p['k'];m=p['m2']
    out=[H,-T*T/3-k*E*E,T,m*P-4*H*T,-H*E,arb(1)]
    for col in range(3):
        u,v=y[6+2*col:8+2*col]
        force=arb(0) if col==0 else (m*P*eta[col-1][0][0]+T*eta[col-1][1][0])/3
        out.extend([v,-4*H*v-2*k*E*E*u-force])
    return out


def coeff(y,N,p):
    c=[[v] for v in y];W,H,P,T,E,s=c[:6];eta=shapes(s[0],p['D'],N-1)
    EE=[];k=p['k'];m=p['m2']
    for n in range(N):
        EE.append(mul(E,E,n))
        out=[H[n],-mul(T,T,n)/3-k*EE[n],T[n],m*P[n]-4*mul(H,T,n),
             -mul(H,E,n),arb(int(n==0))]
        for col in range(3):
            u,v=c[6+2*col:8+2*col]
            force=arb(0) if col==0 else (m*mul(P,eta[col-1][0],n)+mul(T,eta[col-1][1],n))/3
            out.extend([v[n],-4*mul(H,v,n)-2*k*mul(EE,u,n)-force])
        for row,value in zip(c,out):
            row.append(value/(n+1))
    return c


def fields(y,p):
    W,H,P,T,E,s=y[:6]
    return {'W':W,'H':H,'Phi':P,'T':T,'exp_minus_2W':E*E,'q':p['k']*E*E,
            'first_integral':H*H-1-T*T/12+p['m2']*P*P/12-p['k']*E*E}


def columns(y):
    return [(y[6+2*j],y[7+2*j]) for j in range(3)]
