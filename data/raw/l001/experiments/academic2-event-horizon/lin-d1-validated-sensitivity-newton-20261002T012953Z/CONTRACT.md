# D1 validated sensitivity and interval-Newton contract

**Activation:** 2026-10-02T01:29:53Z  
**No-new-test cutoff:** 2026-10-02T02:29:53Z

## Objective

Complete the cheapest decisive remaining D1 test for the exact-dyadic reduced
proper-distance shooting problem: validate the (a)-variational equation,
enclose the first-event derivative

\[
 D'(a)=-G_a/G_s,
\]

enclose the total derivative of the upper scalar residual, and apply a
one-dimensional interval-Newton test.

## Frozen numerical proof design

- State plus sensitivity:
  ((A,H,\Phi,S,Z,k,\partial_aA,\partial_aH,\partial_a\Phi,
  \partial_aS,\partial_aZ,\partial_ak)).
- Exact input interpretation: each declared binary64 value is promoted to its
  exact dyadic rational.
- Arb precision: 512 bits.
- Validated propagation: Picard self-enclosure on every fixed cell plus a
  second-order Taylor endpoint enclosure for the augmented system.
- Proper-distance range: (0\le s\le2).
- Predeclared step counts: 4,096, 8,192 and 16,384.
- Frozen center: `0.09901086589880687`.
- Frozen wide box:
  `[0.09901086289880687, 0.09901086889880687]`.
- Frozen narrow box:
  `[0.09901086489880687, 0.09901086689880687]`.
- Every step level and both boxes are run; no adaptive rescue box is allowed.

On the rigorously identified first upper-Israel event, compute

\[
 G_a=p_H-\frac{\gamma}{6}(\Phi-v_1)p_\Phi,
 \qquad D'=-G_a/G_s,
\]

and

\[
 h'=\left(p_S+\frac\gamma2p_\Phi\right)
       +\left(S_s+\frac\gamma2S\right)D'.
\]

At each level and box, form

\[
 N(X)=m-\frac{h(m)}{h'(X)}.
\]

## Prospective classification

`RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS` requires:

1. all dual-algebra controls pass;
2. all augmented Picard and Taylor steps complete;
3. each event is first, contiguous and transverse with (G_s<0);
4. every derivative enclosure excludes zero; and
5. all six predeclared interval-Newton images are strict self-maps.

Any technical failure is `VALIDATED_SENSITIVITY_NEWTON_INCOMPLETE`. Completed
propagation without all six strict self-maps is
`VALIDATED_SENSITIVITY_NEWTON_NOT_ESTABLISHED`. Neither negative class proves
nonexistence.

## Claim boundary

A passing result proves a unique root only for the declared reduced shooting
problem and within each certified Newton box. Independent replay and complete
derived-quantity/wall-identity enclosures remain separate D1 closure tasks.
It does not supply a same-development bridge, stability, a collapse event
horizon, or authority for D2B evolution.

Frozen producer SHA-256:
`9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653`.
