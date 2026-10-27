"""Prospective Linux-only independent saved-record Fraction audit; no ODE."""
import sys
sys.dont_write_bytecode=True
import hashlib,json,os,signal,time
from pathlib import Path
from fractions import Fraction as F
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
FROZEN_SHA='d3303948130b87644d7e3f9ded73fddc97abdb892695def874d94fb0cc61a986'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,label):
    if not v:raise AssertionError(label)
class I:
    def __init__(self,a,b=None):
        self.lo=F(a);self.hi=F(a if b is None else b)
        need(self.lo<=self.hi,'INTERVAL_ORDER')
    @staticmethod
    def cast(x):return x if isinstance(x,I) else I(x)
    def __add__(self,x):
        x=I.cast(x);return I(self.lo+x.lo,self.hi+x.hi)
    __radd__=__add__
    def __neg__(self):return I(-self.hi,-self.lo)
    def __sub__(self,x):return self+-I.cast(x)
    def __rsub__(self,x):return I.cast(x)+-self
    def __mul__(self,x):
        x=I.cast(x);v=[a*b for a in (self.lo,self.hi) for b in (x.lo,x.hi)]
        return I(min(v),max(v))
    __rmul__=__mul__
    def __truediv__(self,x):
        x=I.cast(x);need(not x.zero(),'ZERO_DIVISOR')
        return self*I(1/x.hi,1/x.lo)
    def zero(self):return self.lo<=0<=self.hi
    def overlap(self,x):return max(self.lo,x.lo)<=min(self.hi,x.hi)
    def contains(self,x):return self.lo<=x.lo and x.hi<=self.hi
    def record(self):return {'exact_bounds':[str(self.lo),str(self.hi)]}
def iv(x):
    need(set(x)=={'exact_bounds'},'BOUND_SCHEMA')
    return I(*x['exact_bounds'])
def save(name,r):
    dest=HERE/name;tmp=HERE/(name+'.tmp')
    with tmp.open('x') as f:json.dump(r,f,indent=2);f.flush();os.fsync(f.fileno())
    os.link(tmp,dest);tmp.unlink()
def authenticate():
    ad=read(HERE/'ADMISSION.json');need(ad['admitted'] is True,'AUDIT_ADMISSION')
    for p,d in ad['files'].items():need(sha(p)==d,'AUDIT_BOUND:'+p)
    need(str(Path(sys.executable).resolve())==ad['executable_realpath'],'AUDIT_INTERPRETER')
    need(sha(ROOT/'FROZEN.json')==FROZEN_SHA,'PRODUCER_FREEZE')
    frozen=read(ROOT/'FROZEN.json')
    for p,d in frozen['files'].items():need(sha(p)==d,'PRODUCER_BOUND:'+p)
    for mode in ('controls','probe','production'):
        terminal=read(ROOT/(mode+'_TERMINAL.json'))
        need(terminal['pass'] is True and terminal['frozen_sha256']==FROZEN_SHA,'TERMINAL:'+mode)
        for suffix in ('RUNTIME_BEFORE','RUNTIME_AFTER'):
            for p,d in read(ROOT/(mode+'_'+suffix+'.json')).items():
                need(frozen['files'].get(p)==d and sha(p)==d,'RUNTIME:'+p)
    need(not any(ROOT.glob('*FAILURE.json')),'FAILED_PACKET')
    return ad
def audit_engine(name):
    r=read(ROOT/('PRODUCTION_'+name+'.json'))
    need(r['engine']==name and r['all_gates'] is True,'ENGINE_IDENTITY')
    h=F(2,8192 if name=='primary' else 16384);dlo,dhi=map(F,r['inputs']['D'])
    n=-((-dhi)//h)
    need(r['cells']==n and F(r['step'])==h and len(r['budgets'])==n,'CELL_COUNT')
    totals={k:I(0) for k in ('p1','p2P','p2H','c2','p1sq','transport')}
    expected_cover=[]
    for j,row in enumerate(r['budgets']):
        pos=j*h;mandatory=max(F(0),min(h,dlo-pos))
        optional=max(F(0),min(h,dhi-pos))-mandatory
        need(row['index']==j and F(row['s'])==pos and F(row['step'])==h,'CELL_POSITION')
        need(F(row['mandatory'])==mandatory and F(row['optional'])==optional and optional>=0,'SIGNED_DOMAIN')
        need(set(row['budgets'])==set(totals),'BUDGET_KEYS')
        for key in totals:
            b=iv(row['budgets'][key]);need((b.lo*2**80).denominator==1 and (b.hi*2**80).denominator==1,'DYADIC_BUDGET')
            totals[key]=totals[key]+b
        if pos+h>=dlo and pos<=dhi:expected_cover.append((max(dlo,pos),min(dhi,pos+h)))
    need([(F(v['lo']),F(v['hi'])) for v in r['cover']]==expected_cover,'COMPLETE_TERMINAL_COVER')
    for key,total in totals.items():need(iv(r['totals'][key]).contains(total),'EXPORTED_SUM:'+key)
    lo,hi=(r['walls'][s] for s in ('lower','upper'))
    lower=list(map(iv,lo['state']));upper=list(map(iv,hi['state']))
    need(len(lower)==len(upper)==14,'STATE_LENGTH')
    freshlo={k:iv(v) for k,v in lo['fresh'].items()};freshhi={k:iv(v) for k,v in hi['fresh'].items()}
    fh=upper[13]+2*upper[3]*upper[11]+freshhi['Gamma2']*upper[12]/2
    need(not iv(r['FH']).zero() and iv(r['FH']).overlap(fh),'HOMOGENEOUS_INVERSE')
    for wall,state,w,sigma in ((lo,lower,freshlo,1),(hi,upper,freshhi,-1)):
        p2,f2,g2=state[8:11];T=state[3]
        chi=(f2+T*w['xi2']-w['o2'])/w['d2']
        q5=g2+w['Tp']*w['xi2']-T*w['c2']+2*T*p2-sigma*(21*(f2+T*w['xi2'])-chi)/2+w['j2']
        q6=2*sigma*(g2+2*T*p2)-w['Gamma2']*f2-w['R2']
        oscillator=w['d2']*chi-f2-T*w['xi2']+w['o2']
        graph=w['graph_divisor']*w['xi2']+w['qI_geometric']+w['qI_current']+w['qI_oscillator']
        rows=dict(oscillator=oscillator,scalar_Q5=q5,undivided_Q6=q6,graph=graph,
                  Q5_Q6_elimination=2*sigma*w['d2']*q5-oscillator-w['d2']*q6)
        for key,v in rows.items():need(v.zero() and iv(wall['rows'][key]).zero() and v.overlap(iv(wall['rows'][key])),'WALL_ROW:'+key)
        need(chi.overlap(iv(wall['chi2'])),'CHI2')
    graph=freshhi['xi2']-freshlo['xi2']
    transport=-2*upper[5]*freshhi['xi']+2*lower[5]*freshlo['xi']
    a2=iv(r['A2'])
    bulk=-2*(totals['p2P']+a2*totals['p2H'])+totals['c2']+2*totals['p1sq']
    d1=freshhi['xi']-freshlo['xi']-2*totals['p1']
    checks=dict(graph=graph,bulk=bulk,endpoint_transport=transport,d1=d1,
                d2=graph+bulk+transport,pulled_d2=graph+bulk+totals['transport'])
    for key,v in checks.items():need(v.overlap(iv(r[key])),'EXACT_FORMULA_COMPATIBILITY:'+key)
    need(totals['transport'].overlap(transport),'TRANSPORT_IDENTITY')
    return dict(engine=name,cells=n,exact_exported_sums_contained=True,
        exact_interval_formula_consistency=True,wall_rows_reconstructed=True,
        reconstructed={k:v.record() for k,v in checks.items()},
        A2_formula_independently_reconstructed=False,
        A2_limitation='Preassembly FP/raw upper particular state is not exported; A2 remains inherited from frozen guarded producer.')
def main():
    need(sys.platform=='linux','LINUX_ONLY');start=time.monotonic();ad=authenticate()
    results=[audit_engine(n) for n in ('primary','independent')]
    raw=[iv(read(ROOT/('PRODUCTION_'+n+'.json'))['d2']) for n in ('primary','independent')]
    need(raw[0].overlap(raw[1]),'ENGINE_OVERLAP')
    union=I(min(x.lo for x in raw),max(x.hi for x in raw))
    final=read(ROOT/'PRODUCTION_RESULT.json');published=iv(final['d2'])
    need(published.contains(union),'HULL_OUTWARD')
    sign=1 if published.lo>0 else -1 if published.hi<0 else 0
    labels={1:'SECOND_ORDER_OPPOSES_SHORTENING',-1:'SECOND_ORDER_REINFORCES_SHORTENING',0:'SECOND_ORDER_SIGN_UNRESOLVED'}
    need(final['sign']==sign and final['classification']==labels[sign],'CLASSIFICATION')
    authenticate()
    save('AUDIT_RESULT.json',dict(status='PASS_SAVED_RECORD_CONSISTENCY',engines=results,sign=sign,
        producer_classification=labels[sign],seconds=time.monotonic()-start,
        no_ode_replay=True,no_complete_A2_witness=True,
        scope='Exact exported budget sums, formula/wall consistency, domain/classification and frozen integrity. Not independent IVP or complete A2 proof.'))
if __name__=='__main__':
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUDIT_CAP_300')));signal.alarm(300)
    try:main()
    except BaseException as e:save('AUDIT_FAILURE.json',dict(status='AUDIT_INCOMPLETE',error=repr(e)));raise
    finally:signal.alarm(0)
