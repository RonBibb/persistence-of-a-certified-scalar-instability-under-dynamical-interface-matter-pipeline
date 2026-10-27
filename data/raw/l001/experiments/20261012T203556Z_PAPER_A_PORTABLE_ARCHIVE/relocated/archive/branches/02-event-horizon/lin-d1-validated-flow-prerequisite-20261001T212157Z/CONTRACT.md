# D1 validated-flow prerequisite contract

**Activation:** 2026-10-01T21:21:57Z  
**Immutable no-new-test cutoff:** 2026-10-01T21:48:22Z

## Question

Can direct outward-rounded interval boxes propagate the exact-dyadic D1
proper-distance shooting interval through (s=2) with widths small enough to
justify implementing the variational equation and interval-Newton stage?

## Frozen pilot

- ODE state: ((A,H,\Phi,S,Z,k)), with (k_s=0).
- Shooting interval:
  ([0.09901076956670637,0.09901087894170638]), after promotion of the
  corresponding binary64 values to exact dyadic rationals.
- Fixed endpoint: (s=2); this does not substitute for enclosing the moving
  first upper-Israel event.
- Validated step: Picard self-enclosure followed by a second-order Taylor
  endpoint enclosure using interval bounds for (y''=Df(y)f(y)).
- Arb precision: 384 bits.
- Step counts: 512 and 1024.
- Shooting-box subdivisions: 1, 8 and 32.
- Runtime: the already bound Linux python-flint 0.9.0 target; one process and
  one core.
- Frozen pilot source SHA-256:
  `53bcaab6420d050bc4f7e3ca825f74390e0b59b20fe96feae10e72c32288dd3c`.

## Prospective classification

`DIRECT_BOX_FLOW_READY` requires every box and level to complete and, at
1024 steps with 32 shooting subdivisions, both upper-wall residual widths to
be at most (10^{-3}). This is a readiness gate, not a scientific pass.

`DIRECT_BOX_FLOW_TOO_WIDE` means all enclosures complete but either width
exceeds the gate; D1 then needs a parameter-dependent Taylor model or a
stronger wrapping-control representation before sensitivities.

`VALIDATED_FLOW_PILOT_INCOMPLETE` means a Picard step fails to self-enclose or
the bound runtime fails. It cannot be interpreted as nonexistence.

## Claim boundary

The pilot does not enclose the moving upper-wall event, integrate
sensitivities, apply interval Newton, prove a BVP solution, bind the Kottler
control to the collapse lineage, or authorize any P407 extension.
