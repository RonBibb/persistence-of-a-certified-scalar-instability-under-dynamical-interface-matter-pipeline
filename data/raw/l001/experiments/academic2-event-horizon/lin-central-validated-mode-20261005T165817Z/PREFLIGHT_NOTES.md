# Preserved synthetic preflight corrections

No D1 physical interval flow was evaluated in either failed synthetic preflight.

1. `preflight-1` stopped while restoring the first analytic-vacuum checkpoint.
   Native midpoint/radius tuple reconstruction is not universally exact for this
   pinned Arb interface. For example a radius `773277837 * 2^-720` reconstructed
   as `773277838 * 2^-720`. The pre-freeze fix canonicalizes outward to a
   constructor-stable radius and continues with that same state on both the
   uninterrupted and resumed paths. Exact post-canonical roundtrip and
   fresh-process continuation remain required, not assumed.

2. `preflight-2` completed the primary analytic/recovery path but stopped on the
   first independent vacuum Picard cell. In the pinned python-flint 0.9.0 runtime,
   `arb(0,(1,-640)) ** 2` returns `nan`, whereas multiplication of that ball by
   itself returns a valid enclosure approximately `+/-4.81e-386`. Runtime squares
   of interval fields are therefore expressed as explicit multiplication. This
   preserves the polynomial equations (and can widen an enclosure); it is not a
   change to the physical model. Symbolic exact polynomial identities retain
   mathematical powers. This matters to regularity through the scalar-gradient
   zero and is checked before production.

The failed synthetic directories are retained unchanged. These are implementation
preflight failures, not counterexamples to static existence or the numerical mode.
No source is frozen until the corrected full analytic and fresh-process controls
and the independent source review pass.
