# Gate review findings and changes: run 20261007T030034Z

- **Review:** `ClaudeCode/reviews/02_lin_static_20261007T030034Z_GATE_REVIEW.md`, by an independent
  gate-review agent for the coordinator, 2026-10-07 at about 04:20Z.
- **Verdict:** READY AFTER MUST-FIXES.
- **Coordinator ruling on point 1:** proceed as assigned, with M1 and M2.

Every change below runs in the final pre-freeze dry run (item 11). The delta goes back to the same
reviewer (DELTA_REVIEW_REQUEST.md) before the freeze.

## Must-fixes

**M1. Registered prediction.**

- The P1–P9 table is frozen in `CONFIG['prediction']`, with the reviewer's tolerances unchanged.
- `assemble4.prediction_record` scores every row CONFIRMED or REFUTED and writes `outputs/PREDICTION.json`.
  - Rows P1–P8 are per amplitude (18 rows each); P9 is the label row. That is 37 rows.
  - The outcome is NEAR_NULL_CONFIRMED iff all 37 are confirmed; otherwise NEAR_NULL_REFUTED.
  - A missing value, or a denominator below 2^-500, is REFUTED with a note.
- The K-only null X'_K = X ∩ [c0 − C G(c0) + (I − C J(B))(X − c0)] is computed exactly from the accepted
  G_center and J_box: `reprep.exact_image_at`, and the verifier's own `own_image_at`.
- The record is scored only when every R, P, T, K and B gate passes. It is never in the validity order.
- `verify4.own_scores` recomputes the scoring, and VS1–VS4 recompute the inputs. The result is
  reported as `prediction_verification`.
- The fixtures test the scoring at every tolerance edge (`unit_edges`).

**M2. Attribution check**, replacing the midpoint diagnostic:

- **Quantities:** Q_c7 = Σ rad(c7_n) D2^n, Q_W0 and Q_W1, for the D' and the K preparation.
- **Variants:** FULL, F, S, B, Z, D and ALL (28 calls), plus the point-mu source variant.
  - The D variant replaces the D ball by mid(D), and takes the upper jets at the point s = mid(D).
  - Those jets use `reprep.imposed_wall_jets`: H is set to its Israel identity, and T and g are met
    with their identities when they meet. At a point away from D*, the inherited wall_jets intersection
    for H would be empty (about 1.4e-7 apart at mid(K), against radii of about 1e-8).
  - This is a departure in implementation detail from the review's text, and it is reported in the
    delta.
- **Decision:** gross normalization with Q_FULL ≥ 2^-500, and DECISIVE at ≤ 0.1 against ≥ 0.9.
  ρ_ALL > 0.1 is FLOOR_LIMITED.
- **Label:** NEXT_WIDTH__<class>, with `__MU_BRACKET` when ρ_mu ≤ 0.1 for all six D' quantities; or
  MIXED, FLOOR_LIMITED or NOT_APPLICABLE.
- **A split:** the label gets `__A_CARRIED_BY_<part>`, plus `__A_NEXT_WIDTH_UNDECIDED` when the part is
  the a box. PHASE.json now carries the end hull.
- **Record:** `outputs/ATTRIBUTION.json`, assigned only when every gate passes. The verifier
  recomputes every variant bitwise (VS6) and the A split (VS5), and recomputes the label; the result is
  `attribution_verification`.
- **Fixtures:**
  - (a) main → NEXT_WIDTH__MODE_JET_RADIUS…;
  - (b) mu at the point 0 → ATTRIBUTION_NOT_APPLICABLE, with no division;
  - (c) unit point jets with a K-size D ball → DECISIVE_D for all three quantities, in the producer and
    the verifier.

**M3. Verifier real-input controls.**

- `verify4.py check` runs the verifier's own controls and returns before any D' quantity.
- `preflight/VERIFIER_CONTROLS_CHECK_1.json`: all controls pass, `outcomes_computed: false`, records
  identical across amplitudes.
- `freeze4` requires it, and the producer's REAL_CONTROLS_CHECK, with current source and runtime hashes,
  and binds both.

## Should-fixes, all adopted

1. B1, the cover, moved to group P.
2. R0m runs for both amplitudes in every job. R1 now also requires identical control records.
3. The accepted lower jets, `common['jets'][0]`, are used in stages A to C, in the producer and the
   verifier.
4. The verifier replays every phase block (VB1, all blocks; VB4, the end hull). The shared `common4`
   helpers are disclosed.
5. New fixtures, each through the production path and resolved:
   - raising-phase → TECHNICAL_INCOMPLETE;
   - zero-slack-closure → BUDGET_NOT_CLOSED;
   - fingerprint-tamper → TECHNICAL_REPLAY_MISMATCH. V1 now passes a fingerprint mismatch only if the
     producer's R1 failed.
6. `freeze4` requires all seven shared inherited modules to equal the finite `BINDINGS.json['sources']`.
7. Latest campaign start 2026-10-07T06:20:00Z. `campaign.sh` refuses afterwards and writes
   FROZEN_NOT_LAUNCHED.json.
8. B2 text corrected to (1 + 2^-29)² − 1 ≈ 2^-28. K2 is kept as a tautology check.
   `previous_bounds()` is exercised in the preflight.
9. The failed REAL_CONTROLS_CHECK.json is kept and cited in the contract.

## Fix found by the dry run

In the fixture the last block is a single cell, so the attribution's cell map must not require cell
last−1. Both the producer and the verifier now keep only the replayed cells. Production is unchanged:
cells 16363 and 16364 are both replayed.

## Delta review (APPROVED AFTER FIXES)

- **Review file:** `ClaudeCode/reviews/02_lin_static_20261007T030034Z_DELTA_REVIEW.md`, sha256 1ce0ef60…,
  from the same reviewer, at about 04:55Z.
- **F1, isolation of the side computations: done exactly as specified.** All four sites are guarded:
  - `reprep.side_inputs`;
  - `assemble4.write_side_records`, for the scoring, labelling and writing;
  - `verify4.side_checks`;
  - `verify4.verify_side_records`, which tolerates missing files and is wrapped in `verify_final`.

  A side error leaves both side records unassigned or unscored (reason `side computation error`), and
  the verifier reports both side verifications as ERROR. The validity label and checks are unchanged.
  The new fixture `side-computation-error` makes the point-mu start state raise in the producer and the
  verifier.
- **C1:** the freeze waits for the final preflight and both real control checks with the final sources,
  and the request's placeholders are filled.
- **Note recorded in the contract:** group Z (H, T, qbg) is a structural no-op, so ρ_Z ≡ 1, and the
  imposed H equals what wall_jets gives wherever the identity lies inside the state's range. The A
  carrier is an argmax, so all four parts are quoted.
