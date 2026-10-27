# D1 curvature well-balance discriminator — final report

## Result

The experiment completed in 14.82 seconds and was independently verified.
The frozen classification is

`D1_CURVATURE_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_WALL_CANDIDATE`.

The analytically well-balanced D1 curvature formulation removes the failed
bulk Hamiltonian defect while retaining a finite, nonzero response to a
generic metric perturbation.  It therefore identifies the preceding
Hamiltonian failure as a discrete curvature-representation error for this D1
background, not as a failure of the analytic static solution.  The same
background nevertheless fails the unchanged compact-wall admission rows, so
it is not admitted for evolution.

No short evolution was run.

## Producer A: analytic D1 curvature well-balance

### Risk

The production Ricci discretization could be incompatible with the exact D1
static-patch background even though the continuum Hamiltonian constraint is
satisfied.

### Criterion

At the frozen original grids, the full and retained-interior Hamiltonian
residuals had to meet `2e-6` and `5e-7`, decrease under refinement, and the
subtract/add operator had to retain a finite, nonzero response to a smooth
`1e-6` metric perturbation.  Passing this discriminator only authorized the
unchanged wall, axis, source, ADM, and raw-GH admission tests.

### Outcome

| Grid | Full Hamiltonian | Interior Hamiltonian | Lower-wall first radial node |
|---|---:|---:|---:|
| 65 x 121 | 5.267e-9 | 2.644e-10 | 5.267e-9 |
| 97 x 181 | 7.359e-10 | 3.692e-11 | 7.359e-10 |
| 129 x 241 | 1.683e-10 | 8.450e-12 | 1.683e-10 |

The last two measured full/interior orders were approximately
`(4.85, 4.86)` and `(5.13, 5.13)`.  Corrected componentwise Ricci errors were
at roundoff (`<=2.22e-15`).  The independently evaluated analytic Hamiltonian
was `1.028e-13`.  A smooth `1e-6` metric perturbation produced a finite
maximum curvature response of `6.902e-5`, confirming that the formulation
does not project generic departures back onto the D1 background.

The unchanged axis rows passed (`<=3.59e-13`).  The compact-wall rows did not:

| Grid | Maximum wall residual |
|---|---:|
| 65 x 121 | 2.007e-4 |
| 97 x 181 | 3.134e-5 |
| 129 x 241 | 7.622e-6 |

The candidate gate is `2e-6`, and the all-level ceiling is `2e-5`.  The
failure is localized to the lower compact wall; the fine upper-wall maximum
is only `6.14e-12`.

### Consequence

The failed Hamiltonian gate in the preceding packet is removable by a
D1-specific, continuum-equivalent curvature well-balance.  Curvature
representation is therefore identified as the cause of that particular
failure.  It is not the only admission incompatibility: the independently
unchanged lower-wall discretization remains too inaccurate on the frozen
original grids.  Source, ADM, raw-GH, and evolution stages were correctly not
reached.

## Producer B: unchanged direct high-resolution operator

### Risk

The apparent curvature mismatch might disappear under brute-force compact
refinement without any reformulation.

### Criterion

The finest full and interior residuals had to meet the same absolute gates,
the entire sequences had to decrease monotonically, the last-pair observed
orders had to lie in `[2,6]`, and two consecutive levels had to pass both
absolute gates.

### Outcome

| Nx x 241 | Full Hamiltonian | Interior Hamiltonian |
|---|---:|---:|
| 257 x 241 | 6.260e-4 | 6.634e-6 |
| 513 x 241 | 2.480e-5 | 2.635e-7 |
| 1025 x 241 | 8.812e-7 | 4.899e-8 |
| 1537 x 241 | 7.072e-7 | 1.501e-7 |
| 2049 x 241 | 1.800e-6 | 2.137e-7 |

Three levels met both absolute gates, so the direct operator can produce
small residuals at isolated high resolutions.  The sequence is not a clean
convergent ladder: the interior residual rises after `Nx=1025`, the full
residual rises at `Nx=2049`, and the last-pair observed orders are negative
(`-3.25` full and `-1.23` interior).  Producer B therefore failed its frozen
monotonicity and observed-order requirements and did not advance to complete
admission.

### Consequence

Brute-force float64 refinement does not provide a defensible replacement for
the well-balanced formulation.  The absolute residual can cross the gates,
but the high-resolution sequence develops a representation/roundoff floor
rather than a verified asymptotic trend.

## Independent audit

The independent verifier returned `VERIFIED` with all 24 checks true.  It
authenticated the frozen source and parents, terminal and evidence hashes,
grid and gate contracts, both producer decisions, represented `q` and source
fields, and independently reconstructed the analytic Hamiltonian.

## Scientific boundary

This is a finite-resolution discriminator for one certified D1 background.
It establishes which discrete subsystem caused the earlier Hamiltonian
failure and exposes a separate lower-wall admission failure.  It does not
establish full Cauchy admission, dynamical preservation, stability, a P16
join, collapse, parent-child propagation, or a causal/event horizon.  No
physical parameter, wall law, source anchor, gate, or manuscript was changed.
