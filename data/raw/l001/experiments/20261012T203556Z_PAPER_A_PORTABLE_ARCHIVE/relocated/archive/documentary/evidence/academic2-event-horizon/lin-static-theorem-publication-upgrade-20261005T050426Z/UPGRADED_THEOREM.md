# Upgraded standalone static theorem

## Fixed problem

Consider the source-pinned five-dimensional Einstein--scalar two-wall model,
the maximally symmetric warped ansatz, the doubled-cover junction conventions,
and the exact binary64 parameter literals already stated in the sealed theorem
packet. Let `a=Phi(0)` be the lower-wall launch value. Let `D(a)` be the first
transverse zero of the upper Israel residual `G`, and let
`q(a)=h(D(a),a)` be the remaining upper scalar-wall residual. For a prescribed
proper separation `D`, let `F(a,D)=(G(D,a),h(D,a))`.

## Theorem

Within the declared positive-curvature launch class `0 <= a <= v0`:

1. **Global first-event uniqueness.** There is exactly one simultaneous-wall
   solution on the first-event branch. Its launch value lies in the certified
   D1 root interval

   `0.09901086489880687 <= a <= 0.09901086689880687`,

   and the original producer encloses its proper separation by

   `1.99749755859375 <= D* <= 1.99761962890625`.

   A gap-free dual-producer cover of the complete launch interval has 726
   terminal boxes: one certified root box, 19 negative-curvature exclusions,
   and 706 first-event scalar-residual exclusions. There are no unresolved
   boxes.

2. **Independent existence and geometry.** A producer-independent fifth-order
   Taylor--Picard/interval-Newton implementation gives a strict self-map for
   the same shooting problem, with positive curvature

   `0.000326841301145298 <= k <= 0.0003268413757636101`,

   a transverse first event, nonzero shooting derivative, positive warp,
   finite conformal length, and full-domain enclosures of the first integral
   and both wall identities.

3. **Isolation in the two-equation problem.** The simultaneous zero
   `(a*,D*)` is locally isolated as a zero of `F`. The primary Jacobian
   determinant enclosure is

   `[2221.879246216278, 2224.53955879436]`,

   and the independent enclosure is

   `[2220.8647309726075, 2225.5545418744878]`.

   Both exclude zero. Therefore the finite width of the displayed `D*`
   enclosure is numerical uncertainty around one separation, not a continuous
   fixed-model solution branch.

4. **Fixed-separation exclusion.** At the exact prescribed separation

   `D0 = 0.9996389747145851`,

   no positive-curvature launch in `0 <= a <= v0` satisfies both upper-wall
   equations. The exact 693-box D2A cover has no gaps and no unresolved boxes;
   on every box not already excluded by negative launch curvature,

   `max(|G(D0,a)|, |h(D0,a)|) > 0.0077`.

## Corollary

For this fixed reduced model, the compatible positive-curvature static
configuration is a unique isolated first-event solution near `D*=1.9975`,
whereas the original proper separation `D0` is excluded. The nearly
factor-of-two separation mismatch is therefore a property of the declared
static boundary-value problem, not a missed launch, root-locator tolerance, or
unresolved continuation in `D`.

## What the theorem does not say

This theorem is restricted to the declared static ansatz, exact parameter
literals, wall conventions, launch interval, positive-curvature class, and
first-event definition. It does not establish parameter robustness, spectral
or nonlinear stability, a dynamical radion transition, selection by collapse,
P16 compatibility, a MOTS, an event horizon, or a child universe.

The later generalized-harmonic calculation is supporting numerical evidence
only: it shows clean finite-resolution convergence of the unchanged raw GH
background acceleration and one bounded short scalar response through
`t=0.001`. It is not part of the theorem and is not a stability certificate.
