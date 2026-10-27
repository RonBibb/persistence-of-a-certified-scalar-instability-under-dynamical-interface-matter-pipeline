# Local response to each wall stiffness

On the saved certified central background and physical negative mode, the upper wall has a substantially larger local stiffness response than the lower wall. The new exact-rational calculation bounds its response at 230 to 262 times the lower-wall response. Both coefficients are strictly positive. The admitted owner test passed its frozen USEFUL criteria and all six corruption controls; separate independent terminal review accepted the conditional coefficient enclosures.

## The action change and the two coefficients

The independently reviewed action deformation is

    tau_i(Phi) -> tau_i(Phi) + eta_i*(Phi-Phi_i_star)^2/2.

Its value and first derivative vanish on the exact central background, while its wall Hessian changes by eta_i. Thus the original background geometry, wall values and proper separation remain fixed. This is a specified nearby action, not a variation of the original gamma with its other wall parameters held unchanged.

For the local simple physical eigenmode branch, the accepted regular Green identity gives

    C_i = partial mu_star / partial eta_i = a_i^4*f_i^2/Z,
    Z = 2 integral a^3*(f^2+6*psi^2) dz.

Here a_i is the warp factor at wall i; the lower normalization is a_a=1. The mode was represented with psi(0)=1, but each coefficient is unchanged by a common nonzero rescaling of the mode. The conventions are those of the original action, ell=kappa_5=1, with doubled-cover norm Z.

## Certified bounds conditional on the saved flow enclosures

Conservative outward bounds in scientific notation are

    1.7409186e-11 <= C_a <= 4.91860844e-10,
    4.008067852e-9 <= C_b <= 1.28603519069e-7,
    230.227047206505331216 <= C_b/C_a <= 261.463367319362497455.

The full outward decimal enclosures are:

| Quantity | Lower bound | Upper bound |
| --- | --- | --- |
| C_a | 0.000000000017409186 | 0.000000000491860844 |
| C_b | 0.000000004008067852 | 0.000000128603519069 |
| C_b/C_a | 230.227047206505331216 | 261.463367319362497455 |
| Z at psi(0)=1 | 292.433558523993267215 | 359.257121113495651912 |
| psi at upper wall | 51.686324541776298691 | 54.797074237945185780 |

The [exact rational result](RESULT.json) is authoritative; the displayed decimal endpoints widen it. Equal infinitesimal increases in the two additive wall Hessians therefore raise this eigenvalue by very different amounts, with the upper-wall change having the larger local effect. A positive derivative alone gives no finite deformation at which the negative mode becomes nonnegative, and no such threshold is inferred.

## How endpoint data and norm were enclosed

The test uses the accepted central mass strip, both saved interval producers and their 94 nonzero-index checkpoint nodes. It never identifies a saved final integration node with the unknown exact wall location.

On the exact background, H_s<0 and the positive scalar endpoint values give 0<Phi<=max(Phi_a,Phi_b) by the scalar equation's maximum principle. The first integral then supplies a uniform |Phi_s|<1/2 bound. With the saved global mode bounds, the regular psi equation has a strictly positive derivative. Thus the log warp decreases and psi increases throughout the physical proper-distance interval.

Those monotonicities turn saved checkpoint values into bounds over each intervening slab. Integrating the regular proper-coordinate density 2*exp(2W)*(f^2+6*psi^2) gives two-sided Z bounds. Separate final-tail bounds cover the unknown exact D using its certified lower and upper endpoints. This sharply improves the old positive norm floor, which was sufficient for admissibility but too coarse for useful coefficient magnitudes.

At the exact upper-wall eigenmode, the regular constraint and Robin condition give

    beta_b = (-gamma/2 + 4*H_b)*Phi_s,b - m2*Phi_b,
    a_b^2*beta_b*f_b = 3*lambda_star*psi_b,
    lambda_star = mu_star + 4*k.

Consequently the coefficients and their ratio can be evaluated without an unrecorded upper-wall mode value:

    C_a = 9*lambda_star^2/(B0^2*Z),
    C_b = 9*lambda_star^2*psi_b^2/(beta_b^2*Z),
    C_b/C_a = psi_b^2*B0^2/beta_b^2.

The upper warp cancels exactly in this reconstruction. The last identity also cancels the common spectral factor and norm, which is why the relative response is much more tightly bounded than either absolute coefficient. All wall identities are applied to the exact eigenmode enclosed by the strip, not to every off-shell strip profile.

## Remaining uncertainty and the smallest useful refinement

The upper/lower enclosure ratios are approximately 28 for C_a and 32 for C_b, whereas the norm ratio is only about 1.23. The inherited shifted spectral strip spans approximately -1.26347e-5 to -2.63463e-6; squaring its magnitudes contributes about a factor of 23. That shared spectral uncertainty accounts for most of the absolute coefficient width. The relative wall-response ratio cancels it and spans only about a factor of 1.14.

The highest-payoff quantitative refinement is therefore a narrower certified central eigenvalue bracket on this same exact background. Denser norm checkpoints would offer a smaller improvement while retaining the broad lambda_star squared factor. Any such refinement needs its own frozen, reviewed calculation; none was launched here.

## Verification and scope

The single admitted owner run finished at 2026-10-13T08:30:45.243809Z under isolated CPython 3.14.4, return code zero, empty stderr, and one worker with BLAS thread limits of one. It authenticated 104 source files and performed standard-library rational arithmetic only. Six semantic controls rejected altered denominator, mass-strip, checkpoint-grid, positive-profile and norm-order premises at the intended predicates. The [gate](INDEPENDENT_GATE.json), [source bindings](SOURCE_BINDINGS.json), [frozen design](DESIGN.md) and [execution record](RUN_METADATA.json) preserve the admission and evidence.

The separate [terminal review](TERMINAL_REVIEW.json) reconstructed all 94 checkpoint nodes, every per-producer and combined rational enclosure, all decimal bounds and the frozen classification. Its independent implementation used degree-80 exponential sums to check the owner's degree-64 enclosure construction. It accepted the action-specific local interpretation and found no blocking issue within the inherited-certificate scope.

Original validated-flow correctness, checkpoint enclosures, exact-background identification, model provenance and the accepted local Green-identity derivative remain inherited. No new interval-flow producer, finite stiffness scan, complete-spectrum analysis, stability threshold, nonlinear evolution or horizon calculation was performed. The original failed predecessor and all source files remain unchanged.

The analytic derivative is supplied by the preceding [finite-stiffness proof review](../20261013T073517Z_PAPER_A_CURVATURE_RESPONSE/FINITE_STIFFNESS_PROOF_REVIEW.md); the numerical mode authority remains the [central certificate](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/RESULT_REPORT.md).
