# Identity of the certified D1 initial family

Independent postrun review accepts the finite-jet target identification and
mode uniqueness within the inherited bracket. The saved-grid replay stopped
at its unchanged acceptance gate; full numerical admission is incomplete.
See [the review](POSTRUN_REVIEW.md) and [its receipt](INDEPENDENT_AUDIT.json).

## Scientific result

The central D1 connected C4 certificate and the nonlinear evolution preparation
target the same exact physical initial-data family on the shared amplitude
interval **−1/200000 ≤ ε ≤ 1/200000**. The identification uses their equations,
mode selection, nonlinear completion and an explicit wall-preserving gauge
bridge. It is not inferred merely from matching filenames, action parameters
or overlapping numerical brackets.

The spatial calculations completed all 49,095 prescribed cells. They identify
the source mode uniquely within its inherited bracket and supply conservative
whole-domain error bounds between the exact source/prepared fields and the
saved material polynomials. The bounds do **not** certify the earlier
parts-per-million numerical evolution comparisons against an exact spacetime.
Exact conformal lapse and inverse-map errors remain unbounded in this packet.

The useful advance is a mathematical connection between the certified
initial-data construction and the preparation used by the evolution study.
Numerical approximation and subsequent dynamics remain distinct questions.

## Why the two constructions agree

The six exact action literals, background boundary problem and wall orientation
agree. Both constructions use the same regular mode equations and ψ(0)=1.
The new derivative enclosure for the upper Robin determinant is strictly
negative throughout the full inherited source rectangle and wall-event interval:

\[
-3{,}738{,}398 < F_\mu < -3{,}736{,}146.
\]

These outward-rounded displayed bounds summarize the exact rational endpoints
in [the mode result](output/mode/RESULT.json). Combined with the inherited
opposite endpoint signs, monotonicity selects one mode in that bracket for
the same fixed exact background. It does not exclude other spectral bands.

The two nonlinear targets have identical C7 Hermite data, fifth-jet correction
shapes, correction coordinates (a,b0,b1), and full Hamiltonian metric
backreaction. The prior connected certificate supplies uniqueness in its
common correction box; the signed numerical coefficient centers are
approximations to those roots, not exact roots themselves.

The remaining apparent difference is the conformal lapse. The independently
derived wall identity is

\[
R_{4,\mathrm{conf}}=R_{4,\mathrm{mat}}+4\eta R_{2,\mathrm{mat}}
+e^{2A}\left[5\Phi_{ll}+(16A_l-c)\Phi_l-4m^2\Phi\right]D_2.
\]

The prescribed third lapse jet sets D₂=0; the fifth supplies fourth-time Israel
compatibility without changing the scalar fourth-time row. Thus the scalar C4
zero sets agree on the same constrained C2 data. All 15 independent symbolic
checks passed. The initial map x_s=exp(ell−B)>0 preserves the spatial metric,
scalar and zero physical momenta. At the walls q=B−A=0 makes the initial
lapses agree; later coordinate times are not assumed equal.

This establishes a finite-jet initial-data identification, not all-order wall
compatibility or a theorem of spacetime existence. The full derivation and its
independently implemented identities are in [DERIVATION.md](DERIVATION.md) and
[INDEPENDENT_IDENTITY_NOTES.md](INDEPENDENT_IDENTITY_NOTES.md).

## What the interval bounds establish

The following are conservative absolute upper bounds, rounded upward for this
table, over the **entire** normalized material interval u=s/D. They cover source,
mode, wall-event, correction-coefficient and polynomial-representation
uncertainty. They are not measured discrepancies or fitted continuum errors.

| Field | ε=+1/200000 | ε=−1/200000 |
|---|---:|---:|
| A | 1.98553×10⁻⁴ | 1.98709×10⁻⁴ |
| ell | 2.29691×10⁻⁷ | 2.29691×10⁻⁷ |
| Φ | 7.75941×10⁻⁵ | 7.89977×10⁻⁵ |

Every overlapping native polynomial segment is included, including the
uncertain upper-wall location. These are coefficient-function bounds evaluated
at a common u, not a tensor norm for the transformed metric: g_uu also contains
D². They do not automatically bound the conformal lapse, inverse coordinate
map, proper-clock observable or evolved solution.

The unscaled source-mode bounds are broader still: the upper bounds for ψ, f
and g are about 0.02297, 2.0551 and 8.5008. This is a limitation of the retained
source rectangle and conservative cell-range comparison, not a measured
failure of the numerical seed. No bracket narrowing or additional calculation
was introduced to improve the outcome.

Exact endpoints and field order are preserved in
[SPATIAL_ENCLOSURES.json](SPATIAL_ENCLOSURES.json).

## Numerical replay stopped at its frozen gate

The zero-amplitude saved grids at degrees 160 and 192 replayed successfully
at 80 decimal digits. All recorded representation differences were below
9.70×10⁻⁸⁰. Their represented coordinate-map polynomials have strictly positive
derivatives across every native cell, and the saved physical momenta are zero.

The next comparison, zero amplitude at 100 decimal digits, exceeded the
predeclared **10⁻⁵⁰ absolute representation gate**. The producer wrote a
failed-closed receipt and stopped. The signed-grid replays were not executed;
there is no successful aggregate numerical-readback result. The tolerance was
not relaxed, and the failed calculation was not restarted.

The independent diagnostic reproduced the failure and localized it to the raw
**coordinate-map polynomial coefficients**. The largest difference is
1.1440258540×10⁻¹⁰, at cell 208 and power 29. At this knot, 80-digit arithmetic
selects native piece 208, while 100-digit arithmetic selects piece 207 through
`floor(s/h)`. All 17 coefficient-failing cells coincide with precision-dependent
piece selection. The raw coefficients describe locally truncated polynomials;
their discrepancy is not itself a physical-field error of that magnitude.

In that same failed zero-case, degree-160 diagnostic, fields evaluated at the
saved material positions differ by about 9.64×10⁻⁸⁰; fields at reconstructed
positions differ by 4.62×10⁻⁶⁵; inverse positions differ by 4.60×10⁻⁶⁵; and
coordinate length/knots differ by 2.35×10⁻⁶⁴. Weighting coefficient differences
by their local powers of h gives a map-difference diagnostic of about
2.89×10⁻⁶⁴. These are numerical representation comparisons, **not** rigorous
exact physical-map or evolution error certificates. Only the raw-coefficient
criterion failed. No alternative map, signed replay or physical integration
was run by this diagnostic.

The failure limits numerical admission. It does not erase the accepted spatial
enclosures or replace the separately derived equality of the exact initial
definitions with a claim that the stored arrays are exact solutions.

The authoritative records are [the completed replay](readback/case0-p80.json),
[the failure receipt](NUMERICAL_READBACK_FAILURE.json), and
[the independent failure diagnostic](audit/FAILED_REPLAY_DIAGNOSTIC.json).

## Remaining mathematical and numerical limits

The material bounds do not yet give validated errors for the exact conformal
lapse, inverse coordinate map, or later time evolution. The zero-amplitude
source comparison also does not separately bound the distinct tiny metric
correction in the saved zero case. These gaps prevent a continuum-accuracy
certificate for the evolved observables, regardless of a successful replay.

The shared certified amplitudes are only |ε|≤5×10⁻⁶. The existing ±10⁻⁵
histories and parameter-neighborhood backgrounds remain outside this
identification. No all-order wall compatibility, long-time stability, collapse,
event horizon, child universe, halo, or connection to the P16/MOTS family is
inferred. No new time evolution was launched here.

## Execution and preserved failures

The three new spatial flows took 21.51, 219.67 and 219.53 seconds, respectively,
or 7.68 minutes in total. Each completed 16,365 cells at 768-bit outward Arb
precision with step 1/8192. Only one heavy worker and one arithmetic/BLAS thread
were used. Atomic full-state checkpoints were saved every 256 accepted cells.

The original frozen attempt stopped before its first cell because the pinned
rational constructor rejected decimal strings. That zero-cell failure and its
original source remain in the sibling packet
`lin-c4-evolution-identity-20261006T044000Z`. The independently reviewed R1
repair parses exact decimals through an integer numerator and denominator;
it changes no physics, tolerance, source interval or decision gate. Earlier
preflight implementation failures and their source receipts are retained in
the original packet. The subsequent 100-digit replay failure is a separate,
preserved outcome, not part of that parser repair.

## Evidence inspected and next distinct step

The inspected scientific sources include this packet's contract, derivation,
mode sensitivity and nonlinear-flow sources; the independent gauge identities;
the connected and signed C4 results; the central and neighborhood mode records;
and the native, conformal-admission, spatial-evolution and second-order
construction sources used by the comparison. Input authentication covered
2,835 file bindings. Hash authentication is not represented as a line-by-line
scientific review of every bound file. Shared Arb/Taylor primitives and the
inherited numerical gauge/map constructor are disclosed.

The immediate prospective step is a small deterministic-knot-selection control:
specify the native polynomial piece explicitly at each knot, distinguish
reproduction of the existing saved map from construction of a revised map,
and compare like representations across arithmetic precisions. This must be a
new, reviewed numerical contract; it cannot retroactively pass the failed gate
or claim that changing a coefficient norm is merely an implementation repair.
The three accepted spatial flows need not be repeated to diagnose this issue.

A separate accuracy study would then need to propagate validated input errors
through the completed lapse, coordinate map and physical observables. Neither
successor is automatically authorized or launched. Longer time evolution
remains owned by the separate evolution line.
