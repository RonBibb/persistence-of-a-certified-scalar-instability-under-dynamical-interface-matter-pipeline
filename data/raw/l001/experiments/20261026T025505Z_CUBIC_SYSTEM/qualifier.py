"""Exact cubic system source qualification and two-engine endpoint loads."""
import sys,json
from pathlib import Path
from fractions import Fraction as Q
from flint import arb,fmpq
import bulk,wall,wall_closed
ROOT=Path(__file__).resolve().parent
GRAPH=ROOT.parent/'20261026T023331Z_CUBIC_GRAPH'
PARENT=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
ring=bulk.load('cubic_wall_ring',bulk.BASE/'T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py')
S=bulk.S
def need(v,label):
    if not v:raise AssertionError(label)
def qualify_wall():
    names=('E','h','H','Hp','Hpp','T','Tp','Tpp','Tppp','p1','u1','u1p','f1','g1','g1p','g1pp','p2','u2','f2','g2','g2p','c2','c2p','xi1','xi2','chi1','chi2','n')+wall.NEW
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*ring.N
    w={k:ring.variable(j) for j,k in enumerate(names)};checks=[];record={}
    def eq(a,b,label):need((a-b).iszero(),label);checks.append(label)
    E,h,H,T,Tp,Tpp,p,u,f,g,gp,x,y,chi,chi2,n,p2,f2,g2,c2=[w[k] for k in ('E','h','H','T','Tp','Tpp','p1','u1','f1','g1','g1p','xi1','xi2','chi1','chi2','n','p2','f2','g2','c2')]
    A=H*x+p;d1=2+18*h*h*E*E;d2=2+108*h*h*E*E
    o2=36*h*h*E*E*A*chi-x*g-x*x*Tp/2
    for sigma in (1,-1):
        r=wall.extract(w,sigma,S);direct=r['direct']
        closed=wall_closed.extract(w,sigma)
        for key in ('o3','j3'):eq(r[key],closed[key],'CUBIC_Q5_DIRECT_CLOSED:'+str(sigma)+':'+key)
        for key in ('normal_tilt','normal_boost','displacement','current_force'):
            need(not (r['j3']-(closed['j3']-closed[key])).iszero(),'WALL_MUTATION:'+key);checks.append('WALL_MUTATION:'+str(sigma)+':'+key)
        for key in ('oscillator_identity','scalar_identity','Q6_identity'):eq(r[key],ring.P(0),key+':'+str(sigma))
        eq(direct['O'].a[0],ring.P(0),'O0:'+str(sigma));eq(direct['J'].a[0],ring.P(0),'J0:'+str(sigma))
        eq(direct['O'].a[1],d1*chi-f-T*x,'O1:'+str(sigma))
        eq(direct['O'].a[2],d2*chi2-f2-T*y+o2,'O2:'+str(sigma))
        first=g+Tp*x+2*T*p-sigma*(21*(T*x+f)-chi-n/1000)/2
        eq(direct['J'].a[1],first,'J1:'+str(sigma))
        j2=x*x*Tpp/2+x*gp+2*p*(x*Tp+g)+(2*p*p+2*x*u)*T+36*h*h*E*E*x*f+18*h*h*E*E*x*x*T-sigma*(21*(x*x*Tp/2+x*g)+6*n*A/1000)/2
        new2=g2+Tp*y-T*c2+2*T*p2-sigma*(21*(f2+T*y)-chi2)/2
        eq(direct['J'].a[2],new2+j2,'J2:'+str(sigma))
        for key in wall.NEW:
            eq(r['o3'].derivative(names.index(key)),ring.P(0),'O_SOURCE_INDEPENDENCE:'+str(sigma)+':'+key)
            eq(r['j3'].derivative(names.index(key)),ring.P(0),'J_SOURCE_INDEPENDENCE:'+str(sigma)+':'+key)
        # These terms must remain visible to the exact coefficient checker.
        need(not r['j3'].derivative(names.index('Tppp')).iszero(),'CUBIC_BACKGROUND_NORMAL_JET')
        need(not r['o3'].derivative(names.index('g2')).iszero(),'CUBIC_SECOND_FIELD_TRANSPORT')
        checks.extend(['CUBIC_BACKGROUND_NORMAL_JET:'+str(sigma),'CUBIC_SECOND_FIELD_TRANSPORT:'+str(sigma)])
        record[str(sigma)]={k:r[k].pack() for k in ('o3','j3','d3','Q6_load_times_d3','Q6_identity')}
    # Independent polynomial antiderivative test for moving integration limits:
    # integrand 1 + z*s^2 + z^2*s^3 + z^3*s^4 at s(z)=H+z*x+z²*y+z³*p3.
    z=S([0,1]);s=S([H,x,y,w['p3']])
    primitive=s+z*s*s*s/3+z*z*s*s*s*s/4+z*z*z*s*s*s*s*s/5
    expected=w['p3']+H*H*y+H*x*x+H*H*H*x+H*H*H*H*H/5
    eq(primitive.a[3],expected,'MOVING_ENDPOINT_ANTIDERIVATIVE')
    return {'pass':True,'variables':names,'checks':checks,'orientations':record}
def iv(r):
    lo,hi=map(fmpq,r['exact_bounds']);return arb((lo+hi)/2,(hi-lo)/2)
def pack(v):
    need(v.is_finite(),'FINITE');return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def zero(v):return v.lower()<=0<=v.upper()
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def evaluate_polynomial(p,values):
    total=arb(0)
    for powers,coefficient in p.t.items():
        term=arb(fmpq(coefficient.numerator,coefficient.denominator))
        for key,power in zip(bulk.ring.NAMES,powers):
            for _ in range(power):term*=values[key]
        total+=term
    return total
def endpoints():
    b=bulk;b.setup();q=b.closed();c3=-Q(8,19)*(6*b.p*b.P+b.f*b.F-3*b.p*b.c2)
    Sp3=b.H*c3-(2*b.p*b.U+(4*b.P-2*b.c2)*b.u+(b.f*b.G+2*b.F*b.g)/3)/3
    Sc3=12*b.H*Sp3-(12*b.H*b.H-b.T*b.T)*c3+q['R']
    Sg3=b.T*b.ds(c3)+2*b.m*b.Phi*c3-6*b.T*Sp3-q['K']
    jets=dict(H=b.H,Hp=b.Hp,Hpp=b.ds(b.Hp),T=b.T,Tp=b.Tp,Tpp=b.ds(b.Tp),Tppp=b.ds(b.ds(b.Tp)),p1=b.p,u1=b.u,u1p=b.ds(b.u),f1=b.f,g1=b.g,g1p=b.gp,g1pp=b.ds(b.gp),p2=b.P,u2=b.U,f2=b.F,g2=b.G,g2p=b.Gp,c2=b.c2,c2p=b.ds(b.c2))
    accepted=json.loads((GRAPH/'RESULT.json').read_text());output={}
    for engine in ('primary','independent'):
        raw=json.loads((PARENT/('PRODUCTION_'+engine+'.json')).read_text());k=iv(raw['parameters']['k']);h=k.sqrt();m=iv(raw['parameters']['m2']);walls={}
        for side,sigma in (('lower',1),('upper',-1)):
            record=raw['walls'][side];state=list(map(iv,record['state']));_,H,Phi,T,E,p,f,g,P,F,G,*_=state
            values=dict(H=H,Phi=Phi,T=T,e=E*E,p=p,f=f,g=g,P=P,F=F,G=G,m=m,h=h)
            w={a:evaluate_polynomial(v,values) for a,v in jets.items()}
            fresh={a:iv(v) for a,v in record['fresh'].items()}
            w.update(E=E,h=h,xi1=fresh['xi'],xi2=fresh['xi2'],chi1=fresh['chi'],chi2=iv(record['chi2']),n=fresh['n'],xi3=iv(accepted['per_engine'][engine]['walls'][side]['xi3']),c3=evaluate_polynomial(c3,values))
            r=wall.extract(w,sigma,S)
            closed=wall_closed.extract(w,sigma)
            for key in ('o3','j3'):need(overlap(r[key],closed[key]),'NUMERIC_Q5_DIRECT_CLOSED:'+engine+side+key)
            for key in ('oscillator_identity','scalar_identity','Q6_identity'):need(zero(r[key]),'NUMERIC_'+key+engine+side)
            for key in ('O','J'):
                for n in (1,2):need(zero(r['direct'][key].a[n]),'WALL_PARENT_REPLAY:'+engine+side+key+str(n))
            need(r['d3'].lower()>0,'D3_POSITIVE')
            load=r['Q6_load_times_d3']/r['d3']
            walls[side]={'inputs':{a:pack(v) for a,v in w.items()},'o3':pack(r['o3']),'j3':pack(r['j3']),'d3':pack(r['d3']),'R3':pack(load),'Sc3':pack(evaluate_polynomial(Sc3,values)),'Sp3':pack(evaluate_polynomial(Sp3,values)),'Sg3':pack(evaluate_polynomial(Sg3,values)),'identities':{a:pack(r[a]) for a in ('oscillator_identity','scalar_identity','Q6_identity')}}
        output[engine]=walls
    for side in ('lower','upper'):
        for key in ('o3','j3','d3','R3','Sc3','Sp3','Sg3'):need(overlap(iv(output['primary'][side][key]),iv(output['independent'][side][key])),'ENGINE_LOAD_OVERLAP:'+side+key)
    return output
def run():
    need(sys.platform=='linux','LINUX_ONLY')
    qb=bulk.qualify();qw=qualify_wall();en=endpoints()
    return {'pass':True,'classification':'CUBIC_SYSTEM_SOURCES_QUALIFIED','bulk':qb,'wall':qw,'per_engine':en,'scope':'Exact Eulerian cubic bulk/wall qualification and endpoint forcing, not a cubic field solution or complete proper-separation coefficient.'}
