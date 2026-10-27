# R2 serialization correction for the D1 roundoff audit

R1 completed the roundoff calculation in memory but failed before publication
because its JSON writer did not convert NumPy scalar booleans.  R2 imports the
frozen R1 audit source, replaces only its JSON serialization function with an
equivalent writer that calls `.item()` on NumPy scalar values, and executes
the unchanged R1 contract and calculation.

The IEEE allowance, evidence, parent bindings, gates, classifications, and
scientific claim boundary are unchanged.  R2 is not outcome blind because it
is a technical repair of a known publication failure.  No numerical evolution
is rerun.

