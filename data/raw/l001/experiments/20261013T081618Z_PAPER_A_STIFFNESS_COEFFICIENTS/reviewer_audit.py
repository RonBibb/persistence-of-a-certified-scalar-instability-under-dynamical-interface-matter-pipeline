"""Independent reconstruction with separately summed degree-80 exponential bounds."""
import hashlib,json,math
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
P=Path(__file__).resolve().parent; L=P.parents[1]
B='experiments/academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/'
def read(p): return json.loads(p.read_text())
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
gate=read(P/'INDEPENDENT_GATE.json'); manifest=read(P/'SOURCE_BINDINGS.json')
for n,h in gate['frozen_hashes'].items(): assert digest(P/n)==h
data={}
for n,h in manifest['sources'].items():
    assert digest(L/n)==h
    if n.endswith('.json'): data[n]=read(L/n)
meta=read(P/'RUN_METADATA.json'); result=read(P/'RESULT.json'); out=result['result']
assert meta['returncode']==0 and (P/'STDERR.txt').read_bytes()==b''
assert meta['stdout_sha256']==digest(P/'RESULT.json') and meta['gate_sha256']==digest(P/'INDEPENDENT_GATE.json')

class I:
    def __init__(self,l,u=None): self.l=F(l); self.u=F(l if u is None else u); assert self.l<=self.u
    def __add__(self,b):
        b=b if isinstance(b,I) else I(b); return I(self.l+b.l,self.u+b.u)
    __radd__=__add__
    def __neg__(self): return I(-self.u,-self.l)
    def __sub__(self,b): return self+-b
    def __mul__(self,b):
        b=b if isinstance(b,I) else I(b)
        p=[self.l*b.l,self.l*b.u,self.u*b.l,self.u*b.u]; return I(min(p),max(p))
    __rmul__=__mul__
    def __truediv__(self,b):
        b=b if isinstance(b,I) else I(b); assert b.l>0 or b.u<0
        return self*I(1/b.u,1/b.l)
    def sq(self): return I(0 if self.l<=0<=self.u else min(self.l**2,self.u**2),max(self.l**2,self.u**2))
    def pair(self): return self.l,self.u
def iv(r): return I(*r['exact_bounds']) if 'exact_bounds' in r else I(r['lo_exact'],r['hi_exact'])
def native(r):
    (m,e),(n,f)=r['_arb_native']; assert n>=0
    midpoint=F(m)*F(2)**e; radius=F(n)*F(2)**f
    return I(midpoint-radius,midpoint+radius)
def fl(x): return x.numerator//x.denominator
def ce(x): return -fl(-x)
@lru_cache(None)
def exp_at(x,upper):
    dy=2**40; x=F(ce(x*dy) if upper else fl(x*dy),dy); y=abs(x); assert y<=5
    # Sum separately from powers and factorials; N=80 differs from owner's N=64 recurrence.
    n=80; low=sum((y**j/F(math.factorial(j)) for j in range(n+1)),F(0))
    high=low+y**(n+1)/F(math.factorial(n+1))/(1-y/F(n+2))
    if x<0: low,high=1/high,1/low
    scale=10**18
    return F(ce(high*scale) if upper else fl(low*scale),scale)
def check(name,expected,saved):
    actual=iv(saved)
    assert actual.pair()==expected.pair(),name
    lo,hi=map(F,saved['outward_decimal_18'])
    assert lo<=actual.l<=actual.u<=hi,name
    assert actual.l-lo<F(1,10**18) and hi-actual.u<F(1,10**18),name

binding=data[B+'BINDINGS.json']; cfg=binding['config']; model={k:F(v) for k,v in binding['model_exact'].items()}
bg=data['experiments/20261013T001854Z_PAPER_A_STATIC_TESTS/inputs/independent_root.json']
fr=bg['frozen_inputs']; ev=bg['levels'][-1]['root_box']
assert ev['event_validated'] and ev['G_s_strictly_negative'] and ev['all_H_strictly_negative']
for k,bk in [('gamma','gamma'),('lambda_a','lambda_a'),('lambda_b','lambda_b'),('m2','m_squared'),('v0','v0'),('v1','v1')]: assert model[k]==F(float(fr[bk]))
launch=I(*cfg['A']); outer=I(*[F(float(x)) for x in fr['root_box']]); assert outer.l<launch.l<=launch.u<outer.u
D=I(*cfg['D']); event=I(*ev['event_bracket_exact']); assert event.l<=D.l<=D.u<=event.u
Hb,Tb,Phib=[iv(ev['event_quantities'][k]) for k in ('H','S','phi')]
gamma,m2,v0,la=[model[k] for k in ('gamma','m2','v0','lambda_a')]
H0=-(I(la)+gamma*(launch-I(v0)).sq()/2)/6
assert Phib.l>0 and launch.l>0 and m2>0 and Hb.u<0 and H0.u<0
T2=12*Hb.sq().u-12+m2*max(launch.u,Phib.u)**2; assert T2<F(1,4)
beta=(-I(gamma/2)+4*Hb)*Tb-m2*Phib; assert beta.l>0 or beta.u<0
assert F(out['background']['T_squared_upper'])==T2
check('H0',H0,out['background']['H0']); check('bb',beta,out['background']['bb'])
computed={}; counts={}
for engine,task,dim,psipos in [('primary',4,8,5),('independent',5,7,4)]:
    rec=data[B+'output/'+engine+'_strip.json']; assert rec['status']=='COMPLETE' and rec['task']==engine+'_strip'
    W,psi,f=[iv(rec['extrema'][k]) for k in ('W','psi','f')]
    K=iv(rec['K']); B0=iv(rec['B0']); lam=I(*cfg['mu'])+4*K
    assert K.l>0 and lam.u<0 and psi.l>0 and (B0.l>0 or B0.u<0)
    fabs=max(abs(f.l),abs(f.u)); mono=-2*H0.u*psi.l-fabs/6; assert mono>0
    rows=[]
    for path in manifest['checkpoint_paths']:
        cp=data[path]; s=cp['state']
        if s['task_index']!=task: continue
        assert cp['guard']==rec['guard'] and len(s['state'])==dim
        mu=native(s['params']['mu']); assert mu.l<=F(cfg['mu'][0])<=F(cfg['mu'][1])<=mu.u
        rows.append((s['cell_index'],native(s['state'][0]),native(s['state'][psipos])))
    rows.sort(key=lambda r:r[0]); assert [r[0] for r in rows]==list(range(256,rows[-1][0]+1,256))
    counts[engine]=len(rows)
    nodes=[(F(0),I(0),I(1))]+[(F(2*j,cfg[engine+'_steps']),w,u) for j,w,u in rows if F(2*j,cfg[engine+'_steps'])<=D.l]
    low=F(0); high=F(0)
    for left,right in zip(nodes,nodes[1:]):
        s,w,u=left; t,v,q=right; dt=t-s; assert dt>0 and u.l>0 and q.l>0
        low+=12*dt*exp_at(2*v.l,False)*u.l**2
        high+=2*dt*exp_at(2*w.u,True)*(fabs**2+6*q.u**2)
    t,w,u=nodes[-1]; assert t<D.l
    low+=12*(D.l-t)*exp_at(2*W.l,False)*u.l**2
    high+=2*(D.u-t)*exp_at(2*w.u,True)*(fabs**2+6*psi.u**2)
    Z=I(low,high); assert Z.l>0
    wallpsi=I(u.l,psi.u)
    Ca=(3*lam/B0).sq()/Z; Cb=(3*lam*wallpsi/beta).sq()/Z
    ratio=wallpsi.sq()*B0.sq()/beta.sq()
    calc={'Z':Z,'psi_b':wallpsi,'Ca':Ca,'Cb':Cb,'Cb_over_Ca':ratio,'lambda':lam,'B0':B0,'monotonicity_lower':I(mono)}
    computed[engine]=calc
    for key,val in calc.items(): check(engine+key,val,out['engines'][engine][key])
    assert out['engines'][engine]['node_count']==len(nodes) and F(out['engines'][engine]['last_node'])==t
combined={}
for key in ('Z','psi_b','Ca','Cb','Cb_over_Ca'):
    a=computed['primary'][key]; b=computed['independent'][key]; z=I(max(a.l,b.l),min(a.u,b.u))
    check('combined'+key,z,out['combined'][key]); combined[key]=z
useful=combined['Z'].u/combined['Z'].l<=2 and all(combined[k].u/combined[k].l<=64 for k in ('Ca','Cb')) and combined['Cb_over_Ca'].u/combined['Cb_over_Ca'].l<=2 and combined['Cb_over_Ca'].l>1
assert out['classification']==('USEFUL' if useful else 'WIDE')
assert out['upper_wall_dominates']==(combined['Cb_over_Ca'].l>1)
expected={'LOWER_DENOMINATOR','CHECKPOINT_MASS','CHECKPOINT_GRID','POSITIVE_PROFILE','UPPER_DENOMINATOR','NORM_ORDER'}
assert {c['control'] for c in result['controls']}==expected and all(c['control']==c['rejected_by'] for c in result['controls'])
print(json.dumps({'status':'PASS','source_hashes_verified':len(manifest['sources']),'checkpoint_nodes':counts,
 'all_owner_intervals_exactly_reconstructed':True,'independent_exp_degree':80,'classification':out['classification'],
 'owner_result_sha256':digest(P/'RESULT.json'),'all_outward_decimals_checked':True},indent=2))
