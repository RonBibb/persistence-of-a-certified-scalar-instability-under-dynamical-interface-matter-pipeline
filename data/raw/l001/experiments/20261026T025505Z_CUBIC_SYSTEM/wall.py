"""Direct degree-three Eulerian moving-wall Q5 extraction.

No computation on import. Caller supplies authenticated cubic-parent S class.
Scalars may be exact sparse polynomials, Fraction, or outward Arb balls.
All coefficients use ordinary powers of z, not factorial coefficients.
"""
from fractions import Fraction as Q

NEW = ('p3', 'f3', 'g3', 'chi3', 'xi3', 'c3')


def div(value, denominator):
    """Keep integer fixtures exact without requiring Arb/Fraction coercion."""
    return Q(value, denominator) if isinstance(value, int) else value / denominator


def direct(w, sigma, S):
    """Return complete Q5 series through z^3 with arbitrary new fields.

    n is Ni^2 E_i^6 at the undisplaced wall. chi_j are intrinsic wall
    oscillator coefficients; they are not composed with a radial shift.
    u1p=p1'', g1p=f1'', g1pp=f1''', g2p=f2''.
    """
    E,h,H,Hp,Hpp,T,Tp,Tpp,Tppp = [w[k] for k in
        ('E','h','H','Hp','Hpp','T','Tp','Tpp','Tppp')]
    p,u,upp,f,g,gp,gpp,p2,u2,f2,g2,g2p,c2,c2p = [w[k] for k in
        ('p1','u1','u1p','f1','g1','g1p','g1pp','p2','u2','f2','g2','g2p','c2','c2p')]
    x,y,chi,chi2,n=[w[k] for k in ('xi1','xi2','chi1','chi2','n')]
    p3,f3,g3,chi3,x3,c3=[w.get(k,0) for k in NEW]
    r=-6*h
    loga=S([0,H*x,H*y+div(Hp*x*x,2),
            H*x3+Hp*x*y+div(Hpp*x*x*x,6)])
    pwall=S([0,p,p2+x*u,p3+y*u+div(x*x*upp,2)+x*u2])
    bwall=S([0,-2*p,c2-2*p2-2*x*u,
             c3-2*p3+x*(c2p-2*u2)-2*y*u-x*x*upp])
    shift=S([0,x,y,x3]);St=shift.dt(r)
    invN=(-loga-pwall).expzero()*E
    v=bwall.expzero()*invN*St
    v2=v*v;invone=1+v2;invsqrt=1+v2/2
    # Hwall cubic term cannot contribute through degree three: Hwall is
    # multiplied by St (order one) and chi_t (order one).
    Hwall=S([H,Hp*x,Hp*y+div(Hpp*x*x,2)])
    Ewall=(-loga).expzero()*E
    Twall=S([T,Tp*x,Tp*y+div(Tpp*x*x,2),
             Tp*x3+Tpp*x*y+div(Tppp*x*x*x,6)])
    scalar_delta=S([0,T*x+f,
        T*y+div(Tp*x*x,2)+f2+x*g,
        T*x3+Tp*x*y+div(Tpp*x*x*x,6)+f3+y*g+div(x*x*gp,2)+x*g2])
    scalar_radial=S([0,g,g2+x*gp,g3+y*gp+div(x*x*gpp,2)+x*g2p])
    # Df is fixed-s time differentiation, followed by wall composition.
    # It is not d/dt of the already composed scalar trace.
    scalar_time=S([0,r*f,2*r*f2+r*x*g,
                   3*r*f3+2*r*x*g2+r*y*g+div(r*x*x*gp,2)])
    oscillator=S([0,chi,chi2,chi3]);chid=oscillator.dt(r)
    nu2=S([0,n])*(-6*loga-6*pwall).expzero()
    friction=S([3*h])+2*Hwall*St+2*pwall.dt(r)+v*v.dt(r)*invone
    O=invN*invN*invone*(chid.dt(r)+friction*chid)+2*oscillator-scalar_delta
    normal=invsqrt*((-bwall).expzero()*(Twall+scalar_radial)
                    +v*(-pwall).expzero()*Ewall*scalar_time)
    # tau_Phi + W_Phi = 2 sigma T + 21 deltaPhi - chi;
    # the selected affine coupling has c_Phi=-1/1000 exactly.
    J=normal-(S([2*sigma*T])+21*scalar_delta-oscillator-nu2/1000)*sigma/2
    return {'O':O,'J':J,'normal':normal,'nu2':nu2,
            'scalar_delta':scalar_delta,'pwall':pwall,'bwall':bwall,'loga':loga}


def extract(w, sigma, S):
    """Source/new-row decomposition and undivided Q6 identity witnesses.

    Returned residual identities must be exactly zero for polynomial inputs;
    interval execution checks zero containment without intersection.
    """
    full=direct(w,sigma,S)
    lower=dict(w)
    for key in NEW:lower[key]=0
    trunc=direct(lower,sigma,S)
    o3=trunc['O'].a[3];j3=trunc['J'].a[3]
    E,h,T,Tp=[w[k] for k in ('E','h','T','Tp')]
    p3,f3,g3,chi3,x3,c3=[w.get(k,0) for k in NEW]
    d3=2+270*h*h*E*E
    newO=d3*chi3-f3-T*x3
    newJ=g3+Tp*x3-T*c3+2*T*p3-div(sigma*(21*(f3+T*x3)-chi3),2)
    load_times_d=2*sigma*d3*(T*c3-Tp*x3-j3)+(21*d3-1)*T*x3+o3
    robin_times_d=2*sigma*d3*(g3+2*T*p3)-(21*d3-1)*f3-load_times_d
    return {'o3':o3,'j3':j3,'d3':d3,'O3':full['O'].a[3],'J3':full['J'].a[3],
            'new_O3':newO,'new_J3':newJ,
            'oscillator_identity':full['O'].a[3]-newO-o3,
            'scalar_identity':full['J'].a[3]-newJ-j3,
            'Q6_load_times_d3':load_times_d,'Q6_robin_times_d3':robin_times_d,
            'Q6_identity':2*sigma*d3*full['J'].a[3]-full['O'].a[3]-robin_times_d,
            'direct':full,'truncated':trunc}
