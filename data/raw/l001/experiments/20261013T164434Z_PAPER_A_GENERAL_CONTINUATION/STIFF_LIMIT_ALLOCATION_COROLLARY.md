# Double-Dirichlet deficit and optimal stiffness allocation

Status: proposed corollary for independent review, conditional on the compact analytic response theorem. This is a quantitative asymptotic formula in terms of exact DD data, not a numerical evaluation or a claim that Robin asymptotic expansions are new.

Fix any one of the negative-shifted branches supplied by the theorem. Let `μ_DD`, `λ_DD=μ_DD+4k`, `Z_DD`, and `L_b,DD` denote its normalized DD corner data. Set

    A_a=36λ_DD²/(T_a² Z_DD)>0,
    A_b=4a_b⁴ L_b,DD²/Z_DD>0.

Analyticity on a neighborhood of the corner and the exact response derivatives give

    μ_DD-μ(c_a,c_b)=A_a c_a+A_b c_b+R(c_a,c_b),
    |R(c_a,c_b)|<=C(c_a+c_b)²                      (1)

for a sufficiently small nonnegative corner neighborhood and a finite constant C. The constant exists by a bound on the second derivatives there; no numerical value is claimed. First derivatives of R are O(c_a+c_b) and second derivatives are bounded. In physical Hessians this yields

    μ_DD-μ(κ_a,κ_b)=A_a/κ_a+A_b/κ_b
                      +O((1/κ_a+1/κ_b)²).        (2)

The coefficients are invariant under constant rescaling of the mode: the numerator and Z scale equally. Formula A_a uses the chosen a_a=1 background normalization.

## A fixed total Hessian budget

Let `κ_a+κ_b=K`, with `κ_i>=κ_i0`. For large enough K, the feasible set is a nonempty compact interval. Maximize this branch's physical μ, equivalently minimize its positive deficit `D(c)=μ_DD-μ(c)`.

The strict derivative formulas and compactness give constants `0<m<=M<∞` such that each partial derivative D_ci lies between m and M throughout the full reciprocal rectangle. Integrating along the segment from the DD corner gives

    m(c_a+c_b)<=D(c_a,c_b)<=M(c_a+c_b).           (3)

The feasible balanced pair κ_a=κ_b=K/2 has deficit at most 4M/K for all sufficiently large K. Any global minimizer must therefore satisfy

    1/κ_a+1/κ_b<=4M/(mK),
    κ_a,κ_b>=mK/(4M).                            (4)

Hence every minimizing sequence enters the corner with both reciprocal coordinates O(1/K); for large K it is interior relative to the baseline constraints. This justifies using (2) uniformly at optimizers, rather than assuming in advance that both walls receive comparable stiffness.

Write `t=κ_a/K`. On the fixed compact fractional interval supplied by (4),

    K D = A_a/t+A_b/(1-t)+O(1/K).

The leading function has its unique minimum at

    t0=√A_a/(√A_a+√A_b).

Uniform convergence proves t→t0 for every global optimizer and gives

    min D=(√A_a+√A_b)²/K+O(K^-2).               (5)

The stationary condition, using the derivative remainder after (1), strengthens the allocation to

    κ_a/K=t0+O(K^-1),
    κ_b/K=1-t0+O(K^-1).                         (6)

Indeed the stationary equation is `A_a/t²-A_b/(1-t)²=O(1/K)`, whose derivative is strictly negative and bounded away from zero near t0. For sufficiently large K the global optimizer is unique: along the budget line the deficit has second derivative

    2A_a/κ_a³+2A_b/κ_b³+O(K^-4)>0

uniformly on the compact fractional interval containing every possible optimizer. Thus strict convexity there excludes two global minima. No global convexity for finite or small K is assumed.

The budget here is the sum of total Hessians. A budget on increments `η_a+η_b=E` is the same feasible problem with `K=E+κ_a0+κ_b0`; the leading large-budget fraction and coefficient are unchanged. Increasing stiffness raises this mode, but the theorem's DD ceiling remains strictly below -4k, so no allocation stabilizes it within the declared action family.

## Uniform version and limitations

For a compact smooth background family with ordered branch labels as in COUNTING_FAMILY_COROLLARY.md, continuous derivatives on the compact family give uniform positive bounds on A_a,A_b and uniform finite Taylor bounds, provided the coefficient dependence is sufficiently smooth to differentiate twice. The above estimates then hold uniformly on that family. This is a conditional family corollary, not an assertion that such a family has been constructed.

These formulas predict how much additional stiffness is needed to approach the DD ceiling and how to divide a large budget between walls. They do not give the uncomputed coefficients numerically, claim a finite-budget global optimum without the large-K condition, or optimize any nonlinear fate or full-spectrum stability criterion.
