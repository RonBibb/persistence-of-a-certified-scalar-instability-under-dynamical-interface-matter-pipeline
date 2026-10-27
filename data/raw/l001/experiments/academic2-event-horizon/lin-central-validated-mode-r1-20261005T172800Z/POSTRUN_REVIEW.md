# Independent post-run review — central validated mode R1

Disposition: PASS. Independently supported classification:
`NEGATIVE_SCALAR_RADION_MODE_CERTIFIED_AT_CENTRAL_D1`.

For the same exact central D1 static background and declared two-wall action,
there exists a nontrivial positive-norm scalar eigenmode with physical mass
squared strictly between the exact decimals -0.00132 and -0.00131. It has a
nonzero inter-wall separation response. This upgrades the central negative-mode
existence claim from numerical qualification to an interval-validated result,
conditional on the previously audited action/gauge/boundary formulation and
the authenticated static existence certificate.

## Decisive mathematical evidence

All six prospectively fixed integrations completed. Each primary task accepted
8183 cells and each independent task 16365 cells, at their unchanged step sizes.
The following displayed bounds are approximate; all sign decisions in the audit
used the stored exact rational endpoints.

| Formulation | F(-0.00132) | F(-0.00131) |
| --- | --- | --- |
| Primary E-variable | [29.0307960975, 29.0461903671] | [-8.3444467092, -8.3240136128] |
| Independent exp(-2W) | [29.0307960998, 29.0461904271] | [-8.3444467691, -8.3240135529] |

Both pairs have strict opposite signs; their same-endpoint enclosures overlap.
Each task covers the complete exact event interval
[32727/16384,32729/16384], with its two cell intersections meeting exactly at
4091/2048. The audit reconstructed these intersections independently, checked
their cell indices, and verified no missing endpoint or gap. The previously
reviewed Taylor range encloses every time in these intersections, not just
sampled values. The actual certified a_star and D_star are held fixed throughout
the intermediate-value argument; the encompassing A-times-D rectangle does not
replace them by independently chosen backgrounds at the two masses.

Every task retained K>0, B0 excluding zero, and the entire mass strip below the
exceptional sector. Numerically, K is enclosed near
[0.000326841334433,0.000326841340485], B0 near
[-0.099942517828,-0.099942489356], and the upper bound of mu+4K is less than
-0.00000263463804. The regular equations, lower-wall launch and exact propagated
constraint contain no division by the scalar gradient. The scalar-gradient turn
therefore introduces no singular matching condition.

Both conditional full-mass-strip tasks also passed. Their global psi lower
bounds exceed 0.99977. Positive finite warp and finite field bounds give a finite
kinetic norm. An independent exact-rational exponential series with a geometric
tail remainder, rather than the producer's norm evaluator, verifies the useful
conservative bounds

    0.4372607382 < Z < 72010.

The independently checked outward separation bounds are approximately
[-218.988067967,-3.994358164] for the primary strip and
[-218.927422533,-3.994093189] for the independent strip. In particular the simple
common enclosing interval [-219,-3.9940] excludes zero rigorously. These are
conservative global-field bounds with psi(0)=1, not estimates of the actual
overlap magnitude. Overall mode sign is arbitrary: nonzero separation response
does not predict contraction rather than expansion.

## Integrity, recovery and independent audit

The terminal integration finished at 2026-10-05T17:32:45.519223+00:00, reporting
50.8758 seconds. The read-only audit did not perform any new physical IVP,
shooting, parameter scan or source change. It independently derived the final
classification from exact stored bounds and checked:

- All 288 declared checkpoint positions, canonical-content digests, guards,
  committed-task prefixes, completion states and the final latest pointer.
- 11,808 native Arb midpoint/radius instances restored exactly to their stored
  constructor-stable pairs under the pinned runtime.
- 445 file/digest consistency checks, including 42 runtime libraries, the
  Python executable, final source-bound preflight, input and review bindings,
  six task receipts, terminal linkage and all 82 files of the prior MP manifest.
- All 443 distinct checked files remained unchanged through the audit.
- Exact six-parameter identity, static root/event authority, fixed scientific
  configuration and exact sign/sector/separation inequalities.

The source-level Taylor/Picard and action/formulation reviews remain essential
parts of this computer-assisted result; checkpoint hashes alone are not a
mathematical proof. The audit checks the resulting evidence without duplicating
the already completed independent physical formulation.

The original attempt remains `TECHNICAL_INCOMPLETE`: its fmpz JSON failure at
the first checkpoint supplies no spectral conclusion. R1 changed only exact
integer metadata serialization and related control/provenance coverage. Neither
interval engine nor the scientific contract changed. The pre-freeze radius
canonicalization and generic-power findings remain documented; no frozen source
was repaired in place and no gate was relaxed.

## Claim boundary and evidence anchors

This is an existence certificate for at least one negative scalar mode with a
separation component at the central exact static background. It is not a
uniqueness or lowest-mode certificate, a complete spectrum, or a rigorous
parameter-neighborhood theorem. The prior nine-point persistence result remains
numerical. It proves no nonlinear fate, causal evolution, global initial data,
event horizon, universe formation or P16 identification. No remaining blocker
was identified within the declared central linear problem.

- R1 freeze guard: `fca1b49a652afc1832e61e31e5e8c47dc86d63144de791211c89372f55a82e00`.
- Producer output RESULT: `1e14fdf03724f7249aeb5a8177e9671e917e7ea323fbaefe11fddb8d5be16ae5`.
- Producer TERMINAL: `834b719f156287d1c393991461501e25041b87e6920afe203ce5045ba24cb556`.
- Read-only audit source: `9d2334aee18c7085036639858feff1f3a962517040ba3f1258e9ee3fe776be84`.
- INDEPENDENT_AUDIT.json: `9513410d036e1577156ab5f1febaa6b6ed44ff79f776f85971ed443e32fe3e85`.

The producer's provisional flag remains unchanged as execution provenance; this
separate independent review supplies the required post-run qualification.
