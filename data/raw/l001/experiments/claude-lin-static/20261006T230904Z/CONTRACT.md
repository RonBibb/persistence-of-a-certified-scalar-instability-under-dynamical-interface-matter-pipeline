# Narrowing the certified upper-wall interval D*, and the bounds it controls (line 02, run 20261006T230904Z)

Status: final draft after gate review (see the Gate review record). It becomes frozen at FREEZE.json.

## Question

Run 20261006T205203Z decomposed the accepted A bound of 1.99e-4 at its argmax next to the upper wall:

| Component | Share |
|---|---:|
| Comparison step | 62% |
| Event width (wall position D* in K = [32727/16384, 32729/16384], width 1.22e-4) | 31% |
| Center discrepancy | 4.4% |
| State radius | 2.6% |

At 16 subcells the bound fell to 8.3e-5, and the event width then made up 74% of it.

**Question.** How narrowly do the existing validated enclosures of the last two cells locate D*?
Given that location, what rigorous bounds follow for:

- the material fields A, ell and Phi, and the eight mode-flow fields;
- the wall observables;
- the proper separation?

No time evolution. No new flow. No change to any flow parameter.

## What makes D' valid

The inherited static theorem (lin-static-theorem-publication-upgrade, UPGRADED_THEOREM.md, items 1 and 2) supplies:

- D* = D(a*), the first transverse zero of the upper Israel residual G.
- The scalar residual also vanishes there: h(D*, a*) = 0.
- a* lies in the certified root interval [0.09901086489880687, 0.09901086689880687].
- k lies in [0.000326841301145298, 0.0003268413757636101].
- D* ∈ K = [1.99749755859375, 1.99761962890625].

On the background, G and h are the upper-wall identities of the inherited `preparation.wall_jets`
with sigma = -1. These are also the upper-wall rows of the spatial packet's `build_grid.py`, which is
an independent code base:

    e_I(s) = H - (lambda_b + gamma (P - v1)^2 / 2) / 6     (Israel; e_I(D*) = 0)
    e_R(s) = T + gamma (P - v1) / 2                        (scalar Robin; e_R(D*) = 0)

The three accepted flows carry validated Taylor models of the background (H, P, T, E) on cells 16363
and 16364. These models cover K over the full a, k and mu boxes.

**Exclusion.**

1. Split K at the cell seam 4091/2048 (the exact start of cell 16364). This gives [Dlo, 4091/2048] in
   cell 16363 and [4091/2048, Dhi] in cell 16364.
2. Split each half into 2048 equal closed pieces that share endpoints, 4096 pieces in total.
3. Exclude a piece if and only if the enclosure of e_I or of e_R has lo > 0 or hi < 0.
4. D'_flow is the hull of the surviving pieces. The common D' = [D1, D2] is the intersection over the
   three flows, and every producer job recomputes it identically.

Validity uses only the theorem, the two identities and the validated models. No numerical seed value
enters.

**Diagnostic (not a gate).** The enclosure of e_I' = -T²/3 - k E² - gamma (P - v1) T/6 over K. If it
excludes 0, e_I has at most one zero in K.

**A priori expectation (reviewer, recorded; not a gate).**

- At the common zero, the Robin identity cancels the T² terms. That leaves e_I' = -k E² ≈ -0.018.
- The radius is rad(e_I) ≲ 1.2e-8.
- Hence D' ≈ 1.3e-6 wide, about 44 pieces, or 1% of K. e_R should exclude little.
- A should fall toward about 1.6e-5 (center + state + step), with an event term of about 1e-6.

## Re-evaluated comparisons on [0, D2]

The exact family lives on s ∈ [0, D*] ⊂ [0, D2], with u = s/D* ∈ [s_a/D2, min(1, s_b/D1)].

**Replay.**

- Every 256-cell block of each accepted flow is replayed from its checkpoint; block 0 starts from the
  reconstructed fresh state.
- The replay uses the byte-identical inherited engine, with each flow's own native profile passed
  explicitly.
- Each block must reproduce its checkpoint bitwise.
- R2 compares the running maxima of the replayed final state with the inherited RESULT.json bounds.

**Subcells.**

- Each cell with t < D2 is evaluated on 64 equal subcells of its full width h.
- The subcell containing D2 is clipped at D2, and cells with t ≥ D2 are skipped.
- Each subcell [s_a, s_b] is compared with the native hull over [s_a Dn/D2, min(Dn, s_b Dn/D1)].

**Shapes with D'.** For the signed flows, the shapes H0 and H1 in d = C7 + b0 H0 + b1 H1 are evaluated
with D = D'. This is valid because c7, the root boxes and w were all produced with a D box that contains
K, and K contains D*. A and ell do not depend on D, and the flow states are unchanged.

**Decomposition.** At each cell's worst subcell the bound is split into four classes:

- center: |mid difference|;
- state: the state radius at the subcell start;
- comparison step: source step plus native step;
- event: the native hull over [s_a Dn/D2, s_a Dn/D1].

The dominant width is the largest class at the argmax cell.

## Observables (signed flows, both saved degrees; reported, not gated)

**Walls.**

- Lower wall: the exact launch state at s = 0, including the root box a.
- Upper wall: the hull of the state over the event pieces inside D'.
- Compared with the saved wall nodes: A, ell, Phi, rho = A - W = eps psi + w (flow components), the
  clock rate exp(rho) and the log angular radius A - log(k)/2, with k as the certified ball.
- The clock comparison of exp(A - W) against the saved exp(B_N - W_N) uses q(0) = q(D) = 0. That
  premise holds both in the exact wall-preserving gauge and in the saved Hermite q.
- The state enclosures of W, H, E and psi at both walls are also recorded.

**Proper separation.**

- L* = ∫_0^{D*} exp(ell) ds lies in [lo(I), hi(I) + hi(J)].
  - I: subcells below D1, split at D1, each contributing width × exp(range of ell).
  - J: the same construction on [D1, D2], with lower end 0 because the integrand is positive.
- L* is compared with each saved `proper_separation` record.
- The case-0 background has L*_0 = D*. It is compared with the case-0 records.
- |Dn - D*| is reported as well.

## Alternatives (frozen)

**Narrowing.**

- How many pieces are excluded by e_I and how many by e_R.
- The width of D' relative to K.
- Whether D' contains Dn.

**The dominant class of the new A bound:**

- EVENT_WIDTH, meaning the narrowing was weak;
- STATE_RADIUS, the correction root box a plus backreaction, about 5.1e-6;
- COMPARISON_STEP at 64 subcells;
- CENTER_DISCREPANCY.

The same classes are reported for ell, Phi and the mode fields.

## Gates (validity only; no gate is placed on the size of a bound)

| Gate | Condition |
|---|---|
| R1 | Every replayed comparison-stage block (64 per flow) equals its checkpoint bitwise. |
| R1e | Every event-stage replay of all three flows equals its checkpoints, in every job. |
| R2 | The replayed final running maxima equal the inherited RESULT.json bounds exactly. |
| E1 | All three jobs computed an identical D'. |
| E2 | Every flow's surviving set is nonempty. |
| E3 | Dlo ≤ D1 < D2 ≤ Dhi, exactly. |
| B1 | Closure at every evaluated worst subcell (below). |
| C1 | The evaluated subcells tile [0, D2] with no gap, ending exactly at D2. |

B1 closure condition:

    |E - (center + rad_a + rad_b)| ≤ 2^-27 (rad_a + rad_b) + 2^-600 (1 + |mid_a| + |mid_b|)

**Why 2^-27.** It is a priori. Arb radii are 30-bit mag_t values rounded upward, and arb_sub rounds the
radius up twice: once in mag_add and once when it adds the midpoint ulp. That gives a relative excess
below (1 + 2^-29)^2 - 1 < 2^-27.6. The reviewer's synthetic test of 80,000 adversarial subtractions at
768 bits measured a maximum of (1 - 3.4e-54)·2^-28. 2^-27 therefore leaves a margin of 2. The absolute
floor 2^-600 lies far above 2^-767 |mid|.

All decisions are exact rational comparisons of Arb endpoints, at Arb 768 bits. The binary64 columns
are rounded upward and serve only as profiles.

## Classification (frozen order)

1. `ACCEPTED_FLOW_REPLAY_MISMATCH`: an R gate fails. This is technical.
2. `EVENT_EXCLUSION_INCONSISTENT`: an E gate fails, for example when no piece survives. The producer then
   writes `outputs/<flow>/EVENT_INCONSISTENT.json` and assembly reads it. This is a mathematical
   inconsistency between the theorem, the identities and the accepted enclosures. It goes to
   Questions; it is not a physics verdict.
3. `BUDGET_NOT_CLOSED`: a B or C gate fails.
4. `DSTAR_NARROWED__A_DOMINATED_BY_<CLASS>`: all gates pass and D' ≠ K.
5. `DSTAR_NOT_NARROWED__A_DOMINATED_BY_<CLASS>`: all gates pass and D' = K.
6. `UNRESOLVED_VERIFICATION`: see below.

In labels 4 and 5, CLASS is the dominant class of A, or MIXED if the positive and negative flows
disagree. The width ratio |D'|/|K| is part of the record.

## Independent verification and label precedence

`code/verify3.py` imports neither `narrow.py` nor `assemble3.py`. It uses its own drivers over the
shared inherited engine. Every check is an agreement check:

| Check | Requirement |
|---|---|
| VE0 | Its event-stage bitwise flags equal the producer's. |
| VE1 | Its own exclusion record per flow equals the producer's in every field: interval, kept count, e_I and e_R exclusion counts, contiguity, derivative enclosure, monotonicity flag. |
| VE2 | Its common D' agrees. |
| VR1 | Its full replay of all three flows gives all-block bitwise flags equal to the producer's. |
| VR2 | Its replayed final running maxima agree. |
| VB1, VC1 | Closure and coverage agree; closure is checked on sampled cells. |
| VF, VA, VM, VD | In blocks 0, 31 and 63 and every argmax block, every per-cell component is recomputed exactly and must equal the producer's upward-rounded binary64. The argmax components are exact, the column maximum equals the bound, and the dominant class agrees. |
| VL | Its own subcell integration of the separation equals the producer's enclosure exactly. |
| VW | Its own wall bounds for A, ell, Phi, rho, the clock rate and log R equal the producer's exactly. |
| VS0 | The case-0 background bound agrees. |
| VC | The producer's label follows from the producer's gates in the frozen order. |
| VP | A terminal process check. |

The final label is the producer's label, technical labels included, if and only if every agreement check
passes. Otherwise it is `UNRESOLVED_VERIFICATION`.

## Resources and layout

- **Producers.** Three jobs (mode, positive, negative), each an independent process with its own output
  directory. They are launched in parallel through `slot_run.sh` (LINE=02_lin_static, priority 5, cap 3)
  immediately after the freeze.
  - Each job runs one thread, with RLIMIT_AS 3 GiB, a 3,600 s alarm and at least 8 GiB of MemAvailable.
  - Expected time: mode about 7 min, each signed flow about 15–17 min.
- **Assembly.** Runs after all three producers finish.
- **Verifier.** Runs as its own job, which does full replays of all three flows, under a 3,600 s alarm.
  Expected time is about 25 min. If it must start after 2026-10-07T03:03:15Z, it is launched with
  `COMPLETION_OF=<this run>`.
- **No checkpointing.** Every job is under 1 h.
- **Failures.** A failed job writes a failed-closed receipt and is not restarted. A launch refused before
  any outcome may be retried before the backstop.

## Deferred

The following do not fit this round with an honest preflight and an independent check, so none is
claimed. Their designs are in run 20261006T205203Z/CONTRACT.md.

- The gauge completion q*.
- The conformal lapse.
- The coordinate length X*.
- The inverse map, the node positions and the node-level field bounds.

## Gate review record

- **Reviewer:** an independent gate-review agent for the coordinator, not this line's worker.
- **Date:** 2026-10-06, about 23:55Z.
- **Review file:** `ClaudeCode/reviews/02_lin_static_20261006T230904Z_GATE_REVIEW.md`.
- **Verdict:** READY AFTER MUST-FIXES.

Findings and changes (details in GATE_REVIEW_FINDINGS.md):

**Must-fixes**

- **M1** (cross-flow event replays used the job's own profile): fixed before the review. The profile is
  now an explicit argument with no fallback.
- **M2** (the decision and record path had never run): fixed. Every fixture now goes through
  `narrow.produce`, then `assemble3.assemble`, then `verify3.verify`, with records written by
  `common3.atomic`.
  - Required labels: seam and inflated → DSTAR_NARROWED; tamper → ACCEPTED_FLOW_REPLAY_MISMATCH;
    inconsistent → EVENT_EXCLUSION_INCONSISTENT; D' = K → DSTAR_NOT_NARROWED.
  - EVENT_EXCLUSION_INCONSISTENT now has a written record that assembly reads.

**Should-fixes, all adopted**

- The DSTAR_NOT_NARROWED label.
- The label precedence above.
- B1 at 2^-27, with the derivation corrected.
- Verifier time about 25 min; the alarm is now enforced.
- The theorem citation.
- The reviewer's estimate recorded as an expectation.
- The q(wall) = 0 premise stated; clock rate and log R added to VW; wall closed-form containment
  required in the fixtures.
- Unit-level exclusion fixtures where both functions exclude, a sign-flipped e_R that must give no
  survivors, and an inflated-radius fixture where the width is set by the radius, not the piece size.
- The verifier compares exclusion counts and flags.
- R2 is taken from the replayed state.
- A real-entry `check` mode, recorded with no outcome.
- The verifier checks the case-0 bound.

## Claim limits

- These are finite-resolution enclosure statements about the accepted flows.
- D' is rigorous given the theorem and the junction identities.
- No exact-map, lapse or evolution certificate follows.
- The zero-case metric correction is still not separately validated.
- The old raw-coefficient failure stays failed.
