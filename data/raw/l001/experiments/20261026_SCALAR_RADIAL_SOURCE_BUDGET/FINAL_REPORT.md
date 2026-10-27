# Scalar and radial bulk source result

The Klein–Gordon and radial constraint source bounds passed analytic review and an independent exact-rational replay on Linux. Combined with the tracefree and mixed estimates, all four raw bulk source equations now have explicit all-order bounds on the same fixed working collar. The reconstructed compatible bulk loads S_c, S_g and F are also bounded. Wall estimates and full nonlinear closure remain open.

## Result

For a=80000 and the lower-order envelope y=Y_<n, the new bounds have the common form

    ||source_n||_(2n+2) <= C_source [z^n] y^2/(1-a*y)^4.

The primary-enclosure sufficient constants, rounded for display, are:

| Source | Constant |
| --- | ---: |
| Klein–Gordon q_K | 4.49427e5 |
| Radial constraint q_R | 2.30554e6 |
| Reconstructed S_c | 2.07025e14 |
| Reconstructed S_g | 2.04622e12 |
| Reduced scalar forcing F | 6.94590e15 |

Exact rational values for both authenticated background enclosures are retained in RESULT.json and independently replayed in AUDIT_RESULT.json. These large sufficient bounds are not measured physical amplification. They include conservative derivative and denominator estimates inherited from the earlier steps.

## Why this advances the calculation

The exact neutral-background identities cancel the pure background terms before estimating the residuals. Removing the linear rows then leaves quadratic or higher terms. The moving-coordinate transport, exponential coefficients, and composed background functions all fit the same fixed-collar coefficient estimate; no order-dependent domain shrinking is introduced.

This gives numerical control of all raw bulk nonlinear sources at every positive order, rather than checking only finitely many series coefficients. The statement remains conditional on the inherited compatible recursion and analytic background. It does not independently prove compatibility or show that a numerical charge lies inside a convergence radius. Numerical evaluation of the rational majorants requires a*y<1.

## Remaining chain

The next source estimates are the moving-wall Israel, scalar-normal, and oscillator equations. Their order weights must be retained through boundary reconstruction. Response constants must also be evaluated on the fixed working collar rho=1/40000 before all source and inverse bounds are combined into a closed scalar majorant. Only then can a certified charge-amplitude range and distance-series remainder be extracted.

## Evidence

The audit classification is SCALAR_RADIAL_SOURCE_BUDGET_ARITHMETIC_VERIFIED. Its result SHA-256 is 85fa72f8c36d20d1c9e37902ca836ca33017f87a57e0e02699eb80b15963fba5, bound by AUDIT_TERMINAL.json. The producer binding fingerprints source, derivation, authenticated parents and runtime; the audit separately reconstructs the named source contributions and regrouped constants. All computation ran under the inherited Linux lease. No new evolution was run and no manuscript or parent artifact was changed.
