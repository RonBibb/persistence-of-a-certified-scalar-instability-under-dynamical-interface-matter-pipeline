# D1 lower-wall well-balance discriminator R1

This is a technical correction of the frozen D1 wall discriminator.  The
scientific contract, grids, fields, gates, wall well-balance, direct-refinement
arm, admission sequence, conditional evolution, and claim boundary are
unchanged.

The first execution reached the source/gauge stage after both wall arms
passed, then stopped because its inherited admission helper expected the
legacy `GaugeTaylorSource` diagnostic attributes
`source_time_reduced/source_time_z/source_time_r` on a
`StageRegularGaugeSource` instance.  The actual stage object stores the same
zero source-time field as `source_time`; its spatial derivatives are exactly
zero in this static-source test.

R1 supplies a read-only compatibility adapter:

- `source_time_reduced = source_time`;
- `source_time_z = 0`;
- `source_time_r = 0`.

The public `at(i,j,t)` method, live source values, source spatial derivatives,
GH operator, physical fields, and every scientific gate remain unchanged.
The adapter is tested independently before execution.  No outcome from the
failed first run is used to change a scientific choice.

