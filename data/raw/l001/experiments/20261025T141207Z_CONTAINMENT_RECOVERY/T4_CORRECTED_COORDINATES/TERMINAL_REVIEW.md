# T4 corrected-coordinate terminal review

**ACCEPTED — PASS_IMPLEMENTATION_CORRECTED_TRANSITION_COORDINATES**, conditional on the pinned outward Arb arithmetic and reviewed interval algorithm. This is a new corrected-implementation certificate; neither failed predecessor becomes a pass.

I inspected both level records, final result, controls, execution and current source identities against prospective admission. The two recorded workloads are 3072 and 6144 steps, totaling the fixed 9216. Both report all whole-step tubes and level gates passed. The inspected code makes publication conditional on each strict containment/rectangle check, both Hamiltonian zero inclusions, positive determinant with identity-defect zero inclusion, analytical transfer containment and each threshold gate. Final result additionally requires unchanged source/runtime/failed-parent bindings, level overlap and nonincreasing fine widths.

The fine Hamiltonian intervals and determinant-defect interval have strictly negative lower and positive upper rational endpoints, consistent with their required zero inclusions. Transfer entries have the required positive, positive, negative, positive signs and remain within the broad accepted analytical enclosures. These identity inclusions are controls, not independent proofs of accuracy; rigorous enclosure relies on the inspected per-step first-exit construction and outward endpoint propagation.

## Accepted exact threshold bounds

| Threshold | Lower rational endpoint | Upper rational endpoint |
|---|---|---|
| Lower wall only | 599962461/17179869184 | 600092453/17179869184 |
| Upper wall only | 176023267/4294967296 | 704230505/17179869184 |
| Equal stiffness at each wall | 647809343/34359738368 | 323971661/17179869184 |

These are the unchanged n=2048 intervals copied into RESULT.json, not coarse/fine intersections. Approximate locations are 0.03493, 0.04099 and 0.01886 per wall, respectively. Exact rational endpoints, not the loose Arb display strings, are authoritative.

I independently compared the rational width/overlap gates. On denominator 2^34, the lower-only coarse interval is [599888089,600148064] and the fine interval [599962461,600092453]. The upper-only intervals on the same denominator are [704010700,704285567] and [704093068,704230505]. On denominator 2^35, equal-wall coarse is [647731112,647999062] and fine [647809343,647943322]. In each case the fine interval is actually contained in the coarse interval, stronger than required overlap. Fine width numerators are 129992 versus coarse 259975, 137437 versus 274867, and 133979 versus 267950, respectively. All are positive and pass the fixed 1/10000 width bound by direct integer comparison with their denominators. Thus the numerical gate does not depend on decimal rounding.

The inherited analytical map assigns two negative regular scalar modes below the appropriate threshold, one negative plus one massless mode at it, and one negative mode above it. These coordinate enclosures do not specify actual eigenmasses or growth rates. Intervals containing the threshold should not be classified as a particular side without further evidence. The equal-wall threshold is a per-wall value, not the sum budget.

## Execution and provenance

Execution began 14:23:32.387964Z before cutoff, used CPU0 with one core, exited zero and reaped child 1672212 after 0.6493699590209872 seconds. Producer time was 0.5513675000984222 seconds and peak RSS 36780 KiB. Runtime and final source-hash records match the declared Python 3.12.3/flint 0.9.0/256-bit/one-thread setup and admitted bindings. Current producer and plan hashes agree with prospective review. Original controls passed. No rates, resolutions, physical parameters, precision or acceptance thresholds were changed during the run.

This independent agent audit did not rerun the integration or use a second arithmetic library. It validates the source/result contract and exact recorded gates; it is not independent arithmetic replication or external peer review. No next test is admitted here.

| Artifact | SHA-256 |
|---|---|
| RESULT.json | 0e4530f949ee7c955ae8ec07c2a2208ebd8f20d9cdc45aca8590adf3e946250c |
| LEVEL_1024.json | 132557b37ea91f42436ac53574c3ef613eb47bd5e1c9c6d1b8c706228494949f |
| LEVEL_2048.json | ebb7e29ab62e396847219555569c412b9b39ba71709e80813a060d4487c5e652 |
| producer.py | e9e5b9639da106c0b0df90b07a1b5f4eb013a1e67e6bb6b0c776a4ecd4c80048 |
| PLAN.md | f2de0508244bd9126303f40144e22589f8a6ff903e8e92892511bc253a975fd1 |
| CONTROLS.json | 1b2fd89da26c077ccc2001d05eccda78c5f9528203c66dea08b593deb65becc0 |
| EXECUTION.json | 63270a5a166e3e8b170fe3ba2525702651f642380d4785addae2cd7eca36e3f3 |

No repair or further run is required to accept this bounded certificate.
