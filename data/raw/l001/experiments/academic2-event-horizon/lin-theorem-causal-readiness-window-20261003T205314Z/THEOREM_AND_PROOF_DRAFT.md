# Manuscript-form theorem and proof draft

## Definitions

Fix the doubled-cover Einstein--AdS--scalar action, quadratic wall potentials,
units, maximally symmetric warped ansatz, and exact binary64 parameter literals
in `FORMAL_REDUCTION_LEMMA.md`.  Let `a=Phi(0)` be the lower-wall launch scalar.
The lower junction data and first integral define the proper-distance IVP and
its curvature `k(a)`.

Let

\[
G(s,a)=H(s,a)-\frac{\lambda_b+\gamma(\Phi(s,a)-v_1)^2/2}{6},
\qquad
h(s,a)=S(s,a)+\frac\gamma2(\Phi(s,a)-v_1).
\]

When `G(.,a)` has a first transverse zero, denote it by `D(a)` and set
`q(a)=h(D(a),a)`.  At fixed proper separation `D0`, set
`R_D0(a)=(G(D0,a),h(D0,a))`.

All decimals below denote their exact binary64 dyadic values when they are
inputs.  Reported interval endpoints are outward enclosures from the sealed
certificates; their exact rational forms are bound in
`THEOREM_INTERVALS_EXACT.json`.

## Theorem 1 — validated variable-separation solution

For

\[
I=[0.09901086489880687,0.09901086689880687],
\]

the reduced first-event shooting function `q` has exactly one zero in `I`.
The associated solution has positive curvature and a first upper-Israel event
whose proper separation satisfies

\[
D\in[1.99749755859375,1.99761962890625].
\]

An independent interval-ODE implementation encloses the same root and geometry;
at its fine level,

\[
\begin{aligned}
N(I)&\subset[0.09901086554679088,0.09901086629822892]
       \subset\operatorname{int}I,\\
D&\in[1.9974365234375,1.9976806640625],\\
k&\in[0.000326841301145298,0.0003268413757636101],\\
G_s&\in[-0.017911083024782542,-0.017896675281034263],\\
q'(I)&\subset[124093.76952925383,124255.72137561499].
\end{aligned}
\]

The warp is positive throughout the validated interval and the independently
enclosed conformal separation is finite and positive.

### Proof

The reduction lemma supplies a smooth parameter-dependent IVP and the total
sensitivity equations on every regular flow interval.  The original validated
producer uses 32,768 proper-distance steps at 768-bit Arb precision.  Its
interval-Newton image is

\[
\left[
\frac{456607025194779413}{4611686018427387904},
\frac{114151756532473697}{1152921504606846976}
\right]
\subset\operatorname{int}I.
\]

On the validated event enclosure, `G_s<0`; hence the implicit first-event map
is well-defined.  Its total shooting derivative is strictly positive,

\[
q'(I)\subset[124130.66976980511,124218.80928782765].
\]

The interval-Newton inclusion theorem gives existence and uniqueness of one
zero of `q` in `I`.  The same validated flow gives the narrower displayed event
interval.

The sealed independent replay imports neither the original producer nor its
enclosures.  It propagates the state and launch sensitivity by an autonomous
Taylor expansion with Picard remainder boxes at 8,192 and 16,384 steps.  At both
levels every cell has strict Picard self-containment, the first `G=0` cells are
contiguous, `G` has the required sign on either side, `G_s<0`, `q'` excludes
zero, and the interval-Newton image is a strict self-map.  At the fine level it
gives the second set of intervals stated above.

Both producers implement the same reduced IVP, launch map, first-event
definition, and shooting residual on the same frozen interval `I`. Since each
certificate proves that this common `q` has exactly one zero in `I`, their
enclosures necessarily refer to the same mathematical root; overlap of two
ordinary numerical estimates is not being used as the identification rule.

The replay also encloses a positive warp on the whole domain,

\[
e^A\in[0.13477779494132847,1.0000343344872817],
\]

and conformal separation

\[
Z\in[6.379214731752709,6.381247509927617].
\]

Every cell's first-integral enclosure contains zero, as do the independently
evaluated lower and upper wall identities and both upper-wall residuals on the
root/event box.  The exact algebra checker separately proves propagation of the
first integral and the proper-to-conformal coordinate identity.  The junction
audit matches both wall orientations and half-Robin factors to the doubled-cover
action.  Thus the independent replay certifies that the interval root belongs
to the declared regular warped geometry, completing the proof.  \(\square\)

## Theorem 2 — fixed-separation positive-curvature exclusion

Let

\[
D_0=\frac{2250986857014815}{2251799813685248}
   =0.9996389747145851
\]

and retain the action, wall parameters, launch map, orientations, and residuals
of Theorem 1.  There is no `a` in the exact interval

\[
0\le a\le
\frac{3602879701896397}{36028797018963968}
\]

for which `k(a)>0` and `R_D0(a)=(0,0)`.

Moreover, throughout every terminal interval not already excluded by negative
curvature,

\[
\max\{|G(D_0,a)|,|h(D_0,a)|\}>\frac{77}{10000}.
\]

### Proof

D2A constructs an exact adaptive interval cover of the entire launch domain.
The 693 terminal boxes meet without gaps or overlaps at exact rational
endpoints.  Twenty boxes have a strictly negative upper bound for `k` and are
therefore outside the theorem's positive-curvature class.  Of the remaining
boxes, 670 have both wall-residual intervals separated from zero, one is
excluded by `G` alone, and two are excluded by `h` alone.  There are no
unresolved boxes.

For every box not discharged by negative curvature, exact interval distance
from zero gives

\[
\max\{\operatorname{dist}(0,G),
       \operatorname{dist}(0,h)\}>77/10000.
\]

Thus no point in any positive-curvature box can make both components vanish.
The union of the boxes is the complete declared launch interval, proving the
claim.  The post-run verifier rederives the classifications, exact cover,
and residual floor from the stored terminal enclosures.  \(\square\)

## Corollary — certified separation mismatch

Within this fixed reduced static family, the positive-curvature solution of
Theorem 1 cannot be a positive-curvature static solution at `D0`.  The roughly
factor-of-two difference between the selected event separation and the
prescribed production separation is therefore not attributable to an ordinary
shooting tolerance or to a missed launch value in `0<=a<=v0`.

Using the narrower original event enclosure, the contrast is rigorously

\[
D-D_0\in[0.9978585838791649,0.9979806541916649],
\qquad
\frac{D}{D_0}\in[1.9982189661663317,1.9983410805652175].
\]

### Proof

Theorem 1 supplies a positive-curvature solution with the first event near
`D=1.9975`; Theorem 2 excludes every positive-curvature simultaneous wall root
at `D0=0.9996389747145851` over the complete declared launch interval.  Both
statements use the same fixed action, wall potentials, orientations, and launch
family.  The displayed difference and ratio follow by exact rational interval
arithmetic because `D0` is strictly positive.  \(\square\)

## Scope of the theorem

The uniqueness is confined to the frozen D1 root interval and reduced ansatz.
The exclusion is confined to the exact `D0`, positive curvature, and the exact
launch interval `0<=a<=v0`.  The theorem does not address altered potentials or
parameters, zero/negative-curvature fixed-distance solutions, non-maximally
symmetric geometries, spectral or nonlinear stability, dynamical selection,
radion evolution, collapse, trapped surfaces, event horizons, or baby
universes.

The lower tension is reconstructed from the bound unchanged source constructor
rather than independently archived in the earlier source record.  That
provenance is part of the theorem's fixed inputs and must remain explicit.
