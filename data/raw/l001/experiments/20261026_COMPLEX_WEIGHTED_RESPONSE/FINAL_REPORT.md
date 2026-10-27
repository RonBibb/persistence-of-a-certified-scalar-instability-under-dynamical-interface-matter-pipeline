# Weighted analytic response bounds verified

Both representations passed the weighted complex-response calculation and an independently authored exact-rational audit. The fixed background collar has radius rho=1/20000. For every integer n>=1, the accepted inputs support the following a priori estimates for compatible holomorphic solutions:

    U_n(f) <= 110115 [||F_n||_(2n+2) + n max_i |g_n,i|],

    U_n(p) <= 240524 [||Sc_n||_(2n+2) + U_n(f)
                      + n||Sp_n||_(2n+1)].

Here U_n(u)=n²||u||_(2n)+n||uprime||_(2n+1)+||usecond||_(2n+2), with ||u||_q=sup d^q|u| and d=1-dist(z,I)/rho. The radial metric coefficient b=c-2p satisfies U_n(b)<=U_n(c)+2U_n(p).

## What this adds

The previous real-axis estimates now extend to the analytic weighted norms used in the manuscript's convergence argument. The metric's forcing derivative is controlled by Nagumo's estimate, rather than supplied as an additional independent input. Neither reconstruction divides by the scalar gradient at its turn.

These constants are conservative bounds, not observed physical amplification. The scalar and metric inequalities have different right-hand sides; their constants should not be compared as physical response magnitudes.

## Verification and limits

The independent reviewer accepted the normal-segment integrals, compact exhaustion with the original weight, real/imaginary complexification, compatible metric reconstruction and derivative bookkeeping. The primary agent reviewed the separately authored verifier and ran it on Linux. It reproduced the exact rational constants and outward integer ceilings in both representations, with pinned input and terminal bindings. The write-page skill was used to keep the derivation and this result report in the local research packet.

The result inherits the independently audited background collar and real-axis inverse estimates and their accepted ODE enclosures. It is not a new ODE validation or a solvability theorem for arbitrary incompatible metric sources. No manuscript or sealed parent was modified and no new trajectory was evolved.

## Remaining amplitude task

The next dependency is numerical control of the actual nonlinear source maps: bulk products, moving-interface compositions, wall and oscillator terms, and current contributions. Those constants must close a scalar majorant and then a proper-distance tail estimate. An explicit charge-amplitude interval is still uncomputed.

Exact records: RESULT.json, AUDIT_RESULT.json, TERMINAL.json, AUDIT_TERMINAL.json and the bound DERIVATION.md. No computation from this packet remains running.
