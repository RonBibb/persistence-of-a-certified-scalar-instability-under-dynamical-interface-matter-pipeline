# Independent D1 replay: terminal report

## Outcome

The producer-independent replay succeeds.

Using a separately written fifth-order Taylor-jet interval integrator with a
Picard self-containing remainder at 768-bit Arb precision, the R1 calculation
reproduced a strict interval-Newton self-map at both 8,192 and 16,384 steps.
It imported no source from the original D1 producer and consumed none of the
original producer's interval enclosures. The exact post-run audit re-derived
the inclusions from the sealed result and passed every frozen gate.

The result establishes an independently reproduced solution of the **reduced
static boundary-value problem** on the tested positive-curvature branch. It
does not establish stability, dynamical selection, a constraint-compatible
initial-data embedding, collapse, an event horizon, or a baby universe.

## How the evidentiary bar moved

The earlier D1 result no longer rests on one interval-ODE implementation. The
independent replay certifies a root in the frozen narrow input box and encloses
the corresponding geometry and wall relations across the complete domain.

At 16,384 steps the principal enclosures are:

- input root: `0.09901086554679088` to `0.09901086629822892`;
- proper separation: `1.9974365234375` to `1.9976806640625`;
- positive curvature `k`: `0.000326841301145298` to
  `0.0003268413757636101`;
- conformal separation: `6.379214731752709` to `6.381247509927617`;
- warp factor at the upper wall: `0.13509351736863096` to
  `0.13513095816600185`;
- first-integral union: `-5.982751187821706e-6` to
  `5.982179220404177e-6`;
- lower-wall identity: `-5.96911010203316e-11` to
  `5.96911010203316e-11`;
- upper-wall identity: `-5.906509158863721e-6` to
  `5.3012677201549174e-6`.

Every cell's first-integral enclosure contains zero, the warp factor remains
strictly positive and monotonically decreasing, and both upper-wall residual
forms contain zero. The 16,384-step interval-Newton image is strictly nested
inside the 8,192-step image, whose width is `1.5034798423602114e-9`; the fine
width is `7.514380263862197e-10`.

The independent fine root interval and event bracket overlap the original D1
producer's enclosures. This is a comparison after the independent computation,
not an input to it.

## Retained negative result and disclosed issue

The original frozen replay remains correctly classified as not established:
its 4,096-step interval-Newton image was wider than the frozen root box, even
though its 8,192-step calculation passed. R1 prospectively used 8,192 and
16,384 steps and required both to pass; no failed record was overwritten or
reclassified.

Four of five reported derived-geometry widths narrow under the R1 refinement.
The curvature width changes from `7.461609433621896e-11` to
`7.461831207176278e-11`, a fine/coarse ratio of
`1.0000297219462309`. This negligible non-monotonicity is retained in the
audit record. Monotone narrowing of every derived width was not a frozen gate;
strict curvature positivity is independently certified at both levels. The
scientifically load-bearing refinement result is the exact nesting and nearly
factor-two tightening of the interval-Newton image.

The replay is algorithmically independent of the original producer, but it
uses the same mathematical equations and the same Arb interval library. It is
therefore a strong implementation-independent reproduction, not an independent
derivation of the reduced equations or an independent interval-arithmetic
library cross-check.

## Static-to-dynamical bridge assessment

The exact map required for a dynamical test is specified in
`STATIC_TO_DYNAMICAL_BRIDGE_MAP.md`. In flat de Sitter slicing the static
solution supplies spatial data

`h_ss = 1`, `h_ab = exp(2A) delta_ab`,

with zero scalar momenta but nonzero transverse extrinsic curvature

`K_ss = 0`, `K_ab = -sqrt(k) exp(-A) h_ab`

in the stated sign convention. Thus the D1 geometry is not time-symmetric
Cauchy data in that slicing. A valid bridge must explicitly fix the de Sitter
chart, spatial topology, lapse and shift, wall trajectories, scalar momenta,
Israel data, constraint residuals, and the map from proper coordinate `s` to
the evolution coordinate.

The D1 separation near `1.9975` is physically different from the original
collapse separation near `0.99964`; it cannot be obtained by relabeling a
coordinate. The recent fixed-separation exclusion therefore remains intact and
blocks treating this static solution as a solution at the original collapse
separation.

## Next step

The least expensive defensible successor is a **background-embedding gate**,
not a perturbed collapse run:

1. encode the D1 static geometry as full Cauchy and wall data in one declared
   de Sitter slicing;
2. verify the bulk Hamiltonian and momentum constraints and both wall/junction
   conditions under refinement;
3. evolve the unperturbed data briefly and require the expected static
   background to be preserved to convergent error;
4. only after that passes, add a separately specified constraint-compatible
   perturbation and ask a dynamical-selection question.

This sequence prevents a coordinate or constraint mismatch from being
misread as physical instability. A dynamical study at the original separation
requires a different family or continuation argument; D1 alone supplies no
such bridge.

## Viability assessment

The reduced-static theorem line is viable and materially stronger: the root
and its complete-domain geometric enclosures now have a producer-independent
replay. The broader physical program remains unresolved because the missing
step is no longer numerical reproduction of the static solution; it is the
mathematical and constraint-compatible bridge from that solution to the
separate dynamical formulation and physically relevant separation.

