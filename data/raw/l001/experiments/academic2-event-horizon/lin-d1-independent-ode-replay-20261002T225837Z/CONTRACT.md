# Prospective contract: independent D1 interval-ODE replay

Activation: `2026-10-02T22:58:37Z`  
No-new-test cutoff: `2026-10-02T23:58:37Z`

## Question

Can a producer-independent interval implementation reproduce the D1 shooting
existence certificate from the declared equations and exact binary64 inputs,
without importing the original producer or consuming any of its interval
enclosures?

## Frozen model and domain

Use the action reduction and orientations stated in the sealed D1/D2A theorem
consolidation. The decimal literals are promoted from binary64 to exact dyadic
rationals:

| input | literal |
|---|---:|
| `m^2` | `0.41` |
| `gamma` | `20.0` |
| `v0` | `0.1` |
| `v1` | `0.09048374180359596` |
| `lambda_a` | `5.999990376773895` |
| `lambda_b` | `-6.052844277744164` |
| root center | `0.09901086589880687` |
| narrow root box | `[0.09901086489880687, 0.09901086689880687]` |
| integration endpoint | `s=2` |

The twelve propagated quantities are
`(A,H,Phi,S,Z,k,A_a,H_a,Phi_a,S_a,Z_a,k_a)`, with
`Z_s=exp(-A)`. No prior state or enclosure is an input.

## Independent method

The replay source must not import any D1 producer module. It uses:

- Arb outward ball arithmetic at 768-bit precision;
- an independently implemented truncated power-series algebra;
- an autonomous fifth-order Taylor endpoint enclosure;
- a Picard self-containing Cartesian box on every proper-distance cell to
  bound the fifth-order remainder;
- direct twelve-state propagation rather than the producer's hand-coded
  second derivative and `TimeDual` path;
- two predeclared levels, 4,096 and 8,192 equal steps.

The original D1 enclosure may be compared only after the independent result
has been written.

## Root replay gates

The root replay passes only if, at both step levels:

1. every cell obtains a strict Picard self-containment;
2. the upper-Israel zero-containing cells are nonempty and contiguous;
3. `G>0` on all preceding cells and `G<0` on all following cells;
4. `G_s<0` on the zero-containing cells;
5. the total derivative `q'(a)` excludes zero; and
6. the interval-Newton image is strictly inside the frozen narrow root box.

Nesting of the 8,192-step Newton image inside the 4,096-step image is recorded
but is not needed for the existence theorem.

## Derived-geometry gates

If the root replay passes, use the independently generated root-box flow to
enclose:

- positive curvature `k`;
- proper separation `D` and conformal separation `L=Z(D)`;
- the warp factor and its minimum, with monotonicity reported;
- the proper-coordinate first integral
  `H^2-1-S^2/12+m^2 Phi^2/12-k exp(-2A)` on every cell;
- the lower- and upper-wall algebraic curvature identities; and
- both upper-wall residuals on the root/event enclosure.

This part passes only if `k>0`, `D>0`, `L>0`, the warp lower bound is positive,
the first-integral interval contains zero on every cell, both wall-identity
intervals contain zero, and both upper-wall residual intervals contain zero.

## Classification and boundary

- Root and geometry gates pass:
  `INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS`.
- Root gates pass but a geometry gate fails:
  `INDEPENDENT_D1_ROOT_REPLAY_PASS_GEOMETRY_INCOMPLETE`.
- Complete run without root inclusion:
  `INDEPENDENT_D1_REPLAY_NOT_ESTABLISHED`.
- Exception or missing level:
  `INDEPENDENT_D1_REPLAY_INCOMPLETE`.

No stability, dynamical selection, collapse, event-horizon, radion-transition,
or baby-universe inference follows.

