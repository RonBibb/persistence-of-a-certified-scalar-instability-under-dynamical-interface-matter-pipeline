# D1 raw-GH and bounded-response qualification contract

## Question

Can the unchanged production generalized-harmonic (GH) acceleration satisfy
the already declared two-consecutive-level refinement gate for the certified
D1 background, and, only if it does, does the equilibrium-preserving
formulation give a finite, nonzero, bounded short-time response to one
explicit physical scalar perturbation?

This packet closes the pending raw-GH gate left by the immediately preceding
well-balanced packet.  It does not change the physical solution, production
GH operator, source, wall or outer closure, stencil, thresholds, or prior
results.

## Authority

The packet binds the frozen D1 Cauchy source, curvature/wall/gauge/ADM
well-balancing sources, the full-GH predecessor source and result, its
independent integrity audit, and its post-run contract audit.  Every digest
must match before evaluation.  The representative root and profile are
reconstructed exactly as in the predecessor.

## Stage R: unchanged raw-GH ladder extension

- Keep `N_r=241`, stencil width `7`, the D1 geometric source, the production
  `NativeRegularSO3RHS`, and the legacy wall-axis-outer closure unchanged.
- Recompute `N_x=257` as an anchor.  Its complete raw-GH record must equal the
  predecessor's sealed `257 x 241` record exactly.
- Add two prospectively declared levels: `N_x=385` and `N_x=513`.
- Combine the authenticated predecessor levels
  `N_x=(65,97,129,193)` with the recomputed anchor and the two new levels.

The raw-GH gate passes only if:

1. every level is finite;
2. the maximum normalized acceleration decreases strictly at every level;
3. the final observed order lies in `[2,6]`;
4. the finest maximum is at most `1e-4`; and
5. the final two levels both pass `1e-4`.

No extrapolated value counts.  If the ladder fails or becomes nonmonotone,
the perturbation stage is not run; the component records are used to localize
the first nonconvergent field.

## Conditional Stage P: physical scalar perturbation

Stage P is authorized only if every Stage R gate passes.

Use the admitted D1 equilibrium-preserving full-GH formulation on the frozen
`97 x 181` grid.  Add to the physical scalar position field `Phi` the smooth
perturbation

`delta Phi = 1e-6 sin^4(pi (x-1)/(e-1)) B(r)`,

where `B(r)=(1-(r/4)^2)^4` for `0<=r<4` and `B(r)=0` for `r>=4`.  Set the two
compact-wall rows exactly to zero.  The perturbation is even at the axis,
vanishes with sufficient order at its radial support boundary, leaves the
outer boundary unchanged, and changes no metric or initial velocity.

Evolve eight explicit-midpoint steps with `dt=0.000125`.  The background
subtraction remains the certified unperturbed D1 equilibrium, and the static
outer reference remains the unperturbed D1 field.  Publish an atomic,
binding-aware checkpoint after every accepted step.

The bounded-response discriminator passes only if:

- the initial well-balanced acceleration is finite, exceeds `1e-12`, and is
  at most `1e-2` in the inherited normalized GH measure;
- every stage is finite and every accepted state preserves positive lapse and
  spatial metric;
- the corrected wall residual is at most `2e-5` and the corrected gauge
  absolute residual is at most `2e-4` at every accepted step;
- the Hamiltonian change relative to the unperturbed background is at most
  the larger of four times its initial value and `5e-6`;
- total normalized departure from the equilibrium is at most `1e-4`;
- the final scalar velocity exceeds `1e-12`, showing that the perturbation
  was dynamically acted on rather than projected away.

The scalar perturbation is a bounded physical-field discriminator, not a
constraint-solved family of perturbed initial data.  Passing shows only a
finite, nonzero, bounded short-time response at the declared amplitude and
resolution.

## Classifications

- `D1_RAW_GH_TWO_LEVEL_GATE_PASS__BOUNDED_SHORT_SCALAR_RESPONSE`
- `D1_RAW_GH_TWO_LEVEL_GATE_PASS__PERTURBED_RESPONSE_BLOCKED`
- `D1_RAW_GH_TWO_LEVEL_GATE_NOT_MET__PERTURBATION_NOT_RUN`
- `D1_RAW_GH_DYNAMICAL_QUALIFICATION_TECHNICAL_INCOMPLETE`

No continuum stability, collapse, P16 continuity, event horizon,
parent-child, or manuscript inference follows.

