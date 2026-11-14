# Paper A: 14 November 2026 scientific records

This collection preserves the numerical sources, inputs, outputs, failed attempts
and full saved phase traces supporting the current JMP working draft. No new
scientific computation was performed to assemble it. Original files were copied
without editing; the private paper repository retains the reports, protocols,
input/output manifests and original-to-copy receipts.

| Directory | Contents |
|---|---|
| `families/runs/` | Both upper-wall parameter families, the separate two-parameter attempt, controls, failed cells, and their producer/checker Python and shell sources |
| `families/phase-traces/` | All 450 original primary/independent phase traces, recovered from Linux staging and verified against the original output manifest |
| `flat/NUMERICAL/` | Flat-slice exploratory counts, the interval background, controls, and superseded failed attempts |
| `derivation/CHECKS/` | Symbolic action/constraint checks and the retained failed predecessor |

The archived neutral background and phase engines are also in
`data/raw/neutral-certificates/` and `src/historical/`. The complete earlier
research archive remains in `data/raw/l001/`. These are relative to the pipeline
repository root, not to this directory. An external Python environment is still
required to run the original producers. Historical launchers retain their
machine paths and execution assumptions; collection is not a claim that every
historical command is now portable.

Retrieve Git LFS objects, then run from the repository root:

```sh
git lfs pull
python3 src/verify_paper_a_20261114.py
python3 src/verify_saved_records.py --data-dir data/processed/neutral-certificates
```

The first Python command verifies the collected file identities, including every
new phase trace and the current reading PDFs. The second checks the historical
822-predicate neutral saved-record package. Neither regenerates an interval
trajectory or establishes mathematical correctness from hashes.

`DATA_MANIFEST.json` is the collection manifest; it excludes itself to avoid a
self-hash. `TRACE_IDENTITIES.json` binds all 450 traces to the original recorded
hashes. Source identity and historical scientific acceptance are separate facts.

The unpublished Mishra and leading-order literature-model calculations are not
premises of the current manuscript. Their reports remain private; their missing
scratchpad scripts are explicitly recorded in the private cleanup report and
are not represented here as recovered numerical evidence.
