# Gate review findings and resolutions (run 20261006T230904Z)

- **Reviewer:** independent gate-review agent for the coordinator (not this line's worker).
- **Date:** 2026-10-06, about 23:55Z.
- **Review:** `ClaudeCode/reviews/02_lin_static_20261006T230904Z_GATE_REVIEW.md`.
- **Verdict:** READY AFTER MUST-FIXES.
- Resolutions were applied by the line worker on 2026-10-07, between about 00:00Z and the freeze. This
  file is written before the freeze, and the freeze script requires it.

## MUST-FIX

| ID | Finding | Resolution |
|---|---|---|
| M1 | The event-stage replays of the other flows used the job's own native profile, so R1e would have failed. | Fixed at 23:38Z, before the review. `replay_block` now takes the profile as an explicit argument with no fallback (`P['profiles'][name]` at every call). |
| M2 | The assembly gates, the classification and the record writes had never run. EVENT_EXCLUSION_INCONSISTENT had no code path. | Fixed. See the M2 details below. |

**M2 details.**

- `narrow.produce()` is now the single record path for both production and fixtures:
  - SUMMARY.json and CELLS.f64, or
  - `EVENT_INCONSISTENT.json` with the full per-flow details, or
  - FAILURE.json.
- `assemble3.assemble()` is the single decision path and reads `EVENT_INCONSISTENT.json`.
- The preflight now runs produce, assemble and verify on every fixture, writing all records with
  `common3.atomic`. It requires these labels:

  | Fixture | Required label |
  |---|---|
  | seam | DSTAR_NARROWED__…, resolved |
  | inflated-interior | DSTAR_NARROWED__…, resolved |
  | tamper | ACCEPTED_FLOW_REPLAY_MISMATCH, resolved |
  | inconsistent | EVENT_EXCLUSION_INCONSISTENT, resolved |
  | D' = K label path | DSTAR_NOT_NARROWED__… |

- The final preflight was rerun after the last contract edit (CONTRACT.md is part of the hashed
  sources).

## SHOULD-FIX (all adopted)

| Finding | Decision |
|---|---|
| A label for D' = K | Added `DSTAR_NOT_NARROWED__A_DOMINATED_BY_<CLASS>`. The width ratio is recorded. |
| Final-label precedence lost technical labels | The verifier now uses agreement checks only. The producer's label, technical labels included, is kept if and only if every agreement check passes and the label follows from the producer's gates in the frozen order. Written into the contract. |
| B1 tolerance had zero margin, and the derivation text was wrong | Set to 2^-27 (an a priori factor-2 margin over the double upward rounding in `arb_sub`). Derivation corrected. The 2^-600 floor is kept. |
| Verifier time estimate (25 min, not 15); wall alarm unused | Estimate corrected. The verifier now enforces `verifier_wall_seconds` (3,600 s) with SIGALRM. |
| Cite the theorem's G, h, root box and k box | Added under "What makes D' valid". |
| Record the a priori width estimate | Recorded as an expectation, not a gate. |
| Walls | The q(wall) = 0 premise is stated. clock_rate and log_angular_radius were added to the verifier's VW. The fixtures require the wall state enclosures of W, H, E and psi to contain the closed-form values at s_true and at 0. |
| Synthetic coverage gaps | Added unit-level `narrow_flow` models where e_I and e_R share a known zero with nonzero slopes: both functions must exclude, and s* ∈ D'. Added a sign-flipped e_R that must leave no survivor. Added an inflated-radius fixture, H(0) ± 1e-7, whose width must be set by the radius (at least 3 pieces) and contain s_true. |
| The verifier did not compare the exclusion counts and flags | VE1 now compares the full per-flow record: counts, contiguity, the derivative enclosure and the monotonicity flag. |
| R2 source | Taken from the replayed final state (`accepted_max_errors_source` records this). |
| Real entry `run()` not exercised | Added `narrow.py check <flow> <record>`. It runs the real context (three profiles, checkpoint listings, the `p['D']` ⊇ K check and an atomic record write) with no outcome. It was run before the freeze, and its record is in `preflight/`. |
| The verifier should also check the case-0 bound | Added VS0. |

## Items reviewed as OK and kept unchanged

- D' validity.
- The [0, D2] domain and the u map.
- D' in the Phi shapes.
- The separation enclosure.
- Normalization and scale.
- The old failure, which is not rescored.
- The JSON types (now exercised).
