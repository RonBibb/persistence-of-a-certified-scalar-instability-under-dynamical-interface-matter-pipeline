# R1 prospective refinement confirmation

## Antecedent retained

The frozen first replay completed without exception. Its 4,096-step
interval-Newton image was wider than the frozen root box, while its 8,192-step
image was a strict self-map and all independently generated geometry gates
passed. Because the first contract required both levels, its classification
remains `INDEPENDENT_D1_REPLAY_NOT_ESTABLISHED`.

## R1 question and unchanged method

Does the proof-bearing 8,192-step inclusion reproduce and tighten at 16,384
steps under the same independent engine?

R1 changes only the declared step pair from `(4096,8192)` to
`(8192,16384)`. It retains without change:

- the action, exact binary64 inputs, root center, and narrow root box;
- Arb precision 768 bits;
- fifth-order independent Taylor-jet propagation;
- Picard cell self-containment;
- every root and derived-geometry gate in `CONTRACT.md`; and
- the same classification logic requiring **both** declared levels to pass.

The engine is the already frozen independent source with SHA-256
`d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044`.
It imports no original D1 producer and consumes no original D1 enclosure. The
R1 wrapper only sets the two prospective step counts before invoking that
engine.

The failed 4,096-step record is not overwritten or reclassified. No further
step-count change is authorized within this hour.

