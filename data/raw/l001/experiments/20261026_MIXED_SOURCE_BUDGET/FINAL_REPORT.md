# Mixed Einstein source result

The mixed Einstein nonlinear source estimate passed analytic review and a separately authored exact-rational replay on Linux. Together with the prior tracefree result, this supplies explicit bounds for two bulk source rows in the same fixed working-collar norm. The complete nonlinear remainder and allowed charge amplitude remain uncomputed.

## Verified bounds

With a=80000 and y=Y_<n, both parameter enclosures satisfy

    ||q_M,n||_(2n+1) <= C_M [z^n] y^2/(1-a*y)^2,
    n||S_p,n||_(2n+1) <= C_Sp [z^n] y^2/(1-a*y)^2.

The primary enclosure gives C_M approximately 9767.647148 and C_Sp approximately 8.542105244e12. The independent background enclosure gives approximately 9767.569093 and 8.542084264e12. Exact rational constants are retained in RESULT.json and independently reproduced in AUDIT_RESULT.json. These are sufficient analytic bounds, not physical response measurements.

The estimates hold coefficientwise at all positive orders. Evaluating the rational majorant numerically requires a*y<1; no charge amplitude satisfying the full recursive bound has yet been certified. The large C_Sp is dominated by the inherited conservative tracefree derivative bound.

## What this resolves

The displaced H and T background coefficients are controlled using Cauchy estimates from the larger background collar onto one fixed smaller working collar. The mixed equation therefore has a same-argument coefficient bound, without order-dependent collar shrinking or substituting Y(16z) into the recursive right side. The graph factor in the transport term containing p_rr supplies the required analytic weight.

The compatible identity S_p=Hc-q_M/r_n then propagates the tracefree bound into the metric source. This calculation inherits that identity; it is not a new proof of source compatibility or a numerical evolution.

## Next step and provenance

Next are the Klein–Gordon and radial constraint source rows, using the same composition and transport bounds. Wall sources and response constants on the working collar still follow before full majorant closure.

The audit classification is MIXED_SOURCE_BUDGET_ARITHMETIC_VERIFIED. AUDIT_TERMINAL.json binds audit result SHA-256 bdf44703e299a230dd9646afd1171b11f41aa56ae4e174bd71db4c2ad10b54c9. Source, derivation, parent records and runtime fingerprints are recorded in the producer and audit bindings. No parent record or manuscript was altered. The derivation and this report retain the conditional scope alongside the result.
