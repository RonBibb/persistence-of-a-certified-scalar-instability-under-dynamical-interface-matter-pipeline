# Quantitative amplitude certificate inventory

The accepted archive contains the real-axis background needed for a first quantitative prerequisite. It does not yet contain a uniform charged-branch inverse constant, a certified complex spatial collar, or numerical nonlinear-source majorant constants. The smallest useful next calculation is an authenticated streaming reduction of the saved background cells, followed by an all-higher-order positivity cutoff. It requires no new trajectory solve.

## Evidence inspected

Paths below are relative to the L001 experiments directory unless stated otherwise. This is a document and schema inventory, not a fresh arithmetic replay or full archive hash audit.

| Ingredient | Existing evidence | Reuse and limitation |
| --- | --- | --- |
| Real background and exact parameter intervals | `20261026T033400Z_CUBIC_FULL_FLOW/FLOW_primary.json`, its independent counterpart and chunk manifests; full-flow CONTRACT and FINAL_REPORT | Whole-cell archives can supply extrema of H, T, Phi and E, with endpoint coverage. Global extrema have not been extracted in this inventory. |
| Low-order nonsingular matching | Full-flow matching and accepted first/second-order parents | Supplies particular normalized shooting denominators. A denominator alone is not a source-to-solution operator norm. |
| All-order scalar nonresonance | `20261025T225750Z_AB_MECHANISM_ALLOCATION/INDEPENDENT_NONRESONANCE_REVIEW.md`; manuscript Appendix O.6 and C | Excludes a kernel under inherited premises; does not quantify inverse amplification. |
| Scalar operator and Robin formulas | Manuscript S4 and Q7 | Explicit enough to derive a quantitative high-order cutoff from background extrema. |
| Analytic nonlinear source maps | Manuscript Q1–Q10, S6–S7 | Defines the required equations, but K, M and complex-collar constants remain uncomputed. |
| Complete first three distance coefficients | `20261026T100400Z_CUBIC_DISTANCE/FINAL_REPORT.md` and bound results | Reusable polynomial part, not a tail bound. |
| Earlier explicit analytic radius method | `academic2-event-horizon/lin-c4-local-certificate-r1-20261005T221400Z/ANALYTIC_RADIUS.md` | Different Hamiltonian initial-data map and amplitude parameters. Its constants and radius cannot be transferred to this charged branch. |

The full-flow report records 8,183 primary and 16,365 independent cells, with whole-cell witnesses and uncertain-endpoint coverage. Scientific reuse must authenticate all accessed chunks and preserve the full parameter intervals. No midpoint substitutions or cross-engine intersection narrowing.

## Derived real-axis cutoff candidate

This derivation is prospective and not independently audited. Let certified bounds on the real interval be

    k >= k0 > 0, E >= e0 > 0,
    |H| <= H0, |T| <= T0, |Phi| <= P0, |m²| <= m0,
    |Tprime| <= U0.

The background equation permits U0 from |m² Phi - 4HT|; a directly evaluated whole-cell expression may be tighter. Define

    B0max = 12 H0 T0 + 4 m0 P0,
    d0 = 42 k0 e0²,
    c0 = 9 k0 e0²,
    C0 = B0max U0 / d0.

For integer n>=1, mu_n=-18n(2n-1)k gives

    D_n >= d0 n²,
    V_n >= 18 k0 e0² n² - m0 - C0/n².

Thus the conservative condition

    c0 N² >= m0 + C0

implies V_n>=c0 n² for every n>=N. This uses 2n-1>=n and drops the nonnegative 2T² term; it is deliberately sufficient, not optimal.

For the boundary coefficient, let J_n=D_n-2T². Then

    J_n=-3(mu_n+4k)E² >= d0 n²,
    A_n=J_n/D_n in (0,1],
    beta_n=Gamma_n/(2A_n)-2 sigma T Tprime/J_n,
    Gamma_n > 41/2.

It follows that

    beta_n >= 41/4 - Cb/n²,   Cb=2 T0 U0/d0.

Requiring Cb/N² <= 37/4 suffices for beta_n>=1 at both walls for all n>=N. Endpoint-specific bounds may improve this estimate. The sign of sigma need not be guessed because the second term was bounded in absolute value.

The drift also has the uniform bound

    |a_n| <= 4H0 + B0max T0/d0.

These estimates provide a quantitative high-order positivity threshold and coefficient bounds. They do NOT yet establish the full derivative-weighted inverse estimate S5. A boundary-layer comparison and derivative estimate must still supply its constant; low orders 1 through N-1 need quantitative inverse bounds separately. Nonresonance is already a prerequisite, not the numerical answer to those bounds.

## Next extraction and acceptance requirements

1. Bind the two FLOW records, original frozen/source manifests and all accessed chunks. Verify hashes before consuming witnesses.
2. Stream the saved whole-cell background boxes. Check field ordering from the frozen adapters, domain coverage, and both pieces covering the uncertain upper endpoint. Use an outward enclosure over the covered domain; including the small extra terminal cover is safe if explicitly recorded.
3. Extract rational extrema H0, T0, P0, e0 and parameter extrema; derive U0, B0max and the cutoff inequalities with exact interval arithmetic. Primary E is directly archived. For the direct-W representation, authenticate the inherited exponential enclosures or recompute them with outward arithmetic; do not treat exp of a midpoint as a bound.
4. Report each representation separately and a conservative hull if needed. Require k0,e0 positive. A failed positivity extraction is numerical incompleteness, not evidence of singular physical behavior.
5. Independently reconstruct the reduction and the all-n inequalities before calling the cutoff certified. Predeclare a finite implementation/resource ceiling; if the sufficient cutoff is impractically large, report it rather than launching thousands of solves.

Output should contain the extrema, exact cutoff inequalities, finite low-order workload, hashes, and explicit `uniform_inverse_constant_certified: false` and `amplitude_radius_certified: false`. An accepted cutoff would be a prerequisite result, not an amplitude certificate.

## Decision

Proceed with the background-envelope and cutoff extraction before a new ODE, fourth-order coefficient, or finite-amplitude solve. It tests whether the all-order inverse route is computationally practical and identifies the remaining finite set. Complex-collar construction and full source-majorant accounting remain separate tasks even if this prerequisite succeeds.

Status: inventory and analytic cutoff derivation completed; extraction not launched. No sealed parent or manuscript changed. No numerical amplitude range is claimed.
