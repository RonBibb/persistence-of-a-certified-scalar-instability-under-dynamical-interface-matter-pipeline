# O4-R1 addendum to the two-hour causal-extension report

The original `WINDOW_REPORT.md` remains the issued scientific checkpoint.  Its
issued SHA-256 was
`946d71b4713c4e10be0e6009c31220505e036dd065585f55a79955bcba8efeac`.
The current local bytes have SHA-256
`d68b434b753de5d4ef2a62b646a6a40a8e739ca68ceba2c6d121e8f87365c548`;
the difference is one terminal-newline normalization introduced when the O4
addendum was separated, with no scientific content change.

The manager authorized one fixed-state diagnostic before the original cutoff.
O4-R1 started at 2026-10-01T11:30:21Z and completed without evolving or
changing a state.  It directly measured the branch-01 compatibility quantities
on authenticated P407 H-steps 512, 1152 and 1792 under the active
qualified-batched kernel.

The upper-wall incompatibility is present.  At radial index 35,
`E_ll/T_ll` is -0.005426, +0.006264 and +0.003723; the scalar-wave residual is
+0.1079, -0.09059 and -0.2134.  Meanwhile the wall solver's own raw
coordinate acceleration-level rows remain at approximately 1e-12; the
displayed normalized geometric normal row remains about 1.44e-6 to 1.73e-6.
The result changes sign and does not decay monotonically.  Thus the present
P407 lineage is not cleared as a physical parent for a longer event-horizon
reconstruction.

The appropriate next priority is the common bulk-wall-compatible initial and
boundary construction identified by branch 01, followed by a short evolution
companion and remeasurement—not another long extension of the current
lineage.

## O4-R1 artifacts

| Artifact | SHA-256 |
|---|---|
| `O4_CONTRACT.json` | `9af398d12d397d1bc096e41b005cd026624359551e7dc4d8611f7059a11b3194` |
| `O4_PROTOCOL.md` | `07edde24194e2de5e74e46656793e6a51d1a8a38772690d3089f8c4d01459c21` |
| `o4_late_compatibility.py` | `fe981452cfddc16e9e2de2a270ec8eb72d0f6ffdcb135fcbff3c75c8d8866a07` |
| `o4r1-output/O4_RESULT.json` | `ff74064aa6584245c2d7a6491165b1c695631f14e0031acfa87d6693c17f765e` |
| `o4r1-output/arrays.npz` | `49962a936d7288718fa801400101afbcd485e8c78bdbeb3a91b08f6ec50b0950` |
| `O4_INTERPRETATION.md` | `6ac3d18a4ae7cc454c6e5843d913561c0da0b233aad2832cb0849b98caf9ae32` |
| `O4_INDEPENDENT_INTERPRETIVE_REVIEW.md` | `68f5c926b0787305575a98152adb292d7e43c8a4a301fe7fc5945a6f7bbaf534` |
| `o4-output/FAILURE.json` | `795136184830a7a9b20651d79bb7aef0dac391694653dc990f6dc69fdffd0ada` |

The first O4 namespace failed only while serializing a completed H-step-512
checkpoint containing long-double scalars.  It produced no scientific result.
O4-R1 used a rebound source hash, a new immutable output namespace, and the
corrected scalar serializer.

No predecessor, manuscript, submission, archive, or external record was
modified.
