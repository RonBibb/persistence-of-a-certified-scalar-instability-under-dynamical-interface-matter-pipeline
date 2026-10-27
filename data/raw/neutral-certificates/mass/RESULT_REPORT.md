# Central D1 scalar instability certificate

## Outcome and physical meaning

The bounded interval calculation establishes at least one negative scalar-sector
eigenvalue at the exact central D1 static background, with

    -0.00132 < mu_star < -0.00131.

Both independently implemented validated integrations certify the endpoint
signs while retaining the previously certified uncertainty in the background
shooting root and upper-wall position. Their uniform full-mass-interval controls
also establish positive kinetic norm and a nonzero wall-separation response.
The result therefore upgrades the previous central numerical growing-mode
evidence to an interval-certified existence statement within the declared
Einstein–canonical-scalar, pure-potential two-wall model.

Physically, this static solution exists, but is not linearly stable in every
physical scalar direction. There is a growing scalar/radion perturbation with
a genuine separation component. The perturbation's overall sign is arbitrary:
the certificate does not select contraction instead of expansion, and it does
not predict the nonlinear endpoint.

The producer classification is
`NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1`.
The independent post-run review passed: all 288 checkpoint records, 11,808 native
interval roundtrips, 445 hash/file consistency links and all 42 pinned runtime
libraries were verified. Exact signs and full event-time coverage were independently
reconstructed. The norm was also checked using exact rational exponential-series
and remainder bounds. The frozen producer result intentionally retains its
provisional flag; final acceptance is recorded separately in the audit and root
result rather than rewriting the producer record afterward.

## Decisive measurements

Endpoint determinant intervals below are decimal approximations for readability;
the authoritative bounds are exact rational endpoints in `output/RESULT.json`.

| Implementation | mu = -0.00132 | mu = -0.00131 |
| --- | --- | --- |
| Primary polynomial flow | [29.0307960975, 29.0461903671] | [-8.3444467092, -8.3240136128] |
| Independent exponential flow | [29.0307960998, 29.0461904271] | [-8.3444467691, -8.3240135529] |

The signs are strict and the same-endpoint enclosures overlap. For the same
fixed exact background, the upper Robin determinant is continuous in mu.
The intermediate-value argument thus gives an exact zero strictly inside the
negative interval. This is not an extrapolated best-fit eigenvalue or an estimate
of the observed convergence order.

The launch curvature is enclosed approximately by
`[0.00032684133443318, 0.00032684134048499]`; the lower normalization denominator
stays strictly negative. The full `mu+4k` strip stays below zero, with upper bound
approximately `-2.63463804e-6`. The exceptional sector is therefore excluded.
Constraint propagation is regular through the scalar-gradient zero; no division
by that gradient is used.

Across the full mass interval and full domain, both methods certify
`psi_min > 0.99977`. Under `psi(0)=1`, conservative common bounds are

    Z > 0.437,
    -219 < deltaD < -3.994.

These deliberately broad bounds certify positivity and nonzero overlap. They
are not precise amplitude predictions; the prior numerical values near
`Z=321.284` and `deltaD=-53.545` have a different role. Here
`Z=2 integral exp(2W)(f^2+6 psi^2) ds` and
`deltaD=-2 integral psi ds` use the inherited action and gauge normalization.

## Why this covers the exact background

The central background input is the exact certified Newton image

    [456607025194779413/4611686018427387904,
     114151756532473697/1152921504606846976],

not its floating midpoint. The upper-wall location retains the entire exact
interval `[32727/16384, 32729/16384]`. Each implementation's event evaluation
covers both cells intersecting that interval and all intervening times. Its
determinant bounds therefore include the actual wall event, not merely two
sampled grid points. All six action parameters preserve the predecessor's
exact binary64 rational meanings.

The primary engine evolves an additional `E=exp(-W)` variable with a polynomial
coefficient recurrence. The independent engine evaluates `exp(-2W)` using its
own exponential/convolution recurrence. Both use outward Arb arithmetic at
768 bits, strict Picard cell inclusion, and Taylor order five remainder bounds.
They share the pinned Arb library and checkpoint runner; they are independent
equation implementations, not independent arithmetic-library stacks.

## Execution and preserved technical failures

The successful Linux run started at `2026-10-05T17:31:54.643900+00:00` and
completed at `2026-10-05T17:32:45.519223+00:00`, taking 50.8758 seconds.
All six tasks completed: three primary tasks with 8,183 cells each, and three
independent tasks with 16,365 cells each, totaling 73,644 validated cells.
Every recorded Picard inclusion succeeded on its first iteration. This is
execution information, not a substitute for the endpoint/overlap argument.

Two synthetic preflights identified radius-serialization and zero-straddling
interval-power issues. Both were corrected before the first source freeze,
and their failed directories and explanation remain in the original capsule.
Exact recovery is for the explicitly outward-canonicalized checkpoint algorithm;
it is not a universal lossless-serialization claim about arbitrary raw Arb balls.

The original frozen physical attempt then stopped at its first checkpoint
because the exact ceiling returned an `fmpz` cell count that JSON could not
serialize. It produced no terminal determinant. Its sources, freeze and
`FAILURE.json` remain untouched in the predecessor capsule. R1 converts that
already-integer count to Python `int` and includes the production count in both
analytic fresh-process recovery controls. The two interval engines, contract,
scientific intervals and all gates are byte-identical across that repair.

## What remains open and the next bounded question

This certificate concerns one central static background and one physical scalar
mode. It does not prove that the eigenvalue is unique or the lowest, does not
classify the complete spectrum, and does not extend the instability theorem to
the continuous parameter neighborhood. The earlier nine-point scan remains
numerical evidence outside this central theorem.

Nor does it authorize causal evolution, establish globally admissible initial
data, determine nonlinear contraction/expansion, identify an event horizon, or
merge this branch with P16 or the original horizon-tube residual calculation.
No manuscript, external record or earlier sealed parent was modified.

The next bounded question is whether the same instability certificate extends
over the already-certified static parameter neighborhood. That would test
robustness rather than a new physical model. It is a prospective successor,
not a calculation launched as part of this packet.

## Principal records

- `output/RESULT.json`: exact rational enclosures and all six task outcomes;
  SHA-256 `1e14fdf03724f7249aeb5a8177e9671e917e7ea323fbaefe11fddb8d5be16ae5`.
- `output/TERMINAL.json`: producer terminal integrity;
  SHA-256 `834b719f156287d1c393991461501e25041b87e6920afe203ce5045ba24cb556`.
- `BINDINGS.json`: source, input and runtime guard;
  SHA-256 `fca1b49a652afc1832e61e31e5e8c47dc86d63144de791211c89372f55a82e00`.
- `INDEPENDENT_PROOF_AUDIT.md`, `PREFLIGHT_REVIEW.md` and
  `TECHNICAL_REPAIR_REVIEW.md`: mathematical and prospective admission reviews.
- `POSTRUN_REVIEW.md` and `INDEPENDENT_AUDIT.json`: independent final verdict.
- `RESULT.json`, `TERMINAL.json` and `MANIFEST.json`: final packet acceptance and
  whole-file inventory, published only after independent audit.

The read-only audit can be rerun on Linux using the pinned precision Python,
`PYTHONDONTWRITEBYTECODE=1`, and
`PYTHONPATH=/home/parallels/research-runs/cap-interval-arb-2026-09-12`.
Invoke `postrun_audit.py` with the Linux-mounted absolute path of this packet;
it writes its new receipt to stdout and does not rerun a physical IVP or alter
any sealed file.
