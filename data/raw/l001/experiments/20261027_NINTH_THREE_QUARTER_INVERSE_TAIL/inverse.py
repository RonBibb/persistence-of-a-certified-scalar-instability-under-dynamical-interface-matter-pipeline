"""Positive pulled inverse-clock composition, unresolved tail only."""
from fractions import Fraction as Q
def setup(interval):
 global I
 I=interval
def need(v,n):
 if not v:raise AssertionError(n)
def poly(c,x):
 out=I(0)
 for v in reversed(c):out=out*x+v
 return out
def exp(x):
 need(0<=x.lo<=x.hi<1,'EXP_DOMAIN');s=term=I(1)
 for n in range(1,33):term=term*x/n;s=s+term
 return I.out(s.lo,(s+term*x/33/(1-x/34)).hi)
def calculate(q,constants,old,row):
 R=Q(constants['R']);JC=Q(constants['JC']);a=R*q
 need(Q(row['eta'])==a and Q(old['constants']['radius'])==R,'SAME_RADIUS_POINT')
 lam=Q(old['constants']['graph_weight']);gap=Q(old['constants']['gap']);need(lam>0 and gap>0 and old['constants']['rate_ceiling']=='1/32','PARAMETERS')
 series={k:list(map(Q,v)) for k,v in old['series'].items()}
 need(old['degree']==24 and all(len(v)==25 for v in series.values()),'PREFIX_LENGTH')
 need(all(v>=0 for c in series.values() for v in c),'POSITIVE_PREFIX')
 need(series['Jhat'][0]==1 and series['X'][0]==series['X'][1]==0,'CONSTANTS')
 delta=I(*row['values']['delta']['exact_bounds']);t=I(a)
 B=poly(series['B'],t)+delta/625
 X=poly(series['X'],t)+lam*delta/15625
 EX=poly([n*v for n,v in enumerate(series['X'])],t)+lam*delta/625
 U=4*X/gap;need(0<=U.lo<=U.hi<1,'BACKGROUND_DENOMINATOR')
 E=1+64*U/(1-U);eB=exp(B);e2B=exp(2*B);V=E*e2B*EX/32
 need(0<=V.lo<=V.hi<1,'VELOCITY_DENOMINATOR')
 J=E*eB/(1-V*V);prefix=poly(series['Jhat'],t);difference=J-prefix
 need(difference.hi>=0,'NONNEGATIVE_TAIL_UPPER')
 bound=max(Q(0),difference.hi);fallback=JC*q**25/(1-q);need(fallback>=0,'FALLBACK')
 return dict(q=str(q),eta=str(a),values={k:v.pack() for k,v in dict(B=B,X=X,EulerX=EX,U=U,Ehat=E,expB=eB,exp2B=e2B,Vhat=V,Jhat=J,prefix=prefix,difference=difference).items()},new_tail=str(bound),old_tail=str(fallback),selected_tail=str(min(bound,fallback)))
