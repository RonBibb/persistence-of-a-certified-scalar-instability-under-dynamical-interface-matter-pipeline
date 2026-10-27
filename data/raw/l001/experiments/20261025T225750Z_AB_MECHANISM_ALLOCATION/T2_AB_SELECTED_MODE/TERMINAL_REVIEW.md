# Independent terminal review — manufactured-control technical failure

All 35 admitted bindings remain intact. The one-core worker exited 1, was reaped, and failed at CROSS_ZERO_SQUARE after approximately 0.273 seconds. Only output/STARTED.json and output/FAILURE.json exist. No baseline propagation, selected eigenvalue, mode integral or scientific result was produced. Preserve this failure without rescoring it.

## Independent diagnosis on academic-linux

Under a temporary leased CPU, evaluated only the implicated interval construction and square helper in both engines; no ODE or full control suite was run. For the nominal input [-1,2], both outward Arb balls have exact bounds [-536870913/536870912,1073741825/536870912]. The square helper returns an outward ball with bounds [-2147483647/576460752303423488,2305843015656144897/576460752303423488]. Its lower endpoint is slightly negative, so equality with zero is false, but the ball contains zero and encloses the entire exact squared range of its actual input bounds.

The mathematical square-range construction is valid. The control incorrectly demands an exactly zero representational endpoint after conversion to an outward midpoint-radius Arb ball. A nonnegative function's valid enclosure may extend slightly below zero. This is an overstrict representation predicate, not evidence of an incorrect physical equation or missed mode.

## Prospective technical successor, not an in-place repair

A separately specified T2R1 may replace this one control with a true enclosure test: derive the input ball's exact rational endpoints l,u; form exact squared range [0,max(l²,u²)] when l<=0<=u (otherwise [min(l²,u²),max(l²,u²)]); require the returned ball's bounds to enclose that complete range. Merely checking that zero is contained would be insufficient. Preserve the original helper, model, mass bracket, steps, precision, tolerances, resources and all other controls unless separately reviewed.

This review approves the diagnosis and a narrowly scoped redesign in principle; it does not admit or launch a successor. T3 remains blocked on an accepted selected-mode result.
