"""Ordinary degree-four neutral moving-wall identities; no solve at import."""
from fractions import Fraction as Q

def div(a,n):return Q(a,n) if isinstance(a,int) else a/n

class S:
 def __init__(self,a):self.a=tuple((list(a)+[0]*5)[:5])
 @staticmethod
 def cast(a):return a if isinstance(a,S) else S([a])
 def __add__(self,a):return S([x+y for x,y in zip(self.a,self.cast(a).a)])
 __radd__=__add__
 def __neg__(self):return S([-x for x in self.a])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):
  b=self.cast(a).a
  return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(5)])
 __rmul__=__mul__
 def __truediv__(self,n):return S([div(x,n) for x in self.a])
 def dt(self,r):return S([n*r*x for n,x in enumerate(self.a)])
 def expzero(self):
  out=[1]
  for n in range(1,5):out.append(div(sum((j*self.a[j]*out[n-j] for j in range(1,n+1)),0),n))
  return S(out)

NEW=('p4','f4','g4','chi4','xi4','c4')

def direct(w,sigma,boost=True):
 E,h,r,H,Hp,T,Tp,Tpp,p,u,f,g,gp,P,U,F,G,Gp,c,cp,x,chi,chi2,p3,f3,g3,c3,x3,chi3=[w[k] for k in ('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')]
 p4,f4,g4,chi4,x4,c4=[w.get(k,0) for k in NEW]
 shift=S([0,0,x,x3,x4]);St=shift.dt(r)
 loga=shift*H+shift*shift*Hp/2
 pwall=S([0,p,P,p3+x*u,p4+x3*u+x*U])
 bwall=S([0,-2*p,c-2*P,c3-2*p3-2*x*u,c4-2*p4-2*x3*u+x*(cp-2*U)])
 invN=(-loga-pwall).expzero()*E;v=bwall.expzero()*invN*St
 v2=v*v;inverseboost2=S([1])+v2;inverseboost=S([1])+v2/2 if boost else S([1])
 Hwall=S([H])+shift*Hp;Twall=S([T])+shift*Tp+shift*shift*Tpp/2
 deltaPhi=S([0,f,F+T*x,f3+T*x3+x*g,f4+T*x4+Tp*x*x/2+x3*g+x*G])
 radial=S([0,g,G,g3+x*gp,g4+x3*gp+x*Gp])
 fixedf=S([0,r*f,2*r*F,3*r*f3+r*x*g,4*r*f4+r*x3*g+2*r*x*G])
 fixedp=S([0,r*p,2*r*P,3*r*p3+r*x*u,4*r*p4+r*x3*u+2*r*x*U])
 fixedb=S([0,-2*r*p,2*r*(c-2*P),3*r*(c3-2*p3)-2*r*x*u,4*r*(c4-2*p4)-2*r*x3*u+2*r*x*(cp-2*U)])
 oscillator=S([0,chi,chi2,chi3,chi4]);chid=oscillator.dt(r)
 friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)+v*v.dt(r)*inverseboost2
 O=invN*invN*inverseboost2*(chid.dt(r)+friction*chid)+2*oscillator-deltaPhi
 normal=((-bwall).expzero()*(Twall+radial)+v*invN*fixedf)*inverseboost
 J=normal-(S([2*sigma*T])+21*deltaPhi-oscillator)*sigma/2
 geometric=sigma*invN*inverseboost*(v.dt(r)*inverseboost2+v*(fixedb-h-fixedp))
 kinetic=-invN*invN*inverseboost2*chid*chid/2
 return dict(O=O,J=J,graph=geometric+kinetic,geometric=geometric,kinetic=kinetic,pwall=pwall,bwall=bwall,deltaPhi=deltaPhi,normal=normal,v=v)

def qualify(ring,old):
 names=('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')+NEW
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
 w={k:ring.variable(j) for j,k in enumerate(names)};checks=[];records={}
 def eq(a,b,label):
  assert (ring.P.cast(a)-b).iszero(),label
  checks.append(label)
 E,r,h,T,Tp=[w[k] for k in ('E','rate','h','T','Tp')]
 for sigma in (-1,1):
  full=direct(w,sigma);trunc=direct(dict(w,**{k:0 for k in NEW}),sigma);previous=old.direct(w,sigma)
  for key in ('O','J','graph','pwall','bwall','deltaPhi','normal'):
   for n in range(4):eq(full[key].a[n],previous[key].a[n],f'CUBIC_REPLAY:{sigma}:{key}:{n}')
  d=2+4*r*(4*r+3*h)*E*E;dg=4*sigma*E*E*r*(4*r-h)
  o,j,qi=[trunc[k].a[4] for k in ('O','J','graph')]
  p4,f4,g4,chi4,x4,c4=[w[k] for k in NEW]
  newO=d*chi4-f4-T*x4
  newJ=g4+Tp*x4-T*c4+2*T*p4-sigma*(21*(f4+T*x4)-chi4)/2
  eq(full['O'].a[4],newO+o,f'NEW_OSCILLATOR:{sigma}')
  eq(full['J'].a[4],newJ+j,f'NEW_SCALAR:{sigma}')
  eq(full['graph'].a[4],dg*x4+qi,f'NEW_GRAPH:{sigma}')
  load=2*sigma*d*(T*c4-Tp*x4-j)+(21*d-1)*T*x4+o
  robin=2*sigma*d*(g4+2*T*p4)-(21*d-1)*f4-load
  eq(2*sigma*d*full['J'].a[4]-full['O'].a[4],robin,f'ELIMINATED_ROBIN:{sigma}')
  for key in NEW:
   for label,src in [('O',o),('J',j),('I',qi)]:eq(src.derivative(names.index(key)),0,f'LOWER_ONLY:{sigma}:{label}:{key}')
  removed=direct(w,sigma,False)
  correction=T*(2*r*E*w['xi2'])**2/2
  eq(full['J'].a[4]-removed['J'].a[4],correction,f'BOOST_CORRECTION:{sigma}')
  assert not correction.iszero();checks.append(f'BOOST_OMISSION_DETECTED:{sigma}')
  records[str(sigma)]={k:v.pack() for k,v in dict(o4=o,j4=j,qI4=qi,graph_divisor=dg,d4=d,robin_load_times_d=load).items()}
 # Independent closed trace row: b1=-2p1 and bj=cj-2pj.
 p,P,p3,f,F,f3,c,c3=[w[k] for k in ('p1','p2','p3','f1','f2','f3','c2','c3')]
 ps=S([0,p,P,p3]);bs=S([0,-2*p,c-2*P,c3-2*p3]);fs=S([0,f,F,f3])
 dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r)
 raw=(bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df
 qt=r*r*(36*p*p3+24*P*P+6*f*f3+4*F*F-18*p*c3-24*P*c+4*c*c)
 eq(raw.a[4],qt,'TRACE4_CLOSED')
 return dict(pass_status=True,classification='QUARTIC_WALL_AND_TRACE_IDENTITIES_QUALIFIED',checks=checks,variables=names,orientations=records,trace4=qt.pack(),scope='Exact wall new-row, transport, boost and trace identities only. No quartic solution, coefficient sign, or physical nonlinear trajectory.')
