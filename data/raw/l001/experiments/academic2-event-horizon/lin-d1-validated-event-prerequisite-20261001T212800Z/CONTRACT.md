# D1 validated first-event prerequisite

**Activation:** 2026-10-01T21:28:00Z  
**Immutable no-new-test cutoff:** 2026-10-01T21:48:22Z

The preceding frozen Arb flow pilot passed its prospective readiness gate.
This successor uses the same exact-dyadic ODE and shooting interval, divided
into 32 exact sub-boxes, with 2,048 fixed steps through (s=2).

For every shooting sub-box it must:

1. enclose the full trajectory on every step by a Picard self-enclosure;
2. prove the upper-Israel residual is positive on every cell before one
   contiguous zero-containing group;
3. prove it is negative on every later cell;
4. prove (G_s<0) on every zero-containing cell; and
5. enclose the event in a proper-distance bracket of width at most (10^{-2}).

All 32 boxes must pass for classification
`VALIDATED_FIRST_EVENT_BRACKET_READY`. Failure is incompleteness of this
representation, not absence of a BVP solution.

This does not test the upper scalar wall equation, event-time sensitivity or
an interval-Newton map, and it cannot establish the curved background or any
collapse-line event horizon.

Frozen event-pilot source SHA-256:
`44ee7faa10596c6ae89c32d818448cff44ea17bde7b8890ba0b5451d908810b8`.
