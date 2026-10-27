# Analytic corrections to mode participation and separation

This test derives the first finite-width corrections to the two normalized mode quantities measured in T10. It uses the governing equations and the accepted exact eigenvalue and launch-slope series from T7, with no fitted parameters.

Using T7's rational nested polynomials, reconstruct the central-normalized mode. Integrate each radial-even coefficient over x = r/d as 2 c_j(d) d^j/(j+1). Form the products before truncating. The integral of a² f² must be complete through d^6 before division by d^4; the accepted total degree six and radial degree seven provide this. The integrals of a² psi² and psi are also formed from the same series.

Compute scalar_fraction/D^4 = IF/[16(d^4 IF+6 IP)] and canonical_separation_squared/D = S²/(d^4 IF+6 IP). Only the constant and d² coefficients are complete for both quantities; publish only those, converting the d² coefficient to a D² coefficient by division by four. Check the constant coefficients 1/45 and 1/3, zero odd coefficient, and exact endpoint cancellation. Normalization at the center instead of the lower endpoint cancels from both ratios.

Compare these coefficients with the certified T10 intervals at all three widths. This comparison is retrospective: T10 completed before this test was admitted. Report coefficient discrepancies and the remainder after subtracting the D² term descriptively, without a new pass/fail window or a fitted next coefficient. No uniform finite-width remainder certificate or higher analytic coefficient is claimed.

Independent review must check completeness of the truncated products and the normalization factors before admission. Use the original one-core shared-lease wrapper, 1 GiB cap, immutable 20:07:08Z last-start cutoff, 590/600-second timeout, no retries and no overwrites. Expected execution is seconds. Bind T7 and T10 sources/results/reviews and the mathematical supplement. Obtain independent terminal review.
