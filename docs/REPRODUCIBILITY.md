# Imported pipeline and verification

This repository contains the generated combined-paper PDF, saved-record verification, bounded symbolic checks and historical numerical source. Raw data, processed evidence and run records are now under `data/` in this public-side working tree. These selected records are versioned with the pipeline repository.

From this public repository:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
python3 tests/check_local_algebra.py
```

The first command uses only the Python standard library. The second requires SymPy and prints its report by default. Saving a report requires an explicit `--output` destination.

Saved-record verification does not regenerate interval trajectories. Historical producers remain unqualified in this relocated layout and may retain historical runtime/path assumptions. No new solver or research-line test was launched by this import. Manuscript/TeX and image sources stay in the private root.
