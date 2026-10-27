"""Exact rational comparison bounds for the COMPLEX parameter polydisc.

No physical trajectory, fitted point, finite difference, or sampled nonlinear
family is evaluated here. Every input is a prospective uniform bound.
"""
from fractions import Fraction as Q
import math

N=5
R0=Q(1,2**4096)
DELTA=Q(1,2**9216)


def conv(a,b,n):return sum((a[j]*b[n-j] for j in range(n+1)),Q(0))
def mul(a,b):return [conv(a,b,n) for n in range(6)]
def add(*a):return [sum(v[j] for v in a) for j in range(6)]
def scale(a,x):return [abs(x)*v for v in a]
def c(x):return [abs(Q(x))]+[Q(0)]*5
def d(a):return [(j+1)*a[j+1] for j in range(5)]+[Q(0)]
def exp_series(a,seed):
    out=[Q(seed)]
    for n in range(1,6):out.append(sum(j*a[j]*out[n-j] for j in range(1,n+1))/n)
    return out


class Bound:
    """Absolute value and first epsilon-derivative bounds on a complex disc."""
    def __init__(self,v=0,der=0):self.v=Q(v);self.der=Q(der)
    def __add__(self,o):
        o=bound(o);return Bound(self.v+o.v,self.der+o.der)
    __radd__=__add__
    # Subtraction also uses the triangle inequality.
    __sub__=__add__
    __rsub__=__add__
    def __mul__(self,o):
        o=bound(o);return Bound(self.v*o.v,self.der*o.v+self.v*o.der)
    __rmul__=__mul__
    def __truediv__(self,o):
        assert Q(o)>0
        return Bound(self.v/Q(o),self.der/Q(o))


def bound(x):return x if isinstance(x,Bound) else Bound(abs(Q(x)))
def exp_bound(x):
    assert x.v<=Q(1,2)
    # For |z|<=1/2, |exp z|<=exp(1/2)<2.
    return Bound(2,2*x.der)


def inverse(matrix):
    size=len(matrix)
    a=[[Q(x) for x in row]+[Q(int(i==j)) for j in range(size)] for i,row in enumerate(matrix)]
    for i in range(size):
        pivot=next(j for j in range(i,size) if a[j][i])
        a[i],a[pivot]=a[pivot],a[i];v=a[i][i];a[i]=[x/v for x in a[i]]
        for j in range(size):
            if j!=i:
                v=a[j][i];a[j]=[x-v*y for x,y in zip(a[j],a[i])]
    return [row[size:] for row in a]


def falling(p,j):return math.factorial(p)//math.factorial(p-j) if p>=j else 0
def ceil_log2(x):
    assert x>0
    n=x.numerator.bit_length()-x.denominator.bit_length()
    if x>Q(2)**n:n+=1
    return n


def background_mode_majorants():
    # Majorize the polynomial regular equations using all positive terms.
    cs=[[Q(v)] for v in (3,2,2,2,16,2**1024,2**1024,2**1024)]
    W,H,P,T,E,u,f,g=cs;ee=[];tt=[];ht=[]
    for n in range(5):
        ee.append(conv(E,E,n));tt.append(conv(T,T,n));ht.append(conv(H,T,n))
        r=[H[n],tt[n]/3+Q(1,1000)*ee[n],T[n],P[n]+4*ht[n],conv(H,E,n),
           2*conv(H,u,n)+conv(T,f,n)/3,g[n],
           4*conv(H,g,n)+f[n]+Q(1,500)*conv(ee,f,n)+2*conv(tt,f,n)
           +12*conv(ht,u,n)+4*conv(P,u,n)]
        for row,value in zip(cs,r):row.append(value/Q(n+1))
    bg=[[x*math.factorial(j) for j,x in enumerate(row)] for row in cs[:5]]
    mo=[[x*math.factorial(j) for j,x in enumerate(row)] for row in cs[5:]]
    assert max(x for row in mo for x in row)<2**1536
    return cs,bg,mo


def preparation_bound(bg):
    mode=Q(2**1536)
    phi=[Bound(bg[2][j]+R0*mode,mode) for j in range(6)]
    ell=[Bound(2*R0*mode,2*mode) for _ in range(6)]
    L=exp_bound(ell[0]);Lm2=exp_bound(2*ell[0]);L3=exp_bound(3*ell[0])
    U=8+10*(phi[0]+1)*(phi[0]+1);V=6+phi[0]*phi[0]/2
    p=U/6;t=10*(phi[0]+1);first=L*t
    tl=(phi[2]+ell[1]*first)*Lm2
    tll=(6*p+10)*tl+(4*p*p+1+t*t+2*V/3+40*p)*t+(2*p+10)*phi[0]
    third=L3*tll+3*ell[1]*phi[2]+(2*ell[1]*ell[1]+ell[2])*first
    jet_der=max((first+phi[1]).der,(third+phi[3]).der)
    M=[]
    for side in range(2):
        for j in range(4):
            M.append([Q(falling(p,j)*(side**(p-j))) if p>=j else Q(0) for p in range(8)])
    inv=inverse(M)
    coeff=[sum(abs(inv[p][col])*3**max(col%4-p,0) for col in range(8)) for p in range(8)]
    hermite=max(sum(coeff[p]*falling(p,j)*3**(p-j) for p in range(j,8)) for j in range(6))
    h0={5+r:Q(math.comb(6,r),120) for r in range(7)}
    h1={6+r:Q(math.comb(5,r),120) for r in range(6)}
    shapes=max(sum(row.get(p,Q(0))*falling(p,j)*3**(p-j) for p in range(j,12))
               for row in (h0,h1) for j in range(6))
    C=max(mode+hermite*jet_der+2*shapes,2*mode)
    assert C<2**1800
    return C,{'profile_derivative_log2_upper':ceil_log2(jet_der),
              'hermite_jet_operator_log2_upper':ceil_log2(hermite),
              'fifth_shape_jet_log2_upper':ceil_log2(shapes),
              'complete_prescribed_deviation_coefficient_log2_upper':ceil_log2(C)}


def row_map_bound(cs):
    # All these are coefficient bounds at an arbitrary real s and arbitrary
    # complex parameters in the proved metric/preparation tube.
    phi=[cs[2][j]+Q(1,math.factorial(j)) for j in range(6)]
    ell=[Q(1,16*math.factorial(j)) for j in range(6)]
    L2=exp_series(scale(ell,2),2);ellp=d(ell);phip=d(phi);phi2=mul(phi,phi)
    A=[Q(4)];P=[Q(3)];R=[Q(512)];LR=[]
    for n in range(5):
        LR.append(conv(L2,R,n))
        pn=conv(ellp,P,n)+Q(1,1000)*LR[n]+2*L2[n]+conv(L2,phi2,n)/6+conv(phip,phip,n)/6+2*conv(P,P,n)
        rn=2*conv(P,R,n)
        A.append(P[n]/(n+1));P.append(pn/(n+1));R.append(rn/(n+1))
    a,b,t=map(d,(A,ell,phi));aa,bb,tt=map(d,(a,b,t))
    fac=exp_series(scale(A,2),2**16);rad=exp_series(scale(ell,2),2)
    curv=scale(R,Q(1,1000));potential=add(c(6),scale(mul(phi,phi),Q(1,2)))
    TA=add(aa,scale(mul(a,a),4),mul(b,a))
    TB=add(scale(aa,4),scale(mul(a,a),4),scale(mul(b,a),4),mul(t,t))
    TC=add(tt,mul(add(scale(a,4),b),t))
    SA=add(mul(rad,TA),scale(curv,2),scale(potential,Q(2,3)))
    SB=add(mul(rad,TB),scale(potential,Q(2,3)))
    SC=add(mul(rad,TC),phi)
    second=[mul(fac,S) for S in (SA,SB,SC)]
    U,V,F=[v[:4]+[Q(0),Q(0)] for v in second];up,vp,fp=map(d,(U,V,F));upp,vpp,fpp=map(d,(up,vp,fp))
    DTA=add(upp,scale(mul(a,up),8),mul(vp,a),mul(b,up))
    DTB=add(scale(upp,4),scale(mul(a,up),8),scale(mul(vp,a),4),scale(mul(b,up),4),scale(mul(t,fp),2))
    DTC=add(fpp,mul(add(scale(up,4),vp),t),mul(add(scale(a,4),b),fp))
    DS_A=add(mul(rad,add(DTA,scale(mul(V,TA),2))),scale(mul(curv,U),4),scale(mul(phi,F),Q(2,3)))
    DS_B=add(mul(rad,add(DTB,scale(mul(V,TB),2))),scale(mul(phi,F),Q(2,3)))
    DS_C=add(mul(rad,add(DTC,scale(mul(V,TC),2))),F)
    A4=add(scale(mul(V,U),2),scale(U,Q(4,1000)),scale(mul(U,U),2),mul(fac,DS_A))
    E4=add(scale(mul(U,V),2),scale(V,Q(4,1000)),scale(mul(V,V),2),mul(fac,DS_B))
    F4=add(scale(mul(U,F),2),scale(mul(V,F),2),scale(F,Q(4,1000)),mul(fac,DS_C))
    A2,E2,F2=second
    fourth_bound=(2*(F4[1]+E4[0]*phi[1]+6*E2[0]*F2[1]+3*E2[0]*E2[0]*phi[1])+10*F4[0])*2**34
    israel_bound=3+2*(8+10*(3+1)**2)/Q(6)
    M=max(fourth_bound,israel_bound)
    assert M<2**512
    return M,{'boundary_map_log2_upper':ceil_log2(M),
              'metric_jet_coefficient_log2_upper':max(ceil_log2(v) for v in A if v)}


def certify():
    cs,bg,mo=background_mode_majorants();C,profile=preparation_bound(bg);M,rows=row_map_bound(cs)
    # Exact comparison constants for the 1/16 complex tube.
    tube=Q(1,16);exp_tube=Q(1)/(1-4*tube)
    metric_lipschitz=2*exp_tube+tube+4*(2+tube)
    assert metric_lipschitz<16
    # Triangle-inequality coefficients for the forcing difference at A=W,P=H.
    # |e^(2ell)-1|<=4|ell|, |Phi|,|Phi_s|<=3, and m2<=1.
    forcing_C=2+4+8+Q(1,6)*(2*5+4*4)+Q(5,6)
    # Lower launch: |L-1|<=2|ell|, |pwall|<=28; |dpwall|<=14|dPhi|.
    launch_C=56+14
    assert forcing_C<256 and launch_C<256
    displacement=4*256*C*R0*2**96
    assert displacement<2**2000*R0<tube
    assert C*R0<tube
    contraction=128*2**64*2**512*DELTA/(R0*R0)
    selfmap=32*2**64*2**512*DELTA/(R0*R0)
    assert DELTA/R0<Q(1,8) and contraction<Q(1,2) and selfmap<Q(1,2)
    return {'pass':True,'evidence':'EXACT_RATIONAL_COMPLEX_DOMAIN_COMPARISON_BOUNDS',
            'conditional_on_runtime_background_and_inverse_gates':True,
            'physical_outcomes_evaluated':False,'r0_power_of_two':-4096,'amplitude_radius_power_of_two':-9216,
            'mode_initial_norm_bound':8,'mode_matrix_norm_bound':128,'mode_global_log2_bound':1024,
            'mode_fifth_jet_log2_upper':max(ceil_log2(v) for row in mo for v in row if v),
            **profile,**rows,'metric_lipschitz_exact':str(metric_lipschitz),
            'forcing_coefficient_exact':str(forcing_C),'launch_coefficient_exact':str(launch_C),
            'metric_displacement_log2_upper':ceil_log2(displacement),
            'contraction_exact':str(contraction),'selfmap_ratio_exact':str(selfmap),
            'sample_amplitudes_included':False}


if __name__=='__main__':
    import json
    print(json.dumps(certify(),indent=2))
