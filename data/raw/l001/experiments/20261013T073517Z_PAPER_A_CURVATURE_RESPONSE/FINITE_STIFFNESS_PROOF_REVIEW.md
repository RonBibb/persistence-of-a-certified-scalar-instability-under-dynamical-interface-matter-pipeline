# Independent review of regular norm and finite stiffness identities

Accepted as analytic consequences of the inherited exact background equations, regular constrained mode equations, finite Robin conditions and doubled-cover kinetic normalization. No new mode integration or parameter calculation was performed. No blocking algebraic issue was found. The cutoff lemma, regular Green identity, local determinant simplicity and local background-preserving wall-Hessian derivative are separate accepted statements with the qualifications below.

Reviewed source: METHODS_FINITE_STIFFNESS.md, SHA-256 `65ef9f00383030742704c301f77495bc7823e2ef837853205d0fcb363b8bdec5`. Candidate language in that frozen investigative note records its pre-review status; the present receipt supplies the analytic disposition without rewriting its history.

## Cutoff identity and scalar turn

The [independent regular formulation](../academic2-event-horizon/lin-curved-stability-2026-09-29/analysis/INDEPENDENT_FORMULATION.md) and [kinetic review](../academic2-event-horizon/lin-curved-stability-2026-09-29/analysis/KINETIC_AND_CONTROL_REVIEW.md) were read directly. Their conformal-coordinate conventions give

    Y=a²ψ, Y′=−a²Sf/3, g=3/(2aS²), q=1/a.

For S nonzero, gY′=−af/(2S). Differentiating and substituting the regular constraint gives (gY′)′=qY−λgY. Direct multiplication gives g(Y′)²+qY²=a³(f²+6ψ²)/6. Since Z=2∫a³(f²+6ψ²), the coefficient Z/12 is correct. Integration by parts contributes the endpoint flux with plus sign on the right:

    ZΩ/12 = λ∫Ω gY² + Σ[gYY′]left^right.

The finite Robin condition and constraint give B_i f_i=3λψ_i with the stated inward signs. Therefore g_iY_iY_i′=−3λY_i²/(2a_iS_iB_i) when S_iB_i is nonzero. Subtracting lower from upper flux gives exactly the lower-plus and upper-minus terms in the proposed bracket. A vanishing endpoint denominator forbids that divided rearrangement; the original regular equations remain controlling.

At a smooth simple turn, S=s₁x+O(x²) and the constraint gives s₁f*=−3λψ*. Consequently Y′=λY*x+O(x²), and the stated coefficients of gY² and gYY′ are correct. With symmetric cutouts the two internal fluxes have total leading term −2cλY*²/ε, which cancels the weighted bulk term +2cλY*²/ε. The combined expression has the finite limit Z/12 because its equal regular density is smooth. The lemma assumes a simple turn and nonzero Y*; it does not newly locate or validate the turn numerically. The inherited positive profile and positive warp supply Y* nonzero for the accepted central mode.

This reconciles positive physical norm with the negative shifted eigenvalue. The divergent reduced integral alone is outside the regular mode's admissible representation and is not a ghost diagnostic. It neither identifies a unique cause of instability nor establishes an independently renormalized physical norm.

## Regular Green identity

For real profiles on the same exact background let Δμ=μ_i−μ_j, U=ψ_i f_j−f_iψ_j, W=f_i p_j−p_i f_j, and J=a³(W−2SU). The displayed regular equations independently give

    U′=−2AU+ψ_i p_j−p_iψ_j,
    W′=−3AW+Δμ f_i f_j+4S′U.

Subtracting the two constraints after multiplying by the other ψ gives

    SU′=(S′−3AS)U−3Δμψ_iψ_j.

Substitution in J′ cancels every U term and yields

    J′=Δμ a³(f_i f_j+6ψ_iψ_j).

No division by S was used; this identity is valid through the scalar turn. Equal Robin stiffness gives J=0 at both walls, hence orthogonality of distinct real eigenvalues in the regular physical bilinear form. This is not a completeness or full self-adjoint-domain theorem.

For differing wall Hessians on the same background, Robin substitution gives J_α=σ_α a_α⁴ δγ_α f_i f_j/2. Since σ_a=+1 and σ_b=−1, integration produces

    (μ_j−μ_i) 2∫a³(f_i f_j+6ψ_iψ_j)
      = Σα a_α⁴ δγ_α f_i(z_α)f_j(z_α).

Both orientation and cover factors are correct.

## Local simplicity and Hessian response

For the smooth lower-wall normalized IVP, the nonzero inherited B_a permits smooth initial data in μ. Taking one solution at an exact eigenvalue and the other at nearby μ gives lower J=0 and upper J=a_b³ f_b* R(μ). Differentiation of the integrated identity gives

    R′(μ*)=−Z*/(2a_b³ f_b*).

At either wall, f*=0 together with λ*≠0 forces ψ*=0 through Bf=3λψ, then p*=0 through Robin. Regular IVP uniqueness would contradict the nonzero normalized solution. Thus f_b*≠0 and R′(μ*)≠0. The [central result](../academic2-event-horizon/lin-central-validated-mode-r1-20261005T172800Z/RESULT_REPORT.md) supplies a strictly negative λ strip and positive Z. The proper-coordinate residual differs from R by a positive background warp factor, so local simplicity is invariant under that conversion. No numerical derivative or count of roots is inferred.

The implicit-function theorem therefore supplies a local smooth mode branch for sufficiently small wall-Hessian changes that preserve the exact background. The declared action deformation η_i(Φ−Φ_i*)²/2 has zero value and first derivative on that background and changes only the selected wall Hessian. Dividing the bilinear identity by the deformation and taking the smooth limit gives

    ∂μ*/∂η_i = a_i⁴ f_i(z_i)²/Z* > 0.

This formula is accepted at the equation level for that explicitly changed action and local branch. It does not require a guessed reduced scalar product. It gives no numerical slope, stabilizing threshold, finite-amplitude guarantee, complete spectral classification, or nonlinear fate. A full constrained second-variation cross-check remains useful for a future decomposition of physical energy contributions, but the regular identity already proves this local derivative consequence under the stated inherited equations.

## Literature and reporting scope

Primary texts were opened to check the methodological restrictions: [Frolov and Kofman](https://arxiv.org/html/hep-th/0309002v1), [finite-potential scalar products](https://arxiv.org/html/2404.05141v2), and [Olechowski](https://arxiv.org/html/2408.15343v2). The latter two use flat backgrounds; their conclusions are not substituted for the derivation above. The companion UNBLOCK_OPTIONS.md appropriately distinguishes established methods from model-specific results and rankings.

The proposed identities add explanatory and local analytic consequences to existing evidence. They do not repair or replace the accepted central negative-mode certificate, provide a new numerical mode, or make an independent historical-authentication or validated-flow claim. No additional computational test was needed for this analytic review.
