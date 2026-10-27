# Reproducibility command map

## Status and boundary

This records how the proof-bearing programs fit together. It is not yet a
packaged public replay script: the current producers retain research-tree
relative imports and should be copied into a clean archive layout before the
commands are published. The hashes in `PUBLIC_ARCHIVE_INVENTORY.md`, not copied
filenames alone, identify the authoritative sources.

## Frozen production environment

The sealed independent D1 and D2A records report:

```text
platform: Linux-6.8.0-139-generic-aarch64-with-glibc2.39
python:   3.12.3
flint:    python-flint 0.9.0
```

The D1 producers set Arb precision to 768 bits. D2A sets it to 512 bits. Use:

```bash
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0
export PYTHONNOUSERSITE=1
```

Thread-count variables are immaterial to the current single-process interval
sources, but a public container should set them explicitly if linked numerical
libraries introduce threading.

## Original D1 certificate

Place `confirm_32768.py` and `validated_sensitivity_newton.py` in the same
directory so the wrapper's frozen module import resolves locally. Then run:

```bash
python3 -B confirm_32768.py > RESULT.replay.json
```

The replay is expected to use one 32,768-step level at 768-bit precision. The
publication verifier must compare proof-bearing exact rational fields and gate
outcomes, not require byte identity for runtime metadata.

The sealed `RESULT.json` remains the theorem authority unless the clean replay
is separately reviewed and promoted. `validated_sensitivity_newton_r1.py` is
retained to explain the corrected algebra-control lineage; it is not the
32,768-step entrypoint.

## Independent D1 replay

Place `independent_d1_replay_r1.py` and `independent_d1_replay.py` in the same
directory and run:

```bash
python3 -B independent_d1_replay_r1.py > RESULT.replay.json
```

The wrapper sets the proof-bearing step pair `(8192,16384)` while retaining the
independent Taylor--Picard engine, fifth-order recurrence, 768-bit precision,
root box, and all geometry gates. A valid result must classify
`INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS` at both declared levels.

## D2A exact cover

D2A authenticates and dynamically imports four parents named in its bindings:

- frozen predecessor source and terminal;
- validated-flow source and terminal.

In a public archive, preserve their relative layout or rewrite only the path
adapter before freeze, then regenerate the archive manifest. Do not modify the
interval formulas or thresholds. The two-stage command shape is:

```bash
python3 -B d2a_validated_cover_r1.py \
  --bindings BINDINGS.json --output output --mode preflight

python3 -B d2a_validated_cover_r1.py \
  --bindings BINDINGS.json --output output --mode production
```

The second command is resumable through its content-addressed checkpoint. A
valid terminal result must contain an exact contiguous cover of the complete
launch domain, zero unresolved boxes, the frozen classification counts, and the
uniform positive-route residual floor. A failed or stale binding must close the
run without a theorem result.

## Certificate-only checks

The present source-tree records can be verified without `python-flint`:

```bash
python3 -B reduction_identity_check.py
python3 -B verify_reconciled_authority.py
python3 -B verify_window.py
```

`verify_window.py` also invokes the older consolidated D1/D2A evidence
verifier. These checks validate hashes, exact rational relationships,
classifications, and the local sealed manifest. They do not recreate the
interval integrations.

## Clean-package acceptance

A staged archive is acceptable only if:

1. all copied-source hashes match the declared input manifest;
2. preflight checks pass under the frozen environment;
3. both D1 implementations independently meet their frozen gates;
4. D2A completes with an exact contiguous cover and no unresolved boxes;
5. certificate-only verification passes on macOS and Linux;
6. runtime-only fields are separated from proof-bearing comparisons; and
7. the staged archive is sealed after, not before, the replay.

No command in this map authorizes an external deposit or changes a sealed
parent result.
