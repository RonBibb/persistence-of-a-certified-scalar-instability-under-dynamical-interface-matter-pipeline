# Reproduce the bounded stability decision

The retained result is in RESULT_REPORT.md and results/SUMMARY.json. Replaying is optional; the current numerical test and independent reviews are complete.

## Runtime and inputs

The executed Linux interpreter is `/home/parallels/codex-precision-noble-py312-20260830/bin/python`: Python 3.12.3, NumPy 2.5.1, SciPy 1.18.0 and mpmath 1.3.0, with SymPy and Matplotlib available. NumPy longdouble has 112 stored fraction bits. SciPy eigensolvers/integrators are binary64; the separate verifier uses extended arithmetic and precision_check.py uses mpmath at the explicitly recorded decimal precision.

The files remain on the shared Academic2 mount. The original candidate, earlier fine representation, bound source files and original relative directory layout must be available. CONTRACT.json authenticates the original formulation and inputs; preflight/ADDITIONAL_BINDINGS.json binds the precision implementation, independent formulation and preceding background. MANIFEST.json binds the completed package. A hash mismatch is an execution failure, not a scientific result.

## Non-overwriting replay

Connect to `parallels@linux.vm`, inspect the current workload/storage, and execute:

```sh
cd /media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-curved-stability-2026-09-29
/home/parallels/codex-precision-noble-py312-20260830/bin/python code/reproduce.py --execute
```

The driver creates a unique directory under this successor's `replays/` and redirects all replay outputs there. It authenticates original inputs before running, sets one numerical-library thread, and leaves the sealed results unchanged. Original primary code is loaded without modification; output globals are redirected by the replay driver. The four original spectral cases and four precision cases were executed concurrently in bounded groups; the replay runs the same small cases serially.

The stages are analytic/finite-Robin controls; N=33,49,65,97 undivided spectra; three regular shooting tolerances; previous-background shooting; 40/60-digit RK4 comparisons; independent saved-profile differentiation; symbolic constraint control and final decision/figure. All scientific settings are those in TEST_SPECIFICATION.md. The driver was supplied for reproducibility after the original individual runs; it was not itself used to generate the sealed science results.

## Evidence map and decision

- `results/CONTROLS.json` and `SYMBOLIC_CONTROL.json`: exact limiting and numerical control outcomes.
- `spectral_N*.json/.npz`: every pencil eigenvalue, low candidate profiles and off-grid diagnostics; the N65/N97 profile residual failures stay visible.
- `shoot_*.json/.npz`: accepted regular mode and tolerance/background comparisons.
- `precision_N*_dps*.json`: arbitrary-precision integration on the retained background, not a high-precision background reconstruction.
- `INDEPENDENT_MODE_CHECK.json`: derivatives of saved samples with no use of the primary evolution RHS as a derivative.
- `SUMMARY.json`: fixed decision criteria and actual comparison values.
- `analysis/`: action derivations, independently derived kinetic control, numerical qualifications and physical review.

Successful reproduction means the controls and accepted shooting residuals pass, a positive kinetic norm and nonzero separation overlap remain, and the negative mass sign meets the fixed sensitivity criterion. Technical failure is inconclusive. Do not infer stability from absence of a negative root in a limited search; do not turn a failed high-resolution spectral profile into a passing one. The decisive instability ends this background's test without donor evolution or parameter retuning.
