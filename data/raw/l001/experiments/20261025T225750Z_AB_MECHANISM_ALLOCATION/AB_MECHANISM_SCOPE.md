# AB mechanism scope and smallest meaningful next calculation

Status: read-only source scoping and prospective proposal, not numerical execution or certification. Prepared for the allocation starting 2026-10-25 22:57:50 UTC. No source or manuscript was modified.

## Outcome

The promising next calculation is the **neutral selected-oscillator mode's physical separation and kinetic participation**, on AB's actual original central background. Merely proving nonzero separation for the pure-potential baseline duplicates an existing result. The key distinction is that AB's selected neutral oscillator completion and its pure-potential baseline share the background but have different spectral boundary conditions and generally different modes.

This is not the short concave example. Its exact bulk potential is V=m²Φ²/2; its original wall potentials have Hessian20. The selected centered completion adds ω_i²=β_i=η_i=1 and c_i(Φ)=1−(Φ−Φ_i*)/1000. At zero current the phase does not contribute to a negative-mass mode. Oscillators do contribute. At nonzero charge no static separated spectrum is claimed.

## Freshly inspected authoritative sources

All paths below are relative to `/Users/ronbibb/Research` (Linux shared root `/media/psf/Home/Research`). These are source identities to bind and hash on Linux before computation; this scoping pass has not performed a computational hash audit.

- `papers/interface-instability/20261024_physica_scripta_revision_5/MANUSCRIPT.md`: equations(8)–(11), (15)–(21), AppendixA and AppendixJ.2. AppendixJ.2 explicitly gives δD/Q=−2∫ψ ds after generic Israel removes longitudinal bending. This is a first variation of proper separation, not the curvature-clock width coordinate by itself.
- Same folder `NUMERICAL_SOURCE_MAP.json`, `numerical_evidence/MASS_CERTIFICATE_MAP.json`, `numerical_evidence/mass/BINDINGS.json`, and `numerical_evidence/mass/output/RESULT.json`: action/root/mass provenance. The baseline selected-mass certificate has pure-potential wall Hessians20; it supplies a comparison for the selected oscillator mode, not its measured eigenfunction.
- `research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/20261013T094526Z_PAPER_A_SINGLE_SPECTRAL_NARROWING/`: `engine/primary_interval.py`, `engine/independent_interval.py`, `inputs/central_bindings.json`, `inputs/primary_strip.json`, `inputs/independent_strip.json`, `output/RESULT.json`, `TERMINAL_REVIEW.json`, `RUNTIME_BINDINGS.json`.
- `.../experiments/20261013T001854Z_PAPER_A_STATIC_TESTS/MODE_TEST_DESIGN.md`, `RESULTS.md`, `INDEPENDENT_MODE_AUDIT.json`: already establish baseline ψ>0 throughout the collar and nonzero separation under ψ(0)=1. Their coarse δD interval is inside(−219,−3.994); this is not a preferred contraction sign because eigenmode amplitude can be reversed.
- `.../experiments/20261013T073517Z_PAPER_A_CURVATURE_RESPONSE/DERIVATION_AND_RESULT.md`: already measures static curvature–separation anticorrelation under upper-tension change. It is a different-static-model susceptibility, not temporal evolution.
- `.../experiments/20261013T140416Z_PAPER_A_FINITE_STIFFNESS_HOUR/`: accepted finite-upper-Hessian and Dirichlet tests. These change the upper perturbative wall Hessian while retaining the lower one, so do not mislabel the Dirichlet result as both-wall DD or reuse it as the selected oscillator eigenvalue.

## Exact input and applicability

Copy the six exact parameters and the full A,D intervals from `inputs/central_bindings.json`, and verify equality with manuscript AppendixA. The launch interval is for Φ(0), not the warp factor a(0)=1. Do not round to the plotted central background. Use both inherited regular bulk engines at their existing768-bit precision and spatial steps2/8192 and2/16384; whole launch and full uncertain endpoint interval are retained. These sources and runtime must be reauthenticated and admitted under the new packet, not executed using expired historical wrappers.

The growing homogeneous harmonic Q=e^(γt) has μ=−γ(γ+3h), h=√k. For μ<−4k one has γ>h; it is nonconstant and not the exceptional bending harmonic. Thus the generic longitudinal reconstruction and separation formula apply. No claim that positive ε is physically preferred: opposite signs expand or contract the separation at linear order.

## Proposed bounded selected-action test

Retain the unchanged bulk recurrence, Picard/Taylor enclosure and first-integral/constraint checks. Adapt only the action-derived launch and endpoint law, separately reviewed before execution:

1. For each mass μ<0, compute d_i=2−μ/a_i²>0, Γ_i=21−1/d_i, u_i=f_i/d_i. Retain the undivided rows as a consistency control. The oscillator uses μ, **not μ+4k**.
2. With ψ_a=1, the original lower constraint and wall row give B_a=Γ_a T_a/2−T'_a, f_a=3(μ+4k)/(a_a² B_a), g_a=Γ_a f_a/2−2T_a. Require B_a separated from0. a_a=1. The upper determinant is g_b+2T_bψ_b+Γ_b f_b/2. Opposite inward signs are essential.
3. A priori the selected root is above the pure-potential κ20 root and below−4k. Use fixed prospective endpoints from the accepted broad baseline mass bracket, e.g.−33/25000 and−131/100000, only after verifying both are below−4k for the complete k interval. Independently propagate each endpoint with both engines. No assertion of opposite signs until measured. Failure to bracket is retained, no rescue search unless separately selected and reviewed.
4. If both engines certify opposite endpoint signs, bounded bisection with a predeclared maximum and width target can narrow it. Two engines must agree; a zero-containing midpoint stops narrowing rather than selecting a direction. The manuscript's count supplies uniqueness conditionally, not the numerical sign data alone.
5. On the resulting full mass strip, integrate enclosure budgets from whole-cell boxes (not sampled quadrature): Iψ=∫ψ ds, Iψ²=∫ψ² ds, Zg=12∫a²ψ² ds, Zs=2∫a²f² ds. Include uncertain D by exact fixed-prefix integration to D_lo plus a full possible tail interval through D_hi; do not integrate the whole upper collar as though D=D_hi. All signed tail integrals need a hull including0. Nonnegative densities use lower0 in the uncertain tail. Use positive square enclosures even if a scalar interval straddles0.
6. At the uncertain wall, retain ua,ub and Zw=a_a²ua²+a_b²ub². Then Zext=Zg+Zs+Zw. Report geometric, bulk-scalar and oscillator fractions; they are contributions to this original-action kinetic norm, **not energy-transfer rates or fractions of the instability's cause**.
7. Report normalization-independent Csep=Iψ²/(D Iψ²_integral), where numerator is the square of Iψ and denominator uses the integral of ψ²; equivalently Csep=(∫ψ)²/[D∫ψ²], physically in[0,1]. Report δD/Q=−2Iψ at ψa=1, and its squared canonical susceptibility (δD/Q)²/Zext. Avoid ambiguous notation in machine keys. Relative endpoint intrinsic-radius responses are δa_i/a_i=ψ_i Q; their signed ratios to δD/D supply an inspectable geometric deformation pattern.

The new question is whether the unstable direction in **the selected neutral material action** is geometrically coherent across the collar and how much kinetic participation resides in its walls versus bulk scalar/metric. This goes beyond the already certified existence and nonzero baseline overlap without claiming charged dynamics.

## Required prospective controls and classification

- At β=0 the adapter must reduce exactly to the original κ20 launch/determinant and reproduce an authenticated baseline endpoint sign in each engine.
- Algebraic undivided wall-row residual includes0 at each endpoint after elimination; d_i>0 and B_a nonzero checked. Test a deliberately shifted-mass oscillator formula as rejected semantic mutation.
- Constraint and first-integral enclosures include0 on every accepted cell; positive warp; complete uncertain endpoint cover; finite norm and integral budget enclosures.
- Constant manufactured ψ checks Csep=1 and δD=−2Dψ, with the uncertain-tail convention included. A sign-changing manufactured ψ checks that sign cancellation is not forced positive.
- Two engine outputs overlap for every observable; use conservative hulls, not selecting a tighter favorable engine.
- A narrow interval excluding0 certifies separation participation; a wide interval is inconclusive, never a claim that separation vanishes.
- Do not predeclare a preferred geometric/oscillator dominance threshold without a scientific question; report certified bounds. A partition too broad to distinguish components is an honest outcome.
- Full run under1h, max1 leased core for this test; resources shared with the other current test under aggregate2. Linux only for arithmetic and audits. Estimate: historical ten mass flows took81s; fresh selected-law adapter plus controls/integral strip should be minutes of compute, while derivation/review is likely the larger cost. This is a historical cost indication, not an ETA guarantee.

## Explicit omissions and subsequent decision

This calculation does not determine physical interface separation on the nonzero-charge branch. That requires the first charged background coefficients and the growing-mode correction, plus its common-clock gauge representative. The manuscript gives analytic existence with an uncomputed charge neighborhood, but the inspected records do not provide a numerical charged trajectory or certified charge radius ready for readout. No such result can be imported from the concave example or inferred from pure-potential baseline response.

After this neutral selected-action test, the useful next design would be the first action-consistent charged correction to separation, with both current labels and their fixed-charge perturbations retained. Its source maps, gauge representative and admissible amplitude must be independently derived/bound before execution; it is not authorized by this scoping note alone.
