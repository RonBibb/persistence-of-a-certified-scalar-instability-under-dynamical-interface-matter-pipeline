# T2 first-failure terminal review

**ACCEPTED — PASS_FAILURE_CAPTURE.** The original first-step failure is now localized to a nonfinite scalar-acceleration interval evaluation, not to an evolved trajectory or an unidentified component. A particular power/operator cause is not yet established by this capture.

I inspected the result, execution, raw identity, original-frame data and component detail records against the admitted source. The recorded first failure is backward step 1 at time 0, with zero completed steps and h=-1/102400. All initial values, dt and all four original tube balls are finite. The original derivative balls for a, H and Phi are finite; the original derivative for T is explicitly nan with finite=false. The T candidate is likewise nan and its strict containment predicate is false. Other three candidate predicates are true and agree with exact rational endpoint containment, with strictly positive recorded inward margins.

This is stronger than the previous failed recorder's evidence: the nonfinite derivative is explicitly present in the actual original step frame, not inferred from a conversion exception. The safe recorder retains its nan metadata and rational-conversion errors without aborting. It also preserves the exact first-step/component identity. Source structure identifies the affected evaluation as T'=1-Phi+4*Phi**3-4*H*T on a finite zero-crossing Phi tube. T2 does not isolate the intermediate expression or justify attributing the issue specifically to exponentiation. That requires a separately admitted expression-level discriminator.

No evolution step was accepted, so accumulated integration error, a late trajectory instability or a genuinely singular background cannot explain this recorded first-step event. The underlying polynomial is defined on the finite input box; the captured event is an interval-expression evaluation failure. This does not by itself prove a library defect, a particular API semantic, or that a replacement expression will complete the numerical certificate.

The producer records successful inherited controls and parent/source/runtime invariance gates. Current own source hashes match admission. Execution began 14:17:39.792016Z, before cutoff, on one core CPU0; child 1671129 exited zero and was reaped after 0.29170837509445846 seconds. No coordinate result, repaired integration or new spectrum was produced. The analytical transition map and both previously failed packets remain unchanged.

| Artifact | SHA-256 |
|---|---|
| PLAN.md | c965a250fda847a3195d907e00e5a3f0ff025cec7ac98220d8dc39306372f4d0 |
| producer.py | 0a17d893b2e5da0c1ac8a170da1c97b42ccbbac79d11ad69ba07fa3568852f1b |
| lease_run.py | 7e255cadc28a3adce7f56dd5c1c6a47c7d2313b874bdf79b21cbc8c881c02275 |
| RESULT.json | d55dd08e37498fd658e6aaa99f0b7040bb952a5d5be1e64ec7cc27ada846663b |
| EXECUTION.json | 7374c9bd2e8ad4bdc07d2eecb264c03cffdeafe87f776276f20f19d9b1f671a3 |
| FAILURE_IDENTITY.json | 9f10e4e4c0078d6b9798524ba0cdaac26b421631391952e74f939e25316b8df0 |
| ORIGINAL_RAW.json | f50ab32e8760c1069d5fe29fc2f6c21882591faacc42425456f911b91b7f0fab |
| FIRST_FAILURE.json | 0a2779367caa298852ac88d47ec7d028b3953a2efa2309d6953cba9d4a58e70f |

This independent agent review performed no numerical work. An expression-isolation study is justified prospectively, but no T3 source or plan is admitted by this terminal review.
