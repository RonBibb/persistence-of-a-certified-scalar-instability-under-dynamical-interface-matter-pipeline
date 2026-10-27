# Execution decisions

The initial specification and CONTRACT.json were frozen at 09:02 UTC before controls or scientific spectra. Controls then passed. All four prospectively selected spectral resolutions were executed and retained. The regular three-equation shooting followed at all three declared tolerances.

The candidate negative mass is stable between the methods, but the high-resolution binary64 generalized eigenvectors acquire increasing second-derivative noise. The actual scalar-KG profile residual is 4.30e-8 (N33), 3.37e-7 (N49), 6.00e-6 (N65), and 7.22e-5 (N97). Thus the two finest spectral *profiles* fail the frozen 1e-6 residual criterion and are not accepted physical representations. Their eigenvalues remain numerical comparisons. No failed value is removed or reclassified as passing.

The independently shot smooth mode is the proposed accepted representation. It must pass independent differentiation of its saved fields, both walls, the constraint and the original scalar equation. The lower-resolution spectral profiles supply independent off-grid scalar checks; the finest spectral mass supplies a frequency comparison. This uses the previously specified second method and residual controls rather than changing the criterion.

The declared arithmetic check is now concretized before its launch: fixed-step mpmath RK4/secant on the *same* retained binary64 background polynomial, N=1024,2048,4096 at 40 decimal digits and N=4096 at 60 decimal digits. This is four bounded independent cases, maximum 900 seconds each, one numerical thread each. It checks integration step size and arithmetic; it does not pretend to upgrade the inherited background to 40/60-digit physical accuracy. The preceding fine background is root0_stage1, whose receipt and payload match the hashes already bound in the candidate contract.

The separately completed analytic formulation and forthcoming independent residual implementation are bound in an additional evidence manifest; the original contract stays unchanged.
