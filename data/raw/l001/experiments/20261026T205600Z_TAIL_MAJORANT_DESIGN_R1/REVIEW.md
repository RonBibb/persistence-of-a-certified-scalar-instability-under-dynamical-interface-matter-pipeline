# Independent design review

Reviewer: `/root/jet_bound_review`.
Date: 2026-10-26.
Disposition: **PASS — mathematical design only. No new numerical amplitude certificate or replay is authorized by this review.**

I read the complete `DESIGN.md` and checked the scalar sequence argument against the inherited compatible-recursion majorant. The revised route avoids the earlier gap: it constructs a scalar comparison fixed point, not a physical correction operator on arbitrary incompatible trial fields.

## Checked points

- For the inherited `G(w)=K w²/(1-Kw)²`, removal of degrees two and three gives exactly `B2=K a1²` and `B3=2K a1 a2+2K² a1³`. Tail inputs beginning at degree four cannot change these coefficients.
- In the weighted absolutely summable sequence algebra, projection has norm at most one. Positive coefficients give both the stated self-map bound and the Lipschitz bound `G'(p+delta)=2K(p+delta)/(1-K(p+delta))³`. They apply to signed trial series by absolute-value majorization, not only positive sequences.
- Iteration from zero remains nonnegative. The fixed point's coefficients dominate the actual higher-order norms by induction, because `G` has no constant or linear term and therefore preserves triangular dependence on lower orders. The actual lower-order inputs retain the inherited bulk and wall compatibility; scalar comparison sequences are not asserted to be physical fields.
- The joint majorant is applicable to this tail construction: its source/response estimates are uniform positive coefficient bounds in the lower-order aggregate norm inputs, not a fit to the computed first three coefficients. Its retained-transport trace estimate likewise supplies a formal positive bound with lower-order dependence.
- The `a1,a2,a3` inputs must be qualified in the same aggregate Nagumo norms and radial collar. Real-axis boxes alone do not supply those analytic norm bounds. This obligation remains explicitly open.
- Restriction to the inner radial collar costs `4^n`, so `varrho/4`, not `varrho`, is the physical amplitude radius. Chart, timelike, lapse and observable gates must be recomputed with `p+delta`; the scalar self-map alone supplies no new signed observable conclusion.
- The optimistic `a2=a3=0` case is a necessary feasibility comparison only for the fixed inherited `K` and seed bound. Monotonicity does not make zero valid physical norm data.
- The method ceiling is correct: at `w=1/4`, the derivative is `32/27>1`; hence any accepted target must satisfy `eta_target<1/(16K a1)`. Relative to the current `1/(768K a1)` bound, failure at or above a factor of48 follows. This is only a ceiling of the chosen contraction test and fixed inputs, not the solution's continuation radius.

## Remaining gates

No useful-amplitude target, actual low-order analytic norm triple, tail radius, new physical admissibility interval or new observable remainder has been certified here. A sharper majorant or seed must itself be justified before it is substituted. The pre-replay feasibility gate is therefore the appropriate next implementation boundary; cubic export should not precede a promising result for the intended bound.

The original exact-background, selected-spectrum and compatible-recursion premises remain inherited. No generic Cauchy-flow inverse, neighborhood-wide evolution theorem, saturation, collision or endpoint follows from this design review.

Signed: `/root/jet_bound_review`.
