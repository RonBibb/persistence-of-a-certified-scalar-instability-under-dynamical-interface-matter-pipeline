# Independent saved-mode derivative check

Date: 2026-09-29. This check concerns the saved `shoot_tight` mode on the
fixed candidate background. It does not solve another eigenproblem or
alter the frozen primary implementation, contract, or criteria.

## Consequence

The saved negative-mass mode satisfies the physical equations and finite
wall conditions when its derivatives are independently reconstructed from
its sampled profiles. Its largest normalized equation residual is
**3.292e-10**, below the frozen **1e-6** criterion. The mode has positive
kinetic norm and nonzero proper-separation response. This removes the
specific concern that the accepted shooting profile satisfies the scalar
equation only because its derivatives were supplied by the same ODE
right-hand side used to evolve it.

The check does not certify spectral completeness or supply a rigorous
continuum eigenvalue enclosure. The mass sign and its sensitivity across
methods and backgrounds remain the responsibility of the primary result
comparison.

## Algebraic review of the primary implementation

`code/stability.py` constructs its two-field pencil from

\[
 \Psi'+2A\Psi+Sf/3=0,\qquad
 Sf'-Bf+(2S^2-12k)\Psi=3\mu\Psi,
 \qquad B=a^2m_\Phi^2\Phi-4AS.
\]

Its two endpoint replacements implement
\(f'+2S\Psi-\sigma a\gamma f/2=0\), with lower/upper signs
\(\sigma=+1,-1\). These agree with the independently derived momentum,
Einstein, and finite-wall equations. The singular pencil's infinite roots
are not interpreted as physical modes.

The scalar equation follows by direct variation of the canonical action:

\[
 f''+3Af'+(\mu-a^2m_\Phi^2)f+6S\Psi'+4a^2m_\Phi^2\Phi\Psi=0.
\]

Substituting the momentum constraint into this equation gives exactly the
third shooting ODE. The lower-wall normalization follows by inserting its
Robin condition into the Einstein constraint:
\((c_aS_a-B_a)f_a=3(\mu+4k)\Psi_a\). No division by the background
scalar derivative occurs in the pencil or shooting evolution. I found no
material equation, sign, or endpoint-normalization error in these parts.

The higher-order Chebyshev eigenvectors' elevated scalar residuals remain
a real failed profile diagnostic at those orders. Their stable eigenvalues
do not make those particular profiles pass. The independently checked
shooting profile supplies a separate accepted profile of the same
converged negative branch; the original spectral diagnostics remain
unchanged and should be reported as measured.

## Independent implementation and execution

The standalone `code/independent_mode_check.py` imports neither the primary
solver nor its RHS. It evaluates the inherited background's stored
piecewise polynomials using separate Horner code. Actual-coordinate
Fornberg differentiation weights reconstruct first and second derivatives
from saved \(\Psi,f\) samples, including one-sided endpoint stencils.
The saved \(p=f'\) and constraint arrays are not used as derivatives in
any equation or wall residual. A separate comparison to the saved \(p\)
is reported only after the residuals are formed.

Before the scientific check, a seventh-degree polynomial verified the
first and second derivative formulas, including endpoints. Its maximum
derivative error was 3.945e-31 in the Linux extended arithmetic.

The check ran using
`/home/parallels/codex-precision-noble-py312-20260830/bin/python` on
`parallels@linux.vm`, with one BLAS/OpenMP thread and a 300-second timeout.
The elapsed computation was 1.081 seconds. The NumPy long-double type has
112 mantissa bits. This improves arithmetic in the check; it does not
create additional precision in the saved binary64 background or profile.
Frozen source bindings were verified before execution, and all directly
used source/input hashes were verified unchanged afterward and saved in
`results/INDEPENDENT_MODE_CHECK.json`.

## Results

The saved mass is \(\mu=-0.0013122306827979032\). For nine-point local
polynomials on all 2001 saved samples:

| Diagnostic | Maximum normalized residual |
|---|---:|
| Momentum constraint | 1.1721e-12 |
| Einstein constraint | 1.0712e-14 |
| Scalar field equation | 3.2918e-10 |
| Lower scalar Robin condition | 1.2124e-15 |
| Upper scalar Robin condition | 2.0184e-14 |

Normalization is the frozen expression
\(\max|\sum_j t_j|/(1+\sum_j|t_j|)\), applied also to each wall's
three terms. All sample points and both endpoints are included. The
absolute maximum scalar-equation residual is 4.504e-10; acceptance is not
being obtained through a large normalization denominator.

Nine-point checks on 501 and 1001 nested samples yield maximum normalized
equation residuals 1.368e-10 and 2.524e-10. A seven-point check on 2001
samples yields 3.245e-10. All pass the same 1e-6 criterion. The slight
increase with finer differencing is consistent with differentiation
sensitivity of saved samples/interpolated trajectories; these numbers
are not presented as a measured truncation-convergence order.

Independent quadrature gives

\[
 Z=321.284053011085>0,\qquad
 \delta D/q=-53.54486563354609,\qquad
 (\delta D/q)/\sqrt Z=-2.9872615445453374.
\]

The norm and separation integral agree with the saved shooting receipt
to relative 2.221e-16. The absolute values use the shooting normalization
\(\Psi(z_a)=1\); the scale-independent separation overlap also agrees
with the spectral profile. These are finite numerical verification
results for this mode, not a proof about every scalar or gravitational
sector.
