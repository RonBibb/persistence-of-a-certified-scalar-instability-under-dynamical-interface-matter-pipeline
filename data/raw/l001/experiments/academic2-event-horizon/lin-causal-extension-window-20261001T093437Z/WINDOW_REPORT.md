# Two-hour Lin causal-extension window — final report

Window: 2026-10-01 09:34:37Z to 11:34:37Z.

## Scientific result

This window did not establish an event horizon.  It did establish why the
current finite archive cannot yet provide one and reduced the next decision to
one short physical-fidelity measurement.

The stable late outer-MOTS surfaces are exact and reproducible across the
recovered N=(157,165,173) band.  When outgoing null sheets are launched from
four successive same-lineage terminal surfaces and evolved backward, they do
not collapse toward a terminal-independent sheet.  Their separation is
coherent, nearly affine in terminal-time gap, and about 35 times the measured
numerical envelope.  The current archive therefore ends while the terminal
MOTS is still moving outward; it is not yet a terminal attractor suitable for
event-horizon reconstruction.

The moving MOTS itself supplies the observed offset.  Its three successive
profile-increment vectors are almost collinear (cosines greater than
0.99999964), while their amplitudes damp by only about 0.63% per 16H terminal
gap.  Backward null propagation preserves that offset to within about 0.6%
over the available interval.  This is a concrete mechanism in the represented
geometry, not numerical scatter.

## Completed work

### O1 — terminal-seed interface

- Classification: `P407-R3-STABLE-BAND-TERMINAL-SEED-INTERFACE-PASS`
- Runtime: 999.84 seconds
- 240/240 lineage knots passed
- 12/12 full terminal certificates passed
- 12/12 terminal profile hashes reproduced exactly
- Independent verification: 111 checks, zero failures

O1 packages prerequisites; it is not a new physical result.

### O2 — multi-terminal backward-null localization

- Classification:
  `VALID-NO-EPOCH1-TERMINAL-LOCALIZATION-FUTURE-EXTENSION-REQUIRED`
- Runtime: 1600.97 seconds
- Nine of nine trace families passed all technical gates
- Null defects were about 1e-14 or smaller
- Numerical envelope: 0.009303915 native cells
- Four-terminal diameter: 0.328794 to 0.330726 native cells
- Localized common steps: 0/17, with 16/17 required
- Independent verification: 272 checks, zero failures

This is a valid finite-archive nonlocalization result.  It is not evidence that
an event horizon does not exist.

### O3 — boundary-applicability audit

- Shared P188/P220/P228/P232/P240/P395/P400/P407 prepared-state ancestry is
  confirmed.
- The executed P407-R2 run used qualified H, not the rejected 2H proposal.
- The structural wall route remains `legacy_wall_axis_outer`; all four optional
  P404 wall forcings are inactive (`None`).
- P407 after H-step 512 uses the P404 qualified-batched candidate kernel, which
  is not byte-identical to the older scalar kernel.
- The near-formation approximately 1.04% wall-focusing defect has not been
  measured on a P407 late state and must not be numerically transferred there.

Thus O1/O2 remain valid descriptions of the represented P407 geometry, while
their promotion to physical event-horizon evidence remains conditional.

## Next calculation

Before another long future extension, evaluate the independently reviewed
bulk-wall compatibility diagnostic on authenticated H-steps 512, 1152 and
1792 using the actual P407-R2 qualified-batched contract.  All three complete
q/v/source/memory endpoints already exist and have been inventoried in
`LATE_STATE_COMPATIBILITY_READINESS.md`; no evolution or interpolation is
needed.

If the defect is absent or demonstrably decays, extend to a later terminal
rung and repeat O2 unchanged.  If it is material and persistent, regenerate a
compatible spacetime before spending more compute on causal reconstruction.
If the diagnostic cannot be made representation-consistent with the active
kernel, report technical incompleteness rather than choosing either physical
branch.

After a later terminal rung localizes, a genuine event-horizon claim still
requires a defined causal exterior and independent escape/capture witnesses.

## Principal artifacts and SHA-256

| Artifact | SHA-256 |
|---|---|
| `RUN_WINDOW.json` | `4c286bac19f829bfb06d69b8d353820cbb2bc3d88563cc5bbdb59b28519f18aa` |
| `O1_CONTRACT.json` | `fe68166f3554ca1026e256a8cc3673fe2ef4f17fa23acb0a7303263dc4e3f0f7` |
| `o1-output/P407_R3_TERMINAL_SEED_INTERFACE.json` | `54d9bf58403f84526706432f9ed48ea354d7db3a201306f1b689b8b142119d6f` |
| `o1-output/P407_R3_TERMINAL_SEED_INTERFACE.npz` | `3810b250c4647bd38bbe43959eb86c6231785f9576954d2ff08f6f2cee76fa7c` |
| `o1-output/O1_INDEPENDENT_VERIFICATION.json` | `7536ea5477e297454d16bc799a7f9bf0aa7e52e7fdd9ce858bb4d7fc56365f14` |
| `O2_CONTRACT.json` | `f1a9a454ced633f44e841cf7cedb4f076533e74f0ee13312791d1dc88586ac19` |
| `o2-output/O2_RESULT.json` | `cb0a7a0f78bd0bf2bdf6ca6f148fbd9c03e0c4a4f53b4ea784835d982a5284c9` |
| `o2-output/O2_RESULT.npz` | `84a9ec553eeb7d920d55782d926325167856d440e3fd826bfb91d4f74fe52e90` |
| `o2-output/O2_INDEPENDENT_VERIFICATION.json` | `0ce9945c9ea3513e24c9f851227a06fbc33541b20adf519bd100e67ba89ec560` |
| `P407_BOUNDARY_APPLICABILITY_AUDIT.md` | `5da3aedde3488bca2d1b67fc28580d72251de8b6fb599fb7365a3503bdc7afd7` |
| `P407_BOUNDARY_APPLICABILITY_AUDIT.json` | `a7f7f60a84d8108358bc5dec9f53a42f2e610ea8225fd9a1960741bc687a0ceb` |
| `LATE_STATE_COMPATIBILITY_READINESS.md` | `e50f5cdc38e5d422467bbcc3802da3dba55c7da739c7941293487cb9ce14cb0e` |

No predecessor, manuscript, submission, archive, or external record was
modified.
