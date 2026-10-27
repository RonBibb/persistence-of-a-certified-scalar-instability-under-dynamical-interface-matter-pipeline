# Persistence of a certified scalar instability under dynamical interface matter — pipeline

Public pipeline companion to the private paper project. This repository is checked out as its `pipeline/` submodule.

- `src/verify_saved_records.py`: read-only saved-evidence verifier with an explicit `--data-dir`.
- `src/historical/`: byte-preserved anonymous historical numerical source imports.
- `tests/check_local_algebra.py`: seven bounded symbolic checks, requiring SymPy.
- `configs/`, `docs/`: configuration templates and usage documentation.
- `data/`: selected raw records, processed evidence and saved run receipts.
- `manuscript/paper.pdf`: generated combined A–AB article, revision 5, in anonymous journal-review format.

Editable manuscript, TeX, bibliography, image sources, agent records and journal materials are held in the separate private project. The public dataset is a selected import, not the complete source/data closure. Historical producers have not been qualified for portable regeneration by this import.

From this repository root:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
```

The verifier checks saved identities, terminal arithmetic and stored-cell coverage. It imports no numerical producer and does not regenerate interval trajectories. Read `docs/REPRODUCIBILITY.md` for scope and limitations. Historical dispositions retain their original scope; public availability does not establish external peer review.
