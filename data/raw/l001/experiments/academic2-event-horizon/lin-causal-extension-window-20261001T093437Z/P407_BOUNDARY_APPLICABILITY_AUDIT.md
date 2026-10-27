# P407-R2 boundary-compatibility applicability audit

## Result

Classification:

`SHARED-PREPARATION-ANCESTRY-CONFIRMED__STRUCTURAL-WALL-MODE-APPLICABLE__POST512-KERNEL-NONIDENTICAL__LATE-MAGNITUDE-UNMEASURED`

The branch-01 compatibility finding is relevant to Protocol 407-R2, but its
near-formation numerical magnitude cannot be copied onto the late archive.
The two branches share the prepared-state ancestry and the same legacy wall
closure mode.  Protocol 407-R2 nevertheless switches after H-step 512 to the
P404 H-qualified batched open-bulk implementation.  That implementation is
not byte-identical to the older scalar kernel, even though its added wall
forcings are inactive and its wall equations retain the production legacy
route.

This is enough to require a targeted late-state compatibility measurement
before the represented P407 spacetime is promoted to physical event-horizon
evidence.  It is not enough to declare the P407 evolution invalid.

## What is established exactly

### Executed P407 authority, not the abandoned proposal

The executed lineage is Protocol 407-R2 at the qualified timestep
`H = 1.5625e-5`.  Its frozen authority is

`a3074ad16fe9b7a35d5eddd06e786cc4319d7563e2e01e10dcc91aedfe7a7465`.

The authority records `batch_h_qualified=true`,
`batch_2h_qualified=false`, and classification
`P404-R5-H-ONLY-TERMINAL-QUALIFICATION-PASS`.  Therefore no 2H proposal is
part of the executed P407-R2 state lineage.

### Same prepared-state lineage

The authenticated chain is:

| Stage | Frozen authority SHA-256 | Relevant binding |
|---|---|---|
| P407-R2 | `a3074ad16fe9b7a35d5eddd06e786cc4319d7563e2e01e10dcc91aedfe7a7465` | Starts at the exact P400 H-step-512 terminal state |
| P400 | `7a82c89240d862bcd888f169a4a2f0fc5cc3d497734bd2b23ba17feedf0f8a53` | Binds the P395 authority and result |
| P395 | `288199425ee2e735fc370a72c15ab2f611f6fb1ae2dce0843a1c0676d610420e` | Same-lineage continuation, no new parent solve |
| P240-v3 | `daa82c69e39b683815cf9f61775db38783e621c2d10e6a93cb1073b8082ea104` | Starts from exact P232 steps 72, 80, 88 and 96 |
| P232 | `abc182b4352f8d335e32309e1bbabdbe58eb01826a2406ded8e7137cacddad28` | G10 half-timestep saddle-node parent |

P240's `src/parent_protocol232.py` has SHA-256
`3e1119a7ed3ff469165cd0b9701480cbca6859b5c3493b2ec1af5fd869c7b676`,
exactly matching the corresponding source bound by the branch-01 restored
replay.  That replay also authenticates the P220/P228 inputs and the P188
prepared archive
`7ce55d13e76305b792c144ed5f491c8996876e99991079b7ac5eaf0f201e7b56`.
The branch-01 driver-anchor receipt reports exact identity of all eight G10
constructor arrays after their declared dtype conversions.

This establishes shared prepared-state ancestry.  It does not assert that a
near-formation residual stays constant during the later evolution.

### Same structural wall closure, different post-512 kernel bytes

The old production kernel used by the near-formation audit and by the legacy
P407 bundle has SHA-256
`16de48b28aa62a497bed0a34d786709dc0cfc25fcecc9e960a3aac3e578bca83`.
P407-R2 selects the P404 candidate acceleration after H-step 512; that source
has SHA-256
`48bb5f57e63e0b31bbb1d72e995a84b68fa8fd213942c0b407220dab5a02e945`.

A function-level source comparison shows that the candidate:

1. adds the `batched_open_bulk` positive-radius path;
2. adds four opt-in wall-forcing interfaces; and
3. otherwise retains the legacy compact-wall solve and owner order.

`KernelSwitch` installs all four forcing attributes as `None` on the legacy
RHS object and selects `qualified-batched`.  The bundle retains
`boundary_closure_mode="legacy_wall_axis_outer"`.  No P407 source assigns a
non-`None` forcing later.  Thus the optional wall additions are inactive in
the executed run.  The full acceleration path is still not byte-identical,
because the open-bulk calculation is batched and the candidate source differs.

## What this audit does not establish

- It does not measure `E_ll/T_ll`, the scalar wave residual, the GH
  constraints, or the stored-versus-native acceleration-gradient mismatch on
  a P407 late state.
- It does not transfer the approximately 1.04% near-formation upper-wall
  focusing defect to H-step 512, 1152, or 1792.
- It does not establish that the near-formation defect decays, persists, or
  grows.
- It does not invalidate the exact finite-resolution MOTS lineage or the O2
  null-sheet calculation as statements about the represented P407 geometry.
- It does not authorize recentering the O2 terminal family.  The affine
  terminal-time offset is the measured signal, not a nuisance parameter to be
  removed.

## Consequence for O1 and O2

O1 remains an exact terminal-surface packaging result.  O2 remains a valid,
independently verified finding that the four terminal-seeded null sheets do
not localize on the available finite archive and that this failure is about
35 times its measured numerical envelope.

The physical interpretation remains conditional: O2 characterizes the causal
geometry represented by P407-R2, while branch 01 has shown that the shared
preparation and wall contract can carry a physical bulk-wall mismatch near
formation.  A late-state measurement is therefore a prerequisite to using a
longer P407-like extension as event-horizon evidence.

## Minimal discriminating next calculation

Do not launch another long future extension first.  On three authenticated
P407 states—H-step 512, a middle state such as H-step 1152, and H-step 1792—run
the independently reviewed branch-01 physical compatibility diagnostic using
the actual P407-R2 contract:

- P404 qualified-batched positive-radius kernel;
- `legacy_wall_axis_outer` owner order;
- all optional wall forcings `None`;
- the saved source, memory, and boundary data belonging to each state;
- both supplied boundary jets and native derivatives of stored nodal values.

Record the physical Einstein and scalar residuals, H/M and GH constraints,
all relevant wall rows, and the stored-versus-native acceleration-gradient
comparison.  Preserve absolute values as well as conditioned normalizations.

The decision branches are:

1. **Cleared or demonstrably decaying:** a later terminal-motion rung becomes
   justified.  Repeat the frozen O2 localization test without changing its
   coordinate origin or subtracting the terminal-time offset.
2. **Material and persistent:** the present spacetime is not a clean physical
   parent for an event-horizon claim.  Repair the common initial/boundary
   representation and regenerate from the earliest affected state before
   repeating the MOTS and causal calculations.
3. **Diagnostic not portable to the active kernel:** stop at technical
   incompleteness and first derive/validate the candidate-kernel version.  Do
   not infer either clearance or contamination.

Only after a later archive both passes the physical compatibility gate and
shows terminal-increment damping should full escape/capture or separatrix
reconstruction begin.

