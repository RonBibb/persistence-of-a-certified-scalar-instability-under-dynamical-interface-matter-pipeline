"""Stream accepted cubic boxes into signed distance budgets; no ODE."""
import importlib.util,sys,time,resource
from fractions import Fraction as Q
from flint import arb,fmpq
import math_core as core
from storage import ROOT,read,put,sha
FLOW=ROOT.parent/'20261026T033400Z_CUBIC_FULL_FLOW'
SECOND=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
GRAPH=ROOT.parent/'20261026T023331Z_CUBIC_GRAPH'
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
ring=load('distance_polynomial',ROOT.parent/'20261025T225750Z_AB_MECHANISM_ALLOCATION/T15_AB_QUADRATIC_BULK_SOURCE_QUALIFICATION/producer.py')
S=load('distance_series',GRAPH/'series.py').S
lower=load('distance_lower_rhs',SECOND/'primary.py')
def need(v,label):
    if not v:raise AssertionError(label)
def iv(v):
    a,b=map(fmpq,v['exact_bounds']);need(a<=b,'INTERVAL_ORDER');return arb((a+b)/2,(b-a)/2)
def exact(v):
    need(v.is_finite(),'FINITE_EXPORT');return {'exact_bounds':[str(v.lower().fmpq()),str(v.upper().fmpq())]}
def out(v):
    need(v.is_finite(),'FINITE_EXPORT');lo,hi=v.lower().fmpq(),v.upper().fmpq();scale=fmpq(2**80)
    a=fmpq(Q(str(lo*scale)).__floor__())/scale;b=fmpq(Q(str(hi*scale)).__ceil__())/scale
    need(a<=lo<=hi<=b,'OUTWARD_EXPORT');return {'exact_bounds':[str(a),str(b)]}
def overlap(a,b):return a.lower()<=b.upper() and b.lower()<=a.upper()
def hull(a,b):
    lo=min(a.lower().fmpq(),b.lower().fmpq());hi=max(a.upper().fmpq(),b.upper().fmpq());return arb((lo+hi)/2,(hi-lo)/2)
def controls():
    names=('W','H','Phi','T','E','a','f','g','ap','fp','gp','ah','fh','gh','cp','cf','cg','ch','fh3','gh3','m2','k','mu1','mu2','A2','A3','X1','X2','xp','yp')
    ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
    v=[ring.variable(i) for i in range(len(names))];z=v[:20];p={k:v[names.index(k)] for k in ('m2','k','mu1','mu2','A2','A3')}
    X,Y,xp,yp=v[-4:];f=core.fields(z,p);B=core.endpoint(z,p,X,Y)
    deriv=lower.rhs(z[:14],p)+[ring.P(0)]*12+[xp,yp,ring.P(0),ring.P(0)]
    need(len(deriv)==len(names),'DERIVATIVE_DIMENSION')
    dp=sum((B.derivative(i)*q for i,q in enumerate(deriv)),ring.P(0))
    den=core.densities(z,p,X,Y,xp,yp)
    need((dp-den['transport']).iszero(),'EXACT_TRANSPORT_PRODUCT_RULE')
    exp=S([0,-2*z[5],f['c2']-2*f['p2'],f['c3']-2*(z[14]+p['A3']*z[17])]).expzero().a[3]
    need((exp-den['direct_bulk']).iszero(),'EXACT_CUBIC_DENSITY_EXPANSION')
    need(not (dp-(den['transport']+f['up']*X*X+2*f['u']*X*xp)).iszero(),'TRANSPORT_OMISSION_DETECTED')
    need(not (exp-(den['direct_bulk']-4*z[5]*f['p2'])).iszero(),'DENSITY_OMISSION_DETECTED')
    return {'pass':True,'checks':['EXACT_TRANSPORT_PRODUCT_RULE','EXACT_CUBIC_DENSITY_EXPANSION','TRANSPORT_OMISSION_DETECTED','DENSITY_OMISSION_DETECTED'],'scope':'Exact sparse polynomial identities and sensitive omissions; no numeric sampling.'}
def physical(raw,name):
    y=list(map(iv,raw));return y if name=='primary' else y[:4]+[(-y[0]).exp()]+y[4:]
def arm(name,binding):
    start=time.monotonic();data=read(FLOW/('FLOW_'+name+'.json'));old=read(SECOND/('PRODUCTION_'+name+'.json'));graph=read(GRAPH/'RESULT.json')['per_engine'][name]
    need(data['pass'] and data['matching']['resolved'],'ACCEPTED_FLOW_INVERSE')
    params=dict(data['parameters'],A3=data['matching']['A3']);p={k:iv(v) for k,v in params.items()}
    walls={side:{key:old['walls'][side]['fresh'][key] for key in ('xi','xi2')} for side in ('lower','upper')}
    dlo,dhi=map(fmpq,data['D']);D=arb((dlo+dhi)/2,(dhi-dlo)/2);h=fmpq(data['step'])
    x1a,x1b=[iv(walls[s]['xi']) for s in ('lower','upper')];x2a,x2b=[iv(walls[s]['xi2']) for s in ('lower','upper')]
    slopes={'x1p':out((x1b-x1a)/D),'x2p':out((x2b-x2a)/D)};xp,yp=[iv(slopes[k]) for k in ('x1p','x2p')]
    totals={k:arb(0) for k in ('c3','p3P','p3H','p1c2','p1p2','p1cubed','direct_bulk','transport')};mandatory_total=fmpq(0);optional_total=fmpq(0)
    refs=[];previous=None;nextindex=0;parent_previous=None
    for entry in data['chunks']:
        path=FLOW/entry['file'];need(sha(path)==entry['sha256'],'PARENT_CHUNK_HASH');chunk=read(path)
        need(chunk['binding_sha256']==sha(FLOW/'FROZEN.json') and chunk['parameters_sha256']==data['parameters_sha256'] and chunk['previous_sha256']==parent_previous,'PARENT_CHUNK_BINDING')
        records=[]
        for cell in chunk['records']:
            j=cell['index'];need(j==nextindex,'CELL_SEQUENCE');nextindex+=1;pos=j*h
            zraw=physical(cell['box'],name);z=[out(v) for v in zraw];zz=list(map(iv,z))
            X1=out(x1a+xp*arb((2*pos+h)/2,h/2));X2=out(x2a+yp*arb((2*pos+h)/2,h/2))
            dens=core.densities(zz,p,iv(X1),iv(X2),xp,yp);dens={k:out(v) for k,v in dens.items()}
            mandatory=max(fmpq(0),min(h,dlo-pos));optional=max(fmpq(0),min(h,dhi-pos))-mandatory
            contributions={}
            for k,v in dens.items():
                a=iv(v);contributions[k]=out(a*mandatory+a*arb(optional/2,optional/2));totals[k]+=iv(contributions[k])
            mandatory_total+=mandatory;optional_total+=optional
            records.append({'index':j,'physical_box':z,'X1':X1,'X2':X2,'mandatory':str(mandatory),'optional':str(optional),'densities':dens,'contributions':contributions})
        file=f'budgets/{name}/{entry["first"]:06d}.json'
        saved={'binding_sha256':binding,'engine':name,'parent_chunk':entry['file'],'parent_sha256':entry['sha256'],'previous_sha256':previous,'records':records}
        digest=put(file,saved);refs.append({'file':file,'sha256':digest,'parent_file':entry['file'],'parent_sha256':entry['sha256'],'first':entry['first'],'last':entry['last']});previous=digest;parent_previous=entry['sha256']
        if nextindex%1024==0 or nextindex==data['cells']:print(name,nextindex,'/',data['cells'],'seconds',round(time.monotonic()-start,1),flush=True)
    need(nextindex==data['cells'] and mandatory_total==dlo and optional_total==dhi-dlo,'INTEGRATION_DOMAIN')
    savedtot={k:out(v) for k,v in totals.items()};t={k:iv(v) for k,v in savedtot.items()}
    endpoint_states={'lower':[out(v) for v in physical(data['initial'],name)],'upper':[out(iv(v)) for v in data['physical_upper']]}
    endpoint_terms={s:out(core.endpoint(list(map(iv,endpoint_states[s])),p,iv(walls[s]['xi']),iv(walls[s]['xi2']))) for s in ('lower','upper')}
    transport=iv(endpoint_terms['upper'])-iv(endpoint_terms['lower']);bulk=core.bulk(t,p['A3']);g=iv(graph['graph3'])
    need(overlap(transport,t['transport']),'TRANSPORT_PRODUCT_RULE_RANGE')
    need(overlap(bulk,t['direct_bulk']),'DIRECT_GROUPED_BULK')
    distance=g+bulk+transport;pulled=g+bulk+t['transport'];direct=g+t['direct_bulk']+transport
    need(overlap(distance,pulled) and overlap(distance,direct),'DISTANCE_RECONSTRUCTION')
    result={'pass':True,'engine':name,'parameters':params,'D':data['D'],'step':data['step'],'cells':nextindex,'slopes':slopes,'walls':walls,'endpoint_states':endpoint_states,'endpoint_terms':endpoint_terms,
            'graph':graph['graph3'],'bulk':out(bulk),'transport':out(transport),'totals':savedtot,'distance':out(distance),'pulled_distance':out(pulled),'direct_distance':out(direct),'chunks':refs,
            'mandatory_total':str(mandatory_total),'optional_total':str(optional_total),'seconds':time.monotonic()-start,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    put('DISTANCE_'+name+'.json',result);return result
def run():
    need(sys.platform=='linux','LINUX_ONLY');put('CONTROLS_RESULT.json',controls());binding=sha(ROOT/'FROZEN.json')
    arms={name:arm(name,binding) for name in ('primary','independent')};a,b=[iv(v['distance']) for v in arms.values()];need(overlap(a,b),'ENGINE_DISTANCE_OVERLAP');d=hull(a,b)
    exported=out(d);lo,hi=map(fmpq,exported['exact_bounds']);sign=1 if lo>0 else -1 if hi<0 else 0
    return {'pass':True,'classification':'CUBIC_DISTANCE_REINFORCES_SHORTENING' if sign<0 else 'CUBIC_DISTANCE_OPPOSES_SHORTENING' if sign>0 else 'CUBIC_DISTANCE_SIGN_UNRESOLVED','sign':sign,'distance':exported,
            'arms':{n:{k:v[k] for k in ('graph','bulk','transport','distance','pulled_distance','direct_distance','seconds','peak_rss_kib','cells')} for n,v in arms.items()},
            'scope':'Formal cubic moving-endpoint proper-distance coefficient for the fixed lower-current direction; not finite-amplitude convergence or nonlinear evolution.'}
