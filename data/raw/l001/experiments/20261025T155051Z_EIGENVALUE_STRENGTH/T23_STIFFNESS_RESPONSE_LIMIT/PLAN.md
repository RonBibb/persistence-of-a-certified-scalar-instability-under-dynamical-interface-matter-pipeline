# Strong-stiffness response limit: endpoint pinning versus scalar participation

This exact postprocessing qualifies the accepted T17 response factorization without a new ODE solve or physical action. It is a derived asymptotic consequence, not an independent numerical intervention or a measured crossover.

Use the inherited simple physical Dirichlet eigenvalue and analytic compact boundary characteristic (Supplement L) to continue the branch analytically in t_a,t_b near zero at fixed background/domain. Along equal stiffness k, set t_a=t_b=t=(1+k)^-1. T14 gives C=-dmu/dt>0 at zero, where the derivative follows both equal coordinates; it is the sum of the two positive compact response magnitudes. Analyticity and the chain rule give
mu(k)=mu_DD-C/(1+k)+O((1+k)^-2),
mu'(k)=C/(1+k)^2+O((1+k)^-3),
and k²mu'(k) tends to C.

The scalar kinetic fraction s tends to s_DD>0, certified in T14. T17's exact identity D mu'(k)=s E therefore implies k²E tends to D C/s_DD>0, while E itself tends to zero. Thus very stiff boundaries suppress endpoint-to-bulk coupling even though the interior scalar component remains nonzero. This does not contradict E near unity at the two low-stiffness settings; neither result locates a finite-k crossover.

Check positivity of both compact partial slopes and s_DD, consistency of their sum with T14's equal slope, exact rational chain-rule identities at several finite positive k, and the endpoint identity f_i=plus/minus2L_i/k giving k² partial_mu=4a_i^4 L_i²/Z. Report conservative rational coefficient bounds. Bind original analytic/simplicity authority and T14/T17 sources/results/reviews. No finite-k remainder constant, threshold, monotonicity of E, physical wall motion or nonlinear consequence. Pinned runtime, one-core original lease/cutoff, atomic no-overwrite output, prospective and terminal independent review.
