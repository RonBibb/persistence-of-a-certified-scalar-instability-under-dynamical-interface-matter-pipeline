# Uniqueness of the real scalar eigenvalue in the certified mass strip

The accepted regular Green identity and the already certified full-strip profile bounds imply at most one real scalar eigenvalue in

\[
\mathcal J=[-33/25000,-131/100000].
\]

Combined with the inherited endpoint-sign existence certificate, this gives exactly one real physical scalar eigenvalue in this declared strip for the same exact central background and finite-stiffness wall action. This is a new analytic consequence of retained evidence. No new numerical integration, source-data computation or scientific test was run for this note. Independent proof review is recorded separately.

## Controlling evidence

The [central certificate](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/RESULT_REPORT.md), its [independent proof audit](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/INDEPENDENT_PROOF_AUDIT.md), and the accepted exact rational bounds in [output/RESULT.json](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/output/RESULT.json) control the background, action, root strip and profile domain. In particular, the `primary_strip` task's global extrema, rather than either endpoint-only task, give bounds stronger than the coarse rational inequalities

\[
-1\le f(s;\mu)\le3,\qquad
\psi(s;\mu)\ge99/100
\]

uniformly over the retained exact-background enclosure, the full mass strip and the physical interval through the upper-wall event. The saved approximate endpoints, only for locating these exact source entries, are \(-0.7934771790248728\), \(2.51594813400084\), and \(0.9998406347043585\), respectively. The exact rational source endpoints and the existing audit supply the inequalities; these displayed decimal approximations are not replacement proof inputs.

The [accepted Green-identity review](../20261013T073517Z_PAPER_A_CURVATURE_RESPONSE/FINITE_STIFFNESS_PROOF_REVIEW.md) proves that two real eigenprofiles on the same exact background with distinct eigenvalues and the same finite Robin walls satisfy

\[
\int_0^{D_*} e^{2W(s)}
[f_i(s)f_j(s)+6\psi_i(s)\psi_j(s)]\,ds=0.
\]

This is the proper-coordinate form of the conformal integral \(\int a^3(\cdots)dz\), with \(ds=a\,dz\) and \(a=e^W>0\). Its proof does not divide by the background scalar gradient and remains valid at its interior zero.

## Normalization covers every nontrivial mode in the strip

The lower wall and constraint give \(B_a f_a=3(\mu+4k)\psi_a\), with the inherited \(B_a\ne0\). If a mode had \(\psi_a=0\), then \(f_a=0\), and the lower Robin condition would give \(p_a=0\). Uniqueness for the regular linear IVP would make that entire mode zero. Every nontrivial mode in the retained sector can therefore be normalized to \(\psi_a=1\), precisely the normalization used for the uniform strip bounds. The certified nonzero \(\mu+4k\) also keeps the argument inside the same retained nonexceptional sector.

Different eigenvalues are compared on the same exact background, not different members of a background uncertainty box. Their normalized profiles are each covered by the uniform bounds. No assumption that either scalar profile \(f\) is positive is needed.

## Positive overlap excludes two distinct roots

For any two real numbers in \([-1,3]\), their product is at least \(-3\). Hence two normalized eigenprofiles in \(\mathcal J\) would satisfy, at every point of the physical interval,

\[
f_i f_j+6\psi_i\psi_j
\ge-3+6(99/100)^2
=\frac{14403}{5000}>0.
\]

The interval has positive length and positive warp factor, so

\[
\int_0^{D_*}e^{2W}(f_i f_j+6\psi_i\psi_j)ds
\ge\frac{14403}{5000}\int_0^{D_*}e^{2W}ds>0.
\]

This contradicts Green orthogonality whenever \(\mu_i\ne\mu_j\). There is therefore at most one real eigenvalue in \(\mathcal J\). The inherited endpoint signs already establish an eigenvalue strictly inside \(\mathcal J\), so there is exactly one. The previously accepted determinant-derivative identity additionally makes this root locally simple; uniqueness within the strip and local simplicity are distinct statements.

## Claim boundary

The conclusion concerns the retained regular coupled scalar sector, the same exact central background, unchanged finite wall potentials, and this one declared real mass strip. It does not establish absence of real roots elsewhere, a lowest eigenvalue, exclusion of complex spectrum, a complete spectral classification, uniqueness across other backgrounds or actions, nonlinear evolution, or a stabilizing stiffness threshold. The earlier existence certificate remains preserved; its original no-uniqueness limitation is extended only by this later evidence-linked analytic argument and its independent review.

