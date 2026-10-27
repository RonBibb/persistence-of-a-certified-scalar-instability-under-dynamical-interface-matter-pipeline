# Validated reduced shooting existence and fixed-separation exclusion

## 1. Scope and model

This statement concerns one fixed, symmetry-reduced, static boundary-value
problem. It is not a theorem about the dynamical collapse spacetime.

Work on the doubled `S1/Z2` cover in units `ell = kappa5 = 1`, with the
canonical five-dimensional Einstein-scalar action

\[
\begin{aligned}
S={}&\frac12\int_{\widetilde{\mathcal M}}\!d^5x\sqrt{-g}
(R-2\Lambda_5)
-\frac12\int_{\widetilde{\mathcal M}}\!d^5x\sqrt{-g}
\left[(\nabla\Phi)^2+m^2\Phi^2\right]\\
&-\sum_{i=a,b}\int_{\Sigma_i}\!d^4x\sqrt{-h_i}\,
\tau_i(\Phi),
\end{aligned}
\]

where `Lambda5 = -6`, the independent collapse scalar is set to `chi = 0`,
and

\[
\tau_a(\Phi)=\lambda_a+\frac{\gamma}{2}(\Phi-v_0)^2,
\qquad
\tau_b(\Phi)=\lambda_b+\frac{\gamma}{2}(\Phi-v_1)^2.
\]

The fixed decimal inputs below are interpreted as their exact binary64
dyadic values:

| parameter | value |
|---|---:|
| `m^2` | `0.41` |
| `gamma` | `20` |
| `v0` | `0.1` |
| `v1` | `0.09048374180359596` |
| `lambda_a` | `5.999990376773895` |
| `lambda_b` | `-6.052844277744164` |

The upper tension and `v1` are independently frozen in the Protocol 394
source. The lower tension is a reconstruction from the unchanged source
constructor's explicit `6-U_a` rule at the bound N65 solution; it is not an
independently archived input. This provenance asymmetry is part of the
assumptions.

Use the warped maximally symmetric ansatz

\[
ds_5^2=e^{2A(s)}\gamma_k+ds^2,
\qquad \operatorname{Ric}(\gamma_k)=3k\gamma_k,
\qquad \Phi=\Phi(s),
\]

where `s` is proper distance from the lower wall. Set `H=A_s` and
`S=Phi_s`. The reduced proper-distance system is

\[
A_s=H,\qquad
H_s=-\frac{S^2}{3}-k e^{-2A},\qquad
\Phi_s=S,\qquad
S_s=m^2\Phi-4HS.
\]

For the shooting value `a = Phi(0)`, the lower-wall conditions and first
integral give

\[
\begin{aligned}
A(0)&=0,\\
H(0)&=-\frac{\lambda_a+\gamma(a-v_0)^2/2}{6},\\
\Phi(0)&=a,\\
S(0)&=\frac{\gamma}{2}(a-v_0),\\
k(a)&=H(0)^2-1-\frac{S(0)^2}{12}+\frac{m^2a^2}{12}.
\end{aligned}
\]

Define the upper-wall residuals

\[
G(s,a)=H(s,a)-\frac{\lambda_b+\gamma(\Phi(s,a)-v_1)^2/2}{6},
\]

\[
h(s,a)=S(s,a)+\frac{\gamma}{2}(\Phi(s,a)-v_1).
\]

When it exists, let `D(a)` be the first transverse zero of `G` and define
the one-dimensional shooting residual `q(a)=h(D(a),a)`.

## 2. Computer-assisted theorem

### Part A — variable-separation existence

For the fixed model above, the declared reduced shooting problem has a unique
zero of `q(a)` in the frozen narrow shooting interval

\[
a\in[0.09901086489880687,\ 0.09901086689880687].
\]

The corresponding first upper-Israel event lies in the proper-distance
interval

\[
\boxed{D\in[1.99749755859375,\ 1.99761962890625]}.
\]

At 32,768 validated steps and 768-bit Arb precision, the interval-Newton
image is

\[
[0.09901086573766466,\ 0.09901086594043548],
\]

with exact rational endpoints

\[
\left[
\frac{456607025194779413}{4611686018427387904},
\frac{114151756532473697}{1152921504606846976}
\right].
\]

It is a strict self-map of the frozen narrow interval and is strictly nested
inside the 16,384-step image. The first event is transverse, with

\[
G_s\in[-0.017908234441645222,-0.017899521804775477],
\]

and the total derivative of the scalar shooting residual excludes zero,

\[
q'(a)\in[124130.66976980511,124218.80928782765].
\]

The sealed classification is
`RIGOROUS_CURVED_BACKGROUND_SHOOTING_ROOT_EXISTS`.

### Part B — original fixed-separation exclusion

Fix instead

\[
D_0=0.9996389747145851
\]

as its exact binary64 dyadic value, and retain all other action, wall,
orientation, launch, and residual definitions above. On the complete declared
launch domain

\[
0\le a\le v_0,
\]

there is no positive-curvature solution satisfying both fixed-distance upper
wall equations

\[
G(D_0,a)=0,\qquad h(D_0,a)=0.
\]

The exact validated cover has 693 terminal boxes and no unresolved boxes:

- 20 boxes are excluded by negative launch curvature;
- 670 boxes have both upper-wall residual intervals separated from zero;
- one box is excluded by the upper-Israel residual alone; and
- two boxes are excluded by the upper-scalar residual alone.

On every box not already excluded by negative curvature,

\[
\boxed{\max\{|G(D_0,a)|,|h(D_0,a)|\}>0.0077}.
\]

The sealed classification is
`FIXED_SEPARATION_POSITIVE_CURVATURE_BRANCH_EXCLUDED_ON_ADMISSIBLE_A_RANGE`.

### Corollary — what the pairing establishes

Within this fixed reduced static family, the positive-curvature shooting root
near `D = 1.9975` cannot be identified with a positive-curvature static
solution at the original separation `D0 = 0.9996389747145851`. The nearly
factor-of-two separation mismatch is therefore not a root-locator tolerance
effect or a missed launch within `0 <= a <= v0` under the declared equations.

## 3. Exact limits of the statement

The result does **not** establish any of the following:

- uniqueness outside the frozen D1 root interval, or uniqueness among more
  general geometries;
- nonexistence of zero- or negative-curvature fixed-separation solutions;
- nonexistence outside `0 <= a <= v0`;
- a result for altered tensions, wall targets, potentials, actions, matter
  fields, orientations, or topologies;
- a dynamical radion transition from `D0` to the D1 separation;
- linear or nonlinear stability of the D1 background;
- selection of the D1 background by the authenticated collapse evolution;
- a same-development bridge to the collapse data;
- a collapse event horizon, future null infinity, or global causal exterior;
- a baby universe, a parent-child spacetime bridge, or the full Lin proposal;
- a continuum theorem for the separate collapse simulation.

The present certificate also has two methodological limits that matter for
publication. The D1 variational formulas and interval inclusions were audited
independently, but the ODE enclosure was not replayed by a producer-independent
implementation. Complete publication-grade enclosures of reconstructed
quantities such as `k`, conformal length, warp positivity/minimum, the first
integral along the full interval, and both wall identities have not yet been
sealed. Accordingly, the strongest present wording is a **computer-assisted
theorem for the declared reduced shooting problem**, not yet a fully
independent certification of every reconstructed five-dimensional geometric
quantity.
