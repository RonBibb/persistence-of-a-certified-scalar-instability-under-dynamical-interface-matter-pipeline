# Israel and oscillator source result

Both remaining raw wall-source bounds passed analytic review and independent exact-rational replay on Linux. The selected recursion now has explicit all-order bounds for all four raw bulk rows and all three raw wall rows. Graph-coefficient reconstruction is also bounded. This completes source enumeration, not the full nonlinear convergence or remainder certificate.

## New bounds

With y=Y_<n, G=(1-160001*y)^(-1) and C_N=|N_a|^2+|N_b|^2, the two-wall estimates have the forms

    n*sum |qI_i,n| <= [z^n](C_I*y^2+C_current*z*C_N)*G^9,
    n*sum |o_i,n| <= C_O [z^n]y^2*G^11.

The primary-enclosure constants, rounded for display, are C_I=3.19594e6, C_current=1.04942e6 and C_O=1.53644e10. Dividing the Israel load by the verified graph divisor gives graph-envelope constants approximately 2.71635e8 for the geometric term and 8.91937e7 for the current term. Exact values for both background enclosures are preserved in the producer and audit results.

These are sufficient analytic bounds, not observed amplitudes, physical growth rates or evidence of instability. Numerical evaluation requires 160001*y<1. An allowed charge amplitude and a full series remainder have not yet been extracted.

## Significance

The wall estimates retain acceleration, lapse and Lorentz-factor changes, scalar-dependent current stress, and oscillator kinetic and friction terms. They distinguish derivatives along the wall from transported bulk derivatives. The order weights needed for reconstruction are included rather than added after the estimate.

The Israel equation contains direct current forcing. The oscillator equation has no separate explicit current term in this selected action; its charge response enters through the geometry and scalar fields. Both independent wall charge labels are retained through C_N.

## Remaining steps

The next step is the reduced Robin boundary load and oscillator reconstruction, followed by the response constants on the fixed working collar. Combining those with the completed source bounds must then give a closed scalar majorant. Only that closure can support a numerical charge-amplitude radius and a controlled distance-series remainder.

The audit classification is ISRAEL_OSCILLATOR_WALL_BUDGET_ARITHMETIC_VERIFIED. Audit result SHA-256 is cf6d109bb7580107cfc0f784ec4f09d84b85a8ed3074eee7000d17d6831d7061, bound by AUDIT_TERMINAL.json. Source, derivation, parent and runtime hashes are retained. No new evolution ran, and no manuscript or parent artifact was changed.
