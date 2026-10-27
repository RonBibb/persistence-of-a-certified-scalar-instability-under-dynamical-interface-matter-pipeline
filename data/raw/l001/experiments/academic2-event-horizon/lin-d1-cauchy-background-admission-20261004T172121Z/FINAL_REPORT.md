# Final report

The D1-specific static-patch representative passes its certified-root,
continuum-equation, wall-endpoint, positivity, and independent-reconstruction
checks.  It does not pass the production full-slice Hamiltonian gate at the
prospectively frozen resolutions.  The run stopped before later admission
phases and before evolution, as required.

The failed residual is a monotonically decreasing, approximately fourth-order
scalar-curvature discretization defect concentrated at the compact walls and
dominated by the radial/transverse Ricci contributions.  It is not a scalar
gradient defect and is not evidence that the continuum D1 solution violates
the Hamiltonian constraint.  The production anisotropic curvature operator is
well-balanced for its conformal baseline, not for D1's static-patch shape.

Classification:

> `D1_CAUCHY_BACKGROUND_NOT_ADMITTED__FULL_HAMILTONIAN_FINEST`

Minimum next step: a bounded D1-specific curvature well-balance versus direct
high-resolution refinement test.  Do not evolve this representation unless a
new prospectively frozen admission packet passes every original category.

See `FAILURE_LOCALIZATION.md`, `output/RESULT.json`, and
`POSTRUN_AUDIT.json` for the measured evidence.
