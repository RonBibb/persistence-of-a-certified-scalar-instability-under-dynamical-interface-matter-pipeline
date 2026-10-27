# Independent postrun review: connected signed C4 branch

Decision: **PASS**, `CONNECTED_SIGNED_C4_BRANCH_CERTIFIED`, on the exact closed amplitude interval `[-1/200000,1/200000]`. This is the same prepared central-D1 initial-data family and fixed admitted exact background/normalized physical mode as the sealed signed-sample predecessor. No producer rerun, physical IVP replay, parameter change, gate waiver or successor was performed during this audit.

## Independent scientific decisions

The read-only verifier reconstructed the interval fixed-point image and weighted derivative norm using exact rational arithmetic on the published native `G_center` and `J_box` balls, with the frozen common box radii `(1/100000,1/10,1/10)` and `C=diag(-24/23,1,1)`. Displayed values below are rounded; the receipt retains the exact fractions used for all decisions.

| Node and exact amplitude tile | Largest image/radius | Largest weighted row norm | Decision |
|---|---:|---:|---|
| r: `[-1/200000,1/200000]` | 0.9842209516765048 | 0.01918812606226023 | Fails unchanged strict 0.9 image gate |
| rl: `[-1/200000,0]` | 0.8498250811996619 | 0.01890744234966624 | Pass |
| rr: `[0,1/200000]` | 0.8490598978355058 | 0.01824022899230211 | Pass |

All three components of each accepted leaf pass the strict 0.9 image bound, and both weighted contraction norms are below 1/2. The failed whole-interval parent remains non-certified despite its ratio being below one. Only the predeclared first bisection was used; no quarter tiles or altered boxes are present. The exact accepted closed union is the whole target interval, without an unresolved tile or gap.

For every fixed amplitude, the same exact-source map is a contraction on the identical common box. Its unique root therefore agrees at the shared zero endpoint of the two leaves. The analytic map and invertible correction derivative give local analytic dependence; uniqueness glues these local roots into one connected branch. This statement does not choose a different background or mode as amplitude varies.

The old signed root images were independently recomputed, translated by their authenticated old centers, and proved entirely inside the new common box. Their component absolute-radius ratios are `(0.3276071042,0.007216202187,0.09609579201)` at the negative endpoint and `(0.3268109412,0.007212275657,0.09608407447)` at the positive endpoint. Thus uniqueness identifies both old signed samples with this branch; mere overlap of boxes was not used. The inherited rounded example-epsilon strings remain metadata, not exact amplitudes: center translation uses exact `+/-1/200000` and the original `A0`/fifth-coefficient strings, as already disclosed in the predecessor audit.

At zero, the authenticated independent algebraic identities, unchanged physical source and rechecked zero control establish `G(0,0)=G_epsilon(0,0)=0`. Hence `x(0)=x'(0)=0` in the shifted chart and the physical tangent remains `(psi,-2psi,f)`. The accepted local C4 family is inside the common box sufficiently near zero and agrees there by uniqueness. No extrapolation of its tiny quantitative radius is needed.

## Integrity, enclosure coverage and execution

The audit authenticated the frozen configuration, exact model/root/event/mode domains, all source/review/input bindings, final `analytic-control-05` receipt (45 new plus 15 inherited controls), runtime executable/libraries/environment, ancestor manifests and graph terminal evidence. It checked 1,122 source/review/input hash links and 43 runtime links; 1,575 distinct canonical file paths remained unchanged (1,581 recorded path references before alias normalization).

All 390 current checkpoints passed guard, digest, filename, phase, native-ball roundtrip, parameter, canonical interval-epsilon, common-source and traversal checks. The audit examined 106,422 current native interval representations. It separately rechecked 129 inherited source/zero checkpoints and 18,188 inherited representations; those are not included in the current counts. The complete upper-wall event bracket is covered in both center and box flows by the two adjoining exact intersections `[32727/16384,4091/2048]` and `[4091/2048,32729/16384]`. Preparation remainder domains cover `hull({0},I)` and only the proved constant/linear coefficients are removed. Required wall-diagnostic positivity, source consistency and the original-root-equivalent map premises passed.

The six flows contain 98,190 validated cells; the two accepted leaves account for 65,460. Maximum Picard count is 3. Recorded cumulative validated step-loop CPU is 1,286.390375 seconds, within the declared 7,200-second scope; this is not an all-process CPU measurement. The producer completed before authorization for the sole serialized verifier, which exited successfully on its first attempt. The successful stdout JSON was preserved directly, without manually retyping its rational payload. A subsequent read-only Linux process check returned no matching packet runner, serial launcher or auditor at approximately 01:19 UTC on 2026-10-06.

Independence is at the derivation, provenance and rational decision layers. The new graph/coverage/endpoint audit is separately written, but reuses this reviewer's hash-authenticated predecessor Fraction/native audit primitives and inherits the reviewed Arb/Taylor/Picard enclosure implementation. It is not a second disjoint physical integration. Exact rational products on published balls are slightly sharper than the producer's additionally rounded Arb products; the scientific decisions agree and all gates are applied to the published enclosures, not to rounded decimal summaries.

The staged `RESULT_REPORT.md` was read for claim scope and is consistent with this acceptance. The result establishes connected finite-amplitude C4-compatible initial data, uniqueness only in the declared correction box, both endpoint identities and the original mode tangent. It does not establish all-order wall compatibility, a hyperbolic spacetime-existence theorem, evolution, collapse, horizon formation or causal fate.

## Exact audit bindings

- Frozen guard: `20151671f46efccf55d0a6aba012acaef477eb1705e922d454ede5d3b3104412`.
- `postrun_audit.py`: `3326e1b057acad47eb281462742dd499ad76046bb4c670ec744802efb2077023`.
- `INDEPENDENT_AUDIT.json`: `de21f24f9ac427fcdffe7e54ba1ef0c86fe5e812130b6cf50fe440e133756006`.
- Graph terminal evidence: `4f5ce6c67fce01deee01d930638d5f302cf5d7d20727427ec0726f9603280b9b`.

Audit artifacts were written only in the new Research staging directory. Frozen production and all parent files were read-only throughout.
