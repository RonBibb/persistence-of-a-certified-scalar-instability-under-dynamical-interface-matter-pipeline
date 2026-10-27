"""Exact spatial derivative polynomials for seventh wall inputs."""
from fractions import Fraction as Q
def build(ring,cubic,quartic,fifth,wall):
 names=('H','T','Phi','e','p','f','g','P','F','G','p3','f3','g3','p4','f4','g4','p5','f5','g5','m','C','J','L','M','r','h')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
 v={k:ring.variable(i) for i,k in enumerate(names)};z=ring.P(0)
 H,T,Phi,e,p,f,g,P,F,G=[v[k] for k in names[:10]];r,h,m=v['r'],v['h'],v['m']
 params=dict(m2=m,k=h*h,rate=r,h=h,c_factor=v['C'],c3_factor=v['J'],c4_factor=v['L'],**{'mu'+str(n):-n*r*(n*r+3*h) for n in range(1,6)})
 B=12*H*T-4*m*Phi;Hp=-T*T/3-h*h*e;Tp=m*Phi-4*H*T
 u=-2*H*p-T*f/3;gp=-4*H*g+(m-params['mu1']*e+2*T*T)*f+B*p
 c2=-v['C']*(6*p*p+f*f);cp=-v['C']*(12*p*u+2*f*g);sp2=H*c2-p*u-f*g/6
 qk2=(4*m-6*params['mu1']*e)*p*f+6*u*g-8*m*Phi*p*p
 sg2=T*cp+2*m*Phi*c2-6*T*sp2-qk2
 U=-2*H*P-T*F/3+sp2;Gp=-4*H*G+(m-params['mu2']*e+2*T*T)*F+B*P+sg2
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params)
 s4=quartic.quartic(H,T,Phi,e,p,f,g,P,F,G,v['p3'],v['f3'],v['g3'],params,cubic)
 def poly(key):
  out=z
  for row in fifth['sources'][key]:
   term=ring.P(Q(row['coefficient']))
   for k,n in zip(fifth['variables'],row['powers']):
    if n:term=term*v[k]**n
   out+=term
  return out
 s5={k:poly(k) for k in ('c5','Sp5','Sg5')}
 d={k:z for k in names};d.update(H=Hp,T=Tp,Phi=T,e=-2*H*e,p=u,f=g,g=gp,P=U,F=G,G=Gp)
 for n,s in ((3,s3),(4,s4),(5,s5)):
  pn,fn,gn=[v[k+str(n)] for k in ('p','f','g')];mu=-n*r*(n*r+3*h)
  d['p'+str(n)]=-2*H*pn-T*fn/3+s['Sp'+str(n)]
  d['f'+str(n)]=gn;d['g'+str(n)]=-4*H*gn+(m-mu*e+2*T*T)*fn+B*pn+s['Sg'+str(n)]
 def ds(x):return sum((x.derivative(i)*d[k] for i,k in enumerate(names)),z)
 targets=dict(u5=d['p5'],g5prime=d['g5'],c5prime=ds(s5['c5']),u3prime=ds(d['p3']),g3second=ds(d['g3']),c3second=ds(ds(s3['c3'])),u1second=ds(ds(u)),g1third=ds(ds(gp)))
 # An independent coefficient-level Leibniz derivative of packed monomials.
 def leibniz(x):
  out=z
  for powers,coef in x.t.items():
   for j,n in enumerate(powers):
    if not n:continue
    a=list(powers);a[j]-=1;out+=ring.P({tuple(a):coef*n})*d[names[j]]
  return out
 checks=[]
 for key,base,order in [('c5prime',s5['c5'],1),('u3prime',d['p3'],1),('g3second',d['g3'],1),('c3second',s3['c3'],2),('u1second',u,2),('g1third',gp,2)]:
  q=base
  for _ in range(order):q=leibniz(q)
  assert (q-targets[key]).iszero(),key;checks.append('EXACT_LEIBNIZ:'+key)
 # Return base equations and derivative map for independent reconstruction.
 return dict(pass_status=True,variables=names,derivative_map={k:x.pack() for k,x in d.items()},base_polynomials={k:x.pack() for k,x in dict(c5=s5['c5'],c3=s3['c3'],u1=u,g1prime=gp,u3=d['p3'],g3prime=d['g3']).items()},sources={k:x.pack() for k,x in targets.items()},checks=checks,scope='Exact reduced-equation spatial jets. No field enclosure, new solution or amplitude claim.')
