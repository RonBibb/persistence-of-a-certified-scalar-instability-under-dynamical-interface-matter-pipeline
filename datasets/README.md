# Optional dataset repositories

Action and constraint checks live in the independently versioned public repository https://github.com/RonBibb/paper-A-action-constraint-checks.

Initialize its pinned checkout after cloning this pipeline:

```sh
git submodule update --init datasets/action-constraint-checks
```

The historical `data/raw/paper-a-20261114/derivation/CHECKS` path is a relative symlink to this checkout. The original collection DATA_MANIFEST.json remains unchanged. A clone without this optional submodule will not have the CHECKS files available and cannot complete collection verification until initialization. Published Git history is preserved; this split does not remove historical bytes or change other datasets.

## Flat-background numerical evidence

Repository: https://github.com/RonBibb/paper-A-flat-background-numerics.

```sh
git submodule update --init datasets/flat-background-numerics
```

The historical `data/raw/paper-a-20261114/flat/NUMERICAL` path links to this pinned checkout. All 113 original files and collection-manifest identities are preserved. See the dataset README for Linux/Python and python-flint runtime requirements and the distinction between exploratory outputs and certificates. Initialize both dataset submodules before full collection verification.

## Kinetic verifier qualification evidence

Historical qualification receipts: https://github.com/RonBibb/paper-A-kinetic-verifier-evidence. Initialize `datasets/kinetic-verifier-evidence` with `git submodule update --init datasets/kinetic-verifier-evidence`. The old `data/processed/kinetic-verifier` path is preserved by a relative symlink. Inputs and executable verification tools remain in the main pipeline; see `docs/kinetic-verifier/README.md`. The dataset is an evidence archive, not a complete reproduction bundle. All original platform disclosures and failures are preserved.

## L001 research archive

Repository: https://github.com/RonBibb/paper-A-l001-research-data. This dataset preserves the full historical experiment archive, including adverse results, together with its processed manifest and result index.

```sh
git submodule update --init datasets/l001-research-data
git -C datasets/l001-research-data lfs pull
python3 src/verify_l001_archive.py --data-dir data/raw/l001 --manifest data/processed/l001/ARCHIVE_MANIFEST.json
```

The old raw and processed L001 paths are relative compatibility links into the submodule. Its data remain optional for a lightweight checkout; archive and full catalog checks require initialization. Scientific producer portability and claim limits are unchanged. Published Git/LFS history is retained.
