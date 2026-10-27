"""Exact affine wall-load channels, with fixed lower-order geometry."""
import importlib.util,sys
from pathlib import Path
_path=Path(__file__).resolve().parent.parent/'20261026_GROWING_MODE_CUBIC_WALL/wall.py'
_spec=importlib.util.spec_from_file_location('affine_qualified_cubic_wall',_path)
base=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=base;_spec.loader.exec_module(base)
def polynomial_channels(w,t,sigma):
    b=base.closed(w,sigma)
    E,r,h,a,f,g,T,chi=[w[k] for k in ('E','rate','h','p1','f1','g1','T','chi1')]
    P,F,G,chi2=[t[k] for k in ('p2','f2','g2','chi2')]
    d=dict(qI3=-2*r*r*E*E*chi*chi2,
           o3=E*E*(-4*r*(r+3*h)*a*chi2+2*r*(r-3*h)*P*chi),
           j3=2*a*G+2*P*g+4*T*a*P,
           c3_numerator=-4*r*(6*a*P+f*F))
    return b,d
def channels(w,t,sigma):
    b,d=polynomial_channels(w,t,sigma)
    divisor=b['graph_divisor'];dn=b['d3'];Gamma=21-1/dn
    out=[]
    for item,c3 in ((b,w['c3']),(d,t['c3'])):
        x=-item['qI3']/divisor
        R=2*sigma*(w['T']*c3-w['Tp']*x-item['j3'])+Gamma*w['T']*x+item['o3']/dn
        out.append(dict(item,c3=c3,xi3=x,R3=R))
    out[0].update(Gamma3=Gamma,xi2=w['xi2'])
    return tuple(out)
