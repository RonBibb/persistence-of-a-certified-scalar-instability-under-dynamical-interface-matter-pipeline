# The accepted A bound is mostly a comparison artifact; the wall-position width dominates next

Run `20261006T205203Z`, line 02 Lin static, 2026-10-06 UTC.

**Classification:** `ENCLOSURE_BUDGET_RESOLVED__A_DOMINATED_BY_COMPARISON_STEP`.

- Producer gates: 23 of 23.
- Independent verifier: 65 of 65 checks. It resolved the result and agrees with the producer.
- Freeze: guard `8d5f5d014df2ff1b3c66d3122a9c7ccca5e488650a2b626c88e29c41a2e5a25c`, written at 21:01:35Z, before any real outcome.
- Contract: [CONTRACT.md](CONTRACT.md).
- Production started at 21:01:43Z. Ronald's launch cutoff was 21:51:21Z.

## Success and gap movement

Every 256-cell block of the three accepted identity flows (mode, positive and negative) was
replayed from its own checkpoint.

- All 192 blocks reproduced the checkpoints bitwise.
- The replayed bounds equal the inherited RESULT.json and SPATIAL_ENCLOSURES.json values
  exactly.
- Each per-cell bound E then splits exactly into four classes (closure has no violations):
  - **Center discrepancy**: how far apart the enclosure centers are.
  - **State radius**: the radius of the validated state.
  - **Comparison step**: the cost of comparing whole-cell ranges at step h = 1/8192.
  - **Event width**: the certified wall interval D*, width 1.22e-4, entering through u = s/D*.

**A (positive / negative).**

- The accepted bound is 1.986e-4 / 1.988e-4. It is attained at cell 16362, s = 1.99731, next to
  the upper wall.
- At that cell:

  | Class | Size | Share | Notes |
  |---|---:|---:|---|
  | Comparison step | 1.23e-4 | 62% | source 6.16e-5 + native 6.15e-5 |
  | Event width | 6.15e-5 | 31% | |
  | Center discrepancy | 8.8e-6 | 4.4% | |
  | State radius | 5.1e-6 | 2.6% | |

- The certified source rectangle, mode bracket and correction boxes together reach only 5.1e-6
  at this cell.
- Evaluating the same validated cells on 16 subcells gives a rigorous refined bound of
  **8.31e-5 / 8.32e-5**, 42% of the accepted value. The event width then dominates at 74%
  (6.15e-5).

**ell.** The accepted bound is 2.297e-7, with the same pattern (step 59%, event 29%). The refined
bound is 1.03e-7, with the event width at 65%.

**Phi.** The accepted bound is 7.76e-5 / 7.90e-5, and the state radius dominates (91% / 89%).
Refinement gains only 3% (7.51e-5 / 7.65e-5).

- Of the state radius at the argmax (7.06e-5):
  - rad(P) is 8.9e-7;
  - |eps|·rad(f) is 6.6e-6;
  - about 6.3e-5 is left over.
- By the frozen field formula, that remainder is the prepared scalar correction
  d = C7 + b0 H0 + b1 H1, evaluated with the D ball, the root boxes and the C7 eps remainder.
  This is derived arithmetic on recorded values, not a separately recorded component.

**Mode source.**

- psi: the accepted bound is 2.297e-2, mostly step (59%) and event (29%). The refined bound is
  1.03e-2. Only about 24% of psi's state radius is first-order mu.
- f and g: the accepted bounds are 2.056 and 8.50. They are dominated by the state radius (64%)
  plus the center discrepancy (36%). The first-order mu share equals the whole state radius
  (1.32 against 1.32, and 5.46 against 5.46), so the mu bracket of width 1e-5 dominates these.
- The large center term (0.73 and 3.03) is consistent with the bracket midpoint lying away from
  the eigenvalue. That is reasoning; it was not computed separately.
- Background W: 1.94e-4 accepted and 7.8e-5 refined, dominated by the event width.

**Gap movement.**

- The "about 2e-4" A bound that the TRANSFER flagged is not a limit of the source rectangle or
  the mode bracket. 93% of it is the comparison step plus the event width.
- A free re-evaluation already halves it. The next width to narrow is the certified upper-wall
  interval D*.
- Phi is instead limited by the scalar-correction state radius.
- The large mode-function bounds (f, g) come from the mu bracket. They enter the prepared fields
  only through eps·f, which is 6.6e-6.

## Issues

- **Propagation not performed.** The time window did not allow propagation through the
  gauge-completion lapse, the inverse map or the initial observables. The design is recorded,
  unexecuted, in CONTRACT.md under "Deferred". No lapse, map or observable bound is claimed.
- **Sub-attribution is diagnostic only.** The state-radius split is first order. The Phi part from
  d is inferred as a remainder, and the f/g center offset is attributed by reasoning.
- **Shared engine.** The verifier uses its own driver but the same inherited validated engine,
  which is disclosed. It recomputed all components in its sampled blocks: 73,402 values, each
  equal to the producer's upward rounding. It also recomputed every argmax cell exactly.
- **Scope of the refined bound.** It is a sharper rigorous evaluation of the same accepted
  enclosures. It extends no claim.
- **Zero case.** Its metric correction is still not separately validated.

## Next steps

These are for a later window; nothing further runs in this one.

1. Narrow the D* enclosure by event refinement inside the existing last two cells. This is a
   permitted follow-up now that the dominant width is identified. After it, the A bound would
   fall toward the center + state + step remainder, about 2e-5.
2. Then freeze and run the deferred propagation design unchanged.

## Viability

Continue in a later window. The dominant width is identified, and a free sharpening (×0.42 for
A) is already established.

## Evidence class

An exact, independently verified decomposition of accepted validated (768-bit Arb) enclosures,
plus rigorous refined bounds. It is finite-resolution enclosure analysis, not a new certificate.

## Execution

| Job | Slot | PID | Wall time |
|---|---:|---:|---:|
| Mode | 4 | 490798 | 133 s |
| Positive | 1 | 490775 | 314 s |
| Negative | 2 | 490782 | 318 s |
| Verifier | 1 | 495475 | 33 s |

- The three producer jobs ran in parallel through slot_run.sh with LINE=02_lin_static.
- Assembly ran on slot 1.
- Every job used one thread and an RLIMIT_AS of 3 GiB.
- The run bound 214 inputs; the 210 that are not manifest files each match their predecessor
  manifest.
- No new flow, interval change or time evolution.

## Artifacts

All paths are relative to this run.

- **Contract and freeze:** `CONTRACT.md`, `FREEZE.json`, `FREEZE_RECORD.json`.
- **Final preflight:** `preflight/20261006T210057Z/PREFLIGHT.json`.
- **Code:** `code/budget.py`, `code/verify2.py`, `code/assemble.py`, `code/preflight2.py`,
  `code/freeze2.py`, `code/common2.py`, and `code/inherited/` (byte-identical copies).
- **Producer outputs:** `outputs/{mode,positive,negative}/SUMMARY.json` and `CELLS.f64`
  (per-cell components), and `outputs/PRODUCER_RESULT.json`.
- **Verification:** `verification/VERIFICATION.json`.
- **Logs:** `logs/`.
- **Seal:** `FINAL_PROCESS_CHECK.json` and `MANIFEST.json`.
