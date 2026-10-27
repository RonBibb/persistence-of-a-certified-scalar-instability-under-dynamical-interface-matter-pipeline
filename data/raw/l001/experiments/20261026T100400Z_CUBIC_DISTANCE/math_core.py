"""Generic cubic distance densities; scalar algebra only."""
def fields(z,p):
    W,H,Phi,T,E,a,f,g,ap,fp,gp,ah,fh,gh,cp,cf,cg,ch,fh3,gh3=z
    P=ap+p['A2']*ah;F=fp+p['A2']*fh
    c2=-(6*a*a+f*f)*3/13
    c3=-(6*a*P+f*F-3*a*c2)*8/19
    u=-2*H*a-T*f/3;Sp2=H*c2-a*u-f*g/6
    U=-2*H*P-T*F/3+Sp2
    Hp=-T*T/3-p['k']*E*E;Tp=p['m2']*Phi-4*H*T
    up=-2*Hp*a-2*H*u-(Tp*f+T*g)/3
    c2p=-(12*a*u+2*f*g)*3/13
    w2=c2-2*P+2*a*a;w2p=c2p-2*U+4*a*u
    return dict(p1=a,p2=P,c2=c2,c3=c3,u=u,up=up,w2=w2,w2p=w2p,p3P=cp,p3H=ch)
def endpoint(z,p,x1,x2):
    v=fields(z,p);return -2*v['p1']*x2+v['w2']*x1-v['u']*x1*x1
def densities(z,p,X1,X2,x1p,x2p):
    v=fields(z,p);a=v['p1'];u=v['u']
    d={k:v[k] for k in ('c3','p3P','p3H')}
    d.update(p1c2=a*v['c2'],p1p2=a*v['p2'],p1cubed=a*a*a)
    d['direct_bulk']=v['c3']-2*(v['p3P']+p['A3']*v['p3H'])-2*d['p1c2']+4*d['p1p2']-4*d['p1cubed']/3
    d['transport']=-2*u*X2-2*a*x2p+v['w2p']*X1+v['w2']*x1p-v['up']*X1*X1-2*u*X1*x1p
    return d
def bulk(t,A3):return t['c3']-2*(t['p3P']+A3*t['p3H'])-2*t['p1c2']+4*t['p1p2']-4*t['p1cubed']/3
