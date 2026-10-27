"""Neutral growing-mode quadratic Eulerian wall equations, no factorials."""
def reconstruct(y,p,sigma):
    assert len(y)==14 and sigma in (-1,1)
    W,H,Phi,T,E,v,f,g,*_=y
    m,k,r,h=p['m2'],p['k'],p['rate'],p['h']
    Tp=m*Phi-4*H*T
    d1=2-p['mu1']*E*E;d2=2-p['mu2']*E*E
    assert d1.lower()>0 and d2.lower()>0 and (2*r-h).lower()>0
    chi=f/d1;xi2=sigma*r*chi*chi/(4*(2*r-h))
    c2=-p['c_factor']*(6*v*v+f*f)
    o2=-6*h*r*E*E*v*chi;j2=2*v*g+2*T*v*v
    G=21-1/d2
    R=2*sigma*(T*c2-(Tp-sigma*G*T/2)*xi2-j2+sigma*o2/(2*d2))
    return dict(chi1=chi,xi2=xi2,c2=c2,o2=o2,j2=j2,Gamma2=G,R2=R,d2=d2,Tp=Tp,
                qI=-r*r*E*E*chi*chi/2,divisor=sigma*E*E*2*r*(2*r-h))

def residuals(y,w,p,sigma):
    W,H,Phi,T,E,v,f,g,p2,f2,g2,*_=y
    chi2=(f2+T*w['xi2']-w['o2'])/w['d2']
    osc=w['d2']*chi2-f2-T*w['xi2']+w['o2']
    scalar=g2+w['Tp']*w['xi2']-T*w['c2']+2*T*p2-sigma*(21*(f2+T*w['xi2'])-chi2)/2+w['j2']
    robin=2*sigma*(g2+2*T*p2)-w['Gamma2']*f2-w['R2']
    return dict(oscillator=osc,scalar_normal=scalar,robin=robin,graph=w['divisor']*w['xi2']+w['qI'],
                elimination=2*sigma*w['d2']*scalar-osc-w['d2']*robin)

