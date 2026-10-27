# Independent preflight: uniform connected C4 branch

Status: **PASS FOR THE DECLARED BOUNDED EXPERIMENT**, conditional on unchanged
authenticated sources/inputs, the frozen production gates, and independent
postrun verification. No new physical or numerical Linux job was run by this
reviewer. This is not yet a connected-branch result.

## Mathematical sufficiency

For one fixed exact D1 background and admitted normalized physical mode, the
same root-equivalent boundary map G(e,x) is enclosed throughout. The source
rectangle does not designate a new eigenmode for each amplitude or tile.
The unknown is always x=(a,b0,b1), with A(0)=e+a, and every tile uses the same
zero-centered box with radii (1e-5,0.1,0.1) and C=diag(-24/23,1,1).

A verified uniform image inside 0.9X and weighted derivative norm <=1/2 imply
that x -> x-CG(e,x) is a contraction of X into itself for every e in the tile.
Thus each e has a unique root in X. Continuity follows from the parameterized
contraction estimate. The unchanged preparation and regular finite-distance
IVP are analytic; the derivative bound makes G_x invertible. The analytic
implicit-function theorem therefore gives local analytic dependence about
each root, including a neighborhood of a tile endpoint because the root is
strictly interior to X.

Roots of adjacent closed tiles agree at their common endpoint by uniqueness
in the identical X. A complete closed cover therefore gives one connected,
locally analytic branch, not merely a set of point solutions. For a partial
cover, only the computed connected components may be joined; a gap must remain
a gap. Only the component containing zero is identified with the local theorem.

At zero, x=0 is an exact solution by the static and physical-mode identities,
not by numerical zero inclusion alone. The previously derived exact
G_e(0,0)=0 and invertible G_x imply x'(0)=0 in this shifted chart. Consequently
the initial-data tangent is still (psi,-2psi,f). The inherited local analytic
family lies in X near zero and agrees there by uniqueness. This does not
extrapolate its tiny certified radius to the new target interval.

To identify the two old signed samples, the postrun audit must recompute each
old certified root image from its published native G/J, add its old rational
center, and prove containment in X. Overlap of boxes or containment of the old
center alone is insufficient. The producer correctly leaves endpoint/local
identification pending rather than declaring the final accepted classification.

## Interval amplitude and unchanged physical map

I read the complete CONTRACT.md, CONNECTION_ARGUMENT.md, preparation.py and
runner.py, including the final recovery changes. The inherited nonlinear,
source, arithmetic, validated-integration and record modules match the exact
previously reviewed bytes. The three variation columns, original/reduced
boundary-map equivalence, Hermite shapes, q(A) feedback and physical-source
uncertainties are unchanged. The source and zero control are reused only from
the authenticated, independently accepted two-sample packet; no fitted source
or fresh point-valued reconstruction is substituted.

The changed preparation applies Taylor's theorem separately to each e in a
closed tile I. It encloses the degree-seven polynomial about zero and the
eighth coefficient on hull({0},I), multiplying by the outward range of I^8.
The first derivative at the interval Taylor center is one and higher input
derivatives vanish. The shifted-center coefficient construction retains all
terms. Only the already proved zero/linear coefficients at the original zero
center are removed. This is valid also for one-sided tiles not containing zero.

integer_range uses exact rational endpoint powers, odd-power monotonicity and
the zero minimum for even powers crossing zero. Conversion back to Arb is
outward. It avoids the previously excluded generic real-power operation on a
zero-straddling ball. Interval e then remains a fixed parameter while taking
the three x derivatives. Dependencies discarded by interval evaluation enlarge
enclosures rather than omit physical source or preparation uncertainty.

The mathematical Taylor argument is the enclosure proof. Manufactured
polynomial/power controls are consistency and recovery corroboration, not a
replacement for that argument or a sampled error bound.

## Finite graph and recovery

The runner starts at the full exact interval [-1/200000,1/200000], bisects only
a completed non-certified parent, and follows depth-first left-before-right
order. A passing node is not subdivided. Maximum depth two permits at most
seven evaluated nodes and fourteen flows, or 229,110 cells. Depth-two failures
remain unresolved. Technical exceptions stop the graph with completed tiles
retained; they do not authorize splitting or retuning.

Exact rational coverage merges touching closed intervals and distinguishes
the zero component from disjoint components. Full coverage is accepted only
when the merged interval equals the original target. Every flow also retains
the full inherited wall-event coverage test. No parameter, precision, step,
Picard, image or contraction gate is changed after an outcome.

The active entry point is the new serial runner. inherited_driver.py is byte
identical to the previous driver, but only its manufactured controls and
helpers are used; its concurrent launcher is not called. One heavy process
and one arithmetic/BLAS thread apply to this line, including later verification.
The documented CPU allowance is specifically 7,200 seconds of cumulative
validated step-loop CPU, not total process CPU or wall time. Preparation,
authentication and final publication are explicitly excluded. The finite
node/cell graph is the additional work bound.

Every production advance reads current state['p'] after outward checkpoint
canonicalization. Node identity, amplitude interval, preparation, source hash,
native state and phase state are persisted. Ordinary resumption reconstructs
the deterministic finite traversal from authenticated completed tiles and the
active checkpoint, with completed integration CPU included in the remaining
allowance. Cached tiles require matching guard, complete status, exact node,
source hash and terminal/result hash. A tile RESULT published just before an
interruption is compared to the reconstructed result before its missing
terminal is published; no IVP is repeated. Terminal and failed-closed work is
refused for restart.

## Resolved prefreeze findings and final controls

The review requested three narrow corrections: stronger cached-result identity
checks; recovery of the result-before-terminal publication window; and precise
CPU-budget wording. The final source contains them. A repeated polynomial-test
dictionary key was also corrected so that the full, positive and negative
remainder domains have distinct recorded checks. None alters the mathematical
map, target, source interval or scientific gate.

The authoritative staged receipt is analytic-control-05/RESULT.json, dated
2026-10-06 00:49:38 UTC: all 45 new checks pass, with all 15 inherited checks
also passing. These include interval and nonlinear interval-parameter
fresh-process continuation, exact-power boundary cases, remainder consistency,
closed coverage, gap rejection, native recovery and stale-guard rejection.
Earlier numbered receipts are retained but are not final-source authority.

Control SHA-256:
`c237d85bd86bdfcbff4c135ff3dcf7d76646f7336720f48e958e8f9c804409be`.

Inherited-control SHA-256:
`f821ad35a91ea714d2d8f1deabdd139f75be1ae5ef7971f388bdc386218a45db`.

No remaining substantive blocker was identified. Acceptance still requires
independent rational reconstruction of published image/norm gates, exact tile
coverage, old endpoint-image containment, zero/local reconciliation, native
checkpoint and input integrity, after production has stopped. Failure remains
unresolved rather than nonexistence. This is initial-data existence with the
retained C4 compatibility, not all-order compatibility or spacetime evolution.

## Exact reviewed source bytes

```text
25e2a7460e0eefb14f48b4749da99f2d1a65978ea602ea7b7e2899d4351a4cde CONTRACT.md
9a60b71c13a3703268502f490e60dc6eb9d3f33f56484c328b8ecaaa559a1aed CONNECTION_ARGUMENT.md
cd76af8917f142c782c6de70fee3f40829f0e36a162b2f8daecf0286f5e43c26 CENTERED_IVP_DERIVATION.md
26d58740fa49c3e93d642f126802e0261629997e608e8e855fe1b456af57ece3 runner.py
92b06c0aa373c2e06ad1951e748d5cb2b7c12356d0cf05bf6178573cd4da415c inherited_driver.py
5402279f4d73f37523c1b55fe91d67b6c08aa576e800fa0fd140b18548807881 preparation.py
2b6d373839620cd9abdd0d88b88aee8d4bd3f780f30ce75b96a494ab246b180d algebra.py
f303d46f2d6f5fd4639294df9d6db777689e2ea3f4f144e38e2321ec5c31bf2c nonlinear.py
a9faa6490ae30842180c39ef1e61cc555488ee26f2afe94319d0d215d2e296a5 source_flow.py
d2c52ced97bbc78398420f22e40d24b3ee2cf88668a2d00ae0de6f46fdd07603 series.py
0a48f058b282197b9b4e6d5a99e36af578bcb9e6d036d9848d5513adc009c7d3 validated.py
081e7b0b95b416e987bd873179e41152421ad73529163a33982ac8f8e6c2647e records.py
```

The inherited independent nonlinear-endpoint and centered-equation scripts,
receipts and derivations are bound by REVIEWS. Shared Arb, Taylor/Picard,
arithmetic and recovery code is explicitly disclosed; this is not a claim of
a disjoint interval library. No parent or frozen file was edited by the review.
