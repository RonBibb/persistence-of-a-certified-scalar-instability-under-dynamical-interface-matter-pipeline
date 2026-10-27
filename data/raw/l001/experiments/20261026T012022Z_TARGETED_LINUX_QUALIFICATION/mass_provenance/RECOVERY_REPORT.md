# Historical central mass certificate: recovered platform evidence

Documentary recovery only, 2026-10-26. No numerical replay, hash calculation, or audit was executed for this report.

## Conclusion

The accepted R1 mass producer has direct historical Linux execution evidence. The computational auditor has a source-bound successful receipt whose executable and library gates require the recorded Linux runtime, but its original invocation/process receipt was not recovered. These are different strengths of provenance; neither should be described as an unqualified new Linux revalidation.

## Accepted producer receipt

Original transcript:
`/Users/ronbibb/.codex/sessions/2026/09/01/rollout-2026-09-01T19-56-16-01a0543c-b99b-72e2-b0c2-ca518a4dd5d1_01a05f66-ee84-7991-998a-fa0acac11eed.jsonl`

CommandExecution ordinal **91336**, timestamp **2026-10-05T17:32:45.491Z**, start **1791221514437 ms**, completion **1791221565491 ms**, exit **0**. The actual command was:

```sh
ssh linux.vm 'env PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH=/home/parallels/research-runs/cap-interval-arb-2026-09-12 /home/parallels/codex-precision-noble-py312-20260830/bin/python -B /media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/runner.py run /media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/output'
```

Its saved stdout records all six endpoint/strip tasks COMPLETE and packet wall time approximately 50.88 seconds. This establishes the producer host through an executed SSH command and successful output, not merely through Linux-looking paths in a manifest. It does not independently establish the historical kernel/compiler build.

Do not confuse this accepted R1 with ordinal **91263**, timestamp **17:27:34.863Z**, exit **1**, targeting the earlier `lin-central-validated-mode-20261005T165817Z` namespace. The failed predecessor remains separate.

## Computational auditor: what is and is not recovered

Current immutable archive, relative to `/Users/ronbibb/Research`:
`research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/`.

* `postrun_audit.py:137–147` requires the actual resolved interpreter, its digest, Flint version, and every recorded native library digest to match `BINDINGS.json.runtime`; this precedes successful receipt publication.
* `BINDINGS.json:94` onward specifies `/usr/bin/python3.12`, executable digest `c86f21d0da9290ece2d7d49a3f7ed52aed59cb029abdf0ea25c79634f6cbe960`, python-flint `0.9.0`, and 42 native library bindings. This is the frozen runtime contract, not a fresh availability check.
* `INDEPENDENT_AUDIT.json` reports `audit_pass: true`, source digest `9d2334aee18c7085036639858feff1f3a962517040ba3f1258e9ee3fe776be84`, 288 checkpoints, 11,808 native roundtrips, 445 hash links, and 42 runtime libraries verified.
* The historical transcript ordinal **91411**, **17:39:10.058Z**, exit 0, reads the already-existing receipt and auditor source. Ordinal **91437**, **17:41:25.783Z**, copies them into the archive. Neither is the auditor execution command.

The source-bound receipt is consequently strong conditional evidence of execution under the specified Linux runtime: an ordinary successful execution of that source could not bypass those gates. The independent process invocation, actual platform string, compiler provenance, and host-attestation chain remain unavailable in this recovery. Do not invent them or infer them from the later copy operation.

## Mathematical evidence scope

The auditor verifies exact exported signs, checkpoint/link/native serialization integrity, event coverage and an independent rational exponential-series norm estimate. It explicitly records no new physical integration. Its receipt is **not** a complete independent reconstruction of every interval-IVP cell from exact witnesses. The producer's interval-flow implementation and native outward-enclosure assumptions remain dependencies. This baseline pure-potential scalar certificate is not itself the selected dynamical-wall action's mass certificate; that connection has its own analytic/action premises.

## Minimal recommendation

No mass ODE rerun is justified solely by the now-resolved producer-host uncertainty. Preserve this recovered receipt as provenance evidence. If direct computational-auditor process evidence is required, the smallest additional qualification is a separately admitted Linux execution of the unchanged `postrun_audit.py` against the sealed archive, after checking its write behavior and historical runtime availability. It writes its report to stdout and performs no ODE integration; new stdout must go into a new qualification namespace, never the parent.

Only if the historical audit/runtime cannot be made available, or the requested assurance is a fresh numerical endpoint certificate rather than provenance, propose a separate two-engine/four-endpoint qualification at the original frozen masses and original full parameter/domain boxes. No root search, new mass endpoints, precision tuning, or uniform strip replay follows automatically. Historical endpoint cost was tens of seconds, but current runtime/resource admission would supply the ETA. This report authorizes neither alternative.
