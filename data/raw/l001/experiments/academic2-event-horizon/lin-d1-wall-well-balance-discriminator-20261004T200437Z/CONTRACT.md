# D1 lower-wall well-balance discriminator

## Bounded question

The frozen curvature discriminator repaired the D1 bulk Hamiltonian from
`1.287e-2` to `1.683e-10`, then stopped at the unchanged lower compact-wall
position residual (`7.622e-6` against `2e-6`).  This experiment asks whether
that remaining failure is the analogous finite-difference representation
defect in the wall rows.

No certified root, field, domain, wall action, wall coefficient, gauge source,
physical parameter, gate, or continuum equation may change.

## Producer A: D1-background wall well-balance

On grids `(65,121)`, `(97,181)`, and `(129,241)`, retain the frozen
D1-curvature well-balance and define each compact-wall residual row by

`J_WB(q) = J_prod(q) - J_prod(q_D1) + J_exact(q_D1)`.

The exact D1 wall residual is zero by the independently certified Israel and
scalar endpoint identities.  Thus the correction subtracts only the
finite-difference image of the exact background and changes no continuum wall
law.  The rows are the four tangential metric Robin conditions, the scalar
Robin condition, reflecting chi, and the normal-tangential Dirichlet data.

A smooth `1e-6` perturbation of one tangential metric field must produce a
finite, nonzero corrected wall response.  This forbids an implementation that
simply returns zero for arbitrary candidate data.

## Producer B: unchanged direct wall refinement

At fixed `N_r=241`, evaluate the unchanged production wall operator at

`N_x = 129, 193, 257, 385, 513`.

The direct arm passes only if the residual is monotone, the final observed
order lies in `[2,6]`, the finest value is at most `2e-6`, every evaluated
value is at most `2e-5`, and at least two consecutive levels meet the
candidate gate.  No extrapolated value counts as a pass.  This arm diagnoses
the wall operator only; it cannot override the preceding non-monotone bulk
curvature result.

## Conditional complete admission

Producer A advances only after the corrected Hamiltonian and corrected wall
rows meet their existing gates.  The regular-axis, source, gauge,
outer-reference, corrected-ADM, and raw-GH equilibrium tests remain identical
to the frozen predecessor.  No later gate is relaxed or silently
well-balanced.

Only if all complete-admission categories pass may the already frozen
four-step unperturbed evolution (`dt=0.000125`) run.  The raw GH evolution
operator remains unchanged, while diagnostics use the admitted curvature and
wall well-balances.  Atomic per-step checkpoints are required.

## Existing gates

- full Hamiltonian `<=2e-6`;
- retained interior Hamiltonian `<=5e-7`;
- candidate wall `<=2e-6`, every evaluated wall `<=2e-5`;
- axis `<=5e-12`;
- gauge absolute/local-relative `<=5e-5`;
- source traces/moment and outer residuals `<=1e-12`;
- ADM acceleration `<=5e-5`;
- raw GH acceleration `<=1e-4`.

## Classification

- `D1_WALL_WELL_BALANCE_ADMITS__SHORT_PRESERVATION_PASS`
- `D1_WALL_REPRESENTATION_IDENTIFIED__FULL_ADMISSION_BLOCKED_<GATE>`
- `D1_WALL_REPRESENTATION_IDENTIFIED__SHORT_EVOLUTION_BLOCKED`
- `D1_WALL_WELL_BALANCE_TECHNICAL_INCOMPLETE`

Passing is finite-resolution formulation evidence for one D1 background, not
a continuum, stability, collapse, P16, parent-child, or causal-horizon result.

