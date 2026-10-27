"""Positive all-order tail enclosure from finite fixed-point residual."""
from fractions import Fraction as Q
N=24
def need(v,n):
 if not v:raise AssertionError(n)
def setup(interval):
 global I
 I=interval
def upper(v):return max(Q(0),v.hi)
def poly(coeff,x):
 out=I(0)
 for n in range(len(coeff)-1,-1,-1):out=out*x+coeff[n]
 return out
def exponential(x):
 need(x.lo>=0 and x.hi<1,'EXP_DOMAIN')
 term=I(1);s=term
 for n in range(1,33):term=term*x/n;s=s+term
 rem=term*x/33/(1-x/34)
 return I.out(s.lo,(s+rem).hi)
def calculate(q,constants,data,weights):
 R,seed,K,Y,JC=[Q(constants[k]) for k in ('R','seed','K','Y','JC')];lam,kap=map(Q,weights)
 eta=R*q;t=I(eta);H=list(map(Q,data['H']));z=list(map(Q,data['majorant']));d=list(map(Q,data['distance']))
 need(len(H)==len(z)==len(d)==25 and H[0]==H[1]==z[0]==0 and z[1]==seed,'PREFIX_DOMAIN')
 need(all(v>=0 for row in (H,z,d) for v in row),'POSITIVE_COEFFICIENTS')
 need(all(H[n]<=(n-1)*K**(n-1) for n in range(2,25)),'UNIFORM_SOURCE_DOMINATION')
 def source(y):
  x=y*K
  return poly(H,y)+y*x**24*(24-23*x)/(1-x)**2
 def derivative(y):
  x=y*K
  return poly([n*H[n] for n in range(1,25)],y)+x**24*(I(600)/(1-x)+49*x/(1-x)**2+x*(1+x)/(1-x)**3)
 P=poly(z,t);ystar=2*seed*t;need(ystar.hi<=Y and K*ystar.hi<1 and P.hi<=ystar.lo,'MAJORANT_BALL')
 supres=ystar-seed*t-source(ystar);L=derivative(ystar);need(supres.lo>=0 and 0<=L.lo<=L.hi<1,'SUPER_SOLUTION_CONTRACTION')
 e=seed*t+source(P)-P;need(e.hi>=0,'RESIDUAL_UPPER');delta=I(e.hi)/(1-L.hi);need((P+delta).hi<=ystar.lo,'RESIDUAL_BALL')
 # Original degree24 envelopes, not smaller actual coefficients, are subtracted.
 b=[Q(0)]+[z[n]/n**2 for n in range(1,25)];x=[Q(0),Q(0)]+[2*lam*z[n]/n**3 for n in range(2,25)]
 B=poly(b,t)+delta/625;X=poly(x,t)+2*lam*delta/15625
 EB=poly([n*b[n] for n in range(25)],t)+delta/25;EX=poly([n*x[n] for n in range(25)],t)+2*lam*delta/625
 expB=exponential(B);full=3*(expB*(1+X)-1);efull=3*expB*(EB*(1+X)+EX)
 prefix=poly(d,t);eprefix=poly([n*d[n] for n in range(25)],t)
 need((full-prefix).hi>=0 and (efull-eprefix).hi>=0,'POSITIVE_TAIL_CONTAINMENT')
 dtail=upper(full-prefix);etail=upper(efull-eprefix)
 need(dtail>=0 and etail>=0,'TAIL_NONNEGATIVE')
 # Harmonic weights also pay scalar time derivatives from the same z-tail.
 scalar_tail=upper(kap*delta/15625);scalar_euler_tail=upper(kap*delta/625)
 return dict(q=str(q),eta=str(eta),values={k:v.pack() for k,v in dict(P=P,ystar=ystar,supersolution_residual=supres,L=L,residual=e,delta=delta,B=B,X=X,EulerB=EB,EulerX=EX,expB=expB,full_distance_majorant=full,full_euler_majorant=efull,distance_prefix=prefix,euler_prefix=eprefix).items()},bounds={k:str(v) for k,v in dict(distance_tail=dtail,euler_distance_tail=etail,scalar_tail=scalar_tail,scalar_euler_tail=scalar_euler_tail).items()},scope='Positive unresolved-series tail upper bounds only; no new actual coefficients or analytic radius.')
