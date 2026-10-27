# T13 — upper-observer radar and four-readout response rank

Prospective candidate. No execution until independent source approval and normal Linux admission. Existing T12 remains UNRESOLVED; this is a distinct measurement, not a precision adjustment or rescoring of that determinant.

## Defined observer and derivation

An ideal negligible-energy radial pulse leaves the upper interface, reflects instantaneously at the lower interface, and returns to the same upper-interface comoving observer. Reflection is an ideal kinematic probe condition, not a prediction of material reflectivity. The round trip stays within the common patch with timelike interfaces. Time factors and three other readouts are normalized to the same emission event.

With tau(s)=integral[a,s]E and L=tau(b), outbound/down travel samples L-tau, returning/up travel samples L+tau. For p=epsilon_e exp(r(t-te))P, b=-2p and graphs xi:

    Iupper = integral E P [exp(r(L-tau))+exp(r(L+tau))] ds
    graph = Eb(1+exp(2rL))xi_b - 2Ea exp(rL)xi_a
    Cradar_upper = ab[graph - 3 Iupper + (Pb+Hb xi_b) J]
    J=(exp(2rL)-1)/r.

The first graph leg is Eb xi_b-Ea exp(rL)xi_a; the return is Eb exp(2rL)xi_b-Ea exp(rL)xi_a. Moving-emitter speed enters the clock only quadratically; its linear lapse is Pb+Hb xi_b.

General gauge check retains independent radial B, lapse P and shift C. The shift contribution is integral C E²(w_up-w_down), reversing the lower-launch sign. For radial gauge P=-H alpha, B=-alpha_prime, C=-r alpha, the whole integrand equals minus the derivative of E alpha(w_down+w_up). Its boundary values cancel the displayed graph terms and Pb+Hb xi_b=0. Temporal gauge cancels upper beta_b(exp(2rL)-1) against the emitter clock. Controls test both rate signs, flat constant P, static graph limits, reversed gauge derivatives/endpoints, and dependent/permuted determinant columns.

## Fixed input choices and numerical procedure

No new ODE. Use saved T8 neutral E,psi,tau cell boxes and optical L; selected neutral rate gamma and full mass strip remain unchanged. **Predeclared neutral endpoint source is matched T2R1 event psi_b and a_squared_b**, not a selectable estimate from T8 last cells. Neutral graphs vanish, hence no upper H is needed. Use saved T10 H/P cell boxes and first-current assembly at r=-6h for both current channels; upper psi,H,E,xi and lower E,xi come from that assembly. Apply the existing homogeneous wall multiplier and sum basis contributions. Current proper-density normalization remains a_i^6. Require background D equality and overlapping optical L across all sources.

At Arb768, re-evaluate the reversed whole-cell kernels with full uncertain L and tau. Export kernels and signed mandatory/optional-tail contributions outward to dyadic denominator2^80 and sum the reimported contributions. Never substitute midpoints. Preserve parent budget hashes and link every new cell budget to the authenticated old budget. Fraction resummation validates exported arithmetic, not the exponential premise, which is outward Arb plus inherited validated cells.

## Four-readout matrix and frozen decision

Columns remain neutral, lower-current and upper-current directions. Rows are proper separation, scalar-minimum value, lower-emitter elapsed radar, upper-emitter elapsed radar. T12 authenticated raw columns supply the first three. Normalize each whole column by its strictly positive minimum scalar coefficient; its middle entry is exactly1 by algebra.

Predeclare all four 3x3 row minors: (0,1,2), (0,1,3), (0,2,3), (1,2,3). For (0,1,2), independently reconstruct as a consistency check but retain the **unchanged T12 authoritative determinant and UNRESOLVED classification**. Evaluate the other minors by exact Fraction interval arithmetic, require engine overlap and use hulls. Any new zero-excluding hull establishes LOCAL_LINEAR_READOUT_INJECTIVITY; otherwise report UNRESOLVED. Zero inclusion is not degeneracy. No minor or parameter choice is selected after observing data; all four are reported.

This concerns formal linear response-space injectivity. Current amplitudes physically occupy a nonnegative cone. It proves neither useful conditioning nor noise robustness, free-mode excitation, finite-charge inverse uniqueness, nonlinear evolution or a universal time-space relation. The individual chart pieces of the radar coefficient are diagnostics; their sum is the observer's elapsed proper-time response.

## Execution and records

Require accepted T2R1, T8, T10 and T12 reviews/results and all cited engine records and cell budgets. Standard admitted/sources flags plus t2,t8,t10,t12_terminal_review_accepted. Exact Python/Flint/source runtime binding; Linux only, one normal leased core, memory ceiling1GiB, hard producer900 seconds, wrapper910 seconds. Atomic no-overwrite results, controls, per-engine readout/rank records and six new kernel budgets. No exact resume. Independent terminal audit must verify parent/source bindings, budget sums, reversed kernel enclosure and every minor before scientific use. Main supplies wrapper/runtime/admission; source author performs no calculation.
