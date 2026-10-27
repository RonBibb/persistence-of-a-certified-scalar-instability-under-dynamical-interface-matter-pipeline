"""Ordinary degree-eight series over a commutative exact coefficient algebra."""
from fractions import Fraction as Q
def div(a,n):return Q(a,n) if isinstance(a,int) else a/n
class S:
 def __init__(self,a):self.a=tuple((list(a)+[0]*9)[:9])
 @staticmethod
 def cast(a):return a if isinstance(a,S) else S([a])
 def __add__(self,a):return S([x+y for x,y in zip(self.a,self.cast(a).a)])
 __radd__=__add__
 def __neg__(self):return S([-x for x in self.a])
 def __sub__(self,a):return self+-self.cast(a)
 def __rsub__(self,a):return self.cast(a)+-self
 def __mul__(self,a):
  b=self.cast(a).a;return S([sum((self.a[j]*b[n-j] for j in range(n+1)),0) for n in range(9)])
 __rmul__=__mul__
 def __truediv__(self,n):return S([div(x,n) for x in self.a])
 def dt(self,r):return S([n*r*x for n,x in enumerate(self.a)])
 def expzero(self):
  out=[1]
  for n in range(1,9):out.append(div(sum((j*self.a[j]*out[n-j] for j in range(1,n+1)),0),n))
  return S(out)

BASE=('E','h','rate','H','Hp','T','Tp','Tpp','p1','u1','f1','g1','g1prime','p2','u2','f2','g2','g2prime','c2','c2prime','xi2','chi1','chi2','p3','f3','g3','c3','xi3','chi3')
OLD4=('p4','f4','g4','chi4','xi4','c4')
OLD5=('p5','f5','g5','chi5','xi5','c5')
EXTRA5=('u1prime','g1second','u3','g3prime','c3prime')
EXTRA6=('u4','g4prime','c4prime','u2prime','g2second','c2second','Hpp','Tppp')
OLD6=('p6','f6','g6','chi6','xi6','c6')
EXTRA7=('u5','g5prime','c5prime','u3prime','g3second','c3second','u1second','g1third')
OLD7=('p7','f7','g7','chi7','xi7','c7')
EXTRA8=('u6','g6prime','c6prime','u4prime','g4second','c4second','u2second','g2third','c2third','Hppp','Tpppp')
NEW=('p8','f8','g8','chi8','xi8','c8')

def direct(w,sigma,boost=True,quarticboost=True):
 E,h,r,H,Hp,T,Tp,Tpp=[w[k] for k in ('E','h','rate','H','Hp','T','Tp','Tpp')]
 shift=S([0,0]+[w.get('xi'+str(n),0) for n in range(2,9)]);St=shift.dt(r);shift2=shift*shift;shift3=shift2*shift;shift4=shift2*shift2
 def pull(vals,first=None,second=None,fixed=False,third=None):
  first=first or {};second=second or {};third=third or {};out=S([0])
  for n,value in vals.items():out+=S([0]*n+[n*r*value if fixed else value])
  for n,value in first.items():out+=S([0]*n+[n*r*value if fixed else value])*shift
  for n,value in second.items():out+=S([0]*n+[n*r*value if fixed else value])*shift2/2
  for n,value in third.items():out+=S([0]*n+[n*r*value if fixed else value])*shift3/6
  return out
 ps={n:w.get('p'+str(n),0) for n in range(1,9)};fs={n:w.get('f'+str(n),0) for n in range(1,9)};gs={n:w.get('g'+str(n),0) for n in range(1,9)}
 bs={n:(w.get('c'+str(n),0) if n>=2 else 0)-2*ps[n] for n in range(1,9)}
 up={n:w['u'+str(n)] for n in range(1,7)};upp={1:w['u1prime'],2:w['u2prime'],3:w['u3prime'],4:w['u4prime']}
 bp={n:(w['c'+str(n)+'prime'] if n>=2 else 0)-2*up[n] for n in range(1,7)};bpp={1:-2*w['u1prime'],2:w['c2second']-2*w['u2prime'],3:w['c3second']-2*w['u3prime'],4:w['c4second']-2*w['u4prime']}
 gp={1:w['g1prime'],2:w['g2prime'],3:w['g3prime'],4:w['g4prime'],5:w['g5prime'],6:w['g6prime']};gpp={1:w['g1second'],2:w['g2second'],3:w['g3second'],4:w['g4second']}
 loga=shift*H+shift2*Hp/2+shift3*w['Hpp']/6+shift4*w['Hppp']/24
 pwall=pull(ps,up,upp,third={1:w['u1second'],2:w['u2second']});bwall=pull(bs,bp,bpp,third={1:-2*w['u1second'],2:w['c2third']-2*w['u2second']});invN=(-loga-pwall).expzero()*E;v=bwall.expzero()*invN*St
 v2=v*v;v4=v2*v2;inverseboost2=S([1])+v2+(v4 if quarticboost else S([0]));inverseboost=(S([1])+v2/2+(3*v4/8 if quarticboost else S([0]))) if boost else S([1])
 Hwall=S([H])+shift*Hp+shift2*w['Hpp']/2+shift3*w['Hppp']/6;Twall=S([T])+shift*Tp+shift2*Tpp/2+shift3*w['Tppp']/6+shift4*w['Tpppp']/24
 deltaPhi=shift*T+shift2*Tp/2+shift3*Tpp/6+shift4*w['Tppp']/24+pull(fs,{n:gs[n] for n in range(1,7)},{1:w['g1prime'],2:w['g2prime'],3:w['g3prime'],4:w['g4prime']},third={1:w['g1second'],2:w['g2second']})
 radial=pull(gs,gp,gpp,third={1:w['g1third'],2:w['g2third']});fixedf=pull(fs,{n:gs[n] for n in range(1,7)},{1:w['g1prime'],2:w['g2prime'],3:w['g3prime'],4:w['g4prime']},True,{1:w['g1second'],2:w['g2second']});fixedp=pull(ps,up,upp,True,{1:w['u1second'],2:w['u2second']});fixedb=pull(bs,bp,bpp,True,{1:-2*w['u1second'],2:w['c2third']-2*w['u2second']})
 oscillator=S([0]+[w.get('chi'+str(n),0) for n in range(1,9)]);chid=oscillator.dt(r)
 friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)+v*v.dt(r)*inverseboost2
 O=invN*invN*inverseboost2*(chid.dt(r)+friction*chid)+2*oscillator-deltaPhi
 normal=((-bwall).expzero()*(Twall+radial)+v*invN*fixedf)*inverseboost
 J=normal-(S([2*sigma*T])+21*deltaPhi-oscillator)*sigma/2
 geometric=sigma*invN*inverseboost*(v.dt(r)*inverseboost2+v*(fixedb-h-fixedp));kinetic=-invN*invN*inverseboost2*chid*chid/2
 return dict(O=O,J=J,graph=geometric+kinetic,geometric=geometric,kinetic=kinetic,pwall=pwall,bwall=bwall,deltaPhi=deltaPhi,normal=normal,v=v)

def qualify(ring,old):
 names=BASE+OLD4+EXTRA5+OLD5+EXTRA6+OLD6+EXTRA7+OLD7+EXTRA8+NEW
 assert len(names)==len(set(names)),'UNIQUE_VARIABLES'
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);w={k:ring.variable(j) for j,k in enumerate(names)};checks=[];records={}
 def eq(a,b,label):
  assert (ring.P.cast(a)-b).iszero(),label;checks.append(label)
 E,r,h,T,Tp=[w[k] for k in ('E','rate','h','T','Tp')]
 for sigma in (-1,1):
  full=direct(w,sigma);trunc=direct(dict(w,**{k:0 for k in NEW}),sigma);previous=old.direct(w,sigma)
  for key in ('O','J','graph','pwall','bwall','deltaPhi','normal','v'):
   for n in range(8):eq(full[key].a[n],previous[key].a[n],f'SEVENTH_REPLAY:{sigma}:{key}:{n}')
  d=2+8*r*(8*r+3*h)*E*E;dg=8*sigma*E*E*r*(8*r-h);o,j,qi=[trunc[k].a[8] for k in ('O','J','graph')]
  p8,f8,g8,chi8,x8,c8=[w[k] for k in NEW]
  eq(full['O'].a[8],d*chi8-f8-T*x8+o,f'NEW_OSCILLATOR:{sigma}')
  eq(full['J'].a[8],g8+Tp*x8-T*c8+2*T*p8-sigma*(21*(f8+T*x8)-chi8)/2+j,f'NEW_SCALAR:{sigma}')
  eq(full['graph'].a[8],dg*x8+qi,f'NEW_GRAPH:{sigma}')
  load=2*sigma*d*(T*c8-Tp*x8-j)+(21*d-1)*T*x8+o;robin=2*sigma*d*(g8+2*T*p8)-(21*d-1)*f8-load
  eq(2*sigma*d*full['J'].a[8]-full['O'].a[8],robin,f'ELIMINATED_ROBIN:{sigma}')
  for key in NEW:
   for label,src in [('O',o),('J',j),('I',qi)]:eq(src.derivative(names.index(key)),0,f'LOWER_ONLY:{sigma}:{label}:{key}')
  removed=direct(w,sigma,False);noquartic=direct(w,sigma,True,False);v=full['v'].a;A=removed['normal'].a
  correction=sum((A[8-k]*sum((v[jj]*v[k-jj] for jj in range(k+1)),0)/2 for k in range(4,9)),ring.P(0))+3*T*v[2]**4/8
  eq(full['J'].a[8]-removed['J'].a[8],correction,f'BOOST_CONVOLUTION:{sigma}')
  quartic=3*T*(2*r*E*w['xi2'])**4/8
  eq(full['J'].a[8]-noquartic['J'].a[8],quartic,f'QUARTIC_BOOST:{sigma}');assert not quartic.iszero();checks.append(f'QUARTIC_BOOST_OMISSION_DETECTED:{sigma}')
  x=w['xi2']
  for row,var,expected,label in [('pwall','u6',x,'FIRST_JET6'),('pwall','u4prime',x*x/2,'SECOND_JET4'),('pwall','u2second',x*x*x/6,'THIRD_JET2'),('bwall','c2third',x*x*x/6,'THIRD_TRACE2'),('J','g2third',x*x*x/6,'THIRD_RADIAL2'),('J','Tpppp',x**4/24,'FOURTH_BACKGROUND_NORMAL'),('deltaPhi','Tppp',x**4/24,'FOURTH_BACKGROUND_VALUE')]:
   eq(full[row].a[8].derivative(names.index(var)),expected,f'{label}:{sigma}')
  records[str(sigma)]={k:v.pack() for k,v in dict(o8=o,j8=j,qI8=qi,graph_divisor=dg,d8=d,robin_load_times_d=load).items()}
 return dict(pass_status=True,classification='EIGHTH_WALL_IDENTITIES_QUALIFIED',checks=checks,variables=names,orientations=records,scope='Eighth moving-wall algebra with quartic boost and fourth background shifts. Jets still independent until qualified/enclosed; no field or coefficient admission.')
