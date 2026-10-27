# Pipeline data

- `raw/`: selected original, unredacted scientific records.
- `processed/`: anonymous inspection copies and their bound manifests.
- `runs/`: saved execution, validation and layout receipts.

The entire folder was relocated from the private root without changing any pre-existing file contents. Historical paths and receipt statements inside those records retain their original scope. The inspection package’s `article.pdf` is a relative link to `manuscript/paper.pdf` in the pipeline repository.

Run saved-record verification from the pipeline repository root:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
```

This verifies saved identities, terminal arithmetic and stored-cell coverage; it does not regenerate interval trajectories. The current dataset is a selected import, not the complete source/data closure. The folder relocation itself preserved the scientific record contents. Those records are now versioned with the public pipeline repository.
