# Exact bridge required from the static theorem to the initial-data line

## Present conclusion

The D1/D2A theorem and the coupled initial-data work share an action family,
wall potentials, and parameter literals. They do **not** yet share a Cauchy
development. The static root lives at a different proper and conformal wall
separation from the original collapse domain, and its positive-curvature
four-dimensional base carries nontrivial slice geometry. A bridge therefore
requires an explicit initial-data embedding and a new constrained evolution;
shared ancestry or terminology is insufficient.

## 1. The exact background-to-Cauchy map

Let the independently certified static solution be

\[
ds_5^2=e^{2A(s)}\gamma_k+ds^2,\qquad \Phi=\Phi(s),
\qquad 0\leq s\leq D,
\]

with `k>0`. One explicit de Sitter chart is

\[
\gamma_k=-dt^2+e^{2\sqrt{k}t}
(dr^2+r^2d\Omega_2^2).
\]

On its `t=0` slice, in the ADM sign convention
`K_ij=-(2 alpha)^{-1} partial_t h_ij`, the fields are

\[
\begin{aligned}
\alpha&=e^A,\qquad \beta^i=0,\\
h_{ss}&=1,\qquad h_{ab}=e^{2A}\bar h_{ab},\\
K_{ss}&=0,\qquad K_{ab}=-\sqrt{k}\,e^{-A}h_{ab},\\
\Phi&=\Phi(s),\qquad \Pi_\Phi=0,\\
\chi&=0,\qquad \Pi_\chi=0.
\end{aligned}
\]

Here `a,b` are the three noncompact spatial directions. The production code's
extrinsic-curvature sign must be applied explicitly when implementing this
map. The important invariant fact is that a flat-slicing de Sitter embedding
is **not time symmetric**: setting `K_ij=0` changes the solution.

Alternatively, a global de Sitter slice can have `K_ij=0` at its symmetry
time, but its noncompact spatial geometry is replaced by a three-sphere. A
static-patch slice has different lapse and a cosmological coordinate horizon.
Neither alternative is silently equivalent to the original radial collapse
domain. The chart, radial topology, lapse, outer boundary, and extrinsic
curvature must be frozen together.

Introduce the conformal coordinate

\[
z(s)=z_a+\int_0^s e^{-A(\sigma)}d\sigma,
\qquad L=z(D)-z_a,
\]

or normalized coordinate `u=(z-z_a)/L`. This supplies the code-level profiles
`A(u)`, `Phi(u)`, their normal derivatives, the lapse, spatial metric, and
extrinsic curvature. It also makes clear that `L` and the proper separation
`D` are different quantities.

## 2. Why the original collapse slice is not already this map

The D1 root selects `D` near `1.9975`; D2A excludes the corresponding
positive-curvature static solution at the original
`D0=0.9996389747145851` over the declared launch interval. Consequently:

- the D1 background cannot be inserted on the old interval by a coordinate
  relabeling that preserves proper geometry;
- fixing the old wall locations while importing the D1 profiles violates the
  certified wall problem;
- a change from `D0` to the D1 value is a physical radion/separation history,
  not gauge by default; and
- the current time-symmetric initial-data ansatz is not the flat-slicing D1
  Cauchy slice because its `K_ij` differs.

The current coupled initial-data branch has not supplied an alternative
bridge. Its best construction closes selected equations at finite nodes but
fails joint admission through large interior/off-grid Hamiltonian residuals,
unresolved boundary functions, and remaining metric-corner conditions.

## 3. The commutative test that would constitute a bridge

A defensible bridge needs the following objects and equalities.

### A. Static-equilibrium embedding

1. Convert the certified `A(s), Phi(s), k, D, L` enclosures to one frozen
   dynamical chart.
2. Construct `h_ij, K_ij, Phi, Pi_Phi, alpha, beta^i` from the equations above.
3. Verify the Hamiltonian and momentum constraints, both physical wall
   junction conditions, scalar wall conditions, all wall-axis/outer corners,
   and the chosen gauge-source identities using one represented field.
4. Evolve the unperturbed data. Gauge-invariant residuals and the proper wall
   separation must remain within a declared refinement envelope. This is an
   equilibrium/code-compatibility test, not stability proof by itself.

### B. Constraint-compatible perturbation family

1. Add a declared collapse-scalar perturbation `chi` and its momentum.
2. Re-solve the complete Hamiltonian and momentum constraints and every wall,
   scalar, gauge, axis, and outer compatibility condition. Superposition is
   not allowed.
3. Preserve the static action and wall parameters. If the perturbation changes
   wall separation, boundary data, or topology, record that as a new family.
4. Establish spatial and temporal convergence of invariant observables on the
   new lineage before importing any MOTS or horizon inference.

### C. Original-separation dynamical bridge

To connect the old `D0` collapse line to D1 rather than merely test dynamics
near D1, one must begin from **admitted** data at `D0` and measure a
gauge-invariant separation history, for example the proper length of the
specified wall-normal geodesic congruence. A bridge requires evidence that

\[
D(t)\longrightarrow D_{\rm D1}
\]

together with convergence of the scalar profile, warp/curvature invariants,
wall data, and extrinsic geometry to the D1 background in one invariantly
defined comparison. A coordinate wall motion or a single separation scalar is
insufficient. The current D2A theorem says this path, if it exists, must be
genuinely time dependent near `D0`.

## 4. Smallest justified sequence

1. **Background embedding gate:** no collapse scalar, no shooting; translate
   the D1 certified background into the evolution variables and evaluate the
   full constraint/wall/gauge system.
2. **Short unperturbed evolution:** only if the embedding gate passes; test
   preservation and formulation compatibility.
3. **Constrained small perturbation:** solve rather than superpose the collapse
   scalar on the D1 background.
4. **Local stability or response:** compare a small amplitude family and
   refinements. This establishes dynamics near D1, not ancestry from `D0`.
5. **Original-lineage bridge:** only after globally admitted `D0` data exist;
   track invariant separation and full geometric convergence.

This order is cheaper and more discriminating than attempting a long evolution
of the currently inadmissible initial-data candidate.

## 5. Claim boundary

The map above specifies prerequisites; it does not establish any of them. A
successful static replay strengthens proof authority for D1 but does not by
itself repair the initial-data branch. Conversely, an admitted Cauchy slice at
`D0` would not imply convergence to D1. Stability, dynamical selection,
event-horizon formation, and baby-universe interpretation remain separate
claims.

