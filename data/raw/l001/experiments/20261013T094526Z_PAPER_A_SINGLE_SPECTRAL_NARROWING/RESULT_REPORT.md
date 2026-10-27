# One central spectral narrowing test

The single admitted test reached its mass-width target after five bisections, with both interval engines agreeing at every midpoint. The negative eigenvalue bracket is now 32 times narrower. Both absolute wall-stiffness coefficient bounds meet the frozen upper/lower width-ratio target of two. The separate independent terminal review accepted the SHARPENED result.

The new certified bracket is

    -21/16000 < mu_star < -4199/3200000,
    -0.0013125 < mu_star < -0.0013121875.

Its exact width is 1/3200000 = 3.125e-7, below the frozen 5e-7 target. The accepted signs at successive exact midpoints were positive, positive, negative, negative, negative in both engines. No zero-containing midpoint, failed cell predicate, timeout or retry occurred.

Conservative outward coefficient bounds are

    5.8319773e-11 <= C_a <= 8.1234169e-11,
    1.3426796e-8 <= C_b <= 2.1239748e-8.

The [exact rational output](output/RESULT.json) controls these displayed bounds. Their multiplicative widths are below two, improving the earlier factors of roughly 28 and 32 without recomputing the norm or endpoint profiles. The existing relative wall-response bound remains unchanged: C_b/C_a is between approximately 230.227 and 261.464. That ratio already canceled the shared spectral factor and norm.

The question is whether a narrower certified interval for the existing central negative eigenvalue improves the two local wall-Hessian response bounds. The exact action, central background, scalar launch enclosure, wall-location enclosure and mode normalization remain those of the accepted certificate. The local stiffness deformation is the previously reviewed background-preserving change eta_i*(Phi-Phi_i_star)^2/2.

The test began with the accepted mass interval (-33/25000,-131/100000). At each rational midpoint, the unchanged primary and independent interval engines had to agree on a strict determinant sign over the complete wall-location interval before the bracket was updated. A zero-containing enclosure would have supplied no sign and stopped this test with the last admitted bracket retained. The maximum was six attempts, with early stopping at width5e-7; the fifth successful attempt reached that target. No retry, adjusted precision, changed background box or successor was used.

The saved norm and wall-profile bounds are valid throughout the original mass strip and therefore remain valid on a narrowed subset. With lambda=mu+4k, the coefficients are recalculated as C_a=9lambda²/(B0²Z) and C_b=9lambda²psi_b²/(beta_b²Z). Their direct ratio is unchanged because it already cancels lambda and Z. A smaller mass uncertainty can tighten absolute coefficients; it does not establish any finite change of stiffness that removes the instability.

The owner process exited with code zero after approximately 81 seconds under one admitted Linux CPU lease and BLAS1. Ten completed midpoint integrations retain their exact determinant enclosures and complete event-subinterval coverage. The unchanged engine algebra controls and fresh semantic controls passed. The original mode and all predecessor results remain unchanged.

The [frozen design](DESIGN.md), [test specification](TEST_SPEC.json), [source bindings](SOURCE_BINDINGS.json), [runtime bindings](RUNTIME_BINDINGS.json), [independent gate](INDEPENDENT_GATE.json) and [user time boundary](TIME_BOUNDARY.json) control this one test. Original flow correctness, exact-background identification and the accepted strip-uniqueness and local response lemmas remain inherited. The [independent terminal audit](TERMINAL_REVIEW.json) reconstructed the sign bracket and coefficient arithmetic without another physical integration, and separately verified the displayed outward bounds. No further test was launched.
