# D1 raw-GH and bounded-response qualification — final report

## Success and how the bar moved

The pending D1 generalized-harmonic qualification is now decided positively.
The unchanged production GH acceleration passes the predeclared refinement
gate at consecutive compact-direction levels, and the equilibrium-preserving
formulation gives a finite, nonzero, bounded short-time response to a smooth
physical scalar-field perturbation.

The raw-GH result closes the contract gap left by the predecessor packet.  Its
sealed `257 x 241` endpoint was recomputed exactly, then the prospectively
declared `385 x 241` and `513 x 241` levels were added without changing the
operator, source, boundary closure, stencil, radial grid, or `1e-4` gate.  The
maximum normalized acceleration continued to decrease with increasing
observed order.  All three final levels pass the absolute gate, so the
required consecutive-level condition is met.

The conditional perturbation then changed the physical scalar `Phi` by a
smooth compactly supported `1e-6` profile while leaving the metric and initial
velocity unchanged.  Eight explicit-midpoint steps completed.  The scalar
acquired a nonzero velocity, while the Hamiltonian change, gauge residual,
wall residual, signature, and total departure all remained comfortably
inside their frozen limits.  This distinguishes exact equilibrium
preservation from an operator that simply projects nearby physical fields
back onto the background.

The defensible combined classification is:

`D1_RAW_GH_TWO_LEVEL_GATE_PASS__BOUNDED_SHORT_SCALAR_RESPONSE`

The original producer retains its frozen terminal label
`D1_RAW_GH_TWO_LEVEL_GATE_PASS__PERTURBED_RESPONSE_BLOCKED` because a strict
floating-point amplitude comparison reported a false failure.  The separate
roundoff audit verifies that this was technical, not scientific.

## Decisive numbers

### Unchanged raw-GH ladder

| `N_x x 241` | Maximum normalized acceleration | Observed order from preceding level | Passes `1e-4` |
|---:|---:|---:|:---:|
| `65 x 241` | `1.0519114783e-2` | — | no |
| `97 x 241` | `2.4505178409e-3` | `3.593` | no |
| `129 x 241` | `7.9260181114e-4` | `3.924` | no |
| `193 x 241` | `1.4500890573e-4` | `4.189` | no |
| `257 x 241` | `4.0885748120e-5` | `4.401` | yes |
| `385 x 241` | `6.4346795214e-6` | `4.560` | yes |
| `513 x 241` | `1.6732223747e-6` | `4.682` | yes |

The recomputed `257 x 241` record is exactly equal to the predecessor's
sealed record.  The same `h00/h_perp` pair remains dominant and converges
cleanly; `hzz` falls from `1.3433e-5` at `N_x=257` to `5.5321e-7` at
`N_x=513`.  No nonconvergent component or new floor appeared.

### Scalar-response discriminator

- Declared scalar amplitude: `1e-6`.
- Initial normalized full-GH response: `2.5633768606e-6`, finite and nonzero,
  against a `1e-2` upper gate.
- Initial Hamiltonian change: `7.9540409439e-8`, against the `5e-6` floor.
- Final time: `t=0.001` after eight steps of `1.25e-4`.
- Final maximum scalar velocity: `2.5633755883e-9`.
- Final scalar-position change from the perturbed initial state:
  `1.2816830930e-12`.
- Final Hamiltonian change: `7.9525693761e-8`.
- Final corrected gauge maximum: `4.0627456968e-12` against `2e-4`.
- Final corrected wall maximum: `2.2737367544e-13` against `2e-5`.
- Final normalized departure from the equilibrium: `9.9999875350e-7`
  against `1e-4`.
- All eight positivity and per-step gates passed.

The scalar velocity increases nearly linearly over this very short interval,
as expected from the essentially constant initial acceleration.  That is a
resolved short-time response, not evidence for damping or long-time
stability.

## Issues and failed gates

### Frozen amplitude false failure

The producer constructed the declared increment in binary64 by adding it to
the nonzero background and measuring it through subtraction.  The measured
maximum was

`1.000000000001e-6`,

which exceeded the literal upper comparison by `1.0001342e-18`.  That single
boolean was false; every other response gate and every time step passed.

The separate post-run audit used the predeclared binary64 allowance

`8 u max(1, ||Phi_bg||_inf) = 1.7763568394e-15`.

The excess is only `0.000563` of that allowance.  The exact declared
increment `1e-6 shape` is unit bounded, both compact-wall rows are exactly
zero, and the stored increment is inside the roundoff enclosure.  The
corrected classification

`D1_SCALAR_RESPONSE_PASS__FROZEN_AMPLITUDE_GATE_FALSE_FAILURE`

was independently verified.  The frozen producer result was not rewritten.

### Technical audit publication history

The first roundoff-audit capsule failed only when serializing a NumPy boolean
to JSON; it published no result and is preserved as technical incomplete.
The R2 capsule published the complete result and terminal record after a
serialization-only adapter, then encountered the same issue in its optional
console pretty-print.  The authoritative files were intact.  An R3 adapter
published the frozen independent verifier output, which returned `VERIFIED`.
No numerical calculation was repeated or changed during these repairs.

### Remaining scientific limitations

1. The raw ladder refines only `N_x` at fixed `N_r=241`; it is not a complete
   two-dimensional continuum study.
2. The scalar perturbation is a physical-field perturbation but not a
   constraint-solved family of perturbed initial data.
3. Eight steps through `t=0.001` establish immediate bounded response only.
   They do not measure mode growth, damping, or nonlinear stability.
4. A single amplitude and one evolution grid do not establish linear scaling
   or dynamical convergence.
5. Nothing here supplies P16 continuity, collapse, an event horizon, or a
   parent-child relation.

## Publication effect

This result does not alter the saddle/MOTS-to-spacelike-tube paper, whose
finite-resolution horizon evidence belongs to a different branch.  It does
strengthen the separate D1 curved-static-background program in two concrete
ways:

1. the last outstanding unchanged raw-GH representation gate now has a clean
   refinement pass rather than a one-level crossing; and
2. the well-balanced formulation demonstrably responds to a nearby physical
   scalar field instead of preserving only the exact background by
   construction.

That moves D1 from “static equilibrium with a numerically compatible but
contract-qualified GH bridge” to “fully qualified finite-resolution GH
background plus one bounded short-response example.”  It is suitable as
methodological or supporting evidence for a future D1 stability paper, but it
is not yet a stability result and should not be promoted into the horizon
paper's central claim.

## Next step

The qualification requested here is complete, so no further calculation was
started.  The next scientifically meaningful test is not another exact
background preservation run.  It is a prospectively frozen,
constraint-compatible perturbation family:

1. solve the linearized constraints for a scalar/metric perturbation of D1;
2. use at least two amplitudes to test response scaling;
3. evolve on at least two grids with exact-resumption checkpoints; and
4. measure a declared physical norm long enough to distinguish bounded
   oscillation, damping, or growth.

Only that successor could begin to address perturbative stability.

## Verification and artifacts

- Primary producer integrity audit: `VERIFIED`.
- Raw-GH anchor equality and every refinement decision independently
  reconstructed.
- Eight checkpoint pairs authenticated and finite.
- Roundoff correction independent audit: `VERIFIED`.
- Parent sources and frozen manifests match their bound SHA-256 digests.

Primary packet:
`lin-d1-raw-gh-dynamical-qualification-20261005T000023Z`

Roundoff audit:
`lin-d1-raw-gh-dynamical-qualification-r2-roundoff-audit-20261005T004308Z`

Independent-audit adapter receipt:
`lin-d1-raw-gh-dynamical-qualification-r3-audit-adapter-20261005T005131Z`

