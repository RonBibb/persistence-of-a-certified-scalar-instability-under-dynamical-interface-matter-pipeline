# Physical mean pp form and an exact retained-width sign control

Producer derivation for independent exact-byte audit. Same five-dimensional action and fixed-rho clock/new orthogonal cuts. This test uses the PHYSICAL homogeneous q/Pq sector, not an auxiliary zero-mode mean condition. No numerical calculation is used in this derivation.

## 1. Actual homogeneous coefficient

Hold all physical canonical configurations X, both wall psi_i, and q fixed along a pure momentum direction; retain independent true densities delta Pi_A, both independent wall momenta delta pi_i, and delta Pq. In fixed-time isothermal r=q_bg rho put p_A=delta Pi_A/q_bg, w=delta lambda and delta bar A=diag(a,-a). The physical constraint map is R2 with h=delta q/q=0 and

    2 average_r(a)=delta Pq.

Both metric and scalar wall rows remain those of the same original action. R2's exact augmented mean action has Pq qdot+tau(2 integral A-Pq). Its canonical one-form is linear in Pq; a linear pure-momentum path has no second canonical mean. The post-clock endpoint generator, clock term and actual shift terms are retained. C10's pure-momentum moving-section correction vanishes because all paired extended configuration rows are fixed; no q pair is removed.

Expanding the full R2 Hamiltonian and wall Hamiltonians, the same square completion as C8 therefore gives the PHYSICAL mean coefficient (coefficient of epsilon squared)

    K_pp = integral dr alpha exp(-2lambda)
          [2(a-2wA)^2 + (1/2)G^AB(p_A-2w barp_A)(p_B-2w barp_B)]
       + sum_i alpha_i exp(-lambda_i)/2
              (delta pi_i-w_i pi_i)^T H_i^-1(delta pi_i-w_i pi_i)
       -2 integral dr (partial_r^2 alpha) w^2
       +sum_i partial_barnu(alpha)_i w_i^2.                (K0)

The spatial derivative here is with respect to r (not rho); throughout the rest of this note it is written alpha''. Its measure is dr=q_bg d rho, while TIME derivatives keep the fixed-rho convention. At nonzero Fourier k, add 2|b|^2 inside the metric momentum square with its corresponding background b=0, using the original C8/R1 response. The physical mean has b=0, and a's mean is supplied by delta Pq rather than set to zero. All four independent wall momentum components remain. K0 is not the positive auxiliary evolution norm.

No second-order mean source is set to zero in a volume-only Hessian. This is the complete on-shell quadratic-action route; the canonical mean, clock, shift and endpoint terms explain its identification. Exact independent review of that identification is required.

## 2. Exact two-dimensional zero-charge plane

At one anchor time tau, write h=sqrt(k_dS)>0, sigma=log a(s)+h tau,

    alpha=a^3 exp(2h tau), exp(lambda)=exp(h tau)alpha,
    d=h exp(2h tau), A=-d alpha/2,
    barp_sigma=12d alpha, barp_Phi=0.

Primes here are partial_r, with dr=exp(-h tau)ds/a. The actual anchor lapse obeys its BOTH pressure Robin laws. For arbitrary real c,C define a momentum direction with

    w=c alpha,
    a=C alpha^(1/3)-d c alpha^2,
    p_sigma=2C alpha^(1/3)+18d c alpha^2,
    p_Phi=0, delta pi_a=delta pi_b=0,
    delta Pq=2 average_r(a).                            (P)

The independent canonical data are the displayed p_sigma and delta Pq; w,a are their solved constraint response. The plane does not prescribe a new scalar boundary condition or freeze width. The raw first constraint uses Lbar alpha=10h^2 exp(2h tau)alpha and gives Lbar w=exp(-2lambda)A(2a-p_sigma). The momentum row uses exp(2lambda)kappa'=10A' and sigma'=alpha'/(3alpha), giving a'=exp(2lambda)kappa'w+p_sigma sigma'/2. Both hold exactly. The Robin row holds because w is proportional to the actual lapse. The physical mean is exactly the one supplied above.

The residual square variables are

    a-2wA=C alpha^(1/3),
    p_sigma-2w barp_sigma=2C alpha^(1/3)-6d c alpha^2.

Thus S in K0 is a sum of genuine positive squares. More decisively, combining BOTH wall remainders with the bulk by parts gives

    R[c alpha]=c^2 integral dr [2alpha(alpha')^2-alpha^2 alpha'']
      =c^2 exp(2h tau) integral dr alpha^3
                      [6a^2 H^2+a^2 T^2+3h^2] >0       (R)

when c is nonzero, where H=a_s/a and T=Phi_s are the actual anchor fields. To check the last equality, alpha'=3exp(h tau)aH alpha and alpha''/alpha=3exp(2h tau)a^2(H_s+4H^2); insert H_s=-T^2/3-h^2/a^2. This proof uses no division by Phi_s, warp derivative or oscillator denominator.

If c=0 but C is nonzero, the square integral is strictly positive. Hence K_pp is positive definite on this EXACT TWO-PARAMETER physical-mean plane. By finite-dimensional form continuity it remains positive on the corresponding frozen canonical-data plane in some sufficiently small charged neighborhood on a fixed compact time slab, provided that plane is transported through the actual admitted response map. That radius is uncomputed; this is not positivity on all canonical momenta.

## 3. What this tests and what it leaves open

This is a nontrivial canonical sign control with physical width retained, including the adverse bulk term and both wall terms. It can validate a prospective numerical mean-sector implementation. It does not classify the orthogonal radial complement, all wall-current directions at nonzero charge, low-frequency bands, or the full kinetic form. A positive plane or a finite positive numerical matrix cannot be promoted to full no-ghost. Any numerical test must separately freeze its background approximation, momenta, radial/frequency truncation and tail/error acceptance rules.
