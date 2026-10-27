# Lin static two-parameter neighborhood theorem contract

## Scientific question

Does the sealed D1 reduced static first-event solution persist as a unique,
isolated positive-curvature solution in a prospectively declared neighborhood
of the upper-wall scalar target `v1` and upper-wall tension `lambda_b`, while
the exact bulk action, lower-wall launch family, junction equations, proper
distance, and admissible launch interval remain unchanged?  Does the sealed
fixed-separation value `D0` remain excluded throughout that same neighborhood?

This calculation is a robustness theorem for the declared reduced static
boundary-value problem.  It is not a stability, dynamical-selection, collapse,
MOTS, event-horizon, radion-transition, or baby-universe calculation.

## Prospectively frozen parameter box

The aggregate parameter box was declared before any numerical outcome from
this successor was evaluated:

- `v1` central value: `0.09048374180359596`
- `v1` exact lower endpoint: `3256417487256207/36028797018963968`
- `v1` exact upper endpoint: `101988226458125/1125899906842624`
- `lambda_b` central value: `-6.052844277744164`
- `lambda_b` exact lower endpoint: `-1703752349608937/281474976710656`
- `lambda_b` exact upper endpoint: `-1703696054613595/281474976710656`

The approximate half-widths are `1e-4` in each parameter.  No endpoint may be
moved after observing an outcome.

## Frozen root container and launch domain

- root center: `1783621195069987/18014398509481984`
- root-container lower endpoint:
  `222948145784121/2251799813685248`
- root-container upper endpoint:
  `891828611933503/9007199254740992`
- full launch domain: `0 <= a <= V0_Q`
- proper-distance endpoint: `2`

The root container is wider than the sealed point-parameter D1 box by design;
it is not to be contracted or translated in response to a result.

## Frozen numerical operators

The runner imports by digest:

1. the sealed primary D1 Arb interval flow and variational producer;
2. the independently implemented fifth-order D1 Arb producer;
3. the sealed validated D2A fixed-endpoint flow;
4. the sealed D2A exact launch-box cover;
5. the publication-track static theorem authority being extended.

Upper-wall parameters are replaced only by exact Arb balls spanning the
declared parameter cell.  Bulk evolution, lower-wall launch data, action,
junction formulas, precision, step counts, and event rules are unchanged.

## Admission gates for every terminal parameter cell

### A. Parametric root persistence and uniqueness

Both independent D1 producers must validate the first transverse `G=0` event
over the full root container and at the frozen center.  Their event unions must
have `G_s < 0`; the total derivative `q_a` must exclude zero; and

`N(P) = a_center - q(a_center,P) / q_a(X,P)`

must lie strictly inside the frozen root container.  This is required from
both producers for the entire parameter cell.

### B. Global first-event uniqueness

Outside the root container, a gap-free dual-producer interval cover of
`0 <= a <= V0_Q` must classify every launch interval by either strictly
negative initial curvature or same-sign exclusion of the scalar wall residual
at the validated first transverse upper-wall event.  There may be no unresolved
launch interval and exactly one certified root container.

Frozen controls: target launch width `1/65536`, maximum launch bisection depth
`48`, `8192` proper-distance cells per producer, Arb precision `768` bits.

### C. Fixed-separation exclusion

The exact 693 terminal launch intervals from sealed D2A are replayed at the
fixed binary64-promoted dyadic `D0 = 0.9996389747145851`.  Negative-curvature
boxes retain their analytic exclusion.  Every other box is re-integrated with
the sealed 1024-step validated flow and the full parameter-cell Arb balls.
At least one of the two upper-wall residuals must exclude zero on every such
box.  Any unresolved box fails the parameter cell.

## Frozen parameter subdivision rule

The aggregate box is attempted first.  If any gate is unresolved, the failed
cell is subdivided without shrinking the aggregate domain:

1. depth 0 splits `v1` at its exact midpoint;
2. depth 1 splits `lambda_b` at its exact midpoint;
3. depth 2 is terminal.

Thus at most four terminal parameter cells may replace the original box.  A
failed depth-2 cell remains unresolved.  No axis, midpoint, depth, root box,
launch width, or numerical accuracy may be changed after outcomes are known.

## Recovery and reporting

Production writes content-addressed immutable checkpoints after each completed
parallel batch and at least every 180 seconds, plus a mutable informational
`STATUS.json`.  Resume is allowed only when source and input guards match
exactly.  A terminal result is immutable and is never restarted.

The result must report the admitted parameter volume (or exact admitted cells),
all exclusions, unresolved cells, limiting root margins, limiting launch boxes,
and which parameter faces occur in the limiting records.  Negative or
incomplete outcomes are preserved and block a neighborhood-theorem claim.
