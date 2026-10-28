# Pipeline companions and evidence catalog

The [current revision-8 guide](revision_8/README.md) links the updated article, companion and stage map. The assurance update is complete in that local successor; external anonymous delivery remains open.

The historical catalog in this directory supplies the pipeline index for the revision 6 companion PDF at `manuscript/revisions/20261027_revision_6/output/pdf/pipeline-supplement.pdf`. These are local release additions; the underlying scientific source/data archive is pinned at `f135faa390af8cf7f497e96407a03cae052662e7`. This is not a statement that the new documentation has already been pushed or delivered to referees.

**Subsequent kinetic-verifier qualification:** the [new guide](../kinetic-verifier/README.md) and [qualification report](../../data/processed/kinetic-verifier/20261027_portable_v1/QUALIFICATION_REPORT.md) document recovery of the exact historical implementation and a fresh portable check of all 16,365 saved cells, with nine negative controls. The companion PDF and reports below remain frozen historical records; this update does not describe their 822-check inventory as performing the stronger calculation. That historical update left the manuscript/supplement assurance work open; revision 8 now incorporates it. Anonymous evidence delivery remains open.

- `STAGE_MAP.json`: interpreted claim-to-test stages, inputs, gates, outputs and repository-relative locations, covering B1–B4, N1–N9 and three verification levels.
- `TEST_CATALOG.md`: searchable inventory of 210 top-level L001 folders and 107 eligible immediate child tests. Copied inputs/review snapshots are not extra experiments.
- `TEST_CATALOG.json`: normalized input/hash crosswalk, source locations, static gate excerpts, output/boolean records and bound predecessor references for the 317 entries. Resolve each `binding_groups[].artifact_ids` against the top-level `artifact_table`; `same_digest_locations` records alternative identical copies. The selected closure is broader than the mathematical chain because historical bindings flatten ancestors and authenticate controls.
- `ARCHIVE_CHECK.json`: streamed actual-byte inventory/hash check, no producers.
- `NEUTRAL_RECORD_CHECK.json`: 822 saved-record checks including 16,365 stored kinetic cells, no integration.
- `LOCAL_ALGEBRA_CHECK.json`: seven bounded symbolic/homogeneity checks.
- `DOCUMENTATION_CHECK.json`: locator, catalog, selected identity and exact terminal/majorant arithmetic checks; no source-domination or analytic-inverse proof audit.

Rebuild the catalog outside the raw archive:

```sh
python3 src/build_pipeline_catalog.py --output-dir /tmp/pipeline-catalog
```

Check the stage map and selected stored arithmetic:

```sh
python3 src/check_pipeline_documentation.py --output /tmp/pipeline-doc-check.json
```

The generator parses sources; it imports no scientific producer. A static gate excerpt is a navigation aid, not semantic certification. Inherited terminal flags and audit dispositions retain their original scope. An external/unmapped catalog binding may be a runtime object, an outside-line artifact or an unresolved locator; it is not silently supplied by a guessed file. The manifest-based crosswalk does not replace checking actual archive bytes.

The PDF gives exact launch formulas, per-stage scientific roles, algorithm/precision settings, failure policies, detailed final gates and remaining portability/access gaps. Historical producers retain absolute paths, runtime bindings, one-shot output rules and execution cutoffs. Do not execute them in the frozen evidence folders as though they were portable verification entry points.
