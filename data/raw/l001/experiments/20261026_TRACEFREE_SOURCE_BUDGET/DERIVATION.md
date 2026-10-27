# Tracefree bulk source bound

This calculation supplies an explicit coefficientwise nonlinear bound for the tracefree bulk row and its reconstructed combination c=b+2p. It is one component of the full compatible source estimate, not a closed majorant for the charged solution.

## Fixed working collar

Use the background collar R=1/20000 as the prior domain and fix the working collar rho=R/2=1/40000. All weighted norms and the envelope Y in this calculation are defined on the working collar, with d=1-dist(r,I)/rho. This is a new norm convention for subsequent source assembly; the earlier numerical response constants cannot simply be relabeled and must be recalculated for rho. No collar is shrunk with recursion order.

The previous conditional domain statement involving Y(16|z|) remains valid in its own convention. It is not a same-argument recursive majorant and is not substituted into this coefficient estimate. The tracefree row contains no composed background coefficients: D annihilates the composed background exactly. The larger collar is reserved for the other rows.

## Graph transport bounds

Let y stand for the nonnegative lower-order envelope Y_<n. All perturbations have positive order, with the neutral background already separated. Its order-i coefficient bounds the sum of bulk U_i norms and cubic graph and oscillator norms. On the working collar, D_min>1 and 1+rho/D_min<2 give coefficient bounds X_i by 2Y_i/i^3 and (X_r)_i by Y_i/i^3. Set h_*=1/50 and g=6h_*=3/25, which bound h and 6h respectively. Dropping negative powers of positive orders gives

    w(y) = 2g y/(1-y),
    w_r(y) = g y/(1-y),
    w_t(y) = 2g^2 y/(1-y) + 2g^2 y^2/(1-y)^2.

These bound W=D0X/(1+X_r), its radial derivative, and D0W. The radial derivative formula uses X_rr=0. Each W factor retains at least one positive-order graph factor for analytic-index accounting even though its inverse-order decay has been dropped from the scalar expression.

## Exact source allocation

The lower-order tracefree source is the sum of

    -2W D0 c_r + (W W_r - D0W + hW)c_r + W^2 c_rr
    + (Db)^2 - 2(Dp)(Db) - 2(Dp)^2 + (Df)^2.

The omitted term (D0^2-hD0)c has no order-n coefficient in the lower-order truncation. Since U_i(c)<=2Y_i, its source norm at index 2n is bounded coefficientwise by

    B(y) = y[4g w + 2w w_r + 2w_t + 2h_*w + 2w^2]
           + 6(g+w)^2 y^2.

For every extra radial index, a positive graph order pays the difference: 2j+1<=2(i+j) and 2j+2<=2(i+l+j) for i,l>=1. The temporal derivative of a first radial bulk jet costs at most gY_j. A first temporal bulk jet costs at most gY_j; a first radial jet costs at most Y_j. Thus all terms above fit the target index without an unpaired positive expansion-order factor.

Putting B over a common denominator gives

    B(y) = y^2/(1-y)^2 * [a0+a1 y+a2 y^2],
    a0 = 18g^2+4h_*g,
    a1 = 16g^2-4h_*g,
    a2 = 6g^2.

All three coefficients are positive and their sum is 40g^2. Coefficientwise, y^j/(1-y)^2 is bounded by 1/(1-y)^2 for j>=0. Therefore

    ||q_T,n||_(2n) <= 40g^2 [z^n] y^2/(1-y)^2.

This is an all-order algebraic estimate, not an inference from a finite coefficient sample.

## Reconstruction

The divisor is 6k n(6n+1)>=36k_min n^2. Applying Nagumo once and twice, using e<3, 2n+1<=3n and (2n+1)(2n+2)<=12n^2, gives

    U_n(c) <= C_T [z^n] y^2/(1-y)^2,
    C_T = 40g^2 [1+9/rho+108/rho^2]/(36k_min).

The source expression is quadratic at the origin and vanishes at order one. The large sufficient constant reflects the conservative derivative estimates on a thin analytic collar; it is not measured physical amplification. Mixed Einstein, scalar, radial, and wall source bounds and final majorant closure remain separate work.
