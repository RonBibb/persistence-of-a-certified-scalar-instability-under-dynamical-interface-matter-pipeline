# Complete cubic proper distance

Post-process the accepted full cubic flow without a new ODE solve. Bind the full-flow manifest, terminal artifacts and all streamed parent chunk hashes; bind the accepted cubic graph and full second-order endpoint records. Preserve full A2/A3 intervals, both numerical representations, the original lower-current normalization and Eulerian chart.

Compute the cubic coefficient of the moving-endpoint proper distance as graph plus bulk plus endpoint transport:

    graph = xi_b3 - xi_a3
    bulk = integral[c3 - 2p3 - 2p1*c2 + 4p1*p2 - (4/3)p1^3] ds
    transport = [-2p1*xi2 + (c2-2p2+2p1^2)*xi1 - p1prime*xi1^2]_a^b.

Use c2=-(3/13)(6p1^2+f1^2) and the accepted c3=-(8/19)(6p1*p2+f1*f2-3p1*c2). Assemble p2/f2 with full A2, and p3 with one full A3 throughout. Integrate p3 particular and homogeneous separately before multiplying the latter total by A3, and compare with an independently grouped whole-density integral. No intersection narrowing.

Use validated whole-cell boxes as enclosure quadrature. For uncertain D, each cell contributes mandatory length times density plus [0,optional length] times density, with exact coverage checks. Outward dyadic 2^-80 exports are permitted to keep archive and audit sizes bounded; they must contain their original bounds. Such exports only widen, never replace inputs by midpoints. No post-result precision tuning.

Independently reconstruct transport as the integral of B'(s), where B=-2p1 X2+(c2-2p2+2p1^2)X1-p1prime X1^2 and X1,X2 are affine interpolants of the accepted wall displacements. Verify its exact generic product-rule identity and the cubic metric-density exponential coefficient before execution; retain both endpoint and integrated transport bounds. Require overlap of the two transport forms, grouped/direct bulk forms, and final distance forms within each engine, then overlap between engines. Report the outward hull of the endpoint-form distance, without using cross-check intersections to shrink it. A zero-containing final interval is a valid unresolved scientific outcome.

Scientific execution Linux only, 768-bit single-thread Arb, inherited line/CPU leases and HOLDs, maximum two aggregate cores, 2 GiB process cap. Stream parent and output chunks; never collect all parent cells. Production plus exact saved-budget audit operational cap 1800 seconds, one attempt per stage. Preserve any technical failure with no in-place repair/retry. No automatic successor or tail/radius claim. Durable per-chunk records are evidence, not a tested bitwise-resume interface.

Independent source review, frozen admission, exact saved-budget audit and terminal integrity review required. The auditor must separately reconstruct budget densities, integration weights, sums and endpoint algebra using exact Fraction intervals; inherited full-flow validation is not rerun. For direct-W inputs, independent exp evaluation is outside this saved-budget audit scope and must remain disclosed.
