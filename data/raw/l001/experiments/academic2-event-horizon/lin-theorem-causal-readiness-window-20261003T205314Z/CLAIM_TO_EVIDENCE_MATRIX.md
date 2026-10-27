# Claim-to-evidence matrix

This matrix applies the article-body rule: identify the risk, predeclare the
criterion, report the decisive outcome, and state the resulting inference.
Only the rows marked **main article** belong in the primary narrative.

| Claim or control | Risk addressed | Criterion | Decisive outcome | Permitted consequence | Placement |
|---|---|---|---|---|---|
| Reduction from the five-dimensional action to the proper-distance IVP | The certified root could solve the wrong equations or junction conditions | Derive the bulk ODEs, constraint, first integral, launch data, first-event residual, and fixed-distance residual from one fixed convention | Exact algebra checker passes five identities; the junction audit matches both normals and half-Robin factors | D1 and D2A are certificates for the declared reduced model | Main article + derivation appendix |
| Variable-separation positive-curvature solution | A numerical shooting trace could miss nonexistence or mistake a near-zero for a root | Strict interval-Newton self-map, transverse first event, nonzero total shooting derivative, positive curvature | One root in the frozen interval; `D` near 1.9975; `G_s<0`; `q'>124093`; `k>0` | Existence and local uniqueness in the frozen root interval | **Main article** |
| Producer-independent D1 replay | The result could be an implementation-specific enclosure error | Independent Taylor--Picard flow and interval Newton reproduce the root and enclose the geometry without importing original enclosures | Both 8,192- and 16,384-step levels pass; fine root, curvature, warp, conformal length, first integral, and wall identities are enclosed | The existence certificate is not dependent on one producer implementation | **Main article**, compact; details in supplement |
| Fixed-separation positive-curvature exclusion | A root at the prescribed separation could have been missed by a local or sparse scan | Exact contiguous cover of the full declared launch interval; every box discharged with zero unresolved cases | 693 boxes: 20 negative-curvature, 670 both residuals exclude, 1 Israel-only, 2 scalar-only; residual floor exceeds 0.0077 on the positive route | No positive-curvature simultaneous wall root exists at exact `D0` within `0<=a<=v0` | **Main article** |
| Paired separation mismatch | The factor-of-two separation difference could be ordinary tolerance error or a missed launch value | D1 and D2A must share the action, parameters, orientations, and launch family, while certifying their distinct separation conditions | D1 selects `D≈1.9975`; D2A excludes exact `D0≈0.999639`; exact arithmetic gives `D/D0` in `[1.998218966,1.998341081]` for the narrower D1 enclosure | The mismatch is intrinsic to this reduced static family | **Main article**, headline inference |
| Exact provenance and cross-platform replay | Copying, path assumptions, or stale records could detach the prose from the certificates | Verify all bound SHA-256 values and classifications on macOS and Linux with dependency-free checks | 107 reconciled checks and 21 bound hashes pass on both systems; Linux required a documented portable-root fallback | Existing sealed evidence is internally consistent and portable at the certificate-verification level | Supplement/archive |
| Novelty boundary | Established scalar-brane or rigorous-numerics results could be relabeled as new | Compare the exact paired theorem, not its individual ingredients, with the closest primary literature | Curved scalar-brane solutions, parameter-selected distance, and computer-assisted Einstein existence already exist; the exact pairing was not located in the focused search | Use model-specific “to our knowledge” language; do not claim a new stabilization principle | Introduction/discussion |
| Static-family limitation | A reader could infer stability or dynamical selection from a static certificate | State every excluded inference adjacent to the theorem and in the conclusion | Neither D1 nor D2A evolves perturbations or constructs Cauchy data | No claim of stability, radion evolution, collapse, MOTS, event horizon, or baby universe | **Main article** |
| Future causal-readiness contract | An attractive null-ray result could be run on incompatible data or tuned after inspection | Require same source and boundary data, a 2x2 short-development compatibility matrix, separately solved domains, held-out terminal surfaces, convergence and tail gates | Prospective contract only; no compatible evolution admitted in this window | Defines what a later causal calculation must prove; supplies no present physical result | Separate future-work document |

## Central article logic

The article should make only one vertical argument:

1. the fixed action and junction convention define two related reduced
   boundary-value questions;
2. interval methods prove a locally unique variable-separation solution;
3. a producer-independent implementation reproduces and geometrically encloses
   that solution;
4. an exhaustive exact cover excludes the required fixed-separation solution;
5. therefore the separation mismatch is a certified feature of this fixed
   reduced family, not a missed numerical root.

The number of checks is not the novelty. The paired inference is.
