# D1-specific Cauchy-background admission contract

## Question

Does one representative member of the independently certified D1 root box,
embedded in a single static-patch Cauchy chart and supplied with its own
geometric generalized-harmonic source and outer reference, satisfy the
production initial-data and boundary operators well enough to admit one short
unperturbed preservation evolution?

This is a new D1 background family.  It is not a repair of P16, imports no P16
field or source anchor, and does not vary the static proper separation.

## Frozen physics and chart

- Five-dimensional Einstein--scalar action parameters:
  `Lambda_5=-6`, `kappa_5^2=1`, `m_Phi^2=0.41`.
- Wall data: `gamma=20`, `v0=0.1`, `v1=0.09048374180359596`,
  `lambda_a=5.999990376773895`, `lambda_b=-6.052844277744164`.
- `chi=0` and both scalar momenta vanish.
- D1 is represented on the de Sitter static-patch slice
  `gamma_k=-f dt^2+dr^2/f+r^2 dOmega_2^2`, `f=1-k r^2`.
- The radial domain is `0 <= r <= 10`, strictly inside the static-patch
  coordinate horizon.
- The compact coordinate is `x in [1,e]`, with conformal distance
  `Z=L(x-1)/(e-1)` and `c=L/(e-1)`.
- Lapse `alpha=e^A sqrt(f)`, shift zero, `K_ij=0`, and all initial velocities
  vanish.
- The nine production fields are
  `(0,0,-e^(2A)f,e^(2A),e^(2A)k/f,0,e^(2A)c^2,Phi,0)`.
- The D1-specific natural source/reference is
  `(H_0,H_x,H_r/r)=(0,-3 c e^A A_s,4k/f)`, with zero time trace.  The source,
  target, and outer reference are the same represented D1 field.

The representative root is solved only inside the certified D1 launch box
`[0.09901086489880687,0.09901086689880687]`.  The authoritative interval
result remains the parent; this test does not replace its enclosure.

## Frozen representation

- Production stencil width: 7.
- Admission grids `(N_x,N_r)`: `(65,121)`, `(97,181)`, `(129,241)`.
- Short-evolution grids: `(49,91)`, `(65,121)`.
- All grids are uniform in `x` and `r` on the frozen domains above.
- Root/profile integration uses SciPy DOP853 with `rtol=2e-13`, `atol=2e-15`,
  and maximum proper-distance step `1e-3`.
- Short evolution uses four explicit-midpoint steps of
  `dt=0.000125`, the frozen production legacy wall--axis--outer closure,
  static D1 geometric source, zero normal-wall acceleration datum, and a
  static outer Sommerfeld reference.

## Ordered admission gates

Evaluation is fail-closed in the order below.  A failed phase prevents every
later phase and prevents evolution.  Diagnostics within the failed phase may
be decomposed to localize the failure, but no field, action, grid, threshold,
or boundary condition may be changed.

1. **Authority and continuum profile**
   - every bound parent/source digest matches;
   - the numerical representative root lies inside the certified launch box;
   - both terminal wall equations have absolute residual `<2e-10`;
   - the independent first-integral residual is `<5e-10` everywhere sampled;
   - all arrays are finite and `f`, lapse, and every spatial metric factor are
     strictly positive.
2. **Full constraints**
   - production full-slice Hamiltonian `L_inf <=2e-6` on the finest grid;
   - retained-interior Hamiltonian `L_inf <=5e-7` on the finest grid;
   - finest full and interior values do not exceed their middle-grid values;
   - the ADM momentum constraint is exactly zero to `1e-14`, from the common
     represented `K_ij=Pi_Phi=Pi_chi=0` data.
3. **Walls and axis**
   - the full unbuffered production wall-junction maximum is `<=2e-6` on the
     finest grid and `<=2e-5` on every grid;
   - the finest wall maximum does not exceed the middle-grid maximum;
   - the independent continuum wall residual is `<2e-10`;
   - the regular-axis structural residual is `<=5e-12`.
4. **Gauge source and outer reference**
   - the production GH-constraint maximum absolute and local-relative
     residuals are each `<=5e-5` on the finest grid and do not increase from
     the middle grid;
   - the represented source time trace and mixed time/space trace are
     `<=1e-12`;
   - the natural radial source moment is `<=1e-12`;
   - the initial metric and source Sommerfeld residuals are `<=1e-12`;
   - the outward characteristic speed is strictly positive.
5. **Equilibrium compatibility**
   - the independent ADM metric/scalar acceleration, normalized component by
     component, is `<=5e-5` on the finest grid and nonincreasing from the
     middle grid;
   - the full GH production acceleration is finite, has normalized maximum
     `<=1e-4` on the `(65,121)` grid, and every wall/axis/outer closure
     diagnostic reports finite data.

## Conditional short evolution gates

The evolution is authorized if and only if all admission gates pass.  At each
RK stage and accepted step:

- every field and boundary diagnostic remains finite;
- lapse and spatial metric remain positive and Lorentzian;
- the final Hamiltonian, GH-constraint, and wall residual are no larger than
  four times their initial value or, respectively, `5e-6`, `2e-4`, and
  `2e-5`, whichever floor is larger;
- the component-normalized state change is `<=5e-6`;
- no axis, wall, source, or outer-reference incompatibility appears.

Passing this four-step run means only immediate formulation compatibility and
constraint preservation at the tested resolutions.  It is not a stability
result.

## Classifications and stop rule

- `D1_CAUCHY_BACKGROUND_NOT_ADMITTED__<FIRST_FAILED_GATE>`: stop before
  evolution and report the localized failure.
- `D1_CAUCHY_BACKGROUND_ADMITTED__SHORT_UNPERTURBED_PRESERVATION_PASS`:
  all admission and short-evolution gates pass.
- `D1_CAUCHY_BACKGROUND_ADMITTED__SHORT_EVOLUTION_INCOMPATIBILITY`:
  admission passes but the bounded evolution fails a frozen gate.
- `D1_CAUCHY_BACKGROUND_TECHNICAL_INCOMPLETE`: authentication or execution
  prevents a scientific classification.

No perturbation, static continuation in separation, parent/child mechanism,
causal-horizon inference, or manuscript change is authorized.
