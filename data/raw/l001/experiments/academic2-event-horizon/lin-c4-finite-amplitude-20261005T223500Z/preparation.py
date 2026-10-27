"""Exact unchanged C7 lift and C4 row, epsilon Taylor with interval remainder."""
import math
from flint import arb, fmpq
from algebra import Taylor, exp, e1, e2, ev, hermite_inverse
from series import interval, power, bounds
import source_flow

EPS_ORDER=8
HERMITE=hermite_inverse()


def wall_jets(y,p,side):
    """Intersect certified IVP values with identities of its actual admitted wall/mode."""
    z=list(y[:9]);sigma=1 if side==0 else -1
    vi=p['v0'] if side==0 else p['v1'];lam=p['lambda_a'] if side==0 else p['lambda_b']
    P=z[2];c=sigma*p['gamma']/2
    identities={1:-sigma*(lam+p['gamma']*(P-vi)*(P-vi)/2)/6,
                3:c*(P-vi)}
    for j,a in identities.items():
        l,h=bounds(z[j]);u,v=bounds(a)
        z[j]=interval(max(l,u),min(h,v))
    z[7]=c*z[6]-2*z[3]*z[5]
    # g is replaced only after separately requiring overlap with its certified IVP enclosure.
    l,h=bounds(y[7]);u,v=bounds(z[7]);z[7]=interval(max(l,u),min(h,v))
    cc=source_flow.coeff(z,5,p)
    return {name:[cc[j][n]*math.factorial(n) for n in range(6)] for name,j in [('Phi',2),('psi',5),('f',6)]} | {
        'H':z[1],'T':z[3],'qbg':p['k']*z[4]*z[4], 'sigma':sigma,'vi':vi,'lam':lam}


def endpoint_raw(e,j,p):
    phi=[j['Phi'][n]+e*j['f'][n] for n in range(6)]
    ell=[-2*e*j['psi'][n] for n in range(5)];L=exp(ell[0])
    sigma=j['sigma'];m=p['m2'];c=sigma*p['gamma']/2
    t=c*(phi[0]-j['vi']);pt=-sigma*(j['lam']+p['gamma']*(phi[0]-j['vi'])**2/2)/6
    u=(phi[2]-ell[1]*L*t)*exp(-2*ell[0]);V=-6+m*phi[0]*phi[0]/2
    v=-(6*pt-c)*u-(4*pt*pt-m-t*t-2*V/3-4*c*pt)*t+(2*pt-c)*m*phi[0]
    third=L**3*v+3*ell[1]*phi[2]-(2*ell[1]*ell[1]-ell[2])*L*t
    delta=[e*0,L*t-phi[1],e*0,third-phi[3]]
    return phi,ell,L,pt,t,u,delta


def c7_series(e,jets,p,impose_zero):
    rhs=[];D=p['D']
    for j in jets:
        delta=endpoint_raw(e,j,p)[-1]
        for n in range(4):rhs.append(delta[n]*power(D,n))
    co=[sum((rhs[i]*HERMITE[n][i] for i in range(8)),e*0)/power(D,n) for n in range(8)]
    if impose_zero:
        for v in co:v.c[0]=arb(0);v.c[1]=arb(0)
    return co


def static_refs(P,t,p,m):
    w=-(-2*P**3*m*m+14*P*P*m*p*t-3*P*m*m-72*P*m*p*p-14*P*m*t*t+24*P*m+24*m*p*t+360*p**3*t+66*p*t**3-168*p*t)/3
    z=(7*P**4*m*m*t-156*P**3*m*m*p+216*P*P*m*m*t+960*P*P*m*p*p*t+54*P*P*m*t**3-168*P*P*m*t-144*P*m*m*p-3024*P*m*p**3-2244*P*m*p*t*t+1872*P*m*p+18*m*m*t+1152*m*p*p*t+120*m*t**3-288*m*t+15120*p**4*t+6768*p*p*t**3-11520*p*p*t+99*t**5-648*t**3+1008*t)/18
    return w,z


def W_series(e,j,p,co,side):
    phi,ell,L,pt,t,u,delta=endpoint_raw(e,j,p)
    s=arb(0) if side==0 else p['D']
    # Exact endpoints preserve scalar value and second coordinate jet; use exact first/third targets.
    phi[1]=L*t;phi[3]=phi[3]+delta[3]
    phi[4]=phi[4]+ev(co,s,4);phi[5]=phi[5]+ev(co,s,5)
    l1,l2,l3,l4=ell[1:5]
    P4=phi[4]-6*l1*phi[3]+(11*l1*l1-4*l2)*phi[2]+(-6*l1**3+7*l1*l2-l3)*phi[1]
    P5=phi[5]-10*l1*phi[4]+(35*l1*l1-10*l2)*phi[3]+(-50*l1**3+45*l1*l2-5*l3)*phi[2]+(24*l1**4-46*l1*l1*l2+7*l2*l2+11*l1*l3-l4)*phi[1]
    wr,zr=static_refs(phi[0],t,pt,p['m2']);c=j['sigma']*p['gamma']/2;m=p['m2'];P=phi[0]
    C1=-(3*P*P*c*m+2*P*P*m*pt+66*P*m*t+36*c*c*pt-324*c*pt*pt+11*c*t*t-36*c+24*m*pt+1008*pt**3-190*pt*t*t-24*pt)/3
    S=u+4*pt*t-m*P
    return P5-L**5*zr+(16*pt-c)*(L*P4-L**5*wr)+L**5*(C1*S-fmpq(32,3)*t*S*S)


def remainder_eval(base,rem,eps):
    out=rem.c[EPS_ORDER]*arb(eps**EPS_ORDER)
    for n in range(EPS_ORDER):out+=base.c[n]*arb(eps**n)
    return out


def prepare(eps,jets,p):
    eps=fmpq(eps)
    e=Taylor([0,1]+[0]*(EPS_ORDER-1))
    er=Taylor([interval(min(fmpq(0),eps),max(fmpq(0),eps)),1]+[0]*(EPS_ORDER-1))
    co=c7_series(e,jets,p,True);cr=c7_series(er,jets,p,False)
    c7=[remainder_eval(a,b,eps) for a,b in zip(co,cr)]
    W=[];details=[]
    for side,j in enumerate(jets):
        z=W_series(e,j,p,co,side);r=W_series(er,j,p,cr,side)
        removed=[z.c[0],z.c[1]];z.c[0]=arb(0);z.c[1]=arb(0)
        W.append(remainder_eval(z,r,eps))
        details.append({'base_coefficients':z.c,'remainder_coefficient':r.c[EPS_ORDER],
                        'analytically_zero_unreduced_interval_coefficients':removed})
    return {'eps':eps,'c7':c7,'W':W,'W_epsilon_evidence':details,
            'c7_epsilon_evidence':[{'base':a.c,'remainder':b.c[EPS_ORDER]} for a,b in zip(co,cr)]}


def wall_increment(y,j,p,eps):
    """Centered exact slope target and q-r/S data using physical source identities."""
    H,T=j['H'],j['T'];P=j['Phi'][0];psi=j['psi'][0];f=j['f'][0]
    c=j['sigma']*p['gamma']/2;df=eps*f;dt=c*df
    dp_quad=-j['sigma']*p['gamma']*df*df/12;dp=-T*df/3+dp_quad
    ell=-2*eps*psi;L=exp(ell);pt=H+dp;t=T+dt
    target=H*e2(ell)+dp_quad+e1(ell)*dp
    dr=2*H*dp+dp*dp-(2*T*dt+dt*dt)/12+p['m2']*(2*P*df+df*df)/12
    ell_s=-2*eps*j['psi'][1]
    du=j['Phi'][2]*e1(-2*ell)+eps*j['f'][2]*exp(-2*ell)-ell_s*t*exp(-ell)
    S=du+4*H*dt+4*T*dp+4*dp*dt-p['m2']*df
    return {'target':target,'dr':dr,'S':S,'L':L,'p':pt,'t':t,'c':c,'psi':psi}
