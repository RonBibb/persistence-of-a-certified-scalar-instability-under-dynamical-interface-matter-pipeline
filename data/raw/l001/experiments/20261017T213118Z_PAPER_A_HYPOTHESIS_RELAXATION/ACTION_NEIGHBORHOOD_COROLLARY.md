# Complete count in a local action parameter neighborhood

Status: analytical corollary proposed for independent terminal review. This is the same implicit-function and strict-phase-margin argument as LOCAL_TOTAL_COUNT_PERSISTENCE.md with a finite parameter vector, not a new numerical certificate or an arbitrary function-space theorem.

## Statement

Let

    eta=(m²,gamma,v0,v1,lambda_a,lambda_b,q)

vary near the original exact parameter vector eta_* with q=0, keeping the canonical doubled-cover action and its generic regular scalar sector. Use

    V_eta(Phi)=m²Phi²/2+qPhi⁴/4,
    tau_a,eta=lambda_a+gamma(Phi-v0)²/2,
    tau_b,eta=lambda_b+gamma(Phi-v1)²/2.

There is an open neighborhood U of eta_* in R^7 such that each eta in U has a unique local simultaneous-wall solution (A(eta),D(eta)) near the original exact root, with a>0,k>0, one turn and positive T'. For every such background, the entire nonnegative background-preserving wall-Hessian family has exactly one regular physical scalar tachyon. U is existential and unquantified. Global bounded-below quartic selection restricts this result to U intersect {q>=0}; no claim that the unrestricted negative-q potentials are globally bounded below is intended.

## Proof

The lower launch is

    a_a=1, Phi_a=A,
    H_a=-[lambda_a+gamma(A-v0)²/2]/6,
    T_a=gamma(A-v0)/2,
    k(A,eta)=H_a²-1-T_a²/12+m²A²/12+qA⁴/24.

The bulk flow and upper residuals F(A,D,eta) are smooth jointly in all arguments around the original positive-warp closed trajectory. The inherited exact nonzero determinant D_(A,D)F at eta_* therefore gives a smooth local root graph by the finite-dimensional implicit-function theorem. No derivatives of numerical root estimates with respect to eta are substituted. A small ball U can be chosen with m²,gamma,D,k positive, positive warp, opposite endpoint T signs and T'>0 throughout the rescaled interval x=s/D(eta). These are all strict central properties, preserved by uniform continuous dependence on the compact x interval.

At physical mu=0 and zero perturbative Hessians, the normalized regular launch varies smoothly in eta. The vector z=L+if remains nonzero; at the central parameters it has a positive minimum magnitude on the interval. On a small ball U, [0,1] times U is simply connected and the lift anchored at theta(0,eta)=3pi/2 is continuous. The original exact endpoint phase has a strict margin below 3pi/2. Shrinking U preserves that inequality throughout U.

Each background therefore has an empty remaining tachyon band at the soft corner. The endpoint-based compact-wall theorem and injection apply separately to every eta in this same U, giving the claimed quantifiers:

    exists U containing eta_* such that
    for every eta in U and every (c_a,c_b) in [0,1]²,
    the total negative regular scalar count is one.

The size of U is controlled by the background and soft-corner margins, not by taking a separate parameter neighborhood for each unbounded physical Hessian. Compact wall coordinates and injection cover all walls at once. A smaller closed ball inside U can be used when a compact parameter family is needed. □

## Two different variations must remain separate

Varying eta changes the bulk or original wall action, and the background is solved again. This is not background-preserving stiffness tuning. After obtaining that new exact background, independently choose nonnegative perturbative Hessians kappa_a,kappa_b by

    tau_i,eta -> tau_i,eta
       +(kappa_i-gamma)[Phi-Phi_i(eta)]²/2.

The added term has zero value and slope at that background's own wall scalar value. It preserves that background while changing its perturbative Hessian. The theorem's two layers therefore concern a local family of exact geometries, and a full nonnegative Hessian family on each geometry.

## Meaning and limits

The complete count is not restricted to a single exactly tuned numerical parameter point: it holds in some open neighborhood of the original finite-dimensional action parameters. This is qualitative robustness, not a measured tolerance to parameter changes. The existing q~4 interval certificate lies at a separate point and does not acquire a total count from this statement. Local uniqueness does not imply a global first-event cover or rule out remote roots. No statement about arbitrary potential functions, other sectors, nonlinear fate or horizons follows.

This is a conventional smooth-dependence corollary with useful application-specific content. It should be presented as a consequence of the original strict certificates and regular compact-wall proof, not as an independent discovery of structural stability in general.
