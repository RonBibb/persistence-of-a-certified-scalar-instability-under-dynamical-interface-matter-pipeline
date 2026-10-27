# Explicit static-to-initial bridge and its domain

## Physical and coordinate objects

The action is R_ab=Phi_a Phi_b+(2/3)V g_ab, Box Phi=m2 Phi, with
V=-6+m2 Phi^2/2 and U_i=lambda_i+gamma(Phi-v_i)^2/2. All six rational
parameters are compared exactly. The source is the central static D1 root and
its fixed normalized mode, not an interchangeable member of P01's tension
neighborhood. The latter can supply conservative enclosures containing the
central model but does not change its action.

On the time-reflection slice, use material coordinate s in [0,D]:

    dl^2 = exp(2 ell(s)) ds^2 + exp(2 A(s))/k dOmega_3^2,
    lapse = exp(B(s)), B=A+q, K_ij=Pi=0, shift=0.

Define x(s)=integral_0^s exp(ell-B) ds, X=x(D), y=x/X. The initial conformal
spatial metric is exp(2B) dx^2+exp(2A)/k dOmega_3^2. Because x_s>0, this map
is invertible. The fixed-x values are A(s(x)), B(s(x)), Phi(s(x)). Changing
the grid label also pulls back s; native tangents cannot be compared directly
to fixed-x or fixed-y array differences.

For sigma=+1 at the lower wall and -1 at the upper wall,

    n=-sigma exp(-ell) partial_s=-sigma exp(-B) partial_x.

The spatial rows are exp(-ell) A_s+sigma U/6=0 and
exp(-ell) Phi_s-sigma U'/2=0. The B row agrees with the A row when q_s=0.
At a wall q=0, so the normalized clock rate is exp(A_wall-W_wall), not
identically one at nonzero amplitude. The areal radius is R=exp(A)/sqrt(k),
and proper separation L=integral exp(ell) ds=integral exp(B) dx. No finite
future time or causal horizon is defined by this initial-slice map.

The C4 lapse preparation fixes q,q_s,q_ss=0 at each wall; its third/fifth
jets remove the second/fourth temporal-minus-angular Israel rows. The C6
preparation also supplies seventh lapse jets after a PHYSICAL scalar/metric
completion. A coordinate map cannot itself supply that physical completion.

## Why theorem membership is separate

For the certified C4 family, the scalar correction at fixed source and epsilon
belongs to the degree-at-most-eleven space C7+b0 H5_L+b1 H5_R. The metric
correction a does not add a scalar basis direction. The new datum adds

    dPhi=dc5_L H5_L+dc5_R H5_R+dc7_L H7_L+dc7_R H7_R,
    H_j,L=s^j(1-s/D)^(j+1)/j!,
    H_j,R=(s-D)^j(s/D)^(j+1)/j!.

H7 terms preserve endpoint scalar derivatives 0..6 while changing the interior
profile. Their degree-15 coefficient is

    (dc7_L+dc7_R)/(7! D^8).

When this is nonzero, no change of a,b0,b1 absorbs the scalar change at the
same source and epsilon. Since ell and D are unchanged in the represented
preparation, proper distance from the lower wall is the same function of s.
A nonzero dPhi(s) is therefore also a nonzero scalar-at-proper-distance
difference: it is not an artifact of choosing x instead of s.

This exact polynomial witness tests the shared SAVED source representation.
The continuum source uncertainty and the rigorous existence of an enlarged
C6 physical family remain separate. A failure of this restricted ansatz is
not a no-go for a new C6 family theorem or for a broader bridge.

## Transfer of admitted error enclosures

Let hats denote a numerical C4 representative at common u=s/D. Suppose

    |A-Ahat|<=EA, |ell-ellhat|<=El, |q-qhat|<=Eq,
    |log(D/Dhat)|<=ED, |log(k/khat)|<=Ek.

Then radius and proper-distance ratios obey

    |log(R/Rhat)| <= EA+Ek/2,
    |log(L/Lhat)| <= ED+El.

At the lower wall W=0 exactly and q=0, so the initial normalized clock ratio
has log error <=EA. At the upper wall it needs an additional EW bound.

For the coordinate integrand f(u)=D exp(ell-A-q), put
EJ=ED+El+EA+Eq. Then exp(-EJ)<=f/fhat<=exp(EJ), and the same inequalities
hold for x(u)/xhat(u) away from x=0 and for X/Xhat. In particular a safe
normalized-map bound is |y-yhat|<=expm1(2 EJ). If y_u has a known positive
lower bound m, the inverse has |u(y)-uhat(y)|<=expm1(2 EJ)/m (with endpoints
handled exactly). A field F with a valid u-derivative bound MF then has
fixed-y error <=EF+MF*expm1(2 EJ)/m.

These are sufficient conservative inequalities, not best constants. They
show exactly what remains missing if Eq or the required derivative bounds
have not been validated. A numerical q comparison does not supply Eq.

The test instantiates the lapse-independent C4 radius, lower-clock and
proper-distance bounds from the admitted material bounds. It separately
certifies positivity and integral enclosures for the saved C6 polynomial map.
Neither operation transfers a C4 continuum certificate to the physically
different C6 family.
