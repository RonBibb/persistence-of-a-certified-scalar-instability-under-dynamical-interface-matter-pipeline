"""Ordinary degree-seven series over a commutative exact coefficient algebra."""
from fractions import Fraction as Q
def div(a,n):return Q(a,n) if isinstance(a,int) else a/n
class S:
 def __init__(self,a):self.a=tuple((list(a)+[0]*8)[:8])
 @staticmethod
 def cast(a):return a if isinstance(a,S) else S([a])
 def __add__(self,a):return S([x+y for x,y in zip(self.a,self.cast(a).a)])
 __radd__=__add__
 def __neg__(self):return S([-x for x in self.a])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):
  b=self.cast(a).a;return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(8)])
 __rmul__=__mul__
 def __truediv__(self,n):return S([div(x,n) for x in self.a])
 def dt(self,r):return S([n*r*x for n,x in enumerate(self.a)])
 def expzero(self):
  out=[1]
  for n in range(1,8):out.append(div(sum((j*self.a[j]*out[n-j] for j in range(1,n+1)),0),n))
  return S(out)

BASE=('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')
OLD4=('p4','f4','g4','chi4','xi4','c4')
OLD5=('p5','f5','g5','chi5','xi5','c5')
EXTRA5=('u1prime','g1second','u3','g3prime','c3prime')
EXTRA6=('u4','g4prime','c4prime','u2prime','g2second','c2second','Hpp','Tppp')
OLD6=('p6','f6','g6','chi6','xi6','c6')
EXTRA7=('u5','g5prime','c5prime','u3prime','g3second','c3second','u1second','g1third')
NEW=('p7','f7','g7','chi7','xi7','c7')

def direct(w,sigma,boost=True):
 E,h,r,H,Hp,T,Tp,Tpp=[w[k] for k in ('E','h','rate','H','Hp','T','Tp','Tpp')]
 shift=S([0,0]+[w.get('xi'+str(n),0) for n in range(2,8)]);St=shift.dt(r);shift2=shift*shift;shift3=shift2*shift
 def pull(vals,first=None,second=None,fixed=False,third=None):
  first=first or {};second=second or {};third=third or {};out=S([0])
  for n,value in vals.items():out+=S([0]*n+[n*r*value if fixed else value])
  for n,value in first.items():out+=S([0]*n+[n*r*value if fixed else value])*shift
  for n,value in second.items():out+=S([0]*n+[n*r*value if fixed else value])*shift2/2
  for n,value in third.items():out+=S([0]*n+[n*r*value if fixed else value])*shift3/6
  return out
 ps={n:w.get('p'+str(n),0) for n in range(1,8)};fs={n:w.get('f'+str(n),0) for n in range(1,8)};gs={n:w.get('g'+str(n),0) for n in range(1,8)}
 bs={n:(w.get('c'+str(n),0) if n>=2 else 0)-2*ps[n] for n in range(1,8)}
 up={n:w['u'+str(n)] for n in range(1,6)};upp={1:w['u1prime'],2:w['u2prime'],3:w['u3prime']}
 bp={n:(w['c'+str(n)+'prime'] if n>=2 else 0)-2*up[n] for n in range(1,6)};bpp={1:-2*w['u1prime'],2:w['c2second']-2*w['u2prime'],3:w['c3second']-2*w['u3prime']}
 gp={1:w['g1prime'],2:w['g2prime'],3:w['g3prime'],4:w['g4prime'],5:w['g5prime']};gpp={1:w['g1second'],2:w['g2second'],3:w['g3second']}
 loga=shift*H+shift2*Hp/2+shift3*w['Hpp']/6
 pwall=pull(ps,up,upp,third={1:w['u1second']});bwall=pull(bs,bp,bpp,third={1:-2*w['u1second']});invN=(-loga-pwall).expzero()*E;v=bwall.expzero()*invN*St
 v2=v*v;inverseboost2=S([1])+v2;inverseboost=S([1])+v2/2 if boost else S([1])
 Hwall=S([H])+shift*Hp+shift2*w['Hpp']/2;Twall=S([T])+shift*Tp+shift2*Tpp/2+shift3*w['Tppp']/6
 deltaPhi=shift*T+shift2*Tp/2+shift3*Tpp/6+pull(fs,{n:gs[n] for n in range(1,6)},{1:w['g1prime'],2:w['g2prime'],3:w['g3prime']},third={1:w['g1second']})
 radial=pull(gs,gp,gpp,third={1:w['g1third']});fixedf=pull(fs,{n:gs[n] for n in range(1,6)},{1:w['g1prime'],2:w['g2prime'],3:w['g3prime']},True,{1:w['g1second']});fixedp=pull(ps,up,upp,True,{1:w['u1second']});fixedb=pull(bs,bp,bpp,True,{1:-2*w['u1second']})
 oscillator=S([0]+[w.get('chi'+str(n),0) for n in range(1,8)]);chid=oscillator.dt(r)
 friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)+v*v.dt(r)*inverseboost2
 O=invN*invN*inverseboost2*(chid.dt(r)+friction*chid)+2*oscillator-deltaPhi
 normal=((-bwall).expzero()*(Twall+radial)+v*invN*fixedf)*inverseboost
 J=normal-(S([2*sigma*T])+21*deltaPhi-oscillator)*sigma/2
 geometric=sigma*invN*inverseboost*(v.dt(r)*inverseboost2+v*(fixedb-h-fixedp));kinetic=-invN*invN*inverseboost2*chid*chid/2
 return dict(O=O,J=J,graph=geometric+kinetic,geometric=geometric,kinetic=kinetic,pwall=pwall,bwall=bwall,deltaPhi=deltaPhi,normal=normal,v=v)

def qualify(ring,old):
 names=BASE+OLD4+EXTRA5+OLD5+EXTRA6+OLD6+EXTRA7+NEW;ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);w={k:ring.variable(j) for j,k in enumerate(names)};checks=[];records={}
 def eq(a,b,label):
  assert (ring.P.cast(a)-b).iszero(),label;checks.append(label)
 E,r,h,T,Tp=[w[k] for k in ('E','rate','h','T','Tp')]
 for sigma in (-1,1):
  full=direct(w,sigma);trunc=direct(dict(w,**{k:0 for k in NEW}),sigma);previous=old.direct(w,sigma)
  for key in ('O','J','graph','pwall','bwall','deltaPhi','normal','v'):
   for n in range(7):eq(full[key].a[n],previous[key].a[n],f'SIXTH_REPLAY:{sigma}:{key}:{n}')
  d=2+7*r*(7*r+3*h)*E*E;dg=7*sigma*E*E*r*(7*r-h);o,j,qi=[trunc[k].a[7] for k in ('O','J','graph')]
  p7,f7,g7,chi7,x7,c7=[w[k] for k in NEW]
  eq(full['O'].a[7],d*chi7-f7-T*x7+o,f'NEW_OSCILLATOR:{sigma}')
  eq(full['J'].a[7],g7+Tp*x7-T*c7+2*T*p7-sigma*(21*(f7+T*x7)-chi7)/2+j,f'NEW_SCALAR:{sigma}')
  eq(full['graph'].a[7],dg*x7+qi,f'NEW_GRAPH:{sigma}')
  load=2*sigma*d*(T*c7-Tp*x7-j)+(21*d-1)*T*x7+o;robin=2*sigma*d*(g7+2*T*p7)-(21*d-1)*f7-load
  eq(2*sigma*d*full['J'].a[7]-full['O'].a[7],robin,f'ELIMINATED_ROBIN:{sigma}')
  for key in NEW:
   for label,src in [('O',o),('J',j),('I',qi)]:eq(src.derivative(names.index(key)),0,f'LOWER_ONLY:{sigma}:{label}:{key}')
  removed=direct(w,sigma,False);p,P,x,x3,x4,c=[w[k] for k in ('p1','p2','xi2','xi3','xi4','c2')]
  v2=2*r*E*x;v3=r*E*(3*x3-6*p*x);v4=r*E*(4*x4-9*p*x3+2*x*(c-3*P-w['H']*x+9*p*p/2))
  a1=w['g1']+2*T*p;a2=w['g2']+Tp*x+2*p*w['g1']+(2*P-c+2*p*p)*T
  W1=-3*p;W2=c-3*P-w['H']*x;W3=w['c3']-3*w['p3']-3*w['u1']*x-w['H']*x3
  v5=r*E*(5*w['xi5']+4*x4*W1+3*x3*(W2+W1*W1/2)+2*x*(W3+W1*W2+W1*W1*W1/6))
  a3=w['g3']+Tp*x3+w['g1prime']*x+2*p*(w['g2']+Tp*x)+(2*P-c+2*p*p)*w['g1']+(2*w['p3']+2*w['u1']*x-w['c3']+2*p*(2*P-c)+4*p*p*p/3)*T+2*r*r*E*E*x*w['f1']
  correction=T*(v2*v5+v3*v4)+a1*(v2*v4+v3*v3/2)+a2*v2*v3+a3*v2*v2/2
  eq(full['J'].a[7]-removed['J'].a[7],correction,f'BOOST_CORRECTION:{sigma}');assert not correction.iszero();checks.append(f'BOOST_OMISSION_DETECTED:{sigma}')
  eq(full['pwall'].a[7].derivative(names.index('u1second')),x*x*x/6,f'THIRD_TAYLOR_P:{sigma}');eq(full['J'].a[7].derivative(names.index('g1third')),x*x*x/6,f'THIRD_TAYLOR_G:{sigma}')
  records[str(sigma)]={k:v.pack() for k,v in dict(o7=o,j7=j,qI7=qi,graph_divisor=dg,d7=d,robin_load_times_d=load).items()}
 return dict(pass_status=True,classification='SEVENTH_WALL_IDENTITIES_QUALIFIED',checks=checks,variables=names,orientations=records,scope='Seventh moving-wall algebra only. New spatial derivatives remain independent jets until separately enclosed; no seventh solution, bound or amplitude gain.')
