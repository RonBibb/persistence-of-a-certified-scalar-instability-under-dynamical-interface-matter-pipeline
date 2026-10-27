"""Closed neutral quartic bulk loads over any commutative coefficient algebra."""
def quartic(H,T,Phi,e,p,f,g,P,F,G,p3,f3,g3,params,cubic):
 zero=p*0;m=zero+params['m2'];k=zero+params['k'];r=zero+params['rate'];h=zero+params['h']
 mu1=zero+params['mu1'];mu2=zero+params['mu2'];mu3=zero+params['mu3']
 u=-2*H*p-T*f/3;gp=-4*H*g+(m-mu1*e+2*T*T)*f+(12*H*T-4*m*Phi)*p
 c2=-(6*p*p+f*f)*params['c_factor'];cp=-(12*p*u+2*f*g)*params['c_factor']
 sp2=H*c2-p*u-f*g/6;qk2=(4*m-6*mu1*e)*p*f+6*u*g-8*m*Phi*p*p
 sg2=T*cp+2*m*Phi*c2-6*T*sp2-qk2
 U=-2*H*P-T*F/3+sp2;Gp=-4*H*G+(m-mu2*e+2*T*T)*F+(12*H*T-4*m*Phi)*P+sg2
 s3=cubic.cubic(H,T,Phi,e,p,f,g,P,F,G,params);c3=s3['c3']
 c3p=-(6*u*P+6*p*U+g*F+f*G-3*u*c2-3*p*cp)*params['c3_factor']
 u3=-2*H*p3-T*f3/3+s3['Sp3'];gp3=-4*H*g3+(m-mu3*e+2*T*T)*f3+(12*H*T-4*m*Phi)*p3+s3['Sg3']
 inner=36*p*p3+24*P*P+6*f*f3+4*F*F-18*p*c3-24*P*c2+4*c2*c2
 innerp=36*(u*p3+p*u3)+48*P*U+6*(g*f3+f*g3)+8*F*G-18*(u*c3+p*c3p)-24*(U*c2+P*cp)+8*c2*cp
 c4=-inner*params['c4_factor'];c4p=-innerp*params['c4_factor']
 qm=2*p*u3+(4*P-2*c2)*U+(6*p3-3*c3)*u+(f*g3+2*F*G+3*f3*g)/3
 sp4=H*c4-qm/4
 a2=-2*c2+4*P;a3=-2*c3+4*p3
 be1=4*p;be2=a2+8*p*p;be3=a3+4*p*a2+32*p*p*p/3
 be4=4*p*a3+a2*a2/2+8*p*p*a2+32*p*p*p*p/3
 pe1=-2*p;pe2=-2*P+2*p*p;pe3=-2*p3+4*p*P-4*p*p*p/3
 pe4=4*p*p3+2*P*P-4*p*p*P+2*p*p*p*p/3
 ka1=gp+4*H*g+6*u*T
 ka2=Gp+4*H*G+(6*U-cp)*T+6*u*g
 ka3=gp3+4*H*g3+(6*u3-c3p)*T+(6*U-cp)*g+6*u*G
 ka4=(6*u3-c3p)*g+(6*U-cp)*G+6*u*g3
 kt1=-mu1*f;kt2=-mu2*F;kt3=-mu3*f3+2*r*r*c2*f;kt4=4*r*r*c2*F+3*r*r*c3*f
 qk=ka4+be1*ka3+be2*ka2+be3*ka1+be4*m*Phi-e*(kt4+pe1*kt3+pe2*kt2+pe3*kt1)
 qr0=6*H*H-T*T/2;qr1=12*H*u-T*g;qr2=12*H*U-T*G+6*u*u-g*g/2
 qr3=12*H*u3-T*g3+12*u*U-g*G;qr4=12*u*u3+6*U*U-g*g3-G*G/2
 rt1=-3*mu1*p;rt2=-3*mu2*P+3*r*r*p*p+r*r*f*f/2
 rt3=-3*mu3*p3+12*r*r*p*P+2*r*r*f*F
 rt4=18*r*r*p*p3+12*r*r*P*P+3*r*r*f*f3+2*r*r*F*F
 qr=qr4+be1*qr3+be2*qr2+be3*qr1+be4*qr0+m*(f*f3+F*F/2)-e*(rt4+pe1*rt3+pe2*rt2+pe3*rt1+pe4*6*k)
 return dict(c4=c4,Sp4=sp4,Sc4=12*H*sp4-(12*H*H-T*T)*c4+qr,Sg4=T*c4p+2*m*Phi*c4-6*T*sp4-qk,qT4=r*r*inner,qM4_over_r=qm,qK4=qk,qR4=qr)

