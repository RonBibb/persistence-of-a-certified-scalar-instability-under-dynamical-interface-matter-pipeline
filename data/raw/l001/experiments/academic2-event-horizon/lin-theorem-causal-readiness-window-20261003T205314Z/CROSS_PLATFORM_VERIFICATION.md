# Cross-platform clean verification

## Environments

- macOS host: system `python3`, dependency-free mode;
- Linux VM: Linux `6.8.0-146-generic` aarch64, Python `3.12.3`;
- Linux research mount:
  `/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research`.

Both runs used

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONHASHSEED=0
PYTHONNOUSERSITE=1
python3 -B
```

No package was installed and no parent artifact was modified.

## Portability defect found and corrected

The first Linux replay passed the exact algebra checker but the new authority
verifier failed before inspecting evidence because `AUTHORITY_BINDINGS.json`
records the Mac absolute research-root path.  That path is provenance, not a
portable locator.

The verifier was corrected to:

1. retain and report the declared Mac path;
2. use it when it exists;
3. otherwise derive the research root from the verifier's fixed location under
   `branches/02-event-horizon`; and
4. require the derived root to contain `RESEARCH_MAP.md` before reading any
   bound artifact.

The scientific records, hashes, theorem intervals, and parents were unchanged.

## Final results

| Check | macOS | Linux |
|---|---:|---:|
| exact constraint propagation | PASS | PASS |
| exact ss Einstein reduction | PASS | PASS |
| exact tangential Einstein reduction | PASS | PASS |
| exact conformal first integral | PASS | PASS |
| exact wall identity | PASS | PASS |
| reconciled theorem authority | 107 checks PASS | 107 checks PASS |
| bound parent files | 21 hashes PASS | 21 hashes PASS |
| older D1/D2A consolidation verifier | PASS | PASS |
| machine-readable result contract | PASS | PASS |

The added checks recompute the exact difference and ratio between each D1
separation enclosure and the positive exact D2A separation. They also rederive
the D2A classification counts, every terminal classification, exact contiguous
cover, uniform residual floor, and the exact worst-box lower bound directly
from the 693 stored terminal boxes. They do not add a new numerical assumption.

The Linux authority output explicitly records
`portable_root_fallback_used=true`; the Mac output records `false`.  Both resolve
the same content-addressed parents and return the same theorem classifications.

## Replay commands

From the research root on either platform:

```bash
python3 -B branches/02-event-horizon/lin-theorem-causal-readiness-window-20261003T205314Z/reduction_identity_check.py
python3 -B branches/02-event-horizon/lin-theorem-causal-readiness-window-20261003T205314Z/verify_reconciled_authority.py
python3 -B branches/02-event-horizon/lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py
```

## Consequence

The minimal theorem-navigation and algebra checks now replay without SymPy,
Arb, or a platform-specific absolute root.  This materially closes the old
clean-environment verification requirement for the **existing sealed
certificates**.  A submission archive still needs to package the original and
independent interval producers, their declared runtimes, and all source files;
this check does not recreate the expensive interval integrations.

## Expanded packet pre-seal replay

After adding the theorem-first introduction and discussion drafts, standard
methods citation map, and the two provenance-bound figures, the window-level
verifier was replayed again on both macOS and Linux. Both platforms parsed all
five authority/provenance/result JSON files, validated the result classification
and claim boundary, found all 21 required documents, verified
all six figure/script hashes, found no cache or bytecode, and passed the exact
reduction checker, 107-check reconciled authority verifier, and older
consolidated-evidence verifier. Both correctly reported
`local_manifest=NOT_YET_SEALED` before terminal sealing.

The post-seal replay is a final integrity check of the frozen window, not a new
scientific calculation.
