# Proposed public proof archive

## Purpose

This is a packaging plan, not an external deposit. It identifies the smallest
clean archive that would let a reader connect the paired theorem to its exact
inputs, inspect both independent existence certificates and the exhaustive
fixed-separation exclusion, and rerun the evidence checks. No sealed parent is
modified by this plan.

The public archive should be organized around the scientific inference rather
than around the chronological protocol history:

1. the action, ansatz, and exact parameter literals;
2. the reduction and theorem statement;
3. the validated variable-separation existence certificate;
4. the exhaustive fixed-separation exclusion certificate;
5. independent verification and environment instructions.

## Tier 1 — reader-facing theorem package

These files should sit at the archive root (renamed without timestamps if
desired) and explain the result without requiring knowledge of the research
directory structure:

- `README.md`: one-paragraph result, exact scope, commands, and directory map;
- `THEOREM_AND_PROOF.md`: the paired theorem and proof narrative;
- `FORMAL_REDUCTION_LEMMA.md`: action-to-IVP and fixed-distance reductions;
- `JUNCTION_CONVENTION_AUDIT.md`: normal orientations and half-Robin factors;
- `THEOREM_AUTHORITY_TABLE.md`: human-readable interval table;
- `THEOREM_INTERVALS_EXACT.json`: exact rational endpoints;
- `NOVELTY_AND_SCOPE.md`: bounded novelty and explicit nonclaims;
- `LICENSE` and `CITATION.cff` once the author chooses terms and an archive
  identity.

The present window supplies the source content for every scientific item in
this tier, including its own `README.md`. The clean archive must still adapt
the draft/scope filenames to the archive layout and add `LICENSE` and
`CITATION.cff` after the author chooses terms and an archive identity. A DOI or
public release must not be promised until an actual deposit is authorized.

## Tier 2 — core machine-verifiable evidence

The following bound files are the minimum scientific core. Sizes are current
uncompressed byte counts; hashes are SHA-256.

| Role | Bytes | SHA-256 | Bound source |
|---|---:|---|---|
| Action and parameter source | 5,559 | `4077686eb06ea8eea23d11b059336db877d8466f34b710f0fa416e116d343dc9` | `source-snapshot/brane-horizon-phase-structure/MODEL_V1.md` |
| Reduced BVP design | 11,981 | `5f73207bbab64947e5bf30de285c3bee7b221c5d97214f08d46ec1857208c55a` | `capture-to-model-2026-09-12/static-background-successor/PROSPECTIVE_BVP_DESIGN.md` |
| Original D1 result | 1,259 | `07b22a8bc27eb1884c5607004c8fa8590d603be6e6157f7332369fcbaaf278f9` | `lin-d1-high-resolution-confirmation-20261002T015100Z/RESULT.json` |
| Original D1 terminal | 484 | `914416d98779fc468f61629b8afdda7fb8d7251acc33b7cf42db929272e78f9d` | `lin-d1-high-resolution-confirmation-20261002T015100Z/TERMINAL.json` |
| Original D1 high-resolution wrapper | 872 | `98d17ad555c7012266debe9e406fab02eae6db6b57dbe41c53dc635c66e7fe09` | `lin-d1-high-resolution-confirmation-20261002T015100Z/confirm_32768.py` |
| Original D1 high-resolution manifest | 422 | `62ba3fa1d30b6baad17f52651b9da69492c622a52fc7c076fa7b891a89a66ade` | `lin-d1-high-resolution-confirmation-20261002T015100Z/MANIFEST.json` |
| Original D1 base producer | 13,598 | `9c711da262d49a58e23e51b84bd30efce3e5c2a8730ebbc44034ac1ec546f653` | `lin-d1-validated-sensitivity-newton-20261002T012953Z/validated_sensitivity_newton.py` |
| Original D1 refinement wrapper | 806 | `c388b3bd1e616f38dfa9a27be9d74cbe1de0b618386749e32fbc8a2de48896f3` | `lin-d1-validated-sensitivity-newton-r1-20261002T014500Z/validated_sensitivity_newton_r1.py` |
| Independent D1 producer | 21,003 | `d198c6e98d949190d479a33b3c5aadaee2021982e03141d0c1d252a0c370e044` | `lin-d1-independent-ode-replay-20261002T225837Z/independent_d1_replay.py` |
| Independent D1 R1 wrapper | 223 | `25e90b9b881787f8fd3d7f4e93bf2fb05ea64e2e30534f511c99b9911bdfe043` | `lin-d1-independent-ode-replay-20261002T225837Z/independent_d1_replay_r1.py` |
| Independent D1 result | 102,419 | `41077a7977079705dbd49379f2f9ecb3fe9c007c518b02277aba6aa4b8df7d16` | `lin-d1-independent-ode-replay-20261002T225837Z/output/r1/RESULT.json` |
| Independent D1 manifest | 2,059 | `61d48dd2b491ef9834aec104a179c9b6258e802a39bbb5af1d14efd28e4e0bd8` | `lin-d1-independent-ode-replay-20261002T225837Z/MANIFEST.json` |
| Independent D1 terminal | 1,170 | `c6ed5898252990dc3b87d006d82dba114312728955b7712cedb05c03094c2c47` | `lin-d1-independent-ode-replay-20261002T225837Z/TERMINAL.json` |
| Independent D1 audit result | 4,012 | `f51a3999efda6354360ff4ca621575730716b793c7bd075a0795e7681c2b4c76` | `lin-d1-independent-ode-replay-20261002T225837Z/POSTRUN_AUDIT.json` |
| Independent D1 audit source | 8,550 | `9ac648ec9d9cf2e4f1a639b860429146f56c3ad00a280ac0c31a46ed910be599` | `lin-d1-independent-ode-replay-20261002T225837Z/postrun_audit.py` |
| D2A cover producer | 22,455 | `b0110bbb5f5bdda9a69d9958dfba050389db4c375b3d9187e8d706f1be8a3691` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/d2a_validated_cover_r1.py` |
| D2A bindings | 1,157 | `92e613848d8ebf542b035ea65559dc700ac8ad96bdb2a41f8a00a53ec347c935` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/BINDINGS.json` |
| D2A frozen predecessor source | 5,990 | `af68d38340c950a1482c9796c97bec153cb584f7749aab54e8996ab87772346c` | `lin-d2a-fixed-separation-cover-20261002T020000Z/d2a_validated_cover.py` |
| D2A frozen predecessor terminal | 394 | `1f43d6d6887308d2b6d4ccb0360ce5d3cfb48439f3bac5fc9a07a600253e0ef7` | `lin-d2a-fixed-separation-cover-20261002T020000Z/TERMINAL.json` |
| D2A validated-flow parent source | 7,621 | `53bcaab6420d050bc4f7e3ca825f74390e0b59b20fe96feae10e72c32288dd3c` | `lin-d1-validated-flow-prerequisite-20261001T212157Z/validated_flow_pilot.py` |
| D2A validated-flow parent terminal | 554 | `0b559edc6f1ec9fe5bba78a0f31812aa773ad393f1040a7efc92c51844452f3d` | `lin-d1-validated-flow-prerequisite-20261001T212157Z/TERMINAL.json` |
| D2A result and complete terminal cover | 3,540,156 | `eb16a5e4bb027aaf598f954bdd48d51611a1c48ffc7669afabb6b3f3a3dea8a5` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/RESULT.json` |
| D2A terminal checkpoint | 885 | `79e9b26f4a88cdc6e525ebdc567612af8e102c859ae797ff88575f7f72c5a77a` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/TERMINAL_CHECKPOINT.json` |
| D2A preflight | 3,712 | `0163ef25fc8a42ec68b0019c71be558b25af79ab40baf1f4c331974cdcfa9173` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/output/PREFLIGHT.json` |
| D2A manifest | 1,082 | `c8130ed4b2605a567ce1716c84f919f898238aeb2dd10a4c9f04e28852b31e7a` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/MANIFEST.json` |
| D2A audit | 1,296 | `bc904a2e9d5baced7e2abfc0b846e7c25c609d3ce40a62a79d7ce47295bc5a09` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/POSTRUN_AUDIT.json` |
| D2A terminal | 770 | `47b35e77299a5b150d4c4f86a2ba1648654484c61ddd8b71235138d1cfddda5b` | `lin-d2a-fixed-separation-cover-r1-20261002T083633Z/TERMINAL.json` |
| Consolidated verifier | 11,507 | `b26329fe4bb58012e2cd86e6cbea49620375e6b8828ccafade5a016cd48b7424` | `lin-d1-d2a-theorem-consolidation-20261002T175556Z/verify_evidence.py` |
| Consolidated evidence index | 9,120 | `5219b74087747188ba6dcf3185a0d99e228cfcc0a0053489a44cfea396796ad5` | `lin-d1-d2a-theorem-consolidation-20261002T175556Z/EVIDENCE_INDEX.json` |

The listed core payload is about 3.78 MB before documentation and environment
metadata. This is small enough to accompany a manuscript directly.

## Tier 3 — full audit trail

The D2A run also has 86 immutable content-addressed checkpoint files totaling
150,880,312 bytes. They are valuable because the audit rederives the exact
cover and verifies every checkpoint address, but they are not required to read
the theorem or inspect the terminal cover. They should be included in the
public archival deposit when practical, while the article and a compact source
package should depend only on Tier 2.

The archive should exclude Python cache files, mutable status records, launcher
PIDs, temporary logs, stale trials, and failed predecessors from the executable
core. Scientifically material failed or incomplete studies can be listed in a
separate history file without being mixed into the proof authority.

## Required clean-build sequence

Before deposit:

1. copy, never move, the bound files into a new staging directory;
2. preserve each original path and SHA-256 in a generated manifest;
3. add an environment lock that identifies Python and the interval-arithmetic
   dependency used by each producer;
4. run the dependency-free algebra checker and reconciled authority verifier;
5. rerun the packaged consolidated verifier against the staged relative paths;
6. perform one clean replay on macOS and one on Linux;
7. compile the actual manuscript upload package and inspect every rendered page;
8. seal the archive only after all commands return zero and the output manifest
   is internally consistent.

The existing source-tree checks already pass on both platforms. They do not
replace step 5, because repackaging can introduce path or dependency errors.

The sealed production environment records Python 3.12.3 and `python-flint`
0.9.0 on Linux/aarch64. D1 uses 768-bit Arb precision; D2A uses 512-bit Arb
precision. The archive lock should preserve these versions while allowing a
separate compatibility replay under later versions rather than silently
substituting them for the proof-bearing environment.

## Archive claim boundary

The archive supports a computer-assisted theorem for the fixed reduced static
Einstein--scalar two-wall family. It does not support stability, dynamical
selection, collapse, trapped surfaces, an event horizon, or a baby universe.
