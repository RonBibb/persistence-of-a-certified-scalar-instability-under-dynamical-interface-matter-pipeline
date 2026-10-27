import hashlib,json,os,sys,math
from fractions import Fraction as F
from pathlib import Path
HERE=Path(__file__).resolve().parent
N=5
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,d):
    p=HERE/n;assert not p.exists();tmp=HERE/(n+'.tmp')
    with tmp.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,p);tmp.unlink()
def c(x):return [F(x)]+[F(0)]*(N-1)
def add(*xs):return [sum((x[j] for x in xs),F(0)) for j in range(N)]
def scale(x,s):return [v*s for v in x]
def mul(x,y):return [sum((x[k]*y[j-k] for k in range(j+1)),F(0)) for j in range(N)]
def inv(x):
    assert x[0]!=0
    y=[1/x[0]]+[F(0)]*(N-1)
    for j in range(1,N):y[j]=-sum((x[k]*y[j-k] for k in range(1,j+1)),F(0))/x[0]
    return y
def rhs(y,mu):
    a,H,P,T,psi,f,g=y
    a2=mul(a,a);P2=mul(P,P);P3=mul(P2,P);T2=mul(T,T);HT=mul(H,T)
    vp=add(c(1),scale(P,-1),scale(P3,4))
    C=add(c(-1),scale(P2,12),scale(inv(a2),-mu),scale(T2,2))
    E=add(scale(HT,12),scale(vp,-4))
    return [mul(H,a),add(scale(T2,F(-1,3)),scale(inv(a2),-3)),T,
        add(vp,scale(HT,-4)),add(scale(mul(H,psi),-2),scale(mul(T,f),F(-1,3))),
        g,add(scale(mul(H,g),-4),mul(C,f),mul(E,psi))]
def main():
    ad=json.loads((HERE/'ADMISSION.json').read_text());assert ad['admitted']
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    assert sys.version_info[:3]==(3,12,3)
    assert digest(Path(sys.executable).resolve())=='c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960'
    assert mul([F(1),F(1),F(0),F(0),F(0)],inv([F(1),F(1),F(0),F(0),F(0)]))==c(1),'SERIES_INVERSE_CONTROL'
    assert mul([F(1),F(1),F(0),F(0),F(0)],[F(1),F(-1),F(0),F(0),F(0)])==[F(1),F(0),F(-1),F(0),F(0)],'SERIES_PRODUCT_CONTROL'
    y=[c(v) for v in (1,-2,0,0,1,0,0)]
    for j in range(N-1):
        r=rhs(y,F(-12))
        for v,w in zip(y,r):v[j+1]=w[j]/(j+1)
    deriv=[y[5][j]*math.factorial(j) for j in range(N)]
    assert deriv[2:]==[F(-4),F(-72),F(-1256)],'CENTRAL_JET'
    def fsecond(lam,B):
        return rhs([c(v) for v in (1,-2,0,0,1,-3*lam,B)],lam-12)[6][0]
    assert fsecond(0,0)==-4
    Bco=fsecond(0,1)-fsecond(0,0)
    Lco=(fsecond(1,0)-fsecond(-1,0))/2
    L2co=(fsecond(1,0)+fsecond(-1,0)-2*fsecond(0,0))/2
    assert (Bco,Lco,L2co)==(8,-33,3),'PARAMETER_COEFFICIENTS'
    B2=-deriv[3]/6;lambda2=deriv[2]/6
    lambda4=((Bco*B2+Lco*lambda2)/2+deriv[4]/24)/3
    assert -3*lambda2+deriv[2]/2==0
    assert B2+deriv[3]/6==0
    assert -3*lambda4+(Bco*B2+Lco*lambda2)/2+deriv[4]/24==0
    assert (B2,lambda2,lambda4)==(12,F(-2,3),F(20,9))
    D=F(1,50);gap2=-lambda2*(D/2)**2;correction=-lambda4*(D/2)**4;gap4=gap2+correction
    br=json.loads((HERE.parent/'T12_DIRICHLET_CEILING/RESULT.json').read_text())['physical_mu_bracket']
    lo=-F(br['hi'])-12;hi=-F(br['lo'])-12
    assert all(digest(HERE/p)==h for p,h in ad['sources'].items())
    save('RESULT.json',dict(classification='CERTIFIED_LOCAL_DIRICHLET_SERIES_COEFFICIENTS',
        background_and_profile_series={name:[str(v) for v in values] for name,values in zip(('a','H','Phi','T','psi','f','g'),y)},
        central_f_derivatives=[str(v) for v in deriv],
        halfwidth_coefficients=dict(g0_d2=str(B2),lambda_d2=str(lambda2),lambda_d4=str(lambda4)),
        fullwidth_gap_coefficients=dict(D2='1/6',D4='-5/36'),
        implicit_jacobian_determinant='-3',
        fixed_width_diagnostic=dict(D=str(D),leading_gap=str(gap2),fourth_order_correction=str(correction),
            corrected_gap=str(gap4),accepted_gap=[str(lo),str(hi)],
            both_approximations_inside=lo<=gap2<=hi and lo<=gap4<=hi,
            enclosure_width_over_correction=str((hi-lo)/abs(correction))),
        fixed_width_remainder_certified=False,moving_physical_walls_claim=False,all_gates_passed=True))
try:main()
except BaseException as e:save('FAILURE.json',dict(classification='TECHNICAL_INCOMPLETE',error=repr(e)));raise
