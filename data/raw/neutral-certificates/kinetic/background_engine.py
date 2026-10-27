"""Whole-parameter-box polynomial Picard/Taylor enclosure; no run on import."""
from fractions import Fraction
from dyadic_interval import I,SCALE
ORDER=5
MAX_PICARD=32
NAMES=['W','H','Phi','T','Ewarp','q']

def initial(model):
    m={n:I.exact(v) for n,v in model['model_exact'].items()}
    A=I.endpoints(*model['A']);disp=A-m['v0']
    H=-(m['lambda_a']+m['gamma']*disp.square()/2)/6
    T=m['gamma']*disp/2
    m['k']=H.square()-1-T.square()/12+m['m2']*A.square()/12
    return [I.exact(0),H,A,T,I.exact(1),I.exact(0)],m

def rhs(y,p):
    W,H,P,T,E,q=y
    return [H,-T.square()/3-p['k']*E.square(),T,p['m2']*P-4*H*T,-H*E,E]

def conv(a,b,n):return sum((a[j]*b[n-j] for j in range(n+1)),I.exact(0))
def coeff(y,order,p):
    c=[[v] for v in y];W,H,P,T,E,q=c
    for n in range(order):
        val=[H[n],-conv(T,T,n)/3-p['k']*conv(E,E,n),T[n],p['m2']*P[n]-4*conv(H,T,n),-conv(H,E,n),E[n]]
        for row,v in zip(c,val):row.append(v/(n+1))
    return c

def picard(y,h,p):
    dt=I.endpoints(0,h);box=[a.hull(a+dt*v).pad() for a,v in zip(y,rhs(y,p))]
    for j in range(1,MAX_PICARD+1):
        image=[a.hull(a+dt*v) for a,v in zip(y,rhs(box,p))]
        if all(a.inside(b) for a,b in zip(image,box)):return box,j
        box=[a.hull(b).pad() for a,b in zip(image,box)]
    raise RuntimeError('Strict whole-step Picard inclusion failed')

def evaluate(point,remainder,lo,hi):
    t=I.endpoints(lo,hi);out=[]
    for c,r in zip(point,remainder):
        v=r
        for a in reversed(c):v=v*t+a
        out.append(v)
    return out

def step(y,h,p):
    if h<=0:raise ValueError('Nonpositive validated step')
    box,j=picard(y,h,p);point=coeff(y,ORDER-1,p);rem=[row[ORDER] for row in coeff(box,ORDER,p)]
    return evaluate(point,rem,h,h),evaluate(point,rem,0,h),box,j,point,rem

def controls():
    checks=[]
    grid=[Fraction(-7,3),Fraction(-1,10),Fraction(0),Fraction(2,7),Fraction(13,4)]
    for a in grid:
        for b in grid:
            x,y=I.exact(a),I.exact(b)
            checks.extend([(x+y).contains(a+b),(x-y).contains(a-b),(x*y).contains(a*b),x.square().contains(a*a)])
            if b:checks.append((x/y).contains(a/b))
    p={'k':I.exact(0),'m2':I.exact(0)};y=[I.exact(v) for v in [0,-1,0,0,1,0]]
    c=coeff(y,5,p);fac=1
    for n in range(6):
        if n:fac*=n
        checks.append(c[4][n].contains(Fraction(1,fac)))
        checks.append(c[5][n].contains(0 if n==0 else Fraction(1,fac)))
    h=Fraction(1,8);end,ran,box,it,point,rem=step(y,h,p)
    term=Fraction(1);series=term
    for n in range(1,21):term=term*h/n;series+=term
    nextterm=term*h/21;upper=series+nextterm/(1-h/Fraction(22))
    checks += [end[4].contains(series),end[4].contains(upper),end[5].contains(series-1),end[5].contains(upper-1),end[0].contains(-h),end[1].contains(-1)]
    if not all(checks):raise RuntimeError('Exact arithmetic/synthetic vacuum control failed')
    return {'status':'PASS','rational_and_vacuum_checks':len(checks),'synthetic_vacuum_steps':1,'scientific_background_steps':0,'float_inputs_used':False}
