# First conserved-current correction to physical separation

Status: prospective analytical scope only. No symbolic program, numerical calculation or scientific audit was executed for this note. No implementation or launch is authorized by this note itself.

## Proposed question

On the actual selected AB action, what is the first response of proper interface separation to each independently conserved current? Write

`D_phys(t)=D0+z(t)[C_a N_a²+C_b N_b²]+O(z²)`,

where `z=δ² exp(−6ht)`, `h=√k`. Compute bounded enclosures of `C_a,C_b`, separating bulk metric and physical graph contributions. This is a small-charge derivative on the declared analytic redshift branch. It is not a finite-charge trajectory, a charged spectral mode, a numerical charge radius, or nonlinear stability/formation.

The exact selected action and all central background inputs are already specified. A first-order coefficient does **not** require an existing numerical charged trajectory, but it requires a newly admitted forced-boundary solver and independent verification of the following reduction.

## Source and chart

Read-only source: `papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md`, Section5.1, AppendixA, AppendixC.1–C.3, specifically Q1–Q7 and S2,S6,S7. The source must be freshly hashed into an admission on Linux. Numerical background engines and exact intervals are those already bound for T2; no midpoint background or different action is substituted.

Use original proper radial coordinate `s` and the manuscript's redshift time `t`, with moving interfaces `S_i=s_i+z ξ_i1+O(z²)`. Radial metric is `g_ss=exp(2b)`. At fixed declared time, the proper length is the integral between these actual endpoints. Therefore its first coefficient is

`C=∫b1 ds + ξ_b1−ξ_a1 = −2∫p1 ds + ξ_b1−ξ_a1`.

This expression includes both embeddings and is invariant under first-order transverse-coordinate relabeling because the lapse integral and endpoint shifts cancel. It must not be replaced by the later curvature-clock coordinate width `q` without reconstruction. The neutral proper separation is time independent, suggesting first-order cut shifts contribute no background-distance derivative; however, any stronger statement equating clock charts needs an explicit gauge review. The computational observable may simply remain the proper separation on the specified redshift cuts.

## First-order source reduction to review

At n=1 the truncation in Q1 has no positive-order bulk fields. The composed background obeys its equations and D annihilates it. There is no direct bulk current stress. Thus

`q_T1=q_M1=q_K1=q_R1=0`, `c1=b1+2p1=0`, `S_p1=S_c1=S_g1=0`.

The regular bulk equations are consequently the same neutral homogeneous three-variable equations, now at the forced temporal mass

`μ1=−18k`, `λ1=μ1+4k=−14k`.

This is not the unstable mode mass. The background and mass are correlated: compute k from the exact launch, then set μ1=−18k in that same flow. Interval enclosure can retain a broader box but must enclose that correlation, not replace k by a numerical midpoint.

For the selected centered action, `c(Φ_i*)=1`, `c_Φ=−1/1000`, `ν_i²=z N_i² E_i⁶+O(z²)`, `E_i=a_i^-1`. The first graph coefficient in the manuscript is

`ξ_i1=σ_i N_i² E_i⁴/(42k)`.

At the zero-order truncation the oscillator residual has no explicit current term, hence `o_i1=0`. Q5's normalized scalar residual supplies

`j_i1=−σ_i c_Φ N_i² E_i⁶/2 = σ_i N_i² E_i⁶/2000`.

With `d_i=2−μ1 E_i²=2+18kE_i²` and `Γ_i=21−1/d_i`, Q6 reduces to

`2σ_i(g_i+2T_i p_i)−Γ_i f_i = R_i`,

`R_i=(Γ_i T_i−2σ_i T_i')ξ_i1 − N_i²E_i⁶/1000`.

The surface oscillator coefficient is `χ_i1=(f_i+T_i ξ_i1)/d_i`. The graph term here is essential; using the neutral `u=f/d` would give the wrong charged response. Independent currents must be treated separately, not constrained by a density ratio. Phase integration constants can be fixed as in the branch construction; phases do not add another free first-order stress once the two conserved density labels are fixed. The local exchange and junction compatibility must nevertheless be checked from the complete action, not assumed because a scalar solution exists.

## Smallest numerical realization

Use unchanged inherited bulk interval recurrences at768 bits and the existing spatial steps. A common homogeneous solution `H` obeys the homogeneous lower selected boundary law with `p_a=1`. A particular solution `P_a` supplies the lower-current load with `p_a=0`. The upper-only load has zero particular initial state; its response is a multiple of H. Thus each engine needs two regular propagations, not a full nonlinear evolution.

For a lower boundary load R_a define `B=Γ_aT_a/2−T_a'`. Constraint plus lower scalar wall row give

`f_a=[3λ1 E_a² p_a−T_a R_a/2]/B`,

`g_a=Γ_a f_a/2+R_a/2−2T_a p_a`.

Require B separated from0. For the homogeneous solution set R_a=0,p_a=1. For the lower-load particular solution set its unit-current R_a,p_a=0. The upper homogeneous determinant is

`F_H=g_H+2T_b p_H+Γ_b f_H/2`.

Require its full uncertain-wall interval to exclude0. If a validated upper particular value is F_P and required upper load is R_b, the homogeneous multiplier is

`c_H=(−R_b/2−F_P)/F_H`.

The response is `p=c_H p_H+p_P`, similarly for f,g, and the separation integral follows from the corresponding linear combination of saved integrals. Upper-only has P=0. Lower-only has R_b=0. Correlations may widen interval output but do not justify selecting midpoint coefficients or favorable endpoints. If determinant or final sign remains unresolved, preserve that outcome.

The upper background and Γ,R,ξ must be enclosed over the **entire uncertain wall**, not at D_hi alone. Integrals require exact mandatory-prefix and optional-tail treatment as in T2, plus saved outward dyadic contributions for an independent rational re-sum. Save each response's `C_bulk`, `C_graph`, `C_total`, both endpoint loads, graph coefficients, oscillator coefficients, and consistency residuals.

## Independent prospective gates

1. Derive Q5's first-current sign and Q6's loaded Robin row independently from the undivided scalar/oscillator/Israel equations. Confirm c_Φ and reflected half-factors. This is the largest new scientific gate.
2. Verify the zero-current case gives zero forced response; verify source linearity separately in N_a² and N_b². Do not call an independent-current sum a finite nonzero-charge solution.
3. Exact algebra controls: loaded lower constraint, scalar row, oscillator row with displaced trace, upper multiplier formula, transverse gauge cancellation of the proper-length variation. Execute all symbolic/exact checks on Linux only.
4. Fresh whole-cell background, Hamiltonian and perturbative constraint enclosures; μ1=−18k relation; positive warp; complete uncertain endpoint coverage; nonzero B and F_H. The manuscript's nonresonance theorem is a premise, not a substitute for a numerically nonzero inverse denominator.
5. Both copied independent bulk engines must overlap on each coefficient and contribution. Use hulls; retain opposite or unresolved signs. Full current-source field-equation and wall-compatibility residual checks should be derived before accepting a charged coefficient result.
6. Resource gate: one leased core, under an agreed sub-hour cap, remaining time for independent review. No >1h trajectory or automatic extension. No rescue precision/mesh/source tuning after seeing output.

## Readiness and cost assessment

Mathematical inputs are present; the crucial missing work is independently qualified source reduction and forced-solution assembly. The background engines already accept a general negative mass and regular launch; no singular scalar-turn matching is needed. Two propagations per engine are modest compared with T2's bisection sequence. Computational cost is plausibly minutes based on earlier engine timings, but no fresh probe has measured this mass/load. Review and implementation, not integration, likely dominate.

This looks feasible within a substantial remaining portion of the allocation **if** the first-current source and full compatibility gates can be independently admitted. If those gates remain unproved, the correct product is this concrete boundary-value specification and missing derivation, not an unqualified number. Even a successful C_a,C_b measurement would leave the analytic convergence radius, higher-order error, finite-charge existence verification and growing perturbation on that branch uncomputed.
