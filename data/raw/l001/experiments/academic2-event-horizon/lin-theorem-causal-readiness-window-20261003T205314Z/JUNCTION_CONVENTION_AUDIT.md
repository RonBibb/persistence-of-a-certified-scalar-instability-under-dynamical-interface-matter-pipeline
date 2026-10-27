# Line-by-line junction convention audit

## Question

Do the doubled-cover action, the source manuscript's outward-normal convention,
the proper-distance reduction, and the independently replayed D1 residuals use
the same signs and factors at both walls?

## Bound records

- source action: `source-snapshot/brane-horizon-phase-structure/MODEL_V1.md`,
  SHA-256 `4077686eb06ea8eea23d11b059336db877d8466f34b710f0fa416e116d343dc9`;
- source manuscript convention: `source-snapshot/free-boundary-mots-saddle-node/article/universe-submission/supplement.tex`,
  SHA-256 `f9833992b611f6cc5fc55f461b683252cc8a726c273c3ee7b2931257f7da5f27`,
  lines 112--135 in the current file;
- independent replay implementation:
  `lin-d1-independent-ode-replay-20261002T225837Z/independent_d1_replay.py`,
  SHA-256 `d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044`;
- sealed independent result SHA-256
  `41077a7977079705dbd49379f2f9ecb3fe9c007c518b02277aba6aa4b8df7d16`.

## 1. Outward-normal source convention

The source manuscript declares the doubled-cover wall action and gives the
one-sided equations, with the normal pointing **out of the retained interval**,

\[
 K^{\rm out}_{\mu\nu}=\frac{\kappa_5^2}{2}
 \left(S_{\mu\nu}-\frac13S h_{\mu\nu}\right),
 \qquad n_{\rm out}\!\cdot\!\nabla\Phi=-\frac12U_{i,\Phi}.
\]

For a pure scalar-dependent tension
`S_mu_nu=-tau_i h_mu_nu` in four wall dimensions, `S=-4 tau_i`.  Therefore

\[
 S_{\mu\nu}-\frac13S h_{\mu\nu}
 =\left(-1+\frac43\right)\tau_i h_{\mu\nu}
 =\frac13\tau_i h_{\mu\nu},
\]

and, with `kappa_5=1`,

\[
 K^{\rm out}_{\mu\nu}=+\frac{\tau_i}{6}h_{\mu\nu},
 \qquad n_{\rm out}\!\cdot\!\nabla\Phi=-\frac12\tau_{i,\Phi}.
\]

This recovers both the factor `1/6` and the half-Robin factor `1/2`; neither is
inserted independently into the reduction.

## 2. Conversion to the lemma's inward normals

The formal reduction uses inward normals.  Since
`n_in=-n_out`, extrinsic curvature and normal scalar derivative both reverse:

\[
 K^{\rm in}_{\mu\nu}=-\frac{\tau_i}{6}h_{\mu\nu},
 \qquad n_{\rm in}\!\cdot\!\nabla\Phi=+\frac12\tau_{i,\Phi}.
\]

Let proper distance increase from the lower wall `a` at `s=0` to the upper wall
`b` at `s=D`.  Then

\[
 n_a^{\rm in}=+\partial_s,\qquad n_b^{\rm in}=-\partial_s.
\]

For `ds^2=e^{2A(s)} gamma_k+ds^2`, with `H=A_s` and `S=Phi_s`, this gives:

| wall | geometric inward derivatives | inward junction equation | reduced condition |
|---|---|---|---|
| lower `a` | `K_in=+H h`, `n_in Phi=+S` | `K_in=-tau_a h/6`, `n_in Phi=tau_a,Phi/2` | `H=-tau_a/6`, `S=+tau_a,Phi/2` |
| upper `b` | `K_in=-H h`, `n_in Phi=-S` | `K_in=-tau_b h/6`, `n_in Phi=tau_b,Phi/2` | `H=+tau_b/6`, `S=-tau_b,Phi/2` |

These are exactly equations (3) in `FORMAL_REDUCTION_LEMMA.md`.

## 3. Lower launch map

For

\[
 \tau_a(\Phi)=\lambda_a+\frac\gamma2(\Phi-v_0)^2,
 \qquad \tau_{a,\Phi}=\gamma(\Phi-v_0),
\]

and launch value `a=Phi(0)`, the table gives

\[
 H(0)=-\frac{\lambda_a+\gamma(a-v_0)^2/2}{6},
 \qquad S(0)=\frac\gamma2(a-v_0).
\]

Lines 171--184 of the independent replay implement these formulas literally.
Substitution into the first integral gives the replay's launch curvature

\[
 k=H(0)^2-1-\frac{S(0)^2}{12}+\frac{m^2a^2}{12}.
\]

There is no lower-wall sign mismatch.

## 4. Upper residuals and first-event definition

At the upper wall, the two reduced conditions are equivalent to

\[
 G=H-\frac{\tau_b}{6}=0,
 \qquad
 h=S+\frac\gamma2(\Phi-v_1)=0.
\]

Lines 262--268 of the independent replay use precisely these definitions.
The first event is a zero of `G`; the scalar shooting equation evaluates `h`
at that event.  Consequently the sealed D1 event and shooting root have the
same orientation as the displayed action.  Reversing either normal without
also reversing its geometric extrinsic curvature would change these residuals
and is not the implemented problem.

## 5. Wall identity cross-check

Squaring the junction values in the first integral removes the lower/upper
orientation while retaining the normalization:

\[
 ke^{-2A_i}=\frac{\tau_i^2}{36}-1
 -\frac{\tau_{i,\Phi}^2}{48}+\frac{m^2\Phi_i^2}{12}.
\]

The coefficients `1/36` and `1/48` independently test the Israel and scalar
half-Robin factors.  The dependency-free exact checker reproduces this identity.
The sealed replay encloses zero in the lower identity within
`+/-5.96911010203316e-11` and in the upper identity within
`[-5.906509158863721e-6,5.3012677201549174e-6]`.

## Decision

**PASS: the action, outward-normal source convention, inward-normal reduction,
lower launch map, upper residuals, and independent replay are mutually
consistent.**  The audit resolves the remaining convention caveat in the
formal lemma for this fixed doubled-cover convention.

This is a convention audit, not a new existence certificate.  It does not
extend the theorem beyond the reduced static family and does not establish
stability, a Cauchy bridge, dynamical selection, collapse, an event horizon, or
a baby universe.
