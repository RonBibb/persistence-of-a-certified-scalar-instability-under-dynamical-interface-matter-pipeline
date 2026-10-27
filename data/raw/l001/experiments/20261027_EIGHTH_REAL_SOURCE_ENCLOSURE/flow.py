"""Eighth actual-source enclosure; qualified polynomial jets, no ODE."""
from fractions import Fraction as Q
def need(v,n):
 if not v:raise AssertionError(n)
def setup(interval,cubic,quartic,wall,qualified,jets):
 global I,c3mod,c4mod,w8mod,qual,jetqual
 I,c3mod,c4mod,w8mod,qual,jetqual=interval,cubic,quartic,wall,qualified,jets
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
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h'];need((8*r-h).lo>0,'TRACE8_DIVISOR')
 v.update(p7=I(-Q(constants['p7_bound']),Q(constants['p7_bound'])),f7=I(-Q(constants['f7_bound']),Q(constants['f7_bound'])),g7=I(-Q(constants['f7prime_bound']),Q(constants['f7prime_bound'])),N8=r/(8*(8*r-h)),p8=I(0),f8=I(0),g8=I(0))
 return v
def endpoint(seventh,p,side,sigma):
 old=seventh['walls'][side];w={k:iv(x) for k,x in old['inputs'].items()};v=extend(old['source_variables'],seventh['constants'],p);q={k:iv(x) for k,x in old['quantities'].items()}
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];r,h=p['rate'],p['h'];Tp=w['Tp']
 need(q['d7_wall'].lo>0,'SEVENTH_WALL_DIVISOR')
 w.update(p7=v['p7'],f7=v['f7'],g7=v['g7'],c7=q['c7'],xi7=q['xi7'],chi7=(v['f7']+T*q['xi7']-q['o7'])/q['d7_wall'])
 jets={k:polynomial(v,k,jetqual) for k in ('u6','g6prime','c6prime','u4prime','g4second','c4second','u2second','g2third','c2third','Hppp','Tpppp')};w.update(jets)
 full=w8mod.direct(w,sigma);o8,j8,qi8=[full[k].a[8] for k in ('O','J','graph')];div=8*sigma*e*r*(8*r-h);need(div.lo>0 or div.hi<0,'EIGHTH_GRAPH_DIVISOR');xi8=-qi8/div
 mu8=-8*r*(8*r+3*h);dwall=2-mu8*e;J=-3*(mu8+4*p['k'])*e;D=J+2*sq(T);need(dwall.lo>0 and J.lo>0 and D.lo>0,'EIGHTH_ENDPOINT_POSITIVITY')
 c8=polynomial(v,'c8');Sc8=polynomial(v,'Sc8');gamma=21-I(1)/dwall;R=2*sigma*(T*c8-Tp*xi8-j8)+gamma*T*xi8+o8/dwall;robin=-D*R/(2*J)+2*sigma*T*Sc8/J
 b=[0]+[w['c'+str(n)]-2*w['p'+str(n)] if n>=2 else -2*w['p1'] for n in range(1,7)]
 E=w8mod.S(b).expzero()
 bp=w8mod.S([0,-2*w['u1']]+[w['c'+str(n)+'prime']-2*w['u'+str(n)] for n in range(2,5)])
 bpp=w8mod.S([0,-2*w['u1prime'],w['c2second']-2*w['u2prime']])
 Ep=E*bp;Epp=E*(bpp+bp*bp)
 x={n:w['xi'+str(n)] for n in range(2,8)};x[8]=xi8
 transport=transport8(E.a,Ep.a,Epp.a,x)

 return dict(inputs={k:x.pack() for k,x in w.items()},source_variables={k:x.pack() for k,x in v.items()},jets={k:x.pack() for k,x in jets.items()},quantities={k:x.pack() for k,x in dict(xi8=xi8,robin=robin,transport=transport,c8=c8,Sc8=Sc8,D8=D,J8=J,d8_wall=dwall,graph_divisor=div,o8=o8,j8=j8,qI8=qi8,R8=R).items()})
def calculate(arm,seventh,sixth,globalrow,inverse):
 p={k:iv(x) for k,x in arm['parameters'].items()};v=extend(seventh['source_variables'],seventh['constants'],p);r,h,m=p['rate'],p['h'],p['m2']
 H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];mu8=-8*r*(8*r+3*h);J=-3*(mu8+4*p['k'])*e;D=J+2*sq(T);need(J.lo>0 and D.lo>0,'GLOBAL_EIGHTH_POSITIVITY')
 s={k:polynomial(v,k) for k in ('c8','Sp8','Sc8','Sg8')};B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;forcing=s['Sg8']+B*s['Sc8']/D
 walls={side:endpoint(seventh,p,side,sg) for side,sg in [('lower',1),('upper',-1)]};G=max(ab(iv(w['quantities']['robin'])) for w in walls.values())
 cf=Q(inverse['finite_orders']['8']['constant'])*Q(inverse['f_transfer_multiplier']);need(cf>0,'FINITE8_INVERSE');size=ab(forcing)+8*G;fb=cf*size/64;gb=cf*size/8;pb=(ab(s['Sc8'])+ab(T)*gb+ab(Tp)*fb)/D.lo
 s3,s4=sources34(v,p);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f']);c5=iv(globalrow['sources']['c5']);c6=iv(sixth['sources']['c6']);c7=iv(seventh['sources']['c7'])
 bs=[0,-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],c5-2*v['p5'],c6-2*v['p6'],c7-2*v['p7'],s['c8']];density=w8mod.S(bs).expzero().a[8];length=I(*arm['D']);need(length.lo>0,'DOMAIN')
 integral=density*length;known=iv(walls['upper']['quantities']['transport'])-iv(walls['lower']['quantities']['transport'])+integral;metric=2*length.hi*pb;d8=known+I(-metric,metric)
 return dict(walls=walls,source_variables={k:x.pack() for k,x in v.items()},sources={k:x.pack() for k,x in s.items()},bulk={k:x.pack() for k,x in dict(J8=J,D8=D,Tp=Tp,B0=B,forcing=forcing,density=density,integral=integral,known=known,d8=d8).items()},constants={k:str(x) for k,x in dict(Cf8=cf,Robin_abs=G,source_size=size,f8_bound=fb,f8prime_bound=gb,p8_bound=pb,metric_integral_bound=metric).items()},scope='Unsigned actual eighth coefficient enclosure; no eighth profile, sign, trajectory or full-clock claim.')

def transport8(E,Ep,Epp,x):
 return x[8]+sum((x[8-n]*E[n] for n in range(1,7)),0)+x[2]**2*Ep[4]/2+x[2]*x[3]*Ep[3]+(x[2]*x[4]+x[3]**2/2)*Ep[2]+(x[2]*x[5]+x[3]*x[4])*Ep[1]+x[2]**3*Epp[2]/6+x[2]**2*x[3]*Epp[1]/2
def qualify_transport(ring,S):
 names=tuple('E'+str(n) for n in range(1,7))+tuple('Ep'+str(n) for n in range(1,5))+('Epp1','Epp2')+tuple('x'+str(n) for n in range(2,9))
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(i) for i,k in enumerate(names)}
 E=[1]+[v['E'+str(n)] for n in range(1,7)];Ep=[0]+[v['Ep'+str(n)] for n in range(1,5)];Epp=[0,v['Epp1'],v['Epp2']];x={n:v['x'+str(n)] for n in range(2,9)}
 shift=S([0,0]+[x[n] for n in range(2,9)]);direct=(S(E)*shift+S(Ep)*shift*shift/2+S(Epp)*shift*shift*shift/6).a[8]
 assert (direct-transport8(E,Ep,Epp,x)).iszero(),'TRANSPORT8_EXACT'
 return dict(pass_status=True,check='TRANSPORT8_EXACT',premise='Background radial density identically one; fourth displacement derivative term vanishes')
