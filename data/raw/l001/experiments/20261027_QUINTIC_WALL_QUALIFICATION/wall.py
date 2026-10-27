"""Ordinary degree-five neutral moving-wall identities; no solve at import."""
from fractions import Fraction as Q

def div(a,n):return Q(a,n) if isinstance(a,int) else a/n

class S:
 def __init__(self,a):self.a=tuple((list(a)+[0]*6)[:6])
 @staticmethod
 def cast(a):return a if isinstance(a,S) else S([a])
 def __add__(self,a):return S([x+y for x,y in zip(self.a,self.cast(a).a)])
 __radd__=__add__
 def __neg__(self):return S([-x for x in self.a])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):
  b=self.cast(a).a
  return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(6)])
 __rmul__=__mul__
 def __truediv__(self,n):return S([div(x,n) for x in self.a])
 def dt(self,r):return S([n*r*x for n,x in enumerate(self.a)])
 def expzero(self):
  out=[1]
  for n in range(1,6):out.append(div(sum((j*self.a[j]*out[n-j] for j in range(1,n+1)),0),n))
  return S(out)

FOUR=('p4','f4','g4','chi4','xi4','c4')
NEW=('p5','f5','g5','chi5','xi5','c5')
EXTRA=('u1prime','g1second','u3','g3prime','c3prime')

def direct(w,sigma,boost=True):
 E,h,r,H,Hp,T,Tp,Tpp,p,u,f,g,gp,P,U,F,G,Gp,c,cp,x,chi,chi2,p3,f3,g3,c3,x3,chi3=[w[k] for k in ('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')]
 p4,f4,g4,chi4,x4,c4=[w.get(k,0) for k in FOUR]
 p5,f5,g5,chi5,x5,c5=[w.get(k,0) for k in NEW]
 up,gpp,u3,g3p,c3p=[w[k] for k in EXTRA]
 shift=S([0,0,x,x3,x4,x5]);St=shift.dt(r)
 loga=shift*H+shift*shift*Hp/2
 pwall=S([0,p,P,p3+x*u,p4+x3*u+x*U,p5+x4*u+x3*U+x*u3+x*x*up/2])
 bwall=S([0,-2*p,c-2*P,c3-2*p3-2*x*u,c4-2*p4-2*x3*u+x*(cp-2*U),c5-2*p5-2*x4*u+x3*(cp-2*U)+x*(c3p-2*u3)-x*x*up])
 invN=(-loga-pwall).expzero()*E;v=bwall.expzero()*invN*St
 v2=v*v;inverseboost2=S([1])+v2;inverseboost=S([1])+v2/2 if boost else S([1])
 Hwall=S([H])+shift*Hp;Twall=S([T])+shift*Tp+shift*shift*Tpp/2
 deltaPhi=S([0,f,F+T*x,f3+T*x3+x*g,f4+T*x4+Tp*x*x/2+x3*g+x*G,f5+T*x5+Tp*x*x3+x4*g+x3*G+x*g3+x*x*gp/2])
 radial=S([0,g,G,g3+x*gp,g4+x3*gp+x*Gp,g5+x4*gp+x3*Gp+x*g3p+x*x*gpp/2])
 fixedf=S([0,r*f,2*r*F,3*r*f3+r*x*g,4*r*f4+r*x3*g+2*r*x*G,5*r*f5+r*x4*g+2*r*x3*G+3*r*x*g3+r*x*x*gp/2])
 fixedp=S([0,r*p,2*r*P,3*r*p3+r*x*u,4*r*p4+r*x3*u+2*r*x*U,5*r*p5+r*x4*u+2*r*x3*U+3*r*x*u3+r*x*x*up/2])
 fixedb=S([0,-2*r*p,2*r*(c-2*P),3*r*(c3-2*p3)-2*r*x*u,4*r*(c4-2*p4)-2*r*x3*u+2*r*x*(cp-2*U),5*r*(c5-2*p5)-2*r*x4*u+2*r*x3*(cp-2*U)+3*r*x*(c3p-2*u3)-r*x*x*up])
 oscillator=S([0,chi,chi2,chi3,chi4,chi5]);chid=oscillator.dt(r)
 friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)+v*v.dt(r)*inverseboost2
 O=invN*invN*inverseboost2*(chid.dt(r)+friction*chid)+2*oscillator-deltaPhi
 normal=((-bwall).expzero()*(Twall+radial)+v*invN*fixedf)*inverseboost
 J=normal-(S([2*sigma*T])+21*deltaPhi-oscillator)*sigma/2
 geometric=sigma*invN*inverseboost*(v.dt(r)*inverseboost2+v*(fixedb-h-fixedp))
 kinetic=-invN*invN*inverseboost2*chid*chid/2
 return dict(O=O,J=J,graph=geometric+kinetic,geometric=geometric,kinetic=kinetic,pwall=pwall,bwall=bwall,deltaPhi=deltaPhi,normal=normal,v=v)

def qualify(ring,old):
 names=('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')+FOUR+EXTRA+NEW
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
 w={k:ring.variable(j) for j,k in enumerate(names)};checks=[];records={}
 def eq(a,b,label):
  assert (ring.P.cast(a)-b).iszero(),label
  checks.append(label)
 E,r,h,T,Tp=[w[k] for k in ('E','rate','h','T','Tp')]
 for sigma in (-1,1):
  full=direct(w,sigma);trunc=direct(dict(w,**{k:0 for k in NEW}),sigma);previous=old.direct(w,sigma)
  for key in ('O','J','graph','pwall','bwall','deltaPhi','normal'):
   for n in range(5):eq(full[key].a[n],previous[key].a[n],f'QUARTIC_REPLAY:{sigma}:{key}:{n}')
  d=2+5*r*(5*r+3*h)*E*E;dg=5*sigma*E*E*r*(5*r-h)
  o,j,qi=[trunc[k].a[5] for k in ('O','J','graph')]
  p5,f5,g5,chi5,x5,c5=[w[k] for k in NEW]
  newO=d*chi5-f5-T*x5
  newJ=g5+Tp*x5-T*c5+2*T*p5-sigma*(21*(f5+T*x5)-chi5)/2
  eq(full['O'].a[5],newO+o,f'NEW_OSCILLATOR:{sigma}')
  eq(full['J'].a[5],newJ+j,f'NEW_SCALAR:{sigma}')
  eq(full['graph'].a[5],dg*x5+qi,f'NEW_GRAPH:{sigma}')
  load=2*sigma*d*(T*c5-Tp*x5-j)+(21*d-1)*T*x5+o
  robin=2*sigma*d*(g5+2*T*p5)-(21*d-1)*f5-load
  eq(2*sigma*d*full['J'].a[5]-full['O'].a[5],robin,f'ELIMINATED_ROBIN:{sigma}')
  for key in NEW:
   for label,src in [('O',o),('J',j),('I',qi)]:eq(src.derivative(names.index(key)),0,f'LOWER_ONLY:{sigma}:{label}:{key}')
  removed=direct(w,sigma,False)
  v2=2*r*E*w['xi2'];v3=r*E*(3*w['xi3']-6*w['p1']*w['xi2'])
  correction=T*v2*v3+(w['g1']+2*T*w['p1'])*v2*v2/2
  eq(full['J'].a[5]-removed['J'].a[5],correction,f'BOOST_CORRECTION:{sigma}')
  assert not correction.iszero();checks.append(f'BOOST_OMISSION_DETECTED:{sigma}')
  records[str(sigma)]={k:v.pack() for k,v in dict(o5=o,j5=j,qI5=qi,graph_divisor=dg,d5=d,robin_load_times_d=load).items()}
 return dict(pass_status=True,classification='QUINTIC_WALL_IDENTITIES_QUALIFIED',checks=checks,variables=names,orientations=records,scope='Exact fifth wall new-row, transport and boost identities only. No fifth-order solution, source bound, coefficient sign, or physical nonlinear trajectory.')

