"""Parameter-uniform quartic background Krawczyk attempt, frozen radii."""
import hashlib,json,math,os,sys,time,traceback
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parent
from flint import arb,fmpq,ctx
ctx.prec=768;ctx.threads=1
OUT=ROOT/'family_certificate';OUT.mkdir(exist_ok=True)
def exact(x):return x if isinstance(x,arb) else arb(fmpq(str(Q(x))))
def bounds(x):return x.lower().fmpq(),x.upper().fmpq()
def interval(a,b):a,b=fmpq(str(a)),fmpq(str(b));return arb((a+b)/2,(b-a)/2)
def hull(a,b):al,ah=bounds(a);bl,bh=bounds(b);return interval(min(al,bl),max(ah,bh))
def pad(x):lo,hi=bounds(x);e=(hi-lo)/8+fmpq(1,2**640);return interval(lo-e,hi+e)
def inside(a,b):al,ah=bounds(a);bl,bh=bounds(b);return bl<al and ah<bh
def pack(x):lo,hi=bounds(x);return {'bounds':[str(lo),str(hi)],'approx':[float(lo),float(hi)]}
def save(p,x):
    t=p.with_suffix('.tmp')
    with t.open('w') as f:json.dump(x,f,indent=2);f.flush();os.fsync(f.fileno())
    os.replace(t,p)
def need(ok,label):
    if not ok:raise RuntimeError(label)
class Dual:
    def __init__(self,v,d=0):self.v=exact(v);self.d=exact(d)
    def __add__(self,b):
        b=asdual(b);return Dual(self.v+b.v,self.d+b.d)
    __radd__=__add__
    def __neg__(self):return Dual(-self.v,-self.d)
    def __sub__(self,b):return self+-asdual(b)
    def __rsub__(self,b):return asdual(b)+-self
    def __mul__(self,b):
        b=asdual(b);return Dual(self.v*b.v,self.d*b.v+self.v*b.d)
    __rmul__=__mul__
    def __truediv__(self,b):
        b=asdual(b);return Dual(self.v/b.v,(self.d*b.v-self.v*b.d)/(b.v*b.v))
def asdual(x):return x if isinstance(x,Dual) else Dual(x)
def flatten(y):return [x.v for x in y]+[x.d for x in y]
def dualize(y):return [Dual(v,d) for v,d in zip(y[:5],y[5:])]
def potential(P,p):return p['m2']*P*P/2+p['q']*P*P*P*P/4
def slope(P,p):return p['m2']*P+p['q']*P*P*P
def initial(A,p):
    a=Dual(A,1);H=-(p['lambda_a']+p['gamma']*(a-p['v0'])*(a-p['v0'])/2)/6;T=p['gamma']*(a-p['v0'])/2
    k=H*H-1-T*T/12+potential(a,p)/6
    return flatten([Dual(0),H,a,T,Dual(1)]),k
def rhs(y,p,k):
    W,H,P,T,E=dualize(y)
    return flatten([H,-T*T/3-k*E*E,T,slope(P,p)-4*H*T,-H*E])
def conv(a,b,n):return sum((a[j]*b[n-j] for j in range(n+1)),Dual(0))
def coefficients(y,nmax,p,k):
    rows=[[v] for v in dualize(y)];W,H,P,T,E=rows;pp=[]
    for n in range(nmax):
        pp.append(conv(P,P,n))
        vals=[H[n],-conv(T,T,n)/3-k*conv(E,E,n),T[n],p['m2']*P[n]+p['q']*conv(pp,P,n)-4*conv(H,T,n),-conv(H,E,n)]
        for row,v in zip(rows,vals):row.append(v/(n+1))
    return [[z.v for z in row] for row in rows]+[[z.d for z in row] for row in rows]
def step(y,h,p,k):
    dt=interval(0,h);box=[pad(hull(a,a+dt*v)) for a,v in zip(y,rhs(y,p,k))]
    for it in range(32):
        image=[hull(a,a+dt*v) for a,v in zip(y,rhs(box,p,k))]
        if all(inside(a,b) for a,b in zip(image,box)):break
        box=[pad(hull(a,b)) for a,b in zip(image,box)]
    else:raise RuntimeError('PICARD_FAIL')
    point=coefficients(y,4,p,k);rem=[r[5] for r in coefficients(box,5,p,k)]
    return evaluate(point,rem,h),{'point':point,'rem':rem,'box':box,'h':h}
def evaluate(point,rem,t):
    yy=[]
    for row,r in zip(point,rem):
        v=r
        for c in reversed(row):v=v*t+c
        yy.append(v)
    return yy
def residuals(y,p):
    W,H,P,T,E=dualize(y)
    return [H-(p['lambda_b']+p['gamma']*(P-p['v1'])*(P-p['v1'])/2)/6,T+p['gamma']*(P-p['v1'])/2]
def jacD(y,p,k):
    W,H,P,T,E=y[:5]
    return [-T*T/3-k.v*E*E-p['gamma']*(P-p['v1'])*T/6,slope(P,p)-4*H*T+p['gamma']*T/2]
def flow(A,D,p,label):
    y,k=initial(A,p);h=fmpq(1,8192);dlo,dhi=bounds(D);n=math.ceil(Q(str(dhi))/Q(str(h)))
    need(k.v.lower()>0,'CURVATURE');start=time.monotonic();event=None;cover=[];profile={};source=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for j in range(n):
        y,cell=step(y,h,p,k);W,H,P,T,E=cell['box'][:5];Tp=slope(P,p)-4*H*T
        need(all(v.is_finite() for v in y),'NONFINITE');need(E.lower()>0,'POSITIVE_E')
        invariant=H*H-1-T*T/12+potential(P,p)/6-k.v*E*E
        need(invariant.contains(0),'BACKGROUND_CONSTRAINT_ESCAPE')
        for key,v in [('W',W),('H',H),('P',P),('T',T),('Tp',Tp),('E',E)]:profile[key]=v if key not in profile else hull(profile[key],v)
        s=j*h
        if s+h>=dlo and s<=dhi:
            lo=max(fmpq(0),dlo-s);hi=min(h,dhi-s);v=evaluate(cell['point'],cell['rem'],interval(lo,hi))
            event=v if event is None else [hull(a,b) for a,b in zip(event,v)]
            cover.append([str(s+lo),str(s+hi)])
        if j%512==0:save(OUT/'progress.json',{'state':'RUNNING','flow':label,'completed_cells':j+1,'total_cells':n,'elapsed_seconds':time.monotonic()-start})
        need(time.monotonic()-start<900,'TIMEOUT')
    need(event is not None,'EVENT_EMPTY');last=dlo
    for lo,hi in cover:need(fmpq(lo)==last,'EVENT_GAP');last=fmpq(hi)
    need(last==dhi,'EVENT_END')
    rr=residuals(event,p);jd=jacD(event,p,k);record={'A':pack(A),'D':pack(D),'q':pack(p['q']),'k':pack(k.v),'residual':[pack(v.v) for v in rr],'J_A':[pack(v.d) for v in rr],'J_D':[pack(v) for v in jd],'profile':{key:pack(v) for key,v in profile.items()},'endpoint':[pack(v) for v in event[:5]],'event_cover':cover,'cells':n,'elapsed_seconds':time.monotonic()-start,'source':source}
    save(OUT/f'{label}.json',record);return rr,jd,k,profile,event
def controls():
    p={'m2':exact('41/100'),'q':exact(2),'gamma':exact(20),'v0':exact('1/10'),'lambda_a':exact(6),'v1':exact('9/100'),'lambda_b':exact(-6)}
    P=Dual(2,1);v=potential(P,p);need((v.d-slope(P.v,p)).contains(0) and v.d.contains(exact('841/50')),'DUAL_POTENTIAL_DERIVATIVE')
    y,k=initial(exact('1/10'),p);R=rhs(y,p,k);c=coefficients(y,1,p,k)
    need(all((cc[1]-r).contains(0) for cc,r in zip(c,R)),'FIRST_COEFFICIENT')
    return {'potential_derivative':True,'first_taylor_coefficient':True}
def main():
    if '--controls' in sys.argv:print(controls());return
    need(not (OUT/'RESULT.json').exists() and not (OUT/'FAILURE.json').exists(),'NO_RETRY')
    checks=controls();binding=json.loads((ROOT/'inputs/central_bindings.json').read_text());p={key:exact(v) for key,v in binding['model_exact'].items()};p['q']=interval(fmpq(3999999,1000000),fmpq(4000001,1000000))
    x=[Q('0.09892438157982089'),Q('1.9756909300322794')];r=[Q('1e-10'),Q('1e-5')];X=[interval(a-b,a+b) for a,b in zip(x,r)]
    rr,jd,k,profile,end=flow(X[0],X[1],p,'box')
    F0,_,_,_,_=flow(exact(x[0]),exact(x[1]),p,'center')
    J=[[rr[i].d,jd[i]] for i in range(2)]
    jm=[[sum(Q(str(v)) for v in bounds(a))/2 for a in row] for row in J];det=jm[0][0]*jm[1][1]-jm[0][1]*jm[1][0];need(det!=0,'MID_J_SINGULAR')
    R=[[jm[1][1]/det,-jm[0][1]/det],[-jm[1][0]/det,jm[0][0]/det]]
    M=[[exact(int(i==j))-sum((exact(R[i][l])*J[l][j] for l in range(2)),arb(0)) for j in range(2)] for i in range(2)]
    corr=[-sum((exact(R[i][l])*F0[l].v for l in range(2)),arb(0)) for i in range(2)]
    image=[exact(x[i])+corr[i]+sum((M[i][j]*interval(-r[j],r[j]) for j in range(2)),arb(0)) for i in range(2)]
    norms=[sum((abs(M[i][j])*exact(r[j]/r[i]) for j in range(2)),arb(0)) for i in range(2)]
    inclusion=[inside(a,b) for a,b in zip(image,X)];contract=all(v.upper()<1 for v in norms)
    y0,_=initial(X[0],p);Ta=y0[3];Tpa=slope(y0[2],p)-4*y0[1]*Ta;Tb=end[3];Tpb=slope(end[2],p)-4*end[1]*Tb
    Ba=p['gamma']*Ta/2-Tpa;beta=-p['gamma']*Tb/2-Tpb
    predicates={'positive_curvature':k.v.lower()>0,'positive_scalar':profile['P'].lower()>0,'positive_Tprime':profile['Tp'].lower()>0,'opposite_endpoint_T':Ta.upper()<0<Tb.lower(),'negative_Ba':Ba.upper()<0,'negative_beta_b':beta.upper()<0,'convex_potential':p['m2'].lower()>0 and p['q'].lower()>0}
    result={'status':'COMPLETE_PENDING_INDEPENDENT_REVIEW','parameter_q':pack(p['q']),'center':list(map(str,x)),'radii':list(map(str,r)),'Krawczyk_image':[pack(v) for v in image],'weighted_contraction_rows':[pack(v) for v in norms],'strict_inclusion':inclusion,'contraction_pass':contract,'background_predicates':{k:bool(v) for k,v in predicates.items()},'controls':checks,'certified_family_candidate':all(inclusion) and contract and all(predicates.values()),'scope':'Uniform local exact background family; no global first-event uniqueness or complete tachyon count at q4.'}
    save(OUT/'RESULT.json',result);save(OUT/'progress.json',{'state':'COMPLETE_PENDING_AUDIT'});print(json.dumps(result,indent=2))
if __name__=='__main__':
    try:main()
    except BaseException as e:save(OUT/'FAILURE.json',{'status':'TECHNICAL_INCOMPLETE','error':repr(e),'traceback':traceback.format_exc()});raise
