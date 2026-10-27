"""General-rate neutral degree-four bulk identities, no physical integration."""
from fractions import Fraction as Q

def qualify(ring,S,cubic,closed):
 names=('g3','G','g','H','T','Phi','e','p','f','P','F','p3','f3','m','C','J','L','r','h')
 ring.NAMES=names;ring.N=len(names);ring.ZERO=(0,)*len(names)
 v={k:ring.variable(j) for j,k in enumerate(names)}
 g3,G,g,H,T,Phi,e,p,f,P,F,p3,f3,m,C,J,L,r,h=[v[k] for k in names]
 mu1=-r*(r+3*h);mu2=-2*r*(2*r+3*h);mu3=-3*r*(3*r+3*h);mu4=-4*r*(4*r+3*h)
 Hp=-T*T/3-h*h*e;Tp=m*Phi-4*H*T;u=-2*H*p-T*f/3;B0=12*H*T-4*m*Phi
 gp=-4*H*g+(m-mu1*e+2*T*T)*f+B0*p
 c2=-C*(6*p*p+f*f);c2p=-C*(12*p*u+2*f*g)
 sp2=H*c2-p*u-f*g/6
 qk2=(4*m-6*mu1*e)*p*f+6*u*g-8*m*Phi*p*p
 sg2=T*c2p+2*m*Phi*c2-6*T*sp2-qk2
 qr2=6*u*u-g*g/2+4*p*(12*H*u-T*g)+8*p*p*(6*H*H-T*T/2)+m*f*f/2-e*((12*h*h-3*r*r-18*h*r)*p*p+r*r*f*f/2)
 sc2=12*H*sp2-(12*H*H-T*T)*c2+qr2
 U=-2*H*P-T*F/3+sp2;Gp=-4*H*G+(m-mu2*e+2*T*T)*F+B0*P+sg2
 params=dict(m2=m,k=h*h,rate=r,h=h,mu1=mu1,mu2=mu2,mu3=mu3,c_factor=C,c3_factor=J,c4_factor=L)
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params);c3=s3['c3']
 u3=-2*H*p3-T*f3/3+s3['Sp3'];gp3=-4*H*g3+(m-mu3*e+2*T*T)*f3+B0*p3+s3['Sg3']
 deriv=(gp3,Gp,gp,Hp,Tp,T,-2*H*e,u,g,U,G,u3,g3,ring.P(0),ring.P(0),ring.P(0),ring.P(0),ring.P(0),ring.P(0))
 def ds(x):return sum((ring.P.cast(x).derivative(j)*q for j,q in enumerate(deriv)),ring.P(0))
 c3p=ds(c3)
 ps=S([0,p,P,p3]);bs=S([0,-2*p,c2-2*P,c3-2*p3]);fs=S([0,f,F,f3])
 up=S([0,u,U,u3]);ub=S([0,-2*u,c2p-2*U,c3p-2*u3]);gf=S([0,g,G,g3]);gfp=S([0,gp,Gp,gp3])
 dp,db,df=ps.dt(r),bs.dt(r),fs.dt(r);ep=(-2*ps).expzero();eb=(-2*bs).expzero()
 rawT=(bs+2*ps).dt(r).dt(r)-h*(bs+2*ps).dt(r)+db*db-2*dp*db-2*dp*dp+df*df
 # Remove the common factor r analytically in the mixed equation.
 rawM=up.dt(1)-bs.dt(1)*(H+up)+fs.dt(1)*(T+gf)/3
 rawK=-ep*e*(fs.dt(r).dt(r)+(3*h+2*dp+db)*df)+eb*(Tp+gfp+(4*H+4*up-ub)*(T+gf))-m*(Phi+fs)
 rawR=eb*(6*(H+up)*(H+up)-(T+gf)*(T+gf)/2)-6+(Phi+fs)*(Phi+fs)*m/2-ep*e*(6*h*h+3*(ps.dt(r).dt(r)+3*h*dp)+3*dp*dp+df*df/2)
 qt=36*p*p3+24*P*P+6*f*f3+4*F*F-18*p*c3-24*P*c2+4*c2*c2
 c4=-L*qt;sp4=H*c4-rawM.a[4]/4
 sc4=12*H*sp4-(12*H*H-T*T)*c4+rawR.a[4]
 sg4=T*ds(c4)+2*m*Phi*c4-6*T*sp4-rawK.a[4]
 checks=[]
 def clear(poly):
  indices=[names.index(n) for n in ('C','J','L')];nums=[r,4*r,r];dens=[2*(2*r-h),3*(3*r-h),4*(4*r-h)]
  maxima=[max((a[i] for a in poly.t),default=0) for i in indices];out=ring.P(0)
  for powers,coef in poly.t.items():
   a=list(powers);ns=[a[i] for i in indices]
   for i in indices:a[i]=0
   term=ring.P({tuple(a):coef})
   for n,top,num,den in zip(ns,maxima,nums,dens):term=term*num**n*den**(top-n)
   out+=term
  return out
 def eq(a,b,label):
  assert clear(ring.P.cast(a)-b).iszero(),label
  checks.append(label)
 bg=6*H*H-T*T/2-6+m*Phi*Phi/2-6*h*h*e
 con1=T*g-Tp*f+(2*T*T-3*(mu1+4*h*h)*e)*p
 con2=T*G-Tp*F+(2*T*T-3*(mu2+4*h*h)*e)*P-sc2
 con3=T*g3-Tp*f3+(2*T*T-3*(mu3+4*h*h)*e)*p3-s3['Sc3']
 for n,con in ((1,con1),(2,con2),(3,con3)):
  eq(rawT.a[n],0,f'LOWER_TRACE:{n}');eq(rawM.a[n],0,f'LOWER_MIXED:{n}');eq(rawK.a[n],0,f'LOWER_SCALAR:{n}');eq(rawR.a[n],-con,f'LOWER_RADIAL:{n}')
 eq(rawR.a[0],bg,'BACKGROUND_RADIAL');eq(rawK.a[0],0,'BACKGROUND_SCALAR')
 eq(rawT.a[4],r*r*qt,'INDEPENDENT_TRACE4')
 eq(4*r*(4*r-h)*c4+rawT.a[4],0,'TRACE4_DIVISOR')
 eq(4*(sp4-H*c4)+rawM.a[4],0,'MIXED4_DIVISOR')
 direct=dict(c4=c4,Sp4=sp4,Sc4=sc4,Sg4=sg4,qT4=rawT.a[4],qM4_over_r=rawM.a[4],qK4=rawK.a[4],qR4=rawR.a[4])
 formula=closed.quartic(H,T,Phi,e,p,f,g,P,F,G,p3,f3,g3,params,cubic)
 for key in direct:eq(direct[key],formula[key],'DIRECT_CLOSED:'+key)
 residual=ds(sc4)+4*H*sc4-T*sg4-(2*T*T-3*(mu4+4*h*h)*e)*sp4
 witnesses=[];reduced=residual;cumulative=0
 for label,variable,constraint in [('g3',g3,con3),('G',G,con2),('g',g,con1)]:
  index=names.index(label);degree=max((powers[index] for powers in reduced.t),default=0)
  B=constraint-T*variable
  assert B.derivative(index).iszero(),'TRIANGULAR_CONSTRAINT:'+label
  coeff=[ring.P(0) for _ in range(degree+1)]
  for powers,value in reduced.t.items():
   powers=list(powers);n=powers[index];powers[index]=0
   coeff[n]+=ring.P({tuple(powers):value})
  new=ring.P(0);q=ring.P(0)
  for n,c in enumerate(coeff):
   new+=c*((-B)**n)*(T**(degree-n))
   for j in range(n):q+=c*(T**(degree-n))*((T*variable)**(n-1-j))*((-B)**j)
  assert (T**degree*reduced-new-constraint*q).iszero(),'PSEUDO_RECONSTRUCTION:'+label
  assert new.derivative(index).iszero(),'VARIABLE_ELIMINATED:'+label
  checks.append('EXACT_PSEUDO_ELIMINATION:'+label)
  witnesses.append(dict(variable=label,power=degree,input=reduced.pack(),output=new.pack(),constraint=constraint.pack(),quotient=q.pack()))
  cumulative+=degree;reduced=new
 reduction_lhs=clear(reduced);reduction_basis=[bg]
 quotient,remainder=ring.divide(reduction_lhs,reduction_basis)
 cleared=remainder
 if not cleared.iszero():
  err=AssertionError('QUARTIC_COMPATIBILITY_REDUCTION_INCONCLUSIVE')
  err.evidence=dict(remainder=cleared.pack(),checks=checks)
  raise err
 checks.append('QUARTIC_BIANCHI_REMAINDER')
 for label,bad in [('TRACE_C2_SQUARED',rawT.a[4]-4*r*r*c2*c2),('TRACE_P1C3',rawT.a[4]+18*r*r*p*c3)]:
  assert not clear(rawT.a[4]-bad).iszero(),label
  checks.append('MUTATION:'+label)
 return dict(pass_status=True,classification='QUARTIC_BULK_IDENTITIES_QUALIFIED',checks=checks,variables=names,sources={k:x.pack() for k,x in dict(c4=c4,Sp4=sp4,Sc4=sc4,Sg4=sg4,qT4=rawT.a[4],qM4_over_r=rawM.a[4],qK4=rawK.a[4],qR4=rawR.a[4]).items()},pseudo_elimination=witnesses,cumulative_T_power=cumulative,compatibility_reduction_lhs=reduction_lhs.pack(),compatibility_reduction_basis=[x.pack() for x in reduction_basis],compatibility_quotients=[x.pack() for x in quotient],compatibility_remainder=cleared.pack(),scope='Exact neutral quartic sources and compatibility along the selected analytic background, using initial nonzero T and continuation across isolated T zeros; not unrestricted algebraic T=0 data. No quartic field solution or physical trajectory.')

