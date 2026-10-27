# Remaining C6 correction widths

Both remaining failed correction coordinates now have substantially tighter same-center enclosures. The lower-H5 bound narrowed by about 112.5 times and the upper-H7 bound by about 59.45 times, with agreement at 768 and 1024 bits. The bounded producer calculation is complete and all local gates passed. Independent admission and any unchanged C6 inclusion decision belong to Lin Initial.

The result changes what can be bounded about the original data, not the physical data themselves. No new integration, recentering, parameter adjustment or threshold change was made.

## Quantitative result

The targets are coordinates 1 and 4 of the original correction vector `-C F(c)`, not identically numbered residual rows. Comparisons use literal exact-rational endpoints from the previously audited inclusion readback.

| Target | Precision | Prior halfwidth | New halfwidth |
| --- | ---: | ---: | ---: |
| Lower H5 | 768 | 2.3295857090488425e-5 | 2.0707420800292198e-7 |
| Lower H5 | 1024 | 2.3295857090488425e-5 | 2.0707420866905580e-7 |
| Upper H7 | 768 | 0.9642662331305175 | 0.01621977990726009 |
| Upper H7 | 1024 | 0.9642662312657679 | 0.01621977993636392 |

Both target intervals strictly tighten at both precisions and overlap across precision. The producer classification is `REMAINING_C6_CHANNELS_TIGHTENED`. This is not a producer root-existence or inclusion claim.

## Exact attribution of the previous widths

The attribution first propagates each original residual halfwidth through the absolute value of the fixed preconditioner coefficient. It then records separately any reduction from intersecting direct correction bounds. The channel budget before that intersection is an exact linear upper-bound ledger.

For lower H5, the lower C4 residual supplies effectively all of that linear radius budget. For upper H7, upper C6 supplies 99.5715 percent, upper C4 supplies 0.40884 percent and lower C4 supplies 0.01965 percent. Other contributions are smaller. These percentages describe an enclosure representation, not measured physical error or flux fractions.

The sealed archive retains source/root uncertainty, endpoint-event localization, accumulated integration and interval wrapping. It does not provide a disjoint cumulative error history from which each could be separately measured. The previous inventory records only 128 last-cell remainder samples out of 16,365 integrated cells. Those local samples are not substituted for a global error bound. Their mixture remains enclosed and explicitly unresolved.

## Correlation used in the improvement

For the unchanged static source and normalized mode, an exact invariant gives

    (c T - m2 P + 4 H T) f = 3 (mu + 4 k) E^2 psi.

The calculation proves that the denominator excludes zero throughout each full derivative domain before using this relation to eliminate the independently boxed mode amplitude f. The prior positive static Hamiltonian relation is retained. Both integrated metric-compensation variables, the exact finite-amplitude canonical C7 correction and the original physical fifth/seventh derivative controls remain uncertain inputs.

The original conformal time-recursion driver is reused unchanged with a private field-builder dependency. The new field builder propagates the source-mode correlation and its derivatives through the same spatial Hamiltonian, gauge and time equations. It does not impose the unsolved finite-amplitude upper-wall metric condition. Clock factors and both endpoint orientations are unchanged.

The primitive target domain and the derivative domain are now recorded separately. Exact checks prove that every original source-containing target interval lies inside its pivot-radius rectangle, which in turn lies inside the saved derivative domain. This incorporates the prior audit's native-serialization finding prospectively, without changing old files or discarding uncertainty.

## What sets the new bounds

In the 1024-bit mean-value upper budget, the lower-H5 bound is primarily associated with endpoint length D, at 69.31 percent, upper source scalar P, at 21.15 percent, and mode eigenvalue mu, at 9.18 percent. The upper-H7 bound is primarily associated with upper metric value W, at 66.37 percent, D, at 28.46 percent, and upper source scalar P, at 4.14 percent.

These remain representation-dependent upper bounds. They do not separate physical source uncertainty from prior integration or wrapping, and they do not establish irreducible physical residuals.

## Verification and resource closure

The contract and executable sources were frozen before the new attribution or mode-correlated outcomes. The binding is `e9bb4da163f0609c690214a59fec835a229c9939839021167911c9a89c9085e2`.

The original residual map reproduced at both precisions. A fresh process resumed a genuine prepared-domain checkpoint and reproduced the next whole-box calculation exactly. Changed fingerprints and an uncommitted partial write were rejected. Both mode-denominator and Hamiltonian-radicand domain gates passed, as did source-mode identity checks for values and automatic derivatives.

All 40 terminal local checks passed. The two production cases ran concurrently on Linux CPUs 0 and 1, approximately 8.5 seconds each, with peak resident sets of 42,352 KiB. Preflight, producer and worker processes have exited; all owned resource leases are released. No new IVP, C6 rerun, evolution or automatic successor was launched by Static.

## Independent consumer boundary

The sealed candidate correction bounds have been handed to Initial for independent source-equivalence, domain and arithmetic admission. Only admitted new evidence may enter its one authorized rerun of the unchanged five-variable inclusion test. This producer has evaluated neither those inequalities nor a new root decision.

The enabling value is direct: both outstanding correction bounds have improved without changing the problem. Standalone novelty is not assessed. A root certificate, global coordinate-map result, evolution, stability, horizon or cosmology claim does not follow from the producer's local classification alone.

## Controlling artifacts

- `ATTRIBUTION.json`: `707a0ffb33a6d3818cc23432408a4216d7a2f6a8010ca833183eb3d7e6f939fd`
- `RESULT.json`: `00965ac9a2041aae9b7c6f10a425b48929d0e4071a8b1f89b7f6b26ea2a1a87b`
- `TERMINAL.json`: `54d66070fd4f2fc3f41e9033769f9e1a661efb41c4e0b55022e9d27a49c34564`
- `LOCAL_AUDIT.json`: `ee724fc255bddf10ceb43a7d990a5a9bd9fb5bea579d857954712609807338f2`
- `RESOURCE_RELEASED.json`: `daf6e4c3255d5f49a424112ea5d69172b5082ec590380c6554957e9b283da1b9`
- `STATIC_SUBMISSION.json`: `df4e62c5236390e9d14489bb653eccbcfbf3c00a49aa72d7f2a5469ef4636caa`

Complete native states, full gradients, original target endpoints, derivative domains, case outputs and immutable checkpoints remain in `preflight/` and `work/`. The previous C4 admission and failed full-certificate result are preserved unchanged.
