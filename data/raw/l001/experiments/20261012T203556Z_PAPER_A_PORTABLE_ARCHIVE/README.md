# Paper A portable saved evidence archive

This packet supplies a working, byte-preserving archive for two original read-only verifiers and an offline selection of the evidence for all seven Paper A claims. Both verifiers passed from the primary and relocated archives on macOS, and an independent auditor reproduced all four results directly through the original entrypoints. The completed scope is authority-record replay and exact reconstruction from saved proof records. It is not the complete recursive archive or producer replication for the paper.

## Replay the archive

Copy this entire packet to the desired location. The replay wrapper and its two layer manifests are top-level siblings of `archive/`; copying only `archive/` omits the wrapper manifests. No canonical source checkout, historical Academic2 directory, staging script, network service, or third-party Python package is needed for replay. The executed environment was CPython 3.14.4 on macOS. Other operating systems and Python versions have not been tested in this packet.

From any unrelated working directory, substitute the copied packet's absolute path:

```sh
python3 -I -B /absolute/path/to/copied-packet/replay.py --layer authority
python3 -I -B /absolute/path/to/copied-packet/replay.py --layer consolidation
```

Both commands must return zero and print JSON with `"status": "PASS"`. The authority output must report 23 of 23 checks. The consolidation output must show 14 matching hash anchors, six manifests without mismatches and with matching terminal bindings, 11 true D1 checks, and 12 true D2A checks. Its `root` field correctly changes when the archive is relocated, so full stdout hashes are location-dependent for that layer.

The wrapper verifies every byte listed in the selected layer manifest, rejects symlinks and path escapes, and invokes the unchanged original verifier with isolated Python and bytecode disabled. Each original verifier resolves `branches/02-event-horizon/...` relative to the staged archive. Historical absolute paths inside copied records are provenance text and are not consulted by the replay entrypoints.

The saved relocation copy is `relocated/archive/`. To replay it, add `--archive /absolute/path/to/copied-packet/relocated/archive`. The owner and auditor used `/private/tmp` as their unrelated working directory. `run_pair.py` is the reviewed macOS capture driver, not a required end-user entrypoint. The `stage_*.py` scripts and `build_closure_map.py` reproduce packaging from the canonical source layout; they are not needed or intended to run in a distributed copy without those sources.

## Results and files

| Layer | Staged scope | Executed result |
| --- | --- | --- |
| Authority | Original publication-upgrade verifier, unchanged BINDINGS, 17 bound records | 23/23 predicates passed in both locations |
| Consolidation | Original verifier, 14 anchors, six manifest closures, 86 checkpoints | Exact D1 Newton inclusion and nesting, exact 693-box D2A cover, exclusions and residual floor, checkpoint content addresses passed in both locations |
| Documentary | All 21 selected source records, original claim map and contribution; 11 reused and 12 added files | Offline evidence access and byte-identity checks only |

The union contains 183 unique files totaling 165,140,004 bytes. `ARCHIVE_UNION_MANIFEST.json` maps each archived path to its original path relative to the L001 experiments directory, unchanged SHA-256, byte count, and role. `AUTHORITY_ARTIFACT_MANIFEST.json`, `CONSOLIDATION_ARTIFACT_MANIFEST.json`, and `DOCUMENTARY_ARTIFACT_MANIFEST.json` distinguish the scopes. The documentary map's `evidence_key` resolves references from the original claim map without rewriting its historical absolute links.

`runs/` contains the owner's raw stdout, stderr and execution metadata. `independent_runs/` contains the independent direct-entrypoint outputs. `INDEPENDENT_TERMINAL_AUDIT.json` records the four independent PASS results and the byte, confinement, metadata, and output comparisons. All verifier stderr streams were empty. Shell initialization emitted an unrelated RVM `ps` permission warning before the owner's commands; it was outside the captured Python verifier streams and did not affect their zero return codes.

## Claim coverage and remaining work

`CLAIM_CLOSURE_MAP.json` distinguishes offline availability from executed proof coverage for each of the seven selected claims. The global 726-box first-event uniqueness and the two-variable isolation result remain authority-record checks in this packet. The later tension result and accepted central negative mode are available as documentary evidence only. The staged reduction text is hash-bound, not symbolically rederived.

The next full-archive work is to close the producers' recursive imports and bound input records, preserve required failed predecessors, pin numerical arithmetic environments, and review separate producer-replay commands. The independent D1 engine imports `flint`; its numerical execution is not supplied by these standard-library verifiers. Global uniqueness, isolation, tension, and spectral dependencies each require their own closure. The original lower-tension constructor/N65 provenance also needs recursive packaging. The D2A evidence still has one full producer with an independent saved-cover audit.

Linux replay, ODE regeneration, a second full D2A producer, new parameter or spectral tests, manuscript compilation, bibliography review, and publication were not performed. Full selected-paper proof-archive completeness remains false. See `REPRODUCIBILITY_CONTRIBUTION.md` for paper-facing wording and the precise assurance boundary.
