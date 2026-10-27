# Local persistence of the complete scalar count

Status: analytical proposal for independent terminal review. This is an existential exact-family consequence of the original background and phase certificates. It supplies no new interval integration, numerical parameter radius, or connection to the separately certified family near q=4.

## 1 Statement

Retain Paper A revision 3's six exact original action parameters and original wall potentials. Replace only the bulk potential by

    V_q(Phi)=m²Phi²/2+qPhi⁴/4.

There exists epsilon>0 and a unique local smooth simultaneous-wall root (A(q),D(q)) through the exact central root at q=0, for every |q|<epsilon. After decreasing epsilon if necessary, every member has positive warp and curvature, exactly one scalar turn and positive T' at both endpoints. For each such background, make background-preserving wall-Hessian changes centered at that background's own wall values. The resulting entire compactified nonnegative wall-Hessian family has exactly one negative regular scalar eigenvalue, below -4k(q), including zero-Hessian and Dirichlet limits.

This is a local total-count family around q=0, unlike the existing quantitative local q~4 certificate, which gives only the count below -4k. No claim is made that epsilon reaches any previously sampled nonzero q, that the two local families connect, or that the neighborhood's size has been computed. Negative q is allowed by the local canonical equations; if a globally bounded-below quartic potential is imposed as an additional physical selection, restrict the conclusion to 0<=q<epsilon. The one-sided restriction still contains genuinely nonquadratic exact backgrounds.

## 2 Inherited evidence and precise use

The premises are not re-proved by a continuity argument:

- Revision 3 and its bound background records establish an exact central simultaneous-wall root with a>0,k>0,T_a<0<T_b. Quadratic convexity gives T'>0 throughout its closed interval. The root is within the specified exact launch/event enclosures.
- `inputs/isolation.json` in the L001 static-tests packet encloses the determinant of the simultaneous residual Jacobian in (A,D) away from zero. The primary and independent chain-rule enclosures are approximately [2221.879246216278,2224.53955879436] and [2220.8647309726075,2225.5545418744878]. Their exact endpoints, not these decimals, are the certificate data. `INDEPENDENT_ISOLATION_AUDIT.json` independently reconstructs the saved determinant arithmetic; it is not another trajectory enclosure.
- The original `test1_v3/RESULT.json`, accepted by `T1_TERMINAL_REVIEW.json`, gives the soft-corner lifted endpoint phase at physical mu=0 in

      theta_E(0)/pi in [577838035/536870912,
                        577858823/536870912].

  The strict distance of its upper bound below 3/2 is exactly 227447545/536870912>0. The original audit checks sources, saved charts and endpoint coverage under inherited flow-engine and exact-background premises, not an independent regeneration of every historical computation.

These inputs and manuscript hashes are listed in SOURCE_BINDINGS.json. The analytic conclusion is conditional on their accepted original certificate premises, just as revision 3's central total count is.

## 3 The exact local background family

For any lower scalar launch A near A_*, define

    a(0)=1, Phi(0)=A,
    H(0)=-[lambda_a+gamma(A-v0)²/2]/6,
    T(0)=gamma(A-v0)/2,
    k(A,q)=H(0)²-1-T(0)²/12+m²A²/12+qA⁴/24.        (1)

This satisfies the exact first integral at launch. The regular background ODE propagates it identically. The polynomial potential, smooth lower data and positive central warp give a smooth solution map in (s,A,q) on a neighborhood of the original closed interval; regular local continuation extends slightly beyond its upper endpoint. Curvature is a parameter of the ODE, given by (1), not held fixed while changing A or q.

With the unchanged upper-wall potential define

    F(A,D,q)=(H(D;A,q)-tau_b(Phi(D;A,q))/6,
              T(D;A,q)+tau_b'(Phi(D;A,q))/2).          (2)

At the inherited exact root F(A_*,D_*,0)=0 and det D_(A,D)F!=0. The ordinary finite-dimensional implicit-function theorem gives a smooth local root graph A(q),D(q) for |q|<epsilon_1, unique within a sufficiently small fixed neighborhood of (A_*,D_*). This is uniqueness of the local graph, not a new global cover over all launches, nor a global uniqueness result for other backgrounds.

The lower wall conditions hold by (1); the upper ones hold by (2); first-integral propagation and a>0 complete the exact static background equations. Normalize the moving interval using x=s/D(q), x in [0,1]. The pulled-back profiles solve an ODE with smooth coefficients and the factor D(q). They vary continuously in the derivatives needed below. D(q)>0, k(q)>0 and a(x;q)>0 persist after reducing epsilon_1. The lower and upper scalar-gradient signs persist. Since the original continuous T' is strictly positive on a compact interval, its minimum is positive; uniform continuous dependence gives T'(s;q)>0 on the whole interval for small q. Thus every member has exactly one scalar turn.

Alternatively V_q''=m²+3qPhi² remains positive on the uniformly bounded local scalar range for sufficiently small |q|. Either route proves the same sufficient local signs; no quantitative lower margin or epsilon is inferred from a floating profile. We use the strictly positive exact central predicates and compactness.

The theorem claims a locally continued simultaneous-wall solution. It does not need, and does not newly assert, preservation of global first-event uniqueness for all q. The central first-event certificate identifies the starting root; retaining an additional first-event label over the family would require carrying its own event-separation argument. The spectral proof itself depends on the exact interval and wall equations, not a global shooting classification.

## 4 Continuous transport of the soft-corner phase

For each exact background use zero perturbative wall Hessians, preserving the just-constructed wall values and slopes. At physical mu=0, lambda=4k(q)>0, the normalized data are

    psi_a=1, f_a=-12k(q)/T'_a(q), g_a=-2T_a(q),
    L_a=0, theta_a=3pi/2.                             (3)

Their dependence on q is smooth because T'_a>0. The regular constrained scalar system on x in [0,1] therefore has solutions continuous jointly in (x,q), with uniform convergence to the original solution as q tends to zero. The constraint propagation is exact for every q.

Let z(x,q)=L(x,q)+i f(x,q). It never vanishes: the constraint

    T L-T'f=3lambda psi/a²

would force psi=0 at a simultaneous zero of L,f, and then g=0; uniqueness of the homogeneous regular IVP would contradict psi_a=1. This argument uses lambda=4k(q)>0, not a principal-angle choice. At q=0, |z| has a strictly positive minimum over [0,1]. Uniform continuity preserves a nonzero margin for q in a smaller closed neighborhood.

The domain [0,1] times a small real parameter interval is simply connected. Thus z/|z| has a unique continuous real phase lift once fixed by theta(0,q)=3pi/2, which is consistent for all q since f_a<0,L_a=0. This is the same lift used in revision 3's positive-shift corner argument: its sign T'_a>0 remains valid. Consequently theta_E(q)=theta(1,q) is continuous. No independent principal-angle reset is permitted at any q.

Let Delta=227447545/536870912. The original certificate supplies theta_E(0)/pi <=3/2-Delta. There is an epsilon_2>0 such that

    |theta_E(q)-theta_E(0)|/pi < Delta/2

whenever |q|<epsilon_2. Hence theta_E(q)/pi<3/2-Delta/2<3/2. This is an existence-of-margin argument; it neither computes epsilon_2 nor reuses the old interval-flow output as an enclosure at q!=0.

For each member, the single-turn auxiliary phase at mu=-4k(q) lies in (pi,3pi/2). Strict spectral phase monotonicity and the preceding physical-zero endpoint bound exclude every root in (-4k(q),0) at the soft corner, and also exclude a massless soft-corner root. The required winding, not just a determinant sign, has been transported.

## 5 Uniform wall-family conclusion

The endpoint conditions T_a<0<T_b and T'_a,T'_b>0 hold for every sufficiently small q. For each such fixed exact background, Theorem B in RELAXED_HYPOTHESIS_THEOREM.md gives exactly one root below -4k(q), with regular compact wall coordinates c_i=1/(kappa_i+1). The same endpoint-based soft-corner injection carries the empty remaining tachyon band from c=(1,1) to every c in [0,1]². This proves exactly one regular physical scalar tachyon throughout the whole wall family, not merely at a finite list of Hessians.

The quantifiers are

    exists epsilon>0 such that for every |q|<epsilon
    and every (c_a,c_b) in [0,1]², the total count is one.

Only the soft-corner phase continuity needs to determine epsilon; the inherited injection then covers the compact wall family at each q. We do not interchange pointwise continuity with a noncompact supremum over kappa. If desired, restrict to a smaller closed |q|<=epsilon/2: exact profiles, endpoint signs and determinant bounds are then uniformly controlled on the product with the compact wall square, giving common symbolic barriers and a positive gap below -4k(q). No numerical gap is supplied.

## 6 Added value and limits

The original total count was already complete and is not rerun. The added statement is that its value is robust under small self-consistent changes of the bulk action and the resulting exact geometry, uniformly across background-preserving nonnegative Hessian changes. It is a standard IFT and strict-margin corollary made applicable by the existing certificates, not a new numerical validation method or a new instability mechanism.

The existing certified interval around q=4 remains useful for a different reason: it supplies an explicit quantitative nonquadratic family with a restricted index. The existential neighborhood here need not reach q=4, and gives no new total count there. No global parameter path, other perturbation sector, self-adjoint completeness, nonlinear evolution, causal horizon or cosmological consequence is claimed.
