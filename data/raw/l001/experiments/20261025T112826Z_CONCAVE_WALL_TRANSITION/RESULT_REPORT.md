# Wall stiffness removes the extra mode but not the persistent instability

**Two independently accepted analytical tests resolve the allocation objective.** In the existing exact concave example, nonnegative wall stiffening removes the extra remaining-band instability through a single massless transition. The other negative regular scalar mode remains for every wall pair, including both Dirichlet limits. Thus this family contains a two-mode region and a one-mode region, but no fully stable regular scalar member.

This is a conditional exact analytical result, not a numerical spectrum. It preserves the authenticated background, bulk potential, wall values/slopes and action; only the allowed wall Hessians vary. It does not change the original central model's separate complete-one-mode result.

## The complete transition criterion

Let x and y be the lower and upper wall Hessians in this example's fixed conventions. Let M be the exact two-by-two transfer matrix for the constrained physical-zero-mass flow, in coordinates (f,L). The proof establishes m11,m12,m22>0, m21<0 and det M>0. Define

    S(x,y)=2m21+x m22+y m11+(xy/2)m12.

The entire finite nonnegative quadrant has the classification

| Condition | Negative regular scalar modes | Massless modes |
|---|---:|---:|
| S<0 | 2 | 0 |
| S=0 | 1 | 1 |
| S>0 | 1 | 0 |

The zero set is one strictly decreasing convex curve between finite positive axis intercepts. Both Dirichlet faces have one negative mode and no massless mode. The count is proved by constrained flow equivalence, exact sign enclosures, simple-root continuation and positive stiffness response—not determinant parity alone.

The curve is specified exactly by uniquely defined IVP transfer coefficients, whose conservative rational bounds are proved. This is not a high-precision numerical plot or pointwise numerical determination throughout the transition strip.

## Explicit usable regions

In the same fixed Hessian units:

- **x+y<=0.02:** two negative regular scalar modes, no massless mode.
- **x+y>=0.10:** one negative regular scalar mode, no massless mode.
- Between these regions, use the exact implicit S criterion; the coarse witness bounds alone do not decide each numerical pair.

On the lower-soft path x=0, T1 already proves a unique threshold y*=-2L_b/f_b, with two modes below, one negative plus one massless at the threshold, and one negative above. T2 generalizes this to both walls and gives sharper intercept enclosures:

    27/1030 <= x* <= 40/569,
    8100/250511 <= y* <= 20000/249489.

It also proves x*<y*: for this particular background, stiffening the lower wall alone reaches the transition at a smaller Hessian than stiffening the upper wall alone. This asymmetry is not asserted for other backgrounds.

## Why this matters

The two instabilities have different behavior under the same allowed change. The extra mode is controlled by the boundary conditions and can cross through zero mass. The below-threshold mode is preserved by the scalar-turn index and cannot be removed by any nonnegative wall stiffness in this family. This gives an explicit distinction between the restricted count and complete physical count, and an exact transition law rather than a list of parameter samples.

The result does not isolate bulk concavity as the sole cause, estimate eigenvalue masses or growth rates, or address nonlinear evolution, other perturbation sectors, charged interfaces, horizons or cosmology. Action/domain and background-existence premises remain inherited. The independent audits are agent reviews, not external human peer review.

## Executed evidence and lifecycle

| Test | Actual analytical start UTC | Accepted result | Independent audit |
|---|---|---|---|
| T1 upper-only path | 2026-10-25 11:32:52 | [Unique crossing and full path count](T1_RESULT.md) | [T1 terminal review](T1_TERMINAL_REVIEW.md) |
| T2 full two-wall family | 2026-10-25 11:37:18 | [Transfer proof and full implicit map](T2_RESULT.md) | [T2 terminal review](T2_TERMINAL_REVIEW.md) |

Each test had a separate prospective admission before its recorded start. No thresholds, boxes or physical inputs were relaxed. Two tests executed; zero numerical workers or CPU leases used. Read-only final local/Linux checks found no matching owned workers, and the independent reviewer turn is complete.

The actual allocation began **October 25 at 7:28:26 AM EDT**; its immutable new-test cutoff remains **9:28:26 AM EDT**. Scientific closeout is **7:41:21 AM EDT**, well before that cutoff. The independent reviewer confirms that both tests complete the recommended fate/transition/one-versus-two-region objective; another calculation merely to consume the allocation is unnecessary. This is early objective completion, not an extension, a resource failure or a claim that every possible further question is exhausted.

Precise curve coordinates, masses and growth rates remain quantitative follow-ups, not indispensable inputs to these conclusions. No successor or queued launch remains. Predecessors, manuscripts, shared inventory and external records were left unchanged. [AUTHORITY.json](AUTHORITY.json) preserves the original two-hour/two-core terms; [CLOSURE.json](CLOSURE.json) records the terminal disposition and source/result identities.
