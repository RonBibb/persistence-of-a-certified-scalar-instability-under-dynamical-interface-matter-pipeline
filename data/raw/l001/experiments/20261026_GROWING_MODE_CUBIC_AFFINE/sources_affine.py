"""Analytic A2 channels of qualified cubic sources; no interval subtraction."""
import importlib.util,sys
from pathlib import Path
_path=Path(__file__).resolve().parent.parent/'20261026_GROWING_MODE_CUBIC_FLOW/sources.py'
_spec=importlib.util.spec_from_file_location('affine_qualified_cubic_source',_path)
base=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=base;_spec.loader.exec_module(base)
def channels(z,p):
    W,H,Phi,T,E,a,f,g,P,F,G,Ph,Fh,Gh=z[:14];e=E*E
    src0=base.cubic(H,T,Phi,e,a,f,g,P,F,G,p)
    zero=a*0;m=zero+p['m2'];k=zero+p['k'];r=zero+p['rate'];h=zero+p['h'];mu1=zero+p['mu1'];mu2=zero+p['mu2']
    u=-2*H*a-T*f/3;Uh=-2*H*Ph-T*Fh/3
    Gph=-4*H*Gh+(m-mu2*e+2*T*T)*Fh+(12*H*T-4*m*Phi)*Ph
    c3=-(6*a*Ph+f*Fh)*p['c3_factor']
    cp=-(6*u*Ph+6*a*Uh+g*Fh+f*Gh)*p['c3_factor']
    Sp=H*c3-(2*a*Uh+4*Ph*u+(f*Gh+2*Fh*g)/3)/3
    gp=-4*H*g+(m-mu1*e+2*T*T)*f+(12*H*T-4*m*Phi)*a
    K1=gp+4*H*g+6*u*T
    K2h=Gph+4*H*Gh+6*Uh*T;K3h=6*u*Gh+6*Uh*g
    qK=K3h+4*a*K2h+4*Ph*K1+16*a*Ph*m*Phi-e*(2*mu2*a*Fh+2*Ph*mu1*f)
    R0=6*H*H-T*T/2;R1=12*H*u-T*g
    qR=12*u*Uh-g*Gh+4*a*(12*H*Uh-T*Gh)+4*Ph*R1+16*a*Ph*R0+m*f*Fh
    qR=qR-e*(12*r*r*a*Ph+2*r*r*f*Fh+6*mu2*a*Ph+6*mu1*a*Ph+24*k*a*Ph)
    src1=dict(c3=c3,Sp3=Sp,Sc3=12*H*Sp-(12*H*H-T*T)*c3+qR,Sg3=T*cp+2*m*Phi*c3-6*T*Sp-qK)
    return src0,src1
