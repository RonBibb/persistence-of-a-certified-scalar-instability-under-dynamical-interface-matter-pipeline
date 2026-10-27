# Independent D1 formula and inclusion audit

This audit does not import the validated producer. It independently derives
the six-state variational equation, all launch sensitivities, (G_s,G_a), and
the total event derivative of the upper scalar residual with SymPy. It then
uses exact rational arithmetic to check all six recorded Newton images against
their frozen boxes and tests the expected finer-level nesting.

Pass requires all symbolic identities, exactly five strict self-maps, the only
miss at the predeclared 4,096-step narrow case, and nesting of both 16,384-step
images inside their 8,192-step counterparts.

This checks formulas and certificate arithmetic independently. It is not an
independent implementation of the Arb ODE enclosure and cannot by itself
promote the frozen aggregate R1 classification.

Frozen audit source SHA-256:
`d7fb80006175ab1fa281247732d3289526d54c71b7e27ca8de9c480f2f9d514c`.

Frozen certificate SHA-256:
`7f3e1ec5c464f6790934534acabe200aab54413453b4e237f50525b9f8485725`.
