# Validated coordinates of the concave wall transition

The user's new “Continue” authorizes this single bounded successor to the completed analytical map. It does not reopen the previous goal or extend its allocation. This test estimates no mass or growth rate: it attempts validated enclosures for the lower-only, upper-only and equal-wall massless thresholds of the same exact concave example.

## Frozen scientific inputs

Use the exact model V(Phi)=Phi-Phi^2/2+Phi^4, initial (a,H,Phi,T)=(1,-2,0,0) at r=0, k=3, walls r=+-1/100. The accepted T2 transfer and phase classification in `20261025T112826Z_CONCAVE_WALL_TRANSITION` remain the analytical premises. No new physical model or parameter search is selected. All stiffness coordinates use the same fixed proper-wall conventions.

Numerically enclose the background backward from 0 to -1/100, then propagate that enclosing lower state together with the physical-mu=0 transfer M from identity to +1/100. The M equations and derived threshold expressions are precisely the accepted T2 system. Keeping the enclosing lower background uncertainty is mandatory; no midpoint reset or reinjection of the exact interior seed is allowed on the forward path.

## Method and finite workload

Use outward Arb balls at fixed 256-bit precision, python-flint 0.9.0 under Python 3.12.3 on academic-linux. Two fixed resolutions: n=1024 and n=2048 backward steps of size -1/(100n), followed by 2n forward steps of size +1/(100n). Total production workload is 9216 interval steps, one producer, no retries or adaptive subdivision.

Every step constructs B=Y+[-|h|r,|h|r] with fixed rates r=(3,5,1/10,2) for background and (1/10,2,2,12) for M11,M12,M21,M22. Compute F(B), then verify Y+[min(0,h),max(0,h)]F(B) is strictly interior to B and B remains in the inherited background rectangle. Smoothness on the positive-warp box plus this first-exit/Picard containment establishes existence within the tube. The rigorous endpoint update is Y+hF(B), not a midpoint Euler trajectory. It contains the exact endpoint, including integration remainder and all inherited interval uncertainty. Both signs of h must be covered.

This deliberately simple first-order enclosure has no omitted Taylor remainder. Dependency widening is allowed and can make the test fail; it may not be hidden by narrowing an enclosure. No numerical threshold is accepted solely from two-level agreement.

Finite controls run inside the same admitted worker before production: constant and exponential manufactured scalar flows at both time signs, deliberate too-small-tube rejection, and exact same-model derivative values at the seed for both transfer columns. Each level checks whole-step background rectangle containment, finite balls, final Hamiltonian zero inclusion and exact determinant identity consistency. The four final M balls must lie inside the accepted T2 analytical enclosures. Each threshold interval must be positive and have width <=1/10000. Corresponding coarse/fine threshold balls must overlap; the finer widths must not exceed coarse widths. Preserve both outputs rather than silently replace them by their intersection.

PASS requires all controls, every tube gate, both level gates, level comparison, immutable source/runtime bindings and independent terminal audit. Any violation is TECHNICAL_INCOMPLETE or INCONCLUSIVE_ENCLOSURE as recorded, with no changed step count, rate, precision, threshold or rescue run. The final accepted bounds come from the n=2048 level, conditional on Arb's outward arithmetic and the inspected containment algorithm. This is numerical validation with an independent code/result audit, not independent arithmetic libraries or external human review.

## Resources and writes

One Linux core, all library threads=1; below the continuing two-core ceiling. One nonblocking normal global admission attempt, CPU lease, own-line lease, current process/affinity accounting and memory check. Require at least 4 GiB available and <=10 occupied/admitted shared cores; never bypass HOLD or an unavailable lease. Hold CPU/line locks in both wrapper and child so parent loss does not release an active child's reservation. No queued retries. The 600-second worker cap is a finite workload safety bound, not a new research allocation. RSS/virtual-memory ceiling is 1 GiB. No >1-hour run or resumption is authorized.

The child independently enforces a 590-second wall alarm within the wrapper's 600-second cap, including after abrupt wrapper loss. Expected Python and Arb binary hashes are enforced before scientific work and rechecked after. Background rectangle and analytical M bounds use exact rational comparisons against outward dyadic endpoints, not slightly expanded Arb container bounds.

The read-only preflight found no matching own job. This new packet alone receives source and generated outputs. Existing parents, manuscripts and inventory remain unchanged. Immutable per-level records and periodic progress are retained; progress is not advertised as a resumable solver checkpoint. Resource denial closes with RESOURCE_HOLD and no pending launch. One independent reviewer admits the frozen source/plan before execution and audits actual evidence afterward.
