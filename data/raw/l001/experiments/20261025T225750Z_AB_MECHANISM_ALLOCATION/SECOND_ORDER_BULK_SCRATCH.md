# Prospective Eulerian quadratic bulk reduction — unverified scratch

This is a manual derivation awaiting independent verification, not a computed result or execution contract. It must not be substituted into a pulled-chart calculation without the coordinate transformation. Its purpose is to identify a buildable exact source-compatibility qualification before a full second-order solve.

Use the manuscript's four S6 residuals in the original physical radial coordinate s, so L=partial_s and D=partial_t. Set X=0 in the bulk representation; actual walls still move and require separate endpoint expansion. Write the first-order fields p=z p1, b=-2z p1, f=z f1, with Dz=Rz, R=-6h, k=h squared and mu1=-18k. In the following p,f,g,u mean p1,f1,f1 prime,p1 prime. Let M denote the manuscript's scalar mass coefficient mathfrak m (not its square again).

The first-order bulk relations are

    u = -2Hp - Tf/3
    g_prime = -4Hg + (M-mu1 E²+2T²)f + (12HT-4M Phi)p.

The proposed coefficient extractions from lower-order fields alone are

    qT2 = R²(6p²+f²)
    qM2 = R(2pu+fg/3)
    qK2 = (4M-6mu1 E²)pf + 6ug - 8M Phi p²
    qR2 = 6u²-g²/2 + 4p(12Hu-Tg)
          + 8p²(6H²-T²/2) + M f²/2
          - E²(12kp²+18kf²).

For qK2, before first-order reduction the radial quadratic part is
6ug + 4p(g_prime+4Hg+6Tu) + 8M Phi p²;
the time part is -2mu1 E²pf. This intermediate expression should be checked separately from the reduced expression.

At r2=-12h, mu2=-108k, the Q2-Q3 reconstruction proposes

    c2 = -(3/13)(6p²+f²)
    Sp2 = Hc2-pu-fg/6
    Sc2 = 12H Sp2-(12H²-T²)c2+qR2
    Sg2 = T c2_prime+2M Phi c2-6T Sp2-qK2.

The exact compatibility target is

    Sc2_prime+4H Sc2-T Sg2-D2 Sp2 = 0,
    D2 = 2T²-3(mu2+4k)E².

A qualification must independently expand the original residuals, not merely assert these proposed expressions. It must state which background Hamiltonian and first-order scalar constraint identities were used. Symbolic zero or exact polynomial reduction is required; random numerical examples are controls, not a proof. All programmatic algebra must run on Linux under the allocation leases.

Even successful bulk qualification would not determine second-order wall graphs, scalar and oscillator boundary loads, p2/f2, or D2 as an observable. Here the symbol D2 in the compatibility formula is the manuscript's algebraic coefficient, not the second-order proper-distance coefficient; production code must give them distinct names.
