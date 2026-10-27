# Finite amplitude feasibility findings

**The existing quadratic profiles can be reused, but the cubic archive is incomplete for the proposed full-residual calculation.** The completed inventory identifies a targeted data requirement rather than a need to repeat the whole research line. The local convergence and remainder result is unchanged.

## Completed check

The Linux inventory verified 2,728 bound input files, all 192 seed chunks and their state/checkpoint chains, and all 24,548 cells across the two representations. Runtime was 61.13 seconds on one leased core. No ODE solve or physical evolution was launched.

| Representation | Whole cells | Seed chunks | Available profile data |
| --- | ---: | ---: | --- |
| Primary | 8,183 | 64 | Full 14-component canonical quadratic-engine boxes |
| Independent | 16,365 | 128 | Full 13-component native and 14-component canonical boxes |

The seed archive retained more than the first-mode quantities used in its original conclusion: it saved the complete quadratic-engine state. Together with the authenticated shooting coefficient `A2`, those boxes support reconstruction of the actual quadratic fields. Bounds on real-axis radial jets can be obtained from the equations without repeating that evolution. Whether these enclosures are sharp enough for the eventual norm remains to be assessed.

The cubic producer instead saved selected cell integration budgets and wall endpoints. It discarded the full cubic scalar and derivative profiles. Its 96 progress records are counters, not resumable states. The retained metric-related budgets cannot substitute for the missing scalar channels.

## What must happen before another solve

The central mathematical task is a correction inverse around the nonzero polynomial branch. The previous harmonic inverse acts about the background; it does not automatically control the coupled finite-amplitude operator. The correction must preserve the selected amplitude normalization, satisfy compatible bulk/wall forcing and live in a norm closed under derivatives and moving-wall evaluation.

`CORRECTION_STRATEGY.md` specifies the next derivation: a tail beginning at order four, an explicit perturbation bound relative to the background inverse, and a residual/radii inequality. It also explains why re-centering the old large-constant majorant alone does not solve the conditioning problem. If that design closes, the minimal new computation is a cubic-only replay exporting full states and Taylor/remainder models. The original cubic producer used about 8.8 minutes across both engines; a new export's cost and storage must be measured separately, not assumed equal.

No useful-amplitude target was selected, no cubic replay was launched, and no stronger physical claim was made. The readiness result is `QUADRATIC_PROFILE_REUSABLE_CUBIC_PROFILE_EXPORT_REQUIRED`, with `finite_amplitude_certificate_ready=false`.

## Independent review and provenance

The reviewer inspected the original producer layouts, inventory source, output hashes/counts/schema and correction strategy. The review passed, including the distinction between real-axis boxes and a complex-collar certificate. This was an independent structural review, not a second full inventory execution. A prelaunch suggestion to check native-state continuity across all cells, checkpoints and final states was incorporated before the run.

Terminal SHA-256: `628a76b0cd40555fc5b2ac1d71ef496ca17c08859b702921b9d52c4c54a32018`.

Result SHA-256: `ccb4e3e265956a1401bfdae9e6db0c7823648e5a7cffe2eba169d1cc8fe6371e`.

The source-bound inventory records are `CONTRACT.md`, `check.py`, `BINDING.json`, `RESULT.json` and `TERMINAL.json`. This interpretation and the correction strategy are subsequent explanatory records. Parent sources, results and manuscripts were not changed.
