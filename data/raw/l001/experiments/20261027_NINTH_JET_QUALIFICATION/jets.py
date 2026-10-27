"""Exact spatial derivatives needed by degree-nine moving-wall loads."""
from fractions import Fraction as Q
def build(ring,prior,seventh,fifth,seventhjets):
 names=tuple(prior['variables'])+('p7','f7','g7','N7')
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
 s7={k:unpack(seventh['sources'][k],seventh['variables']) for k in ('c7','Sp7','Sg7')}
 H,T,Phi,e,m,r,h=[v[k] for k in ('H','T','Phi','e','m','r','h')]
 d['p7']=-2*H*v['p7']-T*v['f7']/3+s7['Sp7'];d['f7']=v['g7']
 d['g7']=-4*H*v['g7']+(m+7*r*(7*r+3*h)*e+2*T*T)*v['f7']+(12*H*T-4*m*Phi)*v['p7']+s7['Sg7']
 c3=unpack(seventhjets['base_polynomials']['c3'],seventhjets['variables']);c5=unpack(fifth['sources']['c5'],fifth['variables'])
 def ds(x):return sum((x.derivative(i)*d[k] for i,k in enumerate(names)),z)
 bases=dict(u7=d['p7'],g7prime=d['g7'],c7=s7['c7'],u5=d['p5'],g5prime=d['g5'],c5=c5,u3=d['p3'],g3prime=d['g3'],c3=c3,u1=d['p'],g1prime=d['g'])
 specs={'u7':('u7',0),'g7prime':('g7prime',0),'c7prime':('c7',1),'u5prime':('u5',1),'g5second':('g5prime',1),'c5second':('c5',2),'u3second':('u3',2),'g3third':('g3prime',2),'c3third':('c3',3),'u1third':('u1',3),'g1fourth':('g1prime',3)}
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
 return dict(pass_status=True,variables=names,derivative_map={k:x.pack() for k,x in d.items()},base_polynomials={k:x.pack() for k,x in bases.items()},derivative_specs=specs,sources={k:x.pack() for k,x in targets.items()},checks=checks,scope='Exact reduced-equation derivatives including p1 fourth and f1 fifth spatial derivatives. No interval enclosure or ninth coefficient admission.')
