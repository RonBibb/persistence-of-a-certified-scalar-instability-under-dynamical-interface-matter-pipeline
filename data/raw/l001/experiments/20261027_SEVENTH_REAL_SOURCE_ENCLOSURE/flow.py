"""Seventh actual-source enclosure; qualified polynomial jets, no ODE."""
from fractions import Fraction as Q
def need(v,n):
 if not v:raise AssertionError(n)
def setup(interval,cubic,quartic,wall,qualified,jets):
 global I,c3mod,c4mod,w7mod,qual,jetqual
 I,c3mod,c4mod,w7mod,qual,jetqual=interval,cubic,quartic,wall,qualified,jets
def iv(v):return I(*v['exact_bounds'])
def ab(v):return max(abs(v.lo),abs(v.hi))
def sq(v):return I.out(0 if v.lo<=0<=v.hi else min(v.lo*v.lo,v.hi*v.hi),max(v.lo*v.lo,v.hi*v.hi))
def polynomial(v,key,record=None):
 record=record or qual;out=I(0);names=record['variables'];rows=record['sources'][key]
 maxima=[max((row['powers'][i] for row in rows),default=0) for i in range(len(names))];powers=[[v[k]**j for j in range(m+1)] for k,m in zip(names,maxima)]
 for row in rows:
  term=I(Q(row['coefficient']))
  for i,n in enumerate(row['powers']):
   if n:term=term*powers[i][n]
  out=out+term
 return out
def sources34(v,p):
 args=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')]
 return c3mod.cubic(*args,p),c4mod.quartic(*args,v['p3'],v['f3'],v['g3'],p,c3mod)
def extend(old,constants,p):
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h'];need((7*r-h).lo>0,'TRACE7_DIVISOR')
 v.update(p6=I(-Q(constants['p6_bound']),Q(constants['p6_bound'])),f6=I(-Q(constants['f6_bound']),Q(constants['f6_bound'])),g6=I(-Q(constants['f6prime_bound']),Q(constants['f6prime_bound'])),N7=r/(7*(7*r-h)),p7=I(0),f7=I(0),g7=I(0))
 return v
def endpoint(sixth,p,side,sigma):
 old=sixth['walls'][side];w={k:iv(x) for k,x in old['inputs'].items()};v=extend(old['source_variables'],sixth['constants'],p);q={k:iv(x) for k,x in old['quantities'].items()}
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];r,h=p['rate'],p['h'];Tp=w['Tp']
 need(q['d6_wall'].lo>0,'SIXTH_WALL_DIVISOR')
 w.update(p6=v['p6'],f6=v['f6'],g6=v['g6'],c6=q['c6'],xi6=q['xi6'],chi6=(v['f6']+T*q['xi6']-q['o6'])/q['d6_wall'])
 jets={k:polynomial(v,k,jetqual) for k in ('u5','g5prime','c5prime','u3prime','g3second','c3second','u1second','g1third')};w.update(jets)
 full=w7mod.direct(w,sigma);o7,j7,qi7=[full[k].a[7] for k in ('O','J','graph')];div=7*sigma*e*r*(7*r-h);need(div.lo>0 or div.hi<0,'SEVENTH_GRAPH_DIVISOR');xi7=-qi7/div
 mu7=-7*r*(7*r+3*h);dwall=2-mu7*e;J=-3*(mu7+4*p['k'])*e;D=J+2*sq(T);need(dwall.lo>0 and J.lo>0 and D.lo>0,'SEVENTH_ENDPOINT_POSITIVITY')
 c7=polynomial(v,'c7');Sc7=polynomial(v,'Sc7');gamma=21-I(1)/dwall;R=2*sigma*(T*c7-Tp*xi7-j7)+gamma*T*xi7+o7/dwall;robin=-D*R/(2*J)+2*sigma*T*Sc7/J
 b1=-2*a;b2=w['c2']-2*P;b3=w['c3']-2*v['p3'];b4=w['c4']-2*v['p4'];b5=w['c5']-2*v['p5'];ex=w7mod.S([0,b1,b2,b3,b4,b5]).expzero()
 b1p=-2*w['u1'];b2p=w['c2prime']-2*w['u2'];b3p=w['c3prime']-2*w['u3'];E2p=b2p+b1*b1p;E3p=b3p+b1p*b2+b1*b2p+b1*b1*b1p/2
 x2,x3,x4=w['xi2'],w['xi3'],w['xi4']
 transport=xi7+w['xi6']*b1+w['xi5']*ex.a[2]+x4*ex.a[3]+x3*ex.a[4]+x2*ex.a[5]+x2*x2*E3p/2+x2*x3*E2p+(x2*x4+x3*x3/2)*b1p+x2*x2*x2*(-2*w['u1prime'])/6
 return dict(inputs={k:x.pack() for k,x in w.items()},source_variables={k:x.pack() for k,x in v.items()},jets={k:x.pack() for k,x in jets.items()},quantities={k:x.pack() for k,x in dict(xi7=xi7,robin=robin,transport=transport,c7=c7,Sc7=Sc7,D7=D,J7=J,d7_wall=dwall,graph_divisor=div,o7=o7,j7=j7,qI7=qi7,R7=R).items()})
def calculate(arm,sixth,globalrow,inverse):
 p={k:iv(x) for k,x in arm['parameters'].items()};v=extend(sixth['source_variables'],sixth['constants'],p);r,h,m=p['rate'],p['h'],p['m2']
 H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];mu7=-7*r*(7*r+3*h);J=-3*(mu7+4*p['k'])*e;D=J+2*sq(T);need(J.lo>0 and D.lo>0,'GLOBAL_SEVENTH_POSITIVITY')
 s={k:polynomial(v,k) for k in ('c7','Sp7','Sc7','Sg7')};B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;forcing=s['Sg7']+B*s['Sc7']/D
 walls={side:endpoint(sixth,p,side,sg) for side,sg in [('lower',1),('upper',-1)]};G=max(ab(iv(w['quantities']['robin'])) for w in walls.values())
 cf=Q(inverse['finite_orders']['7']['constant'])*Q(inverse['f_transfer_multiplier']);need(cf>0,'FINITE7_INVERSE');size=ab(forcing)+7*G;fb=cf*size/49;gb=cf*size/7;pb=(ab(s['Sc7'])+ab(T)*gb+ab(Tp)*fb)/D.lo
 s3,s4=sources34(v,p);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f']);c5=iv(globalrow['sources']['c5']);c6=iv(sixth['sources']['c6'])
 bs=[0,-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],c5-2*v['p5'],c6-2*v['p6'],s['c7']];density=w7mod.S(bs).expzero().a[7];length=I(*arm['D']);need(length.lo>0,'DOMAIN')
 integral=density*length;known=iv(walls['upper']['quantities']['transport'])-iv(walls['lower']['quantities']['transport'])+integral;metric=2*length.hi*pb;d7=known+I(-metric,metric)
 return dict(walls=walls,source_variables={k:x.pack() for k,x in v.items()},sources={k:x.pack() for k,x in s.items()},bulk={k:x.pack() for k,x in dict(J7=J,D7=D,Tp=Tp,B0=B,forcing=forcing,density=density,integral=integral,known=known,d7=d7).items()},constants={k:str(x) for k,x in dict(Cf7=cf,Robin_abs=G,source_size=size,f7_bound=fb,f7prime_bound=gb,p7_bound=pb,metric_integral_bound=metric).items()},scope='Unsigned actual seventh coefficient enclosure; no seventh profile, sign, trajectory or full-clock claim.')
