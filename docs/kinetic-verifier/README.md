# Exact-Fraction saved-cell verification

This route checks the saved kinetic certificate using the recovered historical exact-Fraction verifier. It is separate from the 822-check saved-record inventory and separate from interval-trajectory regeneration. The historical implementation, plan, candidate and admission-linked review receipts are preserved under `data/raw/neutral-certificates/kinetic/`; source recovery does not change their original review or execution scopes.

**Local qualification passed on 27 October 2026:** one relocated read-only run checked all 16,365 cells and 64 chunks, with all seven coarse gates true, in approximately 233 seconds. All nine predeclared rejection controls passed. See the [execution and scope report](../../data/processed/kinetic-verifier/20261027_portable_v1/QUALIFICATION_REPORT.md). The run used the recorded macOS/Python platform; no cross-platform rerun or independent scientific review is implied.

The new launcher loads the pristine implementation with SHA-256 `4fb8bad4ef5f197074f6fc5709fe023753a523185c26f26546de64c62d7284f7`. It replaces only packet discovery, the expired deadline and the original-path guard. All interval classes, exact initial-state calculation, vector field, Taylor/Horner routines and saved-cell numerical predicates execute from that unchanged source. No interval producer is imported.

## Export and run

Use Python 3.10 or later, its standard library, and a POSIX platform with `SIGALRM` (the qualification platform is recorded in the result). No NumPy, SymPy, Arb or historical author directory is needed by this check. Retrieve the repository data before exporting; do not run the original historical launcher with its expired execution window.

From the pipeline repository, using new output paths:

```sh
python3 src/export_kinetic_verifier_bundle.py --output /tmp/kinetic-inputs
```

The exporter copies the explicit execution closure and prints its manifest hash. For the frozen qualification version, the root is `e69a740d23951c794231330c5d53e0e432a493ef0b43179ce53d427dbcdd9c19`: 104 bound files, 13,914,197 bytes, 16,365 cells and 64 chunks. The manifest is deterministic for those source/data bytes and uses bundle-relative file locations. Original absolute locations survive only as historical provenance in preserved records; the launcher resolves them through an explicit hash-checked snapshot map.

```sh
python3 /tmp/kinetic-inputs/verify_kinetic_cells.py \
  --bundle /tmp/kinetic-inputs \
  --expected-manifest-sha256 e69a740d23951c794231330c5d53e0e432a493ef0b43179ce53d427dbcdd9c19 \
  --output /tmp/kinetic-positive-run \
  --timeout-seconds 600
```

The explicit manifest hash is the content trust anchor. An unexpected hash is a version difference or integrity failure to investigate. Do not merely replace it to accept unexplained changes. Existing output paths are refused. A full run emits chunk progress, `VERIFICATION_RESULT.json` from the pristine numerical routine and `PORTABLE_RUN.json` identifying the new launcher, runtime and manifest. Failures retain diagnostic receipts; a validated prefix or timeout is not a full PASS.

Run the predeclared negative controls in a separate new directory:

```sh
python3 tests/check_kinetic_verifier_controls.py \
  --bundle /tmp/kinetic-inputs \
  --output /tmp/kinetic-negative-controls
```

Each case has a 30-second worker bound. Fixtures are copied derivatives: unchanged metadata must reject byte corruption; deliberately rebound metadata lets malformed proof data reach the numerical predicates. The nine controls cover changed chunk bytes, protocol bits, cell index, Picard box, whole-cell bounds, endpoint bounds, spurious event, iteration count and existing-output preservation. They do not exhaustively verify every branch of the implementation.

## What is checked

- Reconstruct the exact rational initial box and curvature from the full model inputs; verify the saved protocol, payload/chunk identities and ordered time/cell coverage.
- For every saved cell, require strict Picard inclusion and containment of independently evaluated exact-rational Taylor whole-cell and endpoint enclosures. The saved certified endpoint starts the next cell.
- Check every uncertain upper-wall overlap, the final endpoint, whole-collar/event hulls, invariants, derived coefficient bounds and original coarse kinetic gates.
- Recompute the final rational comparison and check final pointer/payload stability. Input writes and reads outside the bundle, output directory and Python runtime are refused by the worker's file audit.

This verifies an inductive certificate already stored by the historical producer. It does not select new Picard boxes, regenerate the original IVP, prove exact-root existence, independently establish the analytical weighted-form theorem or resolve the nonlinear seven-source/inverse estimates. The historical admission is evidence of its original content review; it does not approve the new launcher or count as a new independent review.

## Evidence and manuscript status

The prospective plan and source freeze, execution results, controls and final disposition are retained in `data/processed/kinetic-verifier/20261027_portable_v1/`. Their `QUALIFICATION_REPORT.md` states the actual outcome and scope; instructions and source presence alone are not a successful run.

Revision 7 and the revision-6 pipeline PDF remain frozen. Their historical statements are not silently rewritten by this repair. The next manuscript/supplement assurance update must distinguish (1) the 822 record checks, (2) this newly qualified exact-Fraction saved-cell check, and (3) interval-trajectory regeneration, which has not been performed. The identifying public-side working tree is not an anonymous referee-delivery route. These local additions are not claimed to have been committed, pushed or externally delivered.
