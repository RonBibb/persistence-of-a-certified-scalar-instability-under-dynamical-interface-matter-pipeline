# Paper A portable saved evidence replay

The first layer stages the original publication-upgrade verifier, its unchanged binding record, and all 17 bound canonical parent files. The archive layout preserves the original `branches/02-event-horizon` paths. The 23 checks establish the saved authority chain, including recorded finite-resolution GH support. They do not regenerate any numerical producer.

## Execution gate and commands

Independent review must approve the staged scope, manifest, path confinement, and original entrypoint before either command is run. Mechanical staging and hash inventory do not execute a verifier.

Run with system Python in isolated mode and bytecode disabled, from `/private/tmp`:

```sh
python3 -I -B /absolute/path/to/packet/replay.py --layer authority
python3 -I -B /absolute/path/to/packet/replay.py --layer authority --archive /absolute/path/to/packet/relocated/archive
```

The second command follows a byte-preserving copy of the archive into `relocated/archive` inside this owned packet. Its purpose is to verify that the original entrypoint resolves its inputs relative to the relocated archive. Save stdout, stderr, return code, elapsed time, Python version, cwd, command, and hashes under this packet. Both replays must pass; an independent postrun audit must inspect the results before classification.

The wrapper validates every manifested byte and rejects symlinks and path escapes. It invokes only the original verifier, with a 120-second timeout. The original binding record retains its historical root as provenance text; neither verifier nor wrapper uses that root for input resolution. No fallback path, producer import, network access, or source modification is part of the plan.

## Distinct second layer

Inspect the original consolidation verifier for its exact dependency closure. If feasible, stage its unchanged code and only its required records, including manifest-bound files and 86 saved checkpoints. A separate review must approve that layer before execution. Its intended scope is exact-rational Newton inclusion, 693-box cover and exclusion reconstruction, and checkpoint content-address reconstruction from saved records. ODE integration remains outside this task.

The inspected closure contains 14 hard-coded hash anchors, six packet manifest inventories, their terminal bindings, and 86 checkpoints totaling 150,880,312 bytes. The six manifest inventories total 7,347,068 bytes before deduplication. `stage_consolidation.py` reads the original verifier with `ast.parse` and extracts only the literal `EXPECTED` dictionary; it does not import the verifier or any producer. Historical capture-window, failed predecessor, and producer-source files remain context or hash inputs only. The original verifier recomputes saved exact inequalities and checkpoint addresses, but does not derive intervals from ODEs.

After separate approval, run the same two commands with `--layer consolidation`. The wrapper selects only the original `verify_evidence.py`. Any deeper independent ODE replay would require a new reviewed producer dependency closure and is excluded here.
