# Containment diagnostic outcome

**TECHNICAL_INCOMPLETE.** The single diagnostic replay reproduced the original containment exception, but its recorder failed before publishing the first failing step, component or interval margins. The cause of the original failure remains unresolved. No numerical transition coordinates were produced, and the analytical one-versus-two-mode classification remains unchanged.

## What executed

The independently admitted diagnostic imported the unchanged predecessor and called its original controls and backward step routine. It used the original seed, h=-1/102400, rates, RHS and Arb 256-bit runtime. The inherited controls and three strict-containment semantic controls passed.

At 2026-10-25 08:43:03 EDT, the one-core worker started on Linux CPU 0. It reproduced `TUBE_CONTAINMENT` in the original backward step. During exception handling, conversion of a candidate endpoint via `lower().fmpq()` raised `ValueError: fmpq requires an exact, finite value`. Neither `FIRST_FAILURE.json` nor `RESULT.json` was published. The recorder had not durably saved the step index or component; these cannot be reconstructed from the traceback alone.

The wrapper recorded exit code 1, a reaped child and 0.255583 seconds elapsed. The producer recorded 0.088537 seconds to its exception. These cover different scopes. No second attempt or production calculation ran.

## What this establishes

The original containment failure reproduces under the bound method and runtime. The additional evidence identifies an inadequate diagnostic serialization path: it assumes that each candidate endpoint is convertible to a finite exact rational. The failed conversion itself does not identify the numerical cause of the original containment failure or establish that the physical trajectory is invalid. Passing the fixed semantic controls does not certify semantics for the missing failed candidate.

The smallest next unblock is an exception-safe recorder that saves step/component identity and raw interval properties before attempting rational conversion, retaining per-field conversion failures. That would require a separately admitted diagnostic; no repair or replay is included in this closeout. Precision, rates, step counts and physical parameters have not been changed.

## Integrity and resource disposition

At 08:43:58 EDT the owner found no worker PID 1656307 and no held CPU-0 or L001 lease. The controller returned; no successor is queued. Manual digest reconciliation matched all 16 predecessor files, all three admitted diagnostic source files and both pinned runtime binaries. The program's final reconciliation gates were not reached; manual checks are recorded separately in `OWNER_RECONCILIATION.json`.

The original coordinate attempt and this diagnostic retain their separate failed classifications. Independent prospective review is in `PROSPECTIVE_REVIEW.md`; terminal review is recorded separately in `TERMINAL_REVIEW.md`.
