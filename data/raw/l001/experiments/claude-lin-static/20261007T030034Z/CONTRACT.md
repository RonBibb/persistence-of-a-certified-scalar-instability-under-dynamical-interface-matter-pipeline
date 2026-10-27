# Narrowed-D' re-preparation of the C7 correction and the root boxes, and the material bounds (line 02, run 20261007T030034Z)

Status: final, after the gate review (READY AFTER MUST-FIXES) and the delta review (APPROVED AFTER FIXES, F1
applied). It becomes frozen at FREEZE.json.

## Question

Run 20261006T230904Z (verified, DSTAR_NARROWED__A_DOMINATED_BY_STATE_RADIUS) narrowed the certified
upper-wall interval from K = [32727/16384, 32729/16384] (width 1.22e-4) to

    D' = [33513605/16777216, 67027255/33554432]   (width 1.34e-6, inside the last source cell 16364)

The family pieces built with the K-width D ball were left unchanged:

- the C7 scalar correction d = C7(s) + b0 H0 + b1 H1;
- the certified root boxes for x = (a, b0, b1);
- therefore A = W + eps psi + w and Phi = P + eps f + d.

Run 3's A bound was 7.81e-6 and its Phi bound 7.39e-5 / 7.49e-5 (positive / negative), both dominated by
the state radius.

**Question.** With every D dependence enclosed over D' instead of K, how far do these shrink?

- the C7 coefficient enclosures and the wall terms W;
- the map G at the box center, and the root boxes a, b0 and b1 after one Krawczyk step;
- the material bounds for A, ell and Phi, the wall observables and the proper separation.

This test introduces a new validated flow and a new root iteration. Run 3 and the historical 1e-50
failure stay as recorded; nothing is rescored.

## Precision, inputs and engine

- Arb (python-flint 0.9.0) at 768 bits, one thread.
- All flows use the inherited strict-Picard, fifth-order Taylor cell enclosure (`validated.step`) with
  step 1/8192. Every decision is an exact rational comparison of Arb endpoints.
- Inherited code (copies in `code/inherited/`, hashes bound at the freeze):
  - `preparation.py` comes from the finite packet, because that version produced the accepted
    preparations. Its hash is 70f6cfa0…, not the identity copy's 5402279f…: the identity copy's
    `remainder_eval` differs, and it returns an extra key.
  - All other modules come from the identity packet. `series`, `records`, `validated`, `algebra`,
    `source_flow` and `nonlinear` are byte-identical in both packets.
- Inputs:
  - the finite packet: the source flow with its checkpoints, both signed case certificates with their
    checkpoints, and `BINDINGS.json`;
  - the connected packet's certified translated root images, X;
  - the native profiles, the spatial packet's grids and records;
  - run 3's verified D' record.

## Stage A: controls, then the D' jets and preparations (every job, before any outcome)

Every job first runs these controls on the accepted inputs. All are bitwise.

| Control | Requirement |
|---|---|
| R0 | Replay the accepted source flow's last block, cells 16128 to 16365, from its own checkpoint with this run's port of the finite cell update. It must equal the accepted final checkpoint bitwise, except elapsed_seconds. |
| R0m | For both amplitudes, in every job, replay the last block of both accepted certificate phases (center and box, cells 16128 to 16365) with this run's port of the upper-wall map. Each must equal its accepted final checkpoint bitwise, including the map hull, and must reproduce the accepted G_center and J_box. |
| R0j | Recompute the accepted K jets. The lower jets use this run's port of the finite runner's fresh initial state, whose canonicalized copy must equal the stored y0. The upper jets use the canonicalized replayed hull over K. |
| R0p | `prepare(eps, jets_K, p)` must equal both accepted preparations bitwise, for both amplitudes. |
| D0 | D' equals run 3's verified record, and K1 ≤ D1 < D2 ≤ K2. D' lies inside the last source cell [16364/8192, 16365/8192]. |

**If any control fails**, the job writes `CONTROL_FAILED.json`, which holds the controls only, and stops.
Every job runs every control, so the six control records are identical, and a control failure stops
every job before any D' quantity exists. The campaign launches no material job. The assembly opens no
outcome record, and the outcomes stay unopened until the coordinator decides.

**Pre-freeze real-data control check.** `reprep.py check` runs the controls alone, with no D' jet or
preparation and no flow, on the real inputs. It is run before the freeze and bound by it.

- The first check failed R0j and R0p. The identity copy of `preparation.py` was in use, and the lower
  jets were formed from the canonicalized y0.
  That failed record, `preflight/REAL_CONTROLS_CHECK.json`, is kept and cited.
- After the port of the finite preparation and initial state, all controls pass for both amplitudes.
- **Verifier twin (M3).** `verify4.py check` runs the verifier's own ports of the same controls, also
  returning before any D' quantity.
- Both checks are rerun with the final sources. The freeze binds both and requires all controls to pass,
  `outcomes_computed: false`, identical records across amplitudes, and current source and runtime
  hashes. Current records: `REAL_CONTROLS_CHECK_6.json` and `VERIFIER_CONTROLS_CHECK_1.json`.

**After the controls pass:**

- **Upper jets over D'.** Range the replayed last source cell over [D1 - s, D2 - s]. Canonicalize it as
  the inherited checkpoint writer does. Intersect it with the wall identities using the inherited
  `wall_jets`. The lower jets are the accepted stored balls, `common['jets'][0]`, used throughout
  stages A to C.
- **Preparation.** `prepare(eps, jets', p | {D: D'})`, which gives c7 and W with the D ball D'. It uses
  the inherited eps-Taylor of order 8 with an interval remainder.

## Stage B: phase flows (four jobs)

These are the inherited 17-state nonlinear flow and its three-parameter variations, with
p = common p | prep' | {D: D'}. They run from s = 0 to cell ceil(D2/h) = 16365.

- **Center phase:** x is the exact midpoint c of X, as an Arb ball.
- **Box phase:** x ranges over X.

The upper-wall map of the finite certificate is formed on the range of each cell over its part of D'.
That covers exactly one piece, [D1, D2] in cell 16364:

- the Israel mismatch;
- the two fifth-jet rows;
- the Jacobian from the variations;
- the wall positivity diagnostics.

**Diagnostic (not a gate).** The center map at the points s = D1 and s = D2. The map hull over D' minus
the point map shows the event-hull part of G.

## Stage C: root iteration and material flows (two jobs)

**Root iteration.** One Krawczyk step, with the frozen preconditioner C = diag(-24/23, 1, 1) of the
certificate:

    K(X) = c - C G(c) + (I - C J(X)) (X - c),      X' = X ∩ K(X)

Here G(c) is the center-phase map hull and J(X) the box-phase Jacobian hull.

**Validation.**

1. The old certificate proved a unique root x* of the true map in the old box, and x* ∈ X, the
   certified image.
2. The true map is the map at D = s = D* with c7(D*) and W(D*). D* ∈ D', so G(c) and J(X) enclose it.
3. By the row-wise mean-value form on the convex box X, x* ∈ K(X). Hence x* ∈ X'.

**Not claimed.** No new existence claim is needed. Uniqueness is inherited because X' ⊂ X ⊂ old box.
Strict inclusion K(X) ⊂ int X and the weighted row norms are recorded as diagnostics only.

**Exclusion.** An empty X ∩ K(X) would contradict x* ∈ X. It can only come from a defect, so it is
classified `ROOT_ITERATION_INCONSISTENT` and is never read as physics.

**Material.** The inherited 11-state prepared flow with x ∈ X' and the D' preparation, on [0, D2]:

- 16365 cells; the last is clipped at D2. Checkpoints every 256 cells, for verification only.
- On each cell, 64 equal subcells are compared with the native hull over [s_a Dn/D2, min(Dn, s_b Dn/D1)].
- At each cell's worst subcell the bound is split into four classes (as in run 3): center, state,
  comparison step (source plus native) and event.
- Walls:
  - The lower wall is the launch state with a ∈ X'_a.
  - The upper wall is the last cell over [D1, D2].
  - Both are compared with the saved nodes for A, ell, Phi, rho, the clock rate and log R. The radius
    split is recorded: rad W, eps rad psi, rad w, rad P, eps rad f, and rad d with its c7 part and its
    root-box part.
- Proper separation: L* ∈ [lo(I), hi(I) + hi(J)], split at D1. It is compared with both saved records.

**Diagnostics (not gates).**

- The c7 and W radii, old K against new D'.
- The G(c) radii, old against new.
- The root widths, old against new, with their ratios.
- The source state radius at the upper wall, K hull against D'.
- The phase records carry the end hull over D' for the A split of the attribution check.

## Registered prediction (M1): frozen, scored, outside the validity order

The near-null expectation is registered as a scored prediction. The table is frozen in
`CONFIG['prediction']`; the reviewer proposed the tolerances, and they are adopted unchanged.

- `assemble4` writes a separate `outputs/PREDICTION.json` and scores every row CONFIRMED or REFUTED. A
  row whose denominator is missing or below 2^-500 is REFUTED, with a note.
- The outcome is NEAR_NULL_CONFIRMED only if every row is confirmed; otherwise it is NEAR_NULL_REFUTED,
  with the refuted rows listed.
- It is scored only when every R, P, T, K and B gate passes. `verify4` recomputes the inputs and the
  scoring with its own code.
- It never enters the validity order or the label.

Rows P1 to P8 are scored per amplitude; P9 is scored once.

| ID | Quantity, each amplitude | Confirmed if |
|---|---|---|
| P1 | Q_c7(D') / Q_c7(K), with Q_c7 = Σ_n rad(c7_n) D2^n | in [0.99, 1.001] |
| P2 | rad W0 and rad W1, D' / K | each in [0.99, 1.001] |
| P3 | rad G(c), new / accepted, for a, b0 and b1 | each in [0.98, 1.02] |
| P4 | widths of X'_{D'} / widths of X'_K, for a, b0 and b1 | each in [0.98, 1.02] |
| P5 | a width of X'_{D'} / a width of X | in [0.90, 0.99] |
| P6 | A bound / run 3 | in [0.93, 1.00], with STATE_RADIUS dominant |
| P7 | Phi bound / run 3 | in [0.98, 1.00], with STATE_RADIUS dominant |
| P8 | attribution, for D' and K, for Q_c7, Q_W0 and Q_W1 | ρ_F ≤ 0.1 and ρ_D ≥ 0.99 |
| P9 | label | REPREPARED__A_DOMINATED_BY_STATE_RADIUS__PHI_DOMINATED_BY_STATE_RADIUS |

**The K-only null in P4.** X'_K = X ∩ [c0 − C G(c0) + (I − C J(B))(X − c0)] is computed in exact
rational arithmetic from the accepted G_center at the certificate center c0 and the accepted J_box over
the certificate box B.

- It is valid because X ∪ {c0} ⊂ B.
- It separates the gain from the iteration from the gain from D'.

**Basis.** These rest on recorded inputs only.

- The upper f and g jet radii (1.32 and 5.47) are point-state radii, and their K-hull part is about
  1.2e-4.
- The c7 and W radii follow the f jets (f[5] radius 1.33e3 against a K-hull part of 0.75).
- G_a is the point radius of v at the wall. G_b0 and G_b1 are the W radii.
- The old row-0 contraction term, about 1.8e-7, mostly drops out of the a width.
- The A state share is 66%, and rad d is set by c7.

## Attribution check (M2): gated, outside the validity order

**Quantities.** For each amplitude, for both the D' and the K preparation:

- Q_c7 = Σ_n rad(c7_n) D2^n, the c7 part of rad d at the upper wall, where both argmaxes sit;
- Q_W0 = rad W[0];
- Q_W1 = rad W[1].

**Variants.** `prepare` is called with one input group replaced by a point, its midpoint ball. That is
7 calls per preparation, 28 in all, computed in the material jobs.

| Variant | Replaced |
|---|---|
| FULL | none |
| F | the f jets at both walls (these carry g) |
| S | the psi jets |
| B | the Phi jets |
| Z | H, T and qbg |
| D | the D ball → mid(D), and the upper jets → those of the replayed source state at the point s = mid(D) |
| ALL | all five groups at once: the floor |

**The D variant's upper jets** (attribution input only, not an enclosure claim) use the inherited
`wall_jets` at that point, with two changes:

- H is set to its Israel identity value;
- T and g are met with their identities when they meet, and set to the identity values otherwise.

Away from D*, the state need not meet the identities.

- The Israel identity's radius comes from rad P and lies far below the state's H radius. So wherever
  the identity lies inside the state's range, the imposed H equals what `wall_jets` gives. T and g use
  the same meet.
- The D variant therefore differs from FULL only by the removed D channel.

- mid(K) = 4091/2048 is the start of cell 16364.
- mid(D') lies inside cell 16364.

**Group Z is a structural no-op.** `prepare` reads only the Phi, psi and f jets, sigma, vi and lam.
Replacing H, T and qbg by points therefore has no effect by construction: ρ_Z ≡ 1. H and T act only
through the jets, inside F, S and B.

- Z's ρ ≥ 0.9 in a decision is not evidence about H or T.
- The decision rule itself is unaffected.

**Normalization.** Every ratio is ρ_g = Q_{g→point} / Q_FULL, a ratio of gross radii.

- No ratio is ever taken over the K→D' change.
- If Q_FULL < 2^-500, the outcome is NOT_APPLICABLE, and no division is made.

**Decision, per quantity.** No additivity is assumed.

- If ρ_ALL > 0.1, the outcome is FLOOR_LIMITED.
- Group g is DECISIVE_g iff ρ_g ≤ 0.1 and ρ_h ≥ 0.9 for every other h.
- Otherwise the outcome is MIXED.

**Label.** It is formed from the six D' quantity outcomes (three quantities, two amplitudes).

1. If all six are decisive with one class: NEXT_WIDTH__MODE_JET_RADIUS (F), NEXT_WIDTH__WALL_POSITION
   (D) or NEXT_WIDTH__BACKGROUND_JET_RADIUS (S, B or Z).
2. Otherwise, if all six are NOT_APPLICABLE: ATTRIBUTION_NOT_APPLICABLE.
3. Otherwise, if any is FLOOR_LIMITED: ATTRIBUTION_FLOOR_LIMITED.
4. Otherwise: ATTRIBUTION_MIXED.

The K outcomes are recorded and enter P8.

**Mu bracket.** This is one point-mu source variant:

- The fresh y0 and p['mu'] are set to the bracket midpoint.
- The 9-state source flow is rerun over all 16365 cells.
- Its last cell is ranged over D', and the upper jets are formed as in the D variant.
- `prepare` is then called with D'.

The suffix `__MU_BRACKET` is added to NEXT_WIDTH__MODE_JET_RADIUS only if ρ_mu ≤ 0.1 for all six D'
quantities. If F is decisive but mu is not, the label stays MODE_JET_RADIUS, because wrapping or the
a box then feeds f.

**A.** The linear split of rad w at the upper wall is recorded:

- the point part, the center phase's rad w over D';
- |u_a| rad X'_a, |u_b0| rad X'_b0 and |u_b1| rad X'_b1, with u from the box phase's end hull
  (y[11], y[13], y[15]).

The largest part names A's carrier. The label gets `__A_CARRIED_BY_<POINT_PART|A_BOX|B0_BOX|B1_BOX|MIXED>`.
If the carrier is the a box, it also gets `__A_NEXT_WIDTH_UNDECIDED`, because this run then leaves A's
next width undecided.

The carrier is an argmax with no dominance threshold, so the result report quotes all four parts.

**Record.** The record is `outputs/ATTRIBUTION.json`, assigned only when every R, P, T, K and B gate
passes. It is never in the validity order, and it is never a defect or physics label. The verifier
recomputes every variant, requires bitwise-equal radii (its own variant code), and recomputes the
label.

## Isolation of the side computations (delta review F1)

The prediction and attribution computations can never fail the validity path. Every site is guarded:

1. **The material job's side inputs** (`reprep.side_inputs`: X'_K, the A split, the 28 variant
   preparations, and the point-mu start state and 16365-cell flow). An error is recorded as
   `side_error` in SUMMARY.json, and the job completes normally.
2. **The assembly's scoring and labelling, and the writing of both side records.** They are written only
   after PRODUCER_RESULT.json. An error leaves the record unassigned or unscored, with reason `side
   computation error`.
3. **The verifier's VS1–VS6** (`verify4.side_checks`). An error, or a producer `side_error`, is reported
   as `side_error`.
4. **The final reading of both side records** (`verify_side_records`). It tolerates missing files and is
   wrapped as a whole.

**Effect of a side error.**

- `ATTRIBUTION.json` has `assigned: false` and `PREDICTION.json` has `scored: false`, both with reason
  `side computation error`.
- The verifier reports `attribution_verification` and `prediction_verification` as ERROR.
- The validity label, `resolved` and every validity check are unchanged.

The fixture `side-computation-error` makes the point-mu start state raise in both the producer and the
verifier. It must still give a resolved REPREPARED label, with both side records unassigned and both
side verifications ERROR.

The point-mu start-state port was also smoke-tested once on the real BINDINGS before the freeze, in the
producer and the verifier. Both gave a finite state with an f0 radius of 3.97e-10. That test computes
only an initial state, not an outcome.

## Gates (validity only; no gate on the size of a bound)

| Gate | Group | Condition |
|---|---|---|
| R0.<job> | R | The source last block replays bitwise. |
| R0m.<job>.<case> | R | The accepted certificate phase maps are reproduced bitwise. |
| R1 | R | The jets' and preparation fingerprints, and the control records, are identical across all six jobs. |
| R0j.<job>, R0p.<job>.<case>, D0.<job> | P | As above. |
| B1.<case>.<phase> | P | The map cover equals [[D1, D2]] exactly. This is a premise of the Krawczyk validity, so it sits before K. |
| T1.<job> | T | A terminal record exists (PHASE.json, SUMMARY.json or ROOT_INCONSISTENT.json) and there is no FAILURE.json. |
| K1.<case> | K | The Krawczyk image meets X, so X' is nonempty. |
| K2.<case> | K | X' ⊆ X. This holds by construction and is kept as a tautology check. |
| B2.<case> | B | Closure holds at every worst subcell (below). |
| B3.<case> | B | The subcells tile [0, D2] with no gap, ending exactly at D2. |

B2 closure, unchanged from run 3:

    |E - (center + rad_a + rad_b)| ≤ 2^-27 (rad_a + rad_b) + 2^-600 (1 + |mid_a| + |mid_b|)

The 2^-27 is a priori. Arb radii are 30-bit mag_t values, rounded up twice in arb_sub, so the excess is
at most (1 + 2^-29)² − 1 ≈ 2^-28. The reviewer's synthetic test found a maximum of 1.00 × 2^-28 over 30,000
adversarial cases. The absolute floor 2^-600 lies far above 2^-767 |mid|.

## Classification (frozen order)

1. `TECHNICAL_REPLAY_MISMATCH`: an R gate fails.
2. `PREPARATION_PIPELINE_MISMATCH`: a P gate fails.
3. `TECHNICAL_INCOMPLETE`: a T gate fails, or a material record is missing.
4. `ROOT_ITERATION_INCONSISTENT`: a K gate fails. This is a defect.
5. `BUDGET_NOT_CLOSED`: a B gate fails.
6. `REPREPARED__A_DOMINATED_BY_<CLASS>__PHI_DOMINATED_BY_<CLASS>`: all gates pass. CLASS is the
   dominant class at the argmax, or MIXED if the amplitudes disagree.
7. `UNRESOLVED_VERIFICATION`: the verifier disagrees.

When a control fails, labels 1 and 2 are assigned from the control records alone, and no outcome record
is opened. No label is a physics verdict. PREDICTION.json and ATTRIBUTION.json sit outside this order.
They are assigned only under label 6.

## Independent verification and label precedence

`code/verify4.py` imports neither `reprep.py` nor `assemble4.py`. It uses its own drivers, its own map
assembly, an exact rational Krawczyk step and its own attribution variants and scoring.

It shares two things, both disclosed:

- the inherited engine;
- the `common4` helpers: paths, CONFIG, read, atomic, plain, fq, up_float, show and the environment
  checks.

Per amplitude (`verify4.py case <w>`):

| Check | Requirement |
|---|---|
| V0, V1 | Its own R0, R0m (both amplitudes), R0j, R0p and D0 equal every job's control records. Its own jets' and preparation fingerprints equal every job's; a mismatch passes only if the producer's R1 failed. After a control failure: its own controls fail as recorded, and no outcome is opened. |
| VB0–VB4 | Phase checkpoint cells. Every block is bitwise, block 0 from its own fresh state. Its own map hull over D' and its own end hull equal the records, and its own cover equals D'. |
| VK1–VK3 | Its exact rational Krawczyk step on the recorded G and J bounds. Its own box satisfies X'_own ⊆ X'_producer ⊆ X, and emptiness agrees. X and c are as recorded. |
| VM0–VM4 | Material checkpoint cells. It replays every block bitwise, block 0 from its own fresh state with X'. Closure and coverage agree. Every per-cell component in blocks 0, 31, 63 and every argmax block equals the producer's upward-rounded binary64. |
| VA, VC, VD | The argmax components are exact, the column maximum equals the bound, and the dominant class agrees. |
| VL | Its own subcell integration of the separation equals the producer's enclosure, and each bound against the saved records agrees. |
| VW | Its own wall bounds for A, ell, Phi, rho, the clock rate and log R equal the producer's, exactly. |

Side records (per amplitude, outside the validity label):

| Check | Requirement |
|---|---|
| VS1–VS4 | The prediction inputs agree: G radii new and accepted, widths, and its own exact X'_K. |
| VS5 | The A split agrees. |
| VS6 | Every attribution variant's radii (D', K and point mu) equal its own recomputation, bitwise. |

Final (`verify4.py final`):

- **VC:** the producer's label follows from the producer's gates in the frozen order.
- **VP:** no recorded producer PID is alive with `reprep.py` in its `/proc/<pid>/cmdline`. Only
  recorded PIDs are checked; there is no name search.

The final label is the producer's label, technical labels included, if and only if every agreement check
passes. Otherwise it is `UNRESOLVED_VERIFICATION`.

The verifier then recomputes the attribution label and the prediction scoring with its own code. It
reports `attribution_verification` and `prediction_verification` as AGREES or DISAGREES. These depend on
VS1–VS6, and they do not change the validity label.

## Pre-freeze tests (`code/preflight4.py`, synthetic only)

**Fixture.** A manufactured background:

- gamma = 0, m2 = 0, T = 0 and P = v0 = v1, so the background is closed-form;
- psi = sec², f = 1 and g = 0 at mu = 0, with mu in a bracket around 0;
- lambda_b = 6 H(s_target), which puts the wall at a known s*.

The fixture builds its own accepted artifacts, at 768 bits, in the finite-packet formats:

- a source flow with checkpoints;
- the K preparations;
- a two-phase certificate with checkpoints;
- a certified root image, which must be strictly included.

It then runs the production record path at 768 bits with 64 subcells, in the production order and with
the production stop rule: `produce_phase` ×4, `produce_material` ×2, `assemble`, `verify_case` ×2 and
`verify_final`. All records are written through `common4.atomic`.

- Step 1/64 and K = [2 - 1/128, 2 + 1/128], over the last two cells as in production.
- D' of width 7.6e-6 lies inside the last cell. Checkpoints every 32 cells.
- The fixture's preconditioner is diag(1/mid J00, 1, 1), formed from its own box phase as the
  certificate's -24/23 was.

Required outcomes:

- **main:** a REPREPARED label, resolved by the verifier. Both wall state enclosures contain the closed
  forms at 0 and s*. The separation encloses the quadrature reference. The upper jets over D' contain
  psi(s*) and P; H encloses the Israel value lambda_b/6 with a width below 1e-200.
- **source-tamper** (R0) and **phase-map-tamper** (R0m): TECHNICAL_REPLAY_MISMATCH, resolved. No
  outcome is opened, and no material outcome exists.
- **preparation-tamper** (R0p) and **D' unrecorded** (D0): PREPARATION_PIPELINE_MISMATCH, resolved.
  There are no outcome files.
- **root-inconsistent:** a box that misses the root in b1 gives ROOT_ITERATION_INCONSISTENT, resolved.
- **verifier-tamper:** an altered material checkpoint gives UNRESOLVED_VERIFICATION, with VM1 failed.
- **unit Krawczyk:** a linear map with a known root. X' contains the root, and the exact rational box
  lies inside the Arb box and contains the root. A box that misses the root gives an empty meet in both.
- **main, side records:**
  - The attribution label starts with NEXT_WIDTH__MODE_JET_RADIUS (fixture (a)), and the verifier AGREES.
  - The prediction is scored over 37 rows, and the verifier AGREES.
- **mu-point (b):** mu is at the point 0, an exact C7 background with Q_FULL < 2^-500. It gives
  ATTRIBUTION_NOT_APPLICABLE without a division, resolved, with both side records AGREES. This is
  item 11's exact-background case.
- **unit wall position (c):** point jets with a nonzero mismatch and a D ball of K size. All three
  quantities give DECISIVE_D in both the producer and the verifier, so the label would be WALL_POSITION.
- **unit edges:** the scoring at both ends of an interval and 2^-60 outside them, a denominator below
  the floor, and a failed side condition. The attribution decision at ρ = 1/10 and 9/10 exactly and
  2^-60 beyond them, the ALL floor edge, Q_FULL at 2^-500 and just below, and Q_FULL = 0. Every case is
  checked in both the producer and the verifier.
- **raising-phase:** an injected failure in the negative phases gives TECHNICAL_INCOMPLETE, resolved.
- **zero-slack-closure:** CLOSURE_RADIUS = FLOOR = 0 gives BUDGET_NOT_CLOSED, resolved, with the side
  records not assigned.
- **fingerprint-tamper:** a PHASE.json fingerprint altered after the phases gives
  TECHNICAL_REPLAY_MISMATCH through R1, resolved.
- **run-3 bounds:** `assemble4.previous_bounds()` reads the recorded run-3 bounds.
- **side-computation-error (F1):** as described in the isolation section above.

The first two runs, `preflight/20261007T033356Z` and `20261007T033928Z`, passed everything except a
definition defect in the closed-form jet check. The check first asked a point identity value lambda_b/6
to contain a 55-digit reference, then asked an Arb-rounded value to equal lambda_b/6 exactly. It now
requires the H enclosure to contain lambda_b/6 with a width below 1e-200, and |lambda_b/6 - H(s*)| < 1e-50.

## Resources and layout

- **Jobs.** Ten jobs, each an independent single-thread process through `slot_run.sh`
  (LINE=02_lin_static, priority 5, cap 3), with RLIMIT_AS 3 GiB, a 3,600 s alarm and at least 8 GiB of
  MemAvailable.
- **Order.** Four phase jobs are launched together. Both material jobs start only after all four phases
  exit 0. Then come the assembly, one verifier per amplitude, and the final verifier.
- **Driver.** `code/campaign.sh` waits only with `wait <pid>` on its own children's recorded PIDs. Its
  own PID is recorded, and the worker monitors it with `kill -0 <pid>`.
- **Expected times.** The real control check ran 948 cells of the 17-state flow, plus 474 source cells and
  four preparations, in under 15 s.
  - each phase: about 3–5 min;
  - each material: about 10–15 min, as in run 3's comparisons;
  - each verifier case: about 20–25 min, with full phase replays;
  - campaign: about 50 min plus queueing.
- **Stage A per job** now replays the accepted phase maps of both amplitudes, which adds about 1 min.
- **No restarts.** Every job is under 1 h, so there is no restart test. A failed job fails closed and is
  not restarted.
- **Cutoff.** Production (phases and materials) must start before 2026-10-07T06:53:30Z. The assembly
  and verifier jobs declare `COMPLETION_OF=<this run>`.
- **Latest campaign start: 2026-10-07T06:20:00Z.** `campaign.sh` refuses to start after it and writes
  `FROZEN_NOT_LAUNCHED.json`; the run is then recorded as FROZEN_NOT_LAUNCHED.

## Deferred stages

The conformal lapse, the inverse map and the node-level propagation are not added. Each needs a new
validated derivation with its own fixtures and an independent review:

- the gauge completion q*;
- X*;
- the inverse map s(x) and the node positions.

One review cycle fits this window, and that cycle is spent on the re-preparation. Their designs remain
in run 20261006T205203Z/CONTRACT.md.

## Gate review record

- **Reviewer:** an independent gate-review agent for the coordinator, not this line's worker.
- **Date:** 2026-10-07, about 04:20Z.
- **Review file:** `ClaudeCode/reviews/02_lin_static_20261007T030034Z_GATE_REVIEW.md`.
- **Verdict:** READY AFTER MUST-FIXES.
- **Coordinator ruling on point 1:** proceed as assigned, with M1 and M2.
- **Other rulings:** the port provenance is sound; the real control check is acceptable and required;
  the deferral is accepted. The next report must name either the propagation or the attributed width
  as the next step.

**Must-fixes** (details in GATE_REVIEW_FINDINGS.md):

- **M1:** the registered prediction P1–P9 above, with two-sided tolerances and the K-only Krawczyk null.
  It is scored in `PREDICTION.json` and recomputed by the verifier.
- **M2:** the gated attribution check above, replacing the midpoint diagnostic. It has the D channel,
  the floor variant, gross normalization with a 2^-500 floor, decisions at 0.1 against 0.9, the point-mu
  variant and the A split. It is written to `ATTRIBUTION.json`, and the verifier recomputes it. Three
  fixtures, (a) to (c), test it.
- **M3:** `verify4.py check` on the real inputs, bound by the freeze.

**Should-fixes, all adopted:**

- B1 moved to group P;
- R0m for both amplitudes in every job, with control-record equality in R1;
- the accepted lower jets used throughout stages A to C;
- full phase replays in the verifier, and the common4 helpers disclosed;
- fixtures for TECHNICAL_INCOMPLETE, BUDGET_NOT_CLOSED and an R1 mismatch;
- all seven shared inherited modules required to equal the finite BINDINGS sources;
- the 06:20Z latest campaign start;
- the B2 text fix;
- `previous_bounds()` exercised in the preflight.

**Delta review.**

- **Reviewer:** the same independent agent. **Date:** 2026-10-07, about 04:55Z.
- **Request:** `DELTA_REVIEW_REQUEST.md`.
- **Verdict:** APPROVED AFTER FIXES.
- **F1** (required): isolate the side computations. Done as specified; see the isolation section.
- **C1:** freeze only after the final preflight and both real control checks pass with the final
  sources, and after the request's placeholders are filled.
- **Rulings:**
  - `imposed_wall_jets` accepted; the two notes it asked for are recorded above, including that Z is a
    structural no-op;
  - the `__MU_BRACKET` and `__A_CARRIED_BY_` suffixes accepted, with the four parts quoted in the
    report;
  - the point-mu lower jets accepted;
  - the synthetic previous record in the fixture accepted.
- The coordinator ruled that no further review is needed if F1 is exactly this.

**Review files (sha256):**

- `ClaudeCode/reviews/02_lin_static_20261007T030034Z_GATE_REVIEW.md`:
  b5cbf1de44efc43dc7268084aee6ecc2dd6238ad0faaa95b506f750571e31ae1
- `ClaudeCode/reviews/02_lin_static_20261007T030034Z_DELTA_REVIEW.md`:
  1ce0ef60ac0ef9027b13c77021849acc2ebc6fe754da2e86ee544496bf7892aa
