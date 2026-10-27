# O2 — Stable-band multi-terminal backward-null localization pilot

## Question

When four independently certified late outer-MOTS profiles from the same
authenticated P407 evolution are used as terminal data, do their outgoing null
sheets localize to one terminal-independent curve when evolved backward over
the common finite archive?

This is the first consequential use of the new stable-band interface.  It is
not another MOTS-lineage qualification.

## Bound inputs

- P407-R2 epoch-1 evolution, H-steps 512 through 1792;
- the O1 terminal-seed interface at H-steps 1744, 1760, 1776 and 1792;
- midpoint surface resolution N=165 for the four primary sheets;
- the reviewed P405-R3 null-geodesic and unparameterized-curve-comparison
  implementation;
- the P408-R2 Hermite spacetime construction and frozen trace tolerances.

All spacetime and terminal-surface inputs are read-only and hash-bound.  The
surface solver remains binary64.  O2 performs no spacetime evolution and no
MOTS root solve.

## Frozen traces

Primary traces:

- T=1744, 1760, 1776 and 1792;
- N=165 terminal profile;
- 257 angular labels;
- coordinate null formulation;
- base tolerance: `rtol=2e-9`, `atol=2e-11`, maximum step 2H.

Controls, all at T=1792:

- strict integration tolerance at N=165 and 257 labels;
- Hamiltonian formulation at base tolerance, N=165 and 257 labels;
- 129-label transfer at base tolerance and N=165;
- N=157 and N=173 surface transfer at base tolerance and 257 labels.

Every trace is an immutable atomic unit.  No failed control may be replaced,
rescued, or omitted.

## Technical gates

For every trace:

- all generators remain inside the represented domain;
- maximum normalized null defect is at most `1e-8`;
- no local caustic candidate, nonlocal crossover, or polar-ordering loss is
  detected on the requested archive.

For every curve comparison, projection success and target coverage must each
be at least 0.95.  A technical failure produces
`TECHNICALLY-INCONCLUSIVE`; it is not an adverse physical result.

## Scientific observable

At each of the 17 common H-steps 512, 576, ..., 1536, compute all six
pairwise symmetric proper Hausdorff distances among the four primary sheets
and normalize conservatively by the smaller native proper grid cell of the
two curves.  Define:

- `D_all`: the largest of all six normalized distances;
- `D_tail`: the largest distance among T=1760, 1776 and 1792;
- `E`: the largest normalized primary-versus-control distance over every
  common output step and all five T=1792 controls.

The frozen localization target is 0.05 native cells and the frozen numerical
budget is one third of that target.  A common step is localized only if

`E <= 0.05/3` and `D_all + 2 E <= 0.05`,

with all required curve projections admitted.  Finite-archive localization is
supported only if at least 16 of 17 common steps localize.  `D_tail` is
reported as the direct test of whether dropping the earliest terminal tightens
the family; it is descriptive and cannot rescue a failed localization gate.

## Outcomes

- `FINITE-ARCHIVE-TERMINAL-SHEET-LOCALIZATION-SUPPORTED`: at least 16 of 17
  common steps pass after the frozen numerical allowance.
- `VALID-NO-EPOCH1-TERMINAL-LOCALIZATION-FUTURE-EXTENSION-REQUIRED`: all
  technical gates pass, but fewer than 16 common steps localize.
- `TECHNICALLY-INCONCLUSIVE`: any required trace or projection gate fails.

## Interpretation boundary

A positive result would establish only finite-archive terminal insensitivity
of this null-sheet construction, conditional on the inherited P407 spacetime
and its physical-wall treatment.  A negative result would establish only that
epoch 1 is too short for this localization criterion.

Neither outcome establishes an event horizon, future null infinity, a causal
exterior, escape/capture witnesses, global outermostness, a continuum limit,
or the fate of the spacetime.  The `r=10` computational wall is not infinity.
The unresolved boundary-acceleration compatibility question remains an
explicit condition on the interpretation.
