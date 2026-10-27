# D1 global first-event uniqueness result

## Result

The certified D1 root is the only positive-curvature simultaneous-wall solution on the complete declared launch interval for first-event placement.

- Classification: `GLOBAL_FIRST_EVENT_SIMULTANEOUS_WALL_ROOT_UNIQUE_ON_DECLARED_POSITIVE_CURVATURE_LAUNCH_INTERVAL`
- Post-run audit: `VERIFIED`
- Exact gap-free cover: `True`
- Terminal boxes: 726
- Certified root boxes: 1
- Negative-curvature exclusions: 19
- Dual-producer first-event scalar exclusions: 706
- Unresolved boxes: 0
- Dual-evaluated boxes including refined attempts: 736
- Accumulated wall time: 1282.9 s
- Worker processes: 10

## What was established

The existing interval-Newton certificate supplies exactly one root in the
inherited narrow D1 box. The new exact cover accounts for every launch value
outside that box. Every admitted positive-curvature exclusion was reproduced
by both the validated second-order Taylor/Picard flow and the independent
fifth-order Taylor/Picard flow: both locate the first transverse upper-Israel
event and enclose the scalar residual strictly on the same side of zero.

## Boundary of inference

This is a global uniqueness result only for the declared reduced static
first-event shooting problem. It does not establish dynamical selection,
stability, collapse matching, a MOTS, an event horizon, a radion transition,
or a baby universe. D2A and the manuscripts were not changed.
