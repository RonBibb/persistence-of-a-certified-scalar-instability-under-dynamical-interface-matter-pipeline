# Mixed Einstein nonlinear source bound

This estimate controls the mixed bulk source q_M and its reconstructed metric source S_p in the actual compatible recursion. It uses the fixed working collar rho=1/40000 and the larger background collar R=1/20000. It neither proves source compatibility independently nor closes the full nonlinear majorant.

## Background composition on a fixed collar

Let y be the nonnegative lower-order coefficient envelope Y_<n in the working-collar norms. All perturbations have positive order, with the neutral background separated. Use the tracefree packet's graph bounds and set g=3/25, j=(1-y)^(-1), w=2g y j and w_r=g y j. Here j majorizes the inverse graph Jacobian, rather than denoting an expansion index.

The background functions have bounds Hbar=H0+epsilon and Tbar=T0+epsilon on the prior collar. Every point in the working collar has a background Cauchy disk of radius rho (with the boundary radius obtained by a limit). Since the affine graph coefficients are bounded by 2y, set a=2/rho=80000. The composed backgrounds and their differences obey the formal coefficientwise bounds

    H(r+X) <= Hbar/(1-a y),
    H(r+X)-H(r) <= Hbar a y/(1-a y),

in absolute coefficient norms, with the same expressions replacing Hbar by Tbar for T. These are bounds on Taylor coefficients at the same argument y, not an insertion of Y(16z) into the recursion. A numerical evaluation of these rational majorants requires a*y<1; the formal coefficient statement does not presume a certified charge amplitude.

## Mixed source decomposition

Write Jinv for the actual inverse graph Jacobian, DeltaH=H(r+X)-H(r) and DeltaT=T(r+X)-T(r). Removing the new linear row from L(Dp)-(Db)(H+Lp)+(Df)(T+Lf)/3 leaves the following lower-order source terms:

    (Jinv-1) D0 p_r - Jinv(W_r p_r + W p_rr)
    - D0b DeltaH + W b_r H(r+X) - (Db)Lp
    + [D0f DeltaT - W f_r T(r+X)]/3 + (Df)Lf/3.

Every term fits weight index 2n+1. In particular, W contains a positive graph order i, so a second derivative of a bulk term of order j fits because 2j+2<=2(i+j)+1. Temporal and radial jet factors carry no remaining positive unpaired order power after the inherited bulk and cubic graph weights are applied.

With B=Hbar+Tbar/3, the groups above give

    Q(y)=g y^2 j + 3g y^2 j^2
         + Bg y^2 (a+2j)/(1-a y)
         + (4g/3)y^2(1+y)j^2.

For a>=1, both j and (1-a y)^(-1) have nonnegative coefficients. Replacing the denominators by (1-a y)^(-2), and using y*j^2<=j^2 coefficientwise, yields

    ||q_M,n||_(2n+1) <= C_M [z^n] y^2/(1-a y)^2,
    C_M = g [20/3 + B(a+2)].

The five sufficient contributions to C_M are g, 3g, Bga, 2Bg and 8g/3. This is an all-order coefficient bound, not a finite sampled series test.

## Metric source reconstruction

The exact compatible identity is S_p,n=H c_n-q_M,n/r_n with r_n=-6hn. The authenticated k lower bound is greater than 1/10000, so h>1/100. At order n>=1, n||c_n||_(2n+1)<=U_n(c). The prior tracefree estimate has denominator (1-y)^2, which is coefficientwise bounded by (1-a y)^2 in the inverse sense. Therefore

    n||S_p,n||_(2n+1) <= C_Sp [z^n] y^2/(1-a y)^2,
    C_Sp=Hbar C_T + C_M/(6/100).

The coefficient C_T is inherited from the independently audited tracefree estimate on this same working collar. Both estimates start at quadratic order. Scalar/radial and wall source estimates, response constants on this collar, complete majorant closure and an allowed charge-amplitude range remain to be established.
