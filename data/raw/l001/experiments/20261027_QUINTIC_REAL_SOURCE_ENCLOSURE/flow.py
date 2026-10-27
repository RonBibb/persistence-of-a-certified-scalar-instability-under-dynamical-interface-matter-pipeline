"""Actual fifth coefficient bounds; no new ODE or fifth field profile."""
from fractions import Fraction as Q
def need(v,n):
 if not v:raise AssertionError(n)
def setup(interval,cubic,quartic,wall5,qualified):
 global I,c3mod,c4mod,w5mod,qual
 I,c3mod,c4mod,w5mod,qual=interval,cubic,quartic,wall5,qualified
def iv(v):return I(*v['exact_bounds'])
def ab(v):return max(abs(v.lo),abs(v.hi))
def sq(v):
 return I.out(0 if v.lo<=0<=v.hi else min(v.lo*v.lo,v.hi*v.hi),max(v.lo*v.lo,v.hi*v.hi))
def overlaps(a,b):return max(a.lo,b.lo)<=min(a.hi,b.hi)
def polynomial(v,key):
 names=qual['variables'];out=I(0)
 maxima=[max((row['powers'][i] for row in qual['sources'][key]),default=0) for i in range(len(names))]
 powers=[[v[n]**j for j in range(k+1)] for n,k in zip(names,maxima)]
 for row in qual['sources'][key]:
  term=I(Q(row['coefficient']))
  for i,n in enumerate(row['powers']):
   if n:term=term*powers[i][n]
  out=out+term
 return out
def sources34(v,p):
 args=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')]
 s3=c3mod.cubic(*args,p)
 s4=c4mod.quartic(*args,v['p3'],v['f3'],v['g3'],p,c3mod)
 return s3,s4
def endpoint(arm,old,p,side,sigma):
 z=[iv(x) for x in arm[side+'_canonical']]
 w={k:iv(x) for k,x in old['walls'][side]['data'].items()}
 # Both authenticated endpoint archives enclose the same actual lower-order solution.
 for key,j in [('H',1),('T',3),('E',4),('p1',5),('f1',6),('g1',7)]:need(overlaps(w[key],z[j]),'ENDPOINT_OVERLAP:'+side+':'+key)
 H,T,E=w['H'],w['T'],w['E'];Phi=z[2];e=sq(E);m=p['m2'];r=p['rate'];h=p['h']
 need(overlaps(w['rate'],r) and overlaps(w['h'],h),'WALL_PARAMETER_IDENTITY')
 v=dict(H=H,T=T,Phi=Phi,e=e,p=w['p1'],f=w['f1'],g=w['g1'],P=w['p2'],F=w['f2'],G=w['g2'],
        p3=w['p3'],f3=w['f3'],g3=w['g3'],p4=I(-Q(arm['p4_bound']),Q(arm['p4_bound'])),
        f4=I(-Q(arm['f4_bound']),Q(arm['f4_bound'])),g4=I(-Q(arm['f4prime_bound']),Q(arm['f4prime_bound'])),
        m=m,C=p['c_factor'],J=p['c3_factor'],L=p['c4_factor'],M=r/(5*(5*r-h)),r=r,h=h,p5=I(0),f5=I(0),g5=I(0))
 s3,s4=sources34(v,p);a,f,g=v['p'],v['f'],v['g'];P,F,G=v['P'],v['F'],v['G']
 Hp=-sq(T)/3-p['k']*e;Tp=m*Phi-4*H*T;B=12*H*T-4*m*Phi
 u=-2*H*a-T*f/3;c2=-p['c_factor']*(6*a*a+f*f);cp=-p['c_factor']*(12*a*u+2*f*g)
 sp2=H*c2-a*u-f*g/6
 qk2=(4*m-6*p['mu1']*e)*a*f+6*u*g-8*m*Phi*a*a
 sg2=T*cp+2*m*Phi*c2-6*T*sp2-qk2
 U=-2*H*P-T*F/3+sp2
 gp=-4*H*g+(m-p['mu1']*e+2*sq(T))*f+B*a
 Gp=-4*H*G+(m-p['mu2']*e+2*sq(T))*F+B*P+sg2
 u3=-2*H*v['p3']-T*v['f3']/3+s3['Sp3']
 gp3=-4*H*v['g3']+(m-p['mu3']*e+2*sq(T))*v['f3']+B*v['p3']+s3['Sg3']
 c3p=-p['c3_factor']*(6*u*P+6*a*U+g*F+f*G-3*u*c2-3*a*cp)
 up=-2*Hp*a-2*H*u-Tp*f/3-T*g/3
 gpp=-4*Hp*g-4*H*gp+(2*p['mu1']*H*e+4*T*Tp)*f+(m-p['mu1']*e+2*sq(T))*g+(12*Hp*T+12*H*Tp-4*m*T)*a+B*u
 saved=arm['walls'][side];xi4=iv(saved['xi4']);o4=iv(saved['o4']);d4wall=2-p['mu4']*e
 need(d4wall.lo>0,'FOURTH_OSCILLATOR_DIVISOR')
 w.update(Hp=Hp,Tp=Tp,Tpp=m*T-4*Hp*T-4*H*Tp,u1=u,g1prime=gp,u2=U,g2prime=Gp,c2=c2,c2prime=cp,
          c3=s3['c3'],u3=u3,g3prime=gp3,c3prime=c3p,u1prime=up,g1second=gpp,
          p4=v['p4'],f4=v['f4'],g4=v['g4'],c4=s4['c4'],xi4=xi4,chi4=(v['f4']+T*xi4-o4)/d4wall)
 full=w5mod.direct(w,sigma);o5,j5,qi5=[full[k].a[5] for k in ('O','J','graph')]
 graphdiv=5*sigma*e*r*(5*r-h);need(graphdiv.lo>0 or graphdiv.hi<0,'GRAPH_DIVISOR')
 xi5=-qi5/graphdiv;mu5=-5*r*(5*r+3*h);dwall=2-mu5*e
 J=-3*(mu5+4*p['k'])*e;D=J+2*sq(T)
 need(dwall.lo>0 and J.lo>0 and D.lo>0,'FIFTH_ENDPOINT_POSITIVITY')
 c5=polynomial(v,'c5');Sc5=polynomial(v,'Sc5');gamma=21-I(1)/dwall
 R=2*sigma*(T*c5-Tp*xi5-j5)+gamma*T*xi5+o5/dwall
 robin=-D*R/(2*J)+2*sigma*T*Sc5/J
 b1=-2*a;b2=c2-2*P;b3=s3['c3']-2*v['p3']
 transport=xi5+xi4*b1+w['xi3']*(b2+b1*b1/2)+w['xi2']*(b3+b1*b2+b1**3/6)+w['xi2']**2*(-2*u)/2
 return dict(inputs={k:x.pack() for k,x in w.items()},source_variables={k:x.pack() for k,x in v.items()},
             quantities={k:x.pack() for k,x in dict(Hp=Hp,Tp=Tp,xi5=xi5,robin=robin,transport=transport,c5=c5,Sc5=Sc5,
             D5=D,J5=J,d5_wall=dwall,graph_divisor=graphdiv,o5=o5,j5=j5,qI5=qi5,R5=R,d4_wall=d4wall).items()})
def calculate(arm,old,globalrow,inverse):
 p={k:iv(x) for k,x in arm['parameters'].items()}
 v={k:iv(x) for k,x in globalrow['variables'].items()};H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')]
 r,h,m=p['rate'],p['h'],p['m2']
 need((r-h).lo>0 and h.lo>0 and e.lo>0,'PARAMETER_POSITIVITY')
 mu5=-5*r*(5*r+3*h);J=-3*(mu5+4*p['k'])*e
 need(J.lo>0,'GLOBAL_J5_POSITIVE');D=J+2*sq(T);need(D.lo>0,'GLOBAL_D5_POSITIVE')
 s={k:iv(x) for k,x in globalrow['sources'].items()};B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T
 forcing=s['Sg5']+B*s['Sc5']/D
 walls={side:endpoint(arm,old,p,side,sg) for side,sg in [('lower',1),('upper',-1)]}
 G=max(ab(iv(w['quantities']['robin'])) for w in walls.values())
 cf=Q(inverse['finite_orders']['5']['constant'])*Q(inverse['f_transfer_multiplier']);need(cf>0,'FINITE_INVERSE_POSITIVE')
 size=ab(forcing)+5*G;fb=cf*size/25;gb=cf*size/5
 pb=(ab(s['Sc5'])+ab(T)*gb+ab(Tp)*fb)/D.lo
 s3,s4=sources34(v,p)
 c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f'])
 b1=-2*v['p'];b2=c2-2*v['P'];b3=s3['c3']-2*v['p3'];b4=s4['c4']-2*v['p4']
 density=s['c5']+b1*b4+b2*b3+(b1*b1*b3+b1*b2*b2)/2+b1**3*b2/6+b1**5/120
 length=I(*arm['D']);need(length.lo>0,'POSITIVE_DOMAIN')
 integral=density*length
 known=iv(walls['upper']['quantities']['transport'])-iv(walls['lower']['quantities']['transport'])+integral
 metric=2*length.hi*pb;d5=known+I(-metric,metric)
 return dict(walls=walls,bulk={k:x.pack() for k,x in dict(J5=J,D5=D,Tp=Tp,B0=B,forcing=forcing,density=density,integral=integral,known=known,d5=d5).items()},
             constants={k:str(x) for k,x in dict(Cf5=cf,Robin_abs=G,source_size=size,f5_bound=fb,f5prime_bound=gb,p5_bound=pb,metric_integral_bound=metric).items()},
             scope='Unsigned actual fifth coefficient enclosure using globally enclosing lower fields and finite-n5 inverse; no fifth profile or sign.')

