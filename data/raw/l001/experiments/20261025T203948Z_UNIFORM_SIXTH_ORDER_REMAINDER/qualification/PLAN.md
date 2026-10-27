# Qualification of the parameter derivative enclosure

Fresh one-test authority includes this necessary method qualification. No previous timed cutoff applies. The target is the continuous sixth-order envelope in the parent NEXT_TEST plan, not additional sampled-width science.

The characteristic C(d,beta)=F(1) uses the scaled lower-end normalization psi(-1)=1 and alpha=-2/3+20d²/9+beta d⁴. Analytically prove C^(j)(0)=0 for j=0,1,2,3. Then C(d)/d⁴=4 integral_0^1 (1-t)^3 [C''''(td)/4!] dt. The weight is positive and integrates to one. Thus strict signs of the fourth derivative coefficient throughout the continuous parameter domain imply the required residual signs.

The implementation propagates parameter jets at every base q in an interval, not a polynomial merely centered at zero. The jet seed is d=q+(1/100)epsilon. Every propagated coefficient k encloses (1/100)^k times the kth parameter derivative divided by k!. An outer parameter jet contains spatial jets when computing the spatial Taylor remainder. All 35 derivative-system variables receive strict Picard-tube and order-eight spatial remainder enclosures. Four background states alone have 20 jet coefficients. No small-width division occurs.

Analytic cancellation is independently computed using the accepted rational radial jets. Set lambda2=-2/3, lambda4=20/9, lambda6=beta, and solve the central slope coefficients B0 through B5 successively from f(-d)=0. Do not assume B is even. Divide the upper residual by d² psi(-d). The complete coefficients through order four must be zero through order three and -6(beta+383/15) at order four.

Freeze derivative order four; spatial order eight; dyadic precision 256 fractional bits; parameter seed scale1/100; derivative tube rate factors [1,2,1,1,1] times each accepted scaled physical rate. No radius retry or adaptation. Use exact endpoint betas -766/25 and -1532/75.

Controls: interval reciprocal and zero-divisor rejection; signed manufactured d⁴ integral; undersized tube rejection; analytic zero jets; both parameter endpoints and both G/W systems at q=0,n16; positive q=.01,beta lower,G and q=.005,beta upper,W at n16/32, compared with independently implemented accepted pointwise propagation. All parameter Hamiltonian and constraint coefficients must enclose zero; endpoint background jets must agree. Preserve raw controls and failures.

Qualification uses one core, 1 GiB, the existing shared leases/HOLDs and a 1190-second child/1200-second wrapper ceiling, without retry. Every control record is atomic/no-overwrite. This is below one hour and no automatic resume is claimed. If qualification fails, stop this authorized test with a technical result and independent audit; do not repair and rerun.

If it passes, independently review qualification before freezing production. The production candidate is already fixed in advance: sixteen equal d intervals covering[0,.01], both beta endpoints, G and W representations, n16, identical method bytes, one core, 2690/2700-second child/wrapper caps. Any failed technical gate or unresolved derivative sign is preserved, with no adaptive subdivision or rescue. Size feasibility from qualification timing before admission; if the finite resource plan is not feasible, report that blocker rather than silently raising it.
