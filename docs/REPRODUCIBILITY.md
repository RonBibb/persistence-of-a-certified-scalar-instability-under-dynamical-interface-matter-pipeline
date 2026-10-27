# Imported pipeline and verification

This repository contains the generated combined-paper PDF, saved-record verification, bounded symbolic checks and historical numerical source. Raw data, processed evidence and run records are now under `data/` in this public-side working tree. These selected records are versioned with the pipeline repository.

From this public repository:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
python3 tests/check_local_algebra.py
```

The first command uses only the Python standard library. The second requires SymPy and prints its report by default. Saving a report requires an explicit `--output` destination.

Saved-record verification does not regenerate interval trajectories. Historical producers remain unqualified in this relocated layout and may retain historical runtime/path assumptions. No new solver or research-line test was launched by this import. Manuscript/TeX and image sources stay in the private root.

The 27 October L001 transfer additionally preserves its entire local experiment tree. Run `python3 src/verify_l001_archive.py --data-dir data/raw/l001 --manifest data/processed/l001/ARCHIVE_MANIFEST.json` to verify its pre-transfer bytes. Retrieve Git LFS numerical records before running this command in a future clone. The latest accepted scientific result is indexed by `data/processed/l001/CURRENT_RESULT.json`; earlier reports keep their historical scope and may describe successors as pending. Transfer verification is distinct from the recorded scientific audits and does not execute them. The manuscript PDF remains revision 5.

Git omits empty directories. The manifest retains their historical names; the verifier reports absent empty directories separately and still requires every archived file and every directory needed to contain those files. All byte, size and unexpected-file checks remain unchanged.
