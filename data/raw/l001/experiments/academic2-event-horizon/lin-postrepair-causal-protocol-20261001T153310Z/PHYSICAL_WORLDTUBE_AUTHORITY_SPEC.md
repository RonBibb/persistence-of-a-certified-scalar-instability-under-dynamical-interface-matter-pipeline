# Physical worldtube authority specification

## Objective

Qualify one all-future barrier cylinder together with its immediately outer
physical end and visibility portion.  This is a theorem or validated-numerics
interface, not a producer Boolean.

## Identity fields

The authority must bind:

- development, action, gauge and physical-time-orientation IDs;
- physical brane and corner model;
- exterior ID and the exact definition of \(E\);
- quantitative exterior onset \(R_0\);
- cylinder radius \(R>R_0\), topology
  \(S^2\times[z_-,z_+]\), and time extent;
- source, initial/boundary data, runtime and payload hashes; and
- the admitted causal-curve class at the physical boundaries.

For the SO(3)-reduced production model, also bind the symmetry authority that
turns one radial bracket at each compact coordinate \(z\) into a sphere-orbit
bracket.  Without that authority, sampled meridional curves do not cover the
full horizon cross-section.

Changing a domain wall, time interval, exterior onset or boundary model creates
a new authority identity.

## Exterior gate

Supply either an exact exterior/matching construction or validated bounds that
establish an all-future regular product exterior in the same development.  A
sufficient route is the uniform cone control already derived for the warped-KK
end:

\[
\widehat g_{tt}\le-a<0,\qquad
|\widehat g(\partial_t,X)|\le b|X|_{h_0},\qquad
\widehat g(X,X)\le c|X|_{h_0}^2,
\]

with time-independent finite constants and future-directed \(\partial_t\)
tangent to the branes.  This supports the slow-time connectivity argument in
the exterior.  An alternative route must state exactly which causal inclusion
or equality it proves.

Define the end used by the barrier as \(E_R=\{r>R\}\), or another region for
which every cap-to-end curve must cross \(\mathcal T_R\).  A visibility witness
should reach a certified outer portion \(W\subset E_R\).  Reaching the barrier
itself is enough only when the authority includes that boundary in the end or
encloses a causal continuation through it.

If the program's intended exterior \(E\) begins at a different \(R_0<R\),
prove the time-qualified equality
\(J^-(E_R)=J^-(E)\) before transferring the relative-horizon statement.  This
is where the slow-time connectivity argument is used; local timelikeness of
the cylinder does not supply the equality.

## Barrier gate

For every future section of the same cylinder establish:

- timelikeness and regularity;
- compact finite-time slabs;
- orthogonal physical-rim contact;
- separation of the trapped cap from the declared outer end \(E_R\); and
- strictly positive outward future null expansion.

The production-variable target is already explicit.  For orbit radius
\(\mathcal A=r\sqrt B\), compact metric coefficient \(A=g_{zz}\),
\(U_0=g_{tz}\), \(V_0=g_{zr}\), and the outward section normal
\(k=T+\nu\),

\[
\frac{\theta^+}{k^r}=\frac2R+\mathcal E,
\]

where \(\mathcal E\) is the full radial/time/compact derivative combination
defined in the bound predecessor
`ALL_FUTURE_BARRIER_SUFFICIENT_CONDITION.md`.  The authority may use the direct
one-sided estimate

\[
\inf_{t\ge t_C,z}\mathcal E(t,R,z)>-2/R,
\]

or the stronger symmetric budget

\[
\sup_{t\ge t_C,z}\frac R2|\mathcal E(t,R,z)|\le\eta_*<1.
\]

It must retain the compact tilt times warp slope and all time-derivative terms;
cone closeness alone does not bound them.

The common physical development must also satisfy the finite-barrier lemma's
NCC, umbilic-wall and causal-closedness hypotheses.  The cap must have exact or
rigorously enclosed \(\theta^+\le0\) and \(\theta^-\le0\).  Finite-resolution
signs without a continuum enclosure produce only a numerical capture
candidate.

Canonical NCC and pure-tension/umbilic walls do not propagate this sign by
themselves.  The exact contracting warped-FLRW counterfamily in the predecessor
keeps the cylinders timelike while driving \(\theta^+\) through zero.  Any
all-future authority must therefore supply the derivative continuation bound,
not infer it from the matter energy condition.

## Numerical evidence required before analytic promotion

At minimum, sample the same common interior radii in two independently solved
outer domains and two evolution resolutions.  Retain the full derivative
combination entering \(\theta^+\), timelike margin, section metric, area-
variation cross-check and both rim-contact residuals.  Include continuous-time
enclosures between archive knots or label the result discrete-time only.

The earlier R10 sample had favorable positive expansion margins, but it is not
portable authority: O4 left the P407 lineage physically unqualified for causal
inference, and finite sampling did not supply all-future persistence or
moved-domain invariance.

## Allowed outputs

- `NUMERICAL-WORLDTUBE-CANDIDATE`: finite compatible samples pass.
- `FINITE-SLAB-WORLDTUBE-QUALIFIED`: continuum-enclosed signs hold only on a
  stated finite interval.
- `ALL-FUTURE-PHYSICAL-WORLDTUBE-AUTHORITY`: all exterior and barrier gates are
  discharged for the same development.
- `TECHNICALLY-INCOMPLETE`: any required identity, bound or enclosure is
  missing.

Only the all-future outcome can feed the finite-barrier capture theorem.  A
finite-slab outcome can exclude arrival only through that slab and cannot be
silently promoted by a longer numerical trace.
