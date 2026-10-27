# Independent physical result review — 2026-09-29

**Conclusion:** the retained calculation resolves a physical linear instability
of the fixed curved candidate in its coupled stabilizer–geometry sector. The
accepted representation is the independently differentiated shooting mode. It
has negative four-dimensional mass squared, positive kinetic energy and a
nonzero proper-separation response. Thus it is a radion instability, not a
constraint mode, a negative-kinetic-energy ghost, or an exceptional de Sitter
coordinate mode. The two finest spectral profiles fail their scalar-equation
residual gate and remain failed profiles; their stable masses are comparison
data only.

This review does not prove a globally lowest eigenvalue or classify the entire
spectrum. A single accepted unstable physical mode is sufficient for the
decision. Under the authorized stopping rule, stop this candidate's stability
test and do not launch its proposed donor-source experiment or retune it to
avoid the instability.

## Physical identification of the mode

The tight shooting result is

| Quantity | Independently checked value |
|---|---:|
| Physical mass squared mu | -0.0013122306827979032 |
| Background base curvature k | 0.0003268413384542497 |
| mu/k | -4.014885904591856 |
| Shifted lambda = mu+4k | -4.865328980904532e-6 |
| Doubled-cover kinetic coefficient Z | 321.284053011085 |
| Separation amplitude delta D/q | -53.5448656335461 |
| Canonically normalized separation overlap | -2.98726154454534 |
| Growing exponent r/H_dS | 1.00297541030507 |
| Growing exponent r, lower-wall proper time | 0.0181325454963 |
| Lower-wall proper-time e-folding scale | 55.1494548961 |

The unnormalized mode uses psi(z_a)=1. Consequently delta D/q is a response
coefficient, not a prediction that the branes move by 53.5 length units. The
linear amplitude q remains arbitrary and initially small. Its sign can also
be reversed. The nonzero canonical overlap is invariant under mode rescaling.

The action has canonical scalar and Einstein kinetic terms, finite scalar-wall
potentials, and no localized kinetic or induced-curvature terms. The physical
norm in these conventions is

    Z = 2 integral a^3 (f^2 + 6 psi^2) dz.

The straight-wall proper-separation variation is

    delta D/q = -2 integral a psi dz.

Both formulae were derived independently before the result in
`INDEPENDENT_FORMULATION.md`; the other analytic reviewer independently obtains
the same formulae in `KINETIC_AND_CONTROL_REVIEW.md`. The norm is regular through
the scalar minimum and strictly positive for this nonzero mode. In the retained
2001 samples, psi ranges from 1 to 54.7810951985 and stays positive; the separation
integral is not a small cancellation of large terms. This establishes the
physical separation component of the instability.

### Why the exceptional harmonic does not invalidate this result

For a scalar harmonic Box_gamma q=mu q on Ric(gamma)=3k gamma,

    D^mu (D_mu D_nu q - gamma_mu_nu Box q/4)
       = (3/4)(mu+4k) D_nu q.

If its trace-free Hessian vanished and mu+4k were nonzero, q would be constant.
Since this mode also has mu nonzero, that constant would have to vanish. Thus a
nontrivial mode at the measured mass is outside the exceptional harmonic
kernel. The measured lambda differs from zero by approximately 4.8653e-6,
compared with a conservative observed mass-sensitivity envelope of 1.1e-11.

The generic pure-potential Israel condition therefore permits straight walls
in longitudinal gauge without deleting the radion. Full brane bending obeys
D_mu D_nu zeta_i+k gamma_mu_nu zeta_i=0; generic harmonics have zeta_i=0. The
nonzero separation observable still measures the integrated metric-lapse
perturbation. The regular momentum equation, Einstein constraint, scalar
equation and finite-gamma wall conditions are all required; the code retains
them rather than imposing f=0 or dividing by the background scalar derivative.

Mu is the physical mass squared. In an expanding de Sitter chart the late-time
growth rate is

    r/H_dS = sqrt(9/4 - mu/k) - 3/2,   H_dS = sqrt(k).

It is positive for the measured negative mu. Generic spatial Fourier modes
have the same late-time criterion after their physical momentum redshifts;
the claim does not require choosing a potentially exceptional homogeneous
embedding function. At the upper wall both r and H_dS scale by 1/a_b, leaving
their ratio unchanged. The numerical e-folding time above uses a_a=1 and the
declared ell=1 units; it is not a physical clock prediction for G10.

## Independent inspection and reconstruction

I read the frozen specification, complete `code/stability.py`, controls, all
four spectral records, three shooting-tolerance records, previous-background
comparison, arbitrary-precision checker and results, independent derivative
checker and its result, and both analytic formulation notes. I recomputed all
nine original contract bindings from their actual local bytes; all match.

For an additional calculation I evaluated the inherited piecewise background
polynomial directly by Horner's rule, without importing the producer's
Background class, then used the saved tight shooting arrays. Independent
composite Simpson sums reproduce Z, delta D and the canonical overlap above.
The reconstructed upper/lower scalar-wall residuals are respectively
-3.76088e-14 and 4.33681e-19. The reconstructed Einstein constraint maximum is
3.38325e-16; its maximum difference from the retained constraint array is
1.23e-17. Small differences from the producer are floating-point evaluation
order. No new eigenvalue search or background solve was performed by this
review.

The separate actual-sample derivative verifier supplies the decisive
non-tautological differential check. I read its entire implementation. It uses
Fornberg polynomial derivatives of the saved psi and f values, including
one-sided endpoint stencils; it does not substitute the evolution right side
or saved p into the derivative slots of the equations. Independent Horner
background evaluation and source/payload hashes are explicit. Four derivative
configurations (501/1001/2001 points and 7/9-point stencils) pass the unchanged
1e-6 normalized residual gate. At the 2001-point, nine-point configuration:

| Independent residual | Maximum normalized value |
|---|---:|
| Momentum | 1.1721e-12 |
| Einstein constraint | 1.0712e-14 |
| Original scalar equation | 3.2918e-10 |
| Lower scalar wall | 1.2124e-15 |
| Upper scalar wall | 2.0184e-14 |

The original scalar equation, not merely the constraint or pencil residual,
therefore admits the shooting profile. The finest shooting record also retains
a regular scalar-turn constraint of approximately -2.46e-16. Background
interpolation is not promoted to an exact continuum solution by these tests.

## Resolution, arithmetic and failed profiles

The four spectral resolutions return the same negative branch in the declared
mu window [-1,1], together with a positive branch near .4348455. The largest
negative-branch discrepancy from tight shooting is 1.0053e-11 and the total
spectral spread is 1.0100e-11. No ordering outside that search window is proved.
The positive branch need not be fully qualified to establish the negative
mode's consequence.

| Spectral N | Original scalar-equation residual | Profile decision |
|---|---:|---|
| 33 | 4.3007e-8 | Pass |
| 49 | 3.3723e-7 | Pass |
| 65 | 6.0009e-6 | Fail |
| 97 | 7.2223e-5 | Fail |

These failures are consistent with differentiation amplifying the high-order
binary64 eigenvector error, but the mass comparison alone does not prove the
specific numerical mechanism. They are not erased by the smooth shooting
result. The physical inference uses the independently verified shooting
representation, corroborated by the lower-order admissible spectral profiles
and all four mass comparisons. This is the second method and independent
residual procedure already specified, not a relaxed residual threshold.

Other measured mass sensitivities are:

- DOP853 tolerance 2e-9 to 2e-13: total spread 1.5765e-16.
- Immediately preceding qualified background representation: 5.2615e-15.
- Arbitrary-precision RK4, 1024 to 4096 steps: approximately 1.9157e-14.
- RK4, 2048 to 4096 steps: approximately 1.1336e-15.
- Finest RK4 versus tight DOP853: 7.500e-17.
- 4096-step, 40/60-digit results agree through the reported 40 digits.

The precision implementation uses its own fixed-step RK4/secant solver and
Horner polynomial evaluation; I checked the normalized-coordinate L factors
against the formulation. Its higher arithmetic precision applies to evolution
on the same retained binary64 background polynomial. It does not create a
40-digit physical background or prove an interval enclosure.

The maximum observed mass spread is conservatively below 1.1e-11. Thus
abs(mu) exceeds 100 times that sensitivity by more than six orders of magnitude,
and also exceeds the frozen absolute 1e-8 threshold. The physical negative sign
passes the stated numerical decision rule with a wide margin. The eigenvector
failures remain material to representation quality, but do not make this
separately verified sign near zero or unresolved.

## Scope and stopping decision

The result excludes this fixed curved candidate as a linearly stable background
within the tested coupled scalar–radion sector. It neither disproves the
existence of the stationary numerical solution nor identifies its nonlinear
endpoint. In particular, instability does not imply baby-universe formation,
collapse to a horizon, singularity formation, donor accretion, energy transfer,
or relaxation to a different selected vacuum.

The calculation is not a stability classification of all parameter choices,
all backgrounds of this action, the tensor sector, or the independent collapse
scalar. It does not change the accepted finite MOTS/dynamical-horizon core and
does not reconstruct the future of G10. The static candidate and G10 remain
distinct states.

The authorized next-step rule is therefore satisfied: **stop the stability test
with a resolved instability; do not launch the donor-source calculation for
this background, and do not retune this candidate as part of this task.**

## Evidence anchors

Paths in this table are relative to the stability successor. The hashes bind
the exact evidence inspected; the original source and results were read-only.

| Artifact | SHA-256 |
|---|---|
| `CONTRACT.json` | `93202029fff997b8b8ddf2a66bae5b67f3ab3dd0f433dfeb089d2bd29b850ee0` |
| `TEST_SPECIFICATION.md` | `2af32729617afc25a54a3f076fd7742b02f95c07ef944b30c40bd40aec2ee05c` |
| `code/stability.py` | `48b5b5bad1321964c9ac856af3f65a3746469beaa1a294339090f0facbee27fd` |
| `results/shoot_tight.json` | `0fcc09f6baedec1e008e2405d70a68b00a46f3b481c64cdfc66eac113f36f5a2` |
| `results/shoot_tight.npz` | `c16d55eebe4fd37e756fc8c27b2e90e335fd7b427969b981423b8d82c593f059` |
| `results/INDEPENDENT_MODE_CHECK.json` | `d085a230eb8515e3815d28f44d52228465105f1a6daa4c319f5c754004d5f230` |
| `results/shoot_previous_background.json` | `76d88858199651f00acae6dc8d1362f8517f0f81ef98c81ca41d0a738900d8f8` |
| `results/precision_N4096_dps40.json` | `b1ea689fba5483d97543c6beaa2a8e8d074d068a593d1e50eda5d26b7a767a83` |
| `results/precision_N4096_dps60.json` | `9a348b731d94edf11aec3165ae79b8c84d99e9d6ed8bd3d7b559a33cf9f0c5a8` |

The mathematical and primary-literature derivation is in the independently
authored `INDEPENDENT_FORMULATION.md`, SHA-256
`3d51f34d6cd790ef9a025ff6f1018934661ff2c8721d8820b14aa66c506b6828`.
In particular, the de Sitter shift and finite wall equations were checked
against Frolov–Kofman, [Physical Review D 69, 044021](https://arxiv.org/html/hep-th/0309002),
and the canonical kinetic conventions against Kofman–Martin–Peloso,
[Physical Review D 70, 085015](https://arxiv.org/html/hep-ph/0401189).
Those sources supply formulation comparisons; the numerical finding here is
from the separately bound candidate and retained new computation.
