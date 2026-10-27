# Scalar kinetic norm and curved pure-gravity radion control

Date: 2026-09-29. Independent analytic review for this successor only.

This note derives a kinetic diagnostic and an exact control before evaluating
the candidate's spectrum. It uses the doubled-cover action in
`source-snapshot/brane-horizon-phase-structure/MODEL_V1.md`, the finite wall
potentials fixed by `EXECUTION_REQUEST.md`, and the conventions of the inherited
`static-background-successor/PROSPECTIVE_BVP_DESIGN.md`. No candidate eigenvalue
is asserted here. This is a five-dimensional scalar–gravity calculation, not
an extension of the four-dimensional interface comparator.

## 1. Conventions and the physical variable

Write the background as

\[
 ds^2=a(z)^2\{dz^2+\gamma_{\mu\nu}dx^\mu dx^\nu\},\qquad
 R_{\mu\nu}[\gamma]=3k\gamma_{\mu\nu},\qquad A=a'/a.
\]

The signature of the four-dimensional metric is \((-+++)\). In longitudinal
scalar gauge take

\[
 ds^2=a^2\{[1+2N(z)q(x)]dz^2+
              [1+2\Psi(z)q(x)]\gamma_{\mu\nu}dx^\mu dx^\nu\},
 \qquad \delta\Phi=f(z)q(x),\qquad \Box_\gamma q=\mu q.
\]

Here \(\mu=m_4^2\); it is not the five-dimensional scalar potential parameter
\(m_\Phi^2\). For generic scalar harmonics the traceless tangential and mixed
Einstein equations give

\[
 N=-2\Psi,\qquad
 \Psi'+2A\Psi=-\frac{\kappa_5^2}{3}\Phi'f.                 \tag{1}
\]

The word generic concerns the tensor decomposition, not an exclusion of an
eigenvalue: scalar functions with vanishing trace-free Hessian require the
unprojected equations. In particular, division by \(\mu+4k\) is not allowed
when specifying the physical domain.

Let the two coordinate wall displacements be \(\zeta_aq\) and
\(\zeta_bq\). The first variation of their background-normal separation is

\[
 \delta D=q\left[a_b\zeta_b-a_a\zeta_a+
                  \int_{z_a}^{z_b} aN\,dz\right].          \tag{2}
\]

The change of the connecting normal curve does not contribute to its length
at first order. Under a normal coordinate shift \(z\mapsto z+T(z)q\),
\(N\mapsto N-T'-AT\) and \(\zeta_i\mapsto\zeta_i+T_i\);
the endpoint and integral changes in (2) cancel. Tangential coordinate
changes do not change this first-order observable because the background
separation is constant on a slice.

For the generic scalar sector, the trace-free Israel condition of a pure
potential wall sets its longitudinal-gauge bending to zero: its trace-free
part is proportional to
\(\zeta_i(D_\mu D_\nu q-\gamma_{\mu\nu}\Box q/4)\). Straight
coordinate walls are consequently compatible with (1); their proper
separation remains dynamical:

\[
             \delta D=-2q\int_{z_a}^{z_b}a\Psi\,dz.       \tag{3}
\]

A nonzero (3) diagnoses a separation perturbation. Its vanishing would not
by itself make an arbitrary coupled scalar mode pure gauge.

## 2. Kinetic norm directly from the action

The action is normalized on the doubled cover. Equivalently, both the
interval bulk action and its Gibbons–Hawking–York contribution are doubled,
whereas each wall action occurs once. There are no wall curvature terms or
wall scalar kinetic terms in the selected model.

Use a radial ADM decomposition with radial shift zero. To identify the
quadratic tangential derivatives, write its induced metric and radial lapse
as
\(h_{\mu\nu}=a^2e^{2\psi}\gamma_{\mu\nu}\) and
\(\mathcal N=ae^n\), where
\(\psi=\Psi q\), \(n=Nq\) at first order. The intrinsic-curvature piece is

\[
 \mathcal N\sqrt{-h}\,R[h]
 =a^3\sqrt{-\gamma}\,e^{n+2\psi}
  \left[R[\gamma]-6\Box_\gamma\psi-6(\partial\psi)^2\right].
                                                               \tag{4}
\]

The extrinsic-curvature terms contain normal derivatives, but no tangential
derivatives in this gauge. After imposing the first constraint in (1),
\(n+2\psi\) has no linear term. The term \(\Box\psi\) is then a
tangential total derivative through the required order, and (4) contributes
\(-3a^3(\partial\psi)^2/\kappa_5^2\). The canonical scalar contributes
\(-a^3(\partial(fq))^2/2\). Second-order choices of metric parametrization
do not change this result when expanded about a stationary background with
its junction conditions.

The physical mode therefore has

\[
 S_{\mathrm{kin}}^{(2)}
 =-\frac12 Z\int d^4x\sqrt{-\gamma}\,
              \gamma^{\mu\nu}\partial_\mu q\partial_\nu q,
 \qquad
 \boxed{Z=2\int_{z_a}^{z_b}dz\,a^3
        \left(f^2+\frac{6}{\kappa_5^2}\Psi^2\right).}      \tag{5}
\]

For complex mode conventions replace squares by absolute squares. The
leading factor two is the doubled-cover factor; \(\kappa_5=1\) for the
candidate. Each mode must be an admissible solution of the bulk constraints
and both wall conditions before (5) is interpreted as its kinetic norm.

For every nonzero real admissible profile of finite norm, (5) is positive.
Thus a negative mass squared in this sector is a tachyonic instability,
not a negative-kinetic-energy ghost. Positivity of (5) does not establish
the sign of the mass operator, nor classify other perturbation sectors or
modified wall actions. In particular, it does not establish stability of
the candidate.

There is no division by \(\Phi'\) in (5). It is the appropriate norm to
retain at a background scalar turning point, even when a reduced
Sturm–Liouville variable or its weight is singular there. A numerical
implementation may evaluate a smooth reduced variable elsewhere, but
must reconstruct the regular physical profiles for this diagnostic.

## 3. Finite wall stiffness

Let the inward signs be \(s_a=+1\), \(s_b=-1\), and
\(\tau_i=\lambda_i+\gamma_i(\Phi-v_i)^2/2\). The background junctions are

\[
 s_i\frac{a'}{a^2}=-\frac{\kappa_5^2\tau_i}{6},\qquad
 s_i\frac{\Phi'}a=\frac{\tau_i'}2.
\]

For straight coordinate walls their first variations give

\[
 \boxed{\ s_i\frac{f'-N\Phi'}a=\frac{\gamma_i}{2}f\ },\qquad
 s_i\frac{\Psi'-AN}{a}=-\frac{\kappa_5^2\tau_i'}6 f.     \tag{6}
\]

After (1), the latter is the boundary value of the mixed constraint and
the background scalar junction. The independent scalar Robin conditions
can be written

\[
 f'_a+2\Psi_a\Phi'_a-\frac{a_a\gamma_a}{2}f_a=0,\qquad
 f'_b+2\Psi_b\Phi'_b+\frac{a_b\gamma_b}{2}f_b=0.          \tag{7}
\]

The fixed value \(\gamma_i=20\) must remain in (7). Replacing these
conditions by \(f_i=0\) changes the spectral problem. Dirichlet behavior
can arise only as an appropriate stiff limit with bounded other terms;
even that limit does not set (3) to zero. Pure wall potentials contribute
to the potential energy and to (6)–(7), but provide no direct tangential
kinetic term in the straight-wall action used to derive (5).

## 4. Exact curved pure-gravity control

Switch off the background stabilizer and its perturbation, and set the
wall scalar targets to zero. Construct a vacuum warped solution with the
chosen nonzero \(k\), and choose its two fixed wall tensions from the
background Israel conditions. This is a separate control background;
it does not inherit the candidate's two numerical tensions.

The mixed constraint in (1) now integrates to

\[
                  \Psi=C a^{-2},\qquad N=-2Ca^{-2},
                  \qquad f=0.                            \tag{8}
\]

For the positive-\(z\) normal define
\(B=a'/a^2\), so \(K^\mu{}_{\nu}=B\delta^\mu{}_{\nu}\). The
first variation is

\[
 \delta K^\mu{}_{\nu}
 =\frac{\Psi'-AN}{a}q\,\delta^\mu{}_{\nu}=0.             \tag{9}
\]

Both fixed-tension Israel conditions are therefore satisfied. The
normal-normal Einstein constraint, using a unit spacelike normal, is

\[
 G_{nn}=-\tfrac12R[h]+\tfrac12(K^2-K_{\mu\nu}K^{\mu\nu}).
\]

Its vacuum first variation is zero, while (9) makes its extrinsic part
unchanged. The intrinsic curvature variation is

\[
 \delta R[h]=-6a^{-2}\Psi(\Box_\gamma+4k)q.
\]

Thus the nonzero radion obeys

\[
                   \boxed{\mu=m_4^2=-4k.}                \tag{10}
\]

This is a constraint derivation of the mass, independent of fitting a
spectrum. The same profiles satisfy the remaining vacuum equations; they
are the standard curved two-brane radion control. Their norm and separation
variation are

\[
 Z=\frac{12C^2}{\kappa_5^2}\int_{z_a}^{z_b}\frac{dz}{a}>0,
 \qquad
 \delta D=-2Cq\int_{z_a}^{z_b}\frac{dz}{a}\ne0.           \tag{11}
\]

The integration interval is finite and has positive warp factor. These
profiles are not eliminated by fixing wall coordinates: their proper
separation changes. For \(k=0\), the control becomes the massless vacuum
radion. For \(k>0\), it is a positive-norm separation instability.

The independent primary-source check is Z. Chacko and P. J. Fox,
“Wave Function of the Radion in the dS and AdS Brane Worlds,”
*Physical Review D* **64**, 024015 (2001),
[doi:10.1103/PhysRevD.64.024015](https://doi.org/10.1103/PhysRevD.64.024015),
[arXiv:hep-th/0102023](https://arxiv.org/abs/hep-th/0102023).
Their equations (20)–(24) give the same wavefunction and curved mass;
equation (34) provides a positive kinetic coefficient. With their warp
factor \(f_{\rm CF}=a^2\), proper coordinate \(dr=a\,dz\), and
\(1/(2\kappa_5^2)=2M^3\), their perturbation amplitude corresponds to
\(C=1/2\) in (8). Equation (5) then gives
\(Z=12M^3\int dr/f_{\rm CF}\), agreeing with their effective action.

## 5. The exceptional value and the growth criterion

The pure-gravity control sits at \(\mu+4k=0\). Any reduction dividing by
that factor loses a real physical control and is unacceptable without a
separate analysis at that value. For a scalar function in four-dimensional
constant curvature,

\[
 D^\mu\left(D_\mu D_\nu q-\tfrac14\gamma_{\mu\nu}\Box q\right)
 =\tfrac34 D_\nu(\Box+4k)q.
\]

Consequently, tensor decomposition has an exceptional structure there.
Some functions also have zero trace-free Hessian. This affects which
projected equation supplies a constraint; it is not evidence that all
solutions at that mass are gauge. Gauge identification must use the full
equations and observables such as (2). Equations (8)–(11) supply an explicit
physical representative.

For \(k>0\), let \(H=\sqrt{k}\). A homogeneous physical mode obeys

\[
 \ddot q+3H\dot q+\mu q=0,\qquad
 r_\pm=\frac{-3H\pm\sqrt{9H^2-4\mu}}2.
\]

A resolved negative \(\mu\), with positive (5) and nonzero physical
amplitude, has a growing branch. For the control \(\mu=-4k\),
\(q\propto e^{Ht}\) or \(e^{-4Ht}\). Spatial momenta redshift on the
expanding patch, so the long-wavelength criterion is not replaced by a
flat-space oscillation test. The stabilizer can change the eigenvalue;
the control alone does not decide whether this particular stabilized
candidate grows.

## Review conclusion

The proposed numerical problem should retain the regular constrained
profiles across every zero of \(\Phi'\), keep finite wall stiffness,
include \(\mu+4k=0\) in its domain, report (5), and measure the separation
overlap (3). Recovering (8)–(11) on a separately specified vacuum curved
background is an exact control of the physical radion convention. No
candidate spectrum or stability conclusion has been computed in this note.
