# D1 fixed-D continuation dimension and robustness test

## Question

With every model parameter fixed, does the certified D1 simultaneous-wall
solution extend through a nonzero connected interval of prescribed proper
separations `D`, or is it an isolated solution of the two-wall boundary
problem?

This test treats `D` as the proposed continuation coordinate but first checks
that the zero set has the mathematical dimension required for continuation.
It does not assume that the numerical width of the certified D1 event bracket
is a physical interval of solutions.

## Frozen problem

- The launch variable is `a` on the complete declared interval
  `0 <= a <= v0`.
- The second coordinate is fixed proper separation `D` on `0 <= D <= 2`.
- The simultaneous-wall map is
  `F(a,D) = (G(a,D), h(a,D))`, with the same `G` and `h` as D1 and D2A.
- All action and wall parameters, exact binary64-promoted dyadics, launch map,
  ODE, positive-curvature condition, and first-event convention remain fixed.
- The inherited D1 root box, global first-event uniqueness cover, and D2A
  fixed-separation exclusion are immutable authorities.

## Registered algorithm

At the inherited D1 root box, two independent validated interval producers
recompute the first transverse `G=0` event:

1. the second-order Taylor/Picard producer at 32,768 cells and 768-bit Arb;
2. the independent fifth-order Taylor/Picard producer at 16,384 cells and
   768-bit Arb.

Each must certify positive launch curvature, all pre-event cells `G>0`, a
contiguous zero-containing event cluster, `G_D = G_s < 0` throughout that
cluster, an immediate post-event cell with `G<0`, and the inherited root
authority.

For `F=(G,h)` with coordinates `(a,D)`, each producer encloses

`det(dF/d(a,D)) = G_a h_D - G_D h_a = -G_D q_a`,

where `q_a = d[h(a,D(a))]/da` is the scalar residual derivative along the
first-event graph. The primary producer calls this quantity `hprime`; the
independent producer calls it `q_a`.

## Objective continuation and stopping rule

A nontrivial fixed-D continuation interval is admissible only if the zero set
of `F` can have dimension one. The test stops immediately with an isolated-root
classification if both independent determinant enclosures exclude zero with
the same sign. A nonsingular two-by-two Jacobian makes the simultaneous zero
locally zero-dimensional, so treating `D` as a free continuation parameter
would add a solution degree of freedom that the fixed model does not possess.

If either determinant contains zero, or either producer loses interval-Newton
authority, positive curvature, first-event transversality, or admissible
launch coverage, the result is `CONTINUATION_DIMENSION_UNRESOLVED`. No step
size, domain, parameter, root box, precision, or sign gate may be changed after
the outcome.

If the seed is not stopped by nonsingularity, a successor would require a
prospectively registered pseudo-arclength formulation. This contract does not
invent a second physical parameter after seeing the result.

## Meaning of the maximal D set

If the determinant is nonsingular and the gap-free D1 cover verifies, the
solution set contains one pair `(a*,D*)`. Its projection onto the D axis is the
singleton `{D*}`. The reported event bracket is then only a rigorous enclosure
of the unknown number `D*`; it is not an interval in which every separation is
a solution.

The test reports how the enclosure lies relative to the source-bound
`D0 = 0.9996389747145851`, but it may not infer a branch between `D*` and D0.

## Required terminal evidence

- exact determinant bounds from both interval producers;
- exact event brackets and curvature bounds;
- verified global D1 uniqueness and D2A classifications;
- a machine-readable result, independent record-level audit, research report,
  and verified manifest.

## Claim boundary

An isolated-root result concerns only the declared reduced static boundary
problem and first-event placement. It does not establish parameter robustness
under a changed action or wall coupling, dynamical selection, stability,
collapse matching, a MOTS, an event horizon, a radion transition, or a baby
universe. D1, D2A, the dynamical work, and all manuscript files remain
unchanged.
