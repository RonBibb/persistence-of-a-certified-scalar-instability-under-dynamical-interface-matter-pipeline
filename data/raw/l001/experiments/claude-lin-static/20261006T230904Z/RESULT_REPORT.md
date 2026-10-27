# The upper-wall position is now located to 1.3e-6; A's rigorous bound falls 25-fold to 7.8e-6

Run `20261006T230904Z`, line 02 Lin static. Gate-reviewed, then frozen at 2026-10-07T00:52:34Z
(guard `dcd2f39d3420224b4a7f0fef493f4e9dbdfca813cb8fd8685332b8cdd433b25e`).

**Classification:** `DSTAR_NARROWED__A_DOMINATED_BY_STATE_RADIUS`. The producer passes 28 of 28 gates.
The independent verifier resolved it, with all 77 agreement checks passing, and confirms the label. The contract and its gate-review record
are in [CONTRACT.md](CONTRACT.md) and [GATE_REVIEW_FINDINGS.md](GATE_REVIEW_FINDINGS.md).

## Success and gap movement

**Where the upper wall sits.** I used the inherited theorem (D* lies in K and is a zero of both upper-wall
junction residuals) together with the accepted validated background models of the last two cells.
Subintervals of K where either residual is certainly nonzero were excluded.

- The certified interval narrows from width 1.22e-4 to D' = [33513605/16777216, 67027255/33554432],
  that is [1.9975665212, 1.9975678623], width 1.341e-6, or 1.1% of K.
- All three flows give the same 45 surviving subintervals, and the survivors are contiguous.
- The Israel condition excluded 4051 of the 4096 subintervals; the scalar Robin condition excluded 1830.
- The Israel residual is strictly monotone on K, with derivative between -0.017906 and -0.017901, so its
  zero there is unique.
- This matches the reviewer's prior estimate (slope -kE² ≈ -0.018, about 44 pieces).
- D' contains the native wall Dn, and |Dn - D*| ≤ 7.58e-7 is now proved.

**Material bounds.** Re-evaluated on [0, D2] with 64 subcells and with every replayed block checked
bitwise:

| Field | Accepted | Run 2 (16 subcells) | Now (positive / negative) |
|---|---:|---:|---:|
| A | 1.99e-4 | 8.3e-5 | 7.81e-6 / 7.82e-6 |
| ell | 2.30e-7 | 1.03e-7 | 2.08e-8 |
| Phi | 7.8e-5 | 7.5e-5 | 7.39e-5 / 7.49e-5 |

- A is now 25 times below the accepted value. Its budget at the argmax cell (16363):

  | Component | Value | Share |
  |---|---:|---:|
  | State radius (the correction root box a carried by w) | 5.1e-6 | 66% |
  | Comparison step | 1.9e-6 | 25% |
  | Event width | 6.8e-7 | 8.7% |
  | Center discrepancy | 8.7e-8 | 1.1% |

  The 8.7e-6 center term of run 2 was an artifact of where the D interval sat, and it has gone.
- ell is limited by eps × the psi radius, which comes from the mu bracket.
- Phi is still about 94% state radius (7.07e-5). The radius sits in the prepared scalar correction d,
  whose C7 coefficients were built with the wide D box. Evaluating its shapes with D' changes little.

**Mode fields.**

| Field | Accepted | Now |
|---|---:|---:|
| psi | 2.30e-2 | 2.08e-3 |
| W | 1.94e-4 | 2.69e-6 |
| H | 3.47e-6 | 5.6e-8 |

f and g (2.06 and 8.50) are still set by the mu bracket.

**Initial observables.** Bounds against the saved grids, the same for N = 160 and 192:

- **Lower wall.**
  - A, the radius perturbation rho = A - W, the clock rate and log R are each about 3.27e-6. Every one is
    the root-box radius of the correction coordinate a.
  - Phi 1.2e-9; ell 1e-236.
  - Since eps = 5e-6, the certified initial radius perturbation at this wall is known only to about ±65%
    of eps.
- **Upper wall.**
  - A 5.9e-6, rho 5.1e-6, clock 5.1e-6, log R 5.9e-6, ell 1.9e-8. These are again dominated by w's root
    box.
  - Phi 7.4e-5, from d.
- **Proper separation.**
  - Signed cases: |L* - L_saved| ≤ 7.6e-7, set by the narrowed wall interval.
  - Background: L*₀ = D*, so the saved case-0 separation is certified to within 7.58e-7.

## Issues

- **Propagation not performed.** The gauge completion, the conformal lapse, the inverse map and the
  node-level bounds were deferred as contracted. None is claimed.
- **Remaining limits.** A is now limited by the correction root boxes (a, b0, b1), whose images are loose
  relative to the coefficients. Phi is limited by the C7 enclosure built with the old D box. Tightening
  either needs a new validated flow or root iteration with the narrowed D'. That would be a new contract,
  not an evaluation of existing enclosures.
- **Shared engine.** The verifier uses its own drivers over the same inherited validated engine, and this
  is disclosed.
- **The old failure stands.** The 1e-50 raw-coefficient failure stays failed and was not rescored.
- **Process lesson.** During drafting, a wait loop matched its own command line and hid a verifier crash
  for about 28 minutes. That crash was a Fraction/fmpq comparison, which is now fixed. Each fix was
  followed by a full preflight before the freeze.

## Next steps

For a later window:

1. Freeze a narrowed-D' re-preparation of the C7 and root-box enclosures, which is the dominant width for
   both A and Phi.
2. Then run the deferred lapse, inverse-map and node propagation.

## Viability

Continue. The wall-position width is resolved. What remains is set by the correction-coefficient
enclosures.

## Evidence class

Rigorous enclosure results:

- 768-bit Arb;
- an exclusion argument resting on the certified theorem and the junction identities;
- exact rational decisions;
- every block of the accepted flows replayed bitwise;
- an independent agreement verifier.

Finite-resolution; not a continuum or evolution certificate.

## Verification

`verify3.py` resolved the run: 77 of 77 agreement checks passed, in 821 s (slot 5, PID 575711). It used
its own drivers over the shared inherited engine. The checks covered:

- its own event replay and exclusion for every flow, which matched the producer's records in every field:
  the interval, the keep count, the e_I and e_R exclusion counts, contiguity and the derivative
  enclosure;
- its own full replays of all three flows, with block flags and running maxima agreeing;
- exact recomputation of every component in the sampled and argmax blocks: 62,916 values, all equal to the
  producer's upward-rounded binary64;
- the separation enclosures, equal exactly;
- the wall bounds for all six quantities;
- the case-0 bound;
- the frozen-order label;
- the terminal process check.

## Execution

| Job | Started | Slot |
|---|---|---|
| Producer, positive | 00:52:41Z | 3 |
| Producer, negative | 00:53:01Z | 5 |
| Producer, mode | 01:01:02Z | 1 |
| Assembly | 01:08:48Z | — |
| Verifier | 01:08:51Z | 5 |

- The producers were launched through slot_run.sh with LINE=02_lin_static, each about 7–16 min, and all
  had finished by 01:08:40Z.
- Every job ran on one thread with a 3 GiB address-space limit.
- 227 inputs are bound by hash; the 222 that are not manifest files each match their predecessor manifest.
- No new flow, no change to any parameter, no time evolution.

## Artifacts

- Run records: `CONTRACT.md`, `GATE_REVIEW_REQUEST.md`, `GATE_REVIEW_FINDINGS.md`, `FREEZE.json`.
- Final preflight: `preflight/20261007T004145Z/PREFLIGHT.json` (synthetic only), plus
  `preflight/REAL_ENTRY_CHECK_positive.json` (no outcome).
- Producer outputs: `outputs/{mode,positive,negative}/SUMMARY.json` and `CELLS.f64`, and
  `outputs/PRODUCER_RESULT.json`.
- Verification: `verification/VERIFICATION.json`.
- Logs: `logs/`.
- Seal: `FINAL_PROCESS_CHECK.json`, `MANIFEST.json`.
