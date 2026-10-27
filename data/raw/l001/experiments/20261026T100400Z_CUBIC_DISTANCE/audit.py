"""Independent exact saved-budget audit; no producer algebra imports or ODE."""
import hashlib,importlib.util,json,sys
from fractions import Fraction as F
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PARENT=ROOT.parent/'20261026T033400Z_CUBIC_FULL_FLOW'
SECOND=ROOT.parent/'20261026T015206Z_FORCED_SECOND_ORDER_R1'
GRAPH=ROOT.parent/'20261026T023331Z_CUBIC_GRAPH'
def need(v,label):
    if not v:raise AssertionError(label)
def read(p):return json.loads(Path(p).read_text())
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):h.update(block)
    return h.hexdigest()
def setup():
    global I
    s=importlib.util.spec_from_file_location('distance_audit_interval',SECOND/'terminal_audit/audit.py')
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);I=m.I
def iv(v):return I(*v['exact_bounds'])
def same(a,b):return a.lo==b.lo and a.hi==b.hi
def independent_fields(z,p):
    _,H,phi,T,E,a,f,g,ap,fp,_,ah,fh,_,p3p,_,_,p3h,_,_=z
    P=ap+p['A2']*ah;F2=fp+p['A2']*fh
    c2=-F(3,13)*(6*a*a+f*f)
    c3=-F(8,19)*(6*a*P+f*F2-3*a*c2)
    u=-2*H*a-T*f/3
    source2=H*c2-a*u-f*g/6
    derivative2=-2*H*P-T*F2/3+source2
    Hp=-T*T/3-p['k']*E*E;Tp=p['m2']*phi-4*H*T
    up=-2*Hp*a-2*H*u-(Tp*f+T*g)/3
    c2p=-F(3,13)*(12*a*u+2*f*g)
    return a,P,c2,c3,u,up,c2-2*P+2*a*a,c2p-2*derivative2+4*a*u,p3p,p3h
def endpoint(z,p,x,y):
    a,_,_,_,u,_,w2,_,_,_=independent_fields(z,p)
    return -2*a*y+w2*x-u*x*x
def densities(z,p,x,y,xp,yp):
    a,P,c2,c3,u,up,w2,w2p,part,hom=independent_fields(z,p)
    return {'c3':c3,'p3P':part,'p3H':hom,'p1c2':a*c2,'p1p2':a*P,'p1cubed':a*a*a,
            'direct_bulk':c3-2*(part+p['A3']*hom)-2*a*c2+4*a*P-F(4,3)*a*a*a,
            'transport':-2*u*y-2*a*yp+w2p*x+w2*xp-up*x*x-2*u*x*xp}
def grouped(t,A):return t['c3']-2*t['p3P']-2*A*t['p3H']-2*t['p1c2']+4*t['p1p2']-F(4,3)*t['p1cubed']
def generic_identities():
    # Small independent exact polynomial ring, only for the two fixed identities.
    names=('a','u','up','w','wp','x','xp','y','yp','c2','P','c3','p3');n=len(names);zero=(0,)*n
    def const(c):return {zero:F(c)} if c else {}
    def add(*polys):
        out={}
        for poly in polys:
            for k,v in poly.items():out[k]=out.get(k,F(0))+v
        return {k:v for k,v in out.items() if v}
    def scale(p,c):return {k:v*c for k,v in p.items() if v*c}
    def mul(a,b):
        out={}
        for x,u in a.items():
            for y,v in b.items():
                key=tuple(i+j for i,j in zip(x,y));out[key]=out.get(key,F(0))+u*v
        return {k:v for k,v in out.items() if v}
    variables={}
    for j,key in enumerate(names):
        powers=[0]*n;powers[j]=1;variables[key]={tuple(powers):F(1)}
    v=variables;a,u,up,w,wp,x,xp,y,yp=[v[k] for k in names[:9]]
    mapping={'a':'u','u':'up','w':'wp','x':'xp','y':'yp'}
    B=add(scale(mul(a,y),-2),mul(w,x),scale(mul(u,mul(x,x)),-1));derivative={}
    for powers,c in B.items():
        for name,dname in mapping.items():
            j=names.index(name)
            if powers[j]:
                q=list(powers);q[j]-=1;q[names.index(dname)]+=1
                derivative=add(derivative,{tuple(q):c*powers[j]})
    expected=add(scale(mul(u,y),-2),scale(mul(a,yp),-2),mul(wp,x),mul(w,xp),scale(mul(up,mul(x,x)),-1),scale(mul(u,mul(x,xp)),-2))
    need(derivative==expected,'EXACT_GENERIC_TRANSPORT_PRODUCT_RULE')
    b1=scale(a,-2);b2=add(v['c2'],scale(v['P'],-2));b3=add(v['c3'],scale(v['p3'],-2))
    coefficient=add(b3,mul(b1,b2),scale(mul(b1,mul(b1,b1)),F(1,6)))
    expected=add(v['c3'],scale(v['p3'],-2),scale(mul(a,v['c2']),-2),scale(mul(a,v['P']),4),scale(mul(a,mul(a,a)),F(-4,3)))
    need(coefficient==expected,'EXACT_CUBIC_EXPONENTIAL_COEFFICIENT')
    return ['EXACT_GENERIC_TRANSPORT_PRODUCT_RULE','EXACT_CUBIC_EXPONENTIAL_COEFFICIENT']
def run():
    need(sys.platform=='linux','LINUX_ONLY');setup();checks=generic_identities()
    binding=sha(ROOT/'FROZEN.json');parent_binding=sha(PARENT/'FROZEN.json')
    for mode in ('production','audit'):
        terminal=read(PARENT/(mode+'_TERMINAL.json'))
        need(terminal['pass'] and terminal['frozen_sha256']==parent_binding,'PARENT_TERMINAL')
        for name,digest in terminal['artifacts'].items():need(sha(PARENT/name)==digest,'PARENT_ARTIFACT')
    result=read(ROOT/'RESULT.json');controls=read(ROOT/'CONTROLS_RESULT.json')
    need(result['pass'] and controls['pass'],'RESULT_CONTROLS_PASS')
    keys={'c3','p3P','p3H','p1c2','p1p2','p1cubed','direct_bulk','transport'}
    reports={};distances={}
    def outward(saved,expected,label):need(iv(saved).contains(expected),label)
    def physical_mapping(saved,raw,name,label):
        z=list(map(iv,saved));r=list(map(iv,raw));need(len(z)==20,'PHYSICAL_DIMENSION')
        mapped=z if name=='primary' else z[:4]+z[5:]
        need(len(mapped)==len(r) and all(a.contains(b) for a,b in zip(mapped,r)),label)
        need(z[4].lo>0,'POSITIVE_INVERSE_WARP');return z
    for name in ('primary','independent'):
        data=read(ROOT/('DISTANCE_'+name+'.json'));flow=read(PARENT/('FLOW_'+name+'.json'))
        old=read(SECOND/('PRODUCTION_'+name+'.json'));graph=read(GRAPH/'RESULT.json')['per_engine'][name]['graph3']
        need(data['pass'] and data['engine']==name and flow['pass'] and flow['matching']['resolved'],'ENGINE_PARENT_PASS')
        expected_params=dict(flow['parameters'],A3=flow['matching']['A3'])
        need(data['parameters']==expected_params,'FULL_PARAMETER_BINDING');p={k:iv(v) for k,v in data['parameters'].items()}
        need(data['D']==flow['D'] and data['step']==flow['step'],'DOMAIN_BINDING')
        dlo,dhi=map(F,data['D']);h=F(data['step']);need(0<dlo<=dhi and h>0,'POSITIVE_DOMAIN')
        walls={side:{key:old['walls'][side]['fresh'][key] for key in ('xi','xi2')} for side in ('lower','upper')}
        need(data['walls']==walls,'WALL_DISPLACEMENT_BINDING')
        xa,xb=[iv(walls[s]['xi']) for s in ('lower','upper')];ya,yb=[iv(walls[s]['xi2']) for s in ('lower','upper')]
        xp,yp=[iv(data['slopes'][k]) for k in ('x1p','x2p')]
        need(xp.contains((xb-xa)/I(dlo,dhi)) and yp.contains((yb-ya)/I(dlo,dhi)),'OUTWARD_AFFINE_SLOPES')
        totals={k:I(0) for k in keys};previous=None;parent_previous=None;index=0;mandatory_sum=F(0);optional_sum=F(0)
        need(len(data['chunks'])==len(flow['chunks']),'CHUNK_COUNT')
        for entry,parent_entry in zip(data['chunks'],flow['chunks']):
            need(entry['parent_file']==parent_entry['file'] and entry['parent_sha256']==parent_entry['sha256'],'PARENT_CHUNK_REFERENCE')
            need(entry['first']==parent_entry['first']==index and entry['last']==parent_entry['last'],'CHUNK_INDICES')
            bp=ROOT/entry['file'];pp=PARENT/parent_entry['file']
            need(bp.resolve().is_relative_to(ROOT.resolve()) and pp.resolve().is_relative_to(PARENT.resolve()),'CHUNK_PATH')
            need(sha(bp)==entry['sha256'] and sha(pp)==parent_entry['sha256'],'CHUNK_HASH')
            budget=read(bp);parent=read(pp)
            need(budget['engine']==name and budget['binding_sha256']==binding and budget['previous_sha256']==previous,'BUDGET_BINDING_CHAIN')
            need(budget['parent_chunk']==parent_entry['file'] and budget['parent_sha256']==parent_entry['sha256'],'BUDGET_PARENT_BINDING')
            need(parent['engine']==name and parent['binding_sha256']==parent_binding and parent['parameters_sha256']==flow['parameters_sha256'] and parent['previous_sha256']==parent_previous,'PARENT_BINDING_CHAIN')
            need(parent['first']==index and parent['last']==parent_entry['last'],'PARENT_CHUNK_INDICES')
            need(len(budget['records'])==len(parent['records']) and 1<=len(budget['records'])<=32,'BOUNDED_CHUNK')
            for row,cell in zip(budget['records'],parent['records']):
                need(row['index']==cell['index']==index,'CELL_INDEX')
                z=physical_mapping(row['physical_box'],cell['box'],name,'WHOLE_PARENT_BOX')
                pos=index*h;x=iv(row['X1']);y=iv(row['X2'])
                need(x.contains(xa+xp*I(pos,pos+h)) and y.contains(ya+yp*I(pos,pos+h)),'AFFINE_CELL_ENCLOSURE')
                mandatory=max(F(0),min(h,dlo-pos));optional=max(F(0),min(h,dhi-pos))-mandatory
                need(F(row['mandatory'])==mandatory and F(row['optional'])==optional,'EXACT_INTEGRATION_WEIGHTS')
                need(set(row['densities'])==set(row['contributions'])==keys,'DENSITY_INVENTORY')
                rebuilt=densities(z,p,x,y,xp,yp)
                for key in keys:
                    outward(row['densities'][key],rebuilt[key],'OUTWARD_DENSITY:'+key)
                    density=iv(row['densities'][key]);contribution=iv(row['contributions'][key])
                    need(contribution.contains(density*mandatory+density*I(0,optional)),'OUTWARD_CONTRIBUTION:'+key)
                    totals[key]=totals[key]+contribution
                mandatory_sum+=mandatory;optional_sum+=optional;index+=1
            need(index-1==entry['last'],'CHUNK_LAST');previous=entry['sha256'];parent_previous=parent_entry['sha256']
        need(index==data['cells']==flow['cells'],'COMPLETE_CELL_COUNT')
        need(mandatory_sum==F(data['mandatory_total'])==dlo and optional_sum==F(data['optional_total'])==dhi-dlo,'EXACT_DOMAIN_COVERAGE')
        need(set(data['totals'])==keys,'TOTAL_INVENTORY')
        for key in keys:outward(data['totals'][key],totals[key],'OUTWARD_SUM:'+key)
        t={k:iv(v) for k,v in data['totals'].items()}
        lower=physical_mapping(data['endpoint_states']['lower'],flow['initial'],name,'LOWER_ENDPOINT_BINDING')
        upper=list(map(iv,data['endpoint_states']['upper']))
        need(len(upper)==20 and all(a.contains(iv(b)) for a,b in zip(upper,flow['physical_upper'])),'UPPER_ENDPOINT_BINDING')
        for side,z,x,y in (('lower',lower,xa,ya),('upper',upper,xb,yb)):
            outward(data['endpoint_terms'][side],endpoint(z,p,x,y),'OUTWARD_ENDPOINT_TRANSPORT:'+side)
        transport=iv(data['endpoint_terms']['upper'])-iv(data['endpoint_terms']['lower']);bulk=grouped(t,p['A3'])
        need(data['graph']==graph,'GRAPH_BINDING');g=iv(graph)
        outward(data['bulk'],bulk,'OUTWARD_GROUPED_BULK');outward(data['transport'],transport,'OUTWARD_TRANSPORT')
        distance=g+bulk+transport;pulled=g+bulk+t['transport'];direct=g+t['direct_bulk']+transport
        for key,value in (('distance',distance),('pulled_distance',pulled),('direct_distance',direct)):outward(data[key],value,'OUTWARD_DISTANCE:'+key)
        need(transport.overlap(t['transport']) and bulk.overlap(t['direct_bulk']),'INTEGRATED_IDENTITIES')
        need(distance.overlap(pulled) and distance.overlap(direct),'DISTANCE_FORMS')
        distances[name]=iv(data['distance']);reports[name]={'cells_checked':index,'chunks_checked':len(data['chunks']),'mandatory_total':str(mandatory_sum),'optional_total':str(optional_sum),'distance':data['distance']}
    a,b=distances.values();need(a.overlap(b),'CROSS_ENGINE_DISTANCE')
    hull=I(min(a.lo,b.lo),max(a.hi,b.hi));outward(result['distance'],hull,'OUTWARD_ENGINE_HULL')
    # Outward export may legitimately erase a strict sign, but cannot create one.
    sign=lambda v:1 if v.lo>0 else -1 if v.hi<0 else 0
    s=sign(iv(result['distance']));need(result['sign']==s,'CLASSIFICATION_SIGN')
    if s:need(sign(hull)==s,'NO_EXPORT_CREATED_SIGN')
    label={-1:'CUBIC_DISTANCE_REINFORCES_SHORTENING',1:'CUBIC_DISTANCE_OPPOSES_SHORTENING',0:'CUBIC_DISTANCE_SIGN_UNRESOLVED'}[s]
    need(result['classification']==label,'CLASSIFICATION')
    return {'pass':True,'classification':'CUBIC_DISTANCE_EXACT_SAVED_BUDGETS_VERIFIED','generic_identity_checks':checks,'engines':reports,'sign':s,
            'scope':'Independent exact Fraction reconstruction of saved whole-cell density, mandatory/optional integration, totals, endpoint transport, distance algebra and un-intersected hull. Inherited ODE certificates are not rerun; direct-W exp(-W) exports are checked for positivity and containment of all other parent coordinates, not independently exponentiated. Formal cubic coefficient only, not a finite-amplitude/tail/radius result.'}
