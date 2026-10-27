# T3 expression-isolation terminal review

**ACCEPTED — PASS_POLYNOMIAL_EVALUATION_QUALIFIED.** The captured failure has a supported operation-level cause: original P**3 evaluates nonfinitely on this captured zero-crossing Phi ball in the pinned runtime, making T-prime and its candidate nonfinite. Mathematically equivalent repeated multiplication gives a finite outward enclosure and a candidate strictly inside the unchanged original tube.

I inspected the result, expression diagnosis, execution record and the 21 control records against the previously reviewed arithmetic and source. Every repeated-multiplication output is finite; the producer's exact rational range tests passed. The original power outputs are nonfinite in exactly six recorded cases: powers 2,3,4 for the zero-centered radius-one ball and the actual Phi tube. The other fifteen original outputs are finite and passed the exact-range containment controls. This is a bounded observed pattern, not a universal statement about all crossing intervals, all integer powers, other runtime versions or Arb internals.

The reconstructed tube matched T2 raw records. In the captured expression, 1-P and -4HT are finite, whereas 4*(P**3) is nan. The original T-prime is nan. P*P*P is finite and the replacement expression encloses T-prime near 1; its first candidate has endpoints strictly within the original symmetric T tube. The original tube, step, physical polynomial, rates and precision were not changed. Exact seed agreement also passed. The isolated substitution therefore resolves the specific first-step expression obstruction without claiming completion of any integration.

The admitted repeated-multiplication range reasoning is valid for each fixed integer exponent: outward interval products enclose the corresponding exact real polynomial range, even where dependency widens the result. The seven-ball controls operationally corroborate it in the pinned runtime. They do not certify every subsequent integration tube, accuracy target or source translation.

Execution began 14:20:44.523954Z, before cutoff, used one core CPU0 and exited zero; child 1671723 was reaped after 0.1923685419606045 seconds. Source/parent/runtime invariant gates are recorded passed; current own plan/producer hashes match admission. No original failed packet changed its classification. No numerical transition coordinate was produced and no blanket library-bug claim is justified.

| Artifact | SHA-256 |
|---|---|
| RESULT.json | f75cc7f740d43209c1ee3e5b8831e1caf3a0bd88c045ece78e6e6478b7465f9a |
| POLYNOMIAL_CONTROLS.json | 2d06c5839f6ab3ea5640be14ef59d55b90192c9f2124b2621abf903926bdd85f |
| EXPRESSION_DIAGNOSIS.json | e10e2930acaa9069e3c6295f1c8e4f8cda0081dad2eb58f45777f5ad007f86c5 |
| EXECUTION.json | 99b05d1a31d76233a362cabb816d131f060e324df3b2f12b2d14ca308cb8f23c |
| PLAN.md | 3331c0cc007f68d2bd887f0ac81f69f9598fbcacec82754db141fddbb200f5ad |
| producer.py | dba03521eb9c8923777729b65ba54a96dbd4d5562bce1881cc05b5ee4434ebe2 |

A separately reviewed implementation-corrected producer is scientifically justified. It is not admitted here. This independent agent review ran no numerical computation and requests no change to the completed T3 packet.
