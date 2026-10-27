# Uniform sixth-order envelope: completed, inconclusive

## Result

The unchanged continuous-cover test completed on academic-linux. All 16 parameter intervals and 64 propagations finished, with all technical gates passing. Its scientific classification is `INCONCLUSIVE_DERIVATIVE_BOUND`: the derivative enclosures do not certify the endpoint signs required by the proof. This is not a certified counterexample to the proposed envelope.

Qualification passed and was independently accepted before production. Production ran from 2026-10-25 21:29:48 UTC for 2008.316 seconds (33.47 minutes), on one leased core under the fixed 45-minute limit. It exited zero and its child was reaped. A separate read-only Linux process check found neither its wrapper nor its worker remaining. No successor calculation was launched.

## What was being tested

For the fixed concave one-turn L001 double-Dirichlet family, the target was

\[
\frac{383}{1200}\leq
\frac{-\lambda-D^2/6+5D^4/36}{D^6}
\leq\frac{383}{800},\qquad 0<D\leq0.02.
\]

The test enclosed the fourth parameter derivative of the normalized characteristic over a continuous cover and used a positive-weight integral identity to supply a sufficient characteristic-sign condition. It did not divide an uncertain residual by a small width or infer a uniform statement from point samples. Both G and W representations were used; their enclosing hull, not their intersection, was used for the decision.

## What the result means

The chosen interval representation and fixed cover cannot establish this sufficient sign condition. An enclosure containing zero does not establish that the true derivative vanishes or changes sign, and failure of a sufficient proof condition does not refute the target relationship.

The saved pointwise qualification controls are tight, whereas the continuous-parameter bounds are broad. The independent terminal audit identifies parameter dependency/wrapping overestimation as the practical limitation. This comparison is diagnostic evidence, not a decomposition proving one exclusive cause. Terminal audit details belong in `production/TERMINAL_REVIEW.md`. All 64 saved endpoint checks and all 32 sign decisions were independently reconstructed. Interior step gates remain inherited from authenticated successful execution; interior tubes were not separately archived for independent replay.

The earlier exact local expansion and independently accepted width-scaling evidence are unchanged. This test adds neither a uniform sixth-order envelope nor an eighth-order remainder certificate. It concerns this fixed L001 family, not the original Paper A background, a physical moving-wall model, nonlinear formation, or the Protocol 394 horizon residual.

## Highest-value prospective next test

Before funding another full cover, test parameter-enclosure width sensitivity at one predeclared positive width: retain the same equations, parameter derivative, endpoint beta, spatial resolution and representation, and compare a point control with a small frozen ladder of enclosing parameter widths. The question is whether narrowing the parameter box restores a strict derivative sign at practical cost. Preserve every outcome and independently review the method and result.

That diagnostic would inform whether to pursue finer parameter subdivision or a dependency-preserving representation such as a Taylor-model enclosure. It would not itself prove the full continuous envelope or establish full-domain cost. This is a recommendation only; no successor is authorized or running.

## Provenance and operational boundary

This is a distinct operational readmission after renewed start authorization. The original `20261025T203948Z_UNIFORM_SIXTH_ORDER_REMAINDER` no-start resource hold remains preserved. Scientific source, controls, coefficients and production cover were unchanged. All scientific computations and computational audits ran on academic-linux. Mac activity was orchestration and documentary editing. No manuscript or inventory was edited.

Machine-readable evidence: `qualification/RESULT.json`, `qualification/EXECUTION.json`, `qualification/TERMINAL_REVIEW.md`, `production/RESULT.json`, `production/EXECUTION.json`, and the production raw records and per-bin summaries. Final independent terminal review and closure manifest complete the packet.
