# Lower wall curvature and separation response

The saved certified upper-tension family has a positive lower-wall curvature susceptibility and a negative intrinsic curvature–separation slope. Increasing the additive upper-wall tension makes its negative baseline value less negative; along this local static family, lower-wall curvature increases while equilibrium proper separation decreases. This is a new quantitative consequence of the saved interval certificates, conditional on their validity and the original action and parameter provenance. The separate independent terminal audit accepted this conditional result.

## The fixed family and invariant quantity

The parameter is lambda_b = -851862101055633/140737488355328 + delta, where delta belongs to the exact rational interval [-1/1000000,1/1000000]. All other inputs retain the original exact dyadic values in P01's `BINDINGS.json`. In particular lambda_a = 6755388606266369/1125899906842624 remains fixed; its original reconstruction from the constructor's lower-wall rule is an inherited model-provenance premise.

Write a=Phi(0), x=a-v0, and fix A(0)=0 throughout the family. The action-derived launch map is

    H0 = -(lambda_a + gamma*x^2/2)/6,
    S0 = gamma*x/2,
    k(a) = H0^2 - 1 - S0^2/12 + m2*a^2/12.

Differentiation at fixed lower-wall parameters yields

    dk/da = -gamma*H0*x/3 - gamma^2*x/24 + m2*a/6.

The four-dimensional lower-wall metric has Ric=3*k*exp(-2*A0)*h and hence scalar curvature R_lower=12*k*exp(-2*A0)=12*k. R_lower is intrinsic; its interpretation does not depend on an arbitrary rescaling of the reference slice metric. D is the original proper wall separation. The derivative dR_lower/dD therefore compares two geometric quantities along the same parameterized family.

The uniform Newton image encloses a(lambda_b), and the saved response intervals enclose da/dlambda_b>0 and dD/dlambda_b<0 throughout the exact tension interval. Smooth dependence of the reduced ODE, the inherited transverse event, and the nonzero boundary Jacobian give local smooth branches. Their certified uniqueness in the common launch box makes them agree on overlaps. Thus the derivative identities and mean value arguments apply across this connected local family.

## Quantitative consequence

The following decimal endpoints are outward bounds obtained from exact rational interval arithmetic:

| Quantity | Uniform enclosure |
| --- | --- |
| dk/da | [0.016657079289, 0.016657086917] |
| dk/dlambda_b | [0.000000422485, 0.000000425573] |
| dR_lower/dlambda_b | [0.000005069823, 0.000005106865] |
| dR_lower/dD | [-0.000000551542, -0.000000545768] |

The last line uses dR_lower/dD = 12*(dk/da)*(da/dlambda_b)/(dD/dlambda_b), whose denominator is uniformly separated from zero. It proves a strict static curvature–separation anticorrelation on this branch, including every secant between two distinct branch points. The separation response is inherited; the new result is the certified curvature response and its geometric slope.

For any lambda1<lambda2 in the interval, multiply the displayed curvature-response bounds by lambda2-lambda1 to enclose the corresponding curvature increase. In particular, the full endpoint tension difference is exactly 1/500000, so conservative consequences of the displayed bounds are

    8.44970e-13 <= k(lambda_plus)-k(lambda_minus) <= 8.51146e-13,
    1.0139646e-11 <= R_lower(lambda_plus)-R_lower(lambda_minus) <= 1.0213730e-11.

These inequalities integrate a uniform derivative bound. They do not subtract two uncertain endpoint background approximations. The exact rational bounds in `RESULT.json` are slightly tighter; its fixed 12-decimal display is too coarse to show the positive lower endpoint of the first difference.

## Verification and premises

The frozen checker builds the exact polynomial k(a) from H0 and S0 and differentiates its coefficients. A separately assembled analytic derivative must match those coefficients exactly. Two interval evaluations of that derivative intersect consistently and give the strictly positive dk/da interval. All arithmetic inputs come from the saved exact model, Newton image and uniform derivative endpoints. No flow, spectral or evolution producer was executed.

The one admitted owner execution completed at 2026-10-13T07:43:18.273402Z using isolated CPython 3.14.4, with return code zero and empty stderr. All six in-memory corruption controls rejected at their intended predicates: reversed scalar response, zero-reaching separation response, altered lower normalization, altered model constant, displaced root image and corrupted derivative coefficient. The baseline source bytes and frozen script/design hashes were checked before computation. `INDEPENDENT_GATE.json` is the preceding single gate decision; `RUN_METADATA.json` records the execution and output hashes.

The separate [terminal review](TERMINAL_REVIEW.json) reconstructed all ten enclosures exactly using an independently expanded polynomial, verified every outward decimal bound and the control outcomes, and accepted the geometric and finite-difference wording. Its accepted classification is a static consequence of saved uniform intervals, not independent flow production.

Validity of the stored uniform interval flows, their derivative enclosures, the action reduction and exact model provenance remain inherited. The newly located October 8 migration manifest supplies earlier documentary hashes for both complete-flow result snapshots; it improves the previously bounded provenance search result, but does not independently verify producer-time validity or replace a numerical producer. The original historical raw and 4096-step failures remain unchanged.

This result concerns different static models along one small tension interval. It does not establish relaxation, nonlinear motion, stability over the interval, global first-event uniqueness at other tensions, a horizon or a cosmological mechanism. Tension dependence of curved two-wall solutions is established background physics; the contribution here is a certified sign and quantitative enclosure for this exact finite-stiffness branch.

## Evidence

- [Original uniform family result](../research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/RESULT.json) and [exact model bindings](../research-rounds/20261007190321Z_PAPER_RADAR_FOUR_TESTS/row_01/BINDINGS.json).
- [Action reduction and launch map](../academic2-event-horizon/lin-theorem-causal-readiness-window-20261003T205314Z/FORMAL_REDUCTION_LEMMA.md).
- [Prior independent tension arithmetic audit](../20261013T001854Z_PAPER_A_STATIC_TESTS/INDEPENDENT_TENSION_AUDIT.json).
- [Earlier migration manifest](../../provenance/manifests/round-20261007190321Z_PAPER_RADAR_FOUR_TESTS.json), SHA-256 `8f63621ba9449289e18d5cd49a158fcd83a10ad8746b3c056e6f845e2a242a5e`.
- This packet's `SOURCE_BINDINGS.json`, `DESIGN.md`, `curvature_response.py`, `RESULT.json` and `RUN_METADATA.json` bind the new consequence and its execution.
