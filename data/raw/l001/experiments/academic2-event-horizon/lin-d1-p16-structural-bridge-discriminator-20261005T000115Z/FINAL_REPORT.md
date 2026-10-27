# Lin D1--P16 structural bridge discriminator

Date: 2026-10-05  
Status: **complete; bounded structural obstruction**

## Outcome

The discriminator succeeds as a bounded negative result:

> **No invariant-preserving join exists between the sealed D1 and P16 lineages by coordinate reparameterization, orientation reversal, regular field normalization, gauge/source-reference change, fixed-model static continuation, or any already-derived complete solution family in the bound evidence.**

This is not a universal no-go theorem. It does not exclude a newly constructed dynamical family, and it does not establish that P16 descends from D1.

The result moves the bar from the earlier component observation that only 32 of 72 wall-jet checks agree to a structural statement about the endpoints: the failed join is not repairable by the allowed transformations because several physical invariants and exact model data disagree.

## Exact obstruction

Three independent obstructions survive every allowed equivalence operation.

1. **The exact actions differ.** The sealed D1 upper-wall tension is `-6.052844277744164`; the authenticated P16 value is `-6.052844277744802`. Their exact serialized gap is `6.38e-13`. Under the frozen exact-literal rules, replacing one by the other would be retuning, not a transformation.

2. **The invariant proper wall separations are disjoint.** D1 has
   `D in [1.9974975585936363, 1.9976196289063637]`. The P16 lineage declares
   `D0 = 0.9996389747145851`, while its archived background value is
   `0.999638958045782`. The minimum gap to the D1 interval is about `0.9978586`.
   Coordinate changes, wall exchange, gauge choices, and source-reference choices cannot alter this proper length.

3. **The collapse-scalar configurations are inequivalent.** D1 fixes `chi` identically to zero. In the authenticated P16 array, the scalar is nonzero at all 31,089 nodes, ranges from `7.6511864725009e-26` to `8.679231221974147`, and has a largest adjacent change of `0.219216913644388`. An invertible regular field redefinition cannot map a nonconstant field to the identically zero field.

The static continuation route is separately closed within its certified scope. The D1 fixed-`D` audit gives nonzero determinant enclosures `[2221.879246216278, 2224.53955879436]` and `[2220.8647309726075, 2225.5545418744878]`, so the D1 root is locally isolated in the declared reduced family. At the P16-line value `D0`, the D2A cover excludes the corresponding D1-action positive-curvature wall solution with residual lower bound `0.0077`. Because the P16 wall-tension literal differs, D2A is used only for the fixed D1 action and is not extended to the P16 action.

## Evidence classification

- **Certified/established:** D1's unique positive-curvature root and its scoped isolation; the D2A exclusion at fixed D1 action; all parent hashes; exact action-literal inequality; disjoint proper lengths; nonconstant P16 scalar array; 32/72 direct wall-jet outcome.
- **Numerically authenticated:** the P16 `q0` scalar statistics and raw-array hash; the latest P16 position-wall residuals.
- **Formulation-level evidence:** D1's equilibrium-preserving generalized-harmonic formulation and short stationary preservation observation. Its raw two-level GH gate remains pending.
- **Incomplete endpoint evidence:** the latest P16 boundary run did not obtain global initial data. Its lower and upper position-wall residuals, `2.371631764690...e-7` and `1.171209412399...e-8`, both remain above the `1e-8` gate.
- **Not established:** a universal impossibility theorem, a D1-to-P16 ancestry relation, global P16 initial data, long-time D1 stability, or a causal evolution linking the endpoints.

## Publication consequence

The defensible publication statement is a bounded structural non-identification: the present D1 theorem packet and P16 collapse packet are not two representations of one already-established solution, and the failed 72-channel join cannot be repaired by gauge, coordinates, orientation, source convention, or regular normalization. They must remain separate lineages unless a new constrained family is derived.

The article should not call this a universal no-go, a proof that no dynamical bridge exists, or evidence that P16 evolved from D1. The exact action mismatch must be disclosed if the two datasets are compared.

## Remaining gap and next justified calculation

The unresolved mathematical question is whether a nonzero collapse scalar can bifurcate from D1 once its quadratic stress and the induced radion/geometry response are solved consistently. The minimum lawful successor is therefore a **D1-fixed-action second-order collapse-scalar tangent test**:

1. retain the exact D1 action, walls, chart, gates, and proper-distance definition;
2. declare one small amplitude `epsilon` and one transported normalized scalar profile before evaluation;
3. solve the order-`epsilon^2` Hamiltonian, momentum, wall, axis, gauge, and outer-boundary system, including the radion response;
4. test the resulting boundary operator and cokernel independently;
5. only if solvable, validate a small nonzero-`epsilon` family.

Such a family would be a new D1-based construction. It should not be labeled P16, and it would not by itself establish ancestry or global collapse.

## Verification and artifacts

`verify_obstruction.py` binds the seven controlling inputs by SHA-256, recomputes the action, proper-length, scalar, wall-jet, static-isolation, and endpoint-readiness tests, and writes `RESULT.json`. `independent_verify.py` rehashes every parent and independently rechecks the decisive arithmetic and scope; its result is recorded in `POSTRUN_AUDIT.json`.
