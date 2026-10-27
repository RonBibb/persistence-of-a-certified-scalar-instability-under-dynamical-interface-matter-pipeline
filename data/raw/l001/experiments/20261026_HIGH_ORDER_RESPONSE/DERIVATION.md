# A real axis high order scalar response bound

For the accepted scalar boundary problem, suppose n>=N, |a|<=A, cn²<=V<=vn² and beta>=1 at both walls. Let L be interval length, F0 the supremum of bulk forcing, and G the maximum magnitude of the two Robin loads. All statements below concern real solutions on the real interval, not the complex collar or the full nonlinear branch.

Choose lambda>0 with lambda²+A lambda/N<=c and lambda N Lmin>=1. The positive barrier

    w(x)=F0/(cn²)+2G/(lambda n) [exp(-lambda n x)+exp(-lambda n(L-x))]

satisfies (-d²+a d+V)w>=F0. Its outward Robin data dominate G: each wall derivative contributes 2G[1-exp(-lambda nL)]>=G, since exp(-1)<1/2, and the beta*w contribution is nonnegative. The maximum principle applied to w-f and w+f gives

    n² M0 <= F0/c + 4nG/lambda,
    Mj=||d^j f/dx^j||_infinity.

When nLmin>=2, every point admits a left or right Taylor segment of length 1/n. Taylor's integral remainder yields

    M1 <= 2n M0 + M2/(2n).

The differential equation gives M2<=A M1+v n²M0+F0. If A<2N, put S=F0+nG and define

    C_value = max(1/c,4/lambda),
    C_first = [(2+v/2) C_value+1/2]/[1-A/(2N)],
    C_second = (A/N) C_first+v C_value+1.

Then n²M0+nM1+M2 <= (C_value+C_first+C_second) S uniformly for all integer n>=N. Regular second-order ODE boundary theory and uniqueness from the maximum principle give the inverse on this real scalar problem; this is not a proof for arbitrary incompatible Einstein source triples.

## Bound inputs

Use the archived diagnostic background extrema and cutoff constants without narrowing. W(0)=0 and Wprime=H give E<=exp(H0 Lmax). The check tests that this is below 8 using outward Arb arithmetic. With k<=k_upper,

    |V_n| <= [m0+36 k_upper*64+2T0²+C0] n²,

where C0 bounds the rational B0*Tprime/D term at n=1 and therefore safely overbounds it for all larger n. This deliberately loose v is sufficient, not optimized.

The proposed fixed choices are N=39 and lambda=1/64. All barrier, segment-length, derivative-absorption and exponential gates must pass in each representation before reporting numbers. The scalar sum bound does not yet provide the constrained metric estimate, a complex-collar inverse, nonlinear source constants, low-order inverse bounds or an amplitude radius.

## Evidence scope

The calculation is a one-core Linux diagnostic using exact Fraction arithmetic and one outward exponential bound per representation. It inherits the preceding authenticated background reduction; no trajectory is evolved. Analytic review and arithmetic replay are separate. The governing cutoff extraction has source review but no independent arithmetic replay, so this successor does not upgrade the whole chain to a fully audited numerical certificate.

## Measured outcome

Both representations passed all numerical gates for N=39 and lambda=1/64. The exact rational sums are in RESULT.json; their approximate displays are 3931.5286351954646 (primary) and 3929.0884785528565 (independent). Outward integer rounding therefore permits the common bound

    n² ||f|| + n ||fprime|| + ||fsecond||
        <= 3932 [||F|| + n max_i |g_i|],   integer n>=39.

This is a conservative bound, not a measured physical amplification factor. The independent analytic reviewer `/root/concave_count_review` checked the barrier, outward boundary signs, Taylor estimate and absorption algebra without finding a blocker. That review did not independently replay the numerical arithmetic or the background extraction.

The inspected low-order nonresonance dependency and full-flow certificates provide nonzero matching denominators, but not general source-to-solution norms. They remain useful inputs for orders 1–38; their denominators must be combined with full fundamental-solution and forcing bounds before they can replace those low-order inverse estimates. Thirty-eight new trajectory solves are not implied.

No scientific process remains running from this calculation. The immediate outstanding real-axis task is quantitative low-order inverse control, followed by the separate complex-collar and nonlinear-source bounds needed for the amplitude result.
