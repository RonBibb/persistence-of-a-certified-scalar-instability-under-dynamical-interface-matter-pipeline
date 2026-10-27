# T10 — operational radar response of the first-current branch

Prospective candidate; independent admission and accepted T8 terminal review required. No execution by the source author.

## Question and physical scope

Does the accepted first-current shorter spatial collar also give a shorter elapsed proper time for a lower-interface observer's ideal reflected radial light pulse? The pulse has negligible energy, fixed three-dimensional comoving coordinates, instantaneous upper-interface reflection, and remains within the common patch. Reflection is a declared kinematic measurement, not a prediction of electromagnetic wall properties. The perturbative interfaces remain timelike. Compare coefficients only; no finite charge, unstable-mode excitation, or finite nonlinear evolution is asserted.

Use the same actual AB background, selected material action, and separately normalized lower/upper current channels as accepted T4. The current time factor is z=delta² exp(-6 h t); set r=-6 sqrt(k), mu=-18k. A negative coefficient is a shorter offset which relaxes as z decays, not continuing contraction.

## Frozen computation

Reuse exact T4 basis code (basis.py), corrected T2R1 helper (common.py), both engines at 768 bits and original steps 2/8192 and 2/16384. Retain full background launch and uncertain D interval. Four fresh flows: homogeneous and lower-current particular in each engine. No new eigenmass search or endpoint tuning.

For every cell export E, psi, f, tau_start, whole-cell tau, optical-length and unweighted psi contributions outward to dyadic denominator 2^80. Reimport exported intervals for all subsequent calculations and summation. The unweighted integral reproduces accepted T4 proper separation through the same upper-wall inverse. The saved f boxes are provenance for a possible later diagnostic; no second-order computation is performed here.

After the full uncertain optical L is known, enclose the kernel exp(r tau)+exp(r(2L-tau)) and integrate E psi times it, retaining signed optional tails. Dropping correlations between L and tau only enlarges the enclosure. Export and reimport each kernel and weighted cell contribution. Positivity, finite flow, both constraints and full wall-event coverage are required throughout. The inherited forced assembly rechecks undivided material, scalar, and Israel rows.

Assemble each channel with the same T4 homogeneous multiplier. With current graph coefficients xi_a,xi_b and lower lapse perturbation P_a+H_a xi_a:

    Ccoord = -Ea(1+exp(2rL))xi_a + 2Eb exp(rL)xi_b - 3 Iweighted
    Cradar = aa*Ccoord + aa*(Pa+Ha*xi_a)*(exp(2rL)-1)/r.

The endpoint response is sampled at its actual outgoing/returning background time, not frozen at emission. The graph, bulk, and clock pieces are diagnostic chart contributions; only their sum is the elapsed proper-time observable. Report Cradar, half Cradar, accepted/reproduced deltaD, and ratios only for nonzero denominator. Rescale each source channel by a_i^6 to coefficients per unit neutral local proper-density amplitude; equal current labels are not equal proper densities. Preserve unresolved signs.

## Controls and admission

Bind T4 accepted review, result and both assembled records; bind T8 accepted review and result. ADMISSION.json must set admitted, sources, t4_terminal_review_accepted and t8_terminal_review_accepted. Runtime authentication is the standard Linux executable/Flint/source map. No Mac computation.

Run inherited T4 first-current controls, corrected integral/tail controls, T8 flat and general transverse/temporal gauge controls, and new negative-r flat constant-mode identity plus two-leg moving-graph identity. Arbitrary gauge controls retain the shift and independent B,P rather than incorrectly enforcing B=-2P. Each engine's freshly reconstructed separation must overlap accepted T4, and all final observables must overlap between engines. Optional ratios use common keys to avoid treating a zero-containing denominator as a technical failure.

Output atomic no-overwrite cell budgets, basis records, assembly records, controls and terminal result/failure. Full transcendental audit requires Arb exponential enclosures; rational resummation checks exported budgets but does not itself validate exponentials.

One normal leased Linux core; hard producer cap 900 seconds, wrapper 910 seconds; each flow including weighted pass capped at 210 seconds. No exact resume; failed runs stay failed. Main adds runtime/bindings/wrapper, reviews source, obtains independent admission, executes, and commissions terminal audit before scientific use.
