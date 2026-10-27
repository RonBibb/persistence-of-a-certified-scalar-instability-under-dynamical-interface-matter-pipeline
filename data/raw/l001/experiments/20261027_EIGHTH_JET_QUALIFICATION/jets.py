"""Exact spatial derivatives needed by degree-eight moving-wall loads."""
from fractions import Fraction as Q
def build(ring,prior,sixth,quartic):
 names=tuple(prior['variables'])+('p6','f6','g6','N6')
 assert len(names)==len(set(names))
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
 v={k:ring.variable(i) for i,k in enumerate(names)};z=ring.P(0)
 def unpack(rows,oldnames):
  out=z
  for row in rows:
   term=ring.P(Q(row['coefficient']))
   for k,n in zip(oldnames,row['powers']):
    if n:term=term*v[k]**n
   out+=term
  return out
 d={k:z for k in names}
 for k,rows in prior['derivative_map'].items():d[k]=unpack(rows,prior['variables'])
 s6={k:unpack(sixth['sources'][k],sixth['variables']) for k in ('c6','Sp6','Sg6')}
 H,T,Phi,e,m,r,h=[v[k] for k in ('H','T','Phi','e','m','r','h')]
 d['p6']=-2*H*v['p6']-T*v['f6']/3+s6['Sp6'];d['f6']=v['g6']
 d['g6']=-4*H*v['g6']+(m+6*r*(6*r+3*h)*e+2*T*T)*v['f6']+(12*H*T-4*m*Phi)*v['p6']+s6['Sg6']
 c2=-v['C']*(6*v['p']**2+v['f']**2);c4=unpack(quartic['sources']['c4'],quartic['variables'])
 def ds(x):return sum((x.derivative(i)*d[k] for i,k in enumerate(names)),z)
 bases=dict(u6=d['p6'],g6prime=d['g6'],c6=s6['c6'],u4=d['p4'],g4prime=d['g4'],c4=c4,u2=d['P'],g2prime=d['G'],c2=c2,Hprime=d['H'],Tprime=d['T'])
 specs={'u6':('u6',0),'g6prime':('g6prime',0),'c6prime':('c6',1),'u4prime':('u4',1),'g4second':('g4prime',1),'c4second':('c4',2),'u2second':('u2',2),'g2third':('g2prime',2),'c2third':('c2',3),'Hppp':('Hprime',2),'Tpppp':('Tprime',3)}
 targets={}
 for key,(base,n) in specs.items():
  q=bases[base]
  for _ in range(n):q=ds(q)
  targets[key]=q
 def leibniz(x):
  out=z
  for powers,coef in x.t.items():
   for j,n in enumerate(powers):
    if n:
     a=list(powers);a[j]-=1;out+=ring.P({tuple(a):coef*n})*d[names[j]]
  return out
 checks=[]
 for key,(base,n) in specs.items():
  q=bases[base]
  for _ in range(n):q=leibniz(q)
  assert (q-targets[key]).iszero(),key;checks.append('EXACT_LEIBNIZ:'+key)
 return dict(pass_status=True,variables=names,derivative_map={k:x.pack() for k,x in d.items()},base_polynomials={k:x.pack() for k,x in bases.items()},derivative_specs=specs,sources={k:x.pack() for k,x in targets.items()},checks=checks,scope='Exact reduced-equation derivatives including background H third and T fourth. No interval enclosure or eighth coefficient admission.')
