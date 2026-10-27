# Connected finite-amplitude C4 initial-data branch certified

Completed October 5, 2026 ET (October 6 UTC). Independent classification:
`CONNECTED_SIGNED_C4_BRANCH_CERTIFIED`.

## Result and why it matters

The corrected central-D1 initial-data family now has a certified connected,
locally analytic branch across the entire exact amplitude interval

    -1/200000 <= epsilon <= 1/200000   (that is, +/-5e-6).

For one fixed exact background and normalized physical mode admitted by the
unchanged source certificates, there is a unique correction x=(a,b0,b1) inside
the declared common box at every amplitude. This branch passes through the
zero-amplitude background, has the original physical-mode tangent, and
contains both previously certified signed endpoint solutions. There are no
unresolved amplitude gaps. The independent verifier accepted the complete
interval claim, not just the producer's Boolean result.

The preceding calculation established two isolated finite-amplitude samples.
It explicitly did not show that one could move continuously from the local
analytic family to those samples without switching solution branches. This
experiment closes that particular gap. It connects an infinitesimal physical
perturbation to a finite signed family satisfying the same prepared constraint
and fourth-time wall-compatibility problem. It is a positive existence and
connection result, not another exclusion or a collection of small residuals.

## What was kept fixed

The six exact central-D1 action literals, complete background-root interval,
physical-mode mass bracket and upper-wall-event interval are unchanged. The
already certified common source and zero control were reused read-only from
`lin-c4-finite-amplitude-20261005T223500Z`, with the full ancestor provenance
authenticated. No dense example profile was substituted for the source.

The physical preparation remains

    ell = -2 epsilon psi,
    Phi = Phi_star + epsilon f + C7(epsilon,s) + b0 H0(s) + b1 H1(s),
    A(0) = epsilon + a.

The same Hermite lift, fifth-jet shapes, full nonlinear metric backreaction,
Israel condition and root-equivalent fourth-time scalar rows are retained.
All three correction variables and their metric responses remain coupled.
The entire nonlinear curvature contribution is included.

Every amplitude tile uses the identical zero-centered correction box with
half-widths (1e-5,0.1,0.1), and exact C=diag(-24/23,1,1). These are proof-box
widths, not precision estimates of the physical correction coefficients.

## Uniform certificate and the measured outcome

For each closed amplitude interval I, the validated calculation encloses
G(I,0) and the full derivative G_x(I,X), including source uncertainties. The
same two frozen conditions apply:

    -C G(I,0) + (Id-C G_x(I,X)) X lies strictly inside 0.9 X;
    ||Id-C G_x(I,X)||_weighted_infinity <= 1/2.

The table displays rounded independent exact-rational audit bounds; the full
rational quantities are in INDEPENDENT_AUDIT.json.

| Attempt | Largest image/radius | Largest contraction bound | Frozen decision |
|---|---:|---:|---|
| Whole interval [-5e-6,+5e-6] | 0.984220952 | 0.019188126 | Does not meet the 0.9 margin |
| Negative half [-5e-6,0] | 0.849825081 | 0.018907442 | Certified uniformly |
| Positive half [0,+5e-6] | 0.849059898 | 0.018240229 | Certified uniformly |

The whole-interval record is preserved as non-certified under the frozen
criterion. Its ratio being below one was NOT used to weaken the 0.9 gate.
The predeclared bisection was then applied, and both closed halves passed.
Only three of the maximum seven allowed nodes were evaluated. No quarter
subdivision, alternative box, changed tolerance or additional amplitude ran.

These are uniform interval bounds, not point samples. For each amplitude,
the fixed-point map is a contraction of X into itself. Adjacent closed tiles
must have the same root at their shared point because both use X and that
root is unique there. This establishes one branch over the exact closed
union, including zero. Analyticity and the invertible x derivative give local
analytic dependence on epsilon; no interpolation across a gap is used.

At zero, the exact source identities give x(0)=0 and G_epsilon(0,0)=0, hence
x'(0)=0 in the shifted chart. The physical tangent remains (psi,-2psi,f).
The accepted local analytic family lies in X near zero, so uniqueness
identifies it with this branch. The independent audit also reconstructs each
old endpoint's certified image, adds its old center, and proves that the
whole resulting root enclosure lies in X. That identifies the old signed
samples with this same branch; overlapping boxes alone would not suffice.
The largest translated old-root image/radius ratios are approximately 0.32761
for the negative sample and 0.32681 for the positive sample, both inside X.

## Error accounting, execution and independent verification

The epsilon preparation encloses a degree-seven Taylor polynomial plus an
eighth-order Lagrange remainder over hull({0},I). Only the already proved
exact constant/linear identities are removed. Shifted-center remainder terms
are retained, and exact integer-power ranges handle intervals crossing zero.

Linux used the existing Python 3.12.3/python-flint 0.9.0 runtime, Arb at 768 bits,
fixed spatial step 1/8192, fifth-order validated Taylor remainder and strict
Picard ceiling 32. Both complete wall-event subintervals are covered by each
flow. Maximum observed Picard count was 3. Scientific controls were frozen
before any new physical outcome.

The three serial cases took 420.02 s, 442.49 s and 428.35 s: approximately 21.5 min
of integration wall time. Six flows validated 98,190 cells. This line used
one heavy process and one arithmetic/BLAS thread; the independent numerical
audit started only after that producer exited. The prospective address-space
limit was 4 GiB. No runtime was installed or changed, and other research jobs
were not interrupted.

The independent audit verified 390 new atomic checkpoints and 106,422 native
interval representations. It independently recomputed the strict image and
contraction decisions using exact rational arithmetic, reconstructed the
finite traversal and gap-free amplitude cover, checked endpoint identities
and local-tangent reconciliation, and rechecked inherited source/zero evidence.
That inherited source/zero check covers another 129 checkpoints. The audit
checked 1,122 source/review/input hash links and 43 runtime links, and verified
1,575 files unchanged. All bound input and source files remained unchanged.

This is independent decision/provenance verification with a separately written
auditor, not a second integration using a disjoint arithmetic library. The
validated Taylor/Picard and Arb primitives are shared and explicitly disclosed.
The proof also depends on the source certificates and the independently
reviewed exact map identities; checkpoint counts alone are not its evidence.

Before freeze, review strengthened cached-tile identity checks, repaired the
result-before-terminal recovery window, disambiguated integration-CPU budget
wording and corrected one duplicate control key. All earlier development
receipts remain preserved. Only analytic-control-05 binds the final source:
45 new narrow controls plus 15 inherited controls passed. No physical outcomes
preceded those corrections or the freeze.

## Meaning, remaining limits and next justified step

Evidence class: computer-assisted uniform existence, uniqueness within the
declared common box, and connectedness for the same prepared initial-data
family, with retained fourth-time wall compatibility.

The line has moved from a tiny local existence neighborhood and two separately
certified finite samples to one certified finite signed branch joining them.
That strengthens the initial-data foundation for a separately qualified
dynamical investigation. It does not decide what the perturbations do later.

No uniqueness outside X, all-order boundary compatibility, hyperbolic spacetime
existence theorem, time evolution, collapse outcome, horizon, child universe
or halo result is established here. This D1 family is not identified with P16
or another research lineage. No manuscript or canonical research inventory
was changed.

The next distinct question is dynamical: whether this unchanged physical
initial-data family can be evolved in an admitted formulation with consistent
boundary conditions and controlled constraint propagation. The separately
owned Lin initial-data/dynamical-response line must answer that under its own
authority. No successor or additional amplitude is launched from this packet.

## Authority and reproducibility

Frozen binding SHA-256:
`20151671f46efccf55d0a6aba012acaef477eb1705e922d454ede5d3b3104412`.

Root RESULT.json and MANIFEST.json are the final sealed authority. Supporting
files: CONTRACT.md; CONNECTION_ARGUMENT.md; the inherited independent
endpoint/centered-IVP derivations; PREFLIGHT_REVIEW.md; analytic-control-05;
output/r, output/rl, output/rr and their checkpoints; INDEPENDENT_AUDIT.json;
POSTRUN_REVIEW.md; postrun_audit.py; and FINAL_LIVENESS.json.

Mac packet:
`/Users/ronbibb/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-c4-connected-branch-20261006T004500Z`.

Linux mirror:
`/media/psf/Home/Library/CloudStorage/OneDrive-Personal/Academic2/collapse-horizon-research/branches/02-event-horizon/lin-c4-connected-branch-20261006T004500Z`.

The sole bounded experiment is complete. Its final liveness record confirms
no producer remains; independent verification completed before final sealing.
