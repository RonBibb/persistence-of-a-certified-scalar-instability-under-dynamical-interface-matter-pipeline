# Uniform tension trace history and provenance

The sixth test passed for both saved uniform-flow traces: 32,768 cells, 131,092 predicates, four source/guard anchor links, and three targeted negative controls. The owner run completed at 00:44:50Z with return code zero and empty stderr. The preceding completed test packet and all original evidence remain unchanged.

For both the root-box and center flows, exact rational G bounds are positive in every cell before 16363, contain zero precisely in cells 16363 and 16364, and are negative in every subsequent cell. G_s is strictly negative throughout that event cluster. The exact event bracket is [16363/8192,16365/8192]. Cell ordering, positive recorded warp lower bounds, and containment of the cluster interval hulls within the saved aggregate event enclosures also pass. Recorded finite-state, first-integral and Picard flags were checked for consistency; the underlying interval operations were not regenerated.

The controls reject an inserted negative pre-event G interval, a zero-reaching event G_s interval, and a corrupted trace hash for their intended reasons. The two semantic controls bypass file hashes, so they test the history predicates themselves.

## What the binding establishes

Each complete-flow RESULT.json contains the SHA-256 of its CELLS.json, the producer-source digest, and the frozen guard. Those links match the copied traces, the original source bound by BINDINGS, and the FREEZE/terminal chain. This demonstrates present saved-record consistency, including a full observational event history for these two uniform tension flows. It does not regenerate their interval enclosures or supply the separate global-cover cell history.

Historical authentication of the whole flow-result bytes remains unresolved. The inspected producer writes plain immutable completed-flow RESULT.json files and stores trace hashes inside them; it does not emit content-addressed flow-result filenames. Searching all 12 original top-level row JSON records found neither whole-flow digest:

- uniform_root: `50c93673b5d9689474e5d9748cc9a87de2fe4b0b37bcd821c540809fa912b4c7`;
- uniform_center: `c1406ababd03dd97736b928adf9aeffe494ef14321516000135d652e4d9e529c`.

This bounded negative finding does not prove that no external historical record exists. A trace hash inside an otherwise unauthenticated flow result cannot authenticate that enclosing result. The prior integrity receipt records that its original check passed, but does not contain those two digests. The new result therefore retains the flow-snapshot provenance premise of the preceding tension test.

The added assurance is independently testable saved trace-history consistency, not a new physical result, an independent numerical producer, or historical authentication supplied by matching internal fields. No Linux access, original-source edit, IVP integration, dynamical conclusion or horizon inference was involved. `RESULT.json`, `RUN_METADATA.json`, `SOURCE_BINDINGS.json`, `BOUNDED_PROVENANCE_SEARCH.json` and the independent gate/audit records provide the supporting evidence.
