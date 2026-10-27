# Pipeline source

Read-only saved-record verification:

```sh
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
```

The supplied directory must contain `PACKAGE_MANIFEST.json` and its bound evidence tree. The verifier imports no interval producer, writes no data and launches no integration. A pass checks stored identities, terminal arithmetic and saved-cell coverage, not regeneration of interval trajectories.

`historical/` contains 26 byte-preserved anonymous inspection source files. Their relative source paths are retained; historical environment, file-layout, producer/input and execution assumptions remain. They are imported for subsequent pipeline organization and are not yet advertised as ready-to-run portable commands.

`../tests/check_local_algebra.py` contains the bounded symbolic checks. It prints a report; `--output /chosen/run/report.json` optionally saves one. These checks do not prove the full analytical theorem. Raw data, processed evidence and saved run outputs are now under `../data/` in this public-side working tree. They are versioned with this public repository.
