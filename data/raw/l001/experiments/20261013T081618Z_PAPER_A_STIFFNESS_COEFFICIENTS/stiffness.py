"""Saved-data interval consequence, with no ODE producer imported or executed."""
import copy, hashlib, json
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path
HERE=Path(__file__).resolve().parent; OWNER=HERE.parents[1]
BASE='experiments/academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/'
BG='experiments/20261013T001854Z_PAPER_A_STATIC_TESTS/inputs/independent_root.json'
class Rejected(Exception): pass
def need(ok,name):
    if not ok: raise Rejected(name)
def I(x):
    a=tuple(map(Q,x['exact_bounds'])) if 'exact_bounds' in x else (Q(x['lo_exact']),Q(x['hi_exact']))
    need(a[0]<=a[1],'INTERVAL_ORDER'); return a
def p(x): return (Q(x),Q(x))
def add(a,b): return (a[0]+b[0],a[1]+b[1])
def neg(a): return (-a[1],-a[0])
def sub(a,b): return add(a,neg(b))
def mul(a,b):
    z=[x*y for x in a for y in b]; return min(z),max(z)
def scale(a,b): return mul(a,p(b))
def div(a,b):
    need(not b[0]<=0<=b[1],'DIVISOR'); return mul(a,(1/b[1],1/b[0]))
def sq(a): return (Q(0) if a[0]<=0<=a[1] else min(x*x for x in a), max(x*x for x in a))
def meet(a,b):
    z=(max(a[0],b[0]),min(a[1],b[1])); need(z[0]<=z[1],'DUAL_OVERLAP'); return z
def floor(x): return x.numerator//x.denominator
def ceil(x): return -floor(-x)
@lru_cache(None)
def exp_bound(x,upper):
    grid=2**40; x=Q(ceil(x*grid) if upper else floor(x*grid),grid)
    need(abs(x)<=5,'EXP_DOMAIN'); y=abs(x); term=Q(1); total=Q(1)
    for n in range(1,65): term=term*y/n; total+=term
    tail=term*y/65/(1-y/66); lo,hi=total,total+tail
    if x<0: lo,hi=1/hi,1/lo
    grid=10**18
    return Q(ceil(hi*grid) if upper else floor(lo*grid),grid)
def native(x):
    (m,e),(r,f)=x['_arb_native']; need(r>=0,'NATIVE_RADIUS')
    center=Q(m)*Q(2)**e; radius=Q(r)*Q(2)**f
    return center-radius,center+radius
def out(a):
    grid=10**18
    def decimal(n):
        sign='-' if n<0 else ''; n=abs(n)
        return f'{sign}{n//grid}.{n%grid:018d}'
    return {'exact_bounds':list(map(str,a)), 'outward_decimal_18':[decimal(floor(a[0]*grid)),decimal(ceil(a[1]*grid))], 'approximate':list(map(float,a))}

def compute(data,control=None):
    binding=data[BASE+'BINDINGS.json']; cfg=binding['config']; model={k:Q(v) for k,v in binding['model_exact'].items()}
    background=data[BG]; frozen=background['frozen_inputs']
    for key,bkey in [('gamma','gamma'),('lambda_a','lambda_a'),('lambda_b','lambda_b'),('m2','m_squared'),('v0','v0'),('v1','v1')]:
        need(model[key]==Q(float(frozen[bkey])),'SAME_EXACT_MODEL')
    A=tuple(map(Q,cfg['A'])); root=tuple(Q(float(v)) for v in frozen['root_box'])
    need(root[0]<A[0]<=A[1]<root[1],'CENTRAL_BACKGROUND_CONTAINMENT')
    Dlo,Dhi=map(Q,cfg['D']); mu=tuple(map(Q,cfg['mu']))
    ev=background['levels'][-1]['root_box']['event_quantities']
    Hb,Tb,Phib=(I(ev[k]) for k in ('H','S','phi'))
    need(Phib[0]>0 and A[0]>0 and model['m2']>0,'SCALAR_MAXIMUM_PRINCIPLE')
    g,m,v,la=(model[k] for k in ('gamma','m2','v0','lambda_a'))
    H0=scale(add(p(la),scale(sq(sub(A,p(v))),g/2)),-Q(1,6))
    phimax=max(A[1],Phib[1]); T2=12*sq(Hb)[1]-12+m*phimax**2
    need(Hb[1]<0 and H0[1]<0 and T2<Q(1,4),'BACKGROUND_T_BOUND')
    bb=sub(mul(add(p(-g/2),scale(Hb,4)),Tb),scale(Phib,m))
    if control=='UPPER_DENOMINATOR': bb=(Q(-1),Q(1))
    need(not bb[0]<=0<=bb[1],'UPPER_DENOMINATOR')
    engines={}
    for task_index,engine in [(4,'primary'),(5,'independent')]:
        r=data[BASE+'output/'+engine+'_strip.json']; ex=r['extrema']
        B0=I(r['B0']); need(not B0[0]<=0<=B0[1],'LOWER_DENOMINATOR')
        K=I(r['K']); need(K[0]>0,'POSITIVE_CURVATURE')
        lam=add(mu,scale(K,4)); need(lam[1]<0,'SHIFTED_SECTOR')
        W,psi,f=(I(ex[k]) for k in ('W','psi','f'))
        need(psi[0]>0,'POSITIVE_PROFILE'); fabs=max(abs(x) for x in f)
        monotone=-2*H0[1]*psi[0]-fabs/6; need(monotone>0,'PSI_MONOTONICITY')
        nodes=[(Q(0),p(0),p(1))]; indices=[]
        for name in data['checkpoint_paths']:
            c=data[name]; s=c['state']
            if s['task_index']!=task_index: continue
            need(c['guard']==r['guard'],'CHECKPOINT_GUARD')
            node_mu=native(s['params']['mu'])
            need(node_mu[0]<=mu[0] and mu[1]<=node_mu[1],'CHECKPOINT_MASS')
            j=s['cell_index']; indices.append(j); t=Q(2*j,cfg[engine+'_steps'])
            need(len(s['state'])==(8 if engine=='primary' else 7),'STATE_DIMENSION')
            if t<=Dlo: nodes.append((t,native(s['state'][0]),native(s['state'][5 if engine=='primary' else 4])))
        indices.sort(); need(indices==list(range(256,max(indices)+1,256)),'CHECKPOINT_GRID')
        nodes.sort(); need(nodes[-1][0]<Dlo,'TAIL_DOMAIN')
        zlo=Q(0); zhi=Q(0)
        for left,right in zip(nodes,nodes[1:]):
            t,w,u=left; t2,w2,u2=right; dt=t2-t
            need(dt>0 and u[0]>0 and u2[0]>0,'NODE_ORDER')
            zlo+=12*dt*exp_bound(2*w2[0],False)*u[0]**2
            zhi+=2*dt*exp_bound(2*w[1],True)*(fabs**2+6*u2[1]**2)
        t,w,u=nodes[-1]
        zlo+=12*(Dlo-t)*exp_bound(2*W[0],False)*u[0]**2
        zhi+=2*(Dhi-t)*exp_bound(2*w[1],True)*(fabs**2+6*psi[1]**2)
        if control=='NORM_ORDER': zlo=2*zhi
        need(0<zlo<=zhi,'NORM_ORDER'); Z=(zlo,zhi)
        psib=(u[0],psi[1]); need(psib[0]>0 and psib[0]<=psib[1],'WALL_PROFILE')
        Ca=div(sq(div(scale(lam,3),B0)),Z)
        Cb=div(sq(div(scale(mul(lam,psib),3),bb)),Z)
        ratio=div(mul(sq(psib),sq(B0)),sq(bb))
        engines[engine]={'Z':Z,'psi_b':psib,'Ca':Ca,'Cb':Cb,'Cb_over_Ca':ratio,'lambda':lam,'B0':B0,'monotonicity_lower':p(monotone),'node_count':len(nodes),'last_node':str(t)}
    combined={key:meet(engines['primary'][key],engines['independent'][key]) for key in ('Z','psi_b','Ca','Cb','Cb_over_Ca')}
    for key in ('Ca','Cb'): need(combined[key][0]>0,'POSITIVE_COEFFICIENT')
    useful=(combined['Z'][1]/combined['Z'][0]<=2 and all(combined[k][1]/combined[k][0]<=64 for k in ('Ca','Cb')) and combined['Cb_over_Ca'][1]/combined['Cb_over_Ca'][0]<=2 and combined['Cb_over_Ca'][0]>1)
    return {'classification':'USEFUL' if useful else 'WIDE','combined':{k:out(v) for k,v in combined.items()},'engines':{e:{k:out(v) if isinstance(v,tuple) else v for k,v in r.items()} for e,r in engines.items()},'background':{'bb':out(bb),'T_squared_upper':str(T2),'H0':out(H0)},'upper_wall_dominates':combined['Cb_over_Ca'][0]>1}

def main():
    manifest=json.loads((HERE/'SOURCE_BINDINGS.json').read_text()); data={'checkpoint_paths':manifest['checkpoint_paths']}
    for name,digest in manifest['sources'].items():
        blob=(OWNER/name).read_bytes(); need(hashlib.sha256(blob).hexdigest()==digest,'SOURCE_HASH:'+name)
        if name.endswith('.json'): data[name]=json.loads(blob)
    result=compute(data); controls=[]
    for name in ('LOWER_DENOMINATOR','CHECKPOINT_MASS','CHECKPOINT_GRID','POSITIVE_PROFILE','UPPER_DENOMINATOR','NORM_ORDER'):
        d=copy.deepcopy(data); flag=None
        if name=='LOWER_DENOMINATOR': d[BASE+'output/primary_strip.json']['B0'].update(lo_exact='-1',hi_exact='1')
        elif name=='CHECKPOINT_MASS': d[d['checkpoint_paths'][0]]['state']['params']['mu']={'_arb_native':[[0,0],[0,0]]}
        elif name=='CHECKPOINT_GRID': d['checkpoint_paths'].pop(1)
        elif name=='POSITIVE_PROFILE': d[BASE+'output/primary_strip.json']['extrema']['psi']['lo_exact']='0'
        else: flag=name
        try: compute(d,flag)
        except Rejected as err:
            need(str(err)==name,'CONTROL_WRONG_REJECTION:'+name+':'+str(err)); controls.append({'control':name,'rejected_by':str(err)})
        else: raise Rejected('CONTROL_ACCEPTED:'+name)
    print(json.dumps({'status':'PASS_PENDING_TERMINAL_REVIEW','result':result,'controls':controls,
      'premises':'Original exact central background, validated uniform strip and checkpoint enclosures, model provenance and accepted local Green-identity derivative remain inherited.',
      'scope':'Two local Hessian derivatives for background-preserving action changes; no finite stabilization threshold.'},indent=2))
if __name__=='__main__': main()
