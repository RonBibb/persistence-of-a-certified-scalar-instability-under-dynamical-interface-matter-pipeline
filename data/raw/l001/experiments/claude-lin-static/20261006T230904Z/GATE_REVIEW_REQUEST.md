# Gate review request: line 02 Lin static, run 20261006T230904Z (draft, NOT frozen)

**Requester:** Lin static worker. **Date:** 2026-10-06 UTC. **Checklist:** `ClaudeCode/weekly/GATE_REVIEW.md`.

## Test

Narrow the certified upper-wall interval D* ∈ K = [32727/16384, 32729/16384] inside the
accepted last two cells.

- **How:** exclude subintervals of K where the validated enclosure of either upper-wall junction
  function, e_I (Israel) or e_R (Robin), excludes zero.
- **Then:** re-evaluate the accepted material and mode comparisons on [0, D2] using
  D' = [D1, D2] and 64 subcells, with each block's bitwise replay checked against its checkpoint.
- **Also bound:** the wall observables (A, ell, Phi, rho = A - W, clock rate, log R) and the
  proper separation (signed cases, plus the case-0 background).
- **Deferred:** the lapse, inverse-map and node stages are deferred and not claimed.

## Files to review (all in this run)

**Contract:** `CONTRACT.md`.

**Code:**

| File | Role |
|---|---|
| `code/narrow.py` | producer |
| `code/assemble3.py` | gates and classification |
| `code/verify3.py` | independent verifier |
| `code/preflight3.py` | synthetic controls |
| `code/freeze3.py` | freeze; refuses unless `GATE_REVIEW_FINDINGS.md` exists |
| `code/common3.py` | configuration |
| `code/inherited/` | byte-identical identity-packet engine; hashes are checked at the freeze |

**Preflight record:** `preflight/<latest>/PREFLIGHT.json` (synthetic only).

## Self-check against the checklist

1. **Normalization cannot vanish.** No gate is normalized.
   - R and E gates use bitwise or exact rational equality and containment.
   - The B1 closure tolerance is relative to gross radii (rad_a + rad_b), with an absolute floor
     of 2^-600 (1 + |mid|). It is not relative to a net change.
   - Dominant-class shares are E-normalized displays at the argmax cell, where E is the global
     maximum and therefore positive. They are not gated.
2. **Thresholds sit above floors.** There are no thresholds on measured values.
   - The B1 tolerance follows a priori from Arb's 30-bit upward-rounded radii (2^-28 margin) and
     768-bit midpoints (2^-600 ≫ 2^-767 |mid|).
   - Exclusion is exact containment of 0 in a rigorous ball.
   - Evaluation precision: Arb 768 bits, the same as the accepted flows.
   - The binary64 columns are display profiles. Decisions use exact rationals.
3. **Scored regions.** The whole domain [0, D2] is scored, including the lower-wall cell and the
   upper-wall cells up to D2 ⊇ D*.
   - Cells beyond D2 are dropped only because D* ≤ D2 is proved: the exact family has no points
     there.
   - No center or physical-boundary cell is dropped.
4. **Seams and conventions.**
   - The event grid splits at the cell seam 4091/2048, and each half uses its own cell model.
   - The preflight crossing fixture places the true crossing exactly at the seam, and a second
     fixture places it inside a cell.
   - Comparison subcells align with cell boundaries. The subcell containing D2 is clipped.
   - The coverage gate checks gap-free tiling up to D2.
   - One convention throughout: a subinterval is excluded iff lo > 0 or hi < 0.
5. **Orders.** No convergence orders are claimed or gated.
6. **Counts and ratios.** Exclusion counts and width ratios are reported, not gated. Shares are
   scale-invariant.
7. **Implementation tolerances.**
   - Bitwise replay is exact.
   - The closure tolerance comes from the a priori Arb rounding model, not a round number.
   - The verifier requires exact equality: the binary64 value must equal the upward rounding of
     the exact value.
8. **Classification order.** Technical failures (R, E, B, C) map to technical labels that are
   checked before the science label.
   - `EVENT_EXCLUSION_INCONSISTENT` is a mathematical-consistency flag routed to Questions, not
     a physics verdict.
   - The science label only names which class dominates. It is not an admissibility verdict.
9. **Synthetic tests expose the failure modes.** Fixtures run at production precision (768
   bits), production event resolution (2048 per half) and production subcells (64). They use a
   manufactured background with a closed form, H(s) = -√k tan(√k s), and a known Israel crossing.
   They check that:
   - D' contains the true crossing, at the seam and inside a cell;
   - D' is at most 4 subintervals wide;
   - an inconsistent case (crossing outside K) is detected;
   - checkpoint tampering is detected;
   - the separation enclosure contains an mpmath quadrature reference;
   - closure and coverage hold;
   - the verifier dry run resolves.

   Limitation: the fixture has 513 cells, not production's 16,365.
10. **Verifier record.** It is dry-run in the preflight, and its records are cast to str, int,
    float or bool. There is no numpy in decisions, no mpmath qr_solve and no sympify.

## Points I would like the reviewer to check specifically

- **Exclusion argument.** Does validity rest only on the inherited D* ∈ K, the two junction
  identities at the exact wall (the identities used by the inherited `preparation.wall_jets`), and
  the validated cell models?
- **Narrowed shapes.** Is it valid to use D' in the shapes H0 and H1 of d for the Phi comparison
  while keeping the inherited C7 coefficients and the w state?
- **Domain restriction.** Is restricting the comparison domain to [0, D2] valid, and is the u
  mapping [s_a/D2, s_b/D1] with native clamping correct?
- **Separation enclosure.** Is [lo(I), hi(I) + hi(J)] a valid enclosure of ∫_0^{D*} exp(ell), given
  a positive integrand?
- **Classification order and labels.**

## Pre-freeze controls (synthetic only)

`preflight/20261006T233841Z/PREFLIGHT.json` passed:

- **Seam fixture:** D' is 2 subintervals wide and contains the exact crossing at the seam.
- **Interior fixture:** D' is 1 subinterval wide and contains the crossing.
- **Inconsistent event:** detected.
- **Tampered checkpoint:** detected.
- **Separation:** both signed fixtures enclose the quadrature reference.
- **Closure and coverage:** exact.
- **Verifier dry run:** resolved, 85 checks.

**Defect found by the preflight and fixed.** The event stage replayed the other flows with the
job's own native profile, so their running maxima mismatched (R1e). Every flow now uses its own
profile. The earlier failing records are kept in `preflight/` and `logs/`.

## Status

**Draft. NOT frozen. Nothing launched on real data.** After the findings, they go in
`GATE_REVIEW_FINDINGS.md` and in the contract's review record; only then does the freeze happen.
