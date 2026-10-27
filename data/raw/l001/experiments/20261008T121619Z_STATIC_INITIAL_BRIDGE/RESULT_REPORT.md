# Static-to-initial bridge: static-half result

## Outcome

**The explicit initial coordinate/lapse map is consistent, but the continuum bridge is not yet certified.** Static-half classification: `STATIC_INITIAL_BRIDGE_INCOMPLETE`.

This test identifies a specific scope gap rather than a disagreement between the two actions or a failure of the coordinate map. The static theorem certifies a three-correction C4 family. The newer initial datum solves a five-correction C6 problem that includes two physical seventh-jet directions. Those additional directions are not covered by the old theorem.

## Positive results

- The six exact action and wall literals agree.
- The derived metric pullback, outward-normal convention, proper-distance identity, areal radius and normalized wall-clock definitions agree algebraically.
- Both saved numerical levels pass the original spatial Israel/scalar rows, wall lapse identities, coordinate-integral comparison and inverse-map checks.
- The finest saved polynomial map has a rigorous outward lower bound `dx/ds >= 0.9999849945306778`. This is the **dx/ds** convention; the older roughly 0.135 margin refers to the reciprocal convention. No sign discrepancy is implied.
- Conformal coordinate length X is approximately **6.37829309444866**; proper wall separation L is approximately **1.99729959214464**. They are different quantities, connected by the explicitly tested metric pullback.
- Across the two saved representations, the largest sampled field/observable disagreement is **3.40e-50**. At 100 digits, Taylor-integral versus direct Gauss quadrature differs by **1.19e-87**, and the largest original spatial wall row is **1.68e-49**.

These small numbers concern arithmetic/representation consistency. Both levels share a saved source; they do not establish that source's continuum error. The diagnostic 65-node samples are not an evolution-grid admission.

## The concrete membership witness

At fixed source and epsilon, the certified C4 scalar correction has degree at most eleven. The new physical datum has a nonzero degree-fifteen term,

    coefficient(s^15) = (dc7_L + dc7_R)/(7! D^8).

No choice of the old (a,b0,b1) absorbs that term. The independently reconstructed scalar change at the material midpoint, hence at the corresponding common proper distance when ell,D and target amplitude are held fixed, is approximately **1.040972320008263e-7**. This is a physical scalar-profile change, not a relabeling of s as x. The tiny stored-epsilon offsets are recorded separately.

This is an exact polynomial-structure exclusion within the common **saved-source C4 ansatz**. It is not an exclusion of every continuum C6 solution, every C4-compatible datum, or a broader integration of the lines. The C6 datum can satisfy the lower C4 wall conditions without belonging to the particular three-correction family previously certified.

## Error bounds that do transfer—and those that do not

For the original admitted C4 representative at common normalized material coordinate, the existing material enclosures and a conservative enclosing static k,D range give:

| Observable | Conservative relative-error upper bound |
|---|---:|
| Areal radius | 1.79405e-6 |
| Initial lower-wall normalized clock | 1.73698e-6 |
| Proper separation | 6.54637e-5 |

The separation bound uses the broader P01 event interval and is not presented as optimal. **None of these is a C6 error bar.** Full exact lapse/inverse-map bounds are not inherited from material-field bounds alone.

The derivation gives an explicit conditional transfer: if EA, El, Eq, ED bound the log-field, lapse and domain errors, EJ=EA+El+Eq+ED controls the coordinate integrand multiplicatively. A positive normalized-map derivative then controls the inverse and the pullback of observables. Eq and the required C6 high-jet enclosures are still missing; observed precision agreement cannot replace them.

## What this means for integrating the lines

The lines already share an explicit action, physical normalization and usable coordinate/observable map. The missing step is **enlarging the physical preparation certificate**, not identifying a new gauge convention. A focused successor would certify the five-unknown C6 completion at the existing positive-amplitude datum and propagate its validated high-jet bounds through the lapse and inverse map. Uniform amplitude continuation is a later, separate question.

That successor is prospective and was not launched. No evolution, mode/root/metric re-solve, parameter rescue, manuscript edit or Git operation occurred.

## Verification and exchange

- Producer: Linux CPU 4, one arithmetic thread, 10.13 seconds, peak RSS 134.3 MiB; two atomic completed-level checkpoints.
- Separate audit: **61 checks passed**, with an independent exact-rational Hermite/degree witness and decision/integrity reader. It is not a second numerical integration or an independent continuum theorem.
- Producer RESULT SHA-256: `c6910736f93c6de1155c4dcd3cb05fb4f7544249e78302556163d11a5dbd35cc`.
- Audit SHA-256: `3a99ab173b717c86b0f0bbd65acb8e2374b44c4a723edba243fa0c1581fa0fa5`.
- Binding SHA-256: `21f2ef4758ce540f19f115604d60f69a7e0d476373bb16bfd45a5c9d911110aa`.
- Complete source, derivation, checkpoints, runtime and audit: [static working folder](</Users/ronbibb/Research/research_repositories/lin/lines/L001-static-theorems-causal-extension/experiments/20261008T121619Z_STATIC_INITIAL_BRIDGE>).
- The exchanged packet binds exact local input/output paths and hashes. The initial-data owner is to perform the independent scientific membership/corner review before issuing a joint classification.

