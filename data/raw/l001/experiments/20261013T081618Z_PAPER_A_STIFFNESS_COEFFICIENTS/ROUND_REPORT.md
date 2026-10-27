# Quantified wall stiffness response on the certified static background

The upper wall is a much stronger local stiffness lever for the accepted unstable scalar mode: its response coefficient is between 230.227 and 261.464 times the lower wall's. This is a certified comparison within the declared background-preserving action deformation, not an extrapolated stabilization threshold. Both absolute response coefficients now have finite positive bounds as well.

The round began at 2026-10-13T08:16:18Z with a hard deadline of 08:46:18Z. The final terminal receipt records completion and integrity. Only this L001 packet was written; no Linux job, other owner's process, shared manuscript or inventory was changed.

## Medium significance positive result

For the exact central background and the certified negative mode, define

\[
C_i=\frac{\partial\mu_*}{\partial\eta_i}
=\frac{a_i^4 f_i^2}{Z},\qquad
\tau_i^{(\eta_i)}(\Phi)=\tau_i(\Phi)
+\frac{\eta_i}{2}(\Phi-\Phi_i^*)^2.
\]

This explicit change preserves each background wall potential's value and first derivative, and changes its Hessian. It leaves the static background, curvature, separation and wall clocks fixed. Increasing the original common stiffness parameter while holding all other original wall parameters fixed would be a different experiment.

Conservative outward summaries of the new enclosures, in the inherited model units and scalar normalization, are:

| Quantity | Enclosure |
| --- | --- |
| Lower-wall coefficient C_a | [1.74e−11, 4.92e−10] |
| Upper-wall coefficient C_b | [4.00e−9, 1.29e−7] |
| Same-mode ratio C_b/C_a | [230.227, 261.464] |
| Physical kinetic norm Z, with psi(0)=1 | [292.4335, 359.2572] |

The full exact rational bounds and higher precision outward decimals are in [RESULT.json](RESULT.json). The ratio is formed for the same exact mode, cancelling both the physical norm and the common shifted-eigenvalue factor. It is not the quotient of two independently selected points from the broad coefficient intervals.

The precise claim advancement is from “both local slopes are positive” to quantitative enclosures of both slopes and a decisive wall comparison. Equal infinitesimal increases of the two wall Hessians do not have comparable effects: the upper-wall change raises this mode's squared mass over 230 times as much. The squared boundary-overlap interpretation is accepted analytically. It is not a statement that the mode's energy or the cause of instability is localized at that wall.

This is a medium model-specific mechanism gain, not a general new stabilization principle. Finite wall potentials affecting radion masses is established prior work; the new contribution is the certified quantitative response in this curved, finite-stiffness model with its regular scalar-turn treatment. No global monotonicity, complete-spectrum result or finite stabilizing threshold is inferred.

## Small to medium additional theorem gain

The same saved evidence also closes the question of root uniqueness within the original mass strip. Every normalized mode in that strip has f between −1 and 3 and psi at least 0.99. Two such real eigenprofiles would therefore have a strictly positive kinetic overlap: their pointwise cross-density is at least −3+6(0.99)²=2.8806. The accepted regular Green identity instead requires zero overlap for distinct eigenvalues on the same background and wall action. Two distinct real roots inside this strip are impossible.

Together with the inherited existence certificate, this proves **exactly one real eigenvalue in [−0.00132, −0.00131]** for the retained scalar sector, and the earlier derivative argument establishes its local simplicity. This is an independently accepted analytic consequence, not another numerical run. It does not prove that this is the lowest mode, exclude other negative modes outside the strip, or establish a complete spectrum. [Proof](ROOT_STRIP_UNIQUENESS.md), [independent review](ROOT_STRIP_UNIQUENESS_REVIEW.json).

## How the bound was obtained

The test reused 104 authenticated source files, including 94 nonzero-index checkpoint nodes from the two existing uniform mode-strip producers. It proved the required monotonicity using the regular background equations, scalar maximum principle, first integral and a positive lower bound on the mode derivative. Checkpoint slabs then bounded the full continuum norm, including a separate tail covering the unknown exact wall location. A nearby final grid state was not substituted for the wall.

The upper-wall scalar amplitude was reconstructed through the exact eigenmode constraint and Robin condition. In proper-coordinate variables this removes the explicit warp factor from the coefficient formula. All numerical operations used outward rational enclosures; the original background and validated-flow correctness remain inherited premises.

One independently approved owner run completed at 08:30:45Z in 0.416 seconds, using isolated CPython 3.14.4 and one local worker with BLAS threads one. It exited zero with empty stderr; all six targeted negative controls rejected. No ODE producer was rerun. The independent terminal reconstruction verified the sources, checkpoint coverage, bounds and controls using a separately implemented exponential enclosure with degree 80 instead of the owner's degree 64.

The frozen USEFUL classification is an operational enclosure-width outcome, not a scientific significance threshold. The numerical significance is the positive finite slopes and resolved same-mode wall ratio. [Frozen design](DESIGN.md), [gate](INDEPENDENT_GATE.json), [runtime](RUN_METADATA.json), [terminal review](TERMINAL_REVIEW.json).

## Remaining uncertainty and next action

The absolute coefficient intervals remain broad: approximately factors 28 and 32 from lower to upper bound. Their shared shifted-eigenvalue factor lambda=mu+4k is much less precise than the norm. The latter has an upper/lower ratio of only about 1.23; the wall-response ratio also cancels the uncertain lambda factor. These are enclosure widths, not physical fluctuations or measurement error bars.

The ranked next steps are:

1. **Narrow the certified mass bracket around the now-unique in-strip root**, then reuse the existing valid norm and profile bounds to tighten both absolute coefficients. This directly targets the dominant width source. [Prospective bounded test](NEXT_TEST_SPEC.md).
2. **Improve the norm or endpoint-profile enclosure only if it then limits the result**, using a narrow-strip replay, monotone checkpoint refinement or validated accumulation of the regular norm.
3. **Validate determinant sensitivities as an independent coefficient representation**, with exact-root coverage and literal residual normalization. This costs more implementation effort and is not needed to establish the present wall ranking.
4. **Derive the full regular quadratic mass form** if the scientific question becomes allocation of wall, bulk and curvature contributions. The derivative comparison alone does not answer that energy-accounting question.

[Analytic methods and interpretation](METHODS_AND_NEXT_TEST.md), [independent analytic review](METHODS_REVIEW.json), and [method comparison with primary literature](NUMERICAL_METHOD_OPTIONS.md) preserve the action, coordinate, clock and normalization requirements. The growing-exponent derivative applies to the expanding de Sitter homogeneous linear mode, not nonlinear evolution.

No successor was launched. The bounded coefficient question is answered; finite stabilization, nonlinear fate and causal horizons remain separate questions. This packet makes no claim about the older Protocol 394 flux residual.
