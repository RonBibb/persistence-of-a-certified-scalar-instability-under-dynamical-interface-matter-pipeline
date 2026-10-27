# Higher-precision qualification of the Lin scalar/radion growing mode

## Success: what changed

The precision discriminator passes. All 18 prescribed cases—nine original
parameter points, each at two numerical controls—qualify under the unchanged
background and mode gates. Independent saved-field differentiation, conformal
mode replays and the separate central conformal-background reconstruction pass.
The physical run, including its admission and final independent audits, took
approximately 3 minutes 49 seconds on one Linux numerical process/thread.

The previous round remains sealed as UNRESOLVED. Its fine direct-metric
residual was 2.4163588398835808e-8 against the frozen 1e-8 limit. The same
2001-node, nine-point, endpoint-inclusive check on the new central fine
background is 4.655745508361346e-19. Across all new cases and both saved-node
checks, the largest independently reconstructed background residual is
2.1949491664713119e-16. No gate was relaxed or removed.

This closes the specific numerical background-qualification gap that prevented
the preceding sensitivity scan. The growing mode survives the repair and all
nine prescribed parameter choices. The result is a qualified finite-resolution
instability finding, not a proof of a perturbation eigenvalue for the exact
static solution.

## Construction and independent checks

The background is newly integrated in proper distance at 50/70 working decimal
digits, Taylor degrees 24/30, and maximum steps 2/64 and 2/128. Its shooting
root, curvature and wall location are recomputed from the exact rational action
parameters. No old binary64 trajectory is promoted to a high-precision one.
The authoritative proper nodes D*j/2000 and all fields are stored as decimal
strings at dps+8 digits; the independent storage audit detects 12,003 values
with information beyond binary64 among the 12,006 checked entries.

The regular mode integration remains the declared binary64 DOP853 calculation
with unchanged tolerances, root bracket and mass gates. Background conversion
to binary64 is confined to this mode interface and comparisons with legacy
data. Stored background differentiation uses genuine Linux 113-bit arithmetic.
Working precision is not a claim that every solution digit is accurate.

The primary Fornberg differentiation is checked with independently constructed
barycentric derivative rows. Both use nine points and include the endpoints
at 1001 and 2001 nodes. The direct metric equation, scalar equation, first
integral, coordinate relation and physical walls remain explicit tests.
The maximum independent mode-equation residual over the complete set is
5.838069394495401e-9, below 1e-6.

At central fine, an independently written 50-digit RK4 integration in conformal
distance reconstructs the same background from its MP initial data. Its four-
and eight-substep controls give largest scaled field differences of 1.0790e-14
and 6.7446e-16; the largest physical-wall residuals are 1.5900e-13 and
9.9385e-15. This is independent equation/integrator verification, not a second
root search. Independent conformal mode replays at 1001/2001 background samples
agree with the proper-coordinate masses within 3.4521e-16 and profiles within
1.1859e-11 over all cases.

## Qualified measurements

| Quantity | Measurement |
| --- | --- |
| Central physical mass squared mu | -0.0013122306827991104 |
| Central shifted value mu+4k | -4.865328981212445e-6 |
| Central growth exponent / H | 1.0029754103052606 |
| Central positive kinetic norm Z | 321.2840529730316 |
| Central normalized separation response | -2.9872615443684056 |
| Largest paired mass difference across nine points | 8.673617379884035e-19 |
| Physical mass range over the nine points | [-0.0013122956834787777, -0.0013121659336991461] |
| Growth exponent / H range | [1.0029362720725348, 1.0030146984601913] |

All scalar-turn relations, positive-norm/nonzero-overlap tests, physical-mass
sign tests and shifted-sector separation tests pass. The central solution
remains within the D1 root, proper-separation and curvature enclosures. Its
largest scaled full-field difference from the archived background is 1.281e-12,
and its mass differs from the archived accepted mode by 1.2072e-15.

The negative mass and positive kinetic norm, together with a nonzero
proper-separation response, support a genuine growing scalar/geometry
perturbation within this numerical linearized problem. A static solution can
exist robustly and nevertheless have a growing perturbation. Neither its
nonlinear endpoint nor the sign of the eventual wall displacement follows:
the overall linear mode amplitude has arbitrary sign.

## Issues and inference boundaries

The simultaneous improvements to integration and stored precision resolve the
failed diagnostic. They do not uniquely assign the old defect to final-storage
rounding rather than binary64 trajectory/dense-sampling error. The preceding
independent conditioning diagnostic remains supporting evidence, not a rigorous
decomposition of those contributions. The old failure has not been relabeled.

The new saved-field errors decrease with denser checking rather than showing
the old endpoint amplification: the central all-equation background maximum
is 2.1652e-16 at 1001 nodes and 1.7254e-18 at 2001. This is consistent with
endpoint differentiation truncation after the precision repair, not by itself
a continuum error theorem.

The R2 static certificate remains rigorous only for its declared reduced
problem and parameter box. These nine numerical stability points do not prove
uniform spectral instability throughout that continuous box, identify the
entire spectrum, or enclose an eigenvalue of the exact-background operator.
There is no nonlinear evolution, global initial-data admission, event-horizon
claim, healthy-background assumption or D1-P16 merger. The historical rejected
spectral profiles remain rejected. No manuscript or external record changed.

## Next step and viability

The next narrow mathematical step is a prospectively designed validated
shooting/sign or eigenvalue-enclosure calculation for the regular coupled
perturbation equations on the certified central background. It must propagate
background uncertainty and boundary conditions without dividing by the turning
scalar gradient. This could turn the central numerical growing-mode statement
into a rigorous spectral statement before considering continuous-box extension.
No such successor was launched in this round.

The static branch remains viable as a constructed solution. It should not be
used as a stable equilibrium or healthy causal starting background without
additional justification: its sampled neighborhood retains a growing mode.
This is a substantive classification of the constructed branch, not a failure
of the static existence theorem and not a statement about the separate MOTS,
residual-balance, P16 or global horizon lines.

## Execution and controlling artifacts

The preceding combined report and 42-file seal were completed and checked
before this successor was frozen. The analytic MP control, lossless storage
round trip, actual fresh-process next-step checkpoint replay, stale-binding
and partial-publication rejection, terminal refusal, and independent polynomial
control passed. Completed scientific cases were atomically checkpointed with
source, input, runtime and three-file hashes. The central independent admission
was published before any neighboring point. All tracked inputs remained
unchanged. No case was uncomputed or failed in this new production run.

- CONTRACT.md: prospective scope, precision controls, fixed gates and ordering.
- BINDINGS.json: SHA-256
  fcf67907cf57828cd4a7b16732b80213935ec0e101a4bb7c99d6ec03adc8fa72.
- preflight-final/RESULT.json and PREFLIGHT_SCIENTIFIC_REVIEW.md.
- output/CHECKPOINT.json: all 18 immutable case/background/array entries.
- output/CENTRAL_INDEPENDENT.json: prerequisite for the neighboring cases.
- output/RESULT.json and output/TERMINAL.json: completed producer result.
- output/FINAL_INDEPENDENT.json and INDEPENDENT_POSTRUN_REVIEW.md.
- Top-level RESULT.json, MANIFEST.json and TERMINAL.json: combined final seal.
- Previous failed-round seal:
  ../lin-r2-stability-qualification-20261005T152128Z/RESULT.json, SHA-256
  e76a80344f721c81435b9aa83f057af6979ce47b95d034b169763a27e62a4c7f.
