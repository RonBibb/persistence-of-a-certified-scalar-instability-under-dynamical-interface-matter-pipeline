# Imported pipeline and verification

This repository contains the generated combined-paper PDF, saved-record verification, bounded symbolic checks and historical numerical source. Raw data, processed evidence and run records are now under `data/` in this public-side working tree. These selected records are versioned with the pipeline repository.

From this public repository:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
python3 tests/check_local_algebra.py
```

The first command uses only the Python standard library. The second requires SymPy and prints its report by default. Saving a report requires an explicit `--output` destination.

Saved-record verification does not regenerate interval trajectories. Historical producers remain unqualified in this relocated layout and may retain historical runtime/path assumptions. No new solver or research-line test was launched by this import. Manuscript/TeX and image sources stay in the private root.

## Qualified exact-Fraction saved-cell route

The [kinetic verifier guide](kinetic-verifier/README.md) supplies an exporter and new portable launcher for the exact historical implementation. A fresh read-only relocated execution passed all 16,365 cells in 64 chunks, all seven coarse gates and nine representative rejection controls. The [new qualification report](../data/processed/kinetic-verifier/20261027_portable_v1/QUALIFICATION_REPORT.md) and its source/input freeze distinguish this execution from historical receipts. Source, plan, candidate and two admission-linked review receipts missing from the imported tree have been recovered with their exact recorded hashes.

This operation reconstructs exact-rational Picard/Taylor containment from the saved cells. It does not run the original producer, re-establish root existence, independently prove the analytical kinetic theorem or audit the nonlinear source/inverse estimates. The 822-check command above remains an inventory/terminal-arithmetic operation and must not be described as performing this stronger check. Historical qualification receipts retain their original scopes. The current article and companion incorporate the completed assurance update. An anonymised inspection package and guide are supplied to editors/referees on request through the editorial office; a standing anonymous download service is not claimed.

The 27 October L001 transfer additionally preserves its entire local experiment tree. Run `python3 src/verify_l001_archive.py --data-dir data/raw/l001 --manifest data/processed/l001/ARCHIVE_MANIFEST.json` to verify its pre-transfer bytes. Retrieve Git LFS numerical records before running this command in a future clone. The latest accepted scientific result is indexed by `data/processed/l001/CURRENT_RESULT.json`; earlier reports keep their historical scope and may describe successors as pending. Transfer verification is distinct from the recorded scientific audits and does not execute them. The current article is `manuscript/paper.pdf`, and its companion is `manuscript/pipeline-supplement.pdf`.

Git omits empty directories. The manifest retains their historical names; the verifier reports absent empty directories separately and still requires every archived file and every directory needed to contain those files. All byte, size and unexpected-file checks remain unchanged.

## Process guide

See [`pipeline-supplement/README.md`](pipeline-supplement/README.md) for the companion PDF, interpreted stage map and searchable 317-entry packet/test catalog. The supplement supplies exact launch formulas, precision/step settings, per-stage inputs/gates/outputs, failed-predecessor policy and the five final nonlinear observable gates. It distinguishes record inspection from fresh producer regeneration. Its documentary reports do not independently establish the sharpened source-domination or analytic-inverse premises.

The added catalog/check commands read source and saved data without importing scientific producers:

```sh
python3 src/build_pipeline_catalog.py --output-dir /tmp/pipeline-catalog
python3 src/check_pipeline_documentation.py --output /tmp/pipeline-doc-check.json
```

The catalog builder and documentation checker require Python 3.11 or later. The working tree keeps only current publication PDFs; Git preserves earlier versions. The historical raw archive remains intact.
