# PLAN_W — family W, a two-parameter box of upper-wall potentials (separate pre-registration)

This is a separate pre-registration, distinct from the V/L freeze (`PLAN.md`, `FREEZE.json`). It has its own review section in `GATE_REVIEW.md`, its own freeze (`FREEZE_W.json`), its own VM stage (`~/claude-second-bg-20261114T055250Z/W/`) and its own run folder (`runs/W/`). Nothing frozen for V and L is changed. All times are UTC from `date -u`; the session deadline is 09:52:50Z, and no job starts after 09:15:00Z.

## 1. Target

Family W is a Target A box. The varied parameters are:
- \(v_1\in[11/125,\ 1/10]=[0.088,0.100]\);
- \(\lambda_b\in[-60529/10000,\ -60429/10000]=[-6.0529,-6.0429]\).

The other four parameters (m², γ, v0, λ_a) keep their exact Table 4 values.

The box is split into 120 closed cells of \(1/1000\times1/1000\). Cell \(j=12k+i\) has \(i=0..11\) along \(v_1\) and \(k=0..9\) along \(\lambda_b\). The anchor \((v_1^{(0)},\lambda_b^{(0)})\) lies in cell `W_02`, which is \([0.090,0.091]\times[-6.0529,-6.0519]\). In that cell the anchor is interior along \(v_1\) and sits \(5.6\times10^{-5}\) inside the lower \(\lambda_b\) edge.

## 2. Design (binary64 exploration, `runs/exploration/make_boxes_2d.py`, labelled)

- **Root estimates.** Each cell uses its centre root and its four corner roots.
- **Spread.** The spread is the largest corner deviation from the centre root.
- **Predicted Newton half-width.** Its \(D\)-term uses \(|\partial_{v_1}D|_A+|\partial_{\lambda_b}D|_A\).
- **Radius.** The radius rule is the same as for V and L: \(r=2.5\max(\text{spread},\text{prediction})+5\times10^{-9}\).
- **Dropped column.** The design also covered \(v_1\in[0.086,0.088]\). That column was dropped before any interval run, because its crude predicted lower bound for \(T_b\) was negative or below 0.002. This is the only selection made from the exploration.
- **Box table.** `runs/W/FAMILY_BOXES_W.json`. A-box widths are 2.7e-7 to 5.8e-7 (sha256 of the table in FREEZE_W.json).

## 3. Statement, engines and gates

**Statement.** Each cell carries the same statement as PLAN §3 (S1–S5), with the parameter set \(P_j\) now a rectangle. The parametric interval Newton is uniform over both balls.

**Engines and regime.** These are the same as PLAN §4: the byte-identical archived producers at 32768, 8192, and 8192/16384 cells and 768 bits. The only addition is in the two wrappers. With `extra_params = [["lambda_b", lo, hi]]`, they install a second outward ball, `LAMBDA_B_Q`, with the same checks. These are the frozen V/L wrappers plus that loop.

**Gates.** All gates of PLAN §5 apply, together with:
- **P2x / I2x (I).** The extra ball contains its interval, and the extra-ball count is correct.
- **R1 / R2 (I), for both balls.**
  - \(\min\operatorname{rad}(h)\ge10\operatorname{rad}(v_1)(1-2^{-600})\).
  - \(\min\operatorname{rad}(G)\ge\operatorname{rad}(\lambda_b)/6\,(1-2^{-600})\).
  - Both bounds hold simultaneously when both balls are consumed, because \(h\) does not involve \(\lambda_b\) and \(G\)'s radius only grows with the \(v_1\) ball.
- **R3 (I), from the independent engine's own centre enclosure.** width(\(h\)) ≥ \(20\operatorname{rad}(v_1)\), and width(\(G\)) ≥ \(\operatorname{rad}(\lambda_b)/3\).

The checker is `check_family_w.py`. It imports the frozen `check_family.py` and replaces only its consumption-gate function by the two-ball version.

## 4. Claim

**Contacts.** The seam test (PLAN §3) is applied to every contact between certified cells. A contact is either an edge, where the cells share a side, or a diagonal, where they share only a corner point. The test is valid at every shared parameter point. A passing contact therefore ties the two cells' roots on all their common points.

**Component.** The component is the set of certified cells joined to the anchor cell by passing edge seams.

**What is claimed.** The one-branch claim is made only if every edge and every diagonal contact between component cells passes. In that case the certified roots form one continuous branch on the component, through the archived root.

**Classifications.**
- FAMILY_CERTIFIED_FULL_BOX: all 120 cells are certified and every edge and diagonal contact passes.
- FAMILY_CERTIFIED_CELL_COMPONENT: the one-branch claim holds on the component only. Certified cells outside it are listed as pointwise certificates.
- FAMILY_CERTIFIED_CELLS_POINTWISE_ONLY: some contact inside the component failed. The untied contacts are listed, and each cell is claimed for its own rectangle only, with no branch claim.
- FAMILY_NOT_CERTIFIED_AT_ANCHOR_CELL.

All 416 contacts in the frozen table (218 edges and 198 diagonals) have overlapping A-boxes.

**Not merged with V or L.** W overlaps V (row k = 0, sub-boxes V_02–V_13) and L (column i = 2, sub-boxes L_00–L_09). No seam is tested between W and V/L. The W and V/L results are reported side by side and never merged into a larger connected claim.

No region beyond the union of the claimed cells is claimed.

## 5. Controls (run first in W production; W cells start only if all pass)

- **CW0, the environment.** CW0 checks the V/L production `CONTROLS_VERDICT.json`, which passed at 07:16:37Z. It reads a pinned copy, `VL_CONTROLS_VERDICT.json` (sha256 `e4436446…`), held in the W stage and listed in `FROZEN_STAGE_W.sha256`. The copy must show `controls_pass` true and every C0/C1 gate passed. That run used the same machine, runtime and archived code. C1 is not rerun; C2w re-establishes the environment in the W stage.
- **C2w, two degenerate balls.** \(v_1\) and \(\lambda_b\) are both degenerate at their archived values, with the archived narrow box and centre.
  - The primary row is byte-identical to the archived narrow row.
  - The independent 8192 level is identical to the archive: Newton image, self-map, root pass and root-box quantities.
  - The binding's A, D and model equal the archived ones.
  - The phase θ_b/π is identical to the archive.
- **C3w, two small balls.** \(v_1=v_1^{(0)}\pm2^{-16}\) and \(\lambda_b=\lambda_b^{(0)}\pm2^{-16}\), with the archived narrow box and centre. At this \(v_1\) radius the R1 bound, 1.5e-4, lies above the unconsumed baseline of 1.3e-6, so R1 decides \(v_1\) consumption in C3w as well.
  - Both engines are COMPLETE, with the two-ball consumption gates.
  - The primary Newton image strictly contains the archived narrow image.
  - The primary box bracket strictly contains \([32727,32729]/16384\).
  - The independent centre \(h\) and \(G\) enclosures are each strictly wider than the archived ones.

## 5b. Pre-freeze dry run for W (after V/L production ends, before `make_freeze_w.py`)

This dry run happens in a scratch directory `W_dryrun/` of the W stage.

The script is `runs/W/dryrun_w.sh`. It refuses to run unless the V/L `production.log` shows PRODUCTION END.

**Steps.**
1. **Full job-list build, zero compute.** Expected: 360 unique jobs, with W_02 first.
2. **Real jobs, about 1 min.** C2w and C3w run with the W code. CW0 reads the pinned copy.
3. **Synthetic 2×2 family, zero compute.** Cells (0,0), (1,0) and (0,1) are symlinked to the C2w jobs. Cell (1,1) has its three jobs marked SKIPPED at the launch cutoff. The checker's 2-D family mode then runs on it.
4. **Syntax check.** `bash -n src/run_production_w.sh`.

**Expected.**
- Every CW0, C2w and C3w gate passes.
- The synthetic family gives FAMILY_CERTIFIED_CELL_COMPONENT, with the three cells (0,0), (1,0) and (0,1), and three contacts checked inside the component: two edges and one diagonal, all passing. The branch flag is true and (1,1) is NOT_RUN.

**Scope.** These steps exercise:
- the two-ball wrappers and both consumption gates for two balls;
- `build_jobs_w.py` controls and `family()`;
- horizontal, vertical and diagonal contacts, a component smaller than the box, and the NOT_RUN listing;
- the W production script's syntax.

No W cell runs before the freeze. After the freeze copy, and before launch, the W stage's `sha256sum -c` line also runs.

**On failure.** The fix goes back to the reviewer, or W is abandoned and reported as not run.

## 6. Failure policy, compute, honesty

**Failure policy.** PLAN §7 applies:
- no tuning after the freeze;
- failed cells are kept and reported;
- a control failure means no W cell runs;
- skips at the launch cutoff are NOT_RUN.

The W stage must match `FROZEN_STAGE_W.sha256`, which `run_production_w.sh` checks with `sha256sum -c --strict`.

**Compute.**
- Runs after V/L production finishes; never concurrent with it. `run_production_w.sh` enforces this: it exits, launching nothing, unless the V/L `production.log` contains PRODUCTION END.
- 6 single-thread processes, no pinning.
- About 120 × 115 ≈ 1.4e4 core-s, roughly 40 min.
- Cells run outward from the anchor cell, so the launch cutoff truncates the outer cells first.

**Honesty.** PLAN §11 applies. In particular:
- The engines share Arb.
- The claim covers the stated cells only, conditional on F04 and on outward Arb execution.
- No connectivity beyond the passing contacts is claimed.
- W is never merged with V or L.

## 7. Review record

| Item | Value |
|---|---|
| Reviewer | The same independent gate-review subagent |
| Section | `GATE_REVIEW.md`, "Review of PLAN_W", 2026-11-14T07:20:08Z |
| Recommendation | FREEZE W, after the §5b dry run passes and with W1 fixed and W2–W3 applied first |

Changes made after the review:
- **W1 (blocking).** `check_family_w.py` now tests diagonal contacts. The component's branch claim needs every internal contact to pass, and the new FAMILY_CERTIFIED_CELLS_POINTWISE_ONLY class covers the case where one fails.
- **W2.** The V/L controls verdict is pinned as `VL_CONTROLS_VERDICT.json`, in the W manifest.
- **W3.** `run_production_w.sh` requires the V/L log to show PRODUCTION END before anything starts.
- **Optional C3w change, adopted.** The \(v_1\) radius is now \(2^{-16}\).
- **W4.** The not-merged statement is added in §4.
- **§5b.** It is extended to the 2×2 case and the 360-job build check.

As the review requires, every one of these changes runs in the §5b dry run.

**§5b dry run executed** 2026-11-14T07:44:39Z–07:45:32Z, in VM `W/W_dryrun/`. Every result matched the pre-stated expectation:
- the job list has 360 unique jobs, with W_02 first;
- CW0, C2w and C3w pass all 39 gates;
- the synthetic 2×2 family gives FAMILY_CERTIFIED_CELL_COMPONENT on W_00, W_01 and W_02, with 3 contacts checked (two edges and one diagonal), none untied, the branch flag true, and W_03 NOT_RUN;
- `bash -n src/run_production_w.sh` passes.

No change followed the dry run.
