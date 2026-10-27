# Paper A: regular turning index and wall response

Scientific synthesis prepared within the authorized window beginning 2026-10-13T16:44:34Z and ending 17:44:34Z. The packet's final closure and completion audit remain separate from this report. No numerical scientific test, background solve, spectral solve, parameter scan or resource lease was launched in this window.

## Main result

The scalar-turn structure fixes the negative-shifted spectral index under explicit canonical-action, exact-background and endpoint hypotheses. If the background scalar derivative has n interior zeros, there are exactly n regular eigenvalues with

    μ<-4k,

for every permitted pair of finite wall Hessians and their Dirichlet limits. These eigenvalues are real and simple, have positive regular kinetic norm, and each continues across the compact reciprocal-Hessian rectangle. Stiffening either wall raises each branch, but its double-Dirichlet ceiling stays strictly below -4k. The index is a count of scalar turns within this regular endpoint-preserving class; it is not a universal topological or nonlinear stability claim.

This explains why the predecessor's tracked mode saturates below the curvature-shift threshold. Its persistence is now a consequence of the background turn structure and endpoint conditions, with no numerical eigenvalue seed required for existence.

For the inherited central quadratic background, an analytic minimum argument using its already accepted exact endpoint signs proves exactly one scalar minimum. Convexity then proves T'>0 throughout the interval. A regular shifted wall coordinate extends the result to every nonnegative wall-Hessian pair, from zero Hessians to either or both Dirichlet limits, including softening below20. Thus there is exactly one regular eigenvalue in the entire μ<-4k sector for all κ_a,κ_b>=0 and their infinite-stiffness limits, with one uniform positive gap below -4k on this compactified family. It is the strictly lowest regular admissible scalar mass and the fastest tachyonic amplitude channel among those separated modes. This is stronger than the old uniqueness statement within a narrow numerical mass strip. It retains the predecessor's exact-background, action and interval-validity premises.

Wall-Hessian tuning alone therefore cannot stabilize this supplied convex-turn background within the declared canonical sector. Any successful stabilization would have to leave at least one theorem hypothesis, such as the exact background/turn structure or action and boundary class. This is a necessary condition on a possible alternative, not evidence that any alternative works.

## What was established

| Result | Added content | Proof and independent receipt |
|---|---|---|
| Seed-free general-potential existence | A division-free zero-shift auxiliary solution and an explicit large-negative-mass invariant cone give opposite determinant signs. This constructs a negative-shifted mode from background predicates alone. | `GENERAL_THEOREM_PROPOSAL.md`; `GENERAL_THEOREM_REVIEW.json` |
| Exact turning index | An off-shell regular Green identity gives a strictly increasing endpoint phase. Its zero-shift winding counts precisely the interior zeros of T, including the lower-corner phase lift and both boundary faces. | `TURNING_COUNT_THEOREM.md`; `TURNING_COUNT_REVIEW.json` |
| Spectral reality | Conjugate Green pairing and the positive regular norm force every regular admissible eigenvalue to be real. | `SPECTRAL_REALITY_COROLLARY.md`; `SPECTRAL_REALITY_REVIEW.json` |
| Compact-family robustness | An exact compact family with uniform regularity and strict endpoint margins has a constant finite sector count and ordered continuous branches, smooth when the family is smooth. No such family is constructed here. | `COUNTING_FAMILY_COROLLARY.md`; `COUNTING_FAMILY_REVIEW.json` |
| Explicit protected gap | Background suprema and a Gronwall bound give an explicit positive symbolic δ with all negative-shifted roots confined to `-q0²<λ<-δ`. No numerical δ is claimed. | `EXPLICIT_GAP_COROLLARY.md`; `EXPLICIT_GAP_REVIEW.json` |
| DD asymptotic and allocation | `μ_DD-μ=A_a/κ_a+A_b/κ_b+O((1/κ_a+1/κ_b)²)`, with positive exact coefficients. At large total Hessian K the unique optimal split approaches `κ_a/K=√A_a/(√A_a+√A_b)` and the minimum deficit is `(√A_a+√A_b)²/K+O(K^-2)`. | `STIFF_LIMIT_ALLOCATION_COROLLARY_V2.md`; `STIFF_LIMIT_ALLOCATION_REVIEW_V2.json` |
| Endpoint-only DD test | Opposite nonzero endpoint scalar derivatives suffice for a negative-shifted DD mode; explicit sufficient finite-Hessian thresholds are given. Field reflection covers the reversed orientation. | `ENDPOINT_AND_GROWTH_COROLLARIES.md`; `ENDPOINT_AND_GROWTH_REVIEW.json` |
| Convex-range uniqueness | V''>=0 over the traversed scalar range forces exactly one turn, hence exactly one negative-shifted mode under the other theorem hypotheses. | `CONVEX_RANGE_SINGLE_TURN_COROLLARY.md`; `CONVEX_RANGE_SINGLE_TURN_REVIEW.json` |
| Every positive wall Hessian | The weighted identity `(a⁴T')'=a⁴CT`, C>0, proves T'>0 throughout the convex background, making the endpoint predicates valid for every positive κ pair. This covers softening as well as stiffening. | `CONVEX_ALL_POSITIVE_HESSIANS_COROLLARY.md`; `CONVEX_ALL_POSITIVE_HESSIANS_REVIEW.json` |
| Zero-to-Dirichlet compact family | Shifted reciprocal coordinates include zero Hessians as regular faces. The cone, norm simplicity and count extend to the full nonnegative square, with a uniform symbolic gap and unique DD maximum. | `CONVEX_NONNEGATIVE_COMPACT_THEOREM.md`; `CONVEX_NONNEGATIVE_COMPACT_REVIEW.json` |
| Central exact application | Existing exact rational signs plus the quadratic minimum lemma establish the single-turn premise without a numerical turn search. | `CENTRAL_SINGLE_TURN_APPLICATION.md`; `CENTRAL_SINGLE_TURN_REVIEW.json` |
| Physical linear growth | Every supplied μ<-4k admits a growing de Sitter perturbation with local rate σ>H. A compact-annulus Fourier construction supplies real smooth finite-spatial-norm packets with that asymptotic local/comoving-amplitude growth rate. | `ENDPOINT_AND_GROWTH_COROLLARIES.md`, `FINITE_PACKET_GROWTH_COROLLARY_V2.md`; corresponding accepted reviews |
| Lowest-mode identity and growth order | Spectral reality and the exact single-turn index identify the central/convex branch as the strictly lowest regular scalar mass. Other possible tachyons have amplitude rates below H, while this one has rate above H. | `LOWEST_MODE_AND_GROWTH_ORDER_COROLLARY.md`; `LOWEST_MODE_AND_GROWTH_ORDER_REVIEW.json` |

The kinetic norm and Green identity are the regular action-derived ones. No singular scalar-gradient weighted norm, artificial interior boundary or reduced-domain completeness theorem was imported.

## The actual hypotheses

The reusable theorem assumes a supplied exact smooth finite canonical Einstein–scalar background with a>0, k>0, no wall kinetic/induced Einstein terms, and the declared generic scalar sector. In the original field orientation it requires T_a<0<T_b and positive baseline Hessians with `B_a0=κ_a0 T_a/2-T'_a<0`, `β_b0=-κ_b0 T_b/2-T'_b<0`. The action path changes wall Hessians by potentials with zero background value and first derivative. The bulk V may be smooth and need not be quadratic or convex for the general index theorem. Convexity is used only for the single-turn corollary.

No exact background is created by these spectral theorems. The central source map identifies the existing exact coefficients and signs and preserves their historical certification assumptions. Uniform-background-family statements apply only after a genuine compact family of exact backgrounds meeting the required margins is supplied. The later nonnegative theorem includes zero Hessians through a new regular compactification and its own proof, rather than inferring them from a noncompact positive-quadrant limit. Negative Hessians remain outside the accepted range.

## Preserved failures and corrections

Two local errors were caught by independent review and corrected in separately named V2 artifacts. Both V1 files and blocking receipts remain unchanged.

1. The first stiffness-allocation note incorrectly claimed normalization invariance for an A_a expression already specialized to ψ_a=1. The corrected arbitrary-normalization expression includes ψ_a² in the numerator. The normalized asymptotic and allocation proof was otherwise accepted.
2. The first finite-packet note assigned the proper-volume factor e^(3Ht) to an L² norm rather than its square. V2 distinguishes the norm factor e^(3Ht/2), and separates local amplitude growth from the integrated proper-volume norm's additional expansion factor.

Neither correction changes the seed-free existence, turning index, central single-turn conclusion or compact response theorem. The failure evidence is part of the packet, not silently replaced.

## Novelty and significance boundary

`PRIMARY_LITERATURE.md` compares the result with Frolov–Kofman, Lesgourgues–Sorbo, Konikowska–Olechowski–Schmidt, Olechowski, finite-potential work, Robin asymptotics, and earlier braneworld nodal arguments. Arbitrary V, curved slices, scalar-turn instability, spectral monotonicity, Robin limits, determinant parity and tachyonic de Sitter growth all have precedents. The defensible added content is the explicit regular curved finite-wall proof, its exact restricted turning index and quantitative continuation consequences, tied to a certified example. Historical priority and publication novelty are not established by this targeted comparison.

## Remaining gate and next work

The full physical-tachyon count is still open because additional masses could lie in `-4k<=μ<0`. The new theorem excludes a root at -4k but does not count the rest of that band. `REMAINING_TACHYON_BAND_GATE.md` derives the appropriate diagnostic: certify the unwrapped endpoint phase up to μ=0. A terminal determinant sign alone gives parity and cannot exclude an additional pair of roots. `ZERO_HESSIAN_REMAINING_BAND_GATE.md` refines the prospective target: additional target-wall tachyons inject into those at the zero-Hessian corner, so emptiness there would exclude extras throughout the nonnegative family. That emptiness premise is unevaluated. The zero-Hessian conditions are L_a=L_b=0, not ordinary f'=0 Neumann conditions.

Ranked next tasks, with no automatic execution authority:

1. Certify the central remaining-band phase at the zero-Hessian corner, after a frozen independent preflight, phase-lift/massless-endpoint convention and resource lease. Estimated setup, bounded calculation and review: approximately 1–3 hours, conditional on the actual validated formulation. If that corner has no additional tachyon, the comparison theorem gives exactly one physical scalar tachyon throughout the nonnegative wall family. This is higher payoff than the earlier baseline20 proposal; a positive extra count would instead be retained as the corner result without an all-family equality claim.
2. Quantify DD data and A_a,A_b with a separately gated validated solve, approximately 1–2 hours if conditioning permits. Payoff: numerical gap/response and an actionable large-stiffness allocation estimate.
3. Construct and certify a compact family of exact backgrounds, requiring a specified physical parameter path and several hours or more. Payoff: a uniform family theorem with actual verified members, beyond a single central solution.

No full-spectrum completeness, nonlinear evolution, collapse, child formation, event horizon, halo or cosmological conclusion follows. No manuscript, inventory or shared-record update was made. Hash-bound independent receipts and the claim inventory identify the accepted proof layer and preserved failed versions.
