# D2 separation and lineage bridge design

## Question

Does the positive-curvature exterior belong to the same physical development
as the collapse problem whose initial physical brane separation is about
0.99964, while the retained curved static candidate has separation about
1.99757?

This question must be split. A same-action static solution at the original
separation is the cheap branch. A dynamical radion transition is a different,
substantially harder branch. Failure of the first does not exclude the second.

## D2A — fixed-separation static discriminator

Use the exact proper-distance initial map from the validated-shooting design.
For each lower scalar value \(a\), the lower wall conditions and constraint
fix \(H_0,S_0,k\), and hence a unique local IVP. At the frozen target
separation \(D_0\), evaluate both upper-wall residuals

\[
 G_D(a)=H(D_0,a)-\tau_b(\Phi(D_0,a))/6,
\]

\[
 h_D(a)=S(D_0,a)+\gamma[\Phi(D_0,a)-v_1]/2.
\]

A fixed-separation static solution requires the **same** \(a\) to make both
zero. One residual changing sign is insufficient.

### Existing archive diagnostic

The already sealed level-0 first-detected-Israel-crossing scan contains 33
admitted events with \(D\) ranging from 0.3606734632 to 1.9652670037. Thus it
does pass through the neighborhood of the collapse separation without a new
solve. The two retained samples bracketing
\(D_0\approx0.9996389747\) are

| \(D\) | \(a\) | upper scalar residual |
|---:|---:|---:|
| 0.9725796695 | 0.0985760625 | -0.8048089310 |
| 1.0631544941 | 0.0987190196 | -0.7927233932 |

The residual is negative and order unity on both sides, while the eventual
curved candidate reaches zero only near \(D=1.99757\). This strongly
disfavors a fixed-separation solution on the sampled first-crossing branch.
It is not a proof: the scan does not exclude a sharp unresolved excursion, an
earlier tangential crossing, or a separate branch.

The stored profiles give a concrete reason for this mismatch. At
\(D=0.97258\), the scalar reaches the upper-Israel event with
\(\Phi_b=0.03404\) and actual \(S_b=-0.24041\), while the upper scalar
condition requires \(S_b=+0.56440\). At \(D=1.06315\), the corresponding
values are \(S_b=-0.23394\) and required \(S_b=+0.55878\). The successful
branch has enough proper distance for the scalar to turn: its single sampled
\(S=0\) crossing is near \(s=1.68919\), after which it arrives at
\(D=1.99757\) with \(S_b\approx+0.021615\). Thus the factor-of-two separation
is associated with satisfying the upper scalar Robin condition after a scalar
turnaround, not with a small solver-tolerance correction. These are
authenticated finite-resolution diagnostics, not interval enclosures.

An analytic flux bound sharpens this observation. For the fixed parameters,
every launch with \(a<0.0989750001\) remains \(S<0\) for all finite proper
distance and can never execute the Robin-required turnaround. Both
target-bracketing samples lie well below this exact-rational threshold, while
the successful long candidate lies above it. D2A can therefore aim to prove
that every upper-Israel solution at \(D_0\) lies below the threshold, instead
of enclosing the entire later-time scalar trajectory in detail.

### Numerical pilot

1. Bind the exact collapse separation and all dyadic action/wall parameters.
2. Continue the known curved branch in \(a\) and/or a pseudo-arclength
   parameter while recording \((D,G,h,k,\min\psi)\).
3. Search the admissible positive-warp range for approach to \(D_0\), retaining
   folds and failed states rather than joining across them.
4. Report the two-dimensional residual norm only as a locator. With every wall
   parameter and \(D_0\) fixed, there is only one shooting parameter for two
   upper residuals. Introducing a second adjustable physical parameter would
   change the question and cannot qualify the fixed-parameter problem.

### Rigorous outcome

The cheapest rigorous result is exclusion: validated-integrate to \(D_0\),
prove all zeros of \(G_D\) lie below the analytic no-turn threshold, and
enclose \(\Phi_b<v_1\). Then the upper Robin condition demands \(S_b>0\)
while the flux bound gives \(S_b<0\). A more general fallback is to cover the
declared admissible \(a\)-range with validated ODE boxes and prove that at
least one of \(G_D,h_D\) excludes zero on every box. If a small box leaves
both residuals unresolved, classify it as FIXED-SEPARATION-UNRESOLVED;
proximity of the two-dimensional residual to zero is not existence.

A positive fixed-separation existence result would additionally require an
analytic dependence reducing the two upper equations to one, or a rigorous
existence theorem for the overdetermined BVP itself. A square interval-Newton
solve obtained by freeing a wall parameter, the separation, or another
physical datum would answer a different problem.

## D2B — dynamical radion bridge

Attempt this only after complete joint initial data are admitted. The current
sibling result explicitly has joint_initial_data_admitted=false and ran no
evolution.

A dynamical bridge must evolve the brane-to-brane proper distance and the
exterior fields in one constraint-compatible initial-boundary problem. It
must demonstrate, rather than assume:

- preserved wall potentials and corner conditions;
- controlled Hamiltonian, momentum and scalar constraints;
- a gauge-invariant or geometrically defined separation observable;
- approach to the D1-enclosed curved branch in a norm controlling the full
  worldtube remainder \(\mathcal E\);
- two evolution resolutions and two independently solved outer domains; and
- an analytic or enclosed stability estimate before any all-future claim.

Reaching \(D\approx1.99757\) at one finite time is not a same-development
proof. A fit of the separation alone is also insufficient because many bulk
profiles share the same proper distance.

## Decision logic

- D1 pass + D2A rigorous existence: a same-action static target exists at the
  collapse separation; design compatible initial data around it before
  evolution.
- D1 pass + D2A rigorous exclusion: the original-separation static route is
  closed, but D2B remains a distinct radion-transition hypothesis.
- D1 pass + D2B pass: the conditional Kottler exterior becomes a justified
  target for the perturbative worldtube and one-bracket calculation.
- D1 failure or inconclusive: do not use the Kottler family as physical
  authority, regardless of D2 locator behavior.

## Cost ordering

D2A is the first separation test because it reuses the five-state shooting
system and can be scanned cheaply. D2B requires solving the already-failed
coupled initial-data gate and then a new evolution, so it should not be used as
a rescue calculation for an unresolved static search.
