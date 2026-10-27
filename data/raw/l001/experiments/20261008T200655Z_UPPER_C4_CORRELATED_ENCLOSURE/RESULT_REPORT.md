# Correlated upper wall C4 enclosure

The same upper scalar C4 residual at the frozen C6 center now has a locally validated enclosure about **341 times narrower** than the best previously audited enclosure. Retaining the correlations between the source scalar, its derivatives and the canonical boundary correction substantially reduces avoidable interval overestimation. This is an enabling numerical result, not a new physical residual, an existence certificate or a horizon calculation.

## Result

| Precision | Prior audited halfwidth | New halfwidth | New to prior width ratio |
| --- | ---: | ---: | ---: |
| 768 bits | 0.016569496743613854 | 0.000048540053853685095 | 0.002929482687662 |
| 1024 bits | 0.016569496743613854 | 0.00004854005373999826 | 0.002929482680801 |

The comparison uses exact rational endpoints and the fixed intersection of all three previously audited representations. Both new representations pass the local controls; the source Hamiltonian representation supplies the tighter bound. The two precisions overlap. The producer classification is `UPPER_C4_CORRELATED_ENCLOSURE_TIGHTENED`, pending independent admission by Lin Initial.

## What changed mathematically

The source scalar and mode are no longer represented by unrelated high derivative intervals. Their derivatives are rebuilt from the unchanged source equations, exact wall identities and, in the second representation, the positive static Hamiltonian branch. The canonical C7 correction is evaluated from its exact finite-amplitude definition, with both endpoint orientations and Hermite normalizations preserved. No epsilon-series remainder is discarded from an approximate formula.

The integrated metric compensation and its derivative remain uncertain inputs. The upper-wall metric mismatch is retained, not set to zero. The original Hamiltonian spatial recursion, dependent lapse controls and conformal time recursion are imported unchanged. In particular, the target remains the scaled coordinate-time derivative, not a substituted fourth proper-time derivative.

The mean-value calculation uses analytic derivatives over the full primitive rectangle. Its binary midpoint is only an algebraic expansion point; it does not replace the admitted source solution. All inherited source, root, mode, event, integration and constant-representation uncertainties remain enclosed.

## What still sets the width

For the 1024-bit source Hamiltonian representation, the largest contributions to the mean-value radius budget are the upper source metric value W, at 63.84 percent, and the endpoint length D, at 34.80 percent. Upper source scalar P contributes 0.98 percent. These are representation-dependent upper-bound contributions, not measured physical errors and not independent upstream error categories. Their combined prominence suggests that the scalar high-jet dependency problem has largely moved out of the leading position in this representation; it does not identify the remaining physical or integration uncertainty.

## Verification and resources

The frozen source and input guard is `a0b18baf3d93e1bed5439049345604e42251ca386a998a36abef38e3ee9fad48`. The original five residuals reproduced at both precisions before production. A fresh Python process resumed a real prepared-source checkpoint and reproduced the next complete whole-box calculation exactly. Altered case fingerprints were rejected, and an uncommitted partial file did not replace the checkpoint pointer.

All four production cases passed their local controls, and all 57 terminal integrity and accounting checks passed. The cases ran concurrently on Linux CPUs 0–3 with one arithmetic thread each. Each case used about 9.5–10.6 seconds of wall time and a peak resident set of 43,000 KiB. All worker leases were released; no new IVP or successor calculation was launched by this producer.

## Consumer decision

The sealed packet has been handed to Lin Initial. Its predeclared protocol independently checks identity, uncertainty, exact endpoint accounting and strict improvement. Only admission permits the unchanged five-variable C6 inclusion readback. That readback retains the same center, box, preconditioner, full-box Jacobian and all scientific inequalities; improvement of this one residual alone does not establish that every inclusion inequality passes.

This result has clear enabling value for the existing initial-data construction. Standalone novelty has not been assessed. Neither evolution, global regularity, an event horizon nor a cosmological interpretation follows from this enclosure calculation.

## Controlling artifacts

- `RESULT.json`: `0ef03c4c1cdc1860d71312ad0122b3feb326d97efd4a3491b6e0fcddd4b13ecd`
- `TERMINAL.json`: `b17acdc67cb2c09f013d1544e738feb87a6cbf5e200c2774bdfc85163563277c`
- `LOCAL_AUDIT.json`: `fcd852d8f1846b58efac545f60a9b7fc4c2f3cb3e9ed0b482e9e898e722f2241`
- `RESOURCE_RELEASED.json`: `b5a04f53515968d2b7d116223644acda7d40d55960012752ee357980cda02b21`
- `PREFLIGHT.json`: `6e7f38e1fb6261447e64025780277b5a0759b481524b47e4210f7db076d1c676`
- `STATIC_SUBMISSION.json`: `c2c47d86511b73266b2e6d3817f234d4e20edce1e10d8c590b8f4344113e5c32`

Native checkpoint states, full gradients, primitive boxes, pivot enclosures and case results remain under `preflight/` and `work/`. All previous producer and consumer artifacts remain unchanged.
