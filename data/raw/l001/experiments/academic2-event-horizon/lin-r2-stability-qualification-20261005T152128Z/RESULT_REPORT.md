# R2 static neighborhood and central stability qualification

## Result and significance

The continuous R2 static parameter-neighborhood certificate passes both formal
postrun audits. Within the declared reduced Einstein-scalar two-wall problem,
the first-event static branch exists throughout the frozen two-parameter box;
the separately imposed fixed separation remains excluded throughout that box.
This strengthens existence from an isolated parameter choice to a neighborhood.

The archived growing scalar/radion mode is authenticated to the central D1
branch by exact action parameters, wall conventions, invariant geometry and
fresh full-profile comparisons. A new proper-distance construction and an
independent conformal-coordinate replay reproduce that growing mode. This is
finite-resolution instability evidence, not a rigorous spectral enclosure.

The new nine-point stability qualification is **UNRESOLVED**. It stopped after
its two central-control cases; the eight neighboring points were never run.
This failure is retained unchanged, notwithstanding the closely reproduced
physical mode.

## Numerical findings

| Quantity | Measurement |
| --- | --- |
| Fresh central physical mass squared, mu | -0.0013122306827971467 |
| Coarse/fine mass difference | 1.5178830414797062e-18 |
| Difference from archived accepted mass | 7.56556275960385e-16 |
| Independent conformal replay difference | 3.2526065174565133e-18 |
| Full central background profile difference | at most 1.044e-13 scaled |
| Positive kinetic norm Z | 321.28405297311565 |
| Normalized proper-separation response | -2.987261544368808 |
| Growth exponent / H | 1.002975410304611 |
| Largest frozen mode-equation residual | 9.566643063e-10, below 1e-6 |
| Failed fine direct-metric residual | 2.4163588398835808e-8, above 1e-8 |

The failed check independently differentiates saved W and Phi, including both
endpoints, in W_ss + Phi_s^2/3 + k exp(-2W). Its maximum occurs at the upper
endpoint s=D=1.99756727919473 with the frozen nine-point/2001-node stencil.
It is not a solver-reported residual or a reused ODE right-hand side.

## Independent verification

The frozen R2 auditor passed six checks. A separate rational-arithmetic and
artifact auditor passed 41 checks. The campaign was not rerun. The full
launch-domain and fixed-separation covers contain zero unresolved boxes.

The independent stability reviewer used actual-node barycentric derivative
rows rather than the producer's Fornberg implementation and reproduced the
failed metric check. For the fine background, nine-point differentiation gives
5.69e-10, 5.50e-10 and 2.42e-8 on 501, 1001 and 2001 nodes. Increasing the
stencil to eleven points worsens the 2001-node result to 5.98e-8. The computed
half-ULP sample-conditioning amplification at the failed endpoint is 4.20e-8.
This supports rounding amplification in stored binary64 data as a mechanism;
it is not a rigorous error bound and does not waive the gate.

Independent conformal mode replays pass at 1001 and 2001 interpolation samples.
Their mass difference is 2.08e-16. Independent norm and displacement integrals
agree. Tracked source and input hashes remained unchanged across the review.

## Preserved issues and boundaries

The first source stopped during control-result serialization of a NumPy
boolean. Its FAILURE.json remains intact. The R1 source changed serialization
and output binding only; its scientific terminal is UNRESOLVED. No failed
record or prior source was overwritten. The archived rejected spectral
eigenvectors remain rejected; reproduced shooting modes do not rehabilitate
them.

The static theorem, the authenticated finite-resolution growing mode and an
eventual rigorous spectral statement are distinct evidence classes. Neither
the two fresh central cases nor the old stability record establishes a uniform
spectral theorem, nonlinear evolution, global initial-data compatibility,
event-horizon formation or a D1-P16 identification. No manuscript was changed.

## Next discriminating calculation and viability

Reconstruct AND store the central background at genuinely higher precision,
retaining the same physical action, branch, boundary conditions, nine-point
checks, 1001/2001 nodes and 1e-8 background gate. Re-evaluating already rounded
binary64 samples at higher precision cannot recover their lost digits. Only
a newly qualified central pair should admit the neighboring-parameter cases.

The static line remains viable and stronger. The central mode supplies
reproducible evidence of a growing perturbation: the static solution must not
be assumed to be a stable scaffold. Persistence away from the center and a
rigorous exact-background eigenvalue bound remain open.

## Controlling artifacts

- R2 result: ../lin-static-parameter-neighborhood-r2-20261005T120100Z/output/RESULT.json,
  SHA-256 3d6353e7277e273fdf35101ef3b9126802de04ac0c1dbf7931d06209e90e8b21.
- R2_POSTRUN_REPORT.md and audit/R2_POSTRUN_AUDIT.json.
- BRANCH_STABILITY_AUDIT_REPORT.md and audit/branch/RESULT.json.
- STABILITY_CONTRACT.md and SPECTRUM_R1_BINDINGS.json.
- spectrum-r1/RESULT.json, SHA-256
  191cb4c941a92ca6decb90fa11598d2662b66151aa8bbd8a123f7161be2a5505.
- audit/INDEPENDENT_POSTRUN.json and reviewer_postrun.py.
- Top-level RESULT.json, MANIFEST.json and TERMINAL.json seal this combined
  workflow without relabeling its unresolved scientific test.
