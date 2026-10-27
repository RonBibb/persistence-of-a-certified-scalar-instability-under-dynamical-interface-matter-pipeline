# T18 — complete quadratic Q5 wall sources and chart bridge

Prospective candidate. No execution before independent admission and accepted T10/T15/T17 reviews. No wrapper launch after 2026-10-26 00:57:50 UTC. If review cannot finish before that cutoff, leave this packet unrun. No author execution or manuscript changes.

## Purpose and scope

Complete the oscillator/scalar boundary-source subsystem that complements accepted T17 graph coefficients, for both predeclared single-current directions and both walls. This is the undivided Q6 load needed by the future regular n2 inverse. It does not solve p2,f2, produce the bulk-dependent reduced Q7 Robin data, compute proper distance at order2, or certify finite-charge evolution.

Retain the selected action, orientations and original Eulerian radial chart. Bind manuscript Q5/Q6 and SECOND_ORDER_EULERIAN_WALL_SCRATCH.md. Use exact formal degree2 series, not chosen amplitudes. z=delta² exp(-6ht), R=-6h. First-order symbols are p,f,g=f',u=p',gp=f'',T,Tp,Tpp,H,Hp,E,xi,chi,n. Saved n=Ni²Ei^6, not Ni². Second-order symbols p2,f2,g2,chi2,xi2,c2 are arbitrary for off-shell reconstruction controls.

## Independent direct Q5 extraction

Reuse the accepted bounded sparse polynomial/series implementation from T15 with a separate declared symbol basis. It is copied byte-for-byte and authenticated against accepted T15 producer. Build displaced Eulerian traces:

    p_wall=zp+z²(p2+xi*u),
    b_wall=-2zp+z²(c2-2p2-2xi*u),
    log(a(S)/a0)=zHxi+z²(Hxi2+Hp*xi²/2),
    Phi_wall-Phi*=z(Txi+f)+z²(Txi2+Tp*xi²/2+f2+xi*g),
    (f_s)_wall=zg+z²(g2+xi*gp),
    (f_t)_wall=zRf+z²(2R f2+Rxi*g),
    S_t=zRxi+z²2Rxi2, chi=zchi1+z²chi2.

Construct N^-1=E exp(-log(a/a0)-p_wall), B=exp(b_wall), v=B N^-1 S_t and the exact degree2 expansions of (1-v²)^-1 and (1-v²)^-1/2. Evaluate Q5 directly, including the wall-total derivative of p_wall, H(S)S_t, oscillator friction, moving normal, scalar trace, and conserved nu²=zn exp(-6log(a/a0)-6p_wall). No lower-order residual is silently set to zero.

Compare exact extracted coefficients with independent reduced sources, A=Hxi+p:

    o2_E = 36kE² A chi - xi*g - xi²Tp/2,
    j2_E = xi²Tpp/2 + xi*gp + 2p(xi*Tp+g)
           +(2p²+2xi*u)T +36kE²xi*f+18kE²xi²T
           -sigma/2[21(xi²Tp/2+xi*g)+6nA/1000].

Retain arbitrary new fields and prove the full coefficient identities:

    O2 = d2 chi2-f2-Txi2+o2_E,
    J2 = g2+Tp xi2-Tc2+2Tp2
          -sigma[21(f2+Txi2)-chi2]/2+j2_E,
    d2=2+108kE², Gamma2=21-1/d2.

Eliminate chi2 by the exact polynomial identity 2sigma*d2*J2-O2, not by division by a symbolic polynomial. This yields d2 times the undivided Q6 Robin law and its source load. Report all polynomial identities and detected normal-tilt, boost, current-force and missing-Jacobian mutations.

## Explicit pulled-chart bridge

The full future solve uses the manuscript pulled chart, so qualify the transformation rather than mixing sources:

    f2_P=f2_E+xi*g,
    p2_P=p2_E+xi*u,
    g2_P=g2_E+X1'*g+xi*gp,
    o2_P=o2_E+xi*g,
    j2_P=j2_E-X1'*g-xi*gp-2Txi*u+(21sigma/2)xi*g.

The derivative Jacobian X1'*g is essential. The two source loads satisfy

    R2_P-R2_E=2sigma[X1'*g+xi*gp+2Txi*u]-Gamma2*xi*g.

Prove this with arbitrary second-order fields and independently through the source expressions, multiplying by d2 where needed. This is an exact load transformation, not a new bulk-source qualification.

## Four-case interval evaluation

Read all first-order endpoint fields from authenticated T10 full assemblies; use exact bound m2 from its central_bindings.json. Obtain jets from the original analytic ODEs, not numerical differencing:

    Hp=-T²/3-kE², Tpp=m2*T-4Hp*T-4H*Tp,
    u=-2H*p-T*f/3,
    gp=-4Hg+(m2-mu1 E²+2T²)f+(12HT-4m2 Phi)p,
    mu1=-18k.

Use saved Tp authoritatively with background-expression overlap only. Set X1'=(xi_b1-xi_a1)/D0 using the authenticated uncertain background length. Take xi2 from accepted T17 and c2=-(3/13)(6p²+f²). Compute o2,j2,d2,Gamma2 and

    R2=2sigma[Tc2-(Tp-sigma Gamma2 T/2)xi2-j2+sigma o2/(2d2)]

in both charts. Compare the bridge by overlap/zero residual, never intersection. Report all four cases, both engines and hulls, with a_i^6 squared normalization for quadratic local-proper-density units. Endpoint jet identities are inherited ODE consequences and interval consistency checks, not new radial integration.

## Resources and outcome

One leased Linux core, 1GiB, producer900 seconds/wrapper910 seconds, standard authenticated source/runtime map and accepted-parent flags. No new dependencies, ODE or scientific execution on Mac. Wrapper enforces the fixed allocation start cutoff. Atomic no-overwrite controls, identity records, per-engine/full result or failure. Independent source and terminal reviews are mandatory. Successful qualification supplies wall source data only; complete n2 bulk inverse and physical separation remain prospective.
