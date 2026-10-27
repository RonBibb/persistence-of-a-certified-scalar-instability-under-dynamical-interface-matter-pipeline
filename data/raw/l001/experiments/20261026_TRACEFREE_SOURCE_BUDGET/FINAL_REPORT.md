# Tracefree nonlinear source result

The first explicit nonlinear source budget passed analytic review and independent exact arithmetic replay on Linux. It controls the tracefree bulk equation and the reconstructed metric combination c=b+2p at every positive expansion order.

On the fixed working collar rho=1/40000, with Y denoting its coefficient envelope, the raw source obeys

    ||q_T,n||_(2n) <= (72/125) [z^n] Y_<n^2/(1-Y_<n)^2.

For the reconstructed c, replace the prefactor 72/125 by an exact rational constant approximately 8.45916800826568e12. Both authenticated parameter enclosures give the same constant because they use the same lower k bound. They are not two independent evolutions of a nonlinear solution. The independent audit instead reconstructs the rational-function numerator separately and checks the exact constants.

## Meaning

This turns one of the nonlinear source estimates into a numerical, all-order bound. The source begins quadratically, as required for the eventual analytic majorant. The large reconstruction constant is a sufficient upper bound dominated by two radial derivative estimates on a thin collar; it does not measure physical amplification or show an instability.

The working collar is fixed once, not shrunk at each order. Background composition retains a larger prior collar. This source calculation does not substitute the earlier conditional Y(16|z|) statement into a same-argument recursion. Composition closure for the remaining equations is still required.

## Evidence and next work

The derivation and source are bound by BINDING.json. RESULT.json and TERMINAL.json record the producer pass. AUDIT_RESULT.json classifies the separate replay as TRACEFREE_SOURCE_BUDGET_ARITHMETIC_VERIFIED; AUDIT_TERMINAL.json binds that result with SHA-256 f48a1106af8f914ca84f16bf8f8b2674b4bfcd9da499ea9d770feb993bc98be9.

Next, bound the mixed Einstein source and its metric source S_p on the same fixed working collar, then the scalar/radial and wall sources. Recompute the response constants for this collar before combining the chain. A complete nonlinear majorant, a numerical charge-amplitude radius, and a distance-series remainder bound have not yet been established. No new evolution was run, and no manuscript or parent record was altered.
