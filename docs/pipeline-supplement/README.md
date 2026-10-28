# Pipeline guide and evidence catalog

Read the [current pipeline companion](../../manuscript/pipeline-supplement.pdf) with the [article](../../manuscript/paper.pdf). `STAGE_MAP.json` gives the current 17 interpreted stages, including exact inputs, gates, outputs and repository-relative locations.

- `TEST_CATALOG.json` and `TEST_CATALOG.md`: searchable inventory of 317 packet/test entries. Source/data identities and historical acceptance scopes remain unchanged.
- `ARCHIVE_CHECK.json`: historical streamed archive identity check.
- `NEUTRAL_RECORD_CHECK.json`: historical 822-check inventory, distinct from full Picard/Taylor saved-cell induction.
- `LOCAL_ALGEBRA_CHECK.json`: seven bounded symbolic/homogeneity checks.
- `DOCUMENTATION_CHECK.json`: historical catalog/locator and saved arithmetic report. Current path changes are checked by the current documentation checker; a historical report is not silently relabelled as a new execution.
- [Stronger verifier guide](../kinetic-verifier/README.md) and [qualification report](../../data/processed/kinetic-verifier/20261027_portable_v1/QUALIFICATION_REPORT.md).

From the public repository root:

```sh
python3 src/check_pipeline_documentation.py --output /tmp/pipeline-doc-check.json
python3 src/build_pipeline_catalog.py --output-dir /tmp/pipeline-catalog
```

These commands inspect saved data and parse source; no scientific producer is imported. The first also checks selected exact constants and the final observable gates. Catalog reconstruction does not regenerate scientific interval trajectories. The historical scientific base is `f135faa390af8cf7f497e96407a03cae052662e7`.

An anonymised inspection subset, guide and proof ledgers are available to editors/referees on request through the editorial office. It contains selected nonlinear sources/results and independently qualified saved checks, with actual inspection hashes distinguished from historical identities. It is not a complete fresh-producer closure.
