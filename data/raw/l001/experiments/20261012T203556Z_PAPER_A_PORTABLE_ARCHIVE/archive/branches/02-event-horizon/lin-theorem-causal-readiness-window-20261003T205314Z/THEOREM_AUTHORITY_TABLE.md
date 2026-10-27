# Reconciled theorem authority table

## Reading rule

This table reconciles the sealed D1/D2A theorem packet with the later
producer-independent D1 replay. It does not replace or edit either parent.
Every decimal interval below is outward-rounded evidence copied from a sealed
record. Full exact rational endpoints, including the long geometric fractions,
are collected without re-evaluation in `THEOREM_INTERVALS_EXACT.json`, SHA-256
`a44b9e3dc4e1fcd6051cf96dc3c4f292f9ed3ea220c64eac4ced4bd88451fa44`.

## Proof-bearing table

| Clause | Exact or displayed enclosure | Certificate consequence | Authority |
|---|---|---|---|
| Fixed model | `m^2=0.41`, `gamma=20`, `v0=0.1`, `v1=0.09048374180359596`, `lambda_a=5.999990376773895`, `lambda_b=-6.052844277744164`, each interpreted as its exact binary64 dyadic | Fixes the reduced Einstein--scalar two-wall problem; the lower-tension provenance remains reconstructed rather than independently archived | `MODEL_V1.md`, SHA `4077686e...dc9`; `PROSPECTIVE_BVP_DESIGN.md`, SHA `5f73207b...55a` |
| Original D1 interval-Newton image, 32,768 steps | `[456607025194779413/4611686018427387904, 114151756532473697/1152921504606846976]` = `[0.09901086573766466, 0.09901086594043548]` | Strict self-map of the frozen launch interval; proves existence and local uniqueness for the original producer | Result SHA `07b22a8b...8f9` |
| Independent D1 interval-Newton image, 16,384 steps | `[456607024314529497/4611686018427387904, 456607027779925737/4611686018427387904]` = `[0.09901086554679088, 0.09901086629822892]` | Independently generated strict self-map; reproduces existence and local uniqueness without importing the original producer or its enclosures | Result SHA `41077a79...d16`; audit SHA `f51a3999...76` |
| Original first upper-Israel event | `[32727/16384,32729/16384]` = `[1.99749755859375,1.99761962890625]` | Transverse first-event enclosure for the unique root | Result SHA `07b22a8b...8f9` |
| Independent first upper-Israel event | `[16363/8192,16365/8192]` = `[1.9974365234375,1.9976806640625]` | Independently reproduces a transverse first event and contains the narrower original enclosure | Result SHA `41077a79...d16` |
| Independent transversality | `G_s in [-0.017911083024782542,-0.017896675281034263]` | `G_s` excludes zero; the first-event map is locally differentiable | Exact rationals at `THEOREM_INTERVALS_EXACT.json#/d1_independent_16384/G_s` |
| Independent shooting derivative | `q'(a) in [124093.76952925383,124255.72137561499]` in the sealed fine record | Derivative excludes zero; supports local uniqueness and interval Newton | Exact rationals at `THEOREM_INTERVALS_EXACT.json#/d1_independent_16384/q_prime` |
| Positive curvature | `[0.000326841301145298,0.0003268413757636101]` | Entire enclosure is positive | Full exact endpoints at `...#/d1_independent_16384/curvature` |
| Conformal length | `[6.379214731752709,6.381247509927617]` | Complete-domain conformal length is positive and finite | Full exact endpoints at `...#/d1_independent_16384/conformal_separation` |
| Global warp | `[0.13477779494132847,1.0000343344872817]`; event value `[4753180581887/35184372088832,4754497912833/35184372088832]` | Warp remains positive on the validated domain; the event warp is independently enclosed | Result SHA `41077a79...d16` |
| First integral over every cell | union `[-5.982751187821706e-6,5.982179220404177e-6]`, with every cell containing zero | Independently encloses the remaining Einstein identity over the full interval | Full exact endpoints at `...#/d1_independent_16384/first_integral_union` |
| Lower wall identity | `[-34409577/576460752303423488,34409577/576460752303423488]` | Contains zero under the independent reconstruction | Result SHA `41077a79...d16` |
| Upper wall identity | `[-5.906509158863721e-6,5.3012677201549174e-6]` | Contains zero under the independent reconstruction | Full exact endpoints at `...#/d1_independent_16384/upper_wall_identity` |
| D2A fixed separation | `D0=2250986857014815/2251799813685248` = `0.9996389747145851` | Fixes the distinct original-separation problem | D2A result SHA `eb16a5e4...8a5` |
| Exact separation contrast | Original D1 gives `D-D0 in [2246977773263329/2251799813685248,2247252651170273/2251799813685248]` and `D/D0 in [4497964630278144/2250986857014815,4498239508185088/2250986857014815]` | Certifies a gap of `0.9978586`--`0.9979807` and ratio of `1.9982190`--`1.9983411`; “roughly twice” is an exact interval consequence rather than a rounded visual comparison | Recomputed exactly by `verify_reconciled_authority.py` from the bound original D1 interval and exact positive `D0` |
| D2A launch domain | `[0,3602879701896397/36028797018963968]` | Exact cover of the complete declared `0 <= a <= v0` interval | D2A audit SHA `bc904a2e...a09` |
| D2A cover | 693 terminal boxes; counts `20/670/1/2`; zero unresolved | Every admissible box is discharged by negative curvature or a wall residual excluding zero | D2A terminal SHA `47b35e77...a5b` |
| D2A residual floor | `max(|G(D0,a)|,|h(D0,a)|) > 77/10000` on every box not excluded by negative curvature; direct exact rederivation finds minimum boxwise bound `0.0077281481292751026` | Excludes a simultaneous fixed-distance wall root throughout the declared positive-curvature launch range; confirms `0.0077` is conservative | D2A audit SHA `bc904a2e...a09`; exact minimum recomputed by `verify_reconciled_authority.py` |

The displayed independent `q'` interval must be read from the sealed payload,
not reconstructed from the rounded numbers in this table. The table's role is
navigation; `THEOREM_INTERVALS_EXACT.json` and the bound parent artifacts are
the arithmetic authorities.

## Reconciliation decision

The older consolidation listed two publication-critical gaps:

1. a producer-independent D1 interval-ODE replay; and
2. complete enclosures of curvature, lengths, warp positivity, the first
   integral and both wall identities.

Both are now closed by the sealed classification
`INDEPENDENT_D1_REPLAY_AND_GEOMETRIC_ENCLOSURES_PASS`. The original D1
producer remains useful because its higher-resolution root and event
enclosures are narrower. The independent replay is not a third physical
result; it is independent proof authority for the same reduced root.

One diagnostic is retained: the independent curvature-interval width is
larger at 16,384 than at 8,192 steps by a factor `1.0000297219462309`, while
both intervals are strictly positive. Monotone narrowing of every derived
quantity was not a frozen theorem gate; exact interval-Newton nesting was.

## Strongest current theorem claim

For the fixed declared reduced static Einstein--scalar two-brane problem, a
locally unique positive-curvature shooting solution exists when the proper
separation is selected by the first upper-Israel event near `D=1.9975`.
Under the same action, parameters, orientation and launch family, no
positive-curvature solution satisfies both upper-wall equations at the fixed
original separation `D0=0.9996389747145851` anywhere on `0<=a<=v0`.

This remains a statement about the reduced static family. It does not provide
stability, a dynamical radion transition, selection by collapse, an event
horizon, or a baby universe.
