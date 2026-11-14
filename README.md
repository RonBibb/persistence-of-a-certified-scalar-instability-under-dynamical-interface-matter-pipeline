# Persistence of a certified scalar instability under dynamical interface matter - pipeline

Public pipeline companion to the private paper project. This repository is checked out as its `pipeline/` submodule.

- [Current JMP working article](manuscript/JMP_scalar_instability_article.pdf), 41 pages including proofs and references.
- [Current JMP working supplement](manuscript/JMP_scalar_instability_supplement.pdf), 26 pages.
- [Collected 14 November sources, data and full phase traces](data/raw/paper-a-20261114/README.md).
- [Preserved submitted article](manuscript/paper.pdf) and [historical pipeline guide](manuscript/pipeline-supplement.pdf).
- [Pipeline map and searchable catalog](docs/pipeline-supplement/README.md).
- [Qualified exact-Fraction verifier](docs/kinetic-verifier/README.md).
- [Reproducibility boundaries and commands](docs/REPRODUCIBILITY.md).

The JMP files are unsubmitted author working copies, not anonymous submission files or a tagged publication release. The previously submitted files retain their original names and bytes. The `pre-cleanup-20261027` tag preserves the preceding publication layout. Editable manuscript/TeX, bibliography, image sources, agent records, referee ZIP and journal materials are held in the private parent.

Scientific source/data remain intact under `data/`, including all failed and superseded L001 runs. `src/l001/experiments/` is a relative entry into `data/raw/l001/experiments/`, not a second dataset. Numerical JSON/arrays use Git LFS: retrieve those objects before checking the data. The historical scientific archive is pinned at `f135faa390af8cf7f497e96407a03cae052662e7`; publication commits identify subsequent documents and qualified checking routes.

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
python3 src/verify_paper_a_20261114.py
python3 src/verify_l001_archive.py --data-dir data/raw/l001 --manifest data/processed/l001/ARCHIVE_MANIFEST.json
```

The first command checks 822 saved-record predicates, including stored kinetic-cell hull coverage. The stronger exact-Fraction route separately verified all 16,365 saved Picard/Taylor cells, 64 chunks and seven coarse gates, with nine rejection controls. Neither operation regenerates every scientific interval trajectory. Internal review is not external human peer review. The article and companion state the retained mathematical and historical-execution premises.

An anonymised inspection package, guide and proof ledgers are supplied to the editor and referees on request through the editorial office. This identified public repository is not an anonymous delivery channel.

The L001 archive's preserved nested ignore rules hide some records from an ordinary add. Its transfer manifest and `data/processed/l001/FORCE_ADD_PATHS.txt` retain the original inventory; do not remove failed cases or rewrite historical gate definitions.

The 14 November preservation pass restores the historical inspection package's
manifest-bound `article.pdf` as an ordinary file. It is no longer a symlink to a
different reading revision. The historical manifest and the submitted PDF are
unchanged. The new collection's sources and records are covered by
`data/raw/paper-a-20261114/DATA_MANIFEST.json`; full producer portability and a
public DOI release remain separate work.
