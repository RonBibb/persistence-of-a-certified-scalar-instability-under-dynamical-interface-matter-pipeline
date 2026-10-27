# General-y hand completion and a conservative sufficient certificate

Same frozen 5D action and zero-charge anchor; no new scientific execution. This note does not use or reinterpret a finite matrix result. Its inequalities are sufficient, not necessary, and failure to certify them is not an adverse kinetic direction.

## Exact remainder completion

Use t=0 isothermal r, alpha=a^3, g=alpha'/alpha, y=w/alpha. Both endpoint terms are included in

    R=-2 integral alpha'' alpha^2 |y|^2 dr
                     +[alpha' alpha^2 |y|^2]_0^q.

Integration by parts is legitimate first for smooth data and then by form continuity. It gives the exact expression

    R=integral alpha^3 [Vplus |y|^2+2g Re(conj(y)y')]dr,
    Vplus=2g^2-alpha''/alpha
         =6a^2 H^2+a^2 T^2+3h^2
         =(2/3)g^2+a^2 T^2+3h^2 >0.

Consequently

    R=integral alpha^3 Vplus |y+(g/Vplus)y'|^2 dr
                     -integral alpha^3(g^2/Vplus)|y'|^2 dr
      >= -(3/2) E,
    E=integral alpha^3 |y'|^2 dr.

This is valid for nonconstant y, complex Fourier amplitudes with their usual Hermitian convention, and the actual homogeneous mean; no gradient or oscillator denominator is divided by. In particular

    K=S+R >= S-(3/2)E.

Thus a response estimate E<=theta S with theta<2/3 proves K>= [1-(3/2)theta] S. This is one concrete complementary continuum gate; a sharper full Schur certificate could succeed even if this sufficient bound is too coarse.

## A conservative radial-gap bound, without evaluation

Let alpha_min/max be the positive real-collar extrema, and a_min=min a. Define the Robin operator Qdagger Q with Q=partial_r-g and Qw=0 endpoints. The factorization note in this folder proves that its sole zero eigenvector is alpha and that its first nonzero eigenvalue lambda_1 satisfies

    lambda_1 >= Lambda,
    Lambda=pi^2/q^2+9h^2+(11/2)a_min^2 >9h^2.

The ACTUAL coupled response obeys the shifted scalar identity

    [Qdagger Q+k^2-3h^2]w=f,
    f=(h/alpha)(-t+P_sigma/2),
    t=a_mom+h alpha w, P_sigma=p_sigma-24h alpha w.

The other residual momenta and b contribute nonnegative terms to S. Pointwise Cauchy-Schwarz in the (t,P_sigma) square yields

    integral |f|^2 dr <= (13/2)(h^2/alpha_min) S.

Project this identity orthogonally in L2(dr) off alpha. This projection is crucial: we do NOT invert the scalar-only ground factor k^2-3h^2, and at its crossing the actual coupled solution already supplies the necessary ground-source compatibility. The derivative Qw annihilates the ground component. Spectral expansion on the excited subspace gives, uniformly for all k>=0,

    ||Qw||^2 <= [Lambda/(Lambda-3h^2)^2] ||f||^2,
    E=integral alpha |Qw|^2 dr <= alpha_max ||Qw||^2.

The estimate follows because lambda/(lambda+k^2-3h^2)^2 is bounded above by lambda/(lambda-3h^2)^2, which is decreasing for lambda>3h^2. Hence

    E <= Theta S,
    Theta=(13/2) h^2(alpha_max/alpha_min)
                                      Lambda/(Lambda-3h^2)^2,
    K >= (1-Delta) S,
    Delta=(39/4) h^2(alpha_max/alpha_min)
                                      Lambda/(Lambda-3h^2)^2.

CERTIFICATE CONDITION: rigorously prove Delta<1 for the SAME exact background using certified extrema, q and h^2 enclosures. None of those numerical evaluations is performed here. This elementary bound may be substantially too pessimistic because it uses global alpha_max/alpha_min. No claim that the present central profile satisfies Delta<1 is made. A box yielding Delta>=1 would leave this particular sufficient test inconclusive, not refute positivity.

This argument handles all momenta through the actual coupled response, including Phi momentum and supplied actual mean. It does not replace C5 by a scalar-only inverse. At t other than zero the positive coordinate/time scaling gives the corresponding rescaled bound; an intended slab norm must explicitly carry those scaling factors rather than use this display with unchanged units.

## Why S itself is a coercive reference at each admitted fixed fiber

At a fixed k the C5/R2 response is smoothing, so S is positive bulk multiplication plus compact response on L2 bulk momenta plus the finite wall variables and, for physical mean, Pq. It has positive essential spectrum. To exclude a zero:

- If k>0 and S=0, its squares give b=ik zeta=0, t=0, P_sigma=P_Phi=0 and all wall residuals zero. Since a_mom=zeta' at nonzero mode, a_mom=0; t=h alpha w=0 forces w=0 and all input momenta vanish.
- In the actual homogeneous sector S=0 gives a_mom=-h alpha w, p_sigma=24h alpha w and p_Phi=0. The momentum row implies w'=0 without division by alpha' or Phi'. The scalar identity would then place w in the kernel of Qdagger Q-3h^2, which has no kernel by the excited gap and its sole ground value -3h^2. Hence w=0 and the actual supplied mean also vanishes. The same argument covers the auxiliary limiting zero-mean fiber separately.

Thus S has a positive lower bound on each fixed fiber; the finite physical mean is not silently replaced by an auxiliary limit. C5/R2 continuous bounded inverse dependence yields uniform bounds on any compact parameter band in the stated finite-slab domain, separately for the physical homogeneous fiber. C8 gives the high-k bounds. This is a reference-square statement, not positivity of K: the missing comparison with R is precisely the issue this note exposes.

## Current disposition

PASS: exact general-y remainder square completion; all-k excited-subspace sufficient estimate; injectivity/coercivity argument for S on the actual admitted momentum fibers.

HELD: verifying Delta<1, proving the sharper response inequality by another route, or certifying the full low/mean pp sign from sampled matrices. No full positivity or adverse witness follows merely from whether this conservative sufficient inequality can be evaluated successfully.
