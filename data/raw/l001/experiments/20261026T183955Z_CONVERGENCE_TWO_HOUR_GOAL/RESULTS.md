# Convergence and remainder: results of the two-hour goal

## Gist

**The local convergence and remainder gap is closed for the selected neutral growing mode, subject to the original exact-background and spectral premises.** The formal coefficients now belong to a convergent analytic solution of the same homogeneous bulk and moving-wall equations. A full higher-order remainder protects its nonlinear proper-clock direction. A nonzero wall oscillator provides a physical scalar departure witness, so this is not merely a coordinate deformation.

The outstanding limitation is the size of the certified neighborhood. The bounds remain extraordinarily conservative. This is not yet a useful-amplitude evolution or a prediction of saturation, collision, singularity, a horizon, or a child universe.

Authorized window: **2026-10-26 18:39:55–20:39:55 UTC** (2:39:55–4:39:55 PM ET). The final closeout records the actual completion state; individual sealed records below carry their own timestamps.

## What changed

Before this goal, we had authenticated low-order coefficients, an all-order real-axis response argument and formal compatibility. The missing bridge was quantitative: one analytic norm controlling the inverse, the complete nonlinear sources and the full remainder of the observable.

That bridge now exists. It includes the actual moving-wall conservation identity, rather than leaving boundary compatibility as an unverified assumption. The resulting series solves the full neutral homogeneous equations locally, with timelike walls and an invertible pulled chart.

For `eta=epsilon exp(rt)` and `x=D-D0`, measured using the lower wall's proper time:

- **Positive amplitude:** `dx/dtau_a<r x<0`. The separation shortens, with nonlinearity reinforcing the linear shortening law.
- **Negative amplitude:** `0<dx/dtau_a<r x`. The separation opens, but more slowly than the corresponding linear law. There is no reversal inside the protected interval.
- **Physical scalar:** the lower-wall oscillator has the sign of `eta`, has magnitude at least `|eta|/40000`, and moves farther from zero with the same signed proper-time derivative.

These are all-orders local statements, not signs inferred from the cubic polynomial alone. The separation remains tied to the chosen homogeneous slicing. The oscillator's nonzero value cannot be produced by a coordinate change of its identically zero background.

## Best audited bounds

| Quantity | Sufficient bound | Interpretation |
| --- | --- | --- |
| Analytic amplitude radius | approximately `2.675781e-42` | Positive local convergence neighborhood |
| Protected proper-clock amplitude | approximately `1.106677e-66` | Both signed motion statements and scalar departure are protected here |
| Guaranteed scalar departure threshold | approximately `2.766692e-71` | Fixed nonzero scalar threshold reached by sufficiently small compatible data along this family |
| Proper-clock residual | `-60 eta² <= dx/dtau_a-rx <= -11 eta²` | Nonlinear sign survives all higher orders |

The exact rational endpoints are authoritative in `NEUTRAL_JOINT_SOURCE_FEASIBILITY/RESULT.json`; the displayed numbers are rounded descriptions. Tiny sufficient bounds are not inferred physical transition scales. The extraordinarily small sizes come from conservative norm estimates.

The prior proper-clock cubic **normal-form** sign remains unresolved. The cubic coefficient used in the final tail bound is a coefficient in amplitude `eta`, not the coefficient after reparameterizing by separation.

This new nonlinear result belongs to the **zero-current neutral branch**. It does not automatically upgrade the paper's nonzero-current charged growing-mode result to a charged nonlinear-instability theorem. That transfer would need its own same-action, charged-background argument.

## Completed tests

All packet names have prefix `20261026_` and are siblings of this goal folder.

| Packet | Result | Independent audit |
| --- | --- | --- |
| `NEUTRAL_ANALYTIC_INVERSE` | Common complex collar and uniform analytic scalar/metric inverse | PASS; 199,736 checks |
| `NEUTRAL_ANALYTIC_SEED` | Full-interval mode norm, both representations; outward seed 16444 | PASS; 478,941 checks |
| `NEUTRAL_SOURCE_MAJORANT` | Complete seven-source majorant and positive radius | PASS; 2,765 checks |
| `NEUTRAL_WALL_IDENTITY` | Exact off-shell moving-wall Codazzi/material identity | PASS; 12 checks via independent warped-product route |
| `NEUTRAL_PROPER_CLOCK_REMAINDER` | Full analytic remainder protects shortening | PASS; 2,755 checks |
| `NEUTRAL_RESPONSE_CONDITIONING` | Removes unnecessary derivative penalty in metric estimate | PASS; 2,780 checks |
| `NEUTRAL_TWO_SIDED_DEPARTURE` | Both amplitude signs and genuine wall-scalar departure | PASS; 2,773 checks |
| `NEUTRAL_WEIGHTED_SOURCE_MAJORANT` | Seven distinct positive load weights; improved radius | PASS; 2,826 checks |
| `NEUTRAL_CUBIC_CLOCK_TAIL` | Uses authenticated cubic coefficient to improve full clock tail | PASS; 2,937 checks |
| `NEUTRAL_JOINT_SOURCE_FEASIBILITY` | Retained-transport trace response plus low-jet background composition; all eight evaluation candidates retained | PASS; 3,040 checks |

Check counts describe each audit's granularity, not independent physical observations. The decisive mathematical argument is reviewed in `REVIEW.md` and laid out in `LOCAL_THEOREM.md`.

The seed calculation replayed **8,183 primary and 16,365 independent whole cells**, with immutable 128-cell checkpoint chunks. The other new stages used exact arithmetic or symbolic identities and existing authenticated enclosures, not new physical evolution runs. Scientific execution was on Linux under the frozen runtime and resource policy.

## Integrity and provenance

The earlier read-only check at 19:50:31 UTC authenticated **2,705 distinct files**, **40 binding documents**, the first nine producer/audit pairs, and **192 seed chunks** covering both full trajectories. That snapshot alone does not cover the later joint packet. See `verification/RESULT.json` and its terminal binding.

The final ten-packet refresh is recorded separately in `final_verification/RESULT.json` and `final_verification/TERMINAL.json`; only a passing terminal establishes its completion. It rechecks the earlier closure plus the joint producer/audit, sealed permissions, worker liveness and unexpected failure/staging/cache files, and binds this document set. `CLOSEOUT.json` records the final status and hashes. Neither hashes nor audit check counts substitute for the mathematical argument.

Original backgrounds, spectra and validated ODE premises are inherited, not silently reproved. `DEPENDENCIES.md` explicitly separates those premises, exact identities, analytic estimates and numerical constant checks.

No manuscript, submission, release or sealed parent was changed. Earlier weaker certificates remain intact; refinements were published in separate packets.

## What remains, and the next useful test

1. **Useful amplitude.** The weighted budget identified a dominant *proof-estimate* trace penalty, but removing it alone could yield only about522-fold improvement with other estimates fixed. The final joint test therefore addressed the trace and background-composition bounds together. It improved the radius by approximately `4.95e13` and the protected clock interval by approximately `4.15e20`, yet the resulting neighborhood is still not practically useful. This is not a physical force allocation.
2. **Coordinate closure.** The final joint test retains and bounds the differentiated transport terms; it does not substitute a simpler Eulerian equation while dropping them. `TRACE_ROUTE_SCOPING.md` is preserved as the bound prelaunch note. Its original prospective wording is superseded by the separate joint producer/audit records and the latest review addendum; the source-bound note itself was not edited.
3. **Actual continuation.** Only after a better bound or a verified a posteriori correction should we claim finite-amplitude dynamics. Generic compatible-data behavior, endpoint, and the unresolved normal-form coefficient remain separate questions.

The prospective test is specified in `NEXT_TEST.md`. It has not been launched. The achievement here is a local nonlinear development and a protected departure direction, not the final fate of the instability.
