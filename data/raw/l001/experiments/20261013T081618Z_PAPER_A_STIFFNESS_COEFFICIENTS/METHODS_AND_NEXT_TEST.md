# Local wall stiffness coefficients and their interpretation

The accepted analytic result is a strictly positive local response of the physical scalar eigenvalue to either wall Hessian when the exact background is preserved. The coefficients

\[
C_i=\frac{a_i^4 f_i^2}{Z}>0,\qquad i=a,b,
\]

measure that response. Their ratio and their shares of a common stiffness change do not require the kinetic integral. Absolute coefficients require either a valid norm enclosure or an independently validated spectral-determinant derivative. These are complementary representations of the same quantity, not independent physical effects.

The [previous independent proof review](../20261013T073517Z_PAPER_A_CURVATURE_RESPONSE/FINITE_STIFFNESS_PROOF_REVIEW.md) accepts the regular Green identity, local determinant simplicity and the derivative formula. It binds the original derivation to SHA-256 `65ef9f00383030742704c301f77495bc7823e2ef837853205d0fcb363b8bdec5`. The central negative-mode certificate remains unchanged. The additional relationships below are supplied for independent analytic review in this packet; their acceptance is to be recorded by that review, separately from the coefficient computation. No scientific code, numerical integration, parameter scan or Linux execution was performed for this note.

## Fixed action deformation and canonical meaning

The deformation is explicitly

\[
\tau_i^{(\eta_i)}(\Phi)=\tau_i(\Phi)
+\frac{\eta_i}{2}(\Phi-\Phi_i^*)^2,
\]

where \(\Phi_i^*\) is the value of the exact central background at the wall. Its value and first derivative vanish on that background. It changes the wall Hessian but leaves the bulk background, wall locations, curvature, warp factors and background junction conditions fixed. The local simple mode branch then obeys

\[
d\mu=C_a\,d\eta_a+C_b\,d\eta_b.
\]

For \(Q_c=\sqrt Z\,Q\), the added pure wall potential contributes

\[
\delta I^{(2)}_i=-\frac12\eta_i C_i
\int d^4x\sqrt{-\gamma_k}\,Q_c^2.
\]

Indeed, the added potential starts at quadratic order as \(\eta_i f_i^2Q^2/2\), so perturbations of the induced volume element first contribute at cubic order. This observation applies to the retained generic straight-wall scalar sector. It gives the interpretation

\[
C_i=\left(\frac{a_i^2f_i}{\sqrt Z}\right)^2:
\]

the coefficient is a squared boundary scalar overlap, weighted by the wall volume factor. It is not a probability, a bulk energy density, or a claim that the instability is localized at that wall. The regular kinetic norm is unchanged as a functional; its value on the varying eigenmode can vary along the branch.

## Ratios and response shares without the norm

An arbitrary common real rescaling \((\psi,f,p)\mapsto c(\psi,f,p)\) sends \(Z\mapsto c^2Z\), leaving each \(C_i\) invariant. In particular,

\[
\rho:=\frac{C_b}{C_a}
=\left(\frac{a_b}{a_a}\right)^4\left(\frac{f_b}{f_a}\right)^2,
\qquad
w_i:=\frac{C_i}{C_a+C_b}
=\frac{a_i^4f_i^2}{a_a^4f_a^2+a_b^4f_b^2}.
\]

Both wall amplitudes are nonzero by the accepted \(\lambda=\mu+4k\ne0\) argument, so \(\rho>0\), \(0<w_i<1\), and \(w_a+w_b=1\). The shares describe the two contributions to the local response under \(\eta_a=\eta_b\); they do not partition the mode's bulk energy. When absolute coefficient bounds are broad because the norm is poorly enclosed, this ratio can still supply a useful comparison. No numerical wall ranking is asserted without a corresponding enclosure.

## Coordinate conversion and an endpoint-constraint ratio

Use conformal warp \(a(z)\), not the shooting parameter sometimes also called \(a\) in other packets. Set

\[
ds=a\,dz,\quad a=e^W,\quad
A=a'/a,\quad S=\Phi',\quad
H=W_s,\quad T=\Phi_s,
\]

with prime denoting conformal differentiation. The profile \(f\) and metric amplitude \(\psi\) are unchanged by this background-coordinate conversion, while \(p=f'=a f_s\), \(A=aH\), and \(S=aT\). Hence

\[
Z=2\int a^3(f^2+6\psi^2)dz
=2\int e^{2W}(f^2+6\psi^2)ds,
\qquad C_i=\frac{e^{4W_i}f_i^2}{Z}.
\]

For inward signs \(\sigma_a=+1\), \(\sigma_b=-1\), define

\[
\beta_i=\frac{\sigma_i\gamma_iT_i}{2}-(T_s)_i,
\qquad B_i=\frac{\sigma_i a_i\gamma_iS_i}{2}-S'_i+A_iS_i.
\]

The coordinate conversion gives \(B_i=a_i^2\beta_i\). At an exact eigenmode, the wall constraint becomes

\[
\beta_i f_i=3\lambda a_i^{-2}\psi_i.
\]

Consequently, when the displayed denominators are nonzero,

\[
C_i=\frac{9\lambda^2\psi_i^2}{\beta_i^2 Z},
\qquad
\rho=\left(\frac{\psi_b\beta_a}{\psi_a\beta_b}\right)^2.
\]

The accepted central profile has \(\psi>0\), \(\lambda<0\) and finite amplitudes, which exclude \(\beta_i=0\) at either wall of the exact eigenmode. An interval enclosure that contains zero still cannot be divided; it must be sharpened or replaced by the undivided representation. The common shifted eigenvalue cancels from the ratio, which can reduce avoidable interval dependence. A tighter ratio is not guaranteed without comparing the actual enclosures.

This constraint rearrangement holds at the spectral root, where both walls satisfy their Robin conditions. An off-root IVP profile in the full mass strip need not satisfy it at the upper wall. It is legitimate to enclose the root-conditioned expression using sets known to contain that exact root and its endpoint values; it is not legitimate to treat every off-root strip profile as an eigenmode. Endpoint data must cover the exact upper-wall event, rather than merely a nearby final grid state.

## Common stiffness and physical growth

If both Hessians receive the same background-preserving increment \(\eta\), then

\[
\frac{d\mu}{d\eta}=C_a+C_b>0.
\]

This is not the derivative obtained by changing the original common \(\gamma\) while holding the original wall tensions and targets fixed. To express the permitted deformation within a quadratic-wall parameterization, write \(u_i=\tau_i(\Phi_i^*)\), \(t_i=\tau'_i(\Phi_i^*)\), and

\[
\tau_i(\Phi)=\Lambda_i+\frac\gamma2(\Phi-v_i)^2.
\]

For sufficiently small \(\eta\), the exact reparameterization preserving both background wall jets is

\[
v_i(\eta)=\Phi_i^*-\frac{t_i}{\gamma+\eta},\qquad
\Lambda_i(\eta)=u_i-\frac{t_i^2}{2(\gamma+\eta)}.
\]

Expanding this quadratic about \(\Phi_i^*\) gives the original value \(u_i\), original first derivative \(t_i\), and Hessian \(\gamma+\eta\), exactly as required. It is an explicitly changed action, not an unreported adjustment of the original six fixed parameters.

For the accepted expanding de Sitter linear mode,

\[
r_+=\frac{-3\sqrt k+\sqrt{9k-4\mu}}2,
\qquad
\frac{\partial r_+}{\partial\eta_i}
=-\frac{C_i}{\sqrt{9k-4\mu}}<0.
\]

Thus raising either background-preserving wall Hessian locally reduces the growing exponent. It does not prove that any finite stiffness change eliminates growth. At wall \(j\), proper-time mass and exponent are \(\mu_j=\mu/a_j^2\) and \(r_{+,j}=r_+/a_j\). Since this deformation fixes the warp factors,

\[
\partial_{\eta_i}\mu_j=C_i/a_j^2,
\qquad
\partial_{\eta_i}r_{+,j}
=-C_i/[a_j\sqrt{9k-4\mu}].
\]

The coefficient ratio and response shares are therefore independent of which fixed wall clock is used to compare the two perturbations.

## Direct norm bounds and determinant sensitivity

The accepted simplicity identity is written with the literal conformal upper residual

\[
R(\mu)=p_b+2S_b\psi_b+\frac{a_b\gamma_b}{2}f_b,
\qquad R_\mu(\mu_*)=-\frac{Z_*}{2a_b^3f_b}.
\]

For the literal proper residual \(F=R/a_b=f_s+2T\psi+\gamma_b f/2\), on the same fixed background and lower normalization,

\[
F_\mu(\mu_*)=-\frac{Z_*}{2a_b^4f_b},\qquad
C_b=-\frac{f_b}{2F_\mu},\qquad
C_a=-\frac{a_a^4f_a^2}{2a_b^4f_bF_\mu}.
\]

Equivalently, implicit differentiation gives \(C_i=-F_{\eta_i}/F_\mu\). For the upper-wall deformation the lower IVP is unchanged and \(F_{\eta_b}=f_b/2\). The lower-wall deformation changes the launch data, so its determinant derivative must include that dependence. It cannot be obtained by adding only an explicit upper-wall term.

The ratio \(-F_{\eta_i}/F_\mu\) is invariant if the entire determinant is multiplied by a smooth nonzero normalization, with both derivatives transformed consistently at the root. The shortcut using \(f_b/2\) is valid for the literal residual above; using a rescaled determinant derivative with an unscaled numerator changes the answer. Determinant endpoint signs or their secant do not enclose the derivative at the exact spectral root. The accepted identity proves its nonvanishing, not a numerical value.

If no accumulated norm integral is available, the first fallback is the inherited validated strip extrema. For proper length bounds \(D_-\le D\le D_+\), \(W_-\le W\le W_+\), \(\psi\ge\psi_->0\), and global absolute bounds \(|f|\le F_+\), \(|\psi|\le P_+\),

\[
12D_-e^{2W_-}\psi_-^2\le Z
\le2D_+e^{2W_+}(F_+^2+6P_+^2).
\]

Use outward bounds and the full exact-background/mass/event coverage; numerical best-fit values of \(Z\) cannot replace them. If \(N_i=a_i^4f_i^2\) has a positive enclosure \([N_{i,-},N_{i,+}]\) and \(0<Z_-\le Z\le Z_+\), then

\[
\frac{N_{i,-}}{Z_+}\le C_i\le\frac{N_{i,+}}{Z_-}.
\]

These can be rigorous but broad. If the available numerator enclosure reaches zero, preserve the accepted qualitative strict positivity while reporting that the new quantitative lower enclosure does not resolve it. Do not clip the interval away from zero.

The second fallback is the norm-free ratio or response shares. A validated determinant-sensitivity IVP is a later alternative only if the simpler saved-data bounds cannot answer the quantitative question: it adds a differentiated mode system and a root-dependent derivative enclosure, whereas direct norm accumulation adds one positive integral. Neither route is automatically superior in width or implementation cost, and both need the same exact-background and wall-event coverage.

## Next bounded discriminator

The current packet should first report whether its saved-data coefficient and ratio bounds resolve a quantitative wall comparison. If it succeeds, no further calculation is required to establish the local sign. If absolute widths remain uninformative, retain those bounds and the independently useful ratio before proposing a successor.

For a separately authorized tightening test, prefer direct validated accumulation of \(Z\) alongside the unchanged regular mode system, with a prescribed root bracket and unchanged background/event enclosures. Its purpose would be a stated coefficient-width target, not a search for stabilizing parameters. A determinant-sensitivity calculation is a useful independent cross-check only after its launch derivatives, literal normalization and exact-root coverage are frozen. An implementation estimate cannot be converted into a runtime estimate without that design.

No local derivative or response ratio gives a finite stabilizing threshold, a global monotonicity theorem, a count of spectral modes, a causal outcome, or permission to change the paper's static theorem.
