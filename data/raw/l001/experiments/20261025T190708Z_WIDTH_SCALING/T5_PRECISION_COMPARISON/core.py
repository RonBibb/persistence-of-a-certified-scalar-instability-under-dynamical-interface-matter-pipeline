import hashlib,itertools,json,os,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from interval import I,box,power
CONTEXT={}
RBG=[I(x) for x in (3,5,F(1,10),2)]
LIMITS=[(F(9,10),F(11,10)),(F(-21,10),F(-19,10)),(F(-1,100),F(1,100)),(F(-1,50),F(1,50))]
TRACE=[]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data):
    dest=HERE/name
    assert not dest.exists(),'OVERWRITE'
    tmp=HERE/(name+'.tmp')
    with tmp.open('x') as f:
        json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
    os.link(tmp,dest); tmp.unlink()
def bg(y):
    a,H,P,T=y[:4]
    return [H*a,-T*T/3-3/(a*a),T,1-P+4*power(P,3)-4*H*T]
def ham(y):
    a,H,P,T=y[:4]
    return H*H-1-T*T/12+(P-P*P/2+power(P,4))/6-3/(a*a)
def coeff(y,mu):
    a,H,P,T=y[:4]; U=bg(y)[3]; K=a*a/(3*(mu+12))
    A=2*K*T*U; E=1-2*K*T*T
    C=-1+12*P*P-mu/(a*a)+4*T*T/3+2*K*U*U
    return A,E,C,-4*H-A
def reduced(y,mu):
    A,E,C,D=coeff(y,mu); f,L=y[4:]
    return bg(y)+[A*f+E*L,C*f+D*L]
def full(y,mu):
    a,H,P,T,psi,f,L=y; U=bg(y)[3]
    return bg(y)+[-2*H*psi-T*f/3,L-2*T*psi,
                  -4*H*L+(-1+12*P*P-mu/(a*a)+4*T*T/3)*f-2*U*psi]
def constraint(y,mu):
    a,H,P,T,psi,f,L=y
    return T*L-bg(y)[3]*f-3*(mu+12)*psi/(a*a)
def step(y,hq,fun,rates,check_bg=True):
    assert len(y)==len(rates)
    h=I(hq); dt=box(min(F(0),hq),max(F(0),hq))
    radii=[(I(abs(hq))*r).hi for r in rates]
    tube=[v+I(-r,r) for v,r in zip(y,radii)]
    if check_bg: assert all(x.in_exact(*lim) for x,lim in zip(tube[:4],LIMITS)),'BACKGROUND_TUBE'
    rhs=fun(tube)
    assert len(rhs)==len(y)
    assert all(b.strict(v+dt*w) for b,v,w in zip(tube,y,rhs)),'TUBE_CONTAINMENT'
    return [v+h*w for v,w in zip(y,rhs)]
def lower(n,half_width):
    y=[I(x) for x in (1,-2,0,0)]; h=-half_width/n
    for j in range(n):
        CONTEXT.update(phase='background',n=n,step=j+1)
        y=step(y,h,bg,RBG)
    assert ham(y).contains(0),'LOWER_HAMILTONIAN'
    return y
def sign(x): return 1 if x.lo>0 else (-1 if x.hi<0 else 0)
def overlap(x,y): return max(x.lo,y.lo)<=min(x.hi,y.hi)
def controls():
    count=0
    for xa,xb,ya,yb in ((F(-1,3),F(2,3),F(1,5),F(4,5)),(-2,-1,-3,-2),(0,1,-1,1)):
        x=box(xa,xb);y=box(ya,yb); xl,xh=x.bounds();yl,yh=y.bounds()
        for out,vals in ((x+y,[a+b for a in (xl,xh) for b in (yl,yh)]),
                         (x-y,[a-b for a in (xl,xh) for b in (yl,yh)]),
                         (x*y,[a*b for a in (xl,xh) for b in (yl,yh)])):
            lo,hi=out.bounds();assert lo<=min(vals) and max(vals)<=hi;count+=1
    try: I(1)/box(-1,1)
    except AssertionError: pass
    else: raise AssertionError('ZERO_DIVISOR_CONTROL')
    for h in (F(-1,100),F(1,100)):
        assert step([I(1)],h,lambda z:[I(1)],[I(2)],False)[0].contains(I(1+h))
    try: step([I(1)],F(1,100),lambda z:[I(1)],[I(0)],False)
    except AssertionError: pass
    else: raise AssertionError('UNDERSIZED_CONTROL')
    for mu in (F(-61,5),F(-1201,100),F(-2),F(-1),F(-1,10),F(0)):
        y=[I(x) for x in (1,-2,0,0)]
        A,E,C,D=coeff(y,mu)
        assert A.contains(0) and E.contains(1) and C.contains(-1-mu+F(2,3)/(mu+12)) and D.contains(8)
        for P,T in ((F(-1,1000),F(-1,100)),(F(0),F(0)),(F(1,1000),F(1,100))):
            z=[I(1),I(-2),I(P),I(T)];f=I(1);L=I(F(1,100));U=bg(z)[3]
            psi=z[0]*z[0]*(z[3]*L-U*f)/(3*(mu+12))
            rr=reduced(z+[f,L],mu); ff=full(z+[psi,f,L],mu)
            assert overlap(rr[-2],ff[-2]) and overlap(rr[-1],ff[-1])
            aa,ee,cc,dd=coeff(z,mu);assert (aa+dd+4*z[1]).contains(0)
    return dict(arithmetic_corners=count,signed_step=True,undersized_rejected=True,
                rational_seed_coefficients=True,constrained_reduction_identity=True,trace_identity=True)
