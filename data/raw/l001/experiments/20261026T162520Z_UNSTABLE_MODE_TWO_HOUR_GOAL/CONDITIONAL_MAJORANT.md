# Conditional neutral majorant: an explicit target for the remaining bridge

This is an analytic planning lemma, not a certificate that the research fields satisfy its hypotheses. In particular, no numerical amplitude radius for the Einstein–scalar solution is asserted. It states what the next source/inverse estimate would buy if established.

## Neutral harmonic denominators

For the authenticated branch `r>h>0` and integers `n>=2`, put `lambda=n*r` and `mu=-lambda*(lambda+3*h)`. Pointwise on the real interval:

\[
\lambda(\lambda-h)\ge \tfrac12 n^2r^2,
\qquad 2+\lambda(\lambda+3h)E^2\ge n^2r^2E_{\min}^2,
\]

\[
J=3[-\mu-4h^2]E^2\ge3n^2r^2E_{\min}^2,
\qquad D=2T^2+J\ge J.
\]

The first follows from `h/(n*r)<1/n<=1/2`. For the third, `3*n*r*h-4*h*h>=(3*n-4)*h*h>0`. Thus the trace, graph, oscillator and algebraic metric denominators retain their quadratic harmonic scaling in the neutral sector. These inequalities are real-axis statements; complex positivity has not been inferred.

The source-counting strategy may therefore retain the same harmonic powers as the charged calculation, but its constants and analytic inverse still require their own proof. The neutral seed is order one and prescribed. There is no charge-forcing term.

## A sufficient scalar lemma

Suppose nonnegative coefficient norms `Y_n` obey `Y_1<=s`, with `s>0`, and for every `n>=2`,

\[
Y_n\le K[z^n]\frac{Y_{<n}(z)^2}{(1-KY_{<n}(z))^M},
\qquad Y_{<n}(z)=\sum_{j<n}Y_jz^j,
\]

where `K>=1` and `M` is a fixed nonnegative integer. This hypothesis must be proved for the actual nonlinear sources and a compatible inverse in one specified analytic norm. It is not supplied by the existing real-axis constants alone.

Define

\[
R=\frac{1}{2^{M+3}K(M+1)},\qquad
\rho=\frac{R}{2s}.
\]

Then the scalar equation

\[
W=sz+\frac{KW^2}{(1-KW)^M}
\]

has a unique analytic fixed point in the disk `|W|<=R`, uniformly for `|z|<=rho`. Its nonnegative Taylor coefficients dominate the `Y_n` coefficientwise.

**Proof.** Set `a=K*R=1/[2^(M+3)*(M+1)]<=1/8`. On the disk, the nonlinear term is at most `K*R^2*2^M=R/[8*(M+1)]`. Together with `s*|z|<=R/2`, the map sends the disk strictly into itself. Its derivative is bounded by

\[
2a2^M+Ma^2 2^{M+1}
=\frac{1}{4(M+1)}+
\frac{M}{2^{M+5}(M+1)^2}<\frac12.
\]

Uniform contraction gives the analytic fixed point, for example by uniformly convergent analytic iteration from zero. Coefficients are nonnegative; induction in the triangular recurrence gives coefficientwise domination. The case `M=0` is included. This is a sufficient, deliberately conservative radius, not an optimal one.

For `|z|<=q*rho`, `0<=q<1`, Cauchy's estimate gives a norm-tail bound beyond cubic order,

\[
\sum_{n\ge4}Y_n|z|^n\le\frac{R q^4}{1-q}.
\]

## What this does and does not certify for proper separation

The tail above is for the hypothesized coefficient norm. It is not automatically the tail of the proper-separation observable. Moving endpoints, exponentiation of the metric and integration need a compatible analytic observable bound; a Lipschitz bound for the full field map does not by itself identify the Taylor truncation of that observable. The successor must either majorize the observable's coefficients directly or certify a uniform bound for the full analytic observable on the amplitude disk and apply Cauchy to those coefficients.

If Nagumo weights are used, restrict to an inner collar with `d>=d_min>0` and explicitly pay the coefficient factor `d_min^(-2n)`, hence reduce the amplitude radius to `rho*d_min^2`, including any fixed derivative factors. The scalar lemma's `rho` is not a physical amplitude radius until that translation and the observable bound are completed.

Consequently, this lemma narrows the missing work to authenticated `s,K,M`, a common analytic inverse/source estimate, and the observable-tail conversion. It does not establish those inputs, a saturation amplitude, finite-time contact or a nonlinear endpoint.
