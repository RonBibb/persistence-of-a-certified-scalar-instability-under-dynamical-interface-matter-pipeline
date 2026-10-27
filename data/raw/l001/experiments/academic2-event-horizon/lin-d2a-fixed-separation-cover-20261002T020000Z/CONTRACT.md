# D2A validated fixed-separation cover

## Question

At the source-bound original proper separation
(D_0=0.9996389747145851), can any admissible positive-curvature launch
(0\le a\le v_0) satisfy both upper wall equations?

## Frozen cover

- Exact-dyadic action and wall inputs from the validated D1 producer.
- Full closed launch range (0\le a\le v_0).
- Exact no-turn lower threshold (a=0.0989750001).
- 1,024 validated proper-distance steps to (D_0).
- 512-bit Arb arithmetic.
- Deterministic bisection to target width (2^{-16}), with a hard maximum
  depth of 24.

Frozen producer SHA-256:
`af68d38340c950a1482c9796c97bec153cb584f7749aab54e8996ab87772346c`.
Imported validated-flow source SHA-256:
`53bcaab6420d050bc4f7e3ca825f74390e0b59b20fe96feae10e72c32288dd3c`.
Imported validated-flow terminal SHA-256:
`0b559edc6f1ec9fe5bba78a0f31812aa773ad393f1040a7efc92c51844452f3d`.

Boxes whose curvature is rigorously negative are outside the positive-(k)
route. For a possible positive-curvature box below the threshold, exclusion
requires a positive scalar path bounded above by (v_0), endpoint
(\Phi_b<v_1), and nonnegative no-turn polynomial. For a box at or above the
threshold, the upper-Israel residual must rigorously exclude zero. Any box
that cannot be certified by depth 24 makes the cover incomplete.

## Prospective classification

If every box is excluded by one of those routes, classify
`FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE`.
This closes the static D2A bridge for the declared wall/action problem. It
does not exclude D2B dynamics, changed physical parameters, or launches
outside the declared admissible (0\le a\le v_0) range.
