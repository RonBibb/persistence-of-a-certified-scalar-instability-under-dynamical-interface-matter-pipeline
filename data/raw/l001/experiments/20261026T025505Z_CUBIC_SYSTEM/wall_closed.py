"""Independent scalar cubic Q5 formulas, no series arithmetic."""
def extract(w,sigma):
    E,h,H,Hp,T,Tp,Tpp,Tppp,p,u,upp,f,g,gp,gpp,P,U,F,G,Gp,c,cp,x,y,chi,chi2,n=[w[k] for k in ('E','h','H','Hp','T','Tp','Tpp','Tppp','p1','u1','u1p','f1','g1','g1p','g1pp','p2','u2','f2','g2','g2p','c2','c2p','xi1','xi2','chi1','chi2','n')]
    r=-6*h;A=H*x+p;B=H*y+Hp*x*x/2+P+x*u
    b2=c-2*P-2*x*u;b3=x*(cp-2*U)-2*y*u-x*x*upp
    v1=E*r*x;v2=E*r*(2*y+x*(-2*p-A))
    phi3=Tp*x*y+Tpp*x*x*x/6+y*g+x*x*gp/2+x*G
    f1=Tp*x+g;f2=Tp*y+Tpp*x*x/2+G+x*gp
    f3=Tpp*x*y+Tppp*x*x*x/6+y*gp+x*x*gpp/2+x*Gp
    radial=f3+2*p*f2+(-b2+2*p*p)*f1+(-b3-2*p*b2+4*p*p*p/3)*T
    tilt=E*v1*(2*r*F+r*x*g)+E*(v2-A*v1)*r*f
    boost=v1*v1*(f1+2*p*T)/2+v1*v2*T
    force=sigma*n*(-6*B+18*A*A)/2000
    j3=radial+tilt+boost-sigma*21*phi3/2+force
    o3=E*E*(-72*h*h*A*chi2+(108*h*h*(B-A*A)+54*h*h*v1*v1)*chi)-phi3
    return dict(o3=o3,j3=j3,normal_tilt=tilt,normal_boost=boost,displacement=-sigma*21*phi3/2,current_force=force)
