# Persistence of a certified scalar instability under dynamical interface matter — pipeline

Public pipeline companion to the private paper project. This repository is checked out as its `pipeline/` submodule.

The current article and **pipeline supplement** are [revision 8](docs/pipeline-supplement/revision_8/README.md), under `manuscript/revisions/20261027_revision_8/output/pdf/`. The [searchable test catalog](docs/pipeline-supplement/README.md) traces exact inputs, test-to-test dependencies, gates and outputs. Revision 8 incorporates bounded audit corrections and reconciles the saved-cell and internal proof-assurance scopes. Historical revision 6/7 PDFs and `manuscript/paper.pdf` (revision 5) are preserved. The scientific archive is pinned at `f135faa390af8cf7f497e96407a03cae052662e7`; the revision-8 release adds the publication assets and verifier qualification without rewriting that scientific baseline.

- `src/verify_saved_records.py`: read-only saved-evidence verifier with an explicit `--data-dir`.
- `src/verify_kinetic_cells.py` and `src/export_kinetic_verifier_bundle.py`: the separately qualified portable exact-Fraction saved-cell route; see [`docs/kinetic-verifier/README.md`](docs/kinetic-verifier/README.md).
- `src/historical/`: byte-preserved anonymous historical numerical source imports.
- `src/l001/experiments/`: relative source entry into the complete frozen L001 experiment archive; `SOURCE_INDEX.json` lists its Python/shell files.
- `src/verify_l001_archive.py`: standalone byte-identity checker for the L001 transfer manifest.
- `tests/check_local_algebra.py`: seven bounded symbolic checks, requiring SymPy.
- `configs/`, `docs/`: configuration templates and usage documentation.
- `data/`: selected raw records, processed evidence and saved run receipts.
- `manuscript/paper.pdf`: generated combined A–AB article, revision 5, in anonymous journal-review format.

Editable manuscript, TeX, bibliography, image sources, agent records and journal materials are held in the separate private project. The public dataset is a selected import, not the complete source/data closure. Historical producers have not been qualified for portable regeneration by this import.

The paper project assumed L001 ownership on 27 October 2026. Its entire local experiment tree, including failed cases and audit sources, is preserved under `data/raw/l001/experiments/`. Mixed frozen code/data packets remain intact to preserve relative imports and recorded hashes. `data/processed/l001/CURRENT_RESULT.json` identifies the accepted ninth-order result; it is incorporated in the revision 6 and later article PDFs, while the top-level legacy PDF remains revision 5. External dependencies remain separately owned. The archive is versioned here; numerical JSON/JSONL/arrays use Git LFS.

From this repository root:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
```

The verifier checks saved identities, terminal arithmetic and stored-cell coverage. It imports no numerical producer and does not regenerate interval trajectories. Read `docs/REPRODUCIBILITY.md` for scope and limitations. Historical dispositions retain their original scope; public availability does not establish external peer review.

The stronger kinetic verifier has now been recovered and locally qualified in a separate relocated run: 16,365 cells, 64 chunks, all seven original coarse gates and nine negative controls. See the [qualification report](data/processed/kinetic-verifier/20261027_portable_v1/QUALIFICATION_REPORT.md). This is exact-rational inductive saved-certificate verification, distinct from the inventory command above and from fresh interval-trajectory regeneration. Revision 8 supplies the coordinated assurance update, preserving revision 7 and the revision-6 companion. A separately qualified anonymous inspection subset has been prepared locally; external referee delivery remains open. The revision-8 release includes the recovered verifier, qualification evidence and current PDFs. The anonymous inspection ZIP and editable sources remain in the private parent repository.

Verify the relocated L001 archive separately:

```sh
python3 src/verify_l001_archive.py --data-dir data/raw/l001 --manifest data/processed/l001/ARCHIVE_MANIFEST.json
```

This checks every original experiment file against its pre-transfer SHA-256. It executes no scientific producer and does not re-prove the numerical conclusions.

When committing this archive, use `git add -f -- data/raw/l001` from the pipeline root: preserved nested historical `.gitignore` files hide some frozen checkpoints from an ordinary add. `data/processed/l001/FORCE_ADD_PATHS.txt` lists those original records. Force-adding the archive preserves their bytes; it does not rewrite the historical ignore files. Transfer and publication receipts distinguish the original local relocation from later Git publication.
