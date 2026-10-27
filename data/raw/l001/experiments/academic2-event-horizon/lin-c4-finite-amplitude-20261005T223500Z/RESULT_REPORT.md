# Two practical-amplitude C4 initial-data samples certified

Date: 2026-10-05. Classification:
`BOTH_SIGNED_FINITE_AMPLITUDE_C4_SAMPLES_CERTIFIED`.

## Result and research meaning

Both exact amplitudes epsilon=+1/200000 and -1/200000 (+/-5e-6) passed
the unchanged interval self-map and contraction gates, and the independent
postrun audit accepted both decisions. For the exact central D1 background
and a physical mode admitted by its source certificate, the original corrected
three-variable initial-data problem has a unique solution inside each declared
parameter box. The certificate includes the full inherited background-root,
mode-mass and upper-wall-event uncertainties. It does not replace them by
rounded example profiles.

This is a constructive advance: the earlier local theorem guaranteed an
analytic family only in an extremely conservative radius, |epsilon|<=2^-9216.
The present result certifies two actual nonzero sample amplitudes of the same
constraint/preparation family. It supplies more than small sampled residuals.
It does NOT certify every intervening epsilon, or identify a connected branch
from the tiny-radius theorem to these samples. Each sample is independently
unique inside its stated box.

## What the independent numerical decision says

The fixed unknowns are x=(a,b0,b1), where A(0)=epsilon+a. Their box
half-widths are (1e-5,0.1,0.1). The fixed preconditioner is diag(-24/23,1,1).
The scalar controls b0,b1 multiply the unchanged endpoint fifth-jet shapes;
these widths are certification boxes, not high-precision error claims about
the old numerical example coefficients.

For x -> x-CG(x), all three component images must lie strictly inside 0.9
times their respective box half-widths, and the weighted infinity norm of
I-CJ(X) must be <=0.5. The independent auditor recomputed these tests with
exact rational interval arithmetic from the published native midpoint/radius
payloads, not from the producer's Boolean decisions.

| Exact epsilon | Image/radius: a | Image/radius: b0 | Image/radius: b1 | Maximum weighted contraction norm |
| --- | ---: | ---: | ---: | ---: |
| +1/200000 | 0.326476262 | 0.005806538 | 0.094788077 | 0.017638499 |
| -1/200000 | 0.327272564 | 0.005809100 | 0.094795805 | 0.018331076 |

Every required gate passed. The strongest restriction is the a-coordinate
self-map enclosure, still well inside the predeclared 0.9 limit. The
eighth-order scalar-row epsilon remainder bounds are below 5.29e-21; no
Taylor remainder was silently discarded. The broad source enclosures remain
in the result, so these findings should not be described as a high-precision
measurement of the three correction coefficients.

## Why this is the original problem

The calculation retains the six exact central D1 action literals, the full
certified background root interval, the physical mode with psi(0)=1, the full
accepted negative mass bracket, both physical walls and the free physical
separation. No artificial boundary, fitted source, smaller amplitude or new
matter model was introduced. The C7 lift and both degree-eleven fifth-jet
shapes are unchanged.

An independent derivation compared the nonlinear fourth-time scalar boundary
polynomial directly against the original sealed time-jet implementation.
Curvature coupling survives at finite amplitude. In proper-normal variables,
the retained terms are -12c S(q-r)-24t(q-r)^2. The metric value q depends on
all three correction parameters through the full nonlinear metric IVP.

Replacing the metric slope in the two scalar rows by its Israel target is an
exact row operation: the old row minus the new row is the retained Israel
mismatch times an analytic factor. Keeping that mismatch as the first
equation preserves the original roots and their local uniqueness. The
calculation does not assume nonlinear triangularity. Both scalar-shape
parameters retain their complete interior metric response.

The centered metric equation A=W+epsilon psi+w removes only exact static and
linear identities. Independent symbolic checks show why the constant and
linear C7/fourth-row forcing coefficients vanish for the actual admitted
physical mode. Higher coefficients, interval remainders and nonlinear
curvature feedback remain. No identity is asserted for every arbitrary point
of an enclosing source rectangle.

## Work performed, recovery and audit

The finite graph contained precisely one fresh common source enclosure, one
zero-amplitude control, and one center plus one full-box evaluation at each
of the two signed amplitudes. No additional physical sample or retry was run.

| Phase | Validated cells | Recorded integration time |
| --- | ---: | ---: |
| Common source | 16,365 | 10.51 s |
| Zero control | 16,365 | 186.62 s |
| Positive center and box | 32,730 | 430.69 s |
| Negative center and box | 32,730 | 438.30 s |

The signed cases ran concurrently. There are 98,190 validated cells in total.
All six flows cover both exact upper-wall-event subintervals, without a gap:
[32727/16384,4091/2048] and [4091/2048,32729/16384]. The signed flows required
at most three Picard construction iterations per cell, inside the frozen
32-iteration limit. Source and zero-control consistency checks passed; the
zero Israel map enclosure is at most approximately 3.15e-205 in magnitude.

Linux runtime: Python 3.12.3, python-flint 0.9.0, Arb at 768 bits, one arithmetic
thread per process, fixed spatial step 1/8192, degree-four cell polynomial with
a fifth-order interval remainder, and an explicit degree-seven epsilon
expansion with an eighth-order interval remainder. No library was changed.
The source, zero and each signed case retained their predeclared time/memory
limits. Other research jobs and sealed parents were not altered.

The independent audit authenticated 389 atomic checkpoints and 88,632 native
interval representations, 650 source/review/input hash links, 43 runtime hash
links and 1,111 unchanged files. Parent inventories of 159, 326 and 144 files
remain intact. The audit uses independent rational decision arithmetic, but
shares the pinned Arb constructor and the reviewed Taylor/Picard numerical
primitives; it is not a second physical integration using a disjoint library.

Two development corrections are part of the record:

1. Before freeze, the reviewer found that a parameter-dict alias could survive
   checkpoint canonicalization. The production step now reads the restored
   state dictionary. A deliberately widening synthetic parameter interval and
   a fresh-process continuation check demonstrate the repair. The final 15
   narrow analytic/recovery controls pass. No physical outcome preceded freeze.
2. During verification, an initial auditor assertion treated rounded epsilon
   metadata in old numerical examples as an exact rational target. Those old
   values differ from +/-1/200000 by about 3.35e-87. The contract and producer
   already used the exact targets and only the old A0/fifth-coefficient strings
   as numerical centers. The auditor was corrected to verify those declared
   centers and record the metadata offsets. Production source and scientific
   gates were unchanged.

## Authority and artifacts

Frozen binding SHA-256:
`3e790eafe0a899d900e94ed8bf4adf2e268e5bab6bf96676ffd4680dc05845b4`.

The root RESULT.json and MANIFEST.json provide the final sealed authority and
complete file inventory. Supporting evidence includes:

- CONTRACT.md and CENTERED_IVP_DERIVATION.md.
- INDEPENDENT_NONLINEAR_ENDPOINT_DERIVATION.md and its exact symbolic receipt.
- INDEPENDENT_CENTERED_IVP_DERIVATION.md and its 14-identity receipt.
- PREFLIGHT_REVIEW.md and the bound analytic-control-04/RESULT.json.
- output/source, output/zero, output/positive and output/negative terminal
  records and immutable checkpoints.
- INDEPENDENT_AUDIT.json, postrun_audit.py and POSTRUN_REVIEW.md.
- FINAL_LIVENESS.json, confirming that this packet's production graph has exited.

Mac packet:
`/Users/ronbibb/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z`.

Linux mirror:
`/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-c4-finite-amplitude-20261005T223500Z`.

## What remains

This certifies initial data satisfying the original Hamiltonian and physical
wall conditions with compatibility through fourth time order at these two
amplitudes. It does not prove all-order compatibility, a hyperbolic spacetime
existence theorem, time evolution, a nonlinear endpoint, a horizon, or a child
universe. It neither certifies a connected epsilon interval nor claims the
old numerical example arrays are the exact solutions.

The next justified research step is the separately qualified evolution of
physical initial data, with its own constraint, boundary and convergence
controls. The other Lin chat owns that evolution qualification; this packet
does not import or endorse its unsealed outputs. The bounded static successor
is complete, and no further experiment was launched from it. Neither
manuscripts nor other research lines were changed.
