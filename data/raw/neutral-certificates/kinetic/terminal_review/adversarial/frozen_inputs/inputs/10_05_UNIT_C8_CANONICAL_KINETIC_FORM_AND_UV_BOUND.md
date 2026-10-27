# Unit C8: exact gauge-tangent canonical momentum coefficient and its high-frequency coercivity

This derives a new explicit quadratic MOMENTUM form from the SAME action, retaining its lapse-curvature and wall-pressure remainder. After the C5 metric constraint response is substituted, the specified FORMAL new-cut coefficient is coercive at sufficiently high spatial frequency. At each fixed nonzero frequency it is positive bare multiplication plus a compact radial correction, so only finitely many nonpositive radial directions can remain in THIS tested form. These are mathematical statements about the defined gauge-tangent coefficient, NOT yet an admitted full physical kinetic norm, no-ghost theorem or scalar evolution energy.

The distinction is essential: a complete canonical/new-cap physical-domain identification and the low-frequency/zero-sector sign problem remain. The inherited C6 generic separated norm and C1 spin2 mass inequality do not supply that identification or its coercive norm equivalence.

## 1. Declared canonical variational class

Use a fixed pulled strip coordinate rho, allowing a homogeneous time-dependent flat spatial representative bargamma=diag(ell(t)^2,1); equivalent formulas use its actual isothermal radial distance r. The width/reference and their canonical mean momentum are retained as background/time data, not silently interpreted as a solved physical zero sector. Keep the original doubled bulk/GHY and counted-once wall factors.

Consider the pure-momentum coefficient at one time with

    delta X=delta psi_i=delta bargamma=0, delta kappa=0,
    delta eta_i=0 in the NEW orthogonal-cut polarization.

All canonical momentum variations delta bar_p_A and delta p_i,r remain independent inputs to the METRIC constraint block; local phase densities are not frozen. The metric response w=delta lambda and delta bar_A is the C5 nonzero-mode response with these supplied profile/boost/reference data. Let v=sqrt(gamma), Q=|bar_A|^2+G^AB bar_p_A bar_p_B/2, Cpot=kappa^2/2-Bpotential. Use coefficient-of-epsilon^2 normalization throughout.

This is a gauge-tangent quadratic-action calculation. The complete action is varied first, with lapse/shift and wall rows retained. The linear lapse/shift variations multiply the linear constraints, which are then imposed. The full on-shell second variation is independent of a second-path parameterization ONLY with the complete cap/joint and canonical time-generator terms carried. This is the possible bypass of the C3 nonlinear-volume lambda2 route, not a proof that its physical mean response was solved by C5's auxiliary k=0 continuation.

The trace identity gives the exact canonical generator F=integral kappa v and Hamiltonian term -integral v partial_t kappa. The endpoint -F(tf)+F(ti) is carried; old fixed physical caps are not additionally imposed. The prescribed representative term is linear in its canonical tracefree momentum, so has no direct quadratic pure-momentum coefficient on a linear unreduced canonical path. The new-cut eta variation is zero, so the direct quadratic corner pair2 delta eta delta dot b vanishes in this class. These facts do NOT establish equivalence to an old-cap canonical quotient or a complete nonlinear phase chart.

## 2. Bulk square completion, including clock and shift

The exact bulk constraint Hamiltonian is -integral sqrt(bargamma) alpha F plus beta^m H_m. At fixed configurations, the scalar constraint contains -exp(-2lambda)Q+exp(2lambda)Cpot. Its quadratic expansion, followed by completing momentum squares, gives

    alpha exp(-2lambda){|delta bar_A-2w bar_A|^2
                 +(G^-1/2)(delta bar_p-2w bar_p)^2}
       -2alpha[exp(-2lambda)Q+exp(2lambda)Cpot]w^2.

The notation (G^-1/2)P^2 means G^AB P_A P_B/2, not a matrix square root. The scalar potential of Lbar is Wbar=exp(-2lambda)Q+exp(2lambda)Cpot. The lapse identity gives

    Lbar alpha=-barDelta alpha+Wbar alpha
              =-exp(2lambda)(partial_t-beta.D)kappa.

The clock coefficient is -2v partial_t kappa w^2. The momentum/shift coefficient is +2v beta.D kappa w^2. These cancel the corresponding lapse-identity terms, leaving precisely

    bulk remainder = -2 integral sqrt(bargamma) barDelta(alpha) w^2.

Omitting either the clock or shift contribution would change this coefficient. No pointwise positive sign is assigned to the unrestricted DeWitt trace.

## 3. Both wall momenta and the actual pressure remainder

At each homogeneous wall psi_x=0, b=exp(lambda) and

    Z=p^T H^-1 p, rho=P+exp(-2lambda)Z/2,
    p_wall=-P+exp(-2lambda)Z/2.

Its exact matter Hamiltonian is alpha[exp(lambda)P+exp(-lambda)Z/2] plus tangential shift momentum. The pure-momentum coefficient is exactly

    (alpha exp(-lambda)/2)(delta p-wp)^T H^-1(delta p-wp)
                          -(alpha exp(lambda)/2)p_wall w_i^2.

Both independent chi and phase momenta occur at EACH wall. The flat-reference gravitational wall term -2alpha b k is affine in lambda, so has no direct quadratic lambda coefficient; it is not discarded from the first variation. The background tangent shift and psi_x vanish here, so its pure-momentum coefficient is zero. For another representative or nonorthogonal cuts those conclusions must be recalculated rather than transplanted.

Define

    T=delta bar_A-2w bar_A,
    Pmom=delta bar_p-2w bar_p,
    R_i=delta p_i-w_i p_i.

The resulting FORMAL canonical momentum coefficient is

    Kform = S + Remainder,
    S=integral sqrt(bargamma) alpha exp(-2lambda)
                       [|T|^2+G^AB Pmom_A Pmom_B/2]
       +sum_i (alpha_i exp(-lambda_i)/2)R_i^T H_i^-1 R_i,
    Remainder=-2 integral sqrt(bargamma)barDelta(alpha)w^2
                   -sum_i(alpha_i exp(lambda_i)/2)p_wall,i w_i^2. (K)

The actual pressure Robin law also writes the wall remainder as sum_i partial_barnu(alpha) w_i^2. All coefficients and both endpoint orientations are actual background values.

The remainder is real and nontrivial. At the zero-charge anchor, barDelta(alpha)/alpha=exp(2lambda)[9k_dS/alpha^2-Bpotential]>0, since the C1 source bound gives Bpotential<0. Thus its bulk contribution is genuinely adverse. This is not a ghost finding: its SIZE on the solved metric response, with both wall terms, must be compared to S.

## 4. High-spatial-frequency bound on the defined form

At fixed configurations the linear Hamiltonian row and canonical wall energy row, in the residual variables above, are

    [Lbar_k-2exp(-2lambda)Q]w
           =exp(-2lambda)[bar_A:T+G^AB bar_p_A Pmom_B/2]=f,
    [partial_barnu+beta_tilde,i]w_i=g_i,
    beta_tilde,i=exp(lambda_i)p_wall,i/2-exp(-lambda_i)Z_i/2
                =-exp(lambda_i)rho_i/2,
    g_i=exp(-lambda_i)p_i^T H_i^-1 R_i/2.             (T)

The shifted Robin coefficient is DERIVED from the canonical data; it is not a replacement wall law added to the full system. This identity is used only to estimate the already C5-solved response. All its lower-order potential/Robin coefficients are smooth bounded on each fixed finite slab.

For sufficiently large |k|, the ordinary scalar parameter form in(T) controls

    E_k(w)^2=||w'||^2+k^2||w||^2.

The bounded potential and adverse Robin terms are absorbed by the k^2 term using the one-dimensional parameter trace inequality. The equation then yields

    E_k(w)<=C[||f||/|k|+|g|/sqrt(|k|)],
    ||w||<=E_k/|k|, sum_i|w_i|^2<=C E_k^2/|k|.

Positive bounded weights make ||f||^2+|g|^2<=C S. Hence, for |k| bounded below by a sufficiently large fixed constant,

    ||w||^2<=C S/|k|^3,
    sum_i|w_i|^2<=C S/k^2,
    |Remainder|<=C S/k^2.

Therefore Kform>=(1-C/k^2)S, and Kform>=S/2 once a finite coefficient-dependent cutoff is chosen. No numerical cutoff, sampled mode or rescue tuning is used. Moreover delta bar_p=Pmom+2w bar_p and delta p_i=R_i+w_i p_i give

    ||delta bar_p||_L2^2+sum_i|delta p_i|^2<=C S

at high frequency. The C5 parameter response supplies the corresponding upper bound for the defined coefficient in terms of those canonical inputs. Thus it is a COERCIVE FORMAL constrained pure-momentum block at sufficiently high spatial |k|, on the stated new-cut gauge-tangent domain. It is not the full scalar time/gradient/potential evolution norm, nor a physical no-ghost theorem on an unproved complete phase domain.

## 5. Fixed-mode compactness and the remaining finite sign test

At a fixed nonzero k, with configurations fixed, the C5 linear response maps the Hilbert momentum data

    Hmom=L2(radial;two bulk canonical densities)
                       plus the finite wall momentum space

to w in H2(radial), and delta bar_A in H1(radial). The momentum source contains a smooth coefficient times delta bar_p and no derivative of it in this class; its supplied boundary loads are finite-dimensional. Compact one-dimensional Sobolev embeddings therefore make all response terms compact into radial L2 and wall traces.

Expanding(K) now shows the bounded self-adjoint form operator is positive BARE multiplication

    integral sqrt(bargamma)alpha exp(-2lambda)G^AB delta bar_p_A delta bar_p_B/2
       +sum_i alpha_i exp(-lambda_i)delta p_i^T H_i^-1 delta p_i/2

plus a compact operator on Hmom. The weights have a positive lower bound on a finite slab. Its essential spectrum is positive. Consequently the DEFINED formal coefficient has only finitely many nonpositive radial directions at any fixed nonzero spatial frequency. This is not a count of them, and finite-dimensional wall/compact negative directions have not been excluded. It does not supply a bound uniform as k->0 or classify the true physical exact-zero sector.

## 6. Physical identification and precise residual gate

C3's weighted-volume-only Hessian selects lambda2,0 when a real nonzero Fourier direction is squared. C5's auxiliary zero continuation does not by itself select that physical mean TT/modulus/edge response. The FULL on-shell quadratic-action route above can remove explicit second-path dependence only with its canonical clock, representative, corner and cap terms included. What is now explicit is the gauge-tangent coefficient and its sign test, not a completed equivalence of every original physical initial datum to this canonical class.

To admit it as the physical scalar kinetic norm one must establish the complete canonical/new-cut phase-domain identification, including how mean width momentum and edge polarization are held, and the scalar-normal/evolution domain. Then the remaining low/finite-frequency inequality is exactly S+Remainder>0 with norm equivalence, uniformly on the intended frequency/domain class. The inherited generic separated Z_ext and C1 spin2 mass gap remain useful same-action anchors; their off-shell completeness/coercive identification with Hmom has not been proved here. Continuity of coefficients is not a substitute for that positive anchor.

C8 classification: EXACT_GAUGE_TANGENT_CANONICAL_COEFFICIENT_PASS; FORMAL_HIGH_SPATIAL_FREQUENCY_COERCIVITY_PASS; FIXED_MODE_POSITIVE_ESSENTIAL_SPECTRUM_PASS; COMPLETE_PHYSICAL_KINETIC_AND_EVOLUTION_ENERGY_HOLD. No claim of scalar stability, removal of the growing mode, arbitrary-data/nonlinear formation, persistent sources or projection follows.
