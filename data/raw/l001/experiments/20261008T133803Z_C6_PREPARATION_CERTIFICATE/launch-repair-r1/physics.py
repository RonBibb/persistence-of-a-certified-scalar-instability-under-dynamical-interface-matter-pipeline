"""Action-derived centered five-variable flow and interval corner recursion."""
import math
from fractions import Fraction
from flint import arb, fmpq
from inherited.algebra import Taylor, e1, e2, exp, ev
from inherited.series import bounds, interval, power
from inherited import source_flow, preparation

def intersect(a,b):
    lo=max(bounds(a)[0],bounds(b)[0]); hi=min(bounds(a)[1],bounds(b)[1])
    if lo>hi: raise ArithmeticError("Disjoint enclosures of the same exact source")
    return interval(lo,hi)

def shapes(s,D):
    out=[]
    for j in (5,7):
        den=math.factorial(j)*power(D,j+1)
        l=s**j*(D-s)**(j+1)/den
        lp=(j*s**(j-1)*(D-s)**(j+1)-(j+1)*s**j*(D-s)**j)/den
        rr=s**(j+1)*(s-D)**j/den
        rp=((j+1)*s**j*(s-D)**j+j*s**(j+1)*(s-D)**(j-1))/den
        out.extend([(l,lp),(rr,rp)])
    return out

def evaluate(y,p):
    W,H,P,T,E,psi,f,g,s,w,v=y[:11]
    eps=p['eps']; k=p['k']; m=p['m2']; hs=shapes(s,p['D'])
    d=ev(p['c7'],s); ds=ev(p['c7'],s,1)
    for b,(h,hp) in zip(p['x'][1:],hs): d+=b*h; ds+=b*hp
    ps=-2*H*psi-T*f/3; ell_s=-2*eps*ps
    qbg=k*E*E; z=-4*eps*psi; a=-6*eps*psi-2*w
    vv=eps*ps+v; ef=eps*f; eg=eps*g
    rv=-4*H*v-2*qbg*w-2*eps*ps*vv-2*vv*vv+qbg*e2(a)+2*e2(z)
    rv-=m*(P*P*e2(z)+2*P*ef*e1(z)+exp(z)*(ef*ef+2*(P+ef)*d+d*d))/6
    rv-=T*ds/3+(eg+ds)*(eg+ds)/6
    src=source_flow.rhs(y[:9],p); src[8]=s*0+1
    out=src+[v,rv]
    for j in range((len(y)-11)//2):
        u,r=y[11+2*j:13+2*j]
        force=0 if j==0 else (m*exp(z)*(P+ef+d)*hs[j-1][0]+(T+eg+ds)*hs[j-1][1])/3
        out += [r,(ell_s-4*(H+vv))*r-2*qbg*exp(a)*u-force]
    return out

def rhs(y,p): return [v.c[0] for v in evaluate([Taylor([v]) for v in y],p)]
def coeff(y,N,p):
    c=[[v] for v in y]
    for n in range(N):
        out=evaluate([Taylor(row) for row in c],p)
        for row,v in zip(c,out): row.append(v.c[n]/(n+1))
    return c

class Dual:
    size=5
    def __init__(self,v=0,d=None):
        if isinstance(v,Dual): self.v=v.v; self.d=v.d; return
        self.v=v if isinstance(v,arb) else arb(v)
        self.d=tuple(arb(0) for _ in range(self.size)) if d is None else tuple(d)
    def __add__(self,o):
        o=Dual(o); return Dual(self.v+o.v,[a+b for a,b in zip(self.d,o.d)])
    __radd__=__add__
    def __neg__(self): return Dual(-self.v,[-a for a in self.d])
    def __sub__(self,o): return self+-Dual(o)
    def __rsub__(self,o): return Dual(o)+-self
    def __mul__(self,o):
        o=Dual(o); return Dual(self.v*o.v,[a*o.v+self.v*b for a,b in zip(self.d,o.d)])
    __rmul__=__mul__
    def __truediv__(self,o):
        o=Dual(o); return Dual(self.v/o.v,[(a-self.v*b/o.v)/o.v for a,b in zip(self.d,o.d)])
    def __rtruediv__(self,o): return Dual(o)/self
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        if n==0: return Dual(1)
        return Dual(power(self.v,n),[n*power(self.v,n-1)*a for a in self.d])
    def exp(self):
        e=self.v.exp(); return Dual(e,[e*a for a in self.d])

class Jet:
    order=7
    def __init__(self,v=0):
        if isinstance(v,Jet): v=v.c
        if not isinstance(v,(list,tuple)): v=[v]
        self.c=[Dual(x) for x in v[:self.order+1]]+[Dual(0)]*max(0,self.order+1-len(v))
    def __add__(self,o):
        o=Jet(o); return Jet([a+b for a,b in zip(self.c,o.c)])
    __radd__=__add__
    def __neg__(self): return Jet([-a for a in self.c])
    def __sub__(self,o): return self+-Jet(o)
    def __rsub__(self,o): return Jet(o)+-self
    def __mul__(self,o):
        o=Jet(o); return Jet([sum((self.c[j]*o.c[i-j] for j in range(i+1)),Dual(0)) for i in range(self.order+1)])
    __rmul__=__mul__
    def __truediv__(self,o): return Jet([a/o for a in self.c])
    def __pow__(self,n):
        assert isinstance(n,int) and n>=0
        out=Jet(1)
        for _ in range(n): out=out*self
        return out
    def exp(self):
        c=[self.c[0].exp()]
        for i in range(1,self.order+1):
            c.append(sum((j*self.c[j]*c[i-j] for j in range(1,i+1)),Dual(0))/i)
        return Jet(c)
    def d(self): return Jet([(i+1)*self.c[i+1] for i in range(self.order)])
    def val(self): return self.c[0]

def shape_unit(j,side):
    c=[fmpq(0)]*(2*j+2)
    if side==0:
        for k in range(j+2): c[j+k]=fmpq(math.comb(j+1,k)*(-1)**k,math.factorial(j))
    else:
        for k in range(j+1): c[j+1+k]=fmpq(math.comb(j,k)*(-1)**(j-k),math.factorial(j))
    return c
def shape_endpoint(j,owner,side,der,D):
    c=shape_unit(j,owner)
    a=sum((c[n]*math.prod(range(n-der+1,n+1))*side**(n-der) for n in range(der,len(c))),fmpq(0))
    return arb(a)*power(D,j-der) if j>=der else arb(a)/power(D,der-j)

def hermite_inverse(n):
    a=[]
    for side in (0,1):
        for der in range(n):
            row=[fmpq(math.prod(range(j-der+1,j+1))*side**(j-der)) if j>=der else fmpq(0) for j in range(2*n)]
            row += [fmpq(int(len(a)==j)) for j in range(2*n)]
            a.append(row)
    for k in range(2*n):
        pivot=next(i for i in range(k,2*n) if a[i][k])
        a[k],a[pivot]=a[pivot],a[k]; d=a[k][k]; a[k]=[v/d for v in a[k]]
        for i in range(2*n):
            if i!=k:
                d=a[i][k]; a[i]=[v-d*w for v,w in zip(a[i],a[k])]
    return [row[2*n:] for row in a]
HM=hermite_inverse(6)

def source_endpoint(y,p,side):
    z=list(y[:9])
    if side and 'source_end' in p:
        z=[intersect(a,b) for a,b in zip(z,p['source_end'])]
    z[8]=arb(0) if side==0 else p['D']
    sig=1-2*side; vi=p['v0' if side==0 else 'v1']; lam=p['lambda_a' if side==0 else 'lambda_b']
    P=z[2]; H=-sig*(lam+p['gamma']*(P-vi)**2/2)/6; T=sig*p['gamma']*(P-vi)/2
    z[1]=intersect(z[1],H); z[3]=intersect(z[3],T)
    z[7]=intersect(z[7],sig*p['gamma']*z[6]/2-2*z[3]*z[5])
    return z

def endpoint_fields(y,p,side):
    z=source_endpoint(y,p,side); cc=source_flow.coeff(z,7,p)
    s=arb(0) if side==0 else p['D']; eps=p['eps']
    js=preparation.wall_jets(z,p,side)
    ph,el,L,pt,t,u,delta=preparation.endpoint_raw(eps,js,p)
    pc=[]; ec=[]
    for n in range(8):
        val=cc[2][n]+eps*cc[6][n]+ev(p['c7'],s,n)/math.factorial(n)
        ds=[arb(0)]
        for idx,(j,own) in enumerate(((5,0),(5,1),(7,0),(7,1))):
            h=shape_endpoint(j,own,side,n,p['D'])/math.factorial(n)
            val+=p['x'][idx+1]*h; ds.append(h)
        if n==0: val=ph[0]
        elif n==1: val=L*t
        elif n==2: val=ph[2]/2
        elif n==3: val=(ph[3]+delta[3])/6
        pc.append(Dual(val,ds)); ec.append(Dual(-2*eps*cc[5][n]))
    F=Jet(pc); ell=Jet(ec)
    derivA=[y[11+2*j] for j in range(5)] if len(y)==21 else [arb(0)]*5
    derivP=[y[12+2*j] for j in range(5)] if len(y)==21 else [arb(0)]*5
    aa=[Dual(z[0]+eps*z[5]+y[9],derivA),Dual(z[1]+eps*cc[5][1]+y[10],derivP)]
    for n in range(6):
        A=Jet(aa); As=A.d()
        V=Jet(-6)+F*F*(p['m2']/2)
        ar=ell.d()*As-2*As*As+(2*ell-2*A).exp()*p['k']-(F.d()*F.d()+2*(2*ell).exp()*V)/6
        aa.append(ar.c[n]/((n+1)*(n+2)))
    return Jet(aa),F,ell,js

TT=6
def tc(x): return [Jet(x)]+[Jet(0) for _ in range(TT)]
def add(*a): return [sum((x[i] for x in a),Jet(0)) for i in range(TT+1)]
def scale(a,c): return [v*c for v in a]
def mul(a,b): return [sum((a[j]*b[i-j] for j in range(i+1)),Jet(0)) for i in range(TT+1)]
def texp(a):
    out=[a[0].exp()]
    for i in range(1,TT+1): out.append(sum((j*a[j]*out[i-j] for j in range(1,i+1)),Jet(0))/i)
    return out
def dt(a): return [(i+1)*a[i+1] for i in range(TT)]+[Jet(0)]

def time_rows(A,B,F,ell,p,side):
    speed=(B-ell).exp(); dx=lambda a:[speed*v.d() for v in a]
    u=[tc(v) for v in (A,B,F)]
    for n in (0,2,4):
        a,b,f=u; ax,bx,fx=[dx(v) for v in u]; at,bt,ft=[dt(v) for v in u]
        EE=texp(scale(b,2)); V=add(tc(-6),scale(mul(f,f),p['m2']/2))
        curv=scale(texp(scale(add(b,scale(a,-1)),2)),p['k'])
        ar=add(dx(ax),scale(add(mul(ax,ax),scale(mul(at,at),-1)),3),scale(curv,-2),scale(mul(EE,V),fmpq(2,3)))
        br=add(dx(bx),scale(add(mul(at,at),scale(mul(ax,ax),-1)),3),scale(curv,3),scale(mul(EE,V),fmpq(-1,3)),scale(add(mul(fx,fx),scale(mul(ft,ft),-1)),fmpq(1,2)))
        fr=add(dx(fx),scale(add(mul(ax,fx),scale(mul(at,ft),-1)),3),scale(mul(EE,f),-p['m2']))
        for q,r in zip(u,(ar,br,fr)): q[n+2]=r[n]/((n+1)*(n+2))
    a,b,f=u; sig=1-2*side
    fv=add(f,tc(-p['v0' if side==0 else 'v1']))
    pot=add(tc(p['lambda_a' if side==0 else 'lambda_b']),scale(mul(fv,fv),p['gamma']/2))
    inv=texp(scale(b,-1)); rows=[]
    for j,q in enumerate(u):
        rr=add(mul(inv,dx(q)),scale(pot,fmpq(sig,6)) if j<2 else scale(fv,-sig*p['gamma']/2))
        rows.append([math.factorial(k)*rr[k].val() for k in (0,2,4,6)])
    return [[rows[j][k] for j in range(3)] for k in range(4)]

class Gauge:
    def __init__(self,D):
        self.D=D; self.target=[Dual(0) for _ in range(12)]; self.eta=[Dual(0),Dual(0)]
    def polynomial(self):
        out=[]
        for n in range(16):
            v=Dual(0)
            if n<12:
                for k in range(12): v+=self.target[k]*(HM[n][k]*power(self.D,k%6)/power(self.D,n))
            for side in (0,1):
                v+=self.eta[side]*(shape_unit(7,side)[n]/power(self.D,n-7) if n>=7 else shape_unit(7,side)[n]*power(self.D,7-n))
            out.append(v)
        return out
    def endpoint(self,side):
        out=[]
        for der in range(8):
            if der<6: v=self.target[6*side+der]
            else:
                v=Dual(0)
                for k in range(12):
                    weight=sum((HM[n][k]*math.prod(range(n-der+1,n+1))*side**(n-der) for n in range(der,12)),fmpq(0))
                    v+=self.target[k]*(weight/power(self.D,der-k%6))
            for own in (0,1): v+=self.eta[own]*shape_endpoint(7,own,side,der,self.D)
            out.append(v/math.factorial(der))
        return Jet(out)

def corner_map(yl,yu,p):
    fields=[endpoint_fields(y,p,side) for side,y in enumerate((yl,yu))]
    q=Gauge(p['D']); rows=None
    for order,index in ((3,1),(5,2),(7,3)):
        rows=[time_rows(A,A+q.endpoint(side),F,ell,p,side) for side,(A,F,ell,_) in enumerate(fields)]
        for side,(A,F,ell,_) in enumerate(fields):
            correction=-(rows[side][index][1]-rows[side][index][0])*((-(order-1))*A.val()+order*ell.val()).exp()
            if order<7: q.target[6*side+order]=correction
            else: q.eta[side]=correction
    rows=[time_rows(A,A+q.endpoint(side),F,ell,p,side) for side,(A,F,ell,_) in enumerate(fields)]
    A,F,ell,js=fields[1]
    sig=-1; phi=F.val(); pt=-sig*(p['lambda_b']+(phi-p['v1'])**2*(p['gamma']/2))/6
    values=[A.c[1]*(-ell.val()).exp()-pt]
    for idx,order in ((2,4),(3,6)):
        for side,(A,F,ell,_) in enumerate(fields): values.append(rows[side][idx][2]*(-order*A.val()).exp())
    return {
      'F':[z.v for z in values], 'J':[list(z.d) for z in values],
      'all_rows':[[[z.v for z in rr] for rr in side] for side in rows],
      'q':[z.v for z in q.polynomial()],
      'q_derivative_targets':[z.v for z in q.target],
      'q7_controls':[z.v for z in q.eta],
      'endpoint_A':[[z.v for z in A.c] for A,F,ell,js in fields],
      'endpoint_Phi':[[z.v for z in F.c] for A,F,ell,js in fields],
      'endpoint_ell':[[z.v for z in ell.c] for A,F,ell,js in fields]
    }
