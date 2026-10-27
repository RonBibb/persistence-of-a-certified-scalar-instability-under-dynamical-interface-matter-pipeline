# Independent terminal review — T15

ACCEPTED: CERTIFIED_COMPACT_WALL_COMPARISON, all three cases individually verified. All 43 bindings match. Execution began 17:00:39.501473Z after T16 publication/acceptance, completed in 259.417 seconds on one core, exited 0 and reaped child 1699411. No case failure was substituted with another result. Independently checked each fine width <=1e-6, coarse/fine overlap, L/g residual overlap, strict endpoint signs and audit constraint containment from exact records.

The positive shifted gaps are:

- Lower Dirichlet/upper soft: [0.000127826171875,0.0001288017578125].
- Lower soft/upper Dirichlet: [0.00013806982421875,0.00013904541015625].
- Equal kappa=100: [0.0001990439453125,0.00020001953125].

All three full mass intervals lie in their unchanged T16 prediction windows. The mixed orientations are measurably different, so the symmetric leading parabola is a useful finite-accuracy approximation, not an exact orientation symmetry. The large-finite-stiffness prediction also succeeds with its inherited derivative/root uncertainty retained. Neither comparison proves a uniform finite-t or short-interval remainder.

One pinned wall already moves the persistent eigenvalue close to its double-Dirichlet ceiling; it does not remove the mode or raise it above -12. The comparison uses the same interval/background and inherited compactified wall family, not a changed physical action or nonlinear evolution.
