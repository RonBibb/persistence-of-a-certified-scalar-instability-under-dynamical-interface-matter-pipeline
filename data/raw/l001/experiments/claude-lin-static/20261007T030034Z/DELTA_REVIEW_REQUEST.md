# Delta review request: line 02_lin_static, run 20261007T030034Z

**Scope.** These are the changes after the gate review
(`ClaudeCode/reviews/02_lin_static_20261007T030034Z_GATE_REVIEW.md`, READY AFTER MUST-FIXES) and the
coordinator's ruling: proceed as assigned, with M1 and M2.

**Status.** Not frozen. No real outcome has been computed. The real-input checks contain controls only.

**Where things are:**

- `GATE_REVIEW_FINDINGS.md` maps every finding to its change.
- `CONTRACT.md` holds the frozen text. See the sections "Registered prediction (M1)", "Attribution
  check (M2)", "Gates", "Independent verification", "Pre-freeze tests", "Resources" and "Gate review
  record".

## M1: the registered prediction, as frozen

The table is in `CONFIG['prediction']` (`code/common4.py`). Your tolerances are adopted unchanged:

| ID | Quantity, each amplitude | Confirmed if |
|---|---|---|
| P1 | Q_c7(D') / Q_c7(K), with Q_c7 = Σ_n rad(c7_n) D2^n | in [99/100, 1001/1000] |
| P2 | rad W0 and rad W1, D' / K (two rows) | in [99/100, 1001/1000] |
| P3 | rad G(c), new / accepted, for a, b0 and b1 (three rows) | in [98/100, 102/100] |
| P4 | widths of X'_{D'} / widths of X'_K, for a, b0 and b1 (three rows) | in [98/100, 102/100] |
| P5 | a width of X'_{D'} / a width of X | in [90/100, 99/100] |
| P6 | A bound / run 3 (exact run-3 SUMMARY bound) | in [93/100, 1], with STATE_RADIUS dominant |
| P7 | Phi bound / run 3 | in [98/100, 1], with STATE_RADIUS dominant |
| P8 | ρ_F ≤ 1/10 and ρ_D ≥ 99/100, for Q_c7, Q_W0 and Q_W1, for D' and K (six rows) | both hold |
| P9 | label (one row) | REPREPARED__A_DOMINATED_BY_STATE_RADIUS__PHI_DOMINATED_BY_STATE_RADIUS |

**Count.** That is 18 rows per amplitude plus P9: 37 rows.

**Scoring.**

- A row is REFUTED if its value is missing or its denominator is below 2^-500, with a note.
- The outcome is NEAR_NULL_CONFIRMED iff all 37 rows are confirmed; otherwise NEAR_NULL_REFUTED, with the
  refuted rows listed.

**X'_K**, the K-only null. It is computed in exact rational interval arithmetic from the accepted
`G_center` (at c0, the finite RESULT `center`) and `J_box`, by `reprep.exact_image_at`. The verifier has
its own copy, `own_image_at`.

**Record.** `outputs/PREDICTION.json`, from `assemble4.prediction_record` and `write_side_records`. It
is scored only when the provisional label starts with `REPREPARED__`; otherwise
`{'scored': false, 'reason': …}`. It is never in the validity order.

**Verifier.**

- VS1–VS4 recompute the inputs: its own G radii, the accepted G radii, the widths, and its own exact X'_K.
- `own_scores` re-scores with its own code.
- The result is `side_records.prediction_verification` (AGREES / DISAGREES) in VERIFICATION.json. It
  does not change the validity label.

## M2: the attribution check (the code and the record)

**Producer** (`code/reprep.py`):

- `ATTR_VARIANTS` lists the variants.
- `variant_preparation` replaces the group's balls by midpoint balls. For D, it sets D → arb(mid D) and
  takes the upper jets at the point.
- `attribution_quantities` computes Q_c7, Q_W0 and Q_W1 as exact rationals.
- `imposed_wall_jets`, `point_state`, `point_mu_preparation` and `attribution_inputs`.
- In each material job, the quantities go into SUMMARY.json under
  `attribution_inputs.quantities[D_prime|K][variant]` and `quantities.MU_point`, as exact strings. The A
  split goes under `attribution_inputs.A_split_rad_w_upper_wall`.

**Decision** (`code/assemble4.py`):

- `attribution_outcome` returns NOT_APPLICABLE if Q_FULL < 2^-500, with no division; FLOOR_LIMITED if
  ρ_ALL > 1/10; DECISIVE_g if ρ_g ≤ 1/10 and ρ_h ≥ 9/10 for every other h; otherwise MIXED.
- `attribution_record` builds the label from the six D' outcomes:
  - NEXT_WIDTH__{MODE_JET_RADIUS | WALL_POSITION | BACKGROUND_JET_RADIUS}, or
  - ATTRIBUTION_{NOT_APPLICABLE | FLOOR_LIMITED | MIXED}, in that precedence.
- The record is `outputs/ATTRIBUTION.json`:
  `{assigned, label, per_quantity_D_prime, per_quantity_K, A_carriers, mu_bracket_named}`. It is
  assigned only when every R, P, T, K and B gate passes.

**Verifier** (`code/verify4.py`):

- `own_points`, `own_imposed_jets`, `own_point_state`, `own_Q` and `own_attribution_quantities` recompute
  all 28 calls plus point mu. VS6 requires bitwise equality of every exact radius string.
- `own_outcome` and `own_attribution_label` recompute the label.
- VS5 checks the A split, using its own replayed phase end hulls.

**Implementation choices that depart from, or add to, your text.** Please rule on these.

1. **The upper jets at a point** (variants D and point mu): `imposed_wall_jets`.
   - The inherited `wall_jets` intersects H, T and g with their wall identities. At s = mid(K), the
     state's H and the Israel value are about 1.4e-7 apart against radii of about 1e-8, so the
     intersection is empty, and `wall_jets` would raise.
   - The same happens for g with mu at a point, because the mode then misses the upper condition.
   - So H is set to its Israel identity value. T and g are met with their identities when they meet;
     otherwise they are set to the identity value.
   - This applies to attribution inputs only. They are not enclosure claims, and no gate depends on
     them.
2. **The mu suffix.**
   - MU_BRACKET is a suffix on the class label: `NEXT_WIDTH__MODE_JET_RADIUS__MU_BRACKET`.
   - It is added only if ρ_mu ≤ 1/10 for all six D' quantities.
   - So fixture (a) reads `NEXT_WIDTH__MODE_JET_RADIUS__MU_BRACKET…`. Its class is MODE_JET_RADIUS, as
     your item 9(a) asks, and the suffix names the mu bracket that the fixture builds in.
3. **The A suffix.** It is always appended: `__A_CARRIED_BY_<POINT_PART|A_BOX|B0_BOX|B1_BOX|MIXED>`,
   where MIXED means the amplitudes disagree. `__A_NEXT_WIDTH_UNDECIDED` is added when the carrier is
   the a box.
   - The parts are the point part (the center phase's rad w over D') and |u| rad X' per box, with |u| as
     maxabs of the box phase's end hull.
4. **The point-mu lower jets** use the inherited `wall_jets` at s = 0. The fresh state satisfies the
   lower identity by construction.
5. **Fixture P6 and P7** use a synthetic previous record, because a fixture has no run 3. Only the
   scoring path and its agreement are required there, not the outcome.

## M3: the verifier's real-input controls

`verify4.py check` runs `own_stage_a(controls_only=True)` for both amplitudes. It returns before any D'
jet, preparation or flow.

**Freeze.** `freeze4` now takes three records: PREFLIGHT, REAL_CONTROLS_CHECK and
VERIFIER_CONTROLS_CHECK. It requires, for both checks:

- all controls pass;
- `outcomes_computed: false`;
- records identical across amplitudes;
- current source and runtime hashes.

It binds both checks.

## Should-fixes (all adopted)

- B1 is in group P.
- R0m runs for both amplitudes in every job, and R1 requires identical control records.
- The lower jets are `common['jets'][0]`.
- The verifier replays every phase block (VB1) and checks the end hull (VB4). The common4 helpers are
  disclosed.
- **New fixtures:** raising-phase, zero-slack-closure and fingerprint-tamper.
  - V1 passes a fingerprint mismatch only if the producer's R1 failed. That makes the R1 fixture
    resolvable while a systematic fingerprint bug still fails.
- `freeze4` checks all seven shared modules against the finite BINDINGS sources.
- `campaign.sh` refuses to start at or after 2026-10-07T06:20:00Z, and writes FROZEN_NOT_LAUNCHED.json.
- The B2 text is corrected, and `previous_bounds()` is exercised.

## Dry-run results (final sources)

- **Preflight:** `preflight/20261007T045713Z/PREFLIGHT.json`. It passed 23 of 23 expectations in 382 s with the
  final sources, including F1's `side-computation-error` fixture. Every fixture resolved.
  - Main: attribution `NEXT_WIDTH__MODE_JET_RADIUS__MU_BRACKET__A_CARRIED_BY_A_BOX__A_NEXT_WIDTH_UNDECIDED`,
    verifier AGREES.
  - Prediction: 37 rows scored, NEAR_NULL_REFUTED as expected for a fixture, verifier AGREES.
  - Mu-point: ATTRIBUTION_NOT_APPLICABLE.
  - Unit (c): DECISIVE_D for all three quantities.
  - Side-error: a resolved REPREPARED label, both side records unassigned (`side computation error`),
    and both side verifications ERROR.
- **Real controls, producer:** `preflight/REAL_CONTROLS_CHECK_8.json`. All pass,
  `outcomes_computed: false`, identical across amplitudes, final sources.
- **Real controls, verifier (M3):** `preflight/VERIFIER_CONTROLS_CHECK_3.json`. All pass,
  `outcomes_computed: false`, identical across amplitudes, final sources.
- **Delta review F1:** applied exactly as specified (see CONTRACT.md, "Isolation of the side
  computations"). The records above are the post-F1 final dry run that C1 requires.
- **Defects found and fixed by the dry runs:**
  - The fixture's single-cell last block lacked cell last−1, which raised a KeyError. The cell map now
    keeps only the replayed cells.
  - VS1 and VS5 compared the verifier's raw replayed map and end hull with the producer's canonicalized
    PHASE.json copies, which pack equal but differ in the last radius bits. The verifier now compares the
    canonical copies; VB2 and VB4 already establish packed equality.

## Timing

- Stage A per job is now about 1 min, because R0m runs for both amplitudes.
- Phases take about 4 min each, materials about 12–16 min (with 28 + 1 preparations and the point-mu
  source flow of about 10 s), and each verifier case about 20–25 min.
- The campaign takes about 55 min plus queueing.
- The latest start is 06:20Z. To finish verification comfortably, the launch is targeted before about
  05:50Z.
