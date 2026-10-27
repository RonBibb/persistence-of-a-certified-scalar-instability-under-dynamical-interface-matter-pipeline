"""Read-only parent solver imports with local augmented RHS adapters."""
import importlib.util,sys
from pathlib import Path
from flint import arb
import sources
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026_GROWING_MODE_QUADRATIC_R1'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def cubic_from_canonical(z,p):
    W,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh=z[:14]
    A2=p['A2'];P=ap+ah*A2;F=fp+fh*A2;G=gp+gh*A2
    return sources.cubic(H,T,Phi,E*E,a,f,g,P,F,G,p)
def new_rows(H,T,Phi,e,triples,p,s):
    zero=H*0;m=zero+p['m2'];k=zero+p['k'];out=[]
    for j in (0,3):
        a,f,g=triples[j:j+3];sp=s['Sp3'] if j==0 else zero;sg=s['Sg3'] if j==0 else zero
        out.extend([-2*H*a-T*f/3+sp,g,-4*H*g+(m-(zero+p['mu3'])*e+2*T*T)*f+(12*H*T-4*m*Phi)*a+sg])
    return out
def augmented_constraints(mod,y,p):
    lower_count=14 if mod.engine=='primary' else 13
    out=mod.lower.constraints(y[:lower_count],p)
    z=mod.physical(y);W,H,Phi,T,E=z[:5];tp=p['m2']*Phi-4*H*T
    s=cubic_from_canonical(z,p)
    for key,j,load in (('third_particular',14,s['Sc3']),('third_homogeneous',17,arb(0))):
        a,f,g=z[j:j+3];out[key]=T*g-tp*f+(2*T*T-3*(p['mu3']+4*p['k'])*E*E)*a-load
    return out
def primary():
    m=load('cubic_primary_augmented',PARENT/'primary.py');lower=load('cubic_primary_lower',PARENT/'primary.py')
    m.STATE_SIZE=20;m.lower=lower;m.engine='primary'
    def physical(y):
        if len(y)!=20:raise ValueError('TWENTY_PRIMARY_STATES_REQUIRED')
        return list(y)
    def rhs(y,p):
        z=physical(y);s=cubic_from_canonical(z,p);W,H,Phi,T,E=z[:5]
        return lower.rhs(y[:14],p)+new_rows(H,T,Phi,E*E,z[14:],p,s)
    m.physical=physical;m.rhs=rhs;m.constraints=lambda y,p:augmented_constraints(m,y,p)
    return m
class Jet:
    """Independent list-convolution algebra for added cubic coefficient rows."""
    def __init__(self,a):self.a=list(a)
    def cast(self,x):return x if isinstance(x,Jet) else Jet([x]+[arb(0)]*(len(self.a)-1))
    def __add__(self,x):return Jet([a+b for a,b in zip(self.a,self.cast(x).a)])
    __radd__=__add__
    def __neg__(self):return Jet([-a for a in self.a])
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        b=self.cast(x).a;c=[]
        for n in range(len(self.a)):
            v=arb(0)
            for j in range(n+1):v+=self.a[j]*b[n-j]
            c.append(v)
        return Jet(c)
    __rmul__=__mul__
    def __truediv__(self,x):return Jet([a/x for a in self.a])
    def exp(self):
        out=[self.a[0].exp()]
        for n in range(1,len(self.a)):
            v=arb(0)
            for j in range(1,n+1):v+=j*self.a[j]*out[n-j]
            out.append(v/n)
        return Jet(out)
def independent():
    m=load('cubic_independent_augmented',PARENT/'independent.py');lower=load('cubic_independent_lower',PARENT/'independent.py')
    m.DIMENSION=19;m.lower=lower;m.engine='independent'
    def physical(y):
        if len(y)!=19:raise ValueError('NINETEEN_INDEPENDENT_STATES_REQUIRED')
        return list(y[:4])+[(-y[0]).exp()]+list(y[4:])
    def point_source(y,p):
        W,H,Phi,T,a,f,g,ap,fp,gp,ah,fh,gh=y[:13];A2=p['A2']
        e=(-2*W).exp();s=sources.cubic(H,T,Phi,e,a,f,g,ap+ah*A2,fp+fh*A2,gp+gh*A2,p)
        return H,T,Phi,e,s
    def rhs(y,p):
        if len(y)!=19:raise ValueError('NINETEEN_INDEPENDENT_STATES_REQUIRED')
        H,T,Phi,e,s=point_source(y,p)
        return lower.rhs(y[:13],p)+new_rows(H,T,Phi,e,y[13:],p,s)
    def jet_rhs(c,p,n):
        z=[Jet(row) for row in c];H,T,Phi,e,s=point_source(z,p)
        tail=new_rows(H,T,Phi,e,z[13:],p,s)
        return lower._jet_rhs(c[:13],p,n)+[v.a for v in tail]
    m.physical=physical;m.rhs=rhs;m._jet_rhs=jet_rhs;m.constraints=lambda y,p:augmented_constraints(m,y,p)
    return m

