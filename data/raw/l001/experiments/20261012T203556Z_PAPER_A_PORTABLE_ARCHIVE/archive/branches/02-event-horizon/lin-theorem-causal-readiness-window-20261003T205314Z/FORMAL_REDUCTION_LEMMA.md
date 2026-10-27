# Formal reduction from the doubled-cover action to the certified shooting problems

## Status

This is a manuscript-form reduction lemma for the fixed action and junction
conventions. It closes the logical map from the five-dimensional static ansatz
to the two certified one-dimensional problems. It does not derive a Cauchy
embedding or a dynamical-selection result.

The displayed algebraic identities were replayed exactly over rational
Laurent polynomials by `reduction_identity_check.py` (SHA-256
`acc29f01d26777417a719b566e8a3a9188a38bc2f99540c9e55f879e5b7eaba9`).
The checker has no third-party dependencies and covers constraint propagation,
both reduced Einstein equations, the conformal first integral, and the wall
identity.  It does not replace the separate junction-orientation audit.

The source conventions are bound to `MODEL_V1.md` (SHA-256
`4077686eb06ea8eea23d11b059336db877d8466f34b710f0fa416e116d343dc9`)
and `PROSPECTIVE_BVP_DESIGN.md` (SHA-256
`5f73207bbab64947e5bf30de285c3bee7b221c5d97214f08d46ec1857208c55a`).

## Lemma (static two-wall reduction)

Set `ell=kappa_5=1`, `Lambda_5=-6`, and set the independent collapse scalar
`chi` identically to zero. On the doubled `S1/Z2` cover consider

\[
 S=\frac12\int_{\widetilde{\mathcal M}}\!\sqrt{-g}\,(R-2\Lambda_5)
 -\frac12\int_{\widetilde{\mathcal M}}\!\sqrt{-g}
 \bigl((\nabla\Phi)^2+m^2\Phi^2\bigr)
 -\sum_{i=a,b}\int_{\Sigma_i}\!\sqrt{-h_i}\,\tau_i(\Phi),
\]

with

\[
 \tau_i(\Phi)=\lambda_i+\frac{\gamma}{2}(\Phi-v_i)^2.
\]

Assume the warped maximally symmetric ansatz

\[
 ds_5^2=e^{2A(s)}\gamma_{k,\mu\nu}dx^\mu dx^\nu+ds^2,
 \qquad \operatorname{Ric}(\gamma_k)=3k\gamma_k,
 \qquad \Phi=\Phi(s),
\]

where `s` increases from the lower wall to the upper wall. Define
`H=A_s` and `S=Phi_s`. With inward normals `n_a=+partial_s` and
`n_b=-partial_s`, the doubled-cover junction convention reduces the static
problem to

\[
 A_s=H,\qquad
 H_s=-\frac{S^2}{3}-ke^{-2A},\qquad
 \Phi_s=S,\qquad
 S_s=m^2\Phi-4HS,                                      \tag{1}
\]

together with the first integral

\[
 \mathcal C=H^2-1-\frac{S^2}{12}+\frac{m^2\Phi^2}{12}
              -ke^{-2A}=0.                              \tag{2}
\]

The one-sided wall conditions are

\[
 \begin{array}{lll}
 s=0: & H=-\tau_a(\Phi)/6,
      & S=+\tau_{a,\Phi}(\Phi)/2,\\[2mm]
 s=D: & H=+\tau_b(\Phi)/6,
      & S=-\tau_{b,\Phi}(\Phi)/2.                       \tag{3}
 \end{array}
\]

After fixing `A(0)=0` and the lower scalar value `a=Phi(0)`, equations
(2)--(3) determine the launch data and curvature:

\[
 \begin{aligned}
 H(0;a)&=-\frac{\lambda_a+\gamma(a-v_0)^2/2}{6},\\
 S(0;a)&=\frac{\gamma}{2}(a-v_0),\\
 k(a)&=H(0;a)^2-1-\frac{S(0;a)^2}{12}+\frac{m^2a^2}{12}. \tag{4}
 \end{aligned}
\]

Define

\[
 \begin{aligned}
 G(s,a)&=H(s,a)-\frac{\lambda_b+\gamma(\Phi(s,a)-v_1)^2/2}{6},\\
 h(s,a)&=S(s,a)+\frac{\gamma}{2}(\Phi(s,a)-v_1).          \tag{5}
 \end{aligned}
\]

If `G(.,a)` has a first zero `D(a)` and `G_s(D(a),a) != 0`, then `D(a)` is
locally differentiable and the variable-separation boundary-value problem is
equivalent, in that neighborhood, to the scalar shooting equation

\[
 q(a)=h(D(a),a)=0.                                      \tag{6}
\]

At a prescribed proper separation `D_0`, the same action and wall conditions
instead require the simultaneous fixed-distance residual equation

\[
 R_{D_0}(a)=\bigl(G(D_0,a),h(D_0,a)\bigr)=(0,0).         \tag{7}
\]

Thus (6) and (7) are two boundary placements in the same reduced static
family: (6) lets the upper wall occur at the first transverse Israel event,
whereas (7) fixes the upper wall first and asks both residuals to vanish there.

## Proof

### 1. Bulk field equations

Variation of the bulk terms gives

\[
 G_{AB}+\Lambda_5g_{AB}
 =\partial_A\Phi\partial_B\Phi
 -\frac12g_{AB}\bigl((\nabla\Phi)^2+m^2\Phi^2\bigr),
 \qquad \Box_g\Phi-m^2\Phi=0.                           \tag{8}
\]

For the warped ansatz,

\[
 R_{ss}=-4(A_{ss}+A_s^2),\qquad
 R_{\mu\nu}=\bigl(3ke^{-2A}-A_{ss}-4A_s^2\bigr)g_{\mu\nu},
\]

and

\[
 R=12ke^{-2A}-8A_{ss}-20A_s^2.                          \tag{9}
\]

The `ss` Einstein equation is exactly (2). The tangential Einstein equation,
combined with (2), gives the second equation in (1); the scalar equation gives
the fourth. The first and third equations are definitions.

Differentiating (2) and substituting (1) gives

\[
 \begin{aligned}
 \mathcal C_s
 &=2H\left(-\frac{S^2}{3}-ke^{-2A}\right)
 -\frac{S}{6}(m^2\Phi-4HS)+\frac{m^2\Phi S}{6}
 +2kHe^{-2A}=0.                                         \tag{10}
 \end{aligned}
\]

Hence imposing the remaining Einstein equation on one slice of the IVP
propagates it throughout every regular solution interval.

### 2. Junction factors and orientations

In the bound doubled-cover convention, the `Z2` jump supplies the factor of
two between a jump equation and a one-sided inward-normal derivative. For a
pure scalar-dependent wall potential, the one-sided equations are

\[
 K_{\mu\nu}^{(i)}=-\frac{\tau_i}{6}h_{\mu\nu},\qquad
 n_i\!\cdot\!\nabla\Phi=\frac12\tau_{i,\Phi}.            \tag{11}
\]

At the lower wall, `K_{mu nu}=H h_{mu nu}` and
`n_a dot grad Phi=S`. At the upper wall the inward normal reverses both
relations: `K_{mu nu}=-H h_{mu nu}` and
`n_b dot grad Phi=-S`. Equation (11) therefore gives (3), including the
opposite upper-wall signs. Substitution at `s=0` yields (4).

At either wall, substituting (3) in (2) gives the independent wall identity

\[
 ke^{-2A_i}=\frac{\tau_i^2}{36}-1
 -\frac{\tau_{i,\Phi}^2}{48}+\frac{m^2\Phi_i^2}{12}.    \tag{12}
\]

This is the identity independently enclosed by the D1 replay.

### 3. First-event map and total shooting derivative

The right-hand side of (1) and launch map (4) are smooth wherever the
solution remains finite. Let `Y=(A,H,Phi,S)` and `W=partial_a Y`. Because
`k=k(a)`, the sensitivity satisfies

\[
 W_s=D_Yf(Y,k)W+f_k(Y,k)k'(a),                           \tag{13}
\]

with

\[
 W(0)=\left(0,-\frac{\gamma(a-v_0)}6,1,\frac\gamma2\right). \tag{14}
\]

At a transverse event the implicit-function theorem gives

\[
 D'(a)=-\frac{G_a}{G_s},\qquad
 q'(a)=h_a+h_sD'(a),                                    \tag{15}
\]

where all derivatives on the right are evaluated at `(D(a),a)`. Explicitly,

\[
 \begin{aligned}
 G_s&=H_s-\frac{\gamma}{6}(\Phi-v_1)S,&
 G_a&=H_a-\frac{\gamma}{6}(\Phi-v_1)\Phi_a,\\
 h_s&=S_s+\frac{\gamma}{2}S,&
 h_a&=S_a+\frac{\gamma}{2}\Phi_a.                       \tag{16}
 \end{aligned}
\]

These are the sensitivity and first-event formulas used by both D1
certificates.

### 4. Validated existence and exclusion propositions

Let `I` be the frozen narrow launch interval. If a validated flow encloses the
first transverse event for every `a in I`, encloses `q'(I)` away from zero,
and an interval-Newton image `N(I)` obeys

\[
 N(I)\subset\operatorname{int}I,                        \tag{17}
\]

then `q` has exactly one zero in `I`. The original D1 producer and the later
independent Taylor--Picard replay each satisfy (17) with separately generated
enclosures.

For the fixed-distance problem, let `{I_j}` be an exact contiguous cover of
`[0,v_0]`. If every box satisfies at least one of

\[
 \sup k(I_j)<0,\qquad 0\notin G(D_0,I_j),\qquad
 0\notin h(D_0,I_j),                                    \tag{18}
\]

then no launch with positive curvature can satisfy (7). D2A supplies 693
terminal boxes, no unresolved boxes, and verifies (18) on every box. This
proves the fixed-separation exclusion on the declared launch domain.

## Coordinate equivalence used by the certificates

With `psi=e^A` and conformal coordinate `z` defined by `ds=psi dz`,

\[
 H=\frac{\psi'}{\psi^2},\qquad S=\frac{\Phi'}{\psi}.
\]

Multiplying (2) by `psi^4` yields

\[
 F=\psi'^2-\psi^4-\frac{\psi^2\Phi'^2}{12}
 +\frac{m^2\psi^4\Phi^2}{12}-k\psi^2=0,                \tag{19}
\]

which is the independently checked conformal-coordinate first integral. The
proper separation is `D=int psi dz`; the conformal separation is
`Z=int exp(-A) ds`. These are distinct certified quantities.

## What is and is not now manuscript-ready

Equations (1)--(19) supply the theorem-level reduction previously missing
from the consolidation packet. `JUNCTION_CONVENTION_AUDIT.md` independently
tracks the doubled-cover outward-normal equations through the inward-normal
proper-distance reduction and returns `PASS`; it also matches the lower launch
map and upper residuals used by the sealed independent replay. Before direct
insertion, the notation should be made identical to the final article. The
computer-assisted implications are already bound by the exact authority table.

Nothing in this lemma maps the static solution into the collapse evolution.
In a flat de Sitter slicing the induced Cauchy data have nonzero transverse
extrinsic curvature, so the D1 geometry cannot be inserted as momentarily
time-symmetric data without changing the problem. That separate bridge remains
open.
