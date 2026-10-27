"""Centered full nonlinear metric with analytic three-parameter variations."""
from flint import arb
from algebra import Taylor,e1,e2,exp,ev
from series import power
import source_flow


def evaluate(y,p):
    W,H,P,T,E,psi,f,g,s,w,v,ua,va,u0,v0,u1,v1=y
    eps=p['eps'];k=p['k'];m=p['m2'];D=p['D']
    psi_s=-2*H*psi-T*f/3
    H0=s**5*(D-s)**6/(120*power(D,6));H1=s**6*(s-D)**5/(120*power(D,6))
    Hp0=(5*s**4*(D-s)**6-6*s**5*(D-s)**5)/(120*power(D,6))
    Hp1=(6*s**5*(s-D)**5+5*s**6*(s-D)**4)/(120*power(D,6))
    d=ev(p['c7'],s)+p['x'][1]*H0+p['x'][2]*H1
    ds=ev(p['c7'],s,1)+p['x'][1]*Hp0+p['x'][2]*Hp1
    ell=-2*eps*psi;ell_s=-2*eps*psi_s
    qbg=k*E*E;z=-4*eps*psi;a=-6*eps*psi-2*w
    vv=eps*psi_s+v;ef=eps*f;eg=eps*g
    rhs_v=-4*H*v-2*qbg*w-2*eps*psi_s*vv-2*vv*vv+qbg*e2(a)+2*e2(z)
    rhs_v-=m*(P*P*e2(z)+2*P*ef*e1(z)+exp(z)*(ef*ef+2*(P+ef)*d+d*d))/6
    rhs_v-=T*ds/3+(eg+ds)*(eg+ds)/6
    src=source_flow.rhs(y[:9],p)
    # Preserve generic Taylor type for the affine coordinate derivative.
    src[8]=s*0+1
    out=src+[v,rhs_v]
    for col,(u,r) in enumerate(((ua,va),(u0,v0),(u1,v1))):
        force=0 if col==0 else (m*exp(z)*(P+ef+d)*(H0 if col==1 else H1)+(T+eg+ds)*(Hp0 if col==1 else Hp1))/3
        out += [r,(ell_s-4*(H+vv))*r-2*qbg*exp(a)*u-force]
    return out


def rhs(y,p):
    # Multiplication powers avoid generic real-power ambiguity on zero-straddling balls.
    return [v.c[0] for v in evaluate([Taylor([v]) for v in y],p)]


def coeff(y,N,p):
    cc=[[v] for v in y]
    for n in range(N):
        yy=[Taylor(row) for row in cc]
        out=evaluate(yy,p)
        for row,v in zip(cc,out):row.append(v.c[n]/(n+1))
    return cc
