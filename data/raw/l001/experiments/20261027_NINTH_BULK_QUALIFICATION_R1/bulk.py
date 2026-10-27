"""Exact neutral ninth bulk extraction and analytic-background compatibility."""
from fractions import Fraction as Q
def group_coefficients(ring,poly,index,degree):
 buckets=[{} for _ in range(degree+1)]
 for powers,value in poly.t.items():
  key=list(powers);n=key[index];key[index]=0;key=tuple(key)
  buckets[n][key]=buckets[n].get(key,Q(0))+value
 return [ring.P(bucket) for bucket in buckets]
def verify_grouping(ring,seventh):
 names=tuple(seventh['variables']);ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
 cases=[ring.P(0),ring.P(Q(7,13))]
 for witness in seventh['pseudo_elimination']:
  for key in ('input','constraint','output'):
   cases.append(ring.P({tuple(row['powers']):Q(row['coefficient']) for row in witness[key][:128]}))
 synthetic={}
 for j in range(257):
  key=[0]*len(names);key[j%len(names)]=j%5;key[(j*7+3)%len(names)]+=j%4
  key=tuple(key);synthetic[key]=synthetic.get(key,Q(0))+Q((-1)**j*(j+1),j%13+1)
 cases.append(ring.P(synthetic));count=0
 for poly in cases:
  for index in range(len(names)):
   degree=max((key[index] for key in poly.t),default=0);old=[ring.P(0) for _ in range(degree+1)]
   for powers,value in poly.t.items():
    powers=list(powers);n=powers[index];powers[index]=0;old[n]+=ring.P({tuple(powers):value})
   new=group_coefficients(ring,poly,index,degree)
   assert len(old)==len(new) and all(a.t==b.t for a,b in zip(old,new)),'GROUP_EQUIVALENCE'
   count+=1
 return dict(pass_status=True,cases=len(cases),variable_cases=count)
def qualify(ring,S,cubic,quartic,fifth,sixth,seventh,eighth,progress=lambda *a,**k:None):
 progress('qualification_start')
 names=('g8','g7','g6','g5','g4','g3','G','g','H','T','Phi','e','p','f','P','F','p3','f3','p4','f4','m','C','J','L','M','r','h','p5','f5','N6','p6','f6','N7','p7','f7','N8','p8','f8','N9','p9','f9','g9')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(j) for j,k in enumerate(names)}
 g8,g7,g6,g5,g4,g3,G,g,H,T,Phi,e,p,f,P,F,p3,f3,p4,f4,m,C,J,L,M,r,h,p5,f5,N6,p6,f6,N7,p7,f7,N8,p8,f8,N9,p9,f9,g9=[v[k] for k in names]
 mus={n:-n*r*(n*r+3*h) for n in range(1,10)};Hp=-T*T/3-h*h*e;Tp=m*Phi-4*H*T;B0=12*H*T-4*m*Phi
 u=-2*H*p-T*f/3;gp=-4*H*g+(m-mus[1]*e+2*T*T)*f+B0*p
 c2=-C*(6*p*p+f*f);c2p=-C*(12*p*u+2*f*g);sp2=H*c2-p*u-f*g/6
 qk2=(4*m-6*mus[1]*e)*p*f+6*u*g-8*m*Phi*p*p;sg2=T*c2p+2*m*Phi*c2-6*T*sp2-qk2
 qr2=6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2-e*((12*h*h-3*r*r-18*h*r)*p*p+r*r*f*f/2)
 sc2=12*H*sp2-(12*H*H-T*T)*c2+qr2;U=-2*H*P-T*F/3+sp2;Gp=-4*H*G+(m-mus[2]*e+2*T*T)*F+B0*P+sg2
 params=dict(m2=m,k=h*h,rate=r,h=h,mu1=mus[1],mu2=mus[2],mu3=mus[3],c_factor=C,c3_factor=J,c4_factor=L)
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params);c3=s3['c3'];u3=-2*H*p3-T*f3/3+s3['Sp3'];gp3=-4*H*g3+(m-mus[3]*e+2*T*T)*f3+B0*p3+s3['Sg3']
 s4=quartic.quartic(H,T,Phi,e,p,f,g,P,F,G,p3,f3,g3,params,cubic);c4=s4['c4'];u4=-2*H*p4-T*f4/3+s4['Sp4'];gp4=-4*H*g4+(m-mus[4]*e+2*T*T)*f4+B0*p4+s4['Sg4']
 def oldpoly(key,record=fifth):
  rows=record['sources'][key];oldnames=record['variables'];indices=[names.index(k) if k in names else None for k in oldnames]
  bucket={}
  for row in rows:
   assert len(row['powers'])==len(oldnames),'SOURCE_DIMENSION'
   powers=[0]*len(names)
   for index,power in zip(indices,row['powers']):
    if power:
     assert index is not None,'SOURCE_VARIABLE_PRESENT'
     powers[index]+=power
   powers=tuple(powers);bucket[powers]=bucket.get(powers,Q(0))+Q(row['coefficient'])
  out=ring.P(bucket)
  # Exact round-trip checks every retained monomial, not a floating sample.
  back={}
  for powers,value in out.t.items():
   mapped=tuple(powers[index] if index is not None else 0 for index in indices)
   back[mapped]=back.get(mapped,Q(0))+value
  original={}
  for row in rows:
   powers=tuple(row['powers']);original[powers]=original.get(powers,Q(0))+Q(row['coefficient'])
  assert {k:v for k,v in original.items() if v}==back,'SOURCE_REMAP_ROUNDTRIP'
  # Compare legacy symbolic construction on first and last128 rows.
  selected=rows[:128]+rows[-128:];legacy=ring.P(0);mapped={}
  for row in selected:
   term=ring.P(Q(row['coefficient']));powers=[0]*len(names)
   for name,power,index in zip(oldnames,row['powers'],indices):
    if power:term*=v[name]**power;powers[index]+=power
   legacy+=term;powers=tuple(powers);mapped[powers]=mapped.get(powers,Q(0))+Q(row['coefficient'])
  assert legacy.t==ring.P(mapped).t,'SOURCE_REMAP_LEGACY_EQUIVALENCE'
  return out
 s5={k:oldpoly(k) for k in ('c5','Sp5','Sc5','Sg5')};c5=s5['c5'];u5=-2*H*p5-T*f5/3+s5['Sp5'];gp5=-4*H*g5+(m-mus[5]*e+2*T*T)*f5+B0*p5+s5['Sg5']
 s6={k:oldpoly(k,sixth) for k in ('c6','Sp6','Sc6','Sg6')};c6=s6['c6'];u6=-2*H*p6-T*f6/3+s6['Sp6'];gp6=-4*H*g6+(m-mus[6]*e+2*T*T)*f6+B0*p6+s6['Sg6']
 s7={k:oldpoly(k,seventh) for k in ('c7','Sp7','Sc7','Sg7')};c7=s7['c7'];u7=-2*H*p7-T*f7/3+s7['Sp7'];gp7=-4*H*g7+(m-mus[7]*e+2*T*T)*f7+B0*p7+s7['Sg7']
 s8={k:oldpoly(k,eighth) for k in ('c8','Sp8','Sc8','Sg8')};c8=s8['c8'];u8=-2*H*p8-T*f8/3+s8['Sp8'];gp8=-4*H*g8+(m-mus[8]*e+2*T*T)*f8+B0*p8+s8['Sg8']
 deriv={k:ring.P(0) for k in names};deriv.update(g8=gp8,p8=u8,f8=g8,g7=gp7,p7=u7,f7=g7,g6=gp6,p6=u6,f6=g6,g5=gp5,p5=u5,f5=g5,g4=gp4,g3=gp3,G=Gp,g=gp,H=Hp,T=Tp,Phi=T,e=-2*H*e,p=u,f=g,P=U,F=G,p3=u3,f3=g3,p4=u4,f4=g4)
 def ds(x):return sum((ring.P.cast(x).derivative(j)*deriv[k] for j,k in enumerate(names)),ring.P(0))
 c3p,c4p,c5p,c6p,c7p,c8p=ds(c3),ds(c4),ds(c5),ds(c6),ds(c7),ds(c8)
 def equations(ps,bs,fs,up,ub,gf,gfp):
  dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r);ep=(-2*ps).expzero();eb=(-2*bs).expzero()
  return ((bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df,
          up.dt(1)-bs.dt(1)*(H+up)+fs.dt(1)*(T+gf)/3,
          -ep*e*(fs.dt(r).dt(r)+(3*h+2*dp+db)*df)+eb*(Tp+gfp+(4*H+4*up-ub)*(T+gf))-m*(Phi+fs),
          eb*(6*(H+up)*(H+up)-(T+gf)*(T+gf)/2)-6+(Phi+fs)*(Phi+fs)*m/2-ep*e*(6*h*h+3*(ps.dt(r).dt(r)+3*h*dp)+3*dp*dp+df*df/2))
 arrays=[[0,p,P,p3,p4,p5,p6,p7,p8],[0,-2*p,c2-2*P,c3-2*p3,c4-2*p4,c5-2*p5,c6-2*p6,c7-2*p7,c8-2*p8],[0,f,F,f3,f4,f5,f6,f7,f8],[0,u,U,u3,u4,u5,u6,u7,u8],[0,-2*u,c2p-2*U,c3p-2*u3,c4p-2*u4,c5p-2*u5,c6p-2*u6,c7p-2*u7,c8p-2*u8],[0,g,G,g3,g4,g5,g6,g7,g8],[0,gp,Gp,gp3,gp4,gp5,gp6,gp7,gp8]]
 progress('lower_sources_constructed')
 rawT,rawM,rawK,rawR=equations(*map(S,arrays))
 progress('raw_equations_constructed')
 qt=96*p*p8+168*P*p7+216*p3*p6+240*p4*p5+16*f*f8+28*F*f7+36*f3*f6+40*f4*f5-48*p*c8-84*P*c7-108*p3*c6-120*p4*c5-120*p5*c4-108*p6*c3-84*p7*c2+28*c2*c7+36*c3*c6+40*c4*c5
 c9=-N9*qt;sp9=H*c9-rawM.a[9]/9;sc9=12*H*sp9-(12*H*H-T*T)*c9+rawR.a[9];sg9=T*ds(c9)+2*m*Phi*c9-6*T*sp9-rawK.a[9]
 checks=[]
 def clear(poly):
  indices=[names.index(n) for n in ('C','J','L','M','N6','N7','N8','N9')];nums=[r,4*r,r,r,r,r,r,r];dens=[2*(2*r-h),3*(3*r-h),4*(4*r-h),5*(5*r-h),6*(6*r-h),7*(7*r-h),8*(8*r-h),9*(9*r-h)]
  maxima=[max((a[i] for a in poly.t),default=0) for i in indices];out=ring.P(0)
  for powers,coef in poly.t.items():
   a=list(powers);ns=[a[i] for i in indices]
   for i in indices:a[i]=0
   term=ring.P({tuple(a):coef})
   for n,top,num,den in zip(ns,maxima,nums,dens):term=term*num**n*den**(top-n)
   out+=term
  return out
 def eq(a,b,label):
  assert clear(ring.P.cast(a)-b).iszero(),label;checks.append(label)
 for key,src in [('c9',c9),('Sp9',sp9),('Sc9',sc9),('Sg9',sg9)]:
  for new in ('p9','f9','g9'):eq(src.derivative(names.index(new)),0,'LOWER_ONLY:'+key+':'+new)
 bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
 cons={1:T*g-Tp*f+(2*T*T-3*(mus[1]+4*h*h)*e)*p,2:T*G-Tp*F+(2*T*T-3*(mus[2]+4*h*h)*e)*P-sc2,3:T*g3-Tp*f3+(2*T*T-3*(mus[3]+4*h*h)*e)*p3-s3['Sc3'],4:T*g4-Tp*f4+(2*T*T-3*(mus[4]+4*h*h)*e)*p4-s4['Sc4'],5:T*g5-Tp*f5+(2*T*T-3*(mus[5]+4*h*h)*e )*p5-s5['Sc5'],6:T*g6-Tp*f6+(2*T*T-3*(mus[6]+4*h*h)*e)*p6-s6['Sc6'],7:T*g7-Tp*f7+(2*T*T-3*(mus[7]+4*h*h)*e)*p7-s7['Sc7'],8:T*g8-Tp*f8+(2*T*T-3*(mus[8]+4*h*h)*e)*p8-s8['Sc8']}
 for n in range(1,9):
  eq(rawT.a[n],0,'LOWER_TRACE:'+str(n));eq(rawM.a[n],0,'LOWER_MIXED:'+str(n));eq(rawK.a[n],0,'LOWER_SCALAR:'+str(n));eq(rawR.a[n],-cons[n],'LOWER_RADIAL:'+str(n))
 eq(rawR.a[0],bg,'BACKGROUND_RADIAL');eq(rawK.a[0],0,'BACKGROUND_SCALAR');eq(rawT.a[9],r*r*qt,'TRACE9_POLYNOMIAL');eq(9*r*(9*r-h)*c9+rawT.a[9],0,'TRACE9_DIVISOR')
 u9=-2*H*p9-T*f9/3+sp9;gp9=-4*H*g9+(m-mus[9]*e+2*T*T)*f9+B0*p9+sg9
 fullT,fullM,fullK,fullR=equations(*[S(a+[b]) for a,b in zip(arrays,[p9,c9-2*p9,f9,u9,ds(c9)-2*u9,g9,gp9])])
 con9=T*g9-Tp*f9+(2*T*T-3*(mus[9]+4*h*h)*e)*p9-sc9
 for a,b,n in [(fullT.a[9],0,'FULL_TRACE9'),(fullM.a[9],0,'FULL_MIXED9'),(fullK.a[9],0,'FULL_SCALAR9'),(fullR.a[9],-con9,'FULL_RADIAL9')]:eq(a,b,n)
 progress('all_equation_checks_pass',checks=len(checks))
 residual=ds(sc9)+4*H*sc9-T*sg9-(2*T*T-3*(mus[9]+4*h*h)*e)*sp9
 reduced=residual;witnesses=[];cumulative=0
 for label,variable,constraint in [('g8',g8,cons[8]),('g7',g7,cons[7]),('g6',g6,cons[6]),('g5',g5,cons[5]),('g4',g4,cons[4]),('g3',g3,cons[3]),('G',G,cons[2]),('g',g,cons[1])]:
  index=names.index(label);degree=max((powers[index] for powers in reduced.t),default=0);B=constraint-T*variable;assert B.derivative(index).iszero(),'TRIANGULAR:'+label
  progress('group_start',variable=label,terms=len(reduced.t),degree=degree)
  coeff=group_coefficients(ring,reduced,index,degree)
  progress('group_done',variable=label,bucket_terms=[len(x.t) for x in coeff])
  new=ring.P(0);q=ring.P(0)
  for n,c in enumerate(coeff):
   new+=c*((-B)**n)*(T**(degree-n))
   for j in range(n):q+=c*(T**(degree-n))*((T*variable)**(n-1-j))*((-B)**j)
  progress('substitution_done',variable=label,terms=len(new.t))
  assert (T**degree*reduced-new-constraint*q).iszero(),'PSEUDO_RECONSTRUCTION:'+label
  assert new.derivative(index).iszero(),'VARIABLE_ELIMINATED:'+label
  checks.append('EXACT_PSEUDO_ELIMINATION:'+label);witnesses.append(dict(variable=label,power=degree,input=reduced.pack(),output=new.pack(),constraint=constraint.pack(),quotient=q.pack()));cumulative+=degree;reduced=new
 progress('elimination_complete',terms=len(reduced.t))
 lhs=clear(reduced)
 progress('denominators_cleared',terms=len(lhs.t))
 quotient,remainder=ring.divide(lhs,[bg])
 progress('background_reduction_done')
 if not remainder.iszero():
  err=AssertionError('NINTH_COMPATIBILITY_REDUCTION_INCONCLUSIVE');err.evidence=dict(remainder=remainder.pack(),checks=checks);raise err
 checks.append('NINTH_BIANCHI_REMAINDER')
 for label,bad in [('TRACE_C4_C5',rawT.a[9]-40*r*r*c4*c5),('TRACE_P1C8',rawT.a[9]+48*r*r*p*c8)]:
  assert not clear(rawT.a[9]-bad).iszero(),label;checks.append('MUTATION:'+label)
 return dict(pass_status=True,classification='NINTH_BULK_IDENTITIES_QUALIFIED',checks=checks,variables=names,sources={k:x.pack() for k,x in dict(c9=c9,Sp9=sp9,Sc9=sc9,Sg9=sg9,qT9=rawT.a[9],qM9_over_r=rawM.a[9],qK9=rawK.a[9],qR9=rawR.a[9]).items()},pseudo_elimination=witnesses,cumulative_T_power=cumulative,compatibility_reduction_lhs=lhs.pack(),compatibility_reduction_basis=[bg.pack()],compatibility_quotients=[x.pack() for x in quotient],compatibility_remainder=remainder.pack(),scope='Exact neutral ninth bulk sources on selected analytic background with nonidentically-zero T and continuation across isolated zeros. No ninth wall qualification, field solve, coefficient enclosure or physical trajectory.')

def verify_ring(ring,legacy):
 names=('a','b','c');pairs=0
 for mod in (ring,legacy):mod.NAMES=names;mod.N=3;mod.ZERO=(0,0,0)
 polys=[{}, {(0,0,0):Q(1)}, {(0,0,0):Q(-7,13)}, {(i%7,(i*3)%5,(i*11)%3):Q((-1)**i*(i+1),i%13+1) for i in range(70)}]
 for left in polys:
  for right in polys:
   a,b=ring.P(left),ring.P(right);x,y=legacy.P(left),legacy.P(right)
   for new,old in ((a+b,x+y),(a-b,x-y),(a*b,x*y)):
    assert new.t==old.t,'RING_EXACT_EQUIVALENCE';pairs+=1
 for left in polys:
  a,x=ring.P(left),legacy.P(left)
  for i in range(3):assert a.derivative(i).t==x.derivative(i).t;pairs+=1
  for n in range(4):assert (a**n).t==(x**n).t;pairs+=1
 return dict(pass_status=True,comparisons=pairs,term_cap=200000,product_pair_cap=1000000)
