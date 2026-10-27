# Second-order nonresonance: inherited theorem versus numerical inverse

Status: read-only dependency assessment; no calculation, new execution, or source modification. This note is prospective and does not admit the full second-order solve.

## Conclusion

The existing same-action argument already excludes a physical homogeneous kernel at **mu_2 = -108 k** on the selected exact neutral AB background. A new spectrum scan or a new theorem of nonresonance is not a prerequisite for the second-order coefficient solve. However, the proposed interval shooting implementation still needs an enclosure of its actual homogeneous upper-wall residual that excludes zero before it divides by that residual. Mathematical invertibility does not make a wide, zero-containing interval numerically invertible.

## Actual dependency chain, rather than the selected-mode bracket alone

Authority inspected: `papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md`, especially Proposition 1, Theorem 2, Appendices B.2, C.1–C.2, M.1–M.4 and O.6. These are the current manuscript/source authorities inherited by the accepted allocation packets. This read-only pass inspected their statements and linkage; it did not re-execute historical arithmetic or freshly hash their bytes.

1. **Restricted physical count and stiffness comparison.** Appendix M constructs the augmented form, removes its artificial zero, and identifies the nonzero constrained physical roots. Its restricted count supplies exactly one physical root below `-4 k`. M.4 obtains nondecreasing eigenvalues under increasing nonnegative wall Hessians from the variational principle on the fixed positive complement. This is the comparison needed here, not an inference from two determinant samples.
2. **A separate baseline mass certificate.** O.6 uses the pure-potential wall problem with both Hessians 20, no oscillator. The original packet is `research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z`. Its opposite-sign whole-wall endpoint enclosures at `-33/25000` and `-131/100000`, together with the restricted count, identify the baseline root `mu_20,20` in that open bracket. O.6 links its six exact action parameters and full launch/distance intervals to the current background, not merely similar approximate profiles.
3. **Apply that comparison to the selected oscillator action.** At a fixed negative mass, the undivided oscillator row has denominator `d_i = 2 - mu E_i^2 > 0`. Eliminating it gives the real wall Hessian `Gamma_i(mu) = 21 - 1/d_i > 41/2 > 20`. A homogeneous physical mode at that fixed mass would therefore be a pure-potential mode for the constant pair `(Gamma_a(mu), Gamma_b(mu))`. Stiffness comparison forces its negative mass to be at least `mu_20,20`.
4. **The n=2 mass lies strictly below that entire allowed region.** O.6 supplies `k > 3/10000` and `mu_20,20 > -33/25000`. Hence the manuscript's exact comparison chain applies:

   `mu_2 = -108 k <= -18 k < -27/5000 < -33/25000 < mu_20,20`.

   This contradicts the necessary mass bound for a homogeneous selected-action mode. The same argument covers every positive-order background-ladder mass `mu_n = -18 n(2n-1) k`.

The stronger complete-negative-count statement in Proposition 1/Theorem 2 also supports the conclusion, but exclusion at `mu_2` specifically needs only the restricted below-`-4 k` count, the baseline mass bracket, and stiffness comparison. The remaining-band phase exclusion need not be rerun for this narrower dependency.

The allocation's T2R1 bracket of the **selected oscillator mode** is not by itself a global exclusion certificate. It is also not the baseline Hessian-20 certificate used in the above proof. These two mass brackets must remain distinct.

## What is and is not inverted

The homogeneous operator is the neutral, regular, constrained `(p,f,g)` system at `mu_2`, with the action-derived undivided Q6 wall rows and eliminated oscillators only after their positive denominators are established. Unknown second-order fields occur in this same homogeneous operator; qualified first-order products supply forcing. It is not the spectrum of a hypothetical nonzero-charge static background.

The constraint and its Q4 compatibility identity are essential: arbitrary solutions of an unconstrained three-component ODE are not automatically physical modes covered by the count. Likewise, graph/tracefree and phase coefficient divisors must be checked separately; they are not certified by the scalar mass bracket. Their nonvanishing at this positive order is provided in Appendix C, with additive phase conventions fixed.

Finite-interval regular ODE boundary theory then supplies the compatible forced inverse in the declared sector. This is not a theorem about arbitrary Einstein–scalar Cauchy data, tensor/vector sectors, a full nonlinear finite-charge solution produced numerically, or a computed convergence radius.

## Remaining numerical gate for the proposed successor

For the prospective shooting architecture in `FULL_SECOND_ORDER_PROPER_SEPARATION_SUCCESSOR.md`, retain the following explicit gate:

- Authenticate the same action, exact background-root enclosure, physical launch constraint and Q6 convention.
- Enclose the lower-wall launch divisor and each oscillator divisor away from zero.
- Propagate the constrained homogeneous solution with both established engines over the full uncertain physical wall interval.
- Require the resulting actual shooting residual `F_homogeneous` to exclude zero in each engine before computing the forced multiplier. The exact nonresonance theorem explains why the true value cannot vanish; it does not supply a numerical lower bound or conditioning estimate for that chosen normalization.
- If the enclosure contains zero, classify the inverse-enclosure feasibility as unresolved. Do not label the mass resonant, alter the mass, replace an interval by its midpoint, or divide using the theorem without a quantitative bound.

A different rigorously validated inverse construction could replace this shooting-residual gate, but must provide its own quantitative inverse bound and prospective review. No such substitute is supplied here.

## Historical provenance and trust boundary

`papers/interface-instability/20261024_physica_scripta_revision_5/numerical_evidence/MASS_CERTIFICATE_MAP.json` identifies the historical baseline bindings, manifest, runner, both active engines and endpoint outputs. The corresponding local `numerical_evidence/mass/BINDINGS.json` and `numerical_evidence/mass/output/RESULT.json` are selected saved copies, not a freshly regenerated full replay. O.6 explicitly treats the original outward interval execution as an inherited premise; two engines share Arb and the input mathematics, so their agreement is not independent arithmetic validation. This note preserves that qualification.

Practical consequence: scope T20 as a **homogeneous inverse/enclosure feasibility diagnostic**, not as discovery of whether the second-order physical mass is resonant. The physical nonresonance dependency is already present; quantitative enclosure quality remains to be demonstrated. The full forced successor remains separately specified and is not launched by this diagnostic.
