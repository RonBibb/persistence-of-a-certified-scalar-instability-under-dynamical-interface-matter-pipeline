"""Exact neutral eighth bulk extraction and analytic-background compatibility."""
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
def qualify(ring,S,cubic,quartic,fifth,sixth,seventh,progress=lambda *a,**k:None):
 progress('qualification_start')
 names=('g7','g6','g5','g4','g3','G','g','H','T','Phi','e','p','f','P','F','p3','f3','p4','f4','m','C','J','L','M','r','h','p5','f5','N6','p6','f6','N7','p7','f7','N8','p8','f8','g8')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(j) for j,k in enumerate(names)}
 g7,g6,g5,g4,g3,G,g,H,T,Phi,e,p,f,P,F,p3,f3,p4,f4,m,C,J,L,M,r,h,p5,f5,N6,p6,f6,N7,p7,f7,N8,p8,f8,g8=[v[k] for k in names]
 mus={n:-n*r*(n*r+3*h) for n in range(1,9)};Hp=-T*T/3-h*h*e;Tp=m*Phi-4*H*T;B0=12*H*T-4*m*Phi
 u=-2*H*p-T*f/3;gp=-4*H*g+(m-mus[1]*e+2*T*T)*f+B0*p
 c2=-C*(6*p*p+f*f);c2p=-C*(12*p*u+2*f*g);sp2=H*c2-p*u-f*g/6
 qk2=(4*m-6*mus[1]*e)*p*f+6*u*g-8*m*Phi*p*p;sg2=T*c2p+2*m*Phi*c2-6*T*sp2-qk2
 qr2=6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2-e*((12*h*h-3*r*r-18*h*r)*p*p+r*r*f*f/2)
 sc2=12*H*sp2-(12*H*H-T*T)*c2+qr2;U=-2*H*P-T*F/3+sp2;Gp=-4*H*G+(m-mus[2]*e+2*T*T)*F+B0*P+sg2
 params=dict(m2=m,k=h*h,rate=r,h=h,mu1=mus[1],mu2=mus[2],mu3=mus[3],c_factor=C,c3_factor=J,c4_factor=L)
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params);c3=s3['c3'];u3=-2*H*p3-T*f3/3+s3['Sp3'];gp3=-4*H*g3+(m-mus[3]*e+2*T*T)*f3+B0*p3+s3['Sg3']
 s4=quartic.quartic(H,T,Phi,e,p,f,g,P,F,G,p3,f3,g3,params,cubic);c4=s4['c4'];u4=-2*H*p4-T*f4/3+s4['Sp4'];gp4=-4*H*g4+(m-mus[4]*e+2*T*T)*f4+B0*p4+s4['Sg4']
 def oldpoly(key,record=fifth):
  out=ring.P(0)
  for row in record['sources'][key]:
   term=ring.P(Q(row['coefficient']))
   for name,power in zip(record['variables'],row['powers']):
    if power:term*=v[name]**power
   out+=term
  return out
 s5={k:oldpoly(k) for k in ('c5','Sp5','Sc5','Sg5')};c5=s5['c5'];u5=-2*H*p5-T*f5/3+s5['Sp5'];gp5=-4*H*g5+(m-mus[5]*e+2*T*T)*f5+B0*p5+s5['Sg5']
 s6={k:oldpoly(k,sixth) for k in ('c6','Sp6','Sc6','Sg6')};c6=s6['c6'];u6=-2*H*p6-T*f6/3+s6['Sp6'];gp6=-4*H*g6+(m-mus[6]*e+2*T*T)*f6+B0*p6+s6['Sg6']
 s7={k:oldpoly(k,seventh) for k in ('c7','Sp7','Sc7','Sg7')};c7=s7['c7'];u7=-2*H*p7-T*f7/3+s7['Sp7'];gp7=-4*H*g7+(m-mus[7]*e+2*T*T)*f7+B0*p7+s7['Sg7']
 deriv={k:ring.P(0) for k in names};deriv.update(g7=gp7,p7=u7,f7=g7,g6=gp6,p6=u6,f6=g6,g5=gp5,p5=u5,f5=g5,g4=gp4,g3=gp3,G=Gp,g=gp,H=Hp,T=Tp,Phi=T,e=-2*H*e,p=u,f=g,P=U,F=G,p3=u3,f3=g3,p4=u4,f4=g4)
 def ds(x):return sum((ring.P.cast(x).derivative(j)*deriv[k] for j,k in enumerate(names)),ring.P(0))
 c3p,c4p,c5p,c6p,c7p=ds(c3),ds(c4),ds(c5),ds(c6),ds(c7)
 def equations(ps,bs,fs,up,ub,gf,gfp):
  dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r);ep=(-2*ps).expzero();eb=(-2*bs).expzero()
  return ((bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df,
          up.dt(1)-bs.dt(1)*(H+up)+fs.dt(1)*(T+gf)/3,
          -ep*e*(fs.dt(r).dt(r)+(3*h+2*dp+db)*df)+eb*(Tp+gfp+(4*H+4*up-ub)*(T+gf))-m*(Phi+fs),
          eb*(6*(H+up)*(H+up)-(T+gf)*(T+gf)/2)-6+(Phi+fs)*(Phi+fs)*m/2-ep*e*(6*h*h+3*(ps.dt(r).dt(r)+3*h*dp)+3*dp*dp+df*df/2))
 arrays=[[0,p,P,p3,p4,p5,p6,p7],[0,-2*p,c2-2*P,c3-2*p3,c4-2*p4,c5-2*p5,c6-2*p6,c7-2*p7],[0,f,F,f3,f4,f5,f6,f7],[0,u,U,u3,u4,u5,u6,u7],[0,-2*u,c2p-2*U,c3p-2*u3,c4p-2*u4,c5p-2*u5,c6p-2*u6,c7p-2*u7],[0,g,G,g3,g4,g5,g6,g7],[0,gp,Gp,gp3,gp4,gp5,gp6,gp7]]
 progress('lower_sources_constructed')
 rawT,rawM,rawK,rawR=equations(*map(S,arrays))
 progress('raw_equations_constructed')
 qt=84*p*p7+144*P*p6+180*p3*p5+96*p4*p4+14*f*f7+24*F*f6+30*f3*f5+16*f4*f4-42*p*c7-72*P*c6-90*p3*c5-96*p4*c4-90*p5*c3-72*p6*c2+24*c2*c6+30*c3*c5+16*c4*c4
 c8=-N8*qt;sp8=H*c8-rawM.a[8]/8;sc8=12*H*sp8-(12*H*H-T*T)*c8+rawR.a[8];sg8=T*ds(c8)+2*m*Phi*c8-6*T*sp8-rawK.a[8]
 checks=[]
 def clear(poly):
  indices=[names.index(n) for n in ('C','J','L','M','N6','N7','N8')];nums=[r,4*r,r,r,r,r,r];dens=[2*(2*r-h),3*(3*r-h),4*(4*r-h),5*(5*r-h),6*(6*r-h),7*(7*r-h),8*(8*r-h)]
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
 for key,src in [('c8',c8),('Sp8',sp8),('Sc8',sc8),('Sg8',sg8)]:
  for new in ('p8','f8','g8'):eq(src.derivative(names.index(new)),0,'LOWER_ONLY:'+key+':'+new)
 bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
 cons={1:T*g-Tp*f+(2*T*T-3*(mus[1]+4*h*h)*e)*p,2:T*G-Tp*F+(2*T*T-3*(mus[2]+4*h*h)*e)*P-sc2,3:T*g3-Tp*f3+(2*T*T-3*(mus[3]+4*h*h)*e)*p3-s3['Sc3'],4:T*g4-Tp*f4+(2*T*T-3*(mus[4]+4*h*h)*e)*p4-s4['Sc4'],5:T*g5-Tp*f5+(2*T*T-3*(mus[5]+4*h*h)*e )*p5-s5['Sc5'],6:T*g6-Tp*f6+(2*T*T-3*(mus[6]+4*h*h)*e)*p6-s6['Sc6'],7:T*g7-Tp*f7+(2*T*T-3*(mus[7]+4*h*h)*e)*p7-s7['Sc7']}
 for n in range(1,8):
  eq(rawT.a[n],0,'LOWER_TRACE:'+str(n));eq(rawM.a[n],0,'LOWER_MIXED:'+str(n));eq(rawK.a[n],0,'LOWER_SCALAR:'+str(n));eq(rawR.a[n],-cons[n],'LOWER_RADIAL:'+str(n))
 eq(rawR.a[0],bg,'BACKGROUND_RADIAL');eq(rawK.a[0],0,'BACKGROUND_SCALAR');eq(rawT.a[8],r*r*qt,'TRACE8_POLYNOMIAL');eq(8*r*(8*r-h)*c8+rawT.a[8],0,'TRACE8_DIVISOR')
 u8=-2*H*p8-T*f8/3+sp8;gp8=-4*H*g8+(m-mus[8]*e+2*T*T)*f8+B0*p8+sg8
 fullT,fullM,fullK,fullR=equations(*[S(a+[b]) for a,b in zip(arrays,[p8,c8-2*p8,f8,u8,ds(c8)-2*u8,g8,gp8])])
 con8=T*g8-Tp*f8+(2*T*T-3*(mus[8]+4*h*h)*e)*p8-sc8
 for a,b,n in [(fullT.a[8],0,'FULL_TRACE8'),(fullM.a[8],0,'FULL_MIXED8'),(fullK.a[8],0,'FULL_SCALAR8'),(fullR.a[8],-con8,'FULL_RADIAL8')]:eq(a,b,n)
 progress('all_equation_checks_pass',checks=len(checks))
 residual=ds(sc8)+4*H*sc8-T*sg8-(2*T*T-3*(mus[8]+4*h*h)*e)*sp8
 reduced=residual;witnesses=[];cumulative=0
 for label,variable,constraint in [('g7',g7,cons[7]),('g6',g6,cons[6]),('g5',g5,cons[5]),('g4',g4,cons[4]),('g3',g3,cons[3]),('G',G,cons[2]),('g',g,cons[1])]:
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
  err=AssertionError('EIGHTH_COMPATIBILITY_REDUCTION_INCONCLUSIVE');err.evidence=dict(remainder=remainder.pack(),checks=checks);raise err
 checks.append('EIGHTH_BIANCHI_REMAINDER')
 for label,bad in [('TRACE_C4_SQUARED',rawT.a[8]-16*r*r*c4*c4),('TRACE_P1C7',rawT.a[8]+42*r*r*p*c7)]:
  assert not clear(rawT.a[8]-bad).iszero(),label;checks.append('MUTATION:'+label)
 return dict(pass_status=True,classification='EIGHTH_BULK_IDENTITIES_QUALIFIED',checks=checks,variables=names,sources={k:x.pack() for k,x in dict(c8=c8,Sp8=sp8,Sc8=sc8,Sg8=sg8,qT8=rawT.a[8],qM8_over_r=rawM.a[8],qK8=rawK.a[8],qR8=rawR.a[8]).items()},pseudo_elimination=witnesses,cumulative_T_power=cumulative,compatibility_reduction_lhs=lhs.pack(),compatibility_reduction_basis=[bg.pack()],compatibility_quotients=[x.pack() for x in quotient],compatibility_remainder=remainder.pack(),scope='Exact neutral eighth bulk sources on selected analytic background with nonidentically-zero T and continuation across isolated zeros. No eighth wall qualification, field solve, coefficient enclosure or physical trajectory.')
