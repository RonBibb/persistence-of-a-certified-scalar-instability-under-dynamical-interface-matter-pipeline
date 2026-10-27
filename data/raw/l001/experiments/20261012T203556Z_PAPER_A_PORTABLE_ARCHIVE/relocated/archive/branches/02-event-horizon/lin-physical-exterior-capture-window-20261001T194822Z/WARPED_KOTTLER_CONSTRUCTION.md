# Warped-Kottler outer-end construction

## Result in one sentence

There is a complete conditional positive control for the physical-exterior and
capture architecture: any exact positive-curvature warp/scalar background of
the declared pure-potential two-brane action can have its four-dimensional de
Sitter base replaced by a Kottler (Schwarzschild-de Sitter) base with the same
curvature.  A fixed-radius cylinder between the black-hole and cosmological
horizons then has the **full** barrier remainder \(\mathcal E=0\) for all time,
and one trapped cap and one visible event give an exact central
end-relative-horizon bracket.

This closes the logic on that exact model family.  It does **not** qualify the
current collapse lineage: the available positive-curvature warp/scalar
background is a numerical candidate at a different brane separation, not a
rigorously enclosed exact background or a continuation of the collapse data.

## 1. Same-action Einstein-base replacement

Let an exact background of the declared action have

\[
 g_5=\psi(z)^2\,[\gamma_k+dz^2],\qquad
 \Phi=\Phi(z),\qquad \chi=0,
 \qquad \operatorname{Ric}(\gamma_k)=3k\gamma_k.
\]

For any other four-dimensional Einstein metric with the same Ricci
coefficient, the five-dimensional curvature reduction is unchanged:

\[
 R^{(5)}_{\mu\nu}
 =\bigl(3k-\omega''-3\omega'^2\bigr)\gamma_{\mu\nu},
 \quad
 R^{(5)}_{zz}=-4\omega'',
 \quad R^{(5)}_{\mu z}=0,
 \qquad \omega=\log\psi.
\]

The scalar equation and its kinetic scalar still depend only on \(z\).  At a
constant-\(z\) brane, the induced metric changes covariantly while

\[
 K_{\mu\nu}=\pm\frac{\psi'}{\psi^2}h_{\mu\nu},
 \qquad n(\Phi)=\pm\frac{\Phi'}\psi
\]

are unchanged.  Thus the same bulk equations and pure-potential Israel/Robin
conditions hold.  This is the curved-base analogue of the bound Ricci-flat
base replacement, not a splice across a radial shell.

Choose the Kottler base

\[
 \gamma_K=-f(r)\,dv^2+2\,dv\,dr+r^2d\Omega_2^2,
 \qquad
 f(r)=1-\frac{2M}{r}-kr^2.
\]

Direct symbolic reduction checks all 25 five-dimensional Ricci components and
returns

\[
 \operatorname{Ric}(\gamma_K)=3k\gamma_K
\]

exactly.  When \(M>0\), \(k>0\), and \(27kM^2<1\), \(f\) has a black-hole
horizon \(r_b\) and cosmological horizon \(r_c\), with \(f>0\) on
\((r_b,r_c)\).  Curved stabilized branes and Einstein-base replacement are
standard background mechanisms; the coefficients here come from the bound
model equations rather than being imported from the literature.  See
[DeWolfe et al., hep-th/9909134](https://arxiv.org/abs/hep-th/9909134) for the
flat-versus-curved brane distinction and
[Chamblin, Hawking and Reall, hep-th/9909205](https://arxiv.org/abs/hep-th/9909205)
for the Ricci-flat black-string precedent.

## 2. Exact all-future barrier

Fix \(R\in(r_b,r_c)\) and use the cylinder
\(\mathcal T_R=\{r=R\}\).  It is timelike because \(f(R)>0\).  The function
\(\tau=v-r\) is temporal because
\(g^{-1}(d\tau,d\tau)=\psi^{-2}(f-2)<0\).  On the fixed-radius cylinder,
constant \(\tau\) and constant \(v\) sections coincide.  Such a section has
metric

\[
 q=\psi^2\bigl(R^2d\Omega_2^2+dz^2\bigr)
\]

and meets both constant-\(z\) branes orthogonally.  Its future unit cylinder
tangent and outward unit normal are

\[
 T=\frac{1}{\psi\sqrt f}\,\partial_v,
 \qquad
 \nu=\frac{1}{\psi\sqrt f}\,\partial_v
      +\frac{\sqrt f}{\psi}\,\partial_r.
\]

Therefore \(k=T+\nu\) is future outward null and
\(k^r=\sqrt f/\psi>0\).  Since the section volume density is proportional to
\(\psi^3R^2\),

\[
 \theta^+=\frac{2\sqrt{f(R)}}{\psi R}>0,
 \qquad
 \frac{\theta^+}{k^r}=\frac2R.
\]

In the previously derived production-variable identity, \(A=B=\psi^2\),
\(U_0=V_0=0\), every radial and time derivative vanishes, and section
normality gives \(k^z=0\).  Consequently every retained radial, temporal,
compact-tilt and warp-slope term has been evaluated, and

\[
 \boxed{\mathcal E=0}
\]

for every future section.  This is stronger than the symmetric
\(R|\mathcal E|/2<1\) budget and is not an extrapolation from a finite archive.
The nonzero Eddington-Finkelstein \(g_{vr}=\psi^2\) is not ignored: it enters
the normalized null direction (here \(k^v/k^r=2/f\)), while multiplying an
identically zero temporal derivative block in \(\mathcal E\).

## 3. Exact trapped cap

For a section at fixed \((v,r)\), take future null normals proportional to

\[
 \ell=\partial_v+\frac f2\partial_r,
 \qquad n=-\partial_r.
\]

Their expansion signs are those of

\[
 \theta_{\ell}=\frac f r,\qquad \theta_n=-\frac2r.
\]

Hence every \(r_0<r_b\) with \(f(r_0)<0\) supplies a future-trapped compact
\(S^2\times[z_-,z_+]\) cap.  It lies on the smooth spacelike slice
\(\tau=v-r=\mathrm{constant}\), whose radial metric coefficient is
\(2-f>0\).  The cap meets the physical branes orthogonally.

For an exact canonical Einstein-scalar lift, null convergence follows from
the scalar-gradient square after null contraction, and the branes remain
umbilic.  Choosing a globally hyperbolic block (or otherwise proving the
closed-future hypothesis) supplies the remaining causal premise of the finite
barrier theorem.

The exact control also has a direct capture cross-check.  Inside the future
black-hole region, \(f<0\) and
\(g(\nabla r,\nabla r)=\psi^{-2}f<0\).  With the advanced-chart future
orientation, \(\nabla r\) is future timelike.  Hence every future causal
vector \(X\) satisfies

\[
 X(r)=g(\nabla r,X)<0.
\]

No future causal curve from the chosen cap can cross \(r_b\) outward.  This
direct Kottler fact independently certifies the control endpoint; it does not
replace the finite-barrier lemma's closed-future hypothesis in a general
nonstationary development.

## 4. Physical outer end and causal-past equality

For a fixed \(\tau_0\), define the connected future static exterior

\[
 E_{\mathrm{stat}}=\{\tau>\tau_0,\ r_b<r<r_c\}
\]

in the chosen common development, and its outer portion

\[
 E_R=\{\tau>\tau_0,\ R<r<r_c\}\subset E_{\mathrm{stat}}.
\]

The nontrivial inclusion needed for transfer is exact.  If
\(q\in E_{\mathrm{stat}}\) has \(r(q)<R\), its fixed-\(z\), fixed-angle
outgoing null curve obeys

\[
 \frac{dr}{dv}=\frac{f(r)}2>0
\]

and reaches any fixed \(R+\epsilon<r_c\) in finite advanced time, with
\(\tau\) increasing, because \(f\) has a positive minimum on every compact
subinterval strictly inside \((r_b,r_c)\).  Points
already outside \(R\) lie in \(E_R\).  Thus

\[
 E_{\mathrm{stat}}\subset J^-(E_R).
\]

Together with \(E_R\subset E_{\mathrm{stat}}\), this gives the transfer
authority

\[
 \boxed{J^-(E_R)=J^-(E_{\mathrm{stat}})}.
\]

This is the curved static-region counterpart of the slow-time finite-infinity
equality used for uniform Kaluza-Klein ends.  Chruściel, Galloway and Solis
state the analogous finite-infinity equality as their Eq. (5.2) under uniform
KK asymptotics: [arXiv:0808.3233](https://arxiv.org/abs/0808.3233).

The equality above is **not** an equality with the original program's
asymptotically flat warped-KK end.  Positive \(k\) changes the global end.  A
further identification with a selected de Sitter conformal-boundary component
would require its own completion statement, but is unnecessary for the
end-relative statement using \(E_{\mathrm{stat}}\).  The absence of an
ordinary spatial infinity and the distinct roles of black-hole and
cosmological horizons in de Sitter black holes are standard; see
[Gomberoff and Teitelboim, hep-th/0302204](https://arxiv.org/abs/hep-th/0302204).

## 5. One central bracket

Choose on one \(\tau\)-slice, at fixed compact coordinate and angles:

- \(p_c\) at \(r_0<r_b\), on the certified trapped cap;
- \(p_v\) at \(r_v\in(r_b,R)\).

The direct Kottler capture argument gives \(p_c\notin J^-(E_R)\), hence
\(p_c\notin J^-(E_{\mathrm{stat}})\): inside \(r_b\), every future causal
curve has strictly decreasing \(r\).  The exact outgoing null curve from
\(p_v\) reaches a certified portion of \(\mathcal T_R\) and then \(E_R\), so
\(p_v\in J^-(E_{\mathrm{stat}})\).  Because the curve enters the open set
\(E_R\), rather than merely terminating on its boundary, \(p_v\) is in the
interior of that causal past.  The connected radial curve from \(p_c\) to
\(p_v\) must cross

\[
 H_{E_{\mathrm{stat}}}=\partial J^-(E_{\mathrm{stat}}).
\]

In the exact control this crossing is the Kottler black-hole horizon
\(r=r_b\).  On the \(\tau\)-slice its fixed-\(z_0\) physical radial width is

\[
 L_{\rm br}=\psi(z_0)\int_{r_-}^{r_+}\sqrt{2-f(r)}\,dr.
\]

Taking certified endpoints \(r_-<r_b<r_+\) toward \(r_b\) makes this width
tend to zero.  For the numerical parameter instance below and
\(r_\pm=r_b\pm0.01\), the integral before multiplication by \(\psi(z_0)\) is
0.02828432273053786.  This is one central intersection, not a full
cross-section atlas.

Thus the exact control bracket does not depend on asserting the generic
finite-barrier theorem's closed-future premise for a partially specified
Kottler block.  That theorem remains the intended captured-endpoint route in
a nonstationary production development, where the direct monotonicity of
\(r\) will generally be unavailable.

## 6. Bound numerical instance

Using the retained curved-background candidate value
\(k=0.0003268413384542497\) only as a parameter and setting \(M=1\):

| quantity | value |
|---|---:|
| \(27kM^2\) | 0.008824716138264741 |
| \(r_b\) | 2.0026250398853990 |
| \(r_c\) | 54.28503858326507 |
| trapped-cap radius | 1.5 |
| visible-launch radius | 4 |
| barrier radius | 8 |
| \(f(1.5)\) | -0.3340687263448554 |
| \(f(8)\) | 0.7290821543389280 |
| \(\theta^+/k^r\) at \(R=8\) | 0.25 |
| \(\theta^+\) at \(R=8,\psi=1\) | 0.21346576926098245 |
| outgoing \(\Delta v\), 4 to 8 | 12.616910706422197 |

The exact symbolic control verifies all 25 warped Ricci identities and eight
independent Eddington-Finkelstein frame/expansion identities.  Nineteen
fail-closed geometry/authority tests pass.  These values demonstrate that the
Kottler geometric side has a nonempty sub-Nariai parameter region and lies
quantitatively well inside its static-region margins.  They do not prove that
the same-action warp/scalar antecedent exists exactly.

## 7. Exact remaining bridge to the collapse line

The construction becomes physical authority for the collapse program only if
all of the following are supplied in one lineage:

1. a rigorously enclosed exact positive-curvature warp/scalar background (or
   another exact all-future exterior);
2. the original brane separation and wall/corner data, or an explicit physical
   transition from the collapse separation to the curved branch;
3. a same-development matching/continuation theorem showing that the evolved
   exterior is the Kottler-type end without an undeclared radial shell;
4. continuum-enclosed trapped-cap expansions and causal closedness for that
   development; and
5. a continuum visible curve and common exterior identity.

The current candidate changes proper separation from approximately 0.99964 to
1.99757 and has only numerical qualification.  Therefore the present outcome
is **conditional model closure, not collapse-line event-horizon evidence**.
