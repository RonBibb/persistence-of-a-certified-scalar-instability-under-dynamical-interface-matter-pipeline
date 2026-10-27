"""Ninth actual-source enclosure; qualified polynomial jets, no ODE."""
from fractions import Fraction as Q
def need(v,n):
 if not v:raise AssertionError(n)
def setup(interval,cubic,quartic,wall,qualified,jets):
 global I,c3mod,c4mod,w9mod,qual,jetqual
 I,c3mod,c4mod,w9mod,qual,jetqual=interval,cubic,quartic,wall,qualified,jets
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
 v={k:iv(x) for k,x in old.items()};r,h=p['rate'],p['h'];need((9*r-h).lo>0,'TRACE9_DIVISOR')
 v.update(p8=I(-Q(constants['p8_bound']),Q(constants['p8_bound'])),f8=I(-Q(constants['f8_bound']),Q(constants['f8_bound'])),g8=I(-Q(constants['f8prime_bound']),Q(constants['f8prime_bound'])),N9=r/(9*(9*r-h)),p9=I(0),f9=I(0),g9=I(0))
 return v
def endpoint(eighth,p,side,sigma):
 old=eighth['walls'][side];w={k:iv(x) for k,x in old['inputs'].items()};v=extend(old['source_variables'],eighth['constants'],p);q={k:iv(x) for k,x in old['quantities'].items()}
 H,T,Phi,e,a,f,g,P,F,G=[v[k] for k in ('H','T','Phi','e','p','f','g','P','F','G')];r,h=p['rate'],p['h'];Tp=w['Tp']
 need(q['d8_wall'].lo>0,'EIGHTH_WALL_DIVISOR')
 w.update(p8=v['p8'],f8=v['f8'],g8=v['g8'],c8=q['c8'],xi8=q['xi8'],chi8=(v['f8']+T*q['xi8']-q['o8'])/q['d8_wall'])
 jets={k:polynomial(v,k,jetqual) for k in ('u7','g7prime','c7prime','u5prime','g5second','c5second','u3second','g3third','c3third','u1third','g1fourth')};w.update(jets)
 full=w9mod.direct(w,sigma);o9,j9,qi9=[full[k].a[9] for k in ('O','J','graph')];div=9*sigma*e*r*(9*r-h);need(div.lo>0 or div.hi<0,'NINTH_GRAPH_DIVISOR');xi9=-qi9/div
 mu9=-9*r*(9*r+3*h);dwall=2-mu9*e;J=-3*(mu9+4*p['k'])*e;D=J+2*sq(T);need(dwall.lo>0 and J.lo>0 and D.lo>0,'NINTH_ENDPOINT_POSITIVITY')
 c9=polynomial(v,'c9');Sc9=polynomial(v,'Sc9');gamma=21-I(1)/dwall;R=2*sigma*(T*c9-Tp*xi9-j9)+gamma*T*xi9+o9/dwall;robin=-D*R/(2*J)+2*sigma*T*Sc9/J
 b=[0]+[w['c'+str(n)]-2*w['p'+str(n)] if n>=2 else -2*w['p1'] for n in range(1,8)]
 E=w9mod.S(b).expzero()
 bp=w9mod.S([0,-2*w['u1']]+[w['c'+str(n)+'prime']-2*w['u'+str(n)] for n in range(2,6)])
 bpp=w9mod.S([0,-2*w['u1prime']]+[w['c'+str(n)+'second']-2*w['u'+str(n)+'prime'] for n in range(2,4)])
 bppp=w9mod.S([0,-2*w['u1second']])
 Ep=E*bp;Epp=E*(bpp+bp*bp);Eppp=E*(bppp+3*bp*bpp+bp*bp*bp)
 x={n:w['xi'+str(n)] for n in range(2,9)};x[9]=xi9
 transport=transport9(E.a,Ep.a,Epp.a,Eppp.a,x)

 return dict(inputs={k:x.pack() for k,x in w.items()},source_variables={k:x.pack() for k,x in v.items()},jets={k:x.pack() for k,x in jets.items()},quantities={k:x.pack() for k,x in dict(xi9=xi9,robin=robin,transport=transport,c9=c9,Sc9=Sc9,D9=D,J9=J,d9_wall=dwall,graph_divisor=div,o9=o9,j9=j9,qI9=qi9,R9=R).items()})
def calculate(arm,eighth,seventh,sixth,globalrow,inverse):
 p={k:iv(x) for k,x in arm['parameters'].items()};v=extend(eighth['source_variables'],eighth['constants'],p);r,h,m=p['rate'],p['h'],p['m2']
 H,T,Phi,e=[v[k] for k in ('H','T','Phi','e')];mu9=-9*r*(9*r+3*h);J=-3*(mu9+4*p['k'])*e;D=J+2*sq(T);need(J.lo>0 and D.lo>0,'GLOBAL_NINTH_POSITIVITY')
 s={k:polynomial(v,k) for k in ('c9','Sp9','Sc9','Sg9')};B=12*H*T-4*m*Phi;Tp=m*Phi-4*H*T;forcing=s['Sg9']+B*s['Sc9']/D
 walls={side:endpoint(eighth,p,side,sg) for side,sg in [('lower',1),('upper',-1)]};G=max(ab(iv(w['quantities']['robin'])) for w in walls.values())
 cf=Q(inverse['finite_orders']['9']['constant'])*Q(inverse['f_transfer_multiplier']);need(cf>0,'FINITE9_INVERSE');size=ab(forcing)+9*G;fb=cf*size/81;gb=cf*size/9;pb=(ab(s['Sc9'])+ab(T)*gb+ab(Tp)*fb)/D.lo
 s3,s4=sources34(v,p);c2=-p['c_factor']*(6*v['p']*v['p']+v['f']*v['f']);c5=iv(globalrow['sources']['c5']);c6=iv(sixth['sources']['c6']);c7=iv(seventh['sources']['c7']);c8=iv(eighth['sources']['c8'])
 bs=[0,-2*v['p'],c2-2*v['P'],s3['c3']-2*v['p3'],s4['c4']-2*v['p4'],c5-2*v['p5'],c6-2*v['p6'],c7-2*v['p7'],c8-2*v['p8'],s['c9']];density=w9mod.S(bs).expzero().a[9];length=I(*arm['D']);need(length.lo>0,'DOMAIN')

 integral=density*length;known=iv(walls['upper']['quantities']['transport'])-iv(walls['lower']['quantities']['transport'])+integral;metric=2*length.hi*pb;d9=known+I(-metric,metric)
 return dict(walls=walls,source_variables={k:x.pack() for k,x in v.items()},sources={k:x.pack() for k,x in s.items()},bulk={k:x.pack() for k,x in dict(J9=J,D9=D,Tp=Tp,B0=B,forcing=forcing,density=density,integral=integral,known=known,d9=d9).items()},constants={k:str(x) for k,x in dict(Cf9=cf,Robin_abs=G,source_size=size,f9_bound=fb,f9prime_bound=gb,p9_bound=pb,metric_integral_bound=metric).items()},scope='Unsigned actual ninth coefficient enclosure; no ninth profile, sign, trajectory or full-clock claim.')

def transport9(E,Ep,Epp,Eppp,x):
 out=x[9]+sum((x[9-n]*E[n] for n in range(1,8)),0)
 for n in range(1,6):
  out+=Ep[n]*sum((x[i]*x[9-n-i] for i in range(2,8) if 2<=9-n-i<=8),0)/2
 for n in range(1,4):
  out+=Epp[n]*sum((x[i]*x[j]*x[9-n-i-j] for i in range(2,8) for j in range(2,8) if 2<=9-n-i-j<=8),0)/6
 return out+Eppp[1]*x[2]**4/24
def qualify_transport(ring,S):
 names=tuple('E'+str(n) for n in range(1,8))+tuple('Ep'+str(n) for n in range(1,6))+tuple('Epp'+str(n) for n in range(1,4))+('Eppp1',)+tuple('x'+str(n) for n in range(2,10))
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(i) for i,k in enumerate(names)}
 E=[1]+[v['E'+str(n)] for n in range(1,8)];Ep=[0]+[v['Ep'+str(n)] for n in range(1,6)];Epp=[0]+[v['Epp'+str(n)] for n in range(1,4)];Eppp=[0,v['Eppp1']];x={n:v['x'+str(n)] for n in range(2,10)}
 shift=S([0,0]+[x[n] for n in range(2,10)]);direct=(S(E)*shift+S(Ep)*shift*shift/2+S(Epp)*shift*shift*shift/6+S(Eppp)*shift*shift*shift*shift/24).a[9]
 assert (direct-transport9(E,Ep,Epp,Eppp,x)).iszero(),'TRANSPORT9_EXACT'
 assert not (direct-(direct-v['Eppp1']*x[2]**4/24)).iszero(),'TRANSPORT9_FOURTH_SHIFT_MUTATION'
 return dict(pass_status=True,check='TRANSPORT9_EXACT',premise='Background radial density identically one; fourth displacement term from E1 third derivative retained; fifth displacement starts beyond9')
