# Lin static parameter-neighborhood R2 recovery contract

## Purpose

Resume the authenticated R1 static parameter-neighborhood calculation from its last
content-addressed checkpoint after a non-finite interval raised during public-record
conversion in one global launch box. The R1 parametric root certificate remains part
of the checkpoint; it is not recomputed or weakened.

## Frozen scientific design

R2 preserves R1's action, junction equations, two-dimensional `(v1, lambda_b)` box,
root tube, 768-bit Arb precision, 8192 event cells, dual-producer requirements,
global gap-free launch cover, fixed-D0 cover, maximum launch-bisection depth, and
parameter-subdivision rule.

The sole numerical-control correction is conservative exception routing:

- if aggregation of an event record raises `fmpq requires an exact, finite value`,
  that launch box is classified as `NONFINITE_EVENT_UNION_REQUIRES_SUBDIVISION`;
- it is then bisected by the already-frozen R1 launch-box rule;
- if the condition persists at the frozen maximum depth, the box is `UNRESOLVED`
  and the theorem remains technically incomplete.

No non-finite enclosure is interpreted as a sign, excluded region, root, or physical
result. No gate or depth ceiling is relaxed.

## Recovery authority

R2 binds both R1's latest checkpoint pointer and the referenced immutable checkpoint.
It verifies their internal digest agreement, copies only the authenticated state into
a new R2 checkpoint with the R2 guard, and then invokes the frozen production path.
The failed R1 namespace remains immutable evidence of technical incompleteness.

## Claim boundary

Success can establish only a rigorous static finite-parameter neighborhood theorem
for the declared model and box. It does not establish dynamical stability, collapse,
a MOTS, an event horizon, cosmology, or a parameter-neighborhood spectral theorem.
