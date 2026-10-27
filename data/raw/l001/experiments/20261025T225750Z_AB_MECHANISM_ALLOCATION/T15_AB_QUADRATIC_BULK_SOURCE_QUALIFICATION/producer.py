"""Exact Eulerian quadratic S6 source qualification, no n2 solution."""
import importlib.util, os, platform, signal, sys, time, traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('source_common',ROOT/'common.py')
c=importlib.util.module_from_spec(s); s.loader.exec_module(c); c.ROOT=ROOT
NAMES=('g','H','T','Phi','e','p','f','m2','h'); N=len(NAMES); ZERO=(0,)*N

class P:
    """Bounded sparse rational polynomial; lex order, no symbolic dependency."""
    def __init__(self,v=0):
        if isinstance(v,P): self.t=dict(v.t)
        elif isinstance(v,dict): self.t={a:Q(b) for a,b in v.items() if b}
        else: self.t={} if not v else {ZERO:Q(v)}
    @staticmethod
    def cast(v): return v if isinstance(v,P) else P(v)
    def __add__(self,v):
        if not isinstance(v,(P,int,Q)): return NotImplemented
        v=P.cast(v); d=dict(self.t)
        for a,b in v.t.items(): d[a]=d.get(a,Q(0))+b
        return P(d)
    __radd__=__add__
    def __neg__(self): return P({a:-b for a,b in self.t.items()})
    def __sub__(self,v):
        if not isinstance(v,(P,int,Q)): return NotImplemented
        return self+-P.cast(v)
    def __rsub__(self,v): return P.cast(v)+-self
    def __mul__(self,v):
        if not isinstance(v,(P,int,Q)): return NotImplemented
        v=P.cast(v); d={}
        c.need(len(self.t)*len(v.t)<=1000000,'POLYNOMIAL_PRODUCT_CAP')
        for a,b in self.t.items():
            for q,r in v.t.items():
                key=tuple(x+y for x,y in zip(a,q)); d[key]=d.get(key,Q(0))+b*r
        c.need(len(d)<=50000,'POLYNOMIAL_TERM_CAP'); return P(d)
    __rmul__=__mul__
    def __truediv__(self,v):
        c.need(isinstance(v,(int,Q)) and v!=0,'SCALAR_RATIONAL_DIVISION_ONLY')
        return self*(1/Q(v))
    def __pow__(self,n):
        c.need(isinstance(n,int) and n>=0,'POWER_DOMAIN'); r=P(1)
        for _ in range(n): r=r*self
        return r
    def derivative(self,j):
        d={}
        for a,b in self.t.items():
            if a[j]:
                q=list(a); q[j]-=1; d[tuple(q)]=b*a[j]
        return P(d)
    def iszero(self): return not self.t
    def pack(self): return [{'powers':list(a),'coefficient':str(b)} for a,b in sorted(self.t.items(),reverse=True)]

def variable(j):
    a=[0]*N; a[j]=1; return P({tuple(a):Q(1)})
def initialize():
    global g,H,T,Phi,e,p,f,m,h,mu1,R,mu2,Tp,Hp,u,B0,gp,DERIV
    g,H,T,Phi,e,p,f,m,h=[variable(j) for j in range(N)]
    mu1=-18*h*h; R=-6*h; mu2=-108*h*h
    Tp=m*Phi-4*H*T; Hp=-T*T/3-h*h*e
    u=-2*H*p-T*f/3; B0=12*H*T-4*m*Phi
    gp=-4*H*g+(m-mu1*e+2*T*T)*f+B0*p
    DERIV=(gp,Hp,Tp,T,-2*H*e,u,g,P(0),P(0))
def ds(v): return sum((v.derivative(j)*q for j,q in enumerate(DERIV)),P(0))
def divide(v,divisors):
    """Return exact identity v=sum(q_i*d_i)+remainder, not a sampled test."""
    q=[P(0) for _ in divisors]; rem=P(0); work=P(v); count=0
    while work.t:
        count+=1; c.need(count<100000,'REDUCTION_CAP')
        a=max(work.t); b=work.t[a]; reduced=False
        for j,d in enumerate(divisors):
            da=max(d.t); db=d.t[da]
            if all(x>=y for x,y in zip(a,da)):
                term=P({tuple(x-y for x,y in zip(a,da)):b/db})
                q[j]=q[j]+term; work=work-term*d; reduced=True; break
        if not reduced:
            term=P({a:b}); rem=rem+term; work=work-term
    c.need((v-sum((a*b for a,b in zip(q,divisors)),P(0))-rem).iszero(),'REDUCTION_RECONSTRUCTION')
    return q,rem

class S:
    """Degree-two z-series; each coefficient is an exact polynomial."""
    def __init__(self,v): self.a=tuple(P.cast(x) for x in v)
    @staticmethod
    def cast(v): return v if isinstance(v,S) else S((v,0,0))
    def __add__(self,v):
        v=S.cast(v); return S(tuple(a+b for a,b in zip(self.a,v.a)))
    __radd__=__add__
    def __neg__(self): return S(tuple(-v for v in self.a))
    def __sub__(self,v): return self+-S.cast(v)
    def __rsub__(self,v): return S.cast(v)+-self
    def __mul__(self,v):
        v=S.cast(v); return S(tuple(sum((self.a[j]*v.a[i-j] for j in range(i+1)),P(0)) for i in range(3)))
    __rmul__=__mul__
    def __truediv__(self,v): return S(tuple(x/v for x in self.a))
    def dtime(self): return S(tuple(i*R*x for i,x in enumerate(self.a)))
    def dradial(self): return S(tuple(ds(x) for x in self.a))
    def expzero(self):
        c.need(self.a[0].iszero(),'EXP_ZERO_CONSTANT_ONLY'); return S((1,self.a[1],self.a[2]+self.a[1]*self.a[1]/2))

def original_sources():
    ps=S((0,p,0)); bs=-2*ps; fs=S((0,f,0))
    dp=ps.dtime(); db=bs.dtime(); df=fs.dtime(); up=ps.dradial(); ub=bs.dradial(); gf=fs.dradial()
    em2p=(-2*ps).expzero(); em2b=(-2*bs).expzero()
    trace=(bs+2*ps).dtime().dtime()-h*(bs+2*ps).dtime()+db*db-2*dp*db-2*dp*dp+df*df
    mixed=dp.dradial()-db*(H+up)+df*(T+gf)/3
    kg=-e*em2p*(fs.dtime().dtime()+(3*h+2*dp+db)*df)
    kg=kg+em2b*(Tp+gf.dradial()+(4*H+4*up-ub)*(T+gf))-m*(Phi+fs)
    radial=em2b*(6*(H+up)*(H+up)-(T+gf)*(T+gf)/2)-6+m*(Phi+fs)*(Phi+fs)/2
    radial=radial-e*em2p*(6*h*h+3*(ps.dtime().dtime()+3*h*dp)+3*dp*dp+df*df/2)
    return {'T':trace,'M':mixed,'K':kg,'R':radial}

def compatibility(q):
    # Divide qM by r2 only after its explicit common R factor has been
    # independently extracted; no division by a symbolic scalar gradient.
    c2=-Q(3,13)*(6*p*p+f*f)
    Sp=H*c2-p*u-f*g/6
    Sc=12*H*Sp-(12*H*H-T*T)*c2+q['R']
    Sg=T*ds(c2)+2*m*Phi*c2-6*T*Sp-q['K']
    Dn=2*T*T-3*(mu2+4*h*h)*e
    return ds(Sc)+4*H*Sc-T*Sg-Dn*Sp,{'c2':c2,'Sp2':Sp,'Sc2':Sc,'Sg2':Sg,'constraint_coefficient_n2':Dn}

def qualify():
    bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
    first=T*g-Tp*f+(2*T*T-3*(mu1+4*h*h)*e)*p
    c.need(ds(bg).iszero(),'BACKGROUND_CONSTRAINT_PRESERVATION')
    c.need((ds(first)+4*H*first).iszero(),'FIRST_ORDER_CONSTRAINT_PRESERVATION')
    rows=original_sources()
    expected={'T':R*R*(6*p*p+f*f),'M':R*(2*p*u+f*g/3),
              'K':(4*m-6*mu1*e)*p*f+6*u*g-8*m*Phi*p*p,
              'R':6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2-e*(12*h*h*p*p+18*h*h*f*f)}
    lower_order={}
    for key,row in rows.items():
        zero=bg if key=='R' else P(0); linear=-first if key=='R' else P(0)
        c.need((row.a[0]-zero).iszero(),'DIRECT_ORDER_ZERO:'+key)
        c.need((row.a[1]-linear).iszero(),'DIRECT_ORDER_ONE:'+key)
        c.need((row.a[2]-expected[key]).iszero(),'DIRECT_QUADRATIC_MATCH:'+key)
        lower_order[key]={'z0':row.a[0].pack(),'z1':row.a[1].pack(),'z2_direct':row.a[2].pack(),'z2_reduced':expected[key].pack()}
    # Leading monomials are g*T and H² in declared lex order; they are coprime.
    # Thus these two generators form a Groebner basis (product criterion).
    lead1=max(first.t); lead0=max(bg.t)
    c.need(all(min(a,b)==0 for a,b in zip(lead1,lead0)),'COPRIME_LEADING_MONOMIALS')
    residual,sources=compatibility(expected); multipliers,remainder=divide(residual,[first,bg])
    c.need((2*R*(2*R-h)*sources['c2']+expected['T']).iszero(),'Q2_TRACE_SOURCE_DIVISOR')
    c.need((2*R*(sources['Sp2']-H*sources['c2'])+expected['M']).iszero(),'Q2_MIXED_SOURCE_DIVISOR')
    c.need(remainder.iszero(),'EXACT_Q4_COMPATIBILITY_REMAINDER')
    # Deliberate altered formulas must disagree with independently extracted S6.
    mutations={'KG_pf_sign':('K',expected['K']-2*(4*m-6*mu1*e)*p*f),
               'mixed_factor_half':('M',expected['M']/2),
               'omitted_scalar_time_stress':('R',expected['R']+18*h*h*e*f*f)}
    mutation_records={}
    for label,(key,mutated) in mutations.items():
        diff=rows[key].a[2]-mutated; c.need(not diff.iszero(),'MUTATION_UNDETECTED:'+label)
        mutation_records[label]={'detected':True,'direct_S6_difference':diff.pack()}
    # Exact local transport identity; integrate this total derivative between
    # endpoints to obtain the pulled/Eulerian distance-coefficient equality.
    # Use p as a nonconstant profile and X=Phi as a manufactured smooth map.
    X=Phi; b1=-2*p
    transport=X*ds(b1)+ds(X)*b1
    c.need((transport-ds(X*b1)).iszero(),'CHART_DISTANCE_PRODUCT_RULE')
    c.need((ds(p*p)-2*p*u).iszero(),'DERIVATIVE_ENGINE_CONTROL')
    c.need(((H+T)*(H-T)-(H*H-T*T)).iszero(),'POLYNOMIAL_RING_CONTROL')
    return {'variables':list(NAMES),'ordering':'lexicographic in listed order','direct_S6_coefficients':lower_order,
            'background_constraint':bg.pack(),'first_order_constraint':first.pack(),
            'constraint_preservation_exact':True,'Q4_raw_residual':residual.pack(),
            'Q4_generator_order':['first_order_constraint','background_constraint'],
            'Q4_multipliers':[v.pack() for v in multipliers],'Q4_remainder':remainder.pack(),
            'Q4_sources':{k:v.pack() for k,v in sources.items()},'mutations':mutation_records,
            'chart_transport_total_derivative':transport.pack(),'chart_distance_identity':'X*b1_prime+X_prime*b1=(X*b1)_prime',
            'no_division_by_T':True}

def authenticate():
    c.need(sys.platform=='linux','LINUX_ONLY'); gate=c.read(ROOT/'ADMISSION.json'); c.need(gate.get('admitted') is True,'ADMISSION')
    for rel,d in gate['sources'].items(): c.need(c.sha(ROOT/rel)==d,'SOURCE_HASH:'+rel)
    for rel in ('../SECOND_ORDER_MECHANISM_SCOPE.md','../SECOND_ORDER_BULK_SCRATCH.md'):
        c.need(rel in gate['sources'],'MISSING_DERIVATION_BINDING:'+rel)
    rt=c.read(ROOT/'RUNTIME_BINDINGS.json')
    c.need(str(Path(sys.executable).resolve())==rt['executable_realpath'],'RUNTIME_PATH')
    c.need(platform.python_version()==rt['python_version'],'RUNTIME_VERSION')
    for path,d in rt['files'].items(): c.need(c.sha(path)==d,'RUNTIME_HASH:'+path)
    c.need(all(os.environ.get(k)=='1' for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS')),'THREAD_ENV')

def main():
    c.need(not any((ROOT/n).exists() for n in ('STARTED.json','RESULT.json','FAILURE.json')),'NO_RESTART'); begun=time.monotonic()
    try:
        signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('SOURCE_QUALIFICATION_CAP_900_SECONDS'))); signal.alarm(900)
        authenticate(); c.put('STARTED.json',{'utc':c.now(),'pid':os.getpid(),'admission_sha256':c.sha(ROOT/'ADMISSION.json')})
        initialize(); identities=qualify(); c.put('IDENTITIES.json',identities)
        c.put('RESULT.json',{'classification':'EULERIAN_QUADRATIC_BULK_SOURCES_QUALIFIED','identity_record':'IDENTITIES.json',
               'identity_sha256':c.sha(ROOT/'IDENTITIES.json'),'seconds':time.monotonic()-begun,'utc':c.now(),
               'scope':'Exact bulk source and compatibility identities under declared background/first-order constraints. Eulerian chart, with separate transport identity only. No full pulled-source qualification, wall sources, n2 solution, amplitude or distance coefficient.'})
    except BaseException as e:
        c.put('FAILURE.json',{'classification':'TECHNICAL_INCOMPLETE','utc':c.now(),'error':repr(e),'traceback':traceback.format_exc()}); raise
    finally: signal.alarm(0)

if __name__=='__main__': main()
