# Persistence of a certified scalar instability under dynamical interface matter — pipeline

Public pipeline companion to the private paper project. This repository is checked out as its `pipeline/` submodule.

- `src/verify_saved_records.py`: read-only saved-evidence verifier with an explicit `--data-dir`.
- `src/historical/`: byte-preserved anonymous historical numerical source imports.
- `src/l001/experiments/`: relative source entry into the complete frozen L001 experiment archive; `SOURCE_INDEX.json` lists its Python/shell files.
- `src/verify_l001_archive.py`: standalone byte-identity checker for the L001 transfer manifest.
- `tests/check_local_algebra.py`: seven bounded symbolic checks, requiring SymPy.
- `configs/`, `docs/`: configuration templates and usage documentation.
- `data/`: selected raw records, processed evidence and saved run receipts.
- `manuscript/paper.pdf`: generated combined A–AB article, revision 5, in anonymous journal-review format.

Editable manuscript, TeX, bibliography, image sources, agent records and journal materials are held in the separate private project. The public dataset is a selected import, not the complete source/data closure. Historical producers have not been qualified for portable regeneration by this import.

The paper project assumed L001 ownership on 27 October 2026. Its entire local experiment tree, including failed cases and audit sources, is preserved under `data/raw/l001/experiments/`. Mixed frozen code/data packets remain intact to preserve relative imports and recorded hashes. `data/processed/l001/CURRENT_RESULT.json` identifies the accepted ninth-order result; it is not yet incorporated into the generated paper PDF. External dependencies remain separately owned. The archive is versioned here; numerical JSON/JSONL/arrays use Git LFS.

From this repository root:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
```

The verifier checks saved identities, terminal arithmetic and stored-cell coverage. It imports no numerical producer and does not regenerate interval trajectories. Read `docs/REPRODUCIBILITY.md` for scope and limitations. Historical dispositions retain their original scope; public availability does not establish external peer review.

Verify the relocated L001 archive separately:

```sh
python3 src/verify_l001_archive.py --data-dir data/raw/l001 --manifest data/processed/l001/ARCHIVE_MANIFEST.json
```

This checks every original experiment file against its pre-transfer SHA-256. It executes no scientific producer and does not re-prove the numerical conclusions.

When committing this archive, use `git add -f -- data/raw/l001` from the pipeline root: preserved nested historical `.gitignore` files hide some frozen checkpoints from an ordinary add. `data/processed/l001/FORCE_ADD_PATHS.txt` lists those original records. Force-adding the archive preserves their bytes; it does not rewrite the historical ignore files. Transfer and publication receipts distinguish the original local relocation from later Git publication.
