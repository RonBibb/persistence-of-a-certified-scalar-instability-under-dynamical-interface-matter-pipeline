# Paper A static proof reconstruction tests

Four newly implemented exact-rational saved-proof tests passed, with 13,567 baseline predicates and all 26 targeted corruption controls rejected for their intended reasons. Each test received a separate pre-execution gate and an independent postrun arithmetic audit. These results add independent confirmation of saved proof arithmetic; they are not new physical discoveries or fresh validated-flow calculations.

| Test | Reconstructed scope | Outcome |
| --- | --- | --- |
| Global cover | Exact 726-box adjacency; 19 dual curvature exclusions, 706 dual scalar exclusions, one root box; primary and independent Newton inclusion; event-bracket arithmetic | 11,389 predicates passed; 7 controls rejected |
| Isolation | Exact chain-rule and direct Jacobian determinant arithmetic for both producers; containment within archived outward bounds; positive determinants and overlapping event brackets | 30 predicates passed; 6 controls rejected |
| Uniform upper tension | Uniform Newton image, both determinants, signed responses, and all 693 transported fixed-D0 rows | 2,091 predicates passed; 7 controls rejected, with stated flow-record provenance premise |
| Central mode | Four exact endpoint signs and dual overlaps; six event-cell covers; exceptional-sector exclusion; independent norm and separation inequalities; final acceptance distinguished from provisional output | 57 predicates passed; 6 controls rejected |

All four owner runs used isolated CPython 3.14.4 on macOS, completed with return code zero and empty stderr, and preserved the copied source bytes. Negative controls operate on deep in-memory copies after hash validation, so their rejection tests semantic predicates rather than merely altered file hashes. The original input files, numerical producers and earlier failures were not changed.

## Quantitative confirmations

For the exact upper-tension interval lambda_b = -851862101055633/140737488355328 + delta, with delta in [-1/1000000,1/1000000], the reconstructed fixed-D0 residual floor is approximately 0.007727981462608436, strictly above 77/10000. The archived static responses are reproduced exactly from rational endpoints; their displayed enclosures are

- da/dlambda_b in [0.0000253637076666173, 0.00002554900876678758];
- dD/dlambda_b in [-9.289328770134265, -9.259257769725302].

The response signs follow from the declared wall residuals: G_lambda=-1/6, h_lambda=0, so a_prime=h_D/(6 det) and D_prime=-h_a/(6 det). This confirms a negative separation response along the local static family. It does not describe time evolution or select physical contraction. Local persistence across the tension interval remains distinct from full-launch exclusion at fixed D0; global first-event uniqueness is not extended across that interval.

For the central mode, the endpoint determinant signs are (+,-) in both implementations. A fresh alternating-series exponential enclosure gives rational kinetic-norm lower floors 136624249/312500000 and 2186303691/5000000000; both exceed 437/1000. The reviewer independently confirmed these inequalities with a different positive-series and geometric-tail construction. Both exact separation bounds lie inside (-219,-1997/500) under psi(0)=1. These conservative inequalities confirm positive norm and nonzero separation component, not a precise amplitude or a preferred perturbation sign.

## Execution environment check

A fifth, distinct test ran the two unchanged original portable-archive entrypoints under system CPython 3.9.6. After verifying their 171 unique bound files, both returned PASS with zero exit codes, empty stderr, and stdout byte-identical to their sealed CPython 3.14.4 results. This is same-host macOS compatibility for those two standard-library entrypoints. It is not Linux validation or numerical-library qualification. The independent environment audit is recorded separately from the four proof-arithmetic audits.

## Remaining premises and provenance

The global-cover records contain aggregate event brackets and derivative intervals, not every earlier-cell G sign enclosure or every internal zero-cluster cell. Full first-event flow history therefore remains inherited. The isolation check similarly assumes validity of the stored derivative intervals; it reconstructs the determinant arithmetic, not those derivatives' integration.

The two uniform tension flow records were newly snapshot-hashed and cross-checked against their recorded source and guard. No separate prior terminal digest of those whole flow records was identified. Exact agreement authenticates the compared arithmetic against the previously bound final result, not the unused fields or complete flow lineage. The tension audit is consequently a pass with that explicit provenance premise, not independent neighborhood-producer replication.

For the central mode, endpoint signs use the saved determinant enclosures. The physical reduction, continuity in the spectral parameter, same exact background, and validated spectral flow remain inherited. The old 288-checkpoint/native-Arb/runtime audit was not rerun here. Neither eigenvalue uniqueness, a complete spectrum, instability over the tension neighborhood, nor nonlinear fate follows.

The central-mode predecessor failure remains at `academic2-event-horizon/lin-central-validated-mode-20261005T165817Z/output/FAILURE.json`, SHA-256 `d3641e735465d48b9eae4efa3f6834b1fb88c288d1845e1741e8ae450b5e2a37`; it still reports the `fmpz` JSON-serialization error and `TECHNICAL_INCOMPLETE`. The bound tension proposal and result retain the earlier 4096-step and historical raw failures. Their direct failure-artifact lineage was not independently resolved in this round, and no different predecessor is substituted for them.

## Scientific and reproducibility maturity

The existing static and central-mode claims gain independently checked arithmetic beyond the previous authority-only and documentary coverage. Their scientific scope remains unchanged. No numerical producer, Linux workload, evolution, Cauchy-admission test, horizon calculation, manuscript edit or publication was performed.

After the fifth result, no further distinct qualified candidate was identified within this round's remaining window. A deeper producer test needs a new reviewed and resource-admitted plan with dependency and runtime qualification. The coordinator's read-only `importlib.util.find_spec('flint')` checks returned false under both isolated interpreters tested here, CPython 3.14.4 and 3.9.6; this does not rule out other environments elsewhere. No pinned Arb producer environment or Linux resource admission was established. Missing global first-event history and unresolved prior authentication of the full tension flow records are additional concrete gates. This is not a claim that all conceivable tests are exhausted.

The executable tests are `global_test.py`, `isolation_test.py`, `tension_test.py` and `mode_test.py`; their frozen designs and separate source manifests are adjacent. `runs/` preserves the owner's raw outputs and execution metadata. `INDEPENDENT_*_GATE.json` and `INDEPENDENT_*_AUDIT.json` contain the independent admission and audit records. `ENVIRONMENT39_RESULT.json` records the separate compatibility result. Replaying a scientific-record checker requires only its copied inputs and standard-library Python; the environment check additionally reads the prior portable archive.
