# End-relative causal bracket lemma

## Purpose

This note isolates the topological step needed to turn independently certified
escape and capture statements into a horizon bracket.  It does not identify the
computational outer wall with infinity, and it does not use a MOTS as the
definition of an event horizon.

Let `D` be the physical spacetime development, with its physical timelike
boundaries retained.  Let `E` be a specified nonempty physical future exterior
in that same development and define

\[
V_E=J_D^-(E),\qquad B_E=D\setminus V_E,\qquad H_E=\partial_D V_E.
\]

The exterior may be a model-specific warped-KK end.  A finite numerical wall or
a sampled cylinder is not `E` unless a separate exterior authority proves the
needed inclusion or causal-past equivalence.

## Lemma

Let `L:[0,1] -> D` be a continuous launch curve.  Suppose there are parameters
`s_c < s_v` such that

\[
L(s_c)\in B_E,\qquad L(s_v)\in V_E.
\]

Then the connected subcurve `L([s_c,s_v])` intersects `H_E`.

### Proof

If the subcurve did not meet `H_E`, its connected image would lie in one
connected component of `D\setminus H_E`.  It cannot contain a point of both
`V_E` and its complement.  Equivalently, the continuous preimages of the
interiors of the two sides would separate `[s_c,s_v]`.  Therefore a parameter
`s_*` exists with \(L(s_*)\in\partial V_E\).  No asymptotic coordinate, null
infinity, MOTS, or geodesic-completeness assumption enters this topological
step.  Those assumptions enter only when certifying the two endpoint fates and
the meaning of `E`.

## Nested-bracket consequence

Suppose `[s_c^n,s_v^n]` is a nested sequence of certified brackets, their
intersection is nonempty, and their physical arc-length diameter on the launch
curve tends to zero.  Then the intersection contains one event \(p_*\), and
\(p_*\in H_E\).  If `L` is injective on the bracketed interval, the event is
unique along that launch curve.

This gives a reconstruction route that is logically independent of a
terminal-MOTS null-sheet limit.  A terminal-independent backward null sheet can
be used to propose where to place launch brackets, but it is not itself an
escape/capture certificate.  Conversely, certified opposing fates can bracket
an end-relative horizon even if the MOTS-seeded terminal family is a poor
numerical estimator.

## What counts as the two endpoint certificates

### Visible endpoint

It is sufficient to certify a future-directed continuum causal curve from the
launch event to a worldtube portion \(W\) together with a proof \(W\subset E\).
The same numerical ray need not then be continued to an ideal infinity.  A
discrete trace with a small null residual is only a numerical candidate until
its interpolation and spacetime errors enclose a continuum causal curve.

### Captured endpoint

The launch event itself must be certified as outside `J^-(E)`.  Sufficient
routes include membership in a captured set established by the finite-barrier
theorem, or a complete-family theorem that rules out every escape route.  One
ray later entering a trapped or captured region does not certify the earlier
launch event: another future curve from that event may still escape.

### Numerical enclosure

If the fate authorities certify whole launch subintervals rather than only
points, use the innermost disjoint certified intervals as the bracket endpoints.
The reported width is the physical arc length between those certified sets,
including the launch-position and metric error allowances.  A role-tagged
record ID is not an event identity; the same physical event cannot be accepted
once as visible and once as captured.

## Scope boundary

The lemma proves an intersection with the horizon relative to the declared
`E`.  Identifying `H_E` with a horizon relative to a separately defined future
null infinity requires a proof that the two causal pasts agree.  Finite samples
cannot establish the all-future hypotheses of an exterior or capture theorem.
