# Prospective successor: full second-order proper separation

**Preparation only; no launch authorization.** T15, T17 and T18 are reported independently accepted by the allocation owner/reviewer. A successor must freshly authenticate their terminal reviews, source identities and results. This document does not modify their frozen scope, certify an uncomputed second-order field, or authorize extending the allocation.

## Target and fixed first direction

Compute the signed coefficient d_sep,2 in

    Dproper(z)=D0+z*d_sep,1+z²*d_sep,2+O(z³),
    z=delta² exp(-6ht), (Na²,Nb²)=(1,0).

Use the same AB background, selected material action, current labels, physical time, normal orientation and first-current branch as the accepted packets. No factorial coefficients. Freeze lower-unit-conserved-current direction first; evaluating the other direction requires an explicitly admitted additional arm. Source-local-proper-density-squared normalization multiplies by source_wall_a6 squared.

The physical question is whether the quadratic correction reinforces or opposes the established first-order proper shortening near zero current. Even a positive quadratic correction would not establish finite-charge saturation; a negative one would not prove runaway contraction. The time-dependent branch coefficients decay with z and z².

## What is available and what remains unsolved

Qualified inputs are Eulerian bulk quadratic sources/compatibility (T15), both necessary graph coefficients xi_i,2 (T17), and Eulerian Q5 oscillator/scalar sources plus the exact pulled-load bridge (T18). Earlier accepted packets supply first-order fields, action/background provenance and full wall reconstruction. Energy-exchange qualification, if separately accepted, may be inherited only after its own fresh authentication.

Still unsolved: continuous p2(s), f2(s), g2(s)=f2'(s), their compatible constraint and both boundary conditions. After solving them reconstruct b2=c2-2p2 and chi_i,2, then evaluate the complete physical distance. Known c2 or graphs alone do not determine that distance.

## Freeze one production representation

Recommended computational representation: **Eulerian fixed physical s** for the bulk inverse, because T15 directly qualifies those source formulas. Moving walls remain physical and their traces are already expanded by T18; this is not a frozen-wall approximation. Report the physical distance using the Eulerian expression and independently verify the exact pullback identity. This prospective choice is explicit; it does not retroactively relabel the earlier pulled-chart specification.

Alternatively, a pulled production solver would need independently qualified transformed bulk sources before launch. The accepted wall bridge by itself is not that bulk qualification. Do not insert Eulerian bulk sources into a pulled solver unchanged.

## Regular bulk system and constraint

At r2=-12h, mu2=-108k and lambda2=mu2+4k, integrate

    p2'=-2H*p2-T*f2/3+Sp2,
    f2'=g2,
    g2'=-4H*g2+(m2-mu2 E²+2T²)*f2+B0*p2+Sg2,
    B0=12HT-4m2 Phi,
    C2=T*g2-T'*f2+Dn2*p2-Sc2,
    Dn2=2T²-3lambda2 E².

T15 supplies the exact Eulerian Sp2,Sc2,Sg2 and identity Sc2'+4HSc2=T Sg2+Dn2 Sp2. Retain regular variables through T=0; no inverse scalar gradient is allowed. A numerical whole-cell enclosure of C2 containing zero supplements the symbolic source identity, not replaces it.

## Q6 load is not Q7 load

Use T18's Eulerian undivided boundary source R_i,2 in

    2sigma_i(g2_i+2T_i p2_i)-Gamma_i,2 f2_i=R_i,2,
    d_i,2=2-mu2 Ei², Gamma_i,2=21-1/d_i,2.

This is the Q6 system. A scalar-only Q7 inverse additionally requires Sc2 at each wall:

    A_i,2=1-2Ti²/Dn2_i,
    beta_i,2=Gamma_i,2/(2A_i,2)-2sigma_i Ti Ti'/(Dn2_i A_i,2),
    g_boundary_i,2=-R_i,2/(2A_i,2)+2sigma_i Ti Sc2_i/(Dn2_i A_i,2),
    outward derivative = -sigma_i partial_s.

T18's R_i,2 must not be passed as g_boundary_i,2. Recommended implementation retains the regular three-variable system and Q6; Q7 becomes an independent cross-check after its extra denominator and source-trace gates pass.

## Buildable shooting architecture

Propagate the common background and accepted first-current direction alongside two n2 solutions: homogeneous (sources zero) and loaded particular. At the lower wall use p2_a=1 and0 respectively. For the loaded launch,

    B_a=Gamma_a,2 T_a/2-T_a',
    f2_a=[Sc2_a+3lambda2 Ea² p2_a-T_a R_a,2/2]/B_a,
    g2_a=Gamma_a,2 f2_a/2+R_a,2/2-2T_a p2_a.

For the homogeneous launch set Sc2_a,R_a,2 and all forcing to zero. Enclose B_a away from zero. At the uncertain upper wall form F=g2+2T p2+Gamma2 f2/2. The solution multiplier is (-R_b,2/2-F_particular)/F_homogeneous. Require F_homogeneous to exclude zero across the entire wall/background interval; no selected endpoint, rescue bracket or post-result tolerance change.

The augmented validated integrator must retain enough interval Taylor coefficients and remainders for the new forced RHS. The old homogeneous engine cannot be used unchanged merely by adding pointwise forcing. Two independently implemented variable conventions/source evaluations must agree.

## Fresh jets and parent replay

Saved endpoint records suffice for T18, but saved whole-cell T10 p,f,E boxes do not supply continuous derivative jets. Fresh validated first-order trajectories must retain H,Phi,T,E,p1,f1,g1 and analytic derivative/Taylor data. Generate derivatives from the original ODEs, never finite differences. Authenticate the same wall multiplier/source direction and reproduce accepted endpoint fields, graph coefficients, first-order distance and Q5 loads before using the trajectory as a forcing source. Treat mismatch as technical incompleteness, not a second-order physical effect.

Prefer one coupled background/first-order source flow shared by the two n2 basis solutions. If the two certified engines use separate interval descriptions, retain outward overenclosures rather than intersecting them for a favorable sign. Resource sizing must include the first-order replay and n2 source evaluation, not just the final inverse.

## Distance and exact chart transport

Eulerian production observable:

    d_sep,2=xi_b,2-xi_a,2
             + integral_0^D0 [c2-2p2_E+2p1²] ds
             + [(-2p1)*xi1]_a^b.

For the manuscript's affine X1(r)=xi_a,1+(r/D0)(xi_b,1-xi_a,1), the pulled fields satisfy

    p2_P=p2_E+X1*p1', f2_P=f2_E+X1*f1',
    g2_P=g2_E+X1'*g1+X1*g1', b2_P=b2_E+X1*b1'.

The same distance is

    d_sep,2=xi_b,2-xi_a,2
             + integral_0^D0 [c2-2p2_P+2p1²-2X1'*p1] dr.

Equality follows from integral(X1*b1'+X1'*b1)=[X1*b1]_a^b. The wall load bridge from T18 must reproduce the transformed new fields; keep its X1'*g term. Record each contribution as chart diagnostic, but use the complete sum as the physical observable.

Retain common uncertain D0, background launch and endpoints. Integrate signed whole-cell density over mandatory [0,Dlo] plus optional [Dlo,Dhi], with zero included in every optional contribution. Preserve wall evaluation over the full terminal strip. Export outward rational cell budgets and sum those exported intervals; retain the same physical endpoint uncertainty in graph and integral terms. Do not infer an error bound merely from small cross-engine differences.

## Prospective gates and feasibility probe

Before a full run: independent source-to-code review; exact manufactured forced-system/control solutions; background and first-order replay; direct Q6 residual reconstruction; optional Q7 cross-check; validation of augmented Taylor/Picard remainders; two-engine comparison and immutable bindings. Preserve all failed probes.

Admit a separate bounded resource probe first: one engine over a short fixed physical interval, with representative nonzero forcing and all augmented states; then a full-domain feasibility run if the local enclosure succeeds. The probe must measure cells/steps, Picard/Taylor iterations, runtime, memory, interval growth and whether the expected wall inverse can be enclosed. It does not certify the final observable or authorize changing the contract mid-run. Predeclare probe parameters and failure handling before execution; no guessed full-run ETA from the saved-record tests.

Normal shared Linux leases only, initially one core per engine with no oversubscription and a prospectively specified memory cap. If projected production exceeds one hour, implement atomic exact-resumption checkpoints for the complete augmented state/source parameters and hashes before freeze. No retrofitted live checkpoint scheme. A new user/owner authorization is required for the probe and production launch.

## Acceptance and interpretation

Accept a d_sep,2 enclosure only after complete source/constraint/wall gates, denominator exclusion, full domain coverage, both engines and independent terminal reconstruction pass. Report sign unresolved when the final enclosure contains zero. An unfavorable sign is a valid scientific result; a solver/admission failure is technical incompleteness. Neither may be rescued by a different current direction, precision, domain or error threshold inside the frozen run.

The result would measure one actual second-order physical geometric response of the selected analytic current branch. It would not prove finite-charge saturation, nonlinear stability, neutral-mode excitation, a source-switch transient, an event horizon or a baby universe. Those are different questions requiring additional specified dynamics and evidence.
