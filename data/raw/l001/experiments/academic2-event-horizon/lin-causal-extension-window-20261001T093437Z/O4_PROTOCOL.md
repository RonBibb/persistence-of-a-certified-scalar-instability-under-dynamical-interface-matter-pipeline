# O4 — P407 late-state bulk-wall compatibility diagnostic

O4 is a fixed-state diagnostic on authenticated H-steps 512, 1152 and 1792.
It performs no evolution and changes no state.  At each endpoint it
reconstructs the exact P407-R2 `qualified-batched` RHS stage, then applies the
reviewed branch-01 physical Einstein/scalar and twice-time-differentiated wall
functionals at the registered radial samples 35 and 36 and compact-direction
probes 0,1,2,4,124,126,127,128.

The output is descriptive.  Near-formation magnitudes are not frozen as late
pass/fail thresholds.  Technical success requires exact input/source binding,
finite reconstructed stages, active `legacy_wall_axis_outer`, all optional
wall forcings `None`, and finite diagnostic arrays.  Raw bulk acceleration is
retained only as a counterfactual comparator and is never substituted into a
state.

Starting after 2026-10-01T11:34:37Z is forbidden.  A valid start record written
before that cutoff may finish afterward.

