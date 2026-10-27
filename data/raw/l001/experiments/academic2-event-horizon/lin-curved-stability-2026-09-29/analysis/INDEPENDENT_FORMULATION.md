# Independent coupled scalar–radion formulation — 2026-09-29

The declared Einstein–scalar action gives a regular three-variable first-order
system with one propagated constraint. It crosses an interior zero of the
background scalar derivative without division or an artificial matching wall.
Its physical four-dimensional mass is **mu**, whereas the convenient shifted
spectral parameter is **lambda = mu + 4k**. Finite wall stiffness must be retained.
The physical kinetic form is positive in the generic scalar-harmonic sector of
this action. These are formulation results, not a numerical stability outcome
for the candidate.

## 1. Action and conventions

Use signature (-++++), ell = kappa5 = 1, and the doubled-cover action

\[
 I=\int_{\widetilde M}\sqrt{-g}
 \left[\frac12(R+12)-\frac12(\nabla\Phi)^2
       -\frac12m_b^2\Phi^2\right]
 -\sum_i\int_{\Sigma_i}\sqrt{-h}\,\tau_i(\Phi),
 \qquad
 \tau_i=\lambda_i+\frac{\gamma}{2}(\Phi-v_i)^2.                 \tag{1}
\]

The background collapse scalar is zero; its separate linear test-field sector
is not included in the coupled stabilizer–geometry calculation. There is no
induced Einstein term, localized scalar kinetic term, or independently
fluctuating wall matter in (1). The equivalent one-sided interval action has
twice the bulk action and the corresponding Gibbons–Hawking terms, with each
wall potential included once. This fixes the half-Robin factor; it is not a
choice made by the perturbation solver.

Write

\[
 ds^2=a^2(z)[dz^2+\gamma_{\mu\nu}dx^\mu dx^\nu],\qquad
 {\rm Ric}(\gamma)=3k\gamma,\qquad
 A=a'/a,\quad S=\Phi',\quad m_b^2=0.41.                       \tag{2}
\]

Prime means differentiation with respect to conformal coordinate z. It does
not mean proper-distance or normalized-u differentiation. With z=z_a+Lu, all
first-order right sides below are multiplied by L when integrating in u.
The exact background identities used in the derivation are

\[
 a'=Aa,\quad \Phi'=S,\quad
 A'=A^2-k-S^2/3,\quad S'=a^2m_b^2\Phi-3AS,
 \quad
 A^2-k=a^2+S^2/12-a^2m_b^2\Phi^2/12.                         \tag{3}
\]

Inward normals are n_i= sigma_i a_i^{-1} partial_z, with sigma_a=+1 and
sigma_b=-1. Background walls satisfy

\[
 \sigma_i A_i/a_i=-\tau_i/6,\qquad
 \sigma_i S_i/a_i=\tau_{i,\Phi}/2.                           \tag{4}
\]

Keep gamma=20, v0=.1, v1=.09048374180359596,
lambda_a=5.999990376773895 and lambda_b=-6.052844277744164 fixed.
Changing L does not redefine v1. The lower tension retains its reconstructed
provenance; it is not promoted to a separately archived tension measurement.

## 2. Regular bulk equations

For a generic scalar harmonic Q on the de Sitter base, set

\[
 \Box_\gamma Q=\mu Q,\qquad
 ds^2=a^2\{(1+2\nu Q)dz^2+(1+2\psi Q)\gamma_{\mu\nu}dx^\mu dx^\nu\},
 \qquad \delta\Phi=fQ.                                      \tag{5}
\]

Here mu is the mass squared, not the mass. Longitudinal gauge has removed the
scalar shift and scalar shear. Equivalently, psi, nu and f are the usual
longitudinal gauge-invariant combinations. The exceptional harmonics for which
the traceless Hessian vanishes are treated separately in Section 4.

The traceless mu-nu Einstein equation gives nu=-2psi. The mixed z-mu equation
gives psi'+2Apsi=-Sf/3. Keeping f rather than eliminating it yields

\[
 \boxed{\begin{aligned}
 \psi'&=-2A\psi-Sf/3,\\
 f'&=p,\\
 p'&=-3Ap+(a^2m_b^2-\mu+2S^2)f
                  +(12AS-4a^2m_b^2\Phi)\psi.
 \end{aligned}}                                             \tag{6}
\]

The remaining Einstein constraint is

\[
 \boxed{C=Sp+(AS-S')f+[2S^2-3(\mu+4k)]\psi=0.}              \tag{7}
\]

These are three ordinary differential equations restricted to a two-dimensional
constraint subspace. A generic unconstrained third solution is not an extra
physical mode.

Here is an independent derivation of the curvature shift and signs. The
spacelike-normal Hamiltonian equation has
G_nn=-R[h]/2+6K_iso^2. At first order,

\[
 \delta R[h]=-6a^{-2}(\mu+4k)\psi Q,\qquad
 \delta G_{nn}=a^{-2}[3(\mu+4k)\psi+12A(\psi'-A\nu)]Q.
\]

The scalar normal stress variation is
a^{-2}[S(p-nu S)-a^2m_b^2 Phi f]Q. Equating these and using the momentum
constraint produces (7). Direct variation of the scalar equation gives

\[
 f''+3Af'+(\mu-a^2m_b^2)f+(4\psi'-\nu')S
                              -2\nu a^2m_b^2\Phi=0,          \tag{8}
\]

which becomes the last line of (6) after substitution. Thus the scalar equation
is independently retained at the turn, rather than recovered by division by S.

An exact algebraic check, substituting (3) and (6) before simplification, gives

\[
                         C'=-2AC.                           \tag{9}
\]

This was independently checked with symbolic polynomial differentiation. In
particular, a^2 C is constant on the exact background. Constraint contamination
can grow as a decreases; the numerical check should retain both C and a^2 C.
For an approximate retained background, (9) is an exact-background identity,
not a claim that interpolation or background residuals vanish.

For S nonzero, (6)–(7) reproduce equations (8a,b) of Frolov–Kofman with their
metric potential equal to -2psi. Their equation (14) supplies an independent
check on the wall sign below. Their physical harmonic mass is mu and their
shift is mu+4k. [Primary text, Sections II–III](https://arxiv.org/html/hep-th/0309002).

### Interior scalar minimum

At a simple turn S(z_star)=0, the equations impose the finite relations

\[
 \psi'(z_\star)=-2A_\star\psi_\star,\qquad
 S'_\star f_\star+3(\mu+4k)\psi_\star=0.                    \tag{10}
\]

For this positive scalar/mass background S'_star=a_star^2 m_b^2 Phi_star>0.
There is no delta-function source at the turn, no new boundary condition, and
no freedom to jump between the two sides. Integrating the smooth system (6)
with (7) is the regular continuation. Dividing by S, removing a small interval,
clipping S, or setting f=0 there changes the problem unless equivalence and
matching are established separately.

The retained candidate report exhibits an interior scalar minimum. This note
does not numerically locate or re-evaluate that minimum; parent authentication
and background diagnostics supply its quantitative location. Lesgourgues–Sorbo
explicitly discuss the singularity of divided variables and a regular variable
in their flat-base problem. Their flat stability theorem is useful context,
but its hypotheses do not establish this curved candidate's outcome.
[Primary text, equations (10)–(15), (44)](https://arxiv.org/html/hep-th/0310007).

## 3. Finite-stiffness walls and an unambiguous determinant

For fixed coordinate walls in longitudinal gauge, variation of (4) gives

\[
 \boxed{p_i+2S_i\psi_i=\sigma_i a_i\gamma f_i/2.}             \tag{11}
\]

The lower sign is plus on the right side; the upper sign is minus. The trace
Israel perturbation is psi'-A nu=-Sf/3, already the bulk momentum equation.
It is not an additional independent wall condition. Imposing a Dirichlet
condition f_i=0 at gamma=20 would substitute the infinite-stiffness model.

Define lambda=mu+4k and

\[
 B_i=\sigma_i a_i\gamma S_i/2-S'_i+A_iS_i.                   \tag{12}
\]

Equations (7),(11) at a wall imply B_i f_i=3lambda psi_i. If B_a is nonzero,
one may start with psi_a=1, f_a=3lambda/B_a and
p_a=sigma_a a_a gamma f_a/2-2S_a. A division-free initial vector is

\[
 (\psi_a,f_a,p_a)=
 (B_a,\,3\lambda,\,3\sigma_a a_a\gamma\lambda/2-2S_aB_a),   \tag{13}
\]

followed by a positive normalization. If B_a=lambda=0, this vector is zero
because the two boundary rows lose rank; construct their actual nullspace
rather than discarding that sector or interpreting a normalization pole as an
eigenvalue. The upper mismatch is simply

\[
             R_b(\mu)=p_b+2S_b\psi_b+a_b\gamma f_b/2.        \tag{14}
\]

Zeros of a properly normalized continuous determinant, with all bulk/constraint
and wall residuals satisfied, are candidate eigenvalues. No theorem here says
a finite sign scan finds the entire spectrum. Finding one resolved physical
negative mu suffices to disprove scalar-sector stability of this candidate.

## 4. Brane bending and physical separation

Fixing coordinate endpoints does not fix proper separation. To see precisely
which bending has been removed, initially allow a brane graph
z=z_i+zeta_i(x). In longitudinal gauge its scalar wall variation is

\[
 \frac{\sigma_i}{a_i}
 [f'-\nu S+(S'-AS)\zeta_i]
 =\frac{\gamma}{2}[f+S\zeta_i]                              \tag{15}
\]

(with harmonic amplitudes understood). Its mixed-index extrinsic curvature
variation is

\[
 \delta K_\mu{}^\nu=\frac{\sigma_i}{a_i}
 \{[\psi'-A\nu+(A'-A^2)\zeta_i]\delta_\mu{}^\nu
                         -D_\mu D^\nu\zeta_i\}.            \tag{16}
\]

Substitute the background wall equations, the bulk momentum constraint and
A'-A^2=-k-S^2/3 into the full pure-potential Israel condition. The f terms
cancel and its remaining bending equation is

\[
               D_\mu D_\nu\zeta_i+k\gamma_{\mu\nu}\zeta_i=0.\tag{17}
\]

Generic four-dimensional scalar harmonics do not obey (17), so their bending
amplitudes vanish in this gauge and (11) is the complete scalar wall condition.
The exceptional nonconstant de Sitter embedding harmonics satisfy
Box_gamma zeta=-4k zeta as well as the stronger tensor equation (17). They require
separate treatment of the degenerate scalar gauge decomposition. This does
**not** justify removing every physical radial solution at mu=-4k: generic
solutions of the Klein–Gordon equation with that mass need not obey (17).
The unstabilized radion control below is an explicit reason to retain that
mass sector. Likewise, a constant harmonic requires its own homogeneous gauge
analysis rather than an assumed propagating mode.

The first variation of proper separation, measured along the background normal
geodesics, is

\[
 \delta D(x)=\int_{z_a}^{z_b}a\,\nu(z,x)\,dz
                              +a_b\zeta_b(x)-a_a\zeta_a(x). \tag{18}
\]

This combination is invariant under an infinitesimal transverse coordinate
change: the integrated lapse variation cancels the endpoint changes. For the
generic straight-brane modes,

\[
             \frac{\delta D}{Q}=-2\int_{z_a}^{z_b}a\psi\,dz.\tag{19}
\]

A nonzero (19) identifies a physical separation component. A mode with zero
overlap can still be a physical instability elsewhere in the coupled scalar
sector; the word radion should not substitute for measuring this overlap.
Neither (18) nor (19) changes the fixed action parameters.

## 5. Positive kinetic form, including its normalization

Use the interval action with its doubled bulk and Gibbons–Hawking terms.
After removal of total derivatives, the terms containing four-dimensional
derivatives, before imposing nu=-2psi, are

\[
 I_{2,\partial x}=2\int dz\,d^4x\sqrt{-\gamma}\,a^3
 \left[-\frac12(D f)^2+rac{3}{\kappa_5^2}
             \{D\nu\mathbin{\cdot}D\psi+(D\psi)^2\}\right].\tag{20}
\]

For example, the gravitational part follows directly by expanding
N sqrt(-h) R[h]: its relevant conformal factor is
a^3(1+nu)e^{2psi}, and
R[e^{2psi}gamma]=e^{-2psi}[R[gamma]-6Box psi-6(Dpsi)^2].
Integration by parts gives the gravitational derivative terms in (20).
Extrinsic-curvature terms contain z derivatives; R[gamma]=12k changes the
potential terms. The pure wall potentials contain no four-dimensional kinetic
term for the generic zeta_i=0 modes.

Thus for a real separated mode the coefficient of the four-dimensional action
-1/2 integral sqrt(-gamma)(DQ)^2 is

\[
 \boxed{{\cal N}=2\int_{z_a}^{z_b}a^3
                 [f^2+6\psi^2/\kappa_5^2]dz>0.}             \tag{21}
\]

The factor 2 is the cover multiplicity. Omitting it merely changes the stated
canonical normalization, but not the sign; it should not be mixed between
reports. With the declared kappa5=1, the integrand has coefficients 1 and 6.
Normalize Q_c=sqrt(N) Q. Report the separation coupling as
[-2 integral a psi dz]/sqrt(N), together with the normalization convention.
There is no inverse S in (21), so its sign and regularity survive the scalar
minimum. Positive N and negative mu mean a tachyonic mode rather than a ghost.

This kinetic calculation independently reproduces the derivative terms of
Kofman–Martin–Peloso's quadratic action, with M^3=1/kappa5^2, their normal
metric potential=-2psi, and their interval-cover convention. Their published
background is flat; the extension of the derivative coefficient to curved
gamma here follows from the displayed action expansion, not from assuming
their entire flat master operator applies.
[Primary text, equations (5), (18)](https://arxiv.org/html/hep-ph/0401189).

## 6. Physical de Sitter criterion and a decisive exact control

For k>0 put H_dS=sqrt(k). In the flat expanding chart, a Fourier amplitude
q(t) with comoving momentum q_com obeys

\[
 \ddot q+3H_{dS}\dot q+
                [q_{com}^2e^{-2H_{dS}t}+\mu]q=0.             \tag{22}
\]

The late-time homogeneous exponents are

\[
 r_\pm=\frac{-3\sqrt{k}\pm\sqrt{9k-4\mu}}2.                 \tag{23}
\]

Every resolved mu<0 gives r_+>0. A positive lambda does not establish stability:
the threshold is lambda=4k, not lambda=0. Mu=0 is marginal at this order and
does not demonstrate nonlinear stability. At wall i, proper-time rates and
mass squared are r_i=r/a_i and mu_i=mu/a_i^2; the dimensionless r/H_dS is
unchanged. A physical scalar instability is enough to end the candidate test,
but it identifies neither the nonlinear endpoint nor the G10 future.

An exact control is the scalar-free dS-sliced AdS interval. Let zeta=z-z_a,
Phi=0, v_i=0, choose the endpoint tensions from (4), and take

\[
 a(\zeta)=\frac{\sqrt{k}}{\sinh[\operatorname{arsinh}\sqrt{k}
                                          +\sqrt{k}\zeta]},\qquad k>0.
\]

Then a_a=1 and the genuine radion solution is

\[
         f=p=0,\qquad \psi=a^{-2},\qquad \mu=-4k.           \tag{24}
\]

It satisfies all three bulk equations, the constraint and both finite-gamma
wall conditions. It has positive finite N=12 integral a^{-1}dz, nonzero
delta D/Q=-2 integral a^{-1}dz and r_+=sqrt(k). Its flat k=0 limit is the
massless RS radion with a=1/(1+zeta). These are deliberately changed analytic
control parameters, not a replacement of the fixed candidate. They test the
mass shift, normal orientation, kinetic coefficient and separation observable
together. Because S vanishes identically in this control, initialization must
use its known constraint subspace rather than an S-divided formula.

## 7. What a numerical test must still establish

Before scientific evaluation the parent freezes the actual implementation,
input identities and numerical thresholds. The following are formulation-level
requirements, not additional unbounded work:

- Preserve finite gamma and the fixed action parameters. Authenticate the
  retained background and distinguish direct metric jets from auxiliary fields.
- Verify independent bulk, wall and C residuals, including through the turn.
  Approximate-background errors can source C; a small solver local error alone
  does not establish a physical eigenpair.
- Resolve a candidate root against integration/resolution and background
  representation changes, with a second formulation or independent residual
  reconstruction. A static BVP Jacobian is not this fluctuation operator.
- Measure N and the properly normalized separation overlap. Retain exceptional
  harmonic qualifications without discarding the physical mu=-4k sector.
- State the mass sign using mu, a measured numerical sensitivity rather than a
  rigorous enclosure, and the actual arithmetic of the solver. Binary128 NumPy
  support does not change a binary64 SciPy solve.
- A finite search with no negative root establishes only its declared search
  coverage unless a completeness argument is supplied. One resolved negative
  physical root is already a decisive instability result.

No scientific eigenvalue or evolution was evaluated for this independent
formulation note. The local exact check was the symbolic identity (9).

## 8. Inspected sources and claim boundary

The model and background sources below were read directly. Paths are relative
to the research root `collapse-horizon-research/`.

| Inspected source | SHA-256 |
|---|---|
| `source-snapshot/brane-horizon-phase-structure/MODEL_V1.md` | `4077686eb06ea8eea23d11b059336db877d8466f34b710f0fa416e116d343dc9` |
| `source-snapshot/brane-horizon-phase-structure/notes/42_undivided_scalar_radion_audit.md` | `6f51c7905f35b53fb090d9f8491493c5a6ff86422f6cfd169fd439e08c75dabe` |
| `branches/02-event-horizon/capture-to-model-2026-09-12/static-background-successor/PROSPECTIVE_BVP_DESIGN.md` | `5f73207bbab64947e5bf30de285c3bee7b221c5d97214f08d46ec1857208c55a` |
| `branches/02-event-horizon/capture-to-model-2026-09-12/static-background-successor/FLAT_BASE_OBSTRUCTION.md` | `d225248a43479ad849f0421626a203347b3e9d51cc0ff98497ba95f11a041100` |
| `branches/02-event-horizon/capture-to-model-2026-09-12/static-background-successor/analysis/CURVED_STATIC_SUCCESSOR_RESULT.md` | `8e6f546bfc9945631f5107ee975e6e280bab3a50e072f494ef95686aadb5beae` |

The historical undivided audit is a methodological precedent only. Its flat
background conclusions cannot be transferred to this curved candidate, and its
old static antecedent is superseded by the separately established distinction
between the initial-data selector and a true static solution. No original
source or historical record was changed.

Primary references consulted in full relevant passages:

1. A. V. Frolov and L. Kofman, *Can Inflating Braneworlds be Stabilized?*,
   Physical Review D **69**, 044021 (2004),
   [doi:10.1103/PhysRevD.69.044021](https://doi.org/10.1103/PhysRevD.69.044021),
   [hep-th/0309002](https://arxiv.org/html/hep-th/0309002), equations (3)–(15).
2. J. Lesgourgues and L. Sorbo, *Goldberger-Wise variations: stabilizing brane
   models with a bulk scalar*, Physical Review D **69**, 084010 (2004),
   [doi:10.1103/PhysRevD.69.084010](https://doi.org/10.1103/PhysRevD.69.084010),
   [hep-th/0310007](https://arxiv.org/html/hep-th/0310007), equations (7)–(17), (44).
3. L. Kofman, J. Martin and M. Peloso, *Exact identification of the radion and
   its coupling to the observable sector*, Physical Review D **70**, 085015
   (2004), [doi:10.1103/PhysRevD.70.085015](https://doi.org/10.1103/PhysRevD.70.085015),
   [hep-ph/0401189](https://arxiv.org/html/hep-ph/0401189), equations (5), (9),
   (12), (18), including the action's cover normalization.

The task is a specified coupled scalar-sector test of one curved numerical
background. It establishes no tensor-sector health, nonlinear stability,
donor-source energy balance, baby-universe production, halo, event horizon,
source ownership, or G10 attractor merely by completing this formulation.
