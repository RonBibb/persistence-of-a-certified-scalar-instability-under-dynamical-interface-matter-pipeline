# Convex-range single-turn corollary

Status: proposed analytic corollary for independent review. It requires the exact finite canonical background and endpoint/wall hypotheses of the general theorem. No neighboring background is constructed.

Suppose, in addition, `V''>=0` on the entire scalar range traversed by the background. Then the scalar has exactly one interior turn, and the regular boundary problem has exactly one eigenvalue with μ<-4k for every allowed wall pair, including the DD limit.

Proof: `T_a<0<T_b` forces the global minimum of Phi to occur in the interior. At that point `T=0` and `V'(Phi_min)=Phi''>=0`. Equality would give T=0 and V'=0, forcing the scalar to be constant by uniqueness of the smooth background IVP, contrary to the endpoint signs. Therefore V'(Phi_min)>0. Since V' is nondecreasing over the entire scalar range, `V'(Phi(s))>=V'(Phi_min)>0` everywhere. At every scalar turn, consequently `T'=V'(Phi)>0`. Every turn is upward, and the opposite endpoint signs then give exactly one. The reviewed turning-count theorem identifies exactly one negative-shifted eigenvalue.

Non-strict convexity suffices; V'' need not be strictly positive. The assertion is conditional on existence of a background meeting the endpoint conditions. For example a constant potential admits no such background, which is consistent with the proof rather than an exception to it. Under scalar reflection the same conclusion applies to the opposite endpoint orientation, because reflection preserves convexity.

For the inherited central potential, the exact positive constant m² gives V''=m²>0 and thus satisfies this condition. The separate CENTRAL_SINGLE_TURN_APPLICATION.md binds that application to the existing exact background evidence. This corollary supplies no count in -4k<=μ<0 and no nonlinear conclusion.
