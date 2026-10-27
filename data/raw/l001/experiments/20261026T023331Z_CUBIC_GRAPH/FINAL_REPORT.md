# Cubic moving-boundary diagnostic — completed and independently accepted

The cubic graph contribution is strictly negative: **[-402024.913497, -402022.821351]** in the frozen lower-unit-current normalization. It continues the boundary-shortening direction rather than providing a cubic reversal. This is a useful additional coefficient, not the full cubic proper-separation coefficient or a bound on finite-charge validity.

## What was computed

One endpoint-only calculation on the accepted first- and full second-order AB solution, in the Eulerian chart and conserved-current direction (Na²,Nb²)=(1,0). No new radial integration, parameter scan, other current direction or manuscript change was performed.

The exact moving-boundary equation S7 gives

    342 sigma k E² xi3 + qI3 = 0.

The cubic source depends only on accepted lower-order fields. Direct degree-three series extraction and a separately written closed expression agree as exact rational polynomials. The actual affine scalar/current coupling, total wall velocity derivative, fixed-s bulk derivatives, cubic velocity factors and intrinsic surface oscillator are retained. New third-order bulk and oscillator unknowns do not enter this graph row.

The proper-separation contribution from the wall positions is graph3 = xi_b,3 − xi_a,3. It does not include the cubic bulk metric integral and all endpoint-transport terms required for the complete physical distance.

## Results and interpretation

The primary and independent parent endpoint enclosures were processed separately, compared for overlap and combined by outward hull, never intersection. Directed decimal bounds were rendered on Linux in the independent terminal review.

| Quantity | Outward interval containing both engines |
|---|---:|
| Lower-wall xi3 | [402022.965332, 402024.695313] |
| Upper-wall xi3 | [-0.218184, 0.143981] |
| Cubic graph difference | [-402024.913497, -402022.821351] |
| graph3 / graph2 | [89.530568, 89.531085] |

The lower-wall displacement dominates this chart-specific difference. The upper-wall coefficient remains sign-unresolved and was not replaced by zero.

The coefficient ratio means that the cubic-to-quadratic **graph-term** ratio is approximately 89.53 z. It does not establish a convergence radius, a safe amplitude threshold or a bound on the omitted tail. Earlier full second-order shortening remains accepted; third-order graph dominance cannot be inferred from second-order graph dominance.

For positive formal z this cubic graph term is negative. On the selected branch z decays as exp(-6 h t), so this is not evidence of runaway or accelerating contraction in time.

## Validation and provenance

- All 30 exact polynomial qualification checks passed: both orientations, lower-order replay, cubic divisor, independence from new unknowns, remote-wall limit with xi2 retained and two sensitive mutation controls.
- The separately authored exact Fraction-interval audit eliminated h using h²=k and reconstructed the cubic sources, divisions, graph differences, ratios and classification without importing the three producer mathematical modules.
- Both source/runtime binding checks and artifact-digest checks passed. Parent ODE evidence was authenticated, not rerun.
- Producer duration: 2.153699 seconds. Independent numerical audit: 2.242188 seconds. Preparation and review time are not included in those execution durations.
- Linux-only scientific execution, one leased CPU, inherited shared resource limits; leases released. No successor is running from this packet.

Frozen manifest SHA-256: `e0e89f255d5c74a29b788976ab1f232358df496c800e022314664a58b20645de` (1,268 bindings).

Result SHA-256: `9b4e23b596ddce2167015fb6f9508d428ab831ff56b657a704a16401b19407ed`.

Independent audit SHA-256: `349d7f471b92660c898ca31ca16848bcf80040421895f4d4cae204e57a660f08`.

The accepted parent is `20261026T015206Z_FORCED_SECOND_ORDER_R1`, frozen SHA-256 `27b9c8799f3bedef8f49788284549e4ba7cffe5adf7cc5b7c85425c324bb5566`. Its assembled second-order states, not the particular shooting solution alone, supply this calculation.

The historical `terminal_review_pending: true` field in RESULT.json is deliberately preserved; FINAL_REVIEW.md and the successful audit terminal supersede that status without altering the produced record.

## Next justified step

Derive and qualify the forced cubic bulk and wall system, then compute the complete cubic proper-separation budget. That would test whether the boundary trend survives in the actual distance, using this graph result as a fixed control. Do not infer the answer from the graph term alone.

A numerically explicit finite-amplitude validity range remains a separate task: the Appendix C majorant and uniform inverse/collar constants need quantitative bounds. Even a complete third coefficient would not by itself bound every higher-order term. No successor was launched here.

Files: CONTRACT.md, SOURCE_REVIEW.md, FROZEN.json, ADMISSION.json, RESULT.json, production_TERMINAL.json, AUDIT_RESULT.json, audit_TERMINAL.json and FINAL_REVIEW.md, alongside the frozen source and runtime inventories.
