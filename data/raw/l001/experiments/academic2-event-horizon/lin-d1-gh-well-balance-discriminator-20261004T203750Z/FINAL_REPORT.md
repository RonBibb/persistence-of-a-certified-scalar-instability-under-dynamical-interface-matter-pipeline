# Lin D1 equilibrium-preserving formulation — useful-hour final report

## Executive result

The useful-hour investigation isolated four successive finite-resolution
failures in the D1 static-to-dynamical admission path: compact-wall rows,
gauge constraints, ADM acceleration, and the full generalized-harmonic (GH)
right-hand side.  In every subsystem, a D1-specific equilibrium-preserving
subtraction removes the background defect without changing the continuum
equations, the certified D1 root, the wall physics, the source, or any
threshold.  Each subtraction retains a finite, nonzero response to a smooth
`1e-6` perturbation.  The corresponding unchanged direct operators decrease
rapidly under compact-direction refinement.

The final producer completed and its integrity verifier returned `VERIFIED`.
It recorded the terminal classification

`D1_FULL_GH_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS`.

That label requires one post-run qualification.  Producer B's unchanged raw
GH ladder did **not** satisfy its frozen requirement for two consecutive
passing levels.  Only the finest level passed `1e-4`.  The runner nevertheless
started the short evolution because its control flow conditioned evolution on
Producer A and complete well-balanced admission, not on Producer B.  The
contract says that evolution begins only after every prior and current gate
passes.  On the strict reading of that sentence, the terminal label is not a
fully contract-qualified classification.

The defensible result is therefore:

`D1_EQUILIBRIUM_PRESERVING_FORMULATION_ADMITS__SHORT_PRESERVATION_OBSERVED__RAW_GH_TWO_LEVEL_GATE_PENDING`

This qualification does not erase the measured well-balanced admission or
the short stationary evolution.  It prevents those measurements from being
reported as having satisfied every frozen branch of the final contract.

## Scientific question

The starting D1 background satisfied the continuum static equations but did
not meet the production finite-resolution admission gates.  The purpose of
this window was to decide whether the remaining lower-wall failure reflected
the physical D1 construction or a discrete representation that was not
well-balanced for that equilibrium, while preserving the root, source, wall
law, continuum equations, and thresholds.

The investigation was deliberately sequential at the level of mathematical
dependencies: once one representation error was removed, the next unchanged
gate became visible.  No physical parameter was retuned.

## Result chain

| Subsystem | Unchanged direct sequence | Observed order | Equilibrium-preserving response to `1e-6` perturbation | Consequence |
|---|---|---:|---:|---|
| Compact wall | `7.622e-6, 9.321e-7, 1.974e-7, 2.073e-8, 4.046e-9` | `5.18` to `5.68` | `1.231e-7` | Wall defect is a high-order representation error; all frozen wall gates pass after subtraction. |
| Gauge | `1.698e-4, 2.077e-5, 4.397e-6` | `5.18`, `5.40` | max absolute `2.743e-6` | Gauge absolute failure is a representation error; direct refinement also passes its frozen ladder. |
| ADM acceleration | `8.471e-4, 1.496e-4, 4.141e-5, 6.392e-6, 1.645e-6` | `4.28` to `4.72` | max normalized `5.914e-6` | ADM background acceleration is a representation error; direct refinement passes its frozen ladder. |
| Full GH RHS | `1.052e-2, 2.451e-3, 7.926e-4, 1.450e-4, 4.089e-5` | `3.59` to `4.40` | max normalized `2.219e-6` | The well-balanced full RHS admits the equilibrium.  The raw ladder is monotone and its finest level passes, but it lacks the required second consecutive pass. |

The wall, gauge, ADM, and full-GH well-balanced background residuals are zero
by construction at the represented equilibrium.  This is meaningful only in
combination with the nonzero perturbation controls and the direct-refinement
ladders: the formulation preserves this exact equilibrium but does not erase
generic departures from it.

## Final well-balanced admission

Under the D1 equilibrium-preserving formulation, the complete finite-grid
admission path passed on the frozen grids:

- compact-wall residuals were zero and axis residuals were at or below
  `3.59e-13`;
- gauge and outer-boundary residuals passed;
- ADM acceleration residuals were zero on `97 x 181` and `129 x 241`;
- the full-GH background acceleration was zero;
- a coherent `1e-6` metric perturbation produced a finite maximum normalized
  full-GH response of `2.219e-6`.

This establishes a working finite-resolution representation of the certified
D1 equilibrium.  It changes the interpretation of the earlier admission
failure: the obstruction was not a demonstrated failure of the continuum D1
solution, but a stack of production discretizations that did not preserve
that equilibrium exactly.

## Short preservation calculation

Four explicit-midpoint steps with `dt=1.25e-4` were completed on both
`97 x 181` and `129 x 241`.  Eight atomic checkpoints were sealed.  At every
step:

- state change was exactly zero;
- the wall and gauge checks passed;
- positivity margins remained unchanged and positive;
- no stage failed.

This is immediate equilibrium preservation, as expected from an exact
background-subtracted semidiscrete right-hand side.  It is **not** a stability
test.  No perturbation was evolved, and the result does not show how nearby
states behave.

## Post-run contract audit

Producer B used the frozen direct-GH gate:

- monotone: pass;
- last observed order in `[2,6]`: pass (`4.4007`);
- finest residual at or below `1e-4`: pass (`4.089e-5`);
- two consecutive passing levels: **fail**.

The passing-index list is `[4]`, corresponding only to `257 x 241`; the
preceding `193 x 241` residual is `1.450e-4`.  In the frozen runner,
`producer_B.passed` is correctly recorded as `false`, but evolution is guarded
only by `producer_A.passed` and the complete well-balanced admission.  The
independent verifier correctly reconstructs this data and returns `VERIFIED`;
it verifies integrity and internal decision recording, not the semantic
requirement that Producer B also gate evolution.

No frozen artifact was altered and no result was recomputed.  The mismatch is
reported rather than repaired post hoc.

## What is established

1. The D1 continuum equilibrium has a coherent finite-resolution,
   equilibrium-preserving formulation for curvature, wall, gauge, ADM, and
   the full GH right-hand side.
2. All four previously exposed defects behave as numerical representation
   errors: their unchanged operators decay rapidly under refinement, and the
   corresponding well-balanced operators retain nonzero generic response.
3. The represented equilibrium is exactly preserved for four explicit
   midpoint steps on two grids under that formulation.
4. The frozen sources, parent bindings, terminal hashes, result hash, evidence
   hash, and decision records were independently authenticated.

## What is not established

The calculation does not establish nonlinear or linear stability, physical
response to a perturbation, long-time evolution, continuum convergence of the
well-balanced evolution, collapse, a P16 join, parent-child propagation, or a
causal/event horizon.  The raw-GH direct branch has not yet met its required
two-consecutive-level gate.  Exact stationarity is expected from the chosen
equilibrium-preserving formulation and must not be described as spontaneous
dynamical settling.

## Next bounded discriminator

No new calculation was started after the one-hour boundary.  In a future
authorized window, the least expensive closure is to extend the unchanged
raw-GH ladder by one predeclared compact-direction level while retaining
`N_r=241`.  If that next level is below `1e-4` with the expected monotone,
order-consistent behavior, the frozen two-consecutive-level requirement can
be tested directly.  The alternative is a prospective contract that declares
Producer B diagnostic rather than gating; that change cannot be applied
retroactively.

Only after the contract issue is resolved would a small, explicitly
perturbed evolution be the informative next physical test.

## Artifact inventory

The useful-hour evidence is distributed across these immutable namespaces:

- `lin-d1-wall-well-balance-discriminator-r1-20261004T201152Z`
- `lin-d1-gauge-well-balance-discriminator-20261004T202200Z`
- `lin-d1-adm-well-balance-discriminator-20261004T203221Z`
- `lin-d1-gh-well-balance-discriminator-20261004T203750Z`

The first disposable wall run is preserved separately as a technical failure:
`lin-d1-wall-well-balance-discriminator-20261004T200437Z`.

