"""Neutral growing cubic wall source and exact polynomial qualification.

Ordinary powers eta=epsilon*exp(r*t), no factorials. Both currents vanish;
xi1=0, b1=-2p1, b2=c2-2p2. chi coefficients are intrinsic wall fields,
not radially shifted. p/f coefficients supplied here are Eulerian.
No execution, imports of numerical libraries, or writes at module import.
"""
from fractions import Fraction as Q

def div(x,n): return Q(x,n) if isinstance(x,int) else x/n

class S:
    """Degree-three ordinary series, with arbitrary exact coefficient ring."""
    def __init__(self,values): self.a=tuple((list(values)+[0]*4)[:4])
    @staticmethod
    def cast(x): return x if isinstance(x,S) else S([x])
    def __add__(self,x):return S([a+b for a,b in zip(self.a,self.cast(x).a)])
    __radd__=__add__
    def __neg__(self):return S([-a for a in self.a])
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        b=self.cast(x).a
        return S([sum((self.a[i]*b[n-i] for i in range(n+1)),0) for n in range(4)])
    __rmul__=__mul__
    def __truediv__(self,n):return S([div(a,n) for a in self.a])
    def dt(self,r):return S([i*r*a for i,a in enumerate(self.a)])
    def expzero(self):
        a,b,c=self.a[1:]
        return S([1,a,b+div(a*a,2),c+a*b+div(a*a*a,6)])

NEW=('p3','f3','g3','chi3','xi3','c3')

def direct(w,sigma):
    E,h,r,H,T,Tp,p,u,f,g,gp,P,F,G,c,x,chi,chi2=[w[k] for k in
        ('E','h','rate','H','T','Tp','p1','u1','f1','g1','g1prime','p2','f2','g2','c2','xi2','chi1','chi2')]
    p3,f3,g3,chi3,x3,c3=[w.get(k,0) for k in NEW]
    shift=S([0,0,x,x3]);St=shift.dt(r)
    loga=S([0,0,H*x,H*x3])
    pwall=S([0,p,P,p3+x*u])
    bwall=S([0,-2*p,c-2*P,c3-2*p3-2*x*u])
    invN=(-loga-pwall).expzero()*E
    velocity=bwall.expzero()*invN*St
    # Velocity starts at eta². Every boost correction starts at eta^4,
    # and velocity*velocity_t starts at eta^4: none contributes below eta^4.
    Hwall=S([H,0,w.get('Hp',0)*x])
    Twall=S([T,0,Tp*x,Tp*x3])
    deltaPhi=S([0,f,F+T*x,f3+T*x3+x*g])
    radial=S([0,g,G,g3+x*gp])
    fixed_time_scalar=S([0,r*f,2*r*F,3*r*f3+r*x*g])
    oscillator=S([0,chi,chi2,chi3]);chid=oscillator.dt(r)
    friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)
    O=invN*invN*(chid.dt(r)+friction*chid)+2*oscillator-deltaPhi
    normal=(-bwall).expzero()*(Twall+radial)+velocity*invN*fixed_time_scalar
    J=normal-(S([2*sigma*T])+21*deltaPhi-oscillator)*sigma/2
    # Only the first order fixed-position time derivatives can multiply v
    # through cubic order; using their longer Eulerian series is harmless.
    fixed_p=S([0,p,P,p3]).dt(r)
    fixed_b=S([0,-2*p,c-2*P,c3-2*p3]).dt(r)
    geometric=sigma*invN*(velocity.dt(r)+velocity*(fixed_b-h-fixed_p))
    kinetic=-(invN*invN*chid*chid)/2
    return dict(O=O,J=J,graph=geometric+kinetic,geometric=geometric,kinetic=kinetic,
                pwall=pwall,bwall=bwall,deltaPhi=deltaPhi,normal=normal)

def closed(w,sigma):
    E,h,r,H,T,Tp,p,u,f,g,gp,P,F,G,c,x,chi,chi2=[w[k] for k in
        ('E','h','rate','H','T','Tp','p1','u1','f1','g1','g1prime','p2','f2','g2','c2','xi2','chi1','chi2')]
    qgeom=4*sigma*E*E*r*(2*h-7*r)*x*p
    qkin=-2*r*r*E*E*chi*chi2+r*r*E*E*p*chi*chi
    tilt=2*r*r*E*E*x*f
    displacement=-div(21*sigma*x*g,2)
    j=x*gp+2*p*(G+Tp*x)+(2*P-c+2*p*p)*g
    j=j+T*(2*x*u+4*p*P-2*p*c+div(4*p*p*p,3))+tilt+displacement
    o=E*E*(-4*r*(r+3*h)*p*chi2+2*r*(r-3*h)*(P+H*x-p*p)*chi)-x*g
    return dict(qI3=qgeom+qkin,qI3_geometric=qgeom,qI3_oscillator=qkin,
                graph_divisor=3*sigma*E*E*r*(3*r-h),o3=o,j3=j,
                normal_tilt=tilt,normal_displacement=displacement,
                d3=2+3*r*(3*r+3*h)*E*E,
                c3_numerator=-4*r*(6*p*P+f*F-3*p*c),c3_denominator=3*(3*r-h))

def extract(w,sigma):
    """Return load polynomials and exact new-row/elimination witnesses."""
    full=direct(w,sigma);trunc=direct(dict(w,**{k:0 for k in NEW}),sigma)
    src=closed(w,sigma)
    E,h,r,T,Tp=[w[k] for k in ('E','h','rate','T','Tp')]
    p3,f3,g3,chi3,x3,c3=[w.get(k,0) for k in NEW]
    d=src['d3'];o=trunc['O'].a[3];j=trunc['J'].a[3]
    newO=d*chi3-f3-T*x3
    newJ=g3+Tp*x3-T*c3+2*T*p3-div(sigma*(21*(f3+T*x3)-chi3),2)
    load_d=2*sigma*d*(T*c3-Tp*x3-j)+(21*d-1)*T*x3+o
    robin_d=2*sigma*d*(g3+2*T*p3)-(21*d-1)*f3-load_d
    return dict(src,full=full,o3_direct=o,j3_direct=j,Q6_load_times_d3=load_d,
                oscillator_identity=full['O'].a[3]-newO-o,
                scalar_identity=full['J'].a[3]-newJ-j,
                graph_identity=full['graph'].a[3]-src['graph_divisor']*x3-src['qI3'],
                Q6_identity=2*sigma*d*full['J'].a[3]-full['O'].a[3]-robin_d)

def qualify():
    """Linux-only exact all-variable identity test; no physical integration."""
    import sys,hashlib,importlib.util,json
    from pathlib import Path
    assert sys.platform=='linux','LINUX_ONLY'
    sys.dont_write_bytecode=True
    base=Path(__file__).resolve().parent.parent
    old=base/'20261026T015206Z_FORCED_SECOND_ORDER_R1/FROZEN.json'
    flow=base/'20261026T033400Z_CUBIC_FULL_FLOW/FROZEN.json'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest(flow)=='625aeaa83acf8be12d628c26bdcc5265c91780431be3c0c7ab46fdc3c343326e'
    assert json.loads(flow.read_text())['files'][str(old)]==digest(old)
    td=base/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION'
    files=json.loads(old.read_text())['files']
    for path in (td/'producer.py',td/'common.py'):assert files[str(path)]==digest(path)
    spec=importlib.util.spec_from_file_location('neutral_cubic_wall_ring',td/'producer.py')
    ring=importlib.util.module_from_spec(spec);spec.loader.exec_module(ring)
    names=('E','h','rate','H','Hp','T','Tp','p1','u1','f1','g1','g1prime','p2','f2','g2','c2','xi2','chi1','chi2')+NEW
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    w={key:ring.variable(i) for i,key in enumerate(names)};checks=[];records={}
    def eq(a,b,label):
        assert (ring.P.cast(a)-b).iszero(),label;checks.append(label)
    E,h,r,T,Tp,p,u,f,g,P,F,G,c,x,chi,chi2=[w[k] for k in
        ('E','h','rate','T','Tp','p1','u1','f1','g1','p2','f2','g2','c2','xi2','chi1','chi2')]
    for sigma in (1,-1):
        result=extract(w,sigma);full=result['full'];d1=2+r*(r+3*h)*E*E;d2=2+2*r*(2*r+3*h)*E*E
        eq(result['o3_direct'],result['o3'],f'O3_DIRECT_CLOSED_{sigma}')
        eq(result['j3_direct'],result['j3'],f'J3_DIRECT_CLOSED_{sigma}')
        for key in ('oscillator_identity','scalar_identity','graph_identity','Q6_identity'):
            eq(result[key],0,key+str(sigma))
        eq(full['O'].a[0],0,f'O0_{sigma}');eq(full['J'].a[0],0,f'J0_{sigma}')
        eq(full['O'].a[1],d1*chi-f,f'O1_{sigma}')
        eq(full['J'].a[1],g+2*T*p-div(sigma*(21*f-chi),2),f'J1_{sigma}')
        eq(full['O'].a[2],d2*chi2-F-T*x-6*h*r*E*E*p*chi,f'O2_{sigma}')
        eq(full['J'].a[2],G+Tp*x-T*c+2*T*P-div(sigma*(21*(F+T*x)-chi2),2)+2*p*g+2*T*p*p,f'J2_{sigma}')
        eq(full['graph'].a[1],0,f'GRAPH1_{sigma}')
        eq(full['graph'].a[2],2*sigma*E*E*r*(2*r-h)*x-r*r*E*E*chi*chi/2,f'GRAPH2_{sigma}')
        for key in NEW:
            for source in ('o3','j3','qI3'):
                eq(result[source].derivative(names.index(key)),0,f'SOURCE_INDEPENDENCE_{sigma}_{source}_{key}')
        for key in ('normal_tilt','normal_displacement','qI3_geometric','qI3_oscillator'):
            assert not result[key].iszero(),f'MUTATION_NOT_DETECTED_{key}';checks.append(f'OMISSION_DETECTED_{sigma}_{key}')
        # Distinct polynomial forced-rate reduction, xi1=0, no current.
        reduced=closed(dict(w,rate=-6*h),sigma)
        eq(reduced['qI3'],-1056*sigma*h*h*E*E*x*p-72*h*h*E*E*chi*chi2+36*h*h*E*E*p*chi*chi,f'FORCED_GRAPH_REDUCTION_{sigma}')
        eq(reduced['o3'],E*E*(-72*h*h*p*chi2+108*h*h*(P+w['H']*x-p*p)*chi)-x*g,f'FORCED_OSCILLATOR_REDUCTION_{sigma}')
        records[str(sigma)]={key:result[key].pack() for key in ('qI3','graph_divisor','o3','j3','d3','Q6_load_times_d3')}
    # Independent Eulerian tracefree bulk extraction: no graph transport is
    # present in these Eulerian fields, and c1=0.
    ps=S([0,p,P,0]);bs=S([0,-2*p,c-2*P,0]);fs=S([0,f,F,0])
    dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r)
    raw=(bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df
    qT3=4*r*r*(6*p*P+f*F-3*p*c)
    eq(raw.a[3],qT3,'BULK_CUBIC_TRACE_DIRECT')
    src=closed(w,1)
    eq(r*src['c3_numerator']+qT3,0,'C3_DIVISOR_CLEARED')
    return {'pass':True,'classification':'NEUTRAL_GENERAL_RATE_CUBIC_WALL_IDENTITIES_QUALIFIED',
            'checks':checks,'variables':names,'orientations':records,'trace_source':qT3.pack(),
            'new_physical_integrations':0,
            'scope':'Exact polynomial source/new-row identities through cubic order, zero currents and xi1=0. No cubic field solution, distance coefficient, convergence or nonlinear endpoint.'}

if __name__=='__main__':
    import json
    print(json.dumps(qualify(),indent=2))
