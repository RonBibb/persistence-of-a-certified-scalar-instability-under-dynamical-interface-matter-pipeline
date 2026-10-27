# Gate review request: line 02_lin_static, run 20261007T030034Z (round 3)

**Test.** The narrowed-D' re-preparation, assigned by the coordinator for round 3. It uses
D' = [33513605/16777216, 67027255/33554432] from run 20261006T230904Z and rebuilds:

- the C7 correction enclosure d;
- the root boxes a, b0 and b1;
- the material bounds, in particular A and Phi.

**Status.** Draft. **Not frozen.** No real outcome has been computed.

## What to review

- `CONTRACT.md`: the question, the precision, the validation method, the a priori expectations, gates,
  classification, verifier, fixtures, resources and deferrals.
- Code, all in `code/`:
  - `reprep.py`: the producer, with stages A, B and C and the controls.
  - `assemble4.py`: the single decision path.
  - `verify4.py`: the independent verifier.
  - `preflight4.py`: the fixtures.
  - `freeze4.py`, `campaign.sh` (the driver) and `common4.py`.
  - `code/inherited/`: the copies.
- Pre-freeze records, both in `preflight/` and both made with the current draft code (the contract text
  changed afterwards only in record paths):
  - `REAL_CONTROLS_CHECK_5.json`: the stage-A controls on real inputs. All pass for both amplitudes.
    No outcome was computed: no D' jets or preparation, and no flow.
  - `20261007T034301Z/PREFLIGHT.json`: passed, 13 of 13 expectations, in 72 s. The main fixture is
    resolved, with 77 of 77 verifier checks.

## Summary of the method

**Stage A (every job).** Bitwise controls run first:

- R0: the source last block;
- R0m: both accepted certificate phase maps;
- R0j: the K jets;
- R0p: both K preparations;
- D0: the D' record.

A failed control writes `CONTROL_FAILED.json` and stops before any outcome. The campaign then launches
no material job, and the assembly opens no outcome record.

**Stage B (four jobs).** The nonlinear 17-state flow with the D' preparation runs at the exact center of
the certified old root image X and over X. The certificate's map is formed over D'.

**Stage C (two jobs).** One Krawczyk step, X' = X ∩ K(X), with the frozen C = diag(-24/23, 1, 1).

- Validity: x* ∈ X (old certificate), so x* ∈ K(X) by the mean-value form. No new existence or
  uniqueness claim is made.
- An empty meet is a defect: ROOT_ITERATION_INCONSISTENT.
- Then the prepared material flow runs with X' and the D' preparation, compared on 64 subcells per cell.
  Walls and separation follow as in run 3.

## Points that need a decision or a check

1. **The a priori expectation is near-null.** Recorded inputs show that the D-width channel is not the
   binding width.
   - The upper f and g jet radii (1.32 and 5.47) are point-state radii at the wall. Their K-hull part is
     about 1.2e-4.
   - The c7 radii (max 7.5e-7) and W radii (4.07e-4, 9.32e-3) are f-dominated: the eps² Hermite weight
     is about 1.1e3 on f0 against about 22 on psi0.
   - The G(c) radii equal rad v at a point (2.96e-6) and the W radii. They therefore set the root boxes.

   Expected: b0, b1 widths unchanged within 1%; a about 5% narrower, but from the contraction terms, not
   from D'; A and Phi within a few % of run 3. The attribution diagnostic, `prepare` with the f jets at
   midpoints, tests whether the propagated f and g source radius (the mu bracket of width 1e-5, plus
   wrapping) is the next width to narrow.

   **Coordinator:** proceed as assigned, or redirect? The worker proceeds as assigned unless told
   otherwise.

2. **Port of the finite preparation.** The identity packet's copy of `preparation.py` (5402279f…)
   cannot reproduce the accepted preparations: its `remainder_eval` differs, and it returns an extra
   key. The finite packet's version (70f6cfa0…) is now the inherited copy, and the freeze binds each copy
   to its origin packet.

   The accepted lower jets were formed from the fresh initial state, not its outward-canonicalized
   stored copy. The finite runner's `initial()` is ported; its canonicalized output must equal the
   stored y0.

   The first real control check failed R0j and R0p for exactly these two reasons; after the ports it
   passes. This is the reason for item 3.

3. **Real-data control check before the freeze.** The controls replay and reproduce accepted, recorded
   quantities only. Please confirm that running them pre-freeze is acceptable. It exercises the
   controls in the production regime, as item 11 asks.

4. **Deferral** of the lapse, inverse-map and node stages: each needs a new derivation, fixtures and a
   review.

## Checklist self-assessment (weekly/GATE_REVIEW.md)

1. **Normalization.** No gate normalizes. Shares (component/E at the argmax) and the old/new width and
   bound ratios are diagnostics. Their denominators are nonzero recorded widths or bounds.
2. **Floors.** Arb runs at 768 bits. R0, R0m, R0j, R0p, R1 and the verifier agreement checks are
   bitwise or exact. B2 is 2^-27 relative, from mag_t rounding below 2^-27.6, with a 2^-600 absolute
   floor far above 2^-767 |mid|. Krawczyk and the containment tests are exact rational comparisons of
   Arb endpoints.
3. **Scored region.** Every cell on [0, D2] and all 64 subcells are scored, the last cell clipped at D2;
   no cell is dropped. Both walls are scored.
4. **Seams.** D' lies inside one cell, and K spans two, in both production and the fixture. The
   separation splits at D1 inside the subcell. Coverage is exact rational tiling. The cover gate is an
   exact equality with [[D1, D2]].
5. **Orders.** No convergence order is claimed (N/A).
6. **Counts and ratios.** Closure counts violations, and any violation fails. There are no ratio gates.
7. **Control tolerances.** All bitwise, except B2, which uses an a priori rounding bound.
8. **Label order.** Technical, pipeline, incomplete and defect labels come before the descriptive
   science label. A control failure is labeled from control records alone. No physics verdict exists in
   the label set. ROOT_ITERATION_INCONSISTENT is a defect label by construction.
9. **Synthetic tests.** Every fixture runs at production precision (768 bits) and 64 subcells, through
   the full production record path. The fixtures are main, source-tamper, phase-map-tamper,
   preparation-tamper, D' unrecorded, root-inconsistent, verifier-tamper and unit Krawczyk. The real
   control check covers the production regime of every control.
10. **Verifier records.** Dry-run in every fixture through `common4.atomic`; plain() rejects
    unserializable types. There is no numpy in production. mpmath is used only in the fixtures.
11. **Post-review changes.** After the review, the preflight and the real control check are re-run with
    the final sources. The freeze requires both, and checks that their source hashes are current. A new
    control the reviewer did not see goes back to the reviewer or is reported only.

## Timing

- The preflight runs in about 72 s. The real control check takes about 15 s.
- The campaign is expected to take about 40 min plus queueing. It is ten jobs, all under 1 h, so no
  restart test is needed.
- Production must start before 2026-10-07T06:53:30Z. The assembly and verifier jobs declare
  COMPLETION_OF.
