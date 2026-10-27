# D1 Cauchy-background admission: failed-gate localization

## Outcome

The test stopped at the first scientific failure, before wall/source admission
and before evolution:

> `D1_CAUCHY_BACKGROUND_NOT_ADMITTED__FULL_HAMILTONIAN_FINEST`

The continuum D1 representative itself passed its preceding phase.  Its launch
value lies inside the certified root box, the two upper-wall residuals are at
most `9.32e-13`, the sampled first-integral residual is `8.57e-15`, and the
static-patch lapse and spatial metric remain strictly positive through
`r=10`.

## Measured production Hamiltonian sequence

| grid `(N_x,N_r)` | full-slice `L_inf` | retained-interior `L_inf` |
|---|---:|---:|
| `(65,121)` | `1.889572534e-1` | `1.907214319e-3` |
| `(97,181)` | `4.125643212e-2` | `4.288196399e-4` |
| `(129,241)` | `1.287352886e-2` | `1.351471343e-4` |

Both sequences decrease monotonically, but they miss the frozen finest-grid
gates `2e-6` and `5e-7`.  The observed refinement orders are approximately
`3.75, 4.05` for the full maximum and `3.68, 4.01` for the retained interior.
Thus the result is a failed finite-resolution admission, not evidence for a
nonzero continuum constraint.

## Where the defect occurs

The full maximum is negative at the lower compact wall and first positive
radial node: `(x_index,r_index)=(0,1)` on all three grids.  On the finest grid
it is `-1.28735e-2`.  The error remains almost radially uniform along the lower
wall, so it is not an isolated axis singularity or artificial outer-face
effect.  Removing successive compact-coordinate rows reduces it rapidly; the
dominant dependence is the one-sided compact-direction curvature stencil.

The constraint was decomposed without changing the saved field:

| grid | scalar-curvature error | scalar-gradient error |
|---|---:|---:|
| `(65,121)` | `1.889572587e-1` | `5.27e-9` |
| `(97,181)` | `4.125643286e-2` | `7.36e-10` |
| `(129,241)` | `1.287352903e-2` | `1.68e-10` |

The production residual is therefore the scalar-curvature discretization
defect to the displayed precision; the scalar derivative is eight orders of
magnitude smaller on the finest grid.  On that grid the curvature-component
errors are `2.05e-4` in the compact Ricci contribution, `3.87e-3` in the
radial contribution, and `4.61e-3` in each of the two transverse
contributions.  Their signed sum gives the measured `1.28735e-2` defect.

The existing production operator explicitly well-balances the conformal
`a=b=c=0` family.  D1's static patch has a nontrivial radial shape
`b=-log(1-k r^2)/2` and a constant compact rescaling `a=log c`; it is outside
that exact discrete balance.  The measured fourth-order decrease is
consistent with a truncation defect in this unmatched representation.

## Independent check

The independent post-run audit reconstructed every saved `q` and source value
exactly from `(A,H,Phi,U,k,c)`.  Its analytic Hamiltonian residual is
`1.03e-13`, its wall residual is below `1.18e-12`, and every integrity and
classification check passes.  Audit status: `VERIFIED`.

The original frozen verifier wrote that valid audit and then encountered a
NumPy-boolean serialization error while printing the already-written summary.
The serialization-only R1 wrapper preserved the frozen verifier and the audit
artifact; no scientific value or classification changed.

## Consequence and minimum next step

This D1 field is **not admitted by the frozen production representation at the
tested grids**, so the wall/gauge phases remain unevaluated and the conditional
short evolution was correctly not run.  The failure does not invalidate the
isolated static D1 theorem; it identifies the first concrete bridge obstacle:
the current anisotropic curvature discretization is not D1-static-patch
well-balanced at affordable resolution.

The minimum discriminating successor is a curvature-only representation test,
not an evolution: independently derive a D1-static-patch background-defect
subtraction analogous to the existing conformal well-balance, verify that it
vanishes on the analytic D1 field and leaves generic perturbations active, and
compare it against a sparse high-`N_x` direct-refinement ladder.  Only after
that operator is prospectively frozen should the complete admission sequence
be repeated.  A simple fourth-order extrapolation suggests roughly `N_x~520`
for the interior gate and `N_x~1150` for the full wall gate, but those are
planning estimates, not verified pass resolutions.

No physical parameter, wall law, threshold, or source anchor was changed, and
no manuscript or parent artifact was modified.
