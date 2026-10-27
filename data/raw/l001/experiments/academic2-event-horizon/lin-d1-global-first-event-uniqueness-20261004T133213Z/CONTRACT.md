# D1 global first-event uniqueness cover

## Question

Is the already certified D1 simultaneous-wall solution the only
positive-curvature solution over the complete declared launch interval
`0 <= a <= v0`, when the upper wall is placed at the first transverse zero
of the upper Israel residual?

This is a bounded theorem test in the existing reduced static model. It does
not change the model, wall parameters, admissible launch interval, certified
D1 root, or any dynamical calculation.

## Frozen mathematical problem

- The exact binary64-promoted dyadics for `m^2`, `gamma`, `v0`, `v1`,
  `lambda_a`, and `lambda_b` are inherited from the sealed D1 producers.
- The launch interval is exactly `0 <= a <= V0_Q`.
- Positive curvature means the launch curvature `k(a)` is nonnegative.
- For each launch box, the upper wall is the first zero of
  `G = H - [lambda_b + gamma(phi-v1)^2/2]/6` on `0 <= s <= 2`.
- A simultaneous-wall solution additionally requires
  `h = S + gamma(phi-v1)/2 = 0` at that first event.
- The certified narrow D1 box is inherited unchanged and is accepted only
  after both sealed root authorities and their byte digests verify.

## Independent interval producers

Every non-root positive-curvature terminal exclusion must be established by
two frozen, digest-checked implementations:

1. the validated second-order Taylor/Picard D1 flow; and
2. the producer-independent fifth-order Taylor/Picard D1 replay.

Both use 768-bit Arb arithmetic and 8,192 proper-distance cells. These are
already validated levels of the two sealed producers. The two implementations
must independently certify the first event, strict transversality, and a
same-sign scalar residual interval excluding zero.

The event calculation stops after the contiguous zero-containing cluster and
the immediately following strictly negative cell. This is sufficient for the
first-event question: every preceding cell has `G>0`, the event cluster has
`G_s<0`, and the following cell has `G<0`. It avoids integrating an irrelevant
post-event branch that can become unbounded.

## Gap-free adaptive cover

The exact launch interval is partitioned around the inherited narrow D1 box.
Outside that box:

1. a box is excluded without integration only when both producers enclose
   launch curvature strictly below zero;
2. boxes wider than `2^-16` are bisected exactly;
3. narrower boxes are evaluated by both interval producers;
4. a box is excluded only when both first-event certificates pass and both
   scalar-residual intervals exclude zero with the same sign;
5. any box that does not certify is bisected, through depth 48;
6. a survivor at depth 48 is recorded exactly as unresolved.

No domain, parameter, interval sign condition, root box, or solver success
criterion may be relaxed during the run.

## Root authority

The inherited D1 root box may be labelled `CERTIFIED_D1_UNIQUE_ROOT` only if:

- the primary 32,768-step result and terminal record verify by digest and carry
  `RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS`;
- the independent replay result and terminal record verify by digest and carry
  `INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS`; and
- both records identify the same inherited narrow root box.

The local interval-Newton theorem establishes exactly one root inside that
box. The new cover addresses all launch values outside it.

## Recovery and integrity

Production uses atomic, content-addressed exact-resumption checkpoints. Each
checkpoint binds the producer source, configuration, bindings, all imported
source and authority artifacts, and the exact pending/terminal state. A
restart must refuse any guard mismatch. A lightweight mutable `STATUS.json`
is informational only and never authoritative.

## Terminal classifications

`GLOBAL_FIRST_EVENT_SIMULTANEOUS_WALL_ROOT_UNIQUE_ON_DECLARED_POSITIVE_CURVATURE_LAUNCH_INTERVAL`
is permitted only if the exact cover is contiguous from `0` through `V0_Q`,
the inherited D1 root is the sole root box, and every other admissible
positive-curvature box is excluded by the two-producer first-event test.

Otherwise the result is
`GLOBAL_FIRST_EVENT_UNIQUENESS_UNRESOLVED`, with every unresolved exact box and
its obstruction preserved. A runtime or integrity failure is technical
incompleteness, not evidence for or against uniqueness.

## Claim boundary

A passing result is a global uniqueness theorem for the declared reduced
static first-event shooting problem only. It does not establish dynamical
selection, stability, collapse matching, a MOTS, an event horizon, a radion
transition, or a baby universe. D2A and all manuscript files remain unchanged.
