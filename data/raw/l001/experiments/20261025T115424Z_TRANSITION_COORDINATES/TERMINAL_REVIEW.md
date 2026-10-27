# Independent terminal review: failed coordinate enclosure

**Accepted terminal disposition: TECHNICAL_INCOMPLETE; transition-coordinate outcome inconclusive.** This is acceptance of the faithfully recorded failed run, not acceptance of any numerical threshold. No rescue or rerun is admitted. The accepted analytical predecessor map and counts remain unchanged.

## Actual evidence

I inspected the current admitted sources, ADMISSION.json, runtime start, controls, resource receipt, execution record, failure record and complete traceback. The source hashes match corrected admission and the runtime-start source record. The runtime record matches Python 3.12.3, flint 0.9.0, 256-bit precision, one library thread and both declared binary hashes.

The worker started at 2026-10-25T12:04:31.373618Z. Recorded admission used CPU 1, one core, about 28.9 GiB available memory, occupied CPU set [0], inherited CPU/line locks, 1 GiB virtual-memory cap and 600-second wrapper cap. EXECUTION.json records exit code 1 and child_reaped=true after 0.1867455419851467 seconds. The producer's own failure record is at 0.015770124970003963 seconds. These are different timing scopes, not a discrepancy.

CONTROLS.json records successful positive/negative-time constant and exponential inclusion controls, expected rejection of a too-small tube, and exact seed RHS inclusion. The traceback then identifies the n=1024 backward-background phase, at the strict TUBE_CONTAINMENT gate. No completed level record or RESULT.json exists in the inspected directory. The forward transfer, fine level and threshold-width/comparison gates were not reached. Final before/after runtime equality therefore was not completed; only initial authenticated runtime evidence exists.

## Cause and limits of diagnosis

The failed condition was the all-component strict inclusion of Y+dt*F(B) in B. The records do not identify the failing step index, coordinate, candidate interval, tube interval or containment margin. Therefore they do not support attributing this to a particular variable, interval wrapping, binary precision, ball-radius rounding, oversized integration step or physical trajectory behavior. Nor does fast failure prove that it occurred on the first step.

One useful analytical constraint on future diagnosis is available without rerunning: on the inherited background rectangle, the previously proved absolute derivative bounds are 231/100, 250009/67500, 1/50 and 294501/250000. Each is strictly below the frozen background tube rates 3, 5, 1/10 and 2. Consequently simply declaring the prescribed physical rate ceilings too small is not justified by the existing mathematical bounds. The interval implementation and its represented tube/candidate margins need examination. This observation does not locate the recorded failure or certify that arithmetic margins survive all implementation details.

The smallest useful subsequent diagnostic, if separately authorized, is to retain exact step/component and ball-endpoint containment evidence on a reproduction or isolate the relevant interval-construction/containment semantics. That is a prospective implementation/enclosure question, not an authorization here to instrument or rerun the sealed attempt. Increasing precision, rate ceilings or step counts before identifying the failed condition would be an unsupported rescue adjustment.

## Scientific disposition and closure

The single attempted numerical enclosure produced no accepted massless-threshold coordinates. It neither falsifies nor weakens the separately accepted analytical existence of the transition curve, the one-versus-two-mode classification, or conservative analytical coordinate bounds. It is a failure to complete this numerical certificate, not an adverse scalar-spectrum finding.

No numerical command, modified solver, hidden diagnostic run or new worker was executed by this reviewer. No threshold, precision, rate, source or prior result was changed. The execution receipt establishes that the producer child was reaped; the wrapper source has unconditional handle cleanup and no queued retry. I have not independently queried live host process/lock state in this audit; any final current-liveness statement should use the owner's live check rather than infer more than the recorded child completion. This reviewer turn ends with the terminal disposition above.

## Evidence SHA-256

| Artifact | SHA-256 |
|---|---|
| PLAN.md | 34eeeb988c01c9f19e103abb35c9110706e42ac86a21d1827b3fc5eee3f6cbd8 |
| producer.py | adc749e5ddbb448d55d70d8e004f41c47f5ec372197553d71b00fba0b0a1d93f |
| lease_run.py | b68edfaacfa5e62c006416d21d18b8ef7f4f49cf7cde4d649850d0e516a98793 |
| ADMISSION.json | d6ef9874ba65d08b3fc8ec32011cd62f1ec4707e315cf96b3137e7a1f0b7ae48 |
| RUNTIME_START.json | 156cdc124d922c577d6b708cf842f4dfa3a01d8b6c188370fc6ec0b25fc9a526 |
| CONTROLS.json | 1b2fd89da26c077ccc2001d05eccda78c5f9528203c66dea08b593deb65becc0 |
| FAILURE.json | 10c4a89f59eb6a326f6575cbc60c11e63ef6f4daac0a27598551e10a6d22bdc9 |
| EXECUTION.json | 3ae81b9aff42b1b898a7e4817978d66bbe254808f84b930613730b7f64304eff |
| RESOURCE_START.json | bc5f610c20db7cba6d884a3f4141af5a7c17838ea4e2fd5c06c22a39daf8cb62 |
| run.log | 0fc1f10dba181720330704f147324044669723810cbae902280246ff434bd1b7 |
