# D1 validated sensitivity/Newton R1 correction

**Parent activation:** 2026-10-02T01:29:53Z  
**Shared no-new-test cutoff:** 2026-10-02T02:29:53Z

The frozen parent source failed before executing an ODE step because its Arb
quotient-rule control compared an enclosing ball to an exact value by object
equality. Independent inspection confirms that the computed derivative ball
contains the exact value (1/25), while object equality is false because Arb
retains a nonzero outward radius.

R1 changes only that self-test predicate from equality to containment. It
imports the parent producer byte-for-byte and replaces only
`dual_algebra_controls`. All scientific equations, exact inputs, root boxes,
step counts, precision, classifications and claim boundaries remain frozen.

Parent producer SHA-256:
`9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653`.

Parent incomplete-result SHA-256:
`bb0778bcbafb0f86691304054008a916154045d8c0aa8e8876c4ef94f0779975`.

R1 wrapper SHA-256:
`c388b3bd1e616f38dfa9a27be9d74cbe1de0b618386749e32fbc8a2de48896f3`.
