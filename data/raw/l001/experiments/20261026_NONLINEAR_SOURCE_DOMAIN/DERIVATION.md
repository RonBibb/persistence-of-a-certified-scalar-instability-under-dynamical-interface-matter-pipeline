# Conditional analytic domain for nonlinear sources

For a finite truncation or a convergent nonnegative coefficient envelope, assume
\(\eta=Y(16|z|)\le10^{-5}\). The following bounds provide a domain for assembling nonlinear source estimates. They do not establish this assumption at any numerical charge amplitude.

## Composition reserve

The authenticated background is holomorphic on the radial collar of radius \(R=1/20000\). Start on its inner half. For the affine interface graph displacement \(X\), the endpoint contributions in \(Y\) give
\[
 |X|\le C_X\eta,\qquad C_X=1+\frac{R}{2D_{\min}},\qquad
 |X_r|\le\frac{\eta}{D_{\min}}.
\]
The exact check gives \(C_X\eta<R/4\). Shifted arguments therefore remain within the collar of radius \(3R/4\). The original normalized distance to the outer edge is at least \(1/4\) there. For the inherited weighted norms this gives perturbation value, first radial derivative, and second radial derivative bounds \(\eta,4\eta,16\eta\). The dilation by 16 is necessary for these uniform shifted-domain bounds; dilation by 4 alone only controls the inner half.

For each background function separately, let \(M\) be its verified supremum on the surrounding background collar. Cauchy's estimate at a starting point on the inner half gives Taylor coefficient bound \(M(2/R)^j\). With \(q=2C_X\eta/R<1/2\), the composition tail after order \(m\) is bounded by \(Mq^{m+1}/(1-q)\). A bound on the background ODE vector field must not be substituted for this function-specific \(M\).

## Physical wall factors

At the physical real walls, endpoint displacements obey \(|S_t|\le6h\eta\) and \(|S_{tt}|\le36k\eta\), with the verified \(h<1/50\). General affine graph time derivatives additionally require \(C_X\). Since \(E\le8+10^{-3}\), \(|p|,|b|\le\eta\), and \(e^{2\eta}<2\), the physical wall speed satisfies
\[
 |v|\le2(8+10^{-3})(6/50)\eta<1/4.
\]
Consequently \(|1-v^2|\ge15/16\); also \(|1+X_r|\ge1-\eta/D_{\min}>3/4\).

For the selected affine wall coupling \(c_i(\Phi)=1-(\Phi-\Phi_i^*)/1000\), the background derivative bound \(\bar T\) gives
\[
 |c_i-1|\le(\bar T+1)\eta/1000<1/2.
\]
This estimate uses the selected coupling and neutral wall reference; it is not a generic wall-action result.

## Source assembly still required

The elementary absolute Taylor coefficient bounds are \(|c|^j\) for \(e^{cu}\), 1 for \((1-u)^{-1}\), and at most 1 for \((1-u)^{-1/2}\). Together with the composition reserve, these are inputs to a term-by-term budget of the actual compatible bulk and wall equations. The complete nonlinear majorant constants \(K,M\), its closure, and a numerical charge-amplitude radius remain to be established.

The producer uses exact rational arithmetic for these sufficient domain inequalities, with separately authenticated primary and independent background bounds. Its terminal files record source and input hashes. The independent replay, when published, checks arithmetic separately from this conditional analytic argument.
