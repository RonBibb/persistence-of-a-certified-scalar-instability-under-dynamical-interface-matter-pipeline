# Deterministic knot selection: the saved D1 conformal grids are reproducible representations

Run `20261006T185122Z`, line 02 Lin static. Completed 2026-10-06 UTC.

Independent classification:
`DETERMINISTIC_KNOT_REPRESENTATION_ADMITTED__HISTORICAL_RAW_GATE_RETAINED_FAILED`.

| Check | Result |
|---|---|
| Producer gates | 266 of 266 |
| Verifier decision gates | 318 of 318: 239 shared gates recomputed independently, 52 verifier-only, 27 producer-only |
| Integrity checks | 97 of 97 |
| Producer classification | Confirmed by the verifier |

The frozen contract is [CONTRACT.md](CONTRACT.md). The freeze guard is FREEZE.json, SHA-256
`c10709f70725644955dc0937918cf6bf3ef9dc0e25f427f84e5948c487a638df`. It was written at
20:22:23Z, before any real outcome.

## Success and gap movement

**What failed before.** The predecessor's 100-digit zero-case replay failed because of the knot
rule. The native polynomial piece used to build each coordinate-map cell was chosen by
`floor(fl(i*h)/h)` in floating point, and that rule switches between pieces i-1 and i at
precision-dependent knots:

- at 80 digits it switches at cells 3, 6, 12, 24, 48, 96 and 192;
- at 100 digits it switches at cells 9, 13, 18, 26, 36, 52, 72, 104, 144 and 208.

The verifier re-derived both tables independently, by exact emulation of round-to-nearest-even
arithmetic. They match the predecessor diagnostic cell for cell.

**Reproduction of the old saved map.** With the predecessor's 80-digit piece choice fixed as an
explicit integer table (`old80`), the saved maps of all six grids are reproduced at 80 and at 100
digits. The largest raw-coefficient differences against the saved maps at 100 digits are:

| Case | Raw difference |
|---|---:|
| 0 | 5.5e-80 |
| +5e-6 | 8.2e-80 |
| -5e-6 | 1.1e-79 |

That is about 29 orders below the unchanged 1e-50 raw gate. Inverse positions, reconstructed
fields, knots and length all agree to at most 1.1e-79.

The verifier independently rebuilt the exact-input map in 768-bit Arb. The saved map equals that
old80 reference to 5.6–5.9e-80, which is its 80-digit storage floor. The saved grids are therefore
exactly the representation they were built as, once that representation is stated. The remaining
dependence on precision is arithmetic rounding only.

**Revised canonical map.** In the revised map (`canonical`), cell i uses native piece i at offset
0, so the selection is integer-valued and needs no floating division. It agrees with itself
across 80 and 100 digits to at most 1.1e-79 in raw coefficients. Against the exact reference it
agrees to about 1e-80 at 80 digits and about 1e-100 at 100 digits.

Against the saved map it is an unlike representation, different on the 7 switched cells. The raw
differences there are 0.9–1.5e-11, but the whole-cell bounds, prospectively justified in the
contract, are:

| Case | Map value V | Jacobian J | Inverse positions and reconstructed fields at nodes |
|---|---:|---:|---:|
| 0 | 2.7e-65 | 5.2e-62 | 5.9e-66 |
| +5e-6 | 2.1e-65 | 4.0e-62 | 4.5e-66 |
| -5e-6 | 3.4e-65 | 6.5e-62 | 7.4e-66 |

The verifier's Arb Horner enclosures give the same values. The choice of piece at a knot is
therefore immaterial at the 1e-50 level.

**Mechanism.** The native Taylor-integrator pieces are continuous in value at knots to about
1e-81, but their first derivatives jump by up to 1.1e-63. Extrapolating piece i-1 across cell i
therefore moves the map Jacobian by about 1e-62. This is consistent with H0. It rules out:

- H1: no like representation is sensitive to precision;
- H2: the choice of piece is not material;
- H3: the signed grids pass every gate the zero case passes.

**Required derivatives, monotone maps and wall traces** (all gates passed):

- The represented Jacobian satisfies the pullback x_s = exp(ell - B) at every saved node to
  1.2e-65 for canonical and 2.4e-63 for old80.
- The Jacobian lower bound on every cell is at least 0.99997 for the saved, old80 and canonical
  maps.
- X matches the last cell evaluated at the wall D to 2.4e-87. Inverting the saved upper-wall x
  returns D to 8.4e-81 under old80 and 4.5e-66 under canonical.
- The gauge q and its first two derivatives vanish at both walls to 4.4e-81, and B - A is exactly
  0 at the wall nodes.
- At the saved positions, fields agree to 1e-79 and seed rows to 5.8e-78.
- The proper-clock rates agree across precisions to 2.1e-81.
- The inherited original-equation wall rows are at most 1.5e-52, against inherited thresholds of
  1e-10 and 1e-12, and agree across precisions to 1.1e-78.
- The inherited Hamiltonian, momentum, wall-row and inverse-derivative admission receipts of all
  six grids are authenticated and unchanged.
- No evaluation point fell within 1e-40 of a shared knot.

**Signed comparisons that never ran.** The signed replays for both amplitudes at both precisions
are now complete and pass. The ported root-bound comparison also passes. The saved numerical
correction centers (A0 - epsilon, b0, b1) equal the certified sample centers, and the
independently translated root images lie strictly inside the common uniqueness box. The rigorous
distances from the centers are:

| Coordinate | Distance (+5e-6) | Distance (-5e-6) | Center |
|---|---:|---:|---:|
| A0 - epsilon | 3.26e-6 | 3.27e-6 | 3.4e-9 |
| b0 | 5.81e-4 | 5.81e-4 | -1.41e-4 |
| b1 | 9.48e-3 | 9.48e-3 | 1.3e-4 |

These distances are much larger than the centers themselves. The certified enclosures identify the
branch, but they do not pin down the numerical coefficients.

## Issues

- **The historical raw-coefficient failure stays failed.** The predecessor's 1e-50 gate compared
  a 100-digit floor-rule map against the 80-digit saved map, which are unlike representations,
  and it failed. This run reproduces that failure exactly as a detector control: 1.144025854e-10
  at cell 208, power 29, on the same 17 cells. It is not rescored. The whole-cell norms are new
  and prospective, and they apply only to the new unlike comparison.
- **The admission is representation-level only.** It shows that the stored grids are determined
  reproducibly by their inputs. It is not an exact-map, conformal-lapse or evolution error
  certificate. The conservative material bounds are unchanged: about 2e-4 for A and about 8e-5 for
  Phi.
- **Root bounds are loose.** The distances are coefficient bounds, and they are loose relative to
  the coefficients, by up to about 70 times for b1.
- **Some checks are weak by construction:**
  - I3 (gauge identity) and C3 are tautological;
  - x(0) = 0 and the orientation signs hold by convention;
  - the q-based wall checks could not fail at 1e-50, given the predecessor's 2.75e-134 gauge
    residual.
- **The verifier's independence has limits.** It re-thresholds the producer's exact wall rows
  rather than rebuilding the inherited time-jet construction. It checks reconstructed positions
  by forward evaluation rather than repeating the Newton inversion.
- **Floating floor rules switch pieces at binary128 too** (113 bits: cells 7, 14, 28, 56, 112,
  224). Any future evaluation of native pieces at knots, for example by Lin initial in binary128,
  should use integer selection.
- **The pre-freeze review caught a design flaw.** It found that the first verifier design
  collapsed hypothesis-bearing failures into UNRESOLVED_VERIFICATION. The flaw was corrected
  before the freeze and dry-run on tampered and disagreeing fixtures. Fixture iterations 01–04 are
  preserved under preflight/ and logs/; only 20261006T201310Z binds the frozen sources.

## Next steps

- **The smallest consequential calculation** is in the TRANSFER's authorized follow-ups. Propagate
  the validated source and input bounds through the conformal lapse, the inverse coordinate map
  and the physical initial observables. Start by identifying the dominant enclosure width: the
  correction-coefficient boxes found here, and the source rectangle behind the 2e-4 bound on A.
  Do this before narrowing any interval or adding flows.
- **For Lin initial:** the six saved grids are admitted as stated. If any grid is regenerated,
  use the canonical integer knot table.
- No question for Ronald is needed.

## Viability

Continue, for one more bounded step. The representation gap that blocked numerical admission is
closed. The remaining gap is quantitative accuracy, meaning validated error propagation, and it
lies within this line's authorized scope.

## Evidence class

Finite-arithmetic representation evidence, independently verified:

- exact rational and 768-bit outward-Arb comparisons of stated representations;
- exact emulation of floating-point knot rules;
- an exact-rational signed root-bound comparison.

It is not a continuum or evolution error certificate.

## Execution

- **Producer:** slot 11, PID 459374, 250 s wall (247.5 s CPU). It wrote 6 immutable case records
  and 18 map files.
- **Verifier:** a separate command after the producer exited, slot 7, PID 463305, 56 s.
- Both ran one thread under a 3 GiB RLIMIT_AS.
- The inputs were 54 files, bound by hash, each listed in its predecessor manifest.
- The runtime binding is identical to the predecessor's (130 libraries; python-flint 0.9.0,
  mpmath 1.3.0, Python 3.12.3).
- The three accepted spatial flows were reused by hash, not rerun.
- No time evolution or physical IVP was run.

## Artifacts

All paths are relative to this run directory.

- **Contract and freeze:** `CONTRACT.md`, `FREEZE.json`, `FREEZE_RECORD.json`.
- **Final preflight:** `preflight/20261006T201310Z/PREFLIGHT.json`.
- **Sources:** `code/` (replay.py, verify.py, representation.py, common.py, preflight.py,
  freeze.py) and `code/reference/`, which holds byte-identical producer.py and jet.py.
- **Producer outputs:** `outputs/PRODUCER_RESULT.json`, `outputs/case{0,3,4}_p{80,100}.json`,
  `outputs/maps/*.json` (exact mantissa and exponent encodings).
- **Verification:** `verification/VERIFICATION.json`.
- **Logs:** `logs/producer.log`, `logs/verifier.log`.
- **Seal:** `FINAL_PROCESS_CHECK.json`, `MANIFEST.json`, written by the publication-only
  `post/seal.py`.
