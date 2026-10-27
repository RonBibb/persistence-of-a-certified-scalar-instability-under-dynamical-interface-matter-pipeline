# D1 gauge-constraint well-balance discriminator

## Bounded question

The verified D1 curvature and wall background well-balances pass their frozen
gates.  The next unchanged stage fails only the absolute GH gauge constraint:
`6.981e-4` at `97x181` and `1.698e-4` at `129x241`, while the local-relative
gate already passes and the sequence decreases.  This experiment asks whether
that mismatch is the discrete image of the exact D1 gauge source.

No physical field, certified root, wall law, gauge-source convention, domain,
admission threshold, or continuum equation may change.

## Producer A: D1-background gauge well-balance

Retain the admitted D1 curvature and wall background formulations.  For the
GH constraint `C=Gamma-H`, define

`C_WB(q) = C_prod(q) - C_prod(q_D1) + C_exact(q_D1)`.

The frozen analytic source is `H=Gamma[g_D1]`, so `C_exact(q_D1)=0`.  The
correction subtracts only the finite-difference background image.  The source
values, public source `at(...)` interface, contracted-Christoffel
implementation, and all evolution equations remain unchanged.

Evaluate original grids `(65,121)`, `(97,181)`, `(129,241)`.  A smooth
`1e-6` tangential-metric perturbation must produce a finite nonzero corrected
constraint.

## Producer B: unchanged direct gauge refinement

At fixed `N_r=241`, evaluate the unchanged gauge constraint at
`N_x=(129,193,257)`.  It passes only if absolute and local-relative values are
monotone, the final observed absolute order lies in `[2,6]`, the finest values
meet `5e-5`, and two consecutive levels meet both gates.  This is a gauge-only
diagnostic and cannot override the previously failed direct bulk-curvature
ladder.

## Conditional continuation

Only Producer A can advance.  After its corrected gauge gate, the source-time,
mixed-source, radial-moment, outer-reference, outgoing-characteristic,
corrected-ADM, and raw-GH acceleration gates remain unchanged.  No later
subsystem is silently corrected.  Four unperturbed midpoint steps at
`dt=0.000125` are authorized only if every admission gate passes, with atomic
per-step checkpoints.

## Classification

- `D1_GAUGE_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS`
- `D1_GAUGE_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_<GATE>`
- `D1_GAUGE_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED`
- `D1_GAUGE_WELL_BALANCE_TECHNICAL_INCOMPLETE`

All conclusions are finite-resolution formulation results for one D1
background.  No continuum, stability, P16, collapse, parent-child, or causal
claim follows.

