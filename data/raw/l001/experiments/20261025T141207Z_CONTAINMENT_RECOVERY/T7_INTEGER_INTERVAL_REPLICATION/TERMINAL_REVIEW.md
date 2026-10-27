# T7 integer-interval terminal review

**ACCEPTED — PASS_INTEGER_INTERVAL_REPLICATION.** A separately implemented outward interval arithmetic and independently transcribed RHS reproduce compatible transition enclosures without Arb. The result still shares the exact physical model, mathematical enclosure method, Python runtime and analytical classification.

I inspected result, controls, level records, execution and current source hashes against the admitted arithmetic proof. The qualification records 33 arithmetic corner checks, outward rational conversion, zero-divisor rejection, signed constant/exponential controls, undersized-tube rejection and exact seed agreement. This matches 27 addition/subtraction/multiplication corner cases and six nonzero-divisor cases from the declared fixed interval set.

Both resolutions completed: 3072 plus 6144 steps, the frozen total 9216. Fine Hamiltonian and determinant-defect rational intervals each have negative lower and positive upper endpoints. Published level/result gates require strict whole-step containment, exact background/transfer bounds, determinant positivity, width <=1e-4, fine/coarse consistency and overlap with all four T4 transfer entries and all three thresholds. The inspected independent integer operations establish outwardness rather than using T4 overlap as the only validation. No Arb calls or imported T4 RHS/step functions occur in this producer.

The accepted fine rational threshold intervals are reproduced verbatim in RESULT.json and LEVEL_2048.json:

| Threshold | Lower endpoint | Upper endpoint |
|---|---|---|
| Lower only | 4043739016539504902413409540795436672115146771393056933881930929582761619409/115792089237316195423570985008687907853269984665640564039457584007913129639936 | 2022307549670369775032029819168917963350971571961558152356766613194956007421/57896044618658097711785492504343953926634992332820282019728792003956564819968 |
| Upper only | 1186394478948641234450395567982099134682700606281941593631551767615782041207/28948022309329048855892746252171976963317496166410141009864396001978282409984 | 1186626045914159296444551536644432552734659924635507367995081949658740218997/28948022309329048855892746252171976963317496166410141009864396001978282409984 |
| Equal each | 10613708548885/562949953421312 | 26539757761971/1407374883553280 |

These independent enclosures are not replaced by intersections with T4 or T6. Fixed-point 256 fractional bits is explicitly different from Arb's floating midpoint precision; agreement does not mean bitwise-identical trajectories or equal uncertainty widths. Equal-wall root enclosure uses independent exact polynomial-envelope bisection, not Arb square-root evaluation.

Execution began 14:33:56.744344Z before cutoff, used one core CPU0, exited zero and reaped child 1674044 after 1.2460078340955079 seconds. Current producer and interval-module hashes match admission. Source/input/runtime invariance is recorded passed. This agent performed no numerical rerun; audit scope is source/arithmetic reasoning and recorded certificate evidence.

T4, T6 and T7 now supply the original-route certificate, a different transfer-composition route and an independently implemented arithmetic certificate. No further fidelity or parameter scan is indispensable to the bounded coordinate-validation claim. A separately admitted conservative-union interpretation of placement/coupling could add an intelligible scientific decomposition; it should not become an excuse for unbounded validation rounds. Actual masses, nonlinear outcomes and other sectors remain new research questions, not missing gates for this certificate.

| Artifact | SHA-256 |
|---|---|
| RESULT.json | 6ebdeb8d4d8eca580689f97eca98fffd0b525f1fa07faed8dafb12d8e851bfcc |
| LEVEL_1024.json | 21771f7af40809f7a157ad915e981b816f7de3e89b35e281e751971617bedb99 |
| LEVEL_2048.json | 412a6b6e8bcbca1390a2c78d0510a3040fde6d6d7ee8df9c8152893c01e28ecb |
| CONTROLS.json | 302bbe3ccac1bc4a522677f9154484b4403abfa03aae057b8febe44fabd5c483 |
| EXECUTION.json | c905e6881702b561d7df5af0fad24de1ef64b5bba4a78e107d50432f739177fe |
| producer.py | f0a252dc4efbe42b975d7d044be01d5c3e398df009b43dc7ca030c9835c1e56b |
| interval.py | b64469c934e75648717365a1d10ddfb2b2ee5e494b17ee2acf4d2ab27f658c1f |

No repair or further numerical validation is requested. Any T8 remains subject to separate prospective admission.
