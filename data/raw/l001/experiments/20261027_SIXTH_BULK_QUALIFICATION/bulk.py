"""Exact neutral sixth bulk extraction and analytic-background compatibility."""
from fractions import Fraction as Q
def qualify(ring,S,cubic,quartic,fifth):
 names=('g5','g4','g3','G','g','H','T','Phi','e','p','f','P','F','p3','f3','p4','f4','m','C','J','L','M','r','h','p5','f5','N6','p6','f6','g6')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names);v={k:ring.variable(j) for j,k in enumerate(names)}
 g5,g4,g3,G,g,H,T,Phi,e,p,f,P,F,p3,f3,p4,f4,m,C,J,L,M,r,h,p5,f5,N6,p6,f6,g6=[v[k] for k in names]
 mus={n:-n*r*(n*r+3*h) for n in range(1,7)};Hp=-T*T/3-h*h*e;Tp=m*Phi-4*H*T;B0=12*H*T-4*m*Phi
 u=-2*H*p-T*f/3;gp=-4*H*g+(m-mus[1]*e+2*T*T)*f+B0*p
 c2=-C*(6*p*p+f*f);c2p=-C*(12*p*u+2*f*g);sp2=H*c2-p*u-f*g/6
 qk2=(4*m-6*mus[1]*e)*p*f+6*u*g-8*m*Phi*p*p;sg2=T*c2p+2*m*Phi*c2-6*T*sp2-qk2
 qr2=6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2-e*((12*h*h-3*r*r-18*h*r)*p*p+r*r*f*f/2)
 sc2=12*H*sp2-(12*H*H-T*T)*c2+qr2;U=-2*H*P-T*F/3+sp2;Gp=-4*H*G+(m-mus[2]*e+2*T*T)*F+B0*P+sg2
 params=dict(m2=m,k=h*h,rate=r,h=h,mu1=mus[1],mu2=mus[2],mu3=mus[3],c_factor=C,c3_factor=J,c4_factor=L)
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params);c3=s3['c3'];u3=-2*H*p3-T*f3/3+s3['Sp3'];gp3=-4*H*g3+(m-mus[3]*e+2*T*T)*f3+B0*p3+s3['Sg3']
 s4=quartic.quartic(H,T,Phi,e,p,f,g,P,F,G,p3,f3,g3,params,cubic);c4=s4['c4'];u4=-2*H*p4-T*f4/3+s4['Sp4'];gp4=-4*H*g4+(m-mus[4]*e+2*T*T)*f4+B0*p4+s4['Sg4']
 def oldpoly(key):
  out=ring.P(0)
  for row in fifth['sources'][key]:
   term=ring.P(Q(row['coefficient']))
   for name,power in zip(fifth['variables'],row['powers']):
    if power:term*=v[name]**power
   out+=term
  return out
 s5={k:oldpoly(k) for k in ('c5','Sp5','Sc5','Sg5')};c5=s5['c5'];u5=-2*H*p5-T*f5/3+s5['Sp5'];gp5=-4*H*g5+(m-mus[5]*e+2*T*T)*f5+B0*p5+s5['Sg5']
 deriv={k:ring.P(0) for k in names};deriv.update(g5=gp5,p5=u5,f5=g5,g4=gp4,g3=gp3,G=Gp,g=gp,H=Hp,T=Tp,Phi=T,e=-2*H*e,p=u,f=g,P=U,F=G,p3=u3,f3=g3,p4=u4,f4=g4)
 def ds(x):return sum((ring.P.cast(x).derivative(j)*deriv[k] for j,k in enumerate(names)),ring.P(0))
 c3p,c4p,c5p=ds(c3),ds(c4),ds(c5)
 def equations(ps,bs,fs,up,ub,gf,gfp):
  dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r);ep=(-2*ps).expzero();eb=(-2*bs).expzero()
  return ((bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df,
          up.dt(1)-bs.dt(1)*(H+up)+fs.dt(1)*(T+gf)/3,
          -ep*e*(fs.dt(r).dt(r)+(3*h+2*dp+db)*df)+eb*(Tp+gfp+(4*H+4*up-ub)*(T+gf))-m*(Phi+fs),
          eb*(6*(H+up)*(H+up)-(T+gf)*(T+gf)/2)-6+(Phi+fs)*(Phi+fs)*m/2-ep*e*(6*h*h+3*(ps.dt(r).dt(r)+3*h*dp)+3*dp*dp+df*df/2))
 arrays=[[0,p,P,p3,p4,p5],[0,-2*p,c2-2*P,c3-2*p3,c4-2*p4,c5-2*p5],[0,f,F,f3,f4,f5],[0,u,U,u3,u4,u5],[0,-2*u,c2p-2*U,c3p-2*u3,c4p-2*u4,c5p-2*u5],[0,g,G,g3,g4,g5],[0,gp,Gp,gp3,gp4,gp5]]
 rawT,rawM,rawK,rawR=equations(*map(S,arrays))
 qt=60*p*p5+96*P*p4+54*p3*p3+10*f*f5+16*F*f4+9*f3*f3-30*p*c5-48*P*c4-54*p3*c3-48*p4*c2+16*c2*c4+9*c3*c3
 c6=-N6*qt;sp6=H*c6-rawM.a[6]/6;sc6=12*H*sp6-(12*H*H-T*T)*c6+rawR.a[6];sg6=T*ds(c6)+2*m*Phi*c6-6*T*sp6-rawK.a[6]
 checks=[]
 def clear(poly):
  indices=[names.index(n) for n in ('C','J','L','M','N6')];nums=[r,4*r,r,r,r];dens=[2*(2*r-h),3*(3*r-h),4*(4*r-h),5*(5*r-h),6*(6*r-h)]
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
 for key,src in [('c6',c6),('Sp6',sp6),('Sc6',sc6),('Sg6',sg6)]:
  for new in ('p6','f6','g6'):eq(src.derivative(names.index(new)),0,'LOWER_ONLY:'+key+':'+new)
 bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
 cons={1:T*g-Tp*f+(2*T*T-3*(mus[1]+4*h*h)*e)*p,2:T*G-Tp*F+(2*T*T-3*(mus[2]+4*h*h)*e)*P-sc2,3:T*g3-Tp*f3+(2*T*T-3*(mus[3]+4*h*h)*e)*p3-s3['Sc3'],4:T*g4-Tp*f4+(2*T*T-3*(mus[4]+4*h*h)*e)*p4-s4['Sc4'],5:T*g5-Tp*f5+(2*T*T-3*(mus[5]+4*h*h)*e)*p5-s5['Sc5']}
 for n in range(1,6):
  eq(rawT.a[n],0,'LOWER_TRACE:'+str(n));eq(rawM.a[n],0,'LOWER_MIXED:'+str(n));eq(rawK.a[n],0,'LOWER_SCALAR:'+str(n));eq(rawR.a[n],-cons[n],'LOWER_RADIAL:'+str(n))
 eq(rawR.a[0],bg,'BACKGROUND_RADIAL');eq(rawK.a[0],0,'BACKGROUND_SCALAR');eq(rawT.a[6],r*r*qt,'TRACE6_POLYNOMIAL');eq(6*r*(6*r-h)*c6+rawT.a[6],0,'TRACE6_DIVISOR')
 u6=-2*H*p6-T*f6/3+sp6;gp6=-4*H*g6+(m-mus[6]*e+2*T*T)*f6+B0*p6+sg6
 fullT,fullM,fullK,fullR=equations(*[S(a+[b]) for a,b in zip(arrays,[p6,c6-2*p6,f6,u6,ds(c6)-2*u6,g6,gp6])])
 con6=T*g6-Tp*f6+(2*T*T-3*(mus[6]+4*h*h)*e)*p6-sc6
 for a,b,n in [(fullT.a[6],0,'FULL_TRACE6'),(fullM.a[6],0,'FULL_MIXED6'),(fullK.a[6],0,'FULL_SCALAR6'),(fullR.a[6],-con6,'FULL_RADIAL6')]:eq(a,b,n)
 residual=ds(sc6)+4*H*sc6-T*sg6-(2*T*T-3*(mus[6]+4*h*h)*e)*sp6
 reduced=residual;witnesses=[];cumulative=0
 for label,variable,constraint in [('g5',g5,cons[5]),('g4',g4,cons[4]),('g3',g3,cons[3]),('G',G,cons[2]),('g',g,cons[1])]:
  index=names.index(label);degree=max((powers[index] for powers in reduced.t),default=0);B=constraint-T*variable;assert B.derivative(index).iszero(),'TRIANGULAR:'+label
  coeff=[ring.P(0) for _ in range(degree+1)]
  for powers,value in reduced.t.items():
   powers=list(powers);n=powers[index];powers[index]=0;coeff[n]+=ring.P({tuple(powers):value})
  new=ring.P(0);q=ring.P(0)
  for n,c in enumerate(coeff):
   new+=c*((-B)**n)*(T**(degree-n))
   for j in range(n):q+=c*(T**(degree-n))*((T*variable)**(n-1-j))*((-B)**j)
  assert (T**degree*reduced-new-constraint*q).iszero(),'PSEUDO_RECONSTRUCTION:'+label
  assert new.derivative(index).iszero(),'VARIABLE_ELIMINATED:'+label
  checks.append('EXACT_PSEUDO_ELIMINATION:'+label);witnesses.append(dict(variable=label,power=degree,input=reduced.pack(),output=new.pack(),constraint=constraint.pack(),quotient=q.pack()));cumulative+=degree;reduced=new
 lhs=clear(reduced);quotient,remainder=ring.divide(lhs,[bg])
 if not remainder.iszero():
  err=AssertionError('SIXTH_COMPATIBILITY_REDUCTION_INCONCLUSIVE');err.evidence=dict(remainder=remainder.pack(),checks=checks);raise err
 checks.append('SIXTH_BIANCHI_REMAINDER')
 for label,bad in [('TRACE_C3_SQUARED',rawT.a[6]-9*r*r*c3*c3),('TRACE_P1C5',rawT.a[6]+30*r*r*p*c5)]:
  assert not clear(rawT.a[6]-bad).iszero(),label;checks.append('MUTATION:'+label)
 return dict(pass_status=True,classification='SIXTH_BULK_IDENTITIES_QUALIFIED',checks=checks,variables=names,sources={k:x.pack() for k,x in dict(c6=c6,Sp6=sp6,Sc6=sc6,Sg6=sg6,qT6=rawT.a[6],qM6_over_r=rawM.a[6],qK6=rawK.a[6],qR6=rawR.a[6]).items()},pseudo_elimination=witnesses,cumulative_T_power=cumulative,compatibility_reduction_lhs=lhs.pack(),compatibility_reduction_basis=[bg.pack()],compatibility_quotients=[x.pack() for x in quotient],compatibility_remainder=remainder.pack(),scope='Exact neutral sixth bulk sources on selected analytic background with nonidentically-zero T and continuation across isolated zeros. No sixth wall qualification, field solve, coefficient enclosure or physical trajectory.')
