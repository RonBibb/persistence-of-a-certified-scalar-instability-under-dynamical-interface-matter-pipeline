# Finite amplitude correction strategy

**Superseded design:** The corrected route is [Low order informed tail certificate](../20261026T205600Z_TAIL_MAJORANT_DESIGN_R1/DESIGN.md). It avoids the unconstructed physical correction inverse below by bounding the already compatible homological coefficient recursion. The discussion below is retained as the original feasibility diagnosis, not the current execution plan. The original inventory records remain unchanged.

The local analytic solution is established under the preceding theorem's premises. The next target is a useful-amplitude enclosure of that same branch. Better profile data are necessary for the proposed low-order-informed route, but they do not replace a correction-inverse estimate.

## Correction variables and normalization

Write the fields, wall graphs and oscillators as the known polynomial `P3(eta)` plus a correction `V(eta)` that vanishes through order three. This preserves the selected mode normalization and the authenticated quadratic and cubic coefficients, rather than allowing an uncontrolled change of amplitude or resonant first harmonic. The coefficients must be expressed in the same affine chart, retaining background composition and graph transport.

Build the complete residual of `P3` from the same action. The correction problem must include the bulk constraints, scalar normal laws, oscillator equations and Israel junction conditions. The compatibility identities restrict admissible forcing; they do not license an arbitrary residual vector in independently chosen rows.

The old inverse is the background harmonic inverse with the first resonant mode fixed. Linearization around `P3` couples harmonic orders and changes wall and radial coefficients. A finite radial matrix inversion at one amplitude is not a proof of invertibility of this analytic correction problem.

## A bounded feasibility criterion

One candidate is to factor the new linearized operator through the qualified background inverse and bound its perturbation on a tail space beginning at order four. A Neumann argument requires an explicit operator-norm bound below one, in a norm closed under radial derivatives, analytic composition and moving-wall traces. The residual bound and correction ball must then satisfy a radii inequality and keep the chart and walls admissible.

The available scalar majorant illustrates why a new estimate is needed. For

`G(W) = K W^2 / (1-KW)^2`,

the derivative is

`G'(W) = 2 K W / (1-KW)^3`.

The existing `G` majorizes compatible homological coefficient recursion; it is not yet a constructed correction map on arbitrary profile perturbations. Only after constructing an admissible correction map and proving its difference estimates in a closed norm can `G'` be used as a Lipschitz bound. If that additional step succeeds, `P` must bound the complete polynomial field/graph/oscillator norm and `delta` the correction norm. Translating the center would then evaluate the inherited bound at `W=P+delta`, without removing the large `K`. At `K W=1/8`, the derivative is `128/343<1`; at `K W=1/4`, it is `32/27>1`. These are statements about a sufficient scalar estimate, not a measured loss of invertibility or failure of the physical solution. `W` is not physical amplitude or separation. Conversion to `eta` must retain the normalization `p1(a)=1`, first-mode norm, radial-collar loss and all other normalization factors.

Therefore the next derivation must exploit actual low-order profiles or a better coupled operator estimate, not simply relabel the existing majorant as an a posteriori proof. If a closed norm cannot be shown, record the precise loss and stop before replay.

## Minimal archive work if the inverse strategy closes

Reuse the full quadratic-engine boxes in the seed archive. Reconstruct the actual second-order channels using the authenticated interval `A2`, preserving its dependence as far as the chosen representation supports. The boxes can support real-axis jet bounds through the exact RHS and its derivatives; they are not automatically sharp complex-collar certificates.

For cubic order, retain the existing affine decomposition into the zero, `A2`-tangent and homogeneous channels. A new read-only replay/export should save every native and canonical cell state, start/end states, the point Taylor coefficients, remainder coefficients and Picard box, exact interval coordinates and domain coverage. Bind the full uncertain parameters and both wall states, loads, graph and oscillator coefficients. Do not collapse shooting-parameter dependence before the norm calculation.

The replay must reproduce the authenticated endpoint and observable enclosures and preserve all source/runtime/parent digests. If projected above one hour, implement exact atomic resumption before launch, with checkpoints limiting lost work to approximately 15 minutes. The actual source and timing contract must be frozen separately; this design note does not launch that replay.

## Decision

First close or reject the tail-space inverse strategy on mathematical grounds. If it closes, size and pre-review the cubic export and residual calculation together. Only then select and freeze an amplitude ladder. Failure of an amplitude's sufficient bound remains a recorded failure of that certificate, not evidence of saturation or disappearance of the nonlinear family.
