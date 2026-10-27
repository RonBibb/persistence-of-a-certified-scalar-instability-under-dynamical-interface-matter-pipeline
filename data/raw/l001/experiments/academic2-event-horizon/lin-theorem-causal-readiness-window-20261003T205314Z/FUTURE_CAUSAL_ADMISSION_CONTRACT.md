# Executable admission contract for a future Lin causal experiment

## Purpose and firewall

This contract specifies the minimum experiment that can turn a compatible
short evolution into a causal-horizon investigation.  It ports the reviewed
method, not the P407/O4 states or their physical interpretation.  The P407/O4
late lineage failed physical admission and **must not be extended or used as
terminal data**.

The static D1/D2A theorem is an independent mathematical result.  Passing or
failing this causal contract cannot strengthen or weaken that theorem.  The
causal experiment does not begin from the D1 static geometry unless a separate
Cauchy-data bridge proves compatibility; none presently exists.

## Pre-run identity

Before any evolution, freeze one machine-readable authority record containing:

- action, bulk equations, wall equations, corner treatment, gauge, time
  orientation, units, and coordinate-domain definitions;
- initial data and every freely specified field, with proof or numerical gates
  for all bulk constraints and one-sided wall limits;
- source, dependency, runtime, compiler/interpreter, input, and output-schema
  hashes;
- baseline and refined evolution spacings, spatial grids, solver tolerances,
  and the two independently solved outer-domain locations;
- physical definitions of the exterior onset, launch slice, terminal schedule,
  localization metric, and all uncertainty budgets;
- prospective success, adverse-result, technical-incompleteness, and stop
  classifications; and
- atomic checkpoint and exact-resumption semantics for every calculation
  expected to exceed one hour.

Changing an action parameter, initial datum, wall rule, outer-domain location,
terminal time, or scientific threshold creates a new authority.  A failed run
may not be rescued by editing its frozen authority.

## Stage 0 — compatible short-development admission

### 0A. Source-level controls

The producer must pass manufactured or exact controls for:

1. bulk evolution equations;
2. Hamiltonian and momentum constraints;
3. both physical wall equations, evaluated as one-sided limits of the physical
   equations rather than only the implemented boundary rows;
4. corner/rim regularity and parity;
5. time orientation and ingoing/outgoing null conventions; and
6. restart equivalence from an atomic checkpoint.

Every control must record the risk, gate, measured outcome, and inferential
consequence.  Unit-test counts alone are not admission evidence.

### 0B. Four-member short-development matrix

Run a predeclared finite interval on the Cartesian product

| axis | level 1 | level 2 |
|---|---|---|
| evolution representation | baseline | refined |
| outer domain | near | farther |

The four developments are independent solves, not interpolation or copying.
They use the same physical initial data on their common domain.  At every
checkpoint retain raw fields and derivatives needed to reconstruct bulk
constraints, physical wall limits, MOTSs, null characteristics, and the full
worldtube expansion formula.

Admission requires all frozen bulk, wall, corner, causality, and finite-value
gates at every retained checkpoint.  The baseline/refined and near/far
differences must fit inside a prospectively frozen physical error budget on the
common region.  A single compatible member is pilot evidence only; a physical
causal result requires the complete matrix.

Allowed Stage-0 outputs:

- `COMPATIBLE-SHORT-DEVELOPMENT-MATRIX-ADMITTED`;
- `PILOT-COMPANION-ONLY`; or
- `TECHNICALLY-INCOMPLETE`.

Only the first opens the claim-grade stages below.

## Stage 1 — same-lineage MOTS terminal family

Track one outer-MOTS lineage at four prospectively fixed terminal times
`T0<T1<T2<T3`, plus a later held-out quartet `T4<T5<T6<T7` that is not used to
choose thresholds.  At each terminal and for each admitted development retain:

- surface profile at three surface resolutions;
- both null expansions with error enclosures;
- outgoing stability eigenpair and normalization;
- physical rim/contact data;
- predecessor and state identity; and
- proof that the surface belongs to the same branch rather than a nearest-root
  reassignment.

Failure at one terminal remains a failure.  It may not be replaced after the
terminal family is inspected.  This stage establishes terminal surfaces, not
an event horizon.

## Stage 2 — terminal-independence estimator

From every terminal, evolve the outgoing null front backward over one common
interval using both coordinate and Hamiltonian formulations, base and strict
integration tolerances, at least two angular-label counts, and all three
terminal-surface resolutions.  Repeat the primary family across the complete
Stage-0 evolution/domain matrix.

Every trace must pass:

- declared-domain and physical-boundary contact;
- normalized null defect;
- projection and target coverage;
- caustic, crossover, generator ordering, and rim coverage; and
- source/interpolation identity.

For each common observation slice compute the symmetric proper Hausdorff
diameter `D_T` of the four-terminal family in the frozen physical spatial
metric.  Construct `E_num` from the maximum independently measured formulation,
tolerance, label, surface, evolution, and domain transfer—not from the primary
terminal spread.  The admission inequality is

\[
 D_T+2E_{\rm num}\le\delta_{\rm loc}.
\]

`delta_loc`, the observation slices, and the number of required passing slices
must be frozen in physical units.  For code-portability comparison only, the
old O2 controls were null defect `<=1e-8`, projection/coverage `>=0.95`,
`delta_loc=0.05` native cells, `E_num<=delta_loc/3`, and 16 of 17 localized
slices.  Those numbers do **not** transfer automatically to a new physical
authority; any replacement must be justified and frozen before seeing its
terminal family.

The held-out quartet must satisfy the same rule without changing
`delta_loc`.  Also compute the terminal-tail quantities

\[
 b=h(N,M_T+\beta)-\alpha,
 \qquad \lambda=N(\alpha)-\alpha K(N,N),
\]

and the corresponding first-variation injection bound.  Finite samples may
support only a finite-archive localization statement unless an integrable
all-terminal envelope and tail bound are proved.

Stage-2 outputs are:

- `REPRESENTED-TERMINAL-LOCALIZATION-SUPPORTED`;
- `VALID-NO-TERMINAL-LOCALIZATION`; or
- `TECHNICALLY-INCOMPLETE`.

None is by itself an event-horizon result.

## Stage 3 — physical exterior authority

Define a nonempty same-development future exterior `E` with:

- topology, time extent, brane and corner treatment;
- quantitative onset radius or invariant onset condition;
- permitted causal-curve class at physical boundaries; and
- an exact or enclosed relation between any finite measurement worldtube `W`
  and `E`.

The minimum visibility route proves `W subset E`.  A complete surrogate proves
the stronger time-qualified equality `J^-(W)=J^-(E)`.  A computational outer
wall, outgoing boundary condition, monotone coordinate radius, or positive
sampled expansion is not an exterior definition.

If capture uses a barrier at radius `R`, separately define the immediately
outer end `E_R={r>R}` and prove the needed relation between `J^-(E_R)` and
`J^-(E)`.  The full cylinder expansion must retain all radial, temporal, compact,
tilt, warp-slope, and physical-rim terms.  Claim-grade capture requires a
continuum-enclosed sign for all future time or a theorem that supplies it;
finite samples admit only a finite-slab candidate.

## Stage 4 — independent opposing-fate witnesses

Choose a connected launch curve on a fixed physical slice.  Event identity is
assigned before fate and includes development, slice, compact label, physical
position enclosure, and metric-error budget.

For each compact label needed by the intended atlas:

1. **Visible witness:** enclose a continuum future-directed causal curve from
   a launch subinterval to `W subset E`.
2. **Captured witness:** prove a disjoint launch subinterval lies outside
   `J^-(E)`, using the finite-barrier theorem or another complete-family
   theorem.

A low-residual discrete ray is not yet a continuum curve.  One ray later
entering a trapped region does not prove its launch event is captured.  The
visible and captured records must have independent event identity, then be
shown to lie on the same launch curve and development.

Opposing certified fates invoke the reviewed end-relative bracket lemma and
produce an intersection with `H_E=boundary J^-(E)`.  Refine prospectively to
nested brackets whose widths are physical arc lengths including event and
metric uncertainties.  A complete SO(3)-reduced cross-section requires one
admitted bracket for every predeclared compact label, both physical rims,
consistent orientation, noncrossing order, and continuity/coverage.

## Stage 5 — identify the terminal estimator with the causal bracket

On common earlier slices, require the Lane-2 front-crossing enclosure to be
contained in each Stage-4 causal bracket, with total front, projection, launch,
metric, evolution, and domain error smaller than the final bracket width.  The
held-out terminal quartet must remain inside the tightened bracket.  Mere
overlap is a candidate, not identification.

Decision outcomes:

| terminal estimator | causal bracket | allowed conclusion |
|---|---|---|
| pass | pass | terminal front is a supported locator inside a certified end-relative horizon bracket at stated finite resolution |
| pass | absent | terminal-stable null surface in the represented geometry; horizon identity unresolved |
| fail | pass | end-relative horizon bracketed; MOTS-seeded estimator unsuitable in tested epoch |
| fail | absent | no causal conclusion |

Even the strongest row does not identify a horizon relative to future null
infinity unless the causal-past equivalence to that separately defined end is
proved.  It also does not prove smoothness, global topology, generator
completeness, or first formation.

## Stop rules and execution order

Stop before further evolution if the action/initial/boundary system fails
Stage 0, the same-development exterior cannot be defined, the worldtube and
witness authorities refer to different ends, or event identity is ambiguous.
Stop the terminal-estimator lane if the held-out quartet leaves the frozen
error envelope.  Do not move the wall, drop a terminal, enlarge an uncertainty
budget, or switch lineages to rescue an outcome.

The shortest justified order is:

1. freeze and run Stage 0;
2. while the short developments run, review the analytic exterior and barrier
   hypotheses without consuming unsealed fields;
3. after Stage 0 seals, run terminal tracking and the two null formulations as
   independent read-only consumers;
4. pursue witness certification independently of terminal localization; and
5. run Stage 5 only if both inputs are admitted.

This order lets terminal localization and causal-fate certification fail or
succeed independently and prevents another long evolution from standing in for
the missing global argument.
