# Scalar normal wall source result

The scalar-normal matching source passed analytic review and independent exact-rational replay on Linux. It includes the geometric corrections, the explicit conserved-current source, and the expansion-order weight required for boundary reconstruction. This is the first of the three moving-wall source budgets, following the four completed bulk-source budgets.

## Verified bound

Let y=Y_<n, C_N=|N_a|^2+|N_b|^2 and H=(1-160001*y)^(-1). For the primary background enclosure the two-wall load satisfies

    n*sum_i |j_i,n| <= [z^n] (C_geometry*y^2+C_current*z*C_N)*H^6,

with sufficient constants approximately C_geometry=9.61199927494e10 and C_current=393.5110041754. The independent background enclosure gives C_geometry approximately 9.61183318966e10 and the same current constant. Exact rational values are recorded in RESULT.json and independently reproduced in AUDIT_RESULT.json.

These are conservative analytic bounds, not measured fluxes or amplification. Formal coefficient bounds apply at all positive orders. Numerical evaluation requires 160001*y<1; no charge amplitude has yet been certified from the full recursion.

## What this resolves

The actual scalar normal includes wall velocity and its Lorentz factor, not just a displaced scalar trace. Those terms are retained. The selected wall action supplies the coefficient 21 and the current half-factor, producing an explicit source proportional to z*C_N that must remain separate from the quadratic geometric correction.

The outer expansion-order factor n is controlled by distributing it across positive-order primitive factors. This preserves the derivative weight needed in the later boundary reconstruction without assuming that z*Y'(z) is bounded by Y(z). Both wall current labels remain independent.

## Remaining work

Next are the tracefree Israel equation controlling wall motion and the surface oscillator equation. Their bounds, the reduced Robin load, and response constants on the fixed working collar must still be combined before full majorant closure and a numerical remainder bound can be claimed.

The audit classification is SCALAR_NORMAL_WALL_BUDGET_ARITHMETIC_VERIFIED. Audit result SHA-256 is 1c42f5aedc5e9759f0621d26d796b7c01a541fa091f54989f24f61ae6d7b1c83, bound by AUDIT_TERMINAL.json. Producer and audit bindings preserve source, derivation, parent and runtime fingerprints. No new evolution ran, and no manuscript or parent artifact was changed.
