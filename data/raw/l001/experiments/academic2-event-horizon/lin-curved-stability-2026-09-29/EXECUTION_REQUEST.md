# Lin-derived curved-background stability: authorized reopening

Issued 2026-09-29, following the user's explicit “Do it” approval of a focused
reopening with the curved-background stability test first.

Research task: **Review Existing Lin paper**, thread
`01a0965f-ad75-7562-a5bf-d402d3f5472f` on host `local`.
Managing task: **Explore adjacent-mass baby universes**,
`01a0bab7-cc82-7c43-a6d5-1454e2653f7a`.

## Question and authorized scope

Does the already constructed positive-curvature Einstein–scalar two-brane
background have a physical instability in its coupled scalar–geometry sector,
especially the mode changing proper brane separation (the radion)?

Develop the perturbation formulation, implement the smallest decisive numerical
test, execute its controls and scientific cases, and interpret the result. This
is execution authorization, not merely a request for another proposal. No new
wall-clock duration was specified. Work to a bounded conclusion for this one
background and sector, without an open-ended model or parameter search.

If this sector passes, recommend the next donor-source/energy-balance experiment;
do not automatically launch a donor-accretion, halo, collapse, or event-horizon
campaign. A resolved physical instability ends this candidate's stability test;
do not retune the background to evade it. A technical or derivational failure
must remain inconclusive, not a physical exclusion.

## Exact starting point

Read Academic2/AGENTS.md, the research README and current position, and:

- `../capture-to-model-2026-09-12/static-background-successor/analysis/CURVED_STATIC_SUCCESSOR_RESULT.md`
- `../capture-to-model-2026-09-12/static-background-successor/PROSPECTIVE_BVP_DESIGN.md`
- `../capture-to-model-2026-09-12/static-background-successor/FLAT_BASE_OBSTRUCTION.md`
- the candidate's bound action, source, fine-collocation contract and retained arrays.

The candidate has ds5² = psi²(gamma_k + dz²), Ric(gamma_k) = 3k gamma_k,
k approximately 0.0003268413384542497, proper separation
D approximately 1.9975672792526362, and conformal length
L approximately 6.38029536996215. These are reported numerical values, not
rigorous enclosures. The base has the de Sitter sign; do not substitute a flat
or globally static time interpretation.

Keep m²=.41, gamma=20, v0=.1, v1=0.09048374180359596,
lambda_a=5.999990376773895, and lambda_b=-6.052844277744164 fixed.
In particular, do not recompute v1 from the adjusted separation. Preserve the
lower-tension reconstruction's stated provenance. The candidate is a different
state from G10, not its established endpoint.

Authenticate the inherited files before numerical work. Recorded anchors under
`static-background-successor/proper-shooting/narrow-gap/fine-collocation/` are:

- `CONTRACT.json`: f5412697026f31a4979c9d29b4d96e054da2b279f64e084e1cadb206bd5a0354
- `results/receipt.json`: 795c92d32918accdb72b326b2f3462c432c8df31995e755031462bee166fec64
- `results/arrays.npz`: 49c86129314b335a6447d40f488b005060eca4de815306c3389ebdb3ba9e23b3

## Physical calculation

Derive the linearized coupled bulk equations and wall conditions from the
declared action and normal conventions. Include finite scalar-wall stiffness
and the physical separation degree of freedom: fixing coordinate wall locations
must not inadvertently remove brane bending or the radion. Explicitly separate
gauge and constraint modes from physical modes. If a reduced master variable
divides by a vanishing background derivative, use a regular formulation or
demonstrate the required regular matching; do not hide a singularity numerically.

State the kinetic normalization/sign and the physical growth criterion in the
curved four-dimensional background. A static shooting Jacobian, coordinate
growth, or scalar-only calculation on a frozen metric is not by itself the
requested stability answer. Conversely, a resolved physical unstable mode is a
useful answer; full stability of every gravitational sector is not required or
implied by a clean scalar-sector result.

Before evaluating the scientific spectrum or evolution, freeze the actual
formulation, boundary conditions, measured observables, control cases, resolution
and precision comparisons, numerical resource limits, and pass/fail/inconclusive
criteria in a test specification. Use a known or independently derived limiting
control where available, separate bulk/wall/constraint residuals, and a second
method or independent residual check sufficient to discriminate physical modes
from discretization artifacts. Use targeted refinement rather than an unlimited
scan. Interpret near-zero or poorly resolved eigenvalues as unresolved unless
the stated precision and convergence checks settle their sign.

## Execution and preservation

Write all new source and results in this successor directory. Do not edit frozen
predecessors, old Academic sources, submitted manuscripts, or unrelated branches.
Do not restart Palatini, Chakrabarty, Deng, Wainwright, the interface campaign,
Protocol 394, or Protocol 407 as part of this authorization.

Linux preflight at 2026-09-29 08:51 UTC succeeded: `parallels@linux.vm` reachable,
load average 0.09/0.10/0.09, no scientific job visible in the high-CPU snapshot,
but root disk 97% used with 2.1 GB free. Recheck before actual numerical launch.
Prefer small jobs and the verified shared Academic2 output path. No archive
deletion, system cleanup, or installation is authorized by this request.

Prefer Linux for precision-sensitive work. Verify the actual arithmetic used by
the solver: binary128-capable NumPy does not make SciPy integration/eigensolvers
binary128. Use suitable arbitrary precision if the physical sign requires it.
Independent numerical cases may use multiple processes with controlled numerical
library thread counts. Newly designed jobs over an hour require atomic exact-
resumption checkpoints and source/input compatibility checks. Never modify an
unrelated running job.

## Deliverables and stopping decision

Maintain a concise machine-readable status separating formulation, controls,
numerical launch, running cases, and completed interpretation. Deliver a
derivation, frozen specification, source/input bindings, reproducible code,
retained results and a RESULT_REPORT.md. Report the lowest relevant physical
mode(s), growth interpretation, numerical uncertainty and kinetic health, or the
specific unresolved obstacle. State what was actually tested and whether the
next donor-source calculation is justified. No baby-universe, source-ownership,
halo, global-event-horizon, or G10-attractor claim follows from this test alone.
