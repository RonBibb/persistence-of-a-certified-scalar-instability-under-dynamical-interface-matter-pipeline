# Finite stiffness and the scalar turning point

The accepted central negative-mode certificate needs no repair on the evidence inspected here. Its finite Robin conditions, regular continuation across the scalar minimum, and positive kinetic norm were already derived from the declared action and independently reviewed. The useful next contribution is explanatory: explicitly reconcile the regular physical norm with the singular weighted Sturm–Liouville representation. The algebra below supplies a compact candidate identity for independent review. It does not classify the complete spectrum or identify which physical feature causes the negative mode.

This note is a read-only scientific investigation plus a prospective analytic derivation. No scientific code, new integration, parameter scan, Linux job, or manuscript change was performed.

## Existing authority and the remaining explanatory question

The [central result](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/RESULT_REPORT.md) and [independent proof audit](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/INDEPENDENT_PROOF_AUDIT.md) establish an admissible mode with

\[
-0.00132<\mu_*<-0.00131,\qquad \lambda_*:=\mu_*+4k<0,
\qquad Z>0,
\]

and nonzero physical wall-separation response. The full mass strip also has strictly positive \(\psi\). The action has canonical Einstein–scalar bulk terms, pure wall potentials, doubled-cover normalization, finite \(\gamma=20\), and no wall kinetic or induced Einstein terms.

The [independent formulation](../academic2-event-horizon/lin-curved-stability-2026-09-29/analysis/INDEPENDENT_FORMULATION.md), especially sections 2–5, and [kinetic review](../academic2-event-horizon/lin-curved-stability-2026-09-29/analysis/KINETIC_AND_CONTROL_REVIEW.md), sections 2–3, already resolve three issues:

- The constrained coupled equations cross the scalar-gradient zero without division, clipping, or an artificial internal boundary.
- Finite wall stiffness gives Robin conditions; replacing them by scalar Dirichlet conditions changes the problem.
- Direct action expansion gives a positive regular physical norm; pure potential walls supply no direct tangential kinetic term for the generic straight-wall sector.

The inspected internal notes do not display the cutoff identity below. That is a limited explanatory opening, not evidence of a missing physical term or failed certificate.

## What the primary sources support

[Frolov and Kofman, hep-th/0309002v1](https://arxiv.org/html/hep-th/0309002v1), sections II–IV, first retain the finite scalar Robin condition in equation 14, then adopt the stiff condition in equation 16. Their equations 17–19 use a positive weight proportional to \(1/(a\varphi'^2)\), Neumann endpoint conditions, and a regular self-adjoint Rayleigh argument. Transferring that nonnegative shifted-eigenvalue conclusion requires both the boundary conditions and the operator domain to match. Neither follows merely from similar bulk equations. Their finite-boundary discussion is not itself a proof of a universal nonnegative \(m^2+4H^2\).

[arXiv:2404.05141v2](https://arxiv.org/html/2404.05141v2), section 2.2 and Appendix A, restores orthogonality of a reduced finite-stiffness problem with explicit endpoint contributions to its scalar product. The reduction divides by the background scalar derivative. Appendix A constructs a reduced action reproducing that equation and its boundary conditions. Its flat superpotential background and stiffness normalization differ from the present curved model. The endpoint product therefore cannot be appended directly to the present regular action norm; an action-specific field transformation and its domain must first be established. Its coefficients are a methodological example, not imported physics.

[Olechowski, arXiv:2408.15343v2](https://arxiv.org/html/2408.15343v2), sections 2 and 4.2–4.3, explicitly treats Minkowski slices and explains why an interior scalar-gradient zero invalidates the naive positive-weight variational inference. It switches to a regular variable for the corresponding instability argument. This is useful corroboration of the domain issue, but its flat stability criterion does not prove the curved candidate's outcome or a curved turning-point theorem.

## Candidate action-specific reconciliation

Use the conformal-coordinate notation of the existing independent formulation:

\[
ds^2=a(z)^2(dz^2+\gamma_k),\quad A=a'/a,\quad S=\Phi',
\quad \lambda=\mu+4k,\quad Y=a^2\psi.
\]

These primes are conformal derivatives, not proper-distance derivatives. The regular equations and constraint give

\[
Y'=-\frac{a^2S}{3}f,\qquad
Sp+(AS-S')f+(2S^2-3\lambda)\psi=0,
\quad p=f'.
\]

On any closed interval where \(S\ne0\), define

\[
g=\frac{3}{2aS^2},\qquad q=\frac1a.
\]

The existing bulk equations imply

\[
-(gY')'+qY=\lambda gY.
\]

More usefully, the physical norm density has the exact identity

\[
g(Y')^2+qY^2=\frac{a^3}{6}(f^2+6\psi^2).
\]

Thus, for a union \(\Omega\) of nonsingular intervals, ordinary integration by parts gives

\[
\boxed{\frac{Z_\Omega}{12}
=\int_\Omega\{g(Y')^2+qY^2\}\,dz
=\lambda\int_\Omega gY^2\,dz+
\sum_{[l,r]\subset\Omega}[gYY']_l^r},
\qquad
Z_\Omega=2\int_\Omega a^3(f^2+6\psi^2)\,dz.
\]

This is an algebraic consequence of the already adopted equations; no source-specific scalar product has been imported. The first integral remains regular at \(S=0\) when interpreted through its equal regular density.

### Finite wall terms

For inward signs \(\sigma_a=+1\), \(\sigma_b=-1\), retain the existing definition

\[
B_i=\frac{\sigma_i a_i\gamma S_i}{2}-S'_i+A_iS_i.
\]

At a wall, the constraint and scalar Robin condition give \(B_if_i=3\lambda\psi_i\). Where \(S_iB_i\ne0\),

\[
g_iY_iY'_i=-\frac{3\lambda Y_i^2}{2a_iS_iB_i}.
\]

Consequently, on an interval with no scalar turn,

\[
\frac Z{12}=\lambda\left[
\int gY^2 dz+rac{3Y_a^2}{2a_aS_aB_a}
-\frac{3Y_b^2}{2a_bS_bB_b}\right].
\]

This equation displays precisely why a reduced boundary-corrected product and the regular action norm need not have the same sign: their relation includes the spectral factor \(\lambda\). The bracket is not independently identified as the original physical kinetic norm. Where an endpoint denominator vanishes, keep the division-free flux identity and the regular wall equations instead of this rearrangement. No sign for the actual upper endpoint denominator has been newly certified here.

### Interior scalar turn

Let \(z_*\) be a simple scalar minimum and put \(x=z-z_*\), \(s_1=S'(z_*)\ne0\). Simplicity is an explicit hypothesis of this local expansion. The inherited background equation gives \(S'_* = a_*^2m_b^2\Phi_*\); hence positive \(\Phi_*\), \(a_*\), and the fixed \(m_b^2=0.41\) imply it. The existing formulation describes that positive-scalar minimum, but this note supplies no new interval location, uniqueness, or simplicity certificate for the turn. The exact cut-domain identity above does not require this expansion. The existing regular equations imply

\[
S=s_1x+O(x^2),\qquad
s_1f_*=-3\lambda\psi_*,\qquad
Y'=\lambda Y_*x+O(x^2).
\]

For \(Y_*\ne0\), which follows for the certified positive \(\psi\) profile and positive warp factor,

\[
gY^2=\frac{cY_*^2}{x^2}+O(x^{-1}),\qquad
gYY'=\frac{c\lambda Y_*^2}{x}+O(1),
\quad c=\frac{3}{2a_*s_1^2}>0.
\]

Take \(\Omega_\epsilon=[z_a,z_*-\epsilon]\cup[z_*+\epsilon,z_b]\). The bulk weighted integral diverges as \(2cY_*^2/\epsilon\). Its coefficient after multiplication by \(\lambda\) is canceled exactly by the leading internal flux

\[
gYY'(z_*-\epsilon)-gYY'(z_*+\epsilon)
=-\frac{2c\lambda Y_*^2}{\epsilon}+O(1).
\]

The left-hand side of the boxed identity tends to the finite positive \(Z/12\). Dropping the internal flux, requiring finite \(\int gY^2\), or imposing \(Y_*=0\) would remove this regular physical mode from the domain. The cutoff is a tool for demonstrating equivalence, not a new wall or a prescription for modifying the certified equations. Only the combined limit has been identified here; no new separately renormalized physical norm is asserted.

This explains compatibility of \(\lambda_*<0\) and \(Z>0\) with failure of the naive positive-weight inference. It does not by itself prove that the scalar turn causes the instability, or separate its influence from finite wall stiffness and curvature.

## A regular Green identity

A second candidate identity avoids the divided variable completely. Take two real admissible profiles indexed by \(i,j\) on exactly the same background and domain. Define

\[
U=\psi_i f_j-f_i\psi_j,\quad
W=f_i p_j-p_i f_j,\quad \Delta\mu=\mu_i-\mu_j,
\quad J=a^3(W-2SU).
\]

The scalar equation uses \(12AS-4a^2m_b^2\Phi=-4S'\). Its antisymmetrized product, and the analogous product of the two constraints, give respectively

\[
W'=-3AW+\Delta\mu f_if_j+4S'U,
\qquad
SU'=(S'-3AS)U-3\Delta\mu\psi_i\psi_j.
\]

Consequently,

\[
\boxed{J'=\Delta\mu\,a^3(f_if_j+6\psi_i\psi_j).}
\]

No division by \(S\), \(\lambda\), or a wall denominator is involved. For equal finite stiffness the Robin conditions imply \(W=2SU\) at both walls. Distinct real eigenvalues are therefore orthogonal in the regular kinetic bilinear form \(2\int a^3(f_if_j+6\psi_i\psi_j)dz\). This is an equation-level orthogonality identity, not a completeness or full self-adjoint-domain theorem.

For two different wall Hessians on the same exact background, put \(\delta\gamma_\alpha=\gamma_{\alpha,j}-\gamma_{\alpha,i}\), where \(\alpha=a,b\) indexes the walls. The endpoint flux is

\[
J_\alpha=\frac{\sigma_\alpha a_\alpha^4}{2}
\delta\gamma_\alpha f_i(z_\alpha)f_j(z_\alpha).
\]

The signed endpoint identity then becomes

\[
\boxed{(\mu_j-\mu_i)\,2\int a^3(f_if_j+6\psi_i\psi_j)dz
=\sum_{\alpha=a,b}a_\alpha^4\delta\gamma_\alpha
f_i(z_\alpha)f_j(z_\alpha).}
\]

Under a differentiable eigenmode branch this gives the response proposed below, without importing a reduced scalar product. The following candidate argument establishes the needed local simplicity from the already accepted regular equations and norm; the numerical existence certificate by itself did not assert that result. The identity gives no numerical slope or finite-change stability threshold.

### Local simplicity from the regular flux

Let \((\psi_*,f_*,p_*)\) be an exact eigenmode at \(\mu_*\) and let \((\psi_\mu,f_\mu,p_\mu)\) be the smooth lower-wall normalized IVP at nearby \(\mu\), on the same exact background. The certified nonzero lower \(B_a\) makes its launch data smooth. Write the conformal upper residual as

\[
R(\mu)=p_\mu(z_b)+2S_b\psi_\mu(z_b)+\frac{a_b\gamma}{2}f_\mu(z_b).
\]

The regular Green identity gives

\[
(\mu_*-\mu)\int a^3(f_*f_\mu+6\psi_*\psi_\mu)dz
=a_b^3 f_*(z_b)R(\mu),
\]

because the lower flux vanishes and \(R(\mu_*)=0\). Moreover, \(f_*(z_b)\ne0\): otherwise \(B_bf_b=3\lambda_*\psi_b\), with \(\lambda_*\ne0\), forces \(\psi_b=0\), and the Robin condition forces \(p_b=0\). Uniqueness for the regular linear IVP would then make the entire normalized mode zero. Differentiating at \(\mu_*\) therefore gives

\[
\boxed{R'(\mu_*)=-\frac{Z_*}{2a_b^3f_*(z_b)}\ne0.}
\]

This establishes a simple local determinant zero, conditional on the displayed Green identity and the already accepted exact-background mode equations. It does not count roots elsewhere or establish a lowest mode. The proper-coordinate determinant used in the interval certificate differs by the nonzero factor \(a_b\), so simplicity is unchanged by that coordinate conversion. Smooth background-preserving wall-Hessian deformations then admit a local smooth mode branch by the implicit-function theorem.

## Ranked smallest follow-ups

1. **Audit the cutoff and regular Green identities as explanatory lemmas.** Independently derive the boxed identities directly from the displayed regular equations, verify both wall signs, and derive the local cancellation without assuming the divided equation at the turn. Preserve \(Y=-\tfrac12Y_{\rm FK}\) when comparing conventions. Estimated effort: 30–60 minutes of analytic review; no physical integration is needed. Pass means exact equivalence and orthogonality statements with explicit domains. Failure means retain the regular norm and identify the erroneous transformation; it does not independently overturn the existing certificate. This is the most immediately useful addition to the interpretation of the negative shifted mode.

2. **Derive the regular quadratic mass form and its Green identity.** Extend the already accepted tangential kinetic derivation to the complete second variation, including Gibbons–Hawking terms, pure wall potentials, constraints, and endpoint terms. Its admissible stationary modes should reproduce the existing three-variable system and both Robin conditions. Keep \((\psi,f)\) regular across the turn. This would place any separation of bulk, curvature and wall energy contributions on an action-derived basis; individual contributions depend on integration-by-parts convention, so freeze that convention. Estimated effort: 2–4 hours of analytic work plus independent review. No completeness, lowest-mode or ghost conclusion follows before the constrained domain and bilinear form have been established.

3. **Prepare a fixed-background wall-Hessian response, conditional on independent review of the regular Green and simplicity identities.** Define an explicit nearby action by
   \[
   \tau_i^{(\eta)}(\Phi)=\tau_i(\Phi)+\tfrac12\eta_i(\Phi-\Phi_i^*)^2.
   \]
   The added term and its first derivative vanish on the exact central background, so its bulk solution, curvature and wall junction values remain fixed while its fluctuation stiffness changes. This is a declared counterfactual action, not a variation of the original fixed model's result. For an isolated simple mode, the prospective Feynman–Hellmann relation is
   \[
   \frac{\partial\mu_*}{\partial\eta_i}
   =\frac{a_i^4 f_i^2}{Z}\ge0.
   \]
   The local simplicity argument above is the additional analytic bridge beyond the existence certificate. The finite-difference identity supplies the derivative directly if the displayed derivation is accepted; a full constrained-action cross-check remains useful before a physical response computation. Both endpoint scalar amplitudes are nonzero by the same \(\lambda_*\ne0\) argument, so the derivative is then strictly positive. Estimated effort: 1–2 hours for independent analytic admission and preparation of any separately frozen validated response computation. This isolates local stiffness response without re-solving a changed background. Varying \(\gamma\) alone while keeping the old \(\lambda_i,v_i\) fixed would not do that. Do not extrapolate the local slope to a stabilizing threshold or automatically continue toward one.

The first item closes an explanatory representation gap. The second and third could identify an action-specific response of the instability. None is required to preserve the present certified positive-norm negative mode, and none establishes nonlinear evolution, causal boundaries, or novelty of the scalar instability itself.
