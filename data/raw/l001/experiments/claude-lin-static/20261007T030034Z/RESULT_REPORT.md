# Result: narrowed-D' re-preparation (line 02, run 20261007T030034Z)

**Validity label: `REPREPARED__A_DOMINATED_BY_STATE_RADIUS__PHI_DOMINATED_BY_STATE_RADIUS`.**

The independent verifier resolved it with 78 of 78 agreement checks (VERIFICATION.json). All phase and
material blocks were replayed bitwise, and the exact rational Krawczyk box lies inside the producer's box.

**Side records**, outside the validity order:

- **Registered prediction:** `NEAR_NULL_CONFIRMED`, all 37 rows confirmed (PREDICTION.json).
- **Attribution:** `NEXT_WIDTH__MODE_JET_RADIUS__MU_BRACKET__A_CARRIED_BY_A_BOX__A_NEXT_WIDTH_UNDECIDED`
  (ATTRIBUTION.json).

SIDE_The independent verifier resolved it with 78 of 78 agreement checks (VERIFICATION.json). All phase and
material blocks were replayed bitwise, and the exact rational Krawczyk box lies inside the producer's box.

## Timeline and process

- Two gate reviews: READY AFTER MUST-FIXES at about 04:20Z, then APPROVED AFTER FIXES at about 04:55Z, with
  F1 applied.
- Final dry runs, all with the final sources:
  - preflight `20261007T045713Z`, 23 of 23 expectations;
  - `REAL_CONTROLS_CHECK_8` (producer) and `VERIFIER_CONTROLS_CHECK_3` (verifier), all controls passing
    and no outcomes computed.
- Frozen at 05:04:01Z (guard c7ed0eee…), with 355 inputs, 349 of them matched to their predecessor
  manifests.
- `campaign.sh` launched at 05:04:05Z.
  - The four phases completed by 05:18:27Z.
  - Both material jobs started at 05:18:27Z, before the 06:53:30Z backstop, and completed at 05:35:53Z.
  - Assembly finished at 05:39:15Z, then the verifiers ran.
- Every wait used recorded PIDs. No job exceeded 1 h.
- All stage-A controls passed in production in all six jobs (R0, R0m for both amplitudes, R0j, R0p, D0),
  and all 61 producer gates passed.

## What D' changed (K → D'; positive amplitude, negative within 0.1%)

| Quantity | K (accepted) | D' (this run) | Ratio |
|---|---:|---:|---:|
| Upper-wall source radius, W | 6.16e-5 | 6.77e-7 | 0.011 |
| Upper-wall source radius, psi | 8.32e-3 | 1.65e-3 | 0.20 |
| Upper-wall source radius, f | 1.323 | 1.323 | 1.000 |
| Upper-wall source radius, g | 5.472 | 5.470 | 1.000 |
| c7, largest coefficient radius | 7.498e-7 | 7.489e-7 | 0.9988 |
| Q_c7 = Σ rad(c7_n) D2^n | 6.316e-5 | 6.308e-5 | 0.9987 |
| rad W0 / rad W1 | 4.072e-4 / 9.317e-3 | 4.067e-4 / 9.305e-3 | 0.9988 / 0.9987 |
| rad G(c), a / b0 / b1 | 2.960e-6 / 4.072e-4 / 9.318e-3 | 2.956e-6 / 4.067e-4 / 9.305e-3 | 0.998–0.999 |
| Root width a | 6.530e-6 (X); 6.200e-6 (K-only step X'_K) | 6.178e-6 | 0.946 of X; 0.9963 of X'_K |
| Root width b0 | 8.144e-4 | 8.134e-4 | 0.9988 |
| Root width b1 | 1.864e-2 | 1.861e-2 | 0.9987 |

**Reading the root widths.**

- The Krawczyk step is strictly inside X, with weighted row norms 1.6e-3, 3.8e-11 and 6.2e-7.
- The a box gains 5.4%. The K-only Krawczyk null shows that 5.0% of this comes from the iteration itself,
  which drops the radius-0.1 contraction terms. D' adds only 0.37%.

## Material bounds on [0, D2] (64 subcells; every cell)

| Bound | Run 3 | This run | Ratio | Dominant |
|---|---:|---:|---:|---|
| A (positive) | 7.805e-6 | 7.585e-6 | 0.972 | STATE_RADIUS (65%) |
| A (negative) | 7.819e-6 | 7.594e-6 | 0.971 | STATE_RADIUS (65%) |
| ell | 2.075e-8 | 2.075e-8 | 1.000 | STATE_RADIUS |
| Phi (positive) | 7.385e-5 | 7.377e-5 | 0.9989 | STATE_RADIUS (96%) |
| Phi (negative) | 7.490e-5 | 7.482e-5 | 0.9989 | STATE_RADIUS (94%) |

**Radius split at the argmax** (cell 16363).

- rad d = 6.31e-5, entirely its c7 part; the root-box part is 1e-29.
- rad w = 4.89e-6.
- eps rad f = 6.6e-6.

**Walls and separation** (N = 160; N = 192 is the same to the digits shown).

- Upper wall: A 5.66e-6 (was 5.88e-6), Phi 7.37e-5, rho, clock rate and log R about 4.9e-6 to 5.7e-6.
- Lower wall: A, rho, clock rate and log R about 3.09e-6, which is the new a box. Phi 1.2e-9.
- Proper separation: 7.62e-7, unchanged. It is set by D'.

## Attribution (gated; D' preparation)

| Quantity | ρ_F | ρ_S | ρ_B | ρ_Z | ρ_D | ρ_ALL | ρ_mu |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q_c7 | 1.90e-4 | 0.99989 | 0.99988 | 1 (structural) | 0.99998 | 1.2e-22 | 3.81e-4 |
| Q_W0 | 1.87e-4 | 0.99989 | 0.99988 | 1 | 0.99998 | 1.2e-22 | 3.77e-4 |
| Q_W1 | 2.10e-4 | 0.99987 | 0.99986 | 1 | 0.99998 | 7.4e-22 | 3.97e-4 |

Both amplitudes are identical to the digits shown. The K preparation is also DECISIVE_F, with ρ_F of about
7.6e-4 and ρ_D of about 0.9986.

**Group Z** (H, T, qbg) is a structural no-op, ρ_Z ≡ 1, and is not evidence.

**What carries the radius.**

- The f jets carry more than 99.98% of the c7 and W radius.
- With mu at the midpoint of its bracket, more than 99.96% of it disappears.
- **The mu bracket (width 1e-5) carries d, and through W it carries the b0 and b1 boxes. D' was never
  binding.**

**A split.** These are linear parts of rad w at the upper wall: an argmax, so all four are quoted.

| Part | Positive | Negative |
|---|---:|---:|
| a box: \|u_a\| rad X'_a | 2.366e-6 | 2.367e-6 |
| point part: center-phase rad w | 6.33e-7 | 6.34e-7 |
| b1 box | 2.35e-9 | 2.35e-9 |
| b0 box | 1.1e-10 | 1.1e-10 |

The a box carries A. Its width is G_a, the point radius of v at the wall, which `prepare` never sees. So
this run leaves A's next width undecided, and the label says so.

## Registered prediction: confirmed

All 37 rows are confirmed. The values for each amplitude:

- P1: 0.99873.
- P2: 0.99879 and 0.99866.
- P3: 0.99847, 0.99879 and 0.99866.
- P4: 0.99633 (0.99640), 0.99879 and 0.99866.
- P5: 0.9461 (0.9448).
- P6: 0.9719 (0.9712), STATE_RADIUS.
- P7: 0.99892 (0.99893), STATE_RADIUS.
- P8: every ρ_F ≤ 8.1e-4 and every ρ_D ≥ 0.99855.
- P9: the label.

## Next step

**Narrow the mu bracket**, the eigenvalue enclosure of width 1e-5. This is the attributed width. It carries
c7, and so Phi's d, and it carries W, and so the b0 and b1 boxes. For A, the a box's width (G_a, the point
radius of v at the wall) is not decided by this run. A point-mu or narrowed-mu flow should report it
together with c7.

**Not claimed:**

- the lapse, the inverse map and the node propagation, which stay deferred;
- any continuum or evolution certificate.

The historical 1e-50 failure and run 3 stay as recorded; nothing was rescored.
