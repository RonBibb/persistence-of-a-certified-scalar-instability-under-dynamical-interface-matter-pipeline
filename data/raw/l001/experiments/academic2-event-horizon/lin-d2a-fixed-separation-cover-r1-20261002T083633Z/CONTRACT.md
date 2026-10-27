# D2A-R1 corrected fixed-separation validated cover

## Question

At the source-bound original proper separation
`D0 = 0.9996389747145851`, can any admissible positive-curvature launch
`0 <= a <= v0` satisfy both upper-wall equations in the declared reduced
static IVP?

## Frozen numerical problem

- The action, wall parameters, launch map, ODE, Picard enclosure, Taylor
  endpoint enclosure, target separation, 1,024 steps, 512-bit Arb precision,
  target launch width `2^-16`, and maximum depth 24 are inherited byte-for-byte
  from the sealed D2A and validated-flow sources.
- The admissible launch range is the complete closed interval `0 <= a <= v0`.
- The exact no-turn lower threshold is `989750001/10000000000`.
- Negative-curvature boxes are outside the positive-curvature route.

## Prospective correction

For every integrated box, the exact Arb enclosures of both upper-wall
residuals are examined. If either residual excludes zero, the box is directly
excluded. Below the analytic threshold, the no-turn theorem is retained as an
additional certificate when its complete path hypotheses hold. It is not the
only fallback. A box that neither route certifies is subdivided; any survivor
at depth 24 makes the cover incomplete.

No separation, wall parameter, interval gate, physical datum, or claim scope
is changed.

## Required preflight

Before production the frozen producer must pass:

1. all six pure classification routes, including the repaired below-threshold
   scalar-residual fallback;
2. exact Arb containment and strict-nesting controls;
3. negative-curvature and target-width branch controls;
4. an exact nominal terminal-cover count;
5. one real below-threshold validated box through the repaired classifier; and
6. exact rational checkpoint round-trip.

## Recovery contract

Production checkpoints atomically record the exact pending bisection stack,
all completed terminal certificates, unresolved boxes, and processed and
integrated counts. Each checkpoint is content-addressed and guarded by the
producer, configuration, bindings, frozen D2A source, validated-flow source,
and validated-flow terminal digests. Resume is refused on any mismatch.

## Classification

Only an exact contiguous cover of `0 <= a <= v0` with no unresolved boxes may
publish
`FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE`.
Otherwise publish `FIXED_SEPARATION_COVER_UNRESOLVED` or technical
incompleteness.

## Claim boundary

An exclusion closes only the original-separation positive-curvature static
route in the declared reduced model. It does not exclude a dynamical radion
bridge, altered action or wall parameters, launches outside the declared
range, the collapse development, or an event horizon. D2B is not authorized
by this contract.
