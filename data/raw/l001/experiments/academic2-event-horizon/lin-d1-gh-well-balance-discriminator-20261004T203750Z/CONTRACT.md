# D1 full-GH equilibrium well-balance discriminator

The verified curvature, wall, gauge, and ADM equilibrium formulations pass.
The final unchanged admission gate is raw GH acceleration, dominated at
`65x121` by `h00=h_perp=1.052e-2` and `hzz=3.321e-3` against `1e-4`.

Producer A uses the standard equilibrium-preserving semidiscrete RHS

`F_WB(q,v) = F_prod(q,v) - F_prod(q_D1,0) + F_exact(q_D1,0)`,

with `F_exact(q_D1,0)=0`.  The same production RHS, source, wall/axis/outer
closure, and continuum equations appear in both terms.  A coherent smooth
`1e-6` metric perturbation must produce a finite nonzero acceleration.

Producer B evaluates the unchanged raw GH acceleration at fixed `N_r=241`
and `N_x=(65,97,129,193,257)`.  It passes only with monotone maximum,
last order in `[2,6]`, finest `<=1e-4`, and two consecutive passes.

Only after every prior and current gate passes, run four explicit-midpoint
steps at `dt=0.000125` on the two frozen evolution grids with atomic
checkpoints.  This tests immediate preservation of the exact equilibrium,
not nonlinear stability.

Classifications:

- `D1_FULL_GH_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS`
- `D1_FULL_GH_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED`
- `D1_FULL_GH_WELL_BALANCE_TECHNICAL_INCOMPLETE`

No continuum, stability, P16, collapse, parent-child, or causal claim follows.

