"""Generic scalar/jet cubic sources; all coefficients exact and regular at T=0."""
def cubic(H,T,Phi,e,p,f,g,P,F,G,params):
    zero=p*0;m=zero+params['m2'];k=zero+params['k'];r=zero+params['rate'];h=zero+params['h'];mu1=zero+params['mu1'];mu2=zero+params['mu2']
    u=-2*H*p-T*f/3
    c2=-(6*p*p+f*f)*params['c_factor'];cp=-(12*p*u+2*f*g)*params['c_factor']
    Sp2=H*c2-p*u-f*g/6
    gp=-4*H*g+(m-mu1*e+2*T*T)*f+(12*H*T-4*m*Phi)*p
    qK2=(4*m-6*mu1*e)*p*f+6*u*g-8*m*Phi*p*p
    Sg2=T*cp+2*m*Phi*c2-6*T*Sp2-qK2
    U=-2*H*P-T*F/3+Sp2
    Gp=-4*H*G+(m-mu2*e+2*T*T)*F+(12*H*T-4*m*Phi)*P+Sg2
    c3=-(6*p*P+f*F-3*p*c2)*params['c3_factor']
    c3p=-(6*u*P+6*p*U+g*F+f*G-3*u*c2-3*p*cp)*params['c3_factor']
    Sp3=H*c3-(2*p*U+(4*P-2*c2)*u+(f*G+2*F*g)/3)/3
    be2=-2*c2+4*P+8*p*p;be3=-8*p*c2+16*p*P+32*p*p*p/3
    K1=gp+4*H*g+6*u*T;K2=Gp+4*H*G+(6*U-cp)*T+6*u*g
    K3=6*u*G+(6*U-cp)*g
    qK=K3+4*p*K2+be2*K1+be3*m*Phi-e*(2*r*r*c2*f+2*mu2*p*F+(-2*P+2*p*p)*(-mu1)*f)
    R0=6*H*H-T*T/2;R1=12*H*u-T*g
    R2=12*H*U-T*G+6*u*u-g*g/2;R3=12*u*U-g*G
    qR=R3+4*p*R2+be2*R1+be3*R0+m*f*F-e*(12*r*r*p*P+2*r*r*f*F-2*p*(-3*mu2*P+3*r*r*p*p+r*r*f*f/2)+(-2*P+2*p*p)*(-3*mu1)*p+(4*p*P-4*p*p*p/3)*6*k)
    Sc3=12*H*Sp3-(12*H*H-T*T)*c3+qR
    Sg3=T*c3p+2*m*Phi*c3-6*T*Sp3-qK
    return dict(c3=c3,Sp3=Sp3,Sc3=Sc3,Sg3=Sg3)

