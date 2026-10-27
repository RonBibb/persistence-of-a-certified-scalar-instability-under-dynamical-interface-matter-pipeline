"""One bounded cubic graph diagnostic. No radial integration or tail claim."""
import sys
sys.dont_write_bytecode=True
import importlib.util,json
from pathlib import Path
from fractions import Fraction
from flint import arb,fmpq
import series,closed
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
T15=ROOT.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py'
spec=importlib.util.spec_from_file_location('cubic_polynomial',T15)
poly=importlib.util.module_from_spec(spec);sys.modules[spec.name]=poly;spec.loader.exec_module(poly)
def need(v,label):
    if not v:raise AssertionError(label)
def qualify():
    names=('E','h','xi1','xi2','p1','p2','H','Hp','u','c2','T','Tp','f1','f2','g1','chi1','chi2','n','L3','b3','xi3','fixed3','phi3','chi3')
    poly.NAMES=names;poly.N=len(names);poly.ZERO=(0,)*len(names)
    w={k:poly.variable(i) for i,k in enumerate(names)}
    E,h,x,y,p,H,n,chi=[w[k] for k in ('E','h','xi1','xi2','p1','H','n','chi1')]
    records={};checks=[]
    def eq(a,b,label):need((a-b).iszero(),label);checks.append(label)
    for sigma in (1,-1):
        direct=series.extract(w,sigma);source=closed.extract(w,sigma)
        divisor=342*sigma*h*h*E*E
        for key in ('geometric','current','oscillator','total'):
            eq(direct[key].a[3],source[key]+(divisor*w['xi3'] if key in ('geometric','total') else 0),'CUBIC:'+str(sigma)+':'+key)
        eq(direct['total'].a[1],42*sigma*h*h*E*E*x-n,'ORDER1:'+str(sigma))
        q2=-sigma*h*h*E*E*x*(384*p+120*H*x)+n*((w['T']*x+w['f1'])/1000+6*(H*x+p))-18*h*h*E*E*chi*chi
        eq(direct['total'].a[2],156*sigma*h*h*E*E*y+q2,'ORDER2:'+str(sigma))
        eq(direct['total'].a[3].derivative(names.index('xi3')),divisor,'DIVISOR:'+str(sigma))
        for key in ('L3','b3','fixed3','phi3','chi3'):
            eq(direct['total'].a[3].derivative(names.index(key)),poly.P(0),'NEW_UNKNOWN_INDEPENDENCE:'+str(sigma)+':'+key)
        remote=dict(w,xi1=poly.P(0),n=poly.P(0),xi3=poly.P(0))
        rd=series.extract(remote,sigma)['total'].a[3]
        expected=-1056*sigma*h*h*E*E*y*p-72*h*h*E*E*chi*w['chi2']+36*h*h*E*E*p*chi*chi
        eq(rd,expected,'REMOTE_NONZERO_XI2:'+str(sigma))
        for label,kwargs in (('NO_CUBIC_BOOST',{'boost':False}),('WRONG_EXPONENTIAL_COUPLING',{'affine':False})):
            delta=direct['total'].a[3]-series.extract(w,sigma,**kwargs)['total'].a[3]
            need(not delta.iszero(),label);checks.append('MUTATION_DETECTED:'+str(sigma)+':'+label)
        records[str(sigma)]={k:v.pack() for k,v in source.items()}
    return {'pass':True,'checks':checks,'variables':names,'sources':records,'arithmetic':'Exact sparse rational polynomial identities, not sampling'}
def iv(record):
    a,b=map(fmpq,record['exact_bounds']);return arb((a+b)/2,(b-a)/2)
def pack(x):
    need(x.is_finite(),'FINITE');return {'exact_bounds':[str(x.lower().fmpq()),str(x.upper().fmpq())]}
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def zero(x):return x.lower()<=0<=x.upper()
def hull(a,b):
    lo=min(a.lower().fmpq(),b.lower().fmpq());hi=max(a.upper().fmpq(),b.upper().fmpq());return arb((lo+hi)/2,(hi-lo)/2)
def run():
    need(sys.platform=='linux','LINUX_ONLY');qualification=qualify();engines={};graphs=[]
    for engine in ('primary','independent'):
        raw=json.loads((PARENT/('PRODUCTION_'+engine+'.json')).read_text())
        k=iv(raw['parameters']['k']);m2=iv(raw['parameters']['m2']);need(k.lower()>0,'K_POSITIVE');h=k.sqrt()
        walls={};xis={}
        for side,sigma in (('lower',1),('upper',-1)):
            wall=raw['walls'][side];z=list(map(iv,wall['state']));fresh={a:iv(b) for a,b in wall['fresh'].items()}
            W,H,Phi,T,E,p,f,g,p2,f2,g2,ph,fh,gh=z
            w=dict(E=E,h=h,xi1=fresh['xi'],xi2=fresh['xi2'],p1=p,p2=p2,H=H,Hp=-T*T/3-k*E*E,u=-2*H*p-T*f/3,c2=fresh['c2'],T=T,Tp=m2*Phi-4*H*T,f1=f,f2=f2,g1=g,chi1=fresh['chi'],chi2=iv(wall['chi2']),n=fresh['n'])
            direct=series.extract(w,sigma);src=closed.extract(w,sigma)
            need(zero(direct['total'].a[1]) and zero(direct['total'].a[2]),'LOWER_ORDER_REPLAY:'+engine+side)
            for key in src:need(overlap(src[key],direct[key].a[3]),'DIRECT_CLOSED:'+engine+side+key)
            divisor=342*sigma*k*E*E;need(not zero(divisor),'CUBIC_DIVISOR')
            xi=-src['total']/divisor;xis[side]=xi
            full=series.extract(dict(w,xi3=xi),sigma)['total'].a[3];need(zero(full),'SOLVED_CUBIC_ROW')
            walls[side]={'inputs':{a:pack(b) for a,b in w.items()},'sources_closed':{a:pack(b) for a,b in src.items()},'sources_direct':{a:pack(b.a[3]) for a,b in direct.items()},'divisor':pack(divisor),'xi3':pack(xi),'solved_row':pack(full),'first_row':pack(direct['total'].a[1]),'second_row':pack(direct['total'].a[2])}
        graph=xis['upper']-xis['lower'];graphs.append(graph);g2=iv(raw['graph']);need(not zero(g2),'GRAPH2_RATIO_DIVISOR')
        engines[engine]={'walls':walls,'graph3':pack(graph),'graph2_parent':pack(g2),'graph3_over_graph2':pack(graph/g2)}
    need(overlap(*graphs),'ENGINE_GRAPH_OVERLAP')
    for side in ('lower','upper'):need(overlap(iv(engines['primary']['walls'][side]['xi3']),iv(engines['independent']['walls'][side]['xi3'])),'ENGINE_WALL_OVERLAP:'+side)
    graph=hull(*graphs);sign=1 if graph.lower()>0 else -1 if graph.upper()<0 else 0
    return {'classification':'CUBIC_GRAPH_NEGATIVE' if sign<0 else 'CUBIC_GRAPH_POSITIVE' if sign>0 else 'CUBIC_GRAPH_SIGN_UNRESOLVED','all_gates':True,'qualification':qualification,'per_engine':engines,'graph3':pack(graph),'scope':'Eulerian moving-boundary contribution only, not full third-order proper separation or convergence radius. Coefficient ratio is not a tail bound.','terminal_review_pending':True}
