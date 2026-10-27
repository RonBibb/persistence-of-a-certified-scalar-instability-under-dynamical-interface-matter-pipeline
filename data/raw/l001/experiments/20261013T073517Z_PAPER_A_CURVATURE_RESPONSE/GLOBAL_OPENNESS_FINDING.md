# Qualitative persistence of global first event uniqueness

The admitted witness check and separate independent terminal review support this conditional corollary: there exists a positive epsilon such that the full original launch interval still has exactly one positive-curvature simultaneous-wall solution on the first-event branch whenever |lambda_b-lambda_b0|<epsilon. The radius is not calculated. In particular, this does not establish full-launch uniqueness over the entire P01 interval [-1/1000000,1/1000000].

The premise is the mathematical validity of the original baseline first-event certificate, including the full earlier-cell positivity and regular interval flows, together with the accepted local P01 family. The saved aggregate cover and the new witness check do not independently reconstruct that missing cell history.

## Why a positive neighborhood follows

The original cover partitions the compact launch interval into 19 negative-curvature boxes, 706 first-event scalar-exclusion boxes and one root box. Because k(a) depends only on the fixed lower launch data, its negative-curvature boxes remain excluded when only lambda_b changes.

For any launch in a scalar-exclusion box, the baseline certificate supplies a finite regular first event with G_s<0 and h nonzero. Its pre-event G is strictly positive. Smooth ODE dependence and the implicit function theorem continue the event under a sufficiently small change of launch and tension. Choose a short interval around the event where transversality persists. The preceding compact time segment has a positive minimum of G, so a sufficiently small perturbation preserves the absence of any earlier event. Continuity also preserves the nonzero scalar residual at the continued event.

These open neighborhoods cover the closed launch box. A finite subcover therefore has a common positive tension radius. Taking the minimum over the finite collection of scalar boxes preserves every exclusion. The P01 theorem supplies one locally unique root in the central box, so taking the smaller of the exclusion radius and 1/1000000 proves the claim over the complete original launch interval.

The new computational witness passed for all 1,412 producer/box pairs: every scalar-exclusion event begins strictly after launch and closes before the finite endpoint. The minimum bracket-start value is exactly 1473/4096, and the minimum distance from a bracket's end to s=2 is exactly 1/1024. These time margins are not bounds on epsilon. The earlier arithmetic audit allowed an event to begin in the first integration cell, so this strict interior witness is an additional checked premise for the compactness argument.

The sole admitted execution finished at 2026-10-13T07:53:55.787474Z using isolated CPython 3.14.4, with return code zero and empty stderr. All three semantic controls rejected at the intended predicate: event at launch, event closing at the endpoint, and mismatch of the two root boxes. The [result](GLOBAL_OPENNESS_RESULT.json) and [execution record](GLOBAL_OPENNESS_RUN.json) preserve exact witnesses and hashes. The [independent terminal review](GLOBAL_OPENNESS_TERMINAL_REVIEW.json) reconstructed every witness and both exact margins, verified controls and execution bindings, and accepted the compactness proof with its inherited-history premise.

## What an explicit radius would require

An explicit uniform tension radius requires quantitative lower bounds for pre-event G and terminal sign margins, together with bounds controlling their parameter dependence and the scalar residual at the moving event. The current aggregate global records omit the earlier-cell G margins. The newly recovered migration hashes concern the separate local P01 flows and cannot supply those missing global-cover data.

The smallest decisive next calculation would retain the original global-cover launch boxes and certify their first-event and scalar-exclusion predicates over a prospectively fixed tension interval, with earlier-cell margins recorded. A radius chosen this way must pass its own reviewed protocol; neither the local P01 width nor the first-event time margins can be substituted for it.

The [frozen proof and test design](GLOBAL_OPENNESS_DESIGN.md), [bound sources](GLOBAL_OPENNESS_BINDINGS.json) and [independent gate](GLOBAL_OPENNESS_GATE.json) distinguish this qualitative corollary from a numerical parameter certificate. It remains a reduced static theorem, with no dynamical or spectral implication.
