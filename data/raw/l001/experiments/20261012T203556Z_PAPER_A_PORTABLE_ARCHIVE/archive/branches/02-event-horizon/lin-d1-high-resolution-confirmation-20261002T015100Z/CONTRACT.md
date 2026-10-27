# D1 high-resolution confirmation

This prospective confirmation reuses the frozen validated producer and the
separately corrected Arb containment self-test. It changes only:

- step count to 32,768; and
- Arb precision to 768 bits.

Both previously frozen wide and narrow root boxes are run. Pass requires both
events to remain first and transverse, both (h') intervals to exclude zero,
and both Newton images to be strict self-maps. The resulting images will then
be compared by exact rational arithmetic with the 16,384-step images; nesting
is reported as a control but is not required by the producer.

This confirms step refinement of the same implementation. It is not an
independent ODE implementation, a same-development bridge, or an event-horizon
calculation.

Frozen parent producer SHA-256:
`9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653`.

Frozen R1 correction wrapper SHA-256:
`c388b3bd1e616f38dfa9a27be9d74cbe1de0b618386749e32fbc8a2de48896f3`.

Frozen confirmation wrapper SHA-256:
`98d17ad555c7012266debe9e406fab02eae6db6b57dbe41c53dc635c66e7fe09`.
