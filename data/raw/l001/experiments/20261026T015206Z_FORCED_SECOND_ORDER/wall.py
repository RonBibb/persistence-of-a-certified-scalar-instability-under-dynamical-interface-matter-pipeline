"""Eulerian second-order physical-wall reconstruction from canonical states.

No imports of either radial engine, no numerical work on import. For residuals,
canonical entries 8:11 contain the ASSEMBLED second-order p,f,g, not merely
the shooting particular. Entries 11:14 are ignored by those boundary rows.
"""


def _check(y, sigma, N2=None):
    if len(y) != 14:
        raise ValueError('Canonical fourteen-state input required')
    if sigma not in (-1, 1):
        raise ValueError('Wall orientation must be +1 lower or -1 upper')
    if N2 is not None and N2 not in (0, 1):
        raise ValueError('Only the frozen zero/unit conserved-current labels')


def reconstruct(ycanonical14, p, sigma, N2):
    """Fresh T17/T18 equations; N2 is Ni^2, while returned n=Ni^2 E^6."""
    _check(ycanonical14,sigma,N2)
    W,H,Phi,T,E,v,f,g,_,_,_,_,_,_=ycanonical14
    m,k,mu1,mu2=p['m2'],p['k'],p['mu1'],p['mu2']
    e2=E*E
    if E.lower() <= 0 or k.lower() <= 0:
        raise ValueError('Positive inverse warp and curvature required')
    Tp=m*Phi-4*H*T
    Hp=-T*T/3-k*e2
    Tpp=m*T-4*Hp*T-4*H*Tp
    u=-2*H*v-T*f/3
    gp=-4*H*g+(m-mu1*e2+2*T*T)*f+(12*H*T-4*m*Phi)*v
    n=N2*e2*e2*e2
    # Algebraically identical to basis.load_wall sigma*N2*E^4/(42k).
    xi=n/(42*sigma*k*e2)
    d1=2-mu1*e2
    d2=2-mu2*e2
    if d1.lower() <= 0 or d2.lower() <= 0:
        raise ValueError('Unresolved oscillator denominator')
    chi=(f+T*xi)/d1
    A=H*xi+v
    qgeom=-sigma*k*e2*xi*(384*v+120*H*xi)
    qcurrent=n*((T*xi+f)/1000+6*A)
    qosc=-18*k*e2*chi*chi
    divisor=156*sigma*k*e2
    if divisor.contains(0):
        raise ValueError('Unresolved second graph divisor')
    xi2=-(qgeom+qcurrent+qosc)/divisor
    c2=-(6*v*v+f*f)*3/13
    o2=36*k*e2*A*chi-xi*g-xi*xi*Tp/2
    j2=(xi*xi*Tpp/2+xi*gp+2*v*(xi*Tp+g)
        +(2*v*v+2*xi*u)*T+36*k*e2*xi*f+18*k*e2*xi*xi*T
        -sigma*(21*(xi*xi*Tp/2+xi*g)+6*n*A/1000)/2)
    Gamma2=21-1/d2
    R2=2*sigma*(T*c2-(Tp-sigma*Gamma2*T/2)*xi2-j2+sigma*o2/(2*d2))
    Sp=H*c2-v*u-f*g/6
    qR=(6*u*u-g*g/2+4*v*(12*H*u-T*g)
        +8*v*v*(6*H*H-T*T/2)+m*f*f/2
        -e2*(12*k*v*v+18*k*f*f))
    Sc=12*H*Sp-(12*H*H-T*T)*c2+qR
    return {'xi':xi,'chi':chi,'n':n,'Tp':Tp,'xi2':xi2,'o2':o2,
            'j2':j2,'R2':R2,'Gamma2':Gamma2,'d2':d2,'c2':c2,'Sc':Sc,
            'E':E,'H':H,'Phi':Phi,'T':T,'psi':v,'f':f,'g':g,
            'u':u,'gp':gp,'Tpp':Tpp,'d1':d1,'qI_geometric':qgeom,
            'qI_current':qcurrent,'qI_oscillator':qosc,
            'graph_divisor':divisor}


def residuals(full, wall, p, sigma):
    """Rows must contain zero; chi2 is a reconstructed field, NOT a residual.

    This checks Q5 oscillator/scalar, undivided Q6 and the necessary graph row;
    it does not claim an independent full trace-Israel n2 reconstruction.
    """
    _check(full,sigma)
    W,H,Phi,T,E,v,f,g,p2,f2,g2,_,_,_=full
    xi2,c2,d2=wall['xi2'],wall['c2'],wall['d2']
    o2,j2,Tp=wall['o2'],wall['j2'],wall['Tp']
    chi2=(f2+T*xi2-o2)/d2
    oscillator=d2*chi2-f2-T*xi2+o2
    scalar=(g2+Tp*xi2-T*c2+2*T*p2
            -sigma*(21*(f2+T*xi2)-chi2)/2+j2)
    robin=2*sigma*(g2+2*T*p2)-wall['Gamma2']*f2-wall['R2']
    graph=wall['graph_divisor']*xi2+wall['qI_geometric']+wall['qI_current']+wall['qI_oscillator']
    elimination=2*sigma*d2*scalar-oscillator-d2*robin
    return {'chi2':chi2,'rows':{'oscillator':oscillator,'scalar_Q5':scalar,
            'undivided_Q6':robin,'graph':graph,'Q5_Q6_elimination':elimination}}


def pullback_bridge(full, wall, sigma, Xprime):
    """Exact T18 wall pullback, with X1=xi at that physical endpoint.

    Xprime must be the frozen affine interpolant derivative using the complete
    common D interval. Both returned loads are diagnostics, not alternative
    output enclosures to select after viewing their widths.
    """
    _check(full,sigma)
    W,H,Phi,T,E,v,f,g,p2,f2,g2,_,_,_=full
    xi,u,gp=wall['xi'],wall['u'],wall['gp']
    oP=wall['o2']+xi*g
    jP=wall['j2']-Xprime*g-xi*gp-2*T*xi*u+21*sigma*xi*g/2
    Gamma,d2=wall['Gamma2'],wall['d2']
    RP=2*sigma*(T*wall['c2']-(wall['Tp']-sigma*Gamma*T/2)*wall['xi2']
                -jP+sigma*oP/(2*d2))
    shift=2*sigma*(Xprime*g+xi*gp+2*T*xi*u)-Gamma*xi*g
    pP,fP,gP=p2+xi*u,f2+xi*g,g2+Xprime*g+xi*gp
    rowE=2*sigma*(g2+2*T*p2)-Gamma*f2-wall['R2']
    rowP=2*sigma*(gP+2*T*pP)-Gamma*fP-RP
    return {'o2_pulled':oP,'j2_pulled':jP,'R2_pulled':RP,'load_shift':shift,
            'p2_pulled':pP,'f2_pulled':fP,'g2_pulled':gP,
            'rows':{'load_bridge':RP-wall['R2']-shift,'row_bridge':rowP-rowE}}
