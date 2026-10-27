# Unit C1: strict Higuchi-relevant tensor mass gap at the same-action zero-charge anchor

Conditional on the inherited exact central A background, every NONZERO tensor radial mass on this compact collar obeys

    M_n^2 >= (n*pi/L_zeta)^2 + (9/4)k + (11/16)a_min^2 > 2k,
    n=1,2,..., L_zeta=integral_0^D ds/a(s), a_min=min_I a>0.

The massless constant radial mode is retained separately. This is an exact analytic bound with uncomputed positive geometric constants, not a numerical spectrum. The test was declared prospectively in UNIT_C1_PROSPECTIVE_ADDENDUM.json. It is a ZERO-CHARGE de Sitter-separated anchor. The finite-charge branch breaks this separation; a full charged physical scalar norm remains a different gate.

## Actual action and tensor wall domain

At zero charge the branch is ds5^2=ds^2+a(s)^2 gamma_k, Ric(gamma_k)=3k gamma_k, with the inherited exact positive warp, quadratic potential V=m Phi^2/2 and original scalar wall potentials tau_i. Here m denotes the positive mass-SQUARED coefficient. The centered added interaction has chi=0, Phi=Phi_i* at its wall background, so W_i and its first derivatives vanish there. Phase gradients vanish. Thus the original background wall stress is pure tension, without altering the same-action perturbation problem.

For a four-dimensional transverse/traceless perturbation delta g_mu nu=a^2 f(s) t_mu nu(x), set delta Phi=delta chi=delta theta=0. Scalar harmonics/normal scalar response do not source this representation at the de Sitter-invariant anchor. The tracefree linearized Einstein equation and tracefree Israel law give

    -(a^4 f_s)'=M^2 a^2 f, f_s(0)=f_s(D)=0,
    (Box_gamma-2k-M^2)t_mu nu=0.

The second equation defines the Fierz-Pauli mass convention. M^2 is neither A's scalar harmonic eigenvalue mu nor its shifted mu+4k. To check the boundary condition directly, use the mixed-index TT Israel row: variation of the background tension-times-delta cancels its metric piece, leaving the normal derivative of f. There is no wall curvature term or tensor anisotropic derivative source at this anchor. The cover factor multiplies the positive tensor action norm, without changing the equation or Neumann domain. Its radial weight is integral a^2 f^2 ds>0. No boundary condition is added to force a gap.

## Source-bound scalar amplitude without a new profile calculation

The frozen MODEL supplies 0<m<1, gamma=20 and 0<v0,v1<1, as exact rational inequalities. The background scalar solves

    (a^4 Phi_s)'=a^4 m Phi,
    Phi_s(0)=(gamma/2)(Phi(0)-v0),
    Phi_s(D)=-(gamma/2)(Phi(D)-v1).

A nonpositive global minimum cannot occur: a negative interior minimum contradicts Phi_ss=m Phi at Phi_s=0; a negative endpoint minimum contradicts its inward Robin slope. At a zero minimum, the interior ODE uniqueness or the endpoint strict slope gives the same contradiction. Thus Phi>0. A global maximum >=1 similarly cannot be interior because Phi_ss=m Phi>0 there. At the lower wall a maximum requires Phi_s<=0, whereas the Robin slope is positive; at the upper wall it requires Phi_s>=0, whereas that Robin slope is negative. Hence Phi<1 on the whole compact collar. In fact the same argument bounds Phi above by max(v0,v1), but the coarse strict bound is sufficient. Consequently V=m Phi^2/2<1/2. This uses only exact background equations, smoothness and the inherited endpoint laws, not a turn division, numerical flow or tunable profile envelope.

## Exact nonzero spectral pairing and endpoint domain

Define d zeta=ds/a, A=log a and u=a^(3/2) f. Then the Sturm-Liouville norm becomes integral u^2 d zeta and the operator is

    H_T=Q^dagger Q=-partial_zeta^2+(9/4)A_zeta^2+(3/2)A_zeta zeta,
    Q=partial_zeta-(3/2)A_zeta,
    Q^dagger=-partial_zeta-(3/2)A_zeta,
    Qu=0 at BOTH endpoints.

The boundary rows are exactly Neumann f_s=0. The form is integral|Qu|^2, so there is no negative tensor eigenvalue. Its zero eigenspace is u proportional to a^(3/2), i.e. f constant, and is one-dimensional on the connected interval.

For an eigenvalue M^2>0, set v=Qu. It is nonzero, Dirichlet at both ends, and obeys

    H_+ v=M^2 v, H_+=Q Q^dagger
          =-partial_zeta^2+(9/4)A_zeta^2-(3/2)A_zeta zeta.

Conversely every Dirichlet eigenfunction v of H_+ with positive eigenvalue reconstructs u=Q^dagger v/M^2, with Qu=v and the correct endpoint law. The regular finite interval gives the usual discrete complete spectra; this map identifies the ordered nonzero spectrum, including multiplicities. This domain step matters: bounding the original Robin potential pointwise would not give the same result.

## Positive partner potential and bound

Because A_zeta=aH and A_zeta zeta=a^2(H_s+H^2), the partner potential is

    V_+=a^2[(3/4)H^2-(3/2)H_s].

Insert the ACTUAL same-action identities

    H_s=-T^2/3-k/a^2,
    H^2=1+T^2/12-V/6+k/a^2, T=Phi_s.

This gives exactly

    V_+=(9/4)k+a^2[3/4+9T^2/16-V/8]
       >=(9/4)k+(11/16)a_min^2.

The last coarse inequality follows from V<1/2 and T^2>=0. Dirichlet Poincare/min-max on length L_zeta yields the displayed bound for ALL n>=1, not a sampled tower or finite-frequency fit. In particular M_n^2-2k is bounded below by pi^2/L_zeta^2+k/4+11a_min^2/16>0. No numerical values of L_zeta or a_min are asserted.

An independent factorization provides an algebraic cross-check. With D=partial_zeta+A_zeta/2 and the SAME Dirichlet v domain,

    H_+=D^dagger D+2k+a^2[1+5T^2/12-m Phi^2/12].

Its residual is positive under the same coarse amplitude bound. This is not needed for the stronger explicit Poincare-plus-partner-potential estimate.

## Physical use and limits

The mass convention matches the four-dimensional spin-2 Higuchi threshold2k=2h^2. The gap removes the forbidden-mass-range concern for this nonzero ZERO-CHARGE tensor radial tower. It is useful because spatial helicity zero includes the helicity-zero polarizations of massive spin2, while the 4D scalar radial norm alone would not cover them.

This calculation does not provide the complete off-shell Fierz-Pauli/Stueckelberg reduction with scalar walls, a positive combined Dirac-reduced scalar kinetic form, a uniform charged perturbation theorem, or arbitrary-data evolution. It does not act on A's tachyonic scalar direction, which remains. Small analytic background coefficients alone do not transfer this separated spectral theorem to a time-dependent charged physical quotient.

## Literature context, not imported premises

Higuchi's original spin2 result identifies the interval0<M^2<2Lambda/3 as inadmissible due to negative-norm states; Lambda=3k in this convention. Source: https://doi.org/10.1016/0550-3213(87)90691-2 (primary abstract verified through the author's institutional publication record).

Luest and Masias, arXiv:2609.16103v1, Section3.2, derive a9h^2/4 nonzero-tower gap for a different, linear-warp vacuum interval. Their example supplies relevant context for the threshold and mass convention, not our Einstein-scalar profile, wall matter or charged continuation. The factorization technique and the general notion of a warped-tower gap are not claimed novel. The proof above was derived independently for the frozen action/background and includes its nonconstant scalar through T and V. Primary source: https://arxiv.org/html/2609.16103v1 .
