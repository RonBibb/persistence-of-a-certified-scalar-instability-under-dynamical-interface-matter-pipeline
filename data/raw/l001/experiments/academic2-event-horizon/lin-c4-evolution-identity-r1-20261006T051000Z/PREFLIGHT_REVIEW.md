# Independent R1 source-bound preflight review

Decision: **PASS for execution of the unchanged bounded identity/admission experiment.** This approves the disclosed implementation repair and its new freeze; it does not certify a physical outcome or authorize another successor.

## Repair and provenance

The original `lin-c4-evolution-identity-20261006T044000Z` remains a failed frozen attempt under guard `84d1e800ebb5deedae8e175dcf6b162a08938977f77752080f75f33be240f3ab`. Its `RUN_FAILURE.json`, SHA-256 `c5dccfb76dd2dc1d710ab6c1d0ca93a6c25f553936c6774f202411ece844346f`, records a saved-decimal reader exception before any accepted physical cell or checkpoint. It is not relabeled as a scientific failure or success. The R1 repair record has SHA-256 `70420ac3f5b0db1dcef2d37e0d59d516a985d042e2cb09572ff83dd67f70bb9e`.

I reviewed the complete source diff against the original frozen sources. Only `identity_run.py` changes among the 16 source bindings:

- Input literals are parsed by `Fraction(str(value))`, then passed as exact integer numerator and denominator to `fmpq`. Decimal and scientific strings are therefore interpreted as the exact stored decimal rationals. There is no binary64 intermediate, fitting, rounding of source literals, or narrowing of their intended uncertainty.
- Four exact parser fixtures cover a terminating decimal, scientific notation, the negative target amplitude, and a rational string.
- A top-level immutable failure receipt now covers ordinary pre-loop exceptions as well as execution failures. A recorded failure is refused on subsequent invocation; the original failed capsule is not restarted.

This is a constructor-compatibility and failure-reporting repair. It does not change an equation, initial profile, action parameter, source interval, step, precision, enclosure test, acceptance margin, work limit, or outcome classification.

## Retained mathematical review and limits

The original full preflight review has SHA-256 `145d29187e1bcdfe2d507f8a39db56e211fddce6f7c8cb18673a54ba076dc204`. Its mathematical assessment is retained because all mathematical sources, the contract, derivation, independent gauge-bridge source and its 15-check symbolic receipt are byte-identical. In particular:

1. The off-defect identity in `INDEPENDENT_IDENTITY_NOTES.md` identifies the material and conformal scalar C4 zero sets only on the stated exact C2/Israel-compatible initial family. The third lapse jet removes the second-Israel defect entering scalar C4; the fifth fixes fourth-Israel compatibility without entering scalar C4. Initial tensors, wall orientations, proper separation, zero momenta and clock pullback retain their stated meanings. This is finite-jet initial-data identification, not an all-order compatibility or spacetime-evolution theorem.
2. The mode sensitivity is taken at fixed exact background and event time. Its inhomogeneous term is `-E^2 f`, its initial scalar derivative is `3/B0`, and the upper determinant derivative is `g_mu + 2T psi_mu + gamma f_mu/2`. A strictly negative enclosure on the full inherited bracket, combined with the inherited endpoint signs for that same exact source, selects a unique zero only within that bracket. The actual outcome must establish this; preflight does not presume it.
3. The signed flows retain full Hamiltonian backreaction and the complete certified background/mode/event rectangles. Their initial correction boxes are the connected predecessor's independently recomputed translated root images, linked to the original signed result hashes. Saved fitted centers do not replace these enclosures.
4. The complete normalized-coordinate comparison uses `[t Dnative/Dhi, (t+h) Dnative/Dlo]` intersected with `[0,Dnative]` and every intersected saved polynomial segment. The validated range polynomial and remainder cover the whole source cell, including the event intersections; this is not node-only comparison. Exact decimal parsing preserves the complete stored polynomial rather than altering it.
5. Numerical readback remains limited to cases 0, 3, 4, degrees 160 and 192, at 80 and 100 decimal arithmetic. It verifies the inherited admission hashes, finite predicates, saved amplitude range, material polynomial replay, represented map monotonicity, zero momenta and clock normalization. The shared inherited gauge/map constructor is disclosed. The Taylor/Picard and native-checkpoint primitives are likewise shared, not a second independently implemented physical solver.

The rigorous full-domain material/source error bounds, the represented-grid replay errors, and any error in an exact conformal lapse or inverse map remain separate. The last two rigorous errors are explicitly not supplied. Source-flow bounds alone do not cover a distinct zero-case metric correction. No continuum evolution-error, nonlinear stability, collapse, causal-fate, enlarged-amplitude, or parameter-neighborhood claim is authorized.

## Final controls and execution boundary

`control-01/RESULT.json`, dated `2026-10-06T05:07:35.128976+00:00`, has SHA-256 `311bc0babc56223764e137ab8fffdbc645b61cb9320666f305f28e8dd90a998f`. I checked all 16 actual source hashes against that receipt. Its configuration and runtime records exactly match the original final `control-06` records. All ten named synthetic/recovery predicates pass, including the new exact parser fixtures, fresh-process exact continuation, inhomogeneous sensitivity, prepared-zero control, complete segment selection, safe zero-crossing shape evaluation, nonfinite rejection, wrong-guard refusal, ignored uncommitted files and both historical manifest schemas. The receipt states `physical_outcomes: false`. No numerical process was launched during this R1 review.

Before execution, the new freeze must authenticate the existing parent/input hashes, runtime, this review and this final control receipt. The unchanged run allows at most three serial spatial flows, 16,365 cells per flow, 768-bit precision, step 1/8192, strict Picard limit 32, checkpoints every 256 cells, 1,800 seconds integration CPU per flow and 4 GiB address space. Only one heavy process/thread is admitted for this line. The finite numerical-readback graph retains its explicitly per-invocation 3,600-second cap and immutable completed-case reuse. No physical flow has been rerun by the reviewer.

Independent postrun acceptance must inspect actual terminal classifications, full event and normalized-u coverage, native checkpoint integrity, source/input/runtime bindings, root-image links, determinant signs and the meanings of the published field-error bounds. Any failed enclosure remains unresolved under the frozen gates.

## R1 source bindings

| File | SHA-256 |
|---|---|
| CONTRACT.md | `15285578dfcfb903bdd89371216a9fe4288141b78452a2c4a29bcc36905465f5` |
| DERIVATION.md | `93f32d1e58232b5725c3b19091713160dd09d4ad34f83fbfd65d8b095f91b4e7` |
| INDEPENDENT_GAUGE_BRIDGE.json | `e669c93bb4402a3f20f6e82c88f5f5168ba47554011e116a422780b0cb06cf42` |
| INDEPENDENT_IDENTITY_NOTES.md | `292b95c80da6bfe336abebc05f2b9a7c52e5721a9be83469bdc2333e869bbf4f` |
| algebra.py | `2b6d373839620cd9abdd0d88b88aee8d4bd3f780f30ce75b96a494ab246b180d` |
| identity_run.py | `9c64bc8444138cacff289d5ec9016c549e7b529a6ea434bfc79590001c92ac09` |
| independent_gauge_bridge.py | `6426cc83707081c1d262e93ba0cc90d696d7d76aa519fa6097d9908f81e61562` |
| mode_flow.py | `8f59b7722c6bac43dc3a0bc1764b0eb3f6600a7c616e5f242df2245248f4cbb4` |
| nonlinear.py | `f303d46f2d6f5fd4639294df9d6db777689e2ea3f4f144e38e2321ec5c31bf2c` |
| numerical_readback.py | `dbf18612337f6e1fc114f2c02d6c88f1736f65ec97790ea6ccfd8c9849863399` |
| preparation.py | `5402279f4d73f37523c1b55fe91d67b6c08aa576e800fa0fd140b18548807881` |
| prepared_flow.py | `05cb1a761b5cda13beaa405a1a30241caf70b26fd1a6cb222f41762a1c413f24` |
| records.py | `081e7b0b95b416e987bd873179e41152421ad73529163a33982ac8f8e6c2647e` |
| series.py | `d2c52ced97bbc78398420f22e40d24b3ee2cf88668a2d00ae0de6f46fdd07603` |
| source_flow.py | `a9faa6490ae30842180c39ef1e61cc555488ee26f2afe94319d0d215d2e296a5` |
| validated.py | `0a48f058b282197b9b4e6d5a99e36af578bcb9e6d036d9848d5513adc009c7d3` |
