# Concave wall transition recovery and validation

The numerical obstruction is resolved and the transition coordinates are validated. The original failure occurred before any evolution: generic integer exponentiation returned NaN on a finite zero-crossing scalar interval. Explicit outward multiplication evaluates the same polynomial correctly. A new corrected certificate passed unchanged accuracy gates, a different propagation route agreed, and an independently implemented integer-interval calculation reproduced compatible bounds without Arb. The original analytical classification and both failed packets remain unchanged.

## What the transition means

For the fixed concave example, sufficiently soft walls admit two negative regular scalar modes. Crossing the established massless transition removes the additional mode, leaving one negative mode. This is not full stability. The original central example's separate one-mode result is untouched.

The exact potential is V(Phi)=Phi-Phi^2/2+Phi^4, with seed (a,H,Phi,T)=(1,-2,0,0), k=3 and walls at r=+-0.01. No physical parameter changed during this allocation. Wall Hessians use the inherited normalization.

The corrected original-route certificate gives these outward-rounded decimal enclosures:

| Wall setting | Critical Hessian interval |
|---|---|
| Lower wall only | [0.034922411490, 0.034929978021] |
| Upper wall only | [0.040983610553, 0.040991610440] |
| Equal Hessian at each wall | [0.018853733286, 0.018857632590] |

The equal-wall value is per wall, not the sum. Exact rational endpoints in [T4 RESULT](T4_CORRECTED_COORDINATES/RESULT.json) are authoritative. A chosen value inside a threshold enclosure is not thereby certified massless; the analytical theorem establishes the actual unique crossing. The independent T6 and T7 intervals are retained separately, not replaced by intersections.

## Diagnosis and correction

The qualified recorder established that the original backward step 1 failed only in T. Every input, time interval and tube was finite, but the computed T derivative was NaN. The expression test isolated Phi**3 on that actual zero-crossing interval. Its other summands were finite. Phi*Phi*Phi provided a finite outward enclosure and placed the candidate strictly inside the original tube, without changing the rate ceiling, step size or precision.

Twenty-one fixed polynomial controls verified explicit multiplication against exact rational polynomial ranges. Six original exponentiation cases returned nonfinite outputs: powers 2, 3 and 4 on two tested zero-crossing balls. This is a pinned-runtime, operation-level finding, not a universal claim about all powers or an asserted internal library defect.

The old diagnostic also had a recorder defect: it attempted rational conversion before persisting step/component evidence. The new recorder saves raw identity first and retains conversion failures as data. Its five controls include NaN, infinity and a deliberately failing conversion object.

The separately frozen corrected producer replaced only the affected integer-power evaluations with explicit multiplication, plus provenance and failure logging. It retained the original 256-bit Arb setting, rates, 1024/2048 resolutions, inherited lower-state uncertainty, strict whole-step enclosure checks and width ceiling 1e-4. Earlier failures were never rescored.

## Scientific interpretation beyond the coordinates

Let x and y be lower and upper wall Hessians. The accepted transfer relation is

    S(x,y) = 2 M21 + M22 x + M11 y + (M12/2) x y.

Its negative and positive sides correspond respectively to two and one negative regular modes. Exact coefficient envelopes classify the whole nonnegative plane where they have definite sign; zero-containing numerical bands remain unresolved.

Exact postprocessing proves the transition curve has slope below -1 throughout. Lower-wall placement therefore minimizes the total stiffness needed to remove the additional mode in this background. At fixed total x+y=0.038, all-upper placement leaves two negative modes, while all-lower placement leaves one. The lower-wall allocation crossing lies in [0.017168131813, 0.017216712947] using T4's certificate; that interval is not an arbitrary selected massless point.

A conservative coefficient hull containing all three numerical certificates gives:

- Upper-only placement requires 17.3521–17.3584 percent more stiffness than lower-only placement, because the axis-threshold ratio is exactly M22/M11.
- Lower-only placement saves 14.7863–14.7909 percent relative to the upper-only budget. This uses a different percentage denominator.
- The deviation from the linear transition chord in the upper-wall coordinate is uniformly at most 0.000003881507, less than 0.009471 percent of the upper-only intercept. This is a rigorous upper bound, not a measured maximum or a local relative error near the other intercept.
- For equal walls, the positive shift from the linear approximation is bounded by [0.000001772853, 0.000001774071], using an exact correlation-preserving identity rather than subtraction of overlapping numerical intervals.

Thus unequal diagonal wall response dominates this fixed boundary-transition relation; the bilinear interaction is tightly bounded. This does not identify a new microscopic gravitational mechanism or describe nonlinear evolution. See [T8 terminal review](T8_TRANSITION_MECHANISM/TERMINAL_REVIEW.md).

## Test inventory

Every test had its own prospective review, frozen dependencies, single execution and independent terminal audit.

| Test | Actual start UTC | Outcome and contribution |
|---|---|---|
| T1 recorder | 14:16:01.537308 | Passed five conversion-safe recording controls |
| T2 first failure | 14:17:39.792016 | Captured step 1, T-only NaN; no evolution accepted |
| T3 polynomial semantics | 14:20:44.523954 | Isolated the cube obstruction; 21 multiplication controls passed |
| T4 corrected coordinates | 14:23:32.387964 | All 9,216 steps and original certificate gates passed |
| T5 wall allocation | 14:28:34.405887 | Exact global slope and fixed-total allocation certificate |
| T6 split transfer | 14:31:54.853613 | All 6,144 steps passed; central-to-both-walls composition agreed |
| T7 integer replication | 14:33:56.744344 | All 9,216 steps passed without Arb; 33 arithmetic corner controls |
| T8 transition interpretation | 14:38:09.104298 | Conservative-hull asymmetry and uniform interaction bounds |

T6 changes the propagation route but shares Arb and the original RHS. T7 uses separately written integer interval arithmetic and an independently transcribed RHS, while sharing Python, the mathematical equations and the enclosure argument. Independent agent audits reviewed source, proof obligations and recorded evidence; they are not external human peer review.

## Allocation and resource closure

The new allocation began 2026-10-25 at 10:12:07 AM EDT (14:12:07Z). Its immutable cutoff for starting tests remains 12:12:07 PM EDT (16:12:07Z). The objective was completed early after eight substantive stages; this does not shorten or overwrite the authorization clock. The independent completion assessment identifies no indispensable remaining validation for the bounded diagnosis and coordinate claims. Unused time is left unused rather than filled with fidelity reruns or parameter scans.

All executions used one core, including inherited controller/worker affinity and single-thread libraries, below the aggregate two-core maximum. Normal HOLD/shared/CPU/L001 admission was respected. Each had a 1 GiB memory limit and 600/590-second wrapper/child caps; none required long-run recovery. Total recorded wrapper runtime was approximately 3.61 seconds; elapsed research time was principally implementation and independent review, not a long physical simulation. Numerical integration totaled 24,576 steps across the three production certificates.

At 14:39:22Z, all eight owned worker PIDs and matching controllers were absent; no owned CPU0 or L001 lease remained. There are no queued jobs or retries. All 64 bound dependency entries matched, and all 31 inventoried files in the two failed predecessor packets were unchanged. [FINAL_RECONCILIATION.json](FINAL_RECONCILIATION.json) records the checks. No manuscript, shared inventory, external record or physical action changed.

## Remaining research questions

Actual eigenmasses and growth rates, other perturbation sectors, nonlinear fate and behavior of other backgrounds remain distinct research questions. They are not unfinished validation gates for this certificate. The completed result establishes the threshold and its boundary-condition structure for the declared example, not a fully stable solution or a new cosmological mechanism.
