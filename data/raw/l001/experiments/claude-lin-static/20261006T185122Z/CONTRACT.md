# Deterministic knot selection for the D1 conformal-grid replay (line 02, run 20261006T185122Z)

## Question and alternatives

The predecessor identity packet `lin-c4-evolution-identity-r1-20261006T051000Z` replayed the six
saved conformal grids of the certified D1 family: cases 0, +5e-6 and -5e-6, at degrees 160 and 192.

- Its case-0 replay at 100 decimal digits failed the frozen 1e-50 raw coordinate-map
  coefficient gate.
- The diagnostic traced the failure to `Dense.locate`. The native polynomial piece used at map
  knot i is `floor(fl(i*h)/h)`. In floating point this picks piece i-1 at some knots and piece
  i at others, and the knots differ between 80 and 100 digits.
- The signed replays and the signed root-bound comparison never ran.

**Question.** Once the native piece is fixed by an explicit integer table at every knot:

1. Are like representations of the saved maps identical to 1e-50 across 80 and 100 digits?
2. Is the choice of piece at knots immaterial in value and Jacobian?
3. Do the signed grids pass the same replay?

**Alternatives this test discriminates:**

- **H0, representation ambiguity only.** With explicit selection, every like-representation
  comparison passes the unchanged 1e-50 raw gates. The old and revised maps differ by at most
  1e-50 in the whole-cell value and Jacobian norms.
- **H1, other precision sensitivity.** The gauge, Newton inversion, exponential series or
  accumulation is sensitive beyond 1e-50, so a like representation fails.
- **H2, material representation choice.** The native pieces disagree at knots strongly enough
  that the old and revised maps differ by more than 1e-50 in value or Jacobian.
- **H3, signed failure.** A signed grid fails a check that the zero case passes.

## Reproduction versus revision

**Reproducing the old saved map (rule `old80`).**

- The table is the piece the predecessor producer actually used: `clamp(floor(fl(fl(i*h)/h)))`.
- It is evaluated by the reference producer's own `locate` at mpmath dps 80 (269 bits), with h
  parsed from the SEED string at that precision.
- The table depends only on h and the precision, so it is the same for every case.
- The map built from this table at dps 80 and at dps 100 must reproduce the saved grid map.
- The local offset keeps the producer's expression `z = i*h - p*h`. At p = i-1 this is the
  floating value close to h.

**Constructing a revised map (rule `canonical`).**

- Map cell i is built from native piece i at offset z = 0, exactly.
- That piece is the one the native Taylor integrator generated at knot i, and it covers the cell
  on which the map polynomial is used. So no piece is extrapolated outside its own cell.
- The selection is integer-valued and independent of precision.
- Everything else is inherited unchanged: degree-28 jets, the truncated exponential series, the
  integration, knot accumulation with width h in every cell, and the gauge polynomial q.
- The revised map is a new representation. It is not the saved map, and the saved grids are not
  regenerated from it.

**Diagnostic only (rule `floor_at_p`).** This is the original floor rule at the running
precision. At dps 80 it equals `old80`. At dps 100 it reproduces the historical failure
mechanism.

The six saved grids remain the authoritative evolution inputs. No grid is rewritten.

## Knot convention and evaluation rules

**Pieces and knots.**

- Native pieces k = 0..255 cover [k h, (k+1) h]. Here h, D and the coefficients are the exact
  decimals of SEED.json and case_*.dense.json.
- Knots 1..255 are shared between two pieces.
- Knot 0 is the lower wall, in piece 0.
- The upper wall is s = D, not 256 h. In the stored decimals D - 256 h = -3.2e-91. The wall lies
  in piece 255, at offset D - 255 h.

**Selection rules.**

- At a map knot, the piece comes from the table. No floating division is involved.
- At a general material point s, the piece is `floor(s/h)` in exact rational arithmetic, clamped
  to [0, 255]. Here s is taken as the exact binary value of its mpf and h as its exact decimal.
- **Ambiguous points.** If s lies within 1e-40 of a shared knot j, the point is flagged.
  - It is evaluated on both adjacent pieces.
  - The reported value uses piece j.
  - The two evaluations must agree to 1e-50.
  - The same rule applies to inverse-map cells: an x within 1e-40 of a shared map knot is
    inverted in both cells.

**Why the margin is 1e-40.** It is far above the largest expected cross-precision or
cross-representation position change (below 1e-60), so any point whose selection could move is
flagged. It is also far below h and the node spacing, so generic nodes are not flagged.

## Fixed inputs, test points and precisions

**Inputs:**

- **Native.** `01-horizon-core/d1-native-cauchy-20261005T201829Z/results/fine_c4/`:
  SEED.json and the case_0, case_3 and case_4 dense files.
- **Saved grids.** `01-horizon-core/d1-spatial-evolution-20261005T232000Z/inputs/fine_c4_case{0,3,4}_N{160,192}_p80.*`.
- **Reference producer.** Byte-identical copies of `d1-evolution-admission-20261005T214600Z/code/producer.py`
  (SHA-256 755be5dc...) and `jet.py` (1c45d7bf...).
- **Binding.** Every input is bound in FREEZE.json by SHA-256. The freeze refuses any input,
  other than a packet's own MANIFEST.json, that its predecessor manifest does not list with the
  same hash.

**Cases and amplitudes:**

- Case 0 at epsilon 0.
- Case 3 at the saved epsilon 4.99...96651514e-6 (target +1/200000).
- Case 4 at the same magnitude with negative sign (target -1/200000).
- The exact offsets from the targets are recorded. Both signed amplitudes lie inside the certified
  interval, and no other amplitude is used.

**Test points:**

- All 256 native cells and all 257 knots.
- Every saved node: 161 and 193 per grid.
- Both walls, s = 0 and s = D.

**Precisions:**

- mpmath dps 80 and dps 100 (269 and 336 bits), the precisions of the frozen predecessor graph.
- The verifier adds an exact-input reference in 768-bit outward Arb. It also emulates the
  floating knot rules exactly in rational arithmetic at 269 and 336 bits.
- Floor tables at 53 and 113 bits are reported as diagnostics only.

**Evaluation precision of comparisons:**

- **Exact.** Map coefficients, knots and X are compared exactly: the mpf binary values as exact
  rationals against the saved decimal strings as exact rationals. The whole-cell bounds are exact
  rational sums.
- **Producer, node-level.** Field, position, gauge and clock values are differenced in the
  producer's own p-digit arithmetic, where rounding stays below 1e-78. The resulting difference
  is then compared exactly with the gate.
- **Verifier.** It re-evaluates the same node quantities as 768-bit Arb enclosures against the
  exact stored decimals, and uses rigorous upper bounds.

## Decision norms

**The historical raw-coefficient failure is retained.**

- The predecessor compared a 100-digit floor-rule map against the 80-digit saved map.
- Under its contract that comparison is the frozen 1e-50 raw gate, and it failed: 1.144e-10 at
  cell 208, power 29.
- This contract does not rescore that record, and it does not rerun the old graph.

**Like representations** (same table, same expansion point, same truncation) are compared
coefficient by coefficient. The unchanged absolute 1e-50 gate applies to:

- every raw coefficient, knot and the length X;
- every gauge coefficient;
- every saved-position field, inverse position and reconstructed field.

Each such quantity is the same mathematical object computed at another precision.

**Unlike representations** (canonical against saved, where the two tables differ) are not judged
on raw coefficients.

- On a cell of width h, the power-j coefficient enters every value it produces weighted by h^j.
  At j = 29, h^-29 is about 1e61. A raw comparison therefore measures the polynomial far outside
  the cell, where it is never evaluated.
- The operational norms are whole-cell bounds over the closed cell [0, w_i], where w_i = h and
  w_255 = D - 255h:
  - Map value: V_i = |dK_i| + sum_j |dc_ij| w_i^j, which bounds sup |dx_i|.
  - Jacobian: J_i = sum_j j |dc_ij| w_i^(j-1), which bounds sup |dx_i'|.
- Gates:
  - max V at most 1e-50;
  - max J at most 1e-50;
  - the canonical inverse positions and reconstructed fields at every saved node at most 1e-50.
- The raw differences are reported, but they are not gated.
- The threshold is the historical representation allowance, unchanged. Map values are O(1-7), so
  it is also a relative bound of about 1e-51.

**Monotonic maps.** A rigorous Arb lower bound of x' > 0 is required on every closed cell of the
saved, old80 and canonical maps, and the knots must increase strictly.

## Gate table

Each gate ID carries its case (c), precision (p) and degree (N) where those apply.

**R — reproduction of the old saved map (rule `old80`)**

- R1: raw coefficients against the saved map.
- R2: knots and length X.
- R3: inverse of the saved x against the saved s.
- R4: fields at the reconstructed s.

**S — saved-grid replay, independent of the map**

- S1: fields (A, B, Phi, ell) and the eight seed rows at the saved s, with the saved q.
- S2: recomputed q against the saved q.
- S3: structure. Audit bound to the grid hash, zero velocities and Cauchy constants, and
  dimensions.
- S4: the saved map is identical for N = 160 and N = 192.

**C — canonical like representation across precisions**

- C1: canonical map at 80 against 100 digits.
- C2: old80 map at 80 against 100 digits.
- Cx: reconstructed positions at 80 against 100 digits.
- C3: canonical and old80 rows differ only on cells where the tables differ.

**U — unlike representation, canonical against saved**

- U1: V bound.
- U2: J bound.
- U3: canonical inverse positions and reconstructed fields.

**M — monotone maps**

- M1: monotonicity of each map.

**W — wall traces**

- W1: q, q' and q'' vanish at both walls. B - A at the wall nodes is at most 1e-50. s_0 = 0,
  x_0 = 0, |s_N - D| is at most 1e-50, and x_N = X.
- W2: the normalized proper clock rates exp(B - W) agree across precisions to 1e-50. The
  orientations are recorded with sigma = +1 below and -1 above; this is a convention.
- W3: x(0) = 0, |X - x_255(D - 255h)| is at most 1e-50, and inverting the saved upper-wall x
  returns D to 1e-50.
- W4: the wall Jacobians match exp(ell - B) at the walls, to 1e-50.

**E — original-equation controls**

- E1: the wall rows from the inherited gauge construction (Israel and scalar Robin, time orders
  0, 2 and 4) are finite and strictly below the inherited producer thresholds: below 1e-10 for
  orders 0 and 2, and below 1e-12 for order 4.
- E1x: those rows and q agree across precisions to 1e-50.
- E2: the represented Jacobian satisfies the defining pullback x_s = exp(ell - B) at every saved
  node, to 1e-50.
- E3: the inherited original-equation admission receipts of the six grids are authenticated
  unchanged and passing.
  - Each grid must carry these GRID_ADMISSION families: Hamiltonian; momentum; strong and weak
    wall orders 0, 2 and 4; and inverse map derivative.
  - The admission and spatial VERIFICATION flags are included too.
  - These receipts stay applicable because the saved grids are unchanged.

**A — ambiguous knots**

- A1: every flagged evaluation agrees across both pieces or cells, to 1e-50.
- A2: the selection tables are valid. Each entry is i-1 or i, the 80-digit floor table equals
  old80, and the tables match the verifier's emulation.

**I — implementation controls (producer only)**

- I1: the explicit floor-rule map is bitwise identical to the reference `make_map`.
- I2: at 80 digits, the old80 map is bitwise identical to the reference.
- I3: the gauge is bitwise identical to the reference. It is trivial because the gauge is
  inherited.
- I4: explicit inversion is bitwise identical to the reference `invert` on unambiguous nodes.

**H — historical detector control**

- H1: the floor rule at 100 digits still exceeds the raw gate for case 0, N = 160, and only on
  precision-switched cells.

**G — signed root bounds (the comparison that never ran)**

- G1: port of the predecessor's `correction_bounds()` in exact rationals.
  - The saved numerical centers (A0 - epsilon, b0, b1) of cases 3 and 4 equal the certified
    sample centers.
  - The independent translated root images are fresh.
  - The images lie strictly inside the common uniqueness box (1e-5, 0.1, 0.1).
  - The distances from the centers are recorded. They are coefficient bounds, not field bounds.

**X — verifier-only scientific gates, filed under the hypothesis group they test**

- XR1 and XC1: the producer's old80 and canonical maps equal the exact-input reference to 1e-50.
- XR2: the saved map equals the exact old80 reference.
- XU1: Horner sup enclosures and triangle bounds for saved against exact canonical, value and
  Jacobian.
- XM1: the exact canonical reference is monotone.
- XR3 and XU2: forward maps at the saved s reproduce the saved x.
- XW1: the saved map's end trace.
- XS1: the saved amplitude lies in the certified interval.
- XH1: the floor-rule failure reproduces the predecessor diagnostic exactly: 17 cells, maximum
  1.144e-10 at cell 208, and the recorded selections.

**Reused accepted work**

- The three accepted spatial flows (mode, positive, negative) and SPATIAL_ENCLOSURES.json are
  bound by hash and reused, not rerun.
- Their applicability is unchanged. They select segments by exact rational intersection,
  including both pieces at a knot, and they never build the conformal map.

## Classification (frozen)

1. `DETERMINISTIC_KNOT_REPRESENTATION_ADMITTED__HISTORICAL_RAW_GATE_RETAINED_FAILED`: every
   decision gate passes.
2. Otherwise, the first rule that matches decides:
   - `IMPLEMENTATION_OR_HISTORICAL_CONTROL_FAILED`: an I or H gate fails.
   - `SIGNED_REPLAY_FAILED`: every failing gate belongs to case 3 or case 4 and to groups
     R, S, C, U, M, W, E or A.
   - `SAVED_MAP_NOT_REPRODUCED`: an R or S gate fails.
   - `CANONICAL_REPRESENTATION_PRECISION_DEPENDENT`: a C gate fails.
   - `REPRESENTATION_CHOICE_MATERIAL`: a U gate fails.
   - `SIGNED_ROOT_BOUND_FAILED`: a G gate fails.
   - `REPRESENTATION_ADMISSION_FAILED_<groups>`: anything else.

## Independent verification and the final decision

`code/verify.py` imports no producer, representation or reference code. Its work:

- **Knot tables.** It derives the tables by exact round-to-nearest-even emulation.
- **Exact-input maps.** It rebuilds them for both tables in 768-bit Arb from the bound decimals,
  once with the saved gauge and once with each producer gauge.
- **Saved grids.** It evaluates every saved grid against the exact decimals: fields, forward maps
  at the saved s, fields at the producer's reconstructed positions, the Jacobian identity, walls,
  and dual evaluations at flagged points.
- **Reconstructed positions.** It checks them by forward evaluation. It does not repeat the Newton
  inversion.
- **Wall rows (E1, E1x).** It re-thresholds the producer's exact values. It does not reimplement
  the inherited time-derivative construction.
- **Other records.** It recomputes the root bounds and the receipts.

It produces three kinds of record:

1. **Shared gates.** These carry the producer's IDs and are recomputed independently.
2. **Verifier-only X gates.**
3. **Integrity checks, group V.** These cover agreement on every shared gate flag, the tables, the
   gauge and root records, the clock enclosures, the forward consistency of the producer's
   inverse positions, the ambiguity flag sets, the bindings of reused and historical records,
   and a terminal process check.

**Final decision.**

- If any integrity check fails, the result is `UNRESOLVED_VERIFICATION`. That includes any
  disagreement on a shared gate.
- Otherwise the verifier's classification is final. It is computed from the shared, X and
  producer-only gates.
- `producer_confirmed` records whether that classification equals the producer's provisional one.

## Resources, layout and stopping

**Layout.**

- Sequential: one producer process, then one verifier process, launched as separate commands
  after the producer exits.
- Each process runs one arithmetic thread under an RLIMIT_AS of 3 GiB; stricter inherited limits
  are kept.
- Launches go through `ClaudeCode/runtime/slot_run.sh`, using pool slots and priority as set in
  `runtime/SLOTS.md` and `runtime/PRIORITY` (line cap 3). This line runs at most one job at a
  time.

**Ceilings.**

- Producer: 1,200 s wall. Verifier: 1,800 s wall.
- MemAvailable must be at least 8 GiB at launch.
- Expected cost is minutes.

**Recovery and refusal.**

- Completed case records and map files are immutable, and they are reused after an ordinary
  interruption. Partial maps for a case without a record are refused.
- Any exception after launch writes a failed-closed receipt, and there is no automatic restart.
- A refused launch writes a refusal record and no outcome. Refusal causes include a guard or
  environment failure, an existing terminal record, and an earlier failed-closed receipt.

**Exclusions.** No time evolution, physical IVP, new amplitude, grid regeneration, refinement or
threshold change.

## Claim limits

- A pass admits the saved grids as reproducible representations under an explicit knot table. It
  also shows that the choice of piece at knots changes map values and Jacobians by less than the
  stated bounds.
- These are finite-arithmetic representation statements. They are not error certificates for the
  exact map, the conformal lapse or the evolution.
- They leave the conservative whole-domain material bounds unchanged (A about 2e-4, Phi about
  8e-5).
- No dynamical, horizon, P16/MOTS or child-universe inference follows.
