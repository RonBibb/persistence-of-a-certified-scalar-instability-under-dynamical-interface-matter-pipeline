# Contract for a future D1 Cauchy embedding

## Shared model data

The new family must bind one exact parameter ledger for `Lambda5`, `m^2`,
`gamma`, `v0`, `v1`, and both bare wall tensions.  The existing D1 and P16
upper-tension literals are not silently identified.  The independent collapse
scalar is zero in the background.

## Frozen geometric choices

Before construction, choose exactly one complete Cauchy chart:

- static patch: zero shift and `K_ij=0`, finite radial domain strictly inside
  `r=1/sqrt(k)`;
- flat slicing: flat radial geometry but nonzero tangential `K_ij`; or
- global slicing: a time-symmetric three-sphere rather than the current radial
  topology.

The compact coordinate map, lapse, shift, outer radius, and radial topology
are frozen with that choice.  They cannot be mixed across charts.

## Data transferred from D1

Transfer the certified interval profiles `A(s)`, `Phi(s)`, curvature `k`,
proper separation `D`, and conformal length `L`.  From one common represented
field derive:

- all nine production fields `q`;
- their first time derivatives and ADM `K_ij`;
- `q_x`, `q_r`, and `q_xr` at both walls;
- scalar momenta;
- the geometric GH source and its required boundary jets;
- D1-specific source targets and outer reference data.

No P16 source array is imported merely because it uses the same field names.

## Constraints and boundary equations to solve

The represented field must pass, together and at unchanged prospective gates:

1. Hamiltonian and momentum constraints throughout the full slice;
2. both metric and scalar wall junction conditions at every radial point;
3. regular-axis conditions;
4. complete outer characteristic compatibility, including time and radial
   source moments;
5. gauge-driver consistency with D1-specific anchors;
6. positivity and signature over the represented domain; and
7. an independent implementation check of the same quantities.

Analytic continuum satisfaction is not a substitute for checking the actual
production representation and boundary operators.

## Remaining free data

The chart and compatible outer reference are data choices.  A later collapse
perturbation may specify `chi` and its momentum, but the complete constraints
must then be re-solved; it may not be superposed.  None of these freedoms may
be used to claim that the existing P16 data are D1.

## Pass and stop rules

The background embedding passes only if one common field satisfies every
constraint, wall, axis, gauge, and outer-boundary gate.  A corner-only or
source-only pass is insufficient.  A failed physical junction or constraint
stops before evolution.  A passed background permits only a short unperturbed,
refinement-controlled preservation evolution; it does not establish stability
or dynamical selection.

The current assessment outcome is:

> `FAILS_AS_DIRECT_P16_JOIN; ADMISSIBLE_AS_A_PROSPECTIVE_NEW_D1_BACKGROUND_EMBEDDING`.

