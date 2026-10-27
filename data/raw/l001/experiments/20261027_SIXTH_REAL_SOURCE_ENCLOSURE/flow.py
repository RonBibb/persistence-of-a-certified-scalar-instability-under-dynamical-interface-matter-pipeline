"""Sixth actual-source bounds from archived lower fields; no ODE."""
from fractions import Fraction as Q
def need(v,n):
 if not v:raise AssertionError(n)
def setup(interval,cubic,quartic,wall,qualified):
 global I,c3mod,c4mod,w6mod,qual
 I,c3mod,c4mod,w6mod,qual=interval,cubic,quartic,wall,qualified
def iv(v):return I(*v['exact_bounds'])
def ab(v):return max(abs(v.lo),abs(v.hi))
def sq(v):return I.out(0 if v.lo<=0<=v.hi else min(v.lo*v.lo,v.hi*v.hi),max(v.lo*v.lo,v.hi*v.hi))
def polynomial(v,key):
 out=I(0);names=qual['variables'];rows=qual['sources'][key]
 maxima=[max((row['powers'][i] for row in rows),default=0) for i in range(len(names))];powers=[[v[k]**j for j in range(m+1)] for k,m in zip(names,maxima)]
 for row in rows:
  term=I(Q(row['coefficient']))
  for i,n in enumerate(row['powers']):
   if n:term=term*powers[i][n]
  out=out+term
 return out
def sources34(v,p):
 args=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')]
 s3=c3mod.cubic(*args,p);s4=c4mod.quartic(*args,v['p3'],v['f3'],v['g3'],p,c3mod)
 return s3,s4
def endpoint(arm,fifth,p,side,sigma):
 old=fifth['walls'][side];w={k:iv(x) for k,x in old['inputs'].items()};v={k:iv(x) for k,x in old['source_variables'].items()};q={k:iv(x) for k,x in old['quantities'].items()};constants=fifth['constants']
 v.update(p5=I(-Q(constants['p5_bound']),Q(constants['p5_bound'])),f5=I(-Q(constants['f5_bound']),Q(constants['f5_bound'])),g5=I(-Q(constants['f5prime_bound']),Q(constants['f5prime_bound'])),N6=p['rate']/(6*(6*p['rate']-p['h'])),p6=I(0),f6=I(0),g6=I(0))
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];m,r,h=p['m2'],p['rate'],p['h'];k=p['k'];mu1,mu2=p['mu1'],p['mu2']
 Hp,Tp,u,U,gp,Gp,up,gpp=[w[k] for k in ('Hp','Tp','u1','u2','g1prime','g2prime','u1prime','g1second')]
 c,cp=w['c2'],w['c2prime'];s3,s4=sources34(v,p);B=12*H*T-4*m*Phi
 Hpp=-2*T*Tp/3+2*k*H*e;Tpp=w['Tpp'];Tppp=m*Tp-4*Hpp*T-8*Hp*Tp-4*H*Tpp
 cpp=-p['c_factor']*(12*(u*u+a*up)+2*(g*g+f*gp))
 sp2=H*c-a*u-f*g/6;sp2p=Hp*c+H*cp-u*u-a*up-(g*g+f*gp)/6
 Upp=-2*Hp*P-2*H*U-Tp*F/3-T*G/3+sp2p
 qk2p=12*mu1*H*e*a*f+(4*m-6*mu1*e)*(u*f+a*g)+6*up*g+6*u*gp-8*m*T*a*a-16*m*Phi*a*u
 sg2p=Tp*cp+T*cpp+2*m*T*c+2*m*Phi*cp-6*Tp*sp2-6*T*sp2p-qk2p
 Bp=12*Hp*T+12*H*Tp-4*m*T
 Gpp=-4*Hp*G-4*H*Gp+(2*mu2*H*e+4*T*Tp)*F+(m-mu2*e+2*sq(T))*G+Bp*P+B*U+sg2p
 u3=w['u3'];c3p=w['c3prime'];c3=s3['c3']
 innerp=36*(u*v['p3']+a*u3)+48*P*U+6*(g*v['f3']+f*v['g3'])+8*F*G-18*(u*c3+a*c3p)-24*(U*c+P*cp)+8*c*cp
 c4p=-p['c4_factor']*innerp;mu4=-4*r*(4*r+3*h)
 u4=-2*H*v['p4']-T*v['f4']/3+s4['Sp4'];g4p=-4*H*v['g4']+(m-mu4*e+2*sq(T))*v['f4']+B*v['p4']+s4['Sg4']
 need(q['d5_wall'].lo>0,'FIFTH_WALL_DIVISOR')
 w.update(p5=v['p5'],f5=v['f5'],g5=v['g5'],c5=q['c5'],xi5=q['xi5'],chi5=(v['f5']+T*q['xi5']-q['o5'])/q['d5_wall'],u4=u4,g4prime=g4p,c4prime=c4p,u2prime=Upp,g2second=Gpp,c2second=cpp,Hpp=Hpp,Tppp=Tppp)
 full=w6mod.direct(w,sigma);o6,j6,qi6=[full[k].a[6] for k in ('O','J','graph')];div=6*sigma*e*r*(6*r-h);need(div.lo>0 or div.hi<0,'SIXTH_GRAPH_DIVISOR');xi6=-qi6/div
 mu6=-6*r*(6*r+3*h);dwall=2-mu6*e;J=-3*(mu6+4*k)*e;D=J+2*sq(T);need(dwall.lo>0 and J.lo>0 and D.lo>0,'SIXTH_ENDPOINT_POSITIVITY')
 c6=polynomial(v,'c6');Sc6=polynomial(v,'Sc6');gamma=21-I(1)/dwall;R=2*sigma*(T*c6-Tp*xi6-j6)+gamma*T*xi6+o6/dwall;robin=-D*R/(2*J)+2*sigma*T*Sc6/J
 b1=-2*a;b2=c-2*P;b3=c3-2*v['p3'];b4=s4['c4']-2*v['p4'];ex=w6mod.S([0,b1,b2,b3,b4]).expzero()
 transport=xi6+w['xi5']*b1+w['xi4']*ex.a[2]+w['xi3']*ex.a[3]+w['xi2']*ex.a[4]+w['xi2']*w['xi3']*(-2*u)+w['xi2']**2*(cp-2*U+b1*(-2*u))/2
 return dict(inputs={k:x.pack() for k,x in w.items()},source_variables={k:x.pack() for k,x in v.items()},quantities={k:x.pack() for k,x in dict(xi6=xi6,robin=robin,transport=transport,c6=c6,Sc6=Sc6,D6=D,J6=J,d6_wall=dwall,graph_divisor=div,o6=o6,j6=j6,qI6=qi6,R6=R).items()})
def calculate(arm,fifth,globalrow,inverse):
 p={k:iv(x) for k,x in arm['parameters'].items()};v={k:iv(x) for k,x in globalrow['variables'].items()};r,h,m=p['rate'],p['h'],p['m2'];fc=fifth['constants']
 need((6*r-h).lo>0,'TRACE6_DIVISOR')
 v.update(p5=I(-Q(fc['p5_bound']),Q(fc['p5_bound'])),f5=I(-Q(fc['f5_bound']),Q(fc['f5_bound'])),g5=I(-Q(fc['f5prime_bound']),Q(fc['f5prime_bound'])),N6=r/(6*(6*r-h)),p6=I(0),f6=I(0),g6=I(0))
 H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];mu6=-6*r*(6*r+3*h);J=-3*(mu6+4*p['k'])*e;D=J+2*sq(T);need(J.lo>0 and D.lo>0,'GLOBAL_SIXTH_POSITIVITY')
 s={k:polynomial(v,k) for k in ('c6','Sp6','Sc6','Sg6')};B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;forcing=s['Sg6']+B*s['Sc6']/D
 walls={side:endpoint(arm,fifth,p,side,sg) for side,sg in [('lower',1),('upper',-1)]};G=max(ab(iv(w['quantities']['robin'])) for w in walls.values())
 cf=Q(inverse['finite_orders']['6']['constant'])*Q(inverse['f_transfer_multiplier']);need(cf>0,'FINITE6_INVERSE');size=ab(forcing)+6*G;fb=cf*size/36;gb=cf*size/6;pb=(ab(s['Sc6'])+ab(T)*gb+ab(Tp)*fb)/D.lo
 s3,s4=sources34(v,p);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f']);c5=iv(globalrow['sources']['c5'])
 bs=[0,-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],c5-2*v['p5'],s['c6']];density=w6mod.S(bs).expzero().a[6];length=I(*arm['D']);need(length.lo>0,'DOMAIN')
 integral=density*length;known=iv(walls['upper']['quantities']['transport'])-iv(walls['lower']['quantities']['transport'])+integral;metric=2*length.hi*pb;d6=known+I(-metric,metric)
 return dict(walls=walls,source_variables={k:x.pack() for k,x in v.items()},sources={k:x.pack() for k,x in s.items()},bulk={k:x.pack() for k,x in dict(J6=J,D6=D,Tp=Tp,B0=B,forcing=forcing,density=density,integral=integral,known=known,d6=d6).items()},constants={k:str(x) for k,x in dict(Cf6=cf,Robin_abs=G,source_size=size,f6_bound=fb,f6prime_bound=gb,p6_bound=pb,metric_integral_bound=metric).items()},scope='Unsigned actual sixth coefficient enclosure from inherited whole-domain lower fields; no sixth profile, sign or trajectory.')
