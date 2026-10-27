# Upper wall finite branch and saturation

Conditional on the certified smooth central background and the previously accepted regular Green identity, the known simple negative mode extends to a strictly increasing branch for every finite upper wall Hessian increment eta>=0. It approaches a strictly negative upper Dirichlet limiting mode as eta tends to infinity. This statement concerns this tracked branch, not the rest of the spectrum.

## Assumptions and exact deformation

Let s be proper distance, a=exp(W), H=W_s, T=Phi_s, and lambda=mu+4k. The fixed finite background satisfies H_s=−T²/3−k/a² and T_s=m²Phi−4HT. It is the certified central exact background, with k>0, T_b>0 and beta_b=(−gamma/2+4H_b)T_b−m²Phi_b<0. The fixed lower launch coefficient B_a=gamma T_a/2−m²Phi_a+4H_aT_a is nonzero. All background enclosure and producer validity premises are inherited, not reconstructed from rounded numbers.

Add eta(Phi−Phi_b*)²/2 to the upper action. Its value and first derivative vanish at the actual upper background, preserving the same background exactly. The proper residual of the normalized lower-launched solution is F(mu,eta)=R_0(mu)+eta f_b(mu)/2. Its regular IVP depends smoothly and indeed analytically on mu over every compact mass interval. No coefficient divides by T or lambda.

The propagated regular constraint and upper residual give the exact identity

T_b F + (beta_b−eta T_b/2) f_b = 3 lambda psi_b/a_b².

## Division free auxiliary solution at zero shifted mass

At mu=−4k define f=T u and psi=−u_s/2, where

u_ss+2H u_s−(2/3)T²u=0,  u(0)=0, u_s(0)=−2.

This supplies the same normalized lower launch: psi(0)=1, f(0)=0 and f_s(0)=−2T_a. Direct substitution gives psi_s=−2Hpsi−Tf/3. For the scalar equation, use

T_ss=−4H T_s+(m²+4k/a²+(4/3)T²)T.

The coefficients of u in f_ss and the regular scalar right hand side agree because the u equation adds (2/3)T³. The coefficients of u_s agree because 2T_s−2HT=2m²Phi−10HT. Thus the full scalar equation f_ss=−4Hf_s+(m²−mu/a²+2T²)f+(12HT−4m²Phi)psi holds at mu=−4k. This construction remains regular at each zero of T.

Put v=−u. Then v(0)=0, v_s(0)=2 and (a²v_s)_s=(2/3)a²T²v. The first possible loss of positivity is impossible: while v>=0, a²v_s>=2, hence v_s>0 and v>0 for every s>0. Consequently psi_b=v_s(b)/2>0 and f_b=−T_b v_b<0. The constraint identity gives R_0=−beta_b f_b/T_b<0, and

F(−4k,eta)=R_0(1−eta T_b/(2beta_b))<0 for every eta>=0.

The auxiliary endpoint is used only to exclude a branch endpoint. It is not asserted to be a physical eigenmode in an exceptional sector.

## Simplicity and global continuation

The numerical witness at mu_L=−33/25000 requires R_0(mu_L)>0 and f_b(mu_L)>0. Hence F(mu_L,eta)>0 for every eta>=0. Start at the previously accepted normalized simple mode mu_0 in (mu_L,−4k).

At any real root in this open interval lambda<0. If f_b vanished, the endpoint identity would force psi_b=0 and the Robin condition would force f_s(b)=0; uniqueness of the regular linear IVP would contradict psi(0)=1. Thus f_b is nonzero. The accepted regular Green identity gives

F_mu=−Z/(2a_b^4 f_b),  Z=2 integral_0^b a²(f²+6psi²) ds>0,

and therefore dmu/deta=a_b^4 f_b²/Z>0. These identities use the regular norm; no reduced weighted L2 assumption is made at the scalar turning point. Every such root is simple, so it has a locally unique differentiable continuation.

For any proposed finite maximal eta endpoint E, monotonicity bounds the branch inside [mu_0,−4k]. A sequence eta approaching E has a convergent mass subsequence; continuity of F gives a root at its limit. Neither mass boundary is an obstruction: the original mu_L sign excludes the lower endpoint, and the strict auxiliary sign excludes −4k. The limit has lambda<0 and is simple, so the implicit function theorem extends the same branch beyond E. Thus no finite endpoint exists, and the original root continues for all eta>=0. Local uniqueness prevents collisions with another root, but this is not a full-spectrum uniqueness claim.

## Strictly negative Dirichlet limit

The strictly increasing bounded function mu(eta) has a limit mu_D in (mu_0,−4k]. Since R_0 is bounded on the compact mass interval, F=0 implies f_b(mu(eta))=−2R_0(mu(eta))/eta tends to zero. Continuity gives f_b(mu_D)=0. The auxiliary solution has f_b(−4k)<0, so mu_D cannot equal −4k. Therefore

mu_0 < mu(eta) < mu_D < −4k < 0 for every eta>0.

The limiting regular nontrivial profile obeys the unchanged lower Robin condition and upper Dirichlet condition f_b=0. This identifies the limit selected by the tracked branch; it does not claim that this is the only Dirichlet eigenvalue or that it is the lowest mode. No numerical enclosure of mu_D beyond these inequalities is claimed.
