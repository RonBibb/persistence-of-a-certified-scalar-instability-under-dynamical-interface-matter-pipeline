# Low order informed tail certificate

## Result and purpose

This design replaces the unresolved finite-amplitude correction-inverse proposal with a scalar tail certificate for the already established compatible homological recursion. It does not assume that arbitrary trial fields satisfy the Einstein constraints or that the background inverse is an inverse about a nonzero solution. Independent mathematical review accepts the construction under the inherited recursion premises.

The design is mathematically specified; a useful-amplitude certificate has not been computed. A cheap, explicit feasibility gate comes before any cubic replay. In particular, keeping both the inherited scalar majorant constant and seed bound cannot certify an amplitude radius 48 times the current one by this contraction test. That limitation belongs to the estimates, not the nonlinear solution.

## Fixed branch and inherited premises

Use the same zero-current action, exact background, selected growing mode, parameter correlations, affine pulled chart and ordinary powers of `eta=epsilon exp(r t)`. Keep `p1(a)=1` and the zero first-order graph displacement. The original exact background, spectrum and validated homological coefficient premises remain unchanged.

Let `Y_n` be the aggregate norm from the certified majorant derivation on its fixed complex radial collar:

`Y_n = U_n(p_n)+U_n(b_n)+U_n(f_n)+n^3 sum_i(|xi_i,n|+|chi_i,n|)`,

`U_n(v)=n^2 ||v||_(2n)+n ||v'||_(2n+1)+||v''||_(2n+2)`.

These are the existing weighted Nagumo norms. For every `n>=2`, the inherited all-order estimates give

`Y_n <= [z^n] G(sum_(j<n) Y_j z^j)`,

`G(w)=K w^2/(1-Kw)^2`, with positive `K` and nonnegative Taylor coefficients.

This is a bound on the actual recursively constructed coefficients. The complete bulk and wall compatibility argument already applies to that recursion. A scalar comparison sequence need not itself be a physical field configuration. This distinction removes the previous arbitrary-forcing inverse gap.

## Same norm low order data

Supply outward constants `a1,a2,a3>=0` with `Y_j<=a_j` for `j=1,2,3`, on the same collar and with the same parameter correlations. Initially `a1=16444` is the inherited seed bound. A sharper seed is a separate, explicitly qualified input.

Define `P(z)=a1 z+a2 z^2+a3 z^3`. This is a scalar norm polynomial, not the field polynomial or a fitted separation curve. Raw real-axis boxes do not establish its complex weighted norms. Qualify those norms by analytic continuation/jet estimates before treating them as certificate inputs.

The existing seed chunks preserve full quadratic-engine states, so quadratic replay is not automatically necessary. Cubic scalar profiles are missing. Whether exporting those profiles is worth doing is decided by the feasibility gates below, not by the mere fact that they are missing.

## Scalar tail map

Let `varrho>0` denote the scalar-series amplitude radius; it is not the physical growth rate `r`. Work in the Banach algebra of absolutely summable scalar series with norm

`||V||_varrho=sum_n |V_n| varrho^n`, restricted to `V_0=...=V_3=0`.

Define the map

`T(V)=Pi_(>=4) G(P+V)`.

The projection has norm at most one. Because `G` has neither a constant nor a linear term, every order of this map depends only on lower orders. Its degree-two and degree-three coefficients, independent of `V`, are exactly

`B2=K a1^2`,

`B3=2K a1 a2+2K^2 a1^3`.

Set `p=P(varrho)` and

`e=G(p)-B2 varrho^2-B3 varrho^3`.

Here `e>=0` is the exact higher-degree mass of the positive scalar majorant, not a subtraction of uncertain physical residuals. Exact rational arithmetic or outward interval arithmetic must preserve that distinction.

For a proposed tail bound `delta>0`, require all of:

1. `K(p+delta)<1`.
2. `e + G(p+delta)-G(p) <= delta`.
3. `L=G'(p+delta)=2K(p+delta)/(1-K(p+delta))^3 < 1`.

The second inequality is the self-map bound. The third is a genuine scalar-series contraction bound: multiplication is bounded in the specified algebra, projection is bounded, and the positive power-series coefficients give the displayed difference estimate. No derivative bound for a physical PDE map is inferred from it.

Iteration from zero has nonnegative coefficients, stays in the ball and converges to its unique scalar tail fixed point. Induction on harmonic order gives `Y_n<=T_n` for every `n>=4`: the three low orders are bounded by `P`, and each later actual coefficient depends only on lower ones and obeys the inherited positive majorant. Thus the actual branch converges wherever the resulting scalar norm estimate, radial-collar restriction and admissibility bounds permit.

## Converting the scalar certificate into physical statements

Restrict to the inner half of the existing radial collar. The factor `4^n` from the radial weights requires the physical amplitude disk `|eta|<varrho/4`; fixed derivatives converge on strict inner disks. Do not quote `varrho` itself as the physical radius.

Recompute all composition, chart-Jacobian, timelike-wall and lapse bounds using `p+delta`, not the preceding certificate's smaller norm bound. The relation `K>=1/a_eval` retains the source-envelope domain when the first gate holds, but does not replace the physical admissibility checks.

Recompute the proper-separation and proper-clock observable suprema and their Cauchy tails. Bind the authenticated signed low-order observable coefficients separately. A pass of the scalar tail gates alone establishes neither a new signed-motion interval nor a charged-branch result.

## Feasibility before export

Predeclare the desired physical-radius improvement before evaluating a target ladder. Keep this separate from a scientific pass criterion or a predicted physical scale.

For the fixed inherited `K` and `a1=16444`, first use the optimistic idealization `a2=a3=0`. All scalar self-map and derivative expressions are monotone in nonnegative `a2,a3`; this idealization supplies necessary feasibility checks, not valid actual low-order norm bounds.

At a requested physical radius `eta_target`, use `varrho=4 eta_target` and `w=K a1 varrho`. If `w>=1`, the domain fails. If `2w >= (1-w)^3`, even the derivative at zero correction is at least one; no nonnegative correction radius can pass the stated contraction gate. Such failure rules out only this fixed majorant/seed certificate. Passing this necessary gate does not establish a feasible tail radius; the optimistic self-map test still has to pass.

An exact method ceiling is available without any profile export. At `w=1/4`, `G'=32/27>1`. Therefore the contraction test requires

`eta_target < 1/(16K a1)`.

The current radius is `eta_old=1/(768K a1)`, so the same `K,a1` route necessarily fails at or above `48 eta_old`. This is a loose upper ceiling for this test; the actual feasible value can be smaller. It says nothing about a sharper seed, a different norm, a sharper coefficient majorant or the physical continuation radius.

**For the stated useful-amplitude objective, do not authorize cubic export merely to rerun this unchanged bound.** First qualify a sharper, still coefficientwise positive source/response estimate or a meaningfully sharper seed and repeat the inexpensive feasibility gate. Any replacement `G_new` must be proved to dominate the compatible recursion for all orders; it cannot be a fit to three coefficients. The same tail construction then applies with the actual degree-two and degree-three coefficients of `G_new(P)` removed.

## Implementation and review gates

1. Authenticate the selected background/mode, all-order recursion, source envelope, inverse, normalization and current terminal records.
2. Qualify the candidate coefficient majorant and its domain. A generic nonlinear correction inverse is not part of this route.
3. Freeze the target ladder and evaluate the optimistic necessary gate and scalar self-map feasibility. Retain every failed target. Stop the route if the desired gain is impossible for those inputs.
4. Only if promising, qualify the same-collar low-order norm bounds. Reuse quadratic data; size a cubic-only export if required. Preserve full affine channels, uncertain shooting coefficients, Taylor/remainder models and wall data.
5. Freeze actual outward norm inputs and rerun all three scalar tail gates. Verify degree projection, positivity and radial-collar conversion independently.
6. Recompute physical and observable gates, then independently review the complete result. Publish the scalar design, its numerical realization and the physical claim as distinct statuses.

Scientific execution remains Linux-only under the established runtime, thread caps and L001 lease. A computation projected above one hour requires atomic exact-resumption checkpoints before launch, with approximately 15-minute recovery boundaries. No frozen parent or manuscript is changed by this design. No new evolution or cubic export is launched by this document.

## Exact implementation controls

A future scalar validator must test: correct `B2/B3` removal; zero tail coefficients through degree three; the same outward inequality for both positive and signed trial series; rejection at the pole; strict contraction rejection at equality; rejection at `w=1/4`; derivative value `128/343` at `w=1/8`; a deliberately failed self-map despite a passing necessary derivative test; normalization and `varrho/4` conversion; and refusal to treat optimistic zero low-order norms as actual data. These are short algebraic controls, not substitutes for the inherited analytical premise.
