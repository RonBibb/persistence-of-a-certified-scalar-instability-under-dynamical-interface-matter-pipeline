# Introduction draft

Warped five-dimensional models with a bulk scalar turn the separation between
two boundary branes into part of the field problem rather than an arbitrary
coordinate interval. The bulk equations, scalar boundary conditions, wall
tensions, and induced four-dimensional curvature must all be compatible with
one another. This makes a simple modeling choice—prescribing both wall data and
their proper separation—potentially overdetermining. When a numerical shooting
calculation fails at that prescribed separation, however, the failure alone
does not distinguish a genuine incompatibility from a missed root, an
incorrect junction convention, or insufficient numerical resolution.

Bulk-scalar stabilization and scalar-selected inter-brane distance are well
established. Goldberger and Wise introduced the canonical modulus-stabilization
mechanism, while DeWolfe, Freedman, Gubser, and Karch and Kanti, Olive, and
Pospelov developed nonlinear scalar--gravity constructions in which the wall
data, spacing, and four-dimensional curvature are linked. Curved scalar branes,
phase-space descriptions of the wall junction conditions, numerical shooting,
multiple or absent static configurations, and dynamical restructuring have
also been studied [Goldberger--Wise; DeWolfe et al.; Kanti--Olive--Pospelov;
Felder--Frolov--Kofman; Martin et al.]. The question addressed here is therefore
not whether a bulk scalar can select a distance, whether curved branes exist,
or whether a shooting problem can have more than one solution.

We ask a narrower compatibility question for one fixed source-pinned model.
The five-dimensional Einstein--AdS--scalar action, two quadratic wall
potentials, junction orientations, and six exact binary64 parameter literals
are held fixed. We compare two boundary placements within the same reduced
maximally symmetric static family. In the first, the upper wall is placed at
the first transverse zero of its Israel residual and the remaining scalar wall
condition becomes a one-parameter shooting equation. In the second, the upper
wall is fixed at the source-prescribed proper separation

\[
 D_0=0.9996389747145851,
\]

and both upper-wall residuals must vanish there. The distinction is physical,
not a reparametrization: it asks whether the same action and wall potentials
support the positive-curvature branch at the originally prescribed distance.

Our main result is a paired computer-assisted theorem. Validated interval
integration and interval Newton prove that the first-event problem has exactly
one root in the frozen launch interval and that its first upper-wall event lies
in

\[
 D\in[1.99749755859375,1.99761962890625].
\]

An independent Taylor--Picard producer reproduces the root and encloses the
positive curvature, transverse event, warp factor, conformal length, first
integral, and both wall identities. For the fixed-distance problem, an exact
adaptive interval cover resolves all 693 terminal launch boxes over the full
declared interval `0<=a<=v0`. Every box is excluded either by negative
curvature or by at least one upper-wall residual being separated from zero;
there are no unresolved boxes. Along the positive-curvature route the residual
vector obeys `max(|G|,|h|)>0.0077`, with a directly rederived minimum boxwise
lower bound of `0.0077281481292751026` in this infinity norm.

The conjunction matters. A certified root near `D=1.9975` by itself would not
show that the prescribed separation is impossible, and a failed fixed-distance
search would not show that the model possesses the desired curved branch
elsewhere. Together, existence at the first-event placement and exhaustive
exclusion at `D0` establish that the separation mismatch is a property of the
declared reduced family rather than an ordinary root-finder miss. Exact
interval arithmetic gives

\[
 D-D_0\in[0.9978585838791649,0.9979806541916649],
 \qquad
 \frac{D}{D_0}\in[1.9982189661663317,1.9983410805652175].
\]

The methodological contribution is likewise specific. The variable-separation
certificate is reproduced by two independently implemented interval-ODE
producers, while the fixed-distance claim is supported by a gap-free exact
cover rather than a parameter scan. The action-to-IVP reduction, doubled-cover
junction factors, constraint propagation, coordinate identities, and exact
separation contrast are independently checked. These controls address the
failure modes that would invalidate the paired inference; the number of checks
is not itself the scientific result.

To our knowledge, the exact pairing of a validated locally unique first-event
solution with exhaustive fixed-separation exclusion has not previously been
reported for one fixed two-wall Einstein--scalar model. This priority statement
is intentionally bounded. Prior work already contains the qualitative
phase-space geometry, shooting construction, multiplicity or nonexistence of
static solutions, and dynamical behavior. The present result instead converts
one source-specific compatibility problem from an ambiguous numerical failure
into a machine-checkable existence-and-exclusion theorem. It thereby isolates
parameter robustness, stability, and dynamical selection as distinct questions
rather than interpretations of the failed fixed-distance solve.

The theorem is static and finite in scope. Local uniqueness holds only on the
certified first-event root interval; fixed-distance exclusion holds only at
the exact `D0`, for positive curvature, and over the exact declared launch
range. We do not establish parameter robustness, stability, radion motion,
dynamical selection, collapse, a marginally trapped tube, an event horizon, or
a baby universe. Those questions require separately admitted Cauchy data and
evolution. The remainder of the article defines the fixed model and its two
reductions, states the paired theorem, presents the independent existence and
exhaustive exclusion certificates, and closes with this boundary of inference.

## Citation keys to resolve in the manuscript bibliography

- Goldberger and Wise, [arXiv:hep-ph/9907447](https://arxiv.org/abs/hep-ph/9907447).
- DeWolfe, Freedman, Gubser, and Karch,
  [arXiv:hep-th/9909134](https://arxiv.org/abs/hep-th/9909134).
- Kanti, Olive, and Pospelov,
  [arXiv:hep-ph/0002229](https://arxiv.org/abs/hep-ph/0002229).
- Felder, Frolov, and Kofman,
  [arXiv:hep-th/0112165](https://arxiv.org/abs/hep-th/0112165).
- Martin, Felder, Frolov, Peloso, and Kofman,
  [arXiv:hep-th/0309001](https://arxiv.org/abs/hep-th/0309001).

The links above are drafting aids, not final bibliography formatting.
