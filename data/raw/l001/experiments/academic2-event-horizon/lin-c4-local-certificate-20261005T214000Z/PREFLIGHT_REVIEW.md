# Independent bounded preflight review

Decision: PASS FOR FREEZE AND THE ONE CONTRACTED TWO-ENGINE RUN. No scientific
outcome of the new physical interval flows has yet been evaluated. Quantitative
admission remains conditional on their background/inverse gates and a read-only
independent postrun audit. No tolerance, domain, model, radius or scope change is
recommended.

## Mathematical and implementation review

I read every source identified below and compared the kernels and direct
time-jet implementation with the exact derivation in
`INDEPENDENT_C4_DERIVATION.md`. The direct and flux equations retain the complete
metric response to both prescribed scalar shapes, including the forcing
`-(m2 Phi eta+T eta_s)/3`. The flux factor is `Q=exp(4W)h_s`; its forcing and
curvature factors have the correct signs and powers. The exact fifth-jet shapes
match the final predecessor preparation without fitted coefficients.

The full boundary Jacobian is

    [ d       c0       c1       ]
    [ 0       1        0        ]
    [ beta*d  beta*c0  1+beta*c1 ],  beta=8k exp(-2W) B_upper.

Its exact row reduction gives determinant `d`, but the finite certificate still
propagates all three columns and encloses the full matrix and inverse. This does
not discard off-diagonal backreaction. The independent dual-number time-jet
evaluation uses the original second/fourth time equations, including the lapse
terms. It is independent of the reduced beta formula. At the wall, omitting the
shape forcing when generating metric jets through fifth order is legitimate:
scalar jets zero through fourth order make the first affected metric derivative
the sixth, which is unused. Own fifth jets are imposed exactly at the actual
wall, not obtained by treating the uncertain evaluation coordinate and uncertain
wall location as unrelated in a Hermite endpoint identity.

The independent symbolic identities and nonlinear mixed-Einstein identity
justify the fourth-Israel row and the physical-mode tangent. In the shifted
coordinate `a=A(0)-epsilon`, the full map has no linear epsilon term;
`b0,b1=O(epsilon^2)`. The closed-chart time factor is
`Q''''(0)=mu(mu+6k)`. These are analytic identities, not conclusions drawn from
finite differences or observed numerical amplitude scaling.

The Taylor/Picard driver constructs a strict enclosure of each complete cell
and uses an interval-valued fifth-order remainder. Event evaluation is over
the whole relevant time subinterval, not just an endpoint hull. The exact
inherited root and event intervals remain unchanged. With the contracted
steps, the expected counts are 8,183 and 16,365 cells; each engine intersects
both subintervals partitioned at `4091/2048` within
`[32727/16384,32729/16384]`. The runner explicitly gates complete event coverage,
both determinant signs, direct/reduced row overlap, implementation overlap and
overlap with the inherited exact regularity intervals.

## Complex-domain radius premises checked against code

The quantitative argument is supported by the implementation, conditional on
the explicit runtime premises. In particular:

1. `Bound` propagates absolute values and epsilon-derivative bounds by the
   complex triangle and product rules. Its exponential derivative bound is
   valid on the checked half-unit disc. The exact zero-amplitude correction
   identity then converts a derivative bound into a uniform correction bound
   by integration along the straight complex epsilon segment. No real-only
   sample is used to infer a holomorphic bound.
2. The degree-seven Hermite inverse is computed exactly over rationals.
   Factors `D^(j-p)` are bounded using `1<=D<=3`, and all requested spatial
   derivatives through fifth order are included. Both degree-eleven shapes
   contribute to the perturbation bound. The small factors of the parameter
   radius remain explicit in value-plus-derivative propagation.
3. In the complex Hamiltonian tube, the Jacobian row-sum bound is `527/48<16`.
   The forcing coefficient is `115/6<256`; the lower launch coefficient is
   `70<256`. They account for lapse, scalar value/gradient, curvature and wall
   variations. The initial value `A(0)=epsilon+a` is also covered. The strict
   Gronwall bootstrap proves nonescape, hence analytic dependence on the
   entire declared parameter polydisc, not just its real center.
4. The positive spatial-jet recurrence majorizes the full metric equation and
   all finite jets entering the original time equations. Truncation of second
   time jets after spatial order three retains every coefficient required by
   the first spatial derivative of the fourth-time row. The bound includes
   the complete normalization `exp(5ell-4A)`, which is entire and nonzero.
5. Four-variable Cauchy coefficient counting includes the sum over all three
   unknown-coordinate derivatives. The stated remainder constants 32 and
   128 are conservative for `delta/r0<=1/8`. With the contracted larger
   constants, the contraction bound is `2^-441`, and the self-map remainder
   divided by the unknown-ball radius is `2^-443`.

An independent Linux execution of `majorants.py` used exact rational arithmetic
only and passed. The resulting upper binary exponents were 1048 for mode jets,
1557 for the endpoint-preparation derivative, 22 for the Hermite jet operator,
20 for the fifth-jet shapes, 1578 for the complete prescribed-deviation
coefficient and 92 for the full boundary map. The metric displacement is below
`2^-2412`. These strengthen, but do not replace or tune, the prospectively
declared constants `2^1536`, `2^1800`, `2^512`, `r0=2^-4096` and
`delta=2^-9216`.

The runner now explicitly checks the needed fixed-model bounds (`gamma=20`,
`|m2|<=1`, `|v_i|<=1`, `|lambda_i|<=8`), `D` and `mu` bounds, all background
extrema, positive bounded curvature, the lower launch denominator and the
inverse norm. Failure of a quantitative premise does not erase the separately
specified qualitative classification. No unsupported quantitative premise was
found in this reviewed version.

## Integrity, recovery and analytic controls

The final runner authenticates configuration, source, reviewer artifacts,
runtime and inputs, including the accepted central physical-mode receipt and
the complete predecessor manifests. The exact root/event/model identities are
checked before freeze. The symbolic receipt's status, checks and source hash
are authenticated. Current source inspection and a direct read of the accepted
central receipt confirmed the expected mass interval and classification.

The native interval serializer can widen a radius outward until construction
is stable. It updates the live continuation to exactly that canonicalized
state; decode demands exact midpoint/radius roundtrip. The task's canonical
parameters are used consistently for flow, diagnostics and endpoint evaluation.
Checkpoint digests and immutable task results are guard-bound. A recovered
published task must have the expected engine and COMPLETE status. Changed
guards and terminal/failed restarts are refused; partial files are not selected
as checkpoints. Source changes after this review require a new source-bound
preflight, not silent reuse of this approval.

The reviewed staging control receipt `preflight-control-01/RESULT.json` has
SHA-256 `153b4446212db47ee002d21304c9175f1c62031215fa6da3c10362ea1a3c9215`.
All 14 listed controls pass: both analytic vacuum flows, native restores,
fresh-process next steps, changed-guard refusals, ignored partial files, the
exact independent algebra, two direct dual vacuum rows and rational majorants.
Its ten source hashes match the current files below. It records Python 3.12.3,
python-flint 0.9.0, 768 bits, one arithmetic thread, and no physical model
evaluation. The final isolated packet must rerun/authenticate its own identical
preflight as planned before freezing and starting the physical flows.

The equation representations and exact symbolic derivation are independent,
but both finite flows share Arb, series primitives, shape evaluation, and the
Taylor/Picard driver. The direct dual endpoint checker also shares elementary
convolution. This is disclosed formulation corroboration, not disjoint software
verification.

## Reviewed source hashes

```text
3f9126e050771a7278bb75120ae9568893d68abc6292266bc0c448db2fed4493  CONTRACT.md
17f31b2e9fd0bc703bd3860d224e83013062c05f14c341ca02687764418c42bb  ANALYTIC_RADIUS.md
d2c52ced97bbc78398420f22e40d24b3ee2cf88668a2d00ae0de6f46fdd07603  series.py
57235737768737b5d159f20b60a67174f5099ec3c2513d0bce66b934fbd62973  primary.py
aacbcf5d9c98d4286f78ae9cb206636dd4358297d14c91d44addd2b8e3b4f00f  flux.py
51bdfd2817c31280e9f283004156f6b4fa9eba31dde1f973674cf02710d12cbf  validated.py
3135091e7dd35cbda4cfad77261553aaf11e18bf7f011ba8336ebd0f10014f2d  jetmap.py
e3a97644a5296324bb1e166433a22c3e016f4ebf98aab26261039a9e262e57d5  majorants.py
081e7b0b95b416e987bd873179e41152421ad73529163a33982ac8f8e6c2647e  records.py
7e4f1026d1e0f28ecf215cfe186c6938e3c2bac136b36918f6d4bfc9631c81f0  runner.py
```

The allowed prospective conclusion is the exact local three-variable C4
Cauchy-data family, with radius `2^-9216` only if all quantitative gates pass.
No predecessor finite-amplitude sample lies inside that claimed radius. No
all-order boundary compatibility, time-evolution existence interval, nonlinear
endpoint, horizon or successor computation is admitted by this review.
