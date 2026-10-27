"""Ordinary degree-six series over a commutative exact coefficient algebra."""
from fractions import Fraction as Q
def div(a,n):return Q(a,n) if isinstance(a,int) else a/n
class S:
 def __init__(self,a):self.a=tuple((list(a)+[0]*7)[:7])
 @staticmethod
 def cast(a):return a if isinstance(a,S) else S([a])
 def __add__(self,a):return S([x+y for x,y in zip(self.a,self.cast(a).a)])
 __radd__=__add__
 def __neg__(self):return S([-x for x in self.a])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):
  b=self.cast(a).a;return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(7)])
 __rmul__=__mul__
 def __truediv__(self,n):return S([div(x,n) for x in self.a])
 def dt(self,r):return S([n*r*x for n,x in enumerate(self.a)])
 def expzero(self):
  out=[1]
  for n in range(1,7):out.append(div(sum((j*self.a[j]*out[n-j] for j in range(1,n+1)),0),n))
  return S(out)

BASE=('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')
OLD4=('p4','f4','g4','chi4','xi4','c4')
OLD5=('p5','f5','g5','chi5','xi5','c5')
EXTRA5=('u1prime','g1second','u3','g3prime','c3prime')
EXTRA6=('u4','g4prime','c4prime','u2prime','g2second','c2second','Hpp','Tppp')
NEW=('p6','f6','g6','chi6','xi6','c6')

def direct(w,sigma,boost=True):
 E,h,r,H,Hp,T,Tp,Tpp=[w[k] for k in ('E','h','rate','H','Hp','T','Tp','Tpp')]
 shift=S([0,0]+[w.get('xi'+str(n),0) for n in range(2,7)]);St=shift.dt(r);shift2=shift*shift;shift3=shift2*shift
 def pull(vals,first=None,second=None,fixed=False):
  first=first or {};second=second or {};out=S([0])
  for n,value in vals.items():out+=S([0]*n+[n*r*value if fixed else value])
  for n,value in first.items():out+=S([0]*n+[n*r*value if fixed else value])*shift
  for n,value in second.items():out+=S([0]*n+[n*r*value if fixed else value])*shift2/2
  return out
 ps={n:w.get('p'+str(n),0) for n in range(1,7)};fs={n:w.get('f'+str(n),0) for n in range(1,7)};gs={n:w.get('g'+str(n),0) for n in range(1,7)}
 bs={n:(w.get('c'+str(n),0) if n>=2 else 0)-2*ps[n] for n in range(1,7)}
 up={n:w['u'+str(n)] for n in range(1,5)};upp={1:w['u1prime'],2:w['u2prime']}
 bp={n:(w['c'+str(n)+'prime'] if n>=2 else 0)-2*up[n] for n in range(1,5)};bpp={1:-2*w['u1prime'],2:w['c2second']-2*w['u2prime']}
 gp={1:w['g1prime'],2:w['g2prime'],3:w['g3prime'],4:w['g4prime']};gpp={1:w['g1second'],2:w['g2second']}
 loga=shift*H+shift2*Hp/2+shift3*w['Hpp']/6
 pwall=pull(ps,up,upp);bwall=pull(bs,bp,bpp);invN=(-loga-pwall).expzero()*E;v=bwall.expzero()*invN*St
 v2=v*v;inverseboost2=S([1])+v2;inverseboost=S([1])+v2/2 if boost else S([1])
 Hwall=S([H])+shift*Hp+shift2*w['Hpp']/2;Twall=S([T])+shift*Tp+shift2*Tpp/2+shift3*w['Tppp']/6
 deltaPhi=shift*T+shift2*Tp/2+shift3*Tpp/6+pull(fs,{n:gs[n] for n in range(1,5)},{1:w['g1prime'],2:w['g2prime']})
 radial=pull(gs,gp,gpp);fixedf=pull(fs,{n:gs[n] for n in range(1,5)},{1:w['g1prime'],2:w['g2prime']},True);fixedp=pull(ps,up,upp,True);fixedb=pull(bs,bp,bpp,True)
 oscillator=S([0]+[w.get('chi'+str(n),0) for n in range(1,7)]);chid=oscillator.dt(r)
 friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)+v*v.dt(r)*inverseboost2
 O=invN*invN*inverseboost2*(chid.dt(r)+friction*chid)+2*oscillator-deltaPhi
 normal=((-bwall).expzero()*(Twall+radial)+v*invN*fixedf)*inverseboost
 J=normal-(S([2*sigma*T])+21*deltaPhi-oscillator)*sigma/2
 geometric=sigma*invN*inverseboost*(v.dt(r)*inverseboost2+v*(fixedb-h-fixedp));kinetic=-invN*invN*inverseboost2*chid*chid/2
 return dict(O=O,J=J,graph=geometric+kinetic,geometric=geometric,kinetic=kinetic,pwall=pwall,bwall=bwall,deltaPhi=deltaPhi,normal=normal,v=v)

def qualify(ring,old):
 names=BASE+OLD4+EXTRA5+OLD5+EXTRA6+NEW;ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);w={k:ring.variable(j) for j,k in enumerate(names)};checks=[];records={}
 def eq(a,b,label):
  assert (ring.P.cast(a)-b).iszero(),label;checks.append(label)
 E,r,h,T,Tp=[w[k] for k in ('E','rate','h','T','Tp')]
 for sigma in (-1,1):
  full=direct(w,sigma);trunc=direct(dict(w,**{k:0 for k in NEW}),sigma);previous=old.direct(w,sigma)
  for key in ('O','J','graph','pwall','bwall','deltaPhi','normal','v'):
   for n in range(6):eq(full[key].a[n],previous[key].a[n],f'FIFTH_REPLAY:{sigma}:{key}:{n}')
  d=2+6*r*(6*r+3*h)*E*E;dg=6*sigma*E*E*r*(6*r-h);o,j,qi=[trunc[k].a[6] for k in ('O','J','graph')]
  p6,f6,g6,chi6,x6,c6=[w[k] for k in NEW]
  eq(full['O'].a[6],d*chi6-f6-T*x6+o,f'NEW_OSCILLATOR:{sigma}')
  eq(full['J'].a[6],g6+Tp*x6-T*c6+2*T*p6-sigma*(21*(f6+T*x6)-chi6)/2+j,f'NEW_SCALAR:{sigma}')
  eq(full['graph'].a[6],dg*x6+qi,f'NEW_GRAPH:{sigma}')
  load=2*sigma*d*(T*c6-Tp*x6-j)+(21*d-1)*T*x6+o;robin=2*sigma*d*(g6+2*T*p6)-(21*d-1)*f6-load
  eq(2*sigma*d*full['J'].a[6]-full['O'].a[6],robin,f'ELIMINATED_ROBIN:{sigma}')
  for key in NEW:
   for label,src in [('O',o),('J',j),('I',qi)]:eq(src.derivative(names.index(key)),0,f'LOWER_ONLY:{sigma}:{label}:{key}')
  removed=direct(w,sigma,False);p,P,x,x3,x4,c=[w[k] for k in ('p1','p2','xi2','xi3','xi4','c2')]
  v2=2*r*E*x;v3=r*E*(3*x3-6*p*x);v4=r*E*(4*x4-9*p*x3+2*x*(c-3*P-w['H']*x+9*p*p/2))
  a1=w['g1']+2*T*p;a2=w['g2']+Tp*x+2*p*w['g1']+(2*P-c+2*p*p)*T
  correction=T*(v2*v4+v3*v3/2)+a1*v2*v3+a2*v2*v2/2
  eq(full['J'].a[6]-removed['J'].a[6],correction,f'BOOST_CORRECTION:{sigma}');assert not correction.iszero();checks.append(f'BOOST_OMISSION_DETECTED:{sigma}')
  records[str(sigma)]={k:v.pack() for k,v in dict(o6=o,j6=j,qI6=qi,graph_divisor=dg,d6=d,robin_load_times_d=load).items()}
 return dict(pass_status=True,classification='SIXTH_WALL_IDENTITIES_QUALIFIED',checks=checks,variables=names,orientations=records,scope='Sixth moving-wall algebra only. New spatial derivatives remain independent jets until separately enclosed; no sixth solution, bound or amplitude gain.')
