# Prospective complete Eulerian wall-source reduction

Unverified manual derivation for independent review. No execution or full second-order solution is asserted. This extends the graph-source preparation to the Q5 oscillator and normalized scalar sources, at fixed original radial coordinate s, with the actual wall S=s_i+z xi. New order-two fields and graph coefficients are set to zero while extracting the known sources.

Use p=p1, f=f1, g=f1 prime, u=p1 prime, gp=f1 double prime at the background endpoint, A=H xi+p, E=a^-1, R=-6h, k=h², n=Ni²E^6 and chi=chi1. Write M for the manuscript's mathfrak m. All first-order endpoint data are available in T10; derivative jets needed here can be reconstructed analytically at the endpoint:

    Hp = -T²/3-k E²
    Tp = M Phi-4HT
    Tpp = M T-4Hp T-4H Tp
    u = -2*H*p-T*f/3
    gp = -4Hg+(M+18kE²+2T²)f+(12HT-4M Phi)p.

Use distinct code names for H prime and H times p in implementation.

## Oscillator source

At this order ell^-2=E²(1-2zA)+O(z²), and the first friction correction is 2RzA. The v v_t term first affects the oscillator row at order three. Thus the proposed Q5 coefficient is

    o2 = 36k E² A chi - xi*g - xi² Tp/2.

The two final terms arise from evaluating the scalar field at the moving wall. They must not be dropped by mixing Eulerian lower fields with pulled coefficients.

## Normalized scalar source

Expansion of exp(-b)(T+f_s), the moving-normal term v exp(-p)E Df, and the normalization 1/sqrt(1-v²) gives the proposed source

    j2 = xi² Tpp/2 + xi*gp
         +2p(xi*Tp+g)+(2p²+2xi*u)T
         +36kE² xi*f+18kE² xi²*T
         -sigma/2 [21(xi² Tp/2+xi*g)+6nA/1000].

The last current term uses c_Phi=-1/1000 and [z²]nu²=-6nA. The centered quadratic wall/oscillator potential gives tau_Phi+W_Phi=2sigma T+21(Phi_wall-Phi*)-chi. The source truncation contains chi=z chi1, so there is no unknown chi2 in j2 or o2.

At an uncharged remote wall with xi=0 these expressions reduce to

    o2=36kE²p chi,
    j2=2p*g+2p²*T.

These are candidate reductions to verify by independent formal coefficient extraction of the original Q5 rows, not by evaluating the same simplified functions twice.

## Assembly and chart boundary

With c2 and xi2 separately qualified, the Eulerian new-field Robin source would be

    d2=2+108kE², Gamma2=21-1/d2,
    R2=2sigma [T*c2-(Tp-sigma Gamma2 T/2)*xi2
                -j2+sigma o2/(2d2)].

The corresponding new-field scalar row must be independently rederived before using this load in an Eulerian solve. Pulled coefficients differ by p2_P=p2_E+xi*u and f2_P=f2_E+xi*g at the wall, with derivative transformation including xi*g prime and X1 prime*g. Thus these sources cannot be silently inserted into the earlier pulled-chart solver specification. A qualified Eulerian coefficient solve plus the explicit observable/chart bridge is an alternative design, not an in-run change.

Successful wall-source qualification would complete another prerequisite for the forced second-order boundary-value problem. It would still supply no p2/f2 solution, total proper-distance coefficient, finite-amplitude radius, saturation or excitation result.
