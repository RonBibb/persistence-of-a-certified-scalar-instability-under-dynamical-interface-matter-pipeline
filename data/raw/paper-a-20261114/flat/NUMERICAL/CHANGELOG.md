# NUMERICAL change log (float exploratory)

Entries are timestamped with `date -u` at write time.

## Pre-freeze design changes (no numerical execution had occurred)

2026-11-14T06:21Z. These changes were made while the gate reviewer was reading PLAN draft v1. They are motivated analytically, not by data.

1. **F3 and F0 use H_a = +√(…) (damping branch), and F3 uses V = 5.5 − 10Φ².**
   - With H_a < 0, the anti-friction term −4HT in T′ grows the scalar amplitude. That raises |H| through the constraint H² = 1 + T²/12 − V/6, which feeds back and gives a finite-distance blow-up of the background. This was estimated by hand for draft v1's F3 (V = −10Φ², H_a < 0): the amplitude grows by about e^{3.9} before D.
   - With V₀ = 5.5, H² ≥ 1 − V₀/6 > 0 along the whole orbit, so H cannot change sign. With H_a > 0, H only damps the oscillation.
   - F1 keeps H_a < 0 and F1b keeps H_a > 0. Both signs of H stay covered (the theorem needs no sign of H).
2. **Steps N = 2000/4000 instead of 4000/8000.** h = D/2000 ≤ 10⁻³ for D ≤ 2. RK4 local error is about (h√|μ_min|)⁵/120, below 10⁻¹⁰ for the expected |μ_min| ≤ 400. This roughly halves the cost and stays within the PLAN floor check (h ≤ 1.5·10⁻³).
3. **Nested grid for G5.** The M1 second count uses the 2M − 1 grid that contains the M grid, so only midpoints are new evaluations. This is equivalent in strength to "M = 800", at half the cost.
4. **G6 first-step rule.** Near μ_top = −10⁻⁶ the phase rotates inside a boundary layer of width O(|λ|), far below one step. The first-step jump can therefore approach π/2–0.9π, even though it is a single monotone rotation along an almost straight segment (audit A9 step 3). The rule becomes: per-step |Δθ| < π/4 for steps 2…N, and first-step |Δθ| < π − 0.01, which is the unwrap-unambiguity condition.
5. **G8 quadrant rule.** When Ẽ_a < 0 (F0 cases with a Dirichlet or B₁ > 0 lower wall), the K4 launch for λ < 0 lies in the closed third quadrant. The cooperative argument then keeps the trajectory in the open third quadrant. G8 is restated as f·L > 0 for s > 0 and θ_b(μ_min) mod π ∈ (0, π/2), which covers both cases.

## Post-freeze fix 1 (allowed by PLAN v2 §8: an implementation-flag failure, not a prediction outcome)

2026-11-14T06:52:30Z (`date -u`).

- **Trigger.** Run 1 (flatcount.py SHA-256 ca75a9a3…a7b, frozen) had every count equal to n, and every prediction and control met. But G6 (per-step abs(Δθ) < π/2 for steps ≥ 2) failed at the F1 pairs with t_a = 0, the F1b pairs with t_a ∈ {0.1, 0}, and the F3 pairs with t_a ∈ {0.1, 0}. The run-1 class under the frozen rules is AMBIGUOUS.
- **Diagnosis.** `run1/diag_g6_diag.py`: the failures sit at intermediate λ (about −2·10⁻⁴ to −3·10⁻³). There the near-wall boundary-layer rotation, up to about 2.9 rad for t_a near 0, is split across two RK4 steps, giving 1.57–2.04 rad in step 2. Every jump is below π, so the unwrap was unambiguous.
- **Fix** (flatcount.py SHA-256 754bcf7c…5e72). When a step's direct increment is at least π/4, that step's phase path is re-sampled by recursive halving, down to h/2¹², using RK4 with a background refined locally from the stored grid point. The refined increments are summed for θ, and G6 is evaluated on them.
  - The state used for 𝒟, 𝒟′ and the constraint is unchanged, so M1, M1′, roots and G3 are bit-identical to run 1. Only phase-derived quantities (M2, G6, G9, G12, G13) can change.
  - No gate, threshold, parameter or prediction changed.
- **Redacted dry run of the fix:** `run2/diag_g6_fix_dry.py`, on the previously failing pairs F1 (0,0), F1b (0.1,1), F3 (0,0) and F3 (0.1,1). Results: zero G6 failures; maximum refined increment 0.78 rad; maximum refined-versus-direct discrepancy 2·10⁻¹¹. The run-1 unwraps were therefore already correct.
- **Rule compliance.** All five cases are rerun as run 2, and both runs are reported.

## Clarification

2026-11-14T06:52:43Z. Pre-freeze entry 4 above records the draft rule (steps ≥ 2 below π/4). The frozen PLAN v2 adopted the reviewer's π/2 for steps ≥ 2, plus the half-plane first-step conditions. PLAN v2 §6 G6 is authoritative.

## Stretch goal: certified background, attempt 1 failed; technical fix for attempt 2

2026-11-14T07:06:09Z. These rules are PLAN v2 §10 (optional; outside the float gates).

- **Attempt 1** (certify_flat_background.py SHA-256 df7646bd…61b8; job CERT_FLAT, 07:03:45–07:03:47Z): exit 1, PICARD_FAIL. Diagnosis (`stretch/diag_cert_diag.py`): the failure is at cell 1373 (s ≈ 0.1676), at the scalar turn (T ≈ −4.6·10⁻⁴). There H′ = −T²/3 vanishes because k = 0. Ball arithmetic encloses T·T for a ball straddling 0 with a negative lower bound, so the H image grows with every padding iteration and the whole-cell box never self-contains. In the archived de Sitter certificate, the −kE² term dominated H′, which masked this.
- **Fix:** in the Picard right-hand side only, T² is enclosed from exact rational bounds (`sq_tight`). The result is rigorous and tight, with lower bound 0 when the ball straddles 0. Nothing else changed. Attempt 2 writes to `flat_certificate_attempt2/`; attempt 1's FAILURE.json is kept.
- **2026-11-14T07:07:07Z, attempt 2** (SHA-256 6e7b3c3a…7253; job CERT_FLAT_2, 07:06:10–07:06:12Z): still PICARD_FAIL at cell 1373. The archived loop pads all components every iteration, so the T box inflates by about 1.25× per iteration and the H image (∝ max T² over the T box) by about 1.5×. The H box cannot keep up. **Attempt 3** grows only the components that are not yet strictly contained. Acceptance still requires the (N5) whole-cell inclusion for every component of one common box. This is the final attempt under the stretch-goal time cap.
- **Attempt 3 result** (logged 2026-11-14T07:10:22Z). SHA-256 e990ccf8…8b9c; job CERT_FLAT_3, 07:07:08–07:07:18Z; exit 0; status COMPLETE; every predicate true. T(3/4) ∈ [55.934031, 55.934032]; T′(3/4) ∈ [3602.850, 3602.851]; the hull of T′ over [0, 3/4] has lower bound 2.3409. Exact copies of the attempt-1 and attempt-2 sources were reconstructed and hash-verified (df7646bd…, 6e7b3c3a…), and are kept in `src/superseded/`.
