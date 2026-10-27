"""Generic scalar/jet cubic sources; all coefficients exact and regular at T=0."""
def cubic(H,T,Phi,e,p,f,g,P,F,G,params):
    zero=p*0;m=zero+params['m2'];k=zero+params['k']
    u=-2*H*p-T*f/3
    c2=-(6*p*p+f*f)*3/13;cp=-(12*p*u+2*f*g)*3/13
    Sp2=H*c2-p*u-f*g/6
    gp=-4*H*g+(m+18*k*e+2*T*T)*f+(12*H*T-4*m*Phi)*p
    qK2=(4*m+108*k*e)*p*f+6*u*g-8*m*Phi*p*p
    Sg2=T*cp+2*m*Phi*c2-6*T*Sp2-qK2
    U=-2*H*P-T*F/3+Sp2
    Gp=-4*H*G+(m+108*k*e+2*T*T)*F+(12*H*T-4*m*Phi)*P+Sg2
    c3=-(6*p*P+f*F-3*p*c2)*8/19
    c3p=-(6*u*P+6*p*U+g*F+f*G-3*u*c2-3*p*cp)*8/19
    Sp3=H*c3-(2*p*U+(4*P-2*c2)*u+(f*G+2*F*g)/3)/3
    be2=-2*c2+4*P+8*p*p;be3=-8*p*c2+16*p*P+32*p*p*p/3
    K1=gp+4*H*g+6*u*T;K2=Gp+4*H*G+(6*U-cp)*T+6*u*g
    K3=6*u*G+(6*U-cp)*g
    qK=K3+4*p*K2+be2*K1+be3*m*Phi-e*(72*k*c2*f-216*k*p*F+(-2*P+2*p*p)*18*k*f)
    R0=6*H*H-T*T/2;R1=12*H*u-T*g
    R2=12*H*U-T*G+6*u*u-g*g/2;R3=12*u*U-g*G
    qR=R3+4*p*R2+be2*R1+be3*R0+m*f*F-e*(432*k*p*P+72*k*f*F-2*p*(324*k*P+108*k*p*p+18*k*f*f)+(-2*P+2*p*p)*54*k*p+(4*p*P-4*p*p*p/3)*6*k)
    Sc3=12*H*Sp3-(12*H*H-T*T)*c3+qR
    Sg3=T*c3p+2*m*Phi*c3-6*T*Sp3-qK
    return dict(c3=c3,Sp3=Sp3,Sc3=Sc3,Sg3=Sg3)
