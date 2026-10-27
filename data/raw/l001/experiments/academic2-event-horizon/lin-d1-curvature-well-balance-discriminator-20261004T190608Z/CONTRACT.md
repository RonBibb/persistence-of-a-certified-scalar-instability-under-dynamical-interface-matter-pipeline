# D1 curvature well-balance discriminator

## Bounded question

The preceding D1 Cauchy-background test found an approximately fourth-order
production scalar-curvature defect even though the independent continuum
Hamiltonian was `1.03e-13`.  This experiment freezes two producers before
outcome and asks whether that failed gate is removable by an analytically
well-balanced D1 background representation or by direct refinement of the
unchanged production operator.

No action parameter, wall law, source anchor, physical field, root, domain, or
admission threshold may change.

## Common authority and field

- Use the previously frozen representative D1 root/profile and reconstruct it
  from the same immutable source.
- Static-patch chart: `x in [1,e]`, `r in [0,10]`, zero shift,
  `K_ij=Pi_Phi=Pi_chi=0`, and `chi=0`.
- Production stencil width: 7.
- Existing admission gates remain:
  - full Hamiltonian `<=2e-6`;
  - retained interior Hamiltonian `<=5e-7`;
  - wall `<=2e-6` at the candidate and `<=2e-5` on every evaluated level;
  - axis `<=5e-12`;
  - GH source absolute/local-relative `<=5e-5`;
  - source traces/moment and outer residuals `<=1e-12`;
  - ADM acceleration `<=5e-5`;
  - GH acceleration `<=1e-4`.

## Producer A: analytic D1 curvature well-balance

Evaluate grids `(65,121)`, `(97,181)`, and `(129,241)`.  For each Ricci
component define

`Ric_WB(candidate) = Ric_prod(candidate) - Ric_prod(D1) + Ric_exact(D1)`.

The exact D1 static-patch contributions in the represented chart are

- `Ric_xx/g_xx = -3(H_s+H^2)`;
- `Ric_rr/g_rr = Ric_perp/g_perp = 2k exp(-2A)-H_s-3H^2`;
- `Ric_xr=0`;
- `H_s=-U^2/3-k exp(-2A)`.

The Hamiltonian uses the corrected scalar curvature but the unchanged
production scalar-gradient operator.  This changes no continuum equation:
the subtracted production defect converges to zero.  A `1e-6` smooth synthetic
metric perturbation is evaluated only as an operator control; the corrected
operator must have a finite, nonzero response and must not project generic
departures back to D1.

For the ADM equilibrium gate, replace only the production Ricci term by the
corrected Ricci term.  The lapse Hessian, matter terms, wall rows, source rows,
axis treatment, and GH evolution operator remain unchanged.  This prevents a
curvature-only correction from silently repairing an unrelated equation.

## Producer B: unchanged high-resolution production operator

Hold the already adequate radial grid at `N_r=241` and evaluate the unchanged
production operator at

`N_x = 257, 513, 1025, 1537, 2049`.

This reaches beyond the prior fourth-order planning estimate for the full wall
gate.  Producer B passes its Hamiltonian discriminator only if:

- the finest full and interior residuals meet the existing gates;
- both residual sequences are monotonically decreasing; and
- the last-pair observed orders lie in `[2,6]`.
- at least two consecutive levels meet both absolute Hamiltonian gates before
  Producer B can advance to the complete admission or evolution stages.

No extrapolated value counts as a pass.

## Required comparisons

For both producers record:

- full-domain Hamiltonian `L_inf`;
- retained interior `[3:-3,3:-3]` `L_inf`;
- lower-wall first-positive-radius residual;
- compact, radial, and each transverse Ricci-contribution error;
- measured refinement orders; and
- the independent analytic Hamiltonian and wall identities.

## Conditional complete admission

Only a producer passing its Hamiltonian discriminator advances.  It must then
pass the same wall/axis, source/reference/outer, ADM-equilibrium, and raw GH
equilibrium gates used in the previous admission packet.  Producer A's raw GH
gate is deliberately uncorrected; Producer B is unchanged throughout.  A
failure stops that producer before evolution.

If and only if one producer passes every admission category, run four
explicit-midpoint steps with `dt=0.000125`, static D1 source, unchanged
wall/axis/outer closure, and exact atomic per-step checkpoints.  Evolution
gates and claim boundaries are identical to the preceding packet.

## Classification

- `D1_CURVATURE_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS`
- `D1_DIRECT_REFINEMENT_ADMITS__SHORT_PRESERVATION_PASS`
- `D1_CURVATURE_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_<GATE>`
- `D1_DIRECT_REFINEMENT_REACHES_HAMILTONIAN_GATE__FULL_ADMISSION_BLOCKED_<GATE>`
- `NEITHER_D1_CURVATURE_PRODUCER_ADMITS`
- `D1_CURVATURE_DISCRIMINATOR_TECHNICAL_INCOMPLETE`

Passing is finite-resolution formulation evidence only.  No stability,
collapse, parent/child, causal-horizon, P16-join, or manuscript inference is
authorized.
