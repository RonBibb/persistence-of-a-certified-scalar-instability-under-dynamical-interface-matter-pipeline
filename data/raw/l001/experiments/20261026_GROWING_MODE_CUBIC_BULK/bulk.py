"""General-rate neutral cubic S6 exact polynomial qualification; no radial solve."""
import importlib.util,sys
from pathlib import Path
from fractions import Fraction as Q
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION'
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
ring=load('cubic_bulk_ring',BASE/'T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py')
S=load('qualified_cubic_series',ROOT.parent/'20261026T023331Z_CUBIC_GRAPH/series.py').S
def need(v,label):
    if not v:raise AssertionError(label)
class QualificationInconclusive(AssertionError):
    def __init__(self,evidence):
        super().__init__('POLYNOMIAL_REDUCTION_INCONCLUSIVE_NOT_PHYSICAL_INCOMPATIBILITY');self.evidence=evidence
def setup():
    global G,g,H,T,Phi,e,p,f,P,F,m,h,r,C,J,mu1,mu2,mu3,c2,Sp2,Sc2,Sg2,u,U,gp,Gp,Hp,Tp,DERIV
    ring.NAMES=('G','g','H','T','Phi','e','p','f','P','F','m','C','J','r','h');ring.N=len(ring.NAMES);ring.ZERO=(0,)*ring.N
    G,g,H,T,Phi,e,p,f,P,F,m,C,J,r,h=[ring.variable(j) for j in range(ring.N)]
    mu1=-r*(r+3*h);mu2=-2*r*(2*r+3*h);mu3=-3*r*(3*r+3*h);Hp=-T*T/3-h*h*e;Tp=m*Phi-4*H*T;u=-2*H*p-T*f/3
    gp=-4*H*g+(m-mu1*e+2*T*T)*f+(12*H*T-4*m*Phi)*p
    c2=-C*(6*p*p+f*f);cp=-C*(12*p*u+2*f*g)
    Sp2=H*c2-p*u-f*g/6
    qK2=(4*m-6*mu1*e)*p*f+6*u*g-8*m*Phi*p*p
    qR2=6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2-e*((12*h*h-3*r*r-18*h*r)*p*p+r*r*f*f/2)
    Sc2=12*H*Sp2-(12*H*H-T*T)*c2+qR2
    Sg2=T*cp+2*m*Phi*c2-6*T*Sp2-qK2
    U=-2*H*P-T*F/3+Sp2
    Gp=-4*H*G+(m-mu2*e+2*T*T)*F+(12*H*T-4*m*Phi)*P+Sg2
    DERIV=(Gp,gp,Hp,Tp,T,-2*H*e,u,g,U,G,ring.P(0),ring.P(0),ring.P(0),ring.P(0),ring.P(0))
def ds(v):return sum((v.derivative(j)*q for j,q in enumerate(DERIV)),ring.P(0))
def radial(s):return S([ds(ring.P.cast(v)) for v in s.a])
def direct():
    ps=S([0,p,P]);bs=S([0,-2*p,c2-2*P]);fs=S([0,f,F])
    dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r)
    up,ub,gf=radial(ps),radial(bs),radial(fs)
    ep=(-2*ps).expzero();eb=(-2*bs).expzero()
    return {'T':(bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df,
            'M':radial(dp)-db*(H+up)+df*(T+gf)/3,
            'K':-e*ep*(fs.dt(r).dt(r)+(3*h+2*dp+db)*df)+eb*(Tp+radial(gf)+(4*H+4*up-ub)*(T+gf))-m*(Phi+fs),
            'R':eb*(6*(H+up)*(H+up)-(T+gf)*(T+gf)/2)-6+m*(Phi+fs)*(Phi+fs)/2-e*ep*(6*h*h+3*(ps.dt(r).dt(r)+3*h*dp)+3*dp*dp+df*df/2)}
def closed():
    cp=ds(c2)
    b2exp=-2*c2+4*P+8*p*p
    b3exp=-8*p*c2+16*p*P+Q(32,3)*p*p*p
    ka1=gp+4*H*g+6*u*T
    ka2=Gp+4*H*G+(6*U-cp)*T+6*u*g
    ka3=6*u*G+(6*U-cp)*g
    kt1=-mu1*f;kt2=-mu2*F;kt3=2*r*r*c2*f
    qr0=6*H*H-T*T/2;qr1=12*H*u-T*g
    qr2=12*H*U-T*G+6*u*u-g*g/2;qr3=12*u*U-g*G
    rt1=-3*mu1*p;rt2=-3*mu2*P+3*r*r*p*p+r*r*f*f/2
    rt3=12*r*r*p*P+2*r*r*f*F
    return {'T':4*r*r*(6*p*P+f*F-3*p*c2),
            'M':r*(2*p*U+(4*P-2*c2)*u+(f*G+2*F*g)/3),
            'K':ka3+4*p*ka2+b2exp*ka1+b3exp*m*Phi-e*(kt3-2*p*kt2+(-2*P+2*p*p)*kt1),
            'R':qr3+4*p*qr2+b2exp*qr1+b3exp*qr0+m*f*F-e*(rt3-2*p*rt2+(-2*P+2*p*p)*rt1+(4*p*P-Q(4,3)*p*p*p)*6*h*h)}
def qualify():
    setup();rows=direct();q=closed();checks=[]
    params=[2*(2*r-h)*C-r,3*(3*r-h)*J-4*r]
    def clear(v):
        # Exact substitution C=r/L, J=4r/M with common denominator.
        ci=ring.NAMES.index('C');ji=ring.NAMES.index('J')
        mc=max((a[ci] for a in v.t),default=0);mj=max((a[ji] for a in v.t),default=0)
        L=2*(2*r-h);M=3*(3*r-h);out=ring.P(0)
        for powers,coef in v.t.items():
            a=list(powers);nc=a[ci];nj=a[ji];a[ci]=a[ji]=0
            out+=ring.P({tuple(a):coef})*(r**nc)*((4*r)**nj)*(L**(mc-nc))*(M**(mj-nj))
        return out
    def eq(a,b,label):need(clear(a-b).iszero(),label);checks.append(label)
    bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
    C1=T*g-Tp*f+(2*T*T-3*(mu1+4*h*h)*e)*p
    C2=T*G-Tp*F+(2*T*T-3*(mu2+4*h*h)*e)*P-Sc2
    for key in rows:
        eq(rows[key].a[0],bg if key=='R' else ring.P(0),'BACKGROUND:'+key)
        eq(rows[key].a[1],-C1 if key=='R' else ring.P(0),'FIRST:'+key)
        eq(rows[key].a[2],-C2 if key=='R' else ring.P(0),'SECOND:'+key)
        eq(rows[key].a[3],q[key],'CUBIC_DIRECT_CLOSED:'+key)
    c3=-J*(6*p*P+f*F-3*p*c2)
    Sp3=H*c3-(2*p*U+(4*P-2*c2)*u+(f*G+2*F*g)/3)/3
    eq(3*r*(3*r-h)*c3+q['T'],ring.P(0),'TRACE_DIVISOR')
    eq(3*r*(Sp3-H*c3)+q['M'],ring.P(0),'MIXED_DIVISOR')
    Sc3=12*H*Sp3-(12*H*H-T*T)*c3+q['R']
    Sg3=T*ds(c3)+2*m*Phi*c3-6*T*Sp3-q['K']
    residual=ds(Sc3)+4*H*Sc3-T*Sg3-(2*T*T-3*(mu3+4*h*h)*e)*Sp3
    quot,rem=ring.divide(residual,[C2,C1,bg])
    if not clear(rem).iszero():raise QualificationInconclusive({'raw_residual':residual.pack(),'generators':[v.pack() for v in (C2,C1,bg)],'quotients':[v.pack() for v in quot],'remainder':clear(rem).pack(),'checks_already_passed':checks})
    checks.append('CUBIC_BIANCHI_REMAINDER')
    eq(ds(C1)+4*H*C1,ring.P(0),'FIRST_CONSTRAINT_PRESERVATION')
    second_quot,second_rem=ring.divide(ds(C2)+4*H*C2,[C1,bg])
    need(clear(second_rem).iszero(),'SECOND_CONSTRAINT_PRESERVATION_MOD_LOWER');checks.append('SECOND_CONSTRAINT_PRESERVATION_MOD_LOWER')
    for key,bad in (('T',q['T']+12*r*r*p*c2),('M',q['M']+2*r*c2*u),('K',q['K']+e*2*r*r*c2*f)):
        need(not (rows[key].a[3]-bad).iszero(),'MUTATION:'+key);checks.append('MUTATION:'+key)
    return {'pass':True,'checks':checks,'variables':ring.NAMES,'sources':{a:b.pack() for a,b in dict(q,c3=c3,Sp3=Sp3,Sc3=Sc3,Sg3=Sg3).items()},'compatibility_raw':residual.pack(),'compatibility_generators':[v.pack() for v in (C2,C1,bg)],'compatibility_quotients':[v.pack() for v in quot],'compatibility_remainder':clear(rem).pack(),'scope':'Exact Eulerian cubic bulk source qualification under authenticated lower-order equations. No cubic field solution.'}

