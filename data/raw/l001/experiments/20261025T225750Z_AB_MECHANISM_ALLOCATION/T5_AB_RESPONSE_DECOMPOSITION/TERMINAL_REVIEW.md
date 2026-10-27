# Independent terminal review — T5

Decision: **ACCEPTED — fixed-operator response decomposition**, not a new trajectory or nonlinear causal attribution.

Reviewer: strength_review. All computational verification was performed on academic-linux under the shared admission lock and one pinned CPU lease. No ODE was replayed. The audit has exited and released its lease.

## Integrity and reconstruction

- All 123 admission source bindings verified unchanged.
- Execution exited 0, child reaped, recorded wall time 0.571549792 seconds; the six manufactured controls passed.
- Independently implemented rational endpoint arithmetic reconstructed 88 saved fields and engine hulls exactly from immutable T4 and T2R1 records. Both engine intervals overlap before hulling.
- Reconstructed the two response coefficients `(IP - FP IH/FH)/Ra` and `-IH/(2 FH)`, each geometric and direct-current load, both bulk responses, explicit interface displacement, totals, proper-density conversion, and neutral kinetic complement. Required denominators exclude zero.
- Reconstruction overlaps the accepted parent bulk and total intervals. The zero-containing subtraction intervals are dependency-enlarged consistency checks, not measured physical residuals.

## Findings (decimal summaries)

For lower-wall unit current, the explicit displacement contribution is approximately -72.84735, the bulk response to its geometric load is [-0.07424794, -0.07383020], and the bulk direct scalar-current response is [-4.97560e-6, -4.94760e-6]. Their total is [-72.921600, -72.921179].

For upper-wall current, expressed per unit local proper-density coefficient, the explicit displacement is [-1.330671, -1.329032], the geometric-load bulk contribution is [-0.001392003, -0.001387094], and the direct scalar-current bulk contribution is [-1.513462e-6, -1.509161e-6]. The total is [-1.3320640, -1.3304212].

All three contributions have the same negative sign in the declared representation. Explicit interface displacement dominates this **fixed-chart response budget**; the direct scalar-current forcing contributes much less. This is not a gauge-independent partition into separate physical causes: bulk, interface, and source-split terms individually depend on the fixed redshift/longitudinal chart. The assembled proper separation on the declared cuts is the relevant combined observable.

The neutral-mode metric kinetic-norm fraction, obtained through the exact normalization identity rather than intersecting or rescoring the raw metric ratio, is enclosed by [0.99998226245, 0.99998272619]. The raw ratio [0.99789505, 1.00207431] remains preserved. This is a kinetic-norm statement, not an energy or excitation probability.

## Physical scope

The charged correction remains negative at a fixed time, while its multiplier decays as exp(-6 h t). Consequently its time derivative is positive: the first-order charged correction relaxes toward the background separation; it does not establish ongoing contraction. The growing neutral mode has a separate freely chosen amplitude. Neither this decomposition nor the kinetic complement fixes that amplitude, proves finite-charge behavior, or transfers conclusions between the AB and concave-example backgrounds.
