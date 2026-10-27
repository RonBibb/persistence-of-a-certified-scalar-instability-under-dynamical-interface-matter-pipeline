# Independent postrun review: both signed C4 samples certified

Overall audit: **PASS**. Both finite-amplitude certificates are independently
accepted for the exact targets epsilon=+1/200000 and -1/200000 in the unchanged
three-variable C4 D1-native preparation.

Independent classification:
`BOTH_SIGNED_FINITE_AMPLITUDE_C4_SAMPLES_CERTIFIED`.

## Decisive result

The read-only verifier reconstructs the published native midpoint/radius balls
as exact rational intervals and independently forms I-CJ, the fixed-point image,
and the weighted infinity norm. It does not import or rerun the producer IVP
kernels. The ratios below correspond to (a,b0,b1), using the fixed half-widths
(1e-5,0.1,0.1) and C=diag(-24/23,1,1).

| Exact epsilon | Image-radius ratios, approximately | Maximum weighted row norm |
| --- | --- | --- |
| +1/200000 | (0.326476262, 0.005806538, 0.094788077) | 0.017638499 |
| -1/200000 | (0.327272564, 0.005809100, 0.094795805) | 0.018331077 |

Every image ratio is strictly below 0.9, and both norm bounds are below 1/2.
The audit JSON records the full exact rational values. These decisions use the
published, outward-canonicalized intervals, not potentially narrower transient
values. No equality between separately rounded interval products is required.
The strict margins remain ample after publication widening.

For each sign, this establishes a unique zero within its declared box for the
same fixed exact admitted background and physical mode. The retained Israel
row and the proved analytic row equivalence transfer that zero and its local
uniqueness to the original full fourth-time boundary map. Both fifth-control
metric responses and nonlinear q(A) terms remain included.

## Source, enclosure and recovery checks

The full original background root, event interval and accepted mode-mass bracket
match the inherited exact input records; all six action parameters match. No
shortened root/event enclosure, fitted source profile or replacement mass was
used. The saved numerical examples enter only as rational center coordinates.

The source enclosure, zero control, and all four signed center/box flows cover
the complete event interval with the same two exact pieces:

    [32727/16384,4091/2048] and [4091/2048,32729/16384].

Each flow has 16,365 validated cells, totaling 98,190. Both signed cases have
maximum Picard construction count 3 in each phase; the source maximum is 1.
The source wall values, Robin rows, background/mode constraints and regular
low-order jet relations are interval-consistent with the certified carrier.
This is not a claim that every point in the bounding rectangle is an eigenmode;
the accepted exact physical source is the common object enclosed throughout.

The zero map contains zero, with first-row absolute bound below 3.14315e-205,
and the two reduced fifth rows satisfy the identity-matrix control. All required
positive interval quantities and finite-state checks pass. The preparation
records retain the full epsilon remainder evidence; the largest recorded
eighth-order W remainder bound is below 5.287e-21. The preflight symbolic
identities justify only the exact constant/linear cancellations actually used.

The audit verifies all 389 checkpoint guards, content digests, names, contiguous
phase sequences, native constructor round trips, parameter domains, publication
links and complete-event records. It checks 88,632 native interval representations
across the evidence it reads. Center/full-box published maps agree with their
terminal phase checkpoints. The producer classification and both return codes
agree with the independent rational decisions.

All 650 source/review/input hash links and 43 runtime links pass, covering 1,111
unchanged files in the read-only audit. The sealed parent manifests retain all
159 Cauchy, 144 local-C4 and 326 central-spectral entries. The 15 packet-local
analytic controls match the frozen sources and runtime. Shared Arb arithmetic
and the disclosed Taylor/Picard/recovery primitives remain shared; this is not
a claim of an independent arithmetic library or a second physical integration.

Recorded integrated-flow elapsed times are 10.51345 s for the source,
186.61782 s for zero, 430.68899 s for the positive case and 438.29655 s for the
negative case. The signed workers ran concurrently, so these must not be added
and described as graph wall time. A read-only Linux process check at
2026-10-05 23:24:11 UTC found no matching packet graph launcher or worker.

## Verifier correction and claim boundary

During audit preparation, an assertion incorrectly treated the old example's
printed epsilon as an exact input. Inspection showed the saved metadata differs
from the exact target by -3.348486e-87 for the positive example and +3.348486e-87
for the negative example. The contract never used those rounded metadata values
as amplitudes. The verifier was corrected before the final audit to record the
offset and authenticate the actual centers as old A0 minus the exact target,
plus the exact decimal fifth-coefficient strings. All production epsilon values
remain exactly +/-1/200000. No production source, input, tolerance or acceptance
gate was changed.

This result certifies two nonzero members of the same prepared initial-data
ansatz, one at each stated sign. It does not certify a connected epsilon interval
or continuation of the tiny-radius branch all the way to these samples. It
does not establish all-order boundary compatibility, a hyperbolic spacetime
existence theorem, a time-evolution outcome, a horizon or any other research-line
claim. No restart, successor or additional amplitude was run by the reviewer.

## Bound evidence

Frozen guard:
`3e790eafe0a899d900e94ed8bf4adf2e268e5bab6bf96676ffd4680dc05845b4`.

Producer graph RESULT SHA-256:
`ca508f3a2e75755dfddc07f8ab5e6c85ca7fe260dd805f7574aae6a70cb3ebd1`.

`postrun_audit.py` SHA-256:
`8ae051f604f2828db3706b0e56877b4346ab8655392febe79863e84856af8716`.

`INDEPENDENT_AUDIT.json` SHA-256:
`45b98ae11d339236018be469f6d2b162cdb7b13e5aa6be09453c45a58aa99639`.

The earlier PREFLIGHT_REVIEW and both independent symbolic derivations/receipts
are authenticated by this packet's frozen bindings. This postrun review and
receipt are new audit artifacts only; no frozen or predecessor file was edited.
