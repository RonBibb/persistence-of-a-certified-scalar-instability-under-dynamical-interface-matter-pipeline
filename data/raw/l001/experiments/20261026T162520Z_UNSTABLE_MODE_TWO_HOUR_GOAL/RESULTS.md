# Nonlinear development of the neutral unstable mode

This two-hour investigation has established the first two nonlinear proper-separation coefficients in the formal expansion seeded by the actual neutral growing mode. Both reinforce the shortening direction. A separate proper-clock readout retains the quadratic reinforcement. We also obtained all-order real-axis response bounds and qualified the formal source-compatibility argument. These are results about the growing mode, not the previously studied charge-forced, forward-decaying branch. Convergence of the nonlinear expansion remains unproved.

**Window:** 26 October 2026, 12:25:20–2:25:20 PM Eastern (16:25:20–18:25:20 UTC). **Record status:** scientific work and review complete; final integrity closeout occurs within that fixed window. This file is a research handoff, not a numerical input or a manuscript change. The closeout manifest binds its final bytes.

## What was calculated

The authenticated selected mode belongs to the same action with its boundary oscillators retained. Both conserved currents are zero. Its growing amplitude is

\[
\eta=\epsilon e^{rt},\qquad \mu_1=-r(r+3h),\qquad r/h\in[1.002948997421,1.002972913782].
\]

The normalization is \(\psi_1(a)=1\), with first-order wall displacement \(\xi_1=0\). Coefficients use ordinary powers, **not factorials**. For proper separation on the chosen time slices,

\[
D(\eta)=D_0+d_1\eta+d_2\eta^2+d_3\eta^3+\cdots.
\]

Conservative rounded enclosures covering the accepted representations are:

| Coefficient | Enclosure | Interpretation |
|---|---:|---|
| \(d_1\) | \([-53.568,-53.520]\) | Positive \(\eta\) selects the shortening direction. |
| \(d_2\) | \([-1520.589,-1465.333]\) | The first nonlinear correction reinforces shortening for positive \(\eta\). Its even parity breaks a simple expansion/contraction mirror symmetry. |
| \(d_3\) | \([-67128.662,-41914.723]\) | The next correction also reinforces shortening for positive \(\eta\). |

These coefficients are in the existing code units and amplitude normalization. Their magnitudes are not invariant under rescaling \(\epsilon\). They are not an error estimate for a truncated trajectory.

The quadratic contribution is overwhelmingly in the bulk term of the proper-distance budget; the direct moving-wall contribution is about \(10^{-3}\), against a total coefficient near \(-1.5\times10^3\). This identifies where that budget contribution is represented. It does **not** show that boundary conditions or boundary oscillators are causally irrelevant.

## Why the cubic sign became resolvable

The first cubic calculation passed its technical checks but produced an enclosure containing zero. Repeated interval evaluation treated the same uncertain quadratic shooting amplitude \(A_2\) as if its appearances could vary independently.

The successor preserved the exact affine structure:

\[
A_3=A_{30}+A_2A_{31},\qquad d_3=d_{30}+A_2d_{31}.
\]

It retained the **entire original \(A_2\) interval**. No midpoint substitution, eigenvalue narrowing, gate adjustment, or discarded unfavorable case was used. Both independent integration representations gave negative cubic enclosures. The separate saved-record audit passed 417,461 checks. The unresolved first calculation remains preserved.

The audit independently checks saved-budget sums, affine reconstruction, original non-affine endpoint equations, lower-order replay, provenance, and the two-engine conclusion. Existence of the radial ODE tubes is inherited from the validated integrators; the audit does not pretend to rerun those integrations.

## Does the result survive a physical clock change?

Let \(x=D-D_0\), and use proper time \(\tau_a\) on the lower wall. Exact formal series reversion gives

\[
\frac{dx}{d\tau_a}=r\left[x+\alpha x^2+\beta x^3+\cdots\right],
\]

with conservative enclosures

\[
\alpha\in[-0.512160,-0.492003],\qquad
\beta\in[-0.018451,0.354216].
\]

Thus the quadratic correction remains negative in this proper-clock description. For the contraction-oriented branch \(x<0\), its contribution reinforces the negative linear rate. It is not eliminated by replacing coordinate time with this wall clock.

The reduced cubic coefficient \(\beta\) remains sign-unresolved. That is consistent with negative \(d_3\): reversion introduces a subtraction involving \(d_2^2\). This distinction prevents overstating what the cubic result means.

The proper-clock coefficients are invariant under constant rescaling of the amplitude when all coefficient transformations are included. They are **not** a proof of invariance under arbitrary foliation changes. Proper separation still refers to the specified slices. The readout has exact polynomial controls and independent source review; its numerical inputs come from the audited coefficient packets.

## Can the nonlinear expansion continue beyond these orders?

A fresh background replay, using the exact current initializer and both validated numerical representations, passed both predeclared sufficient positivity tests at orders 2–8. An attempt to transfer an older archive had failed exact input identity and was preserved; it was not accepted on approximate similarity.

The successor established a conditional real-axis inverse estimate for the reduced neutral scalar boundary problem at **every integer order \(n\ge2\)**. Orders 2–64 are covered by finite-order estimates and orders 65 onward by a uniform maximum-principle and derivative bound. A separate exact-rational audit passed 442,839 checks, including cell-bound reductions and the response constants.

The conservative common estimate has the form

\[
n^2\|f_n\|_\infty+n\|f_n'\|_\infty+\|f_n''\|_\infty
\le 3{,}067{,}149\left(\|F_n\|_\infty+n\max_i|g_{n,i}|\right).
\]

This is a worst-case mathematical bound, not a measured physical amplification factor. It is conditional on the authenticated background and the compatible scalar reduction. It excludes a singular scalar boundary map at an untested higher order; it does not prove convergence of the nonlinear series.

The next completed calculation reconstructs the metric component \(p_n\) from compatible scalar sources. The required identity is

\[
S_{c,n}'+4H S_{c,n}-T S_{g,n}-D_n S_{p,n}=0.
\]

Arbitrary independent source functions do not qualify. The reconstruction bound explicitly pays for source derivatives; it does not conceal derivative loss. Its exact source controls and independent arithmetic audit passed (49,491 checks).

The trace metric component, moving-wall displacement and wall oscillator now also have conditional all-order real-axis response bounds. Eight exact general-rate first-variation controls passed. A separate closeout replay checked the response arithmetic, clock coefficients, displayed decimal enclosures and 15 terminal records (2,906 checks). These are linear response estimates for each order, not a nonlinear fixed-point theorem.

A separate exact five-dimensional Christoffel/Ricci calculation passed 13 off-shell component controls. It identifies the reduced residuals with the Einstein and scalar residuals before imposing the background equations. This supplies the component-level foundation for the all-order Bianchi compatibility argument; the standard contracted Bianchi theorem itself is inherited.

The all-order formal compatibility argument subsequently passed its 19 exact algebraic controls and analytic review. For positive harmonics, the temporal and radial Bianchi identities force the required bulk source identity once lower orders solve the equations. Thus compatibility is not an arbitrary extra load condition for this formal recursion. A separate wall induction removes the remaining pure-trace Israel residual at nonzero harmonic rate, conditional on the inherited Codazzi and material-exchange identities. Those wall identities were not independently rederived here. Neither argument treats an independent zero harmonic or proves convergence.

## What is still missing

We do **not** yet have a certified finite-amplitude evolution, a saturation amplitude, a collapse time, wall contact, child formation, or an event horizon from this calculation.

The key remaining step is a nonlinear source estimate and convergence/remainder argument that closes with the response bounds. In particular:

1. Extend the real-axis inverse/response estimates to the common complex collar needed by the proposed analytic function space, or supply a different complete derivative-loss argument.
2. Bound the actual nonlinear sources, including the needed radial derivatives and moving-boundary compositions, in that same space.
3. Close a neutral-growing-mode majorant and derive an explicit amplitude interval and remainder bound. Only then can a truncated curve be promoted to controlled nonlinear development over that interval.

The existing manuscript's charge-forced decay construction does not discharge these gates: its rates and denominators differ. Its analytic strategy is a useful template, not a numerical certificate for the neutral growing branch.

Computing a fourth coefficient alone would not close these gaps. The highest-value continuation is the convergence bridge, informed by the now-resolved quadratic and cubic signs.

## Evidence inventory

All entries below are siblings of this directory. Scientific execution was on Linux with one-thread, leased jobs; source editing and inspection were on the Mac. Numerical coefficients used 768-bit Arb interval arithmetic. Exact arithmetic controls and audits used rational arithmetic. No manuscript, release, or external record was changed.

| Packet | Result and role |
|---|---|
| `20261026_GROWING_MODE_QUADRATIC` | Preserved technical failure before accepted R1. |
| `20261026_GROWING_MODE_QUADRATIC_R1` | Accepted growing quadratic coefficient; independent audit passed. |
| `20261026_GROWING_MODE_CUBIC_BULK` | General-rate cubic bulk source identities: 24 exact checks. |
| `20261026_GROWING_MODE_CUBIC_WALL` | General-rate cubic wall/source identities: 78 exact checks. |
| `20261026_GROWING_MODE_CUBIC_FLOW` | Valid first cubic enclosure, sign unresolved; independently audited. |
| `20261026_GROWING_MODE_CUBIC_AFFINE` | Full-interval affine reconstruction resolves negative cubic sign; independently audited. |
| `20261026_GROWING_MODE_CLOCK_READOUT` | Exact formal coordinate/proper-clock reversion and interval readout. |
| `20261026_GROWING_INVERSE_READINESS` | Preserved failed exact-identity transfer of an older background archive. |
| `20261026_GROWING_INVERSE_READINESS_R1` | Fresh same-lineage background and successful orders 2–8 positivity tests. |
| `20261026_GROWING_NEUTRAL_ALL_ORDER_INVERSE` | All \(n\ge2\) real-axis scalar inverse estimate; independent exact audit passed. |
| `20261026_GROWING_NEUTRAL_METRIC_RESPONSE` | Compatible scalar-to-metric response; independent arithmetic audit passed. |
| `20261026_GROWING_NEUTRAL_TRACE_WALL` | Preserved provenance failure: qualified wall algebra was absent from inherited authority. |
| `20261026_GROWING_NEUTRAL_TRACE_WALL_R1` | Explicitly bound wall authority; full conditional real-axis response and eight general-rate controls passed. |
| `20261026_GROWING_NEUTRAL_COMPONENT_MAP` | Exact off-shell five-dimensional tensor identification: 13 controls passed. |
| `20261026_GROWING_NEUTRAL_COMPATIBILITY` | Formal bulk compatibility and conditional wall induction; 19 exact controls passed and analytic argument reviewed. |
| This folder's `VERIFICATION_TERMINAL.json` | Independent rational closeout replay: 2,906 checks, 15 terminal records. |

## Closeout and resumption

The Linux numerical jobs have completed; no successor computation is authorized by these planning documents. The one-shot `CLOSEOUT.json`, when present with a passing `CLOSEOUT_TERMINAL.json`, records the final recheck of all 17 accepted terminal records, their applicable bound source closures, document hashes and absence of goal-specific numerical workers. Its absence or failure must not be represented as a passing closeout.

The earlier arithmetic verifier's terminal SHA-256 is `99a84f01a1f86cd79802bb573bea76d0d1975fcc21e60fadaf18522ca6c9310a`. The separately qualified component-map terminal is `a189065e25d7f9eb386ca71ee4baf8d99c5a99a78cd60884e37afe7c40d48753`; the formal-compatibility terminal is `46a3b24af5e15aa9f08894fe5612b18efeb1fc2b33901b0894523e59eb841f6f`.

Read [NEXT_TEST.md](NEXT_TEST.md) for the bounded successor, [SOURCE_NORM_SCOPING.md](SOURCE_NORM_SCOPING.md) for the concrete derivative and wall-weight ledger, and [CONDITIONAL_MAJORANT.md](CONDITIONAL_MAJORANT.md) for the reviewed radius/tail lemma whose research-specific hypotheses remain unproved. [REVIEW.md](REVIEW.md) records the independent review and adopted corrections.

The practical change from the start of this window is that we now have an audited direction of nonlinear feedback through cubic order and an all-order formal response/compatibility framework. The next work is to certify how far that expansion represents an actual solution, rather than infer its endpoint from the coefficient signs.
