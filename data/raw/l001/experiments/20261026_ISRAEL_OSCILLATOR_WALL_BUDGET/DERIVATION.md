# Israel and oscillator wall source bounds

These bounds cover the tracefree Israel and surface-oscillator residuals of the selected action, together with reconstruction of the graph coefficients. They use the same fixed collar and auxiliary primitive-count method as the audited scalar-normal wall estimate. They do not yet reconstruct the reduced Robin load or close the full nonlinear majorant.

## Shared primitives and derivative conventions

Use rho=1/40000, a=80000, A=2a+1, and G=(1-A*y)^(-1). The auxiliary y counts positive-order primitives before substitution y=Y_<n. Let E=8+1/1000, g=3/25, hstar=1/50 and c=E*g<1. Hbar and Pbar bound the background warp gradient and scalar on the prior collar.

At fixed-chart endpoints, p_t^wall and b_t^wall are total coordinate-time derivatives at a fixed wall label. Their ordinary and order-weighted coefficients are bounded by g*Y_i. The corresponding bounds for S_tt and chi_tt are g^2*Y_i, using the cubic graph and oscillator weights. The bounds for S_t and chi_t are g*Y_i. No such bound is asserted for a second bulk time derivative. Physical Dp and Db are the transported derivatives, not the wall total derivatives; each is bounded by 2g*y*G.

Set U=E(S)exp(-p)=1/N, boost=(1-v^2)^(-1/2), and v=exp(b-p)E(S)S_t. The inherited bounds give

    U <= E*G^2,     U-E_i <= E(a+1)yG^2,
    v <= c*yG,     boost <= G,
    boost-1 <= c^2*y^2*G^2.

Here and below comparisons mean absolute-coefficient majorants after the stated neutral or linear subtraction. Along the moving wall E_t=-H(S)E(S)S_t, so the exact derivative is

    v_t=exp(b-p)E(S)[S_tt+(b_t^wall-p_t^wall-H(S)S_t)S_t].

Consequently

    v_t-E_i*S_tt <= E*g^2(a+4+Hbar)y^2G^3,
    v_t <= Bvt*yG^3,     Bvt=E*g^2(3+Hbar).

Direct Cauchy control of E^2, combined with the exponential and boost bounds, gives ell^(-2)<=E^2G^4. Writing P_E=E(S)^2 exp(-2p), the exact difference is (P_E-E_i^2)boost^2+E_i^2(boost^2-1). This split bounds it by E^2(a+2)yG^4+2E^2c^2y^2G^3. Numerical evaluation of the rational bounds requires A*y<1; the estimates themselves are formal coefficientwise.

## Israel source

The exact geometric row is

    sigma*[U*boost^3*v_t+U*boost*v*(Db-Dp-h)].

Remove its complete linear row sigma*E_i^2(S_tt-hS_t). The acceleration remainder has constant E^2*g^2(2a+5+Hbar+3c^2) against y^2G^8. This follows by separating the difference of U*boost^3 from E_i and the difference of v_t from E_i*S_tt. The drift remainder uses the exact identity U*boost*v=E(S)^2 exp(b-2p)boost*S_t and has constant hstar*E^2*g(a+3+c^2). The remaining product with Db-Dp has constant 4E^2g^2. The oscillator kinetic stress chi_t^2/(2ell^2) contributes E^2g^2/2. Thus the noncurrent raw source is bounded per wall by CI*y^2G^8, where

    CI=E^2g^2(2a+5+Hbar+3c^2)
       +hstar*E^2g(a+3+c^2)+(9/2)E^2g^2.

The current stress is c_action(Phi)*nu_i^2. With c_action=1-(Phi-Phi_star)/1000, set K=(Pbar*a+1)/1000. Then |c_action| is majorized by 1+K*yG. Direct Cauchy on E(S)^6 and the exponential yield

    |c_action*nu_i^2| <= Icur*z*|N_i|^2*G^3,
    Icur=E^6(1+K/A),

using yG^3<=G^3/A coefficientwise. The charge factor z is explicit and is retained at first order.

Apply the inherited primitive-count argument before substituting y=Y_<n. Differentiation of y^2G^8 costs at most 10*y^2G^9; the explicit current costs (1+y*d/dy)G^3<=4G^4. Two walls therefore give

    n*sum_i |qI_i,n| <= [z^n](20CI*y^2+4Icur*z*C_N)*G^9,
    C_N=|N_a|^2+|N_b|^2.

The exact graph divisor is E_i^2*6k*n(6n+1)>=36*kmin*emin^2*n^2. Hence Xi_n=n^3*sum_i|xi_i,n| has the same bound divided by 36*kmin*emin^2. The lower emin is the authenticated real-background minimum of E, not an assumed moving-wall value.

## Oscillator source

Remove the complete neutral linear row E_i^2(chi_tt+3hchi_t)+2chi-f-T_i*xi from

    ell^(-2){chi_tt+[3h+2H(S)S_t+2p_t^wall
                    +v*v_t/(1-v^2)]chi_t}
    +2chi-[Phi_0(S)-Phi_i_star+f].

Let t=g^2+3hstar*g. The four nonlinear source groups have sufficient constants

    lapse correction:     E^2*t*(a+2+2c^2),
    ordinary friction:   2E^2g^2(Hbar+1),
    velocity friction:   E^3*c*g^3(3+Hbar),
    scalar trace tail:   Pbar*a^2.

Their sum is CO. The velocity-friction group initially has degree three and denominator G^10; coefficientwise bounding y^3G^10 by y^2G^10 yields the stated constant. Other groups have denominator power at most five. Thus the raw per-wall source is bounded by CO*y^2G^10. The same auxiliary primitive-count argument gives

    n*sum_i |o_i,n| <= 24CO [z^n]y^2G^11.

The oscillator has no direct explicit current forcing in this selected action. Its response to charge enters through the other unknown coefficients. The coefficient-count step does not assume zY'(z)<=Y(z). Increasing the Israel and scalar-normal denominator powers to eleven permits a common envelope later; it does not by itself supply the remaining inverse and boundary-reconstruction estimates.
