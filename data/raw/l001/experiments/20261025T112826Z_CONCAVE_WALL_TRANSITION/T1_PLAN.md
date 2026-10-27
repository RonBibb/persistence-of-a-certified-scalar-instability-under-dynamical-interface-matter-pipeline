# Upper wall stiffness transition on the existing concave background

The first test freezes the path kappa_a=0 and kappa_b in [0,infinity], including the upper Dirichlet limit. The background, exact wall values/slopes and canonical action stay those of the accepted concave construction. Only the background-preserving upper wall Hessian changes. The purpose is an exact transition criterion and certified one-versus-two-mode regions, not a scan or an eigenvalue estimate.

## Inputs

Use the sealed predecessor RESULT_PROOF.md and TERMINAL_REVIEW.md in `20261025T051731Z_CONCAVE_REMAINING_BAND`. They give two regular scalar tachyons at the soft corner, exactly one below -4k for all nonnegative walls, at most one in the remaining band everywhere, and at physical mu=0 under the fixed lower soft condition:

    -56 < f_b < -23,
    14569591/37500000 <= L_b <= 21183503/12500000.

These f_b,L_b are fixed exact IVP endpoint values, independent of upper stiffness. Inherited theory is revision 7 MATHEMATICAL_SUPPLEMENT.md, F.10-F.12: real/simple regular roots, compact-wall continuation, uniform root-free auxiliary strip and positive mass response to nonnegative stiffening. Physical mu=0 differs from auxiliary mu=-4k. Normalization is the same as the predecessor; wall Hessians and proper coordinate are unchanged by the four-metric rescaling.

## Frozen test and finite workload

One analytical derivation. Evaluate the zero-mass upper boundary residual L_b+kappa_b*f_b/2 on the entire fixed path. Attempt to prove a unique finite positive crossing kappa_b*, bracket it using only the inherited endpoint bounds, and determine the complete tachyon count on each side using the inherited simple-root continuation and response—not determinant parity alone. Include the crossing's massless mode and upper Dirichlet limit if justified by the same argument.

Predeclare the quantitative witness regions kappa_b in [0,1/100] and kappa_b in [3/20,infinity]. If inherited bounds cannot separate these regions, retain an inconclusive quantitative gate; do not change them after execution. An implicit exact threshold expressed by authenticated endpoint values is an analytical criterion, not a computed numerical threshold.

Controls: verify the upper boundary sign; prove upper mass response is strictly positive at crossing; do not infer an eigenvalue from principal-phase parity; keep the below-threshold mode intact; do not promote one stabilized extra direction to total stability; handle infinity through compact boundary coordinates; no massless conclusion for untested wall pairs.

PASS requires the unique threshold, count assignment and both witness regions, accepted independently. An algebraic/continuation gap is INCONCLUSIVE, not permission to retune inputs. No numerical trajectory, worker, source mutation or resource lease is used. Exact rational arithmetic and analytical implications only. One reviewer assesses prospectively, then reconstructs the actual result. This test uses no two-core allocation resources and cannot serve as a fallback numerical launch around a HOLD.

Actual analytical execution starts only after prospective admission and before the allocation cutoff, recorded separately. This finite proof is the executed test. Subsequent steps, if justified by its result, require their own prospective admission within the allocation; this plan does not pre-admit them.
