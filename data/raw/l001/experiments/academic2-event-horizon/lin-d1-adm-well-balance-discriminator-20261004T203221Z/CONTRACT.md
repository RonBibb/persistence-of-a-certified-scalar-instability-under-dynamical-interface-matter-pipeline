# D1 ADM-equilibrium well-balance discriminator

The verified D1 curvature, wall, and GH gauge background formulations pass.
The next unchanged gate is the curvature-corrected ADM acceleration, dominated
by the compact `zz` component (`2.705e-3 -> 8.471e-4` from `97x181` to
`129x241`, gate `5e-5`).

Producer A defines a standard equilibrium-preserving operator

`A_WB(q) = A_prod(q) - A_prod(q_D1) + A_exact(q_D1)`,

where the exact static acceleration is zero.  This changes no continuum
equation.  A coherent smooth `1e-6` conformal metric perturbation must produce
a finite nonzero response.  Original grids are retained.

Producer B evaluates the predecessor's curvature-corrected ADM operator
unchanged at fixed `N_r=241` and
`N_x=(129,193,257,385,513)`.  It passes only with monotone maximum residual,
last observed order in `[2,6]`, finest residual `<=5e-5`, and two consecutive
absolute passes.  It is diagnostic only.

After Producer A passes, all already admitted curvature, wall, gauge, source,
axis, and outer gates remain in force.  The raw GH acceleration is unchanged.
Only a pass of every gate authorizes four unperturbed midpoint steps at
`dt=0.000125`, with atomic checkpoints.

Classifications:

- `D1_ADM_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS`
- `D1_ADM_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_<GATE>`
- `D1_ADM_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED`
- `D1_ADM_WELL_BALANCE_TECHNICAL_INCOMPLETE`

This remains a finite-resolution formulation test for one certified D1
background; it supports no continuum, stability, P16, collapse, parent-child,
or causal inference.

