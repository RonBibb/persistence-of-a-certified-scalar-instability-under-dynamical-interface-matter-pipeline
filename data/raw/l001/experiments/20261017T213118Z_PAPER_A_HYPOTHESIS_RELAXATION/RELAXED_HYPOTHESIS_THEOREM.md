# Scalar turning and wall continuation without convexity

Status: analytical proposal for independent terminal review. The hypotheses and retained sector are those of revision 3, not a different perturbation action. The extension replaces potential convexity by a weaker condition on the supplied background, and constructs a local concave-potential example to show that the replacement is not vacuous. It does not determine the example's full physical tachyon count.

## 1 Definitions and inherited premises

Let an exact smooth canonical Einstein–scalar background on a finite interval [a,b] solve

    a_w'=H a_w,  Phi'=T,
    H'=-T²/3-k/a_w²,  T'=V'(Phi)-4HT,
    H²-1-T²/12+V(Phi)/6-k/a_w²=0,

with warp factor a_w>0, k>0 and pure wall potentials satisfying the doubled-cover junctions. Here a_w denotes the warp factor to distinguish it from the endpoint a. Assume V is C³ in a neighborhood of the traversed scalar range. The same generic scalar sector, positive kinetic form, regular constraint and boundary conditions as revision 3 are retained. No localized kinetic or induced Einstein terms are added.

Set p=a_w⁴ and

    Q=V''(Phi)+4k/a_w²+4T²/3.

Differentiating the scalar background equation gives the exact identity

    (p T')'=p Q T.                                      (1)

The existing regular index theorem counts eigenvalues mu<-4k when T_a<0<T_b and the two strict endpoint coefficients hold for positive baseline Hessians. Its proof, regular Green identity, and normalized launch are inherited; the purpose here is to weaken the additional hypothesis previously used to obtain those endpoint properties and extend to every nonnegative Hessian.

## 2 A nonnegative coefficient criterion

**Theorem A.** Suppose T_a<0<T_b and Q>=0 throughout the closed interval. Then T has exactly one interior zero, and T'>0 everywhere, including both walls. Consequently the regular scalar problem has exactly one eigenvalue below -4k for every background-preserving nonnegative wall-Hessian pair, including zero-Hessian and Dirichlet limits. The mode is real, simple, strictly lowest among regular admissible scalar eigenvalues, and has a uniform gap below -4k over the compact wall family.

**Proof of the background conclusion.** A zero of T cannot also have T'=0. At such a point V'(Phi)=0, and the locally unique background IVP would coincide with its constant-scalar solution; continuation would contradict the opposite endpoint signs. Thus every zero is simple. The endpoint signs force at least one zero by continuity.

If T had two distinct zeros u<v, multiply (1) by T and integrate:

    [p T T']_u^v - integral_u^v p(T')² ds
        = integral_u^v p Q T² ds.

The boundary term vanishes. Therefore

    integral_u^v p[(T')²+Q T²] ds=0.                    (2)

Both summands are nonnegative and p>0. This forces T'=0 throughout [u,v], hence T=0 there, contradicting simple zeros and IVP uniqueness. Exactly one zero s_* remains. The endpoint signs and simplicity make its crossing upward, so T'(s_*)>0.

To its left, T<0 and (1) implies (pT')'<=0. Thus p(s)T'(s)>=p(s_*)T'(s_*)>0 for s<=s_*. To its right, T>0 and (pT')'>=0, giving the same strict lower bound. This proves T'>0 on the closed interval, even where Q=0. The spectral conclusion follows from the endpoint theorem in Section 3 below with n=1. □

The sufficient coefficient condition is

    V''(Phi(s)) >= -4k/a_w(s)² - 4T(s)²/3.             (3)

Convexity implies it but is not necessary. This criterion concerns the background equation for T, not positivity of the physical fluctuation operator: it leads here to a forced unstable mode, not stability. Neither Q<0 somewhere nor a failure of (3) proves stability or even failure of the count. Equation (2) is the elementary disconjugacy argument; no new general oscillation principle is claimed.

## 3 Endpoint form of the compact wall theorem

**Theorem B.** Suppose the same supplied exact background satisfies only

    T_a<0<T_b,  T'_a>0,  T'_b>0.                       (4)

No sign condition on V'' or Q in the interior is required. Let n be the finite number of interior zeros of T. Then every nonnegative wall-Hessian pair and its Dirichlet faces has exactly n regular eigenvalues below -4k. These are real, simple, globally ordered continuous branches, analytic in local compact wall coordinates; each branch increases strictly with either finite Hessian and attains its unique maximum at double Dirichlet. All lie a common positive distance below -4k. For n=1 the branch is the strictly lowest regular scalar eigenvalue. The theorem does not count roots between -4k and zero.

**Proof.** The scalar zeros are simple by the same uniqueness argument and finite by compactness and nonzero endpoint values. For every positive Hessian pair,

    B_a=kappa_a T_a/2-T'_a<0,
    beta_b=-kappa_b T_b/2-T'_b<0.

Choose any such pair as a baseline in the inherited index theorem. It gives precisely n roots below -4k at that pair. It remains to include zero-Hessian faces uniformly, not merely to take a pointwise limit in the unbounded physical quadrant.

Use c_i=1/(kappa_i+1) in [0,1], with c_i=1 for zero Hessian and c_i=0 for Dirichlet. Fix a_w(a)=1 by the usual constant normalization. The regular constrained launch and upper residual are

    d=(1-c_a)T_a/2-c_a T'_a <0,
    psi_a=1, f_a=3lambda c_a/d,
    g_a=3lambda(1-c_a)/(2d)-2T_a,
    G=c_b L_b+(1-c_b)f_b/2,
    lambda=mu+4k, L=g+2T psi.                         (5)

The denominator d has a uniform negative bound because it is a convex combination of two negative endpoint values. At lambda=0 the inherited auxiliary solution gives (f,L)=-v(T,T'), with v,v'>0 for s>a. Hence

    G(-4k,c_a,c_b)=-v_b[c_b T'_b+(1-c_b)T_b/2]<0      (6)

uniformly on the square, using only the upper endpoint signs in (4).

For lambda=-rho², eliminate psi using the regular constraint, whose denominator D=2T²+3rho²/a_w² is strictly positive. As in revision 3,

    f''=P_rho f'+Q_rho f,
    Q_rho=rho²/a_w²+V''+4k/a_w²+2T²+E T'/D,
    E=-4(T'+HT).

The bounded coefficients on the fixed finite interval provide Q_rho>=rho²/a_max²-Q_0. Choose rho²>=1 and rho²>a_max²Q_0. Then Q_rho>0 everywhere, regardless of the interior sign of Q. The launch has f_a>=0 and g_a>0 for every compact wall coordinate, including c_a=0 and c_a=1. The cone f,g>=0 is invariant: f'=g and g'=Q_rho f at g=0. Uniqueness excludes the origin, so f_b,g_b>0. At the upper endpoint alone,

    L_b=[3rho²g_b/a_b²+2T_b T'_b f_b]/D_b>0.         (7)

Thus G>0 below a common finite lower mass barrier on the full square. Interior positivity of T' was not used in (7).

At every root with lambda!=0, (f_b,L_b)=K(2c_b,-(1-c_b)) with K!=0; the nonzero-vector constraint argument excludes K=0. The regular Green identity yields

    G_mu=-Z/(4K a_b⁴)!=0,
    mu_ca=-9lambda²/(d²Z)<0,
    mu_cb=-4a_b⁴K²/Z<0.                              (8)

The determinant is analytic in mass and in the compact wall coordinates. The common lower barrier and strict auxiliary margin yield a fixed compact trapping interval inside (-infinity,-4k). Simple roots cannot be born, disappear, collide, or escape at a wall-coordinate face. The finite root count is locally constant and the square is connected, so it equals the positive-interior count n everywhere. Ordered roots define consistent branches. Their coordinate derivatives are negative by (8), giving the asserted wall response and unique double-Dirichlet maxima. Compactness and (6) give a common positive threshold gap. The inherited conjugate Green argument proves reality of every regular eigenvalue. When n=1, no other eigenvalue can lie lower or at -4k, giving the lowest-mode statement. □

This is an endpoint-based extension of the previous convex specialization. It does not assert that an exact background with arbitrary n and (4) has been constructed. The explicit construction below establishes n=1 outside convexity.

## 4 Remaining-band comparison under endpoint assumptions

The soft-corner injection does not require convexity independently of (4). Its regular normalization, Green identity and responses (8) apply also for -4k<mu<=0. The two-sided root-free neighborhood of -4k follows from (6), analyticity and compactness. Continuing a remaining-band root toward c_a=c_b=1 decreases its mass, keeps it negative, and cannot cross the auxiliary gap or collide with another simple root. Therefore

    N_(-4k,0)(target walls) <= N_(-4k,0)(zero Hessians).

For a single-turn background with T'_a,T'_b>0, the auxiliary lifted endpoint phase remains in (pi,3pi/2). At physical mu=0, the soft-corner launch f_a=-12k/T'_a<0,L_a=0 is anchored at 3pi/2 by the existing left-half-plane corner argument, whose required lower derivative is L'_a=-2T'_a<0 at lambda=0. Thus a certified lifted endpoint phase below 3pi/2 excludes additional tachyons for the full wall family under these weaker hypotheses as well. The criterion requires its own value for each changed background.

## 5 A local exact background with a concave potential

The relaxed condition admits exact backgrounds not covered by potential convexity. This construction changes the action and wall data; it is not a deformation of Paper A's prescribed original walls and does not use a numerical trajectory.

Take the smooth, globally bounded-below potential

    V(Phi)=12+Phi-Phi²/2+Phi⁴,

and initial data at an interior point r=0,

    a_w=1, H=0, Phi=0, T=0, k=1.

The Hamiltonian constraint is exactly 0-1+12/6-1=0. Its exact conservation preserves it. The smooth regular background IVP has a unique solution on some two-sided neighborhood. At r=0,

    T'=1, V''=-1, Q=-1+4=3>0.

Continuity supplies epsilon_0>0 such that a_w>0, T'>0, Q>0 and V''(Phi)<0 throughout [-epsilon_0,epsilon_0]. For each 0<epsilon<epsilon_0 restrict this exact solution to [-epsilon,epsilon]. Then T(-epsilon)<0<T(epsilon), the scalar has one turn, and the potential is strictly concave over its traversed range. Theorem A applies although the convexity assumption of revision 3 fails everywhere on this short scalar range. The quartic term makes the potential bounded below globally; global behavior away from the local range is not used.

Normalize at the lower wall by s=r+epsilon, a_new(s)=a_w(r)/a_w(-epsilon), k_new=1/a_w(-epsilon)². Then a_new(0)=1 and k_new/a_new²=k/a_w². H,T,Phi and their proper-distance equations are unchanged, so Q and all sign conclusions are preserved.

At each wall use pure quadratic Taylor potentials centered on the actual endpoint scalar values:

    tau_a(Phi)=-6H_a+2T_a(Phi-Phi_a)+kappa_a(Phi-Phi_a)²/2,
    tau_b(Phi)= 6H_b-2T_b(Phi-Phi_b)+kappa_b(Phi-Phi_b)²/2.

For any prescribed finite kappa_a,kappa_b>=0, these satisfy both exact background junctions and have the required Hessians. Varying the Hessians leaves their values and slopes unchanged. Dirichlet is the limiting perturbative wall condition, not a finite wall potential of infinite coefficient. The example allows the wall tensions determined by this construction; it does not retain the original central tension signs or parameter values.

There is therefore a local exact class of concave-potential two-wall backgrounds with exactly one regular mode below -4k throughout their nonnegative wall families. This is an existence construction with unspecified interval size, not an explicit closed-form metric, a validated numerical epsilon, or a complete tachyon count. Its physical implication is precise: convexity is not the necessary source of the protected unstable branch; the weaker background/endpoint structure is sufficient.

The example need not rely on the positive effective bulk cosmological term at V(0)=12 or on two negative wall tensions. A second exact seed uses V(Phi)=Phi-Phi²/2+Phi⁴, a_w(0)=1,H(0)=-2,Phi(0)=T(0)=0,k=3. The first integral is 4-1-3=0, T'(0)=1, and Q(0)=-1+12=11>0. The identical local-existence and wall-construction argument applies. For sufficiently small intervals H remains negative, so tau_a=-6H_a>0 and tau_b=6H_b<0, matching the central example's tension-sign orientation; the effective constant term at the central point remains the original negative cosmological one since V(0)=0. Both constructions specify different actions and scales, not a quantitative neighborhood of Paper A's original background.

## 6 Relation to the original and quartic applications

The original quadratic background and the already certified local q~4 quartic backgrounds remain within the convex subclass. Their accepted evidence is unchanged. Theorem A expands the sufficient hypothesis class; Theorem B isolates the actual endpoint conditions used for zero-Hessian compactification. Neither result transfers the original remaining-band certificate to q~4 or to the concave construction. A separate local-total-count argument around the original q=0 solution is presented in LOCAL_TOTAL_COUNT_PERSISTENCE.md.
