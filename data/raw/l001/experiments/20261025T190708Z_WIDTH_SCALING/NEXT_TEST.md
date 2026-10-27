# Prospective uniform spectral remainder test

## Question

Does the effective sixth-order coefficient satisfy

383/1200 <= [-lambda - D²/6 + 5D⁴/36]/D⁶ <= 383/800

for every 0<D<=.02 in the same double-Dirichlet family?

The current packet proves a uniform leading quadratic envelope and derives the exact local coefficient 383/960. Three finite widths support that coefficient, but they do not answer this continuous-domain question.

## Proposed characteristic

Use the accepted scaled system with d=D/2 and parameterize

lambda(d,beta) = -2d²/3 + 20d⁴/9 + beta d⁶.

The desired beta interval is [-766/25, -1532/75], containing the analytic limit -383/15. Normalize the lower-end metric profile as before and let C(d,beta) be the upper-end scalar residual F(1).

The accepted analytic series implies that C has a factor d⁴ on this parameterization. Derive the factored function analytically and certify its interval enclosure, including the limit at d=0. Do not evaluate a wide interval for C and divide it by d⁴: near zero that destroys the cancellation and cannot certify the requested statement.

A successful test would prove opposite strict signs of the factored characteristic at the two beta endpoints on every parameter subdomain covering [0,.01]. The accepted root-count argument and fresh endpoint hypotheses would then identify the enclosed branch. The formal endpoint d=0 remains a limit, not a physical zero-width problem.

## Method qualification before production

A parameter-Taylor enclosure must retain both the coefficients and a rigorous remainder over each parameter subdomain. It must propagate the parameter dependence of the background, lower-end launch and boundary normalization, rather than substitute point values or fixed central seeds.

Independently review the transformation, the four-power cancellation and the factored limiting signs. Qualify signed spatial steps, interval-parameter dependence, reciprocal denominators, whole-tube remainders and the distinction between polynomial coefficients and bounded remainders. Include a manufactured cancellation control and agreement with the accepted pointwise method at declared positive widths. Failure of these controls is technical incompleteness, not a physical conclusion.

Only after qualification should a predeclared continuous parameter cover be frozen. Preserve every failed enclosure and inconclusive sign. Do not raise degree, subdivide or tighten a gate in place after observing failure; a redesigned successor receives a separate contract.

## Evidence and interpretation

A complete result requires the full parameter cover, strict endpoint signs, source and parent fingerprints, constraint and background gates, preserved raw records, and independent terminal review. Sampling extra widths or fitting a polynomial is not a substitute.

A pass provides a uniform D⁶ envelope after subtracting the known D² and D⁴ terms. It still does not by itself give an O(D⁸) remainder bound around the exact sixth-order coefficient. A failure to enclose a sign does not prove the proposed coefficient window false unless a separate certified counterexample exists.

This design is prospective only. No successor is launched, and no computation is authorized beyond the current allocation. Resource estimates and checkpoint requirements must be established before a later production run; any job exceeding one hour needs exact-resumption checkpoints and integrity-before-resume checks.
