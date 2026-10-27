# T7 independent integer-interval prospective review

**ADMIT** the fixed independently transcribed integer-interval replication. I read the plan, producer and complete interval.py, and checked the wrapper identity. No numerical execution was performed by this reviewer.

## Arithmetic proof and controls

Let S=2^256. Stored endpoints represent integers divided by S. Fraction conversion uses floor and ceiling of the scaled rational. Addition/negation are exact on that grid. Multiplication takes all four integer endpoint products, then floors the minimum/S and ceilings the maximum/S, so it is outward in all sign cases.

For a nonzero-containing interval [lo/S,hi/S], reciprocal is decreasing on either positive or negative components: its ordered endpoints are S/hi and S/lo. The code's stored reciprocal bounds floor(S^2/hi) and ceil(S^2/lo) are therefore correct even when both endpoint integers are negative. Python integer // rounds toward negative infinity, and ceildiv(a,b)=-((-a)//b) gives the mathematical ceiling for either denominator sign. Division by a zero-containing box is rejected. Repeated multiplication encloses integer powers without generic-power semantics.

The fixed positive/negative/crossing Fraction corner controls exercise these sign cases, including negative divisors. Signed constant and exponential tests are meaningful: the degree-12 exponential Taylor remainder for |h|=.01 is bounded by 2|h|^13/13!, since exp(.01)<2. Requiring the produced enclosure to contain this independent rational Taylor enclosure is sufficient for that manufactured control. Invalid divisor and undersized tube rejection are retained.

## Numerical method and transcription

The independently written RHS and Hamiltonian match the accepted model and zero-mass transfer equations. The same exact seed, wall positions, backward uncertainty retention and 1024/2048 workload are retained. The fixed-grid radius construction uses the outward integer upper radius directly, so the tube encloses the intended Minkowski extension. Exact rational background checks and strict candidate containment establish the same first-exit argument. Endpoint Y+hF(B) then encloses the true endpoint; no Taylor remainder is omitted.

This declares a new 256-fractional-bit representation, not a claim that fixed-point and Arb precision are identical. It is genuine independent interval arithmetic and independently transcribed source while sharing Python and the mathematical method. Equal-wall roots use exact coefficient envelopes and fixed bisection instead of square roots. Analytical transfer signs justify their monotonicity. All Hamiltonian/determinant/root gates, level checks and T4 comparisons remain mandatory; agreement alone is insufficient. No intersections, precision adjustment or rescue run are admitted.

Normal one-core nonblocking leases/HOLD policy, memory cap, dual time caps and immutable actual-start cutoff 16:12:07Z remain. Assertions must be enabled. Before/after bound source and input identities and the pinned Python binary are required. Numerical reviewer execution is not part of this review; independent terminal audit must inspect actual gates and intervals.

| ADMISSION relative binding | SHA-256 |
|---|---|
| PLAN.md | a5fd3a213b7bcc4010241a942c98ff2432a572a847110ac9aece3b2c9db32a52 |
| producer.py | f0a252dc4efbe42b975d7d044be01d5c3e398df009b43dc7ca030c9835c1e56b |
| interval.py | b64469c934e75648717365a1d10ddfb2b2ee5e494b17ee2acf4d2ab27f658c1f |
| lease_run.py | 7e255cadc28a3adce7f56dd5c1c6a47c7d2313b874bdf79b21cbc8c881c02275 |
| ../T4_CORRECTED_COORDINATES/RESULT.json | 0e4530f949ee7c955ae8ec07c2a2208ebd8f20d9cdc45aca8590adf3e946250c |
| ../T4_CORRECTED_COORDINATES/LEVEL_2048.json | ebb7e29ab62e396847219555569c412b9b39ba71709e80813a060d4487c5e652 |
| ../../20261025T115424Z_TRANSITION_COORDINATES/producer.py | adc749e5ddbb448d55d70d8e004f41c47f5ec372197553d71b00fba0b0a1d93f |
| ../../20261025T115424Z_TRANSITION_COORDINATES/PLAN.md | 34eeeb988c01c9f19e103abb35c9110706e42ac86a21d1827b3fc5eee3f6cbd8 |
| ../../20261025T112826Z_CONCAVE_WALL_TRANSITION/T2_RESULT.md | 8e15a53d36565d47e124f5d7385664d9bc606511d7aafee94ff791f4920e1284 |

No admission blocker found. One fixed run only; failure remains technical incompleteness.
